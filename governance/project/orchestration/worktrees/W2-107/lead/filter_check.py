"""Whether the pre-index filter lets the given project-relative paths through (no cache): prints each path's verdict."""
import os
import sys
from pathlib import Path

os.environ["GOV_SECRETS_CACHE"] = ""
from gov.secrets import indexable  # noqa: E402

root = Path("/home/usain/gov-os-worktrees/W2-107")
allowed = set(indexable(root, sys.argv[1:]))
for rel in sys.argv[1:]:
    print(rel, "let through" if rel in allowed else "LEFT OUT")
