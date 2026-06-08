# -*- coding: utf-8 -*-
"""ATOM powiadomienia — jeden wzor karty (#457) dla wielu typow w systemie.

Idea: kazde powiadomienie w systemie (bezpieczenstwo, mail, sejf, gate, najem,
i nowe ktore dojda) to JEDEN atom: ta sama ladna karta-obrazek + przyciski.
Rozni je tylko: ikona paska, kolor (waga), badge i zestaw przyciskow.

Uzycie (jedna linia robi wszystko):

    from tg_alert_kit.atom import build_alert
    a = build_alert(
        typ="sec",
        title="Nowe logowanie na serwer",
        fields=[("Adres IP","185.220.101.47"), ("Czas","18:00"), ("Uzytkownik","sonia")],
        note="Nieznany adres z sieci Tor. Jesli to nie Ty - dzialaj od razu.",
        alert_id="M00099",
        severity="critical",   # opcjonalnie; jak brak -> domyslna waga typu
        badge="SSH",           # opcjonalnie
    )
    # a["card"]         -> sciezka do PNG (wyslij jako media)
    # a["caption"]      -> krotki podpis pod obrazem
    # a["presentation"] -> bloki z przyciskami (tone + buttons)
    # a["buttons"]      -> same rzedy przyciskow

Dodanie NOWEGO typu powiadomienia = jeden wpis w PRESETS (nizej). Nic wiecej.
"""
from __future__ import annotations
from typing import Any

from .card import card_png
from .buttons import build_buttons
from .icons import severity_icon

# Tone OCPlatform wg wagi (kolor ramki przyciskow w kliencie)
_TONE = {
    "critical": "danger", "firing": "danger",
    "warn": "warning", "warning": "warning",
    "info": "info", "ok": "success", "resolved": "success",
}

# ------------------------------------------------------------------
# REJESTR ATOMOW: kazdy typ powiadomienia w systemie.
#   sev      = domyslna waga (kolor/ikona karty), gdy wywolanie nie poda swojej
#   badge    = krotka etykieta w rogu karty (np. zrodlo)
#   caption  = szablon krotkiego podpisu pod obrazem ({icon} {title} {id})
# Przyciski bierze build_buttons() po nazwie typu (buttons.py _LAYOUTS).
# DODAJESZ NOWY TYP? Dopisz tu jeden wpis i ew. layout w buttons.py.
# ------------------------------------------------------------------
PRESETS: dict[str, dict[str, Any]] = {
    "sec":            {"sev": "critical", "badge": "Bezpieczenstwo"},
    "bezpieczenstwo": {"sev": "critical", "badge": "Bezpieczenstwo"},
    "mail":           {"sev": "info",     "badge": "Poczta"},
    "sejf":           {"sev": "warn",     "badge": "Sejf"},
    "gate":           {"sev": "warn",     "badge": "Brama"},
    "najem":          {"sev": "info",     "badge": "Najem"},
    "_default":       {"sev": "warn",     "badge": None},
}


def preset(typ: str) -> dict[str, Any]:
    return PRESETS.get((typ or "").lower(), PRESETS["_default"])


def build_alert(
    typ: str,
    title: str,
    fields: list[tuple[str, str]],
    alert_id: str,
    note: str | None = None,
    severity: str | None = None,
    badge: str | None = None,
    foot_left: str | None = None,
) -> dict[str, Any]:
    """Buduje kompletny atom powiadomienia: karta PNG + podpis + przyciski.

    Zwraca dict gotowy do wyslania narzedziem `message`:
      card, caption, presentation, buttons, tone, severity, type, id
    """
    p = preset(typ)
    sev = (severity or p["sev"]).lower()
    badge = badge if badge is not None else p["badge"]
    tone = _TONE.get(sev, "warning")

    # 1) Karta-obrazek (TEN wzor z #457)
    png = card_png(
        title=title,
        fields=fields,
        severity=sev,
        note=note,
        badge=badge or "",
        foot_left=foot_left,
        alert_id=alert_id,
    )

    # 2) Krotki podpis pod obrazem (gdy klient nie pokaze obrazu / podglad)
    icon = severity_icon(sev)
    caption = f"{icon} {title}" + (f" \u00b7 {alert_id}" if alert_id else "")

    # 3) Przyciski-komendy wg typu
    rows = build_buttons(typ, alert_id)
    blocks = [{"type": "buttons", "buttons": row} for row in rows]

    return {
        "card": png,
        "caption": caption,
        "presentation": {"tone": tone, "blocks": blocks},
        "buttons": rows,
        "tone": tone,
        "severity": sev,
        "type": typ,
        "id": alert_id,
    }
