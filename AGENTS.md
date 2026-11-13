# AGENTS.md — zasady pracy nad materiałami AIiSD

**Wersja:** 1.0.0 · **Data:** 2026-11-13  
**Zakres:** całe repozytorium `MatPomGit/aisd`, wszystkie 20 pakietów i wszystkie lekcje wewnątrz każdego pakietu.

## Pierwsza czynność przy każdej zmianie dydaktycznej

Przed modyfikacją materiałów przeczytaj w całości:

1. [Procedurę niezależnej recenzji i przebudowy lekcji](docs/lesson-review-and-rebuild.md) — nadrzędne kryteria dydaktyczne, merytoryczne, językowe i kryteria odbioru.
2. [Szablon raportu recenzji lekcji](docs/templates/lesson-review-template.md) — obowiązkowy ślad oceny i decyzji.
3. [Zasady przebudowy i weryfikacji SCORM](docs/scorm.md) — ograniczenia techniczne, integralność ZIP, sposób raportowania ukończenia.
4. Dokumenty tematyczne w `docs/`, jeśli istnieją dla danego pakietu; sprawdź także otwarte issues i PR dotyczące tego materiału.

**Hierarchia:** bezpieczeństwo i poprawność źródeł → poprawność matematyczna/algorytmiczna → spójność programu 20 pakietów → wartość dydaktyczna → poprawność językowa → estetyka interfejsu. Ładny wygląd nigdy nie usprawiedliwia błędnego algorytmu.

## Wymagany proces

1. **Inwentaryzacja.** Zidentyfikuj numer pakietu, wszystkie jego lekcje, bloki, pseudokody, multimedia, definicje, przykłady i zależności od innych pakietów. Przejrzyj rzeczywiste dane Rise, a nie wyłącznie stronę startową lub spis treści.
2. **Niezależna recenzja.** Weryfikuj twierdzenia i obliczenia samodzielnie. Sprawdź specyfikację, poprawność, zakończenie, niezmienniki, przypadki brzegowe, model kosztu, czas i pamięć. Błędy klasyfikuj według wagi; przedstaw kontrprzykład lub dowód.
3. **Mapa pojęć.** Ustal, gdzie temat jest wprowadzany, gdzie rozwijany, a gdzie tylko przypominany w całej serii 01–20. Nie kopiuj rozwinięć do wielu kursów.
4. **Projekt narracji.** Dla każdej lekcji prowadź czytelnika przez: problem → specyfikację → rozwiązanie → wykonanie → poprawność → koszt/ograniczenia → przejście. Wybierz jeden przewodni przykład lub wyraźnie uzasadnij zmianę przykładu.
5. **Redakcja.** Usuń powtórzenia, puste zapowiedzi, marketingowe frazy, kalki, nieuzasadnione anglicyzmy i pseudo-interakcje. Zachowaj precyzję definicji. Pseudokod musi nadawać się do śledzenia i testowania.
6. **Implementacja odtwarzalna.** Zapisuj zmiany treści w czytelnej, wersjonowanej formie (np. nakładka JSON i walidowany adapter), nie przez ręczne wyszukiwanie/zmianę Base64 lub przypadkowe przepakowanie ZIP.
7. **Walidacja.** Zbuduj zmieniony ZIP, sprawdź manifest, zasoby, niezmienione identyfikatory, brak quizów i `knowledgeCheck`, statyczny kontrakt SCORM, testy brzegowe kodu, wygląd i nawigację w przeglądarce. Rzeczywisty test w Moodle jest osobnym, obowiązkowym warunkiem publikacji studentom.
8. **Raport i PR.** Dołącz kartę według szablonu, zakres zmian, ryzyka, testy i niezweryfikowane założenia. Podaj numery powiązanych issues. Nie zamykaj zadania tylko dlatego, że skrypt zakończył się kodem 0.

## Zasady bezwzględne

- **Źródło prawdy:** `raw/*.zip` to oryginalne eksporty Rise. Nie nadpisuj ich. `files/scorm_XX/` to historyczne rozpakowane kopie, nie źródło produkcyjnego ZIP. Twórz pochodne pakiety z odrębną nazwą.
- **SCORM:** obsługiwany jest tylko rozpoznany format Rise SCORM 1.2. Nie omijaj zabezpieczeń `fail-closed`. Testy/oceny studentów są osobną aktywnością Moodle; w paczce nie przywracaj quizów końcowych ani bloków sprawdzania wiedzy.
- **Dokładność:** nie utożsamiaj algorytmu z implementacją; notacji O z najgorszym przypadkiem; losowości z niedeterminizmem; testów z dowodem. Podaj założenia modelu obliczeń i zakresu danych.
- **Programy przykładowe:** nigdy nie publikuj pseudokodu lub kodu RAM bez ręcznego prześledzenia i testów automatycznych dla poprawnego, granicznego oraz kontrprzykładowego wejścia. Niedokończony kod oznacz jako fragment, a nie pełny program.
- **Czytelność:** materiały dla III roku informatyki mają być naukowo rzetelne, zwarte, narracyjne, bez „lania wody”. Każdy akapit ma mieć uzasadnioną funkcję dydaktyczną. Nie narzucaj sztywnego limitu słów kosztem koniecznych wyjaśnień.
- **Bezpieczeństwo:** nie uruchamiaj skryptów z nieznanych ZIP ani kodu kursu podczas inspekcji. Unikaj niezaufanych zależności i niepewnych narzędzi.
- **Publikacja:** nie umieszczaj na publicznej stronie kursu informacji o wewnętrznych narzędziach organizacji pracy, agentach ani ich procedurach. Publiczne `docs/` opisują jakość materiału, przebudowę SCORM i obsługę kursu, bez wewnętrznej orkiestracji prac.
- **Kontrola zmian:** preferuj małe, recenzowalne PR, z zachowaniem limitu WIP 4/4. Nie scalać z niepoprawnym CI ani z niezamkniętym błędem merytorycznym dotyczącym modyfikowanej lekcji.

## Co oznacza „gotowe”

Dla każdej zmienionej lekcji istnieje kompletna karta recenzji, poprawne i sprawdzone przykłady, spójna narracja, zredagowana polszczyzna, wynik budowania oraz walidacji ZIP i czytelna lista ryzyk. **PASS CI ≠ zatwierdzenie merytoryczne ani zgodność potwierdzona w Moodle.** Stan „gotowe do publikacji studentom” wymaga dodatkowo udokumentowanego testu integracyjnego i akceptacji dydaktycznej.

Zasady dotyczą **każdej** lekcji w **każdym** z 20 pakietów. Nie ograniczaj ich do pilota SCORM 01.
