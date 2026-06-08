# -*- coding: utf-8 -*-
"""Maskowanie PII — JEDNO zrodlo prawdy: ~/wiki/scripts/mask_sensitive.py (zasada Soni).

Zasada Soni (audyt 2026-06-08): maskuj TYLKO dane naprawde wrazliwe:
PESEL, nr dowodu, data urodzenia, nr konta/IBAN, NIP, nr ksiegi wieczystej.
NIE maskuj: imienia, nazwiska, adresu, TELEFONU, e-maila — to NIE sa dane wrazliwe.

Dlatego w powiadomieniach pokazujemy normalnie: kto (imie i nazwisko), telefon,
e-mail, adres. Ukrywamy tylko twarde PII. Nie wymyslamy wlasnych regul —
uzywamy centralnego mask() zeby polityka byla spojna w calym systemie.
"""
from __future__ import annotations
import os
import sys

_WIKI_SCRIPTS = os.path.expanduser("~/wiki/scripts")


def _load_central_mask():
    try:
        if _WIKI_SCRIPTS not in sys.path:
            sys.path.insert(0, _WIKI_SCRIPTS)
        from mask_sensitive import mask as _mask  # type: ignore
        return _mask
    except Exception:
        return None


_CENTRAL = _load_central_mask()


def mask(text: str | None) -> str | None:
    """Maskuje TYLKO twarde PII wg centralnej polityki Soni.

    Jak centralny modul niedostepny -> zwraca tekst bez zmian (NIE wymyslamy
    wlasnego maskowania; lepiej nie ruszac niz nadmaskowac telefon/nazwisko).
    """
    if not text:
        return text
    if _CENTRAL is not None:
        try:
            return _CENTRAL(text)
        except Exception:
            return text
    return text


def available() -> bool:
    """Czy centralna polityka PII jest podpieta."""
    return _CENTRAL is not None
