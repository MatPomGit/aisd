/* Simulated LMS contract test: real Rise runtime, NOT Moodle or SCORM certification. */
import assert from "node:assert/strict";
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { createRequire } from "node:module";
import { chromium } from "playwright-core";
import { openRiseZip } from "../docs/editor/core.mjs";

const require = createRequire(import.meta.url);
const JSZip = require("jszip");
const zipName = readdirSync("build/scorm-preview")
  .find(filename => filename.startsWith("1-") && filename.endsWith(".zip"));
assert.ok(zipName, "Candidate SCORM 01 ZIP must exist");
const course = await openRiseZip(
  readFileSync(join("build/scorm-preview", zipName)), JSZip);
const lessonId = course.data.course.lessons[0]?.id;
assert.ok(lessonId, "Candidate SCORM 01 first lesson ID missing");

const outputDir = "build/scorm-lms-simulation";
mkdirSync(outputDir, { recursive: true });
const report = {
  scope: "Rise JavaScript runtime + local in-memory LMS callbacks",
  warning: "This is not a Moodle SCORM 1.2 conformance or LMS integration test.",
  lessonId,
  steps: [],
};

const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
});
const page = await context.newPage();
const frameReady = async () => {
  await page.waitForFunction(() =>
    typeof document.querySelector("#content-frame")?.contentWindow
      ?.Runtime?.getProgress === "function", undefined, { timeout: 30000 });
};

try {
  await page.goto("http://127.0.0.1:8787/learner-harness.html",
                  { waitUntil: "domcontentloaded" });
  await frameReady();
  const initial = await page.evaluate(() => ({
    status: window.__scormAudit.status,
    suspend: window.__scormAudit.suspend,
    runtime: window.frames[0]?.Runtime?.getProgress(),
  }));
  assert.equal(initial.status, "incomplete");
  assert.equal(initial.suspend, "");
  report.steps.push("New attempt begins with incomplete status and no suspend data");

  const probe = await page.evaluate(id => {
    const player = window.frames[0];
    player.Runtime.setCourseProgress({
      __ci_resume_probe: { lesson_id: id, value: "saved-by-Rise-runtime" },
    });
    player.Runtime.bookmark(id);
    return player.Runtime.getProgress();
  }, lessonId);
  assert.deepEqual(probe.__ci_resume_probe,
                   { lesson_id: lessonId, value: "saved-by-Rise-runtime" });

  // The real vendor runtime writes progress after a 100 ms debounce.
  await page.waitForFunction(() =>
    window.__scormAudit.suspend.length > 20 &&
    window.__scormAudit.bookmark.includes("#/lessons/"),
    undefined, { timeout: 15000 });
  const beforeReload = await page.evaluate(() => ({
    suspend: window.__scormAudit.suspend,
    bookmark: window.__scormAudit.bookmark,
    status: window.__scormAudit.status,
    calls: window.__scormAudit.calls,
  }));
  assert.equal(beforeReload.status, "incomplete");
  assert.ok(beforeReload.suspend.length <= 4096,
            "Sample progress exceeds SCORM 1.2 suspend_data size");
  assert.equal(beforeReload.calls.filter(([name]) => name === "SetScore").length, 0);
  report.steps.push({
    check: "Runtime persists a progress probe through SetDataChunk and bookmark",
    suspend_chars: beforeReload.suspend.length,
    bookmark: beforeReload.bookmark,
  });

  await page.reload({ waitUntil: "domcontentloaded" });
  await frameReady();
  const restored = await page.evaluate(() => ({
    status: window.__scormAudit.status,
    suspend: window.__scormAudit.suspend,
    bookmark: window.__scormAudit.bookmark,
    progress: window.frames[0].Runtime.getProgress(),
  }));
  assert.equal(restored.status, "incomplete");
  assert.equal(restored.suspend, beforeReload.suspend);
  assert.equal(restored.bookmark, beforeReload.bookmark);
  assert.deepEqual(restored.progress.__ci_resume_probe,
                   { lesson_id: lessonId, value: "saved-by-Rise-runtime" });
  report.steps.push("Restarting the test page restores the progress probe");

  const beforeComplete = await page.evaluate(() => {
    window.frames[0].Runtime.finish(99);
    return { status: window.__scormAudit.status,
             calls: window.__scormAudit.calls.map(item => item[0]) };
  });
  assert.equal(beforeComplete.status, "incomplete");
  assert.equal(beforeComplete.calls.includes("SetReachedEnd"), false);
  assert.equal(beforeComplete.calls.includes("SetScore"), false);
  report.steps.push("Runtime.finish(99) does not signal course completion");

  const completed = await page.evaluate(() => {
    window.frames[0].Runtime.finish(100);
    return { status: window.__scormAudit.status,
             calls: window.__scormAudit.calls.map(item => item[0]) };
  });
  assert.equal(completed.status, "completed");
  assert.equal(completed.calls.includes("SetReachedEnd"), true);
  assert.equal(completed.calls.includes("SetScore"), false);
  assert.equal(completed.calls.includes("SetPassed"), false);
  report.steps.push("Runtime.finish(100) signals completed without grades or passed");

  await page.reload({ waitUntil: "domcontentloaded" });
  await frameReady();
  const final = await page.evaluate(() => ({
    status: window.__scormAudit.status,
    progress: window.frames[0].Runtime.getProgress(),
  }));
  assert.equal(final.status, "completed");
  assert.deepEqual(final.progress.__ci_resume_probe,
                   { lesson_id: lessonId, value: "saved-by-Rise-runtime" });
  report.steps.push("Mock completion and progress survive a second reload");
  console.log("Isolated Rise LMS simulation PASS: suspend/resume and 99/100 threshold, no score");
} finally {
  writeFileSync(join(outputDir, "report.json"),
                JSON.stringify(report, null, 2) + "\n");
  await context.close();
  await browser.close();
}
