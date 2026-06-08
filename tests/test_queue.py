# -*- coding: utf-8 -*-
import sys, os, tempfile, importlib
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def _fresh(tmp):
    import tg_alert_kit.queue as q
    importlib.reload(q)
    q.QUEUE = __import__("pathlib").Path(tmp)/"q.jsonl"
    q.SENT = __import__("pathlib").Path(tmp)/"q.sent"
    return q

def test_enqueue_pending_marksent():
    with tempfile.TemporaryDirectory() as tmp:
        q = _fresh(tmp)
        assert q.pending() == []
        q.enqueue("M1","sec","Tytul",[["A","1"]],"critical","uwaga")
        p = q.pending()
        assert len(p)==1 and p[0]["id"]=="M1"
        q.mark_sent("M1")
        assert q.pending()==[]

def test_no_dup_after_sent():
    with tempfile.TemporaryDirectory() as tmp:
        q = _fresh(tmp)
        q.enqueue("M2","mail","T",[],"info",None)
        q.mark_sent("M2")
        q.enqueue("M3","mail","T2",[],"info",None)
        ids=[r["id"] for r in q.pending()]
        assert ids==["M3"]
