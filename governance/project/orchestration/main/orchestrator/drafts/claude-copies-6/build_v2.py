"""Builds and rehearses ACT-CLAUDE-COPIES-6 (the generated copies of W2-33's nine kernel role files; DEC-1156 (3),
DEC-1109 (2), DEC-1112 (3), CAP-33). Adapted from drafts/claude-copies-5/build_claude_copies_act_5.py and
drafts/claude-copies-4/build_claude_copies_act_4.py (neither is edited), changed in these places:

  * BASE is a clone of integrate with w2/W2-33 merged into it (a clean merge, measured). The copies are generated there:
    every role source by the clone's own ``gov.adapters.portability.compose(root, role)`` (the root ``.rulesync/`` with
    root = the clone; ``template/.rulesync/`` with root = the clone's ``template/``, which the check reads as an adopted
    project, its kernel at ``governance/kernel``), and ``.claude/agents/`` by the clone's rulesync 24.0.0 from the root
    ``.rulesync/`` (portability's own GENERATE form), never by hand;
  * the three new kernel roles (ticket-lead, qa-engineer, senior-engineer) have no rulesync source yet; compose() reads a
    source's front matter, so the builder first writes each new source's front matter (NEW_FRONT below: name, targets,
    description, claudecode.tools from the kernel role's Tools field, claudecode.skills from its Skills field), in both
    source trees, then composes its body like every other source. Those front matters are the one authored text here;
  * the operator's class rules (install class-rules.yaml, equal to the committed one) give template/.rulesync/** no
    row: it falls to the (O) "unknown" row (not an ACT's business; it was a ticket path in ACT-CLAUDE-COPIES-1 and -4,
    and W2-33 itself writes template/.rulesync/subagents/orchestrator.md). So the eight template sources are NOT in the
    bundle: they are written to PATCH (template-patch/: before/, after/, list.txt, the same apply.sh), the CTO's own
    commit in the hand merge after W2-33's merge commit and before this ACT; the ACT is the 18 files under .claude/agents
    and .rulesync/subagents (class (b));
  * the before-bytes are INTEGRATE's (plain integrate), required equal to BASE's (W2-33 touches none of the files), so
    ``apply.sh check`` reads the same on integrate and on integrate after W2-33's merge commit;
  * the manifest's checks are sha256 checks: check 1 the approved copies, check 2 the nine kernel role files and the
    template's orchestrator source they were composed from (so a kernel file that moves before the apply shows red);
  * the rehearsal runs the window (BASE without the ACT) and the landed tree (BASE with the ACT) through the same gated
    folders and compares their failures by test id; a failure on the landed tree must be in EXPECTED_AFTER (named, with
    its reason) to count as expected;
  * rehearsal.log carries no live head, pid, date, timing or count of the live tree.

    python3 build_v2.py <BASE clone> <INTEGRATE clone> <bundle dir> <scratch dir> <template patch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

BASE, INTEG, BUNDLE, SCRATCH, PATCH = (Path(a).resolve() for a in sys.argv[1:6])
ACT = sys.argv[6] if len(sys.argv) > 6 else "ACT-CLAUDE-COPIES-6"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: only to prove the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
W233 = "707d23b82932"
KERNEL_ROLES = "template/governance/kernel/roles"
TREES = (".rulesync", "template/.rulesync")
NEW_ROLES = ("qa-engineer", "senior-engineer", "ticket-lead")
TOOLS8 = '["Read", "Write", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch"]'
NEW_FRONT = {
    "qa-engineer": ("QA engineer role: checks a stream's finished tickets before they merge, as a fresh session; "
                    "writes only its findings report.", '["qa-review"]'),
    "senior-engineer": ("Senior Engineer role: runs one stream's tickets under the CTO, starts each ticket lead and "
                        "reads its return.", '["orchestration", "checkpoint", "retrieval"]'),
    "ticket-lead": ("Ticket lead role: runs one ticket's loop in its worktree and returns one summary; never merges "
                    "into integration.", '["orchestration", "checkpoint", "retrieval"]'),
}
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-153", "tests/unit/adapters", "tests/acceptance/W1-38", "tests/acceptance/W1-33",
         "tests/acceptance/W2-33", "tests/acceptance/W1-35", "tests/acceptance/W2-128"]  # one folder per pytest run
# Red on the landed tree for a reason outside this ACT (named in the package):
EXPECTED_AFTER = {
    "tests/acceptance/W1-33/test_w1_33_agent_definitions.py::test_there_is_one_definition_per_role_and_the_research_one":
        "the roster pinned at the five roles plus research (:86-90); the ACT adds the three new roles' agents, as "
        "CIT-P section 4 says; W2-33's run 4 revises the case",
    "tests/acceptance/W1-33/test_w1_33_kernel_role_files.py::test_the_research_role_file_is_unchanged":
        "pins research.md at W1-46's hash (:149-155); W2-33 changes research.md; the CTO's revision (DEC-1156 (7))",
}
APPLY_SH = r'''#!/bin/bash
# The copies ACT's apply.sh: reads its bundle from its own folder; check, apply, undo by list.txt, relative to the
# repository it is run in (its cwd). A failed step stops it with a non-zero exit (never a silent partial apply).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
while IFS='|' read -r root path before after; do
  [ -z "$root" ] && continue
  case "$root" in repo) f="$PWD/$path" ;; *) exit 9 ;; esac
  case "$step" in
    check)
      if [ -f "$f" ]; then h=$(sha256sum "$f" | cut -c1-64); else h=null; fi
      [ "$h" = "$before" ] || { echo "moved: $path" >&2; exit 3; } ;;
    apply)
      if [ "$after" = null ]; then rm -f "$f" || exit 4
      else mkdir -p "$(dirname "$f")" && rm -f "$f" && cat "$B/after/$root/$path" > "$f" || { echo "failed: $path" >&2; exit 4; }; fi ;;
    undo)
      if [ "$before" = null ]; then rm -f "$f" || exit 4
      else mkdir -p "$(dirname "$f")" && rm -f "$f" && cat "$B/before/$root/$path" > "$f" || { echo "failed: $path" >&2; exit 4; }; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
exit 0
'''


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
say(f"{ACT} rehearsal; base: integrate with w2/W2-33 {W233} merged; rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")
assert run(["git", "merge-base", "--is-ancestor", W233, "HEAD"], gen)[0] == 0, "BASE does not contain w2/W2-33"


def portability(tree, rulesync=True):
    env = dict(os.environ, PYTHONPATH=str(gen / "src"), RULESYNC_BIN=RULESYNC if rulesync else "/nonexistent/rulesync")
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


code, found = portability(gen)
say(f"portability on the base (W2-33 merged, no copies): exit {code}; {len(found)} findings: {tally(found)}")
assert all("/subagents/" in f.get("file", "") or f["code"] == "GENERATED_DIFFERS" for f in found), found


def compose(root, role):
    probe = ("import sys, json; sys.path.insert(0, sys.argv[1] + '/src'); from gov.adapters import portability as p; "
             "from pathlib import Path; print(json.dumps(p.compose(Path(sys.argv[2]), sys.argv[3])))")
    code, out = run([sys.executable, "-I", "-c", probe, str(gen), str(root), role], gen)
    if code != 0:
        raise SystemExit(f"compose() failed for {root} {role}: {out[-300:]}")
    return json.loads(out)


roles = sorted(p.stem for p in (gen / KERNEL_ROLES).glob("*.md"))
assert len(roles) == 9 and set(NEW_ROLES) <= set(roles), roles
for tree, root in ((".rulesync", gen), ("template/.rulesync", gen / "template")):
    for role in roles:
        src = gen / tree / "subagents" / f"{role}.md"
        if role in NEW_ROLES:
            assert not src.exists(), src
            desc, skills = NEW_FRONT[role]
            src.write_text(f'---\nname: {role}\ntargets: ["claudecode"]\ndescription: "{desc}"\nclaudecode:\n'
                           f"  tools: {TOOLS8}\n  skills: {skills}\n---\n", encoding="utf-8")
        src.write_text(compose(root, role), encoding="utf-8")
# the two trees' sources are the same bytes (the front matters were equal on integrate; the kernel is one)
for role in roles:
    assert (gen / ".rulesync/subagents" / f"{role}.md").read_bytes() == \
        (gen / "template/.rulesync/subagents" / f"{role}.md").read_bytes(), role
say(f"the {len(roles)} role sources composed by compose(), in both trees; the two trees' sources byte-equal")

others = []
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
            others.append(rel)
say(f"rulesync's other output that differs from the tree (not written; as in ACT-CLAUDE-COPIES-5): {others}")
code, after = portability(gen)
say(f"portability in the generation clone after the copies: exit {code}; findings {after}")
assert code == 0, after
tcode, tfound = portability(gen / "template", rulesync=False)
tsub = [f for f in tfound if "/subagents/" in str(f.get("file", ""))]
say(f"portability on template/ (as an adopted project, no rulesync): {len(tsub)} subagents findings; "
    f"others: {tally([f for f in tfound if f not in tsub])}")
assert not tsub, tsub
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert all(r.startswith((".claude/agents/", ".rulesync/subagents/", "template/.rulesync/subagents/")) for r in TOUCHED), TOUCHED
assert "template/.rulesync/subagents/orchestrator.md" not in TOUCHED  # W2-33's own
say(f"generation clone: {len(TOUCHED)} files changed or new: " + ", ".join(TOUCHED))
ALL = TOUCHED
PATCHED = [r for r in ALL if r.startswith("template/")]
TOUCHED = [r for r in ALL if not r.startswith("template/")]
say(f"the ACT: {len(TOUCHED)} files (.claude/agents, .rulesync/subagents); the CTO's template commit: {len(PATCHED)} files "
    "(template/.rulesync/subagents, which the class rules give no ACT row)")

# the CTO's template commit: the same form as the bundle, outside it
if PATCH.exists():
    shutil.rmtree(PATCH)
plines = []
for rel in PATCHED:
    cur = (INTEG / rel).read_bytes() if (INTEG / rel).is_file() else None
    assert cur == ((BASE / rel).read_bytes() if (BASE / rel).is_file() else None), f"{rel}: W2-33 changes it"
    new = (gen / rel).read_bytes()
    for side, data in (("before", cur), ("after", new)):
        if data is not None:
            (PATCH / side / "repo" / rel).parent.mkdir(parents=True, exist_ok=True)
            (PATCH / side / "repo" / rel).write_bytes(data)
    plines.append(f"repo|{rel}|{sha(cur) if cur is not None else 'null'}|{sha(new)}")
(PATCH / "list.txt").write_text("\n".join(plines) + "\n")
(PATCH / "apply.sh").write_text(APPLY_SH)
os.chmod(PATCH / "apply.sh", 0o755)
say(f"the template commit's folder written: {len(plines)} files, its list.txt sha256 {sha((PATCH / 'list.txt').read_bytes())}")

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
    assert cur == ((BASE / rel).read_bytes() if (BASE / rel).is_file() else None), f"{rel}: W2-33 changes it"
    new = (gen / rel).read_bytes()
    before, after_h = (sha(cur) if cur is not None else None), sha(new)
    assert before != after_h, rel
    if cur is not None:
        put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after_h})
    lines.append(f"repo|{rel}|{before or 'null'}|{after_h}")
say(f"the before-bytes are integrate's and equal on integrate with W2-33 merged ({sum(1 for t in touched if t['before'])} "
    f"changed, {sum(1 for t in touched if not t['before'])} new)")
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
copies = [(t["path"], t["after"]) for t in touched]
sources = [(f"{KERNEL_ROLES}/{r}.md", sha((gen / KERNEL_ROLES / f"{r}.md").read_bytes())) for r in roles]
sources += [(f"template/.rulesync/subagents/{r}.md", sha((gen / "template/.rulesync/subagents" / f"{r}.md").read_bytes()))
            for r in roles]
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(sources)), "exit": 0, "count": None}]

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
say("--- rehearsal on integrate with W2-33 merged (the tree after the hand merge's merge commit); HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
for tree in (reh,):
    step(tree, f"the CTO's template commit ({tree.name}): apply.sh check, apply, commit",
         f"bash {PATCH}/apply.sh check && bash {PATCH}/apply.sh apply && git add {' '.join(PATCHED)} && "
         f"{GIT} commit -q -m 'template sources' --trailer 'Task: DAEO-lrre' --trailer 'Role: orchestrator'")
before_state = tree_state(reh)
step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copies are the stale ones)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: W2-33's kernel role files and the template sources after the CTO's commit)",
     checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "every target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the apply: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
mark(tree_state(reh) == before_state and changed_set(reh) == [], "undo: every file byte for byte back, the tree clean")
pcode, pfound = portability(reh)
mark(pcode == 1 and all("/subagents/" in f.get("file", "") or f["code"] == "GENERATED_DIFFERS" for f in pfound),
     f"portability after the undo: exit {pcode}; {len(pfound)} findings: {tally(pfound)} (the window's own reading)")
step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
     "the re-apply gives the same bytes and the same changed set as the first apply")

# 2. plain integrate: the check passes too (the before-bytes are integrate's); the package orders the apply after
# the merge commit, never before
say("--- plain integrate (W2-33 not merged): apply.sh check")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (W2-33 changes none of the files)", f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (the kernel role files are not W2-33's yet)", checks[1]["cmd"], expect=1)
rm = SCRATCH / "rehearsal-merge-only"
clone(BASE, rm)
step(rm, "check 2 is red after the merge commit without the CTO's template commit (the order is held)", checks[1]["cmd"],
     expect=1)
mark(changed_set(ri) == [], "check changed nothing")

# 3. the gated runs: the window (no ACT) and the landed tree (the ACT applied)
say("--- the gated runs, one folder per run through the heavy-job gate: the window (W2-33's merge commit alone: the "
    "state CIT-P section 4 counts), then the landed tree (the merge, the CTO's template commit and the ACT)")
res_win = {r[0]: r for r in gated_all(win, "window")}
res_act = {r[0]: r for r in gated_all(reh, "landed")}
red_win, red_act = set(), set()
for folder in GATED:
    _, code, m, ok, failed = res_win[folder]
    red_win |= set(failed)
    say(f"window {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
        + (f", {m['skipped']} skipped" if m.get("skipped") else ""))
for folder in GATED:
    _, code, m, ok, failed = res_act[folder]
    red_act |= set(failed)
    unexpected = [t for t in failed if t not in EXPECTED_AFTER]
    mark(ok and m.get("passed", 0) > 0 and not unexpected,
         f"landed {folder}: exit {code}; {m.get('passed', 0)} passed, {m.get('failed', 0) + m.get('error', 0)} failed"
         + (f", {m['skipped']} skipped" if m.get("skipped") else "")
         + (f"; unexpected: {unexpected}" if unexpected else ""))
for t in sorted(red_act):
    say(f"     red on the landed tree: {t}" + (f" (expected: {EXPECTED_AFTER[t]})" if t in EXPECTED_AFTER else ""))
say(f"red in the window: {len(red_win)}; made green by the ACT: {len(red_win - red_act)}; red after: {len(red_act)}; "
    f"new red brought by the ACT: {sorted(red_act - red_win)}")
(SCRATCH / "red-window.txt").write_text("\n".join(sorted(red_win)) + "\n")
(SCRATCH / "red-landed.txt").write_text("\n".join(sorted(red_act)) + "\n")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"python3 -m gov.adapters.portability on the landed tree: exit {pcode}; findings {pfound}")

# 4. the by-hand steps literally: stage, commit, undo, commit
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
mf = {"act": ACT, "dec": "DEC-1156 (3), DEC-1109 (2), DEC-1112 (3), CAP-33", "author": "cto", "claimed_class": "b",
      "touched": touched, "files": files, "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
      "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
