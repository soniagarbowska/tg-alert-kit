# -*- coding: utf-8 -*-
"""Testy atomu tekstowego (styl #439) — klocki, przepisy, notify."""
from tg_alert_kit import notify, compose, render_recipe
from tg_alert_kit.text_alert import SEV_ICON, TOPIC_ICON, DOT


def test_blocks_compose_basic():
    txt = compose([
        ("header", "⛔", "Tytul", "KRYTYCZNE"),
        ("divider",),
        ("field", "Adres IP", "1.2.3.4"),
        ("note", "uwaga"),
        ("footer", "stopka"),
    ])
    assert "**Tytul**" in txt
    assert "⛔" in txt
    assert "**Adres IP:**" in txt
    assert "`1.2.3.4`" in txt          # auto-monospace dla IP
    assert "> uwaga" in txt
    assert "_stopka_" in txt           # kursywa w stopce


def test_field_mono_auto_and_force():
    # auto: 'Cena' jest w hintach -> mono
    assert "`9 zl`" in compose([("field", "Cena", "9 zl")])
    # plain wymuszony
    assert "`x`" not in compose([("field", "Cena", "x", "plain")])
    # mono wymuszony na polu spoza hintow
    assert "`abc`" in compose([("field", "Cokolwiek", "abc", "mono")])


def test_header_icons_are_bmp():
    # wszystkie ikony wagi i tematyczne musza byc BMP (<= U+FFFF na 1. znaku bazowym)
    for ic in list(SEV_ICON.values()) + list(TOPIC_ICON.values()):
        base = ic[0]
        assert ord(base) <= 0xFFFF, f"ikona {ic!r} nie jest BMP (psuje pogrubienia)"


def test_notify_alert():
    n = notify("alert", title="Logowanie",
               fields=[("Adres IP", "1.2.3.4"), ("Czas", "18:00")],
               severity="critical", buttons_for="sec", alert_id="M1",
               note="uwaga")
    assert "**Logowanie**" in n["text"]
    assert n["tone"] == "danger"
    labels = [b["label"] for r in n["buttons"] for b in r]
    assert "To bylam ja" in labels


def test_notify_digest_matches_439_structure():
    n = notify("digest", title="Podsumowanie poczty",
        items=[
            {"color": "orange", "name": "Allegro", "tag": "oferta",
             "fields": [("Cena", "1 249 zl")], "note": "wskazowka"},
            {"color": "green", "name": "mBank", "tag": "przelew",
             "fields": [("Kwota", "+3 200 zl")]},
            {"color": "white", "name": "Newsletter", "spoiler": "ukryte"},
        ],
        footer="Skrzynka sonia@garbowska.pl", buttons_for="mail", alert_id="M2")
    t = n["text"]
    assert "**Podsumowanie poczty**" in t
    assert DOT["orange"] in t and DOT["green"] in t and DOT["white"] in t
    assert "||ukryte||" in t            # spoiler
    assert "> wskazowka" in t           # cytat
    assert "`1 249 zl`" in t            # mono kwota
    assert "_Skrzynka sonia@garbowska.pl_" in t


def test_notify_status():
    n = notify("status", title="Strona", state_word="PRZYWROCONA",
               severity="ok", fields=[("Przerwa", "4 min")], alert_id="M3")
    assert "**Strona**" in n["text"]
    assert "PRZYWROCONA" in n["text"]
    assert n["tone"] == "success"


def test_unknown_recipe_raises():
    import pytest
    with pytest.raises(ValueError):
        render_recipe("nie-ma-takiego", title="x")
