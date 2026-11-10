"""Builds and rehearses ACT-CLAUDE-COPIES-1 (the .claude/ copies of W2-128 and W2-142; DEC-1109 (2), DEC-1112 (3)).

    python3 build_claude_copies_act.py <live repo> <bundle dir> <scratch dir> [<ACT id>]

1. A clone at the live repository's HEAD; in it, every rulesync source the portability check finds differing from its
   kernel file is brought to the kernel's (a skill file byte for byte; a role as its source's front matter with the
   kernel role's body), rulesync generates into an empty folder (portability's own GENERATE form), every generated
   .claude/ file that differs is taken from there, and the eight kernel templates are copied to .claude/templates/.
   The touched list is what changed in the clone. template/.rulesync/ is a ticket path, never touched here.
2. The bundle: before/ and after/ copies of each touched file, list.txt, apply.sh, manifest.json, rehearsal.log.
3. The rehearsal, in a second fresh clone, as the operator runs it: apply.sh check, apply, the checks, the portability
   check, undo, every file byte-for-byte back; the log ends with "failures: <n>".
"""
import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

LIVE, BUNDLE, SCRATCH = (Path(a).resolve() for a in sys.argv[1:4])
ACT = sys.argv[4] if len(sys.argv) > 4 else "ACT-CLAUDE-COPIES-1"  # the ACT's id (ACT-CLAUDE-COPIES-2 after W2-153)
TEMPLATES = ("brief", "role-research", "role-product-spec", "role-test-designer", "role-engineer", "role-reviewer",
             "role-lead", "role-cto")
GENERATED_FOLDERS = (".claude/agents", ".claude/skills", ".claude/commands")
TOUCHED = []  # computed from the generation clone
GENERATE = ["generate", "--targets", "claudecode,agentsmd", "--features",
            "rules,hooks,permissions,subagents,commands,skills", "--input-roots"]
RULESYNC = shutil.which("rulesync") or str(Path.home() / ".local/bin/rulesync")
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
CHECK_COPIES = None  # built once TOUCHED is known


def sha(b):
    return hashlib.sha256(b).hexdigest()


def run(cmd, cwd, env=None):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)
    return r.returncode, (r.stdout + r.stderr).strip()


def clone(dest):
    if dest.exists():
        shutil.rmtree(dest)
    head = run(["git", "rev-parse", "HEAD"], LIVE)[1]
    assert run(["git", "clone", "-q", "--no-hardlinks", str(LIVE), str(dest)], SCRATCH)[0] == 0
    assert run(["git", "checkout", "-q", head], dest)[0] == 0
    return head


log = []
def say(line):
    log.append(line)
    print(line)


SCRATCH.mkdir(parents=True, exist_ok=True)
gen = SCRATCH / "gen-clone"
head = clone(gen)
say(f"{ACT} rehearsal; live HEAD {head[:12]}; rulesync {run([RULESYNC, '--version'], SCRATCH)[1]}")
def portability(tree):
    env = dict(os.environ, PYTHONPATH=str(tree / "src"), RULESYNC_BIN=RULESYNC)
    code, out = run([sys.executable, "-m", "gov.adapters.portability"], tree, env)
    return code, (json.loads(out)["findings"] if out.startswith("{") else [{"code": "UNREADABLE", "message": out[-300:]}])


code, found = portability(gen)
say(f"portability at HEAD: exit {code}; {len(found)} findings: " + "; ".join(f"{f['code']} {f.get('file')}" for f in found))
def body_of(text):
    """A Markdown file's body after its front matter (portability's _split rule)."""
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end >= 0:
            return text[end + 4:].partition("\n")[2].lstrip("\n")
    return text.lstrip("\n")


def front_of(text):
    end = text.find("\n---", 3) if text.startswith("---") else -1
    if end < 0:
        raise SystemExit("a rulesync role source without front matter")
    return text[:end + 4].rstrip("\n") + "\n"


for f in found:
    code, msg, src = f["code"], f.get("message", ""), f.get("file")
    if code in ("GENERATED_DIFFERS", "TEMPLATE_COPY_MISSING", "TEMPLATE_COPY_DIFFERS"):
        continue  # the generation and copy steps below write these
    if code == "SOURCE_DIFFERS" and "differs from " in msg:
        origin = msg.split("differs from ", 1)[1]
        if "/skills/" in origin:
            (gen / src).write_bytes((gen / origin).read_bytes())
        elif "/roles/" in origin or "/templates/role-" in origin:
            # a role source keeps its own rulesync front matter (tools, and claudecode.skills after W2-153) and takes
            # the body of what the check compares it with: the kernel role (before W2-153) or its role template
            # (after); a template's own front matter is never copied in (review R2)
            text = (gen / src).read_text(encoding="utf-8")
            (gen / src).write_text(front_of(text) + "\n" + body_of((gen / origin).read_text(encoding="utf-8")),
                                   encoding="utf-8")
        else:
            raise SystemExit(f"a SOURCE_DIFFERS this builder does not repair: {f}")
        continue
    raise SystemExit(f"a finding this builder does not repair (a ticket's to fix, not an ACT's): {f}")
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
    cur = (LIVE / rel).read_bytes() if (LIVE / rel).is_file() else None
    new = (gen / rel).read_bytes()
    before, after = (sha(cur) if cur is not None else None), sha(new)
    assert before != after, rel
    if cur is not None:
        put(f"before/repo/{rel}", cur)
    put(f"after/repo/{rel}", new)
    touched.append({"root": "repo", "path": rel, "before": before, "after": after})
    lines.append(f"repo|{rel}|{before or 'null'}|{after}")
put("list.txt", ("\n".join(lines) + "\n").encode())
put("apply.sh", APPLY_SH.encode())
os.chmod(BUNDLE / "apply.sh", 0o755)
pairs = [(f"template/governance/kernel/templates/{t}.md", f".claude/templates/{t}.md") for t in TEMPLATES]
pairs += [(r.replace(".rulesync/skills/", "template/governance/kernel/skills/", 1), r)
          for r in TOUCHED if r.startswith(".rulesync/skills/")]
CHECK_COPIES = " && ".join(f"cmp -s {a} {b}" for a, b in pairs)
checks = [{"cmd": CHECK_COPIES, "exit": 0, "count": None}]

# the rehearsal, as the operator runs it, in a fresh clone
reh = SCRATCH / "rehearsal-clone"
clone(reh)
fails = 0
planted = Path(tempfile.mkdtemp(prefix="planted-home-", dir=SCRATCH))  # the operator's G8 plants HOME the same way
live_before = {rel: (sha((LIVE / rel).read_bytes()) if (LIVE / rel).is_file() else None) for rel in TOUCHED}
say(f"rehearsal clone at the live HEAD; HOME planted at a fresh empty folder")
def step(name, cmd):
    global fails
    code, out = run(["bash", "-c", cmd], reh, dict(os.environ, HOME=str(planted)))
    ok = code == 0
    fails += 0 if ok else 1
    say(f"{'ok  ' if ok else 'FAIL'} {name}: exit {code}{(' ' + out[-300:]) if out and not ok else ''}")
    return code
before_state = {rel: ((reh / rel).read_bytes() if (reh / rel).is_file() else None) for rel in TOUCHED}
step("apply.sh check (the live state as stated)", f"bash {BUNDLE}/apply.sh check")
step("apply.sh apply", f"bash {BUNDLE}/apply.sh apply")
for i, c in enumerate(checks, 1):
    step(f"check {i}", c["cmd"])
env = dict(os.environ, PYTHONPATH=str(reh / "src"), RULESYNC_BIN=RULESYNC)
code, out = run([sys.executable, "-m", "gov.adapters.portability"], reh, env)
fails += 0 if code == 0 else 1
say(f"{'ok  ' if code == 0 else 'FAIL'} portability after the apply: exit {code}; findings "
    f"{json.loads(out)['findings'] if out.startswith('{') else out[-300:]}")
st = run(["git", "status", "--porcelain", "--untracked-files=all"], reh)[1].splitlines()
same = sorted(l.strip().split(None, 1)[1] for l in st) == sorted(TOUCHED)
fails += 0 if same else 1
say(f"{'ok  ' if same else 'FAIL'} the changed set equals the touched list ({len(st)} files)")
step("apply.sh undo", f"bash {BUNDLE}/apply.sh undo")
back = all(((reh / rel).read_bytes() if (reh / rel).is_file() else None) == before_state[rel] for rel in TOUCHED)
clean = run(["git", "status", "--porcelain", "--untracked-files=all"], reh)[1] == ""
fails += 0 if (back and clean) else 1
say(f"{'ok  ' if back and clean else 'FAIL'} undo: every file byte for byte back, the tree clean")
live_after = {rel: (sha((LIVE / rel).read_bytes()) if (LIVE / rel).is_file() else None) for rel in TOUCHED}
untouched = live_after == live_before and not any(planted.iterdir())
fails += 0 if untouched else 1
say(f"{'ok  ' if untouched else 'FAIL'} the live files unchanged by the rehearsal, and nothing written to the planted HOME")
say(f"failures: {fails}")
put("rehearsal.log", ("\n".join(log) + "\n").encode())
m = {"act": ACT, "dec": "DEC-1109", "author": "cto", "claimed_class": "b", "touched": touched, "files": files,
     "rehearsal": {"log": "rehearsal.log", "sha256": files["rehearsal.log"]}, "checks": checks, "commands": []}
raw = json.dumps(m, indent=1).encode()
(BUNDLE / "manifest.json").write_bytes(raw)
print(json.dumps({"manifest_sha256": sha(raw), "touched": len(touched), "failures": fails, "head": head[:12]}))
