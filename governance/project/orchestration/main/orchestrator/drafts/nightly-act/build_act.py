#!/usr/bin/env python3
"""Builds ACT-NIGHTLY-RESTART-1's bundle for the operator agent (OPERATOR-AGENT-1's interface), from this folder.

    python3 build_act.py build        acts/ACT-NIGHTLY-RESTART-1/ beside this file: before/crontab/crontab (the live crontab
                                      as it is now), after/crontab/crontab (the three changes below), list.txt, apply.sh,
                                      manifest.json (its rehearsal entry pending). Refuses when the live crontab is not
                                      shaped as expected.
    python3 build_act.py rehearse     the ACT's own dry run on a stub crontab (check, apply, the manifest's checks, undo
                                      byte for byte) and the wrapper's cases (rehearsal-wrapper.log, from
                                      files/test_nightly_restart.sh) into acts/ACT-NIGHTLY-RESTART-1/rehearsal.log
    python3 build_act.py finalize     rehearsal.log hashed into the manifest; prints the manifest sha
    python3 build_act.py gates        the operator's own code on the bundle, read-only: validate_manifest, the path rule,
                                      act_class.classify; the files as the manifest hashes them

One touched file: the crontab (the `crontab` row of class-rules.yaml: (b), a control path; the owner's one-line yes).
The wrapper nightly_restart.sh, quiet_check.py and their tests (files/) are not touched files: their folder,
governance/project/orchestration/nightly/, has no row of its own, so it falls to the catch-all (O) with no control flag,
"not an ACT's business": the CTO commits them in the ordinary way BEFORE the ACT, and the manifest's checks refuse to
apply while they are not committed (`git ls-files --error-unmatch`, `git diff --quiet HEAD`).
The bundle is built here, in drafts/; the CTO copies acts/ACT-NIGHTLY-RESTART-1/ to .gov-runtime/scratch/orchestrator/acts/
(the manifest does not name its own place). The CTO rebuilds it at the moment it queues the ACT (the crontab may have moved).
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-NIGHTLY-RESTART-1"
BUNDLE = HERE / "acts" / ACT
NIGHTLY = "governance/project/orchestration/nightly"
TAG = "# DEC-1132 (4), ACT-NIGHTLY-RESTART-1:"
WRAPPER_LINE = "0 4 * * * /usr/bin/bash {dir}/nightly_restart.sh  " + TAG + " the nightly back, in its wrapper (quiet, one run, a memory cap)"
CHECK_LINE = "0 8 * * * bash {path}  " + TAG + " the morning check back (its DEC-1049 stop lifted)"

CHECKS = [
    # four active lines: the dispatcher's, the operator's, and the two this ACT adds
    {"cmd": "crontab -l | grep -v '^#' | grep -c .", "exit": 0, "count": 4},
    # the wrapper's line, at 04:00, once
    {"cmd": "crontab -l | grep -c '^0 4 \\* \\* \\* /usr/bin/bash .*/nightly/nightly_restart\\.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:'",
     "exit": 0, "count": 1},
    # the old 04:00 line is still there, stopped, so the undo is exact and nothing else is switched on
    {"cmd": "crontab -l | grep -c '^# DEC-1049 stopped: 0 4 \\* \\* \\* bash .*/nightly/nightly_cron\\.sh$'", "exit": 0, "count": 1},
    {"cmd": "crontab -l | grep -c '^0 8 \\* \\* \\* bash .*/nightly/nightly_check\\.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:'",
     "exit": 0, "count": 1},
    # what stays stopped: the @reboot check and the 09:30 sweep
    {"cmd": "crontab -l | grep -c '^# DEC-1049 stopped: @reboot sleep 300 && bash .*/nightly/nightly_check\\.sh$'", "exit": 0, "count": 1},
    {"cmd": "crontab -l | grep -c '^# DEC-1050 stopped: 30 9 \\* \\* \\* bash .*/nightly/runs_sweep\\.sh$'", "exit": 0, "count": 1},
    # what stays as it is: the dispatcher's every-minute line and the operator's launcher line
    {"cmd": "crontab -l | grep -c '^\\* \\* \\* \\* \\* /usr/bin/bash .*/dispatch/run_tick\\.sh$'", "exit": 0, "count": 1},
    {"cmd": "crontab -l | grep -c 'operator_launch\\.py'", "exit": 0, "count": 1},
    # the wrapper and its helper are committed code at HEAD (the live head in the live run, the clone's in the dry run)
    {"cmd": "git ls-files --error-unmatch " + NIGHTLY + "/nightly_restart.sh " + NIGHTLY + "/quiet_check.py", "exit": 0, "count": None},
    {"cmd": "git diff --quiet HEAD -- " + NIGHTLY, "exit": 0, "count": None},
    {"cmd": "bash -n " + NIGHTLY + "/nightly_restart.sh", "exit": 0, "count": None},
]

APPLY = r'''#!/bin/bash
# ACT-NIGHTLY-RESTART-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256).
# The one listed file is the crontab (root "crontab", path "crontab"): its bytes are `crontab -l`'s. The frozen copies are
# in this script's own folder (before/crontab/crontab, after/crontab/crontab); each is hashed against list.txt before it is
# installed with `crontab <file>`. Nothing but the crontab is touched.
#   check   the live crontab is the "before" (exit 3 "moved: crontab" otherwise)
#   apply   the "after" crontab installed       undo   the "before" crontab put back
#   verify  the live crontab is the "after" (exit 3 "not applied: crontab" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
live() { local t; t="$(mktemp)" || exit 5; if crontab -l > "$t" 2>/dev/null; then sha256sum "$t" | cut -c1-64; else echo null; fi; rm -f "$t"; }
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  [ "$root" = crontab ] && [ "$path" = crontab ] || { echo "not the crontab: $root|$path" >&2; exit 9; }
  case "$step" in
    check) [ "$(live)" = "$before" ] || { echo "moved: crontab" >&2; exit 3; } ;;
    verify) [ "$(live)" = "$after" ] || { echo "not applied: crontab" >&2; exit 3; } ;;
    apply|undo)
      if [ "$step" = apply ]; then want=$after; src="$B/after/crontab/crontab"; else want=$before; src="$B/before/crontab/crontab"; fi
      [ "$(h "$src")" = "$want" ] || { echo "the frozen copy does not hash as listed: $src" >&2; exit 4; }
      crontab "$src" || exit 5 ;;
  esac
done < "$B/list.txt"
exit 0
'''


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def live_crontab():
    r = subprocess.run(["crontab", "-l"], capture_output=True)
    if r.returncode != 0:
        sys.exit("no live crontab")
    return r.stdout.decode()


def transform(before: str) -> str:
    lines = before.split("\n")
    out, n_cron, n_check = [], 0, 0
    for ln in lines:
        m = re.fullmatch(r"# DEC-1049 stopped: 0 4 \* \* \* bash (.*)/nightly_cron\.sh", ln)
        c = re.fullmatch(r"# DEC-1049 stopped: 0 8 \* \* \* bash (.*/nightly_check\.sh)", ln)
        if m:
            out.append(ln)
            out.append(WRAPPER_LINE.format(dir=m.group(1)))
            n_cron += 1
        elif c:
            out.append(CHECK_LINE.format(path=c.group(1)))
            n_check += 1
        else:
            out.append(ln)
    if (n_cron, n_check) != (1, 1):
        sys.exit(f"the live crontab is not as expected (the stopped 04:00 line {n_cron} times, the 08:00 line {n_check}): nothing built")
    return "\n".join(out)


def build():
    before = live_crontab()
    after = transform(before)
    if BUNDLE.exists():
        if (BUNDLE / "review.md").exists():
            sys.exit(f"{BUNDLE} holds a review: a rebuild would make it stale; move it aside first")
        shutil.rmtree(BUNDLE)
    for side, data in (("before", before), ("after", after)):
        f = BUNDLE / side / "crontab" / "crontab"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(data)
    b, a = sha(BUNDLE / "before/crontab/crontab"), sha(BUNDLE / "after/crontab/crontab")
    (BUNDLE / "list.txt").write_text(f"crontab|crontab|{b}|{a}\n")
    (BUNDLE / "apply.sh").write_text(APPLY)
    (BUNDLE / "apply.sh").chmod(0o755)
    write_manifest(None)
    print(f"built {BUNDLE}: before {b[:12]}, after {a[:12]}")


def write_manifest(rehearsal_sha):
    files = {"before/crontab/crontab": sha(BUNDLE / "before/crontab/crontab"),
             "after/crontab/crontab": sha(BUNDLE / "after/crontab/crontab"),
             "apply.sh": sha(BUNDLE / "apply.sh"), "list.txt": sha(BUNDLE / "list.txt")}
    m = {"act": ACT, "dec": "DEC-1132, DEC-1049", "author": "cto", "claimed_class": "b",
         "touched": [{"root": "crontab", "path": "crontab", "before": files["before/crontab/crontab"],
                      "after": files["after/crontab/crontab"]}],
         "files": files, "checks": CHECKS, "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


STUB = """#!/bin/bash
f="$OPERATOR_CRONTAB_FILE"
case "${1:-}" in
  -l) [ -f "$f" ] && { cat "$f"; exit 0; }; echo "no crontab for $USER" >&2; exit 1 ;;
  -r) rm -f "$f"; exit 0 ;;
  -|"") cat > "$f"; exit 0 ;;
  -*) echo "crontab stub: $1 not supported" >&2; exit 2 ;;
  *) cat "$1" > "$f"; exit 0 ;;
esac
"""


def rehearse():
    """The operator's dry run in miniature: a stub crontab seeded with the live bytes, apply.sh check, apply, every manifest
    check (in a clone of the live head: the wrapper is only there once the CTO has committed it, so that check is run
    against the working copy of the committed files when HEAD does not hold them yet, and reported as such), undo."""
    m = json.loads((BUNDLE / "manifest.json").read_text())
    lines, fails = [], 0

    def case(ok, text):
        nonlocal fails
        lines.append(("ok " if ok else "FAIL ") + f"{len(lines) + 1 - sum(1 for l in lines if l.startswith('#'))}: {text}")
        fails += 0 if ok else 1

    tmp = Path(tempfile.mkdtemp(dir=HERE / "tmp"))
    try:
        stubdir = tmp / "bin"
        stubdir.mkdir()
        (stubdir / "crontab").write_text(STUB)
        (stubdir / "crontab").chmod(0o755)
        cronf = tmp / "crontab.txt"
        cronf.write_bytes((BUNDLE / "before/crontab/crontab").read_bytes())
        env = dict(os.environ, OPERATOR_CRONTAB_FILE=str(cronf), PATH=f"{stubdir}:{os.environ['PATH']}")
        run = lambda *a, **k: subprocess.run(list(a), env=env, capture_output=True, text=True, **k)
        case(run("bash", str(BUNDLE / "apply.sh"), "check").returncode == 0, "apply.sh check: the stub crontab (the live bytes at build) is the before")
        r = run("bash", str(BUNDLE / "apply.sh"), "verify")
        case(r.returncode == 3, "apply.sh verify before the apply: exit 3 'not applied'")
        case(run("bash", str(BUNDLE / "apply.sh"), "apply").returncode == 0, "apply.sh apply: the after crontab installed")
        case(cronf.read_bytes() == (BUNDLE / "after/crontab/crontab").read_bytes(), "the stub crontab is the after, byte for byte")
        case(run("bash", str(BUNDLE / "apply.sh"), "verify").returncode == 0, "apply.sh verify after the apply: exit 0")
        for c in m["checks"]:
            if c["cmd"].startswith(("git ", "bash -n")):
                continue
            r = run("bash", "-c", c["cmd"])
            out = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            good = r.returncode == c["exit"] and (c["count"] is None or (out and int(out[-1]) == c["count"]))
            case(bool(good), f"check (exit {c['exit']}, count {c['count']}): {c['cmd'][:90]}")
        # the three "committed code" checks, in a fixture repository holding the wrapper and its helper as committed
        fix = tmp / "fix"
        (fix / NIGHTLY).mkdir(parents=True)
        for f in ("nightly_restart.sh", "quiet_check.py"):
            shutil.copy(HERE / "files" / f, fix / NIGHTLY / f)
        g = lambda *a: subprocess.run(["git", "-C", str(fix), "-c", "user.name=t", "-c", "user.email=t@t", *a], capture_output=True, text=True)
        g("init", "-q", "-b", "w2/integrate")
        g("add", "-A")
        g("commit", "-q", "-m", "plant")
        gitchecks = [c for c in m["checks"] if c["cmd"].startswith(("git ", "bash -n"))]
        for c in gitchecks:
            r = subprocess.run(["bash", "-c", c["cmd"]], cwd=fix, capture_output=True, text=True)
            case(r.returncode == c["exit"], f"committed in a fixture repo (exit {c['exit']}): {c['cmd'][:90]}")
        (fix / NIGHTLY / "quiet_check.py").write_text("# changed\n", encoding="utf-8")
        r = subprocess.run(["bash", "-c", "git diff --quiet HEAD -- " + NIGHTLY], cwd=fix)
        case(r.returncode == 1, "a changed, uncommitted file under nightly/: `git diff --quiet HEAD` exits 1 (the ACT would not apply)")
        g("checkout", "-q", "--", NIGHTLY + "/quiet_check.py")
        (fix / NIGHTLY / "extra.sh").write_text("x\n")
        r = subprocess.run(["bash", "-c", "git ls-files --error-unmatch " + NIGHTLY + "/extra.sh"], cwd=fix, capture_output=True)
        case(r.returncode != 0, "a file that is not committed: `git ls-files --error-unmatch` exits non-zero")
        live = [subprocess.run(["bash", "-c", c["cmd"]], cwd=REPO, capture_output=True).returncode for c in gitchecks]
        lines.append("# at the live head today: " + ", ".join("green" if x == 0 else "red" for x in live)
                     + " (the wrapper is committed by the CTO before the ACT is queued; red here is the hold that makes it so)")
        case(run("bash", str(BUNDLE / "apply.sh"), "undo").returncode == 0, "apply.sh undo")
        case(cronf.read_bytes() == (BUNDLE / "before/crontab/crontab").read_bytes(), "the undo restored the stub crontab byte for byte")
        case(run("bash", str(BUNDLE / "apply.sh"), "check").returncode == 0, "apply.sh check after the undo: the before again")
        # a moved crontab is refused
        cronf.write_text(cronf.read_text() + "# moved\n")
        case(run("bash", str(BUNDLE / "apply.sh"), "check").returncode == 3, "a crontab that moved since the build: check exits 3")
        # a tampered frozen copy is refused
        cronf.write_bytes((BUNDLE / "before/crontab/crontab").read_bytes())
        tampered = tmp / "t"
        shutil.copytree(BUNDLE, tampered)
        (tampered / "after/crontab/crontab").write_text("x\n")
        case(run("bash", str(tampered / "apply.sh"), "apply").returncode == 4, "a frozen copy that does not hash as listed: apply exits 4")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    wrapper = HERE / "rehearsal-wrapper.log"
    wl = wrapper.read_text().splitlines() if wrapper.exists() else []
    wfail = next((int(l.split(":")[1]) for l in wl if l.startswith("failures:")), None)
    wcases = next((int(l.split(":")[1]) for l in wl if l.startswith("cases:")), 0)
    if wfail is None:
        fails += 1
    body = [l for l in wl if not l.startswith(("cases:", "failures:"))]
    total = len(lines) + wcases
    text = ["# ACT-NIGHTLY-RESTART-1 rehearsal, part 1: apply.sh on a stub crontab seeded with the live bytes"] + lines + \
           ["# part 2: nightly_restart.sh and quiet_check.py in a planted world (files/test_nightly_restart.sh); every memory case ran under a real `systemd-run --user --scope`"] + body
    text += [f"cases: {total}", f"failures: {fails + (wfail or 0)}"]
    (BUNDLE / "rehearsal.log").write_text("\n".join(text) + "\n")
    print("\n".join(text[-3:]))


def finalize():
    log = BUNDLE / "rehearsal.log"
    if not log.read_text().rstrip().endswith("failures: 0"):
        sys.exit("the rehearsal did not end with failures: 0: not finalized")
    print(f"manifest sha256 {write_manifest(sha(log))}")


def gates():
    sys.path.insert(0, str(REPO / "governance/project/operator"))
    sys.dont_write_bytecode = True
    import act_class  # noqa: E402
    import operator_run as orun  # noqa: E402
    m = json.loads((BUNDLE / "manifest.json").read_text())
    orun.validate_manifest(m)
    print("validate_manifest: pass")
    for rel, want in m["files"].items():
        assert sha(BUNDLE / rel) == want, rel
    print(f"files: {len(m['files'])} hash as the manifest says")
    s = {"repo": str(REPO), "home": str(Path.home())}
    texts = [("apply.sh", (BUNDLE / "apply.sh").read_text())] + [("a check", c["cmd"]) for c in m["checks"]]
    for where, text in texts:
        why = orun.live_path_refs(text, s)
        assert why is None, f"{where}: {why}"
    print("path rule: pass (apply.sh and every check)")
    v = act_class.classify(str(BUNDLE))
    print(f"act_class.classify: class {v['class']}; hits {v['hits']}; why {v['why']}")
    print(f"manifest sha256 {sha(BUNDLE / 'manifest.json')}")


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates}[sys.argv[1]]()
