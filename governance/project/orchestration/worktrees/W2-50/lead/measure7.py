"""W2-50 run 8: the secrets-indexing check alone on this worktree's real stores, timed (DEC-853's proof).

warm: the declared command (`python3 -m gov.secrets` in the root), as gov check runs it; its stderr holds the reuse labels.
cold: the same scan with no record read and none written (read-only): every store scanned, timed.
"""
import subprocess
import sys
import time
from pathlib import Path

W = Path("/home/usain/gov-os-worktrees/W2-50")
L = W / ".gov-runtime/scratch/lead/log"
env = {"PYTHONPATH": str(W / "src"), "PATH": "/home/usain/.local/bin:/usr/local/bin:/usr/bin:/bin", "HOME": "/home/usain"}

mode = sys.argv[1]
if mode == "warm":
    start = time.time()
    done = subprocess.run(["sh", "-c", "python3 -m gov.secrets"], cwd=W, env=env, capture_output=True, text=True)
    seconds = time.time() - start
    labels = [line for line in done.stderr.splitlines() if "clean result reused" in line]
    (L / "secrets-7-warm.err").write_text(done.stderr)
    print(f"warm: exit {done.returncode}, {seconds:.1f} s, {len(labels)} reuse labels, stdout lines {len(done.stdout.splitlines())}")
    for line in labels:
        if "store.db " in line or "code.db " in line:
            print(line)
else:
    code = (
        "import time, gov.secrets as s\n"
        "from pathlib import Path\n"
        "s._trusted = lambda root, scanner: set()\n"
        "s._record = lambda root, scanner, clean: None\n"
        "t = time.time(); found = s.stores_with_secrets(Path('.')); print(len(found), round(time.time() - t, 1))\n"
    )
    done = subprocess.run([sys.executable, "-c", code], cwd=W, env=env, capture_output=True, text=True)
    print(f"cold: exit {done.returncode}, stores with a secret and seconds: {done.stdout.strip()}, stderr tail: {done.stderr[-300:]}")
