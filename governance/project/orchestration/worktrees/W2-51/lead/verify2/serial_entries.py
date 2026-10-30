"""Print the serial-only entries the close's serial phase runs (W2-57: nightly-routed entries left out), one per line."""
from pathlib import Path

from gov.close import serial
from gov.close.pytest_plugin import gov_close_serial_only as plugin

root = Path("/home/usain/gov-os-worktrees/W2-51")
for entry in serial.phase(root, plugin.entries(root)):
    print(entry)
