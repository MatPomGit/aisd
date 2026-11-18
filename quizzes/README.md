# Quizy do wykładów AIiSD (W01–W20)

**Wersja zestawu:** 1.6.2 (W01–W05); 1.6.1 (W11, W12, W16, W17, W19, W20); 1.6.0 (W14); 1.5.0 (pozostałe banki)  
**Data:** 2026-11-18  
**Zakres:** 20 banków po 20 pytań, czyli 400 pytań wyłącznie jednokrotnego wyboru.

## Organizacja

Każdy plik `quiz_wXX.gift` zawiera 20 pytań. W wersji 1.6.2 przeanalizowano matematycznie i redakcyjnie wszystkie 100 pytań banków W01–W05 oraz ich 400 wariantów odpowiedzi. Zastąpiono 300 powtarzalnych komentarzy do dystraktorów odrębnymi objaśnieniami konkretnych błędów rozumowania. Doprecyzowano pięć poleceń, jeden niejednoznaczny wariant odpowiedzi oraz zapis parametrów asymptotycznych. Zachowano 100 kluczy i ich pozycje. W wersji 1.6.1 doprecyzowano siedem pytań (W02-Q06, W11-Q20, W12-Q06, W16-Q02, W17-Q20, W19-Q05, W20-Q18): określono brakujące założenia, poprawiono ścisłość argumentacji i dodano diagnostyczne objaśnienia do każdej błędnej odpowiedzi, nie zmieniając pozycji kluczy. W wersji 1.6.0 przebudowano sześć zadań (W03-Q10, W05-Q15, W14-Q06, W16-Q05, W16-Q07, W17-Q17), tak aby w każdym pozostał dokładnie jeden poprawny wariant. Dopracowano polecenia, dystraktory i uzasadnienia, zachowano cztery opcje, a także równomierny rozkład kluczy. Walidator odrzuca odtąd wszystkie zapisy wielokrotnego wyboru. W wersji 1.5.0 dodano merytoryczną informację zwrotną do wszystkich 1600 wariantów odpowiedzi, a uzasadnienia wszystkich 400 pytań uzupełniono o jawne wskazanie poprawnych wariantów i reguły rozumowania. W wersji 1.4.0 poprawiono błędny klucz W10-Q01, niejednoznaczne odpowiedzi, konstrukcję zadań i polszczyznę, a sześć pytań przekształcono w wielokrotny wybór. Rozszerzono też walidację GIFT. W wersji 1.3.0 przeprowadzono ponowną recenzję W02–W20 (380 pytań): przebudowano merytorycznie 143 pytania, naprawiono niejednoznaczności i urwane dystraktory, ograniczono powtórzenia tematyczne, uzupełniono zadania o rozumowanie na konkretnych przykładach oraz przemieszano klucze we wszystkich 19 bankach. Zachowano identyfikatory i cztery warianty odpowiedzi. W wersji 1.2.2 dodatkowo poprawiono bank W01 na podstawie niezależnej recenzji merytorycznej: doprecyzowano niezmienniki i kontrakty, wymieniono oczywiste dystraktory, ograniczono powtórzenia tematyczne i usunięto okresowy układ poprawnych odpowiedzi. W wersji 1.2.0 zredagowano większość pytań w każdym banku: wyeliminowano podpowiedzi stylistyczne, przebudowano dystraktory i zastąpiono część powtarzalnych zadań analizą konkretnych przypadków. Każdy bank odpowiada wykładowi XX w kolejności kursu. Pliki są zgodne z formatem **GIFT** służącym do importu do bazy pytań Moodle. Każde pytanie zawiera cztery merytorycznie powiązane możliwości, dokładnie jedną prawidłową odpowiedź oraz informację zwrotną z uzasadnieniem.

- `quiz_w01.gift`–`quiz_w05.gift`: podstawy algorytmiki, RAM, pseudokod, analiza kosztu, notacje asymptotyczne;
- `quiz_w06.gift`–`quiz_w10.gift`: tablice, macierze, rekurencja, listy liniowe, stosy;
- `quiz_w11.gift`–`quiz_w15.gift`: kolejki, drzewa, BST, kopce, grafy;
- `quiz_w16.gift`–`quiz_w20.gift`: przeszukiwanie, teoria sortowania, algorytmy sortowania, metody projektowania.

## Audyt W01–W05 (wersja 1.6.2)

Przegląd obejmował 100 pytań, 400 wariantów, 100 kluczy, 100 uzasadnień i 300 komentarzy do błędnych odpowiedzi. Kontrola sprawdzała rachunki, indeksy, zakresy zmiennych, zapis notacji O/o/Ω/Θ, założenia modeli RAM oraz konwencje pseudokodu.

- W01-Q20: zapisano wymóg wskazania **dokładnie** zbioru dopuszczalnych wyników. Poprzednie „obejmuje” mogło oznaczać również nadzbiór z błędnym `-1`.
- W02-Q16: jednoznacznie nazwano akumulator `A`.
- W03-Q04 i Q16: usunięto wariant potencjalnie równoważny prawidłowemu schematowi oraz wyraźnie opisano warunek akceptacji obu testów.
- W04-Q03: określono jednostkę pamięci jako słowo RAM i przyjęto brak przepełnienia sum częściowych.
- W05-Q03 i Q13: zapisano próg asymptotyczny jako `n₀`, a W05-Q14 ograniczono do potęg dwójki `n ≥ 2`, gdzie logarytm jest dodatni.

Nie zmieniono liczby odpowiedzi, poprawnych kluczy, ich pozycji ani wartości ocen. W każdym banku pozostaje po pięć poprawnych wariantów na pozycjach 1–4. Wszystkie trzy komentarze do dystraktorów w każdym z pierwszych 100 pytań opisują teraz odpowiedni błąd rozumowania, zamiast kopiować ogólną informację o prawidłowym kluczu. Walidacja statyczna nie zastępuje testowego importu i podglądu pytań w Moodle.

## Import do Moodle

1. W Moodle otwórz **Baza pytań → Import → GIFT**.
2. Dla każdego wykładu utwórz odrębną kategorię, np. `AIiSD / W01`, i zaimportuj odpowiadający jej plik UTF-8.
3. Utwórz **osobną aktywność Quiz** dla każdej kategorii. Nie przywracaj testów w pakietach Rise/SCORM.
4. Włącz losową kolejność odpowiedzi i, jeśli jest to uzasadnione dydaktycznie, losowanie pytań z kategorii.
5. W aktywności Moodle wybierz **Zachowanie pytań → Natychmiastowa informacja zwrotna** (*Immediate feedback*), jeśli komentarz ma pojawiać się po sprawdzeniu każdego zadania, a nie dopiero po ukończeniu całego quizu.
6. W sekcji **Opcje przeglądu** dla etapu **Podczas próby** włącz **Poprawność odpowiedzi**, **Informację zwrotną dotyczącą odpowiedzi** (*Specific feedback*) i **Ogólną informację zwrotną** (*General feedback*); opcjonalnie również **Poprawną odpowiedź**. Nazwy ustawień mogą różnić się zależnie od wersji językowej Moodle. Bez tych ustawień samo zaimportowanie pliku GIFT **nie zapewni** wyświetlania informacji zwrotnych po każdym pytaniu.
7. Przed ocenianym użyciem sprawdź na testowym koncie studenta podgląd pytań, działanie przycisku **Sprawdź**, punktację, informacje zwrotne i ograniczenia podejść. Sprawdź, czy Moodle wyświetla przy każdym pytaniu przyciski jednokrotnego wyboru i pozwala wskazać dokładnie jeden wariant.

## Informacja zwrotna dla studenta

Każde z **400 pytań** zawiera dwa poziomy objaśnień:

- **Komentarz do odpowiedzi** po separatorze GIFT `#` w każdym z czterech wariantów (łącznie **1600** komentarzy). Po sprawdzeniu pytania student otrzymuje informację, czy wybrany wariant jest poprawny, oraz zasadę lub obliczenie uzasadniające ocenę. We wszystkich pytaniach, w tym w sześciu przebudowanych w wersji 1.6.0, komentarze odnoszą się do poprawności konkretnego wariantu.
- **Uzasadnienie całego zadania** po separatorze `####`. Wskazuje jedną prawidłową odpowiedź i wyjaśnia właściwą metodę rozwiązania. Pozostaje dostępne niezależnie od wybranego dystraktora, gdy wyświetlanie ogólnej informacji zwrotnej jest włączone w Moodle.

Komentarze nie są podpowiedziami wyświetlanymi przed udzieleniem odpowiedzi. Moment ujawnienia ustawia się w aktywności Moodle, nie w pliku GIFT. W testach ocenianych z odroczoną informacją zwrotną można wyświetlać objaśnienia dopiero po zakończeniu próby, zgodnie z polityką oceniania. W repozytorium nie umieszczamy ustawień wymuszających ujawnienie klucza przed oceną.

Przykładowa składnia:

```gift
::PRZYKLAD::[plain]Ile wynosi 2+2? {
  =4#Prawidłowo. Dodajemy dwie dwójki, otrzymując cztery.
  ~5#Nie. Wynik dodawania 2+2 to cztery, a nie pięć.
  ~3#Nie. Dodając do dwóch kolejne dwa, otrzymujemy cztery.
  ~2#Nie. Wynik jest większy od każdego z dodatnich składników.
  ####Poprawna odpowiedź to 4, ponieważ 2+2\=4.
}
```

Podstawa techniczna: [Moodle GIFT](https://docs.moodle.org/502/en/GIFT), [Zachowanie pytań](https://docs.moodle.org/502/en/Question_behaviours) i [Ustawienia quizu](https://docs.moodle.org/502/en/Quiz_settings).

## Konstrukcja pytań

Priorytetem jest **znajomość materiału i umiejętność zastosowania algorytmu**, a nie eliminacja absurdalnych odpowiedzi. Zastosowano krótkie ślady wykonania, koszty operacji, niezmienniki, warunki brzegowe, porównanie implementacji, stabilność i ograniczenia metod. Dystraktory odnoszą się do tych samych pojęć co odpowiedź prawidłowa; nie stosowano odpowiedzi typu „wszystkie powyższe” ani rozstrzygnięć opartych wyłącznie na stylu sformułowania.

Banki zostały opracowane na podstawie mapy `docs/curriculum-map.md`, tytułów i struktury dostępnych pakietów oraz weryfikowalnych własności algorytmicznych. Nie jest to formalna certyfikacja zgodności każdego pytania z każdym akapitem wszystkich źródłowych lekcji. Przed ocenianiem należy porównać pytania z aktualnie publikowaną wersją danego wykładu. To szczególnie ważne podczas trwającej redakcji materiałów 02–20.

## Reguły redakcji dystraktorów

- Każda błędna odpowiedź ma reprezentować **rozpoznawalne nieporozumienie merytoryczne**: błąd graniczny, błędną kolejność operacji, pomylenie modelu kosztu, niezmiennika albo własności podobnych struktur.
- Wszystkie cztery warianty odnoszą się do **tego samego pytania i mają porównywalny poziom szczegółowości**. Odpowiedź liczbowa nie powinna konkurować z trzema długimi opisami, a wyłącznie dystraktory nie powinny zawierać objaśnień przyczynowych.
- Nie stosujemy opcji absurdalnych ani celowo niepoprawnych stylistycznie. Fałszywość wariantu ma wynikać z **wiedzy o algorytmie**, a nie z językowej eliminacji.
- W zadaniach o śledzeniu kodu trzeba jednoznacznie podać warunki początkowe, semantykę operacji, konwencję indeksowania i moment sprawdzania warunku.
- Każde pytanie musi zawierać dokładnie jedną poprawną odpowiedź oznaczoną znakiem `=`, trzy niepoprawne warianty oznaczone znakiem `~`, komentarz do każdego wariantu oraz ogólne uzasadnienie. Przy imporcie do Moodle należy losować kolejność odpowiedzi.
- Dystraktory muszą być jednoznacznie błędne w warunkach zadania. Relacje równoważne matematycznie, prawdziwe ograniczenia asymptotyczne o różnej dokładności i inne dopuszczalne rozwiązania nie mogą być jednocześnie oferowane jako pojedynczy klucz.

Powyższe zasady ograniczają zgadywanie na podstawie konstrukcji testu. Nie gwarantują, że każde pytanie jest odporne na eliminację bez wiedzy; wymagałoby to pilotażu i analizy psychometrycznej odpowiedzi studentów (trudność, moc różnicująca, częstość wyboru poszczególnych dystraktorów).

## Głębokość sprawdzanej wiedzy

Celem kolejnych redakcji jest następujący rozkład pytań w banku 20-elementowym: pięć zadań analizujących wykonanie algorytmu, pięć dotyczących diagnozy błędu lub kontrprzykładu, cztery wymagające doboru struktury albo strategii, cztery sprawdzające uzasadnienie poprawności lub kosztu oraz najwyżej dwa pytania pojęciowe. To kierunek rozwoju banków, **nie deklaracja, że każde 20 pytań już idealnie spełnia tę proporcję**.

Każdy dystraktor powinien reprezentować prawdopodobny błąd rozumowania, np. pomylenie górnego i dolnego ograniczenia, błędne przejście po wskaźnikach lub przyjęcie nieudowodnionej zachłanności. Rachunek liczbowy bez interpretacji ma ograniczoną wartość pomiarową. Odpowiedzi i uzasadnienia nie mogą sugerować klucza przez długość, oczywiste sformułowania lub niepełne zdania.

## Polszczyzna i wyświetlanie w Moodle

Wszystkie 400 pytań mają jawny znacznik formatu `[plain]`. Moodle zapisuje wówczas treść pytań, odpowiedzi i uzasadnień jako zwykły tekst, bez interpretowania nierówności `a<b`, `a>b` czy zapisów indeksów jako znaczników HTML. Nie należy umieszczać znaczników HTML ani encji `&lt;` i `&gt;` w tych polach. Odwołania do funkcji, instrukcji oraz standardowych nazw algorytmów zachowują pisownię stosowaną w pseudokodzie.

- Pliki są kodowane jako **UTF-8 bez BOM** i używają normalizacji **Unicode NFC**, potrzebnej m.in. dla polskich znaków.
- W treści dosłowne znaki sterujące GIFT `~`, `=`, `#`, `{` i `}` trzeba poprzedzić ukośnikiem `\`. Nie dotyczy to separatorów składniowych: `=`/`~` na początku wariantu, `#` pomiędzy odpowiedzią a jej komentarzem oraz `####` przed uzasadnieniem całego pytania.
- Zachowano standardowe symbole matematyczne Unicode, takie jak `Θ`, `Ω`, `→`, `×`, `≤` oraz indeksy górne i dolne. Rzadziej obsługiwane graficzne nawiasy funkcji podłogi i sufitu zastąpiono zapisami `floor(...)` i `ceil(...)`.
- Walidator kontroluje nagłówki `[plain]`, poprawność UTF-8, obecność BOM, normalizację NFC, niewidoczne lub uszkodzone znaki, poprawne maskowanie separatorów GIFT, unikatowość odpowiedzi i rozkład kluczy. Dodatkowo odrzuca wagi procentowe GIFT, brak pojedynczego klucza i polecenia sugerujące wybór wielu odpowiedzi.
- Przed wykorzystaniem pytań do oceniania trzeba **zaimportować je do testowej kategorii Moodle i obejrzeć podgląd** na komputerze i urządzeniu mobilnym, szczególnie wzory, nierówności, polskie znaki oraz symbole matematyczne. Sam test statyczny nie potwierdza krojów pisma dostępnych w konkretnym motywie Moodle.

Zasady formatu: [dokumentacja GIFT w Moodle](https://docs.moodle.org/502/en/GIFT_format).

## Kontrola jakości

```bash
python3 scripts/validate_quizzes.py
```

Walidator sprawdza liczbę plików, identyfikatory, cztery różne warianty każdej odpowiedzi, dokładnie jedną poprawną odpowiedź, obecność 1600 komentarzy do wariantów oraz 400 ogólnych uzasadnień. W każdym banku wymaga po pięć poprawnych odpowiedzi na każdej pozycji, odrzuca klucze okresowe i powtarzalne wzorce, niedokończone dystraktory, nieprawidłowe sekwencje GIFT oraz warianty z wagami procentowymi. Testy regresyjne sprawdzają, czy wszystkie 400 pytań pozostają jednokrotnego wyboru. Kontrola statyczna nie zastępuje niezależnej recenzji merytorycznej ani testowego importu do Moodle przed ocenianiem.

**Bezpieczeństwo oceniania:** repozytorium jest publiczne, a format GIFT zawiera jawne klucze odpowiedzi. Nie używaj tych plików bezpośrednio do egzaminu o wysokiej stawce. Do takiego zastosowania przenieś bank do prywatnego miejsca, zachowaj kontrolę dostępu i przygotuj alternatywne, nieopublikowane wersje zadań.

**Granica techniczna:** quizy to osobne pliki źródłowe. Nie modyfikują `raw/*.zip`, `files/scorm_XX/`, mechanizmu ukończenia SCORM ani dziennika ocen Moodle.
