import {
  ScormError, MAX_ZIP_SIZE, copyJSON, validateCourse, openRiseZip,
  makeUngraded, assessmentStats, listEditableFields, buildRiseZip, finalFilename
} from "./core.mjs";

const el = id => document.getElementById(id);
const ui = {
  input: el("fileInput"), choose: el("chooseButton"), dropzone: el("dropzone"),
  fileLine: el("fileLine"), message: el("message"), workspace: el("workspace"),
  count: el("lessonCount"), quiz: el("quizState"), quizDetail: el("quizDetail"),
  completion: el("completionState"), reporting: el("reportingState"),
  remove: el("removeQuiz"), reset: el("resetButton"), transform: el("transformNote"),
  lessonList: el("lessonList"), lessonEditor: el("lessonEditor"),
  courseTitle: el("courseTitle"), advanced: el("advancedPanel"),
  json: el("jsonEditor"), applyJson: el("applyJson"), refreshJson: el("refreshJson"),
  filename: el("outputFilename"), download: el("downloadButton"),
  repoSelect: el("repoCourseSelect"), openRepo: el("openRepoCourse"),
  repoMeta: el("repoCourseMeta"), catalogStatus: el("catalogStatus"),
  localUpload: el("localUpload")
};
const state = { doc: null, lessonIndex: 0, busy: false, dirty: false, catalog: [] };
function markDirty() { state.dirty = true; }
function canReplace() {
  return !state.dirty || window.confirm("Masz niezapisane zmiany. Otworzyć inny plik i je odrzucić?");
}

function message(text, kind = "info") {
  ui.message.hidden = false;
  ui.message.textContent = text;
  ui.message.className = "message message-" + kind;
}
function busy(value) {
  state.busy = value;
  for (const button of [ui.choose, ui.remove, ui.reset, ui.applyJson,
                        ui.refreshJson, ui.download]) button.disabled = value;
  ui.repoSelect.disabled = value || state.catalog.length === 0;
  ui.openRepo.disabled = value || state.catalog.length === 0;
  ui.dropzone.classList.toggle("is-busy", value);
}
function node(tag, cls, text) {
  const element = document.createElement(tag);
  if (cls) element.className = cls;
  if (text !== undefined) element.textContent = text;
  return element;
}
function writeHint(parent, content) {
  parent.appendChild(node("p", "hint", content));
}
function labelControl(parent, text, value, multiline, callback, cssClass = "") {
  const wrapper = node("div", "field " + cssClass);
  const id = "field-" + Math.random().toString(36).slice(2);
  const label = node("label", "", text);
  label.htmlFor = id;
  const input = node(multiline ? "textarea" : "input");
  input.id = id;
  if (multiline) {
    input.rows = 3;
    input.spellcheck = false;
  } else input.type = "text";
  input.value = value ?? "";
  input.addEventListener("input", () => { markDirty(); callback(input.value); });
  wrapper.append(label, input);
  parent.appendChild(wrapper);
  return input;
}
function courseTitle() {
  const doc = state.doc;
  return doc.data.course.exportSettings.title || doc.data.course.title || "Kurs bez tytułu";
}
function getScoreMode() {
  const doc = state.doc;
  return doc.transform
    ? "Ukończenie 100%" : (doc.tracking.quizId ? "Ocena quizu" : "Postęp / status");
}
function renderStats() {
  const doc = state.doc;
  const lessons = doc.data.course.lessons;
  const quizCount = lessons.filter(l => l.type === "quiz").length;
  const checkCount = assessmentStats(doc.data).knowledgeChecks;
  const knownBlock = lessons.some(l => l.id === "cmiej97dl000d207092aujenc" &&
                                       l.title === "Test końcowy i omówienie rozwiązań");
  ui.count.textContent = String(lessons.length);
  ui.quiz.textContent = doc.transform ? "Wyłączony" :
    quizCount ? "Obecny" : knownBlock ? "Blokowy" : "Brak";
  ui.quizDetail.textContent = doc.transform || (quizCount ?
    "Formalny quiz Rise · " + quizCount + ", sprawdzania wiedzy: " + checkCount : knownBlock ?
    "Test w blokach lekcji · sprawdzania wiedzy: " + checkCount :
    "Sprawdzania wiedzy: " + checkCount);
  ui.completion.textContent = getScoreMode();
  ui.reporting.textContent = doc.transform ? "completed-incomplete" :
    String(doc.tracking.reporting);
  ui.transform.textContent = doc.transform
    ? doc.transform + ". Usunięto " + (doc.removedChecks || 0) +
      " bloków sprawdzania wiedzy. Test Moodle musi być osobną aktywnością."
    : doc.tracking.quizId
      ? "Ten pakiet pierwotnie śledził wynik quizu. Usuń test przed publikacją, jeśli ma pozostać wyłącznie materiałem."
      : checkCount
        ? "Wykryto " + checkCount + " bloków sprawdzania wiedzy. Użyj przycisku usuwania."
        : "Kurs nie zawiera quizów ani sprawdzania wiedzy. Ocena odbywa się w osobnym teście Moodle.";
  ui.remove.disabled = state.busy || Boolean(doc.transform);
  ui.remove.textContent = doc.transform ? "Testy i sprawdzania wiedzy usunięte ✓" :
    "Usuń testy i sprawdzania wiedzy";
}
function renderLessons() {
  const list = ui.lessonList;
  list.replaceChildren();
  const lessons = state.doc.data.course.lessons;
  lessons.forEach((lesson, index) => {
    const button = node("button", "lesson-item" +
      (state.lessonIndex === index ? " is-active" : ""));
    button.type = "button";
    button.setAttribute("role", "option");
    button.setAttribute("aria-selected", String(state.lessonIndex === index));
    const n = node("span", "lesson-index", String(index + 1).padStart(2, "0"));
    const info = node("span", "lesson-info");
    const title = node("span", "lesson-name",
      typeof lesson.title === "string" ? lesson.title : "Bez tytułu");
    info.appendChild(title);
    if (lesson.type === "quiz") info.appendChild(node("span", "lesson-type", "Quiz Rise"));
    else info.appendChild(node("span", "lesson-type", lesson.type || "Lekcja"));
    button.append(n, info);
    button.addEventListener("click", () => {
      state.lessonIndex = index;
      renderLessons();
      renderLessonEditor();
    });
    list.appendChild(button);
  });
}
function renderLessonEditor() {
  const container = ui.lessonEditor;
  container.replaceChildren();
  const lesson = state.doc.data.course.lessons[state.lessonIndex];
  if (!lesson) { writeHint(container, "Nie wybrano lekcji."); return; }
  const header = node("div", "content-header");
  header.appendChild(node("h3", "", "Lekcja " + (state.lessonIndex + 1)));
  header.appendChild(node("span", "tag", lesson.type || "blocks"));
  container.appendChild(header);

  labelControl(container, "Tytuł lekcji", lesson.title || "", false, value => {
    lesson.title = value;
    renderLessons();
  });
  if (typeof lesson.description === "string") {
    labelControl(container, "Opis lekcji", lesson.description, true, value => {
      lesson.description = value;
    });
  }
  const fields = listEditableFields(lesson);
  container.appendChild(node("h3", "fields-heading", "Treść bloków · " + fields.length));
  if (!fields.length) {
    writeHint(container, "Ta lekcja nie zawiera rozpoznanych pól tekstowych. "
      + "Możesz skorzystać z edytora JSON poniżej.");
    return;
  }
  writeHint(container, "W polach akapitów zachowaj istniejące znaczniki HTML "
    + "(np. <p>, <strong>). Podgląd celowo nie wykonuje kodu kursu.");
  const fieldContainer = node("div", "content-fields");
  for (const field of fields) {
    const multiline = field.key === "paragraph" || field.key === "description" ||
      String(field.target[field.key]).length > 160;
    labelControl(fieldContainer, field.label, field.target[field.key],
      multiline, value => { field.target[field.key] = value; });
  }
  container.appendChild(fieldContainer);
}
function renderAll() {
  if (!state.doc) return;
  ui.workspace.hidden = false;
  ui.courseTitle.value = courseTitle();
  renderStats();
  renderLessons();
  renderLessonEditor();
  if (ui.advanced.open) refreshJSON();
}
function refreshJSON() {
  if (!state.doc) return;
  ui.json.value = JSON.stringify(state.doc.data, null, 2);
}
async function presentFile(file, origin) {
  const doc = await openRiseZip(file, window.JSZip);
  state.doc = doc;
  state.dirty = false;
  state.lessonIndex = 0;
  ui.filename.value = finalFilename(file.name);
  ui.fileLine.hidden = false;
  ui.fileLine.textContent = origin + " · " + file.name + " · " +
    (file.size / 1024 / 1024).toFixed(2) + " MB · " +
    doc.entryCount + " wpisów · SCORM 1.2";
  renderAll();
  message("Pakiet wczytany. Możesz edytować lekcje lub usunąć test.", "success");
}
async function load(file) {
  if (!file || state.busy || !canReplace()) return;
  if (!/\.zip$/i.test(file.name)) {
    message("Wybierz oryginalny plik .zip z Articulate Rise.", "error");
    return;
  }
  if (file.size > MAX_ZIP_SIZE) {
    message("Plik jest większy niż dopuszczalne 120 MB.", "error");
    return;
  }
  busy(true);
  message("Odczytuję ZIP, manifest i dane kursu. Plik pozostaje na Twoim urządzeniu.");
  try {
    await presentFile(file, "Plik lokalny");
  } catch (error) {
    message("Nie udało się wczytać pakietu: " + error.message, "error");
  } finally {
    busy(false);
    if (state.doc) renderStats();
    ui.input.value = "";
  }
}
function selectedCourse() {
  return state.catalog.find(item => String(item.number) === ui.repoSelect.value);
}
function updateRepoMeta() {
  const item = selectedCourse();
  ui.repoMeta.hidden = !item;
  ui.repoMeta.textContent = item ? item.lessons + " lekcji · " +
    (item.bytes / 1024 / 1024).toFixed(2) + " MB · bez quizu i " +
    item.knowledge_checks_removed + " usuniętych bloków sprawdzania wiedzy · źródło: raw/" +
    item.filename : "";
}
async function loadCatalog() {
  try {
    const response = await fetch(new URL("./catalog.json", import.meta.url),
      { cache: "no-store", credentials: "omit" });
    if (!response.ok) throw new Error("HTTP " + response.status);
    const catalog = await response.json();
    if (catalog.version !== 2 || !Array.isArray(catalog.items) || !catalog.items.length)
      throw new ScormError("Nieprawidłowy katalog pakietów.");
    const seen = new Set();
    for (const item of catalog.items) {
      if (!Number.isInteger(item.number) || seen.has(item.number) ||
          typeof item.title !== "string" || !item.title ||
          typeof item.filename !== "string" || !item.filename.toLowerCase().endsWith(".zip") ||
          typeof item.url !== "string" || !item.url.startsWith("./packages/") ||
          !Number.isInteger(item.bytes) || item.bytes <= 0 || item.bytes > MAX_ZIP_SIZE ||
          !/^[a-f0-9]{64}$/.test(item.sha256) ||
          !Number.isInteger(item.lessons) || item.lessons <= 0 ||
          item.prepared !== true ||
          !Number.isInteger(item.knowledge_checks_removed) || item.knowledge_checks_removed < 0 ||
          !Number.isInteger(item.assessment_sections_removed) || item.assessment_sections_removed < 0)
        throw new ScormError("Nieprawidłowy wpis w katalogu SCORM.");
      const base = new URL("./packages/", import.meta.url);
      const url = new URL(item.url, import.meta.url);
      if (base.origin !== url.origin || !url.pathname.startsWith(base.pathname) ||
          url.search || url.hash || url.pathname.includes("../"))
        throw new ScormError("Niedozwolona ścieżka paczki w katalogu.");
      seen.add(item.number);
    }
    state.catalog = catalog.items.sort((a, b) => a.number - b.number);
    ui.repoSelect.replaceChildren();
    for (const item of state.catalog) {
      const option = node("option", "", String(item.number).padStart(2, "0") +
        ". " + item.title);
      option.value = String(item.number);
      ui.repoSelect.appendChild(option);
    }
    ui.repoSelect.disabled = false;
    ui.openRepo.disabled = false;
    ui.catalogStatus.textContent = "Gotowe wersje bez quizów i sprawdzania wiedzy: " +
      state.catalog.length + ". Wybierz kurs i kliknij „Otwórz do edycji”.";
    updateRepoMeta();
  } catch (error) {
    state.catalog = [];
    ui.catalogStatus.textContent = "Nie udało się załadować biblioteki (" +
      error.message + "). Możesz nadal otworzyć własny plik ZIP.";
    ui.localUpload.open = true;
  }
}
async function openRepositoryCourse() {
  const item = selectedCourse();
  if (!item || state.busy || !canReplace()) return;
  busy(true);
  message("Pobieram paczkę nr " + item.number +
    " z repozytorium i weryfikuję sumę SHA-256…");
  try {
    const sourceUrl = new URL(item.url, import.meta.url);
    const response = await fetch(sourceUrl, { cache: "no-store", credentials: "omit" });
    if (!response.ok) throw new ScormError("Nie udało się pobrać ZIP: HTTP " + response.status);
    const headerSize = Number(response.headers.get("content-length"));
    if (headerSize > MAX_ZIP_SIZE) throw new ScormError("Zbyt duży ZIP.");
    const buffer = await response.arrayBuffer();
    if (buffer.byteLength !== item.bytes) {
      throw new ScormError("Rozmiar ZIP różni się od katalogu.");
    }
    const digest = await crypto.subtle.digest("SHA-256", buffer);
    const sha = Array.from(new Uint8Array(digest), byte =>
      byte.toString(16).padStart(2, "0")).join("");
    if (sha !== item.sha256) {
      throw new ScormError("Suma SHA-256 nie zgadza się z katalogiem. Nie otwarto kursu.");
    }
    const file = new File([buffer], item.filename, { type: "application/zip" });
    await presentFile(file, "Repozytorium AIiSD");
  } catch (error) {
    message("Nie udało się otworzyć kursu z repozytorium: " + error.message, "error");
  } finally {
    busy(false);
    if (state.doc) renderStats();
  }
}

ui.repoSelect.addEventListener("change", updateRepoMeta);
ui.openRepo.addEventListener("click", openRepositoryCourse);
void loadCatalog();

ui.choose.addEventListener("click", event => {
  event.stopPropagation();
  ui.input.click();
});
ui.dropzone.addEventListener("click", event => {
  if (event.target !== ui.choose && !state.busy) ui.input.click();
});
ui.dropzone.addEventListener("keydown", event => {
  if ((event.key === "Enter" || event.key === " ") &&
      event.target === ui.dropzone) {
    event.preventDefault();
    ui.input.click();
  }
});
ui.input.addEventListener("change", event => load(event.target.files?.[0]));
for (const name of ["dragenter", "dragover"]) {
  ui.dropzone.addEventListener(name, event => {
    event.preventDefault();
    ui.dropzone.classList.add("dragging");
  });
}
for (const name of ["dragleave", "drop"]) {
  ui.dropzone.addEventListener(name, event => {
    event.preventDefault();
    ui.dropzone.classList.remove("dragging");
  });
}
ui.dropzone.addEventListener("drop", event => {
  const f = event.dataTransfer?.files?.[0];
  if (f) load(f);
});
ui.courseTitle.addEventListener("input", event => {
  const doc = state.doc;
  if (!doc) return;
  markDirty();
  doc.data.course.exportSettings.title = event.target.value;
  if (typeof doc.data.course.title === "string") doc.data.course.title = event.target.value;
});
ui.remove.addEventListener("click", () => {
  if (!state.doc || state.busy) return;
  try {
    const operation = makeUngraded(state.doc);
    markDirty();
    state.lessonIndex = Math.min(state.lessonIndex,
      state.doc.data.course.lessons.length - 1);
    renderAll();
    message(operation + ". Zapisz nowy ZIP, aby utrwalić zmiany.", "success");
  } catch (error) {
    message("Nie można bezpiecznie usunąć testu: " + error.message, "error");
  }
});
ui.reset.addEventListener("click", () => {
  if (!state.doc || state.busy) return;
  state.doc.data = copyJSON(state.doc.originalData);
  state.doc.transform = null;
  state.doc.removedId = null;
  state.lessonIndex = 0;
  state.doc.changes = [];
  state.dirty = false;
  renderAll();
  message("Przywrócono dane z oryginalnego ZIP. Oryginalny plik nie był modyfikowany.");
});
ui.advanced.addEventListener("toggle", () => {
  if (ui.advanced.open && state.doc) refreshJSON();
});
ui.refreshJson.addEventListener("click", () => {
  refreshJSON();
  message("Widok JSON zsynchronizowany z bieżącą edycją.");
});
ui.applyJson.addEventListener("click", () => {
  if (!state.doc || state.busy) return;
  try {
    const data = JSON.parse(ui.json.value);
    validateCourse(data);
    if (state.doc.transform && data.course.lessons.some(l => l.type === "quiz")) {
      throw new ScormError("W trybie bez ocen nie można przywrócić quizu w JSON.");
    }
    state.doc.data = data;
    markDirty();
    state.lessonIndex = Math.min(state.lessonIndex, data.course.lessons.length - 1);
    renderAll();
    message("Zastosowano zmiany JSON. Przed publikacją zweryfikuj treść w Moodle.", "success");
  } catch (error) {
    message("Błąd danych JSON: " + error.message, "error");
  }
});
ui.download.addEventListener("click", async () => {
  if (!state.doc || state.busy) return;
  const filename = ui.filename.value.trim();
  if (!filename || !filename.toLowerCase().endsWith(".zip") ||
      /[\/\\<>:"|?*\x00-\x1F]/.test(filename)) {
    message("Podaj poprawną nazwę pliku kończącą się na .zip.", "error");
    return;
  }
  busy(true);
  message("Sprawdzam integralność i zapisuję nowy ZIP. Może to potrwać przy dużej paczce.");
  try {
    const output = await buildRiseZip(state.doc, window.JSZip);
    const url = URL.createObjectURL(output);
    const a = node("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    message("Zapisano " + filename + " (" + (output.size / 1024 / 1024).toFixed(2) +
      " MB). Kontrola integralności zakończona. Wymagany test integracyjny w Moodle.", "success");
  } catch (error) {
    message("Eksport nie powiódł się: " + error.message, "error");
  } finally {
    busy(false);
    if (state.doc) renderStats();
  }
});
