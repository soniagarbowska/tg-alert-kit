# -*- coding: utf-8 -*-
"""Testy kontekstowych przyciskow (actions.py) + integracja z notify()."""
from tg_alert_kit import notify
from tg_alert_kit import actions


def _labels(rows):
    return [b["label"] for row in rows for b in row]


def _cmds(rows):
    return [b["action"]["command"] for row in rows for b in row]


def test_from_options_deterministic():
    opts = [
        {"name": "Przyjac nowy: ...888", "button": "Numer ...888"},
        {"name": "Zostawic stary: ...200", "button": "Numer ...200"},
    ]
    rows = actions.from_options(opts, "M00013")
    cmds = _cmds(rows)
    assert "/alert_wybierz M00013 1" in cmds
    assert "/alert_wybierz M00013 2" in cmds
    # druga linia: pokaz + pozniej
    assert "/alert_pokaz M00013" in cmds
    assert "Numer ...888" in _labels(rows)


def test_decision_notify_uses_options():
    n = notify("decision", title="X", context="c",
               options=[{"name": "A", "button": "Opcja A"},
                        {"name": "B", "button": "Opcja B"}],
               severity="warn", buttons_for="sejf", alert_id="M1")
    cmds = _cmds(n["buttons"])
    assert "/alert_wybierz M1 1" in cmds
    assert "/alert_wybierz M1 2" in cmds


def test_catalog_whitelist_blocks_unknown():
    # spoza whitelist -> odrzucone
    rows = actions.from_catalog(["rm_rf", "wyslij_pawlowi", "pozniej"], "M1", "mail")
    cmds = _cmds(rows)
    assert all("rm_rf" not in c and "pawl" not in c for c in cmds)
    assert "/alert_pozniej M1" in cmds


def test_llm_garbage_falls_back_safe():
    def bad_llm(prompt):
        return {"actions": ["rm_rf", "drop_table"]}
    n = notify("mail", sender="x", subject="y",
               buttons_for="mail", alert_id="M1", llm_fn=bad_llm)
    cmds = _cmds(n["buttons"])
    # zaden smiec nie przeszedl; jest bezpieczny default
    assert all("rm_rf" not in c and "drop_table" not in c for c in cmds)
    assert any("/alert_" in c for c in cmds)


def test_llm_valid_selection():
    def good_llm(prompt):
        return {"actions": ["zaplacone", "odpisz"]}
    n = notify("mail", sender="x", subject="Faktura",
               buttons_for="mail", alert_id="M00014", llm_fn=good_llm)
    cmds = _cmds(n["buttons"])
    assert "/alert_zaplacone M00014" in cmds
    assert "/alert_odpisz M00014" in cmds


def test_default_per_type():
    rows = actions.default_for("sec", "M1")
    cmds = _cmds(rows)
    assert "/alert_toja M1" in cmds
    assert "/alert_nieja M1" in cmds


def test_sec_alert_contextual_default():
    n = notify("alert", title="Nieudane logowania SSH",
               fields=[("IP", "1.2.3.4")], severity="warn",
               buttons_for="sec", alert_id="M00018")
    labels = _labels(n["buttons"])
    assert "To bylam ja" in labels
    assert "Zablokuj adres" in labels
