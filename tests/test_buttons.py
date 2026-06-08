# -*- coding: utf-8 -*-
"""Testy dynamicznych przycisków."""
import pytest
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tg_alert_kit.buttons import build_buttons, describe_callback


class TestBuildButtons:
    def test_returns_list_of_rows(self):
        rows = build_buttons("sec", "M00042", "warn")
        assert isinstance(rows, list)
        assert len(rows) >= 1
        for row in rows:
            assert isinstance(row, list)

    def test_each_button_has_required_keys(self):
        rows = build_buttons("mail", "M00001", "info")
        for row in rows:
            for btn in row:
                assert "label" in btn
                assert "action" in btn
                assert btn["action"]["type"] == "callback"
                assert "value" in btn["action"]

    def test_alert_id_substituted(self):
        rows = build_buttons("sec", "M00042", "warn")
        all_values = [btn["action"]["value"] for row in rows for btn in row]
        # każdy callback value musi zawierać M00042 albo być gate_status
        for v in all_values:
            assert "M00042" in v or v == "gate_status"

    def test_no_curly_braces_in_values(self):
        rows = build_buttons("mail", "M00099", "critical")
        for row in rows:
            for btn in row:
                assert "{id}" not in btn["action"]["value"]

    def test_escalate_only_for_critical(self):
        rows_warn = build_buttons("sec", "M00001", "warn")
        rows_crit = build_buttons("sec", "M00001", "critical")
        labels_warn = [btn["label"] for row in rows_warn for btn in row]
        labels_crit = [btn["label"] for row in rows_crit for btn in row]
        # eskaluj NIE pojawia sie dla warn
        assert not any("Eskaluj" in l for l in labels_warn)
        # eskaluj POJAWIA sie dla critical
        assert any("Eskaluj" in l for l in labels_crit)

    def test_unknown_monitor_uses_default(self):
        rows = build_buttons("nieznany_monitor", "M00001", "info")
        assert len(rows) >= 1

    def test_all_monitor_types_have_layouts(self):
        for mtype in ("sec", "mail", "sejf", "gate", "najem", "skil"):
            rows = build_buttons(mtype, "M00001", "warn")
            assert len(rows) >= 1, f"brak layoutu dla {mtype}"

    def test_styles_are_valid(self):
        valid_styles = {"primary", "secondary", "success", "danger"}
        rows = build_buttons("sec", "M00042", "critical")
        for row in rows:
            for btn in row:
                assert btn.get("style") in valid_styles


class TestDescribeCallback:
    def test_ack(self):
        r = describe_callback("ack:M00042")
        assert r["action"] == "ack"
        assert r["alert_id"] == "M00042"
        assert r["extra"] == ""

    def test_silence_with_minutes(self):
        r = describe_callback("silence:60:M00042")
        assert r["action"] == "silence"
        assert r["extra"] == "60"
        assert r["alert_id"] == "M00042"

    def test_expand(self):
        r = describe_callback("expand:M00013")
        assert r["action"] == "expand"
        assert r["alert_id"] == "M00013"

    def test_escalate(self):
        r = describe_callback("escalate:M00007")
        assert r["action"] == "escalate"
        assert r["alert_id"] == "M00007"

    def test_gate_status_no_alert(self):
        r = describe_callback("gate_status")
        assert r["action"] == "gate_status"
        assert r["alert_id"] == ""

    def test_reply(self):
        r = describe_callback("reply:M00004")
        assert r["action"] == "reply"
        assert r["alert_id"] == "M00004"
