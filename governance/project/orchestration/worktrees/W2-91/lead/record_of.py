"""Prints the newest visible-half measure record under the run's records folder (the control's, when called right
after the control's measure ends and before the head's starts). The argument (the control's JSON output) is only
checked to exist and be non-empty."""
import sys
from pathlib import Path

if not Path(sys.argv[1]).is_file() or Path(sys.argv[1]).stat().st_size == 0:
    sys.exit(0)
records = sorted(Path("/home/usain/gov-os-runs/W2-91/records").glob("measure-memory-retrieval-visible-*.json"),
                 key=lambda p: p.stat().st_mtime)
if records:
    print(records[-1])
