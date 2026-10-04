"""The secrets-indexing check: ``python3 -m gov.secrets`` in the project root. Exit 0: no secret in a derived store."""

import sys
from pathlib import Path

from gov.secrets import stores_with_secrets

found = stores_with_secrets(Path.cwd())
for rel in found:
    print(f"secret found in derived store: {rel}")  # the file only, never the secret
sys.exit(1 if found else 0)
