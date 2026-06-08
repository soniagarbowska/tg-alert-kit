# -*- coding: utf-8 -*-
"""Testy renderera (wzorzec alertmanager-bot)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tg_alert_kit.render import render_alert


FIELDS = [("Skad", "185.220.101.47"), ("Kiedy", "17:20"), ("Wynik", "udane")]


class TestRenderAlert:
    def test_keys(self):
        a = render_alert("M00099", "bezpieczenstwo", "Nowe logowanie", FIELDS, "critical")
        for k in ("text", "presentation", "tone"):
            assert k in a

    def test_tone_maps(self):
        assert render_alert("x", "sec", "t", [], "critical")["tone"] == "danger"
        assert render_alert("x", "sec", "t", [], "warn")["tone"] == "warning"
        assert render_alert("x", "sec", "t", [], "resolved")["tone"] == "success"
        assert render_alert("x", "sec", "t", [], "info")["tone"] == "info"

    def test_id_in_text(self):
        a = render_alert("M00099", "mail", "Mail", [], "info")
        assert "M00099" in a["text"]

    def test_title_in_text(self):
        a = render_alert("M00001", "sec", "Nowe logowanie SSH", FIELDS, "warn")
        assert "Nowe logowanie SSH" in a["text"]

    def test_fields_in_text(self):
        a = render_alert("M00001", "sec", "Logowanie", FIELDS, "warn")
        assert "185.220.101.47" in a["text"]
        assert "Skad" in a["text"]

    def test_note_in_text(self):
        a = render_alert("M00001", "sec", "Alert", FIELDS, "warn", note="Sprawdz czy to Ty.")
        assert "Sprawdz czy to Ty." in a["text"]

    def test_presentation_has_text_and_buttons(self):
        a = render_alert("M00099", "bezpieczenstwo", "Alert", FIELDS, "critical")
        blocks = a["presentation"]["blocks"]
        assert blocks[0]["type"] == "text"
        assert any(b["type"] == "buttons" for b in blocks)

    def test_buttons_are_commands(self):
        a = render_alert("M00099", "bezpieczenstwo", "Alert", FIELDS, "critical")
        btn_blocks = [b for b in a["presentation"]["blocks"] if b["type"] == "buttons"]
        for b in btn_blocks:
            for btn in b["buttons"]:
                assert btn["action"]["type"] == "command"

    def test_severity_icon_critical(self):
        a = render_alert("M00001", "sec", "Alert", [], "critical")
        assert "⛔" in a["text"]  # BMP emoji, NIE 🔥 (non-BMP psuje bold offset w Telegramie)

    def test_severity_icon_resolved(self):
        a = render_alert("M00001", "sec", "Alert", [], "resolved")
        assert "✅" in a["text"]

    def test_text_under_telegram_limit(self):
        fields = [(f"Pole{i}", f"wartosc {i}") for i in range(10)]
        a = render_alert("M00001", "sec", "Dlugi", fields, "critical", note="x " * 50)
        assert len(a["text"]) <= 4096
