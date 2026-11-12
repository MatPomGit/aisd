#!/usr/bin/env python3
"""Conservative offline helper for inspecting and editing Rise 360 SCORM ZIPs.

Supports the documented modern runtime-data.js wrapper; will refuse legacy
courseData/LZW payloads rather than rewriting them incorrectly.

Commands:
  inspect ORIGINAL.zip
  export ORIGINAL.zip course.json
  rebuild ORIGINAL.zip edited.json NEW.zip
  verify PACKAGE.zip

This is NOT an LMS simulator. Moodle/SCORM Cloud runtime testing is required.
"""

import argparse
import base64
import copy
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PAYLOAD = 'scormcontent/runtime-data.js'
RE = re.compile(
    r'(?P<before>__jsonp\s*\(\s*(?P<q1>[\'\"])runtime-data\.js(?P=q1)\s*,\s*(?P<q2>[\'\"]))'
    r'(?P<blob>[A-Za-z0-9+/=]+)'
    r'(?P<after>(?P=q2)\s*\))'
)


class PackageError(Exception):
    pass


def read_package(path):
    try:
        zf = zipfile.ZipFile(path, 'r')
    except (OSError, zipfile.BadZipFile) as e:
        raise PackageError(f'Cannot open ZIP: {e}') from e
    names = zf.namelist()
    if len(names) != len(set(names)):
        zf.close()
        raise PackageError('Duplicate file names in ZIP; refuse unsafe rewrite')
    if 'imsmanifest.xml' not in names:
        zf.close()
        raise PackageError('imsmanifest.xml is not at ZIP root; not a valid standard SCORM root')
    return zf


def manifest_check(zf):
    try:
        root = ET.fromstring(zf.read('imsmanifest.xml'))
    except ET.ParseError as e:
        raise PackageError(f'Manifest XML is invalid: {e}') from e
    names = set(zf.namelist())
    base = root.attrib.get('{http://www.w3.org/XML/1998/namespace}base', '')
    problems = []
    launches = []
    for res in root.iter():
        if res.tag.split('}')[-1] != 'resource':
            continue
        href = res.attrib.get('href')
        if href and not re.match(r'^\w+://', href):
            from urllib.parse import unquote
            href = unquote(href.split('#')[0].split('?')[0])
            resbase = res.attrib.get('{http://www.w3.org/XML/1998/namespace}base', '')
            candidate = (base + resbase + href).replace('\\', '/')
            launches.append(candidate)
            if candidate and candidate not in names:
                problems.append(f'Launch target missing: {candidate}')
    if not launches:
        problems.append('No local launch href found in manifest (check manually)')
    return problems, launches


def extract_runtime(zf):
    if PAYLOAD not in zf.namelist():
        raise PackageError(
            f'{PAYLOAD} missing. This may be an older Rise output with '
            'window.courseData/LZW inside scormcontent/index.html. '
            'Manual format-specific analysis is required; do NOT patch blindly.'
        )
    raw = zf.read(PAYLOAD).decode('utf-8-sig')
    matches = list(RE.finditer(raw))
    if len(matches) != 1:
        raise PackageError(f'Expected precisely one __jsonp runtime payload; found {len(matches)}')
    match = matches[0]
    try:
        decoded = base64.b64decode(match['blob'], validate=True)
        data = json.loads(decoded.decode('utf-8-sig'))
    except (ValueError, UnicodeError, json.JSONDecodeError) as e:
        raise PackageError(f'Payload cannot be decoded as Base64 JSON: {e}') from e
    if not isinstance(data, dict) or not isinstance(data.get('course'), dict):
        raise PackageError('JSON has no expected course object; format-specific analysis needed')
    lessons = data['course'].get('lessons')
    if not isinstance(lessons, list):
        raise PackageError('JSON has no course.lessons list; format-specific analysis needed')
    return raw, match, data


def lesson_label(lesson):
    if not isinstance(lesson, dict):
        return '<non-object>'
    for key in ('title', 'name', 'heading', 'label'):
        x = lesson.get(key)
        if isinstance(x, str) and x:
            return x.replace('\n', ' ')[:100]
    return '<unnamed>'


def print_details(path, zf, strict_runtime=True):
    problems, launches = manifest_check(zf)
    print(f'Package: {path}')
    print('Launch target(s):', ', '.join(launches) or '<none>')
    print(f'ZIP entries: {len(zf.namelist())}')
    print('Manifest:', 'OK' if not problems else '; '.join(problems))
    bad = zf.testzip()
    print('ZIP integrity:', 'OK' if bad is None else f'FAIL: {bad}')
    if strict_runtime:
        _, _, data = extract_runtime(zf)
        lessons = data['course']['lessons']
        print(f'Course lessons: {len(lessons)}')
        for i, item in enumerate(lessons):
            typ = item.get('type', '?') if isinstance(item, dict) else '?'
            identity = item.get('id', '?') if isinstance(item, dict) else '?'
            print(f'  [{i}] {lesson_label(item)}    (type={typ!r}, id={identity!r})')
        print('CAUTION: type/title are only hints; inspect JSON before removing a lesson.')
        for f in ('scormcontent/index.html', 'indexAPI.html', 'indexapi.html'):
            if f in zf.namelist():
                s = zf.read(f).decode('utf-8', errors='replace')
                quizid = re.search(r'\b(?:var|let|const)\s+quizID\s*=\s*([^;]+);', s)
                if quizid:
                    print(f'Legacy quizID in {f}: {quizid.group(1)[:150]}')
    return not problems and bad is None


def do_inspect(args):
    with read_package(args.zipfile) as zf:
        good = print_details(args.zipfile, zf)
    return 0 if good else 2


def do_export(args):
    with read_package(args.zipfile) as zf:
        _, _, data = extract_runtime(zf)
    target = Path(args.jsonfile)
    if target.exists():
        raise PackageError(f'Output already exists: {target} (no overwrite)')
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Exported editable JSON: {target}')
    print('Edit course.lessons carefully. Check quiz-ID references and LMS tracking separately.')
    return 0


def do_rebuild(args):
    source = Path(args.zipfile)
    target = Path(args.output)
    if source.resolve() == target.resolve():
        raise PackageError('Output path must not equal original ZIP')
    if target.exists():
        raise PackageError(f'Output already exists: {target} (no overwrite)')
    try:
        data = json.loads(Path(args.jsonfile).read_text(encoding='utf-8-sig'))
    except (ValueError, OSError) as e:
        raise PackageError(f'Cannot parse edited JSON: {e}') from e
    if not isinstance(data, dict) or not isinstance(data.get('course'), dict) or not isinstance(data['course'].get('lessons'), list):
        raise PackageError('Edited JSON must include course.lessons array')
    if not data['course']['lessons']:
        raise PackageError('No lessons remain; refuse to create an empty course')
    with read_package(source) as zf:
        original_text, match, original = extract_runtime(zf)
        if len(original['course']['lessons']) <= len(data['course']['lessons']):
            print('CAUTION: lesson count did not decrease. You might not have removed the quiz.', file=sys.stderr)
        old_ids = {str(item.get('id')) for item in original['course']['lessons'] if isinstance(item, dict) and item.get('id') is not None}
        new_ids = {str(item.get('id')) for item in data['course']['lessons'] if isinstance(item, dict) and item.get('id') is not None}
        deleted_ids = old_ids - new_ids
        remaining = json.dumps(data, ensure_ascii=False)
        for ident in sorted(deleted_ids):
            if ident in remaining:
                raise PackageError(
                    f'Removed lesson ID {ident!r} still appears elsewhere in JSON. '
                    'Remove/repair all references (e.g., tracking/branching) before rebuilding.'
                )
        encoded = base64.b64encode(json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')).decode('ascii')
        new_text = original_text[:match.start('blob')] + encoded + original_text[match.end('blob'):]
        # Create a new package without changing zip paths or unaffected file bytes.
        with zipfile.ZipFile(target, 'w') as out:
            out.comment = zf.comment
            for item in zf.infolist():
                payload = new_text.encode('utf-8') if item.filename == PAYLOAD else zf.read(item.filename)
                out.writestr(item, payload)
    try:
        with read_package(target) as check:
            _, _, checked = extract_runtime(check)
            if checked != data:
                raise PackageError('Round-trip JSON mismatch')
            problems, launches = manifest_check(check)
            bad = check.testzip()
            if problems or bad:
                raise PackageError('Rebuilt package failed validation: ' + '; '.join(problems + ([bad] if bad else [])))
    except Exception:
        target.unlink(missing_ok=True)
        raise
    print(f'Rebuilt: {target}')
    print(f'Lessons: {len(original["course"]["lessons"])} -> {len(data["course"]["lessons"])}')
    print('IMPORTANT: This changes course content, not necessarily quiz-based tracking.')
    print('MUST test navigation, completion, scores, resume, and Moodle activity settings before deployment.')
    return 0


def do_verify(args):
    with read_package(args.zipfile) as zf:
        ok = print_details(args.zipfile, zf, strict_runtime=False)
        if PAYLOAD in zf.namelist():
            try:
                _, _, data = extract_runtime(zf)
                print(f'Runtime JSON: OK, {len(data["course"]["lessons"])} lessons')
            except PackageError as e:
                print(f'Runtime JSON: FAIL: {e}')
                ok = False
    print('NOTE: Static verification is not proof that the course completes in an LMS.')
    return 0 if ok else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    for name, positional, fun in [
        ('inspect', ('zipfile',), do_inspect),
        ('export', ('zipfile', 'jsonfile'), do_export),
        ('rebuild', ('zipfile', 'jsonfile', 'output'), do_rebuild),
        ('verify', ('zipfile',), do_verify),
    ]:
        p = sub.add_parser(name)
        for x in positional:
            p.add_argument(x)
        p.set_defaults(func=fun)
    a = parser.parse_args()
    try:
        return a.func(a)
    except (PackageError, OSError) as err:
        print('ERROR:', err, file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
