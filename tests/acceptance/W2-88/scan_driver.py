"""A child process for S27 (``test_w2_88_scan_speed.py``, ``test_w2_88_scan_folder.py``): judge a list of paths with
``gov.secrets.indexable`` from the ``gov`` that sits in the folder given first (the code of the base, a ``git archive`` of
``src`` made by the case, or this worktree's), and print what it returned and how long it took as one JSON line on stdout.

    python scan_driver.py <src folder> <root> <file holding the JSON list of paths>

The line also holds ``counts``: ``gov.secrets.scan_counts()`` after the call, where the module has it (else null). With
``S27_DRIVER_CATCH=1`` in the environment (run 9) an exception out of ``indexable`` is not a crash: the line then holds
``raised`` (the exception's class name) and ``message`` (its first 300 characters), ``kept`` null, and the exit is 0.

Nothing here knows a secret's value: the planted files are made by the case and the answer is a list of paths.
"""

import json
import os
import sys
import time
from pathlib import Path

src, root, listing = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, src)

import gov.secrets as secrets  # noqa: E402

paths = json.loads(listing.read_text(encoding="utf-8"))
counts = getattr(secrets, "scan_counts", None)
began = time.perf_counter()
answer = {"raised": None, "message": None}
try:
    kept = list(secrets.indexable(root, paths))
except Exception as error:  # noqa: BLE001 - reported to the case, which judges it
    if os.environ.get("S27_DRIVER_CATCH") != "1":
        raise
    kept = None
    answer = {"raised": type(error).__name__, "message": str(error)[:300]}
seconds = time.perf_counter() - began
print(json.dumps({"kept": kept, "seconds": seconds, "judged": len(paths), "pool": secrets.pool_size(),
                  "module": secrets.__file__, "counts": counts() if counts else None, **answer}))
