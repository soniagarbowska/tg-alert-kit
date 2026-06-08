# -*- coding: utf-8 -*-
"""Bezpieczne escapowanie tekstu do Telegram MarkdownV2.

Telegram MarkdownV2 wymaga backslasha przed: _ * [ ] ( ) ~ ` > # + - = | { } . !
Wrapper md() chroni gotowe tokeny formatujace (**bold** etc.) — uzyj go
do fragmentow surowego tekstu (wartosci pol, opisy bledow) zanim wkleisz do szablonu.

Uzycie:
    from tg_alert_kit.escape import md, code, bold, mono

    msg = f"{bold('Status')}: {code('DOWN')}\n{bold('Blad')}: {md(error_text)}"
"""
from __future__ import annotations

_SPECIAL = r"\_*[]()~`>#+-=|{}.!"


def md(text: str) -> str:
    """Escapuje surowy tekst (wartosci, nazwy, opisy) do MarkdownV2."""
    out = []
    for ch in str(text):
        if ch in _SPECIAL:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def bold(text: str) -> str:
    """**bold** w MarkdownV2 — tekst wewnatrz tez escapowany."""
    return f"*{md(text)}*"


def italic(text: str) -> str:
    """_italic_ w MarkdownV2."""
    return f"_{md(text)}_"


def code(text: str) -> str:
    """`inline code` w MarkdownV2 — escapuje backtick i backslash wewnatrz."""
    inner = str(text).replace("\\", "\\\\").replace("`", "\\`")
    return f"`{inner}`"


def mono_block(text: str, lang: str = "") -> str:
    """```block kodu``` w MarkdownV2."""
    inner = str(text).replace("\\", "\\\\").replace("`", "\\`")
    return f"```{lang}\n{inner}\n```"


def link(label: str, url: str) -> str:
    """[tekst](url) w MarkdownV2."""
    return f"[{md(label)}]({md(url)})"


def sidebar_line(text: str, indent: bool = False) -> str:
    """Linia z paskiem bocznym ▎ (modern card look). Tekst NIE escapowany — podaj juz zformatowany."""
    prefix = "▎   " if indent else "▎ "
    return f"{prefix}{text}"
