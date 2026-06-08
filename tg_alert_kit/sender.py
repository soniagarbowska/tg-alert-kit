# -*- coding: utf-8 -*-
"""Wysyłka alertów przez OCPlatform gateway (Telegram-first, z callbackami).

Dwie ścieżki:
  1. send_via_ocplatform() — HTTP do lokalnego gateway OCPlatform.
     Kliknięcie przycisku wraca jako callback do agenta (Hugo/Victor).
     To jedyna droga, która daje pełny Telegram-first handler workflow.

  2. send_raw_telegram() — stary fallback (raw urllib, BEZ callbacków).
     Zostawiamy dla kompatybilności / DRY_RUN. Nie używaj dla nowych alertów.

Architektura:
  notify_sonia.py (cron/skrypty)
      └─→ tg_alert_kit.sender.send_alert()
              ├─→ render.render_alert() → payload
              └─→ send_via_ocplatform() → OCPlatform gateway HTTP API
                      └─→ Telegram (z przyciskami inline)
                              └─→ klik Soni → callback → agent Hugo/Victor

Konfiguracja gateway:
  Endpoint: http://127.0.0.1:{GATEWAY_PORT}/api/v1/message/send
  Token:    z ~/.openclaw/ocplatform.json lub env OCPLATFORM_API_KEY
"""
from __future__ import annotations

import json
import os
import urllib.request
import urllib.error
from typing import Any

from .render import render_alert, render_info

_OC_CONFIG = "/home/sonia/.ocplatform/ocplatform.json"
_ENV_FILE  = "/home/sonia/.openclaw/.env"


def _read_env(key: str) -> str:
    v = os.environ.get(key)
    if v:
        return v.strip()
    try:
        for ln in open(_ENV_FILE):
            if ln.strip().startswith(key + "="):
                return ln.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return ""


def _gateway_endpoint() -> tuple[str, str]:
    """Zwraca (url, api_key) dla lokalnego gateway OCPlatform."""
    # Port z ocplatform.json lub domyślny
    port = "3001"
    api_key = ""
    try:
        cfg = json.load(open(_OC_CONFIG))
        port = str(cfg.get("gateway", {}).get("port", port))
        api_key = cfg.get("apiKey", "") or cfg.get("gateway", {}).get("apiKey", "")
    except Exception:
        pass
    if not api_key:
        api_key = _read_env("OCPLATFORM_API_KEY") or _read_env("OC_API_KEY")
    url = f"http://127.0.0.1:{port}/api/v1/message/send"
    return url, api_key


def _telegram_bot_token(bot: str = "hugo-works") -> str:
    try:
        cfg = json.load(open(_OC_CONFIG))
        return cfg["channels"]["telegram"]["accounts"][bot]["botToken"]
    except Exception:
        return ""


def _sonia_chat_id() -> str:
    return _read_env("SONIA_TELEGRAM_ID") or "8565653134"


def send_via_ocplatform(
    payload: dict[str, Any],
    agent_id: str = "hugo-works",
    dry: bool = False,
) -> dict[str, Any]:
    """Wysyła alert przez OCPlatform gateway — pełny Telegram-first z callbackami.

    Args:
        payload:  wynik render_alert() lub render_info()
        agent_id: "hugo-works" lub "victor-estate"
        dry:      jeśli True, zwraca payload bez wysyłki

    Returns:
        {"ok": bool, "method": "ocplatform", "preview": str, ...}
    """
    url, api_key = _gateway_endpoint()
    body = {
        "agentId":      agent_id,
        "channel":      "telegram",
        "target":       _sonia_chat_id(),
        "presentation": payload["presentation"],
    }

    preview = payload.get("text", "")[:200]
    if dry:
        return {"ok": True, "dry": True, "method": "ocplatform", "preview": preview, "body": body}

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp_body = resp.read().decode()
            return {"ok": True, "method": "ocplatform", "preview": preview, "resp": resp_body[:200]}
    except urllib.error.HTTPError as e:
        return {"ok": False, "method": "ocplatform", "error": f"HTTP {e.code}: {e.read().decode()[:200]}"}
    except Exception as e:
        return {"ok": False, "method": "ocplatform", "error": str(e)[:200]}


def send_raw_telegram(
    payload: dict[str, Any],
    bot: str = "hugo-works",
    dry: bool = False,
) -> dict[str, Any]:
    """Fallback: wysyłka raw Telegram API (BEZ callbacków — stary tryb).

    Tylko do kompatybilności / migracji. Dla nowych alertów użyj send_via_ocplatform().
    """
    token = _telegram_bot_token(bot)
    if not token:
        return {"ok": False, "method": "raw_telegram", "error": "brak botToken"}

    text = payload.get("text", "")
    parse_mode = payload.get("parse_mode", "MarkdownV2")
    chat_id = _sonia_chat_id()

    msg_body = json.dumps({
        "chat_id":    chat_id,
        "text":       text,
        "parse_mode": parse_mode,
    }).encode()

    preview = text[:200]
    if dry:
        return {"ok": True, "dry": True, "method": "raw_telegram", "preview": preview}

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        req = urllib.request.Request(url, data=msg_body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": True, "method": "raw_telegram", "preview": preview}
    except Exception as e:
        return {"ok": False, "method": "raw_telegram", "error": str(e)[:200]}


def send_alert(
    alert_id: str,
    monitor_type: str,
    title: str,
    fields: list[tuple[str, str]],
    severity: str = "warn",
    body_text: str | None = None,
    agent_id: str = "hugo-works",
    dry: bool = False,
) -> dict[str, Any]:
    """High-level: renderuje i wysyła alert w jednym wywołaniu.

    To jest główny punkt wejścia dla notify_sonia.py i cronów.
    """
    payload = render_alert(
        alert_id=alert_id,
        monitor_type=monitor_type,
        title=title,
        fields=fields,
        severity=severity,
        body_text=body_text,
    )
    result = send_via_ocplatform(payload, agent_id=agent_id, dry=dry)
    result["payload"] = payload
    return result
