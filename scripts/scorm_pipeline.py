#!/usr/bin/env python3
"""Build and validate assessment-free SCORM 1.2 Rise packages. Python 3.11+, stdlib only.

Fail-closed: only tested embedded Base64 JSON in scormcontent/index.html
(and compatible runtime-data.js wrappers) with explicit quiz-based tracking.
This tool does not upload to Moodle or claim LMS conformance.
"""
import argparse
import base64
import copy
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from scorm_editorial import EditorialError, apply_editorial, SCORM01_COURSE_ID, SCORM01_RELEASE

HTML = "scormcontent/index.html"
MODERN = "scormcontent/runtime-data.js"
LEGACY_RE = re.compile(
    r'(?P<start>async\s+function\s+__fetchCourse\s*\(\s*\)\s*\{\s*'
    r'return\s+Promise\.resolve\s*\(\s*deserialize\s*\(\s*")'
    r'(?P<blob>[A-Za-z0-9+/=]+)(?P<end>"\s*\)\s*\))'
)
MODERN_RE = re.compile(
    r'(?P<start>__jsonp\s*\(\s*["\']runtime-data\.js["\']\s*,\s*["\'])'
    r'(?P<blob>[A-Za-z0-9+/=]+)(?P<end>["\']\s*\))'
)
FIELDS = ("quizId", "storylineId", "completionPercentage", "reporting")
TRACKING = {
    "quizId": None,
    "storylineId": None,
    "completionPercentage": 100,
    "reporting": "completed-incomplete",
}


class BuildError(Exception):
    """Unsupported or invalid package; do not publish it."""


def open_zip(path):
    try:
        archive = zipfile.ZipFile(path)
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise BuildError("Duplicate ZIP entries")
        for name in names:
            parts = name.replace("\\", "/").split("/")
            if name.startswith("/") or ".." in parts or "\\" in name:
                raise BuildError("Unsafe archive entry: " + name)
        if "imsmanifest.xml" not in names:
            raise BuildError("Missing root imsmanifest.xml")
        if archive.testzip() is not None:
            raise BuildError("ZIP checksum failure")
        return archive
    except (zipfile.BadZipFile, OSError, ValueError) as exc:
        raise BuildError(str(exc)) from exc


def check_manifest(zf):
    try:
        root = ET.fromstring(zf.read("imsmanifest.xml"))
    except ET.ParseError as exc:
        raise BuildError("Invalid imsmanifest.xml") from exc
    versions = [e.text.strip() for e in root.iter()
                if e.tag.rsplit("}", 1)[-1] == "schemaversion" and e.text]
    if versions != ["1.2"]:
        raise BuildError("Only SCORM 1.2 supported; found " + repr(versions))
    names = set(zf.namelist())
    base_attr = "{http://www.w3.org/XML/1998/namespace}base"
    root_base = root.get(base_attr, "")
    launches = []
    for resource in root.iter():
        if resource.tag.rsplit("}", 1)[-1] != "resource":
            continue
        resource_base = resource.get(base_attr, "")
        hrefs = [resource.get("href", "")]
        hrefs += [e.get("href", "") for e in resource
                  if e.tag.rsplit("}", 1)[-1] == "file"]
        for i, href in enumerate(hrefs):
            if not href:
                continue
            from urllib.parse import unquote
            path = unquote(href.split("#")[0].split("?")[0])
            if "://" in path:
                raise BuildError("External manifest resource: " + href)
            resolved = (root_base + resource_base + path).replace("\\", "/")
            if resolved not in names:
                raise BuildError("Missing referenced resource: " + resolved)
            if i == 0:
                launches.append(resolved)
    if not launches or any(not x.endswith("indexAPI.html") for x in launches):
        raise BuildError("Unexpected launch targets: " + repr(launches))
    return launches



def complete_manifest(zf):
    """List every regular ZIP member in the SCORM resource without changing assets.

    Preserve original Rise XML (including namespaces, metadata and launch info).
    Manifest itself is not a resource; directory entries are not files.
    """
    from xml.sax.saxutils import quoteattr
    xml = zf.read("imsmanifest.xml").decode("utf-8-sig")
    root = ET.fromstring(xml)
    resources = [r for r in root.iter()
                 if r.tag.rsplit("}", 1)[-1] == "resource"]
    if len(resources) != 1:
        raise BuildError("Expected exactly one Rise SCO resource")
    resource = resources[0]
    if root.get("{http://www.w3.org/XML/1998/namespace}base") or resource.get(
            "{http://www.w3.org/XML/1998/namespace}base"):
        raise BuildError("Cannot safely extend manifest with xml:base")
    referenced = {e.get("href") for e in resource
                  if e.tag.rsplit("}", 1)[-1] == "file"}
    missing = sorted(set(zf.namelist()) - referenced - {"imsmanifest.xml"})
    missing = [name for name in missing if not name.endswith("/")]
    if not missing:
        return zf.read("imsmanifest.xml")
    closing = re.search(r"</(?:[A-Za-z_][\w.-]*:)?resource\s*>", xml)
    if not closing or len(re.findall(r"</(?:[A-Za-z_][\w.-]*:)?resource\s*>", xml)) != 1:
        raise BuildError("Cannot safely find single SCORM resource closing tag")
    additions = "".join("      <file href=" + quoteattr(name) + "/>\n"
                        for name in missing)
    return (xml[:closing.start()] + additions + xml[closing.start():]).encode("utf-8")


def unlisted_manifest_files(zf):
    root = ET.fromstring(zf.read("imsmanifest.xml"))
    referenced = {e.get("href") for e in root.iter()
                  if e.tag.rsplit("}", 1)[-1] == "file"}
    return sorted(name for name in zf.namelist()
                  if name != "imsmanifest.xml" and not name.endswith("/")
                  and name not in referenced)


def get_data(zf):
    path = MODERN if MODERN in zf.namelist() else HTML
    if path not in zf.namelist():
        raise BuildError("No recognized Rise data container")
    html = zf.read(path).decode("utf-8-sig")
    regex = MODERN_RE if path == MODERN else LEGACY_RE
    matches = list(regex.finditer(html))
    if len(matches) != 1:
        raise BuildError("Unsupported Rise data encoding in " + path)
    hit = matches[0]
    try:
        data = json.loads(base64.b64decode(hit["blob"], validate=True).decode("utf-8-sig"))
    except (ValueError, UnicodeError) as exc:
        raise BuildError("Base64/JSON decoding failed") from exc
    if not isinstance(data, dict) or not isinstance(data.get("course"), dict):
        raise BuildError("Missing course object")
    if not isinstance(data["course"].get("lessons"), list):
        raise BuildError("Missing course.lessons array")
    return path, html, hit, data


def get_tracking(html):
    result = {}
    for key in FIELDS:
        regex = re.compile(r"(?P<prefix>\bvar\s+" + key
                           + r"\s*=\s*)(?P<value>[^;\r\n]+)(?P<suffix>\s*;)")
        matches = list(regex.finditer(html))
        if len(matches) != 1:
            raise BuildError("Missing/ambiguous tracking field: " + key)
        val = matches[0]["value"].strip()
        try:
            result[key] = json.loads(val.replace("'", '"')) if val != "undefined" else None
        except ValueError as exc:
            raise BuildError("Unsupported tracking value: " + key) from exc
    return result


def set_tracking(html, values):
    for key, value in values.items():
        regex = re.compile(r"(?P<prefix>\bvar\s+" + key
                           + r"\s*=\s*)(?P<value>[^;\r\n]+)(?P<suffix>\s*;)")
        if len(regex.findall(html)) != 1:
            raise BuildError("Cannot safely patch: " + key)
        html = regex.sub(lambda m: m["prefix"]
                         + json.dumps(value) + m["suffix"], html, count=1)
    return html


def encode(html, hit, data):
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    blob = base64.b64encode(payload).decode("ascii")
    return (html[:hit.start("blob")] + blob + html[hit.end("blob"):]).encode("utf-8")


def get_quiz(data):
    lessons = data["course"]["lessons"]
    quizzes = [(i, l) for i, l in enumerate(lessons)
               if isinstance(l, dict) and l.get("type") == "quiz"]
    if len(quizzes) != 1 or quizzes[0][0] != len(lessons) - 1:
        raise BuildError("Expected exactly one terminal quiz; found "
                         + repr([l.get("id") for _, l in quizzes]))
    if len(lessons) < 2:
        raise BuildError("No instructional lessons to retain")
    quiz = quizzes[0][1]
    if not isinstance(quiz.get("id"), str) or not quiz["id"]:
        raise BuildError("Missing quiz ID")
    return quiz


def adapt_embedded_final_test(data):
    """Known course 04: keep learning advice, remove terminal self-test and answer key.

    This is an exact-schema allowlist, never a title-based global heuristic.
    Unknown block structures must be reviewed rather than auto-trimmed.
    """
    lessons = data["course"]["lessons"]
    last = lessons[-1]
    if last.get("id") != "cmiej97dl000d207092aujenc":
        return False
    if last.get("title") != "Test końcowy i omówienie rozwiązań":
        raise BuildError("Known final assessment changed its title")
    expected_types = (["text", "text", "list", "divider"]
                      + ["knowledgeCheck"] * 7
                      + ["divider", "text", "interactive", "text", "interactive", "text"])
    items = last.get("items")
    if not isinstance(items, list) or [x.get("type") for x in items] != expected_types:
        raise BuildError("Known course 04 block layout changed; refuse automatic edit")
    if items[13].get("variant") != "tabs" or items[15].get("variant") != "accordion":
        raise BuildError("Known answer-key/advice structure changed")
    # Remove test introduction, seven assessment questions and the answer key.
    # Preserve only 'common mistakes and tips' and the course closing message.
    last["items"] = items[14:17]
    last["title"] = "Najczęstsze błędy i wskazówki"
    return True


ASSESSMENT_HEADINGS = {
    "sprawdź swoją wiedzę",
    "sprawdzanie wiedzy",
    "sprawdzenie wiedzy",
    "check your understanding",
}


def is_assessment_heading(block):
    """Only recognize exact Rise assessment headings, not arbitrary topic headings."""
    if not isinstance(block, dict) or block.get("type") != "text":
        return False
    if "heading" not in str(block.get("variant", "")):
        return False
    return any(
        isinstance(part, dict)
        and isinstance(part.get("heading"), str)
        and part["heading"].strip().casefold() in ASSESSMENT_HEADINGS
        for part in block.get("items", [])
    )


def assessment_counts(data):
    """Count actual answerable blocks and section markers in retained lessons."""
    lessons = data["course"]["lessons"]
    return {
        "quizzes": sum(l.get("type") == "quiz" for l in lessons),
        "knowledge_checks": sum(
            b.get("type") == "knowledgeCheck"
            for l in lessons for b in l.get("items", [])
        ),
        "assessment_headings": sum(
            is_assessment_heading(b)
            for l in lessons for b in l.get("items", [])
        ),
    }


def remove_knowledge_checks(data):
    """Delete assessment sections (including check-only interactives) from all lessons.

    A known heading starts a check section, which ends at a CONTINUE divider or
    an explanatory paragraph / impact text after the last question. Only
    assessment-scoped interactives are removed; didactic interactives outside
    those sections are preserved. Remaining isolated knowledgeCheck blocks are
    removed individually.
    """
    removed = {"checks": 0, "headings": 0, "section_blocks": 0}
    for lesson in data["course"]["lessons"]:
        if lesson.get("type") == "quiz":
            raise BuildError("Cannot strip checks before removing quiz")
        items = lesson.get("items", [])
        if not isinstance(items, list):
            raise BuildError("Non-list lesson items: " + str(lesson.get("id")))
        output = []
        i = 0
        while i < len(items):
            block = items[i]
            if not isinstance(block, dict):
                raise BuildError("Unexpected non-object block in " + str(lesson.get("id")))
            if is_assessment_heading(block):
                j, saw_check = i + 1, False
                while j < len(items):
                    candidate = items[j]
                    if not isinstance(candidate, dict):
                        raise BuildError("Invalid assessment block")
                    if candidate.get("type") == "divider" and candidate.get("variant") == "continue":
                        j += 1
                        break
                    if saw_check and candidate.get("type") == "text" and candidate.get("variant") in ("b", "paragraph"):
                        # Keep learning conclusions after the removed questions.
                        break
                    if candidate.get("type") == "knowledgeCheck":
                        saw_check = True
                    j += 1
                if not saw_check:
                    raise BuildError("Cannot safely identify assessment section: " + str(lesson.get("title")))
                removed["headings"] += 1
                removed["checks"] += sum(x.get("type") == "knowledgeCheck" for x in items[i:j])
                removed["section_blocks"] += j - i
                i = j
                continue
            if block.get("type") == "knowledgeCheck":
                removed["checks"] += 1
                removed["section_blocks"] += 1
                i += 1
                continue
            output.append(block)
            i += 1
        if items and not output:
            raise BuildError("Assessment removal would empty lesson: " + str(lesson.get("id")))
        lesson["items"] = output
    remaining = assessment_counts(data)
    if any(remaining.values()):
        raise BuildError("Assessment objects remained after cleanup: " + repr(remaining))
    return removed


def new_course(original, tracking, *, include_editorial=True):
    data = copy.deepcopy(original)
    lessons = data["course"]["lessons"]
    quiz_count = sum(isinstance(l, dict) and l.get("type") == "quiz" for l in lessons)
    settings = data["course"].get("exportSettings")
    if not isinstance(settings, dict):
        raise BuildError("Missing course.exportSettings")
    if tracking["storylineId"] is not None:
        raise BuildError("Unsupported Storyline tracking")
    if quiz_count:
        quiz = get_quiz(data)
        qid = quiz["id"]
        if tracking["quizId"] != qid or settings.get("quizId") != qid:
            raise BuildError("Quiz tracking ID differs from terminal quiz ID")
        if settings.get("completeWith") != "quiz":
            raise BuildError("Unsupported quiz completion mode")
        lessons.pop()
    else:
        # Some originals already contain no formal Rise quiz. Keep all lessons:
        # arbitrary 'test' blocks may also contain explanations and examples.
        quiz = None
        qid = None
        if tracking["quizId"] is not None or settings.get("quizId") is not None:
            raise BuildError("No quiz in lessons but quiz tracking still configured")
        if settings.get("completeWith") not in ("reporting", "course"):
            raise BuildError("Unsupported no-quiz completion mode")
        if not lessons:
            raise BuildError("Empty course")
        adapt_embedded_final_test(data)
    remove_knowledge_checks(data)
    if include_editorial:
        try:
            apply_editorial(data)
        except EditorialError as exc:
            raise BuildError("Editorial overlay rejected: " + str(exc)) from exc
    settings.update({
        "quizId": None,
        "completeWith": "course",
        "quizComplete": False,
        "completionPercentage": 100,
        "reporting": "completed-incomplete",
    })
    if qid and qid in json.dumps(data, ensure_ascii=False):
        raise BuildError("Removed quiz is still referenced elsewhere")
    return data, quiz



def protect_stale_scorm01_bookmark(driver_html, lessons):
    """Prevent a deleted lesson bookmark from navigating to a nonexistent page."""
    marker = '      if (bookmark != "") {'
    if driver_html.count(marker) != 1:
        raise BuildError("Unsupported SCORM01 driver bookmark layout")
    ids = [lesson.get("id") for lesson in lessons]
    if len(ids) != len(set(ids)) or not all(isinstance(x, str) and x for x in ids):
        raise BuildError("Invalid lesson IDs for bookmark guard")
    allowed = json.dumps(ids, ensure_ascii=True)
    guard = (
        '      // Preserve LMS suspend data; only ignore an invalid navigation target.\n'
        '      var validLessonIds = ' + allowed + ';\n'
        '      var bookmarkMatch = /^index\\.html#\\/lessons\\/([^/?#]+)$/.exec(bookmark);\n'
        '      var knownBookmark = bookmark === "index.html" || '
        'bookmark === "index.html#/preview" || '
        '(bookmarkMatch && validLessonIds.indexOf(bookmarkMatch[1]) !== -1);\n'
        '      if (bookmark !== "" && !knownBookmark) {\n'
        '        console.warn("Saved bookmark references a missing lesson; opening cover");\n'
        '      }\n'
    )
    return driver_html.replace(marker, guard + '      if (bookmark != "" && knownBookmark) {', 1)


def strip_missing_optional_options_script(html, zf):
    """Remove a Rise reference to an absent optional script.

    The canonical export is unchanged. Only the exact known script tag is
    removable and only if the referred file is absent from the source ZIP.
    Any unexpected placement or changed tag is deliberately left untouched.
    """
    filename = "scormcontent/allowed-options.js"
    tag = '<script type="text/javascript" src="allowed-options.js"></script>'
    if filename not in zf.namelist() and html.count(tag) == 1:
        return html.replace(tag, "", 1)
    return html



def build_one(source, output, *, include_editorial=True):
    source, output = Path(source), Path(output)
    if source.resolve() == output.resolve() or output.exists():
        raise BuildError("Output exists or would overwrite original: " + str(output))
    with open_zip(source) as src:
        check_manifest(src)
        path, text, match, data = get_data(src)
        if HTML not in src.namelist():
            raise BuildError("No HTML tracking runtime")
        original_html = src.read(HTML).decode("utf-8-sig")
        tracking = get_tracking(original_html)
        result, quiz = new_course(data, tracking, include_editorial=include_editorial)
        replacements = {path: encode(text, match, result),
                        "imsmanifest.xml": complete_manifest(src)}
        if path == HTML:
            replacements[HTML] = set_tracking(replacements[HTML].decode("utf-8"), TRACKING).encode("utf-8")
        else:
            replacements[HTML] = set_tracking(original_html, TRACKING).encode("utf-8")
        replacements[HTML] = strip_missing_optional_options_script(
            replacements[HTML].decode("utf-8"), src).encode("utf-8")
        if include_editorial and result["course"].get("id") == SCORM01_COURSE_ID:
            driver_path = "scormdriver/indexAPI.html"
            if driver_path not in src.namelist():
                raise BuildError("Missing Rise launch driver")
            replacements[driver_path] = protect_stale_scorm01_bookmark(
                src.read(driver_path).decode("utf-8-sig"),
                result["course"]["lessons"]
            ).encode("utf-8")

            # The course is in Polish. Set the first paint language for
            # assistive technologies; the Rise player also reads labelSet
            # and course locale metadata from the edited JSON.
            content_html = replacements[HTML].decode("utf-8")
            if content_html.count('<html lang="en"') != 1:
                raise BuildError("Unexpected Rise HTML document language")
            replacements[HTML] = content_html.replace(
                '<html lang="en"', '<html lang="pl"', 1
            ).encode("utf-8")
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(output, "w") as dst:
                dst.comment = src.comment
                for item in src.infolist():
                    dst.writestr(item, replacements.get(item.filename, src.read(item.filename)))
            validate_pair(source, output, include_editorial=include_editorial)
        except Exception:
            output.unlink(missing_ok=True)
            raise
    before_counts = assessment_counts(data)
    after_counts = assessment_counts(result)
    if any(after_counts.values()):
        raise BuildError("Assessments remain in output")
    removed_checks = before_counts["knowledge_checks"] - after_counts["knowledge_checks"]
    if removed_checks < 0:
        raise BuildError("Knowledge check count unexpectedly increased")
    removed_heading_count = before_counts["assessment_headings"] - after_counts["assessment_headings"]
    manual_review = [
        l.get("title", "") for l in result["course"]["lessons"]
        if isinstance(l, dict) and any(
            word in str(l.get("title", "")).lower()
            for word in ("test końcowy", "egzamin końcowy", "final quiz")
        )
    ]
    adapted_review = (
        not quiz
        and data["course"]["lessons"][-1].get("id") == "cmiej97dl000d207092aujenc"
        and data["course"]["lessons"][-1].get("title") == "Test końcowy i omówienie rozwiązań"
        and result["course"]["lessons"][-1].get("title") == "Najczęstsze błędy i wskazówki"
    )
    return {"source": source.name, "artifact": output.name,
            "removed_quiz": quiz.get("title", quiz["id"]) if quiz else None,
            "lesson_count": len(result["course"]["lessons"]),
            "editorial_overlay": (
                SCORM01_RELEASE
                if include_editorial and result["course"].get("id") == SCORM01_COURSE_ID
                else None
            ),
            "knowledge_checks_removed": removed_checks,
            "assessment_sections_removed": removed_heading_count,
            "embedded_test_removed": adapted_review,
            "manual_review": manual_review,
            "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}


def validate_pair(source, output, *, include_editorial=True):
    with open_zip(source) as src, open_zip(output) as dst:
        check_manifest(src)
        check_manifest(dst)
        if unlisted_manifest_files(dst):
            raise BuildError("Unlisted files in generated manifest: " +
                             repr(unlisted_manifest_files(dst)))
        if dst.read("imsmanifest.xml") != complete_manifest(src):
            raise BuildError("Unexpected manifest modification")
        original_names = src.namelist()
        if original_names != dst.namelist():
            raise BuildError("Archive member list/order changed")
        old_path, _, _, old = get_data(src)
        new_path, _, _, new = get_data(dst)
        if old_path != new_path:
            raise BuildError("Data container changed")
        has_quiz = any(isinstance(x, dict) and x.get("type") == "quiz"
                       for x in old["course"]["lessons"])
        removed = get_quiz(old) if has_quiz else None
        expected, _ = new_course(old, get_tracking(src.read(HTML).decode("utf-8-sig")),
                                 include_editorial=include_editorial)
        if new["course"]["lessons"] != expected["course"]["lessons"]:
            raise BuildError("Unexpected lesson changes")
        if new != expected:
            raise BuildError("Unexpected JSON changes")
        if "scormcontent/allowed-options.js" not in src.namelist():
            source_html = src.read(HTML).decode("utf-8-sig")
            if source_html.count('<script type="text/javascript" src="allowed-options.js"></script>') == 1:
                if 'src="allowed-options.js"' in dst.read(HTML).decode("utf-8-sig"):
                    raise BuildError("Dangling optional Rise script reference retained")
        if get_tracking(dst.read(HTML).decode("utf-8-sig")) != TRACKING:
            raise BuildError("Incorrect completion tracking; potential grade reporting")
        if any(isinstance(x, dict) and x.get("type") == "quiz"
               for x in new["course"]["lessons"]):
            raise BuildError("Quiz remains")
        if any(assessment_counts(new).values()):
            raise BuildError("Knowledge checks or assessment headings remain")
        driver_path = "scormdriver/indexAPI.html"
        if include_editorial and expected["course"].get("id") == SCORM01_COURSE_ID:
            expected_driver = protect_stale_scorm01_bookmark(
                src.read(driver_path).decode("utf-8-sig"), new["course"]["lessons"])
            if dst.read(driver_path).decode("utf-8-sig") != expected_driver:
                raise BuildError("Unexpected SCORM01 launch driver change")
        changed = {old_path, HTML, "imsmanifest.xml"}
        if include_editorial and expected["course"].get("id") == SCORM01_COURSE_ID:
            changed.add(driver_path)
        for item in src.infolist():
            other = dst.getinfo(item.filename)
            if item.compress_type != other.compress_type or item.date_time != other.date_time:
                raise BuildError("ZIP entry metadata changed: " + item.filename)
            if item.filename not in changed and src.read(item.filename) != dst.read(item.filename):
                raise BuildError("Non-course asset changed: " + item.filename)
        return {"removed_quiz_id": removed["id"] if removed else None,
                "lessons": len(new["course"]["lessons"]), "status": "PASS"}


def enumerate_raw(directory, course):
    paths = sorted(Path(directory).glob("*.zip"),
                   key=lambda p: (int(p.name.split("-", 1)[0])
                                  if p.name.split("-", 1)[0].isdigit() else 9999, p.name))
    if course != "all":
        if not course.isdigit() or not (1 <= int(course) <= 20):
            raise BuildError("Course must be 'all' or number 1..20")
        paths = [p for p in paths if p.name.split("-", 1)[0].isdigit()
                 and int(p.name.split("-", 1)[0]) == int(course)]
    if not paths:
        raise BuildError("No source ZIP matched " + course)
    if course == "all" and len(paths) != 20:
        raise BuildError("Expected 20 raw packages, found " + str(len(paths)))
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    build = subs.add_parser("build", help="Rebuild raw ZIP(s) into ungraded SCORM ZIP(s)")
    build.add_argument("--course", default="all")
    build.add_argument("--raw-dir", default="raw")
    build.add_argument("--output-dir", default="build/scorm")
    validate = subs.add_parser("validate", help="Compare rebuilt ZIP with original")
    validate.add_argument("source")
    validate.add_argument("output")
    inspect = subs.add_parser("inspect", help="Inspect a Rise ZIP (no mutation)")
    inspect.add_argument("source")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            results = []
            for raw in enumerate_raw(args.raw_dir, args.course):
                target = Path(args.output_dir) / (raw.stem + "-bez-testow.zip")
                result = build_one(raw, target)
                results.append(result)
                print(json.dumps(result, ensure_ascii=False), flush=True)
            manifest = Path(args.output_dir) / "build-report.json"
            manifest.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        elif args.command == "validate":
            print(json.dumps(validate_pair(args.source, args.output), ensure_ascii=False))
        elif args.command == "inspect":
            with open_zip(args.source) as zf:
                launches = check_manifest(zf)
                path, _, _, data = get_data(zf)
                print(json.dumps({"container": path, "launch": launches,
                                  "lessons": [{"title": l.get("title"), "type": l.get("type")}
                                              for l in data["course"]["lessons"]],
                                  "tracking": get_tracking(zf.read(HTML).decode("utf-8-sig"))},
                                 ensure_ascii=False, indent=2))
        return 0
    except (BuildError, OSError, UnicodeError, zipfile.BadZipFile) as exc:
        print("SCORM ERROR:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
