#!/usr/bin/env node
// Isolated Rise runtime contract test. Reads scormcontent/index.html via stdin.
// This is NOT a Moodle end-to-end test. No external network or browser required.
"use strict";
const fs = require("node:fs");
const vm = require("node:vm");
const html = fs.readFileSync(0, "utf8");
const match = html.match(/<script>\s*(\(function\(root\) \{[\s\S]*?\}\(window\)\);)\s*<\/script>/);
if (!match) throw new Error("Unsupported Rise inline runtime; manual inspection required");

const calls = [];
const parent = { LESSON_STATUS_PASSED: "passed" };
const proxy = [
  "CommitData", "ConcedeControl", "CreateResponseIdentifier", "Finish",
  "GetDataChunk", "GetStatus", "GetStudentID", "MatchingResponse",
  "RecordFillInInteraction", "RecordMatchingInteraction",
  "RecordMultipleChoiceInteraction", "ResetStatus", "SetBookmark",
  "SetDataChunk", "SetFailed", "SetLanguagePreference", "SetPassed",
  "SetReachedEnd", "SetScore", "WriteToDebug"
];
for (const key of proxy) {
  parent[key] = (...args) => {
    calls.push({ name: key, args });
    if (key === "GetDataChunk") return "";
    if (key === "GetStatus") return "incomplete";
    return true;
  };
}
const window = { parent };
const context = {
  window, console, TextEncoder, Uint8Array, clearTimeout, setTimeout,
  document: {}, lzwCompress: { pack: x => x, unpack: x => x },
};
vm.runInNewContext(match[1], context, { timeout: 5000 });
const runtime = window.Runtime;
if (typeof runtime?.finish !== "function" ||
    typeof runtime.finishQuiz !== "function") {
  throw new Error("Rise Runtime.finish/finishQuiz unavailable");
}
function check(progress, required, forbidden) {
  calls.length = 0;
  runtime.finish(progress);
  const names = calls.map(x => x.name);
  for (const item of required) {
    if (!names.includes(item)) throw new Error(`At ${progress}%: missing ${item}`);
  }
  for (const item of forbidden) {
    if (names.includes(item)) throw new Error(`At ${progress}%: unexpected ${item}`);
  }
}
check(99, [], ["SetReachedEnd", "SetPassed", "SetScore"]);
check(100, ["SetReachedEnd"], ["SetPassed", "SetScore", "SetFailed"]);
calls.length = 0;
runtime.finishQuiz(true, 97, "obsolete-quiz-id");
if (calls.some(x => ["SetScore", "SetReachedEnd", "SetPassed"].includes(x.name))) {
  throw new Error("Orphaned quiz emitted score/completion call");
}
console.log("Runtime contract PASS: 99%=incomplete, 100%=completed, no quiz score");
