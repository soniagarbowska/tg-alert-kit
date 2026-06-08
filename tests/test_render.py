# -*- coding: utf-8 -*-
"""Testy renderera alertów."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tg_alert_kit.render import render_alert, render_info


SAMPLE_FIELDS = [
    ("Skąd", "185.1.2.3"),
    ("Kiedy", "16:32 UTC"),
    ("Wynik", "SUKCES"),
]


class TestRenderAlert:
    def test_returns_required_keys(self):
        p = render_alert("M00042", "sec", "Nowe logowanie", SAMPLE_FIELDS, "warn")
        for key in ("text", "presentation", "tone", "parse_mode"):
            assert key in p

    def test_parse_mode_is_markdownv2(self):
        p = render_alert("M00042", "sec", "Test", [], "info")
        assert p["parse_mode"] == "MarkdownV2"

    def test_tone_maps_correctly(self):
        assert render_alert("x", "sec", "t", [], "critical")["tone"] == "danger"
        assert render_alert("x", "sec", "t", [], "warn")["tone"] == "warning"
        assert render_alert("x", "sec", "t", [], "ok")["tone"] == "success"
        assert render_alert("x", "sec", "t", [], "info")["tone"] == "info"

    def test_alert_id_in_text(self):
        p = render_alert("M00099", "mail", "Test mail", [], "info")
        assert "M00099" in p["text"]

    def test_title_in_text(self):
        p = render_alert("M00001", "sec", "Niezwykłe logowanie", SAMPLE_FIELDS, "warn")
        # tytuł musi być gdzieś w tekście (escapowany)
        assert "Niezwykłe logowanie" in p["text"].replace("\\", "")

    def test_fields_appear_in_text(self):
        p = render_alert("M00001", "sec", "Logowanie", SAMPLE_FIELDS, "warn")
        assert "16:32 UTC" in p["text"].replace("\\", "")

    def test_presentation_has_blocks(self):
        p = render_alert("M00042", "sec", "Alarm", SAMPLE_FIELDS, "critical")
        blocks = p["presentation"]["blocks"]
        assert len(blocks) >= 2  # tekst + co najmniej 1 rząd przycisków

    def test_presentation_has_text_block(self):
        p = render_alert("M00042", "sec", "Alarm", SAMPLE_FIELDS, "warn")
        text_blocks = [b for b in p["presentation"]["blocks"] if b["type"] == "text"]
        assert len(text_blocks) >= 1

    def test_presentation_has_button_blocks(self):
        p = render_alert("M00042", "sec", "Alarm", SAMPLE_FIELDS, "warn")
        btn_blocks = [b for b in p["presentation"]["blocks"] if b["type"] == "buttons"]
        assert len(btn_blocks) >= 1

    def test_no_unescaped_special_in_text(self):
        # dot i dash w wartosciach pól muszą być escapowane w MarkdownV2
        fields = [("IP", "192.168.1.1"), ("Region", "eu-west-1")]
        p = render_alert("M00001", "sec", "Test", fields, "warn")
        text = p["text"]
        # sprawdz ze po IP nie ma naga kropka (powinna byc \.   )
        # szukamy wzorca cyfra.cyfra bez backslasha — to byłby bład
        import re
        # te wzorce NIE powinny wystepowac poza blokiem kodu
        bad = re.search(r'(?<!\\)\d\.\d', text)
        assert bad is None, f"Niezabezpieczona kropka w adresie IP: {text}"

    def test_severity_icon_in_text(self):
        p_crit = render_alert("M00001", "sec", "Alert", [], "critical")
        assert "🚨" in p_crit["text"]

        p_warn = render_alert("M00001", "sec", "Alert", [], "warn")
        assert "🔶" in p_warn["text"]

    def test_domain_icon_in_text(self):
        p = render_alert("M00001", "sec", "Alert", [], "warn")
        assert "🛡️" in p["text"]

        p2 = render_alert("M00001", "mail", "Mail", [], "info")
        assert "✉️" in p2["text"]

    def test_body_text_appears(self):
        p = render_alert("M00001", "sec", "Alert", [], "warn",
                         body_text="Szczegóły błędu\nDruga linia")
        assert "Szczegóły błędu" in p["text"].replace("\\", "")

    def test_max_text_length_reasonable(self):
        # Telegram max message = 4096 znaków; alert nie powinien być dłuższy
        fields = [(f"Pole{i}", f"wartość numer {i}") for i in range(8)]
        p = render_alert("M00001", "sec", "Długi alert", fields, "critical",
                         body_text="Body text " * 20)
        assert len(p["text"]) <= 4096


class TestRenderInfo:
    def test_returns_required_keys(self):
        p = render_info("M00042", "skil", "Przeglad skilli OK")
        for key in ("text", "presentation", "tone", "parse_mode"):
            assert key in p

    def test_tone_is_info(self):
        p = render_info("M00042", "skil", "OK")
        assert p["tone"] == "info"

    def test_has_expand_and_ack_buttons(self):
        p = render_info("M00042", "skil", "OK")
        btn_blocks = [b for b in p["presentation"]["blocks"] if b["type"] == "buttons"]
        assert len(btn_blocks) >= 1
        labels = [btn["label"] for b in btn_blocks for btn in b["buttons"]]
        assert any("Rozwiń" in l for l in labels)
        assert any("Ack" in l for l in labels)

    def test_alert_id_in_text(self):
        p = render_info("M00013", "sejf", "Sejf sprawdzony")
        assert "M00013" in p["text"]
