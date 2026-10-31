"""The pre-index filter in a process of its own, for the W2-107 acceptance tests (not a test module).

Reads one JSON request on standard input: ``{"root": ..., "paths": [...], "names": [...]}``. Runs
``gov.secrets.indexable(root, paths)``, then ``gov.secrets.path_holds_secret(root, name)`` for each name, and prints
one JSON line: what ``indexable`` returned (null if anything raised), the verdict per name in order, the process's
``scan_counts()`` (null where there is none), the type of what was raised (null if nothing) and the file
``gov.secrets`` came from. It prints no path name and no content.
"""

import json
import sys
from pathlib import Path

from gov import secrets

request = json.loads(sys.stdin.read())
root = Path(request["root"])
out = {"indexable": None, "names": [], "counts": None, "error": None, "gov": secrets.__file__}
try:
    kept = secrets.indexable(root, request["paths"])
    out["names"] = [secrets.path_holds_secret(root, name) for name in request["names"]]
    out["indexable"] = kept
except Exception as error:  # the case reads the type; the message is not printed
    out["error"] = type(error).__name__
counts = getattr(secrets, "scan_counts", None)
out["counts"] = counts() if callable(counts) else None
print(json.dumps(out))
