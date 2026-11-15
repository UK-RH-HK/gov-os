"""Run 9 (DEC-1183 (2), S27's folder mode): a recording ``gitleaks`` first on ``PATH`` and the reading of its log.

The wrapper is a small Python program the case writes into a folder of its own. At each call it notes, as one JSON line in
the case's log (under a lock): its pid, its arguments, its start and end times, and, for ``gitleaks dir <folder>``, the
folder argument (the one after ``dir``), whether it is a folder, its mode, and every entry under it (the name relative to
the folder and its mode), and for each text it was given (each file of the folder, or the whole of standard input for
``gitleaks stdin``) the planted tags it holds (``s27tag-...``: words the case writes into its planted files, never a secret)
and whether it holds the case's marker. It then runs the real gitleaks with the same arguments and standard input and, by
its mode, passes the answer through or (only for a call whose texts hold the marker) answers otherwise:

- ``pass``: the real answer, unchanged (a logging wrapper only);
- ``fail``: the real report on stdout, but exit code 2 (neither 0 nor 3);
- ``garbage``: exit 3 with a report that cannot be read (``{ not a report``);
- ``foreign``: exit 3 with a report of one finding whose ``File`` names no file of the folder (``<folder>/999999``).

No secret's value is read into the log: only tags, names, modes and the marker's presence. ``delay`` makes each call wait
before it runs the real one (to see calls overlap).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import w2_88_support as W

TAG = "s27tag-"

_PROGRAM = r'''
import fcntl, json, os, re, stat, subprocess, sys, time
REAL, LOG, MODE, MARK, DELAY = {real!r}, {log!r}, {mode!r}, {mark!r}, {delay!r}
TAGS = re.compile(rb"s27tag-[0-9A-Za-z_-]+")
args = sys.argv[1:]
entry = {{"pid": os.getpid(), "args": args, "start": time.time(), "folder": None}}
texts, data = [], None
if len(args) > 1 and args[0] == "dir":
    folder = args[1]
    entry["folder"] = folder
    try:
        info = os.stat(folder)
        entry["mode"], entry["isdir"] = stat.S_IMODE(info.st_mode), stat.S_ISDIR(info.st_mode)
    except OSError as error:
        entry["mode"], entry["isdir"] = None, False
    entries = []
    if entry["isdir"]:
        for here, folders, files in os.walk(folder):
            for name in folders + files:
                full = os.path.join(here, name)
                entries.append([os.path.relpath(full, folder), stat.S_IMODE(os.lstat(full).st_mode)])
            for name in sorted(files):
                with open(os.path.join(here, name), "rb") as handle:
                    texts.append(handle.read())
    elif os.path.isfile(folder):
        with open(folder, "rb") as handle:
            texts.append(handle.read())
    entry["entries"] = entries
elif args and args[0] == "stdin":
    data = sys.stdin.buffer.read()
    texts.append(data)
entry["texts"] = [sorted({{t.decode() for t in TAGS.findall(text)}}) for text in texts]
marked = bool(MARK) and any(MARK.encode() in text for text in texts)
entry["marked"] = marked
del texts
if DELAY:
    time.sleep(DELAY)
done = subprocess.run([REAL, *args], input=data, capture_output=True)
out, code = done.stdout, done.returncode
if marked and MODE == "fail":
    code = 2
elif marked and MODE == "garbage":
    out, code = b"{{ not a report", 3
elif marked and MODE == "foreign":
    where = os.path.join(entry["folder"] or "", "999999")
    out, code = json.dumps([{{"RuleID": "generic-api-key", "Description": "planted", "File": where, "StartLine": 1,
                              "EndLine": 1, "StartColumn": 1, "EndColumn": 9, "Match": "REDACTED", "Secret": "REDACTED",
                              "Fingerprint": where + ":generic-api-key:1"}}]).encode(), 3
entry["code"], entry["end"] = code, time.time()
with open(LOG, "a", encoding="utf-8") as log:
    fcntl.flock(log, fcntl.LOCK_EX)
    log.write(json.dumps(entry) + "\n")
sys.stdout.buffer.write(out)
sys.stderr.buffer.write(done.stderr)
sys.exit(code)
'''


def recording_gitleaks(folder: Path, log: Path, *, mode: str = "pass", mark: str | None = None, delay: float = 0.0) -> Path:
    """Write the recording ``gitleaks`` into ``folder`` (to be put first on ``PATH``); returns ``folder``."""
    assert mode in ("pass", "fail", "garbage", "foreign")
    folder.mkdir(parents=True, exist_ok=True)
    program = folder / "gitleaks"
    body = _PROGRAM.format(real=str(W.S124.REAL_GITLEAKS), log=str(log), mode=mode, mark=mark or "", delay=delay)
    program.write_text(f"#!{sys.executable}\n" + body, encoding="utf-8")
    program.chmod(0o755)
    return folder


def calls(log: Path) -> list[dict]:
    """The calls the wrapper noted, in the order they ended."""
    if not log.is_file():
        return []
    return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines() if line.strip()]


def peak(noted: list[dict]) -> int:
    """The most calls that ran at the same moment."""
    events = sorted([(c["start"], 1) for c in noted] + [(c["end"], -1) for c in noted], key=lambda e: (e[0], e[1]))
    running = top = 0
    for _stamp, step in events:
        running += step
        top = max(top, running)
    return top


def tags_of(call: dict) -> set:
    """Every planted tag among the texts of one call."""
    return {tag for text in call.get("texts", []) for tag in text}
