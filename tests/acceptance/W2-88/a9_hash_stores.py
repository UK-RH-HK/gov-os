"""Child program of S5's planted over-budget case: ``gov`` with the store hashed the moment its build is done.

``a9_hash_stores.py <gov arguments...>`` runs the CLI with ``gov.rebuild.command.run`` (which A9 calls in full, I3) wrapped:
right after the real rebuild returns, the sha256 of every store file (``store_hash``) is written on stderr as one line
``store-hash-after-build: <json>``; nothing is changed. The stage then goes on (the scale figures, the proposal, the record);
the case hashes the same files again once the process has ended and compares the two.
"""

import json
import sys

import gov.rebuild.command as rebuild
from store_hash import digest

original = rebuild.run


def hashed(root, args, config):
    result = original(root, args, config)
    sys.stderr.write("store-hash-after-build: " + json.dumps(digest(root), sort_keys=True) + "\n")
    sys.stderr.flush()
    return result


rebuild.run = hashed
sys.argv = ["gov", *sys.argv[1:]]
from gov.cli.main import main  # noqa: E402

raise SystemExit(main())
