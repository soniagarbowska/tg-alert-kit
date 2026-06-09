# -*- coding: utf-8 -*-
"""Kontekstowe przyciski — KATALOG dozwolonych akcji + dobor do tresci.

Filozofia (uzgodnione z Sonia 2026-06-08):
  Przyciski maja byc KONTEKSTOWE pod konkretny komunikat, nie statyczne
  "Odloz/Zalatwione". ALE nie pozwalamy LLM wymyslac dowolnych komend —
  bo klik = komenda, ktora agent musi UMIEC wykonac, a zlosliwa tresc maila
  moglaby wstrzyknac dziwna akcje. Dlatego:

  1) DETERMINISTYCZNIE: gdy dane wprost daja akcje (np. opcje decyzji) —
     budujemy przyciski 1:1 z danych. 100% pewne, zero LLM.
  2) KATALOG (whitelist) per typ: kazdy typ ma maly zestaw DOZWOLONYCH akcji
     (komenda + wzor etykiety + styl). Handler umie je wykonac.
  3) LLM tylko WYBIERA z katalogu, ktore akcje pasuja, i wypelnia parametr.
     Nigdy nie tworzy surowej komendy. Walidacja whitelist przed wyslaniem.

Komendy to KOMENDY po polsku (klik => bot dostaje tekst => agent wykonuje).
Potwierdzone ze dzialaja (callbacki NIE — brak handlera w pollingu).
"""
from __future__ import annotations
from typing import Any, Callable
import re


# ---------------------------------------------------------------------------
# KATALOG akcji: id -> {label, cmd, style, needs_id}
# label moze miec {param} do wypelnienia (np. numer opcji, data).
# cmd to wzor komendy; {id} = alert_id, {param} = parametr akcji.
# ---------------------------------------------------------------------------
# Telegram inline-buttony NIE maja kolorow (style success/primary jest tylko
# wskazowka dla innych kanalow). Jedyne wizualne rozroznienie na TG to EMOJI w
# labelce — dlatego kazda akcja ma emoji-prefiks (zielone/czerwone/neutralne sie
# nie zlewaja). Labelki z polskimi literami. (uzgodnione z Sonia 2026-06-09)
CATALOG: dict[str, dict[str, Any]] = {
    # --- uniwersalne ---
    "pozniej":     {"label": "⏰ Później",            "cmd": "/alert_pozniej {id}",    "style": "secondary"},
    "zalatwione":  {"label": "✅ Załatwione",          "cmd": "/alert_zalatwione {id}", "style": "success"},
    "odrzuc":      {"label": "✖️ Odrzuć",             "cmd": "/alert_odrzuc {id}",     "style": "secondary"},
    # --- bezpieczenstwo (sec/tech) ---
    "to_ja":       {"label": "✅ To byłam ja",         "cmd": "/alert_toja {id}",       "style": "success"},
    "nie_ja":      {"label": "🔴 To nie ja — zbadaj",  "cmd": "/alert_nieja {id}",      "style": "danger"},
    "zablokuj":    {"label": "⛔ Zablokuj adres",      "cmd": "/alert_zablokuj {id}",   "style": "danger"},
    # --- decyzja (sejf) — przyciski z opcji buduje builder, te sa pomocnicze ---
    "wybierz":     {"label": "{param}",              "cmd": "/alert_wybierz {id} {param_key}", "style": "primary"},
    "pokaz":       {"label": "🔓 Pokaż pełne (2FA)",   "cmd": "/alert_pokaz {id}",      "style": "secondary"},
    # --- mail ---
    "zaplacone":   {"label": "💰 Oznacz zapłacone",    "cmd": "/alert_zaplacone {id}",  "style": "success"},
    "nie_nasze":   {"label": "↪️ To nie nasze",       "cmd": "/alert_nie_nasze {id}",  "style": "secondary"},
    "odpisz":      {"label": "✍️ Przygotuj odpowiedź", "cmd": "/alert_odpisz {id}",     "style": "primary"},
    # --- wiki/crm (sprzecznosci) ---
    "zostaw_nowe": {"label": "🆕 Zostaw nowe",         "cmd": "/alert_zostaw_nowe {id}", "style": "primary"},
    "zostaw_stare":{"label": "📜 Zostaw stare",        "cmd": "/alert_zostaw_stare {id}","style": "secondary"},
    "scal":        {"label": "🔗 Scal",                "cmd": "/alert_scal {id}",       "style": "primary"},
    # --- skille (propozycje skill_proposer) ---
    "buduj":       {"label": "🔨 Buduj ten skill",     "cmd": "/alert_buduj {id}",      "style": "primary"},
    "nie_teraz":   {"label": "⏸️ Nie teraz",          "cmd": "/alert_nie_teraz {id}",  "style": "secondary"},
    # --- dokumenty / radar ---
    "przejrzyj":   {"label": "👀 Przejrzyj",           "cmd": "/alert_przejrzyj {id}",  "style": "primary"},
}

# DOZWOLONE akcje per typ (whitelist). LLM moze wybierac TYLKO z tej listy.
ALLOWED: dict[str, list[str]] = {
    "sec":            ["to_ja", "nie_ja", "zablokuj", "pozniej"],
    "bezpieczenstwo": ["to_ja", "nie_ja", "zablokuj", "pozniej"],
    "tech":           ["zalatwione", "pozniej"],
    "mail":           ["zaplacone", "odpisz", "nie_nasze", "pozniej", "zalatwione"],
    "sejf":           ["wybierz", "pokaz", "pozniej"],
    "decision":       ["wybierz", "pokaz", "pozniej"],
    "wiki":           ["zostaw_nowe", "zostaw_stare", "scal", "pozniej"],
    "crm":            ["scal", "odrzuc", "pozniej"],
    "seo":            ["zalatwione", "pozniej"],
    "skille":         ["buduj", "nie_teraz", "odrzuc"],
    "proposal":       ["buduj", "nie_teraz", "odrzuc"],
    "dokumenty":      ["przejrzyj", "pozniej", "zalatwione"],
    "zadanie":        ["zalatwione", "pozniej"],
    "info":           ["zalatwione", "pozniej"],
    "info-digest":    ["zalatwione", "pozniej"],
    "_default":       ["pozniej", "zalatwione"],
}


def _btn(action_id: str, alert_id: str, *, label: str | None = None,
         param_key: str | None = None) -> dict[str, Any] | None:
    spec = CATALOG.get(action_id)
    if not spec:
        return None
    cmd = spec["cmd"].format(id=alert_id, param_key=(param_key or "")).strip()
    return {
        "label": label or spec["label"],
        "action": {"type": "command", "command": cmd},
        "style": spec["style"],
    }


def from_options(options: list[dict], alert_id: str,
                 *, has_masked: bool = False) -> list[list[dict[str, Any]]]:
    """DETERMINISTYCZNIE: przycisk z kazdej opcji decyzji (1:1 z danych).

    Etykieta = krotka nazwa opcji. Komenda = /alert_wybierz {id} {1|2|...}.
    To jest najpewniejsza sciezka — zero LLM, zero ryzyka.

    has_masked: czy w tresci faktycznie cos zamaskowano (twarde PII). Przycisk
    "Pokaz pelne (2FA)" dodajemy TYLKO wtedy — bez tego nie ma czego odslaniac
    (telefon/nazwisko nie sa wrazliwe, zasada Soni 2026-06-08).
    """
    row = []
    for idx, opt in enumerate(options, 1):
        # krotka, czytelna etykieta: usun prefiksy typu "Przyjac nowy: …888"
        name = opt.get("button") or opt.get("name", f"Opcja {idx}")
        name = re.sub(r"\s+", " ", name).strip()
        if len(name) > 22:
            name = name[:21] + "…"
        row.append({
            "label": name,
            "action": {"type": "command", "command": f"/alert_wybierz {alert_id} {idx}"},
            "style": "primary",
        })
    rows = [row] if row else []
    # druga linia: pokaz pelne (TYLKO gdy cos zamaskowane) + pozniej
    extra = []
    if has_masked:
        pb = _btn("pokaz", alert_id)
        if pb:
            extra.append(pb)
    lb = _btn("pozniej", alert_id)
    if lb:
        extra.append(lb)
    if extra:
        rows.append(extra)
    return rows


def from_catalog(action_ids: list[str], alert_id: str,
                 alert_type: str = "_default") -> list[list[dict[str, Any]]]:
    """Buduje przyciski z listy id akcji — TYLKO te z whitelist danego typu."""
    allow = set(ALLOWED.get((alert_type or "_default").lower(), ALLOWED["_default"]))
    btns = []
    for aid in action_ids:
        if aid not in allow:
            continue
        b = _btn(aid, alert_id)
        if b:
            btns.append(b)
    # ulóz max 2 w rzedzie
    rows = [btns[i:i + 2] for i in range(0, len(btns), 2)]
    return rows


def default_for(alert_type: str, alert_id: str) -> list[list[dict[str, Any]]]:
    """Fallback: domyslny zestaw z whitelist danego typu (bez LLM)."""
    ids = ALLOWED.get((alert_type or "_default").lower(), ALLOWED["_default"])
    return from_catalog(ids, alert_id, alert_type)


def suggest_with_llm(alert_type: str, alert_id: str, title: str, body: str,
                     llm_fn: Callable[[str], Any] | None = None,
                     max_buttons: int = 3) -> list[list[dict[str, Any]]]:
    """LLM WYBIERA z whitelist, ktore akcje pasuja do tresci. Nie tworzy komend.

    llm_fn: funkcja prompt->dict/json (np. wiki/scripts/llm.gemini_flash json_out).
    Gdy brak llm_fn lub blad — zwraca default_for (bezpieczny fallback).
    """
    allow = ALLOWED.get((alert_type or "_default").lower(), ALLOWED["_default"])
    if llm_fn is None:
        return default_for(alert_type, alert_id)
    opts = "\n".join(f"- {aid}: {CATALOG[aid]['label']}" for aid in allow if aid in CATALOG)
    prompt = (
        "Jestes asystentem dobierajacym przyciski-akcje do powiadomienia Telegram.\n"
        "Wybierz NAJWYZEJ {n} akcji z DOZWOLONEJ listy, ktore najlepiej pasuja do tej\n"
        "konkretnej wiadomosci. Zwroc TYLKO JSON: {{\"actions\":[\"id1\",\"id2\"]}}.\n"
        "Uzywaj wylacznie id z listy. Kolejnosc = waznosc.\n\n"
        "DOZWOLONE AKCJE:\n{opts}\n\n"
        "TYP: {typ}\nTYTUL: {title}\nTRESC:\n{body}\n"
    ).format(n=max_buttons, opts=opts, typ=alert_type, title=title, body=body[:1200])
    try:
        res = llm_fn(prompt)
        ids = res.get("actions") if isinstance(res, dict) else None
        if not ids:
            return default_for(alert_type, alert_id)
        # twarda walidacja: tylko z whitelist
        ids = [a for a in ids if a in allow][:max_buttons]
        if not ids:
            return default_for(alert_type, alert_id)
        return from_catalog(ids, alert_id, alert_type)
    except Exception:
        return default_for(alert_type, alert_id)
