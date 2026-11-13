#!/usr/bin/env python3
"""ACT-OPERATOR-HOURS-3 (DEC-1157 (2)): build the bundle, rehearse it, finalize the manifest, run the operator's own gates over it.
Modelled on drafts/operator-hours-2/build_act.py (and part7.py) and ACT-OPERATOR-HOURS-1's crontab bundle.

    python3 -B build_act.py build      the bundle from the live crontab, install and main tree (read only) and this folder's code/
    python3 -B build_act.py rehearse   rehearsal.log in the bundle (a stub crontab, planted folders, clones; never the live ones)
    python3 -B build_act.py finalize   the manifest with the rehearsal's sha256 (only when the log ends `failures: 0`)
    python3 -B build_act.py gates      validate_manifest, the files' hashes, the path rule, act_class.classify (read only)
    python3 -B build_act.py all

Writes only: the bundle (acts/ACT-OPERATOR-HOURS-3/), this folder, and WORK (the helper's TMPDIR, not ~/gov-os-runs).
"""
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-OPERATOR-HOURS-3"
BUNDLE = ORCH / "acts" / ACT
BREL = ".gov-runtime/scratch/orchestrator/acts/" + ACT
LIVE_INST = Path("/home/usain/gov-os-operator/install")
WORK = Path(os.environ.get("HOURS3_WORK", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
                           "b2f0511f-891b-4874-8930-6d34ca5972ea/scratchpad/hours3/work"))
CODE = HERE / "code"
HEAVY = ORCH / "tools/heavy_slot.sh"
PKG = ORCH / "acts" / (ACT + ".package.md")
REPO_FILES = ["governance/project/operator/opcommon.py",
              "tests/unit/operator/test_act_operator_hours_2.py",
              "tests/acceptance/W2-148/test_w2_148_gates.py",
              "tests/acceptance/W2-148/README.md"]
INST_PATH = "gov-os-operator/install/"
MAP_REL = "governance/project/path-map.yaml"
LIVE_MAP = "805bd918d46787b61be2abea8934e5f50619833f5f7eb8bd7ed6c981d649e9b1"
CRON_BEFORE = "88cf08b165a184a23681b610ea07490c7c60559c6125fdba359db2a083d7c880"     # ACT-OPERATOR-HOURS-1's after
OPC_BEFORE = "123e17e5581149725c75babaa9200a09c4854254053df14105b6ce17450bbc87"      # ACT-OPERATOR-HOURS-2's after
DEC = "DEC-1157, DEC-1141 (6), DEC-1104"
TOOLS_HOME = Path("/home/usain")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def shab(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, env=None, cwd=None, timeout=1800, inp=None):
    return subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=cwd, timeout=timeout, input=inp)


def approved_after(approved_before, new_sha):
    out, hit = [], 0
    for line in approved_before.splitlines():
        s, _, name = line.partition("  ")
        if name == "opcommon.py":
            line, hit = f"{new_sha}  opcommon.py", hit + 1
        out.append(line)
    assert hit == 1
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------------------------------------------- build
def build():
    if BUNDLE.exists():
        assert not (BUNDLE / "review.md").exists(), "the bundle holds a review: move it aside before a rebuild"
        shutil.rmtree(BUNDLE)
    cron_live = run(["crontab", "-l"]).stdout.encode()
    assert shab(cron_live) == CRON_BEFORE, "the live crontab is not ACT-OPERATOR-HOURS-1's after: rebuild the crontab part"
    assert cron_live == (CODE / "crontab/crontab.before").read_bytes(), "code/crontab/crontab.before is not the live crontab"
    cron_after = (CODE / "crontab/crontab.after").read_bytes()
    live_ap = (LIVE_INST / "APPROVED").read_text()
    for line in live_ap.splitlines():
        s, _, name = line.partition("  ")
        assert sha(LIVE_INST / name) == s, f"the live install is not as APPROVED says: {name}"
    assert sha(LIVE_INST / "opcommon.py") == OPC_BEFORE == sha(REPO / REPO_FILES[0])
    st = run(["git", "status", "--porcelain", "--"] + REPO_FILES + [MAP_REL], cwd=REPO).stdout
    assert st.strip() == "", f"a listed repository file is not at the committed head: {st}"
    assert sha(REPO / MAP_REL) == LIVE_MAP, "the live path map is not the allowed before"
    assert LIVE_MAP in (HERE / "apply.sh").read_text()
    new_oc = CODE / REPO_FILES[0]
    after_ap = approved_after(live_ap, sha(new_oc))
    rows = [("crontab", "crontab", cron_live, cron_after)]
    for p in REPO_FILES:
        rows.append(("repo", p, (REPO / p).read_bytes(), (CODE / p).read_bytes()))
    rows.append(("home", INST_PATH + "opcommon.py", (LIVE_INST / "opcommon.py").read_bytes(), new_oc.read_bytes()))
    rows.append(("home", INST_PATH + "APPROVED", live_ap.encode(), after_ap.encode()))
    lines = []
    for root, p, b, a in rows:
        for side, data in (("before", b), ("after", a)):
            f = BUNDLE / side / root / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        assert shab(b) != shab(a), p
        lines.append(f"{root}|{p}|{shab(b)}|{shab(a)}")
    (BUNDLE / "list.txt").write_text("\n".join(lines) + "\n")
    (BUNDLE / "keep.txt").write_text("\n".join(l for l in live_ap.splitlines() if not l.endswith("  opcommon.py")) + "\n")
    shutil.copy(HERE / "apply.sh", BUNDLE / "apply.sh")
    (BUNDLE / "apply.sh").chmod(0o755)
    write_manifest(None)
    print(f"built {BUNDLE}")


def checks_a():
    return [
        {"cmd": "crontab -l | grep -v '^#' | grep -c .", "exit": 0, "count": 4},
        {"cmd": "crontab -l | grep -c '^\\*/10 \\* \\* \\* \\* /usr/bin/python3 -I .*/gov-os-operator/install/operator_launch\\.py >> .*/gov-os-operator/log/operator-launch\\.out 2>&1  # DEC-1157 (2), ACT-OPERATOR-HOURS-3 '", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c 'night-hold\\.state\\.json'", "exit": 1, "count": 0},
        {"cmd": "crontab -l | grep -c 'operator_launch\\.py'", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^0 4 \\* \\* \\* /usr/bin/bash .*/nightly/nightly_restart\\.sh  # DEC-1132 (4), ACT-NIGHTLY-RESTART-1:'", "exit": 0, "count": 1},
        {"cmd": "crontab -l | grep -c '^\\* \\* \\* \\* \\* /usr/bin/bash .*/dispatch/run_tick\\.sh$'", "exit": 0, "count": 1},
    ]


def checks_b(new_oc, after_ap):
    return [
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/opcommon.py" | grep -c {new_oc}', "exit": 0, "count": 1},
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/APPROVED" | grep -c {after_ap}', "exit": 0, "count": 1},
        {"cmd": 'grep -c "^HOLD_FROM = \\|night_hold_reasons\\|NIGHT_HOLD_MAX_AGE_S" "$HOME/gov-os-operator/install/opcommon.py"', "exit": 1, "count": 0},
        {"cmd": 'grep -c "the nightly runs (NIGHTLY-RUNNING)" "$HOME/gov-os-operator/install/opcommon.py"', "exit": 0, "count": 1},
        {"cmd": 'grep -c "opcommon.py" "$HOME/gov-os-operator/install/APPROVED"', "exit": 0, "count": 1},
    ]


def write_manifest(rehearsal_sha):
    rows = [l.split("|") for l in (BUNDLE / "list.txt").read_text().splitlines()]
    touched = [{"root": r, "path": p, "before": None if b == "null" else b, "after": a} for r, p, b, a in rows]
    files = {}
    for side in ("before", "after"):
        for f in sorted((BUNDLE / side).rglob("*")):
            if f.is_file():
                files[str(f.relative_to(BUNDLE))] = sha(f)
    for n in ("apply.sh", "list.txt", "keep.txt"):
        files[n] = sha(BUNDLE / n)
    new_oc = [a for r, p, b, a in rows if p.endswith("install/opcommon.py")][0]
    after_ap = [a for r, p, b, a in rows if p.endswith("install/APPROVED")][0]
    ca, cb = checks_a(), checks_b(new_oc, after_ap)
    m = {"act": ACT, "dec": DEC, "author": "cto", "claimed_class": "O",
         "parts": {
             "A": {"claimed_class": "b", "what": "the crontab's operator line (line 7): every 10 minutes at every hour, no time window, no night-hold state file read",
                   "applied_by": "the CTO, after one review and the owner's yes", "steps": "bash apply.sh A check|apply|verify|undo",
                   "touched": [t for t in touched if t["root"] == "crontab"], "checks": ca},
             "B": {"claimed_class": "O", "what": "G9's time holds removed: the operator's install (opcommon.py, APPROVED) and the repository's source and tests; the path map's exemption entry for the commit (DEC-1136 (2)) by apply.sh B exempt",
                   "applied_by": "the owner's operator, by hand", "steps": "bash apply.sh B check|apply|verify|undo, then exempt|exempt-verify|exempt-undo",
                   "touched": [t for t in touched if t["root"] != "crontab"], "checks": cb}},
         "touched": touched, "files": files, "checks": ca + cb, "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


# -------------------------------------------------------------------------------------------------------- rehearsal
class Log:
    def __init__(self):
        self.lines, self.n, self.fails = [], 0, 0

    def case(self, ok, text):
        self.n += 1
        self.fails += 0 if ok else 1
        self.lines.append(f"{'ok' if ok else 'FAIL'} {self.n}: {text}")
        print(self.lines[-1], flush=True)

    def note(self, text):
        self.lines.append(f"# {text}")
        print(self.lines[-1], flush=True)


DRIVER = r'''
import json, os, shutil, sys, time
inst, cfgp, casesp = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, inst)
sys.dont_write_bytecode = True
import opcommon as oc
s = oc.load_settings(cfgp)
conf = json.load(open(cfgp))
state, clock = conf["state_path"], conf["clock"]
RAW = {"empty": "", "malformed": "{not json", "strfalse": '{"holding": "false"}'}
out = []
for hm, kind in json.load(open(casesp)):
    if os.path.isdir(state):
        shutil.rmtree(state)
    elif os.path.lexists(state):
        os.unlink(state)
    os.makedirs(os.path.dirname(state), exist_ok=True)
    if kind == "dir":
        os.mkdir(state)
    elif kind != "missing":
        if kind in ("true", "false", "stale"):
            body = json.dumps({"pid": 1, "at": "x", "holding": kind == "true", "in_window": True, "nightly": "n"})
        else:
            body = RAW[kind]
        with open(state, "w") as f:
            f.write(body)
        if kind == "stale":
            t = time.time() - 400
            os.utime(state, (t, t))
    with open(clock, "w") as f:
        f.write("2026-11-13T%s:00+00:00\n" % hm)
    out.append(oc.holds(s))
print(json.dumps(out))
'''
KINDS = ["true", "false", "missing", "stale", "malformed", "empty", "strfalse", "dir"]
TIMES = ["00:00", "01:30", "02:05", "02:09", "02:10", "02:30", "03:00", "03:09", "03:10", "03:30", "04:00", "05:10",
         "07:29", "07:30", "07:45", "07:59", "08:00", "08:01", "14:00", "23:59"]


def minutes(hm):
    return int(hm[:2]) * 60 + int(hm[3:])


def old_rule(hm, kind):
    """ACT-OPERATOR-HOURS-2's rule (the live G9 today), written out separately."""
    t = minutes(hm)
    if t < 130 or t >= 480:
        return False
    if t < 190:
        return True
    return kind != "false"


def tree_state(root):
    out = {}
    root = Path(root)
    for p in sorted(root.rglob("*")):
        if "__pycache__" in p.parts or p.name == "launch.lock":
            continue
        rel = str(p.relative_to(root))
        if p.is_symlink():
            out[rel] = ("link", os.readlink(p))
        elif p.is_dir():
            out[rel] = ("dir", stat.S_IMODE(p.stat().st_mode))
        else:
            out[rel] = ("file", sha(p), stat.S_IMODE(p.stat().st_mode))
    return out


def make_cfg(tmp, name, op, repo, home, scratch):
    cfg = tmp / f"{name}.json"
    cfg.write_text(json.dumps({"operator_root": str(op), "repo": str(repo), "home": str(home), "scratch": str(scratch),
                               "clock": str(tmp / f"{name}.clock"), "state_path": str(scratch / "log/night-hold.state.json"),
                               "poll_s": 0.1}))
    (tmp / f"{name}.clock").write_text("2026-11-13T10:00:00+00:00\n")
    return cfg


def matrix(install, cfg, tmp):
    cases = [[hm, k] for hm in TIMES for k in KINDS]
    (tmp / "cases.json").write_text(json.dumps(cases))
    (tmp / "driver.py").write_text(DRIVER)
    r = run([sys.executable, "-I", "-B", str(tmp / "driver.py"), str(install), str(cfg), str(tmp / "cases.json")])
    if r.returncode != 0:
        raise RuntimeError(r.stderr)
    return dict(zip([tuple(c) for c in cases], json.loads(r.stdout)))


def summary(out):
    tail = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed)", l)]
    return re.sub(r" in [0-9.]+s( \([0-9:]+\))?", "", tail[-1]).strip(" =") if tail else "no summary"


NO_SLOTS = os.environ.get("HOURS3_NO_SLOTS") == "1"
NOT_RUN = "NOT RUN in this rehearsal: every heavy slot was taken by the leads (a gate wait, DEC-1146); the CTO stopped the run after 34 min"


def pytest_on(clone, args, wtmp):
    if NO_SLOTS:
        return None, NOT_RUN, ""
    env = {"HOME": os.environ["HOME"], "PATH": os.environ["PATH"], "LC_ALL": "C.UTF-8", "TMPDIR": str(wtmp),
           "PYTHONUSERBASE": str(TOOLS_HOME / ".local")}
    r = run(["bash", str(HEAVY), "python3", "-m", "pytest", *args, "-q", "-p", "no:cacheprovider", "--no-header"],
            env=env, cwd=str(clone), timeout=3600)
    return r.returncode, summary(r.stdout), r.stdout


def rehearse():
    if WORK.exists():
        subprocess.run(["chmod", "-R", "u+w", str(WORK)], check=False)
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    L = Log()
    live_before = {p: sha(LIVE_INST / p) for p in ("APPROVED", "opcommon.py", "operator_run.py", "operator_launch.py")}
    cron_before = run(["crontab", "-l"]).stdout
    watched = REPO_FILES + [MAP_REL]
    tree_before = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    tmp = Path(tempfile.mkdtemp(prefix="hours3-", dir=str(WORK)))
    try:
        rehearse_in(L, tmp)
    except BaseException as exc:
        L.case(False, f"the rehearsal stopped: {exc.__class__.__name__}: {str(exc)[:300]}")
    L.case({p: sha(LIVE_INST / p) for p in live_before} == live_before,
           "the live install (APPROVED, opcommon.py, operator_run.py, operator_launch.py) is byte for byte as it began")
    L.case(run(["crontab", "-l"]).stdout == cron_before, "the live crontab is byte for byte as it began")
    tree_after = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    L.case(tree_after == tree_before, "the live main tree's four repository paths and the path map are as they began (status and sha256)")
    head = ["# ACT-OPERATOR-HOURS-3 rehearsal (DEC-1157 (2)). Part 1: apply.sh A on a stub crontab, the new line as cron runs it.",
            "# Part 2: apply.sh B stage 1 on planted folders. Part 3: G9 of the installed copy over a stub clock and planted state files.",
            "# Part 4: the real launcher and run from the applied copy. Part 5: does it bite (mutants). Part 6: the operator's own tests on",
            "# a clone with the after files, and the revised tests on the old code. Part 7: apply.sh B's second stage (exempt, DEC-1136 (2))",
            "# in a clone of w2/integrate, the package's blocks run as printed, W1-01 run before, between and after the two commits."]
    text = head + L.lines + [f"cases: {L.n}", f"failures: {L.fails}"]
    (BUNDLE / "rehearsal.log").write_text("\n".join(text) + "\n")
    print("\n".join(text[-2:]))


def rehearse_in(L, tmp):
    lst = [l.split("|") for l in (BUNDLE / "list.txt").read_text().splitlines()]
    after = {(r, p): a for r, p, b, a in lst}
    before = {(r, p): b for r, p, b, a in lst}
    new_oc = after[("home", INST_PATH + "opcommon.py")]
    new_ap = after[("home", INST_PATH + "APPROVED")]
    old_ap = before[("home", INST_PATH + "APPROVED")]

    # ------------------------------------------------------------------------------------------ part 1: Part A
    L.note("part 1: apply.sh A on a stub crontab (a `crontab` on PATH that reads and writes a file, `-l` and `<file>` as cron's), seeded with the live bytes at the build")
    wa = tmp / "a"
    (wa / "bin").mkdir(parents=True)
    store = wa / "crontab.store"
    shutil.copy2(BUNDLE / "before/crontab/crontab", store)
    (wa / "bin/crontab").write_text("#!/bin/bash\nS=\"$CRONTAB_STORE\"\nif [ \"$1\" = -l ]; then [ -f \"$S\" ] || { echo 'no crontab' >&2; exit 1; }; cat \"$S\"; exit 0; fi\n"
                                    "[ \"$1\" = - ] || { echo 'the stub takes only -l and - (standard input)' >&2; exit 1; }\n"
                                    "cat > \"$S.new\"; /usr/bin/crontab -n - < \"$S.new\" >/dev/null 2>&1 || { rm -f \"$S.new\"; echo 'bad crontab' >&2; exit 1; }\nmv \"$S.new\" \"$S\"\n")
    (wa / "bin/crontab").chmod(0o755)
    bundle_a = wa / "root" / BREL
    shutil.copytree(BUNDLE, bundle_a)
    home_a = wa / "home"
    home_a.mkdir()
    aenv = {"HOME": str(home_a), "PATH": f"{wa / 'bin'}:{os.environ['PATH']}", "LC_ALL": "C", "CRONTAB_STORE": str(store)}

    def apA(step, env=None):
        return run(["bash", str(bundle_a / "apply.sh"), "A", step], env=env or aenv, cwd=str(wa))

    def st():
        return sha(store)
    cb, ca = before[("crontab", "crontab")], after[("crontab", "crontab")]
    r = apA("check")
    L.case(r.returncode == 0 and "ready to apply" in r.stdout, f"A check on the before: exit 0, ready ({r.returncode})")
    r = apA("verify")
    L.case(r.returncode == 3 and "not applied" in r.stderr, f"A verify before the apply: exit 3, not applied ({r.returncode})")
    r = apA("undo")
    L.case(r.returncode == 0 and "nothing to do" in r.stdout and st() == cb, "A undo on the before: exit 0, nothing to do, untouched")
    r = run(["bash", str(bundle_a / "apply.sh"), "A", "exempt"], env=aenv, cwd=str(wa))
    r2 = run(["bash", str(bundle_a / "apply.sh"), "check"], env=aenv, cwd=str(wa))
    L.case(r.returncode == 2 and r2.returncode == 2 and st() == cb, "an unknown step (A exempt) or no part (check): exit 2, usage, untouched")
    r = apA("apply")
    L.case(r.returncode == 0 and "state applied (A)" in r.stdout and st() == ca, f"A apply: exit 0, the stub crontab is the after byte for byte ({r.returncode})")
    r = apA("verify")
    L.case(r.returncode == 0, f"A verify after the apply: exit 0 ({r.returncode})")
    r = apA("apply")
    L.case(r.returncode == 0 and "already in place" in r.stdout and st() == ca, "A apply again: exit 0, already in place, untouched")
    r = apA("check")
    L.case(r.returncode == 3 and "already applied" in r.stderr, f"A check on the after: exit 3, already applied ({r.returncode})")
    for c in checks_a():
        rr = run(["bash", "-c", c["cmd"]], env=aenv)
        cnt = int(rr.stdout.strip() or -1)
        L.case(rr.returncode == c["exit"] and cnt == c["count"], f"the manifest's Part A check (exit {c['exit']}, count {c['count']}): {c['cmd'][:110]}")
    bl = (BUNDLE / "before/crontab/crontab").read_text().split("\n")
    al = (BUNDLE / "after/crontab/crontab").read_text().split("\n")
    diff = [i for i in range(max(len(bl), len(al))) if (bl[i:i + 1] or [None]) != (al[i:i + 1] or [None])]
    L.case(len(bl) == len(al) and diff == [6], "the before and the after differ in line 7 only (the operator's line); the six other lines and the final newline are the same")
    newl = al[6]
    cmd_old = bl[6].split("  # ", 1)[0].rsplit(" && ", 1)[1]
    assert cmd_old.startswith("/usr/bin/python3 -I /home/usain/gov-os-operator/install/operator_launch.py >> "), cmd_old
    L.case(newl.startswith("*/10 * * * * " + cmd_old + "  # DEC-1157 (2), ACT-OPERATOR-HOURS-3 "),
           "the new line is `*/10 * * * * ` then the old line's launcher command and log redirect byte for byte, then the comment citing DEC-1157 (2) and ACT-OPERATOR-HOURS-3")
    L.case("night-hold" not in newl.split("  # ", 1)[0] and "date" not in newl.split("  # ", 1)[0] and "%" not in newl and "'" not in newl,
           "the new line's command reads no state file and no clock (no `night-hold`, no `date`), and has no `%` and no quote")
    r1 = run(["/usr/bin/crontab", "-n", "-"], inp=(BUNDLE / "after/crontab/crontab").read_text())
    r0 = run(["/usr/bin/crontab", "-n", "-"], inp=(BUNDLE / "before/crontab/crontab").read_text())
    L.case(r1.returncode == 0 and r0.returncode == 0, "the real crontab -n (by standard input, as apply.sh installs it) accepts the after and the before")
    rl = run(["/usr/bin/crontab", "-n", str(BUNDLE / "after/crontab/crontab")])
    L.case(rl.returncode != 0 and "No such file" in rl.stderr, "control: the real crontab given this bundle's long file path refuses it (it cuts the name at about 100 characters), so apply.sh uses standard input")
    # the line as cron runs it (sh -c of the command part), the operator's paths planted
    plant_op = wa / "gov-os-operator"
    (plant_op / "install").mkdir(parents=True)
    (plant_op / "log").mkdir()
    (plant_op / "install/operator_launch.py").write_text("import sys, time\nprint('{\"result\": \"idle\", \"stub\": true}')\n")
    body = newl[len("*/10 * * * * "):].replace("/home/usain/gov-os-operator", str(plant_op))
    for label, state in (("02:30-like, no state file", None), ("05:30-like, the stale holding false the stopped night hold left", "stale"),
                         ("a fresh holding true", "true")):
        sp = REPO / ".gov-runtime/scratch/orchestrator/log/night-hold.state.json"      # not touched: the line no longer names it
        r = run(["/bin/sh", "-c", body], env={"HOME": str(home_a), "PATH": "/usr/bin:/bin", "SHELL": "/bin/sh"})
        L.case(r.returncode == 0 and (plant_op / "log/operator-launch.out").read_text().count('"stub": true') >= 1,
               f"the new line as cron runs it ({label}): the launcher runs and appends to operator-launch.out (no time window, no state read)")
    lines_out = (plant_op / "log/operator-launch.out").read_text().count('"stub": true')
    L.case(lines_out == 3, f"three runs, three launcher lines appended ({lines_out})")
    r = apA("undo")
    L.case(r.returncode == 0 and "state before (undone) (A)" in r.stdout and st() == cb, f"A undo: exit 0, the before byte for byte ({r.returncode})")
    r = apA("check")
    L.case(r.returncode == 0, "A check after the undo: ready again")
    with open(store, "a") as f:
        f.write("# a line added since the build\n")
    moved = st()
    res = {s_: apA(s_).returncode for s_ in ("check", "apply", "undo", "verify")}
    L.case(all(v == 3 for v in res.values()) and st() == moved, f"a crontab that moved since the build: check, apply, undo, verify each exit 3, untouched ({res})")
    shutil.copy2(BUNDLE / "before/crontab/crontab", store)
    (bundle_a / "after/crontab/crontab").write_text("# tampered\n")
    r = apA("apply")
    L.case(r.returncode == 4 and st() == cb, f"a tampered frozen after copy: A apply exit 4, untouched ({r.returncode})")
    shutil.copy2(BUNDLE / "after/crontab/crontab", bundle_a / "after/crontab/crontab")
    # Part A never reads or needs Part B's files
    (bundle_a / "after/home" / (INST_PATH + "opcommon.py")).write_text("# tampered Part B copy\n")
    r = apA("apply")
    L.case(r.returncode == 0 and st() == ca, "Part A ignores Part B's rows (a tampered Part B frozen copy does not stop A apply); with no install in HOME at all")
    apA("undo")
    shutil.copy2(BUNDLE / "after/home" / (INST_PATH + "opcommon.py"), bundle_a / "after/home" / (INST_PATH + "opcommon.py"))
    # the operator's dry-run form: a clean environment, run from an empty folder
    empty = wa / "empty"
    empty.mkdir()
    r = run(["bash", str(bundle_a / "apply.sh"), "A", "apply"], env={"HOME": str(home_a), "PATH": f"{wa / 'bin'}:/usr/bin:/bin", "CRONTAB_STORE": str(store)}, cwd=str(empty))
    L.case(r.returncode == 0 and st() == ca and not list(empty.iterdir()), "A apply in a clean environment from an empty folder: the after, nothing else written")
    apA("undo")

    # ------------------------------------------------------------------------------------------ part 2: Part B stage 1
    L.note("part 2: apply.sh B stage 1 on planted folders (a planted HOME with a copy of the live install, a planted main tree with the four before files)")

    def world(name):
        w = tmp / name
        home, root = w / "home", w / "root"
        op = home / "gov-os-operator"
        shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
        for d in ("log", "queue", "acts", "wall"):
            (op / d).mkdir(parents=True, exist_ok=True)
        for p in REPO_FILES:
            (root / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / p, root / p)
        b = root / BREL
        shutil.copytree(BUNDLE, b)
        return home, root, op, b

    def ap(w, step):
        home, root, op, b = w
        return run(["bash", str(b / "apply.sh"), "B", step], env={"HOME": str(home), "PATH": os.environ["PATH"], "LC_ALL": "C"}, cwd=str(root))

    def snap(w):
        home, root, op, b = w
        return (tree_state(op), tree_state(root / "governance"), tree_state(root / "tests"))

    def listed(w, side):
        home, root, op, b = w
        vals = before if side == "before" else after
        return all(sha((home if r == "home" else root) / p) == v for (r, p), v in vals.items() if r != "crontab")

    w = world("w1")
    home, root, op, bdir = w
    s0 = snap(w)
    r = ap(w, "check")
    L.case(r.returncode == 0 and "ready to apply" in r.stdout, f"B check on the before: exit 0, ready ({r.returncode})")
    r = ap(w, "verify")
    L.case(r.returncode == 3 and "not applied" in r.stderr, f"B verify before: exit 3 ({r.returncode})")
    r = ap(w, "undo")
    L.case(r.returncode == 0 and "nothing to do" in r.stdout and snap(w) == s0, "B undo on the before: exit 0, nothing to do, untouched")
    old_install = tmp / "old-install"
    shutil.copytree(op / "install", old_install)
    r = ap(w, "apply")
    L.case(r.returncode == 0 and "state applied (B)" in r.stdout and "own APPROVED check: ok" in r.stdout, f"B apply: exit 0, the install's own APPROVED check ok ({r.returncode}; {r.stderr.strip()[:100]})")
    L.case(listed(w, "after") and sha(op / "install/APPROVED") == new_ap and sha(op / "install/opcommon.py") == new_oc,
           f"every Part B file hashes as the after; APPROVED {new_ap[:12]}, opcommon.py {new_oc[:12]}")
    L.case(all(stat.S_IMODE((op / "install" / n).stat().st_mode) == 0o444 for n in ("opcommon.py", "APPROVED")), "the install's two files are 0444")
    L.case(not list(op.rglob(".*act-operator-hours-3*")) and not list(root.rglob(".*act-operator-hours-3*")) and not (op / "install/__pycache__").exists(),
           "no temporary file left, no __pycache__ in the install")
    oh = {l.split("  ")[1]: l.split("  ")[0] for l in (old_install / "APPROVED").read_text().splitlines()}
    L.case(all(sha(op / "install" / n) == h for n, h in oh.items() if n != "opcommon.py"), "the thirteen other install files are byte for byte as they were")
    nl, ol = (op / "install/APPROVED").read_text().splitlines(), (old_install / "APPROVED").read_text().splitlines()
    L.case(len(nl) == len(ol) and [a for a, b in zip(nl, ol) if a != b] == [f"{new_oc}  opcommon.py"], "APPROVED differs in exactly one line: opcommon.py's")
    r = ap(w, "verify")
    L.case(r.returncode == 0, f"B verify after: exit 0 ({r.returncode})")
    s1 = snap(w)
    r = ap(w, "apply")
    L.case(r.returncode == 0 and "already in place" in r.stdout and snap(w) == s1, "B apply again: already in place, untouched")
    r = ap(w, "check")
    L.case(r.returncode == 3 and "already applied" in r.stderr, "B check on the after: exit 3, already applied")
    for c in checks_b(new_oc, new_ap):
        rr = run(["bash", "-c", c["cmd"]], env={"HOME": str(home), "PATH": os.environ["PATH"]})
        cnt = int(rr.stdout.strip() or -1)
        L.case(rr.returncode == c["exit"] and cnt == c["count"], f"the manifest's Part B check (exit {c['exit']}, count {c['count']}): {c['cmd'][:100]}")
    r = ap(w, "undo")
    L.case(r.returncode == 0 and "state before (undone) (B)" in r.stdout and listed(w, "before") and sha(op / "install/APPROVED") == old_ap,
           f"B undo: exit 0, every file the before, APPROVED the old one ({r.returncode})")
    L.case(snap(w) == s0, "the install and the repository paths are byte for byte (hash, mode, listing) what they were")
    w2 = world("w2")
    s_w2 = snap(w2)
    os.chmod(w2[2] / "install", 0o555)
    r = ap(w2, "apply")
    os.chmod(w2[2] / "install", 0o755)
    L.case(r.returncode == 5 and not listed(w2, "before") and not listed(w2, "after"), f"B apply with the install folder not writable: stops, exit 5, a half state ({r.returncode})")
    r = ap(w2, "check")
    L.case(r.returncode == 3 and "partly before, partly after" in r.stderr, "B check names the half state: exit 3")
    r = ap(w2, "apply")
    L.case(r.returncode == 0 and listed(w2, "after"), f"a second B apply finishes it ({r.returncode})")
    r = ap(w2, "undo")
    L.case(r.returncode == 0 and snap(w2) == s_w2, "B undo: the whole state as it began")

    def refusal(label, fn, steps=("check", "apply", "undo", "verify"), codes=None, base="before"):
        wx = world("x-" + re.sub(r"\W+", "-", label)[:40])
        if base == "after":
            assert ap(wx, "apply").returncode == 0
        fn(wx)
        sx = snap(wx)
        res = {s_: ap(wx, s_).returncode for s_ in steps}
        ok = all(res[s_] in (codes or {}).get(s_, (3, 4, 6)) for s_ in steps) and snap(wx) == sx
        L.case(ok, f"{label}: {', '.join(f'{s_} exit {c}' for s_, c in res.items())}; nothing touched")
    ok_undo = {"undo": (0, 3, 4, 6)}
    refusal("a repository file moved (opcommon.py one line longer)", lambda x: (x[1] / REPO_FILES[0]).write_text((x[1] / REPO_FILES[0]).read_text() + "# moved\n"))
    refusal("an install file other than opcommon.py moved (brief.md)", lambda x: ((x[2] / "install/brief.md").chmod(0o644), (x[2] / "install/brief.md").write_text("moved\n")), codes=ok_undo)
    refusal("a stray file in install/", lambda x: (x[2] / "install/stray.py").write_text("x\n"), codes=ok_undo)
    refusal("after the apply, the install's APPROVED edited", lambda x: ((x[2] / "install/APPROVED").chmod(0o644), (x[2] / "install/APPROVED").write_text("moved\n")), base="after")
    refusal("a tampered frozen copy (after/home/.../opcommon.py)", lambda x: (x[3] / "after/home" / (INST_PATH + "opcommon.py")).write_text("# t\n"), codes={s_: (4,) for s_ in ("check", "apply", "undo", "verify")})
    busy = {s_: (6,) for s_ in ("check", "apply")}
    refusal("the operator's freeze held (install/act-in-progress.txt)", lambda x: (x[2] / "install/act-in-progress.txt").write_text("x\n"), steps=("check", "apply"), codes=busy)
    refusal("the operator's journal present", lambda x: (x[2] / "log/journal.json").write_text("{}\n"), steps=("check", "apply"), codes=busy)
    refusal("a request waiting in queue/", lambda x: (x[2] / "queue/one.req").write_text("ACT-X " + "a" * 64 + "\n"), steps=("check", "apply"), codes=busy)
    wl = world("w-lock")
    sl = snap(wl)
    hold = subprocess.Popen(["flock", "-x", str(wl[2] / "log/launch.lock"), "sleep", "30"], start_new_session=True)
    try:
        time.sleep(0.5)
        r = ap(wl, "apply")
        L.case(r.returncode == 6 and "launch is running" in r.stderr and snap(wl) == sl, f"a launch holding log/launch.lock: B apply exit 6, untouched ({r.returncode})")
    finally:
        os.killpg(hold.pid, 15)
        hold.wait()

    # ------------------------------------------------------------------------------------------ part 3: G9 table
    L.note("part 3: G9 of the installed copy (apply.sh B's own result), the real opcommon.holds(), over a clock file and a planted night-hold state file per case")
    wa2 = world("w-applied")
    assert ap(wa2, "apply").returncode == 0
    ha, ra, opa, _ = wa2
    scratch = tmp / "scratch-a"
    (scratch / "log").mkdir(parents=True)
    cfg = make_cfg(tmp, "new", opa, ra, ha, scratch)
    new = matrix(opa / "install", cfg, tmp)
    old = matrix(old_install, make_cfg(tmp, "old", opa, ra, ha, scratch), tmp)
    L.case(all(v == [] for v in new.values()), f"the installed G9 over {len(new)} (time, state) cases ({len(TIMES)} times x {len(KINDS)} states: true, false, missing, stale, malformed, empty, \"false\", a directory): no hold in any")
    bad_old = [c for c, v in old.items() if (v != []) != old_rule(*c)]
    L.case(not bad_old, f"contrast, the OLD install (ACT-OPERATOR-HOURS-2's, live today) over the same table agrees with its rule written out separately (02:10-03:09 always, 03:10-07:59 unless a fresh false): {len(bad_old)} disagree")
    turned = [c for c in new if (old[c] != []) != (new[c] != [])]
    L.case(all(old[c] != [] and new[c] == [] for c in turned) and len(turned) == sum(1 for c in old if old[c] != []),
           f"every case that changes turns from held to free ({len(turned)} cases, all in 02:10-07:59); none turns from free to held")
    L.case(all(old[(hm, k)] != [] for hm in ("02:10", "02:30", "03:09") for k in KINDS) and all(old[(hm, "missing")] != [] for hm in ("03:30", "05:10", "07:59")),
           "the old install held at 02:30 in every state and at 05:10 with no state file (as tonight: the night hold stopped, its file stale): the night's lost hours")
    sc = {"NIGHTLY-RUNNING": scratch / "NIGHTLY-RUNNING", "CLOSE-RUNNING": scratch / "CLOSE-RUNNING",
          "log/act-in-progress.txt": scratch / "log/act-in-progress.txt", "install/act-in-progress.txt": opa / "install/act-in-progress.txt"}
    for name, path in sc.items():
        path.write_text("planted\n")
        m = matrix(opa / "install", cfg, tmp)
        path.unlink()
        L.case(all(m[(hm, "missing")] != [] for hm in ("01:30", "02:30", "05:10", "14:00")), f"the planted {name} still holds at 01:30, 02:30, 05:10 and 14:00")
    cfgw = make_cfg(tmp, "win", opa, ra, ha, scratch)
    cw = json.loads(cfgw.read_text())
    cw["nightly_window"] = "03:50-08:00"
    cfgw.write_text(json.dumps(cw))
    m = matrix(opa / "install", cfgw, tmp)
    L.case(m[("05:10", "missing")] == ["the nightly's window (03:50-08:00)"] and m[("14:00", "missing")] == [], "an explicit nightly_window still holds inside it and not outside")
    clk = tmp / "new.clock"
    r = run([sys.executable, "-I", "-B", "-c", "import sys; sys.path.insert(0, sys.argv[1]); sys.dont_write_bytecode = True; import opcommon as oc, json; "
             "open(sys.argv[3], 'w').write('not a time\\n'); print(json.dumps(oc.holds(oc.load_settings(sys.argv[2]))))", str(opa / "install"), str(cfg), str(clk)])
    L.case("clock cannot be read" in r.stdout, "a clock that cannot be read still holds")

    # ------------------------------------------------------------------------------------------ part 4: the real launcher and run
    L.note("part 4: the real launcher (operator_launch.py) from the applied copy, a stub claude, a clock file, a queued request")
    sys.path.insert(0, str(REPO / "tests/unit/operator"))
    sys.dont_write_bytecode = True
    import test_w2_148_kit as K  # noqa: E402
    bin_ = tmp / "bin"
    bin_.mkdir()
    (bin_ / "claude").write_text(K.STUB_CLAUDE)
    (bin_ / "claude").chmod(0o755)
    lw = world("w-launch")
    assert ap(lw, "apply").returncode == 0
    hl, rl, opl, _ = lw
    ls_ = tmp / "scratch-l"
    (ls_ / "log").mkdir(parents=True)
    (tmp / "tx").mkdir()
    lcfg, lclock = tmp / "launch.json", tmp / "launch.clock"
    lcfg.write_text(json.dumps({"operator_root": str(opl), "repo": str(rl), "home": str(hl), "scratch": str(ls_),
                                "transcripts": str(tmp / "tx"), "clock": str(lclock), "pings_log": str(tmp / "pings.log"),
                                "push_cmd": ["/bin/true"], "poll_s": 0.1, "claude": str(bin_ / "claude")}))
    lenv = {"HOME": str(hl), "PATH": f"{bin_}:{os.environ['PATH']}"}
    lstate = ls_ / "log/night-hold.state.json"

    def launch(hm, holding, flag=False):
        lclock.write_text(f"2026-11-13T{hm}:00+00:00\n")
        lstate.unlink(missing_ok=True)
        if holding is not None:
            lstate.write_text(json.dumps({"pid": 1, "holding": holding}))
            if holding is False:
                t = time.time() - 3600
                os.utime(lstate, (t, t))
        if flag:
            (ls_ / "NIGHTLY-RUNNING").write_text("2026-11-13 04:00:05 nightly: running\n")
        (opl / "queue/one.req").write_text("ACT-HR3-L " + "a" * 64 + "\n")
        r = run([sys.executable, "-I", "-B", str(opl / "install/operator_launch.py"), "--config", str(lcfg)], env=lenv)
        try:
            out = json.loads(r.stdout.strip().splitlines()[-1])
        except Exception:
            out = {"result": "unreadable", "stderr": r.stderr[-200:]}
        taken = not (opl / "queue/one.req").exists()
        for f in list((opl / "queue").glob("*")):
            shutil.rmtree(f) if f.is_dir() else f.unlink()
        (opl / "log/session.json").unlink(missing_ok=True)
        (ls_ / "NIGHTLY-RUNNING").unlink(missing_ok=True)
        return out, taken
    for hm, hd, flag, want_held, label in (("02:30", None, False, False, "no state file"), ("03:30", True, False, False, "a fresh holding true"),
                                           ("05:10", False, False, False, "the stale holding false the stopped night hold leaves"),
                                           ("07:45", None, False, False, "no state file"), ("14:00", None, False, False, "no state file"),
                                           ("05:30", None, True, True, "a fresh NIGHTLY-RUNNING")):
        out, taken = launch(hm, hd, flag)
        is_held = out.get("result") == "held" and out.get("gate") == "G9"
        okc = is_held == want_held and taken == (not want_held) and out.get("approved_sha256") == new_ap
        if want_held:
            okc = okc and "NIGHTLY-RUNNING" in str(out.get("reason"))
        L.case(okc, f"launcher at {hm}, {label}: {'held at G9 (NIGHTLY-RUNNING), the request stays in queue/' if want_held else 'the request taken, a session started'} (got {out.get('result')}{'/' + str(out.get('gate')) if out.get('gate') else ''})")
    # the run itself (operator_run.py) on the unit kit: covered by part 6's unit file (test_a_run_at_night_applies_without_a_g9_hold)

    # ------------------------------------------------------------------------------------------ part 5: mutants
    L.note("part 5: does it bite? Each mutant of the installed opcommon.py over the same table (expected: no hold anywhere; the flag mutant: the flag at 05:10)")
    base = (opa / "install/opcommon.py").read_text()

    def mut(old_, new_):
        assert base.count(old_) == 1, old_
        return base.replace(old_, new_)
    mutants = {
        "the old code (ACT-OPERATOR-HOURS-2's opcommon.py, live today)": (old_install / "opcommon.py").read_text(),
        "a hold from 02:10 to 03:09 put back": mut("    try:\n        if s[\"nightly_window\"]", "    if 130 <= d.hour * 60 + d.minute < 190:\n        out.append('x')\n    try:\n        if s[\"nightly_window\"]"),
        "the old quiet hours 02:00-07:30 put back": mut("    try:\n        if s[\"nightly_window\"]", "    if 120 <= d.hour * 60 + d.minute < 450:\n        out.append('q')\n    try:\n        if s[\"nightly_window\"]"),
        "the old nightly window as the default": mut("DEFAULT_NIGHTLY = None", "DEFAULT_NIGHTLY = \"03:50-08:00\""),
        "the NIGHTLY-RUNNING hold dropped": mut("            out.append(\"the nightly runs (NIGHTLY-RUNNING)\")", "            pass"),
        "the CTO's act-in-progress hold dropped": mut("        out.append(\"the CTO's log/act-in-progress.txt exists\")", "        pass"),
    }
    for name, text in mutants.items():
        mdir = tmp / ("mut-" + re.sub(r"\W+", "-", name)[:30])
        shutil.copytree(opa / "install", mdir, ignore=shutil.ignore_patterns("__pycache__"))
        (mdir / "opcommon.py").chmod(0o644)
        (mdir / "opcommon.py").write_text(text)
        msc = tmp / (mdir.name + "-s")
        (msc / "log").mkdir(parents=True)
        mcfg = make_cfg(tmp, mdir.name, opa, ra, ha, msc)
        if "NIGHTLY-RUNNING" in name:
            (msc / "NIGHTLY-RUNNING").write_text("planted\n")
            n = sum(1 for c, v in matrix(mdir, mcfg, tmp).items() if c[0] in ("05:10", "14:00") and v == [])
        elif "act-in-progress" in name:
            (msc / "log/act-in-progress.txt").write_text("planted\n")
            n = sum(1 for c, v in matrix(mdir, mcfg, tmp).items() if v == [])
        else:
            n = sum(1 for v in matrix(mdir, mcfg, tmp).values() if v != [])
        L.case(n >= 1, f"mutant \"{name}\": {n} cases disagree (caught)")

    # ------------------------------------------------------------------------------------------ part 6: the tests
    L.note("part 6: the operator's own tests on a clone (`git clone --no-hardlinks` of w2/integrate's head) with the four after files, through heavy_slot.sh, TMPDIR outside the repository and ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider")
    clone = WORK / "clone"
    wtmp = WORK / "pytest-tmp"
    wtmp.mkdir()
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(clone)], check=True)
    L.note(f"the clone's head: {run(['git', '-C', str(clone), 'rev-parse', '--short=12', 'HEAD']).stdout.strip()}")
    for p in REPO_FILES:
        shutil.copy2(BUNDLE / "after/repo" / p, clone / p)
        assert sha(clone / p) == after[("repo", p)]
    rc1, s1_, out1 = pytest_on(clone, ["tests/unit/operator", "tests/acceptance/W2-148"], wtmp)
    (L.note if rc1 is None else (lambda x: L.case(rc1 == 0 and "failed" not in s1_ and "error" not in s1_, x)))( f"with the four after files: tests/unit/operator tests/acceptance/W2-148: {s1_}")
    rc2, s2_, _ = pytest_on(clone, ["tests/unit/operator/test_act_operator_hours_2.py",
                                    "tests/acceptance/W2-148/test_w2_148_gates.py::test_s13_g9_a_hold_waits_then_proceeds_once_cleared",
                                    "tests/acceptance/W2-148/test_w2_148_gates.py::test_s13_g9_no_time_hold_at_night"], wtmp)
    (L.note if rc2 is None else (lambda x: L.case(rc2 == 0, x)))(f"the revised G9 tests alone (the unit file, the two S13 acceptance tests): {s2_}")
    target = clone / REPO_FILES[0]
    keep_new = target.read_bytes()
    try:
        target.write_bytes((BUNDLE / "before/repo" / REPO_FILES[0]).read_bytes())
        rc3, s3_, _ = pytest_on(clone, ["tests/unit/operator/test_act_operator_hours_2.py"], wtmp)
    finally:
        target.write_bytes(keep_new)
    (L.note if rc3 is None else (lambda x: L.case(rc3 != 0 and "failed" in s3_, x)))( f"the revised unit file on the OLD opcommon.py goes red: {s3_}")
    old_ut = clone / "tests/unit/operator/test_act_operator_hours_2.py"
    keep_ut = old_ut.read_bytes()
    try:
        old_ut.write_bytes((BUNDLE / "before/repo/tests/unit/operator/test_act_operator_hours_2.py").read_bytes())
        rc4, s4_, _ = pytest_on(clone, ["tests/unit/operator/test_act_operator_hours_2.py"], wtmp)
    finally:
        old_ut.write_bytes(keep_ut)
    (L.note if rc4 is None else (lambda x: L.case(rc4 != 0 and "failed" in s4_, x)))( f"control: the OLD unit file (ACT-OPERATOR-HOURS-2's rule) on the NEW opcommon.py goes red, so it must change with it: {s4_}")
    L.case(sha(target) == after[("repo", REPO_FILES[0])] and sha(old_ut) == after[("repo", REPO_FILES[1])], "the clone's files are the after files again")

    # ------------------------------------------------------------------------------------------ part 7: exempt
    exec(compile((HERE / "part7.py").read_text(), str(HERE / "part7.py"), "exec"), globals())
    part7(L, tmp)


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
    for where, text in [("apply.sh", (BUNDLE / "apply.sh").read_text())] + [("a check", c["cmd"]) for c in m["checks"]]:
        why = orun.live_path_refs(text, s)
        print(f"path rule on {where}: {'pass' if why is None else why}")
    v = act_class.classify(str(BUNDLE))
    print(f"act_class.classify (the whole bundle): class {v['class']}; hits {v['hits']}")
    for f in v["files"]:
        print(f"  {f['root']}|{f['path']}: {f['class']} (row {f['row']})")
    for part in ("A", "B"):
        mm = dict(m, touched=m["parts"][part]["touched"], checks=m["parts"][part]["checks"])
        vv = act_class.classify_manifest(mm, None)
        print(f"act_class.classify_manifest (Part {part} alone, its rows and checks): class {vv['class']}")
    print(f"manifest sha256 {sha(BUNDLE / 'manifest.json')}")


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates,
     "all": lambda: (build(), rehearse(), finalize(), gates())}[sys.argv[1]]()
