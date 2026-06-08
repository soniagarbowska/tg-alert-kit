# Inwentaryzacja realnych komunikatow systemu (2026-06-08)

Zrodla: `python3 ~/wiki/scripts/alert.py`, skrypty `~/wiki/scripts/*.py` wolajace
`notify_sonia.notify(monitor, type, about, raw, severity, bot, decision, body)`,
`~/docs/HARMONOGRAM.md`. To sa PRAWDZIWE komunikaty, nie wymyslone.

## Typy (type) -> co zawiera -> bot -> przepis docelowy

### mail  (mail_watcher, wiki_mail_cron)  -> Victor / Hugo
Nowy mail na biuro@. Dane realne:
  nadawca, temat, streszczenie tresci, SYTUACJA (kontekst najmu/koszt), AKCJA (co zrobic / termin).
Przyklady: M00007 (zarzadca najmu: termin serwisu drzwi), M00014 (faktura Play 95 zl, termin 22.06).
-> przepis: **mail** (pojedynczy mail: naglowek nadawca/temat + pola + SYTUACJA jako tekst + AKCJA jako cytat).
   Wiele maili naraz -> **digest**.

### sejf  (monitor sejf)  -> decyzja
Konflikt/zmiana danych kontrahenta CRM. Dane realne (M00013):
  sprawa (np. «Damrota»), na czym polega konflikt (numer telefonu …200 -> …888),
  OPCJE: 1) NOWY (+/-)  2) STARY (+/-), REKOMENDACJA, "glosowka: NOWY/STARY", kod 2FA (POKAZ).
-> przepis: **decision** (opcje z plusami/minusami + rekomendacja + jak odpowiedziec).
   Maskowanie: czesc danych ukryta, pelne po 2FA -> uzywa body/passthrough.

### sec  (sonia-sec-scan.sh, 10:00 i 22:00)  -> Hugo
Przeglad bezpieczenstwa LUB konkretny incydent. Dane realne (M00022, M00018):
  STATUS_OK: fail2ban, nieudane/udane SSH, lynis, dysk %, usluga gateway, porty, mapa ekspozycji WWW.
  INCYDENT: nieudane logowania (IP, kraj, liczba prob, cel, status fail2ban) / nowe logowanie.
-> przepis: **status** (gdy OK, zielony, spokojny ton) albo **alert** (gdy incydent, czerwony/zolty + przyciski to_ja/nie_ja).

### tech  (cron_watchdog, provider_watchdog, alert_provider)  -> Hugo, severity=critical
Awaria infrastruktury: cron padl (exit-code), provider LLM nie odpowiada, usluga nieaktywna.
  about = co padlo, raw = szczegoly (kod wyjscia, usluga, czas).
-> przepis: **alert** severity=critical (czerwony) + ew. przycisk pozniej/zalatwione.

### wiki  (wiki_quality 23:30, wiki_crosscheck 23:45)  -> Victor
Jakosc/sprzecznosci bazy wiedzy najmu. Dane:
  wiki_crosscheck: ten sam adres -> rozjazd stawek/dat -> REVIEW (lista sprzecznosci).
  wiki_quality: grounding/recall/faithfulness ponizej progu.
-> przepis: **digest** (lista sprzecznosci/uchybien jako pozycje) albo **alert** (pojedyncze).

### crm  (crm_quality 02:45)  -> 
Audyt CRM zero-FP: duplikaty kontaktow, osierocone relacje, leady bez kontaktu, role bez lokalu.
  Alert tylko o NOWYCH problemach.
-> przepis: **digest** (lista znalezisk per kategoria).

### skille  (skill_proposer)  ->
Propozycje nowych skilli z powtarzalnych wzorcow. about = ile propozycji, debug = gdzie plik.
-> przepis: **digest** lub **status** (lekki, informacyjny).

### seo  (seo_digest)  -> Bruno, severity=info
Okazje SEO: duzo wyswietlen + niski CTR. Skrot najlepszych okazji.
-> przepis: **digest** (pozycje: zapytanie, wyswietlenia, CTR).

## Wagi realne
critical -> tech (awarie), sec (wlam/incydent)
warn     -> wiki (sprzecznosci), sejf (decyzja), sec (podejrzane)
info     -> mail (zwykly), seo, skille, sec (przeglad OK -> raczej ok/zielony)
ok       -> sec przeglad bez zagrozen, status przywrocenia

## Boty (routing — kто wysyla)
hugo-works  -> tech, sec (bezpieczenstwo/infra = domena Hugo)
victor-estate -> mail, wiki, sejf, crm (najem = domena Victora)
bruno-web   -> seo (strona WWW)

## Wniosek dla kitu
Potrzebne przepisy: alert, digest, status (sa) + **mail**, **decision** (DOdac — to realne ksztalty).
Zadnych kosiarek: dane to najem, faktury, bezpieczenstwo serwera, jakosc CRM/wiki.

## Polityka PII (zasada Soni, audyt 2026-06-08)
Maskowanie = JEDNO zrodlo: `~/wiki/scripts/mask_sensitive.py` (podpiete przez pii.py).
- MASKUJ tylko twarde dane wrazliwe: PESEL, nr dowodu, data urodzenia, konto/IBAN,
  NIP, nr ksiegi wieczystej.
- NIE maskuj: imie, nazwisko, adres, TELEFON, e-mail (to NIE sa dane wrazliwe).
- compose() domyslnie przepuszcza tekst przez te polityke (mask_pii=True).
- Przycisk "Pokaz pelne (2FA)" tylko gdy COS faktycznie zamaskowano (has_masked).
  Telefon/nazwisko pokazujemy wprost -> bez 2FA, bo nie ma czego odslaniac.
- W komunikacie podawaj KTO (imie i nazwisko), zeby bylo wiadomo kogo dotyczy.
