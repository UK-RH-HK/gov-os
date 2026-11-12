"""Builds and rehearses ACT-CLAUDE-COPIES-5 (the six generated .claude/skills copies that W2-11's round 2 left stale;
DEC-315, DEC-1112 (3)). Adapted from build_claude_copies_act_4.py (the original is not edited), changed in these places:

  * BASE is a clone of integrate with w2/W2-11 (58ac442d6820) merged into it (a clean merge, measured); the six copies
    are generated there by the clone's own rulesync 24.0.0 from the root .rulesync/ sources, never by hand. The
    before-bytes are BASE's, required equal to the blobs at w2/W2-11 58ac442d6820 (the ACT is applied after W2-11 lands:
    applied before, merging integrate into w2/W2-11 conflicts in four of the six files, measured);
  * the touched set is exactly the files under .claude/skills that the portability check reports as GENERATED_DIFFERS
    and that rulesync's output differs on; it is required disjoint from ACT-CLAUDE-COPIES-4's list;
  * the manifest's two checks are sha256 checks (the six approved copies, and the six root sources they were generated
    from, so a source that moves before the apply shows red);
  * apply.sh stops on a failed step (ACT-4's F2) and leaves no rmdir (F3);
  * a gated test run is read from pytest's own summary line, anchored at the line's start, and must show passed > 0 and
    exit 0 (ACT-4's F5);
  * rehearsal.log carries no live head, pid, date, timing or count of the live tree, so a re-run is byte-equal.

    python3 build_claude_copies_act_5.py <BASE clone> <INTEGRATE clone> <INTEGRATE+ACT-4+W2-11 clone> <bundle dir> <scratch dir> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE, INTEG, X4, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:6])
ACT = sys.argv[6] if len(sys.argv) > 6 else "ACT-CLAUDE-COPIES-5"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: only to prove the rehearsal left it alone
ORCH = LIVE_TREE / ".gov-runtime/scratch/orchestrator"
HEAVY = str(ORCH / "tools/heavy_slot.sh")
ACT4_LIST = ORCH / "acts/ACT-CLAUDE-COPIES-4/list.txt"
W211 = "58ac442d6820"
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
GATED = ["tests/acceptance/W2-11", "tests/acceptance/W2-128", "tests/acceptance/W2-142", "tests/acceptance/W1-35",
         "tests/acceptance/W2-153", "tests/unit/adapters"]          # one folder per pytest run (their conftests clash)
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
say(f"{ACT} rehearsal; base: integrate with w2/W2-11 {W211} merged; rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")
assert run(["git", "merge-base", "--is-ancestor", W211, "HEAD"], gen)[0] == 0, "BASE does not contain w2/W2-11"


def portability(tree):
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), RULESYNC_BIN=RULESYNC)
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


def tally(found):
    n = {}
    for f in found:
        n[f["code"]] = n.get(f["code"], 0) + 1
    return ", ".join(f"{k} {v}" for k, v in sorted(n.items())) or "none"


code, found = portability(gen)
say(f"portability on the base (W2-11 merged, no copies): exit {code}; {len(found)} findings: {tally(found)}")
FINDING_FILES = sorted(f["file"] for f in found)
assert all(f["code"] == "GENERATED_DIFFERS" and f["file"].startswith(".claude/skills/") for f in found), found

# the root sources and the kernel are byte-equal where W2-11 says they are (its CIT-P section 4: cmp, 2 copies)
SKILLS = sorted({Path(p).relative_to(".claude/skills") for p in FINDING_FILES})
for rel in SKILLS:
    root = (gen / ".rulesync/skills" / rel).read_bytes()
    assert root == (gen / "template/.rulesync/skills" / rel).read_bytes() == \
        (gen / "template/governance/kernel/skills" / rel).read_bytes(), f"{rel}: the three source copies differ"
say(f"the {len(SKILLS)} skill files: the root .rulesync/skills source, template/.rulesync/skills and the kernel skill are byte-equal")

with tempfile.TemporaryDirectory() as fresh:
    code, out = run([RULESYNC, *GENERATE, str((gen / ".rulesync").resolve())], fresh)
    assert code == 0, out
    differing = []
    for path in sorted(Path(fresh).rglob("*")):
        rel = str(path.relative_to(fresh))
        if path.is_file() and rel.startswith(GENERATED_FOLDERS) and (
                not (gen / rel).is_file() or (gen / rel).read_bytes() != path.read_bytes()):
            differing.append(rel)
            (gen / rel).parent.mkdir(parents=True, exist_ok=True)
            (gen / rel).write_bytes(path.read_bytes())
assert differing == FINDING_FILES or sorted(differing) == FINDING_FILES, (differing, FINDING_FILES)
code, after = portability(gen)
say(f"portability in the generation clone after the copies: exit {code}; findings {after}")
assert code == 0, after
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert TOUCHED == FINDING_FILES, TOUCHED
say(f"generation clone: {len(TOUCHED)} files changed: " + ", ".join(TOUCHED))

# disjoint from ACT-CLAUDE-COPIES-4
act4 = {l.split("|")[1] for l in ACT4_LIST.read_text().splitlines() if l}
assert not (act4 & set(TOUCHED)), act4 & set(TOUCHED)
say(f"the touched set shares no file with ACT-CLAUDE-COPIES-4 ({len(act4)} files: .claude/templates, .rulesync/subagents, .claude/agents)")

# before-bytes: BASE's, required equal to the blobs at w2/W2-11 (and noted where integrate differs)
def blob(tree, rev, rel):
    r = subprocess.run(["git", "show", f"{rev}:{rel}"], cwd=tree, capture_output=True)
    return r.stdout if r.returncode == 0 else None


if BUNDLE.exists():
    shutil.rmtree(BUNDLE)
BUNDLE.mkdir(parents=True)
files, touched, lines = {}, [], []
def put(rel, data):
    p = BUNDLE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    files[rel] = sha(data)


onint = []
for rel in TOUCHED:
    cur = (BASE / rel).read_bytes() if (BASE / rel).is_file() else None
    assert cur == blob(BASE, W211, rel), f"{rel} is not the blob at w2/W2-11 {W211}"
    ci = (INTEG / rel).read_bytes() if (INTEG / rel).is_file() else None
    onint.append(f"{rel}: {'same as integrate' if ci == cur else ('absent on integrate' if ci is None else 'differs from integrate')}")
    new = (gen / rel).read_bytes()
    before, after_h = (sha(cur) if cur is not None else None), sha(new)
    assert before != after_h, rel
    if cur is not None:
        put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after_h})
    lines.append(f"repo|{rel}|{before or 'null'}|{after_h}")
say("the before-bytes are the blobs at w2/W2-11 " + W211 + " (the tree after W2-11 lands): " + "; ".join(onint))
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
sources = [(".rulesync/skills/" + str(Path(t["path"]).relative_to(".claude/skills")),
            sha((gen / ".rulesync/skills" / Path(t["path"]).relative_to(".claude/skills")).read_bytes())) for t in touched]
copies = [(t["path"], t["after"]) for t in touched]
checks = [{"cmd": sha_check(sorted(copies)), "exit": 0, "count": None},
          {"cmd": sha_check(sorted(sources)), "exit": 0, "count": None}]

# the rehearsal, as the operator runs it
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


def gated(tree, folder):
    """One folder, one pytest run, through the heavy-job gate. The result is read from pytest's own summary line (anchored
    at the line's start; the gate's lines before or after it never count) and must show passed > 0."""
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), TMPDIR=str(TMP))
    code, out = run(["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={tree / 'src'}", "python3", "-m", "pytest", folder,
                     "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"], tree, env)
    summary = [ln.strip() for ln in out.splitlines() if SUMMARY.match(ln.strip())]
    m = {k.rstrip("s") if k.startswith("error") else k: int(v)
         for v, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", summary[-1] if summary else "")}
    (SCRATCH / f"tail-{folder.replace('/', '_')}.txt").write_text("\n".join(out.splitlines()[-40:]) + "\n")
    return code, m, bool(summary)


def rehearse(label, src):
    say(f"--- rehearsal on {label}; HOME planted at a fresh empty folder")
    reh = SCRATCH / "rehearsal-merged"
    clone(src, reh)
    before_state = tree_state(reh)
    step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
    for i, c in enumerate(checks, 1):
        step(reh, f"check {i} before the apply ({'red, as intended: the six copies are the stale ones' if i == 1 else 'green: the six root sources are the approved ones'})",
             c["cmd"], expect=1 if i == 1 else 0)
    step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
    for i, c in enumerate(checks, 1):
        step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
    mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
    after_state = tree_state(reh)
    mark(all(sha(after_state[r]) == next(t["after"] for t in touched if t["path"] == r) for r in TOUCHED),
         "every target is at its stated after sha256")
    pcode, pfound = portability(reh)
    mark(pcode == 0 and not pfound, f"portability after the apply (W2-11 merged): exit {pcode}; findings {pfound}")
    step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
    back = tree_state(reh) == before_state
    clean = run(["git", "status", "--porcelain", "--untracked-files=all"], reh)[1] == ""
    mark(back and clean, "undo: every file byte for byte back, the tree clean")
    pcode, pfound = portability(reh)
    mark(pcode == 1 and sorted(f["file"] for f in pfound) == TOUCHED,
         f"portability after the undo: exit {pcode}; {len(pfound)} findings: {tally(pfound)} (the window's own reading)")
    step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
    step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
    for i, c in enumerate(checks, 1):
        step(reh, f"check {i} after the re-apply", c["cmd"])
    mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
         "the re-apply gives the same bytes and the same changed set as the first apply")
    return reh


# the negative control: on plain integrate (W2-11 not merged) the check refuses, as the operator's G7 would
say("--- plain integrate (W2-11 not merged): the bundle must refuse, as G7 would")
ri = SCRATCH / "rehearsal-integrate"
clone(INTEG, ri)
code, out = step(ri, "apply.sh check refuses (moved)", f"bash {BUNDLE}/apply.sh check", expect=3)
mark(out.startswith("moved: .claude/skills/"), f"the refusal names the first moved file: {out.splitlines()[0] if out else out}")
mark(changed_set(ri) == [], "check changed nothing")

reh = rehearse("integrate with W2-11 merged (the tree the operator's dry run sees when the ACT is queued after W2-11 lands)", BASE)

# the gated runs on the merged clone with the ACT applied: one folder per run
say("--- the gated test runs on the merged tree with the ACT applied (one folder per run, through the heavy-job gate)")
for folder in GATED:
    code, m, found_summary = gated(reh, folder)
    passed, failed = m.get("passed", 0), m.get("failed", 0) + m.get("error", 0)
    mark(code == 0 and found_summary and failed == 0 and passed > 0,
         f"{folder}: exit {code}; {passed} passed, {failed} failed" + (f", {m['skipped']} skipped" if m.get("skipped") else ""))
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"python3 -m gov.adapters.portability on the merged tree with the ACT applied: exit {pcode}; "
     f"findings {pfound}")

# section 5 literally: stage, commit, portability, undo, commit
say("--- the operator's by-hand steps literally on the merged tree")
paths = " ".join(TOUCHED)
GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
step(reh, "git add the touched paths", f"git add {paths}")
step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m '{ACT}: rehearsal' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m '{ACT} undone' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

# ACT-CLAUDE-COPIES-4 first, then W2-11 merged (X4), then this ACT: the order the two ACTs and the merge are planned in
say("--- with ACT-CLAUDE-COPIES-4 applied first and w2/W2-11 merged after it")
x4 = SCRATCH / "rehearsal-act4-first"
clone(X4, x4)
step(x4, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
step(x4, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(x4, f"check {i}", c["cmd"])
act4_changed = {l.split("|")[1] for l in ACT4_LIST.read_text().splitlines() if l}
mark(set(changed_set(x4)) >= set(TOUCHED) and not (set(TOUCHED) & act4_changed),
     "the ACT's six files change on that tree too; none is one of ACT-CLAUDE-COPIES-4's 19")
pcode, pfound = portability(x4)
mark(sorted(f["file"] for f in pfound if f["code"] == "GENERATED_DIFFERS") == [],
     f"portability on that tree after the apply: no GENERATED_DIFFERS (exit {pcode}; {len(pfound)} findings: {tally(pfound)}, "
     "the rest are ACT-CLAUDE-COPIES-4's window until W2-175 merges)")

# the live files, and the planted HOME
untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-315, DEC-992, DEC-1112", "author": "cto", "claimed_class": "b", "touched": touched, "files": files,
      "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}, "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
