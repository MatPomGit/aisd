# Quizy do wykładów AIiSD (W01–W20)

**Wersja zestawu:** 1.5.0 (W01–W20)  
**Data:** 2026-11-18  
**Zakres:** 20 banków po 20 pytań (400 pytań), w tym pytania jednokrotnego i wielokrotnego wyboru.

## Organizacja

Każdy plik `quiz_wXX.gift` zawiera 20 pytań. W wersji 1.5.0 dodano merytoryczną informację zwrotną do wszystkich 1600 wariantów odpowiedzi, a uzasadnienia wszystkich 400 pytań uzupełniono o jawne wskazanie poprawnych wariantów i reguły rozumowania. W wersji 1.4.0 poprawiono błędny klucz W10-Q01, niejednoznaczne odpowiedzi, konstrukcję zadań i polszczyznę, a sześć pytań przekształcono w wielokrotny wybór. Rozszerzono też walidację GIFT. W wersji 1.3.0 przeprowadzono ponowną recenzję W02–W20 (380 pytań): przebudowano merytorycznie 143 pytania, naprawiono niejednoznaczności i urwane dystraktory, ograniczono powtórzenia tematyczne, uzupełniono zadania o rozumowanie na konkretnych przykładach oraz przemieszano klucze we wszystkich 19 bankach. Zachowano identyfikatory i cztery warianty odpowiedzi. W wersji 1.2.2 dodatkowo poprawiono bank W01 na podstawie niezależnej recenzji merytorycznej: doprecyzowano niezmienniki i kontrakty, wymieniono oczywiste dystraktory, ograniczono powtórzenia tematyczne i usunięto okresowy układ poprawnych odpowiedzi. W wersji 1.2.0 zredagowano większość pytań w każdym banku: wyeliminowano podpowiedzi stylistyczne, przebudowano dystraktory i zastąpiono część powtarzalnych zadań analizą konkretnych przypadków. Każdy bank odpowiada wykładowi XX w kolejności kursu. Pliki są zgodne z formatem **GIFT** służącym do importu do bazy pytań Moodle. Każde pytanie zawiera cztery merytorycznie powiązane możliwości, jedną lub kilka prawidłowych odpowiedzi (zależnie od jawnego typu pytania) oraz informację zwrotną z uzasadnieniem.

- `quiz_w01.gift`–`quiz_w05.gift`: podstawy algorytmiki, RAM, pseudokod, analiza kosztu, notacje asymptotyczne;
- `quiz_w06.gift`–`quiz_w10.gift`: tablice, macierze, rekurencja, listy liniowe, stosy;
- `quiz_w11.gift`–`quiz_w15.gift`: kolejki, drzewa, BST, kopce, grafy;
- `quiz_w16.gift`–`quiz_w20.gift`: przeszukiwanie, teoria sortowania, algorytmy sortowania, metody projektowania.

## Import do Moodle

1. W Moodle otwórz **Baza pytań → Import → GIFT**.
2. Dla każdego wykładu utwórz odrębną kategorię, np. `AIiSD / W01`, i zaimportuj odpowiadający jej plik UTF-8.
3. Utwórz **osobną aktywność Quiz** dla każdej kategorii. Nie przywracaj testów w pakietach Rise/SCORM.
4. Włącz losową kolejność odpowiedzi i, jeśli jest to uzasadnione dydaktycznie, losowanie pytań z kategorii.
5. W aktywności Moodle wybierz **Zachowanie pytań → Natychmiastowa informacja zwrotna** (*Immediate feedback*), jeśli komentarz ma pojawiać się po sprawdzeniu każdego zadania, a nie dopiero po ukończeniu całego quizu.
6. W sekcji **Opcje przeglądu** dla etapu **Podczas próby** włącz **Poprawność odpowiedzi**, **Informację zwrotną dotyczącą odpowiedzi** (*Specific feedback*) i **Ogólną informację zwrotną** (*General feedback*); opcjonalnie również **Poprawną odpowiedź**. Nazwy ustawień mogą różnić się zależnie od wersji językowej Moodle. Bez tych ustawień samo zaimportowanie pliku GIFT **nie zapewni** wyświetlania informacji zwrotnych po każdym pytaniu.
7. Przed ocenianym użyciem sprawdź na testowym koncie studenta podgląd pytań, działanie przycisku **Sprawdź**, punktację, informacje zwrotne i ograniczenia podejść. W pytaniach wielokrotnego wyboru zweryfikuj zaznaczanie wielu pól, naliczanie punktów częściowych oraz brak pełnych punktów przy zaznaczeniu wszystkich wariantów.

## Informacja zwrotna dla studenta

Każde z **400 pytań** zawiera dwa poziomy objaśnień:

- **Komentarz do odpowiedzi** po separatorze GIFT `#` w każdym z czterech wariantów (łącznie **1600** komentarzy). Po sprawdzeniu pytania student otrzymuje informację, czy wybrany wariant jest poprawny, oraz zasadę lub obliczenie uzasadniające ocenę. W sześciu pytaniach wielokrotnego wyboru każdy wariant otrzymuje osobne objaśnienie dotyczące jego prawdziwości.
- **Uzasadnienie całego zadania** po separatorze `####`. Wskazuje prawidłową odpowiedź lub wszystkie odpowiedzi oraz wyjaśnia właściwą metodę rozwiązania. Pozostaje dostępne niezależnie od wybranego dystraktora, gdy wyświetlanie ogólnej informacji zwrotnej jest włączone w Moodle.

Komentarze nie są podpowiedziami wyświetlanymi przed udzieleniem odpowiedzi. Moment ujawnienia ustawia się w aktywności Moodle, nie w pliku GIFT. W testach ocenianych z odroczoną informacją zwrotną można wyświetlać objaśnienia dopiero po zakończeniu próby, zgodnie z polityką oceniania. W repozytorium nie umieszczamy ustawień wymuszających ujawnienie klucza przed oceną.

Przykładowa składnia:

```gift
::PRZYKLAD::[plain]Ile wynosi 2+2? {
  =4#Prawidłowo. Dodajemy dwie dwójki, otrzymując cztery.
  ~5#Nie. Wynik dodawania 2+2 to cztery, a nie pięć.
  ~3#Nie. Dodając do dwóch kolejne dwa, otrzymujemy cztery.
  ~2#Nie. Wynik jest większy od każdego z dodatnich składników.
  ####Poprawna odpowiedź to 4, ponieważ 2+2=4.
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
- Pytanie jednokrotnego wyboru ma dokładnie jedną poprawną odpowiedź. Pytanie wielokrotnego wyboru musi zawierać polecenie „Zaznacz wszystkie poprawne odpowiedzi”, co najmniej dwie poprawne odpowiedzi oraz procentową punktację GIFT. W obu przypadkach zachowujemy uzasadnienie i identyfikator, a w Moodle losujemy kolejność odpowiedzi.
- Nie wolno maskować niejednoznaczności wielokrotnym wyborem: każda prawdziwa odpowiedź musi być zamierzona, a polecenie i dystraktory muszą sprawdzać odrębne aspekty rozumowania.

Powyższe zasady ograniczają zgadywanie na podstawie konstrukcji testu. Nie gwarantują, że każde pytanie jest odporne na eliminację bez wiedzy; wymagałoby to pilotażu i analizy psychometrycznej odpowiedzi studentów (trudność, moc różnicująca, częstość wyboru poszczególnych dystraktorów).

## Głębokość sprawdzanej wiedzy

Celem kolejnych redakcji jest następujący rozkład pytań w banku 20-elementowym: pięć zadań analizujących wykonanie algorytmu, pięć dotyczących diagnozy błędu lub kontrprzykładu, cztery wymagające doboru struktury albo strategii, cztery sprawdzające uzasadnienie poprawności lub kosztu oraz najwyżej dwa pytania pojęciowe. To kierunek rozwoju banków, **nie deklaracja, że każde 20 pytań już idealnie spełnia tę proporcję**.

Każdy dystraktor powinien reprezentować prawdopodobny błąd rozumowania, np. pomylenie górnego i dolnego ograniczenia, błędne przejście po wskaźnikach lub przyjęcie nieudowodnionej zachłanności. Rachunek liczbowy bez interpretacji ma ograniczoną wartość pomiarową. Odpowiedzi i uzasadnienia nie mogą sugerować klucza przez długość, oczywiste sformułowania lub niepełne zdania.

## Polszczyzna i wyświetlanie w Moodle

Wszystkie 400 pytań mają jawny znacznik formatu `[plain]`. Moodle zapisuje wówczas treść pytań, odpowiedzi i uzasadnień jako zwykły tekst, bez interpretowania nierówności `a<b`, `a>b` czy zapisów indeksów jako znaczników HTML. Nie należy umieszczać znaczników HTML ani encji `&lt;` i `&gt;` w tych polach. Odwołania do funkcji, instrukcji oraz standardowych nazw algorytmów zachowują pisownię stosowaną w pseudokodzie.

- Pliki są kodowane jako **UTF-8 bez BOM** i używają normalizacji **Unicode NFC**, potrzebnej m.in. dla polskich znaków.
- W treści dosłowne znaki sterujące GIFT `~`, `=`, `#`, `{` i `}` trzeba poprzedzić ukośnikiem `\`. Nie dotyczy to separatorów składniowych: `=`/`~` na początku wariantu, `#` pomiędzy odpowiedzią a jej komentarzem oraz `####` przed uzasadnieniem całego pytania.
- Zachowano standardowe symbole matematyczne Unicode, takie jak `Θ`, `Ω`, `→`, `×`, `≤` oraz indeksy górne i dolne. Rzadziej obsługiwane graficzne nawiasy funkcji podłogi i sufitu zastąpiono zapisami `floor(...)` i `ceil(...)`.
- Walidator kontroluje nagłówki `[plain]`, poprawność UTF-8, obecność BOM, normalizację NFC, niewidoczne lub uszkodzone znaki, poprawne maskowanie separatorów GIFT, unikatowość odpowiedzi, rozkład kluczy jednokrotnego wyboru i wagi wyboru wielokrotnego.
- Dla wyboru wielokrotnego stosujemy warianty `~%50%Poprawna...` i `~%-50%Niepoprawna...` (przy dwóch poprawnych i dwóch błędnych odpowiedziach). Suma dodatnich wag wynosi 100%, a suma ujemnych nie mniej niż 100% wartości bezwzględnej. Dzięki temu zaznaczenie wszystkich opcji nie zapewnia punktów. Nie używamy znaku `=` dla wielokrotnego wyboru.
- Przed wykorzystaniem pytań do oceniania trzeba **zaimportować je do testowej kategorii Moodle i obejrzeć podgląd** na komputerze i urządzeniu mobilnym, szczególnie wzory, nierówności, polskie znaki oraz symbole matematyczne. Sam test statyczny nie potwierdza krojów pisma dostępnych w konkretnym motywie Moodle.

Zasady formatu: [dokumentacja GIFT w Moodle](https://docs.moodle.org/502/en/GIFT_format).

## Kontrola jakości

```bash
python3 scripts/validate_quizzes.py
```

Walidator sprawdza liczbę plików, identyfikatory, liczbę pytań, cztery różne odpowiedzi, poprawność typów i wag odpowiedzi, obecność 1600 komentarzy do wariantów, obecność 400 ogólnych uzasadnień, ich minimalną treść oraz zapis znaków w Moodle. W pytaniach jednokrotnego wyboru kontroluje rozkład kluczy. W bankach mieszanych dopuszcza niewielkie odchylenie od równomiernego rozkładu ze względu na osobny sposób oceniania wyboru wielokrotnego. Dla pytań jednokrotnego wyboru walidator odrzuca klucze okresowe, trzy jednakowe pozycje z rzędu i sześciopozycyjny naprzemienny wzorzec klucza. Sprawdza też sumy wag odpowiedzi wielokrotnego wyboru i część niedokończonych dystraktorów i odpowiedzi logicznie równoważnych typu „Nie” oraz „Nie, ponieważ…”. Nie zastępuje niezależnej recenzji poprawności naukowej ani testowego importu do Moodle. Te dwa etapy pozostają do wykonania przed ocenianiem.

**Bezpieczeństwo oceniania:** repozytorium jest publiczne, a format GIFT zawiera jawne klucze odpowiedzi. Nie używaj tych plików bezpośrednio do egzaminu o wysokiej stawce. Do takiego zastosowania przenieś bank do prywatnego miejsca, zachowaj kontrolę dostępu i przygotuj alternatywne, nieopublikowane wersje zadań.

**Granica techniczna:** quizy to osobne pliki źródłowe. Nie modyfikują `raw/*.zip`, `files/scorm_XX/`, mechanizmu ukończenia SCORM ani dziennika ocen Moodle.
