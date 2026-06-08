# -*- coding: utf-8 -*-
"""Parser pliku propozycji skilli (skill_proposer.py) -> lista propozycji.

Realny format (~/docs/SKILL-PROPOZYCJE/<data>.md), zweryfikowany na M00023:

    ## ROZWINIECIA istniejacych skilli
    **1. sejf - klasyfikacja pol PII...** * agent: hugo * **H**
    - **Co:** dopisac do sejfa...
    - **Z czego:** "dwa NIP sa jawne..."

    ## NOWE skille
    **A. agent-routing...** * agent: victor * **H**
    - **Co:** ...
    - **Z czego:** ...

Cel: rozbic zlepek na OSOBNE propozycje, kazda jako wlasna karta powiadomienia
(zasada Soni: nie jeden gigantyczny tekst, tylko osobne komunikaty z opcjami).
"""
from __future__ import annotations
import re

# naglowek propozycji: **1. nazwa ...** lub **A. nazwa ...**
_HEAD = re.compile(r"^\*\*\s*([0-9]+|[A-Za-z])[\.\)]\s*(.+?)\*\*\s*(.*)$")
# pole "- **Co:** ..." / "- **Z czego:** ..."
_FIELD = re.compile(r"^[-*]\s*\*\*\s*(Co|Z czego|Nie duplikat|Uwaga)\s*:?\s*\*\*\s*:?\s*(.*)$", re.I)
# meta po naglowku: "agent: hugo", priorytet "**H**"
_AGENT = re.compile(r"agent[:\s]+([A-Za-z/\-]+)", re.I)
_PRIO = re.compile(r"\b([HML])\b")


def _clean(s: str) -> str:
    s = re.sub(r"\s+", " ", s or "").strip()
    # usun gwiazdki/markdown resztki na brzegach
    return s.strip(" *·-—\t")


def _kind_from_section(section: str) -> str:
    sl = (section or "").lower()
    if "nowe" in sl:
        return "Nowy skill"
    if "rozwini" in sl or "istniej" in sl:
        return "Rozwiniecie"
    return ""


def parse_proposals(md: str) -> list[dict]:
    """Zwraca liste {name, agent, priority, kind, what, evidence, marker}."""
    lines = (md or "").splitlines()
    section = ""
    items: list[dict] = []
    cur: dict | None = None
    field: str | None = None

    def flush():
        nonlocal cur
        if cur and cur.get("name"):
            items.append(cur)
        cur = None

    for ln in lines:
        raw = ln.rstrip()
        s = raw.strip()
        if s.startswith("## "):
            flush()
            section = s[3:].strip()
            field = None
            continue
        mh = _HEAD.match(s)
        if mh:
            flush()
            marker, title, rest = mh.group(1), mh.group(2), mh.group(3)
            agent = None
            am = _AGENT.search(rest)
            if am:
                agent = am.group(1).strip()
            prio = None
            pm = _PRIO.search(rest)
            if pm:
                prio = pm.group(1).upper()
            cur = {
                "marker": marker,
                "name": _clean(title),
                "agent": agent,
                "priority": prio,
                "kind": _kind_from_section(section),
                "what": "",
                "evidence": "",
            }
            field = None
            continue
        mf = _FIELD.match(s)
        if mf and cur is not None:
            key = mf.group(1).lower()
            val = mf.group(2).strip()
            if key == "co":
                field = "what"
                cur["what"] = val
            elif key.startswith("z czego"):
                field = "evidence"
                cur["evidence"] = val
            else:
                field = None
            continue
        # kontynuacja wieloliniowa biezacego pola
        if cur is not None and field and s and not s.startswith(">") and not s.startswith("---"):
            cur[field] = (cur[field] + " " + s).strip()
            continue
        if not s:
            field = None
    flush()

    # przytnij dlugosci dla czytelnosci
    for it in items:
        it["name"] = _clean(it["name"])
        it["what"] = _clean(it["what"])
        it["evidence"] = _clean(it["evidence"])
    return items
