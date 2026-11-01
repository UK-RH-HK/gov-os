"""The secrets stage of a cold rebuild, alone: the filter calls a rebuild makes, timed, for the tree in the current folder.

As `gov rebuild` makes them on a tree with no store: the lexical index asks `indexable` about every tracked file
(lexical._tracked); the code index asks `indexable` about `git ls-files --cached --others --exclude-standard`, then
`path_holds_secret` about each allowed path from a thread pool. Nothing is indexed or written but the filter's cache.
Prints one JSON line. Usage: python3 measure_filter.py <label>   (PYTHONPATH chooses the code under test)
"""

import json
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def main():
    label = sys.argv[1] if len(sys.argv) > 1 else "run"
    root = Path.cwd().resolve()
    import gov
    import gov.secrets as secrets
    from gov.retrieval import lexical

    counts = getattr(secrets, "scan_counts", None)
    before = counts() if counts else None
    load = os.getloadavg()
    started = time.monotonic()
    tracked = list(lexical._tracked(root))
    lex = secrets.indexable(root, tracked)
    lex_s = time.monotonic() - started
    listed = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
                            capture_output=True, text=True, check=True).stdout
    mid = time.monotonic()
    allowed = secrets.indexable(root, [rel for rel in listed.split("\0") if rel])
    with ThreadPoolExecutor() as pool:
        named = list(pool.map(lambda rel: secrets.path_holds_secret(root, rel), allowed))
    code_s = time.monotonic() - mid
    print(json.dumps({"label": label, "gov_file": gov.__file__, "files": len(tracked), "lexical_allowed": len(lex),
                      "codeintel_allowed": len(allowed), "names_with_secret": sum(named),
                      "secrets_s": round(time.monotonic() - started, 1), "lexical_part_s": round(lex_s, 1),
                      "codeintel_part_s": round(code_s, 1), "load_at_start": [round(x, 1) for x in load],
                      "load_at_end": [round(x, 1) for x in os.getloadavg()],
                      "counts": None if not counts else {kind: {k: v - before[kind][k] for k, v in each.items()}
                                                         for kind, each in counts().items()},
                      "cache": os.environ.get("GOV_SECRETS_CACHE")}))


if __name__ == "__main__":
    main()
