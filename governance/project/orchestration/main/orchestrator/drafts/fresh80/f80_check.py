#!/usr/bin/env python3
"""run_measure.sh's checks (FRESH-80-1 §2 items 1, 5, 11, 12, 14; §3.5). Counts only; exit 0 when the check holds.

    f80_check.py families --sets-root <root> [--clone <dir>]      the families line the measure will print (item 5)
    f80_check.py clone [--clone <dir>]                             clean, HEAD c00d525f, window 4's pool, gov at the pin
    f80_check.py preflight --sets-root <root>                      the pre-flight ran and every check was as expected
    f80_check.py store [--clone <dir>]                             the clone's store.db sha256
    f80_check.py act --sets-root <root> [--repo <main tree>]       ACT-GUARD-SETS-1 applied (by content; readiness-7 F1)
    f80_check.py declared --sets-root <root> [--repo <main tree>]  the declaration committed, no blank left, its digest
                                                                   the set's now and the pre-flight's (readiness-7 F6,
                                                                   F12)
    f80_check.py live [--clone <dir>] [--gov <exe>] [--log <file>] the live reranker READY from the pin, and a probe
                                                                   search answered by it (code review R1)
    f80_check.py control <control folder>                          the visible 40 at E0's 34 within 2, the families
                                                                   line, every kept search answered as declared
    f80_check.py attempt --sets-root <root> <attempt name>         an attempt whole: the families line, 80 question
                                                                   lines, the total line, every call kept, and every
                                                                   kept search answered as declared (code review F1)
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import f80lib as L  # noqa: E402

LINE = re.compile(r"(\S+) \((visible|hidden)\): hit@5 (yes|no) \(first gold rank (\d+|-)\), in the bundle (yes|no); "
                  r"full evidence (yes|no) \((\d+) of (\d+) pieces\); (\d+) calls?")
DECLARATION = "governance/project/orchestration/packages/LIFT-1/FRESH-80-DECLARATION.md"
LIVE_LOG = Path.home() / ".cache/gov-os/rerank.log"
PROBE = "what decides a close"


def parse(measure_txt: Path) -> dict:
    lines = Path(measure_txt).read_text().splitlines()
    qs = [m for m in map(LINE.match, lines) if m]
    total = [x for x in lines if x.startswith("total: hit@5 ")]
    return {"first": lines[0] if lines else "", "questions": qs, "total": total,
            "unresolved": sum(1 for x in lines if " unresolved: " in x)}


def kept_answers(kept: Path) -> dict:
    """Every kept search, how it was answered (code review F1): rerank.by counts, degraded ones by kind."""
    files = sorted(kept.glob("[0-9]*.json")) if kept.is_dir() else []
    by, bad = Counter(), Counter()
    for f in files:
        try:
            result = json.loads(f.read_text()).get("result")
        except (ValueError, OSError, AttributeError):
            result = None
        why = L.degraded(result)
        by[str(L.rerank_by(result))] += 1
        if why:
            bad[why] += 1
    return {"files": len(files), "by": dict(by), "degraded": sum(bad.values()), "kinds": dict(bad)}


def answered_line(name, k) -> str:
    by = ", ".join(f"{b} {n}" for b, n in sorted(k["by"].items()))
    kinds = ", ".join(f"{w} {n}" for w, n in sorted(k["kinds"].items())) or "none"
    return f"{name}: searches by rerank.by: {by}; answered otherwise than declared: {k['degraded']} ({kinds})"


def families(a):
    from preflight import families_line
    line = families_line(L.paths(a.sets_root), Path(a.clone).resolve())
    L.say(f"the families line the measure will print: {line} (as required: {'yes' if line == L.FAMILIES else 'no'})")
    return line == L.FAMILIES


def clone(a):
    from preflight import item12
    ok, _ = item12(Path(a.clone).resolve())
    return ok


def preflight(a):
    try:
        d = json.loads(L.paths(a.sets_root)["preflight"].read_text())
    except (OSError, ValueError):
        L.say("the pre-flight has not run (no preflight.json)")
        return False
    L.say(f"the pre-flight of {d.get('at')}: every check as expected: {'yes' if d.get('all_ok') else 'no'}")
    return bool(d.get("all_ok"))


def store(a):
    f = Path(a.clone) / ".gov-runtime/store.db"
    print(hashlib.sha256(f.read_bytes()).hexdigest() if f.is_file() else "none")
    return f.is_file()


def act(a):
    ok, why = L.act_applied(a.sets_root, Path(a.repo))
    L.say(f"ACT-GUARD-SETS-1 applied: {'yes' if ok else 'no'} ({why})")
    return ok


def declared(a):
    """The declaration committed with no blank, its digest the set's now and the pre-flight's."""
    repo, rel = Path(a.repo), DECLARATION
    f = repo / rel
    tracked = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch", rel], capture_output=True).returncode == 0
    clean = tracked and subprocess.run(["git", "-C", str(repo), "diff", "--quiet", "HEAD", "--", rel],
                                       capture_output=True).returncode == 0
    try:
        text = f.read_text()
    except OSError:
        text = ""
    blanks = text.count("____")
    line = next((x for x in text.splitlines() if "Its digest" in x), "")
    m = re.search(r"\b[0-9a-f]{64}\b", line)
    wrote = m.group(0) if m else None
    now = L.set_digest(a.sets_root)
    try:
        pre = (json.loads(L.paths(a.sets_root)["preflight"].read_text()).get("item1") or {}).get("sha256")
    except (OSError, ValueError):
        pre = None
    ok = tracked and clean and blanks == 0 and wrote == now == pre
    L.say(f"the declaration: committed {'yes' if tracked and clean else 'no'}; blanks left {blanks}; its digest is the "
          f"set's now {'yes' if wrote == now else 'no'} and the pre-flight's {'yes' if now == pre else 'no'}")
    return ok


def _cmdline(pid: str) -> str:
    try:
        return Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return ""


def live(a):
    """The live reranker READY from the pin (its last READY line's pid alive, running the pin's rerank_service.py),
    and one probe search on the clone answered by the shared service with every route (code review R1)."""
    try:
        ready = [x for x in Path(a.log).read_text(errors="replace").splitlines() if "\tREADY\t" in x]
    except OSError:
        ready = []
    m = re.search(r"pid (\d+)", ready[-1]) if ready else None
    cmd = _cmdline(m.group(1)) if m else ""
    up = bool(cmd) and "gov/retrieval/rerank_service.py" in cmd and "pin-bcea09060ebc" in cmd
    env = {k: v for k, v in os.environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "PYTHONPATH")}
    env["GOV_ROLE"] = "orchestrator"
    p = subprocess.run([a.gov, "retrieve", PROBE, "--json"], capture_output=True, text=True, cwd=a.clone, env=env)
    try:
        result = json.loads(p.stdout)["result"]
    except (ValueError, KeyError, TypeError):
        result = None
    why = L.degraded(result) if p.returncode == 0 else f"exit {p.returncode}"
    L.say(f"the live reranker READY from the pin: {'yes' if up else 'no'}; a probe search answered as declared: "
          f"{'yes' if not why else 'no (' + why + ')'}")
    return up and not why


def control(a):
    d = parse(Path(a.folder) / "measure.txt")
    k = kept_answers(Path(a.folder) / "kept")
    hit = sum(1 for m in d["questions"] if m[3] == "yes")
    n = len(d["questions"])
    fam = d["first"] == L.FAMILIES
    in_range = n == 40 and abs(hit - L.CONTROL_WANT) <= L.CONTROL_SPREAD and bool(d["total"])
    ok = fam and in_range and k["degraded"] == 0 and k["files"] > 0
    L.say(f"control: the families line as required: {'yes' if fam else 'no'}; visible questions {n}; hit@5 {hit} "
          f"(E0's {L.CONTROL_WANT} within {L.CONTROL_SPREAD}: {'yes' if in_range else 'no'})")
    L.say(answered_line("control", k))
    return ok


def attempt(a):
    L.guard_root(a.sets_root)
    run = L.paths(a.sets_root)["runs"] / a.name
    d = parse(run / "measure.txt")
    k = kept_answers(run / "kept")
    calls = sum(int(m[9]) for m in d["questions"])
    fam = d["first"] == L.FAMILIES
    hidden = all(m[2] == "hidden" for m in d["questions"])
    ok = (fam and len(d["questions"]) == 80 and hidden and bool(d["total"]) and k["files"] == calls
          and k["degraded"] == 0)
    L.say(f"{a.name}: the families line as required: {'yes' if fam else 'no'}; question lines {len(d['questions'])} "
          f"(80 expected); total line {'yes' if d['total'] else 'no'}; calls {calls}; kept outputs {k['files']}; "
          f"unresolved anchors {d['unresolved']}")
    L.say(answered_line(a.name, k))
    L.say(f"{a.name}: whole: {'yes' if ok else 'no'}")
    return ok


def main(argv=None):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("families", "clone", "preflight", "store", "act", "declared", "live"):
        s = sub.add_parser(name)
        if name in ("families", "preflight", "act", "declared"):
            s.add_argument("--sets-root", required=True)
        if name in ("families", "clone", "store", "live"):
            s.add_argument("--clone", default=str(L.CLONE))
        if name in ("act", "declared"):
            s.add_argument("--repo", default=str(L.R))
        if name == "live":
            s.add_argument("--gov", default=L.GOV)
            s.add_argument("--log", default=str(LIVE_LOG))
    s = sub.add_parser("control")
    s.add_argument("folder")
    s = sub.add_parser("attempt")
    s.add_argument("--sets-root", required=True)
    s.add_argument("name", choices=("attempt-1", "attempt-2"))
    a = ap.parse_args(argv)
    if getattr(a, "sets_root", None):
        L.guard_root(a.sets_root)
    return 0 if globals()[a.cmd](a) else 1


if __name__ == "__main__":
    sys.exit(main())
