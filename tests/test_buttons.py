# -*- coding: utf-8 -*-
"""Testy przyciskow-komend."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tg_alert_kit.buttons import build_buttons, parse_command


class TestBuildButtons:
    def test_returns_rows(self):
        rows = build_buttons("bezpieczenstwo", "M00099")
        assert isinstance(rows, list) and len(rows) >= 1

    def test_every_button_is_command(self):
        rows = build_buttons("bezpieczenstwo", "M00099")
        for row in rows:
            for btn in row:
                assert btn["action"]["type"] == "command"
                assert btn["action"]["command"].startswith("/alert_")

    def test_alert_id_in_command(self):
        rows = build_buttons("mail", "M00042")
        for row in rows:
            for btn in row:
                assert "M00042" in btn["action"]["command"]

    def test_labels_are_polish_no_ack(self):
        rows = build_buttons("bezpieczenstwo", "M00099")
        labels = [b["label"] for r in rows for b in r]
        # zero ACK / angielskiego zargonu
        for l in labels:
            assert "ack" not in l.lower()
            assert "acknowledge" not in l.lower()

    def test_najem_has_victor_not_pawel(self):
        rows = build_buttons("najem", "M00001")
        cmds = [b["action"]["command"] for r in rows for b in r]
        assert any("victor" in c for c in cmds)
        assert not any("pawel" in c for c in cmds)

    def test_sec_has_pawel(self):
        rows = build_buttons("bezpieczenstwo", "M00001")
        cmds = [b["action"]["command"] for r in rows for b in r]
        assert any("pawel" in c for c in cmds)

    def test_unknown_type_uses_default(self):
        rows = build_buttons("cos_nieznanego", "M00001")
        assert len(rows) >= 1

    def test_all_types_have_layout(self):
        for t in ("bezpieczenstwo", "sec", "mail", "sejf", "gate", "najem"):
            assert len(build_buttons(t, "M00001")) >= 1

    def test_styles_valid(self):
        valid = {"primary", "secondary", "success", "danger"}
        rows = build_buttons("bezpieczenstwo", "M00099")
        for r in rows:
            for b in r:
                assert b["style"] in valid


class TestParseCommand:
    def test_pawel(self):
        r = parse_command("/alert_pawel M00099")
        assert r["akcja"] == "pawel"
        assert r["id"] == "M00099"

    def test_pozniej(self):
        r = parse_command("/alert_pozniej M00042")
        assert r["akcja"] == "pozniej"
        assert r["id"] == "M00042"

    def test_szczegoly(self):
        r = parse_command("/alert_szczegoly M00013")
        assert r["akcja"] == "szczegoly"
        assert r["id"] == "M00013"

    def test_zalatwione(self):
        r = parse_command("/alert_zalatwione M00007")
        assert r["akcja"] == "zalatwione"
        assert r["id"] == "M00007"

    def test_victor(self):
        r = parse_command("/alert_victor M00100")
        assert r["akcja"] == "victor"
        assert r["id"] == "M00100"
