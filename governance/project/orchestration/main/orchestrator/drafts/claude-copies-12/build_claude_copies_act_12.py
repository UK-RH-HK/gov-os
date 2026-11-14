"""Builds and rehearses ACT-CLAUDE-COPIES-12: the generated `.claude/skills/adopt/SKILL.md` from W2-188's adopt-skill bytes.
W2-188's kernel copy, root `.rulesync` copy and `template/.rulesync` copy are all at sha256 6a884cf1..., and the CIT-P
approval of W2-188 is pending. Governed by DEC-315, DEC-1112 (3), DEC-1166 (4), DEC-1179 and CAP-33. Adapted from
drafts/claude-copies-9/build_claude_copies_act_9.py, which also re-rendered the adopt copy; COPIES-9's builder is not
edited. Changes from it:

  * one target only, `.claude/skills/adopt/SKILL.md`. W2-188 itself carries all three adopt sources (the kernel, the root
    `.rulesync` and `template/.rulesync`), so the ACT carries only the `.claude` rendering, as in COPIES-7, -10 and -11.
    The file exists already, so `before/` is written and undo restores it. Its before-bytes are integrate's (77faaa13,
    COPIES-9's rendering of 16fd341f), and W2-188 does not touch the file;
  * order 1 (BASE): a clone of integrate with refs/heads/w2/W2-188 merged by one --no-ff commit (the CTO's hand merge,
    Task: DAEO-zlog). W2-188's head is not pinned: the ticket moves for tests and CIT-P only. Pinned instead: its three
    adopt sources at 6a884cf1 in the branch's objects and on the merged tree (check 2). On BASE: generation, bundle,
    apply/undo/re-apply, plain integrate, a moved target, the gated runs (window and landed), the named cases and the
    by-hand steps;
  * order 2: the copies first, then the merge. On a clone of plain integrate, apply.sh check passes, check 2 is red (so
    the operator's G8 refuses this order: the order is held), and apply.sh apply is run anyway. The result is committed,
    then w2/W2-188 is merged --no-ff. Asserted: the merge is clean; the touched file then equals order 1's after bytes;
    checks 1 and 2 are green; portability exits 0 with no finding; the named cases match order 1's landed status;
  * no expected file from the lead: rulesync's rendering is accepted when its body after the front matter equals the
    kernel's body (version 1.1.0) and its front matter keys are the tracked copy's (`name`, `description`), with no
    version: the adopt `.claude` copy carries none, as COPIES-9's did (W2-11's version case leaves adopt out);
  * evidence goes to drafts/claude-copies-12/evidence/; pytest's TMPDIR is <scratch>/tmp; rehearsal commits carry
    Task: DAEO-zlog.

    python3 -I build_claude_copies_act_12.py <INTEGRATE clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

INTEG, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-12"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: the branch to merge, and proof the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
EVID = ORCH / "drafts/claude-copies-12/evidence"
C9 = ORCH / "acts/ACT-CLAUDE-COPIES-9"
C11 = ORCH / "acts/ACT-CLAUDE-COPIES-11"
BRANCH = "refs/heads/w2/W2-188"
TICKET = "DAEO-zlog"
ADOPT_SHA = "6a884cf1639f2e803400205ace80aeabe23badbd59be8df92c06e24cf9a29489"   # W2-188's CIT-P, the bytes for approval
ADOPT_SOURCES = ("template/governance/kernel/skills/adopt/SKILL.md", ".rulesync/skills/adopt/SKILL.md",
                 "template/.rulesync/skills/adopt/SKILL.md")
ADOPT_COPY = ".claude/skills/adopt/SKILL.md"
EXPECTED_TOUCHED = [ADOPT_COPY]
PINS = {a: ADOPT_SHA for a in ADOPT_SOURCES}
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-188", "tests/acceptance/W2-88a", "tests/acceptance/W2-11", "tests/unit/adapters",
         "tests/unit/impact", "tests/acceptance/W1-33", "tests/acceptance/W1-38", "tests/acceptance/W2-153",
         "tests/acceptance/W2-98", "tests/acceptance/W2-52"]
TARGETED = [("tests/acceptance/W2-188", ["tests/acceptance/W2-188/test_w2_188_copies.py"])]
TMP = SCRATCH / "tmp"
HOME_RX = re.compile(r"/home/[A-Za-z0-9_.-]+/")
APPLY_SH = (C11 / "apply.sh").read_text()   # the same apply.sh as ACT-CLAUDE-COPIES-1 to -11
assert APPLY_SH == (C9 / "apply.sh").read_text()


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


GITC = ["git", "-c", "user.name=rehearsal", "-c", "user.email=rehearsal@example.invalid"]
GIT = " ".join(GITC)
SCRATCH.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)
EVID.mkdir(parents=True, exist_ok=True)
INTEG_HEAD = run(["git", "rev-parse", "HEAD"], INTEG)[1]
assert run(["git", "status", "--porcelain", "--untracked-files=all"], INTEG)[1] == ""


def merge_branch(tree, msg):
    assert run(["git", "fetch", "-q", str(LIVE_TREE), f"{BRANCH}:{BRANCH}"], tree)[0] == 0
    code, out = run([*GITC, "merge", "--no-ff", "-q", "-m", msg, BRANCH], tree)
    return code, out


# BASE: integrate with w2/W2-188 merged by one commit, as after the CTO's hand merge
BASE = SCRATCH / "base-merged"
clone(INTEG, BASE)
code, out = merge_branch(BASE, "Merge w2/W2-188 (rehearsal of the CTO's hand merge)")
assert code == 0, out
assert run(["git", "status", "--porcelain", "--untracked-files=all"], BASE)[1] == ""
BR_HEAD = run(["git", "rev-parse", "--short=12", BRANCH], BASE)[1]
mbase = run(["git", "merge-base", "HEAD~1", BRANCH], BASE)[1][:12]
brought = run(["git", "diff", "--name-only", "HEAD~1", "HEAD"], BASE)[1].splitlines()
assert not [p for p in brought if p.startswith(".claude/")], brought
gen = SCRATCH / "gen-clone"
clone(BASE, gen)
say(f"{ACT} rehearsal; base: integrate {INTEG_HEAD[:12]} with w2/W2-188 {BR_HEAD} merged (one --no-ff commit, clean; "
    f"merge base {mbase}; {len(brought)} files brought, none under .claude/); rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")

for src in ADOPT_SOURCES:
    assert sha((gen / src).read_bytes()) == ADOPT_SHA, f"{src} is not at {ADOPT_SHA}"
    shown = subprocess.run(["git", "show", f"{BRANCH}:{src}"], cwd=BASE, capture_output=True).stdout
    assert sha(shown) == ADOPT_SHA, f"the branch's {src} is not the approved bytes"
say(f"the three adopt sources {list(ADOPT_SOURCES)} are at {ADOPT_SHA[:8]}, on the merged tree and in w2/W2-188's objects")


def portability(tree, rulesync=True):
    env = dict(os.environ, PYTHONPATH=str(gen / "src"), RULESYNC_BIN=RULESYNC if rulesync else "/nonexistent/rulesync")
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


def pairs(found):
    return sorted((f["code"], f.get("file", "")) for f in found)


code, int_found = portability(INTEG)
say(f"portability on plain integrate: exit {code}; {len(int_found)} findings: {tally(int_found)}")
assert int_found == [], int_found
code, base_found = portability(gen)
say(f"portability on the merged tree (no copy): exit {code}; findings {pairs(base_found)}")
assert pairs(base_found) == [("GENERATED_DIFFERS", ADOPT_COPY)], base_found


def differing(root, fresh):
    return sorted(str(p.relative_to(fresh)) for p in Path(fresh).rglob("*")
                  if p.is_file() and not ((root / p.relative_to(fresh)).is_file()
                                           and (root / p.relative_to(fresh)).read_bytes() == p.read_bytes()))


before_bytes = {ADOPT_COPY: (gen / ADOPT_COPY).read_bytes()}
with tempfile.TemporaryDirectory() as fresh:
    code, out = run([RULESYNC, *GENERATE, str((gen / ".rulesync").resolve())], fresh)
    assert code == 0, out
    differ1 = differing(gen, fresh)
    rendered = (Path(fresh) / ADOPT_COPY).read_bytes()
say(f"rulesync from the merged tree's root .rulesync: differs from the tree in {differ1}")
assert ADOPT_COPY in differ1
not_written = [r for r in differ1 if r != ADOPT_COPY]
assert not [r for r in not_written if r.startswith(GENERATED_FOLDERS)], not_written
assert not any(r.startswith(("template/", ".rulesync/")) for r in differ1)
say(f"rulesync's other output that differs from the tree (not written, not this ACT's): {not_written}")


def split(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else (None, text)


kfront, kbody = split((gen / ADOPT_SOURCES[0]).read_text())
rfront, rbody = split(rendered.decode())
import yaml  # noqa: E402
kv, rmeta = yaml.safe_load(kfront).get("version"), (yaml.safe_load(rfront).get("metadata") or {})
say(f"rulesync's {ADOPT_COPY}: {sha(rendered)} ({len(rendered)} bytes); body after the front matter equal to the kernel's: "
    f"{rbody.strip() == kbody.strip()}; metadata.version {rmeta.get('version')!r} (kernel {kv!r}); front matter keys "
    f"{sorted(yaml.safe_load(rfront))}; the tracked copy was {sha(before_bytes[ADOPT_COPY])}")
tfront, _ = split(before_bytes[ADOPT_COPY].decode())
assert rbody.strip() == kbody.strip() and str(kv) == "1.1.0", "the rendering's body is not the kernel's"
assert sorted(yaml.safe_load(rfront)) == sorted(yaml.safe_load(tfront)) == ["description", "name"], "front matter keys moved"
assert rmeta.get("version") is None, "the adopt .claude copy carries no version (as the tracked copy; W2-11 leaves adopt out)"
(gen / ADOPT_COPY).write_bytes(rendered)
code, after = portability(gen)
assert code == 0 and not after, (code, after)
say("portability in the generation clone after the copy: exit 0, no finding")
tcode, tfound = portability(gen / "template", rulesync=False)
say(f"portability on template/ (as an adopted project, no rulesync): adopt findings "
    f"{[f for f in tfound if '/adopt/' in str(f.get('file', ''))]}; others: {tally([f for f in tfound if '/adopt/' not in str(f.get('file', ''))])}")
assert not [f for f in tfound if "/adopt/" in str(f.get("file", ""))]
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert TOUCHED == EXPECTED_TOUCHED, TOUCHED
say(f"generation clone: {len(TOUCHED)} file changed: {TOUCHED[0]}")

# the bundle
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
    assert cur == (BASE / rel).read_bytes() == before_bytes[rel], f"{rel}: W2-188 changes it"
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


def sha_check(prs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in prs) + "\nEOF"
copies = [(t["path"], t["after"]) for t in touched]
sources = sorted(PINS.items())
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sources), "exit": 0, "count": None}]
assert not HOME_RX.search(json.dumps(checks)) and "~" not in json.dumps(checks) and "HOME" not in json.dumps(checks)
say(f"check 1: the {len(copies)} copy; check 2: the {len(sources)} adopt sources at {ADOPT_SHA[:8]}; no live HOME path in either")

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
STATUS_LINE = re.compile(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (\S+)")


def pytest_cmd(tree, args):
    return ["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={tree / 'src'}", "PYTHONUSERBASE=/home/usain/.local",
            "python3", "-m", "pytest", *args, "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"]


def pytest_env(tree):
    return dict(os.environ, PYTHONPATH=str(tree / "src"), TMPDIR=str(TMP), PYTHONUSERBASE="/home/usain/.local")


def gated(tree, folder, label):
    code, out = run(pytest_cmd(tree, [folder, "-q", "-rfE"]), tree, pytest_env(tree))
    summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
    m = {k.rstrip("s") if k.startswith("error") else k: int(v)
         for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
    failed = sorted({mm.group(1) for ln in out.splitlines() if (mm := FAILED_LINE.match(ln.strip()))})
    (EVID / f"{label}-{folder.replace('/', '_')}.txt").write_text(out + "\n")
    return folder, code, m, bool(summary), failed


def gated_all(tree, label):
    with ThreadPoolExecutor(max_workers=3) as pool:
        return list(pool.map(lambda f: gated(tree, f, label), GATED))


def targeted(tree, label):
    status = {}
    for folder, ids in TARGETED:
        code, out = run(pytest_cmd(tree, [*ids, "-q", "-rA"]), tree, pytest_env(tree))
        (EVID / f"{label}-targeted-{folder.replace('/', '_')}.txt").write_text(out + "\n")
        for ln in out.splitlines():
            mm = STATUS_LINE.match(ln.strip())
            if mm:
                status[mm.group(2)] = mm.group(1)
    return status


# 1. order 1: apply, verify, undo, re-apply on the merged tree
say("--- order 1 (merge first, then the copy): rehearsal on integrate with W2-188 merged; HOME planted")
reh = SCRATCH / "rehearsal-merged"
clone(BASE, reh)
win = SCRATCH / "window-merged"
clone(BASE, win)
before_state = tree_state(reh)
step(reh, "apply.sh check (the target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
step(reh, "check 1 before the apply (red, as intended: the copy is at the old bytes)", checks[0]["cmd"], expect=1)
step(reh, "check 2 before the apply (green: the three adopt sources at the approved bytes)", checks[1]["cmd"])
step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} file)")
after_state = tree_state(reh)
mark(all(sha(after_state[t["path"]]) == t["after"] for t in touched), "the target is at its stated after sha256")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the apply: exit {pcode}; findings {pfound} (GENERATED_DIFFERS on adopt cleared)")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
mark(tree_state(reh) == before_state and changed_set(reh) == [], "undo: the file byte for byte back, the tree clean")
pcode, pfound = portability(reh)
mark(pairs(pfound) == pairs(base_found), f"portability after the undo: exit {pcode}; {pairs(pfound)} (the merged tree's own reading)")
step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
     "the re-apply gives the same bytes and the same changed set as the first apply")

say("--- plain integrate (W2-188 not merged)")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
step(ri, "apply.sh check passes on plain integrate (the target is at the same before bytes there)", f"bash {BUNDLE}/apply.sh check")
step(ri, "check 2 is red on plain integrate (the adopt sources are the old bytes there: G8 refuses, the order is held)",
     checks[1]["cmd"], expect=1)
mark(changed_set(ri) == [], "check changed nothing")
mv = SCRATCH / "rehearsal-moved"
clone(BASE, mv)
(mv / ADOPT_COPY).write_bytes((mv / ADOPT_COPY).read_bytes() + b"x")
step(mv, "apply.sh check refuses a moved target (exit 3)", f"bash {BUNDLE}/apply.sh check", expect=3)

say("--- order 1, the gated runs, one folder per run through the heavy-job gate: on the merged tree (W2-188's merge alone, "
    "then with this ACT)")
rw = {r[0]: r for r in gated_all(win, "merged-window")}
ra = {r[0]: r for r in gated_all(reh, "merged-landed")}
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

say("--- order 1, the named cases (W2-188's copy cases, -rA)")
tw, ta = targeted(win, "merged-window"), targeted(reh, "merged-landed")
for case in sorted(set(tw) | set(ta)):
    say(f"     {case}: window {tw.get(case, '-')}, landed {ta.get(case, '-')}")

say("--- order 1, the by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
step(reh, "git add the touched path", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: {TICKET}' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched path (undo)", f"git add -A {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: {TICKET}' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched path)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

# 2. order 2: the copy first on plain integrate (check 2 red: G8 would refuse), committed, then w2/W2-188 merged
say("--- order 2 (the copy first, then the merge): plain integrate, apply.sh apply despite check 2's red, commit, then "
    "w2/W2-188 merged --no-ff")
o2 = SCRATCH / "rehearsal-order2"
clone(INTEG, o2)
step(o2, "apply.sh check on plain integrate", f"bash {BUNDLE}/apply.sh check")
step(o2, "check 2 red before the merge (the operator's G8 refuses this order)", checks[1]["cmd"], expect=1)
step(o2, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
step(o2, "check 1 green after the apply", checks[0]["cmd"])
pcode, pfound = portability(o2)
say(f"portability on integrate with the copy but without W2-188: exit {pcode}; findings {pairs(pfound)} (the copy ahead of its sources)")
step(o2, "commit the copy", f"{GIT} add {paths} && {GIT} commit -q -m '{ACT}: order 2 rehearsal' --trailer 'Task: {TICKET}' --trailer 'Role: owner'")
code, out = merge_branch(o2, "Merge w2/W2-188 (order 2 rehearsal)")
mark(code == 0 and changed_set(o2) == [], f"w2/W2-188 merges clean after the copy: exit {code}{(' ' + out[-300:]) if code else ''}")
mark(tree_state(o2) == after_state, "the touched file equals order 1's after bytes")
for i, c in enumerate(checks, 1):
    step(o2, f"order 2 check {i}", c["cmd"])
pcode, pfound = portability(o2)
mark(pcode == 0 and not pfound, f"order 2 portability after the merge: exit {pcode}; findings {pfound}")
t2 = targeted(o2, "order2-landed")
mark(t2 == ta, f"order 2 named cases equal order 1's landed status ({sum(1 for v in t2.values() if v == 'PASSED')} passed, "
     f"{sum(1 for v in t2.values() if v != 'PASSED')} not)")
g2 = gated(o2, "tests/acceptance/W2-188", "order2-landed")
new2 = [t for t in g2[4] if t not in red_a]
mark(g2[3] and not new2, f"order 2 tests/acceptance/W2-188: exit {g2[1]}; {g2[2].get('passed', 0)} passed, "
     f"{g2[2].get('failed', 0)} failed; red beyond order 1's landed: {new2}")

untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live file unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-315, DEC-1112 (3), DEC-1166 (4), DEC-1179, CAP-33", "author": "cto", "claimed_class": "b",
      "touched": touched, "files": files, "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]},
      "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails, "branch_head": BR_HEAD}))
