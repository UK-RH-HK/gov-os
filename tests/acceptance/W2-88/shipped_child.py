"""A child process for S24 (``test_w2_88_p1_installed.py``): ask ``gov.adopt.fabric.shipped(rel, root)`` for a shipped file and print what it
answered (or how it refused) as one JSON line on stdout.

    python shipped_child.py <rel: the path in the Gov OS repository> <root: the adopted repository>

The ``gov`` it imports is the one the child's own environment finds: the worktree's (``PYTHONPATH`` set), a relocated source tree's, or a
wheel's in a venv (no ``PYTHONPATH``). It prints ``gov.__file__`` so the case knows which.
"""

import json
import sys
from pathlib import Path

rel, root = sys.argv[1], Path(sys.argv[2])
out = {}
try:
    import gov

    out["gov_file"] = gov.__file__
    from gov.adopt import fabric

    path = fabric.shipped(rel, root)
    out.update(ok=True, path=str(path), exists=Path(path).exists())
except BaseException as exc:  # noqa: BLE001: the case judges what came out
    out.update(ok=False, type=type(exc).__name__, code=getattr(exc, "code", None), message=getattr(exc, "message", str(exc)),
               details=getattr(exc, "details", None))
print(json.dumps(out, default=str))
