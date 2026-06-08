# -*- coding: utf-8 -*-
"""ATOM tekstowy — styl z wiadomosci #439 (ten ktory Sonia zaakceptowala).

Filozofia: jeden STYL, rozne UKLADY. Kazde powiadomienie sklada sie z KLOCKOW,
ktore renderuja sie w tym samym stylu (naglowek + separatory + punktory +
pogrubienia + monospace + cytat + kropki statusu + kursywa w stopce).

Dodanie NOWEGO powiadomienia = ulozenie listy klockow (albo gotowy przepis
w presets.py). Styl jest wspolny i spojny, dane/uklad dowolne.

KLOCKI (block kinds):
    ("header", icon, title, subtitle)   -> ICON **Title**  /  subtitle
    ("divider",)                        -> ━━━━━━━━━━━━━━
    ("field", label, value)             -> • **Label:** value   (mono auto dla IP/kwot)
    ("field", label, value, "mono")     -> wymus monospace
    ("field", label, value, "plain")    -> wymus zwykly
    ("entry", color, name, tag)         -> 🟠 **Name** — tag    (pozycja listy/digestu)
    ("note", text)                      -> > text               (cytat = uwaga)
    ("spoiler", text)                   -> ||text||             (ukryte, mniej wazne)
    ("text", text)                      -> surowa linia
    ("space",)                          -> pusta linia
    ("footer", text)                    -> divider + _text_ (kursywa)

UWAGA techniczna (zweryfikowane telethoniem 2026-06-08):
  Emoji spoza BMP (np. 🔥 📥 🟠) przed pogrubieniem moga przesunac bold o 1 znak
  (UTF-16 surrogate pair liczony jako 1 zamiast 2). Dlatego:
  - ikony wagi w naglowku to znaki BMP: ⛔ ⚠️ ℹ️ ✅ (bezpieczne).
  - przy kropkach w "entry" dajemy ODSTEP po kropce, a nazwe pogrubiamy po spacji
    — testy live potwierdzaja czytelnosc.
"""
from __future__ import annotations
from typing import Any, Iterable

# --- ikony wagi (BMP, bezpieczne dla pogrubien) -----------------------------
SEV_ICON = {
    "critical": "⛔", "firing": "⛔",
    "warn": "⚠️", "warning": "⚠️",
    "info": "ℹ️",
    "ok": "✅", "resolved": "✅",
}
SEV_WORD = {
    "critical": "KRYTYCZNE", "firing": "KRYTYCZNE",
    "warn": "UWAGA", "warning": "UWAGA",
    "info": "INFORMACJA",
    "ok": "OK", "resolved": "ROZWIAZANE",
}

# --- kropki statusu (kolory) ------------------------------------------------
# Nazwa -> emoji. Uzywane w "entry" do szybkiego oznaczenia wagi pozycji.
DOT = {
    "red": "🔴", "czerwony": "🔴",
    "orange": "🟠", "pomaranczowy": "🟠",
    "yellow": "🟡", "zolty": "🟡",
    "green": "🟢", "zielony": "🟢",
    "blue": "🔵", "niebieski": "🔵",
    "white": "⚪", "bialy": "⚪", "szary": "⚪",
    "black": "⚫", "czarny": "⚫",
}

BULLET = "•"
DIVIDER = "━" * 14

# Ikony tematyczne dla naglowkow — TYLKO BMP (nie psuja pogrubienia tytulu).
# 📥📧📨 sa non-BMP i przesuwaja bold o 1 znak -> uzywamy BMP-owych odpowiednikow.
# Zweryfikowane telethoniem 2026-06-08.
TOPIC_ICON = {
    "mail": "✉️", "poczta": "✉️",
    "sec": "⛔", "bezpieczenstwo": "⛔", "serwer": "⛔",
    "sejf": "⚠️", "gate": "⚠️", "brama": "⚠️",
    "najem": "ℹ️", "dom": "ℹ️",
    "bank": "ℹ️", "przelew": "ℹ️",
    "status": "✅", "ok": "✅",
    "kalendarz": "⏱", "czas": "⏱",
    "info": "ℹ️",
}

# pola pokazywane monospace (dane techniczne / liczby)
# Etykieta sugeruje dane techniczne, ALE mono wlaczamy tylko gdy WARTOSC faktycznie
# wyglada technicznie (cyfry/./:/@/slash) — zeby "Porty: bez zmian" nie szlo monospace.
_MONO_HINT = ("ip", "adres ip", "host", "login", "uzytkownik", "user",
              "plik", "sciezka", "path", "url", "domena", "hash",
              "kwota", "cena", "saldo", "czynsz", "nr konta", "konto", "nip",
              "iban", "telefon", "tel", "kod")

import re as _re
_TECH_VALUE = _re.compile(r"[\d]")  # wartosc techniczna = zawiera cyfre


def b(x: Any) -> str:
    """Pogrubienie."""
    return f"**{x}**"


def m(x: Any) -> str:
    """Monospace."""
    return f"`{x}`"


def i(x: Any) -> str:
    """Kursywa."""
    return f"_{x}_"


def _auto_mono(label: str, value: Any = None) -> bool:
    k = (label or "").lower()
    if not any(tok in k for tok in _MONO_HINT):
        return False
    # mono tylko gdy wartosc wyglada technicznie (ma cyfre); proza zostaje zwykla
    if value is None:
        return True
    return bool(_TECH_VALUE.search(str(value)))


def _render_block(blk: tuple) -> list[str]:
    kind = blk[0]

    if kind == "header":
        _, icon, title, subtitle = (list(blk) + [None, None, None])[:4]
        lines = [f"{icon}  {b(title)}"]
        if subtitle:
            lines.append(subtitle)
        return lines

    if kind == "divider":
        return [DIVIDER]

    if kind == "field":
        # ("field", label, value [, mode])
        label = blk[1]
        value = blk[2]
        mode = blk[3] if len(blk) > 3 else "auto"
        mono = (mode == "mono") or (mode == "auto" and _auto_mono(label, value))
        shown = m(value) if mono else value
        return [f"{BULLET} {b(str(label) + ':')} {shown}"]

    if kind == "entry":
        # ("entry", color, name, tag)
        _, color, name, tag = (list(blk) + [None, None, None])[:4]
        dot = DOT.get((color or "white").lower(), "⚪")
        line = f"{dot}  {b(name)}"
        if tag:
            line += f" — {tag}"
        return [line]

    if kind == "section":
        # ("section", "NAGLOWEK") -> pusta linia + pogrubiony naglowek sekcji
        return ["", b(str(blk[1]).upper())]

    if kind == "option":
        # ("option", marker, name, za, ryzyko) -> zwarty blok opcji (bez pustych linii
        # wewnatrz). 'za'/'ryzyko' zaczynaja sie od slowa (nie +/-), bo Telegram
        # zamienia linie z + lub - na identyczne kropki listy (zweryfikowane #512).
        _, marker, name, za, ryz = (list(blk) + [None] * 5)[:5]
        lines = [f"{marker} {b(name)}"]
        if za:
            lines.append(f"     {b('Za:')} {za}")
        if ryz:
            lines.append(f"     {b('Ryzyko:')} {ryz}")
        return lines

    if kind == "note":
        return [f"> {blk[1]}"]

    if kind == "spoiler":
        return [f"||{blk[1]}||"]

    if kind == "text":
        return [str(blk[1])]

    if kind == "space":
        return [""]

    if kind == "footer":
        return [DIVIDER, i(blk[1])]

    return []


def compose(blocks: Iterable[tuple], *, mask_pii: bool = True) -> str:
    """Sklada liste klockow w tekst w stylu #439.

    mask_pii: domyslnie True -> przepuszcza tekst przez centralna polityke PII
    (~/wiki/scripts/mask_sensitive.py). Maskuje TYLKO twarde dane wrazliwe
    (PESEL/dowod/data ur./konto/NIP/KW). Imie, nazwisko, TELEFON, e-mail, adres
    zostaja widoczne — zgodnie z zasada Soni (2026-06-08).
    """
    out: list[str] = []
    for blk in blocks:
        out.extend(_render_block(blk))
    # zwin potrojne puste linie do pojedynczych
    text = "\n".join(out)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    text = text.strip()
    if mask_pii:
        try:
            from .pii import mask as _mask
            text = _mask(text) or text
        except Exception:
            pass
    return text
