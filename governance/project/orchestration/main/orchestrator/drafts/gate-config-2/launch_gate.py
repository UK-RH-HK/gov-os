"""ACT-GATE-CONFIG-2's rehearsal: W2-20's launch admission step (_admit_start), as `gov launch` runs it, for an
engineer with the given GPU need (MiB, or empty). Prints ADMITTED or REFUSED and exits with the launcher's code.
Run from W2-20's worktree with its src on PYTHONPATH and HOME set to the throwaway home."""
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.launch.launcher import _admit_start

need = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1] else None
try:
    _admit_start(Path.cwd(), "engineer", "W2-20", None, need)
    print(f"gov launch's gate (engineer, GPU need {need}): ADMITTED")
    sys.exit(0)
except GovError as e:
    print(f"gov launch's gate (engineer, GPU need {need}): REFUSED {e.code}, exit {getattr(e, 'exit_code', '?')}: {e.message[:900]}")
    sys.exit(getattr(e, "exit_code", 3) or 3)
