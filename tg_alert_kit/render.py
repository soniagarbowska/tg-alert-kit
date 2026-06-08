# -*- coding: utf-8 -*-
"""Renderer alertow — layout wzorowany na metalmatze/alertmanager-bot.

Ich szablon (default.tmpl):
    🔥 <b>{alertname}</b> 🔥        (firing)  /  ✅ ... ✅ (resolved)
    <b>Labels:</b>
        key: value
    <b>Duration:</b> ...

My: ten sam uklad, po polsku, + nasze przyciski-komendy.

Output:
    {
        "text":         str (czysty, do podgladu),
        "presentation": dict (OCPlatform: tekst + przyciski-komendy),
        "tone":         str,
    }
"""
from __future__ import annotations
import time as _time
from typing import Any

from .icons import state_icon, severity_icon, BULLET
from .buttons import build_buttons


_TONE = {
    "critical": "danger",
    "firing":   "danger",
    "warn":     "warning",
    "warning":  "warning",
    "info":     "info",
    "ok":       "success",
    "resolved": "success",
}

# Slowo wagi w naglowku (jak STATUS w Grafana/alertmanager, po polsku)
_SEV_LABEL = {
    "critical": "KRYTYCZNE",
    "firing":   "KRYTYCZNE",
    "warn":     "UWAGA",
    "warning":  "UWAGA",
    "info":     "INFORMACJA",
    "ok":       "OK",
    "resolved": "ROZWIAZANE",
}

# Pola ktore warto pokazac monospace (dane techniczne) — heurystyka po nazwie klucza
_MONO_KEYS = ("ip", "adres", "host", "port", "login", "uzytkownik", "user",
              "plik", "sciezka", "path", "url", "domena", "hash", "id")


def _is_mono(key: str) -> bool:
    k = (key or "").lower()
    return any(tok in k for tok in _MONO_KEYS)


def render_alert(
    alert_id: str,
    alert_type: str,
    title: str,
    fields: list[tuple[str, str]],
    severity: str = "warn",
    note: str | None = None,
) -> dict[str, Any]:
    """Renderuje alert (wzorzec alertmanager-bot, po polsku, z przyciskami-komendami).

    Args:
        alert_id:   "M00099"
        alert_type: "bezpieczenstwo" | "mail" | "sejf" | "gate" | "najem"
        title:      krotki tytul, np. "Nowe logowanie na serwer"
        fields:     [(klucz, wartosc)] — jak Labels w alertmanager-bot
        severity:   "critical" | "warn" | "info" | "resolved"
        note:       opcjonalna 1-2 zdaniowa uwaga pod polami
    """
    sev = (severity or "warn").lower()
    tone = _TONE.get(sev, "warning")
    icon = severity_icon(sev)
    sev_label = _SEV_LABEL.get(sev, "UWAGA")
    when = _time.strftime("%H:%M")

    # Layout wzorowany na Grafana/alertmanager-bot:
    #   ICON **TYTUL**
    #   waga - data techniczna w naglowku
    #   (pusta linia)
    #   pola: bullet **Klucz:** wartosc  (dane techniczne w `monospace`)
    #   (pusta) > uwaga jako cytat
    #   (pusta) stopka: zegar + ID
    # Tylko emoji/znaki BMP (non-BMP psuje offsety pogrubien).
    lines = [f"{icon}  **{title}**"]
    lines.append(f"{sev_label}")
    if fields:
        lines.append("")
    for key, val in (fields or []):
        shown = f"`{val}`" if _is_mono(key) else val
        lines.append(f"{BULLET} **{key}:** {shown}")
    if note:
        lines.append("")
        lines.append(f"> {note}")
    lines.append("")
    lines.append(f"⏱ {when}  ·  {alert_id}")
    text = "\n".join(lines)

    blocks: list[dict] = [{"type": "text", "text": text}]
    for row in build_buttons(alert_type, alert_id):
        blocks.append({"type": "buttons", "buttons": row})

    return {
        "text": text,
        "presentation": {"tone": tone, "blocks": blocks},
        "tone": tone,
        "_alert_id": alert_id,
        "_type": alert_type,
        "_severity": sev,
    }
