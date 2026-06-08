# -*- coding: utf-8 -*-
"""Kuratorska paleta ikon dla powiadomien na Telegramie.

Zasada: jedna ikona na semantyke, nigdy nie zmieniana. Ikona niesie znaczenie
(kolor/kategoria), tekst niesie tresc. Max 1-2 ikony na wiadomosc (naglowek + ew.
stopka), zeby bylo klasycznie, nie krzykliwie.

Zrodlo doboru: research Perplexity (sonar-pro, 2026-06-08) + wzorce Grafana/
UptimeRobot/Healthchecks/Sentry/BetterStack. Palety dobrane na "modern/classy",
nie domyslne kolka.
"""
from __future__ import annotations

# --- Severity (powaga) — glowna ikona nagłówka ---
SEVERITY = {
    "critical": "🚨",   # alarm, natychmiastowa uwaga
    "error":    "⛔",   # blad/awaria
    "warn":     "🔶",   # ostrzezenie/degradacja (ciekawsze niz zolte kolko)
    "warning":  "🔶",
    "ok":       "🟢",   # przywrocenie/sukces
    "recovery": "🟢",
    "info":     "🔷",   # neutralna informacja (ciekawsze niz ℹ️)
}

# --- Domena/typ — opcjonalna druga ikona przy nagłówku lub w polu ---
DOMAIN = {
    "sec":      "🛡️",   # bezpieczenstwo serwera (Hugo)
    "security": "🛡️",
    "mail":     "✉️",   # poczta
    "sejf":     "🔐",   # sejf/sekrety
    "safe":     "🔐",
    "gate":     "🚧",   # gate/kontrola dostepu
    "najem":    "🏠",   # zarzadzanie najmem (Victor)
    "rent":     "🏠",
    "skil":     "🧩",   # przeglad skilli
    "skill":    "🧩",
    "money":    "💰",   # pieniadze/faktury
    "invoice":  "🧾",
    "deadline": "⏳",   # termin
    "deploy":   "🚀",
    "system":   "⚙️",
    "question": "❓",
}

# --- Drobne symbole do akcji na przyciskach ---
ACTION_ICON = {
    "ack":       "✅",
    "silence":   "🔕",
    "expand":    "🔎",
    "raw":       "📄",
    "escalate":  "📣",
    "snooze":    "💤",
    "details":   "🔎",
    "resolve":   "🟢",
    "reply":     "↩️",
}

# Pasek boczny i punktor do "karty" (subtelny, modern look)
SIDEBAR = "▎"
BULLET = "•"


def severity_icon(severity: str) -> str:
    return SEVERITY.get((severity or "info").lower(), SEVERITY["info"])


def domain_icon(domain: str | None) -> str:
    if not domain:
        return ""
    return DOMAIN.get(domain.lower(), "")


def action_icon(key: str) -> str:
    return ACTION_ICON.get((key or "").lower(), "")
