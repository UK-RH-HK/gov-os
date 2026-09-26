#!/usr/bin/env python3
"""``govbridge cite ...`` / ``govbridge answers lint ...``, mirroring ``govbridge.notes.cli``'s/``govbridge.demo.
cli``'s own thin subcommand-dispatch shape. Wired from ``govbridge/cli.py`` (this node, R1-RA, is the LAST editor
in the RX -> GA1 -> RS -> RA sequence, REPAIR_DAG.yaml conventions.shared_files) with two dispatch lines:

    if cmd == "cite":
        from govbridge.answers import cli as answerscli
        return answerscli.main(["cite", *rest])
    if cmd == "answers":
        from govbridge.answers import cli as answerscli
        return answerscli.main(rest)

Also runnable directly: ``python -m govbridge.answers.cli cite <identifier>`` / ``... lint <answers> --packet DIR``.
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print("usage: govbridge {cite <identifier>|answers lint <answers> --packet DIR}", file=sys.stderr)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "cite":
        from govbridge.answers import cite as citemod
        return citemod.main(rest)
    if cmd == "lint":
        from govbridge.answers import lint as lintmod
        return lintmod.main(rest)
    print(f"govbridge: unknown subcommand {cmd!r} (expected cite|lint)", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
