#!/usr/bin/env python3
"""``govbridge demo grade|validate-oracle|extract-reads`` -- dispatched from ``govbridge/cli.py``."""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: govbridge demo {grade|validate-oracle|extract-reads} ...", file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "grade":
        from govbridge.demo import grade as grademod
        return grademod.main(rest)
    if cmd == "validate-oracle":
        from govbridge.demo import validate_oracle as vomod
        return vomod.main(rest)
    if cmd == "extract-reads":
        from govbridge.demo import extract_reads as ermod
        return ermod.main(rest)
    print(f"govbridge demo: unknown subcommand {cmd!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
