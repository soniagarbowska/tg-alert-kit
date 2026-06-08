# -*- coding: utf-8 -*-
"""Przepisy powiadomien — rozne UKLADY w jednym STYLU (#439).

Kazdy przepis to funkcja: dane -> lista klockow (z text_alert).
Styl jest wspolny (compose), uklad/dane dowolne per typ.

Dodanie NOWEGO powiadomienia:
  1) napisz funkcje przepisu (dane -> bloki) tutaj,
  2) zarejestruj w RECIPES pod nazwa typu,
  3) ew. dodaj layout przyciskow w buttons.py.
To wszystko.
"""
from __future__ import annotations
import time
from typing import Any, Callable

from .text_alert import compose, b, m, i, SEV_ICON, SEV_WORD, TOPIC_ICON


def _clock() -> str:
    return time.strftime("%H:%M")


# ---------------------------------------------------------------------------
# PRZEPIS 1: alert pojedynczy (bezpieczenstwo / sejf / gate) — klucz:wartosc
# ---------------------------------------------------------------------------
def recipe_alert(
    title: str,
    fields: list[tuple],
    severity: str = "warn",
    note: str | None = None,
    badge: str | None = None,
    alert_id: str = "",
) -> list[tuple]:
    sev = (severity or "warn").lower()
    icon = SEV_ICON.get(sev, "⚠️")
    word = SEV_WORD.get(sev, "UWAGA")
    sub = word + (f"  ·  {badge}" if badge else "")
    blocks: list[tuple] = [
        ("header", icon, title, sub),
        ("divider",),
        ("space",),
    ]
    for f in fields:
        blocks.append(("field",) + tuple(f))
    if note:
        blocks += [("space",), ("note", note)]
    foot = f"⏱ {_clock()}" + (f"  ·  {alert_id}" if alert_id else "")
    blocks.append(("footer", foot))
    return blocks


# ---------------------------------------------------------------------------
# PRZEPIS 2: digest/podsumowanie (poczta, wiele pozycji) — wzor DOKLADNIE z #439
# ---------------------------------------------------------------------------
def recipe_digest(
    title: str,
    items: list[dict],
    subtitle: str | None = None,
    footer: str | None = None,
    icon: str | None = None,
    topic: str = "mail",
) -> list[tuple]:
    """items: [{color, name, tag, fields:[(k,v)], note, spoiler}]

    icon: nadpisuje ikone naglowka. Jak None -> BMP-owa ikona wg `topic`
          (bezpieczna dla pogrubien; 📥 non-BMP psuje bold, wiec nie domyslnie).
    """
    if icon is None:
        icon = TOPIC_ICON.get((topic or "mail").lower(), "✉️")
    n = len(items)
    sub = subtitle or f"{n} {'nowa wiadomosc' if n==1 else 'nowe wiadomosci'}  ·  ⏱ {_clock()}"
    blocks: list[tuple] = [
        ("header", icon, title, sub),
        ("divider",),
    ]
    for it in items:
        blocks.append(("space",))
        blocks.append(("entry", it.get("color", "white"),
                       it.get("name", ""), it.get("tag")))
        for f in it.get("fields", []):
            blocks.append(("field",) + tuple(f))
        if it.get("note"):
            blocks.append(("note", it["note"]))
        if it.get("spoiler"):
            blocks.append(("spoiler", it["spoiler"]))
    if footer:
        blocks.append(("footer", footer))
    else:
        blocks += [("divider",)]
    return blocks


# ---------------------------------------------------------------------------
# PRZEPIS 3: status / zmiana stanu (krotka, 1-2 pola) — np. monitor up/down
# ---------------------------------------------------------------------------
def recipe_status(
    title: str,
    state_word: str,
    severity: str = "info",
    fields: list[tuple] | None = None,
    note: str | None = None,
    alert_id: str = "",
) -> list[tuple]:
    sev = (severity or "info").lower()
    icon = SEV_ICON.get(sev, "ℹ️")
    blocks: list[tuple] = [
        ("header", icon, title, state_word),
    ]
    if fields:
        blocks.append(("space",))
        for f in fields:
            blocks.append(("field",) + tuple(f))
    if note:
        blocks += [("space",), ("note", note)]
    foot = f"⏱ {_clock()}" + (f"  ·  {alert_id}" if alert_id else "")
    blocks.append(("footer", foot))
    return blocks


# ---------------------------------------------------------------------------
# REJESTR przepisow: typ powiadomienia -> funkcja przepisu
# ---------------------------------------------------------------------------
RECIPES: dict[str, Callable[..., list[tuple]]] = {
    "alert":   recipe_alert,
    "digest":  recipe_digest,
    "status":  recipe_status,
}


def render_recipe(recipe: str, **kwargs) -> str:
    """Wywoluje przepis i sklada gotowy tekst w stylu #439."""
    fn = RECIPES.get(recipe)
    if not fn:
        raise ValueError(f"nieznany przepis: {recipe}")
    return compose(fn(**kwargs))
