# Quizy do wykładów AIiSD (W01–W20)

**Wersja:** 1.2.0  
**Data:** 2026-11-17  
**Zakres:** 20 oddzielnych banków, po 20 pytań jednokrotnego wyboru (łącznie 400 pytań).

## Organizacja

Każdy plik `quiz_wXX.gift` zawiera 20 pytań. W wersji 1.2.0 zredagowano większość banku: wyeliminowano podpowiedzi stylistyczne, przebudowano dystraktory i zastąpiono część powtarzalnych zadań analizą konkretnych przypadków. Każdy bank odpowiada wykładowi XX w kolejności kursu. Pliki są zgodne z formatem **GIFT** służącym do importu do bazy pytań Moodle. Każde pytanie zawiera cztery merytorycznie powiązane możliwości, dokładnie jedną prawidłową odpowiedź oraz informację zwrotną z uzasadnieniem.

- `quiz_w01.gift`–`quiz_w05.gift`: podstawy algorytmiki, RAM, pseudokod, analiza kosztu, notacje asymptotyczne;
- `quiz_w06.gift`–`quiz_w10.gift`: tablice, macierze, rekurencja, listy liniowe, stosy;
- `quiz_w11.gift`–`quiz_w15.gift`: kolejki, drzewa, BST, kopce, grafy;
- `quiz_w16.gift`–`quiz_w20.gift`: przeszukiwanie, teoria sortowania, algorytmy sortowania, metody projektowania.

## Import do Moodle

1. W Moodle otwórz **Baza pytań → Import → GIFT**.
2. Dla każdego wykładu utwórz odrębną kategorię, np. `AIiSD / W01`, i zaimportuj odpowiadający jej plik UTF-8.
3. Utwórz **osobną aktywność Quiz** dla każdej kategorii. Nie przywracaj testów w pakietach Rise/SCORM.
4. Włącz losową kolejność odpowiedzi i, jeśli jest to uzasadnione dydaktycznie, losowanie pytań z kategorii.
5. Przed ocenianym użyciem przetestuj podgląd pytań, zapis ocen, termin wyświetlania uzasadnień i ograniczenia podejść na koncie testowym studenta.

## Konstrukcja pytań

Priorytetem jest **znajomość materiału i umiejętność zastosowania algorytmu**, a nie eliminacja absurdalnych odpowiedzi. Zastosowano krótkie ślady wykonania, koszty operacji, niezmienniki, warunki brzegowe, porównanie implementacji, stabilność i ograniczenia metod. Dystraktory odnoszą się do tych samych pojęć co odpowiedź prawidłowa; nie stosowano odpowiedzi typu „wszystkie powyższe” ani rozstrzygnięć opartych wyłącznie na stylu sformułowania.

Banki zostały opracowane na podstawie mapy `docs/curriculum-map.md`, tytułów i struktury dostępnych pakietów oraz weryfikowalnych własności algorytmicznych. Nie jest to formalna certyfikacja zgodności każdego pytania z każdym akapitem wszystkich źródłowych lekcji. Przed ocenianiem należy porównać pytania z aktualnie publikowaną wersją danego wykładu. To szczególnie ważne podczas trwającej redakcji materiałów 02–20.

## Reguły redakcji dystraktorów

- Każda błędna odpowiedź ma reprezentować **rozpoznawalne nieporozumienie merytoryczne**: błąd graniczny, błędną kolejność operacji, pomylenie modelu kosztu, niezmiennika albo własności podobnych struktur.
- Wszystkie cztery warianty odnoszą się do **tego samego pytania i mają porównywalny poziom szczegółowości**. Odpowiedź liczbowa nie powinna konkurować z trzema długimi opisami, a wyłącznie dystraktory nie powinny zawierać objaśnień przyczynowych.
- Nie stosujemy opcji absurdalnych ani celowo niepoprawnych stylistycznie. Fałszywość wariantu ma wynikać z **wiedzy o algorytmie**, a nie z językowej eliminacji.
- W zadaniach o śledzeniu kodu trzeba jednoznacznie podać warunki początkowe, semantykę operacji, konwencję indeksowania i moment sprawdzania warunku.
- Należy zachować pojedynczą poprawną odpowiedź, uzasadnienie oraz identyfikator pytania, a przy imporcie do Moodle losować kolejność odpowiedzi.

Powyższe zasady ograniczają zgadywanie na podstawie konstrukcji testu. Nie gwarantują, że każde pytanie jest odporne na eliminację bez wiedzy; wymagałoby to pilotażu i analizy psychometrycznej odpowiedzi studentów (trudność, moc różnicująca, częstość wyboru poszczególnych dystraktorów).

## Kontrola jakości

```bash
python3 scripts/validate_quizzes.py
```

Walidator sprawdza liczbę plików, identyfikatory, liczbę pytań, cztery różne odpowiedzi, pojedynczy klucz, uzasadnienie oraz rozkład pozycji odpowiedzi prawidłowych. W każdym banku pozycje poprawnych odpowiedzi rozłożono po 5 na każdą z czterech możliwości. Nie zastępuje niezależnej recenzji poprawności naukowej ani testowego importu do Moodle. Te dwa etapy pozostają do wykonania przed ocenianiem.

**Bezpieczeństwo oceniania:** repozytorium jest publiczne, a format GIFT zawiera jawne klucze odpowiedzi. Nie używaj tych plików bezpośrednio do egzaminu o wysokiej stawce. Do takiego zastosowania przenieś bank do prywatnego miejsca, zachowaj kontrolę dostępu i przygotuj alternatywne, nieopublikowane wersje zadań.

**Granica techniczna:** quizy to osobne pliki źródłowe. Nie modyfikują `raw/*.zip`, `files/scorm_XX/`, mechanizmu ukończenia SCORM ani dziennika ocen Moodle.
