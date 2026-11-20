"""``gov update <version>`` (W2-17, DAEO-sdhj) as a command module; the convention is in ``gov.cli.main``.

Moves the adopted project to release ``<version>`` (``gov.update.core``). ``--check`` prints the whole plan and
writes nothing. Refused before anything is written: ``UPDATE_REFUSED`` with ``details.reason`` (``not_adopted``,
``same``, ``dirty``, ``no_release``, ``manifest``, ``files``, ``wheel``, ``old_release``); a failed step rolls back:
``UPDATE_FAILED`` with ``details.step`` and ``details.rolled_back``; a failed store refresh after the commit:
``UPDATE_STORE_FAILED`` (the update stays applied). ``--rollback`` (W2-17 fix S7) undoes the last update: refused
(``usage``, ``no_update``, ``dirty``, ``no_previous_pin``, ``rollback_conflict``), failed (``UPDATE_FAILED``, rolled
back) or the store not rebuilt (``UPDATE_STORE_FAILED``, the rollback stays).
"""

from __future__ import annotations

from pathlib import Path

HELP = "update the adopted project to a newer release (--check: show the plan, change nothing)"
CLASS = "act"


def add_arguments(parser) -> None:
    parser.add_argument("version", nargs="?", help="the release to update to (its tag is v<version> in the source)")
    parser.add_argument("--rollback", action="store_true",
                        help="undo the update the lock's release came by: one revert commit, the pin back (no version)")
    parser.add_argument("--check", action="store_true", help="print the plan and stop: nothing is written")
    parser.add_argument("--source", metavar="<path>", help="the Gov OS source (default: _src_path of "
                                                           ".copier-answers.yml)")
    parser.add_argument("--wheel", metavar="<file>", help="the release's wheel (default: built from the release "
                                                          "commit as gov release builds it)")


def _usage(args) -> str | None:
    if args.rollback:
        if args.version:
            return "gov update --rollback takes no version: it undoes the update the lock's release came by"
        given = [flag for flag, value in (("--check", args.check), ("--source", args.source),
                                          ("--wheel", args.wheel)) if value]
        if given:
            return f"gov update --rollback takes no {', '.join(given)}"
        return None
    if not args.version:
        return "gov update needs the release to update to (gov update <version>), or --rollback"
    return None


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.update import core
    usage = _usage(args)
    if usage:
        raise GovError("UPDATE_REFUSED", usage, {"reason": "usage"})
    try:
        if args.rollback:
            return core.rollback(Path(root))
        return core.update(Path(root), args.version, check=args.check, source=args.source, wheel=args.wheel)
    except core.UpdateRefused as exc:
        raise GovError("UPDATE_REFUSED", str(exc), {"reason": exc.reason}) from None
    except core.UpdateFailed as exc:
        raise GovError("UPDATE_FAILED", str(exc), {"step": exc.step, "rolled_back": exc.rolled_back}) from None
    except core.StoreFailed as exc:
        raise GovError("UPDATE_STORE_FAILED", str(exc), {"report": exc.report}) from None
