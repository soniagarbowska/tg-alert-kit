# -*- coding: utf-8 -*-
"""Dynamiczne układy przycisków inline per projekt/monitor.

Zasada Telegram-first: ZERO linków url — wszystko to callback_data.
Kliknięcie wraca do agenta jako callback z wartością np. "ack:M00042".

Schemat przycisku OCPlatform (presentation.blocks):
    {
        "label": "✅ Ack",
        "action": {"type": "callback", "value": "ack:M00042"},
        "style": "success"   # primary | secondary | success | danger
    }

UKŁADY: każdy projekt ma własny zestaw rzędów. Funkcja build_buttons()
dynamicznie dobiera układ na podstawie (monitor_type, severity, alert_id)
i filtruje przyciski nieadekwatne dla danej wagi alertu.
"""
from __future__ import annotations
from typing import Any


# Baza szablonów: klucz = monitor type (np. "sec", "mail", "sejf").
# Każdy rząd to lista przycisków. Zmienne {id} są podmieniane przy build.
_LAYOUTS: dict[str, list[list[dict]]] = {

    "sec": [
        [
            {"label": "🔎 Rozwiń szczegóły", "value": "expand:{id}", "style": "primary"},
            {"label": "📄 Surowe dane",       "value": "raw:{id}",    "style": "secondary"},
        ],
        [
            {"label": "✅ Ack",               "value": "ack:{id}",         "style": "success"},
            {"label": "🔕 Wycisz 1h",         "value": "silence:60:{id}",  "style": "secondary"},
        ],
        # tylko critical:
        [{"label": "📣 Eskaluj do Pawła",     "value": "escalate:{id}",    "style": "danger",
          "_min_severity": "critical"}],
    ],

    "mail": [
        [
            {"label": "🔎 Rozwiń mail",       "value": "expand:{id}", "style": "primary"},
            {"label": "✅ Ack",               "value": "ack:{id}",    "style": "success"},
        ],
        [
            {"label": "↩️ Odpowiedz",         "value": "reply:{id}",       "style": "secondary"},
            {"label": "💤 Pomiń",             "value": "snooze:{id}",      "style": "secondary"},
        ],
    ],

    "sejf": [
        [
            {"label": "🔎 Rozwiń",            "value": "expand:{id}", "style": "primary"},
            {"label": "✅ Ack",               "value": "ack:{id}",    "style": "success"},
        ],
        [{"label": "📣 Eskaluj",              "value": "escalate:{id}", "style": "danger",
          "_min_severity": "warn"}],
    ],

    "gate": [
        [
            {"label": "🔎 Rozwiń",            "value": "expand:{id}",  "style": "primary"},
            {"label": "⚙️ Status gateway",    "value": "gate_status",  "style": "secondary"},
        ],
        [
            {"label": "✅ Ack",               "value": "ack:{id}",           "style": "success"},
            {"label": "🔕 Wycisz 30m",        "value": "silence:30:{id}",    "style": "secondary"},
        ],
    ],

    "najem": [
        [
            {"label": "🔎 Rozwiń",            "value": "expand:{id}",   "style": "primary"},
            {"label": "✅ Wziąłem do wiedzy", "value": "ack:{id}",      "style": "success"},
        ],
        [
            {"label": "📣 Eskaluj do Victora","value": "escalate:{id}", "style": "danger",
             "_min_severity": "critical"},
        ],
    ],

    "skil": [
        [
            {"label": "🔎 Rozwiń raport",     "value": "expand:{id}",  "style": "primary"},
            {"label": "✅ Ack",               "value": "ack:{id}",     "style": "success"},
        ],
    ],

    # fallback — każdy nieznany monitor type
    "_default": [
        [
            {"label": "🔎 Rozwiń",            "value": "expand:{id}", "style": "primary"},
            {"label": "✅ Ack",               "value": "ack:{id}",    "style": "success"},
        ],
        [
            {"label": "📣 Eskaluj",           "value": "escalate:{id}", "style": "danger",
             "_min_severity": "critical"},
        ],
    ],
}

_SEVERITY_ORDER = {"info": 0, "warn": 1, "warning": 1, "critical": 2, "error": 2}


def _severity_level(s: str) -> int:
    return _SEVERITY_ORDER.get((s or "info").lower(), 0)


def build_buttons(
    monitor_type: str,
    alert_id: str,
    severity: str = "warn",
) -> list[list[dict[str, Any]]]:
    """Zwraca listę rzędów przycisków w formacie OCPlatform presentation.blocks.

    Każdy element to lista przycisków jednego rzędu:
        [[{label, action:{type,value}, style}, ...], ...]

    Przyciski z _min_severity są pomijane jeśli severity < próg.
    """
    layout = _LAYOUTS.get((monitor_type or "").lower(), _LAYOUTS["_default"])
    sev = _severity_level(severity)
    rows = []
    for row_tmpl in layout:
        row = []
        for btn in row_tmpl:
            min_sev = _severity_level(btn.get("_min_severity", "info"))
            if sev < min_sev:
                continue
            value = btn["value"].replace("{id}", str(alert_id))
            row.append({
                "label": btn["label"],
                "action": {"type": "callback", "value": value},
                "style": btn.get("style", "secondary"),
            })
        if row:
            rows.append(row)
    return rows


def describe_callback(value: str) -> dict[str, str]:
    """Parsuje callback value z powrotem na (action, alert_id, extra).

    Uzycie w handlerze:
        info = describe_callback(callback_data)
        # info = {"action": "ack", "alert_id": "M00042", "extra": ""}
        # info = {"action": "silence", "alert_id": "M00042", "extra": "60"}
    """
    parts = value.split(":")
    action = parts[0] if parts else "unknown"
    if action in ("silence",) and len(parts) >= 3:
        return {"action": action, "extra": parts[1], "alert_id": parts[2]}
    elif action == "gate_status":
        return {"action": action, "extra": "", "alert_id": ""}
    else:
        return {"action": action, "extra": "", "alert_id": parts[1] if len(parts) > 1 else ""}
