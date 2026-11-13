# SCORM 01 — niezależny audyt renderowania Rise w Chromium

**Wersja:** 1.0.0 · **Data:** 2026-11-13 · **PR:** [#14](https://github.com/MatPomGit/aisd/pull/14) · **SHA:** `94799e47eabef1bdab3b5b3ca2033f232fe1b402`

## Metoda i zakres

Źródłem jest przebudowany pakiet `raw/1-podstawy-algorytmów.zip` z zastosowanymi 11 nakładkami redakcyjnymi. Test `tests/scorm_learner.browser.mjs` rozpakowuje go do lokalnego serwera HTTP, uruchamia **rzeczywisty interfejs ucznia Articulate Rise** w Chromium, a zgodność z LMS zastępuje niewydawniczym, izolowanym adapterem `tests/scorm_learner_harness.html`. Nie loguje się do Moodle i nie przekazuje materiałów do produkcji.

Dla każdej lekcji test ustawia trasę `#/lessons/<id>`, wyszukuje unikatowy fragment opublikowanego akapitu, przewija do niego i sprawdza przecięcie z widocznym viewportem. Następnie przechwytuje ekran i mierzy poziome przepełnienie dokumentu. Bez kontroli elementu widocznego na ekranie test mógł fałszywie przejść na podstawie tekstu już obecnego w DOM.

**Rozdzielczości:** 1440 × 900 (desktop), 390 × 844 (mobile). **Zakres:** 11 lekcji × 2 = 22 ekrany. W skrypcie dodatkowo sprawdzane są błędy `pageerror` i wywołania `SetScore` podczas przeglądania.

## Wynik i dowody

- [PASS: workflow SCORM Studio / Pages](https://github.com/MatPomGit/aisd/actions/runs/43457313786) dla powyższego SHA; artefakt `scorm01-editor-and-rise-qa-65` z 22 zrzutami Rise, dwoma ekranami Studio i `scorm-learner-screenshots/report.json`.
- **11/11** lekcji: unikatowy fragment akapitu został rzeczywiście wyświetlony i przewinięty do obszaru widocznego; zarówno na desktopie, jak i mobile.
- **22/22** ekranów: brak poziomego przepełnienia `documentElement` (0 px według raportu); wszystkie oczekiwane akapity przecinają viewport.
- **0** błędów `pageerror` i **0** wywołań `SetScore` w tej sesji odtwarzacza. Nie jest to równoznaczne z badaniem pełnej ścieżki ukończenia w LMS.
- Zrzuty z pierwszej iteracji testu pokazywały niektóre puste viewporty, mimo obecności tekstu w DOM. Zmieniono metodę: test zawsze przewija do akapitu i kontroluje jego pozycję przed wykonaniem zdjęcia.

## Ograniczenia i otwarte bramki

To **przegląd renderowania pierwszych akapitów**, nie wizualna recenzja każdego bloku. Nie wykonano pełnego cyklu kliknięć i kontroli ukrytych treści w zakładkach, akordeonach, procesach i listach, kontroli czytnika ekranu ani niezależnego manualnego testu klawiatury w odtwarzaczu Rise.

Nie wykonano testów na **docelowej instancji Moodle**: import, autentyczne `suspend_data` po zamknięciu i ponownym otwarciu sesji, `cmi.core.lesson_status`, brak `cmi.core.score.raw`, dziennik ocen i ukończenie 100%. Te punkty nadal wymagają odrębnej akceptacji i nie mogą zostać oznaczone jako PASS na podstawie emulatora LMS.

Przed zatwierdzeniem wydania wymagane pozostają: (1) ręczny przegląd wszystkich 11 lekcji i ich interakcji w rzeczywistym widoku ucznia, (2) pełna weryfikacja Moodle, (3) jawna akceptacja dydaktyczna prowadzącego. Do tego czasu `editorial/approved-releases.json` pozostaje z pustą listą wydań.
