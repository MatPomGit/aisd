/* Browser-core integration tests against the real Articulate Rise 360 exports. */
import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { createRequire } from "node:module";
import {
  openRiseZip, makeUngraded, listEditableFields, buildRiseZip,
  readTracking, TRACKING, validateCourse, planFiles
} from "../docs/editor/core.mjs";

const require = createRequire(import.meta.url);
const JSZip = require("jszip");
const names = readdirSync("raw").filter(name => name.toLowerCase().endsWith(".zip"));

function source(number) {
  const name = names.find(name => new RegExp("^" + number + "-").test(name));
  assert.ok(name, "missing source for course " + number);
  return readFileSync("raw/" + name);
}
async function open(number) { return openRiseZip(source(number), JSZip); }

test("course 13: opens, removes final quiz and emits ungraded valid ZIP", async () => {
  const doc = await open(13);
  const beforeCount = doc.data.course.lessons.length;
  assert.equal(doc.data.course.lessons.at(-1).type, "quiz");
  assert.equal(makeUngraded(doc), "Usunięto quiz końcowy");
  assert.equal(doc.data.course.lessons.length, beforeCount - 1);
  const blob = await buildRiseZip(doc, JSZip);
  const out = await JSZip.loadAsync(await blob.arrayBuffer(), { checkCRC32: true });
  const html = await out.file("scormcontent/index.html").async("string");
  assert.deepEqual(readTracking(html), TRACKING);
  assert.equal(doc.data.course.exportSettings.completeWith, "course");
  assert.equal(doc.data.course.lessons.some(lesson => lesson.type === "quiz"), false);
});

test("course 04: removes only the block quiz, preserves educational advice", async () => {
  const doc = await open(4);
  const count = doc.data.course.lessons.length;
  assert.equal(makeUngraded(doc), "Usunięto test blokowy, zachowano wskazówki");
  assert.equal(doc.data.course.lessons.length, count);
  const finalLesson = doc.data.course.lessons.at(-1);
  assert.equal(finalLesson.title, "Najczęstsze błędy i wskazówki");
  assert.deepEqual(finalLesson.items.map(item => item.type),
                   ["text", "interactive", "text"]);
  assert.ok((await buildRiseZip(doc, JSZip)).size > 1000);
});

test("course 05: no formal quiz; preserve all lessons and normalize tracking", async () => {
  const doc = await open(5);
  const original = JSON.stringify(doc.data.course.lessons);
  assert.equal(makeUngraded(doc), "Ujednolicono śledzenie ukończenia");
  assert.equal(JSON.stringify(doc.data.course.lessons), original);
  assert.ok((await buildRiseZip(doc, JSZip)).size > 1000);
});

test("course 13: text edits survive ZIP round trip", async () => {
  const doc = await open(13);
  makeUngraded(doc);
  const lesson = doc.data.course.lessons[0];
  const fields = listEditableFields(lesson);
  assert.ok(fields.length > 0, "expect editable content");
  lesson.title = "Poprawiony tytuł lekcji";
  fields[0].target[fields[0].key] = "Poprawiona treść";
  const zip = await JSZip.loadAsync(await (await buildRiseZip(doc, JSZip)).arrayBuffer());
  const reread = await openRiseZip(
    await zip.generateAsync({ type: "nodebuffer" }), JSZip);
  assert.equal(reread.data.course.lessons[0].title, "Poprawiony tytuł lekcji");
  const actual = listEditableFields(reread.data.course.lessons[0]);
  assert.equal(actual[0].target[actual[0].key], "Poprawiona treść");
});

test("unknown malformed lesson is rejected", () => {
  assert.throws(() => validateCourse({ course: { lessons: [{ type: "blocks" }],
                                                  exportSettings: {} } }), /identyfikator/);
});

test("structural changes in JSON are blocked before ZIP generation", async () => {
  const doc = await open(13);
  doc.data.course.lessons[0].id = "renamed-id";
  assert.throws(() => planFiles(doc), /identyfikatorów/);
});

test("all 20 real Rise ZIPs can be edited and rebuilt with valid completion", async () => {
  for (let n = 1; n <= 20; n++) {
    const doc = await open(n);
    assert.ok(doc.entryCount > 1);
    assert.equal(doc.data.course.exportSettings.target, "scorm12");
    makeUngraded(doc);
    const output = await buildRiseZip(doc, JSZip);
    assert.ok(output.size > 1000, "empty artifact for course " + n);
  }
});
