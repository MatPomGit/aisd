/* SCORM Studio core: pure data transformation, no network access.
 * Supported: Rise 360 SCORM 1.2, embedded Base64/JSON wrappers only.
 */
export const HTML_PATH = "scormcontent/index.html";
export const MODERN_PATH = "scormcontent/runtime-data.js";
export const TRACKING = Object.freeze({
  quizId: null,
  storylineId: null,
  completionPercentage: 100,
  reporting: "completed-incomplete"
});
export const MAX_ZIP_SIZE = 120 * 1024 * 1024;
const MAX_UNCOMPRESSED = 500 * 1024 * 1024;
const MAX_FILES = 5000;
const FIELDS = Object.keys(TRACKING);

export class ScormError extends Error {
  constructor(message) { super(message); this.name = "ScormError"; }
}
function ensure(value, message) {
  if (!value) throw new ScormError(message);
}
export function copyJSON(value) {
  return JSON.parse(JSON.stringify(value));
}
function decodeBlob(blob) {
  let binary;
  try { binary = atob(blob); }
  catch { throw new ScormError("Nieprawidłowe kodowanie Base64 danych Rise."); }
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
  try { return JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(bytes)); }
  catch { throw new ScormError("Danych kursu nie można odczytać jako JSON/UTF-8."); }
}
function encodeBlob(data) {
  const bytes = new TextEncoder().encode(JSON.stringify(data));
  const chunks = [];
  for (let i = 0; i < bytes.length; i += 32768) {
    let piece = "";
    for (const b of bytes.subarray(i, i + 32768)) piece += String.fromCharCode(b);
    chunks.push(piece);
  }
  return btoa(chunks.join(""));
}
const WRAPPERS = [
  {
    path: MODERN_PATH,
    expression: /(__jsonp\s*\(\s*["']runtime-data\.js["']\s*,\s*["'])([A-Za-z0-9+/=]+)(["']\s*\))/g
  },
  {
    path: HTML_PATH,
    expression: /(\basync\s+function\s+__fetchCourse\s*\(\s*\)\s*\{\s*return\s+Promise\.resolve\s*\(\s*deserialize\s*\(\s*")([A-Za-z0-9+/=]+)("\s*\)\s*\))/g
  }
];
function wrapperFor(zip) {
  return WRAPPERS.find(w => !!zip.file(w.path));
}
function getPayload(text, wrapper) {
  const matches = Array.from(text.matchAll(wrapper.expression));
  ensure(matches.length === 1, "Nieznany format danych Rise: " + wrapper.path);
  const match = matches[0];
  const data = decodeBlob(match[2]);
  validateCourse(data);
  return { data, before: text.slice(0, match.index + match[1].length),
           after: text.slice(match.index + match[1].length + match[2].length) };
}
export function validateCourse(data) {
  ensure(data && typeof data === "object" && data.course &&
         typeof data.course === "object" && Array.isArray(data.course.lessons) &&
         data.course.lessons.length > 0, "Brak poprawnej tablicy course.lessons.");
  ensure(data.course.exportSettings && typeof data.course.exportSettings === "object",
         "Brak course.exportSettings.");
  const ids = new Set();
  for (const lesson of data.course.lessons) {
    ensure(lesson && typeof lesson === "object" &&
           typeof lesson.id === "string" && lesson.id.length > 0,
           "Lekcja ma nieprawidłowy identyfikator.");
    ensure(!ids.has(lesson.id), "Powtórzony identyfikator lekcji: " + lesson.id);
    ids.add(lesson.id);
  }
  return data;
}
function getValue(text, key) {
  const pattern = new RegExp("\\bvar\\s+" + key + "\\s*=\\s*([^;\\r\\n]+)\\s*;", "g");
  const matches = Array.from(text.matchAll(pattern));
  ensure(matches.length === 1, "Brak lub wiele zmiennych sterujących: " + key);
  const raw = matches[0][1].trim();
  try { return JSON.parse(raw.replace(/^'([^']*)'$/, '"$1"')); }
  catch { throw new ScormError("Nieobsługiwana wartość " + key + ": " + raw); }
}
export function readTracking(html) {
  const values = {};
  for (const key of FIELDS) values[key] = getValue(html, key);
  return values;
}
export function patchTracking(html, values = TRACKING) {
  let result = html;
  for (const [key, value] of Object.entries(values)) {
    getValue(result, key); // refuse ambiguous runtime
    const pattern = new RegExp("(\\bvar\\s+" + key + "\\s*=\\s*)([^;\\r\\n]+)(\\s*;)");
    result = result.replace(pattern, (_, before, _old, after) =>
      before + JSON.stringify(value) + after);
  }
  return result;
}
function manifestCheck(xml, names) {
  ensure(/<([a-z0-9_-]+:)?manifest\b/i.test(xml), "Brak elementu manifest XML.");
  const m = xml.match(/<(?:[a-z0-9_-]+:)?schemaversion\b[^>]*>\s*([^<]+)\s*<\/(?:[a-z0-9_-]+:)?schemaversion>/i);
  ensure(m && m[1].trim() === "1.2", "Obsługiwany jest wyłącznie SCORM 1.2.");
  ensure(!/\bxml:base\s*=/i.test(xml), "Manifest XML używa xml:base; wymaga analizy.");
  const links = Array.from(xml.matchAll(/<(?:[a-z0-9_-]+:)?(?:resource|file)\b[^>]*?\bhref\s*=\s*["']([^"']+)["']/gi));
  ensure(links.length > 0, "Manifest nie deklaruje zasobów.");
  let launch = false;
  for (const link of links) {
    let file;
    try { file = decodeURIComponent(link[1].split(/[?#]/)[0]); }
    catch { throw new ScormError("Błędna ścieżka href w manifeście."); }
    ensure(safeName(file), "Niedozwolona ścieżka w manifeście: " + file);
    ensure(names.has(file), "Brakuje pliku z manifestu: " + file);
    if (file === "scormdriver/indexAPI.html") launch = true;
  }
  ensure(launch, "Brak standardowego pliku startowego Rise.");
}
function safeName(name) {
  if (!name || name.startsWith("/") || name.includes("\\") || /^[a-z]+:/i.test(name)) return false;
  return !name.split("/").some(x => x === ".." || x === ".");
}
export async function inspectZip(zip) {
  const entries = Object.values(zip.files);
  ensure(entries.length <= MAX_FILES, "Zbyt dużo wpisów ZIP.");
  const names = new Set();
  let total = 0;
  for (const file of entries) {
    ensure(safeName(file.name.replace(/\/$/, "")), "Niebezpieczna ścieżka w ZIP: " + file.name);
    ensure(!names.has(file.name), "Powtórzona nazwa pliku ZIP: " + file.name);
    names.add(file.name);
    total += file._data?.uncompressedSize ?? 0;
  }
  ensure(total <= MAX_UNCOMPRESSED, "Zbyt duża rozpakowana zawartość ZIP.");
  ensure(!!zip.file("imsmanifest.xml"), "Brak imsmanifest.xml w katalogu głównym ZIP.");
  const manifest = await zip.file("imsmanifest.xml").async("string");
  manifestCheck(manifest, names);
  ensure(!!zip.file(HTML_PATH), "Brak scormcontent/index.html.");
  return { entries: entries.length };
}
export async function openRiseZip(file, JSZip) {
  const size = typeof file?.size === "number" ? file.size : file?.byteLength;
  ensure(typeof size === "number" && size <= MAX_ZIP_SIZE,
         "Plik ZIP przekracza limit 120 MB.");
  ensure(typeof JSZip?.loadAsync === "function", "Biblioteka JSZip nie została załadowana.");
  let zip;
  try { zip = await JSZip.loadAsync(file, { checkCRC32: true, createFolders: false }); }
  catch (error) { throw new ScormError("Nie można odczytać archiwum ZIP: " + error.message); }
  const structure = await inspectZip(zip);
  const wrapper = wrapperFor(zip);
  ensure(wrapper, "Nieobsługiwana wersja Rise: brak obsługiwanego wrappera danych.");
  const payload = await zip.file(wrapper.path).async("string");
  const decoded = getPayload(payload, wrapper);
  const html = wrapper.path === HTML_PATH ? payload : await zip.file(HTML_PATH).async("string");
  const tracking = readTracking(html);
  return {
    filename: file.name || "kurs.zip",
    file, zip, wrapper, payload, html, tracking,
    data: decoded.data, originalData: copyJSON(decoded.data),
    originalNames: Object.keys(zip.files),
    entryCount: structure.entries, transform: null, removedId: null,
    changes: []
  };
}
function knownEmbeddedTest(data) {
  const lessons = data.course.lessons;
  const last = lessons[lessons.length - 1];
  if (last?.id !== "cmiej97dl000d207092aujenc") return false;
  ensure(last.title === "Test końcowy i omówienie rozwiązań",
         "Zmienił się tytuł znanej lekcji testowej.");
  const types = ["text", "text", "list", "divider",
                 ...Array(7).fill("knowledgeCheck"),
                 "divider", "text", "interactive", "text", "interactive", "text"];
  ensure(Array.isArray(last.items) && last.items.length === 17 &&
         last.items.every((v, i) => v.type === types[i]) &&
         last.items[13].variant === "tabs" &&
         last.items[15].variant === "accordion",
         "Zmieniła się struktura testu blokowego kursu 04.");
  last.items = last.items.slice(14, 17);
  last.title = "Najczęstsze błędy i wskazówki";
  return true;
}
export function makeUngraded(doc) {
  const data = copyJSON(validateCourse(doc.data));
  const settings = data.course.exportSettings;
  const lessons = data.course.lessons;
  const quizzes = lessons.filter(l => l.type === "quiz");
  ensure(doc.tracking.storylineId == null, "Nieobsługiwane śledzenie Storyline.");
  let operation = "Ujednolicono śledzenie ukończenia";
  let deletedId = null;
  if (quizzes.length) {
    ensure(quizzes.length === 1 && lessons.at(-1) === quizzes[0] && lessons.length > 1,
           "Quiz nie jest pojedynczym, końcowym elementem.");
    deletedId = quizzes[0].id;
    ensure(settings.quizId === deletedId && doc.tracking.quizId === deletedId &&
           settings.completeWith === "quiz",
           "Identyfikatory quizu lub tryb śledzenia nie zgadzają się.");
    lessons.pop();
    operation = "Usunięto quiz końcowy";
  } else {
    ensure(settings.quizId == null && doc.tracking.quizId == null &&
           ["course", "reporting"].includes(settings.completeWith),
           "Brak quizu, ale kurs ma nieznane śledzenie quizowe.");
    if (knownEmbeddedTest(data)) operation = "Usunięto test blokowy, zachowano wskazówki";
  }
  settings.quizId = null;
  settings.completeWith = "course";
  settings.quizComplete = false;
  settings.completionPercentage = 100;
  settings.reporting = "completed-incomplete";
  if (deletedId) {
    ensure(!JSON.stringify(data).includes(deletedId),
           "Usunięty quiz nadal ma odwołania w danych kursu.");
  }
  doc.data = data;
  doc.transform = operation;
  doc.removedId = deletedId;
  doc.changes.push(operation);
  return operation;
}
export function listEditableFields(lesson) {
  const results = [];
  const include = ["heading", "paragraph", "title", "description"];
  const walk = (item, depth, label) => {
    if (!item || typeof item !== "object" || depth > 6) return;
    if (Array.isArray(item)) {
      item.forEach((value, i) => walk(value, depth + 1, label + " / " + (i + 1)));
      return;
    }
    for (const key of include) {
      if (typeof item[key] === "string") {
        results.push({ target: item, key, label: label + " · " + key });
      }
    }
    if (Array.isArray(item.items)) walk(item.items, depth + 1, label);
  };
  if (Array.isArray(lesson.items)) {
    lesson.items.forEach((block, i) => walk(block.items || [], 0,
      "Blok " + (i + 1) + " (" + (block.type || "?") + ")"));
  }
  return results;
}
function patchedText(payload, wrapper, data) {
  const current = getPayload(payload, wrapper);
  return current.before + encodeBlob(data) + current.after;
}
export function planFiles(doc) {
  validateCourse(doc.data);
  const json = JSON.stringify(doc.data);
  if (doc.removedId) ensure(!json.includes(doc.removedId),
                             "Pozostały odniesienia do usuniętego quizu.");
  const payload = patchedText(doc.payload, doc.wrapper, doc.data);
  let html = doc.wrapper.path === HTML_PATH ? payload : doc.html;
  if (doc.transform) {
    ensure(!doc.data.course.lessons.some(l => l.type === "quiz"),
           "Kurs nadal zawiera formalny quiz.");
    ensure(doc.data.course.exportSettings.quizId === null &&
           doc.data.course.exportSettings.completeWith === "course" &&
           doc.data.course.exportSettings.completionPercentage === 100 &&
           doc.data.course.exportSettings.reporting === "completed-incomplete",
           "Nieprawidłowe ustawienia ukończenia kursu.");
    html = patchTracking(html);
    ensure(JSON.stringify(readTracking(html)) === JSON.stringify(TRACKING),
           "Błąd konfiguracji śledzenia ukończenia.");
  }
  const files = new Map([[doc.wrapper.path, doc.wrapper.path === HTML_PATH ? html : payload]]);
  if (doc.wrapper.path !== HTML_PATH && doc.transform) files.set(HTML_PATH, html);
  return files;
}
export async function buildRiseZip(doc, JSZip) {
  const changes = planFiles(doc);
  const clone = await JSZip.loadAsync(doc.file, { checkCRC32: true, createFolders: false });
  for (const [path, text] of changes) {
    const original = clone.file(path);
    ensure(original, "Brak pliku do modyfikacji: " + path);
    clone.file(path, text, {
      date: original.date,
      compression: "DEFLATE",
      compressionOptions: { level: 6 },
      createFolders: false
    });
  }
  const output = await clone.generateAsync({
    type: "blob", compression: "DEFLATE",
    compressionOptions: { level: 6 }, streamFiles: true
  });
  const roundtrip = await JSZip.loadAsync(output, { checkCRC32: true, createFolders: false });
  await inspectZip(roundtrip);
  ensure(JSON.stringify(Object.keys(roundtrip.files)) === JSON.stringify(doc.originalNames),
         "Liczba lub kolejność plików archiwum zmieniła się.");
  const decoded = getPayload(await roundtrip.file(doc.wrapper.path).async("string"), doc.wrapper);
  ensure(JSON.stringify(decoded.data) === JSON.stringify(doc.data),
         "Niepoprawny odczyt zapisanych zmian w kursie.");
  if (doc.transform) {
    const html = await roundtrip.file(HTML_PATH).async("string");
    ensure(JSON.stringify(readTracking(html)) === JSON.stringify(TRACKING),
           "Zmodyfikowany ZIP nie zawiera wymaganego śledzenia ukończenia.");
  }
  // Verify unchanged resources by actual bytes, not only ZIP metadata.
  for (const [path, file] of Object.entries(doc.zip.files)) {
    if (file.dir || changes.has(path)) continue;
    const before = await file.async("uint8array");
    const after = await roundtrip.file(path)?.async("uint8array");
    ensure(after && before.length === after.length,
           "Brak lub zmiana zasobu: " + path);
    for (let i = 0; i < before.length; i++) {
      if (before[i] !== after[i]) throw new ScormError("Zmieniono zasób: " + path);
    }
  }
  return output;
}
export function finalFilename(name) {
  return String(name || "kurs.zip").replace(/\.zip$/i, "")
    .replace(/[<>:"/\\|?*\x00-\x1F]/g, "_") + "-edited-scorm12.zip";
}
