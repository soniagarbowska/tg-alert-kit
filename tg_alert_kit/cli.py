# -*- coding: utf-8 -*-
"""CLI tg-alert-kit.

Monitor woła:
    python3 -m tg_alert_kit enqueue --id M00120 --type sec \
        --title "Nowe logowanie" --field "Adres IP=1.2.3.4" --field "Czas=17:20" \
        --severity critical --note "Nieznany adres."

Agent (Hugo) woła, zeby zobaczyc co czeka:
    python3 -m tg_alert_kit pending        # JSON: lista alertow + gotowy presentation
"""
from __future__ import annotations
import argparse
import json
import sys

from .queue import enqueue, pending, mark_sent
from .notify import notify


def _parse_fields(items):
    out = []
    for it in (items or []):
        if "=" in it:
            k, v = it.split("=", 1)
            out.append([k.strip(), v.strip()])
    return out


def main(argv=None):
    p = argparse.ArgumentParser(prog="tg_alert_kit")
    sub = p.add_subparsers(dest="cmd", required=True)

    e = sub.add_parser("enqueue", help="dopisz alert do kolejki")
    e.add_argument("--id", required=True)
    e.add_argument("--type", required=True)
    e.add_argument("--title", required=True)
    e.add_argument("--field", action="append", default=[], help="Klucz=Wartosc")
    e.add_argument("--severity", default="warn")
    e.add_argument("--note", default=None)

    pe = sub.add_parser("pending", help="lista nie-wyslanych alertow + presentation")
    pe.add_argument("--with-presentation", action="store_true", default=True)

    m = sub.add_parser("mark-sent", help="oznacz alert jako wyslany")
    m.add_argument("--id", required=True)

    args = p.parse_args(argv)

    if args.cmd == "enqueue":
        rec = enqueue(args.id, args.type, args.title,
                      _parse_fields(args.field), args.severity, args.note)
        print(json.dumps(rec, ensure_ascii=False))
        return 0

    if args.cmd == "pending":
        items = pending()
        out = []
        for rec in items:
            # styl #439 (notify/alert) zamiast starego render_alert
            n = notify(
                "alert",
                title=rec["title"],
                fields=[tuple(f) for f in rec.get("fields", [])],
                severity=rec.get("severity", "warn"),
                note=rec.get("note"),
                badge=rec.get("badge"),
                buttons_for=rec["type"],
                alert_id=rec["id"],
            )
            out.append({
                "id": rec["id"],
                "type": rec["type"],
                "enqueued": rec.get("enqueued"),
                "presentation": n["presentation"],
                "text": n["text"],
            })
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    if args.cmd == "mark-sent":
        mark_sent(args.id)
        print(json.dumps({"marked": args.id}, ensure_ascii=False))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
