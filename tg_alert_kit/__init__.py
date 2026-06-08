# -*- coding: utf-8 -*-
"""tg-alert-kit — alerty na Telegram, wzorzec metalmatze/alertmanager-bot.

Przyciski jako KOMENDY po polsku (potwierdzone ze dziala). Zero ACK, zero zargonu.

    from tg_alert_kit import render_alert, build_buttons, parse_command

    a = render_alert(
        alert_id="M00099",
        alert_type="bezpieczenstwo",
        title="Nowe logowanie na serwer",
        fields=[("Skad", "185.220.101.47"), ("Kiedy", "17:20"), ("Wynik", "udane")],
        severity="critical",
        note="Nieznany adres. Sprawdz czy to Ty.",
    )
    # a["presentation"] -> wysylasz przez narzedzie message (z przyciskami)
"""
from .render import render_alert
from .buttons import build_buttons, parse_command
from .icons import state_icon, severity_icon
from .card import card_png, card_html
from .atom import build_alert, PRESETS, preset

__version__ = "0.3.0"
__all__ = [
    # ATOM — glowne API (karta-obrazek + przyciski dla wielu typow)
    "build_alert", "PRESETS", "preset",
    # karta-obrazek (wzor #457)
    "card_png", "card_html",
    # przyciski-komendy
    "build_buttons", "parse_command",
    # tekstowy render (legacy/fallback)
    "render_alert",
    "state_icon", "severity_icon",
]
