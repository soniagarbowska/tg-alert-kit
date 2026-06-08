# Handler komend alertow (dla Hugo)

Gdy Sonia klika przycisk pod alertem, do mnie przychodzi komenda tekstowa.
Reaguje natychmiast wg tej tabeli. ID to numer M00xxx z alertu.

## Komendy

- `/alert_toja <ID>` — "To bylam ja"
  -> Zamykam alert jako dzialanie Soni. Krotko potwierdzam: "OK, zamykam <ID>, to bylo Twoje."
     Nic nie sprawdzam dalej. Oznaczam w rejestrze jako zamkniete.

- `/alert_nieja <ID>` — "To nie ja"
  -> POWAZNIE. To moze byc realne zagrozenie. Sprawdzam glebiej:
     `python3 ~/wiki/scripts/alert.py <ID>` (pelny kontekst), patrze na logi (kto/skad/kiedy),
     sprawdzam czy adres dalej aktywny. Wracam do Soni z ustaleniem + propozycja (np. zmiana hasla,
     blokada IP, kontakt z Pawlem przy sprawach serwerowych).

- `/alert_pozniej <ID>` — "Odloz na pozniej"
  -> Ustawiam cron przypomnienie za 2h (isolated agentTurn, announce telegram 8565653134).
     Potwierdzam: "Przypomne za 2h."

- `/alert_zalatwione <ID>` — "Zalatwione"
  -> Oznaczam jako zalatwione. Krotkie potwierdzenie. Bez dalszych akcji.

## Zasada
Zawsze po polsku, zwiezle (1-2 linie). Bez emoji w odpowiedzi. ID podaje w potwierdzeniu.
Akcje miedzy mna a Sonia — zadnego automatycznego pisania do osob trzecich (Pawel/Victor)
chyba ze Sonia wprost o to poprosi.
