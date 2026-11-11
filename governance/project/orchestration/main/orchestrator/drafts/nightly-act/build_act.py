#!/usr/bin/env python3
"""Builds ACT-NIGHTLY-RESTART-1's bundle for the operator agent (OPERATOR-AGENT-1's interface), from this folder.
Round 2 (DEC-1133 (4)): the one fix pass on review round 1's findings F1 to F11; the round-1 bundle is kept as
acts/ACT-NIGHTLY-RESTART-1.round1/.

    python3 build_act.py build        acts/ACT-NIGHTLY-RESTART-1/ beside this file: before/crontab/crontab (the live crontab
                                      as it is now), after/crontab/crontab (the two changed lines), list.txt, apply.sh,
                                      manifest.json (its rehearsal entry pending). Refuses when the live crontab is not
                                      shaped as expected, or when the bundle holds a review.md.
    python3 build_act.py rehearse     the ACT's own dry run (part 1: apply.sh on a stub crontab, F1 and F3 cases in a
                                      fixture repository; part 2: the operator's own form, in a clone of the live head with
                                      a planted HOME and a crontab stubbed by a file; part 3: test_nightly_restart.sh on
                                      the wrapper as committed in that clone) into acts/ACT-NIGHTLY-RESTART-1/rehearsal.log.
                                      The log holds nothing that depends on the live head, the date or a pid (F2): a rebuild
                                      with the same inputs gives the same manifest sha.
    python3 build_act.py finalize     rehearsal.log hashed into the manifest; prints the manifest sha
    python3 build_act.py gates        the operator's own code on the bundle, read-only: validate_manifest, the path rule,
                                      act_class.classify; the files as the manifest hashes them
    python3 build_act.py all          build, rehearse, finalize, gates

One touched file: the crontab (the `crontab` row of class-rules.yaml: (b), a control path; the owner's yes).
The wrapper nightly_restart.sh, quiet_check.py and their test are not touched files. The wrapper and quiet_check.py are
committed already (db8576bc0cdd, blobs 5e08e247 and 1b887c11, the copies review round 1 read); wrapper-r2.diff
(files/nightly-r2/) is the fix pass for F8 to F11. The CTO commits wrapper-r2 after round 2's READY and before queuing; the
manifest's checks pin the PATCHED blob ids (git hash-object of files/nightly-r2/) and stay red at any head that does not
hold them: they fail closed.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-NIGHTLY-RESTART-1"
BUNDLE = HERE / "acts" / ACT
R2 = HERE / "files" / "nightly-r2"
NIGHTLY = "governance/project/orchestration/nightly"
PKG = "governance/project/orchestration/packages/" + ACT
TAG = "# DEC-1132 (4), ACT-NIGHTLY-RESTART-1:"
WRAPPER_LINE = "0 4 * * * /usr/bin/bash {dir}/nightly_restart.sh  " + TAG + " the nightly back, in its wrapper (quiet, one run, a memory cap)"
CHECK_LINE = "0 8 * * * bash {path}  " + TAG + " the morning check back (its DEC-1049 stop lifted)"
# the files the CTO commits as wrapper-r2: (name in files/nightly-r2, path in the repository)
R2_FILES = {"nightly_restart.sh": NIGHTLY + "/nightly_restart.sh",
            "quiet_check.py": NIGHTLY + "/quiet_check.py",
            "test_nightly_restart.sh": PKG + "/test_nightly_restart.sh"}
# review round 1 read these two as committed (db8576bc0cdd); round 2 pins the patched ones instead
ROUND1_BLOBS = {"nightly_restart.sh": "5e08e24764f00c2aff895057c31c8093afe1d7ea",
                "quiet_check.py": "1b887c11b49168bb73e2803ff9f5e52af380ad5f"}


def blob(path):
    """git hash-object: the blob id the file will have once committed."""
    r = subprocess.run(["git", "hash-object", str(path)], capture_output=True, text=True, check=True)
    return r.stdout.strip()


def pins():
    return {k: blob(R2 / k) for k in R2_FILES}


def checks():
    p = pins()
    pin = lambda name: {"cmd": f'[ "$(git rev-parse HEAD:{NIGHTLY}/{name})" = {p[name]} ]', "exit": 0, "count": None}
    return [
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
        # the wrapper and its helper are committed code at HEAD (the live head in the live run, the clone's in the dry run) ...
        {"cmd": "git ls-files --error-unmatch " + NIGHTLY + "/nightly_restart.sh " + NIGHTLY + "/quiet_check.py", "exit": 0, "count": None},
        {"cmd": "git diff --quiet HEAD -- " + NIGHTLY, "exit": 0, "count": None},
        {"cmd": "bash -n " + NIGHTLY + "/nightly_restart.sh", "exit": 0, "count": None},
        # ... and are the reviewed bytes (F3): the patched blobs of wrapper-r2
        pin("nightly_restart.sh"),
        pin("quiet_check.py"),
    ]


APPLY = r'''#!/bin/bash
# ACT-NIGHTLY-RESTART-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256).
# The one listed file is the crontab (root "crontab", path "crontab"): its bytes are `crontab -l`'s. The frozen copies are
# in this script's own folder (before/crontab/crontab, after/crontab/crontab); each is hashed against list.txt before it is
# installed with `crontab <file>`. Nothing but the crontab is touched.
#   check   the live crontab is the "before" (exit 3 "moved: crontab" otherwise)
#   apply   the "after" crontab installed; only over the "before" (or when it is already the "after": nothing to do);
#           over anything else exit 3 and nothing is touched (review round 1, F1)
#   undo    the "before" crontab put back; only over the "after" (or when it is already the "before"); otherwise exit 3
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
      if [ "$step" = apply ]; then want=$after; other=$before; src="$B/after/crontab/crontab"; else want=$before; other=$after; src="$B/before/crontab/crontab"; fi
      now="$(live)"
      [ "$now" = "$want" ] && { echo "already in place: crontab ($step)"; continue; }
      [ "$now" = "$other" ] || { echo "moved: crontab (neither the before nor the after; $step refused, nothing touched)" >&2; exit 3; }
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
         "files": files, "checks": checks(), "commands": []}
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


def git(cwd, *a, check=False):
    return subprocess.run(["git", "-C", str(cwd), "-c", "user.name=rehearsal", "-c", "user.email=r@r", *a],
                          capture_output=True, text=True, check=check)


def tree_state(root, skip=(".git",)):
    """path -> sha256 of every file under root (a quiet comparison of two moments)."""
    out = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in skip]
        for f in fn:
            p = os.path.join(dp, f)
            try:
                out[os.path.relpath(p, root)] = sha(p) if not os.path.islink(p) else "link"
            except OSError:
                out[os.path.relpath(p, root)] = "unreadable"
    return out


class Log:
    def __init__(self):
        self.lines, self.fails, self.n = [], 0, 0

    def case(self, ok, text):
        self.n += 1
        self.fails += 0 if ok else 1
        self.lines.append(("ok " if ok else "FAIL ") + f"{self.n}: {text}")

    def note(self, text):
        self.lines.append("# " + text)


def simulate_commit(clone):
    """The CTO's commit of wrapper-r2, in the clone only: the patched files over the clone's, committed, when the clone's
    HEAD does not hold them already (at a head that does, nothing is done and nothing differs)."""
    changed = []
    for name, rel in R2_FILES.items():
        dst = clone / rel
        if not dst.exists() or blob(dst) != blob(R2 / name):
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(R2 / name, dst)
            dst.chmod(0o755 if name.endswith(".sh") else 0o644)
            changed.append(rel)
    if changed:
        git(clone, "add", "--", *changed, check=True)
        git(clone, "commit", "-q", "-m", "wrapper-r2 (rehearsal clone only)", check=True)
    return changed


def rehearse():
    m = json.loads((BUNDLE / "manifest.json").read_text())
    L = Log()
    tmp = Path(tempfile.mkdtemp(dir=HERE / "tmp"))
    try:
        stubdir = tmp / "bin"
        stubdir.mkdir()
        (stubdir / "crontab").write_text(STUB)
        (stubdir / "crontab").chmod(0o755)
        before_b = (BUNDLE / "before/crontab/crontab").read_bytes()
        after_b = (BUNDLE / "after/crontab/crontab").read_bytes()
        apply_sh = str(BUNDLE / "apply.sh")

        # ------------------------------------------------------------------------------------------ part 1
        cronf = tmp / "crontab.txt"
        cronf.write_bytes(before_b)
        env = dict(os.environ, OPERATOR_CRONTAB_FILE=str(cronf), PATH=f"{stubdir}:{os.environ['PATH']}")
        run = lambda *a, **k: subprocess.run(list(a), env=env, capture_output=True, text=True, **k)
        ap = lambda step, sh=apply_sh: run("bash", sh, step)
        L.note("part 1: apply.sh on a stub crontab (a file) seeded with the live bytes at the build")
        L.case(ap("check").returncode == 0, "apply.sh check: the stub crontab is the before")
        L.case(ap("verify").returncode == 3, "apply.sh verify before the apply: exit 3 'not applied'")
        L.case(ap("undo").returncode == 0 and cronf.read_bytes() == before_b, "F1: apply.sh undo when the crontab is already the before: exit 0, nothing touched")
        L.case(ap("apply").returncode == 0, "apply.sh apply: the after crontab installed")
        L.case(cronf.read_bytes() == after_b, "the stub crontab is the after, byte for byte")
        L.case(ap("verify").returncode == 0, "apply.sh verify after the apply: exit 0")
        L.case(ap("apply").returncode == 0 and cronf.read_bytes() == after_b, "F1: apply.sh apply when the crontab is already the after: exit 0, nothing touched")
        for c in m["checks"]:
            if c["cmd"].startswith(("git ", "bash -n", "[ ")):
                continue
            r = run("bash", "-c", c["cmd"])
            out = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            good = r.returncode == c["exit"] and (c["count"] is None or (out and int(out[-1]) == c["count"]))
            L.case(bool(good), f"check (exit {c['exit']}, count {c['count']}): {c['cmd'][:90]}")
        # F1: undo over a crontab that moved after the apply is refused, and nothing is touched
        moved_after = after_b + b"# moved\n"
        cronf.write_bytes(moved_after)
        r = ap("undo")
        L.case(r.returncode == 3 and cronf.read_bytes() == moved_after, "F1: apply.sh undo over a crontab that is neither the after nor the before: exit 3, nothing touched")
        cronf.write_bytes(after_b)
        L.case(ap("undo").returncode == 0, "apply.sh undo")
        L.case(cronf.read_bytes() == before_b, "the undo restored the stub crontab byte for byte")
        L.case(ap("check").returncode == 0, "apply.sh check after the undo: the before again")
        # F1: a crontab that moved between check and apply: apply refused, nothing touched
        moved_before = before_b + b"# moved\n"
        cronf.write_bytes(moved_before)
        L.case(ap("check").returncode == 3, "a crontab that moved since the build: check exits 3")
        r = ap("apply")
        L.case(r.returncode == 3 and cronf.read_bytes() == moved_before, "F1: apply.sh apply over a crontab that is neither the before nor the after: exit 3, nothing touched (the added line stays)")
        # a tampered frozen copy is refused
        cronf.write_bytes(before_b)
        tampered = tmp / "t"
        shutil.copytree(BUNDLE, tampered)
        (tampered / "after/crontab/crontab").write_text("x\n")
        L.case(ap("apply", str(tampered / "apply.sh")).returncode == 4 and cronf.read_bytes() == before_b, "a frozen copy that does not hash as listed: apply exits 4, nothing touched")

        # the "committed code" checks (and the F3 blob pins), in a fixture repository holding wrapper-r2 as committed
        fix = tmp / "fix"
        for name, rel in R2_FILES.items():
            (fix / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(R2 / name, fix / rel)
        git(fix, "init", "-q", "-b", "w2/integrate", check=True)
        git(fix, "add", "-A", check=True)
        git(fix, "commit", "-q", "-m", "plant", check=True)
        gitchecks = [c for c in m["checks"] if c["cmd"].startswith(("git ", "bash -n", "[ "))]
        for c in gitchecks:
            r = subprocess.run(["bash", "-c", c["cmd"]], cwd=fix, capture_output=True, text=True)
            L.case(r.returncode == c["exit"], f"wrapper-r2 committed in a fixture repo (exit {c['exit']}): {c['cmd'][:96]}")
        wr = fix / NIGHTLY / "nightly_restart.sh"
        wr.write_text(wr.read_text() + "# changed\n")
        r = subprocess.run(["bash", "-c", "git diff --quiet HEAD -- " + NIGHTLY], cwd=fix)
        L.case(r.returncode == 1, "a changed, uncommitted file under nightly/: `git diff --quiet HEAD` exits 1 (the ACT would not apply)")
        git(fix, "add", "-A")
        git(fix, "commit", "-q", "-m", "a different wrapper")
        pin_checks = [c for c in gitchecks if c["cmd"].startswith("[ ")]
        reds = [subprocess.run(["bash", "-c", c["cmd"]], cwd=fix, capture_output=True).returncode for c in pin_checks]
        L.case(len(pin_checks) == 2 and reds[0] != 0 and reds[1] == 0,
               "F3: a wrapper committed with other bytes than the pinned blob: its pin check fails, the other pin still holds")
        (fix / NIGHTLY / "extra.sh").write_text("x\n")
        r = subprocess.run(["bash", "-c", "git ls-files --error-unmatch " + NIGHTLY + "/extra.sh"], cwd=fix, capture_output=True)
        L.case(r.returncode != 0, "a file that is not committed: `git ls-files --error-unmatch` exits non-zero")

        # ------------------------------------------------------------------------------------------ part 2
        # the operator's own form (operator_run.py _g8): a clone of the live head, HOME planted, the crontab stubbed by a
        # file seeded with the live crontab's bytes, apply.sh check / apply / the manifest's checks in the clone / undo,
        # the changed set equal to the touched list, the undo byte for byte. The one thing added: the CTO's commit of
        # wrapper-r2 is simulated in the clone when the live head does not hold it yet (so the pins can be green).
        L.note("part 2: the operator's dry run in a clone of the live head (planted HOME, crontab stubbed by a file)")
        clone, home = tmp / "clone", tmp / "home"
        home.mkdir()
        for args in (["git", "clone", "-q", "--no-checkout", str(REPO), str(clone)],):
            subprocess.run(args, check=True, capture_output=True)
        head = subprocess.run(["git", "-C", str(REPO), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
        git(clone, "checkout", "-q", "--detach", head, check=True)
        held = all(subprocess.run(["git", "-C", str(clone), "rev-parse", f"HEAD:{rel}"], capture_output=True, text=True).stdout.strip() == blob(R2 / name)
                   for name, rel in R2_FILES.items())
        print(f"# live head {head[:12]}: wrapper-r2 {'is' if held else 'is not'} committed there (not in the log: F2)")
        # the checks that are red at this head, run as they stand (printed here, not logged: they depend on the live head)
        red_now = [c["cmd"][:60] for c in gitchecks
                   if subprocess.run(["bash", "-c", c["cmd"]], cwd=clone, capture_output=True).returncode != 0]
        print(f"# at the live head, the git checks that are red: {len(red_now)} of {len(gitchecks)}")
        simulate_commit(clone)
        real_cron = subprocess.run(["crontab", "-l"], capture_output=True).stdout
        cron2 = tmp / "crontab2.txt"
        cron2.write_bytes(real_cron)
        env2 = {"PATH": f"{stubdir}:{os.environ['PATH']}", "HOME": str(home), "LANG": "C.UTF-8",
                "OPERATOR_CRONTAB_FILE": str(cron2), "PYTHONDONTWRITEBYTECODE": "1"}
        run2 = lambda *a, **k: subprocess.run(list(a), env=env2, capture_output=True, text=True, **k)
        t0, h0 = tree_state(clone), tree_state(home)
        L.case(real_cron == before_b, "the crontab seeded from the live one is the bundle's before, byte for byte")
        L.case(run2("bash", apply_sh, "check").returncode == 0, "apply.sh check in the clone's environment: exit 0")
        L.case(run2("bash", apply_sh, "apply").returncode == 0, "apply.sh apply in the clone's environment: exit 0")
        L.case(cron2.read_bytes() == after_b, "the planted crontab is the bundle's after, byte for byte")
        L.case(tree_state(clone) == t0 and tree_state(home) == h0, "the apply changed nothing in the clone or the planted HOME (only the crontab file)")
        for c in m["checks"]:
            r = subprocess.run(["bash", "-c", c["cmd"]], cwd=clone, env=env2, capture_output=True, text=True)
            out = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            good = r.returncode == c["exit"] and (c["count"] is None or (out and int(out[-1]) == c["count"]))
            L.case(bool(good), f"the manifest's check, run in the clone (exit {c['exit']}, count {c['count']}): {c['cmd'][:80]}")
        L.case(run2("bash", apply_sh, "verify").returncode == 0, "apply.sh verify in the clone's environment: exit 0")
        L.case(run2("bash", apply_sh, "undo").returncode == 0, "apply.sh undo in the clone's environment: exit 0")
        L.case(cron2.read_bytes() == before_b and tree_state(clone) == t0 and tree_state(home) == h0,
               "the undo restored the planted crontab byte for byte; the clone and the planted HOME are as they were")
        L.case(git(clone, "status", "--porcelain").stdout.strip() == "", "the clone's tree is clean after the whole dry run")

        # ------------------------------------------------------------------------------------------ part 3
        # F5: the wrapper's own cases, re-run on the wrapper as committed in that clone (the folder nightly/, with the test
        # beside the ACT in packages/), under a real `systemd-run --user --scope` (a stub run command, small caps)
        L.note("part 3: test_nightly_restart.sh on the wrapper as committed in the clone (nightly/); the memory cases run a real `systemd-run --user --scope`")
        L.note("the files tested (git blob ids): " + ", ".join(f"{name} {blob(clone / rel)[:12]}" for name, rel in R2_FILES.items()))
        test = clone / R2_FILES["test_nightly_restart.sh"]
        envt = dict(os.environ, TMPDIR=str(tmp))
        r = subprocess.run(["bash", str(test), str(clone / NIGHTLY)], env=envt, capture_output=True, text=True, timeout=600)
        body = [l for l in r.stdout.splitlines() if l.startswith(("ok ", "FAIL "))]
        wl = {l.split(":")[0]: int(l.split(":")[1]) for l in r.stdout.splitlines() if l.startswith(("cases:", "failures:"))}
        print(f"# the wrapper's cases: {wl.get('cases')} cases, {wl.get('failures')} failures, exit {r.returncode}")
        if "failures" not in wl or r.returncode not in (0, 1):
            L.fails += 1
            body.append("FAIL: the wrapper's cases did not finish: " + (r.stderr or r.stdout)[-200:])
        part3 = body
        wfail, wcases = wl.get("failures", 1), wl.get("cases", 0)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # assemble: parts 1 and 2 (numbered together), then part 3 (its own numbering, as the test prints it)
    head = ["# ACT-NIGHTLY-RESTART-1 rehearsal (round 2). Parts 1 and 2: the ACT's own dry run; part 3: the wrapper's cases."]
    text = head + L.lines + part3
    text += [f"cases: {L.n + wcases}", f"failures: {L.fails + wfail}"]
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


def all_():
    build()
    rehearse()
    finalize()
    gates()


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates, "all": all_}[sys.argv[1]]()
