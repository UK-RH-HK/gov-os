#!/usr/bin/env python3
"""ACT-CLASS-RULES-AGENTS-1 (DEC-1173): build the bundle, rehearse it, finalize the manifest, run the operator's own gates over it.
Adapted from drafts/w2-148-s15/build_act.py (ACT-W2-148-S15-1, the precedent: one row in the rule table, in the repository's
source and the install's copy, with APPROVED's one line). The second base is the install after ACT-LANDING-CTO-ROUTE-1
(pending, it also edits APPROVED), as the precedent's was the install after ACT-OPERATOR-HOURS-3 Part B.

    python3 -B build_act.py build      the bundle from the live install and main tree (read only) and this folder's code/
    python3 -B build_act.py rehearse   rehearsal.log in the bundle (planted folders and clones; never the live ones)
    python3 -B build_act.py finalize   the manifest with the rehearsal's sha256 (only when the log ends `failures: 0`)
    python3 -B build_act.py gates      validate_manifest, the files' hashes, the path rule, act_class.classify (read only)

Writes only: the bundle (acts/ACT-CLASS-RULES-AGENTS-1/), this folder, and WORK (/tmp/claude-1000/act-class-rules-agents-1/).
"""
import hashlib
import importlib.util
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
ACT = "ACT-CLASS-RULES-AGENTS-1"
BUNDLE = ORCH / "acts" / ACT
BREL = ".gov-runtime/scratch/orchestrator/acts/" + ACT
LIVE_INST = Path("/home/usain/gov-os-operator/install")
WORK = Path(os.environ.get("CRA_WORK", "/tmp/claude-1000/act-class-rules-agents-1/work"))
CODE = HERE / "code"
HEAVY = ORCH / "tools/heavy_slot.sh"
PKG = ORCH / "acts" / (ACT + ".package.md")
RULES_REL = "governance/project/operator/class-rules.yaml"
INST_RULES = "gov-os-operator/install/class-rules.yaml"
INST_AP = "gov-os-operator/install/APPROVED"
RULES_BEFORE = "38ac2f2decce660a9e190c85038b7175dcbae0e0c0ce79acc0597df17d0e79a4"   # the committed table (4be656e70), = the install's
AP_BEFORE = "3744df3a637feadc26c673b88a10cbc757e8c8746aced078d700300906962815"      # the live APPROVED (S15-1 on HOURS-3's base)
LD = ORCH / "acts/ACT-LANDING-CTO-ROUTE-1"
LD_AP_AFTER = "ef5afbac78f3fce16ab7551ef88987a6898acd8f9a7a18439bf83aeb9216c157"    # ACT-LANDING-CTO-ROUTE-1's APPROVED
LD_LC_AFTER = "fd0b59ede124bdd0913b58542daf6fc5da7fe675f60d1f2e9531d7994bd362cb"    # its landing_check.py
DEC = "DEC-1173, DEC-1104"
TOOLS_HOME = Path("/home/usain")
NEW_ROW = "agent-instructions"
TRIAL = REPO / "tests/unit/operator/test_w2_148_unit_trial.py"
RULES1 = ORCH / "acts/ACT-CLAUDE-RULES-1"


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
        rv = BUNDLE / "review.md"
        assert not rv.exists() or "not written yet" in rv.read_text(), "the bundle holds a written review: move it aside before a rebuild"
        shutil.rmtree(BUNDLE)
    live_ap = (LIVE_INST / "APPROVED").read_text()
    assert shab(live_ap.encode()) == AP_BEFORE, "the live APPROVED is not the before this bundle was written for"
    for line in live_ap.splitlines():
        s, _, name = line.partition("  ")
        assert sha(LIVE_INST / name) == s, f"the live install is not as APPROVED says: {name}"
    assert sha(LIVE_INST / "class-rules.yaml") == RULES_BEFORE == sha(REPO / RULES_REL)
    st = run(["git", "status", "--porcelain", "--", RULES_REL], cwd=REPO).stdout
    assert st.strip() == "", f"the repository's class-rules.yaml is not at the committed head: {st}"
    ld_ap = (LD / "after/home" / INST_AP).read_text()
    assert shab(ld_ap.encode()) == LD_AP_AFTER
    diff = [(a, b) for a, b in zip(live_ap.splitlines(), ld_ap.splitlines()) if a != b]
    assert len(live_ap.splitlines()) == len(ld_ap.splitlines()) and diff == [(diff[0][0], f"{LD_LC_AFTER}  landing_check.py")], \
        "ACT-LANDING-CTO-ROUTE-1's after APPROVED is not the live one with landing_check.py's line changed"
    new_rules = (CODE / RULES_REL).read_bytes()
    rules_after = shab(new_rules)
    ap1 = approved_after(live_ap, rules_after)
    ap2 = approved_after(ld_ap, rules_after)
    old_rules = (REPO / RULES_REL).read_bytes()
    for d, apb, apa in [(BUNDLE, live_ap, ap1), (BUNDLE / "alt/landing", ld_ap, ap2)]:
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
    (BUNDLE / "review.md").write_text(f"# {ACT}: the ACT review\n\nReview: not written yet\n")
    write_manifest(None)
    print(f"built {BUNDLE}")


def rows_of(listfile):
    return [l.split("|") for l in Path(listfile).read_text().splitlines() if l]


PROBE_OUT = "agent-instructions b agent-instructions b agents-skills-kernel b unknown O"


def checks(rules_after, ap1, ap2):
    probe = ("import sys; sys.path.insert(0, \".\"); import act_class as a; r = a.load_rules(); "
             "c = a.row_for(r, \"repo\", \"CLAUDE.md\"); g = a.row_for(r, \"repo\", \"AGENTS.md\"); "
             "h = a.row_for(r, \"home\", \".claude/CLAUDE.md\"); d = a.row_for(r, \"repo\", \"docs/CLAUDE.md\"); "
             "print(c[\"id\"], c.get(\"class\"), g[\"id\"], g.get(\"class\"), h[\"id\"], h.get(\"class\"), d[\"id\"], d.get(\"class\"))")
    return [
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/class-rules.yaml" | grep -c {rules_after}', "exit": 0, "count": 1},
        {"cmd": f'sha256sum "$HOME/gov-os-operator/install/APPROVED" | grep -cE "^({ap1}|{ap2}) "', "exit": 0, "count": 1},
        {"cmd": f'grep -c "^{rules_after}  class-rules.yaml$" "$HOME/gov-os-operator/install/APPROVED"', "exit": 0, "count": 1},
        {"cmd": f"cd \"$HOME/gov-os-operator/install\" && python3 -I -B -c '{probe}' | grep -c \"^{PROBE_OUT}$\"",
         "exit": 0, "count": 1},
        {"cmd": f"sha256sum governance/project/operator/class-rules.yaml | grep -c {rules_after}", "exit": 0, "count": 1},
    ]


def write_manifest(rehearsal_sha):
    r1, r2 = rows_of(BUNDLE / "list.txt"), rows_of(BUNDLE / "alt/landing/list.txt")
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
         "what": "the agent instructions every session loads (the repository's CLAUDE.md and AGENTS.md) a fixed class (b) in the "
                 "operator's rule table (a new row agent-instructions, straight after guard-hook, control: true), in the repository's "
                 "source and the install's copy, with APPROVED's one line; an approved change to them is then applied by the operator "
                 "agent (DEC-1173)",
         "applied_by": "the owner's operator, by hand (class (O): the operator's own rule table and install, OPERATOR-AGENT-1 §5, DEC-1104 (4))",
         "steps": "bash apply.sh check|apply|verify|undo, then the owner's one commit of governance/project/operator/class-rules.yaml",
         "touched": mk(r1),
         "alt_base": {"why": "the same change on the install after ACT-LANDING-CTO-ROUTE-1 (its landing_check.py and APPROVED); "
                             "apply.sh picks the base by the install's APPROVED",
                      "list": "alt/landing/list.txt", "keep": "alt/landing/keep.txt", "touched": mk(r2)},
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
    watched = [RULES_REL, "governance/project/path-map.yaml", "CLAUDE.md", "AGENTS.md"]
    tree_before = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    tmp = Path(tempfile.mkdtemp(prefix="cra-", dir=str(WORK)))
    try:
        rehearse_in(L, tmp)
    except BaseException as exc:
        import traceback
        traceback.print_exc()
        L.case(False, f"the rehearsal stopped: {exc.__class__.__name__}: {str(exc)[:300]}")
    L.case(tree_state(LIVE_INST) == live_before, "the live install (every file, hash and mode) is as it began")
    L.case(run(["crontab", "-l"]).stdout == cron_before, "the live crontab is byte for byte as it began")
    tree_after = (run(["git", "status", "--porcelain", "--"] + watched, cwd=REPO).stdout, {p: sha(REPO / p) for p in watched})
    L.case(tree_after == tree_before, "the live main tree's class-rules.yaml, path map, CLAUDE.md and AGENTS.md are as they began (status and sha256)")
    head = [f"# {ACT} rehearsal (DEC-1173). Part 1: apply.sh on planted folders, the live base. Part 2: the",
            "# ACT-LANDING-CTO-ROUTE-1 base and the order with that ACT. Part 3: the rule's effect (act_class on paths, on W2-148's",
            "# 57 ACT file lists and every ACT file, on every bundle on the machine, before against after). Part 4: the operator's own",
            "# tests on a clone with the after file. Part 5: the package's blocks as printed in a clone of w2/integrate with a planted",
            "# HOME (apply, the owner's commit, the landing check, both undos)."]
    text = head + L.lines + [f"cases: {L.n}", f"failures: {L.fails}"]
    (BUNDLE / "rehearsal.log").write_text("\n".join(text) + "\n")
    print("\n".join(text[-2:]))


def rehearse_in(L, tmp):
    r1 = rows_of(BUNDLE / "list.txt")
    r2 = rows_of(BUNDLE / "alt/landing/list.txt")
    after = {(r, p): a for r, p, b, a in r1}
    before = {(r, p): b for r, p, b, a in r1}
    after2 = {(r, p): a for r, p, b, a in r2}
    before2 = {(r, p): b for r, p, b, a in r2}
    rules_after = after[("repo", RULES_REL)]

    # ------------------------------------------------------------------------------------------ part 1
    L.note("part 1: apply.sh on planted folders (a planted HOME with a copy of the live install, a planted main tree with the before class-rules.yaml)")

    def world(name, landing=False):
        w = tmp / name
        home, root = w / "home", w / "root"
        op = home / "gov-os-operator"
        shutil.copytree(LIVE_INST, op / "install", ignore=shutil.ignore_patterns("__pycache__"))
        if landing:
            for n, src in (("landing_check.py", LD / "after/home/gov-os-operator/install/landing_check.py"),
                           ("APPROVED", LD / "after/home/gov-os-operator/install/APPROVED")):
                (op / "install" / n).chmod(0o644)
                shutil.copy2(src, op / "install" / n)
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
    L.case(not list(op.rglob(".*act-class-rules-agents-1*")) and not list(root.rglob(".*act-class-rules-agents-1*")) and not (op / "install/__pycache__").exists(),
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
    refusal("a tampered frozen copy of the other base (alt/landing/after/.../APPROVED)", lambda x: (x[3] / "alt/landing/after/home" / INST_AP).write_text("# t\n"), codes={s_: (4,) for s_ in ("check", "apply", "undo", "verify")})
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
        os.killpg(hold.pid, 15)     # by its own process group (pid), never a name match
        hold.wait()
    we = world("w-empty")
    empty = tmp / "empty-cwd"
    empty.mkdir()
    r = ap(we, "apply", cwd=empty, env={"HOME": str(we[0]), "PATH": "/usr/bin:/bin"})
    L.case(r.returncode == 0 and listed(we, after) and not list(empty.iterdir()), "apply in a clean environment from an empty folder: the after, nothing else written")
    ap(we, "undo", env={"HOME": str(we[0]), "PATH": "/usr/bin:/bin"})
    L.case(listed(we, before), "and its undo: the before")

    # ------------------------------------------------------------------------------------------ part 2
    L.note("part 2: the ACT-LANDING-CTO-ROUTE-1 base (the install after it) and the order with that ACT")
    wh = world("w-ld", landing=True)
    sh = snap(wh)
    r = ap(wh, "check")
    L.case(r.returncode == 0 and "after ACT-LANDING-CTO-ROUTE-1" in r.stdout, f"check on the LANDING base: exit 0, names the base ({r.returncode}; {r.stderr.strip()[:120]})")
    r = ap(wh, "apply")
    L.case(r.returncode == 0 and "own APPROVED check: ok" in r.stdout and listed(wh, after2), f"apply on the LANDING base: exit 0, every file the alt after ({r.returncode})")
    L.case(sha(wh[2] / "install/landing_check.py") == LD_LC_AFTER and sha(wh[2] / "install/APPROVED") == after2[("home", INST_AP)],
           f"LANDING's landing_check.py kept; APPROVED {after2[('home', INST_AP)][:12]}")
    for c in m["checks"]:
        rr = run(["bash", "-c", c["cmd"]], env={"HOME": str(wh[0]), "PATH": os.environ["PATH"]}, cwd=str(wh[1]))
        cnt = int((rr.stdout.strip().splitlines() or ["-1"])[-1])
        L.case(rr.returncode == c["exit"] and cnt == c["count"], f"on the LANDING base, the manifest's check: {c['cmd'][:90]}")
    r = ap(wh, "verify")
    L.case(r.returncode == 0, f"verify on the LANDING base: exit 0 ({r.returncode})")
    r = ap(wh, "undo")
    L.case(r.returncode == 0 and snap(wh) == sh and listed(wh, before2), f"undo on the LANDING base: the LANDING install byte for byte ({r.returncode})")
    ldfiles = ["governance/project/operator/landing_check.py"]

    def world_ld(name):
        wx = world(name)
        for p in ldfiles:
            (wx[1] / p).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / p, wx[1] / p)
        (wx[1] / "tests/unit/operator").mkdir(parents=True, exist_ok=True)
        (wx[1] / ".git").mkdir(exist_ok=True)
        hb = wx[1] / ".gov-runtime/scratch/orchestrator/acts/ACT-LANDING-CTO-ROUTE-1"
        shutil.copytree(LD, hb)
        return wx, hb

    def ld(wx, hb, step):
        return run(["bash", str(hb / "apply.sh"), step], env={"HOME": str(wx[0]), "PATH": os.environ["PATH"], "LC_ALL": "C"}, cwd=str(wx[1]))
    wo, hb = world_ld("w-order-1")
    ra = ld(wo, hb, "apply")
    rb = ap(wo, "apply")
    rv3, rv = ld(wo, hb, "verify"), ap(wo, "verify")
    L.case(ra.returncode == 0 and rb.returncode == 0 and rv.returncode == 0 and listed(wo, after2),
           f"LANDING first, then this ACT: both apply (exit {ra.returncode}, {rb.returncode}); this ACT verifies; LANDING's own verify then exits {rv3.returncode} (its keep.txt pins today's class-rules.yaml): verify LANDING BEFORE applying this ACT")
    ru = ap(wo, "undo")
    ru3 = ld(wo, hb, "undo")
    L.case(ru.returncode == 0 and ru3.returncode == 0 and listed(wo, before), f"undo in reverse order (this ACT, then LANDING): both exit 0, the live base again ({ru.returncode}, {ru3.returncode})")
    wo2, hb2 = world_ld("w-order-2")
    rb = ap(wo2, "apply")
    s_o2 = snap(wo2)
    rc3 = ld(wo2, hb2, "check")
    L.case(rb.returncode == 0 and rc3.returncode == 3 and snap(wo2) == s_o2,
           f"this ACT first: LANDING's own check then refuses (exit {rc3.returncode}, {rc3.stderr.strip()[:80]!r}), nothing touched: LANDING would need a rebuild; so LANDING goes first")

    # ------------------------------------------------------------------------------------------ part 3
    L.note("part 3: the rule's effect: act_class (the live install's code; the old table against the new) on paths, on W2-148's 57 ACT file lists and every ACT file, and on every bundle on the machine")
    sys.path.insert(0, str(old_install))
    sys.dont_write_bytecode = True
    import act_class  # noqa: E402  (the live code; only the table differs)
    old_rules = act_class.load_rules(str(old_install / "class-rules.yaml"))
    new_rules = act_class.load_rules(str(BUNDLE / "after/home" / INST_RULES))
    ids_o, ids_n = [r["id"] for r in old_rules["rows"]], [r["id"] for r in new_rules["rows"]]
    i = ids_o.index("guard-hook")
    L.case(ids_n == ids_o[:i + 1] + [NEW_ROW] + ids_o[i + 1:], f"the rows: the old {len(ids_o)} in order, one new row {NEW_ROW} straight after guard-hook")
    no = {r["id"]: r for r in old_rules["rows"]}
    nn = {r["id"]: r for r in new_rules["rows"]}
    L.case(all(no[k] == nn[k] for k in ids_o) and {k: v for k, v in old_rules.items() if k != "rows"} == {k: v for k, v in new_rules.items() if k != "rows"},
           "every old row, the hits and the version are equal (no row other than the new one changes)")
    na_ = nn[NEW_ROW]
    L.case(na_["match"] == [{"root": "repo", "path": "CLAUDE.md"}, {"root": "repo", "path": "AGENTS.md"}] and na_.get("class") == "b"
           and na_.get("control") is True and "list" not in na_ and "DEC-1173" in na_.get("why", ""),
           f"{NEW_ROW}: {{root: repo, path: CLAUDE.md}}, {{root: repo, path: AGENTS.md}}, class b, control true, no list rule, why names DEC-1173")
    earlier = [ids_o[j] for j in range(i + 1) if act_class.row_for({"rows": [no[ids_o[j]]]}, "repo", "CLAUDE.md")
               or act_class.row_for({"rows": [no[ids_o[j]]]}, "repo", "AGENTS.md")]
    L.case(not earlier and act_class.row_for(old_rules, "repo", "CLAUDE.md")["id"] == "unknown"
           and act_class.row_for(old_rules, "repo", "AGENTS.md")["id"] == "unknown",
           "no earlier row matches CLAUDE.md or AGENTS.md; under the old table both fall to the catch-all unknown (O)")
    corpus = set()
    for rules in (old_rules, new_rules):
        for row in rules["rows"]:
            for mm in row["match"]:
                p = str(mm["path"])
                for a, b in (("x/y", "x"), ("", ""), ("a", "b")):
                    corpus.add((mm["root"], p.replace("**", a).replace("*", b)))
    corpus |= {("repo", "CLAUDE.md"), ("repo", "AGENTS.md"), ("repo", "docs/CLAUDE.md"), ("repo", "template/CLAUDE.md"),
               ("repo", "template/AGENTS.md"), ("repo", "CLAUDE.md.bak"), ("repo", "claude.md"), ("repo", "CLAUDE.local.md"),
               ("repo", "src/CLAUDE.md"), ("repo", ".claude/CLAUDE.md"), ("home", "CLAUDE.md"), ("home", "AGENTS.md"),
               ("home", ".claude/CLAUDE.md"), ("home", "gov-os-operator/CLAUDE.md"), ("repo", "AGENTS.md.orig"),
               ("crontab", "CLAUDE.md")}
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
    L.case(sorted((r, p) for r, p, o, n in changed) == [("repo", "AGENTS.md"), ("repo", "CLAUDE.md")]
           and all(o == ("unknown", "O") and n == (NEW_ROW, "b") for r, p, o, n in changed),
           f"over {len(corpus)} (root, path) pairs (every row's globs instantiated, edge names, every path any bundle on the machine names): "
           f"the {len(changed)} that change are exactly repo CLAUDE.md and AGENTS.md, unknown (O) to {NEW_ROW} (b)")
    MD = "# Governance\n\nSome text.\n"

    def one(rules, files):
        d = tmp / ("cls-" + hashlib.sha1(f"{files}{id(rules)}".encode()).hexdigest()[:10])
        touched = []
        for root, path in files:
            for side, t in (("before", MD), ("after", MD + "One more line.\n")):
                f = d / side / root / path
                f.parent.mkdir(parents=True, exist_ok=True)
                f.write_text(t)
            touched.append({"root": root, "path": path, "before": shab(MD.encode()), "after": shab((MD + "One more line.\n").encode())})
        man = {"touched": touched, "files": {}, "checks": [], "commands": []}
        return act_class.classify_manifest(man, str(d), rules)["class"]
    for files, want_old, want_new, label in (
            ([("repo", "CLAUDE.md")], "O", "b", "an ACT that rewrites only CLAUDE.md"),
            ([("repo", "AGENTS.md")], "O", "b", "an ACT that rewrites only AGENTS.md"),
            ([("repo", ".rulesync/rules/governance.md"), ("repo", "CLAUDE.md"), ("repo", "AGENTS.md")], "O", "b", "the rule source with both copies (ACT-CLAUDE-RULES-1's shape)"),
            ([("repo", "CLAUDE.md"), ("repo", "src/gov/x.py")], "O", "O", "CLAUDE.md with a src/ file (still the catch-all's O)"),
            ([("repo", "docs/CLAUDE.md")], "O", "O", "a CLAUDE.md elsewhere in the tree (docs/CLAUDE.md)"),
            ([("home", ".claude/CLAUDE.md")], "b", "b", "the home ~/.claude/CLAUDE.md (agents-skills-kernel, unchanged)")):
        co, cn = one(old_rules, files), one(new_rules, files)
        L.case(co == want_old and cn == want_new, f"classify_manifest, {label}: old table ({co}), new table ({cn})")
    # W2-148's trial (S23): its 57 ACT file lists, and every ACT file now in the packages folder, each made a manifest the trial's way
    spec = importlib.util.spec_from_file_location("w2_148_unit_trial", str(TRIAL))
    trial = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trial)
    entries = {e["act"]: e for e in json.loads(trial.ACTS_JSON.read_text())}
    rows57, rowsall = [], []
    ttmp = tmp / "trial"
    for f in trial.act_files():
        act = f.stem
        entry = entries.get(act) or {"act": act, "commits": [], "repo_paths": [], "home_paths": [], "crontab": False, "flags": [], "kind": ""}
        bd = ttmp / act
        mm = trial.act_manifest(entry, bd, f.read_text(errors="replace"))
        co = act_class.classify_manifest(mm, str(bd), old_rules)["class"]
        cn = act_class.classify_manifest(mm, str(bd), new_rules)["class"]
        rowsall.append((act, co, cn))
        if act in entries:
            rows57.append((act, co, cn))
    mv57 = [x for x in rows57 if x[1] != x[2]]
    mvall = [x for x in rowsall if x[1] != x[2]]
    cnt = lambda rows, k: {c: sum(1 for x in rows if x[k] == c) for c in ("a", "b", "O")}
    L.case(len(rows57) == 57 and not mv57,
           f"W2-148's trial lists (S23), the 57 ACT files with their commits, classed with both tables: none changes class (old {cnt(rows57, 1)}, new {cnt(rows57, 2)})")
    L.case(len(rowsall) > 57 and all(any(t["path"] in ("CLAUDE.md", "AGENTS.md") for t in trial.act_manifest(entries.get(a) or {"act": a, "commits": [], "repo_paths": [], "home_paths": [], "crontab": False, "flags": []}, ttmp / ("re-" + a), (trial.PKG / (a + ".md")).read_text(errors="replace"))["touched"]) for a, _, _ in mvall),
           f"every ACT file in the packages folder ({len(rowsall)}), the trial's way, both tables: " +
           (f"{len(mvall)} change class, each one that touches CLAUDE.md or AGENTS.md: " + ', '.join(f'{a} {o} to {n}' for a, o, n in mvall) if mvall
            else f"none changes class (old {cnt(rowsall, 1)}, new {cnt(rowsall, 2)})"))
    seen, moved = 0, []
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
    L.case(seen > 20 and all(any(t.get("path") in ("CLAUDE.md", "AGENTS.md") and t.get("root") == "repo" for t in json.loads((ORCH / "acts" / a / "manifest.json").read_text())["touched"]) for a, _, _ in moved),
           f"every bundle under acts/ ({seen}) classified with both tables: {len(moved)} change, each one that touches the repository's CLAUDE.md or AGENTS.md{': ' + ', '.join(f'{a} {o} to {n}' for a, o, n in moved) if moved else ''}")
    c_old = act_class.classify(str(RULES1), old_rules)
    c_new = act_class.classify(str(RULES1), new_rules)
    L.case(c_old["class"] == "O" and c_new["class"] == "b" and not c_new["hits"]
           and {f["path"]: f["row"] for f in c_new["files"]} == {".rulesync/rules/governance.md": "rulesync-other", "CLAUDE.md": NEW_ROW, "AGENTS.md": NEW_ROW},
           f"ACT-CLAUDE-RULES-1's bundle (act_class.classify): old table {c_old['class']}, new table {c_new['class']} (rows {sorted({f['row'] for f in c_new['files']})}, no hit)")
    sys.path.remove(str(old_install))

    # ------------------------------------------------------------------------------------------ part 4
    L.note("part 4: the operator's own tests on a clone (`git clone --no-hardlinks` of w2/integrate's head) with the after file, through heavy_slot.sh, TMPDIR outside the repository and ~/gov-os-runs, PYTHONUSERBASE=/home/usain/.local, -p no:cacheprovider")
    if os.environ.get("CRA_SKIP_TESTS") == "1":
        L.case(False, "part 4 skipped (CRA_SKIP_TESTS=1: a draft run, never the final rehearsal)")
    else:
        clone = WORK / "clone"
        wtmp = WORK / "pytest-tmp"
        wtmp.mkdir()
        subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(REPO), str(clone)], check=True)
        L.note(f"the clone's head: {run(['git', '-C', str(clone), 'rev-parse', '--short=12', 'HEAD']).stdout.strip()}")
        L.case(sha(clone / RULES_REL) == before[("repo", RULES_REL)], "the clone's class-rules.yaml is the before")
        shutil.copy2(BUNDLE / "after/repo" / RULES_REL, clone / RULES_REL)
        L.case(sha(clone / RULES_REL) == rules_after, "the clone's class-rules.yaml is the after")
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
               "the clone's only change is class-rules.yaml (the tests wrote nothing into the tree)")

    # ------------------------------------------------------------------------------------------ part 5
    exec(compile((HERE / "part5.py").read_text(), str(HERE / "part5.py"), "exec"), globals())
    part5(L, tmp, world)  # noqa: F821


def finalize():
    log = BUNDLE / "rehearsal.log"
    if not log.read_text().rstrip().endswith("failures: 0"):
        sys.exit("the rehearsal did not end with failures: 0: not finalized")
    print(f"manifest sha256 {write_manifest(sha(log))}")


def gates():
    sys.path.insert(0, str(LIVE_INST))
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
    assert not list(BUNDLE.rglob("__pycache__"))
    print(f"files: {len(m['files'])} hash as the manifest says; no file in the bundle unlisted; no __pycache__")
    s = {"repo": str(REPO), "home": str(Path.home())}
    for where, text in [("apply.sh", (BUNDLE / "apply.sh").read_text())] + [("a check", c["cmd"]) for c in m["checks"]]:
        why = orun.live_path_refs(text, s)
        print(f"path rule on {where}: {'pass' if why is None else why}")
    v = act_class.classify(str(BUNDLE))
    print(f"act_class.classify (the bundle, the live table): class {v['class']}; hits {v['hits']}")
    for f in v["files"]:
        print(f"  {f['root']}|{f['path']}: {f['class']} (row {f['row']})")
    va = act_class.classify_manifest(dict(m, touched=m["alt_base"]["touched"]), None)
    print(f"act_class.classify_manifest (the LANDING base's rows): class {va['class']}")
    vn = act_class.classify_manifest(m, str(BUNDLE), act_class.load_rules(str(BUNDLE / "after/home" / INST_RULES)))
    print(f"act_class.classify_manifest (the bundle under its own after table): class {vn['class']}")
    print(f"manifest sha256 {sha(BUNDLE / 'manifest.json')}")


if __name__ == "__main__":
    {"build": build, "rehearse": rehearse, "finalize": finalize, "gates": gates,
     "all": lambda: (build(), rehearse(), finalize(), gates())}[sys.argv[1]]()
