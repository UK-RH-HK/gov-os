"""Park or unpark the merge queue's approvals (DEC-1037 (5)): an emergency stop parks them with the dispatcher's lists.

    python3 queue_park.py park [--keep W2-x ...] [--queue DIR]   approved/*.json -> parked-by-emergency/ (but --keep)
    python3 queue_park.py unpark [--queue DIR]                    parked-by-emergency/*.json -> approved/
    python3 queue_park.py list [--queue DIR]

Moves files only (never deletes); an entry already at the destination is left where it is and named. land.py refuses
a landing while the queue holds an approval it was not given, so a parked or stray approval never rides along."""
import argparse
import os
import sys
from pathlib import Path

QUEUE = Path(os.environ.get("LAND_ROOT", "/home/usain/Dynamic-Agentic-Engineering-OS")) / \
    ".gov-runtime/scratch/orchestrator/merge-queue"
PARKED = "parked-by-emergency"


def move(src, dst, keep=()):
    dst.mkdir(exist_ok=True)
    moved, clashed = [], []
    for p in sorted(src.glob("*.json")) if src.is_dir() else []:
        if p.stem in keep:
            continue
        if (dst / p.name).exists():
            clashed.append(p.stem)
            continue
        p.rename(dst / p.name)
        moved.append(p.stem)
    return moved, clashed


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["park", "unpark", "list"])
    ap.add_argument("--keep", nargs="*", default=[])
    ap.add_argument("--queue", default=str(QUEUE))
    a = ap.parse_args(argv)
    q = Path(a.queue)
    if a.action == "list":
        for d in ("approved", PARKED):
            print(f"{d}: {', '.join(sorted(p.stem for p in (q / d).glob('*.json'))) or '-'}")
        return 0
    src, dst = (q / "approved", q / PARKED) if a.action == "park" else (q / PARKED, q / "approved")
    moved, clashed = move(src, dst, set(a.keep) if a.action == "park" else set())
    print(f"{a.action}ed: {', '.join(moved) or '-'}")
    if clashed:
        print(f"left in {src.name} (already in {dst.name}): {', '.join(clashed)}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
