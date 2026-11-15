"""A child process for S27 (``test_w2_88_scan_speed.py``): judge a list of paths with ``gov.secrets.indexable`` from the ``gov`` that
sits in the folder given first (the code of the base, a ``git archive`` of ``src`` made by the case, or this worktree's), and print what
it returned and how long it took as one JSON line on stdout.

    python scan_driver.py <src folder> <root> <file holding the JSON list of paths> [<path of a file to write the pool size to>]

Nothing here knows a secret's value: the planted files are made by the case and the answer is a list of paths.
"""

import json
import sys
import time
from pathlib import Path

src, root, listing = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
sys.path.insert(0, src)

import gov.secrets as secrets  # noqa: E402

paths = json.loads(listing.read_text(encoding="utf-8"))
began = time.perf_counter()
kept = secrets.indexable(root, paths)
seconds = time.perf_counter() - began
print(json.dumps({"kept": list(kept), "seconds": seconds, "judged": len(paths), "pool": secrets.pool_size(),
                  "module": secrets.__file__}))
