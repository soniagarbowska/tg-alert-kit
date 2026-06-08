# -*- coding: utf-8 -*-
"""Testy atomu: jeden wzor karty (#457) dla wielu typow powiadomien."""
import os
import pytest

from tg_alert_kit import build_alert, PRESETS, preset


def _has_chrome():
    import shutil
    return any(shutil.which(b) for b in ("google-chrome", "chromium", "chromium-browser"))


def test_preset_known_types():
    for t in ("sec", "bezpieczenstwo", "mail", "sejf", "gate", "najem"):
        p = preset(t)
        assert "sev" in p and "badge" in p


def test_preset_unknown_falls_back():
    p = preset("cos-nowego-czego-nie-ma")
    assert p == PRESETS["_default"]


@pytest.mark.skipif(not _has_chrome(), reason="brak google-chrome/chromium")
def test_build_alert_sec_makes_card_and_buttons():
    a = build_alert("sec", "Nowe logowanie",
                    [("Adres IP", "1.2.3.4"), ("Czas", "18:00")],
                    alert_id="M00099", note="uwaga")
    assert os.path.exists(a["card"])
    assert a["card"].endswith(".png")
    assert a["severity"] == "critical"
    assert a["tone"] == "danger"
    labels = [b["label"] for row in a["buttons"] for b in row]
    assert "To bylam ja" in labels and "To nie ja" in labels


@pytest.mark.skipif(not _has_chrome(), reason="brak google-chrome/chromium")
def test_build_alert_types_differ_in_color():
    sec = build_alert("sec", "x", [("a", "b")], "M1")
    mail = build_alert("mail", "x", [("a", "b")], "M2")
    najem = build_alert("najem", "x", [("a", "b")], "M3")
    assert sec["tone"] == "danger"
    assert mail["tone"] == "info"
    assert najem["tone"] == "info"
    # mail/najem maja akcje zalatwione, sec ma to_ja/nie_ja
    assert "Zalatwione" in [b["label"] for row in mail["buttons"] for b in row]


@pytest.mark.skipif(not _has_chrome(), reason="brak google-chrome/chromium")
def test_severity_override_wins():
    a = build_alert("mail", "x", [("a", "b")], "M9", severity="critical")
    assert a["severity"] == "critical"
    assert a["tone"] == "danger"
