# Przebudowa pakietów SCORM (Articulate Rise 360)

**Wersja procedury:** 1.1.1 · **Data:** 2026-11-13  
**Zakres:** repozytorium `MatPomGit/aisd`, pakiety SCORM 1.2 w `raw/`.  
**Cel:** zachować materiał dydaktyczny Rise, usunąć końcowe quizy, wszystkie bloki `knowledgeCheck` i rozpoznane sekcje „Sprawdź swoją wiedzę”, a ukończenie opierać na 100% postępu. Weryfikacja wiedzy odbywa się w oddzielnym teście Moodle.

**Przed zmianą treści dowolnej lekcji:** zastosuj [standard niezależnej recenzji i przebudowy](lesson-review-and-rebuild.md) oraz wypełnij [kartę przeglądu](templates/lesson-review-template.md). Niniejszy dokument określa warunki techniczne pracy z formatem SCORM; nie zastępuje recenzji merytorycznej ani dydaktycznej.

## 1. Zasady i źródła prawdy

| Ścieżka | Rola |
|---|---|
| `raw/*.zip` | Oryginalne, niezmienne eksporty Rise, 20 kursów. Jedyny wejściowy materiał do budowania |
| `files/scorm_01/`–`files/scorm_20/` | Historyczne rozpakowane kopie; **nie są** źródłem przebudowy ZIP |
| `scripts/rise_scorm_tool.py` | Starsze narzędzie diagnostyczne; nie używać go do automatycznego usuwania quizów z tych eksportów |
| `scripts/scorm_pipeline.py` | Nowy, konserwatywny builder i walidator pakietów bez testów |
| `tests/test_scorm_pipeline.py` | Automatyczne testy poprawnych i celowo błędnych ZIP |
| `tests/scorm_runtime.test.cjs` | Izolowany test logiki ukończenia i braku oceny w runtime Rise |
| `build/scorm/` | Lokalne, tymczasowe pliki wyjściowe, poza Git |
| `dist/` | Istniejące artefakty historyczne; workflow nie nadpisuje ich i nie zatwierdza |
| `.github/workflows/scorm.yml` | Automatyczne sprawdzenie zmian i ręczne tworzenie paczek |

Oryginałów z `raw/` nie edytujemy. Nigdy nie zapisujemy nowego ZIP pod nazwą wejściową. Przy potrzebie odtworzenia historii należy użyć oryginału i zachować sumy SHA-256 oraz raport budowy.

## 2. Obsługiwane i nieobsługiwane formaty

Builder jest ograniczony do SCORM **1.2**, eksportów Rise, w których:

1. `imsmanifest.xml` znajduje się na najwyższym poziomie archiwum, a launch prowadzi do `scormdriver/indexAPI.html`.
2. Dane kursu znajdują się w rozpoznanym Base64/JSON wrapperze: `__fetchCourse() → deserialize(...)` w `scormcontent/index.html` lub `__jsonp("runtime-data.js", ...)` w `scormcontent/runtime-data.js`.
3. Kurs ma **jeden formalny quiz na końcu** albo **zero formalnych quizów**. W przypadku zera wszystkie lekcje są zachowywane, poza dokładnie rozpoznanym testem blokowym kursu nr 4 opisanym poniżej.
4. `course.exportSettings.completeWith == "quiz"`, identyfikator quizu zgadza się z `exportSettings.quizId` oraz zmienną `quizId` w HTML.
5. `storylineId == null`; w HTML występują dokładnie po jednym: `quizId`, `storylineId`, `completionPercentage` oraz `reporting`.
6. Po usunięciu quizu jego ID nie jest używane nigdzie indziej w danych kursu.

**Fail-closed:** błąd weryfikacji, wielokrotne quizy, quiz w środku kursu, nieznany wrapper, brak pól trackingowych lub SCORM 2004 powodują przerwanie. Nie obchodzimy tych zabezpieczeń podmianą tekstu ani ręcznym usuwaniem zasobów.

Ograniczenie: przekonwertowany kurs ma przestać wysyłać **ocenę quizu**, ale nadal może raportować status ukończenia i postęp. Nie oznacza to automatycznie usunięcia pozycji SCORM z dziennika ocen Moodle.

## 3. Jak działa transformacja

Przykład dla `raw/13-zasady-dzialania-i-implementacja-drzew-bst-scorm12-5s8301_d.zip`:

- Przed: 11 lekcji materiału + końcowy `Quiz` (17 pytań); raportowanie `passed-incomplete` zależne od testu.
- Po: 11 lekcji bez quizu, 12 bloków `knowledgeCheck` i 10 sekcji kontrolnych; zachowana pozostała treść.
- W `course.exportSettings`: `quizId = null`, `completeWith = "course"`, `quizComplete = false`, `completionPercentage = 100`, `reporting = "completed-incomplete"`.
- W HTML: odpowiadające zmienne runtime `quizId = null`, `storylineId = null`, `completionPercentage = 100`, `reporting = "completed-incomplete"`.
- Manifest, SCORM driver, identyfikatory lekcji i multimedia pozostają bez zmian; z list bloków usunięto elementy sprawdzania wiedzy.

ZIP jest przepakowywany przy zachowaniu nazw wpisów, kolejności, dat i metody kompresji. Sama edycja manifestu nie usunie quizu, ponieważ Rise przechowuje lekcje wewnątrz pojedynczego SCO.

### Rozpoznane wyjątki: kursy 4 i 5

- **Kurs 4** nie ma formalnego quizu, ale ostatnia lekcja „Test końcowy i omówienie rozwiązań” zawiera siedem interaktywnych bloków `knowledgeCheck` oraz klucz odpowiedzi. Reguła jest **ściśle powiązana z oryginalnym ID lekcji i listą typów 17 bloków**. Usuwa wprowadzenie do testu, pytania i klucz odpowiedzi, zachowuje wyłącznie końcowe „Najczęstsze błędy i wskazówki” (3 bloki), nie zmienia ID lekcji. Każda zmiana schematu tych bloków zatrzymuje operację. Wymagany przegląd wizualny.
- **Kurs 5** nie ma formalnego quizu, lecz zawiera 23 bloki `knowledgeCheck` i 11 sekcji kontrolnych. Builder usuwa je, zachowuje 12 lekcji i ustawia ukończenie po 100% materiału.

Pozostałe kursy zachowują lekcje i treści objaśniające, ale nie zawierają sekcji kontrolnych. Raport `build-report.json` zawiera `removed_quiz`, `knowledge_checks_removed`, `assessment_sections_removed`, `embedded_test_removed` i `manual_review`.

## 4. Lokalna przebudowa na Fedorze

Wymagane: Python 3.11+ (biblioteka standardowa), Node.js 20+ dla testu runtime oraz `unzip`.

```bash
git clone https://github.com/MatPomGit/aisd.git
cd aisd

# Analiza oryginału bez zmian
python3 scripts/scorm_pipeline.py inspect \
  raw/13-zasady-dzialania-i-implementacja-drzew-bst-scorm12-5s8301_d.zip

# Jeden pakiet
python3 scripts/scorm_pipeline.py build --course 13 --output-dir build/scorm

# Wszystkie 20 oryginałów; operacja przerywa się, jeśli jakiś format jest nieobsługiwany
python3 scripts/scorm_pipeline.py build --course all --output-dir build/scorm

# Testy jednostkowe i negatywne
python3 -m unittest discover -s tests -p 'test_scorm_pipeline.py' -v

# Test rzeczywistego runtime na każdej przebudowanej paczce
for z in build/scorm/*.zip; do
  unzip -p "$z" scormcontent/index.html | node tests/scorm_runtime.test.cjs
done

# Sumy kontrolne
(cd build/scorm && sha256sum -- *.zip)
```

Uwaga: builder nie nadpisuje plików wyjściowych. Przed ponowną przebudową usuń wyłącznie stare artefakty z `build/scorm/`. Nigdy nie usuwaj `raw/`.

Do pojedynczej walidacji porównawczej:

```bash
python3 scripts/scorm_pipeline.py validate \
  raw/13-zasady-dzialania-i-implementacja-drzew-bst-scorm12-5s8301_d.zip \
  build/scorm/13-zasady-dzialania-i-implementacja-drzew-bst-scorm12-5s8301_d-bez-testow.zip
```

W `build/scorm/` otrzymasz zmodyfikowane ZIP, `build-report.json` i listę SHA-256 w przypadku wykonania workflow.

### Bramka zatwierdzenia redakcji SCORM 01 na Pages

Katalog GitHub Pages publikuje domyślnie beztestową wersję źródłową SCORM 01, **bez niezaakceptowanych nakładek redakcyjnych**. Kandydat z `editorial/scorm01/lesson-01.json`–`lesson-11.json` jest budowany i testowany w CI, ale nie jest automatycznie udostępniany jako paczka w katalogu Pages. Mechanizm `scripts/build_scorm_pages_catalog.py` sprawdza plik `editorial/approved-releases.json`; zatwierdzenie wymaga rekordu z dokładną nazwą wydania `scorm01/lessons-01-11@2.0.0` **oraz SHA-256 identycznego ZIP**, który przeszedł test i akceptację. Przykładowy rekord ma pola `release` i `sha256`, a nie sam ciąg tekstowy. Katalog odrzuci publikację, jeśli suma nowego ZIP różni się od zatwierdzonego skrótu. Nie dopisywać zatwierdzenia przed udokumentowanym testem Moodle, ręcznym przeglądem bloków i akceptacją dydaktyczną. Nie wolno „naprawiać” błędu skrótu przez przepisanie go bez ponownej weryfikacji.

Zrzuty ekranu generowane przez Chromium obejmują **SCORM Studio i rzeczywisty odtwarzacz Rise** (11 lekcji na komputerze i telefonie). Symulacja LMS sprawdza wybrane zachowania runtime, ale nie zastępuje testu na Moodle.

## 5. GitHub Actions

Workflow: [SCORM | rebuild and validate](../.github/workflows/scorm.yml).

**Automatyczna walidacja:** po utworzeniu PR zmieniającego `raw/`, kod, testy, dokumentację lub workflow wykonywane są:

1. Testy jednostkowe, w tym przypadki wymagające odrzucenia paczki.
2. Przebudowa wszystkich 20 źródeł `raw/`, bez zapisu do repozytorium.
3. Porównanie źródła i artefaktu: identyczne zasoby i sterownik, zachowane identyfikatory lekcji; usunięte quizy, sprawdzania wiedzy i zbędne separatory.
4. Test Python/JS: zero quizów, bloków `knowledgeCheck` i nagłówków testowych, brak ukończenia przy 99%, `SetReachedEnd()` przy 100% i brak `SetScore()`.
5. Raport w podsumowaniu działania i sumy SHA-256.

**Ręczna przebudowa i pobranie ZIP:**

1. Otwórz repozytorium → **Actions** → **SCORM | rebuild and validate** → **Run workflow**.
2. Wybierz `course = all` lub numer 1–20.
3. Po zakończeniu pobierz artefakt `scorm-bez-testow-…` z ekranu runu. Zawiera zmodyfikowane ZIP, `build-report.json` i `SHA256SUMS.txt`.
4. Zachowaj identyfikator runu, SHA commita i raport jako ślad audytowy.

Workflow publikuje zbiorczy artefakt również po przebiegu na `main`. Działa na izolowanym `ubuntu-latest` z `contents: read`, bez sekretów Moodle, bez samodzielnego wdrażania na platformę. Artefakty są przechowywane przez 7 dni; po tym czasie należy uruchomić build ponownie. Nie wykonywać niezaufanych PR na prywatnych runnerach uczelni.

## 6. Weryfikacja i ograniczenia automatycznych testów

| Warstwa | Sprawdzane | Nie sprawdza |
|---|---|---|
| ZIP/manifest | CRC, ścieżki, SCORM 1.2, zasoby launch | Poprawności HTML w przeglądarce |
| Kurs Rise | Usunięte 18 quizów, 504 bloki `knowledgeCheck` i 207 sekcji kontrolnych; ukończenie po 100% | Wyświetlania wszystkich bloków na różnych ekranach |
| Dystans do oryginału | Identyczne pozostałe pliki i metadane archiwum | Semantycznej jakości materiału |
| Izolowany runtime JavaScript | `finish(99)`, `finish(100)`, `finishQuiz(...)`, brak `SetScore` | Rzeczywistej sesji LMS, logowania, suspend/resume |
| Test Moodle (ręczny, wymagany) | Import, nawigacja, wznowienie, status, brak ocen | Nie jest wykonywany przez CI |

**PASS w GitHub Actions nie jest certyfikatem SCORM ani gwarancją Moodle.** Szczególnie pierwszą paczkę z każdej wersji eksportu należy przetestować na odrębnej, testowej aktywności z nowym kontem/próbą studenta.

## 7. Konfiguracja Moodle

Dla pakietu bez quizu:

- **Metoda oceniania:** *Liczba obiektów SCO*; nie traktować tego jako oceny z testu.
- **Warunki ukończenia:** `Dodaj wymagania` → zaznaczone **Zakończony**.
- Niezaznaczone: **Wymagany minimalny wynik**, **Zaliczony**, **Otrzymaj ocenę** i **Wymagany status ukończenia od wszystkich elementów** (jeden SCO).
- Dziennik ocen: **wyłącz pozycję SCORM z agregacji** albo ustaw jej wagę na **0**, aby nie wpływała na ocenę końcową.
- Dodaj osobną aktywność **Test**, która będzie jedyną ocenianą weryfikacją wiedzy.

Po przejściu 100% materiału w raporcie SCORM 1.2 powinny wystąpić `cmi.core.lesson_status = completed` i brak nowej wartości `cmi.core.score.raw`. Kontrola samego `score.raw` nie zastępuje kontroli dziennika ocen.

**Próba integracyjna:**

1. Utwórz nową aktywność SCORM na testowym Moodle.
2. Zaimportuj wygenerowany ZIP; potwierdź start wszystkich lekcji, otwarcie multimediów i brak quizu w menu.
3. Przejdź 99%, zamknij sesję; status nie może być ukończony.
4. Otwórz ponownie (sprawdź zachowanie postępu), przejdź 100% i zamknij; oczekiwany `completed`.
5. Sprawdź „Raporty → Track Details”: status, `suspend_data`, brak nowego `score.raw` i brak interakcji z usuniętym quizem.
6. Sprawdź dziennik ocen, wyzerowaną wagę SCORM i działanie niezależnego testu Moodle.

Jeżeli studenci rozpoczęli już wcześniejszą paczkę, nie zastępuj aktywności w miejscu bez planu migracji: zmiana liczby lekcji może unieważnić istniejące `suspend_data`. Bezpieczniej udostępnić nową aktywność i zachować starą do audytu wyników.

## 8. Diagnostyka i decyzje

| Objaw | Przyczyna / działanie |
|---|---|
| `runtime-data.js missing` w starszym skrypcie | Użyj `scripts/scorm_pipeline.py`; wspiera HTML/Base64 eksportu 13 |
| `Unsupported Rise data encoding` | Inny wariant Rise/LZW; nie patchować heurystycznie, przeanalizować konkretną paczkę |
| `Expected exactly one terminal quiz` | Brak quizu, wiele quizów lub quiz w środku kursu; konieczne rozstrzygnięcie manualne |
| `Quiz tracking ID differs` | Tracking zewnętrzny, Storyline lub inny quiz; nie usuwać powiązań na ślepo |
| `Removed quiz is still referenced elsewhere` | Dodatkowe zależności od identyfikatora; ręczna analiza referencji |
| `Missing referenced resource` | Uszkodzony ZIP/manifest; ponownie wyeksportować oryginał |
| Status `incomplete` mimo 100% | Sprawdzić faktyczny progres w Rise, JS runtime, zapis LMS, stare `suspend_data` |
| Ocena w Moodle mimo braku quizu | Pozycja SCORM/Learning Objects nadal punktowana w dzienniku; zmienić agregację |
| Biały ekran po aktualizacji | Niekompatybilne stare dane sesji; uruchomić nową aktywność i nową próbę |

Zmiana algorytmu lub dopuszczenie kolejnego formatu wymaga osobnego testu regresyjnego na kopii reprezentatywnego ZIP. Oryginalne biblioteki Rise są własnością ich producentów; zmiany ograniczamy do danych pakietu, nie rozprowadzamy zmodyfikowanego silnika.

## 9. Materiały referencyjne

- [Articulate: publikacja Rise 360 dla LMS](https://www.articulatesupport.com/article/Rise-360-Publishing-a-Course-for-LMS-Distribution)
- [Articulate: SCORM completion i tracking](https://access.articulate.com/support/article/Rise-360-How-to-Track-Course-Completion-in-an-LMS)
- [Moodle: aktywność SCORM](https://docs.moodle.org/en/SCORM_activity)
- [Moodle: ustawienia aktywności SCORM](https://docs.moodle.org/en/SCORM_settings)
- [GitHub: zdarzenie workflow_dispatch](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows#workflow_dispatch)

Ta procedura nie obejmuje automatycznego wdrożenia na produkcyjny Moodle, SCORM 2004 ani migracji rozpoczętych prób.


## 10. Przeglądarkowy edytor GitHub Pages: SCORM Studio

Statyczna strona znajduje się w [`docs/editor/index.html`](editor/index.html); po włączeniu GitHub Pages jej standardowy adres to **https://matpomgit.github.io/aisd/editor/**. Strona startowa jest w [`docs/index.html`](index.html).

### Domyślna biblioteka kursów repozytorium

Źródłem prawdy pozostaje **20 oryginalnych plików ZIP w `raw/`**. GitHub Pages publikuje **20 oczyszczonych pakietów** z sufiksem `-bez-testow.zip`. Edytor domyślnie pokazuje te gotowe wersje. Wybierz kurs i kliknij **Otwórz do edycji**. Nie trzeba wcześniej pobierać pliku z GitHub ani rozpakowywać go ręcznie.

**Architektura:** ZIP jest lepszy niż rozpakowane pliki `files/scorm_XX/`, ponieważ zawiera kompletny pakiet z manifestem i sterownikiem. Publikowana paczka jest zweryfikowaną pochodną oryginału z `raw/`. Pozwala zachować `imsmanifest.xml`, ścieżki, zasoby, sterownik SCORM i strukturę archiwum. Edytor rozpakowuje ZIP **wyłącznie w pamięci przeglądarki**, modyfikuje dozwolone pola Rise i zapisuje kopię jako nowy ZIP. Praca na `files/scorm_XX/` wymagałaby odtworzenia opakowania i mogłaby wprowadzić rozbieżności względem `raw/`.

Przy każdym wdrożeniu GitHub Actions uruchamia `scripts/build_scorm_pages_catalog.py`. Skrypt usuwa quizy i sprawdzania wiedzy, generuje `catalog.json` z SHA-256 oraz **tymczasowo** tworzy oczyszczone ZIP w artefakcie Pages jako `editor/packages/`. W historii repozytorium nie powstają kopie. Niezmienione zasoby w archiwach odpowiadają bitowo oryginałom. Przeglądarka pobiera wyłącznie wybrany plik, porównuje jego długość i sumę SHA-256 z katalogiem, a niezgodny plik odrzuca. Katalog nie wymaga tokenów ani uwierzytelniania, gdyż `raw/` i GitHub Pages są publiczne.

**Zapis w edytorze oznacza pobranie nowego ZIP na komputer.** Strona statyczna nie nadpisuje `raw/` ani nie tworzy commitów. Jeżeli wynik ma być zapisany również w repozytorium, musi przejść przez normalną recenzję zmian i kontrolę CI. Oryginał należy zachować. Można też używać poprzedniego trybu „Lub otwórz własny plik ZIP”, rozwijając go pod katalogiem.

### Funkcje i sposób użycia

1. Otwórz stronę. Domyślnie wybierz gotowy kurs **bez testów**, przygotowany na podstawie `raw/`, kliknij **Otwórz do edycji**; alternatywnie rozwiń „Lub otwórz własny plik ZIP”. Limit jednego pliku: 120 MB.
2. Odczytaj listę lekcji, tytuł kursu, obecność quizu i tryb raportowania.
3. Wybierz lekcję. Możesz edytować jej tytuł, opis oraz pola tekstowe bloków Rise (w tym źródłowe fragmenty HTML).
4. W razie potrzeby rozwiń sekcję **Zaawansowane**. Możesz edytować dane JSON kursu i zatwierdzić je przyciskiem „Zastosuj JSON”. Nie modyfikuj struktury ani identyfikatorów bez dokładnej znajomości schematu.
5. W katalogu Pages testy są już usunięte. Przy wczytaniu własnego oryginalnego ZIP kliknij **Usuń testy i sprawdzania wiedzy**, aby usunąć także kontrole wewnątrz lekcji.
6. Ustaw nazwę i kliknij **Sprawdź i pobierz ZIP**. Aplikacja ponownie odczytuje nowy ZIP, sprawdza manifest, zawartość danych, tracking i bajtową identyczność zasobów niewymagających zmian.
7. Wgraj nowy ZIP do **testowej** aktywności Moodle. Sprawdź otwieranie, przejście, wznowienie, status `completed` po 100% oraz brak nowego `cmi.core.score.raw`.

Pobranie wybranego pakietu z repozytorium odbywa się przez GitHub Pages. Dalsza edycja i tworzenie wynikowego ZIP są lokalne: zmiany nie są przesyłane na serwer ani do GitHub. Biblioteka JSZip v3.10.1 jest pobierana z publicznej CDN z przypiętą sumą Subresource Integrity. Wszystkie modyfikowane pliki pozostają na urządzeniu użytkownika.

### Ograniczenia

- Obsługiwane są **wyłącznie rozpoznane warianty Rise SCORM 1.2** z zakodowanym JSON. SCORM 2004, H5P, xAPI, inne implementacje SCORM i nieznane eksporty są odrzucane.
- Nie jest to pełny wizualny kreator Rise: można zmieniać znane pola tekstowe i JSON, ale nie należy przebudowywać silnika, nawigacji ani interakcji bez dodatkowych testów.
- Nie należy uruchamiać nieznanego HTML z pakietu: edytor pokazuje go jako tekst, **nie renderuje aktywnej zawartości ZIP**.
- Usunięcie quizu zmienia dane wznowienia. Pakiet już rozpoczęty przez studentów należy opublikować w osobnej aktywności, nie nadpisywać bez migracji.
- Eksport ZIP przechodzi walidację **statyczną**; prawidłowość działania w Moodle nadal wymaga próby integracyjnej.

### Wdrożenie GitHub Pages

Automatyzacja znajduje się w `.github/workflows/scorm-editor-pages.yml`. PR uruchamia generator katalogu i testy JS na rzeczywistych paczkach z `raw/`, w tym przebudowę i walidację wszystkich 20 ZIP. Kontrole katalogu weryfikują SHA-256 każdej paczki wynikowej, identyczność pozostałych zasobów i brak obiektów oceniania. Dodatkowo Chromium automatycznie testuje interfejs: wczytanie pliku nr 13, zmianę tytułu, usunięcie testu, pobranie nowego ZIP oraz kontrolę jego zawartości. Po scaleniu do `main` workflow publikuje stronę z `docs/`, wraz z wygenerowanym katalogiem, raportem i 20 ZIP bez oceniania.

Jeśli Pages jeszcze nie jest skonfigurowane, wykonaj **Settings → Pages → Build and deployment → Source: GitHub Actions**. Nie trzeba dodawać sekretów, tokenów ani repozytorium `gh-pages`. Ponów przebieg „SCORM Studio | test and publish Pages” po włączeniu usługi, jeśli wcześniejsze wdrożenie zakończyło się błędem. Dla kontroli testów i statusu wdrożenia przejdź do repozytorium → **Actions**.

Strona używa statycznych ścieżek względnych, dzięki czemu działa również w gałęzi Pages z katalogu `docs/`.


## 11. Pakiety bez quizów i sprawdzania wiedzy (13 listopada 2026)

Z 20 oryginalnych paczek przeprowadzono spójną przebudowę:

- Usunięto **18 formalnych quizów końcowych Rise** oraz osobny test blokowy w kursie 04 (zachowując końcowe wskazówki).
- Usunięto **504 bloki `knowledgeCheck`** i **207 sekcji „Sprawdź swoją wiedzę” / „Check Your Understanding”** wraz z ćwiczeniami znajdującymi się w sekcjach kontrolnych i ich zbędnymi separatorami.
- Zachowano objaśnienia, przykłady, multimedia i interakcje edukacyjne niezwiązane z testami.
- Ustawiono `quizId = null`, `completionPercentage = 100` i `reporting = "completed-incomplete"`, bez punktowej oceny quizu.
- Oryginały w `raw/` pozostały niezmienione. Każda przygotowana paczka opublikowana w Pages ma sufiks `-bez-testow.zip`.

**Pobieranie pojedynczych kursów:** [SCORM Studio](https://matpomgit.github.io/aisd/editor/) pokazuje 20 gotowych pakietów bez sprawdzania wiedzy. Po wybraniu kursu można go edytować i pobrać jako nowy ZIP.

**Pobranie kompletu:** artefakty najnowszego poprawnego przebiegu [SCORM | rebuild and validate](../.github/workflows/scorm.yml) na `main` zawierają 20 zmodyfikowanych plików ZIP, `build-report.json` i `SHA256SUMS.txt`.

**Walidacja:** kontrolowane są manifest, CRC ZIP, komplet zasobów i niezmienność plików innych niż dane kursu; zero obiektów `quiz`, `knowledgeCheck` i nagłówków sekcji oceniania; kod raportowania ukończenia; przeglądarkowa edycja i ponowny eksport. Testy nie zastępują próby integracyjnej na instancji Moodle, zwłaszcza kontroli wznowienia postępu i dziennika ocen.

