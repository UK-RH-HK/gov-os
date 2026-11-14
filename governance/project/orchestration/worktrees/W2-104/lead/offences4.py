"""Run 4: W1-01's merge_offences on run 4's merges (and run 3's WIP merge, for contrast). Read-only."""
import sys
from pathlib import Path

ROOT = Path("/home/usain/gov-os-worktrees/W2-104")
sys.path.insert(0, str(ROOT / "tests/acceptance/W1-01"))
import w1_01_support as s  # noqa: E402

for ref in sys.argv[1:]:
    sha = s.git("rev-parse", ref, root=ROOT).strip()
    print(ref, sha[:12], "merge_offences:", s.merge_offences(sha, "tests/acceptance", ROOT))
