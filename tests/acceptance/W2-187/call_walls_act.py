"""Calls A9's ``memory_sets.walls_act`` as a library function in a child process (this tree's ``src/`` first).

``python3 call_walls_act.py <out> <sets_root> <audit> [<repo>]``: prints the ACT.md path it wrote.
"""
import sys
from pathlib import Path

from gov.adopt import memory_sets

GOV_OS = Path(memory_sets.__file__).resolve().parents[3]


def main(argv):
    out, sets_root, audit = Path(argv[0]), argv[1], argv[2]
    made = memory_sets.variants(GOV_OS / memory_sets.BRIEFS, {}, [])
    extra = {"repo": argv[3]} if len(argv) > 3 else {}
    act = memory_sets.walls_act(out, sets_root=sets_root, audit=audit, made=made, blind=["x/**"], **extra)
    print(act / "ACT.md")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
