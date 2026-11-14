"""Lead's own planted proof of W2-61h's hidden S4 case (DEC-1178 (1)): a throwaway sets root of planted questions
citing real non-evaluation files of this repository. Never reads ~/gov-os-eval. Prints outcomes only."""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-61h-c39")
OLD = "289b9314a"
REL = "src/gov/retrieval/measure.py"


def show(rev, rel):
    return subprocess.run(["git", "-C", str(ROOT), "show", f"{rev}:{rel}"], capture_output=True, text=True,
                          check=True).stdout.splitlines()


old, now = show(OLD, REL), show("HEAD", REL)
W = 3
moved = changed = None
for i in range(len(old) - W + 1):
    block = old[i:i + W]
    if any(not l.strip() for l in block) or len(set(block)) < W:
        continue
    hits = [j for j in range(len(now) - W + 1) if now[j:j + W] == block]
    if moved is None and len(hits) == 1 and hits[0] != i:
        moved = (i + 1, i + W)
    if changed is None and not hits:
        changed = (i + 1, i + W)
    if moved and changed:
        break
assert moved and changed, (moved, changed)
head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

tmp = Path(tempfile.mkdtemp(prefix="w2-61h-lead-plant-"))
hidden = tmp / "fixtures/evaluation/memory-retrieval/hidden"
hidden.mkdir(parents=True)
(tmp / "governance/project").mkdir(parents=True)
(tmp / "governance/project/path-map.yaml").write_text((ROOT / "governance/project/path-map.yaml").read_text())
os.chmod(tmp, 0o700)


def q(name, rel, lines, commit):
    (hidden / name).write_text(
        f"id: {name[:-5]}\nquestion: planted lead question {name}\ngold_answer: planted answer {name}\n"
        f"category: decision\ncommit: {commit}\nsources:\n- path: {rel}\n  lines: [{lines[0]}, {lines[1]}]\n")


q("x01.yaml", REL, moved, OLD)                        # (a) moved unchanged
q("x02.yaml", REL, changed, OLD)                      # (b) lines changed
q("x03.yaml", REL, (len(old) + 5, len(old) + 7), OLD)  # (c) no span at its own commit
q("x04.yaml", REL, (1, 3), head)                      # (d) control at HEAD
mode = sys.argv[1] if len(sys.argv) > 1 else "all"
if mode == "no-c":
    (hidden / "x03.yaml").unlink()
print(f"planted root {tmp} (moved block {moved}, changed block {changed}, files {sorted(p.name for p in hidden.iterdir())})")
env = {k: v for k, v in os.environ.items() if k not in ("GOV_ROLE", "GOV_TICKET")}
env.update(GOV_EVAL_SETS_ROOT=str(tmp), PYTHONPATH=str(ROOT / "src"), PYTHONUSERBASE="/home/usain/.local",
           HOME=str(ROOT / ".gov-runtime/scratch/empty-home"))
done = subprocess.run([sys.executable, "-m", "pytest", "tests/acceptance/W2-61h/test_w2_61h_hidden_form.py", "-q",
                       "-p", "no:cacheprovider", "-o", "tmp_path_retention_policy=failed", "-rA", "-k", "s4"],
                      cwd=ROOT, env=env, capture_output=True, text=True)
print(done.stdout[-2500:])
print("exit", done.returncode)
