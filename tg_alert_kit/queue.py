# -*- coding: utf-8 -*-
"""Kolejka alertow — monitor dopisuje, agent (Hugo) odbiera i wysyla ladnie.

Dlaczego kolejka: przyciski dzialaja TYLKO gdy alert wysyla agent przez
narzedzie 'message' (potwierdzone 2026-06-08). Monitory z crona nie moga tego
zrobic bezposrednio (CLI miga przez overlay). Wiec:

    monitor  --enqueue-->  kolejka JSONL  --cron agentTurn co 1 min-->  Hugo
    Hugo: czyta nowe -> render -> message(presentation z przyciskami) -> oznacz wyslane

Plik kolejki: ~/.ocplatform/alert-queue.jsonl  (dopisywanie, jedna linia = alert)
Stan wyslanych: ~/.ocplatform/alert-queue.sent  (id wyslanych, zeby nie dublowac)
"""
from __future__ import annotations
import json
import os
import time
from pathlib import Path

QUEUE = Path(os.path.expanduser("~/.ocplatform/alert-queue.jsonl"))
SENT = Path(os.path.expanduser("~/.ocplatform/alert-queue.sent"))


def enqueue(alert_id: str, alert_type: str, title: str,
            fields: list, severity: str = "warn", note: str | None = None) -> dict:
    """Dopisuje alert do kolejki (wola monitor/cron). fields = [[k,v],...]."""
    rec = {
        "id": alert_id,
        "type": alert_type,
        "title": title,
        "fields": fields,
        "severity": severity,
        "note": note,
        "ts": int(time.time()),
        "enqueued": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return rec


def _sent_ids() -> set:
    if not SENT.exists():
        return set()
    return set(l.strip() for l in SENT.read_text(encoding="utf-8").splitlines() if l.strip())


def pending() -> list:
    """Zwraca alerty z kolejki jeszcze NIE wyslane (wola agent)."""
    if not QUEUE.exists():
        return []
    done = _sent_ids()
    out = []
    for line in QUEUE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if rec.get("id") and rec["id"] not in done:
            out.append(rec)
    return out


def mark_sent(alert_id: str) -> None:
    """Oznacza alert jako wyslany (wola agent po udanej wysylce)."""
    SENT.parent.mkdir(parents=True, exist_ok=True)
    with open(SENT, "a", encoding="utf-8") as f:
        f.write(alert_id + "\n")
