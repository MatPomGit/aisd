# Przebudowa pakietów SCORM (Articulate Rise 360)

**Wersja procedury:** 1.0.0 · **Data:** 2026-11-12  
**Zakres:** repozytorium `MatPomGit/aisd`, pakiety SCORM 1.2 w `raw/`.  
**Cel:** pozostawić materiał dydaktyczny Rise, usunąć końcowy quiz i jego ocenę, a ukończenie opierać na 100% postępu. Weryfikacja wiedzy odbywa się w oddzielnym teście Moodle.

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
- Po: 11 lekcji bez quizu, usunięty obiekt z `course.lessons`.
- W `course.exportSettings`: `quizId = null`, `completeWith = "course"`, `quizComplete = false`, `completionPercentage = 100`, `reporting = "completed-incomplete"`.
- W HTML: odpowiadające zmienne runtime `quizId = null`, `storylineId = null`, `completionPercentage = 100`, `reporting = "completed-incomplete"`.
- Manifest, SCORM driver, wszystkie pozostałe lekcje i zasoby pozostają bez zmian.

ZIP jest przepakowywany przy zachowaniu nazw wpisów, kolejności, dat i metody kompresji. Sama edycja manifestu nie usunie quizu, ponieważ Rise przechowuje lekcje wewnątrz pojedynczego SCO.

### Rozpoznane wyjątki: kursy 4 i 5

- **Kurs 4** nie ma formalnego quizu, ale ostatnia lekcja „Test końcowy i omówienie rozwiązań” zawiera siedem interaktywnych bloków `knowledgeCheck` oraz klucz odpowiedzi. Reguła jest **ściśle powiązana z oryginalnym ID lekcji i listą typów 17 bloków**. Usuwa wprowadzenie do testu, pytania i klucz odpowiedzi, zachowuje wyłącznie końcowe „Najczęstsze błędy i wskazówki” (3 bloki), nie zmienia ID lekcji. Każda zmiana schematu tych bloków zatrzymuje operację. Wymagany przegląd wizualny.
- **Kurs 5** już nie zawiera quizu ani testu końcowego. Builder zachowuje wszystkie 12 lekcji i normalizuje śledzenie do ukończenia po 100% materiału.

Pozostałe kursy z formalnym quizem zachowują swoje lekcje dydaktyczne bez zmian. Wynik i wariant transformacji znajdują się w `build-report.json` (`removed_quiz`, `embedded_test_removed`, `manual_review`).

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
  build/scorm/13-zasady-dzialania-i-implementacja-drzew-bst-scorm12-5s8301_d-noquiz.zip
```

W `build/scorm/` otrzymasz zmodyfikowane ZIP, `build-report.json` i listę SHA-256 w przypadku wykonania workflow.

## 5. GitHub Actions

Workflow: [SCORM | rebuild and validate](../.github/workflows/scorm.yml).

**Automatyczna walidacja:** po utworzeniu PR zmieniającego `raw/`, kod, testy, dokumentację lub workflow wykonywane są:

1. Testy jednostkowe, w tym przypadki wymagające odrzucenia paczki.
2. Przebudowa wszystkich 20 źródeł `raw/`, bez zapisu do repozytorium.
3. Porównanie źródła i artefaktu: identyczne zasoby, 11 oryginalnych lekcji w przykładzie nr 13, zmienione jedynie dane kursu i pola trackingowe.
4. Test JS: brak ukończenia przy postępie 99%, `SetReachedEnd()` przy 100%, brak `SetScore()` i `SetPassed()` dla usuniętego quizu.
5. Raport w podsumowaniu działania i sumy SHA-256.

**Ręczna przebudowa i pobranie ZIP:**

1. Otwórz repozytorium → **Actions** → **SCORM | rebuild and validate** → **Run workflow**.
2. Wybierz `course = all` lub numer 1–20.
3. Po zakończeniu pobierz artefakt `scorm-noquiz-…` z ekranu runu. Zawiera zmodyfikowane ZIP, `build-report.json` i `SHA256SUMS.txt`.
4. Zachowaj identyfikator runu, SHA commita i raport jako ślad audytowy.

Workflow działa na izolowanym `ubuntu-latest` z `contents: read`, bez sekretów Moodle, bez samodzielnego wdrażania na platformę. Artefakty są przechowywane przez 7 dni; po tym czasie należy uruchomić build ponownie. Nie wykonywać niezaufanych PR na prywatnych runnerach uczelni.

## 6. Weryfikacja i ograniczenia automatycznych testów

| Warstwa | Sprawdzane | Nie sprawdza |
|---|---|---|
| ZIP/manifest | CRC, ścieżki, SCORM 1.2, zasoby launch | Poprawności HTML w przeglądarce |
| Kurs Rise | Zachowanie treści wszystkich lekcji poza quizem, ustawienia ukończenia | Wyświetlania wszystkich bloków na różnych ekranach |
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

Statyczna strona znajduje się w [\`docs/editor/index.html\`](editor/index.html); po włączeniu GitHub Pages jej standardowy adres to **https://matpomgit.github.io/aisd/editor/**. Strona startowa jest w [\`docs/index.html\`](index.html).

### Funkcje i sposób użycia

1. Otwórz stronę i przeciągnij **oryginalny ZIP Articulate Rise 360 SCORM 1.2** do obszaru wyboru. Limit jednego pliku: 120 MB.
2. Odczytaj listę lekcji, tytuł kursu, obecność quizu i tryb raportowania.
3. Wybierz lekcję. Możesz edytować jej tytuł, opis oraz pola tekstowe bloków Rise (w tym źródłowe fragmenty HTML).
4. W razie potrzeby rozwiń sekcję **Zaawansowane**. Możesz edytować dane JSON kursu i zatwierdzić je przyciskiem „Zastosuj JSON”. Nie modyfikuj struktury ani identyfikatorów bez dokładnej znajomości schematu.
5. Kliknij **Usuń test końcowy i oceny**. Przetwarzanie odpowiada sprawdzonemu algorytmowi z \`scripts/scorm_pipeline.py\`. Rozpoznaje formalny test na końcu kursu, specyficzny test blokowy kursu 04 oraz pakiet bez testu.
6. Ustaw nazwę i kliknij **Sprawdź i pobierz ZIP**. Aplikacja ponownie odczytuje nowy ZIP, sprawdza manifest, zawartość danych, tracking i bajtową identyczność zasobów niewymagających zmian.
7. Wgraj nowy ZIP do **testowej** aktywności Moodle. Sprawdź otwieranie, przejście, wznowienie, status \`completed\` po 100% oraz brak nowego \`cmi.core.score.raw\`.

Edycja jest lokalna w przeglądarce: ZIP nie jest przesyłany na serwer ani do GitHub. Biblioteka JSZip v3.10.1 jest pobierana z publicznej CDN z przypiętą sumą Subresource Integrity. Wszystkie modyfikowane pliki pozostają na urządzeniu użytkownika.

### Ograniczenia

- Obsługiwane są **wyłącznie rozpoznane warianty Rise SCORM 1.2** z zakodowanym JSON. SCORM 2004, H5P, xAPI, inne implementacje SCORM i nieznane eksporty są odrzucane.
- Nie jest to pełny wizualny kreator Rise: można zmieniać znane pola tekstowe i JSON, ale nie należy przebudowywać silnika, nawigacji ani interakcji bez dodatkowych testów.
- Nie należy uruchamiać nieznanego HTML z pakietu: edytor pokazuje go jako tekst, **nie renderuje aktywnej zawartości ZIP**.
- Usunięcie quizu zmienia dane wznowienia. Pakiet już rozpoczęty przez studentów należy opublikować w osobnej aktywności, nie nadpisywać bez migracji.
- Eksport ZIP przechodzi walidację **statyczną**; prawidłowość działania w Moodle nadal wymaga próby integracyjnej.

### Wdrożenie GitHub Pages

Automatyzacja znajduje się w \`.github/workflows/scorm-editor-pages.yml\`. PR uruchamia testy JS na rzeczywistych paczkach z \`raw/\`. Po scaleniu do \`main\` i po **jednorazowej konfiguracji Pages** workflow publikuje wyłącznie katalog \`docs/\`.

Jeśli Pages jeszcze nie jest skonfigurowane, wykonaj **Settings → Pages → Build and deployment → Source: GitHub Actions**. Nie trzeba dodawać sekretów, tokenów ani repozytorium \`gh-pages\`. Ponów przebieg „SCORM Studio | test and publish Pages” po włączeniu usługi, jeśli wcześniejsze wdrożenie zakończyło się błędem. Dla kontroli testów i statusu wdrożenia przejdź do repozytorium → **Actions**.

Strona używa statycznych ścieżek względnych, dzięki czemu działa również w gałęzi Pages z katalogu \`docs/\`.
