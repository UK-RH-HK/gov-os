from pathlib import Path

from gov.close.pytest_plugin.gov_close_serial_only import entries
from gov.close.serial import phase

print("\n".join(phase(Path("."), entries(Path(".")))))
