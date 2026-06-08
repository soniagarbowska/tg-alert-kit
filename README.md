# tg-alert-kit

Telegram-first alert renderer dla systemu powiadomień Soni (Hugo + Victor).

## Zasada

**Telegram-first** — zero linków na zewnątrz. Wszystko obsługiwane w Telegramie przez przyciski inline z callbackami. Klik Soni wraca do agenta (Hugo/Victor) i tam jest obsługiwany.

## Wygląd alertu (card style)

```
🔶  🛡️ SEC · Nowe logowanie SSH

▎ Skąd         185.1.2.3
▎ Kiedy        16:32 UTC
▎ Wynik        SUKCES

M00042 · 16:32 UTC

[🔎 Rozwiń szczegóły]  [📄 Surowe dane]
[✅ Ack]               [🔕 Wycisz 1h]
```

## Paleta ikon (kuratorska)

| Severity    | Ikona | Domena  | Ikona |
|-------------|-------|---------|-------|
| critical    | 🚨    | sec     | 🛡️   |
| error       | ⛔    | mail    | ✉️   |
| warn        | 🔶    | sejf    | 🔐   |
| ok/recovery | 🟢    | gate    | 🚧   |
| info        | 🔷    | najem   | 🏠   |
|             |       | skil    | 🧩   |
|             |       | money   | 💰   |
|             |       | deadline| ⏳   |

## Przyciski per projekt

| Monitor  | Przyciski warn            | Dodatkowe critical     |
|----------|--------------------------|------------------------|
| sec      | Rozwiń, Surowe, Ack, Wycisz 1h | Eskaluj do Pawła  |
| mail     | Rozwiń, Ack, Odpowiedz, Pomiń  | —                  |
| sejf     | Rozwiń, Ack              | Eskaluj               |
| gate     | Rozwiń, Status, Ack, Wycisz 30m | —                |
| najem    | Rozwiń, Ack              | Eskaluj do Victora    |
| skil     | Rozwiń raport, Ack        | —                     |

## Użycie

```python
from tg_alert_kit import render_alert, send_alert

# Render tylko (do podejrzenia / testów)
payload = render_alert(
    alert_id="M00042",
    monitor_type="sec",
    title="Nowe logowanie SSH",
    fields=[("Skąd", "185.1.2.3"), ("Kiedy", "16:32 UTC"), ("Wynik", "SUKCES")],
    severity="warn",
)
print(payload["text"])          # MarkdownV2
print(payload["presentation"])  # OCPlatform presentation object

# Wyślij przez OpenClaw (Telegram-first, z callbackami)
result = send_alert(
    alert_id="M00042",
    monitor_type="sec",
    title="Nowe logowanie SSH",
    fields=[("Skąd", "185.1.2.3"), ("Kiedy", "16:32 UTC")],
    severity="warn",
    agent_id="hugo-works",
)
```

## Testy

```bash
cd /home/sonia/projects/tg-alert-kit
python -m pytest tests/ -v
```

## Architektura wysyłki

```
notify_sonia.py (cron/skrypty)
    └─→ tg_alert_kit.sender.send_alert()
            ├─→ render_alert() → payload (text + presentation + buttons)
            └─→ send_via_ocplatform() → OCPlatform gateway HTTP API
                    └─→ Telegram (z przyciskami inline)
                            └─→ klik Soni → callback → agent Hugo/Victor
```

## Źródła / inspiracje

- Wzorce: Grafana, UptimeRobot, Healthchecks.io, Sentry, BetterStack
- Research: Perplexity sonar-pro 2026-06-08
- Escaping: sudoskys/telegramify-markdown (podejście)
- Callback patterns: metalmatze/alertmanager-bot
