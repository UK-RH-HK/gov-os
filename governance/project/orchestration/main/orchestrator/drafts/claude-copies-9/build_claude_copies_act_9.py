"""Builds and rehearses ACT-CLAUDE-COPIES-9 (the generated copies of W2-37's approved change-skill bytes: the root
.rulesync/skills/change/SKILL.md, a byte copy of the template source, and rulesync 24.0.0's rendering of it,
.claude/skills/change/SKILL.md; the owner's "yes W2-37 CIT-P a25b02a7, version 1.1.0", DEC-1166 (4); DEC-315, DEC-1112 (3),
DEC-1156 (3), CAP-33). Adapted from drafts/claude-copies-7/build_claude_copies_act_7.py (not edited). Changes:

  * the files exist already (all replaced, not new): the before-bytes are integrate's, required equal to the merged
    tree's (W2-37 does not touch either), so before/ is written and undo restores them;
  * BASE is built here: a clone of integrate with refs/heads/w2/W2-37 (head 7bde87727b0f, asserted) merged by one --no-ff
    commit, exactly what the operator sees after the CTO's hand merge;
  * the sources (check 2) are the two template files of W2-37's CIT-P: template/governance/kernel/skills/change/SKILL.md and
    template/.rulesync/skills/change/SKILL.md, both at cdf43a49 (red on plain integrate: they are the old bytes there, so
    the operator's G8 refuses a run before the hand merge);
  * the root .rulesync copy is written into the generation clone as a byte copy of template/.rulesync's file, then rulesync
    24.0.0 runs from that root .rulesync (portability's own GENERATE form). Its .claude/skills/change/SKILL.md is required
    to equal the lead's expected bytes (dc4d01de...); if it differs the builder reports both hashes and stops.
    Rulesync's other differing output (.claude/settings.json by DEC-616) is not written and not part of this ACT;
  * v2 (the coordinator's addition): the stale .claude/skills/adopt/SKILL.md is folded in. Its sources (kernel, root
    .rulesync, template/.rulesync; W2-88a's CIT-P, DEC-1163 (8)) are all at 16fd341f...; rulesync renders the copy from the
    root .rulesync/ with the same GENERATE form; the three sources are pinned in check 2 beside the change skill's. The
    touched set is three files, and portability must then read exit 0 with no finding after the apply;
  * integrate is fully landed (COPIES-6, -7, -8 applied): no full-landed or other-order rehearsal; the gated runs are the
    merged tree's window and landed pairs only.

    python3 -I build_claude_copies_act_9.py <INTEGRATE clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INTEG, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-9"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: the branch to merge, and proof the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
C6 = ORCH / "acts/ACT-CLAUDE-COPIES-6"
C7 = ORCH / "acts/ACT-CLAUDE-COPIES-7"
EXPECTED_FILE = Path("/home/usain/gov-os-worktrees/W2-37/.gov-runtime/scratch/lead/changes/expected-claude-change-SKILL-1.1.0.md")
W237 = "7bde87727b0f"
SRC_SHA = "cdf43a49709676acbd6d253178b193445d5e4505611bb5280bdb69cb7d3c3a76"      # the template source at W2-37's head
CLAUDE_SHA = "dc4d01de95fb22703f3ef2db79ce5ca516990d641bb6f425af1732cce99f7cd8"   # the lead's expected rulesync rendering
SKILL = "change"
ADOPT_SHA = "16fd341f267b4300c3e7e7ef779933e889b1cc8d6a574d8bff5270bb0d60d0a0"   # W2-88a's CIT-P, the approved bytes
ADOPT_SOURCES = ("template/governance/kernel/skills/adopt/SKILL.md", ".rulesync/skills/adopt/SKILL.md",
                 "template/.rulesync/skills/adopt/SKILL.md")
ADOPT_COPY = ".claude/skills/adopt/SKILL.md"
KERNEL_SRC = f"template/governance/kernel/skills/{SKILL}/SKILL.md"
TEMPLATE_SRC = f"template/.rulesync/skills/{SKILL}/SKILL.md"
ROOT_SRC = f".rulesync/skills/{SKILL}/SKILL.md"
CLAUDE_COPY = f".claude/skills/{SKILL}/SKILL.md"
EXPECTED_TOUCHED = sorted([ROOT_SRC, CLAUDE_COPY, ADOPT_COPY])
SOURCES = (KERNEL_SRC, TEMPLATE_SRC)
PINS = {**{s_: SRC_SHA for s_ in SOURCES}, **{a: ADOPT_SHA for a in ADOPT_SOURCES}}
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-37", "tests/unit/impact", "tests/unit/adapters", "tests/acceptance/W1-33",
         "tests/acceptance/W1-38", "tests/acceptance/W2-153", "tests/acceptance/W2-11", "tests/acceptance/W2-98", "tests/acceptance/W2-88a", "tests/acceptance/W2-52"]
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")
APPLY_SH = (C6 / "apply.sh").read_text()   # the same apply.sh as ACT-CLAUDE-COPIES-1 to -8
assert APPLY_SH == (C7 / "apply.sh").read_text()


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


GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
SCRATCH.mkdir(parents=True, exist_ok=True)
TMP = SCRATCH / "tmp"
TMP.mkdir(exist_ok=True)
INTEG_HEAD = run(["git", "rev-parse", "HEAD"], INTEG)[1]
assert run(["git", "status", "--porcelain", "--untracked-files=all"], INTEG)[1] == ""

# BASE: integrate with w2/W2-37 merged by one commit, as after the CTO's hand merge
BASE = SCRATCH / "base-merged"
clone(INTEG, BASE)
assert run(["git", "fetch", "-q", str(LIVE_TREE), "refs/heads/w2/W2-37:refs/heads/w2/W2-37"], BASE)[0] == 0
w237_head = run(["git", "rev-parse", "--short=12", "refs/heads/w2/W2-37"], BASE)[1]
assert w237_head == W237, f"w2/W2-37 is at {w237_head}, not the approved {W237}"
code, out = run(["git", "-c", "user.name=rehearsal", "-c", "user.email=rehearsal@example.invalid", "merge", "--no-ff", "-q",
                 "-m", "Merge w2/W2-37 (rehearsal of the CTO's hand merge)", "refs/heads/w2/W2-37"], BASE)
assert code == 0, out
assert run(["git", "status", "--porcelain", "--untracked-files=all"], BASE)[1] == ""
gen = SCRATCH / "gen-clone"
clone(BASE, gen)
say(f"{ACT} rehearsal; base: integrate {INTEG_HEAD[:12]} with w2/W2-37 {W237} merged (one --no-ff commit, clean); rulesync "
    f"{run([RULESYNC, '--version'], SCRATCH)[1]}")

# the sources at W2-37's approved bytes
for src in SOURCES:
    assert sha((gen / src).read_bytes()) == SRC_SHA, f"{src} is not at {SRC_SHA}"
for src in ADOPT_SOURCES:
    assert sha((gen / src).read_bytes()) == ADOPT_SHA, f"{src} is not at {ADOPT_SHA}"
shown = subprocess.run(["git", "show", f"refs/heads/w2/W2-37:{TEMPLATE_SRC}"], cwd=BASE, capture_output=True).stdout
assert sha(shown) == SRC_SHA, "the branch's template source is not the approved bytes"
say(f"the two template sources ({KERNEL_SRC}, {TEMPLATE_SRC}) are at {SRC_SHA[:8]}, the bytes of w2/W2-37 {W237}")
say(f"the three adopt sources {list(ADOPT_SOURCES)} are at {ADOPT_SHA[:8]}, W2-88a's approved bytes")


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
    return [f for f in found if f"/{SKILL}/" in str(f.get("file", "")) or f"/adopt/" in str(f.get("file", ""))]


def others(found):
    return sorted((f["code"], f.get("file", "")) for f in found if f not in ours(found))


code, int_found = portability(INTEG)
say(f"portability on plain integrate: exit {code}; {len(int_found)} findings: {tally(int_found)}; "
    f"files {sorted(f.get('file') for f in int_found)}")
OTHERS_INTEG = others(int_found)
assert [(f["code"], f["file"]) for f in int_found] == [("GENERATED_DIFFERS", ADOPT_COPY)], int_found
code, base_found = portability(gen)
say(f"portability on the merged tree (no copies): exit {code}; {len(base_found)} findings: {tally(base_found)}; "
    f"of them the change skill's: {[(f['code'], f['file']) for f in ours(base_found)]}")
BASE_OTHERS = others(base_found)
assert BASE_OTHERS == OTHERS_INTEG, "W2-37's merge changes a finding that is not the change skill's"
assert BASE_OTHERS == [], BASE_OTHERS
say("  no finding outside the change and adopt skills' copies")


def fresh_generation(root):
    """rulesync's output from root/.rulesync into a fresh folder; returns (folder object, list of relative files)."""
    d = tempfile.TemporaryDirectory()
    code, out = run([RULESYNC, *GENERATE, str((root / ".rulesync").resolve())], d.name)
    assert code == 0, out
    return d


# the generation on the unchanged merged tree: only the two known drifts differ (settings.json, the adopt skill)
with fresh_generation(gen) as fresh:
    differ0 = sorted(str(p.relative_to(fresh)) for p in Path(fresh).rglob("*")
                     if p.is_file() and not ((gen / p.relative_to(fresh)).is_file()
                                              and (gen / p.relative_to(fresh)).read_bytes() == p.read_bytes()))
say(f"rulesync from the merged tree's own root .rulesync (before the copy): differs from the tree in {differ0}")
assert CLAUDE_COPY not in differ0, "the .claude copy already matches the old root source"
assert ADOPT_COPY in differ0, "the adopt copy is not stale"

# step 1: the root .rulesync copy is a byte copy of the template source
before_bytes = {ROOT_SRC: (gen / ROOT_SRC).read_bytes(), CLAUDE_COPY: (gen / CLAUDE_COPY).read_bytes(),
                ADOPT_COPY: (gen / ADOPT_COPY).read_bytes()}
(gen / ROOT_SRC).write_bytes((gen / TEMPLATE_SRC).read_bytes())
assert sha((gen / ROOT_SRC).read_bytes()) == SRC_SHA
# step 2: rulesync's own rendering from that source
with fresh_generation(gen) as fresh:
    made = Path(fresh) / CLAUDE_COPY
    assert made.is_file(), "rulesync made no change skill"
    rendered = made.read_bytes()
    adopt_rendered = (Path(fresh) / ADOPT_COPY).read_bytes()
    differ1 = sorted(str(p.relative_to(fresh)) for p in Path(fresh).rglob("*")
                     if p.is_file() and not ((gen / p.relative_to(fresh)).is_file()
                                              and (gen / p.relative_to(fresh)).read_bytes() == p.read_bytes()))
got = sha(rendered)
expected_lead = sha(EXPECTED_FILE.read_bytes())
say(f"rulesync's .claude/skills/change/SKILL.md: {got}; the expected hash {CLAUDE_SHA}; the lead's expected file {expected_lead}")
if got != CLAUDE_SHA or expected_lead != CLAUDE_SHA:
    say("MISMATCH: the generated bytes are not the expected ones; stopping before any bundle is written")
    print(json.dumps({"stopped": True, "generated": got, "expected": CLAUDE_SHA, "lead_file": expected_lead}))
    sys.exit(2)
(gen / CLAUDE_COPY).write_bytes(rendered)
(gen / ADOPT_COPY).write_bytes(adopt_rendered)
say(f"rulesync's .claude/skills/adopt/SKILL.md (from the root .rulesync/ at {ADOPT_SHA[:8]}): {sha(adopt_rendered)}; "
    f"the tracked copy was {sha(before_bytes[ADOPT_COPY])}")
not_written = [r for r in differ1 if r not in (CLAUDE_COPY, ADOPT_COPY)]
say(f"rulesync's other output that differs from the tree (not written, not this ACT's): {not_written}")
assert [r for r in differ1 if r.startswith(GENERATED_FOLDERS) and r != CLAUDE_COPY] == [r for r in differ0
       if r.startswith(GENERATED_FOLDERS)], "the copy changes another generated file"
assert not any(r.startswith(("template/", ".rulesync/")) for r in differ1), "the generation writes under a source folder"
code, after = portability(gen)
say(f"portability in the generation clone after the three copies: exit {code}; change-skill findings {ours(after)}; "
    f"the others unchanged: {others(after) == BASE_OTHERS}")
assert not ours(after) and others(after) == BASE_OTHERS, after
tcode, tfound = portability(gen / "template", rulesync=False)
say(f"portability on template/ (as an adopted project, no rulesync): {len(ours(tfound))} change-skill findings; "
    f"others: {tally([f for f in tfound if f not in ours(tfound)])}")
assert not ours(tfound), tfound
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert TOUCHED == EXPECTED_TOUCHED, TOUCHED
say(f"generation clone: {len(TOUCHED)} files changed: " + ", ".join(TOUCHED))
say(f"  {ROOT_SRC}: byte copy of {TEMPLATE_SRC}; {CLAUDE_COPY}: rulesync's rendering of it ({len(rendered)} bytes); "
    f"{ADOPT_COPY}: rulesync's rendering of the adopt source ({len(adopt_rendered)} bytes)")
code, after2 = portability(gen)
assert code == 0 and not after2, (code, after2)
say("portability in the generation clone: exit 0, no finding")

# the bundle: before-bytes are integrate's, required equal to the merged tree's
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
    cur = (INTEG / rel).read_bytes()
    assert cur == (BASE / rel).read_bytes() == before_bytes[rel], f"{rel}: W2-37 changes it"
    new = (gen / rel).read_bytes()
    before, after_h = sha(cur), sha(new)
    assert before != after_h, rel
    put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after_h})
    lines.append(f"repo|{rel}|{before}|{after_h}")
say("the before-bytes are integrate's and equal on the merged tree: " +
    ", ".join(f"{t['path']} {t['before'][:8]}" for t in touched))
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
copies = [(t["path"], t["after"]) for t in touched]
sources = list(PINS.items())
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(sources)), "exit": 0, "count": None}]
assert not HOME_RX.search(json.dumps(checks)) and "~" not in json.dumps(checks) and "HOME" not in json.dumps(checks)
say(f"check 1: the {len(copies)} copies; check 2: the {len(sources)} sources (the two change-skill template files at {SRC_SHA[:8]}, the three adopt sources at {ADOPT_SHA[:8]}); no live HOME path in either")

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


# 1. apply, verify, undo, re-apply on the merged tree
say("--- rehearsal on integrate with W2-37 merged (the tree after the hand merge's merge commit); HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
before_state = tree_state(reh)
step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copies are at the old bytes)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: the two template sources at the approved bytes)", checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the apply: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
mark(tree_state(reh) == before_state and changed_set(reh) == [], "undo: both files byte for byte back, the tree clean")
pcode, pfound = portability(reh)
mark(sorted((f["code"], f.get("file")) for f in pfound) == sorted((f["code"], f.get("file")) for f in base_found),
     f"portability after the undo: exit {pcode}; {len(pfound)} findings: {tally(pfound)} (the merged tree's own reading)")
step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
     "the re-apply gives the same bytes and the same changed set as the first apply")

# 2. plain integrate: the check passes (the before bytes are the same there); check 2 is red, so G8 refuses
say("--- plain integrate (W2-37 not merged)")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (both targets are at the same before bytes there as on the merged tree)",
     f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (the template sources are the old bytes there: the order is held)",
     checks[1]["cmd"], expect=1)
mark(changed_set(ri) == [], "check changed nothing")
# a moved target is refused
mv = SCRATCH / "rehearsal-moved"
clone(BASE, mv)
(mv / CLAUDE_COPY).write_bytes((mv / CLAUDE_COPY).read_bytes() + b"x")
step(mv, "apply.sh check refuses a moved target (exit 3)", f"bash {BUNDLE}/apply.sh check", expect=3)

# 3. the gated runs: window and landed on the merged tree
say("--- the gated runs, one folder per run through the heavy-job gate: on the merged tree (W2-37's merge alone, then "
    "with this ACT)")
results = {"window": {r[0]: r for r in gated_all(win, "merged-window")},
           "landed": {r[0]: r for r in gated_all(reh, "merged-landed")}}
rw, ra = results["window"], results["landed"]
red_w, red_a = set(), set()
for folder in GATED:
    _, code, m, ok, failed = rw[folder]
    red_w |= set(failed)
    say(f"merged window {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
        + (f", {m['skipped']} skipped" if m.get("skipped") else ""))
for folder in GATED:
    _, code, m, ok, failed = ra[folder]
    red_a |= set(failed)
    new = [t for t in failed if t not in red_w]
    mark(ok and m.get("passed", 0) > 0 and not new,
         f"merged landed {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
         + (f", {m['skipped']} skipped" if m.get("skipped") else "") + (f"; new red: {new}" if new else ""))
for t in sorted(red_w - red_a):
    say(f"     merged: made green by the ACT: {t}")
for t in sorted(red_a):
    say(f"     merged: red after the ACT: {t}")
say(f"merged: red in the window: {len(red_w)}; made green by the ACT: {len(red_w - red_a)}; red after: {len(red_a)}; "
    f"new red brought by the ACT: {sorted(red_a - red_w)}")
(SCRATCH / "red-merged-window.txt").write_text("\n".join(sorted(red_w)) + "\n")
(SCRATCH / "red-merged-landed.txt").write_text("\n".join(sorted(red_a)) + "\n")

# 4. the by-hand steps literally: stage, commit, undo, commit (on the merged tree)
say("--- the by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
step(reh, "git add the touched paths", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add -A {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-315, DEC-1112 (3), DEC-1156 (3), DEC-1166 (4), CAP-33", "author": "cto", "claimed_class": "b",
      "touched": touched, "files": files, "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
      "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
