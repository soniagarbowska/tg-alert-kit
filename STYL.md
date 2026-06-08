# Styl powiadomien (#439) — jak robic nowe

Jeden STYL, rozne UKLADY. Kazde powiadomienie sklada sie z KLOCKOW, ktore
renderuja sie w tym samym stylu (naglowek + separatory + punktory + pogrubienia
+ monospace + cytat + kropki statusu + kursywa w stopce). To jest wzor, ktory
Sonia zaakceptowala (wiadomosc #439).

## Jak wyslac powiadomienie (1 funkcja)

```python
from tg_alert_kit import notify

n = notify("alert",
    title="Nowe logowanie na serwer",
    fields=[("Adres IP","185.220.101.47"),("Czas","18:00"),("Uzytkownik","sonia")],
    severity="critical", badge="SSH",
    note="Nieznany adres. Jesli to nie Ty - dzialaj od razu.",
    buttons_for="sec", alert_id="M00099")

# n["text"]         -> tekst w stylu #439
# n["presentation"] -> {tone, blocks:[przyciski]}
```
Wysylka (agent): message(action=send, target=..., message=n["text"], presentation=n["presentation"]).

## Gotowe przepisy (recipe)

- **alert**  — pojedynczy alert klucz:wartosc (sec, sejf, gate, brama).
  Args: title, fields[(k,v)], severity, badge, note, alert_id.
- **digest** — podsumowanie wielu pozycji (poczta, lista). DOKLADNIE wzor #439.
  Args: title, items[{color,name,tag,fields,note,spoiler}], subtitle, footer, topic.
- **status** — krotka zmiana stanu (monitor up/down, przywrocono).
  Args: title, state_word, severity, fields, note, alert_id.

## Wagi (kolor/ikona, BMP-safe)
critical -> ⛔ | warn -> ⚠️ | info -> ℹ️ | ok/resolved -> ✅

## Kropki statusu (entry w digescie)
red 🔴 | orange 🟠 | yellow 🟡 | green 🟢 | blue 🔵 | white ⚪ | black ⚫

## Klocki (gdy chcesz wlasny uklad bez przepisu)
```python
from tg_alert_kit import compose
txt = compose([
    ("header", "⛔", "Tytul", "podtytul"),
    ("divider",),
    ("field", "Klucz", "wartosc"),        # mono auto dla IP/kwot/login
    ("field", "Cokolwiek", "x", "mono"),  # wymus monospace
    ("entry", "orange", "Allegro", "tag"),# pozycja z kropka
    ("note", "uwaga jako cytat"),
    ("spoiler", "ukryte mniej wazne"),
    ("footer", "stopka kursywa"),
])
```

## DODANIE NOWEGO TYPU POWIADOMIENIA
1. (Opcja A, najczesciej) uzyj gotowego przepisu alert/digest/status z `notify(...)`.
2. (Opcja B, wlasny uklad) napisz funkcje przepisu w `presets.py`
   (dane -> lista klockow), zarejestruj w `RECIPES`.
3. Przyciski: dodaj/uzyj layoutu w `buttons.py` (`_LAYOUTS[typ]`),
   podaj `buttons_for="typ"`.

## WAZNE technicznie (zweryfikowane telethoniem)
- Ikony naglowka MUSZA byc BMP (⛔⚠️ℹ️✅✉️). Emoji spoza BMP (🔥📥📧) przesuwaja
  pogrubienie tytulu o 1 znak. `TOPIC_ICON` ma juz tylko BMP.
- Kolorowe kropki 🟠🟢⚪ sa non-BMP i daja minimalne (1 znak) przesuniecie
  pojedynczej etykiety pod nimi — to ten sam efekt co w zaakceptowanym #439,
  wizualnie niezauwazalny. To cena za kolory; zostawiamy.
- Pogrubienia, monospace, cytat, spoiler, kursywa, auto-link — dzialaja.
- Telegram NIE renderuje HTML/CSS. To maksimum co da sie tekstem.
```
