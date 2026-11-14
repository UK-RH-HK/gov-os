"""Every `gov links --all` finding of <repo>'s HEAD, as JSON, without writing the mark. Read-only.

    python3 findings.py <repo> <out.json>

Uses <repo>/src's gov.links.check (byte-identical to the pinned wheel's on 2026-11-08) exactly as `gov links --all`
does: check.findings(repo, None) judges every commit. Prints the counts by code and role, as gov links' first line.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(ROOT / "src"))
from gov.links import check  # noqa: E402

repo = check._Repo(ROOT)
found, commits = check.findings(repo, None)
by = collections.Counter((f["code"], f["role"]) for f in found)
Path(sys.argv[2]).write_text(json.dumps({"counts": {f"{c} {r}": n for (c, r), n in sorted(by.items())},
                                         "total": len(found), "findings": found}, indent=1, default=str))
print(f"{len(found)} findings: " + ", ".join(f"{c} {r} {n}" for (c, r), n in sorted(by.items())))
