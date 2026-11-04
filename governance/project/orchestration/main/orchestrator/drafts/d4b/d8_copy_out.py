#!/usr/bin/env python3
"""D-8 step 1 (DEC-1055, G-3): copy the memory measure's hidden half to a sets root outside every worktree.

Prints counts and one combined sha256 only, never a question, answer or gold path. Idempotent: an existing copy is
verified, never overwritten with different bytes (refuses instead).
    d8_copy_out.py <source hidden dir> <dest sets root>
The dest gets governance/project/path-map.yaml (a stub holding only the set's evaluation_sets entry) and
fixtures/evaluation/memory-retrieval/hidden/. The visible part is copied from the measured head at each measure.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

STUB = """# The memory measure's sets root outside every worktree (DEC-1055, DEC-1052 G-3). Only measure.py reads it.
evaluation_sets:
  memory-retrieval:
    visible: ["docs/assessment/2026-10/B-memory-retrieval.md"]
    hidden: ["fixtures/evaluation/memory-retrieval/hidden/**"]
    measures:
      roles: [engineer, research]
"""


def digest(files):
    h = hashlib.sha256()
    for f in files:
        h.update(f.name.encode() + b"\0" + hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def main(src, dest):
    src, dest = Path(src), Path(dest)
    files = sorted(src.glob("*.yaml"))
    out = dest / "fixtures/evaluation/memory-retrieval/hidden"
    out.mkdir(parents=True, exist_ok=True)
    os.chmod(dest, 0o700)
    stub = dest / "governance/project/path-map.yaml"
    stub.parent.mkdir(parents=True, exist_ok=True)
    stub.write_text(STUB)
    for f in files:
        t = out / f.name
        if t.exists():
            if t.read_bytes() != f.read_bytes():
                print(f"REFUSED: an existing copy differs ({f.name[:1]}…)")
                return 1
        else:
            shutil.copy2(f, t)
    copied = sorted(out.glob("*.yaml"))
    same = digest(files) == digest(copied) and len(files) == len(copied)
    print(f"source files: {len(files)}; copied files: {len(copied)}; identical: {same}; sha256: {digest(copied)}")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
