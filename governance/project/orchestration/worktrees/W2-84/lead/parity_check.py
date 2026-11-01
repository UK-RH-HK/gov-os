"""Lead's check of rev-1's finding 1: do name listings that reach a hidden file get the same decision in the
session's own tree and in another tree? Planted world only (w2_84_support.make_world), under /tmp/gov-os-lead-W2-84.
Usage: PYTHONPATH=<worktree>/src python3 parity_check.py"""
import shutil
import sys
import tempfile

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-84/tests/acceptance/W2-84")
import w2_84_support as s  # noqa: E402

base = tempfile.mkdtemp(prefix="parity-", dir="/tmp/gov-os-lead-W2-84")
try:
    from pathlib import Path
    world = s.make_world(Path(base), links=False)
    own = world.tree(s.WT_OWN)
    other = world.tree(s.WT_OTHER)
    for label, tree in (("own", own), ("other", other)):
        calls = [
            s.bash(f"find {s.q(tree)} -type f"),
            s.bash(f"ls -R {s.q(tree)}"),
            s.glob_call("**/*", str(tree)),
            s.bash(f"find {s.q(tree)} -type f -exec cat {{}} +"),
            s.bash(f"ls {s.q(tree / 'eval' / 'memory' / 'hidden')}"),
            s.read(tree / s.HIDDEN_FILE),
        ]
        for call in calls:
            r = world.ask(call, s.ENGINEER, s.ENG, own)
            print(f"{label:5} {r.decision:5} {call}")
finally:
    shutil.rmtree(base, ignore_errors=True)
