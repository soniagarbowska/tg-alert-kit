# -*- coding: utf-8 -*-
"""Przyciski alertow jako KOMENDY po polsku.

Wzorzec: metalmatze/alertmanager-bot + ix-ai/alertmanager-telegram-bot.
Klik przycisku = bot dostaje komende (np. "/alert_pawel M00099"), agent ja
wykonuje. POTWIERDZONE ze dziala (test 2026-06-08, M00099).

ZERO zargonu: etykiety po polsku mowia wprost co robia.
Komendy: /alert_<akcja> <id>, obslugiwane przez agenta (Hugo/Victor).

Akcje (slownik, nie wymyslanie przy kazdym alercie):
    szczegoly  -> rozwin pelne info
    pawel      -> przekaz Pawlowi (sprawy techniczne/serwer)
    victor     -> przekaz do najmu
    pozniej    -> odloz, przypomnij za 2h
    zalatwione -> oznacz jako zalatwione
"""
from __future__ import annotations
from typing import Any


# Etykieta -> (komenda, styl). Styl: primary | secondary | success | danger
_ACTIONS = {
    "szczegoly":  ("Pokaz szczegoly",   "/alert_szczegoly",  "primary"),
    "pawel":      ("Wyslij do Pawla",   "/alert_pawel",      "danger"),
    "victor":     ("Przekaz do najmu",  "/alert_victor",     "primary"),
    "pozniej":    ("Odloz na pozniej",  "/alert_pozniej",    "secondary"),
    "zalatwione": ("Zalatwione",        "/alert_zalatwione", "success"),
}

# Ktore przyciski dla ktorego typu alertu (gotowe zestawy, nie wymyslanie)
_LAYOUTS = {
    "bezpieczenstwo": [["szczegoly", "pawel"], ["pozniej", "zalatwione"]],
    "sec":            [["szczegoly", "pawel"], ["pozniej", "zalatwione"]],
    "mail":           [["szczegoly"], ["pozniej", "zalatwione"]],
    "sejf":           [["szczegoly", "pawel"], ["zalatwione"]],
    "gate":           [["szczegoly", "pawel"], ["pozniej", "zalatwione"]],
    "najem":          [["szczegoly", "victor"], ["pozniej", "zalatwione"]],
    "_default":       [["szczegoly"], ["pozniej", "zalatwione"]],
}


def build_buttons(alert_type: str, alert_id: str) -> list[list[dict[str, Any]]]:
    """Zwraca rzedy przyciskow w formacie OCPlatform presentation.blocks[].buttons.

    Kazdy przycisk: {label, action:{type:"command", command:"/alert_x ID"}, style}
    """
    layout = _LAYOUTS.get((alert_type or "").lower(), _LAYOUTS["_default"])
    rows = []
    for row_keys in layout:
        row = []
        for key in row_keys:
            if key not in _ACTIONS:
                continue
            label, cmd, style = _ACTIONS[key]
            row.append({
                "label": label,
                "action": {"type": "command", "command": f"{cmd} {alert_id}"},
                "style": style,
            })
        if row:
            rows.append(row)
    return rows


def parse_command(text: str) -> dict[str, str]:
    """Parsuje przychodzaca komende '/alert_pawel M00099' -> {akcja, id}.

    Uzycie w agencie gdy przyjdzie klik:
        info = parse_command("/alert_pawel M00099")
        # {"akcja": "pawel", "id": "M00099"}
    """
    parts = text.strip().split()
    cmd = parts[0] if parts else ""
    akcja = cmd.replace("/alert_", "") if cmd.startswith("/alert_") else ""
    alert_id = parts[1] if len(parts) > 1 else ""
    return {"akcja": akcja, "id": alert_id}
