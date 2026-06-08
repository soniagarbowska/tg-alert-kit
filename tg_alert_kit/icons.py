# -*- coding: utf-8 -*-
"""Ikony alertow — wzorzec metalmatze/alertmanager-bot (653 gwiazdki).

Tamten bot uzywa DWOCH stanow: firing i resolved. Prosto, czytelnie.
My rozszerzamy minimalnie o wage (krytyczny/uwaga/info), reszta jak u nich.

Zero wymyslania kolorow tla — to tylko znaki w tekscie.
"""
from __future__ import annotations

# Stan alertu — dokladnie jak alertmanager-bot
# UWAGA: emoji spoza BMP (np. 🔥 U+1F525) powoduja przesuniecie pogrubien
# o 1 znak w Telegramie (UTF-16 surrogate pair = 2 jednostki, Python liczy 1).
# Uzywamy WYLACZNIE emoji z zakresu BMP (U+0000-U+FFFF).
# Zweryfikowane telethoniem 2026-06-08: ⛔ ⚠️ ℹ️ ✅ — pogrubienia idealne.

STATE = {
    "firing":   "⛔",   # aktywny problem (BMP: U+26D4)
    "resolved": "✅",   # rozwiazane / przywrocone
}

# Waga (gdy chcemy rozroznic) — minimalne rozszerzenie
SEVERITY = {
    "critical": "⛔",   # U+26D4 BMP — NIE 🔥 (non-BMP psuje bold offset)
    "warn":     "⚠️",
    "warning":  "⚠️",
    "info":     "ℹ️",
    "ok":       "✅",
    "resolved": "✅",
}

# Pasek i punktor do ukladu (jak w czytelnych botach)
BULLET = "•"


def state_icon(state: str) -> str:
    return STATE.get((state or "firing").lower(), "🔥")


def severity_icon(severity: str) -> str:
    return SEVERITY.get((severity or "info").lower(), "ℹ️")
