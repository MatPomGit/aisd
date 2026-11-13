# Dokumentacja AIiSD

- [Standard niezależnej recenzji i przebudowy wszystkich lekcji](lesson-review-and-rebuild.md)
- [Szablon karty przeglądu lekcji](templates/lesson-review-template.md)
- [Mapa 20 tematów i granic dydaktycznych](curriculum-map.md)
- [Plan redakcji SCORM 01](scorm01-editorial-plan.md)
- [Standard polszczyzny i narracji akademickiej](style-guide.md)
- [Edytor SCORM Studio na GitHub Pages](editor/) — edycja kursu i pobranie ZIP w przeglądarce
- [Pakiety SCORM z Articulate Rise: przebudowa, walidacja i wdrażanie do Moodle](scorm.md)

Źródła niezmienne: [`../raw/`](../raw/). Skrypt przebudowy: [`../scripts/scorm_pipeline.py`](../scripts/scorm_pipeline.py). GitHub Actions: [`../.github/workflows/scorm.yml`](../.github/workflows/scorm.yml).

Zasady obowiązują w każdej lekcji każdego z 20 pakietów. Najpierw wypełnij kartę recenzji, następnie przeprowadź odtwarzalną przebudowę i testy; zielony wynik CI nie zastępuje testu Moodle.
