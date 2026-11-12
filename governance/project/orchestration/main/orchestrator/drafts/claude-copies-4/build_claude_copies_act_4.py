"""Builds and rehearses ACT-CLAUDE-COPIES-4 (the .claude/ and root .rulesync/ copies of W2-175's approved role templates;
DEC-1139 (1)). A copy of build_claude_copies_act.py (the committed tool is not edited), changed in these places:

  * the generation is made in a clone of BASE, a clone of integrate with w2/W2-175 (4c0c73472fd8) merged into it, so the
    copies come from the approved bytes; the before-bytes come from INTEGRATE, a clone of plain integrate (the tree the
    operator's dry run and the real apply see before W2-175 merges), and are required to equal BASE's;
  * the manifest's checks are sha256 checks of the owner-approved bytes (CIT-P section 2), so they read the same on
    integrate before and after W2-175 merges (the model's check compared the template copies with template/, which
    fails on integrate until W2-175 merges);
  * the rehearsal runs on BOTH trees (check, apply, verify, undo, re-apply), with HOME planted, then on the merged tree
    S6's cases (through the heavy-job gate) and the portability check, then section 5 literally (stage, commit,
    portability, undo, commit);
  * rehearsal.log carries no live head, pid, date, timing or count of the live tree, so a re-run is byte-equal.

    python3 build_claude_copies_act_4.py <BASE clone> <INTEGRATE clone> <bundle dir> <scratch dir> <CIT-P file> [ACT id]
"""
import hashlib, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

BASE, INTEG, BUNDLE, SCRATCH, CITP = (Path(a).resolve() for a in sys.argv[1:6])
ACT = sys.argv[6] if len(sys.argv) > 6 else "ACT-CLAUDE-COPIES-4"
LIVE_TREE = Path("/home/usain/Dynamic-Agentic-Engineering-OS")      # read-only: only to prove the rehearsal left it alone
HEAVY = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh"
W175 = "4c0c73472fd8"
TEMPLATES = ("role-research", "role-product-spec", "role-test-designer", "role-engineer", "role-reviewer", "role-lead",
             "role-cto")
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
S6_CASES = ["tests/acceptance/W2-128", "tests/acceptance/W2-152", "tests/acceptance/W2-153"]
APPLY_SH = r'''#!/bin/bash
# The copies ACT's apply.sh: reads its bundle from its own folder; check, apply, undo by list.txt, relative to the
# repository it is run in (its cwd).
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
      if [ "$after" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/after/$root/$path" > "$f"; fi ;;
    undo)
      if [ "$before" = null ]; then rm -f "$f"; else mkdir -p "$(dirname "$f")"; rm -f "$f"; cat "$B/before/$root/$path" > "$f"; fi ;;
    *) exit 2 ;;
  esac
done < "$B/list.txt"
[ "$step" = undo ] && rmdir .claude/templates 2>/dev/null
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
say(f"{ACT} rehearsal; base: integrate with w2/W2-175 {W175} merged; rulesync "
    f"{run([RULESYNC, '--version'], SCRATCH)[1]}")


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
say(f"portability on the base (W2-175 merged, no copies): exit {code}; {len(found)} findings: {tally(found)}")


def composed(src):
    probe = ("import sys, json; sys.path.insert(0, sys.argv[1] + '/src'); from gov.adapters import portability as p; "
             "from pathlib import Path; print(json.dumps(p.compose(Path(sys.argv[1]), sys.argv[2])))")
    code, out = run([sys.executable, "-I", "-c", probe, str(gen), Path(src).stem], gen)
    if code != 0:
        raise SystemExit(f"compose() failed for {src}: {out[-300:]}")
    return json.loads(out)


for f in found:
    code, msg, src = f["code"], f.get("message", ""), f.get("file")
    if code in ("GENERATED_DIFFERS", "TEMPLATE_COPY_MISSING", "TEMPLATE_COPY_DIFFERS"):
        continue  # the generation and copy steps below write these
    if code == "SOURCE_DIFFERS" and src.startswith(".rulesync/subagents/") and "its composition of" in msg:
        (gen / src).write_text(composed(src), encoding="utf-8")   # the check's own compose(): one implementation
        continue
    raise SystemExit(f"a finding this builder does not repair: {f}")
with tempfile.TemporaryDirectory() as fresh:
    code, out = run([RULESYNC, *GENERATE, str((gen / ".rulesync").resolve())], fresh)
    assert code == 0, out
    for path in sorted(Path(fresh).rglob("*")):
        rel = str(path.relative_to(fresh))
        if path.is_file() and rel.startswith(GENERATED_FOLDERS) and (
                not (gen / rel).is_file() or (gen / rel).read_bytes() != path.read_bytes()):
            (gen / rel).parent.mkdir(parents=True, exist_ok=True)
            (gen / rel).write_bytes(path.read_bytes())
(gen / ".claude/templates").mkdir(exist_ok=True)
for t in TEMPLATES:
    (gen / f".claude/templates/{t}.md").write_bytes((gen / f"template/governance/kernel/templates/{t}.md").read_bytes())
code, after = portability(gen)
say(f"portability in the generation clone after the copies: exit {code}; findings {after}")
assert code == 0, after
changed = run(["git", "status", "--porcelain", "--untracked-files=all"], gen)[1].splitlines()
TOUCHED = sorted(l.strip().split(None, 1)[1] for l in changed)
assert all(r.startswith((".claude/", ".rulesync/")) for r in TOUCHED), TOUCHED
say(f"generation clone: {len(TOUCHED)} files changed or new: " + ", ".join(TOUCHED))

# the approved bytes (CIT-P section 2): the seven templates and the six composed subagents
approved = {p: n for p, _b, n in re.findall(r"\| `(template/[^`]+)` \| `([0-9a-f]{64})` \| `([0-9a-f]{64})` \|",
                                            CITP.read_text(encoding="utf-8"))}
assert len(approved) == 13, approved
want = {}
for p, n in approved.items():
    if p.startswith("template/governance/kernel/templates/"):
        want[".claude/templates/" + Path(p).name] = n
    else:
        want[p.replace("template/.rulesync/", ".rulesync/", 1)] = n
for rel, n in want.items():
    assert sha((gen / rel).read_bytes()) == n, f"{rel} is not the approved sha256"
say(f"the {len(want)} copies equal the approved sha256 of CIT-P section 2 (7 .claude/templates, 6 .rulesync/subagents)")

# the bundle: before-bytes from plain integrate (the tree the operator's dry run sees), required equal to the base's
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
    cur_base = (BASE / rel).read_bytes() if (BASE / rel).is_file() else None
    assert cur == cur_base, f"{rel} differs between integrate and the merged base"
    new = (gen / rel).read_bytes()
    before, after_h = (sha(cur) if cur is not None else None), sha(new)
    assert before != after_h, rel
    if cur is not None:
        put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after_h})
    lines.append(f"repo|{rel}|{before or 'null'}|{after_h}")
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)


def sha_check(pairs):
    return "sha256sum -c - <<'EOF'\n" + "\n".join(f"{h}  {p}" for p, h in pairs) + "\nEOF"
agents = [(t["path"], t["after"]) for t in touched if t["path"].startswith(".claude/agents/")]
checks = [{"cmd": sha_check(sorted(want.items())), "exit": 0, "count": None},
          {"cmd": sha_check(agents), "exit": 0, "count": None}]

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


def step(tree, name, cmd, show_ok_output=False):
    code, out = run(["bash", "-c", cmd], tree, dict(os.environ, HOME=str(planted)))
    mark(code == 0, f"{name}: exit {code}{(' ' + out[-300:]) if out and code != 0 else ''}")
    return code, out


def tree_state(tree):
    return {rel: ((tree / rel).read_bytes() if (tree / rel).is_file() else None) for rel in TOUCHED}


def changed_set(tree):
    st = run(["git", "status", "--porcelain", "--untracked-files=all"], tree)[1].splitlines()
    return sorted(l.strip().split(None, 1)[1] for l in st)


def rehearse(label, src, merged):
    say(f"--- rehearsal on {label}; HOME planted at a fresh empty folder")
    reh = SCRATCH / f"rehearsal-{'merged' if merged else 'integrate'}"
    clone(src, reh)
    before_state = tree_state(reh)
    code, _ = step(reh, "apply.sh check (every target at its stated before sha256)", f"bash {BUNDLE}/apply.sh check")
    step(reh, "apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
    for i, c in enumerate(checks, 1):
        step(reh, f"check {i} (sha256sum -c, {len(c['cmd'].splitlines()) - 2} files)", c["cmd"])
    mark(changed_set(reh) == TOUCHED, f"the changed set equals the touched list ({len(TOUCHED)} files)")
    after_state = tree_state(reh)
    mark(all(sha(after_state[r]) == next(t["after"] for t in touched if t["path"] == r) for r in TOUCHED),
         "every target is at its stated after sha256")
    pcode, pfound = portability(reh)
    if merged:
        mark(pcode == 0 and not pfound, f"portability after the apply (W2-175 merged): exit {pcode}; findings {pfound}")
    else:
        say(f"info portability after the apply (W2-175 not merged): exit {pcode}; {len(pfound)} findings: {tally(pfound)}")
    step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
    back = tree_state(reh) == before_state
    clean = run(["git", "status", "--porcelain", "--untracked-files=all"], reh)[1] == ""
    mark(back and clean, "undo: every file byte for byte back, the tree clean")
    step(reh, "apply.sh check after the undo", f"bash {BUNDLE}/apply.sh check")
    step(reh, "apply.sh apply (re-apply)", f"bash {BUNDLE}/apply.sh apply")
    for i, c in enumerate(checks, 1):
        step(reh, f"check {i} after the re-apply", c["cmd"])
    mark(tree_state(reh) == after_state and changed_set(reh) == TOUCHED,
         "the re-apply gives the same bytes and the same changed set as the first apply")
    return reh


rehearse("plain integrate (the main tree before W2-175 merges)", INTEG, merged=False)
reh = rehearse("integrate with W2-175 merged", BASE, merged=True)

# S6 and portability on the merged clone with the ACT applied, through the heavy-job gate
say("--- S6 on the merged tree with the ACT applied: " + " ".join(S6_CASES))
env = dict(os.environ, PYTHONPATH=str(reh / "src"), TMPDIR=str(TMP))
code, out = run(["bash", HEAVY, "env", f"TMPDIR={TMP}", f"PYTHONPATH={reh / 'src'}", "python3", "-m", "pytest", *S6_CASES,
                 "-q", "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed"], reh, env)
# the gate may add a line after pytest's own summary ("heavy_slot: ... waiting"), so the summary is the last line that
# ends "in <seconds>s"; the seconds themselves never reach the log
summary = [ln for ln in out.splitlines() if re.search(r" in [\d.]+s(?: \(.*\))?$", ln)]
m = {k: int(v) for v, k in re.findall(r"(\d+) (passed|failed|error|errors|skipped|xfailed|xpassed|deselected)",
                                      summary[-1] if summary else "")}
passed, failed = m.get("passed", 0), m.get("failed", 0) + m.get("error", 0) + m.get("errors", 0)
(SCRATCH / "s6-tail.txt").write_text("\n".join(out.splitlines()[-40:]) + "\n")
mark(code == 0 and failed == 0 and passed > 0, f"S6 (W2-128, W2-152, W2-153 acceptance): exit {code}; {passed} passed, {failed} failed"
     + (f", {m.get('skipped')} skipped" if m.get("skipped") else ""))
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"python3 -m gov.adapters.portability on the merged tree with the ACT applied: exit {pcode}; "
     f"findings {pfound}")

# section 5 literally: stage, commit, portability, undo, commit
say("--- section 5 literally on the merged tree")
paths = " ".join(TOUCHED)
GIT = "git -c user.name=rehearsal -c user.email=rehearsal@example.invalid"
step(reh, "git add the touched paths", f"git add {paths}")
code, out = step(reh, "staged count equals the touched list", f"test \"$(git diff --cached --name-only | wc -l)\" = {len(TOUCHED)}")
step(reh, "commit", f"{GIT} commit -q -m 'ACT-CLAUDE-COPIES-4: rehearsal' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
pcode, pfound = portability(reh)
mark(pcode == 0 and not pfound, f"portability after the commit: exit {pcode}; findings {pfound}")
step(reh, "apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
step(reh, "git add the touched paths (undo)", f"git add {paths}")
step(reh, "commit the undo", f"{GIT} commit -q -m 'ACT-CLAUDE-COPIES-4 undone' --trailer 'Task: DAEO-sdxk' --trailer 'Role: owner'")
step(reh, "the undo commit returns the tree to the start (empty diff over the touched paths)",
     f"git diff --quiet HEAD~2 HEAD -- {paths}")

# the live files, and the planted HOME
untouched = live_state() == live_before and not any(planted.iterdir())
mark(untouched, "the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
mf = {"act": ACT, "dec": "DEC-1139", "author": "cto", "claimed_class": "b", "touched": touched, "files": files,
      "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}, "checks": checks, "commands": []}
raw = json.dumps(mf, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails}))
