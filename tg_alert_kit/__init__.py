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
from .notify import notify
from .presets import render_recipe, RECIPES, recipe_alert, recipe_digest, recipe_status
from .text_alert import compose, b, m, i, SEV_ICON, SEV_WORD, DOT
from .render import render_alert
from .buttons import build_buttons, parse_command
from .icons import state_icon, severity_icon
from .card import card_png, card_html
from .atom import build_alert, PRESETS, preset

__version__ = "0.4.0"
__all__ = [
    # GLOWNE API — styl tekstowy #439, adaptowalny
    "notify",
    # przepisy (rozne uklady, jeden styl)
    "render_recipe", "RECIPES", "recipe_alert", "recipe_digest", "recipe_status",
    # klocki + helpery stylu
    "compose", "b", "m", "i", "SEV_ICON", "SEV_WORD", "DOT",
    # przyciski-komendy
    "build_buttons", "parse_command",
    # karta-obrazek (wariant alternatywny)
    "build_alert", "card_png", "card_html", "PRESETS", "preset",
    # legacy
    "render_alert", "state_icon", "severity_icon",
]
