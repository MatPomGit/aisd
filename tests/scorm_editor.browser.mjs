/* Chromium end-to-end: choose a repository ZIP, edit, save, verify and preserve manual upload. */
import assert from "node:assert/strict";
import { readFileSync, readdirSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { chromium } from "playwright-core";
import { createRequire } from "node:module";
import { TRACKING, openRiseZip } from "../docs/editor/core.mjs";

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

  // Main/default flow uses the indexed ZIP already present in the repository.
  await page.waitForFunction(() => document.querySelector("#repoCourseSelect").options.length === 20,
                             { timeout: 30000 });
  assert.equal(await page.locator("#localUpload").evaluate(el => el.open), false);
  assert.equal(await page.locator("#repoCourseSelect").isEnabled(), true);
  await page.locator("#repoCourseSelect").selectOption("13");
  assert.match(await page.locator("#repoCourseMeta").innerText(), /raw\/13-/);
  await page.locator("#openRepoCourse").click();
  await page.locator("#workspace").waitFor({ state: "visible", timeout: 30000 });
  assert.equal(await page.locator("#quizState").innerText(), "Obecny");

  await page.locator("#courseTitle").fill("Algorytmy i struktury danych — zmiana z katalogu");
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
               "Algorytmy i struktury danych — zmiana z katalogu");
  assert.equal(doc.data.course.lessons.some(lesson => lesson.type === "quiz"), false);
  assert.deepEqual(doc.tracking, TRACKING);

  // The original upload path must remain functional and not require the repository catalog.
  await page.reload();
  await page.locator("#localUpload summary").click();
  await page.locator("#fileInput").setInputFiles({
    name: source, mimeType: "application/zip", buffer: input
  });
  await page.locator("#workspace").waitFor({ state: "visible", timeout: 30000 });
  assert.equal(await page.locator("#quizState").innerText(), "Obecny");
  assert.match(await page.locator("#fileLine").innerText(), /Plik lokalny/);

  // Invalid hosted content cannot be accepted even if the filename matches the catalog.
  const other = await browser.newPage();
  other.on("pageerror", error => failures.push(error.message));
  await other.route("**/editor/packages/*.zip", route => route.fulfill({
    status: 200, contentType: "application/zip", body: "corrupted-zip"
  }));
  await other.goto("http://127.0.0.1:8787/editor/", { waitUntil: "domcontentloaded" });
  await other.waitForFunction(() => document.querySelector("#repoCourseSelect").options.length === 20);
  await other.locator("#repoCourseSelect").selectOption("13");
  await other.locator("#openRepoCourse").click();
  await other.waitForFunction(() => document.querySelector("#message").textContent.includes("Rozmiar ZIP różni się"));
  assert.equal(await other.locator("#workspace").isVisible(), false);
  await other.close();

  assert.deepEqual(failures, []);
  console.log("Browser smoke PASS: catalog 20, repo ZIP edit/download, manual upload, corrupted hosted ZIP rejected");
} finally {
  await browser.close();
  rmSync(directory, { recursive: true, force: true });
}
