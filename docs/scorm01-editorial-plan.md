# SCORM 01 – projekt redakcji

**Wersja planu:** 1.0.0 · **Data:** 2026-11-13  
**Pakiet:** `raw/1-podstawy-algorytmów.zip` · **Odbiorca:** III rok informatyki  
**Stan:** rozpoczęto pilot pierwszej części; pozostała część pakietu nadal wymaga redakcji merytorycznej.

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
| 01 Wprowadzenie do algorytmów | **W realizacji:** nowa narracja, specyfikacja, liniowe wyszukiwanie, dowód, przypadki brzegowe |
| 02 Definicja i klasyfikacje | Zredukować do precyzyjnej definicji i 2–3 odróżnień pojęciowych; obszerne klasyfikacje wyprowadzić z problemów |
| 03 Pseudokod | Ograniczyć do wprowadzenia i odsyłacza do szczegółów w SCORM 03 |
| 04 Poprawność i złożoność | Zachować tylko motywację, podstawowe rozróżnienie i powiązanie z przykładem; formalizm w SCORM 04 |
| 05 O, Ω, Θ | Usunąć formalne przykłady z SCORM 01; SCORM 05 jako miejsce szczegółowe |
| 06 Przykłady analizy | Zastąpić jednym spójnym przykładem śledzenia i niezmiennika |
| 07 Model RAM | Zastąpić krótką zapowiedzią; pełna definicja SCORM 02 |
| 08 Instrukcje RAM | Przenieść do 02 po naprawie semantyki i kodu |
| 09 Implementacje RAM | Nie publikować niepoprawnych przykładów; korekta w #8, selektywne przeniesienie do 02–03 |
| 10 Analiza RAM | Wyprowadzić do 04 i naprawić pomyłki w sortowaniu |
| 11 Podsumowanie | Jedno zwięzłe zakończenie i logiczny pomost do następnej części; bez duplikatów |

## Wdrożenie i kontrola jakości

Przejście od źródłowej wersji Rise do ZIP realizuje wersjonowana nakładka `editorial/scorm01/lesson-01.json`. Dzięki temu zmiany są przeglądalne w PR, a archiwum źródłowe pozostaje niezmienne. Adapter sprawdza identyfikator kursu, identyfikator pierwszej lekcji i identyfikatory wszystkich bloków, zanim wymieni tekst i usunie zbędne bloki.

**Kontrole automatyczne:** test jednostkowy danych, odmowa nieznanego schematu, regresja wszystkich 20 pakietów, pełny round-trip ZIP/SCORM 1.2, brak quizów i sprawdzań wiedzy, kontrakt raportowania `completed` bez `score.raw`.

**Kontrola dydaktyczna (ręczna):** przeczytać treść w działającym interfejsie Rise; sprawdzić czy pseudokod i tabelka śladów mają zgodną indeksację, czy przykłady nie wprowadzają nowego błędu, czy obrazy pasują do nowej narracji, i czy żadna interakcja nie blokuje przejścia do następnej części.

**Kontrola Moodle (ręczna):** nowa aktywność, testowy student, ukończenie po 100%, wznowienie `suspend_data`, brak punktowej oceny i niezależny test Moodle.

Powiązania: [Epic #6](https://github.com/MatPomGit/aisd/issues/6), [narracja #9](https://github.com/MatPomGit/aisd/issues/9), [korekta RAM #8](https://github.com/MatPomGit/aisd/issues/8), [walidacja #12](https://github.com/MatPomGit/aisd/issues/12).
