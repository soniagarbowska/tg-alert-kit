# -*- coding: utf-8 -*-
"""Testy polityki PII (zasada Soni 2026-06-08): maskuj TYLKO twarde dane wrazliwe.

NIE maskuj: imie, nazwisko, adres, TELEFON, e-mail.
Maskuj: PESEL, dowod, data urodzenia, konto/IBAN, NIP, ksiega wieczysta.
Zrodlo: ~/wiki/scripts/mask_sensitive.py (centralne, nie wlasne reguly).
"""
from tg_alert_kit import notify
from tg_alert_kit.pii import mask, available


def test_telefon_i_nazwisko_zostaja():
    assert "512 340 200" in mask("Tel. 512 340 200")
    assert "Andrzej Damrota" in mask("Andrzej Damrota, ul. Kwiatowa 5")
    assert "biuro@x.pl" in mask("Mail: biuro@x.pl")


def test_twarde_pii_maskowane():
    assert "[DANE]" in mask("PESEL: 90010112345")
    assert "[KONTO]" in mask("Konto: 61 1090 1014 0000 0712 1981 2874")
    assert "[DOWOD]" in mask("Dowod ABC123456")


def test_decision_pokazuje_telefon_i_nazwisko():
    n = notify("decision", title="Andrzej Damrota - numer telefonu?",
               context="Bylo 512 340 200, teraz 512 340 888.",
               options=[{"name": "Nowy", "button": "Nowy"},
                        {"name": "Stary", "button": "Stary"}],
               recommendation="Stary.", how_to_answer="Klik.",
               severity="warn", buttons_for="sejf", alert_id="M00013")
    t = n["text"]
    assert "Andrzej Damrota" in t
    assert "512 340 200" in t and "512 340 888" in t
    # nic nie zamaskowane -> brak przycisku 2FA
    cmds = [b["action"]["command"] for r in n["buttons"] for b in r]
    assert not any("pokaz" in c for c in cmds)


def test_decision_z_kontem_dodaje_2fa():
    n = notify("decision", title="Rozbieznosc numeru konta",
               context="Aneks: 61 1090 1014 0000 0712 1981 2874.",
               options=[{"name": "Nowe", "button": "Nowe"},
                        {"name": "Stare", "button": "Stare"}],
               recommendation="Sprawdz.", how_to_answer="Klik.",
               severity="warn", buttons_for="sejf", alert_id="M00030")
    assert "[KONTO]" in n["text"]
    cmds = [b["action"]["command"] for r in n["buttons"] for b in r]
    assert any("pokaz" in c for c in cmds)


def test_central_policy_loaded():
    # centralny modul powinien byc dostepny na VPS
    assert available() is True
