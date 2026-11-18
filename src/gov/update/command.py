"""``gov update <version>`` (W2-17, DAEO-sdhj) as a command module; the convention is in ``gov.cli.main``.

Moves the adopted project to release ``<version>`` (``gov.update.core``). ``--check`` prints the whole plan and
writes nothing. Refused before anything is written: ``UPDATE_REFUSED`` with ``details.reason`` (``not_adopted``,
``same``, ``dirty``, ``no_release``, ``manifest``, ``files``, ``wheel``, ``old_release``); a failed step rolls back:
``UPDATE_FAILED`` with ``details.step`` and ``details.rolled_back``; a failed store refresh after the commit:
``UPDATE_STORE_FAILED`` (the update stays applied).
"""

from __future__ import annotations

from pathlib import Path

HELP = "update the adopted project to a newer release (--check: show the plan, change nothing)"
CLASS = "act"


def add_arguments(parser) -> None:
    parser.add_argument("version", help="the release to update to (its tag is v<version> in the source)")
    parser.add_argument("--check", action="store_true", help="print the plan and stop: nothing is written")
    parser.add_argument("--source", metavar="<path>", help="the Gov OS source (default: _src_path of "
                                                           ".copier-answers.yml)")
    parser.add_argument("--wheel", metavar="<file>", help="the release's wheel (default: built from the release "
                                                          "commit as gov release builds it)")


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.update import core
    try:
        return core.update(Path(root), args.version, check=args.check, source=args.source, wheel=args.wheel)
    except core.UpdateRefused as exc:
        raise GovError("UPDATE_REFUSED", str(exc), {"reason": exc.reason}) from None
    except core.UpdateFailed as exc:
        raise GovError("UPDATE_FAILED", str(exc), {"step": exc.step, "rolled_back": exc.rolled_back}) from None
    except core.StoreFailed as exc:
        raise GovError("UPDATE_STORE_FAILED", str(exc), {"report": exc.report}) from None
