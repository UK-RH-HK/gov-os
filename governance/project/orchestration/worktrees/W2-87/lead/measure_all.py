"""The lead's re-measure of W2-87 (visible half only): W2-61's measure on the head clone's stores, three times, with
the base's retrieval code (the control), batch 1's (the register fix) and the head's (both parts), DEC-877.
Each run's stdout, stderr, exit code and record path go to the run folder's log/. Never --part hidden."""
import os
import subprocess
import time
from pathlib import Path

RUNS = Path("/home/usain/gov-os-runs/W2-87")
BIN = Path("/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-87/64065a1a-8024-4e7b-9e9b-f50286d504ca/scratchpad/bin")
LOG = Path("/tmp/claude-1000/-home-usain-gov-os-worktrees-W2-87/64065a1a-8024-4e7b-9e9b-f50286d504ca/scratchpad/measure")
LOG.mkdir(parents=True, exist_ok=True)
OUT = RUNS / "records"
env = {key: value for key, value in os.environ.items() if key != "GOV_TICKET"}
env["PYTHONPATH"] = str(RUNS / "measure/src")


def measure(name, launcher, compare=None):
    before = set(OUT.glob("*.json")) if OUT.exists() else set()
    argv = ["python3", "-m", "gov.retrieval.measure", "memory-retrieval", "--root", str(RUNS / "head"),
            "--sets-root", str(RUNS / "measure"), "--part", "visible", "--gov", str(BIN / launcher),
            "--out", str(OUT), "--json", *(["--compare", str(compare)] if compare else [])]
    started = time.time()
    with open(LOG / f"{name}.out", "w") as out, open(LOG / f"{name}.err", "w") as err:
        code = subprocess.run(argv, cwd=str(RUNS / "head"), env=env, stdout=out, stderr=err,
                              stdin=subprocess.DEVNULL).returncode
    new = sorted(set(OUT.glob("*.json")) - before)
    (LOG / f"{name}.exit").write_text(f"{code} {time.time() - started:.0f}s {' '.join(map(str, new))}\n")
    return new[-1] if new else None


import sys  # noqa: E402

# one run per background call (each about 38 minutes), so none passes the Bash tool's two-hour limit:
# argv: control | register <control record> | head <control record>
phase = sys.argv[1]
launcher = {"control": "gov-base", "register": "gov-reg", "head": "gov-head"}[phase]
print(measure(phase, launcher, sys.argv[2] if len(sys.argv) > 2 else None))
