#!/usr/bin/env python3
"""``govbridge notes {validate|build} ...``, mirroring ``govbridge.demo.cli``'s subcommand dispatch shape.

Not yet wired into ``govbridge/cli.py``'s top-level dispatch table -- that file is edited in a fixed sequence by
other REPAIR-1 nodes (R1-RX -> R1-GA1 -> R1-RS -> R1-RA, REPAIR_DAG.yaml conventions.shared_files) and this node's
mutation_scope does not include it. The next editor in that sequence adds one dispatch line:

    if cmd == "notes":
        from govbridge.notes import cli as notescli
        return notescli.main(rest)

Until then, this module is runnable directly: ``python -m govbridge.notes.cli validate <file>``.
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: govbridge notes {validate|build} ...", file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "validate":
        from govbridge.notes import validate as validatemod
        return validatemod.main(rest)
    if cmd == "build":
        from govbridge.notes import build as buildmod
        return buildmod.main(rest)
    print(f"govbridge notes: unknown subcommand {cmd!r}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
