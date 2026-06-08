# -*- coding: utf-8 -*-
"""Ikony alertow — wzorzec metalmatze/alertmanager-bot (653 gwiazdki).

Tamten bot uzywa DWOCH stanow: firing i resolved. Prosto, czytelnie.
My rozszerzamy minimalnie o wage (krytyczny/uwaga/info), reszta jak u nich.

Zero wymyslania kolorow tla — to tylko znaki w tekscie.
"""
from __future__ import annotations

# Stan alertu — dokladnie jak alertmanager-bot
STATE = {
    "firing":   "🔥",   # aktywny problem
    "resolved": "✅",   # rozwiazane / przywrocone
}

# Waga (gdy chcemy rozroznic) — minimalne rozszerzenie
SEVERITY = {
    "critical": "🔥",   # jak firing — najwyzszy
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
