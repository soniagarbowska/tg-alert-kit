# -*- coding: utf-8 -*-
"""tg-alert-kit — Telegram-first alert renderer z dynamicznymi przyciskami.

Telegram-first workflow: wszystko obsługiwane w Telegramie, zero linkow na zewnatrz.
Przyciski inline z callbackami, ikony per domena, MarkdownV2 card style.

Szybki start:
    from tg_alert_kit import render_alert, build_buttons
    from tg_alert_kit.sender import send_alert

    payload = render_alert(
        alert_id="M00042",
        monitor_type="sec",
        title="Nowe logowanie SSH",
        fields=[("Skad", "185.1.2.3"), ("Kiedy", "16:32 UTC"), ("Wynik", "SUKCES")],
        severity="warn",
    )
    # payload["text"]         -> MarkdownV2 do wyslania
    # payload["presentation"] -> OCPlatform presentation object (z przyciskami)
"""
from .render import render_alert, render_info
from .buttons import build_buttons, describe_callback
from .escape import md, bold, code, italic, mono_block
from .icons import severity_icon, domain_icon, action_icon

__version__ = "0.1.0"
__all__ = [
    "render_alert", "render_info",
    "build_buttons", "describe_callback",
    "md", "bold", "code", "italic", "mono_block",
    "severity_icon", "domain_icon", "action_icon",
    # sender importowany lazy:
    "send_alert", "send_via_ocplatform", "send_raw_telegram",
]


def __getattr__(name):
    """Lazy import sender (ma systemowe zaleznosci, nie chcemy go przy testach)."""
    if name in ("send_alert", "send_via_ocplatform", "send_raw_telegram"):
        from .sender import send_alert, send_via_ocplatform, send_raw_telegram
        g = {"send_alert": send_alert, "send_via_ocplatform": send_via_ocplatform,
             "send_raw_telegram": send_raw_telegram}
        return g[name]
    raise AttributeError(f"module 'tg_alert_kit' has no attribute {name!r}")
