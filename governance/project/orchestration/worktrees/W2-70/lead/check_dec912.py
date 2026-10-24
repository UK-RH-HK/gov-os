"""Lead check for DEC-912 item 1 (W2-70 run 2): merge_offences on the two real merges and a hand-edited fixture.

Run with PYTHONPATH=<worktree>/src. Prints 12-digit ids only (DEC-911).
"""
import os
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path("/home/usain/gov-os-worktrees/W2-70")
sys.path.insert(0, str(WT / "tests" / "acceptance" / "W1-01"))
import w1_01_support as s  # noqa: E402


def full(ref):
    return subprocess.run(["git", "-C", str(WT), "rev-parse", "--verify", ref + "^{commit}"],
                          capture_output=True, text=True, check=True).stdout.strip()


failures = 0
for short in ("03f470a5", "4ef3293a"):
    sha = full(short)
    offences = s.merge_offences(sha, "tests/acceptance", root=WT)
    print(f"{sha[:12]}: merge_offences = {offences!r}")
    if offences:
        failures += 1

env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@example.invalid",
           GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@example.invalid")


def g(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          check=True, env=env).stdout.strip()


with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
    repo = Path(tmp) / "r"
    repo.mkdir()
    g(repo, "init", "-q", "-b", "main")
    f = repo / "tests" / "acceptance" / "X" / "test_x.py"
    f.parent.mkdir(parents=True)
    lines = [f"line {i}\n" for i in range(10)]
    f.write_text("".join(lines))
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", "base\n\nRole: independent-test-designer")
    g(repo, "checkout", "-q", "-b", "side")
    lines_side = list(lines)
    lines_side[8] = "side edit\n"
    f.write_text("".join(lines_side))
    g(repo, "commit", "-q", "-am", "side\n\nRole: independent-test-designer")
    g(repo, "checkout", "-q", "main")
    lines_main = list(lines)
    lines_main[1] = "main edit\n"
    f.write_text("".join(lines_main))
    g(repo, "commit", "-q", "-am", "main\n\nRole: independent-test-designer")
    g(repo, "merge", "-q", "--no-ff", "--no-commit", "side")
    clean = f.read_text()
    f.write_text(clean.replace("line 5\n", "hand edit\n"))
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", "merge with a hand edit\n\nRole: orchestrator")
    hand = g(repo, "rev-parse", "HEAD")
    offences = s.merge_offences(hand, "tests/acceptance", root=repo, exempt={})
    print(f"hand-edited fixture {hand[:12]}: merge_offences = {offences!r}")
    if not offences:
        failures += 1
    # control: the same merge left as git made it passes
    g(repo, "checkout", "-q", "-b", "control", "HEAD^1")
    g(repo, "merge", "-q", "--no-ff", "-m", "clean merge\n\nRole: orchestrator", "side")
    ctl = g(repo, "rev-parse", "HEAD")
    offences = s.merge_offences(ctl, "tests/acceptance", root=repo, exempt={})
    print(f"clean fixture {ctl[:12]}: merge_offences = {offences!r}")
    if offences:
        failures += 1

print("RESULT:", "PASS" if failures == 0 else f"FAIL ({failures})")
sys.exit(1 if failures else 0)
