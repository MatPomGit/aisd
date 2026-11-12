/* End-to-end smoke test: actual Chromium UI, ZIP upload, edit, save, verify. */
import assert from "node:assert/strict";
import { readFileSync, readdirSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright-core";
import { createRequire } from "node:module";
import { readTracking, TRACKING, openRiseZip } from "../docs/editor/core.mjs";

const require = createRequire(import.meta.url);
const JSZip = require("jszip");
const source = readdirSync("raw").find(name => name.startsWith("13-") && name.endsWith(".zip"));
assert.ok(source, "Real course 13 ZIP missing");
const input = readFileSync("raw/" + source);
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"]
});
const directory = mkdtempSync(join(tmpdir(), "scorm-pages-"));
const failures = [];
try {
  const page = await browser.newPage({ acceptDownloads: true });
  page.on("pageerror", error => failures.push(error.message));
  await page.goto("http://127.0.0.1:8787/editor/", { waitUntil: "domcontentloaded" });
  await page.locator("#fileInput").setInputFiles({
    name: source, mimeType: "application/zip", buffer: input
  });
  await page.locator("#workspace").waitFor({ state: "visible", timeout: 20000 });
  assert.equal(await page.locator("#quizState").innerText(), "Obecny");
  await page.locator("#courseTitle").fill("Algorytmy i struktury danych — poprawiona nazwa");
  await page.locator("#removeQuiz").click();
  assert.equal(await page.locator("#quizState").innerText(), "Wyłączony");
  const [download] = await Promise.all([
    page.waitForEvent("download", { timeout: 60000 }),
    page.locator("#downloadButton").click()
  ]);
  const output = join(directory, download.suggestedFilename());
  await download.saveAs(output);
  const data = readFileSync(output);
  assert.ok(data.length > 100000);
  const doc = await openRiseZip(data, JSZip);
  assert.equal(doc.data.course.exportSettings.title,
               "Algorytmy i struktury danych — poprawiona nazwa");
  assert.ok(!doc.data.course.lessons.some(lesson => lesson.type === "quiz"));
  assert.deepEqual(doc.tracking, TRACKING);
  assert.deepEqual(failures, []);
  console.log("Browser smoke PASS: upload, edit, ungrade, save, SCORM ZIP round-trip");
} finally {
  await browser.close();
  rmSync(directory, { recursive: true, force: true });
}
