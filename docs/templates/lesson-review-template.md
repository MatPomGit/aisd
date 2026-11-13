# Karta niezależnej recenzji i przebudowy lekcji

> Skopiuj ten szablon do dokumentacji przeglądu konkretnej lekcji. Nie publikuj niewypełnionej karty jako wyniku recenzji.

**Wersja szablonu:** 1.0.0 · **Data:** YYYY-MM-DD  
**Pakiet:** XX / 20 — …  
**Lekcja:** XX / YY — …  
**ID lekcji Rise:** `…`  
**Archiwum źródłowe:** `raw/….zip`  
**SHA-256 źródła:** `…`  
**Powiązane issues i PR:** #…  
**Stan:** do recenzji / w redakcji / do poprawek / zaakceptowano / wstrzymano

## A. Kontekst i cele

**Odbiorca:** studenci III roku informatyki.  
**Wymagania wstępne:** …  
**Główne pytanie lekcji:** …  
**Wątek przewodni i przykład:** …  
**Zależności od innych pakietów:** …

**Mierzalne efekty uczenia się (3–6):**
1. …
2. …
3. …

## B. Inwentaryzacja zawartości

| Element | Stan źródłowy | ID/ścieżka i uwagi |
|---|---|---|
| Tekst i nagłówki | … | … |
| Definicje i twierdzenia | … | … |
| Pseudokod/programy | … | … |
| Diagramy/grafika | … | … |
| Interakcje dydaktyczne | … | … |
| Quizy i sprawdzania wiedzy | … | Usuwane z wynikowej paczki |
| Odsyłacze i zależności | … | … |

## C. Niezależne ustalenia

| ID | Waga P0–P3 | Lokalizacja (lekcja/blok/pole) | Problem, kontrprzykład lub dowód | Sposób naprawy | Status |
|---|---|---|---|---|---|
| F01 | … | … | … | … | … |

Zasada: **nie wpisuj jedynie ogólnika „błędny algorytm”**. Zapisz konkretne wejście, oczekiwany wynik, wynik uzyskany oraz warunek, pod którym ujawnia się błąd. Przy poprawnym twierdzeniu zapisz przesłanki i metodę uzasadnienia.

## D. Ocena jakości (0–3)

| Obszar | Ocena | Dowody i decyzje |
|---|---:|---|
| A. Poprawność merytoryczna | … | … |
| B. Specyfikacja, kod, przypadki brzegowe | … | … |
| C. Poprawność, zakończenie i koszt | … | … |
| D. Narracja i ciągłość wywodu | … | … |
| E. Zwięzłość, polszczyzna, kalki i terminologia | … | … |
| F. Ilustracje i interakcje | … | … |
| G. Spójność z pozostałymi 19 pakietami | … | … |
| H. Poprawność przebudowy SCORM i zgodność z Moodle | … | … |

Skala: 0 niepotwierdzone/błędne; 1 istotne braki; 2 poprawne z uwagami; 3 poprawne i uzasadnione. Wynik ogólny nie kompensuje otwartego P0/P1.

## E. Plan redakcji

**Treści do zachowania:** …  
**Treści do skondensowania:** …  
**Błędne treści do poprawy:** …  
**Treści do usunięcia (zbędne):** …  
**Treści należące do innego pakietu (numer i miejsce):** …  
**Nowe przykłady lub wizualizacje:** …

**Docelowy szkielet narracji:**
1. Problem: …
2. Specyfikacja: …
3. Rozwiązanie i pseudokod: …
4. Ślad wykonania: …
5. Poprawność i terminacja: …
6. Koszt i ograniczenia: …
7. Przejście do kolejnego zagadnienia: …

**Przykład redakcji przed/po:** krótki fragment źródłowy → wersja poprawiona → uzasadnienie zmiany.

## F. Testy algorytmiczne

| Przypadek | Dane wejściowe | Oczekiwany wynik / niezmiennik | Wynik sprawdzenia |
|---|---|---|---|
| Typowy | … | … | … |
| Pusty/minimalny | … | … | … |
| Brak wyniku | … | … | … |
| Duplikaty/skrajne wartości | … | … | … |
| Kontrprzykład wcześniejszego błędu | … | … | … |

**Model kosztu i założenia:** …  
**Dowód poprawności i zakończenia:** …  
**Pliki testów / wyniki:** …

## G. Przebudowa i QA pakietu

- [ ] Źródłowy ZIP zachowany bez zmian (SHA-256).
- [ ] Poprawność `imsmanifest.xml`, punktu startowego i struktury archiwum.
- [ ] Przebudowa odtwarzalna z wersjonowanych, czytelnych zmian.
- [ ] Zmienione tylko rozpoznane, dozwolone identyfikatory i pola Rise.
- [ ] Brak quizów końcowych, `knowledgeCheck` i sekcji kontrolnych w wyniku.
- [ ] Poprawność logiczna kodu, danych przykładów oraz symboli i wzorów.
- [ ] Niepogorszony dostęp do multimediów i innych zasobów.
- [ ] Testy jednostkowe i regresyjne — wynik oraz odnośnik: …
- [ ] Test w przeglądarce (rozmiary ekranu, nawigacja, typografia, multimedia): …
- [ ] Test na właściwej instancji Moodle (wznowienie, `completed`, brak oceny): …

## H. Decyzja końcowa

**Decyzja:** zaakceptowano / do poprawy / wstrzymano  
**Otwarte problemy P0/P1:** …  
**Ryzyka i założenia niezweryfikowane:** …  
**Dowody testu Moodle:** …  
**Dalsze zadania:** …

Ostateczna akceptacja wymaga poprawności merytorycznej oraz udokumentowanej próby Moodle. Test statyczny i test przeglądarkowy nie są jej zamiennikami.

Zasady główne: [Standard recenzji i przebudowy](../lesson-review-and-rebuild.md).
