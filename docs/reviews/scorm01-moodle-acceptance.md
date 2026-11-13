# SCORM 01 — protokół odbioru na docelowej instancji Moodle

**Wersja szablonu:** 1.0.0 · **Status:** NIE PRZEPROWADZONO · **Powiązania:** [PR #14](https://github.com/MatPomGit/aisd/pull/14), [#12](https://github.com/MatPomGit/aisd/issues/12)

Ten dokument jest **formularzem dowodowym do wypełnienia po rzeczywistym teście**. Żadna pozycja nie jest zaliczona na podstawie GitHub Actions ani lokalnego emulatora LMS.

## Metadane obowiązkowe

| Pole | Wartość do uzupełnienia |
|---|---|
| Data i osoba wykonująca test | NIE UZUPEŁNIONO |
| Adres/identyfikator testowego kursu Moodle (bez tokenów, haseł i danych osobowych) | NIE UZUPEŁNIONO |
| Wersja Moodle i konfiguracja SCORM | NIE UZUPEŁNIONO |
| Git SHA PR (wersja testowana) | NIE UZUPEŁNIONO |
| SHA-256 wynikowego `.zip` | NIE UZUPEŁNIONO |
| Identyfikator testowego konta (zanonimizowany) | NIE UZUPEŁNIONO |
| Raport i dowody testu (linki do niepublicznych materiałów) | NIE UZUPEŁNIONO |

## Warunki wstępne

W wydzielonym kursie/testowej aktywności Moodle importować nowy ZIP SCORM 1.2 z 11 lekcjami, **bez punktowego quizu**. Ustawić ukończenie na status `completed`, nie na wynik punktowy; nie włączać SCORM do agregacji ocen. Użyć świeżego testowego konta i próby, aby wcześniejsze dane `score.raw` nie zniekształcały wyniku. Zapisać ustawienia aktywności jako materiał dowodowy.

## Testy odbiorcze

| ID | Krok wykonywany na Moodle | Warunek PASS | Wynik | Dowód |
|---|---|---|---|---|
| M01 | Nowa aktywność SCORM → otworzyć i przejść przez wszystkie 11 lekcji | Brak brakujących zasobów, błędów JS, nieprawidłowego formatowania i blokady nawigacji | ☐ NIE WYKONANO | — |
| M02 | Zatrzymać się przed ukończeniem wszystkich lekcji | Status w Moodle nadal `incomplete`; brak oceny liczbowej | ☐ NIE WYKONANO | — |
| M03 | Przejść kilka części, zamknąć aktywność i zalogować się ponownie tym samym użytkownikiem | Wznowienie prawidłowej lekcji, zachowane dane `cmi.suspend_data` i postęp | ☐ NIE WYKONANO | — |
| M04 | Dokończyć cały kurs, osiągnąć 100% postępu | Status `cmi.core.lesson_status = completed` | ☐ NIE WYKONANO | — |
| M05 | Zweryfikować dane SCORM i log raportowania na nowej próbie | Nie pojawia się nowy wynik `cmi.core.score.raw` ani wywołanie `SetScore` | ☐ NIE WYKONANO | — |
| M06 | Otworzyć dziennik ocen Moodle jako prowadzący | Wpis SCORM nie wpływa na ocenę końcową; osobny test może być oceniany niezależnie | ☐ NIE WYKONANO | — |
| M07 | Przejść tabs/accordion/process i kod RAM na desktop oraz telefonie | Każdy element da się obsłużyć, tekst jest czytelny, brak poziomego obcięcia | ☐ NIE WYKONANO | — |
| M08 | Sprawdzić dostęp klawiaturą i czytnikiem ekranu dla reprezentatywnych kontrolek | Logiczna kolejność fokusu, nazwy kontrolek i ogłoszenia stanu rozwinięcia | ☐ NIE WYKONANO | — |
| M09 | Odłączyć/ponownie otworzyć kurs i porównać identyfikatory lekcji | Brak utraty postępu i błędnego przypisania ukończeń po aktualizacji | ☐ NIE WYKONANO | — |

## Dane z symulacji, które nie zamykają M01–M09

[CI z 13.11.2026](https://github.com/MatPomGit/aisd/actions/runs/43487615640) potwierdziło zachowanie funkcji `Runtime` Rise z lokalnym, izolowanym adapterem LMS: zapamiętanie przykładowego postępu, wznowienie po przeładowaniu, `incomplete` przy 99%, `completed` przy 100% oraz brak wywołania `SetScore`. Raport znajduje się w artefakcie `scorm01-editor-and-rise-qa-104`, `scorm-lms-simulation/report.json`.

**Wszystkie M01–M09 pozostają NIE WYKONANO**, ponieważ żadnej z tych operacji nie wykonano na rzeczywistej instancji Moodle. Test syntetyczny używał 407 znaków zapamiętanego stanu i nie obejmował całej ścieżki studenta ani agregacji ocen. Sam test struktury 14 interakcji × dwa widoki także nie jest manualną recenzją dostępności każdego elementu.

## Reguły akceptacji

Wynik **PASS** wolno wpisać tylko po wykonaniu kroku i przypięciu dowodu. Wynik **FAIL** wymaga opisu błędu, zrzutu lub logu, wersji środowiska i nowego testu po poprawce. Wynik **NIE WYKONANO** nie jest PASS.

Jeżeli testowana jest **aktualizacja istniejącej aktywności**, a nie nowa aktywność, należy wykonać osobną próbę migracji stanu. Zachowanie identyfikatorów 11 lekcji w pakiecie nie gwarantuje automatycznie zgodności `suspend_data` między dwiema wersjami.

## Decyzja wydawnicza

- [ ] Wszystkie krytyczne testy M01–M07 mają dowody PASS.
- [ ] Dostępność (M08) i aktualizacja/przeniesienie postępu (M09) ocenione oraz udokumentowane.
- [ ] Osobna akceptacja merytoryczna i dydaktyczna prowadzącego.
- [ ] Odnotowano wynik niezależnej recenzji wizualnej każdego zmienionego bloku.
- [ ] Osoba zatwierdzająca i data: **NIE UZUPEŁNIONO**.

**Dopóki bramki nie są zamknięte:** PR #14 pozostaje Draft, a lista `editorial/approved-releases.json` pusta. Dopiero osobny PR wydawniczy, po dowodowym odbiorze, może umieścić rekord z `release = scorm01/lessons-01-11@2.0.0` i **SHA-256 sprawdzonego ZIP** na liście zatwierdzonych wydań. Zmiana choćby jednego bajtu od czasu akceptacji musi spowodować odmowę publikacji.
