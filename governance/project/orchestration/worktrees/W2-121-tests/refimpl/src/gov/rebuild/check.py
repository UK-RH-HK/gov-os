"""Recovery-rebuild check (CAP-38.b): current store digest must match a clean rebuild."""

import os
import shutil
import sys
import tempfile
from pathlib import Path


def main():
    root = Path.cwd()
    store_path = root / ".gov-runtime" / "store.db"

    if not store_path.is_file():
        print("unmeasured", file=sys.stderr)
        sys.exit(1)

    from gov.store import digest as get_digest, load as store_load

    current = get_digest(root)

    tmpdir = tempfile.mkdtemp(prefix="gov-check-")
    try:
        os.symlink(str(root / ".git"), os.path.join(tmpdir, ".git"))
        result = store_load(Path(tmpdir))
        rebuilt = result["digest"]
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    if current != rebuilt:
        print(f"mismatch: current={current} rebuilt={rebuilt}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
