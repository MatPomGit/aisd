/* Real Rise learner renderer in an isolated in-memory LMS proxy, NOT Moodle. */
import assert from "node:assert/strict";
import { readFileSync, readdirSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { chromium } from "playwright-core";
import { createRequire } from "node:module";
import { openRiseZip } from "../docs/editor/core.mjs";

const require = createRequire(import.meta.url);
const JSZip = require("jszip");
const name = readdirSync("build/scorm-preview")
  .find(n => n.startsWith("1-") && n.endsWith(".zip"));
assert.ok(name, "Cannot find candidate SCORM 01 ZIP");
const raw = readFileSync(join("build/scorm-preview", name));
const source = await openRiseZip(raw, JSZip);
const lessons = source.data.course.lessons;
assert.equal(lessons.length, 11, "SCORM 01 must retain 11 lessons");

const uniqueText = [
  "Wyobraź sobie, że system przechowuje milion identyfikatorów",
  "Teraz spróbujmy je zepsuć",
  "Opis „przeglądaj tablicę i zwróć pierwsze trafienie”",
  "Kilka pozytywnych prób nie stanowi dowodu poprawności",
  "Czas działania wyszukiwania liniowego zależy",
  "Programista postanawia przyspieszyć wyszukiwanie identyfikatora",
  "Model obliczeniowy określa, jakie operacje są dostępne",
  "Model RAM rozbija tę operację na zmianę stanu",
  "pierwsze 0 oznacza koniec danych",
  "Program sumujący wartości do pierwszego zera",
  "Te obserwacje łączą się w pięć praktycznych zasad",
];
assert.equal(uniqueText.length, lessons.length);

// Representative user interactions, evaluated against the rendered Rise UI.
const interactionChecks = new Map([
  [1, { control: "Iteracyjny lub rekurencyjny",
        revealed: "powtarza kroki w pętli", kind: "accordion" }],
  [2, { control: "Python",
        revealed: "def pierwsze(A, x):", kind: "tabs" }],
  [7, { control: "2. LOAD 1",
        revealed: "kopiuje zawartość", kind: "process" }],
]);

const screenshotDir = "build/scorm-learner-screenshots";
mkdirSync(screenshotDir, { recursive: true });
const report = { kind: "isolated-rise-learner-qa", disclaimer:
  "Local static browser harness only; not Moodle SCORM compliance or suspend/resume",
  lessons: lessons.map(l => ({ id: l.id, title: l.title })),
  images: [], errors: [], metrics: [] };
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
try {
  for (const viewport of [
    { name: "desktop", width: 1440, height: 900 },
    { name: "mobile", width: 390, height: 844 },
  ]) {
    const page = await browser.newPage({ viewport, deviceScaleFactor: 1 });
    const errors = [];
    page.on("pageerror", error => errors.push(error.message));
    await page.goto("http://127.0.0.1:8787/learner-harness.html",
                    { waitUntil: "domcontentloaded", timeout: 30000 });
    const frameLocator = page.frameLocator("#content-frame");
    await frameLocator.locator("#app").waitFor({ state: "attached", timeout: 30000 });
    for (let i = 0; i < lessons.length; i++) {
      const lesson = lessons[i];
      const player = page.frames().find(f =>
        f.url().includes("/learner-preview/scormcontent/index.html"));
      assert.ok(player, "Rise player iframe missing");
      await player.evaluate(id => { window.location.hash = "#/lessons/" + id; },
                            lesson.id);
      try {
        await page.waitForFunction(text => {
          const root = document.querySelector("#content-frame")
            ?.contentDocument?.querySelector("#app");
          return !!root && (root.innerText || "").includes(text);
        }, uniqueText[i], { timeout: 30000, polling: 250 });
      } catch (err) {
        const diagnostic = await page.evaluate(() => {
          const frame = document.querySelector("#content-frame");
          return {
            hash: frame?.contentWindow?.location.hash,
            app: frame?.contentDocument?.querySelector("#app")?.innerText?.slice(0, 1600),
            page: frame?.contentDocument?.body?.innerText?.slice(0, 1600)
          };
        });
        report.errors.push({ viewport: viewport.name, index: i + 1,
                             lesson: lesson.title, diagnostic, pageerrors: errors });
        throw new Error("Rise lesson did not render expected content: " +
                        (i + 1) + " " + JSON.stringify(diagnostic), { cause: err });
      }
      // DOM presence alone is insufficient: the early screenshots showed
      // the course cover or an empty viewport. Scroll the *actual Rise player*
      // to a rendered lesson paragraph, then verify onscreen intersection.
      const meaningfulParagraph = frameLocator.locator("p")
        .filter({ hasText: uniqueText[i] }).first();
      await meaningfulParagraph.scrollIntoViewIfNeeded({ timeout: 20000 });
      const paraRect = await meaningfulParagraph.boundingBox();
      assert.ok(paraRect, "Rendered Rise paragraph is not visible");
      const visibleHeight = Math.min(paraRect.y + paraRect.height, viewport.height) -
                            Math.max(paraRect.y, 0);
      assert.ok(visibleHeight > 35,
        "Lesson content is not onscreen after scrolling: " +
        viewport.name + " " + (i + 1) + ": " + JSON.stringify(paraRect));
      await page.waitForTimeout(150);
      const metrics = await page.evaluate(() => {
        const doc = document.querySelector("#content-frame").contentDocument;
        const app = doc.querySelector("#app");
        return {
          visibleChars: app?.innerText?.length ?? 0,
          scrollWidth: doc.documentElement.scrollWidth,
          clientWidth: doc.documentElement.clientWidth,
          horizontalOverflowPx: Math.max(0, doc.documentElement.scrollWidth -
                                            doc.documentElement.clientWidth),
        };
      });
      assert.ok(metrics.visibleChars > 80, "Empty Rise lesson " + (i + 1));
      const shot = join(screenshotDir,
        "scorm01-rise-" + viewport.name + "-" + String(i + 1).padStart(2, "0") + ".png");
      await page.screenshot({ path: shot, fullPage: true });
      report.images.push(shot);
      report.metrics.push({ viewport: viewport.name, lesson: i + 1,
                            visibleParagraphPx: Math.round(visibleHeight), ...metrics });
      const scenario = interactionChecks.get(i);
      if (scenario) {
        if (scenario.kind === "process") {
          // Rise process blocks use Previous/Next carousel controls; the
          // inactive step title is not itself a clickable target.
          const candidates = await player.evaluate(() =>
            [...document.querySelectorAll("button")].filter(el => {
              const r = el.getBoundingClientRect();
              return r.width > 0 && r.height > 0 && r.bottom > 0 &&
                     r.top < window.innerHeight;
            }).slice(-25).map(el => ({
              label: el.getAttribute("aria-label"),
              text: (el.innerText || "").slice(0, 50),
              classes: el.className,
            }))
          );
          console.log("Rise process visible buttons:", JSON.stringify(candidates));
          await frameLocator.getByRole("button", {
            name: /next|dalej|następny/i
          }).last().click({ timeout: 12000 });
        } else {
          const button = frameLocator.getByText(scenario.control,
                                                { exact: true }).first();
          await button.click({ timeout: 20000 });
        }
        const revealed = frameLocator.getByText(scenario.revealed,
                                                { exact: false }).first();
        await revealed.waitFor({ state: "visible", timeout: 15000 });
        await revealed.scrollIntoViewIfNeeded({ timeout: 10000 });
        const controlShot = join(screenshotDir,
          "scorm01-rise-" + viewport.name + "-" +
          String(i + 1).padStart(2, "0") + "-" + scenario.kind + ".png");
        await page.screenshot({ path: controlShot, fullPage: true });
        report.images.push(controlShot);
        if (!report.interactions) report.interactions = [];
        report.interactions.push({ viewport: viewport.name, lesson: i + 1,
                                   kind: scenario.kind, result: "visible" });
      }
    }
    report.errors.push(...errors.map(message => ({ viewport: viewport.name, message })));
    const events = await page.evaluate(() => window.__scormAudit?.calls || []);
    assert.equal(events.filter(e => e[0] === "SetScore").length, 0,
                 "Ungraded learner must never send SetScore");
    await page.close();
  }
  assert.deepEqual(report.errors, [], "Unexpected error in rendered Rise player");
  console.log("Rise learner browser QA PASS: 11 lessons x 2 viewports, plus accordion/tabs/process interactions, zero SetScore");
} finally {
  writeFileSync(join(screenshotDir, "report.json"),
                JSON.stringify(report, null, 2) + "\n");
  await browser.close();
}
