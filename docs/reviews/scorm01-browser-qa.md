# SCORM 01 — niezależny audyt renderowania Rise w Chromium

**Wersja:** 1.1.0 · **Data:** 2026-11-13 · **PR:** [#14](https://github.com/MatPomGit/aisd/pull/14) · **SHA kandydata po korekcie procesu:** `ff22dae52cee52d7a0991180c5eb1c2573302742` (testy końcowe na tym commicie, kolejne commity dokumentacyjne nie modyfikują pakietu)

## Metoda i zakres

Źródłem jest przebudowany pakiet `raw/1-podstawy-algorytmów.zip` z zastosowanymi 11 nakładkami redakcyjnymi. Test `tests/scorm_learner.browser.mjs` rozpakowuje go do lokalnego serwera HTTP, uruchamia **rzeczywisty interfejs ucznia Articulate Rise** w Chromium, a zgodność z LMS zastępuje niewydawniczym, izolowanym adapterem `tests/scorm_learner_harness.html`. Nie loguje się do Moodle i nie przekazuje materiałów do produkcji.

Dla każdej lekcji test ustawia trasę `#/lessons/<id>`, wyszukuje unikatowy fragment opublikowanego akapitu, przewija do niego i sprawdza przecięcie z widocznym viewportem. Następnie przechwytuje ekran i mierzy poziome przepełnienie dokumentu. Bez kontroli elementu widocznego na ekranie test mógł fałszywie przejść na podstawie tekstu już obecnego w DOM.

**Rozdzielczości:** 1440 × 900 (desktop), 390 × 844 (mobile). **Zakres:** 11 lekcji × 2 = 22 ekrany podstawowe oraz 6 interakcji (akordeon lekcji 02, karta Python w lekcji 03, sekwencja RAM w lekcji 08; każda na desktopie i telefonie). Skrypt sprawdza też skuteczną widoczność tekstu po animacjach, błędy `pageerror` i wywołania `SetScore` podczas przeglądania.

## Wynik i dowody

- [PASS: rzeczywisty odtwarzacz Rise w Chromium, workflow 43463605302](https://github.com/MatPomGit/aisd/actions/runs/43463605302), artefakt `scorm01-editor-and-rise-qa-79`; [PASS: przebudowa i testy SCORM, workflow 43463605212](https://github.com/MatPomGit/aisd/actions/runs/43463605212).
- Raport `scorm-learner-screenshots/report.json`: **22/22** poprawnie wyświetlone początkowe akapity, **6/6** uruchomionych interakcji (3 typy × 2 rozdzielczości), **0** błędów JS, **0** poziomego przepełnienia dokumentu (0 px), **0** wywołań `SetScore` w badanej sesji. Powstało 30 zrzutów odtwarzacza Rise wraz ze zdjęciami diagnostycznymi oraz 2 ekrany SCORM Studio.
- Zweryfikowano rzeczywistą widoczność po przewinięciu i po zakończeniu animacji: element interakcji musi mieć łączną przezroczystość przodków większą niż 0,85 i przecinać obszar ekranu. Jest to wyraźnie silniejsza kontrola niż samo `state: visible` w Playwright.
- **Odkryty i poprawiony błąd merytoryczno-prezentacyjny:** elementy procesu Rise zapisuje jako `intro`, `summary`, a następnie `step`. Wyświetla je jednak jako **wprowadzenie → kroki → podsumowanie**. Nakładki 06 i 08 zostały skorygowane, a nowe testy sprawdzają widoczną kolejność `1…5` oraz `1…7` i odrzucają zmieniony schemat źródłowy. Po zmianach kontrola procesu wykazuje widoczny krok „2. LOAD 1” na desktopie i mobile.
- Na desktopie przejście procesu wykonuje się przyciskiem strzałki, na telefonie przyciskiem `START` rozpoczynającym proces. Testy dostosowano do faktycznego interfejsu użytkownika.

## Aktualizacja: inwentarz wszystkich interakcji i test wznowienia (13.11.2026)

**Commit:** `0863579a6d20a8c674a3d03ee53ec7db233f76c5`.

- [SCORM rebuild and validate, PASS](https://github.com/MatPomGit/aisd/actions/runs/43487615487).
- [SCORM Studio / Rise i symulacja LMS, PASS](https://github.com/MatPomGit/aisd/actions/runs/43487615640). Zrzuty oraz dwa raporty JSON w [artefakcie `scorm01-editor-and-rise-qa-104`](https://github.com/MatPomGit/aisd/actions/runs/43487615640/artifacts/14067937230).
- **22/22 ekranów**: 11 lekcji w rozdzielczościach 1440 × 900 i 390 × 844; brak błędów JS i poziomego przepełnienia.
- **28/28 kontrole struktury interaktywnej**: każda wersja wyświetla dokładnie 8 akordeonów, 4 zestawy zakładek i 2 bloki typu `process`, zgodnie z wynikowym JSON. Kontrola używa rzeczywistych klas Rise: `.blocks-accordion`, `.blocks-tabs`, `.block-process`.
- **6/6 reprezentatywnych interakcji**: otwarcie akordeonu, zakładki z Pythonem i przejście do kolejnego kroku `process` na desktopie i telefonie; weryfikacja widoczności, położenia i przezroczystości wyświetlanej treści.
- **Symulacja LMS**: faktyczny runtime Rise zapisał 407 znaków przykładowego `suspend_data` i zakładkę, odzyskał je po przeładowaniu, nie ukończył kursu przy `finish(99)`, zgłosił `completed` przy `finish(100)`, bez wywołania `SetScore` ani `SetPassed`. Dowód: `scorm-lms-simulation/report.json`.
- Limit `cmi.suspend_data` w SCORM 1.2 wynosi 4096 znaków ([tabela elementów runtime SCORM](https://scorm.com/scorm-explained/technical-scorm/run-time/run-time-reference/)). Zmierzone 407 znaków dotyczy **syntetycznego znacznika stanu**, nie postępu faktycznego studenta przez 11 lekcji.

**Zakres niedomknięty:** zgodność liczby i typu 14 komponentów nie dowodzi funkcjonalności wszystkich przycisków i kart w każdym z nich. Test bezpośrednio aktywuje po jednym przykładzie trzech typów. Ręczny przegląd całych 14 komponentów, klawiatury i czytnika ekranu oraz faktyczna obsługa `suspend_data` i raportowanie w Moodle pozostają obowiązkowe. Symulacji LMS **nie wolno oznaczyć jako PASS testu Moodle**.

## Ograniczenia i otwarte bramki

To **przegląd renderowania pierwszych akapitów**, nie wizualna recenzja każdego bloku. Wykonano **reprezentatywne** interakcje akordeonu, zakładek i procesu; nie przejrzano ręcznie wszystkich rozwijanych bloków, wszystkich kroków procesów i list. Nie wykonano kontroli czytnikiem ekranu ani niezależnego manualnego testu klawiatury w odtwarzaczu Rise.

Nie wykonano testów na **docelowej instancji Moodle**: import, autentyczne `suspend_data` po zamknięciu i ponownym otwarciu sesji, `cmi.core.lesson_status`, brak `cmi.core.score.raw`, dziennik ocen i ukończenie 100%. Te punkty nadal wymagają odrębnej akceptacji i nie mogą zostać oznaczone jako PASS na podstawie emulatora LMS.

Przed zatwierdzeniem wydania wymagane pozostają: (1) ręczny przegląd wszystkich 11 lekcji i ich interakcji w rzeczywistym widoku ucznia, (2) pełna weryfikacja Moodle, (3) jawna akceptacja dydaktyczna prowadzącego. Do tego czasu `editorial/approved-releases.json` pozostaje z pustą listą wydań.
