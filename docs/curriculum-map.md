# Mapa programu: Algorytmy i struktury danych (20 pakietów)

**Wersja:** 0.1.0 · **Data:** 2026-11-13 · **Status:** wstępny plan redakcyjny, wymagający przeglądu wszystkich treści źródłowych.

Ta mapa rozdziela rolę każdej z dwudziestu części. Lista opiera się na tytułach pakietów w `raw/`, a szczegółowa ocena zachodzenia treści dotyczy obecnie przede wszystkim SCORM 01. Nie należy traktować zamierzonych granic tematycznych jako potwierdzenia jakości istniejącego tekstu innych pakietów.

## Architektura kursu

| Pakiet | Rola w sekwencji | Główne osiągnięcie studenta |
|---|---|---|
| 01. Podstawy algorytmów | Myślenie algorytmiczne | Formułuje problem, pisze prosty algorytm, śledzi wykonanie, uzasadnia poprawność i szacuje koszt intuicyjnie |
| 02. Maszyna RAM | Model obliczeń | Definiuje rejestry i semantykę instrukcji, wykonuje program w jednym jawnie przyjętym wariancie RAM |
| 03. Pseudokod i schematy blokowe | Reprezentacja algorytmów | Przekłada specyfikację na jednoznaczny pseudokod i poprawny schemat sterowania |
| 04. Analiza i złożoność algorytmów RAM | Analiza krok po kroku | Rozróżnia poprawność, terminację, koszt jednostkowy i koszt logarytmiczny oraz liczy operacje |
| 05. Notacje asymptotyczne | Formalizacja wzrostu kosztu | Poprawnie stosuje O, Ω, Θ, rozróżnia ograniczenia funkcji kosztu od przypadków wejściowych |
| 06. Tablice jednowymiarowe | Podstawowa struktura danych | Rozumie indeksowanie, dostęp, wyszukiwanie i aktualizacje, koszty zależne od operacji |
| 07. Tablice dwuwymiarowe | Dane macierzowe | Przechodzi po wierszach/kolumnach, rozróżnia fizyczny układ i model indeksowania |
| 08. Rekurencja i struktury dynamiczne | Tworzenie złożonych struktur | Formułuje przypadki bazowe, śledzi stos wywołań, poznaje reprezentację wskaźnikową |
| 09. Listy liniowe | Struktura dynamiczna | Wyjaśnia operacje, warianty implementacji, koszty i przypadki brzegowe |
| 10. Stosy | LIFO | Implementuje push/pop i analizuje zastosowania oraz błędy pustego stosu |
| 11. Kolejki | FIFO | Implementuje enqueue/dequeue, bufor cykliczny i rozróżnia kolejkę zwykłą od priorytetowej |
| 12. Podstawy drzew | Hierarchia | Opisuje korzeń, dzieci, liście, wysokość, przejścia i warunki strukturalne |
| 13. BST | Drzewo wyszukiwań | Implementuje search/insert/delete i analizuje wpływ wysokości drzewa |
| 14. Kopce i kolejki priorytetowe | Priorytety | Odróżnia heap od BST i analizuje insert/extract-min lub max |
| 15. Grafy | Model relacji | Reprezentuje graf listami i macierzą sąsiedztwa, rozpoznaje ścieżki i spójność |
| 16. Przeszukiwanie drzew i grafów | Strategie wyszukiwania | Dobiera BFS/DFS i inne algorytmy, formułuje założenia i koszty |
| 17. Teoria sortowania | Kryteria | Definiuje stabilność, adaptacyjność i dolne ograniczenia sortowania przez porównania |
| 18. Sortowanie porównawcze | Implementacja i analiza | Śledzi i porównuje algorytmy z poprawnym worst/average/best case |
| 19. Zaawansowane sortowanie | Dobór metod | Poznaje sortowania inne niż porównawcze i ograniczenia zakresu kluczy |
| 20. Zaawansowane projektowanie | Strategie | Stosuje dziel i zwyciężaj, zachłanność, programowanie dynamiczne z założeniami |

## Zasada niedublowania

**Pakiet 01** nie zawiera pełnego języka RAM, formalnych wyprowadzeń O/Ω/Θ, klasyfikacji sortowań ani implementacji drzew. Może *zapowiadać* problem kosztu na przykładzie wyszukiwania liniowego. Wszystkie powyższe tematy otrzymują własny, pełny przykład w odpowiadającej im części.

**Pakiet 02** odpowiada za formalne znaczenie `LOAD`, `READ`, `STORE`, `JZERO` itd. Nie wolno mieszać konwencji: `READ 0` nie może po cichu zmieniać sumatora, jeżeli deklarujemy, że zapisuje do rejestru.

**Pakiet 03** nie ponawia ogólnej definicji algorytmu. Uczy zapisu, zmiennych, warunków, pętli i kontraktu pseudokodu.

**Pakiety 04–05** oddzielają liczenie operacji/uzasadnienie poprawności od definicji i rachunku notacji asymptotycznych. Przykłady stosowane w 01 wolno przywołać krótkim odsyłaczem, nie kopiując objaśnienia.

**Pakiety 17–19** nie przedstawiają „wszystkich sortowań porównawczych” jako kwadratowych. Trzeba rozdzielić klasę problemu, klasę algorytmu i przypadek wejścia.

## Reguła narracyjna dla wszystkich 20 części

1. **Problem** (konkretny przypadek i pytanie decyzyjne), nie definicja bez kontekstu.
2. **Specyfikacja** (wejście, wyjście, założenia, przypadki brzegowe).
3. **Rozwiązanie** (pseudokod/struktura i jeden pełny przykład).
4. **Śledzenie** (stan zmiennych, tabelka lub czytelna, uzasadniona interakcja).
5. **Poprawność i koszt** (argument lub jawny zakres wstępny).
6. **Wniosek** (ograniczenie obecnego rozwiązania wprowadza temat następny).

Najpierw rozwijamy intuicję, potem nazywamy pojęcie i wprowadzamy formalizm. Każda interakcja musi objaśniać zjawisko; nie wstawiamy fiszek tylko po to, aby kurs wyglądał „interaktywnie”. Oceny pozostają w osobnym teście Moodle, nie w paczce SCORM.

## Wymagane przekazanie między częściami

- 01 → 02: od nieformalnego liczenia kroków do jawnego modelu wykonania.
- 02 → 03: od wykonywania niskopoziomowych instrukcji do czytelnego opisu niezależnego od maszyny.
- 03 → 04 → 05: zapis → argument poprawności i koszt → asymptotyczne granice funkcji kosztu.
- 05 → 06–11: analizowanie operacji na konkretnych strukturach liniowych.
- 11 → 12–16: przejście od sekwencji do relacji hierarchicznych i grafowych.
- 16 → 17–19: porządkowanie, stabilność i koszt porównań.
- 19 → 20: uogólnienie strategii na problemy optymalizacyjne.

**Dalszy audyt:** zweryfikować pełną treść kursów 02–20, odnotować miejsca nakładania się, a następnie modyfikować je w kolejnych, mniejszych PR. Nie przenosić błędnych kodów RAM z kursu 01 do kursu 02 bez naprawy i wykonania testów.
