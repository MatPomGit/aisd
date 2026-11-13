# Standard redakcyjny AIiSD: teoria, przykłady i polszczyzna

**Wersja:** 0.1.0 · **Data:** 2026-11-13  
**Zastosowanie:** wszystkie 20 pakietów SCORM dla studentów III roku informatyki.  
**Status:** wytyczne początkowe, do dopracowania podczas redakcji SCORM 01.

## Narracja

Materiał powinien być czytelny jak dobrze napisany rozdział podręcznika. Zaczyna się od problemu, nie od katalogu definicji. Kolejność typowa: **pytanie → specyfikacja → decyzja projektowa → algorytm → śledzenie → uzasadnienie poprawności → koszt → ograniczenia**.

Każdy akapit wnosi nową informację: definiuje, wyjaśnia, uzasadnia lub rozwija przykład. Jeżeli pełni wyłącznie rolę reklamową („to kluczowy fundament”), usunąć go. Nie wstawiać instrukcji „zapoznaj się z poniższymi fiszkami”, jeśli interfejs sam jednoznacznie pokazuje fiszki.

## Styl i słownictwo

| Unikać | Preferować |
|---|---|
| „W tej lekcji skupimy się na...” | Zacząć od konkretnego problemu |
| „Jasne określenie celów ułatwia...” | Podać mierzalny cel bez komentarza |
| „Będziesz miał okazję...” | „Zapisz”, „Porównaj”, „Oblicz”, „Wykaż” |
| „Algorytmy stanowią kluczowy fundament...” | Pokazać, do czego konkretna metoda jest potrzebna |
| „Implementacja w pseudokodzie” | „Opis w pseudokodzie”; „implementacja w języku X” |
| „Dla dużych danych algorytm jest bardzo wydajny” | Określić funkcję kosztu i założenia |
| „Zawsze zwraca poprawny wynik” | Podać warunek i zbiór dopuszczalnych wejść |
| „Najbardziej optymalny” | „Optymalny” lub „o mniejszym koszcie” |
| „Rozwiązanie jest lepsze” | Wskazać metrykę: czas, pamięć, prostotę, warunki |
| „Dzięki temu będziesz przygotowany...” | Zaproponować naturalne pytanie otwierające kolejny temat |

Stosować jeden polski język interfejsu i opisu. Angielskie nazwy rozkazów RAM lub notacji zachować, gdy są elementem formalizmu. Unikać nieuzasadnionych wykrzykników, nieprecyzyjnych porównań i pustych akapitów HTML (`<p></p>`).

## Dokładność merytoryczna

- **Algorytm** nie jest tym samym co program, pseudokod ani wynik obliczenia.
- **Poprawność częściowa**: jeśli obliczenie się zakończy, wynik spełnia specyfikację. **Poprawność całkowita**: dodatkowo algorytm kończy działanie dla każdego dopuszczalnego wejścia.
- **Niezmiennik pętli** wymaga uzasadnienia inicjalizacji, zachowania i wniosku po zakończeniu.
- **Model kosztu** musi być nazwany; w modelu RAM nie zawsze można ignorować długość liczb i rozmiar pamięci.
- **Big O** jest asymptotyczną granicą górną funkcji kosztu, nie synonimem „najgorszego przypadku”. Funkcję kosztu można definiować dla najgorszych, średnich lub innych przypadków.
- **Losowość** i **niedeterminizm** są różnymi pojęciami. W opisie klasyfikacji nie wolno utożsamiać algorytmu randomizowanego z niedeterministycznym.
- Każdy pseudokod musi określać indeksowanie, konwencje wejścia/wyjścia i zachowanie przy danych brzegowych. Niedopuszczalne są niekompletne „programy” z wielokropkami prezentowane jako działające implementacje.
- W analizie sortowania rozróżniać algorytm, klasę metod i przypadek wejściowy. Nie przypisywać (O(n^2)) całemu sortowaniu przez porównania.

## Elementy wizualne i interaktywne

Ilustracja lub interakcja musi objaśniać rzeczywiste zjawisko: zmianę indeksu, stanu stosu, układu tablicy, granic wyszukiwania lub zależność kosztu od rozmiaru. Jedna czytelna wizualizacja stanu jest cenniejsza niż seria dekoracyjnych fiszek.

Elementy sprawdzania wiedzy są z definicji poza pakietem. Nie należy odtwarzać `knowledgeCheck` ani quizów Rise podczas redakcji. Ocena odbywa się przez osobny test Moodle.

## Lista kontrolna przed publikacją

- [ ] Co najmniej jeden konkretny problem ze specyfikacją i poprawnymi przykładami.
- [ ] Warunki brzegowe oraz kontrprzykład dla typowego błędnego pomysłu.
- [ ] Pseudokod możliwy do śledzenia krok po kroku, bez luk w instrukcjach.
- [ ] Jawne założenia przy twierdzeniach o poprawności i złożoności.
- [ ] Narracja bez powtarzanych celów i zakończeń.
- [ ] Poprawna polszczyzna, nazewnictwo i składnia HTML.
- [ ] Brak testów/ocen w SCORM; komplet zasobów i poprawne raportowanie ukończenia.
- [ ] Kontrola wizualna wszystkich zmienionych bloków w przeglądarce.
- [ ] Próba integracyjna w Moodle przed użyciem ze studentami.

Powiązane zadania: [#6](https://github.com/MatPomGit/aisd/issues/6), [#11](https://github.com/MatPomGit/aisd/issues/11).
