# SCORM 01 — karta audytu po redakcji

**Wersja:** 1.0.0 · **Data:** 2026-11-13 · **Stan:** redakcja tekstu 11/11 części; kontrola LMS i akceptacja dydaktyczna oczekują.  
**Pakiet źródłowy:** `raw/1-podstawy-algorytmów.zip` (nietykalny)  
**Przebudowa:** `editorial/scorm01/lesson-01.json` … `lesson-11.json`  
**Zadania:** [#6](https://github.com/MatPomGit/aisd/issues/6), [#8](https://github.com/MatPomGit/aisd/issues/8), [#10](https://github.com/MatPomGit/aisd/issues/10), [#12](https://github.com/MatPomGit/aisd/issues/12) · **PR:** [#14](https://github.com/MatPomGit/aisd/pull/14)

## 1. Wyniki porównania

Tekst we wszystkich 11 częściach zmniejszył się szacunkowo z **9169 do 4515 słów (−51%)**. Obliczenie dotyczy bloków źródłowych Rise i wynikowych bloków tekstowych, wraz z eliminacją bloków oceniania; liczby nie są czasem potrzebnym na przeczytanie materiału. Docelowa długość 1800–2300 słów z pierwotnego planu nie została osiągnięta: świadomie zachowano 11 odrębnych identyfikatorów lekcji dla bezpieczeństwa danych wznowienia w Moodle. Dalsze scalenie wymaga testów migracji stanu; nie należy skracać kosztem argumentów poprawności.

| Część | Nowa funkcja dydaktyczna | Wynik redakcyjny | Otwarte ryzyko |
|---|---|---|---|
| 01 | Wyszukiwanie pierwszego identyfikatora, kontrakt i niezmiennik | Przepisano | Podgląd nawigacji/typografii |
| 02 | Warunki poprawności, deterministyczność i randomizacja | Przepisano, poprawiono terminologię | Kontrola interakcji accordion |
| 03 | Pseudokod i program Python, ślad | Przepisano | Czytelność listingów na telefonie |
| 04 | Poprawność częściowa/całkowita, średnia przy jawnym rozkładzie | Przepisano | Przegląd matematyczny sformułowań |
| 05 | Rozmiar wejścia, intuicja O/Ω/Θ | Skrócono | Szczegółowe dowody w SCORM 05 |
| 06 | Kontrprzykład błędnej optymalizacji | Przepisano | Wizualizacja pięciu etapów |
| 07 | Model RAM i jego założenia kosztowe | Skrócono | Rozwinięcie w SCORM 02 |
| 08 | Ślad `LOAD; ADD; STORE` na rejestrach | Przepisano | Kontrola czytelności sekwencji |
| 09 | Poprawny program sumujący do zera | Usunięto błędne NWD/maksimum; wykonano nowy kod | Zgodność wariantu RAM z materiałem SCORM 02 |
| 10 | Niezmiennik, koszt Θ(m+1), granice wnioskowania | Skorygowano twierdzenia o sortowaniu | Dalsza weryfikacja przykładów sortowania w pakietach 17–19 |
| 11 | Pięć zasad projektowania | Usunięto powtarzające się fiszki, zwięzłe zakończenie | Brak |

## 2. Najważniejsze ustalenia metodologiczne

| ID | Waga pierwotna | Problem w źródle | Korekta w SCORM 01 | Stan |
|---|---|---|---|---|
| F01 | P0 | `READ 0; JZERO` sprawdza nieaktualny sumator zamiast świeżo wczytanego rejestru | `READ 2; LOAD 2; JZERO`; oddzielna suma w `R[1]` | Poprawiono, test emulatora |
| F02 | P0 | Niepoprawne przekształcenia rejestrów w wersji NWD/Euklidesa | Usunięto błędny kod z pakietu 01; poprawna wersja należy do pełnego kursu RAM | Przeniesienie/naprawa w #8 otwarte |
| F03 | P0 | Niepoprawny program szukający maksimum i niejawna interpretacja zera | Usunięto z pakietu 01 | Przeniesienie/naprawa w #8 otwarte |
| F04 | P0 | Sortowanie z wielokropkiem przedstawione jak kompletny program | Usunięto niepełny listing | Korekta w kursie sortowania otwarta |
| F05 | P1 | Utożsamianie notacji O z najgorszym przypadkiem | Wyjaśniono, że notacja ogranicza funkcję kosztu | Poprawiono w SCORM 01 |
| F06 | P1 | Uogólnienie O(n²) na sortowanie przez porównania | Rozróżniono wybór: Θ(n²), scalanie: O(n log n) | Poprawiono w SCORM 01 |
| F07 | P1 | Randomizację utożsamiano z niedeterminizmem teoretycznym | Oddzielono definicje | Poprawiono w SCORM 01 |
| F08 | P1 | Brak założenia o zerze kończącym strumień i o kosztach operandów | Zdefiniowano dziedzinę wejścia i model jednostkowego kosztu RAM | Poprawiono w SCORM 01 |
| F09 | P1 | Semantyka kolejności slajdów Rise `process`: zapis `intro, summary, step…`, lecz prezentacja `intro, step…, summary` | Skorygowano mapowanie tekstów i numerację w lekcjach 06 i 08, dodano regresję oraz test interaktywny desktop/mobile | Poprawiono i sprawdzono [w Chromium](scorm01-browser-qa.md) |

## 3. Test wykonywalnego kodu RAM

**Wariant modelu:** `READ i` zapisuje następną liczbę do rejestru `R[i]`; `LOAD i` kopiuje rejestr do sumatora, `JZERO` sprawdza sumator; `WRITE i` odczytuje rejestr. Rejestry zawierają liczby całkowite (bez ograniczenia długości w abstrakcyjnym modelu). Zakładamy skończony ciąg zakończony zerem.

Utworzony test odczytuje **faktyczny listing ze zmodyfikowanej lekcji 09**, interpretuje jego instrukcje RAM i sprawdza:

| Wejście | Oczekiwana suma |
|---|---:|
| `[0]` | 0 |
| `[4, −2, 0]` | 2 |
| `[4, −4, 0]` | 0 |
| `[−5, 2, 0]` | −3 |
| `[1, 2, 3, 0]` | 6 |
| `[0, 1, 2]` | 0 (przerwanie na pierwszym zerze) |
| `[5]` | niedopuszczalne wejście: brak zera kończącego |

Weryfikowane są również identyfikatory i kolejność wszystkich 11 lekcji, kompletność zasobów ZIP, manifest, tryb ukończenia, brak quizów i bloków `knowledgeCheck` oraz brak włączonych wcześniej błędnych listingów RAM.

Wniosek z testów jest ograniczony do **zdefiniowanego wariantu modelu** i wymienionych wejść. Poprawność dla wszystkich dopuszczalnych wejść opiera się dodatkowo na niezmienniku sumy już przetworzonych liczb oraz warunku wystąpienia zera kończącego.

## 4. Bramka techniczna i dydaktyczna

- [x] Odtwarzalna redakcja we wszystkich 11 częściach.
- [x] Oryginały ZIP nie są nadpisywane.
- [x] Testy strukturalne i wykonywanie przykładu RAM w testowym interpreterze.
- [x] Przebudowa i kontrola runtime 20 pakietów SCORM 1.2 w CI.
- [x] Test przeglądarkowego otwarcia i eksportu pakietów w SCORM Studio.
- [x] Automatyczny render rzeczywistych lekcji Rise w Chromium: 11/11 × desktop/mobile, 0 px poziomego przepełnienia, zapis 22 ekranów ([raport](scorm01-browser-qa.md)).
- [ ] Ręczny przegląd **każdego zmienionego bloku** w docelowym wyglądzie (różne rozmiary ekranu).
- [ ] Niezależny przegląd językowo-naukowy i akceptacja prowadzącego.
- [ ] Import do testowej aktywności Moodle, nawigacja po wszystkich 11 częściach ([formularz dowodowy](scorm01-moodle-acceptance.md)).
- [ ] Wznowienie `suspend_data`, ukończenie `cmi.core.lesson_status`, brak `cmi.core.score.raw` i kontrola dziennika ocen.
- [ ] Analiza bezpieczeństwa migracji 11 części do krótszej struktury, jeżeli taka konsolidacja zostanie zatwierdzona.

**Decyzja:** redakcja treści jest kompletna; pakiet **nie jest jeszcze zatwierdzony do publikacji studentom**. Automatyczne testy nie zastępują ręcznej oceny w Moodle.

## 5. Literatura odniesienia

- [MIT OpenCourseWare, 6.006 — Introduction to Algorithms](https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/) — algorytmy, niezmienniki, analiza asymptotyczna i sortowanie; rozróżnienie kosztu selection sort oraz merge sort.
- [Wolfram MathWorld — Random Access Machine](https://mathworld.wolfram.com/RandomAccessMachine.html) — definicja abstrakcyjnego modelu RAM i ograniczenia założeń dotyczących długości słowa.
- [Efficient Algorithms, Unit 2: Machines & Models](https://www.wild-inter.net/teaching/ea/02-machines-and-models) — stosunek pomiarów empirycznych do modelu RAM, rodzaje przypadków wejścia oraz notacje asymptotyczne.

Materiały te wspierają ogólne rozróżnienia teoretyczne. Dokładną semantykę rozkazów `READ`, `LOAD`, `JZERO` i `WRITE` zredagowanego przykładu definiuje **ten kurs**; nazwy rozkazów nie narzucają jednej uniwersalnej wersji maszyny RAM.

Standard: [Ocena i przebudowa lekcji](../lesson-review-and-rebuild.md) · [Plan SCORM 01](../scorm01-editorial-plan.md).
