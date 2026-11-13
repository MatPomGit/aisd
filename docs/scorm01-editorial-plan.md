# SCORM 01 – projekt redakcji

**Wersja planu:** 2.0.0 · **Data:** 2026-11-13  
**Pakiet:** `raw/1-podstawy-algorytmów.zip` · **Odbiorca:** III rok informatyki  
**Stan:** nakładki redakcyjne obejmują **11 z 11 części**; pakiet pozostaje w statusie Draft do przeglądu wizualnego, niezależnej recenzji merytorycznej i testu integracyjnego Moodle.

## Teza dydaktyczna

Student powinien przejść drogę od nieprecyzyjnego zadania do algorytmu, którego wynik można uzasadnić. Przewodnim przykładem jest **odnalezienie pierwszego wystąpienia identyfikatora** w nieposortowanej tablicy danych. Wyszukiwanie liniowe jest wystarczająco proste, by ujawnić problem specyfikacji, przypadku brzegowego, niezmiennika pętli i analizy kosztu bez rozbudowy zaplecza teoretycznego.

### Model docelowego rozdziału

| Sekcja | Pytanie prowadzące | Cel konkretnej części | Planowana długość |
|---|---|---|---:|
| 1. Zanim napiszemy program | Co dokładnie znaczy „znajdź rekord”? | Dane, wynik, najwcześniejsze wystąpienie, brak wyniku | 250–300 słów |
| 2. Co sprawia, że to algorytm? | Czym algorytm różni się od intencji i kodu? | Jednoznaczność, określona dziedzina wejścia, warunki zakończenia | 250–350 słów |
| 3. Pierwsze rozwiązanie | Jak znaleźć najwcześniejszy indeks? | Pseudokod i ślad wykonania | 350–450 słów |
| 4. Sprawdzamy przypadki brzegowe | Co z duplikatami, brakiem wartości, pustą tablicą? | Cztery przykłady, śledzenie zmiennych | 300–400 słów |
| 5. Uzasadniamy poprawność | Skąd wiadomo, że wynik jest najmniejszym indeksem? | Niezmiennik, zakończenie, argument o poprawności | 350–450 słów |
| 6. Ile kosztuje rozwiązanie? | Co rośnie wraz z liczbą danych? | 1 do n porównań, pamięć O(1), rola założeń | 250–350 słów |

Wielkości w tabeli są orientacyjne, a suma obejmuje narrację i objaśnienia przykładów. Usuwanie treści nie może naruszyć poprawności logicznej lub definicyjnej.

## Zasady redakcji

- Rozpoczynać sekcję konkretnym dylematem, nie etykietą typu „W tej lekcji dowiesz się”.
- Każda nowa definicja ma wynikać z poprzedniego przykładu; nie poprzedzać każdej sekcji powtórną motywacją o „fundamencie informatyki”.
- Terminów `pseudokod`, `program` i `algorytm` nie używać zamiennie.
- Prezentować kompletny pseudokod. W przykładach nie zastępować kodu wielokropkiem i narracją „to jest proste”.
- Dla algorytmu z pętlą podać specyfikację, warunek zakończenia, niezmiennik i co najmniej jeden przypadek obalający typowy błędny pomysł.
- Liczyć konkretne operacje przed przejściem do asymptotycznych oznaczeń, bez formalnego rozwijania tematu notacji, który należy do SCORM 05.
- Zachować tylko interakcje pomagające prześledzić wykonanie; test końcowy i `knowledgeCheck` pozostają poza SCORM.
- Nie zmieniać znaczenia starych przykładów RAM „w locie”; naprawić je osobno w #8, uzgadniając semantykę maszyny.

## Macierz przeniesienia treści źródłowej

| Część źródłowa SCORM 01 | Działanie |
|---|---|
| 01 Wprowadzenie do algorytmów | **Zredagowano:** specyfikacja, wyszukiwanie liniowe, dowód, przypadki brzegowe |
| 02 Definicja i klasyfikacje | **Zredagowano:** kontrprzykład na nieposortowanej tablicy; osobno terminacja, poprawność, iteracja, rekurencja, randomizacja i niedeterminizm |
| 03 Pseudokod | **Zredagowano:** jasne konwencje, poprawny pseudokod, równoważny program w Pythonie i ślad wykonania; szczegóły reprezentacji w SCORM 03 |
| 04 Poprawność i złożoność | **Zredagowano:** poprawność częściowa/całkowita, niezmiennik, zakończenie, koszt 1–n porównań i średnia pod jawnym założeniem |
| 05 O, Ω, Θ | **Zredagowano i skrócono:** znaczenie rozmiaru wejścia, trzy rodzaje granic i przykład liniowy; formalne rozwinięcie pozostaje w SCORM 05 |
| 06 Przykłady analizy | **Zredagowano:** studium przypadku błędnej optymalizacji, kontrprzykład `[8, 3, 7]`, ślad i uzasadnienie poprawności |
| 07 Model RAM | **Zredagowano:** rola modelu jednostkowego, rejestry, koszt bitowy i granice uproszczenia; pełne rozwinięcie w SCORM 02 |
| 08 Instrukcje RAM | **Zredagowano:** siedmioetapowy ślad `LOAD 1; ADD 2; STORE 3`, suma 3 + 5 i jednoznaczny stan rejestrów |
| 09 Implementacje RAM | **Zredagowano:** kompletny, testowalny program sumowania liczb do zera, jawne założenia `READ`, `LOAD`, `JZERO`, ślad i niezmiennik; usunięto błędne programy NWD i maksimum |
| 10 Analiza RAM | **Zredagowano:** kontrprzykłady, koszt `Θ(m+1)`, warunek obecności zera, rozróżnienie sortowania przez wybór i scalanie |
| 11 Podsumowanie | **Zredagowano:** pięć zasad projektowania, usunięto powtarzane fiszki i błędne definicje, wprowadzono pomost do kolejnych pakietów |

## Stan wykonania i pozostające ryzyka

- Zredagowane: **11 z 11 części dydaktycznych**. Dla każdej istnieje osobna, deklaratywna nakładka, bez modyfikacji `raw/`.
- Pierwsza część utrzymuje algorytm wyszukiwania liniowego jako temat przewodni. Części 02–11 rozdzielają kontrakt problemu, zapis, dowód poprawności oraz intuicję asymptotycznego tempa wzrostu.
- W części 06 przedstawiono pięć kroków niezależnej analizy błędnej optymalizacji i cztery typowe błędy pętli, bez testu końcowego.
- W części 02 usunięto mylące utożsamienie randomizacji z niedeterminizmem. W części 04 jawnie określono warunek dla średniej `(n+1)/2`; w części 05 poprawiono błędne utożsamianie `O` z przypadkiem najgorszym.
- **Nie uznawać SCORM 01 za gotowy do publikacji.** Stare błędne przykłady NWD, maksimum, sortowania i błędna wersja sumowania zostały usunięte z paczki 01; poprawny przykład sumowania jest poddawany testowi emulatora. Pełna naprawa i ewentualna migracja pozostałych przykładów do ich docelowych pakietów jest nadal otwartym zadaniem [#8](https://github.com/MatPomGit/aisd/issues/8). Konieczny pozostaje niezależny przegląd i test Moodle.
- Obecnie zachowano wszystkie **11 identyfikatorów lekcji**, by nie ryzykować niepotwierdzonej migracji stanu wznowienia; celem końcowym jest bardziej zwarta, spójna struktura, co wymaga odrębnych testów nawigacji w Moodle.
- Akceptacja dydaktyczna wymaga wizualnego przeglądu układu bloków Rise po przebudowie i testu na właściwej instancji Moodle. Test statyczny nie zastępuje tych kontroli.

**Szczegółowy wynik recenzji:** [Karta audytu SCORM 01](reviews/scorm01-editorial-review.md), obejmująca 11 części, błędy kodu RAM, testy i bramkę akceptacyjną Moodle.

**Wynik po kontroli renderowania:** [audyt 22 ekranów Rise](reviews/scorm01-browser-qa.md). Automatyczne testy wykazały obecność treści w viewportach, ale nie sprawdziły ręcznie wszystkich rozwijanych bloków i ścieżki Moodle.

## Bramka publikacji na GitHub Pages

Wersje redakcyjne SCORM 01 są **domyślnie niezatwierdzone**. Publiczny katalog Pages przygotowuje beztestową wersję źródłową kursu 01, bez zastosowania nakładek redakcyjnych. Jednocześnie walidacja PR i lokalne przebudowanie kursu 01 stosują wszystkie 11 nakładek, aby przetestować wersję kandydującą bez jej publikowania.

Dopiero po udokumentowaniu **(1) kontroli wszystkich zmienionych bloków w docelowym interfejsie Rise na desktop i mobile**, **(2) akceptacji dydaktycznej przez prowadzącego** oraz **(3) testu importu, nawigacji, ukończenia, `suspend_data` i braku oceny w docelowym Moodle** należy w **odrębnym PR wydawniczym** dodać dokładny identyfikator `scorm01/lessons-01-11@2.0.0` do tablicy `approved_releases` w `editorial/approved-releases.json`. Kontrola CI weryfikuje zgodność identyfikatora, ale nie zastępuje akceptacji człowieka. Zrzuty ekranu SCORM Studio z CI są tylko kontrolą edytora; nie stanowią dowodu poprawnego renderowania kursu w Rise/Moodle.

## Wdrożenie i kontrola jakości

Przejście od źródłowej wersji Rise do ZIP realizują wersjonowane nakładki `editorial/scorm01/lesson-01.json` do `lesson-11.json`. Dzięki temu zmiany są przeglądalne w PR, a archiwum źródłowe pozostaje niezmienne. Adapter sprawdza identyfikator kursu, indeks i identyfikator lekcji oraz pełną sekwencję identyfikatorów bloków po usunięciu quizów, zanim wymieni treść i usunie zbędne bloki.

**Kontrole automatyczne:** test jednostkowy danych, odmowa nieznanego schematu, regresja wszystkich 20 pakietów, pełny round-trip ZIP/SCORM 1.2, brak quizów i sprawdzań wiedzy, kontrakt raportowania `completed` bez `score.raw`.

**Kontrola dydaktyczna (ręczna):** przeczytać treść w działającym interfejsie Rise; sprawdzić czy pseudokod i tabelka śladów mają zgodną indeksację, czy przykłady nie wprowadzają nowego błędu, czy obrazy pasują do nowej narracji, i czy żadna interakcja nie blokuje przejścia do następnej części.

**Kontrola Moodle (ręczna):** nowa aktywność, testowy student, ukończenie po 100%, wznowienie `suspend_data`, brak punktowej oceny i niezależny test Moodle.

Powiązania: [Epic #6](https://github.com/MatPomGit/aisd/issues/6), [narracja #9](https://github.com/MatPomGit/aisd/issues/9), [korekta RAM #8](https://github.com/MatPomGit/aisd/issues/8), [walidacja #12](https://github.com/MatPomGit/aisd/issues/12).
