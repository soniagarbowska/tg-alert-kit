# -*- coding: utf-8 -*-
"""Renderer alertów → gotowy payload OCPlatform presentation + tekst MarkdownV2.

Wzorzec: header(ikona+domena+tytuł) → pola klucz/wartość (▎ card) → stopka
z ID i czasem. Osobno: przyciski inline z buttons.py.

Render output:
    {
        "text":         str,   # MarkdownV2, do wysylki raw Telegram API
        "presentation": dict,  # OCPlatform message tool presentation object
        "tone":         str,   # info | success | warning | danger | neutral
        "parse_mode":   "MarkdownV2",
    }
"""
from __future__ import annotations

import datetime
from typing import Any

from .icons import severity_icon, domain_icon, SIDEBAR, BULLET
from .escape import md, bold, code
from .buttons import build_buttons


_TONE_MAP = {
    "critical": "danger",
    "error":    "danger",
    "warn":     "warning",
    "warning":  "warning",
    "ok":       "success",
    "recovery": "success",
    "info":     "info",
}

_SEVERITY_LABELS = {
    "critical": "KRYTYCZNY",
    "error":    "BŁĄD",
    "warn":     "UWAGA",
    "warning":  "UWAGA",
    "ok":       "OK",
    "recovery": "PRZYWRÓCONO",
    "info":     "INFO",
}


def _now_str() -> str:
    return datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC")


def render_alert(
    alert_id: str,
    monitor_type: str,
    title: str,
    fields: list[tuple[str, str]],
    severity: str = "warn",
    body_text: str | None = None,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Renderuje alert do payload-u gotowego do wysylki.

    Args:
        alert_id:     np. "M00042"
        monitor_type: np. "sec", "mail", "sejf", "gate", "najem", "skil"
        title:        krotki tytul, np. "Nowe logowanie SSH", "Mail od Jana"
        fields:       lista (klucz, wartosc) — max 6-8 par
        severity:     "critical" | "warn" | "ok" | "info"
        body_text:    opcjonalny dodatkowy blok tekstu pod polami
        timestamp:    np. "16:32 UTC"; domyslnie teraz

    Returns:
        dict z kluczami: text, presentation, tone, parse_mode
    """
    sev = (severity or "info").lower()
    tone = _TONE_MAP.get(sev, "info")
    sev_icon = severity_icon(sev)
    dom_icon = domain_icon(monitor_type)
    sev_label = _SEVERITY_LABELS.get(sev, sev.upper())
    ts = timestamp or _now_str()

    # --- Naglowek ---
    # np. "🔶 · 🛡️ SEC · Nowe logowanie SSH"
    domain_part = f"{dom_icon} {monitor_type.upper()} · " if dom_icon else f"{monitor_type.upper()} · "
    header_plain = f"{sev_icon}  {domain_part}{title}"

    # --- Pola klucz/wartość (▎ card style) ---
    field_lines_md = []
    field_lines_plain = []
    for key, val in (fields or []):
        key_str = str(key)
        val_str = str(val)
        # wyrownanie: klucz do 12 znakow
        key_padded = key_str.ljust(12)
        field_lines_md.append(f"{SIDEBAR} {bold(key_padded)}  {md(val_str)}")
        field_lines_plain.append(f"{SIDEBAR} {key_padded}  {val_str}")

    # --- Blok dodatkowy (body_text) ---
    body_lines_md = []
    if body_text:
        body_lines_md.append("")
        for line in body_text.strip().splitlines():
            body_lines_md.append(f"{SIDEBAR} {BULLET} {md(line)}")

    # --- Stopka ---
    footer_md = f"_{md(alert_id)} · {md(ts)}_"
    footer_plain = f"{alert_id} · {ts}"

    # --- Sklad MarkdownV2 ---
    parts_md = [f"*{md(header_plain)}*"]
    if field_lines_md:
        parts_md.append("")
        parts_md.extend(field_lines_md)
    if body_lines_md:
        parts_md.extend(body_lines_md)
    parts_md.append("")
    parts_md.append(footer_md)
    text_md = "\n".join(parts_md)

    # --- Presentation (OCPlatform format, Telegram-native) ---
    blocks: list[dict] = []

    # Blok tekstowy (header + pola)
    plain_parts = [header_plain, ""]
    plain_parts.extend(field_lines_plain)
    if body_text:
        plain_parts.append("")
        for line in body_text.strip().splitlines():
            plain_parts.append(f"{SIDEBAR} {BULLET} {line}")
    plain_parts.append("")
    plain_parts.append(footer_plain)

    blocks.append({
        "type": "text",
        "text": "\n".join(plain_parts),
    })

    # Przyciski inline
    btn_rows = build_buttons(monitor_type, alert_id, sev)
    for row in btn_rows:
        blocks.append({
            "type": "buttons",
            "buttons": row,
        })

    presentation = {
        "tone":   tone,
        "blocks": blocks,
    }

    return {
        "text":         text_md,
        "presentation": presentation,
        "tone":         tone,
        "parse_mode":   "MarkdownV2",
        "_alert_id":    alert_id,
        "_monitor":     monitor_type,
        "_severity":    sev,
    }


def render_info(
    alert_id: str,
    monitor_type: str,
    about: str,
    timestamp: str | None = None,
) -> dict[str, Any]:
    """Uproszczony render dla severity=info (rutynowe, bez opcji).

    Zwraca ten sam format co render_alert, ale minimal (1 przycisk Ack).
    """
    ts = timestamp or _now_str()
    dom_icon = domain_icon(monitor_type)
    domain_part = f"{dom_icon} {monitor_type.upper()} · " if dom_icon else f"{monitor_type.upper()} · "
    header = f"🔷  {domain_part}INFO"

    text_plain = f"{header}\n\n{SIDEBAR} {about}\n\n{alert_id} · {ts}"
    text_md = f"*{md(header)}*\n\n{SIDEBAR} {md(about)}\n\n_{md(alert_id)} · {md(ts)}_"

    presentation = {
        "tone": "info",
        "blocks": [
            {"type": "text", "text": text_plain},
            {"type": "buttons", "buttons": [
                {"label": "🔎 Rozwiń", "action": {"type": "callback", "value": f"expand:{alert_id}"}, "style": "primary"},
                {"label": "✅ Ack",    "action": {"type": "callback", "value": f"ack:{alert_id}"},    "style": "success"},
            ]},
        ],
    }

    return {
        "text":         text_md,
        "presentation": presentation,
        "tone":         "info",
        "parse_mode":   "MarkdownV2",
        "_alert_id":    alert_id,
        "_monitor":     monitor_type,
        "_severity":    "info",
    }
