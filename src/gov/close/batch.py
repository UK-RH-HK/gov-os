"""Batched closes (W2-68; DEC-883 items 1 to 3, DEC-889 items 2 and 4, DEC-890): ``python3 -m gov.close.batch``.

- ``refresh --root <project>``: the incremental record load at ``HEAD`` (``gov.store.load_records``). It exits 0
  when the store is fresh at ``HEAD`` after the load (``gov.close.repo.store_is_of_head``), and 1 with the error's
  code otherwise: ``STORE_CODE_CHANGED`` where the store was built on other code (a full rebuild is needed),
  ``STORE_STALE`` where the load left it stale.

The design is ``docs/research/W2-68-batched-close.md``. Each answer is the API-0002 envelope, as
``gov.close.nightly`` gives it.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from gov.cli.errors import GovError
from gov.close.repo import git as _git, store_is_of_head as _store_is_of_head

COMMAND = "batch"


def refresh(root: Path) -> dict:
    """The incremental record load at ``HEAD``; ``STORE_STALE`` where the store is not fresh at ``HEAD`` after it."""
    from gov.store import load_records

    root = Path(root)
    loaded = load_records(root)
    if _store_is_of_head(root) is not True:
        raise GovError("STORE_STALE", "the record store is not of HEAD after the record load; run gov rebuild",
                       {"head": _git(root, "rev-parse", "HEAD").strip(), "load": loaded})
    return {"load": loaded, "fresh": True}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python3 -m gov.close.batch", description=__doc__.split("\n")[0])
    commands = parser.add_subparsers(dest="action", required=True)
    action = commands.add_parser("refresh", help="the incremental record load at HEAD")
    action.add_argument("--root", default=".")
    action.add_argument("--json", action="store_true")
    action.add_argument("--session", default="")
    args = parser.parse_args(argv)
    try:
        result = refresh(Path(args.root))
    except GovError as error:
        envelope = {"ok": False, "command": COMMAND, "result": {}, "session": args.session,
                    "error": {"code": error.code, "message": error.message, "details": error.details}}
        print(json.dumps(envelope) if args.json else f"{COMMAND}: {error.code}: {error.message}")
        return error.exit_code
    envelope = {"ok": True, "command": COMMAND, "result": result, "session": args.session}
    print(json.dumps(envelope) if args.json else json.dumps(envelope, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
