/* Verify the actual LoadContent() function embedded in all 20 rebuilt Rise ZIPs.
 * This executes its JS branch logic; no Moodle account or learner data is used. */
import assert from "node:assert/strict";
import {readFileSync, readdirSync, mkdirSync, writeFileSync} from "node:fs";
import {join} from "node:path";
import vm from "node:vm";
import {createRequire} from "node:module";
const require = createRequire(import.meta.url);
const JSZip = require("jszip");
const directory = "build/scorm-all20-qa";
const names = readdirSync(directory).filter(n => n.endsWith("-bez-testow.zip")).sort();
assert.equal(names.length, 20, "Twenty derived ZIPs must be built");
const report = {kind:"all20-actual-driver-bookmark-regression", results:[]};
mkdirSync("build/scorm-all20-report", {recursive:true});
let failed = false;
for (const filename of names) {
  const entry = {filename, cases:[]};
  report.results.push(entry);
  try {
    const zip = await JSZip.loadAsync(readFileSync(join(directory,filename)));
    const driver = await zip.file("scormdriver/indexAPI.html").async("string");
    const xml = await zip.file("imsmanifest.xml").async("string");
    assert.match(xml, /scormdriver\/indexAPI\.html/, "Missing SCORM launch file");
    assert.equal((driver.match(/function LoadContent\(\)\s*\{/g)||[]).length, 1);
    // Extract the exact generated implementation from the inline script:
    const start = driver.indexOf("function LoadContent() {");
    assert.ok(start >= 0);
    let depth = 0, end = -1;
    for (let pos = driver.indexOf("{", start); pos < driver.length; pos++) {
      if (driver[pos] === "{") depth++;
      else if (driver[pos] === "}" && --depth === 0) {
        end = pos + 1; break;
      }
    }
    assert.ok(end > start, "Cannot identify LoadContent function end");
    const body = driver.slice(start,end);
    const allow = /var validLessonIds = (\[[^;]+\]);/.exec(body);
    assert.ok(allow, "Guard did not emit lesson allowlist");
    const ids = JSON.parse(allow[1]);
    assert.ok(ids.length > 0);
    const cases = [
      ["first-launch", "", "#/preview"],
      ["valid-resume", "index.html#/lessons/" + ids[0], "#/lessons/" + ids[0]],
      ["stale-resume", "index.html#/lessons/deleted-final-quiz", "#/preview"]
    ];
    for (const [label,bookmark,suffix] of cases) {
      const state = {bookmark, stored:"existing-suspend-data"};
      const frame = {document:{location:{href:""}}};
      const context = {
        window:{scormdriver_content:frame},
        console:{warn(){}},
        strContentLocation:"../scormcontent/index.html#/preview",
        verifySuspendDataVersion(){},
        verifyForcedCommitTime(){},
        GetBookmark(){return state.bookmark}
      };
      vm.createContext(context);
      vm.runInContext(body + "\nLoadContent();", context, {timeout:1000});
      assert.ok(frame.document.location.href.endsWith(suffix),
        label+" navigated to "+frame.document.location.href);
      assert.equal(state.stored,"existing-suspend-data",
        label+" modified LMS progress");
      entry.cases.push(label);
    }
    entry.status="PASS";
  } catch(error) {
    entry.status="FAIL";
    entry.error=String(error);
    failed=true;
  }
}
writeFileSync("build/scorm-all20-report/bookmarks.json",
              JSON.stringify(report,null,2)+"\n");
console.log(JSON.stringify({passed:report.results.filter(x=>x.status==="PASS").length,
                             failed:report.results.filter(x=>x.status==="FAIL")}));
if(failed) process.exitCode=1;
