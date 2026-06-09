# -*- coding: utf-8 -*-
"""Testy parsera propozycji skilli + przepisu proposal (realny M00023)."""
from tg_alert_kit import notify
from tg_alert_kit.parse_proposals import parse_proposals


SAMPLE = """# Propozycje skilli (2026-06-08)

## ROZWINIECIA istniejacych skilli

**1. sejf - klasyfikacja pol PII** * agent: hugo * **H**
- **Co:** dopisac do sejfa ktore pola sa jawne a ktore wrazliwe.
- **Z czego:** "dwa NIP sa jawne, firmy nazwy tez".

**2. system-powiadomien - pryncypia** * agent: hugo/victor * **H**
- **Co:** zapisac twarde zasady telegram-first.
- **Z czego:** "telegram first workflow zapisz to jako pryncypia".

## NOWE skille

**A. agent-routing** * agent: victor * **H**
- **Co:** skill tozsamosciowo-nawigacyjny per agent.
- **Z czego:** "masz skilla do maila, dlaczego go nie uzywasz".
"""


def test_parse_splits_into_separate_items():
    items = parse_proposals(SAMPLE)
    assert len(items) == 3
    assert items[0]["name"].startswith("sejf")
    assert items[0]["agent"] == "hugo"
    assert items[0]["priority"] == "H"
    assert items[0]["kind"] == "Rozwiniecie"
    assert "jawne" in items[0]["what"]
    assert "NIP" in items[0]["evidence"]


def test_parse_new_skill_section():
    items = parse_proposals(SAMPLE)
    a = items[-1]
    assert a["name"].startswith("agent-routing")
    assert a["kind"] == "Nowy skill"
    assert a["agent"] == "victor"


def test_proposal_recipe_renders_sections():
    items = parse_proposals(SAMPLE)
    p = items[0]
    n = notify("proposal", name=p["name"], what=p["what"], agent=p["agent"],
               kind=p["kind"], priority=p["priority"], evidence=p["evidence"],
               index="1 z 3", severity="warn", buttons_for="skille",
               alert_id="M00023.1")
    t = n["text"]
    assert "**CO MA ROBIĆ**" in t
    assert "**Z CZEGO WYNIKA**" in t
    assert "propozycja 1 z 3" in t
    assert "wysoki" in t
    # kontekstowe przyciski skilli
    labels = [b["label"] for r in n["buttons"] for b in r]
    assert any("Buduj ten skill" in l for l in labels)
    assert any("Odrzu" in l for l in labels)


def test_proposal_priority_maps_severity():
    n = notify("proposal", name="x", what="y", priority="M",
               buttons_for="skille", alert_id="M1")
    assert n["tone"] == "info"
    n2 = notify("proposal", name="x", what="y", priority="H",
                severity="warn", buttons_for="skille", alert_id="M2")
    assert n2["tone"] == "warning"


def test_empty_input():
    assert parse_proposals("") == []
    assert parse_proposals("# tylko naglowek\n\nbla bla") == []


def test_proposal_rich_args():
    # nowe lepsze argumenty: scope, value, themes
    n = notify("proposal", name="X", what="robi Y",
               scope="a | b | c", value="da Z",
               evidence="bo wraca", themes=["t1", "t2", "t3"],
               priority="H", severity="warn", buttons_for="skille",
               index="1 z 2", alert_id="M1")
    t = n["text"]
    assert "**ZAKRES**" in t
    assert "**CO TO DA**" in t
    assert "3 zgrupowane" in t          # licznik tematow
    assert "a | b | c" in t


def test_enqueue_payload_roundtrip(tmp_path, monkeypatch):
    import tg_alert_kit.queue as q
    monkeypatch.setattr(q, "QUEUE", tmp_path / "q.jsonl")
    monkeypatch.setattr(q, "SENT", tmp_path / "q.sent")
    q.enqueue_payload("M1", "proposal", buttons_for="skille",
                      severity="info", payload={"name": "n", "what": "w"})
    pend = q.pending()
    assert len(pend) == 1
    assert pend[0]["recipe"] == "proposal"
    assert pend[0]["payload"]["name"] == "n"
