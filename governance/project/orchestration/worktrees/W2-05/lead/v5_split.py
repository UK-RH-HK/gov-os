"""Run 5: split the selection's runs in two parts (A now, B after the repair batch's tests merge).

Part A: everything selected but tests/acceptance/W1-02 and tests/acceptance/W2-05 (the two suites the repair batch
changes). Part B: those two suites, and the serial entries under them. Writes in log/v5:
  parallel-opts-A.txt, serial-args-A.txt, parallel-opts-B.txt, parallel-args-B.txt, serial-args-B.txt
"""
from pathlib import Path

LOG = Path("/home/usain/gov-os-worktrees/W2-05/.gov-runtime/scratch/lead/log/v5")
ROOT = "/home/usain/gov-os-worktrees/W2-05"
SUITES = ("tests/acceptance/W1-02", "tests/acceptance/W2-05")
opts = [line for line in (LOG / "parallel-opts.txt").read_text().splitlines() if line]
serial = [line for line in (LOG / "serial-args.txt").read_text().splitlines() if line]

(LOG / "parallel-opts-A.txt").write_text("".join(f"{o}\n" for o in opts + [f"--ignore={ROOT}/{s}" for s in SUITES]))
(LOG / "serial-args-A.txt").write_text("".join(f"{e}\n" for e in serial if not e.startswith(SUITES)))
# Part B runs only the two suites; the selection's options that concern them are kept.
mine = [o for o in opts if any(f"{ROOT}/{s}" in o for s in SUITES)]
(LOG / "parallel-opts-B.txt").write_text("".join(f"{o}\n" for o in mine))
(LOG / "parallel-args-B.txt").write_text("".join(f"{s}\n" for s in SUITES))
(LOG / "serial-args-B.txt").write_text("".join(f"{e}\n" for e in serial if e.startswith(SUITES)))
print("A opts", len(opts) + 2, "A serial", sum(1 for e in serial if not e.startswith(SUITES)))
print("B opts", mine, "B serial", [e for e in serial if e.startswith(SUITES)])
