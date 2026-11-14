"""Builds and rehearses ACT-LANDING-CTO-ROUTE-1 (the landing check's route for the CTO's (b) ACTs; the owner, DEC-1167 (5)).

    python3 -I build_landing_act.py build     <BASE clone>            freeze the bundle (apply.sh, list.txt, keep.txt, before/, after/, manifest)
    python3 -I build_landing_act.py rehearse  <BASE clone> <scratch>  the rehearsal on fresh clones with a planted HOME; writes rehearsal.log
    python3 -I build_landing_act.py finalize                          the manifest with the rehearsal log's sha256
    python3 -I build_landing_act.py gates     <evidence dir>          the operator's read-only gates over the bundle

The class is the classifier's: every file is under the operator-own row, (O): the owner's operator applies it by hand."""
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from actkit import HEAVY, INSTALL, LIVE, ORCH, Log, clone, failed_ids, git, pytest, run, sha, shab, tree_state  # noqa: E402

ACT = "ACT-LANDING-CTO-ROUTE-1"
DEC = "DEC-1167 (5), DEC-1104 (2), (4), CAP-33"
BUNDLE = ORCH / "acts" / ACT
CODE = HERE / "code"
MIRROR = "governance/project/operator/landing_check.py"
TESTS = "tests/unit/operator/test_landing_cto_route.py"
INST_LC = "gov-os-operator/install/landing_check.py"
INST_AP = "gov-os-operator/install/APPROVED"
DISPATCH_ACT = "ACT-DISPATCH-NIGHTLY-SLOT-1"
DISPATCH_PATH = "governance/project/orchestration/tools/dispatch/dispatcher.py"
LIVE_EXAMPLE = "7cc654e49f9b"


def approved_after(approved_before, new_sha):
    out, hit = [], 0
    for line in approved_before.splitlines():
        s, _, name = line.partition("  ")
        if name == "landing_check.py":
            line, hit = f"{new_sha}  landing_check.py", hit + 1
        out.append(line)
    assert hit == 1
    return "\n".join(out) + "\n"


BEHAVIOUR = r'''python3 -I - <<'EOF'
import hashlib, json, os, subprocess, sys, tempfile
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.environ["HOME"], "gov-os-operator", "install"))
import landing_check as lc
T = tempfile.mkdtemp(); R = T + "/r"; A = T + "/acts/ACT-C-1"; L = T + "/approvals.jsonl"; P = ".claude/hooks/x.py"
def g(*a):
    return subprocess.run(["git", "-C", R, *a], check=True, capture_output=True, text=True).stdout.strip()
os.makedirs(R); g("init", "-q", "-b", "main"); g("config", "user.email", "t@t"); g("config", "user.name", "t")
open(R + "/README", "w").write("x"); g("add", "-A"); g("commit", "-q", "-m", "base"); base = g("rev-parse", "HEAD")
os.makedirs(R + "/.claude/hooks"); open(R + "/" + P, "w").write("a\n")
os.makedirs(A); open(A + "/apply.sh", "w").write("#!/bin/bash\nexit 0\n")
m = json.dumps({"act": "ACT-C-1", "claimed_class": "b", "touched": [{"root": "repo", "path": P, "before": None, "after": "0" * 64}], "files": {}, "checks": []})
open(A + "/manifest.json", "w").write(m); s = hashlib.sha256(m.encode()).hexdigest()
open(L, "w").write(json.dumps({"act": "ACT-C-1", "manifest": s, "route": "the CTO"}) + "\n")
g("add", "-A"); g("commit", "-q", "-m", "act", "-m", "Role: orchestrator\nAct: ACT-C-1\nAct-sha: " + s)
passes = lc.check(R, base + "..HEAD", approvals=L, acts_dir=T + "/acts")
open(L, "w").write("")
flagged = lc.check(R, base + "..HEAD", approvals=L, acts_dir=T + "/acts")
ok = passes == [] and len(flagged) == 1
import shutil; shutil.rmtree(T)
print("landing check: the CTO route passes a commit with all three conditions and flags it when the approvals line is gone" if ok else "FAIL " + repr((passes, flagged)))
sys.exit(0 if ok else 1)
EOF'''


def checks(new_lc, after_ap, new_tests):
    return [
        {"cmd": f'sha256sum "$HOME/{INST_LC}" | grep -c {new_lc}', "exit": 0, "count": 1},
        {"cmd": f'sha256sum "$HOME/{INST_AP}" | grep -c {after_ap}', "exit": 0, "count": 1},
        {"cmd": f'cmp -s {MIRROR} "$HOME/{INST_LC}"', "exit": 0, "count": None},
        {"cmd": f"sha256sum {TESTS} | grep -c {new_tests}", "exit": 0, "count": 1},
        {"cmd": f'grep -c "  landing_check.py$" "$HOME/{INST_AP}"', "exit": 0, "count": 1},
        {"cmd": BEHAVIOUR, "exit": 0, "count": None},
    ]


def write_manifest(rehearsal_sha):
    rows = [ln.split("|") for ln in (BUNDLE / "list.txt").read_text().splitlines()]
    touched = [{"root": r, "path": p, "before": None if b == "null" else b, "after": a} for r, p, b, a in rows]
    files = {}
    for side in ("before", "after"):
        for f in sorted((BUNDLE / side).rglob("*")):
            if f.is_file():
                files[str(f.relative_to(BUNDLE))] = sha(f)
    for n in ("apply.sh", "list.txt", "keep.txt"):
        files[n] = sha(BUNDLE / n)
    after = {p: a for r, p, b, a in rows}
    m = {"act": ACT, "dec": DEC, "author": "cto", "claimed_class": "O", "touched": touched, "files": files,
         "checks": checks(after[INST_LC], after[INST_AP], after[TESTS]), "commands": []}
    if rehearsal_sha:
        files["rehearsal.log"] = rehearsal_sha
        m["rehearsal"] = {"log": "rehearsal.log", "sha256": rehearsal_sha}
    (BUNDLE / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    return sha(BUNDLE / "manifest.json")


def build(base):
    if BUNDLE.exists():
        assert not (BUNDLE / "review.md").exists() or "not written yet" in (BUNDLE / "review.md").read_text(), \
            "the bundle holds a written review: move it aside before a rebuild"
        keep_review = (BUNDLE / "review.md").read_text() if (BUNDLE / "review.md").exists() else None
        shutil.rmtree(BUNDLE)
    else:
        keep_review = None
    live_ap = (INSTALL / "APPROVED").read_text()
    for line in live_ap.splitlines():
        s, _, name = line.partition("  ")
        assert sha(INSTALL / name) == s, f"the live install is not as APPROVED says: {name}"
    before_lc = (INSTALL / "landing_check.py").read_bytes()
    assert before_lc == (CODE / "landing_check.py.before").read_bytes(), "code/landing_check.py.before is not the install's file"
    assert before_lc == (LIVE / MIRROR).read_bytes() == git(LIVE, "show", f"HEAD:{MIRROR}")[1].encode() + b"\n", \
        "the source copy is not the install's file, or the main tree's differs from HEAD"
    assert git(LIVE, "status", "--porcelain", "--untracked-files=all", "--", MIRROR, TESTS)[1] == "", "a listed path is dirty"
    after_lc = (CODE / "landing_check.py").read_bytes()
    tests = (CODE / "test_landing_cto_route.py").read_bytes()
    after_ap = approved_after(live_ap, shab(after_lc))
    rows = [("repo", MIRROR, before_lc, after_lc), ("repo", TESTS, None, tests),
            ("home", INST_LC, before_lc, after_lc), ("home", INST_AP, live_ap.encode(), after_ap.encode())]
    lines = []
    for root, p, b, a in rows:
        for side, data in (("before", b), ("after", a)):
            if data is None:
                continue
            f = BUNDLE / side / root / p
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_bytes(data)
        lines.append(f"{root}|{p}|{shab(b) if b is not None else 'null'}|{shab(a)}")
    (BUNDLE / "list.txt").write_text("\n".join(lines) + "\n")
    (BUNDLE / "keep.txt").write_text("\n".join(ln for ln in live_ap.splitlines() if not ln.endswith("  landing_check.py")) + "\n")
    shutil.copy(HERE / "apply.sh", BUNDLE / "apply.sh")
    (BUNDLE / "apply.sh").chmod(0o755)
    (BUNDLE / "review.md").write_text(keep_review or f"# {ACT}: the ACT review\n\nReview: not written yet\n")
    write_manifest(None)
    print(f"built {BUNDLE}; manifest {sha(BUNDLE / 'manifest.json')}")


# ----------------------------------------------------------------------------------------------------------- rehearsal
def plant_home(home):
    if home.exists():
        shutil.rmtree(home)
    inst = home / "gov-os-operator/install"
    for f in INSTALL.rglob("*"):
        rel = f.relative_to(INSTALL)
        if "__pycache__" in rel.parts:
            continue
        d = inst / rel
        if f.is_dir():
            d.mkdir(parents=True, exist_ok=True)
        else:
            d.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, d)
            os.chmod(d, 0o444)
    for sub in ("log", "queue"):
        (home / "gov-os-operator" / sub).mkdir(parents=True, exist_ok=True)
    return home


def op_status(root):
    return git(root, "status", "--porcelain", "--untracked-files=all", "--", "governance/project/operator", "tests/unit/operator")[1]


def tree_hash(root):
    return {str(f.relative_to(root)): sha(f) for f in sorted(Path(root).rglob("*")) if f.is_file() and "__pycache__" not in f.parts}


def rehearse(base, scratch):
    log = Log(BUNDLE / "rehearsal.log")
    scratch.mkdir(parents=True, exist_ok=True)
    tmp = scratch / "tmp"
    ev = scratch / "evidence"
    ev.mkdir(exist_ok=True)
    rows = [ln.split("|") for ln in (BUNDLE / "list.txt").read_text().splitlines()]
    listed = {(r, p): (b, a) for r, p, b, a in rows}
    live_before = {"inst": tree_hash(INSTALL), "tree": op_status(LIVE), "mirror": sha(LIVE / MIRROR)}
    live_acts_manifest = sha(ORCH / "acts" / DISPATCH_ACT / "manifest.json")
    live_approvals = sha(ORCH / "log" / "act-approvals.jsonl")

    def apply(cwd, home, step, expect=0):
        env = dict(os.environ, HOME=str(home))
        code, out = run(["bash", str(BUNDLE / "apply.sh"), step], cwd=cwd, env=env)
        return code, out.strip()

    def state(cwd, home):
        out = {}
        for (root, p), (b, a) in listed.items():
            f = (home if root == "home" else cwd) / p
            out[(root, p)] = sha(f) if f.is_file() else "null"
        return out

    def side(cwd, home, which):
        i = 0 if which == "before" else 1
        return all(state(cwd, home)[k] == v[i] for k, v in listed.items())

    def run_checks(cwd, home, manifest):
        res = []
        for c in manifest["checks"]:
            code, out = run(["bash", "-c", c["cmd"]], cwd=cwd, env=dict(os.environ, HOME=str(home)))
            last = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
            cnt_ok = c["count"] is None or last[0].strip() == str(c["count"])
            res.append(code == c["exit"] and cnt_ok)
        return res

    manifest = json.loads((BUNDLE / "manifest.json").read_text())
    log.say(f"{ACT} rehearsal; bundle {BUNDLE}; base: a fresh clone of w2/integrate")
    log.head("A. the bundle")
    log.case(all(sha(BUNDLE / pth) == h for pth, h in manifest["files"].items() if pth != "rehearsal.log"), "A1 every file the manifest names hashes as it says")
    log.case([f"{t['root']}|{t['path']}|{t['before'] or 'null'}|{t['after']}" for t in manifest["touched"]] == [ln for ln in (BUNDLE / "list.txt").read_text().splitlines()], "A2 list.txt equals the manifest's touched list")
    log.case(sha(INSTALL / "landing_check.py") == listed[("home", INST_LC)][0] == listed[("repo", MIRROR)][0], "A3 the live install's landing_check.py and the source copy are the frozen before")
    log.case(sha(INSTALL / "APPROVED") == listed[("home", INST_AP)][0], "A4 the live APPROVED is the frozen before")
    log.case(subprocess.run(["bash", "-n", str(BUNDLE / "apply.sh")]).returncode == 0, "A5 apply.sh parses")
    log.case(not list(BUNDLE.rglob("__pycache__")), "A6 no __pycache__ in the bundle")

    log.head("B. a fresh clone of w2/integrate, a planted HOME (the live install is never touched)")
    R, home = scratch / "clone", plant_home(scratch / "home")
    head = clone(base, R)
    log.note(f"clone at {head[:12]}; HOME planted at {home}")
    log.case(tree_hash(home / "gov-os-operator/install") == live_before["inst"], "B0 the planted install is a copy of the live one")
    code, out = apply(R, home, "check")
    log.case(code == 0 and "ready to apply" in out, "B1 apply.sh check: ready (exit 0)", out.splitlines()[-1] if out else "")
    pre = run_checks(R, home, manifest)
    log.case(pre[0] is False and pre[1] is False and pre[3] is False and pre[5] is False, f"B2 the manifest's checks before the apply: the install, APPROVED, tests and behaviour checks refuse ({pre})")
    code, out = apply(R, home, "apply")
    log.note(out.replace("\n", " | ")[:400])
    log.case(code == 0 and "state applied" in out and "APPROVED check: ok" in out, "B3 apply (exit 0; the install's own APPROVED check ok)")
    log.case(side(R, home, "after"), "B4 every listed file is the frozen after, byte for byte")
    modes = {p: stat.S_IMODE(os.stat((home if r == "home" else R) / p).st_mode) for (r, p) in listed}
    log.case(modes[INST_LC] == 0o444 and modes[INST_AP] == 0o444 and modes[MIRROR] == 0o644 and modes[TESTS] == 0o644, "B5 modes: the install's two files 0444, the repository's 0644", str({k.split('/')[-1]: oct(v) for k, v in modes.items()}))
    code, out = apply(R, home, "verify")
    log.case(code == 0, "B6 verify (exit 0)")
    post = run_checks(R, home, manifest)
    log.case(all(post), f"B7 the manifest's six checks after the apply ({post})")
    st = run(["git", "-C", str(R), "status", "--porcelain", "--untracked-files=all"])[1].splitlines()
    log.case(sorted(ln[3:] for ln in st) == sorted([MIRROR, TESTS]), "B8 the clone's changed set is the two repository paths", ", ".join(sorted(ln[3:] for ln in st)))
    log.case(tree_hash(home / "gov-os-operator/install") != live_before["inst"] and
             {k for k, v in tree_hash(home / "gov-os-operator/install").items() if live_before["inst"].get(k) != v} == {"landing_check.py", "APPROVED"},
             "B9 in the planted install only landing_check.py and APPROVED changed")
    code, out = apply(R, home, "apply")
    log.case(code == 0 and "nothing to do" in out, "B10 apply again: nothing to do")
    code, out = apply(R, home, "check")
    log.case(code == 3, "B11 check after the apply refuses (already applied, exit 3)")
    code, out = apply(R, home, "undo")
    log.case(code == 0 and side(R, home, "before") and tree_hash(home / "gov-os-operator/install") == live_before["inst"], "B12 undo: byte for byte the before (install back to the live copy)")
    log.case(git(R, "status", "--porcelain", "--untracked-files=all")[1] == "", "B13 the clone is clean after the undo")
    log.case(apply(R, home, "undo")[0] == 0, "B14 undo again: nothing to do (exit 0)")
    code, out = apply(R, home, "apply")
    log.case(code == 0 and side(R, home, "after"), "B15 apply again gives the same bytes")

    log.head("C. refusals (each on its own clone and planted HOME; nothing is touched when one fires)")

    def fresh(name):
        c, h = scratch / f"c-{name}", plant_home(scratch / f"h-{name}")
        clone(base, c, head)
        return c, h

    c, h = fresh("moved")
    (h / "gov-os-operator/install/landing_check.py").chmod(0o644)
    (h / "gov-os-operator/install/landing_check.py").write_text("# changed\n")
    code, out = apply(c, h, "check")
    log.case(code == 3 and "moved: home/" + INST_LC in out, "C1 a changed install file: check refuses (exit 3)")
    code, out = apply(c, h, "apply")
    log.case(code == 3 and sha(c / MIRROR) == listed[("repo", MIRROR)][0], "C2 apply refuses and touches nothing (exit 3)")
    c, h = fresh("other")
    (h / "gov-os-operator/install/opcommon.py").chmod(0o644)
    (h / "gov-os-operator/install/opcommon.py").write_text("# another install change\n")
    code, out = apply(c, h, "check")
    log.case(code == 3 and "install/opcommon.py" in out, "C3 another install file changed: refused (exit 3)")
    c, h = fresh("stray")
    (h / "gov-os-operator/install/extra.py").write_text("x\n")
    code, out = apply(c, h, "apply")
    log.case(code == 3 and "not listed" in out and side(c, h, "before"), "C4 a stray file in install/: refused, nothing applied")
    c, h = fresh("busy")
    (h / "gov-os-operator/queue/ACT-X-12345678.req").write_text("x\n")
    code, out = apply(c, h, "apply")
    log.case(code == 6 and "busy" in out and side(c, h, "before"), "C5 a request waiting in queue/: busy (exit 6), nothing applied")
    c, h = fresh("freeze")
    (h / "gov-os-operator/install/act-in-progress.txt").write_text("x\n")
    code, out = apply(c, h, "apply")
    log.case(code == 6 and side(c, h, "before"), "C6 the operator's commit freeze present: busy (exit 6)")
    c, h = fresh("mirror")
    (c / MIRROR).write_text("# the source copy moved\n")
    run(["git", "-C", str(c), "commit", "-qam", "moved copy"])
    code, out = apply(c, h, "check")
    log.case(code == 3 and "moved: repo/governance/project/operator/landing_check.py" in out, "C7 a source copy that is not the before: refused (exit 3)")
    c, h = fresh("dirty")
    (c / TESTS).parent.mkdir(parents=True, exist_ok=True)
    (c / TESTS).write_text("# someone's file\n")
    code, out = apply(c, h, "check")
    log.case(code == 3 and TESTS in out, "C8 the new test file already there: refused (exit 3)")
    c, h = fresh("half")
    put = BUNDLE / "after/repo" / MIRROR
    shutil.copyfile(put, c / MIRROR)
    code, out = apply(c, h, "check")
    log.case(code == 3, "C9 a half-applied state (the source copy already the after): check refuses (exit 3)")
    c, h = fresh("lock")
    import fcntl
    os.makedirs(h / "gov-os-operator/log", exist_ok=True)
    fd = os.open(h / "gov-os-operator/log/launch.lock", os.O_CREAT | os.O_RDWR)
    fcntl.flock(fd, fcntl.LOCK_EX)
    code, out = apply(c, h, "apply")
    os.close(fd)
    log.case(code == 6 and "launch is running" in out and side(c, h, "before"), "C10 a launch holding log/launch.lock: busy (exit 6), nothing changed")

    log.head("D. the owner's steps literally on the applied clone (apply.sh, the two paths staged, the commit, the undo)")
    base_head = git(R, "rev-parse", "HEAD")[1]
    code, _ = run(["git", "-C", str(R), "add", MIRROR, TESTS])
    log.case(code == 0 and sorted(git(R, "diff", "--cached", "--name-only")[1].splitlines()) == sorted([MIRROR, TESTS]), "D1 the two repository paths staged, and only them")
    code, out = run(["git", "-C", str(R), "commit", "-q", "-m", f"{ACT}: the landing check passes the CTO's (b) ACTs", "--trailer", "Task: DAEO-sdxk",
                     "--trailer", "Implements: DEC-1167", "--trailer", "Role: owner", "--", MIRROR, TESTS])
    log.case(code == 0, "D2 the commit with Role: owner", out.strip()[-100:])
    c1 = git(R, "rev-parse", "HEAD")[1]
    code, out = run([sys.executable, "-I", str(home / "gov-os-operator/install/landing_check.py"), "--repo", str(R), f"{base_head}..{c1}"])
    log.case(code == 0 and json.loads(out.strip().splitlines()[-1]) == [], "D3 the planted (new) landing check does not flag that commit (Role: owner)")
    code, out = apply(R, home, "undo")
    log.case(code == 0 and side(R, home, "before"), "D4 apply.sh undo (install and repository paths back)")
    run(["git", "-C", str(R), "add", "-A", MIRROR, TESTS])
    code, out = run(["git", "-C", str(R), "commit", "-q", "-m", f"{ACT}: undo", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: owner"])
    log.case(code == 0, "D5 the undo commit")
    log.case(git(R, "diff", "--stat", base_head, "HEAD", "--", MIRROR, TESTS)[1] == "", "D6 an empty diff over the paths against the start")
    code, _ = apply(R, home, "apply")
    log.case(code == 0 and side(R, home, "after"), "D7 and the apply goes through again")

    log.head("E. the unit tests (each through heavy_slot.sh, TMPDIR outside the repository)")
    # E1: the new tests on the before code (the source copy before, the tests added): red
    cb, hb = fresh("tests-before")
    shutil.copyfile(BUNDLE / "after/repo" / TESTS, cb / TESTS)
    code, last = pytest(cb, [TESTS], tmp / "e1", ev / "e1-tests-before.txt")
    nb = len(failed_ids(ev / "e1-tests-before.txt"))
    log.case(code != 0 and nb > 20, f"E1 the new tests on the before code: red ({last})", f"{nb} failed")
    # E2: after
    code, last = pytest(R, [TESTS], tmp / "e2", ev / "e2-tests-after.txt")
    log.case(code == 0, f"E2 the new tests on the after code: green ({last})")
    code, last = pytest(R, ["tests/unit/operator"], tmp / "e3", ev / "e3-unit-operator.txt")
    log.case(code == 0, f"E3 tests/unit/operator after: green ({last})")
    code, last = pytest(R, ["tests/acceptance/W2-148"], tmp / "e4", ev / "e4-w2-148.txt")
    log.case(code == 0, f"E4 tests/acceptance/W2-148 after (the landing check's own acceptance test among them): green ({last})")
    # E5: mutation: each condition removed in turn, the new tests go red
    mutants = {
        "condition 1 (the approvals line)": ("    if not cto_approved(approvals, act, sha):", "    if False:"),
        "condition 1 (the route names the CTO)": ('route.strip().lower().startswith("the cto")', '"cto" in route.lower()'),
        "the manifest is found by its hash": ("            if hashlib.sha256(raw).hexdigest() != sha:", "            if False:"),
        "condition 2 (the manifest claims b)": ('    if manifest.get("claimed_class") != "b":', "    if False:"),
        "condition 2 (the classifier's vote on the bundle)": ('    if act_class.classify(bundle, rules)["class"] != "b":', "    if False:"),
        "condition 2 (the class of the commit's paths)": ('if not classes or act_class.top(*classes.values()) != "b":', "if not classes:"),
        "condition 3 (the paths are the touched list)": ('    if sorted(t.get("path") for t in touched) != sorted(paths):', "    if False:"),
        "condition 3 (every touched root is repo)": ('t.get("root") != "repo"\n', "False\n"),
    }
    for i, (name, (old, new)) in enumerate(mutants.items()):
        cm, hm = fresh(f"mut{i}")
        for rel in (MIRROR, TESTS):
            shutil.copyfile(BUNDLE / "after/repo" / rel, cm / rel)
        src = (cm / MIRROR).read_text()
        assert src.count(old) == 1, name
        (cm / MIRROR).write_text(src.replace(old, new))
        code, last = pytest(cm, [TESTS], tmp / f"m{i}", ev / f"e5-mutant-{i}.txt")
        log.case(code != 0, f"E5.{i + 1} without {name}: the new tests go red ({last})")
        shutil.rmtree(cm)

    log.head("F. the live example and the history (the planted install's landing check, run as landing_select.sh runs it)")
    new_cli = home / "gov-os-operator/install/landing_check.py"
    old_cli = INSTALL / "landing_check.py"

    def lc_run(cli, repo, rng):
        code, out = run([sys.executable, "-I", str(cli), "--repo", str(repo), rng])
        return code, json.loads(out.strip().splitlines()[-1])

    parent = git(LIVE, "rev-parse", f"{LIVE_EXAMPLE}^")[1]
    full = git(LIVE, "rev-parse", LIVE_EXAMPLE)[1]
    code, items = lc_run(new_cli, LIVE, f"{parent}..{full}")
    log.case(code == 0 and [i["commit"] for i in items] == [full], f"F1 {LIVE_EXAMPLE} (no Act: trailer) is flagged by the new check, as by the old", items[0]["reason"] if items else "")
    code, items_old = lc_run(old_cli, LIVE, f"{parent}..{full}")
    log.case([i["commit"] for i in items_old] == [full], "F2 and by the old check")
    # a clone at the live example's parent, the ACT's own after file committed as the CTO would commit it
    cx = scratch / "live-example"
    clone(LIVE, cx, parent)
    dman = ORCH / "acts" / DISPATCH_ACT / "manifest.json"
    dsha = sha(dman)
    shutil.copyfile(ORCH / "acts" / DISPATCH_ACT / "after/repo" / DISPATCH_PATH, cx / DISPATCH_PATH)
    run(["git", "-C", str(cx), "add", DISPATCH_PATH])
    run(["git", "-C", str(cx), "commit", "-q", "-m", f"{DISPATCH_ACT}: as the CTO would commit it", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator",
         "--trailer", f"Act: {DISPATCH_ACT}", "--trailer", f"Act-sha: {dsha}"])
    cx_head = git(cx, "rev-parse", "HEAD")[1]
    log.note(f"{DISPATCH_ACT}: manifest {dsha[:8]}, in the live approvals log with the route: " +
             next((json.loads(ln)["route"][:40] for ln in (ORCH / "log/act-approvals.jsonl").read_text().splitlines() if dsha in ln), "none"))
    code, items = lc_run(new_cli, cx, f"{parent}..{cx_head}")
    log.case(code == 0 and items == [], f"F3 the same commit with Role: orchestrator, Act: and Act-sha: passes the new check ({DISPATCH_ACT}, the live approvals line and the live bundle, read only)")
    code, items = lc_run(old_cli, cx, f"{parent}..{cx_head}")
    log.case([i["commit"] for i in items] == [cx_head], "F4 and is a P1 for the old check")
    run(["git", "-C", str(cx), "commit", "-q", "--amend", "-m", "x", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator",
         "--trailer", f"Act: {DISPATCH_ACT}", "--trailer", f"Act-sha: {'0' * 64}"])
    code, items = lc_run(new_cli, cx, f"{parent}..{git(cx, 'rev-parse', 'HEAD')[1]}")
    log.case(len(items) == 1 and "the CTO's route refuses" in items[0]["reason"], "F5 with a wrong Act-sha: a P1 that says why", items[0]["reason"][-120:] if items else "")
    run(["git", "-C", str(cx), "reset", "-q", "--hard", cx_head])
    (cx / DISPATCH_PATH).write_text((cx / DISPATCH_PATH).read_text() + "\n# one more line\n")
    (cx / "governance/project/orchestration/tools/sentinel.py").write_text("# x\n")
    run(["git", "-C", str(cx), "add", "-A"])
    run(["git", "-C", str(cx), "commit", "-q", "-m", "extra path", "--trailer", "Task: DAEO-sdxk", "--trailer", "Role: orchestrator",
         "--trailer", f"Act: {DISPATCH_ACT}", "--trailer", f"Act-sha: {dsha}"])
    code, items = lc_run(new_cli, cx, f"{cx_head}..{git(cx, 'rev-parse', 'HEAD')[1]}")
    log.case(len(items) == 1 and "touched list" in items[0]["reason"], "F6 the same ACT with one more path in the commit: a P1 (the paths are not the touched list)")
    old_range = f"{base_head}~300..{base_head}"
    code, a = lc_run(old_cli, R, old_range)
    code2, b = lc_run(new_cli, R, old_range)
    log.case(code == code2 == 0 and a == b, f"F7 on the last 300 first-parent commits of w2/integrate the old and the new check print the same {len(a)} items")

    log.head("G. the operator's read-only gates, and the classifier")
    sys.path.insert(0, str(INSTALL))
    sys.dont_write_bytecode = True
    import act_class
    import opcommon as oc
    import operator_run as orun
    try:
        orun.validate_manifest(manifest)
        v = True
    except ValueError as e:
        v = str(e)
    log.case(v is True, "G1 validate_manifest (the operator's own): pass", "" if v is True else v)
    try:
        orun.check_act(manifest, ACT)
        v = True
    except oc.Refused as e:
        v = str(e)
    log.case(v is True, "G2 check_act: pass")
    try:
        orun.path_rule(str(BUNDLE), manifest, oc.load_settings())
        v = True
    except oc.Refused as e:
        v = str(e)
    log.case(v is True, "G3 path_rule: pass", "" if v is True else v)
    cls = act_class.classify(str(BUNDLE))
    log.case(cls["class"] == "O" and {f["row"] for f in cls["files"]} <= {"operator-own", "unknown"} and not cls["hits"],
             f"G4 act_class: class {cls['class']}; rows {sorted({f['row'] for f in cls['files']})}; hits {cls['hits']}")
    for f in cls["files"]:
        log.note(f"{f['root']}|{f['path']}: {f['class']} ({f['row']})")
    unnamed = sorted(str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file()
                     and str(p.relative_to(BUNDLE)) not in set(manifest["files"]) | {"manifest.json", "review.md", "rehearsal.log"})
    log.case(not unnamed and not list(BUNDLE.rglob("__pycache__")), "G5 no unlisted file and no __pycache__ in the bundle", str(unnamed))

    log.head("H. the live files")
    log.case(tree_hash(INSTALL) == live_before["inst"], "H1 the live install is byte for byte as before")
    log.case(op_status(LIVE) == live_before["tree"] and sha(LIVE / MIRROR) == live_before["mirror"], "H2 the main tree's tracked status and the source copy are unchanged")
    log.case(sha(ORCH / "acts" / DISPATCH_ACT / "manifest.json") == live_acts_manifest and sha(ORCH / "log/act-approvals.jsonl") == live_approvals,
             "H3 the live approvals log and the dispatch ACT's manifest were only read")
    n = log.finish()
    shutil.copyfile(BUNDLE / "rehearsal.log", scratch / "rehearsal.copy.log")
    return n


def finalize():
    s = write_manifest(sha(BUNDLE / "rehearsal.log"))
    print(f"manifest sha256 {s}")


def gates(evid):
    sys.path.insert(0, str(INSTALL))
    sys.dont_write_bytecode = True
    import act_class
    import opcommon as oc
    import operator_run as orun
    out = [f"manifest sha256: {sha(BUNDLE / 'manifest.json')}"]
    m = json.loads((BUNDLE / "manifest.json").read_text())
    for name, fn in (("validate_manifest", lambda: orun.validate_manifest(m)), ("check_act", lambda: orun.check_act(m, ACT)),
                     ("path_rule", lambda: orun.path_rule(str(BUNDLE), m, oc.load_settings()))):
        try:
            fn()
            out.append(f"{name}: pass")
        except (ValueError, oc.Refused) as e:
            out.append(f"{name}: FAIL {e}")
    bad = [p for p, h in m["files"].items() if sha(BUNDLE / p) != h]
    named = set(m["files"]) | {"manifest.json", "review.md"}
    unnamed = sorted(str(p.relative_to(BUNDLE)) for p in BUNDLE.rglob("*") if p.is_file() and str(p.relative_to(BUNDLE)) not in named)
    out.append(f"hash mismatches: {bad} ; unnamed on disk: {unnamed}")
    cls = act_class.classify(str(BUNDLE))
    out.append(f"act_class: class {cls['class']}; rows {sorted({f['row'] for f in cls['files']})}; hits {cls['hits']}")
    Path(evid).mkdir(parents=True, exist_ok=True)
    (Path(evid) / "operator_gates.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "build":
        build(Path(sys.argv[2]))
    elif cmd == "rehearse":
        sys.exit(1 if rehearse(Path(sys.argv[2]), Path(sys.argv[3])) else 0)
    elif cmd == "finalize":
        finalize()
    elif cmd == "gates":
        gates(sys.argv[2])
