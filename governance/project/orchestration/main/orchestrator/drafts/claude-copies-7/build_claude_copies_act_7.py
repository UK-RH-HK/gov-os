"""Builds and rehearses ACT-CLAUDE-COPIES-7 (the generated .claude/skills copy of W2-98's new kernel skill spec-writing;
the owner's CIT-P approval at 3a86f11c3981, 2026-11-13; DEC-315, DEC-1112 (3), DEC-1156 (3), CAP-33). Adapted from
drafts/claude-copies-6/build_v2.py (not edited), with the skills handling of drafts/claude-copies-5/
build_claude_copies_act_5.py (not edited). Changes from build_v2.py:

  * BASE is a clone of integrate with w2/W2-98 merged into it (a clean merge, measured). W2-98 itself carries the root
    .rulesync/skills/spec-writing/ and template/.rulesync/skills/spec-writing/ copies (CIT-P section 2), byte-equal to the
    kernel: the builder asserts the twelve files at the CIT-P section 3 hashes. A skill has no compose(): portability
    compares a kernel skill with its .rulesync source by bytes (SKILL.md by front matter and body). The builder still
    runs compose() for the nine roles and requires it to give ACT-CLAUDE-COPIES-6's after bytes, so W2-98 changes no
    role composition;
  * .claude/skills/ by the clone's rulesync 24.0.0 from the root .rulesync/ (portability's own GENERATE form), never by
    hand. The touched set is the rulesync output under the generated folders that differs from BASE, required to be
    exactly the four files of .claude/skills/spec-writing/;
  * the generation writes nothing under template/ (no role source changes, and the template's skill copy is W2-98's
    own): so there is NO template patch and no CTO template commit; the builder asserts it;
  * the before-bytes are integrate's (absent), required equal to BASE's (absent);
  * check 1 the four copies; check 2 the twelve sources (the four kernel files at the CIT-P hashes, the four root and the
    four template .rulesync copies): red on plain integrate (the files are absent), so the operator's G8 refuses a run
    before the hand merge; no live HOME path in either (asserted by pattern);
  * integrate still holds ACT-CLAUDE-COPIES-6's and -8's window (neither applied at build time). The rehearsal runs on
    BASE (the merge alone) and on BASE with COPIES-6 then COPIES-8 applied by their own apply.sh (the fully landed
    tree, where portability must read exit 0), and the other order (this ACT first, then COPIES-6 and -8);
  * the gated runs: one folder per run through heavy_slot.sh, before (the window) and after (the ACT) on both trees;
    the ACT must bring no new red, and the W2-98 suite must be green after it.

    python3 -I build_claude_copies_act_7.py <BASE clone> <INTEGRATE clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE, INTEG, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:5])
ACT = sys.argv[5] if len(sys.argv) > 5 else "ACT-CLAUDE-COPIES-7"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: only to prove the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
C6 = ORCH / "acts/ACT-CLAUDE-COPIES-6"
C8 = ORCH / "acts/ACT-CLAUDE-COPIES-8"
W298 = "3a86f11c3981"
SKILL = "spec-writing"
KERNEL_SKILL = f"template/governance/kernel/skills/{SKILL}"
KERNEL_ROLES = "template/governance/kernel/roles"
CITP = {  # CIT-P section 3, the owner-approved bytes at 3a86f11c3981
    "SKILL.md": "34500d5ed3694abce258ee73616bc2832cc169ff0083c66e46b9c82453c8637d",
    "check_spec.py": "b18ebd98028e33aa06c2b3aba634e0a7b012122db304b48436c616aa1c15f310",
    "imports.yaml": "3ddd0e1ab98d22585922395b0915014db4f048994be757b8283422986f9f9cff",
    "spec-form.md": "9174042b22312e69aac2fe4b02ca16e48216566371cf22e781a3985f3c604e4f",
}
SOURCE_TREES = (KERNEL_SKILL, f".rulesync/skills/{SKILL}", f"template/.rulesync/skills/{SKILL}")
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-98", "tests/unit/adapters", "tests/acceptance/W1-33", "tests/acceptance/W1-38",
         "tests/acceptance/W2-153", "tests/acceptance/W2-11"]   # one folder per pytest run
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")
APPLY_SH = (C6 / "apply.sh").read_text()   # the same apply.sh as ACT-CLAUDE-COPIES-1 to -6 and -8


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def clone(src, dest):
    if dest.exists():
        shutil.rmtree(dest)
    head = run(["git", "rev-parse", "HEAD"], src)[1]
    assert run(["git", "clone", "-q", "--no-hardlinks", str(src), str(dest)], SCRATCH)[0] == 0
    assert run(["git", "checkout", "-q", head], dest)[0] == 0
    return head


log = []
def say(line):
    log.append(line)
    print(line, flush=True)


SCRATCH.mkdir(parents=True, exist_ok=True)
TMP = SCRATCH / "tmp"
TMP.mkdir(exist_ok=True)
gen = SCRATCH / "gen-clone"
clone(BASE, gen)
say(f"{ACT} rehearsal; base: integrate with w2/W2-98 {W298} merged; rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")
assert run(["git", "merge-base", "--is-ancestor", W298, "HEAD"], gen)[0] == 0, "BASE does not contain w2/W2-98"

# the twelve sources at the owner-approved bytes
for tree in SOURCE_TREES:
    held = sorted(p.name for p in (gen / tree).rglob("*") if p.is_file())
    assert held == sorted(CITP), (tree, held)
    for name, h in CITP.items():
        assert sha((gen / tree / name).read_bytes()) == h, f"{tree}/{name} is not the CIT-P's bytes"
say(f"the twelve sources (kernel, root .rulesync, template/.rulesync; 4 files each) at the CIT-P section 3 hashes "
    f"(approved at {W298})")


def portability(tree, rulesync=True):
    env = dict(os.environ, PYTHONPATH=str(gen / "src"), RULESYNC_BIN=RULESYNC if rulesync else "/nonexistent/rulesync")
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


def ours(found):
    return [f for f in found if f"/{SKILL}/" in str(f.get("file", ""))]


def others(found):
    return sorted((f["code"], f.get("file", "")) for f in found if f not in ours(found))


code, base_found = portability(gen)
say(f"portability on the base (W2-98 merged, no copies): exit {code}; {len(base_found)} findings: {tally(base_found)}; "
    f"of them spec-writing's: {tally(ours(base_found))}")
BASE_OTHERS = others(base_found)
say(f"  the others are ACT-CLAUDE-COPIES-6's and -8's window (neither applied on integrate): {tally([f for f in base_found if f not in ours(base_found)])}")


def compose(root, role):
    probe = ("import sys, json; sys.path.insert(0, sys.argv[1] + '/src'); from gov.adapters import portability as p; "
             "from pathlib import Path; print(json.dumps(p.compose(Path(sys.argv[2]), sys.argv[3])))")
    code, out = run([sys.executable, "-I", "-c", probe, str(gen), str(root), role], gen)
    if code != 0:
        raise SystemExit(f"compose() failed for {root} {role}: {out[-300:]}")
    return json.loads(out)


# compose() for the nine roles: W2-98 changes no role composition (the bytes are COPIES-6's after files)
c6after = {}   # COPIES-6's after bytes, with COPIES-8's where it rewrites a source (the orchestrator's)
for bundle in (C6, C8):
    for line in (bundle / "list.txt").read_text().splitlines():
        if line.startswith("repo|.rulesync/subagents/"):
            rel, after = line.split("|")[1], line.split("|")[3]
            c6after[Path(rel).stem] = after
roles = sorted(p.stem for p in (gen / KERNEL_ROLES).glob("*.md"))
assert len(roles) == 9, roles
existing = [r for r in roles if (gen / ".rulesync/subagents" / f"{r}.md").is_file()]
for role in existing:
    got = sha(compose(gen, role).encode())
    assert got == c6after[role], (role, got)
say(f"compose() for the {len(existing)} roles with a source on the base gives ACT-CLAUDE-COPIES-6's after bytes (-8's for the orchestrator; the "
    f"other {len(roles) - len(existing)} need COPIES-6's front matter; portability exit 0 on the fully landed tree "
    "covers them): W2-98 changes no role composition, so no role source is in this ACT")

made_others = []
with tempfile.TemporaryDirectory() as fresh:
    code, out = run([RULESYNC, *GENERATE, str((gen / ".rulesync").resolve())], fresh)
    assert code == 0, out
    for path in sorted(Path(fresh).rglob("*")):
        rel = str(path.relative_to(fresh))
        if not path.is_file() or ((gen / rel).is_file() and (gen / rel).read_bytes() == path.read_bytes()):
            continue
        if rel.startswith(GENERATED_FOLDERS):
            (gen / rel).parent.mkdir(parents=True, exist_ok=True)
            (gen / rel).write_bytes(path.read_bytes())
        else:
            made_others.append(rel)
say(f"rulesync's other output that differs from the tree (not written; as in ACT-CLAUDE-COPIES-5 and -6): {made_others}")
code, after = portability(gen)
say(f"portability in the generation clone after the copies: exit {code}; spec-writing findings {ours(after)}; "
    f"the others unchanged: {others(after) == BASE_OTHERS}")
assert not ours(after) and others(after) == BASE_OTHERS, after
tcode, tfound = portability(gen / "template", rulesync=False)
say(f"portability on template/ (as an adopted project, no rulesync): {len(ours(tfound))} spec-writing findings; "
    f"others: {tally([f for f in tfound if f not in ours(tfound)])}")
assert not ours(tfound), tfound
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert TOUCHED == sorted(f".claude/skills/{SKILL}/{n}" for n in CITP), TOUCHED
assert not any(r.startswith("template/") for r in TOUCHED)
say(f"generation clone: {len(TOUCHED)} files new: " + ", ".join(TOUCHED))
say("the generation writes nothing under template/ or .rulesync/: no template patch, no CTO template commit; the root "
    "and template .rulesync copies are W2-98's own (its merge brings them)")
for n in CITP:
    g = (gen / ".claude/skills" / SKILL / n).read_bytes()
    k = (gen / KERNEL_SKILL / n).read_bytes()
    say(f"  .claude/skills/{SKILL}/{n}: " + ("byte-equal to the kernel file" if g == k else
                                             f"rulesync's rendering of the kernel file ({len(g)} bytes, kernel {len(k)})"))

# the bundle: before-bytes are integrate's, required equal to BASE's
if BUNDLE.exists():
    shutil.rmtree(BUNDLE)
BUNDLE.mkdir(parents=True)
files, touched, lines = {}, [], []
def put(rel, data):
    p = BUNDLE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    files[rel] = sha(data)


for rel in TOUCHED:
    cur = (INTEG / rel).read_bytes() if (INTEG / rel).is_file() else None
    assert cur == ((BASE / rel).read_bytes() if (BASE / rel).is_file() else None), f"{rel}: W2-98 changes it"
    new = (gen / rel).read_bytes()
    before, after_h = (sha(cur) if cur is not None else None), sha(new)
    assert before != after_h, rel
    if cur is not None:
        put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after_h})
    lines.append(f"repo|{rel}|{before or 'null'}|{after_h}")
say(f"the before-bytes are integrate's and equal on integrate with W2-98 merged ({sum(1 for t in touched if t['before'])} "
    f"changed, {sum(1 for t in touched if not t['before'])} new)")
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
copies = [(t["path"], t["after"]) for t in touched]
sources = [(f"{tree}/{n}", h) for tree in SOURCE_TREES for n, h in CITP.items()]
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(sources)), "exit": 0, "count": None}]
assert not HOME_RX.search(json.dumps(checks)) and "~" not in json.dumps(checks) and "HOME" not in json.dumps(checks)
say(f"check 1: the {len(copies)} copies; check 2: the {len(sources)} sources; no live HOME path in either")

planted = Path(tempfile.mkdtemp(prefix="planted-home-", dir=SCRATCH))  # the operator's G8 plants HOME the same way
live_state = lambda: {rel: (sha((LIVE_TREE / rel).read_bytes()) if (LIVE_TREE / rel).is_file() else None) for rel in TOUCHED}
live_before = live_state()
fails = 0


def mark(ok, text):
    global fails
    fails += 0 if ok else 1
    say(f"{'ok  ' if ok else 'FAIL'} {text}")
    return ok


def step(tree, name, cmd, expect=0):
    code, out = run(["bash", "-c", cmd], tree, dict(os.environ, HOME=str(planted)))
    mark(code == expect, f"{name}: exit {code}{(' ' + out[-300:]) if out and code != expect else ''}")
    return code, out


def tree_state(tree):
    return {rel: ((tree / rel).read_bytes() if (tree / rel).is_file() else None) for rel in TOUCHED}


def changed_set(tree):
    st = run(["git", "status", "--porcelain", "--untracked-files=all"], tree)[1].splitlines()
    return sorted(l.strip().split(None, 1)[1] for l in st)


SUMMARY = re.compile(r"^(?:\d+ (?:passed|failed|errors?|skipped|xfailed|xpassed|deselected|warnings?)(?:, )?)+ in [\d.]+s(?: \(.*\))?$")
FAILED_LINE = re.compile(r"^(?:FAILED|ERROR) (\S+)")


def gated(tree, folder, label):
    """One folder, one pytest run, through the heavy-job gate; the result from pytest's own summary line and its -rfE
    lines (anchored at the line's start)."""
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), TMPDIR=str(TMP), PYTHONUSERBASE="/home/usain/.local")
    code, out = run(["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={tree / 'src'}", "PYTHONUSERBASE=/home/usain/.local",
                     "python3", "-m", "pytest", folder, "-q", "-rfE", "-p", "no:cacheprovider",
                     "-o", "tmp_path_retention_policy=failed"], tree, env)
    summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
    m = {k.rstrip("s") if k.startswith("error") else k: int(v)
         for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
    failed = sorted({mm.group(1) for ln in out.splitlines() if (mm := FAILED_LINE.match(ln.strip()))})
    (SCRATCH / f"{label}-{folder.replace('/', '_')}.txt").write_text(out + "\n")
    return folder, code, m, bool(summary), failed


def gated_all(tree, label):
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda f: gated(tree, f, label), GATED))


GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"

# 1. apply, verify, undo, re-apply on the merged tree
say("--- rehearsal on integrate with W2-98 merged (the tree after the hand merge's merge commit); HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
before_state = tree_state(reh)
step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copies are absent)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: W2-98's twelve sources at the approved bytes)", checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS,
     f"portability after the apply: exit {pcode}; spec-writing findings {ours(pfound)}; the {len(BASE_OTHERS)} others "
     "(COPIES-6's and -8's window) unchanged")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
mark(tree_state(reh) == before_state and changed_set(reh) == [], "undo: every file byte for byte back, the tree clean")
pcode, pfound = portability(reh)
mark(sorted((f["code"], f.get("file")) for f in pfound) == sorted((f["code"], f.get("file")) for f in base_found),
     f"portability after the undo: exit {pcode}; {len(pfound)} findings: {tally(pfound)} (the base's own reading)")
step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
     "the re-apply gives the same bytes and the same changed set as the first apply")

# 2. plain integrate: the check passes (the files are absent there too); check 2 is red, so G8 refuses
say("--- plain integrate (W2-98 not merged)")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (the four copies are absent there as on the merged tree)",
     f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (W2-98's sources are absent: the order is held)", checks[1]["cmd"], expect=1)
mark(changed_set(ri) == [], "check changed nothing")

# 3. the fully landed tree: COPIES-6 then COPIES-8 applied by their own apply.sh, then this ACT
say("--- the merged tree with ACT-CLAUDE-COPIES-6 and then ACT-CLAUDE-COPIES-8 applied by their own apply.sh (both "
    "queued, neither applied on integrate at build time); HOME planted")
full = SCRATCH / "rehearsal-full"
clone(BASE, full)
for name, b in (("ACT-CLAUDE-COPIES-6", C6), ("ACT-CLAUDE-COPIES-8", C8)):
    step(full, f"{name}: apply.sh check, apply, commit",
         f"bash {b}/apply.sh check && bash {b}/apply.sh apply && git add -A $(cut -d'|' -f2 {b}/list.txt) && "
         f"{GIT} commit -q -m '{name} (rehearsal)' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
pcode, pfound = portability(full)
mark(pcode == 1 and pfound and not [f for f in pfound if f not in ours(pfound)],
     f"portability before this ACT: exit {pcode}; {len(pfound)} findings, all spec-writing's: {tally(pfound)}")
fullwin = SCRATCH / "window-full"
clone(full, fullwin)
step(full, "apply.sh check", f"bash {BUNDLE}/apply.sh check")
step(full, "check 2 before the apply", checks[1]["cmd"])
step(full, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(full, f"check {i}", c["cmd"])
mark(changed_set(full) == TOUCHED, "the changed set equals the touched list")
pcode, pfound = portability(full)
mark(pcode == 0 and not pfound, f"portability on the fully landed tree: exit {pcode}; findings {pfound}")

# 4. the other order: this ACT first on the merged tree, then COPIES-6 and COPIES-8 (disjoint paths)
say("--- the other order: this ACT on the merged tree, then ACT-CLAUDE-COPIES-6 and -8")
oth = SCRATCH / "rehearsal-other-order"
clone(BASE, oth)
step(oth, "this ACT: apply.sh check, apply, commit",
     f"bash {BUNDLE}/apply.sh check && bash {BUNDLE}/apply.sh apply && git add {' '.join(TOUCHED)} && "
     f"{GIT} commit -q -m '{ACT} (rehearsal)' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
for name, b in (("ACT-CLAUDE-COPIES-6", C6), ("ACT-CLAUDE-COPIES-8", C8)):
    step(oth, f"{name} after it: apply.sh check, apply, commit",
         f"bash {b}/apply.sh check && bash {b}/apply.sh apply && git add -A $(cut -d'|' -f2 {b}/list.txt) && "
         f"{GIT} commit -q -m '{name} (rehearsal)' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
for i, c in enumerate(checks, 1):
    step(oth, f"check {i}", c["cmd"])
pcode, pfound = portability(oth)
mark(pcode == 0 and not pfound, f"portability: exit {pcode}; findings {pfound}")
mark(changed_set(oth) == [], "the tree clean after the three ACTs' commits")
same = all((oth / r).read_bytes() == (full / r).read_bytes() for r in TOUCHED)
mark(same, "the four copies are the same bytes in either order")

# 5. the gated runs: window and landed on the merged tree, and on the fully landed tree
say("--- the gated runs, one folder per run through the heavy-job gate: on the merged tree (W2-98's merge alone, then "
    "with this ACT), and on the merged tree with COPIES-6 and -8 (without, then with this ACT)")
pairs = (("merged", win, reh), ("full", fullwin, full))
results = {}
for label, w, a in pairs:
    results[(label, "window")] = {r[0]: r for r in gated_all(w, f"{label}-window")}
    results[(label, "landed")] = {r[0]: r for r in gated_all(a, f"{label}-landed")}
for label, _w, _a in pairs:
    rw, ra = results[(label, "window")], results[(label, "landed")]
    red_w, red_a = set(), set()
    for folder in GATED:
        _, code, m, ok, failed = rw[folder]
        red_w |= set(failed)
        say(f"{label} window {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
            + (f", {m['skipped']} skipped" if m.get("skipped") else ""))
    for folder in GATED:
        _, code, m, ok, failed = ra[folder]
        red_a |= set(failed)
        new = [t for t in failed if t not in red_w]
        mark(ok and m.get("passed", 0) > 0 and not new and (folder != "tests/acceptance/W2-98" or code == 0),
             f"{label} landed {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
             + (f", {m['skipped']} skipped" if m.get("skipped") else "") + (f"; new red: {new}" if new else ""))
    for t in sorted(red_w - red_a):
        say(f"     {label}: made green by the ACT: {t}")
    for t in sorted(red_a):
        say(f"     {label}: red after the ACT: {t}")
    say(f"{label}: red in the window: {len(red_w)}; made green by the ACT: {len(red_w - red_a)}; red after: {len(red_a)}; "
        f"new red brought by the ACT: {sorted(red_a - red_w)}")
    (SCRATCH / f"red-{label}-window.txt").write_text("\n".join(sorted(red_w)) + "\n")
    (SCRATCH / f"red-{label}-landed.txt").write_text("\n".join(sorted(red_a)) + "\n")

# 6. the by-hand steps literally: stage, commit, undo, commit (on the merged tree)
say("--- the by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
step(reh, "git add the touched paths", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(not ours(pfound) and others(pfound) == BASE_OTHERS, f"portability after the commit: exit {pcode}; spec-writing findings {ours(pfound)}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add -A {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-315, DEC-1112 (3), DEC-1156 (3), CAP-33", "author": "cto", "claimed_class": "b",
      "touched": touched, "files": files, "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
      "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
