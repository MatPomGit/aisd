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
  for (const variant of ["original", "candidate"]) {
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
      await page.goto("http://127.0.0.1:8787/scorm12-driver-harness.html?source=" + variant,
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
        return Boolean(child?.contentWindow?.document?.body
          ?.innerText?.includes("ROZPOCZNIJ KURS"));
      }, null, {timeout:30000});
      diagnostic.rendered = true;
      diagnostic.lessonStatus = await page.evaluate(
        () => window.__scorm12.store["cmi.core.lesson_status"]);
      await page.screenshot({path:output + "/" + variant + ".png", fullPage:true});
      assert.equal(diagnostic.lessonStatus, "incomplete");
      assert.deepEqual(diagnostic.badResponses, [],
        "Launch requested missing resources");
      assert.deepEqual(diagnostic.requestsFailed, [],
        "Launch had failed HTTP requests");
      assert.deepEqual(diagnostic.errors, [],
        "Browser errors during driver launch");
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
