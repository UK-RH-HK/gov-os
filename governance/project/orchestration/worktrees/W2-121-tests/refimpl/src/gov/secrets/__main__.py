"""The secrets-indexing check: ``python3 -m gov.secrets`` in the project root. Exit 0: no secret in a derived store.

With the scan off by configuration (DEC-1045) it says so and exits 2, the check runner's not-applicable answer, which
its declaration allows: reported YELLOW with that reason, never a silent GREEN.
"""

import json
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.secrets import SCAN_OFF, scan_on, stores_with_secrets

try:
    scanning = scan_on(Path.cwd())
except GovError as error:  # the switch cannot be read: no verdict, never off
    print(f"{error.code}: {error.message}")
    sys.exit(1)
if not scanning:
    print(json.dumps({"not_applicable": True, "reason": SCAN_OFF}))
    sys.exit(2)
found = stores_with_secrets(Path.cwd())
for rel in found:
    print(f"secret found in derived store: {rel}")  # the file only, never the secret
sys.exit(1 if found else 0)
