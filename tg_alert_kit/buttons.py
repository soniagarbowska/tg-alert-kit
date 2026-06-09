# -*- coding: utf-8 -*-
"""Przyciski alertow jako KOMENDY po polsku.

Wzorzec: metalmatze/alertmanager-bot. Klik = bot dostaje komende, Hugo wykonuje.
POTWIERDZONE ze dziala (test 2026-06-08, M00099).

ZASADA: alerty obsluguja TYLKO Sonia i Hugo. Zadnego "wyslij do Pawla/Victora".
Wszystko zalatwiamy miedzy soba w czacie.

ZASADA 2: wiadomosc zawiera PELNE info od razu. Zadnego 'pokaz szczegoly' —
wszystko co wazne jest w tekscie alertu. Przyciski to tylko REALNE akcje.

Akcje:
    to_ja      -> Sonia potwierdza ze to bylo Jej dzialanie (bezpieczenstwo)
    nie_ja     -> Sonia mowi ze to NIE Ona -> Hugo sprawdza glebiej
    pozniej    -> odloz, Hugo przypomni za 2h
    zalatwione -> oznacz jako zalatwione
"""
from __future__ import annotations
from typing import Any


# Etykieta -> (tekst na przycisku, komenda, styl)
# Emoji-prefiks bo Telegram nie koloruje inline-buttonow (style zlewa sie wizualnie).
_ACTIONS = {
    "to_ja":      ("✅ To byłam ja",     "/alert_toja",       "success"),
    "nie_ja":     ("🔴 To nie ja",       "/alert_nieja",      "danger"),
    "pozniej":    ("⏰ Później",          "/alert_pozniej",    "secondary"),
    "zalatwione": ("✅ Załatwione",        "/alert_zalatwione", "success"),
}

# Zestawy per typ alertu — tylko REALNE akcje miedzy Sonia a Hugo
_LAYOUTS = {
    "bezpieczenstwo": [["to_ja", "nie_ja"], ["pozniej"]],
    "sec":            [["to_ja", "nie_ja"], ["pozniej"]],
    "mail":           [["pozniej", "zalatwione"]],
    "sejf":           [["pozniej", "zalatwione"]],
    "gate":           [["pozniej", "zalatwione"]],
    "najem":          [["pozniej", "zalatwione"]],
    "_default":       [["pozniej", "zalatwione"]],
}


def build_buttons(alert_type: str, alert_id: str) -> list[list[dict[str, Any]]]:
    """Zwraca rzedy przyciskow (format OCPlatform presentation.blocks[].buttons)."""
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
    """Parsuje '/alert_pozniej M00099' -> {akcja, id}."""
    parts = text.strip().split()
    cmd = parts[0] if parts else ""
    akcja = cmd.replace("/alert_", "") if cmd.startswith("/alert_") else ""
    alert_id = parts[1] if len(parts) > 1 else ""
    return {"akcja": akcja, "id": alert_id}
