# Quizy do wykładów AIiSD (W01–W20)

**Wersja zestawu:** 1.3.0 (W02–W20); W01: 1.2.2  
**Data:** 2026-11-17  
**Zakres:** 20 oddzielnych banków, po 20 pytań jednokrotnego wyboru (łącznie 400 pytań).

## Organizacja

Każdy plik `quiz_wXX.gift` zawiera 20 pytań. W wersji 1.3.0 przeprowadzono ponowną recenzję W02–W20 (380 pytań): przebudowano merytorycznie 143 pytania, naprawiono niejednoznaczności i urwane dystraktory, ograniczono powtórzenia tematyczne, uzupełniono zadania o rozumowanie na konkretnych przykładach oraz przemieszano klucze we wszystkich 19 bankach. Zachowano identyfikatory i cztery warianty odpowiedzi. W wersji 1.2.2 dodatkowo poprawiono bank W01 na podstawie niezależnej recenzji merytorycznej: doprecyzowano niezmienniki i kontrakty, wymieniono oczywiste dystraktory, ograniczono powtórzenia tematyczne i usunięto okresowy układ poprawnych odpowiedzi. W wersji 1.2.0 zredagowano większość pytań w każdym banku: wyeliminowano podpowiedzi stylistyczne, przebudowano dystraktory i zastąpiono część powtarzalnych zadań analizą konkretnych przypadków. Każdy bank odpowiada wykładowi XX w kolejności kursu. Pliki są zgodne z formatem **GIFT** służącym do importu do bazy pytań Moodle. Każde pytanie zawiera cztery merytorycznie powiązane możliwości, dokładnie jedną prawidłową odpowiedź oraz informację zwrotną z uzasadnieniem.

- `quiz_w01.gift`–`quiz_w05.gift`: podstawy algorytmiki, RAM, pseudokod, analiza kosztu, notacje asymptotyczne;
- `quiz_w06.gift`–`quiz_w10.gift`: tablice, macierze, rekurencja, listy liniowe, stosy;
- `quiz_w11.gift`–`quiz_w15.gift`: kolejki, drzewa, BST, kopce, grafy;
- `quiz_w16.gift`–`quiz_w20.gift`: przeszukiwanie, teoria sortowania, algorytmy sortowania, metody projektowania.

## Import do Moodle

1. W Moodle otwórz **Baza pytań → Import → GIFT**.
2. Dla każdego wykładu utwórz odrębną kategorię, np. `AIiSD / W01`, i zaimportuj odpowiadający jej plik UTF-8.
3. Utwórz **osobną aktywność Quiz** dla każdej kategorii. Nie przywracaj testów w pakietach Rise/SCORM.
4. Włącz losową kolejność odpowiedzi i, jeśli jest to uzasadnione dydaktycznie, losowanie pytań z kategorii.
5. Przed ocenianym użyciem przetestuj podgląd pytań, zapis ocen, termin wyświetlania uzasadnień i ograniczenia podejść na koncie testowym studenta.

## Konstrukcja pytań

Priorytetem jest **znajomość materiału i umiejętność zastosowania algorytmu**, a nie eliminacja absurdalnych odpowiedzi. Zastosowano krótkie ślady wykonania, koszty operacji, niezmienniki, warunki brzegowe, porównanie implementacji, stabilność i ograniczenia metod. Dystraktory odnoszą się do tych samych pojęć co odpowiedź prawidłowa; nie stosowano odpowiedzi typu „wszystkie powyższe” ani rozstrzygnięć opartych wyłącznie na stylu sformułowania.

Banki zostały opracowane na podstawie mapy `docs/curriculum-map.md`, tytułów i struktury dostępnych pakietów oraz weryfikowalnych własności algorytmicznych. Nie jest to formalna certyfikacja zgodności każdego pytania z każdym akapitem wszystkich źródłowych lekcji. Przed ocenianiem należy porównać pytania z aktualnie publikowaną wersją danego wykładu. To szczególnie ważne podczas trwającej redakcji materiałów 02–20.

## Reguły redakcji dystraktorów

- Każda błędna odpowiedź ma reprezentować **rozpoznawalne nieporozumienie merytoryczne**: błąd graniczny, błędną kolejność operacji, pomylenie modelu kosztu, niezmiennika albo własności podobnych struktur.
- Wszystkie cztery warianty odnoszą się do **tego samego pytania i mają porównywalny poziom szczegółowości**. Odpowiedź liczbowa nie powinna konkurować z trzema długimi opisami, a wyłącznie dystraktory nie powinny zawierać objaśnień przyczynowych.
- Nie stosujemy opcji absurdalnych ani celowo niepoprawnych stylistycznie. Fałszywość wariantu ma wynikać z **wiedzy o algorytmie**, a nie z językowej eliminacji.
- W zadaniach o śledzeniu kodu trzeba jednoznacznie podać warunki początkowe, semantykę operacji, konwencję indeksowania i moment sprawdzania warunku.
- Należy zachować pojedynczą poprawną odpowiedź, uzasadnienie oraz identyfikator pytania, a przy imporcie do Moodle losować kolejność odpowiedzi.

Powyższe zasady ograniczają zgadywanie na podstawie konstrukcji testu. Nie gwarantują, że każde pytanie jest odporne na eliminację bez wiedzy; wymagałoby to pilotażu i analizy psychometrycznej odpowiedzi studentów (trudność, moc różnicująca, częstość wyboru poszczególnych dystraktorów).

## Głębokość sprawdzanej wiedzy

Celem kolejnych redakcji jest następujący rozkład pytań w banku 20-elementowym: pięć zadań analizujących wykonanie algorytmu, pięć dotyczących diagnozy błędu lub kontrprzykładu, cztery wymagające doboru struktury albo strategii, cztery sprawdzające uzasadnienie poprawności lub kosztu oraz najwyżej dwa pytania pojęciowe. To kierunek rozwoju banków, **nie deklaracja, że każde 20 pytań już idealnie spełnia tę proporcję**.

Każdy dystraktor powinien reprezentować prawdopodobny błąd rozumowania, np. pomylenie górnego i dolnego ograniczenia, błędne przejście po wskaźnikach lub przyjęcie nieudowodnionej zachłanności. Rachunek liczbowy bez interpretacji ma ograniczoną wartość pomiarową. Odpowiedzi i uzasadnienia nie mogą sugerować klucza przez długość, oczywiste sformułowania lub niepełne zdania.

## Polszczyzna i wyświetlanie w Moodle

Wszystkie 400 pytań mają jawny znacznik formatu `[plain]`. Moodle zapisuje wówczas treść pytań, odpowiedzi i uzasadnień jako zwykły tekst, bez interpretowania nierówności `a<b`, `a>b` czy zapisów indeksów jako znaczników HTML. Nie należy umieszczać znaczników HTML ani encji `&lt;` i `&gt;` w tych polach. Odwołania do funkcji, instrukcji oraz standardowych nazw algorytmów zachowują pisownię stosowaną w pseudokodzie.

- Pliki są kodowane jako **UTF-8 bez BOM** i używają normalizacji **Unicode NFC**, potrzebnej m.in. dla polskich znaków.
- Znaki sterujące GIFT `~`, `=`, `#`, `{` i `}` występują w treści wyłącznie z poprzedzającym je ukośnikiem `\`. Importer GIFT usuwa ten ukośnik i wyświetla znak dosłownie.
- Zachowano standardowe symbole matematyczne Unicode, takie jak `Θ`, `Ω`, `→`, `×`, `≤` oraz indeksy górne i dolne. Rzadziej obsługiwane graficzne nawiasy funkcji podłogi i sufitu zastąpiono zapisami `floor(...)` i `ceil(...)`.
- Walidator kontroluje nagłówki `[plain]`, poprawność UTF-8, obecność BOM, normalizację NFC, niewidoczne lub uszkodzone znaki, poprawne maskowanie separatorów GIFT, unikatowość odpowiedzi i rozkład kluczy.
- Przed wykorzystaniem pytań do oceniania trzeba **zaimportować je do testowej kategorii Moodle i obejrzeć podgląd** na komputerze i urządzeniu mobilnym, szczególnie wzory, nierówności, polskie znaki oraz symbole matematyczne. Sam test statyczny nie potwierdza krojów pisma dostępnych w konkretnym motywie Moodle.

Zasady formatu: [dokumentacja GIFT w Moodle](https://docs.moodle.org/502/en/GIFT_format).

## Kontrola jakości

```bash
python3 scripts/validate_quizzes.py
```

Walidator sprawdza liczbę plików, identyfikatory, liczbę pytań, cztery różne odpowiedzi, pojedynczy klucz, uzasadnienie, rozkład pozycji odpowiedzi prawidłowych i poprawność zapisu znaków w Moodle. W każdym banku pozycje poprawnych odpowiedzi rozłożono po 5 na każdą z czterech możliwości. Od wersji 1.3.0 walidator odrzuca klucze okresowe, trzy jednakowe pozycje z rzędu i sześciopozycyjny naprzemienny wzorzec klucza. Kontroluje też część niedokończonych dystraktorów i odpowiedzi logicznie równoważnych typu „Nie” oraz „Nie, ponieważ…”. Nie zastępuje niezależnej recenzji poprawności naukowej ani testowego importu do Moodle. Te dwa etapy pozostają do wykonania przed ocenianiem.

**Bezpieczeństwo oceniania:** repozytorium jest publiczne, a format GIFT zawiera jawne klucze odpowiedzi. Nie używaj tych plików bezpośrednio do egzaminu o wysokiej stawce. Do takiego zastosowania przenieś bank do prywatnego miejsca, zachowaj kontrolę dostępu i przygotuj alternatywne, nieopublikowane wersje zadań.

**Granica techniczna:** quizy to osobne pliki źródłowe. Nie modyfikują `raw/*.zip`, `files/scorm_XX/`, mechanizmu ukończenia SCORM ani dziennika ocen Moodle.
