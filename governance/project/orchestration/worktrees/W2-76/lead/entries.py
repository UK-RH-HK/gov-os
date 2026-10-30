"""The serial-only list's entries, one per line, as the close's plugin reads them. Arg 1: the worktree."""
import sys
from pathlib import Path

from gov.close.pytest_plugin.gov_close_serial_only import entries

print("\n".join(entries(Path(sys.argv[1]))))
