"""Write the close's serial phase entries (the serial-only list less the nightly-routed ones), one per line."""
import sys
from pathlib import Path

from gov.close import serial
from gov.close.pytest_plugin import gov_close_serial_only as serial_only

root = Path("/home/usain/gov-os-worktrees/W2-84")
declared = serial.phase(root, serial_only.entries(root))
Path(sys.argv[1]).write_text("\n".join(declared) + "\n", encoding="utf-8")
print(len(declared), "serial entries")
