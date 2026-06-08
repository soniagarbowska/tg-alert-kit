# tg-alert-kit

Alerty na Telegram dla Soni. Wzorzec: **metalmatze/alertmanager-bot** (653 gwiazdki) — sprawdzony gotowiec, nie wymyslanie.

## Zasada

- Przyciski to **komendy po polsku**, nie martwe callbacki. Klik = bot dostaje `/alert_pawel M00099`, agent wykonuje akcje. **Potwierdzone ze dziala** (test 2026-06-08).
- Zero ACK, zero angielskiego zargonu. Etykiety mowia wprost co robia.
- Layout jak alertmanager-bot: ikona + tytul, pola `klucz: wartosc`, ID na dole.

## Jak wyglada alert

```
🔥  Nowe logowanie na serwer

• Skad: 185.220.101.47
• Kiedy: 17:20
• Wynik: udane

Nieznany adres. Sprawdz czy to Ty.

M00099

[Pokaz szczegoly]   [Wyslij do Pawla]
[Odloz na pozniej]  [Zalatwione]
```

## Ikony (jak alertmanager-bot)

- 🔥 krytyczny / aktywny problem (firing)
- ⚠️ uwaga
- ℹ️ informacja
- ✅ zalatwione / przywrocone (resolved)

## Przyciski = komendy

| Etykieta          | Komenda              | Co robi                    |
|-------------------|----------------------|----------------------------|
| Pokaz szczegoly   | /alert_szczegoly ID  | rozwijam pelne info        |
| Wyslij do Pawla   | /alert_pawel ID      | przekazuje Pawlowi (tech)  |
| Przekaz do najmu  | /alert_victor ID     | przekazuje do najmu        |
| Odloz na pozniej  | /alert_pozniej ID    | przypomne za 2h            |
| Zalatwione        | /alert_zalatwione ID | oznaczam jako zalatwione   |

## Zestawy przyciskow per typ alertu

| Typ            | Przyciski                                    |
|----------------|----------------------------------------------|
| bezpieczenstwo | szczegoly, Pawel, pozniej, zalatwione        |
| mail           | szczegoly, pozniej, zalatwione               |
| sejf           | szczegoly, Pawel, zalatwione                 |
| gate           | szczegoly, Pawel, pozniej, zalatwione        |
| najem          | szczegoly, Victor, pozniej, zalatwione       |

## Uzycie

```python
from tg_alert_kit import render_alert

a = render_alert(
    alert_id="M00099",
    alert_type="bezpieczenstwo",
    title="Nowe logowanie na serwer",
    fields=[("Skad", "185.220.101.47"), ("Kiedy", "17:20"), ("Wynik", "udane")],
    severity="critical",
    note="Nieznany adres. Sprawdz czy to Ty.",
)
# a["presentation"] -> wysylasz przez narzedzie message (z przyciskami)
```

Gdy przyjdzie klik (komenda):
```python
from tg_alert_kit import parse_command
info = parse_command("/alert_pawel M00099")   # {"akcja": "pawel", "id": "M00099"}
```

## Testy

```bash
python3 -m pytest tests/ -q   # 25 passed
```

## Zrodla

- metalmatze/alertmanager-bot (default.tmpl) — layout, ikony firing/resolved
- ix-ai/alertmanager-telegram-bot — przyciski jako akcje

## Architektura (droga B — alerty z monitorow z przyciskami)

Przyciski dzialaja tylko gdy alert wysyla agent (Hugo) przez OCPlatform.
Monitory nie moga tego wprost, wiec przez kolejke:

```
monitor --> notify_sonia.py --queue --> kolejka JSONL --> cron dispatcher (60s) --> Hugo
   Hugo: pending -> message(presentation z przyciskami) -> mark-sent
```

- `~/.ocplatform/alert-queue.jsonl` — alerty czekajace
- `~/.ocplatform/alert-queue.sent` — juz wyslane (anty-dublowanie)
- cron "Alert dispatcher" — co 60s, isolated agentTurn, pusta kolejka => NO_REPLY
- `HANDLER.md` — co Hugo robi gdy Sonia klika przycisk

### Monitor wysyla alert tak:
```bash
python3 ~/wiki/scripts/notify_sonia.py --queue \
  --monitor sonia-sec --type sec \
  --about "Nowe logowanie na serwer" \
  --raw $'Adres IP=1.2.3.4\nCzas=17:20\nWynik=udane' \
  --severity critical
```
