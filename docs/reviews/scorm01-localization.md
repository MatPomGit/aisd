# SCORM 01 — lokalizacja interfejsu Rise

**Wersja:** 1.0.0 · **Data:** 2026-11-13 · **Stan:** nakładka robocza, testy i odbiór w toku.

## Problem

Treść dydaktyczna SCORM 01 jest polska, ale oryginalny eksport Rise 360 wykorzystuje angielski zestaw etykiet. W rzeczywistym odtwarzaczu występowały m.in. „EXIT COURSE”, „Step 1”, „Swipe to continue” i „By”. Są to etykiety interfejsu Rise, a nie akapity lekcji.

## Zakres implementacji

Plik `editorial/scorm01/labels-pl.json` zawiera **65 jawnych par** `expected` → `replace`. Obejmuje widoczne komunikaty kursu, nawigację, podstawowe komponenty procesu i część etykiet dla czytników ekranu. Adapter `scripts/scorm_editorial.py` sprawdza identyfikator pierwotnego `labelSet`, nazwę i wartość źródłową każdego modyfikowanego pola; obca wersja źródła powoduje odmowę przebudowy.

Wydanie robocze ustawia `labelSet.iso639Code = "pl"` oraz `<html lang="pl">` w odtwarzaczu. **Nie zmienia** `course.locale` ani `course.defaultLocaleId`. Oba pola są `null` w źródle; niezweryfikowana podmiana na `"pl"` zatrzymywała inicjalizację interfejsu i została wycofana. Oryginalny `raw/` pozostaje niezmienny. Publiczny wariant SCORM 01 bez zatwierdzenia nadal nie otrzymuje tej nakładki.

## Dowody i ograniczenia

Zestaw źródłowy ma **272 etykiety**, z których 65 zostało objętych poprawką. Jest to lokalizacja częściowa, **nie** kompletny polski zestaw Rise. Kod i testy regresyjne sprawdzają zgodność mapowania, a scenariusz Chromium porównuje komunikaty startowe, wyjścia, nazwy kroku i gestu przewijania z rzeczywistym odtwarzaczem. Ostateczny wynik tych testów należy weryfikować w bieżącym workflow PR #14; sam zapis polskich wartości w JSON nie dowodzi, że użytkownik widzi je na ekranie.

Producent opisuje poprawne tworzenie osobnych zestawów językowych i tłumaczenie etykiet czytników ekranu, również przez XLIFF 1.2: [Articulate Rise 360, edycja etykiet](https://www.articulatesupport.com/article/Rise-360-Edit-Text-Labels). Przed publikacją należy skontrolować i ewentualnie przetłumaczyć **wszystkie faktycznie używane** w kursie etykiety i ich poprawną wymowę w czytniku ekranu. Zmiana kodu ISO nie zastępuje pełnego testu dostępności.

## Odbiór

- [ ] Przejście najnowszego CI wraz z renderowaniem w Chromium.
- [ ] Przegląd tekstów na 11 lekcjach desktop i mobile, w tym rozwijanych interakcji.
- [ ] Kontrola `lang` i dostępności nazw/stanów elementów w czytniku ekranu.
- [ ] Potwierdzenie działania na testowej instancji Moodle zgodnie z [protokołem](scorm01-moodle-acceptance.md).
- [ ] Potwierdzenie prowadzącego. Dopiero osobny PR wydawniczy może zatwierdzić publiczny SCORM 01.
