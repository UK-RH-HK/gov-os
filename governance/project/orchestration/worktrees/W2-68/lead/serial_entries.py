"""The serial-only entries the close runs in its serial phase (the list, less the entries routed to the nightly)."""
import sys
from pathlib import Path

from gov.close import serial
from gov.close.pytest_plugin import gov_close_serial_only as serial_only

root = Path(sys.argv[1])
out = Path(sys.argv[2])
listed = serial_only.entries(root)
phase = serial.phase(root, listed)
out.write_text("\n".join(phase) + "\n", encoding="utf-8")
print(f"{len(listed)} listed, {len(phase)} in the serial phase")
