# -*- coding: utf-8 -*-
"""Testy na REALNYCH typach komunikatow systemu (nie wymyslonych).

Dane wzorowane na rejestrze alertow: M00007/M00014 (mail), M00013 (sejf/decision),
M00018/M00022 (sec), tech (cron/provider watchdog).
"""
from tg_alert_kit import notify
from tg_alert_kit.text_alert import DOT


def test_mail_faktura_play():
    # realny M00014
    n = notify("mail", sender="awizo@mojefinanseplay.pl",
               subject="Play - e-faktura do pobrania",
               summary="Faktura za Internet Swiatlowodowy. Koszt operacyjny biura.",
               action="Oplacic do 22.06.2026 - 95,00 zl.", deadline="22.06.2026",
               severity="info", buttons_for="mail", alert_id="M00014")
    t = n["text"]
    assert "Play - e-faktura" in t
    assert "**Od:**" in t and "awizo@mojefinanseplay.pl" in t
    assert "> Oplacic do 22.06.2026" in t        # akcja jako cytat
    assert "Zalatwione" in [b["label"] for r in n["buttons"] for b in r]


def test_decision_sejf_konflikt_telefonu():
    # realny M00013
    n = notify("decision",
               title="Sprawa Damrota - zmienil sie numer telefonu?",
               context="Nowy dokument podaje inny numer. Bylo ...200, nowe ...888.",
               options=[
                   {"name": "NOWY - bierzemy ...888", "plus": "aktualne", "minus": "jesli literowka, zly"},
                   {"name": "STARY - zostaje ...200", "plus": "potwierdzone 2 dok.", "minus": "jesli sie zmienil"},
               ],
               recommendation="STARY (2 dokumenty kontra 1).",
               how_to_answer="Glosowka: NOWY czy STARY. Pelne? Napisz POKAZ.",
               severity="warn", badge="Sejf", buttons_for="sejf", alert_id="M00013")
    t = n["text"]
    assert "Decyzja do podjecia" in t and "Sejf" in t
    # nowy uklad: jasne sekcje
    assert "**SYTUACJA**" in t and "**OPCJE**" in t and "**REKOMENDACJA**" in t
    assert "NOWY" in t and "STARY" in t
    # za/ryzyko zamiast +/- (Telegram zjada +/-)
    assert "**Za:**" in t and "**Ryzyko:**" in t
    assert "aktualne" in t
    assert n["tone"] == "warning"


def test_sec_przeglad_ok_jako_status():
    # realny M00022 - przeglad bezpieczenstwa wszystko OK
    n = notify("status", title="Przeglad bezpieczenstwa serwera",
               state_word="WSZYSTKO OK",
               severity="ok",
               fields=[("fail2ban", "aktywny, banow 0"),
                       ("SSH 12h", "190 nieudanych (szum), 7 udanych"),
                       ("Dysk", "51%"), ("Porty", "bez zmian")],
               alert_id="M00022")
    assert n["tone"] == "success"
    assert "WSZYSTKO OK" in n["text"]


def test_sec_incydent_jako_alert():
    # realny M00018 - nieudane logowania SSH
    n = notify("alert", title="Nieudane proby logowania SSH",
               fields=[("Adres IP", "193.41.206.12"), ("Kraj", "Rosja"),
                       ("Prob", "47 w 3 minuty"), ("Cel", "root, admin, sonia"),
                       ("Status", "fail2ban zablokowal")],
               severity="warn", badge="SSH", buttons_for="sec", alert_id="M00018")
    t = n["text"]
    assert "Nieudane proby logowania SSH" in t
    assert "`193.41.206.12`" in t                 # IP mono
    assert "To bylam ja" in [b["label"] for r in n["buttons"] for b in r]


def test_tech_awaria_critical():
    # realny ksztalt cron_watchdog/provider_watchdog
    n = notify("alert", title="Provider LLM nie odpowiada",
               fields=[("Usluga", "anthropic-proxy"), ("Status", "timeout 3x"),
                       ("Czas", "21:00")],
               severity="critical", badge="Infra", buttons_for="tech", alert_id="M00050")
    assert n["tone"] == "danger"
    assert "⛔" in n["text"]


def test_seo_digest_okazje():
    # realny ksztalt seo_digest - okazje (wyswietlenia, CTR)
    n = notify("digest", title="Okazje SEO", topic="info",
               items=[
                   {"color": "orange", "name": "zarzadzanie najmem katowice",
                    "tag": "duzo wyswietlen, niski CTR",
                    "fields": [("Wyswietlenia", "1 240"), ("CTR", "1,2%")]},
               ],
               footer="Search Console - 7 dni")
    assert "Okazje SEO" in n["text"]
    assert DOT["orange"] in n["text"]
