# -*- coding: utf-8 -*-
"""notify() — glowne API. Typ + dane -> gotowy tekst (styl #439) + przyciski.

    from tg_alert_kit import notify

    # alert bezpieczenstwa
    n = notify("alert",
        title="Nowe logowanie na serwer",
        fields=[("Adres IP","185.220.101.47"),("Lokalizacja","Niemcy (Tor)"),
                ("Czas","18:00"),("Uzytkownik","sonia"),("Wynik","udane")],
        severity="critical", badge="SSH",
        note="Nieznany adres z sieci Tor. Jesli to nie Ty - dzialaj od razu.",
        alert_id="M00099", buttons_for="sec")

    # n["text"]         -> tekst w stylu #439 (wyslij jako message text)
    # n["presentation"] -> {tone, blocks:[buttons...]}
    # n["tone"], n["buttons"]

Wysylka (przez narzedzie message agenta):
    message(action=send, target=..., message=n["text"], presentation=n["presentation"])
"""
from __future__ import annotations
from typing import Any

import inspect

from .presets import render_recipe, RECIPES
from .buttons import build_buttons
from .text_alert import SEV_ICON

_TONE = {
    "critical": "danger", "firing": "danger",
    "warn": "warning", "warning": "warning",
    "info": "info", "ok": "success", "resolved": "success",
}


def notify(
    recipe: str,
    *,
    buttons_for: str | None = None,
    alert_id: str = "",
    severity: str | None = None,
    **kwargs,
) -> dict[str, Any]:
    """Buduje powiadomienie tekstowe w stylu #439 + przyciski.

    recipe:      "alert" | "digest" | "status" (z presets.RECIPES)
    buttons_for: typ dla zestawu przyciskow ("sec","mail","sejf","gate","najem"...).
                 Jak None -> bez przyciskow.
    alert_id:    M-numer (do przyciskow i stopki).
    severity:    nadpisuje wage (kolor/ikona); jak None -> z danych przepisu.
    kwargs:      argumenty przepisu (title, fields, items, note, ...).
    """
    # przekaz alert_id/severity TYLKO do przepisow ktore te argumenty przyjmuja
    fn = RECIPES.get(recipe)
    accepted = set(inspect.signature(fn).parameters) if fn else set()
    if alert_id and "alert_id" in accepted and "alert_id" not in kwargs:
        kwargs["alert_id"] = alert_id
    if severity and "severity" in accepted and "severity" not in kwargs:
        kwargs["severity"] = severity

    text = render_recipe(recipe, **kwargs)

    sev = (severity or kwargs.get("severity") or "info").lower()
    tone = _TONE.get(sev, "info")

    blocks: list[dict] = []
    rows: list = []
    if buttons_for:
        rows = build_buttons(buttons_for, alert_id)
        blocks = [{"type": "buttons", "buttons": row} for row in rows]

    return {
        "text": text,
        "presentation": {"tone": tone, "blocks": blocks},
        "buttons": rows,
        "tone": tone,
        "severity": sev,
        "recipe": recipe,
        "id": alert_id,
    }
