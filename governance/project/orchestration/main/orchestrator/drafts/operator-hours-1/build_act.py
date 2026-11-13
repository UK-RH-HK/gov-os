#!/usr/bin/env python3
"""Builds ACT-OPERATOR-HOURS-1's bundle (OPERATOR-AGENT-1's interface), rehearses it and prints the manifest sha.

    python3 build_act.py build      acts/ACT-OPERATOR-HOURS-1/: before/crontab/crontab (the live crontab as it is now, read
                                    only), after/crontab/crontab (the operator's line replaced), list.txt, apply.sh,
                                    manifest.json (its rehearsal entry pending). Refuses when the live crontab is not
                                    shaped as expected, or when the bundle holds a review.md.
    python3 build_act.py rehearse   part 1: apply.sh on a stub crontab (a file); part 2: the operator's own form (clean
                                    environment, planted HOME, stub crontab, the manifest's checks); part 3: the guard,
                                    the line exactly as cron will run it, under /bin/sh, with a stub `date`, a planted
                                    state file and a stub operator_launch.py that records its call; part 4: the real
                                    writer (night_hold.py) in a planted folder; part 5: crontab -n on the after file.
                                    Writes acts/ACT-OPERATOR-HOURS-1/rehearsal.log (nothing in it depends on the date, a
                                    pid or the live head: a rebuild from the same inputs gives the same manifest sha).
    python3 build_act.py finalize   rehearsal.log hashed into the manifest; prints the manifest sha256
    python3 build_act.py gates      the operator's own code on the bundle, read only: validate_manifest, the path rule,
                                    act_class.classify, the files as the manifest hashes them
    python3 build_act.py all        build, rehearse, finalize, gates

Round 2 (the last review round, DEC-1010): apply.sh check and apply refuse (exit 7) unless the live install's opcommon.py is
ACT-OPERATOR-HOURS-2's after copy; the guard treats a state file dated more than 60 s in the future as stale (F3) and is
silent when `date` fails (F4).

Never touches the live crontab (only `crontab -l`, and `crontab -n` on files), ~/gov-os-operator, or anything outside
acts/ACT-OPERATOR-HOURS-1/ and this folder.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-OPERATOR-HOURS-1"
BUNDLE = ORCH / "acts" / ACT
OP_ROOT = "/home/usain/gov-os-operator"
H2 = ORCH / "acts" / "ACT-OPERATOR-HOURS-2"           # the companion ACT's bundle (read only)
H2_PATH = "gov-os-operator/install/opcommon.py"
STATE = str(ORCH / "log" / "night-hold.state.json")

OLD_LINE = ("*/10 0,8-23 * * * /usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> "
            "/home/usain/gov-os-operator/log/operator-launch.out 2>&1  # DEC-1104 (2) (5), ACT-OPERATOR-1: the operator "
            "agent launched from its queue (the CTO only queues)")

# The guard, in the line itself (sh, as cron runs it; no `%` but the escaped ones of `date`):
#   h = the local time as HHMM (date failing or printing nothing: every test below errors, nothing launches)
#   launch when h < 02:10 or h >= 08:00 (the state file is not read at those hours), or
#   when h >= 03:10 and the night hold's state file is younger than 300 s (and not dated more than 60 s in the future: F3)
#   and says holding is exactly false; the whole test group's standard error goes to /dev/null (F4: `date` failing or
#   printing garbage makes `[` complain; nothing is printed, nothing launches)
#   (a missing, empty or malformed file, a missing key, a string "false", null, 0: python raises or exits 1: no launch)
GUARD = ('h=$(date +\\%H\\%M 2>/dev/null); { [ "$h" -lt 0210 ] || [ "$h" -ge 0800 ] || { [ "$h" -ge 0310 ] && /usr/bin/python3 -I -c '
         "'import json,os,sys,time;s=sys.argv[1];a=time.time()-os.stat(s).st_mtime;sys.exit(0 if -60<=a<300 and "
         'json.load(open(s))["holding"] is False else 1)\' ' + STATE + "; }; } 2>/dev/null && ")
LAUNCH = ("/usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> "
          "/home/usain/gov-os-operator/log/operator-launch.out 2>&1")
COMMENT = ("  # DEC-1141 (6), ACT-OPERATOR-HOURS-1 (was DEC-1104 (2) (5), ACT-OPERATOR-1): the operator agent launched from its "
           "queue every 10 minutes at every hour, except no launch from 02:10 and, from 03:10, none unless the night hold state file "
           "(under 5 minutes old) says holding false; missing or unreadable means none; needs ACT-OPERATOR-HOURS-2 first")
NEW_LINE = "*/10 * * * * " + GUARD + LAUNCH + COMMENT


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def live_crontab():
    r = subprocess.run(["crontab", "-l"], capture_output=True)
    if r.returncode != 0:
        sys.exit("no live crontab")
    return r.stdout.decode()


def transform(before):
    out, n = [], 0
    for ln in before.split("\n"):
        if ln == OLD_LINE:
            out.append(NEW_LINE)
            n += 1
        else:
            out.append(ln)
    if n != 1:
        sys.exit(f"the live crontab does not hold the operator's old line exactly once ({n}): nothing built")
    return "\n".join(out)


def checks():
    return [
        # four active lines before and after: the dispatcher's, the nightly's two, the operator's
        {"cmd": "crontab -l | grep -v '^#' | grep -c .", "exit": 0, "count": 4},
        # the new line, once: every 10 minutes at every hour, the guard's date call, the launcher, the ACT's tag
        {"cmd": "crontab -l | grep -c '^\\*/10 \\* \\* \\* \\* h=\\$(date +\\\\%H\\\\%M 2>/dev/null); .*operator_launch\\.py .*# DEC-1141 (6), ACT-OPERATOR-HOURS-1 '",
         "exit": 0, "count": 1},
        # the old schedule is gone
        {"cmd": "crontab -l | grep -c '^\\*/10 0,8-23 '", "exit": 1, "count": 0},
        {"cmd": "crontab -l | grep -c 'operator_launch\\.py'", "exit": 0, "count": 1},
        # the guard reads the night hold's state file, and nothing else
        {"cmd": "crontab -l | grep -c 'night-hold\\.state\\.json'", "exit": 0, "count": 1},
        # what stays as it is
        {"cmd": "crontab -l | grep -c '^0 4 \\* \\* \\* /usr/bin/bash .*/nightly/nightly_restart\\.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:'",
         "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^0 8 \\* \\* \\* bash .*/nightly/nightly_check\\.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:'",
         "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^\\* \\* \\* \\* \\* /usr/bin/bash .*/dispatch/run_tick\\.sh$'", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^# DEC-1049 stopped: 0 4 \\* \\* \\* bash .*/nightly/nightly_cron\\.sh$'", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^# DEC-1049 stopped: @reboot sleep 300 && bash .*/nightly/nightly_check\\.sh$'", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^# DEC-1050 stopped: 30 9 \\* \\* \\* bash .*/nightly/runs_sweep\\.sh$'", "exit": 0, "count": 1},
    ]


APPLY = r'''#!/bin/bash
# ACT-OPERATOR-HOURS-1's apply.sh: check | apply | undo | verify, by list.txt (root|path|before sha256|after sha256).
# The one listed file is the crontab (root "crontab", path "crontab"): its bytes are `crontab -l`'s. The frozen copies are
# in this script's own folder (before/crontab/crontab, after/crontab/crontab); each is hashed against list.txt before it is
# installed with `crontab <file>` (which refuses a file it cannot parse and leaves the old table). Nothing but the crontab
# is touched.
#   check   the install's opcommon.py is ACT-OPERATOR-HOURS-2's after copy (exit 7 otherwise); the live crontab is the "before"
#           (exit 3 "moved: crontab" otherwise)
#   apply   the same gate first (exit 7, nothing touched); then the "after" crontab installed; only over the "before" (or when it is already the "after": nothing to do);
#           over anything else exit 3 and nothing is touched
#   undo    the "before" crontab put back; only over the "after" (or when it is already the "before"); otherwise exit 3
#   verify  the live crontab is the "after" (exit 3 "not applied: crontab" otherwise)
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
h() { if [ -f "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
# The gate (round 2): this ACT's crontab guard and the launcher's own G9 must agree, so check and apply refuse (exit 7) until the
# install's opcommon.py is ACT-OPERATOR-HOURS-2's after copy (its list.txt, the home row of gov-os-operator/install/opcommon.py).
# undo and verify never need it (an undo must always work).
HOURS2_AFTER=@HOURS2@
OPC="$HOME/@H2PATH@"
case "$step" in check|apply)
  if [ -L "$OPC" ] || [ ! -f "$OPC" ] || [ "$(h "$OPC")" != "$HOURS2_AFTER" ]; then
    echo "ACT-OPERATOR-HOURS-2 is not applied: the install's opcommon.py is not its after copy (${HOURS2_AFTER:0:12}); apply it first; $step refused, nothing touched" >&2
    exit 7
  fi ;;
esac
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


def hours2_after_sha():
    """The full sha256 of ACT-OPERATOR-HOURS-2's after opcommon.py, read from its list.txt and checked against its frozen copy."""
    rows = [l.split("|") for l in (H2 / "list.txt").read_text().splitlines() if l.strip()]
    got = {r[0] + "|" + r[1]: r[3] for r in rows}
    want = got["home|" + H2_PATH]
    assert sha(H2 / "after/home" / H2_PATH) == want, "ACT-OPERATOR-HOURS-2's frozen after copy does not hash as its list.txt says"
    return want


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
    (BUNDLE / "apply.sh").write_text(APPLY.replace("@HOURS2@", hours2_after_sha()).replace("@H2PATH@", H2_PATH))
    (BUNDLE / "apply.sh").chmod(0o755)
    write_manifest(None)
    print(f"built {BUNDLE}: before {b[:12]}, after {a[:12]}")


def write_manifest(rehearsal_sha):
    files = {"before/crontab/crontab": sha(BUNDLE / "before/crontab/crontab"),
             "after/crontab/crontab": sha(BUNDLE / "after/crontab/crontab"),
             "apply.sh": sha(BUNDLE / "apply.sh"), "list.txt": sha(BUNDLE / "list.txt")}
    m = {"act": ACT, "dec": "DEC-1141, DEC-1104, DEC-1138", "author": "cto", "claimed_class": "b",
         "touched": [{"root": "crontab", "path": "crontab", "before": files["before/crontab/crontab"],
                      "after": files["after/crontab/crontab"]}],
         "files": files, "checks": checks(), "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


STUB_CRONTAB = """#!/bin/bash
f="$OPERATOR_CRONTAB_FILE"
case "${1:-}" in
  -l) [ -f "$f" ] && { cat "$f"; exit 0; }; echo "no crontab for $USER" >&2; exit 1 ;;
  -r) rm -f "$f"; exit 0 ;;
  -|"") cat > "$f"; exit 0 ;;
  -*) echo "crontab stub: $1 not supported" >&2; exit 2 ;;
  *) cat "$1" > "$f"; exit 0 ;;
esac
"""
# `date +%H%M` as the test says: FAKE_HM; FAKE_DATE_FAIL=1: date fails (a message on standard error, exit 1, no output);
# FAKE_DATE_RAW=1: FAKE_HM is printed as it is (garbage, or empty). Anything else: the real date.
STUB_DATE = """#!/bin/sh
[ -n "${FAKE_DATE_FAIL:-}" ] && { echo "date: stub failure" >&2; exit 1; }
[ -n "${FAKE_DATE_RAW:-}" ] && { echo "$FAKE_HM"; exit 0; }
if [ "$1" = "+%H%M" ] && [ -n "${FAKE_HM:-}" ]; then echo "$FAKE_HM"; exit 0; fi
exec /usr/bin/date "$@"
"""
# the stub launcher: records its argv and its stdin-less call, prints one JSON line as the real one does
STUB_LAUNCH = """import json, os, sys
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "calls.jsonl"), "a") as f:
    f.write(json.dumps({"argv": sys.argv[1:]}) + "\\n")
print(json.dumps({"result": "idle"}))
"""


def tree_state(root):
    out = {}
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            out[os.path.relpath(p, root)] = sha(p) if not os.path.islink(p) else "link"
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


def cron_command(line):
    """What cron hands to /bin/sh for a crontab line: the text after the five time fields, a backslash before % removed;
    an unescaped % would split it (the first one starts standard input): refused here."""
    parts = line.split(None, 5)
    assert len(parts) == 6, "a crontab line has five fields and a command"
    cmd = parts[5]
    assert not re.search(r"(?<!\\)%", cmd), "an unescaped % in the command"
    return " ".join(parts[:5]), cmd.replace("\\%", "%")


def expand_minutes(spec):
    """The ticks of a `*/10`-style minute field: [0, 10, ..., 50]; the hour field `*` means every hour."""
    m = re.fullmatch(r"\*/(\d+)", spec)
    assert m, spec
    return list(range(0, 60, int(m.group(1))))


def rehearse():
    m = json.loads((BUNDLE / "manifest.json").read_text())
    L = Log()
    tmp = Path(tempfile.mkdtemp(dir=HERE / "tmp"))
    live_before = subprocess.run(["crontab", "-l"], capture_output=True).stdout
    try:
        stubdir = tmp / "bin"
        stubdir.mkdir()
        (stubdir / "crontab").write_text(STUB_CRONTAB)
        (stubdir / "crontab").chmod(0o755)
        before_b = (BUNDLE / "before/crontab/crontab").read_bytes()
        after_b = (BUNDLE / "after/crontab/crontab").read_bytes()
        apply_sh = str(BUNDLE / "apply.sh")

        def plant_home(root, kind):
            """A HOME whose gov-os-operator/install/opcommon.py is: ACT-OPERATOR-HOURS-2's after copy, its before copy, absent,
            the after copy with one line added, a link to the after copy, or a directory."""
            root.mkdir(parents=True, exist_ok=True)
            shutil.rmtree(root / "gov-os-operator", ignore_errors=True)
            if kind == "none":
                return
            d = root / "gov-os-operator/install"
            d.mkdir(parents=True)
            f, aft, bef = d / "opcommon.py", H2 / "after/home" / H2_PATH, H2 / "before/home" / H2_PATH
            if kind == "after":
                shutil.copy(aft, f)
            elif kind == "before":
                shutil.copy(bef, f)
            elif kind == "tampered":
                f.write_bytes(aft.read_bytes() + b"# x\n")
            elif kind == "symlink":
                shutil.copy(aft, d / "real.py")
                f.symlink_to(d / "real.py")
            elif kind == "dir":
                f.mkdir()
            else:
                raise ValueError(kind)

        # ------------------------------------------------------------------------------------------ part 1
        cronf = tmp / "crontab.txt"
        cronf.write_bytes(before_b)
        home1 = tmp / "home1"
        plant_home(home1, "after")
        env = dict(os.environ, OPERATOR_CRONTAB_FILE=str(cronf), PATH=f"{stubdir}:{os.environ['PATH']}", HOME=str(home1))
        run = lambda *a, **k: subprocess.run(list(a), env=env, capture_output=True, text=True, **k)
        ap = lambda step, sh=apply_sh: run("bash", sh, step)
        L.note("part 1: apply.sh on a stub crontab (a file) seeded with the live bytes at the build; HOME planted with ACT-OPERATOR-HOURS-2's after opcommon.py")
        L.case(ap("check").returncode == 0, "apply.sh check: the stub crontab is the before")
        L.case(ap("verify").returncode == 3, "apply.sh verify before the apply: exit 3 'not applied'")
        L.case(ap("undo").returncode == 0 and cronf.read_bytes() == before_b, "apply.sh undo when the crontab is already the before: exit 0, nothing touched")
        L.case(ap("apply").returncode == 0, "apply.sh apply: the after crontab installed")
        L.case(cronf.read_bytes() == after_b, "the stub crontab is the after, byte for byte")
        L.case(ap("verify").returncode == 0, "apply.sh verify after the apply: exit 0")
        L.case(ap("apply").returncode == 0 and cronf.read_bytes() == after_b, "apply.sh apply when already the after: exit 0, nothing touched")
        for c in m["checks"]:
            r = run("bash", "-c", c["cmd"])
            out = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            good = r.returncode == c["exit"] and (c["count"] is None or (out and int(out[-1]) == c["count"]))
            L.case(bool(good), f"check (exit {c['exit']}, count {c['count']}): {c['cmd'][:90]}")
        moved_after = after_b + b"# moved\n"
        cronf.write_bytes(moved_after)
        r = ap("undo")
        L.case(r.returncode == 3 and cronf.read_bytes() == moved_after, "apply.sh undo over a crontab that is neither the after nor the before: exit 3, nothing touched")
        cronf.write_bytes(after_b)
        L.case(ap("undo").returncode == 0, "apply.sh undo")
        L.case(cronf.read_bytes() == before_b, "the undo restored the stub crontab byte for byte")
        L.case(ap("check").returncode == 0, "apply.sh check after the undo: the before again")
        moved_before = before_b + b"# moved\n"
        cronf.write_bytes(moved_before)
        L.case(ap("check").returncode == 3, "a crontab that moved since the build: check exits 3")
        r = ap("apply")
        L.case(r.returncode == 3 and cronf.read_bytes() == moved_before, "apply.sh apply over a crontab that is neither the before nor the after: exit 3, nothing touched (the added line stays)")
        cronf.write_bytes(before_b)
        tampered = tmp / "t"
        shutil.copytree(BUNDLE, tampered)
        (tampered / "after/crontab/crontab").write_text("x\n")
        L.case(ap("apply", str(tampered / "apply.sh")).returncode == 4 and cronf.read_bytes() == before_b, "a frozen copy that does not hash as listed: apply exits 4, nothing touched")
        # the diff between the two tables is the one line
        bl, al = before_b.decode().split("\n"), after_b.decode().split("\n")
        changed = [i for i, (x, y) in enumerate(zip(bl, al)) if x != y]
        L.case(len(bl) == len(al) and len(changed) == 1 and bl[changed[0]] == OLD_LINE and al[changed[0]] == NEW_LINE,
               "the before and the after differ in one line only: the operator's, the old line for the new one")

        # the gate (round 2, F1): check and apply refuse, exit 7, unless the install's opcommon.py is ACT-OPERATOR-HOURS-2's after copy
        rows = [l.split("|") for l in (H2 / "list.txt").read_text().splitlines() if l.strip()]
        op_rows = [r for r in rows if r[1].endswith("operator/opcommon.py") or r[1] == H2_PATH]
        gate_sha = hours2_after_sha()
        L.case(len(op_rows) == 2 and all(r[3] == gate_sha for r in op_rows) and gate_sha in Path(apply_sh).read_text() and
               sha(H2 / "after/home" / H2_PATH) == gate_sha,
               "the gate's hash is ACT-OPERATOR-HOURS-2's after opcommon.py (its list.txt, both rows: the install's and the repository's; its frozen copy hashes to it) and is written in apply.sh in full")
        for kind, what in (("none", "absent"), ("before", "ACT-OPERATOR-HOURS-2's before copy (the file as it is live today)"),
                           ("tampered", "its after copy with a line added"), ("symlink", "a link to its after copy"), ("dir", "a directory")):
            plant_home(home1, kind)
            cronf.write_bytes(before_b)
            rc_ = ap("check")
            ra_ = ap("apply")
            L.case(rc_.returncode == 7 and ra_.returncode == 7 and "ACT-OPERATOR-HOURS-2 is not applied" in rc_.stderr and "ACT-OPERATOR-HOURS-2 is not applied" in ra_.stderr
                   and cronf.read_bytes() == before_b,
                   f"the install's opcommon.py is {what}: check and apply exit 7 naming ACT-OPERATOR-HOURS-2, the crontab untouched")
        plant_home(home1, "none")
        cronf.write_bytes(after_b)
        r1_, r2_, r3_ = ap("verify"), ap("apply"), ap("undo")
        L.case(r1_.returncode == 0 and r2_.returncode == 7 and r3_.returncode == 0 and cronf.read_bytes() == before_b,
               "with the install's opcommon.py absent and the crontab already the after: verify exits 0, apply exits 7 (the gate comes first), undo exits 0 and restores the before (an undo never needs the gate)")
        plant_home(home1, "after")
        cronf.write_bytes(before_b)
        L.case(ap("check").returncode == 0 and ap("apply").returncode == 0 and cronf.read_bytes() == after_b and ap("undo").returncode == 0 and cronf.read_bytes() == before_b,
               "with ACT-OPERATOR-HOURS-2's after copy in place: check 0, apply 0 (the after installed), undo 0 (the before back)")
        cronf.write_bytes(before_b)

        # ------------------------------------------------------------------------------------------ part 2
        L.note("part 2: the operator's dry-run form: a clean environment (HOME planted, PATH, LANG), the crontab stubbed by a file, apply.sh run from an empty folder")
        home, cwd = tmp / "home", tmp / "cwd"
        plant_home(home, "after")
        cwd.mkdir()
        cron2 = tmp / "crontab2.txt"
        cron2.write_bytes(live_before)
        env2 = {"PATH": f"{stubdir}:{os.environ['PATH']}", "HOME": str(home), "LANG": "C.UTF-8", "OPERATOR_CRONTAB_FILE": str(cron2)}
        run2 = lambda *a, **k: subprocess.run(list(a), env=env2, cwd=cwd, capture_output=True, text=True, **k)
        t0, h0 = tree_state(cwd), tree_state(home)
        L.case(live_before == before_b, "the crontab seeded from the live one is the bundle's before, byte for byte")
        L.case(run2("bash", apply_sh, "check").returncode == 0, "apply.sh check in the clean environment: exit 0")
        L.case(run2("bash", apply_sh, "apply").returncode == 0, "apply.sh apply in the clean environment: exit 0")
        L.case(cron2.read_bytes() == after_b, "the planted crontab is the bundle's after, byte for byte")
        L.case(tree_state(cwd) == t0 and tree_state(home) == h0, "the apply changed nothing in the working folder or the planted HOME (only the crontab file)")
        for c in m["checks"]:
            r = run2("bash", "-c", c["cmd"])
            out = [l.strip() for l in r.stdout.splitlines() if l.strip()]
            good = r.returncode == c["exit"] and (c["count"] is None or (out and int(out[-1]) == c["count"]))
            L.case(bool(good), f"the manifest's check, run in the clean environment (exit {c['exit']}, count {c['count']}): {c['cmd'][:80]}")
        L.case(run2("bash", apply_sh, "verify").returncode == 0, "apply.sh verify in the clean environment: exit 0")
        L.case(run2("bash", apply_sh, "undo").returncode == 0, "apply.sh undo in the clean environment: exit 0")
        L.case(cron2.read_bytes() == before_b and tree_state(cwd) == t0 and tree_state(home) == h0,
               "the undo restored the planted crontab byte for byte; the working folder and the planted HOME are as they were")

        # ------------------------------------------------------------------------------------------ part 3
        L.note("part 3: the guard. The operator's line from the after table, exactly as cron runs it: five fields, the command with its \\% unescaped, under /bin/sh -c.")
        L.note("Only three things differ from production: the clock (a stub `date` first in PATH, as `date` is called by name), and the two literal prefixes planted (the operator's folder, the CTO's scratch folder).")
        lines = [l for l in after_b.decode().split("\n") if "ACT-OPERATOR-HOURS-1" in l and not l.startswith("#")]
        L.case(len(lines) == 1, "the after table holds the ACT's line once, active")
        line = lines[0]
        fields, cmd = cron_command(line)
        L.case(fields == "*/10 * * * *", "the schedule is `*/10 * * * *`: every 10 minutes at every hour, every day")
        L.case(len(line) < 900, "the line is under 900 characters (crontab -n refuses a command past about 1000)")
        L.case(cmd.count(OP_ROOT) == 2 and cmd.count(str(ORCH)) == 1, "the line names the operator's folder twice (launcher, log) and the scratch folder once (the state file)")
        plant = tmp / "plant"
        (plant / "op/install").mkdir(parents=True)
        (plant / "op/log").mkdir()
        (plant / "orch/log").mkdir(parents=True)
        (plant / "op/install/operator_launch.py").write_text(STUB_LAUNCH)
        (plant / "bin").mkdir()
        (plant / "bin/date").write_text(STUB_DATE)
        (plant / "bin/date").chmod(0o755)
        subs = {OP_ROOT: str(plant / "op"), str(ORCH): str(plant / "orch")}
        planted = re.sub("|".join(re.escape(k) for k in subs), lambda mo: subs[mo.group(0)], cmd)  # one pass: the planted folder lies under the scratch folder
        state = plant / "orch/log/night-hold.state.json"
        calls = plant / "op/calls.jsonl"

        def fire(hm, content=None, age=None, date_fail=False, mutate=None, keep_state=False, shell="/bin/sh", raw=False):
            """One cron firing at HHMM: the state file as given (None: missing; bytes/str written as is; dict as JSON),
            its mtime `age` seconds ago; returns (launched?, completed process)."""
            for f in ((calls,) if keep_state else (state, calls)):
                if f.exists():
                    f.unlink()
            if content is not None:
                state.write_text(content if isinstance(content, str) else json.dumps(content, indent=1))
                if age is not None:
                    t = datetime.now().timestamp() - age
                    os.utime(state, (t, t))
            e = {"PATH": f"{plant / 'bin'}:/usr/bin:/bin", "HOME": str(home), "LANG": "C.UTF-8", "FAKE_HM": hm}
            if date_fail:
                e["FAKE_DATE_FAIL"] = "1"
            if raw:
                e["FAKE_DATE_RAW"] = "1"
            r = subprocess.run([shell, "-c", planted if mutate is None else mutate], env=e, capture_output=True, text=True, cwd=cwd)
            return calls.exists() and calls.read_text().count("\n") == 1, r

        S = lambda holding, **k: dict({"pid": 4242, "at": "2026-11-12 03:30:00", "holding": holding, "in_window": True, "nightly": "x"}, **k)
        got = lambda hm, **k: fire(hm, **k)[0]
        # the five cases of the task, at the times it names
        L.case(got("0330", content=S(True), age=5) is False, "holding true at 03:30 (state 5 s old): no launch")
        L.case(got("0330", content=S(False), age=5) is True, "holding false at 03:30 (state 5 s old): launch")
        L.case(got("0330") is False, "state file missing at 03:30: no launch")
        L.case(got("1400") is True, "state file missing at 14:00: launch")
        L.case(got("0330", content='{"pid": 4242, "holding": fal') is False, "malformed JSON at 03:30: no launch (as missing)")
        L.case(got("1400", content='{"pid": 4242, "holding": fal') is True, "malformed JSON at 14:00: launch (as missing)")
        # the rest of the state's shapes at 03:30: only the boolean false lets a launch through
        for what, body in (("empty file", ""), ("not an object", "[false]"), ("no `holding` key", json.dumps({"pid": 1})),
                           ("holding \"false\" (a string)", json.dumps({"holding": "false"})), ("holding null", json.dumps({"holding": None})),
                           ("holding 0", json.dumps({"holding": 0})), ("holding \"\"", json.dumps({"holding": ""})),
                           ("a directory in its place", None)):
            if body is None:
                if state.exists():
                    state.unlink()
                state.mkdir()
                ok = not fire("0330", keep_state=True)[0]
                state.rmdir()
                L.case(ok, f"{what} at 03:30: no launch")
                continue
            L.case(got("0330", content=body, age=5) is False, f"{what} at 03:30: no launch")
        L.case(got("0330", content=S(False, extra="x"), age=5) is True, "holding false with other keys present at 03:30: launch")
        # F3: a state file dated in the future is not fresh (a little skew is allowed)
        L.case(got("0330", content=S(False), age=-30) is True, "holding false, state dated 30 s in the future (clock skew), at 03:30: launch")
        L.case(got("0330", content=S(False), age=-120) is False, "holding false, state dated 2 minutes in the future, at 03:30: no launch (stale, F3)")
        L.case(got("0330", content=S(False), age=-86400) is False, "holding false, state dated a day in the future, at 03:30: no launch (F3)")
        # freshness: a hold that has stopped writing is as good as missing
        L.case(got("0330", content=S(False), age=240) is True, "holding false, state 4 minutes old, at 03:30: launch")
        L.case(got("0330", content=S(False), age=360) is False, "holding false, state 6 minutes old (the hold stopped looking), at 03:30: no launch")
        L.case(got("0750", content=S(False), age=3600) is False, "holding false, state an hour old, at 07:50: no launch")
        L.case(got("0330", content=S(True), age=360) is False, "holding true, state 6 minutes old, at 03:30: no launch")
        # outside the window the state file is not read: a leftover `true` never stops the operator
        L.case(got("1400", content=S(True), age=86400) is True, "holding true in a day-old file at 14:00: launch (the file is not read outside 02:10-08:00)")
        L.case(got("0100", content=S(True), age=5) is True, "holding true at 01:00: launch (the hold is not in its window; the owner's 01:00-02:00 hour is back)")
        L.case(got("0000") is True and got("2350") is True, "state missing at 00:00 and at 23:50: launch")
        # the margin before the hold and the first look
        L.case(got("0200", content=S(False), age=5) is True, "02:00, holding false: launch (the last launch before the margin)")
        L.case(got("0210", content=S(False), age=5) is False, "02:10, holding false: no launch (a 50-minute session would end after 03:00)")
        L.case(got("0250", content=S(False), age=5) is False, "02:50, holding false: no launch")
        L.case(got("0300", content=S(False), age=5) is False, "03:00, holding false: no launch (the hold has not made its first look yet: the file is the pre-03:00 one)")
        L.case(got("0310", content=S(False), age=5) is True, "03:10, holding false: launch (the hold has looked ten times; false then means the nightly has ended)")
        L.case(got("0310", content=S(True), age=5) is False, "03:10, holding true: no launch")
        L.case(got("0730", content=S(True), age=5) is False and got("0750", content=S(True), age=5) is False, "07:30 and 07:50, holding true (the hold has not released): no launch")
        L.case(got("0730", content=S(False), age=5) is True, "07:30, holding false (released at 07:30 at the latest): launch")
        L.case(got("0800", content=S(True), age=5) is True and got("0800") is True, "08:00, any state: launch (the hold's window is over)")
        # F4: `date` failing or printing garbage: nothing launches, nothing is written to either stream
        ok, r = fire("0330", content=S(False), age=5, date_fail=True)
        L.case(ok is False and r.stdout == "" and r.stderr == "", "`date` failing (it writes a message to standard error): no launch, nothing on either stream (F4)")
        okk = True
        for garbage in ("abc", "", "12:30", "0a15", "2400x"):
            ok, r = fire(garbage, content=S(False), age=5, raw=True)
            okk = okk and ok is False and r.stdout == "" and r.stderr == ""
        L.case(okk, "`date` printing garbage (abc, empty, 12:30, 0a15, 2400x): no launch, nothing on either stream (F4)")
        L.case(fire("1400", raw=True)[0] is True, "control: the raw stub printing 1400 launches (so the cases above fail for the right reason)")
        # the whole day, tick by tick, against the old line
        ticks = [h * 100 + mi for h in range(24) for mi in expand_minutes("*/10")]
        old_ticks = [t for t in ticks if (t // 100 == 0) or (8 <= t // 100 <= 23)]
        for label, kw, expect_skip in (("holding false, fresh", dict(content=S(False), age=5), lambda t: 210 <= t < 310),
                                       ("holding true, fresh", dict(content=S(True), age=5), lambda t: 210 <= t < 800),
                                       ("state missing", dict(), lambda t: 210 <= t < 800)):
            launched = [t for t in ticks if fire(f"{t:04d}", **kw)[0]]
            want = [t for t in ticks if not expect_skip(t)]
            L.case(launched == want, f"all 144 ticks of a day, {label}: {len(launched)} launch, exactly the ticks outside "
                                     f"{'02:10-02:59 and 03:00' if label.startswith('holding false') else '02:10-07:59'}")
            if label == "holding false, fresh":
                gained = sorted(set(launched) - set(old_ticks))
                lost = sorted(set(old_ticks) - set(launched))
                L.case(gained == [t for t in ticks if 100 <= t < 210 or 310 <= t < 800] and lost == [],
                       "against the old line (00:00-00:50 and 08:00-23:50): nothing the old line ran is lost; 01:00-02:00 and 03:10-07:50 are added (holding false)")
            if label == "holding true, fresh":
                L.case(sorted(set(launched) - set(old_ticks)) == [t for t in ticks if 100 <= t < 210] and set(old_ticks) <= set(launched),
                       "against the old line, with the hold on (the whole night): the old ticks all stay, only 01:00-02:00 is added")
        # the same line under bash (cron uses /bin/sh = dash unless the table sets SHELL=; the guard is POSIX)
        bash_ok = (fire("0330", content=S(True), age=5, shell="/bin/bash")[0] is False and fire("0330", content=S(False), age=5, shell="/bin/bash")[0] is True
                   and fire("0330", shell="/bin/bash")[0] is False and fire("1400", shell="/bin/bash")[0] is True
                   and fire("0330", content='{"holding": fal', shell="/bin/bash")[0] is False and fire("0210", content=S(False), age=5, shell="/bin/bash")[0] is False)
        L.case(bash_ok, "the same six cases under /bin/bash (a table with SHELL=/bin/bash): the same answers")
        # the launcher's call, exactly: its argv is empty, the log is appended
        launched, r = fire("1400")
        L.case(launched and json.loads(calls.read_text()) == {"argv": []}, "the launch is `python3 -I operator_launch.py` with no arguments (the stub recorded one call)")
        lp = plant / "op/log/operator-launch.out"
        L.case(lp.exists() and '"result": "idle"' in lp.read_text(), "the launcher's output is appended to the operator's log, as before")
        skipped = fire("0330", content=S(True), age=5)[1]
        L.case(skipped.stdout == "" and skipped.stderr == "", "a skip prints nothing on stdout or stderr (cron has nothing to mail)")
        missing = fire("0330")[1]
        L.case(missing.stdout == "" and missing.stderr == "", "a missing state file prints no traceback (cron has nothing to mail)")
        # the line's own comment is not part of the command (sh ignores it) and the line parses under dash
        L.case(subprocess.run(["/bin/sh", "-n", "-c", planted]).returncode == 0, "/bin/sh -n accepts the command")
        # the guard cannot be tricked by an unrelated variable in cron's environment
        e = {"PATH": f"{plant / 'bin'}:/usr/bin:/bin", "FAKE_HM": "0330", "h": "1400", "HOME": str(home)}
        for f in (state, calls):
            if f.exists():
                f.unlink()
        subprocess.run(["/bin/sh", "-c", planted], env=e, capture_output=True, cwd=cwd)
        L.case(not calls.exists(), "an `h` already in the environment is overwritten by the line's own (03:30, state missing: still no launch)")
        L.case(line.count("%") == 2 and line.count("\\%") == 2, "the table's line holds exactly two %, both escaped (\\%H\\%M)")

        # ------------------------------------------------------------------------------------------ part 4
        L.note("part 4: the real writer. night_hold.py's own step() in a planted folder, at fixed times, writes the file the guard reads (its fields, its timing, its values when it runs).")
        sys.path.insert(0, str(ORCH / "tools"))
        sys.dont_write_bytecode = True
        import hold_lib as H  # noqa: E402
        import night_hold as NH  # noqa: E402
        orch = plant / "orch"
        (orch / "dispatch").mkdir(exist_ok=True)
        (orch / "dispatch/ready.txt").write_text("")
        (orch / "log/nightly").mkdir(exist_ok=True)
        (plant / "wt").mkdir(exist_ok=True)
        cfg = H.Cfg(str(orch), str(plant / "wt"))
        clock = {"t": datetime(2026, 11, 12, 2, 59, 30)}
        nh = NH.NightHold(cfg, now=lambda: clock["t"], leads=lambda: [])
        for f in (state, calls):
            if f.exists():
                f.unlink()

        def real_fire(hm):
            if calls.exists():
                calls.unlink()
            e = {"PATH": f"{plant / 'bin'}:/usr/bin:/bin", "HOME": str(home), "FAKE_HM": hm}
            subprocess.run(["/bin/sh", "-c", planted], env=e, capture_output=True, cwd=cwd)
            return calls.exists()

        nh.step()
        s0 = json.loads(state.read_text())
        L.case(s0["holding"] is False and s0["in_window"] is False and isinstance(s0["pid"], int), "02:59:30: the real writer's file says holding false, in_window false; it has `pid`, `at`, `holding`, `in_window`, `nightly`")
        L.case(real_fire("0300") is False, "the guard at 03:00 on that file (written at 02:59:30): no launch, the margin holds")
        clock["t"] = datetime(2026, 11, 12, 3, 0, 20)
        nh.step()
        L.case(json.loads(state.read_text())["holding"] is True, "03:00:20: the real writer's first look inside the window: holding true")
        L.case(real_fire("0310") is False and real_fire("0330") is False, "the guard at 03:10 and 03:30 on that file: no launch")
        clock["t"] = datetime(2026, 11, 12, 5, 0, 0)
        (Path(cfg.nightly) / "status.txt").write_text("2026-11-12 ran | planted: the night ended\n")
        nh.step()
        s2 = json.loads(state.read_text())
        L.case(s2["holding"] is False and s2["in_window"] is True, "05:00 with the nightly's status line for today: the real writer releases, holding false, in_window true")
        L.case(real_fire("0510") is True, "the guard at 05:10 on that file: launch (the nightly has ended; the owner's 'until the nightly ends')")
        clock["t"] = datetime(2026, 11, 12, 7, 31, 0)
        nh2 = NH.NightHold(cfg, now=lambda: clock["t"], leads=lambda: [])
        (Path(cfg.nightly) / "status.txt").unlink()
        clock["t"] = datetime(2026, 11, 12, 6, 0, 0)
        nh2.step()
        L.case(json.loads(state.read_text())["holding"] is True and real_fire("0600") is False, "a night with no end by 06:00: holding true: no launch")
        clock["t"] = datetime(2026, 11, 12, 7, 31, 0)
        nh2.step()
        L.case(json.loads(state.read_text())["holding"] is False and real_fire("0740") is True, "07:31, the nightly still not ended: the writer releases at 07:30 at the latest: holding false: launch")
        # the file when the hold is not running: it keeps its last content, its mtime ages out
        t_old = datetime.now().timestamp() - 3600
        os.utime(state, (t_old, t_old))
        L.case(real_fire("0740") is False and real_fire("1400") is True, "the writer stopped an hour ago (its file keeps its last content, `holding false`): no launch at 07:40, launch at 14:00")

        # ------------------------------------------------------------------------------------------ part 5
        L.note("part 5: the table parses (crontab -n: syntax check, then bails out; never installs)")
        # (crontab cuts a file name at about 100 characters: the files are named relative to their folder)
        shutil.copy(BUNDLE / "after/crontab/crontab", tmp / "a.cron")
        r = subprocess.run(["crontab", "-n", "a.cron"], capture_output=True, text=True, cwd=tmp)
        L.case(r.returncode == 0, "crontab -n on the after table: exit 0")
        (tmp / "long.cron").write_text(after_b.decode().replace("2>&1  # DEC-1141", "2>&1 " + "x" * 600 + "  # DEC-1141"))
        L.case(subprocess.run(["crontab", "-n", "long.cron"], capture_output=True, cwd=tmp).returncode != 0, "control: the same table with the command padded past cron's limit is refused by crontab -n (so the check above can fail)")
        L.case(subprocess.run(["crontab", "-l"], capture_output=True).stdout == live_before, "the live crontab is byte for byte what it was when the rehearsal began")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    head = ["# ACT-OPERATOR-HOURS-1 rehearsal. Parts 1 and 2: apply.sh on a stub crontab, then in the operator's dry-run form; part 3: the guard, the line as cron runs it; part 4: the real night_hold.py writer; part 5: crontab -n."]
    text = head + L.lines + [f"cases: {L.n}", f"failures: {L.fails}"]
    (BUNDLE / "rehearsal.log").write_text("\n".join(text) + "\n")
    print("\n".join(l for l in text if l.startswith("FAIL")) or "no failing case")
    print("\n".join(text[-2:]))


def real_clock_smoke():
    """Read only, not in the log: the line's guard on the real clock and the real state file, the launcher replaced by echo."""
    line = [l for l in (BUNDLE / "after/crontab/crontab").read_text().split("\n") if "ACT-OPERATOR-HOURS-1" in l and not l.startswith("#")][0]
    _, cmd = cron_command(line)
    cmd = cmd.split(" && ", 1)[0] + " && echo WOULD-LAUNCH"
    r = subprocess.run(["/bin/sh", "-c", cmd], capture_output=True, text=True)
    print(f"# real clock {datetime.now():%H:%M}, real state file: {r.stdout.strip() or 'no launch'}")


def real_home_smoke():
    """Read only, not in the log: apply.sh check on the real HOME (the real install), the crontab stubbed by a file."""
    tmp = Path(tempfile.mkdtemp(dir=HERE / "tmp"))
    try:
        (tmp / "bin").mkdir()
        (tmp / "bin/crontab").write_text(STUB_CRONTAB)
        (tmp / "bin/crontab").chmod(0o755)
        (tmp / "c").write_bytes((BUNDLE / "before/crontab/crontab").read_bytes())
        r = subprocess.run(["bash", str(BUNDLE / "apply.sh"), "check"], capture_output=True, text=True,
                           env=dict(os.environ, OPERATOR_CRONTAB_FILE=str(tmp / "c"), PATH=f"{tmp / 'bin'}:{os.environ['PATH']}"))
        print(f"# real HOME, stub crontab: apply.sh check exit {r.returncode} ({(r.stderr or r.stdout).strip()[:110]})")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


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
    real_clock_smoke()
    real_home_smoke()


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates, "all": all_, "smoke": real_clock_smoke, "smoke2": real_home_smoke}[sys.argv[1]]()
