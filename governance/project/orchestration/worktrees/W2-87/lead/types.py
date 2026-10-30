"""Lead's look at the store: record types, statuses and paths shared by several records (W2-87 design)."""
import collections
import sys
from pathlib import Path

sys.path.insert(0, "/home/usain/gov-os-worktrees/W2-87/src")
from gov import records  # noqa: E402

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/usain/gov-os-worktrees/W2-87")
known = records.records(root)
print(collections.Counter((r["type"], r["status"]) for r in known).most_common(40))
paths = collections.Counter(r["path"] for r in known)
print([(p, n) for p, n in paths.items() if n > 1])
last = {r["path"]: r["id"] for r in known}
print("register maps to", last.get("docs/DECISION_REGISTER.md"))
