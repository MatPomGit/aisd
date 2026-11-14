/* Launch real Rustici SCORM driver from a parent SCORM 1.2 API fixture.
   Separate from player-only tests. This is NOT a Moodle integration test. */
import assert from "node:assert/strict";
import { chromium } from "playwright-core";
import { mkdirSync, writeFileSync } from "node:fs";

const output = "build/scorm12-driver-qa";
mkdirSync(output, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: process.env.CHROME_BIN || "/usr/bin/google-chrome",
  args: ["--no-sandbox", "--disable-dev-shm-usage"],
});
const report = {kind:"real-scorm12-driver-in-api-fixture", limitations:
  "In-memory SCORM 1.2 API, not a Moodle installation or SCORM certification",
  scenarios:[]};
let failures = 0;
try {
  for (const variant of ["original", "candidate", "candidate-stale"]) {
    const page = await browser.newPage({viewport:{width:1280,height:900}});
    const diagnostic = {variant, errors:[], badResponses:[], requestsFailed:[],
                        init:[], rendered:false};
    page.on("pageerror", err => diagnostic.errors.push(err.message));
    page.on("console", msg => {
      if (msg.type() === "error") diagnostic.errors.push("console: " + msg.text());
    });
    page.on("requestfailed", request => diagnostic.requestsFailed.push({
      url:request.url(), failure:request.failure()?.errorText
    }));
    page.on("response", response => {
      if (response.status() >= 400) diagnostic.badResponses.push({
        url:response.url(), status:response.status()
      });
    });
    try {
      const source = variant.startsWith("candidate") ? "candidate" : "original";
      const bookmarkQuery = variant === "candidate-stale" ? "&bookmark=stale" : "";
      await page.goto("http://127.0.0.1:8787/scorm12-driver-harness.html?source=" +
                      source + bookmarkQuery,
                      {waitUntil:"domcontentloaded", timeout:30000});
      await page.waitForFunction(() => {
        const audit = window.__scorm12;
        return audit && audit.calls.some(call => call[0] === "LMSInitialize");
      }, null, {timeout:30000});
      diagnostic.init = await page.evaluate(() => window.__scorm12.calls.slice(0,35));
      await page.waitForFunction(() => {
        const paths = Array.from(document.querySelectorAll("iframe"));
        const outer = paths.find(frame => frame.id === "sco");
        const child = outer?.contentWindow?.document
          ?.querySelector('iframe[name="scormdriver_content"]');
        const displayed = child?.contentWindow?.document?.querySelector("#app")?.innerText || "";
        return displayed.length > 100 && displayed.includes("Podstawy algorytmów");
      }, null, {timeout:30000});
      diagnostic.rendered = true;
      if (variant === "candidate-stale") {
        const resume = await page.evaluate(() => ({
          url: document.getElementById("sco").contentWindow
            .document.querySelector('iframe[name="scormdriver_content"]')
            .contentWindow.location.href,
          stored: window.__scorm12.store["cmi.core.lesson_location"]
        }));
        assert.match(resume.url, /#\/preview$/, "Old quiz bookmark was not ignored");
        assert.match(resume.stored, /S5YWke1r4/, "Test must not destroy stored LMS progress");
        diagnostic.resume = resume;
      }
      diagnostic.lessonStatus = await page.evaluate(
        () => window.__scorm12.store["cmi.core.lesson_status"]);
      await page.screenshot({path:output + "/" + variant + ".png", fullPage:true});
      assert.equal(diagnostic.lessonStatus, "incomplete");
      // Both unmodified Articulate sources reference allowed-options.js
      // without shipping it. The player renders without this optional file.
      // Record the missing resource, but do not pretend it blocks launch.
      const knownOptional = url => new URL(url).pathname.endsWith(
        "/scormcontent/allowed-options.js");
      diagnostic.knownOptionalMissing = diagnostic.badResponses.filter(
        item => item.status === 404 && knownOptional(item.url));
      const unexpectedResponses = diagnostic.badResponses.filter(item =>
        !(item.status === 404 && knownOptional(item.url)));
      const unexpectedFailures = diagnostic.requestsFailed.filter(item =>
        !knownOptional(item.url));
      const unexpectedErrors = diagnostic.errors.filter(message =>
        !message.includes("Failed to load resource: the server responded with a status of 404"));
      assert.deepEqual(unexpectedResponses, [],
        "Launch requested unexpected missing resources");
      assert.deepEqual(unexpectedFailures, [],
        "Launch had unexpected failed HTTP requests");
      assert.deepEqual(unexpectedErrors, [],
        "Browser errors during driver launch");
      if (variant === "original") {
        assert.ok(diagnostic.knownOptionalMissing.length >= 1,
          "Expected source Rise optional script 404");
      } else {
        assert.equal(diagnostic.knownOptionalMissing.length, 0,
          "Rebuilt package must not reference missing optional script");
      }
    } catch (error) {
      failures++;
      diagnostic.error = String(error);
      diagnostic.frames = page.frames().map(f => ({url:f.url(), name:f.name()}));
      diagnostic.calls = await page.evaluate(
        () => window.__scorm12?.calls?.slice(0,60) || []).catch(()=>[]);
      await page.screenshot({path:output+"/"+variant+"-failure.png",
                            fullPage:true}).catch(()=>{});
    } finally {
      report.scenarios.push(diagnostic);
      await page.close();
    }
  }
} finally {
  writeFileSync(output+"/report.json",JSON.stringify(report,null,2)+"\n");
  await browser.close();
}
if(failures) {
  console.error(JSON.stringify(report,null,2));
  process.exitCode = 1;
} else {
  console.log("SCORM 1.2 real-driver QA PASS: both original and candidate launched");
}
