# Standard oceny i przebudowy lekcji AIiSD

**Wersja:** 1.0.0 · **Data:** 2026-11-13  
**Zakres:** wszystkie lekcje dydaktyczne we wszystkich 20 pakietach „Algorytmy i struktury danych”, studenci III roku informatyki.

## 1. Cel i zasada recenzji

Celem jest zbudowanie **ciągłej, logicznej i samowystarczalnej narracji**, w której student rozumie nie tylko definicję, lecz również źródło problemu, motywację konstrukcji, przebieg algorytmu, jego poprawność i ograniczenia. Tekst powinien przypominać dobrze napisany rozdział podręcznika, a nie listę haseł z prezentacji.

Każda lekcja ma przejść **niezależną ocenę**, nawet jeśli wcześniejsze testy i recenzje zakończyły się pozytywnie. Kontrola automatyczna struktury SCORM nie weryfikuje prawdziwości treści matematycznej ani skuteczności dydaktycznej.

Rozróżniaj trzy jednostki pracy:

- **Pakiet/kurs SCORM**: jeden z 20 archiwów ZIP, zawierający kilka lub kilkanaście części.
- **Lekcja/część Rise**: jednostka w `course.lessons` — oceniamy ją osobno, ale także jej miejsce w całym pakiecie.
- **Blok**: akapit, nagłówek, lista, kod, grafika, karta czy interakcja. Kontrolujemy go w kontekście lekcji, nie tylko izolowany tekst.

## 2. Inwentaryzacja i ślad dowodowy

Dla pakietu podaj: numer, pełną nazwę ZIP, sumę SHA-256, schemat SCORM, tytuły i identyfikatory lekcji, liczbę oraz typy bloków, zależności od innych tematów. Zobacz rzeczywiste źródło tekstu, a nie wyłącznie automatyczny spis tytułów. Dla długich kursów przeczytaj każdą lekcję w całości; fragmentaryczne próbki wystarczają wyłącznie do triage, **nie do końcowej recenzji**.

W archiwach Rise starszego typu dane mogą znajdować się jako zakodowany Base64 JSON w `scormcontent/index.html`; w nowszych eksportach może występować `scormcontent/runtime-data.js`. Nie zakładaj, że każdy eksport ma identyczny wrapper. Zidentyfikuj wersję i sprawdź schemat przed zmianami.

Przy każdej uwadze rejestruj: **lokalizację** (pakiet → lekcja ID → blok ID → pole), cytowane krótko twierdzenie lub pseudokod, ocenę, uzasadnienie, proponowaną korektę, metodę sprawdzenia oraz status. Nie wystarczy napisać „poprawić złożoność”.

## 3. Recenzja naukowa i algorytmiczna

### 3.1 Definicje i warunki

Sprawdź, czy każdy nowy termin jest zdefiniowany jednoznacznie i zgodnie z powszechnie przyjętym znaczeniem. Rozdzielaj **problem, instancję, specyfikację, algorytm, pseudokod, implementację i program**. Każde twierdzenie zależne od założeń ma te założenia jawnie podane, np. uporządkowanie wejścia, model kluczy, sposób indeksowania, dostępne operacje, typ liczb, rozmiar pamięci.

Weryfikuj z literaturą akademicką, dokumentacją normatywną lub podstawowym dowodem; nie opieraj korekty na samym autorytecie wcześniejszej wersji. Gdy istnieją różne konwencje (wysokość drzewa, indeksowanie, reprezentacja grafu, semantyka RAM), zdefiniuj wybraną i stosuj ją konsekwentnie.

### 3.2 Poprawność i zakończenie

Każdy istotny przykład algorytmu powinien zawierać:

1. **Specyfikację:** poprawne wejścia, wyjścia i przypadki szczególne.
2. **Kompletny opis/pseudokod:** bez niejawnego stanu i brakujących aktualizacji.
3. **Ślad wykonania:** przynajmniej jedno wejście podstawowe i jedno diagnostyczne.
4. **Poprawność:** argument, niezmiennik pętli albo dowód indukcyjny odpowiedni do tematu.
5. **Zakończenie:** dlaczego liczba kroków jest skończona na dopuszczalnych wejściach.
6. **Kontrprzykład dla błędnego wariantu:** tam, gdzie jest użyteczny dydaktycznie.

Nie zamieniaj testowania na „dowód poprawności”. Testy znajdują błędy i weryfikują przykłady; uogólnienie na wszystkie wejścia wymaga argumentu.

### 3.3 Analiza kosztu

Oddzielaj koszt **w najlepszym, średnim i najgorszym przypadku** od asymptotycznych ograniczeń funkcji tego kosztu. `O(f(n))` jest ograniczeniem górnym; **nie oznacza z definicji przypadku najgorszego**. `Ω` i `Θ` też wymagają prawidłowych kwantyfikatorów oraz zakresu stosowania. Podaj, czy analizujesz liczbę porównań, odczytów, operacji RAM czy koszt bitowy.

Wskazuj złożoność czasu i **dodatkowej** pamięci. Uważaj na koszt rekurencji (stos wywołań), kopiowanie struktur, zaalokowane bufory, wielkość liczb, powtarzające się klucze i ograniczenia danych wejściowych. Gdy to uzasadnione, porównaj rozwiązanie z alternatywą i wyjaśnij, w jakich warunkach wybór ma sens.

### 3.4 Krytyczne przypadki w programie

| Zakres | Niezbędne sprawdzenie |
|---|---|
| Tablice | `n = 0`, pierwszy/ostatni indeks, brak elementu, duplikaty, indeksowanie od 0 lub 1 |
| Listy, stosy, kolejki | Pusty element, przepełnienie, usuwanie ostatniego, niezmienniki wskaźników |
| Rekurencja | Przypadek bazowy, miara malejąca, złożoność stosu, głębokość |
| Drzewa BST | Wstawianie i usuwanie 0/1/2 dzieci, duplikaty, przypadek skrajnej wysokości |
| Kopce | Własność kopca, indeks rodzica/dzieci, operacja naprawy i priorytety |
| Grafy | Graf pusty, cykle, niespójność, wielokrotne krawędzie, skierowanie, odwiedzone w BFS/DFS |
| Sortowanie | Stabilność, adaptacyjność, zachowanie kluczy równych, model porównań, granice kosztu |
| RAM | Semantyka każdego rozkazu, rejestry i sumator, wariant kosztu, koniec wejścia, dzielenie i liczby ujemne |

W szczególności nie przenoś do następnej lekcji niepoprawnego kodu RAM z wcześniejszego materiału pod pozorem „uproszczenia”.

### 3.5 Wagi usterek

| Kod | Definicja | Działanie |
|---|---|---|
| **P0 – blokujący** | Błędny wynik, niekończący się program, nieprawdziwe twierdzenie, uszkodzenie pakietu | Nie publikować; poprawić i ponownie zweryfikować |
| **P1 – istotny** | Pominięte założenia, błędna złożoność, sprzeczna definicja, nieczytelny przykład prowadzący do nieporozumienia | Naprawić przed dydaktyczną akceptacją |
| **P2 – redakcyjny** | Kalka, redundancja, złe przejście, niekonsekwentne pojęcia | Poprawić w ramach redakcji |
| **P3 – kosmetyczny** | Niewpływające na sens formatowanie lub drobny detal wizualny | Usunąć bez ryzykownej zmiany semantyki |

## 4. Projekt dydaktyczny i narracja

Dla każdej lekcji ustal **3–6 mierzalnych efektów uczenia się**, odpowiednich do poziomu III roku. Używaj czasowników: *sformułuje, skonstruuje, prześledzi, uzasadni, wykaże, porówna, oszacuje*. „Zna” lub „rozumie” bez obserwowalnego kryterium to zbyt mało.

Preferowana droga czytelnika:

**Problem → pytanie → specyfikacja → pomysł → algorytm → ślad wykonania → poprawność → koszt/ograniczenia → nowe pytanie.**

Nie narzucaj sztywnego szablonu sekcji, jeśli temat wymaga innego porządku, ale zachowaj związek przyczynowo-skutkowy. Jedna lekcja powinna mieć **jeden wątek przewodni**; drugi przykład wprowadzaj tylko dla kontrastu lub wykazania ograniczenia pierwszego. Nie powtarzaj tej samej definicji w kolejnych częściach.

Każdy wykres, diagram, fiszka i animacja muszą realizować konkretny cel: objaśniać stan algorytmu, zmianę danych, porównanie kosztu lub relację między strukturami. Usuń dekoracyjne elementy bez funkcji dydaktycznej, ale nie usuwaj istotnego rysunku tylko po to, by skrócić tekst. Przykłady kodu i ich wyniki przedstawiaj blisko siebie, z czytelnymi etykietami.

### Kontrola zgodności całej serii

Przed zmianą zakresu lekcji sprawdź tytuły i treści sąsiednich kursów. Każde pojęcie ma **jedno główne miejsce rozwinięcia**; wcześniejszy pakiet może je wprowadzić intuicyjnie, a późniejszy krótko przypomnieć. Dla SCORM 01 nie rozwijaj formalnego języka RAM (02), pseudokodu i schematów (03), metod liczenia kosztu (04) i notacji asymptotycznych (05) na poziomie, który dubluje te lekcje. Tę samą regułę stosuj do pozostałych pakietów.

Jeżeli przenosisz fragment, wskaż w raporcie **miejsce docelowe**, sprawdź, czy materiał nie istnieje tam już w poprawnej postaci, a potem usuń duplikat. Nie „przenoś” błędnego twierdzenia bez naprawy.

## 5. Redakcja językowa i eliminacja kalk

Stosuj współczesną polszczyznę akademicką, krótkie zdania i terminologię właściwą informatyce. Nie jest potrzebny marketingowy ton ani metakomentarze o tym, jak ciekawy jest temat. Zamiast zapowiadać, że dany problem jest ważny, pokaż jego znaczenie przykładem.

| Unikać | Preferować |
|---|---|
| „W tej lekcji skupimy się na kluczowym fundamencie...” | Od razu opisać problem |
| „Jasne określenie celów ułatwia...” | Podać konkretny efekt uczenia się bez komentarza |
| „Będziesz miał okazję spróbować...” | „Prześledź”, „Wykaż”, „Porównaj” |
| „Implementacja w pseudokodzie” | „Zapis/Opis w pseudokodzie”; „implementacja w Pythonie/C” |
| „Algorytm jest najbardziej optymalny” | „Algorytm jest optymalny” przy podanych założeniach |
| „Algorytm jest efektywny” | Podać funkcję kosztu, model i porównanie |
| „Wszystkie sortowania przez porównania są kwadratowe” | Wskazać konkretny algorytm i rodzaj analizowanego przypadku |
| „Algorytm niedeterministyczny losuje wynik” | Odróżnić model niedeterministyczny od algorytmu randomizowanego |

Kontroluj fleksję, interpunkcję, spójność interfejsu, terminów i symboli, błędy wstawione przez HTML, puste akapity, zbędne wyróżnienia i angielskie etykiety. Nie dokonuj bezrefleksyjnej globalnej podmiany pojedynczych słów — wymaga ona oceny kontekstu.

**Test akapitu:** czy wnosi definicję, mechanizm, przykład, uzasadnienie lub przejście do nowego problemu? Jeżeli nie, usuń albo połącz. **Test zdania:** czy student dzięki niemu wie coś nowego lub rozumie coś lepiej?

## 6. Projekt przebudowy technicznej

### Źródła i zakres odpowiedzialności

| Ścieżka | Status |
|---|---|
| `raw/*.zip` | Kanoniczne eksporty Rise, **nietykalne** |
| `files/scorm_XX/` | Historyczne rozpakowane dane pomocnicze; nie traktować jako źródła pakietu |
| `scripts/scorm_pipeline.py` | Budowanie oraz walidacja SCORM 1.2 |
| `scripts/build_scorm_pages_catalog.py` | Przygotowanie pakietów publikacyjnych i katalogu |
| `docs/editor/` | Przeglądarkowa edycja i eksport gotowych paczek |
| `tests/` | Testy regresji struktur, przypadków negatywnych i zachowania runtime |
| `docs/scorm.md` | Szczegółowa dokumentacja formatu oraz kontroli integralności |

Drobna poprawka tekstowa może być wykonana w edytorze przeglądarkowym i wyeksportowana na potrzeby testów, ale **zmiana będąca częścią programu kursu musi być odtwarzalna z repozytorium**. Dla istotnej redakcji stosuj tekstowe i przeglądalne wersjonowane zmiany danych kursu (np. nakładki JSON), łączone z walidowanym adapterem do rozpoznanej wersji Rise. Jeśli funkcji brak dla danego formatu, najpierw dodaj adapter i jego testy; nie zastępuj tego ręczną podmianą niejawnego fragmentu Base64 w ZIP.

Przed modyfikacją określ dozwolone pola i identyfikatory bloków. Odrzuć modyfikację, jeśli struktura, identyfikator lekcji, schema JSON lub ustawienia SCORM odbiegają od rozpoznanego stanu (**fail-closed**). Nie modyfikuj manifestu, plików sterownika ani plików multimedialnych bez uzasadnionej potrzeby i odrębnej kontroli. Nie wykonuj skryptów z rozpakowanych, niezweryfikowanych archiwów.

### Kolejność przebudowy

1. Zachowaj SHA-256 źródłowego ZIP i listę plików archiwum.
2. Zweryfikuj integralność ZIP, `imsmanifest.xml`, punkt startowy i typ źródła Rise.
3. Zdekoduj dane kursu i ustal jednoznaczne identyfikatory modyfikowanych lekcji/bloków.
4. Usuń formalne quizy i sekcje `knowledgeCheck` zgodnie z istniejącą bezpieczną procedurą.
5. Zastosuj recenzowaną korektę treści; **nie przywracaj** testów Rise.
6. Odtwórz ZIP jako **nowy plik** z nazwą pochodną od oryginału.
7. Ponownie sprawdź manifest, strukturę pakietu, odczyt danych i SHA-256 niezmienionych zasobów.
8. Wykonaj regresję wybranej lekcji, pełnego pakietu i — gdy wspólne narzędzie się zmieniło — wszystkich 20 pakietów.
9. Przejrzyj wygląd na komputerze i telefonie, przewijanie, pseudokod, grafikę, kolejność sekcji i nawigację.
10. Przetestuj wynik w docelowej wersji Moodle na koncie testowym.

**Uwaga:** w wyniku przebudowy paczka ma raportować postęp/ukończenie po 100% materiału, bez przesyłania oceny quizu. Brak `SetScore` w testach runtime nie dowodzi jeszcze braku pozycji oceny w dzienniku Moodle; ustawienia tej pozycji należy osobno sprawdzić.

### Test Moodle i rozróżnienie dowodów

Minimalny scenariusz: import ZIP do **osobnej aktywności testowej**, otwarcie pierwszej/ostatniej lekcji, przejście między lekcjami, zapamiętanie `suspend_data` i wznowienie nauki, ukończenie przy 100%, kontrola `cmi.core.lesson_status`, brak nowej oceny `cmi.core.score.raw`, kontrola dziennika ocen i współdziałania z oddzielnym testem Moodle.

Stan raportu musi jasno odróżniać **test statyczny**, **test przeglądarkowy**, **test integracyjny Moodle** i **akceptację dydaktyczną**. Nie przedstawiaj pierwszych dwóch jako certyfikacji zgodności LMS.

## 7. Kryteria akceptacji i ocena jakości

Dla każdego kryterium przypisz ocenę 0–3:

| Wynik | Interpretacja |
|---|---|
| 0 | Błędne, nieobecne lub niezweryfikowane |
| 1 | Istotne braki |
| 2 | Poprawne, ale wymagające redakcji |
| 3 | Poprawne, jasne i dydaktycznie uzasadnione |

Oceniaj osobno: **(A) poprawność merytoryczna**, **(B) specyfikacja/kod/testy**, **(C) poprawność i koszt**, **(D) narracja i ciągłość**, **(E) ekonomia treści i język**, **(F) grafika/interakcje**, **(G) spójność z programem**, **(H) integralność SCORM i Moodle**.

**Próg dopuszczenia:** wszystkie obszary A–G mają ocenę co najmniej 2, A–C ocenę 3 dla przykładów zawierających algorytmy, brak otwartych P0/P1 i brak niezweryfikowanych twierdzeń. Do publikacji studentom obszar H musi obejmować **udokumentowany pozytywny test Moodle**, a nie sam wynik CI. Suma punktów nie kompensuje błędu krytycznego.

Dla każdego przeglądu utwórz kartę według [szablonu](templates/lesson-review-template.md). Zapisz dowody, kontrprzykłady, zmiany przed/po, wynik testów, ryzyko oraz decyzję **zaakceptowano / do poprawy / wstrzymano**. Niezakończone elementy pozostaw w issues, a dokumentację uzupełniaj wraz z kolejnymi poprawkami.

## 8. Zasady publicznej dokumentacji

Dokumentacja publikowana studentom opisuje wyłącznie treść dydaktyczną, pracę z materiałem, wymagania techniczne i weryfikowalne kryteria jakości. Nie publikuj w niej informacji o wewnętrznych systemach organizacji prac, agentach lub ich sposobie działania. Dokumentacja nie może zawierać sekretów, danych studentów ani informacji o niepublicznej infrastrukturze.

## 9. Powtarzanie procesu w całym kursie

Procedurę wykonuje się **dla każdej lekcji w każdym pakiecie**, a następnie przeprowadza się recenzję całego pakietu i przejść pomiędzy pakietami. Nowy standard zweryfikowany dla SCORM 01 jest wzorcem jakości, lecz nie automatycznym dowodem poprawności innych 19 pakietów. Zagadnienia muszą pozostać kompletne we właściwym miejscu programu, bez przypadkowego usuwania potrzebnej teorii.

Po każdej fali aktualizuj kartę przeglądu, mapę zależności oraz rejestr znanych błędów. **Celem jest lepsze rozumienie, nie tylko krótszy tekst lub zielony workflow.**
