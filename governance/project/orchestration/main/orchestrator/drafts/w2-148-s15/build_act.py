#!/usr/bin/env python3
"""ACT-W2-148-S15-1 (DEC-1142 (4)): build the bundle, rehearse it, finalize the manifest, run the operator's own gates over it.
Modelled on drafts/operator-hours-3/build_act.py (ACT-OPERATOR-HOURS-2/-3).

    python3 -B build_act.py build      the bundle from the live install and main tree (read only) and this folder's code/
    python3 -B build_act.py rehearse   rehearsal.log in the bundle (planted folders and clones; never the live ones)
    python3 -B build_act.py finalize   the manifest with the rehearsal's sha256 (only when the log ends `failures: 0`)
    python3 -B build_act.py gates      validate_manifest, the files' hashes, the path rule, act_class.classify (read only)
    python3 -B build_act.py all

Writes only: the bundle (acts/ACT-W2-148-S15-1/), this folder, and WORK (this helper's own TMPDIR folder).
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

import yaml

HERE = Path(__file__).resolve().parent
ORCH = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator")
REPO = Path("/home/usain/Dynamic-Agentic-Engineering-OS")
ACT = "ACT-W2-148-S15-1"
BUNDLE = ORCH / "acts" / ACT
BREL = ".gov-runtime/scratch/orchestrator/acts/" + ACT
LIVE_INST = Path("/home/usain/gov-os-operator/install")
WORK = Path(os.environ.get("S15_WORK", "/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/"
                           "b2f0511f-891b-4874-8930-6d34ca5972ea/scratchpad/w2-148-s15-helper/work"))
CODE = HERE / "code"
HEAVY = ORCH / "tools/heavy_slot.sh"
PKG = ORCH / "acts" / (ACT + ".package.md")
RULES_REL = "governance/project/operator/class-rules.yaml"
INST_RULES = "gov-os-operator/install/class-rules.yaml"
INST_AP = "gov-os-operator/install/APPROVED"
RULES_BEFORE = "0f130073bbbd06f7b56c7be44e72d42ffe6460bc49f4c6a684f81f499979bab1"   # the committed table (f680fc5ae), = the install's
AP_BEFORE = "1e557c49be5802256efa1906753964b53893a2eb507701fac02ebfe4f60914bc"      # the live APPROVED (ACT-OPERATOR-HOURS-2's after)
H3 = ORCH / "acts/ACT-OPERATOR-HOURS-3"
H3_AP_AFTER = "ff3579ff5abd13f54c8c5b844db5baa23d97f8372dd7ea84f01b3a93c9809114"    # ACT-OPERATOR-HOURS-3 Part B's APPROVED
H3_OPC_AFTER = "c7ec467c569126d803046ad7ca0e883d19d69a8f03bca17ffdd615a815981f7f"
DEC = "DEC-1142 (4), DEC-1104"
TOOLS_HOME = Path("/home/usain")
PROBE = HERE / "probe/test_s15_home_settings_probe.py"


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
        if name == "class-rules.yaml":
            assert s == RULES_BEFORE
            line, hit = f"{new_sha}  class-rules.yaml", hit + 1
        out.append(line)
    assert hit == 1
    return "\n".join(out) + "\n"


def keep_of(approved):
    return "\n".join(l for l in approved.splitlines() if not l.endswith("  class-rules.yaml")) + "\n"


# ------------------------------------------------------------------------------------------------------------- build
def build():
    if BUNDLE.exists():
        assert not (BUNDLE / "review.md").exists(), "the bundle holds a review: move it aside before a rebuild"
        shutil.rmtree(BUNDLE)
    live_ap = (LIVE_INST / "APPROVED").read_text()
    assert shab(live_ap.encode()) == AP_BEFORE, "the live APPROVED is not the before this bundle was written for"
    for line in live_ap.splitlines():
        s, _, name = line.partition("  ")
        assert sha(LIVE_INST / name) == s, f"the live install is not as APPROVED says: {name}"
    assert sha(LIVE_INST / "class-rules.yaml") == RULES_BEFORE == sha(REPO / RULES_REL)
    st = run(["git", "status", "--porcelain", "--", RULES_REL], cwd=REPO).stdout
    assert st.strip() == "", f"the repository's class-rules.yaml is not at the committed head: {st}"
    h3_ap = (H3 / "after/home" / INST_AP).read_text()
    assert shab(h3_ap.encode()) == H3_AP_AFTER
    diff = [(a, b) for a, b in zip(live_ap.splitlines(), h3_ap.splitlines()) if a != b]
    assert len(live_ap.splitlines()) == len(h3_ap.splitlines()) and diff == [(diff[0][0], f"{H3_OPC_AFTER}  opcommon.py")], \
        "ACT-OPERATOR-HOURS-3's after APPROVED is not the live one with opcommon.py's line changed"
    new_rules = (CODE / RULES_REL).read_bytes()
    rules_after = shab(new_rules)
    ap1 = approved_after(live_ap, rules_after)
    ap2 = approved_after(h3_ap, rules_after)
    old_rules = (REPO / RULES_REL).read_bytes()
    bases = [(BUNDLE, live_ap, ap1), (BUNDLE / "alt/hours3", h3_ap, ap2)]
    for d, apb, apa in bases:
        rows = [("repo", RULES_REL, old_rules, new_rules), ("home", INST_RULES, old_rules, new_rules),
                ("home", INST_AP, apb.encode(), apa.encode())]
        lines = []
        for root, p, b, a in rows:
            for side, data in (("before", b), ("after", a)):
                f = d / side / root / p
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_bytes(data)
            assert shab(b) != shab(a), p
            lines.append(f"{root}|{p}|{shab(b)}|{shab(a)}")
        (d / "list.txt").write_text("\n".join(lines) + "\n")
        (d / "keep.txt").write_text(keep_of(apb))
    shutil.copy(HERE / "apply.sh", BUNDLE / "apply.sh")
    (BUNDLE / "apply.sh").chmod(0o755)
    write_manifest(None)
    print(f"built {BUNDLE}")


def rows_of(listfile):
    return [l.split("|") for l in Path(listfile).read_text().splitlines() if l]


def checks(rules_after, ap1, ap2):
    probe = ("import sys; sys.path.insert(0, \".\"); import act_class as a; r = a.load_rules(); "
             "h = a.row_for(r, \"home\", \".claude/settings.json\"); l = a.row_for(r, \"home\", \".claude/settings.local.json\"); "
             "p = a.row_for(r, \"repo\", \".claude/settings.json\"); "
             "print(h[\"id\"], h.get(\"class\"), l[\"id\"], l.get(\"class\"), p[\"id\"], \"list\" if \"list\" in p else p.get(\"class\"))")
    return [
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/class-rules.yaml" | grep -c {rules_after}', "exit": 0, "count": 1},
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/APPROVED" | grep -cE "^({ap1}|{ap2}) "', "exit": 0, "count": 1},
        {"cmd": f'grep -c "^{rules_after}  class-rules.yaml$" "$HOME/gov-os-operator/install/APPROVED"', "exit": 0, "count": 1},
        {"cmd": f"cd \"$HOME/gov-os-operator/install\" && python3 -I -B -c '{probe}' | grep -c \"^home-settings b home-settings b settings list$\"",
         "exit": 0, "count": 1},
        {"cmd": f"sha256sum governance/project/operator/class-rules.yaml | grep -c {rules_after}", "exit": 0, "count": 1},
    ]


def write_manifest(rehearsal_sha):
    r1, r2 = rows_of(BUNDLE / "list.txt"), rows_of(BUNDLE / "alt/hours3/list.txt")
    mk = lambda rows: [{"root": r, "path": p, "before": None if b == "null" else b, "after": a} for r, p, b, a in rows]
    files = {}
    for top in ("before", "after", "alt"):
        for f in sorted((BUNDLE / top).rglob("*")):
            if f.is_file():
                files[str(f.relative_to(BUNDLE))] = sha(f)
    for n in ("apply.sh", "list.txt", "keep.txt"):
        files[n] = sha(BUNDLE / n)
    rules_after = r1[0][3]
    ap1, ap2 = r1[2][3], r2[2][3]
    m = {"act": ACT, "dec": DEC, "author": "cto", "claimed_class": "O",
         "what": "the home ~/.claude/settings*.json a fixed class (b) in the operator's rule table (a new row home-settings; the "
                 "settings row keeps the repository's settings only), in the repository's source and the install's copy, with "
                 "APPROVED's one line; W2-148 S15 then passes as written (DEC-1142 (4))",
         "applied_by": "the owner's operator, by hand (class (O): the operator's own rule table and install, DEC-1104 (4))",
         "steps": "bash apply.sh check|apply|verify|undo, then the owner's one commit of governance/project/operator/class-rules.yaml",
         "touched": mk(r1),
         "alt_base": {"why": "the same change on the install after ACT-OPERATOR-HOURS-3 Part B (its opcommon.py and APPROVED); "
                             "apply.sh picks the base by the install's APPROVED",
                      "list": "alt/hours3/list.txt", "keep": "alt/hours3/keep.txt", "touched": mk(r2)},
         "files": files, "checks": checks(rules_after, ap1, ap2), "commands": []}
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


def summary(out):
    tail = [l for l in out.splitlines() if re.search(r"\d+ (passed|failed|error)", l)]
    return re.sub(r" in [0-9.]+s( \([0-9:]+\))?", "", tail[-1]).strip(" =") if tail else "no summary"


def pytest_on(clone, args, wtmp, logname):
    env = {"HOME": os.environ["HOME"], "PATH": os.environ["PATH"], "LC_ALL": "C.UTF-8", "TMPDIR": str(wtmp),
           "PYTHONUSERBASE": str(TOOLS_HOME / ".local")}
    r = run(["bash", str(HEAVY), "python3", "-m", "pytest", *args, "-q", "-p", "no:cacheprovider", "--no-header", "-rfE"],
            env=env, cwd=str(clone), timeout=7200)
    (WORK / logname).write_text(r.stdout + "\n--- stderr ---\n" + r.stderr)
    return r.returncode, summary(r.stdout), r.stdout


def rehearse():
    if WORK.exists():
        subprocess.run(["chmod", "-R", "u+w", str(WORK)], check=False)
        shutil.rmtree(WORK)
    WORK.mkdir(parents=True)
    L = Log()
    live_before = tree_state(LIVE_INST)
    cron_before = run(["crontab", "-l"]).stdout
    watched = [RULES_REL, "governance/project/path-map.yaml"]
    tree_before = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    tmp = Path(tempfile.mkdtemp(prefix="s15-", dir=str(WORK)))
    try:
        rehearse_in(L, tmp)
    except BaseException as exc:
        import traceback
        traceback.print_exc()
        L.case(False, f"the rehearsal stopped: {exc.__class__.__name__}: {str(exc)[:300]}")
    L.case(tree_state(LIVE_INST) == live_before, "the live install (every file, hash and mode) is as it began")
    L.case(run(["crontab", "-l"]).stdout == cron_before, "the live crontab is byte for byte as it began")
    tree_after = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    L.case(tree_after == tree_before, "the live main tree's class-rules.yaml and path map are as they began (status and sha256)")
    head = ["# ACT-W2-148-S15-1 rehearsal (DEC-1142 (4)). Part 1: apply.sh on planted folders, the live base. Part 2: the",
            "# ACT-OPERATOR-HOURS-3 base and the order with that ACT. Part 3: the rule's effect (act_class on paths, on every",
            "# bundle on the machine, before against after). Part 4: the operator's own tests on a clone with the after file, and",
            "# the reviewer's FR-1 plant as a probe (red on the before, green on the after). Part 5: the package's blocks as printed",
            "# in a clone of w2/integrate with a planted HOME (apply, the owner's commit, the landing check, both undos)."]
    text = head + L.lines + [f"cases: {L.n}", f"failures: {L.fails}"]
    (BUNDLE / "rehearsal.log").write_text("\n".join(text) + "\n")
    print("\n".join(text[-2:]))


def rehearse_in(L, tmp):
    r1 = rows_of(BUNDLE / "list.txt")
    r2 = rows_of(BUNDLE / "alt/hours3/list.txt")
    after = {(r, p): a for r, p, b, a in r1}
    before = {(r, p): b for r, p, b, a in r1}
    after2 = {(r, p): a for r, p, b, a in r2}
    before2 = {(r, p): b for r, p, b, a in r2}
    rules_after = after[("repo", RULES_REL)]

    # ------------------------------------------------------------------------------------------ part 1
    L.note("part 1: apply.sh on planted folders (a planted HOME with a copy of the live install, a planted main tree with the before class-rules.yaml)")

    def world(name, hours3=False):
        w = tmp / name
        home, root = w / "home", w / "root"
        op = home / "gov-os-operator"
        shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
        if hours3:
            for n in ("opcommon.py", "APPROVED"):
                (op / "install" / n).chmod(0o644)
                shutil.copy2(H3 / "after/home/gov-os-operator/install" / n, op / "install" / n)
                (op / "install" / n).chmod(0o444)
        for d in ("log", "queue", "acts", "wall"):
            (op / d).mkdir(parents=True, exist_ok=True)
        (root / RULES_REL).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO / RULES_REL, root / RULES_REL)
        b = root / BREL
        shutil.copytree(BUNDLE, b)
        return home, root, op, b

    def ap(w, step, cwd=None, env=None):
        home, root, op, b = w
        return run(["bash", str(b / "apply.sh"), step], env=env or {"HOME": str(home), "PATH": os.environ["PATH"], "LC_ALL": "C"},
                   cwd=str(cwd or root))

    def snap(w):
        home, root, op, b = w
        return (tree_state(op), tree_state(root / "governance"))

    def listed(w, vals):
        home, root, op, b = w
        return all(sha((home if r == "home" else root) / p) == v for (r, p), v in vals.items())

    w = world("w1")
    home, root, op, bdir = w
    s0 = snap(w)
    r = ap(w, "check")
    L.case(r.returncode == 0 and "ready to apply on the install as built" in r.stdout, f"check on the before: exit 0, ready, the install as built ({r.returncode}; {r.stderr.strip()[:120]})")
    r = ap(w, "verify")
    L.case(r.returncode == 3 and "not applied" in r.stderr, f"verify before: exit 3, not applied ({r.returncode})")
    r = ap(w, "undo")
    L.case(r.returncode == 0 and "nothing to do" in r.stdout and snap(w) == s0, "undo on the before: exit 0, nothing to do, untouched")
    r = run(["bash", str(bdir / "apply.sh"), "exempt"], env={"HOME": str(home), "PATH": os.environ["PATH"]}, cwd=str(root))
    r2 = run(["bash", str(bdir / "apply.sh")], env={"HOME": str(home), "PATH": os.environ["PATH"]}, cwd=str(root))
    L.case(r.returncode == 2 and r2.returncode == 2 and snap(w) == s0, "an unknown step (exempt) or none: exit 2, usage, untouched")
    old_install = tmp / "old-install"
    shutil.copytree(op / "install", old_install)
    r = ap(w, "apply")
    L.case(r.returncode == 0 and "state applied (the install as built)" in r.stdout and "own APPROVED check: ok" in r.stdout,
           f"apply: exit 0, the install's own APPROVED check ok ({r.returncode}; {r.stderr.strip()[:120]})")
    L.case(listed(w, after), f"every listed file hashes as the after: class-rules.yaml {rules_after[:12]} (both), APPROVED {after[('home', INST_AP)][:12]}")
    L.case(all(stat.S_IMODE((op / "install" / n).stat().st_mode) == 0o444 for n in ("class-rules.yaml", "APPROVED"))
           and stat.S_IMODE((root / RULES_REL).stat().st_mode) == stat.S_IMODE((REPO / RULES_REL).stat().st_mode),
           "the install's two files are 0444; the repository file keeps its mode")
    L.case(not list(op.rglob(".*act-w2-148-s15-1*")) and not list(root.rglob(".*act-w2-148-s15-1*")) and not (op / "install/__pycache__").exists(),
           "no temporary file left, no __pycache__ in the install")
    oh = {l.split("  ")[1]: l.split("  ")[0] for l in (old_install / "APPROVED").read_text().splitlines()}
    L.case(all(sha(op / "install" / n) == h for n, h in oh.items() if n != "class-rules.yaml") and len(oh) == 14,
           "the thirteen other install files are byte for byte as they were")
    nl, ol = (op / "install/APPROVED").read_text().splitlines(), (old_install / "APPROVED").read_text().splitlines()
    L.case(len(nl) == len(ol) and [a for a, b in zip(nl, ol) if a != b] == [f"{rules_after}  class-rules.yaml"],
           "APPROVED differs in exactly one line: class-rules.yaml's")
    r = ap(w, "verify")
    L.case(r.returncode == 0 and "the install as built" in r.stdout, f"verify after: exit 0 ({r.returncode})")
    s1 = snap(w)
    r = ap(w, "apply")
    L.case(r.returncode == 0 and "already in place" in r.stdout and snap(w) == s1, "apply again: already in place, untouched")
    r = ap(w, "check")
    L.case(r.returncode == 3 and "already applied" in r.stderr, "check on the after: exit 3, already applied")
    m = json.loads((BUNDLE / "manifest.json").read_text())
    for c in m["checks"]:
        rr = run(["bash", "-c", c["cmd"]], env={"HOME": str(home), "PATH": os.environ["PATH"]}, cwd=str(root))
        cnt = int((rr.stdout.strip().splitlines() or ["-1"])[-1])
        L.case(rr.returncode == c["exit"] and cnt == c["count"], f"the manifest's check (exit {c['exit']}, count {c['count']}): {c['cmd'][:110]}")
    L.case(not (op / "install/__pycache__").exists(), "the manifest's checks wrote no __pycache__ into the install")
    r = ap(w, "undo")
    L.case(r.returncode == 0 and "state before (undone) (the install as built)" in r.stdout and listed(w, before),
           f"undo: exit 0, every file the before ({r.returncode})")
    L.case(snap(w) == s0, "the install and the repository file are byte for byte (hash, mode, listing) what they were")
    bad = [c["cmd"][:60] for c in m["checks"] if (lambda rr: rr.returncode == c["exit"] and int((rr.stdout.strip().splitlines() or ["-1"])[-1]) == c["count"])(
        run(["bash", "-c", c["cmd"]], env={"HOME": str(home), "PATH": os.environ["PATH"]}, cwd=str(root)))]
    L.case(not bad, f"the bite: on the before, every manifest check is red ({len(m['checks']) - len(bad)} of {len(m['checks'])} red)")
    w2 = world("w2")
    s_w2 = snap(w2)
    os.chmod(w2[2] / "install", 0o555)
    r = ap(w2, "apply")
    os.chmod(w2[2] / "install", 0o755)
    L.case(r.returncode == 5 and not listed(w2, before) and not listed(w2, after), f"apply with the install folder not writable: stops, exit 5, a half state ({r.returncode})")
    r = ap(w2, "check")
    L.case(r.returncode == 3 and "partly before, partly after" in r.stderr, "check names the half state: exit 3")
    r = ap(w2, "apply")
    L.case(r.returncode == 0 and listed(w2, after), f"a second apply finishes it ({r.returncode})")
    r = ap(w2, "undo")
    L.case(r.returncode == 0 and snap(w2) == s_w2, "undo: the whole state as it began")

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
    refusal("the repository's class-rules.yaml moved (one line longer)", lambda x: (x[1] / RULES_REL).write_text((x[1] / RULES_REL).read_text() + "# moved\n"))
    refusal("an install file other than the two moved (brief.md)", lambda x: ((x[2] / "install/brief.md").chmod(0o644), (x[2] / "install/brief.md").write_text("moved\n")), codes=ok_undo)
    refusal("a stray file in install/", lambda x: (x[2] / "install/stray.py").write_text("x\n"), codes=ok_undo)
    refusal("APPROVED neither base's (edited)", lambda x: ((x[2] / "install/APPROVED").chmod(0o644), (x[2] / "install/APPROVED").write_text("moved\n")))
    refusal("after the apply, the install's class-rules.yaml edited", lambda x: ((x[2] / "install/class-rules.yaml").chmod(0o644), (x[2] / "install/class-rules.yaml").write_text("rows: []\n")), base="after")
    refusal("a tampered frozen copy (after/home/.../class-rules.yaml)", lambda x: (x[3] / "after/home" / INST_RULES).write_text("# t\n"), codes={s_: (4,) for s_ in ("check", "apply", "undo", "verify")})
    refusal("a tampered frozen copy of the other base (alt/hours3/after/.../APPROVED)", lambda x: (x[3] / "alt/hours3/after/home" / INST_AP).write_text("# t\n"), codes={s_: (4,) for s_ in ("check", "apply", "undo", "verify")})
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
        L.case(r.returncode == 6 and "launch is running" in r.stderr and snap(wl) == sl, f"a launch holding log/launch.lock: apply exit 6, untouched ({r.returncode})")
    finally:
        os.killpg(hold.pid, 15)
        hold.wait()
    we = world("w-empty")
    empty = tmp / "empty-cwd"
    empty.mkdir()
    r = ap(we, "apply", cwd=empty, env={"HOME": str(we[0]), "PATH": "/usr/bin:/bin"})
    L.case(r.returncode == 0 and listed(we, after) and not list(empty.iterdir()), "apply in a clean environment from an empty folder: the after, nothing else written")
    ap(we, "undo", env={"HOME": str(we[0]), "PATH": "/usr/bin:/bin"})
    L.case(listed(we, before), "and its undo: the before")

    # ------------------------------------------------------------------------------------------ part 2
    L.note("part 2: the ACT-OPERATOR-HOURS-3 base (the install after its Part B) and the order with that ACT")
    wh = world("w-h3", hours3=True)
    sh = snap(wh)
    r = ap(wh, "check")
    L.case(r.returncode == 0 and "after ACT-OPERATOR-HOURS-3 Part B" in r.stdout, f"check on the HOURS-3 base: exit 0, names the base ({r.returncode}; {r.stderr.strip()[:120]})")
    r = ap(wh, "apply")
    L.case(r.returncode == 0 and "own APPROVED check: ok" in r.stdout and listed(wh, after2), f"apply on the HOURS-3 base: exit 0, every file the alt after ({r.returncode})")
    L.case(sha(wh[2] / "install/opcommon.py") == H3_OPC_AFTER and sha(wh[2] / "install/APPROVED") == after2[("home", INST_AP)],
           f"HOURS-3's opcommon.py kept; APPROVED {after2[('home', INST_AP)][:12]}")
    for c in m["checks"]:
        rr = run(["bash", "-c", c["cmd"]], env={"HOME": str(wh[0]), "PATH": os.environ["PATH"]}, cwd=str(wh[1]))
        cnt = int((rr.stdout.strip().splitlines() or ["-1"])[-1])
        L.case(rr.returncode == c["exit"] and cnt == c["count"], f"on the HOURS-3 base, the manifest's check: {c['cmd'][:90]}")
    r = ap(wh, "verify")
    L.case(r.returncode == 0, f"verify on the HOURS-3 base: exit 0 ({r.returncode})")
    r = ap(wh, "undo")
    L.case(r.returncode == 0 and snap(wh) == sh and listed(wh, before2), f"undo on the HOURS-3 base: the HOURS-3 install byte for byte ({r.returncode})")
    # the real ordering: HOURS-3's own apply.sh B on a planted world, then this ACT; and this ACT first, then HOURS-3's check
    h3files = ["governance/project/operator/opcommon.py", "tests/unit/operator/test_act_operator_hours_2.py",
               "tests/acceptance/W2-148/test_w2_148_gates.py", "tests/acceptance/W2-148/README.md"]

    def world_h3(name):
        wx = world(name)
        for p in h3files:
            (wx[1] / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / p, wx[1] / p)
        hb = wx[1] / ".gov-runtime/scratch/orchestrator/acts/ACT-OPERATOR-HOURS-3"
        shutil.copytree(H3, hb)
        return wx, hb

    def h3(wx, hb, step):
        return run(["bash", str(hb / "apply.sh"), "B", step], env={"HOME": str(wx[0]), "PATH": os.environ["PATH"], "LC_ALL": "C"}, cwd=str(wx[1]))
    wo, hb = world_h3("w-order-1")
    ra = h3(wo, hb, "apply")
    rb = ap(wo, "apply")
    rv3, rv = h3(wo, hb, "verify"), ap(wo, "verify")
    L.case(ra.returncode == 0 and rb.returncode == 0 and rv3.returncode != 0 and rv.returncode == 0 and listed(wo, after2),
           f"HOURS-3 Part B first, then this ACT: both apply (exit {ra.returncode}, {rb.returncode}); this ACT verifies; HOURS-3's own verify then exits {rv3.returncode} (its keep.txt pins the old class-rules.yaml): verify HOURS-3 BEFORE applying this ACT")
    ru = ap(wo, "undo")
    ru3 = h3(wo, hb, "undo")
    L.case(ru.returncode == 0 and ru3.returncode == 0 and listed(wo, before), f"undo in reverse order (this ACT, then HOURS-3 B): both exit 0, the live base again ({ru.returncode}, {ru3.returncode})")
    wo2, hb2 = world_h3("w-order-2")
    rb = ap(wo2, "apply")
    s_o2 = snap(wo2)
    rc3 = h3(wo2, hb2, "check")
    L.case(rb.returncode == 0 and rc3.returncode == 3 and snap(wo2) == s_o2,
           f"this ACT first: HOURS-3's own B check then refuses (exit {rc3.returncode}, 'moved: install/class-rules.yaml'), nothing touched: HOURS-3 would need a rebuild; so HOURS-3 Part B goes first")

    # ------------------------------------------------------------------------------------------ part 3
    L.note("part 3: the rule's effect: act_class (the applied install's copy against the old) on paths and on every bundle on the machine")
    sys.path.insert(0, str(old_install))
    sys.dont_write_bytecode = True
    import act_class  # noqa: E402  (the live code; only the table differs)
    old_rules = act_class.load_rules(str(old_install / "class-rules.yaml"))
    new_rules = act_class.load_rules(str(BUNDLE / "after/home" / INST_RULES))
    ids_o, ids_n = [r["id"] for r in old_rules["rows"]], [r["id"] for r in new_rules["rows"]]
    i = ids_o.index("settings")
    L.case(ids_n == ids_o[:i + 1] + ["home-settings"] + ids_o[i + 1:], f"the rows: the old {len(ids_o)} in order, one new row home-settings straight after settings")
    no = {r["id"]: r for r in old_rules["rows"]}
    nn = {r["id"]: r for r in new_rules["rows"]}
    L.case(all(no[k] == nn[k] for k in ids_o if k != "settings") and old_rules.get("hits") == new_rules.get("hits") and
           {k: v for k, v in old_rules.items() if k not in ("rows",)} == {k: v for k, v in new_rules.items() if k not in ("rows",)},
           "every other row, the hits and the version are equal")
    so, sn = no["settings"], nn["settings"]
    L.case({k: v for k, v in so.items() if k not in ("match", "why")} == {k: v for k, v in sn.items() if k not in ("match", "why")}
           and sn["match"] == [mm for mm in so["match"] if mm["root"] != "home"],
           "the settings row: its list rule, else and control unchanged; its match loses only the home line")
    hs = nn["home-settings"]
    L.case(hs["match"] == [{"root": "home", "path": ".claude/settings*.json"}] and hs.get("class") == "b" and hs.get("control") is True and "list" not in hs,
           "home-settings: {root: home, path: .claude/settings*.json}, class b, control true, no list rule")
    corpus = set()
    for rules in (old_rules, new_rules):
        for row in rules["rows"]:
            for mm in row["match"]:
                p = str(mm["path"])
                for a, b in (("x/y", "x"), ("", ""), ("a", "b")):
                    corpus.add((mm["root"], p.replace("**", a).replace("*", b)))
    corpus |= {("home", ".claude/settings.json"), ("home", ".claude/settings.local.json"), ("home", ".claude/settingsX.json"),
               ("home", ".claude/settings.json.pre-act-guard-fix-4"), ("home", ".claude/sub/settings.json"), ("home", ".claude/CLAUDE.md"),
               ("repo", ".claude/settings.json"), ("repo", ".claude/settings.local.json"), ("home", "gov-os-writer/.claude/settings.json"),
               ("home", ".claude/hooks/x.py"), ("home", ".claude/agents/x.md"), ("home", ".claude/keybindings.json")}
    for mf in sorted(ORCH.glob("acts/*/manifest.json")) + sorted(ORCH.glob("drafts/*/manifest.json")):
        try:
            for t in json.loads(mf.read_text()).get("touched") or []:
                if isinstance(t, dict) and isinstance(t.get("path"), str):
                    corpus.add((t.get("root"), t["path"]))
        except Exception:
            pass

    def key(rules, root, path):
        row = act_class.row_for(rules, root, path)
        return None if row is None else (row["id"], row.get("class") or "list")
    changed = sorted((r, p, key(old_rules, r, p), key(new_rules, r, p)) for r, p in corpus if key(old_rules, r, p) != key(new_rules, r, p))
    want = act_class.glob_re(".claude/settings*.json")
    L.case(changed and all(r == "home" and want.match(p) and o == ("settings", "list") and n == ("home-settings", "b") for r, p, o, n in changed),
           f"over {len(corpus)} (root, path) pairs (every row's globs instantiated, edge names, every path any bundle on the machine names): the {len(changed)} that change are all home .claude/settings*.json, settings (list) to home-settings (b): {', '.join(p for r, p, o, n in changed)}")
    SET = json.dumps({"permissions": {"allow": ["Read"], "deny": ["Bash(sudo *)"]}, "hooks": {}}, indent=1) + "\n"

    def one(rules, root, path, before_t, after_t):
        d = tmp / ("cls-" + hashlib.sha1(f"{root}{path}{before_t}{after_t}{id(rules)}".encode()).hexdigest()[:10])
        for side, t in (("before", before_t), ("after", after_t)):
            f = d / side / root / path
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(t)
        man = {"touched": [{"root": root, "path": path, "before": shab(before_t.encode()), "after": shab(after_t.encode())}],
               "files": {}, "checks": [], "commands": []}
        return act_class.classify_manifest(man, str(d), rules)["class"]
    deny_add = SET.replace('"Bash(sudo *)"', '"Bash(sudo *)",\n   "Read(**)"')
    allow_add = SET.replace('"Read"', '"Read", "Bash"')
    for root, path, after_t, want_old, want_new, label in (
            ("home", ".claude/settings.json", deny_add, "a", "b", "the home settings.json, Read(**) added to permissions.deny (the reviewer's FR-1 plant)"),
            ("home", ".claude/settings.local.json", deny_add, "a", "b", "the home settings.local.json, a deny addition"),
            ("home", ".claude/settings.json", allow_add, "b", "b", "the home settings.json, an allow addition"),
            ("repo", ".claude/settings.json", deny_add, "a", "a", "the repository's settings.json, a deny addition (still (a), with S15's replay)"),
            ("repo", ".claude/settings.local.json", deny_add, "a", "a", "the repository's settings.local.json, a deny addition"),
            ("repo", ".claude/settings.json", allow_add, "b", "b", "the repository's settings.json, an allow addition")):
        co, cn = one(old_rules, root, path, SET, after_t), one(new_rules, root, path, SET, after_t)
        L.case(co == want_old and cn == want_new, f"classify_manifest, {label}: old table ({co}), new table ({cn})")
    seen = 0
    moved = []
    for mf in sorted(ORCH.glob("acts/*/manifest.json")):
        try:
            mm = json.loads(mf.read_text())
            co = act_class.classify_manifest(mm, str(mf.parent), old_rules)["class"]
            cn = act_class.classify_manifest(mm, str(mf.parent), new_rules)["class"]
        except Exception:
            continue
        seen += 1
        if co != cn:
            moved.append((mf.parent.name, co, cn))
    L.case(seen > 20 and all(act_class.RANK[cn] > act_class.RANK[co] for _, co, cn in moved),
           f"every bundle under acts/ ({seen}) classified with both tables: none lower; {len(moved)} higher{': ' + ', '.join(f'{a} {o} to {n}' for a, o, n in moved) if moved else ''}")
    sys.path.remove(str(old_install))

    # ------------------------------------------------------------------------------------------ part 4
    L.note("part 4: the operator's own tests on a clone (`git clone --no-hardlinks` of w2/integrate's head) with the after file, through heavy_slot.sh, TMPDIR outside the repository and ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider")
    if os.environ.get("S15_SKIP_TESTS") == "1":
        L.case(False, "part 4 skipped (S15_SKIP_TESTS=1: a draft run, never the final rehearsal)")
        exec(compile((HERE / "part5.py").read_text(), str(HERE / "part5.py"), "exec"), globals())
        part5(L, tmp, world)
        return
    clone = WORK / "clone"
    wtmp = WORK / "pytest-tmp"
    wtmp.mkdir()
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(clone)], check=True)
    L.note(f"the clone's head: {run(['git', '-C', str(clone), 'rev-parse', '--short=12', 'HEAD']).stdout.strip()}")
    L.case(sha(clone / RULES_REL) == before[("repo", RULES_REL)], "the clone's class-rules.yaml is the before")
    probe_dst = clone / "tests/acceptance/W2-148" / PROBE.name
    shutil.copy2(PROBE, probe_dst)
    rc0, s0_, _ = pytest_on(clone, [str(probe_dst.relative_to(clone))], wtmp, "pytest-probe-before.out")
    L.case(rc0 != 0 and "failed" in s0_, f"the probe on the BEFORE table goes red (the reviewer's FR-1 reproduced: the home deny addition applied as (a)): {s0_}")
    shutil.copy2(BUNDLE / "after/repo" / RULES_REL, clone / RULES_REL)
    L.case(sha(clone / RULES_REL) == rules_after, "the clone's class-rules.yaml is the after")
    rc1, s1_, _ = pytest_on(clone, [str(probe_dst.relative_to(clone))], wtmp, "pytest-probe-after.out")
    L.case(rc1 == 0 and "failed" not in s1_, f"the probe on the AFTER table goes green (the code votes (b): refused at G6 without the owner's yes, the home file untouched): {s1_}")
    probe_dst.unlink()
    rc2, s2_, out2 = pytest_on(clone, ["tests/unit/operator", "tests/acceptance/W2-148"], wtmp, "pytest-after.out")
    L.case(rc2 == 0 and "failed" not in s2_ and "error" not in s2_, f"with the after file: tests/unit/operator tests/acceptance/W2-148: {s2_}")
    if rc2 != 0:
        fails = sorted({l.split(" ")[1] for l in out2.splitlines() if l.startswith(("FAILED ", "ERROR "))})
        L.note("failed: " + "; ".join(fails[:20]))
        shutil.copy2(BUNDLE / "before/repo" / RULES_REL, clone / RULES_REL)
        rc3, s3_, _ = pytest_on(clone, fails or ["tests/unit/operator"], wtmp, "pytest-before-of-failed.out")
        L.note(f"the same cases on the BEFORE table: {s3_}")
        shutil.copy2(BUNDLE / "after/repo" / RULES_REL, clone / RULES_REL)
    L.case(run(["git", "-C", str(clone), "status", "--porcelain"]).stdout.strip() == f"M {RULES_REL}",
           "the clone's only change is class-rules.yaml (the probe removed, the tests wrote nothing into the tree)")

    # ------------------------------------------------------------------------------------------ part 5
    exec(compile((HERE / "part5.py").read_text(), str(HERE / "part5.py"), "exec"), globals())
    part5(L, tmp, world)


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
    have = {str(f.relative_to(BUNDLE)) for f in BUNDLE.rglob("*") if f.is_file()} - {"manifest.json", "review.md"}
    assert have == set(m["files"]), have ^ set(m["files"])
    print(f"files: {len(m['files'])} hash as the manifest says; no file in the bundle unlisted")
    s = {"repo": str(REPO), "home": str(Path.home())}
    for where, text in [("apply.sh", (BUNDLE / "apply.sh").read_text())] + [("a check", c["cmd"]) for c in m["checks"]]:
        why = orun.live_path_refs(text, s)
        print(f"path rule on {where}: {'pass' if why is None else why}")
    v = act_class.classify(str(BUNDLE))
    print(f"act_class.classify (the bundle, the live table): class {v['class']}; hits {v['hits']}")
    for f in v["files"]:
        print(f"  {f['root']}|{f['path']}: {f['class']} (row {f['row']})")
    va = act_class.classify_manifest(dict(m, touched=m["alt_base"]["touched"]), None)
    print(f"act_class.classify_manifest (the HOURS-3 base's rows): class {va['class']}")
    vn = act_class.classify_manifest(m, str(BUNDLE), act_class.load_rules(str(BUNDLE / "after/home" / INST_RULES)))
    print(f"act_class.classify_manifest (the bundle under its own after table): class {vn['class']}")
    print(f"manifest sha256 {sha(BUNDLE / 'manifest.json')}")


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates,
     "all": lambda: (build(), rehearse(), finalize(), gates())}[sys.argv[1]]()
