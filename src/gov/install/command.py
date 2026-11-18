"""``gov install <version>`` (W2-18, DAEO-057v) as a command module; the convention is in ``gov.cli.main``.

Installs a hash-verified release's gov into the repository's own pinned environment, ``<common>/gov/``
(``gov.install.pin``). Refused: ``INSTALL_REFUSED`` with ``details.reason`` (``no_release``, ``manifest``, ``wheel``,
``environment``), and ``<common>/gov/`` left as it was.
"""

from __future__ import annotations

from pathlib import Path

HELP = "install a release's gov, hash-verified, as the repository's pinned gov (<git common dir>/gov/)"
CLASS = "act"


def add_arguments(parser) -> None:
    parser.add_argument("version", help="the release to install (its tag is v<version> in the source)")
    parser.add_argument("--source", metavar="<path>", help="the Gov OS source (default: _src_path of "
                                                           ".copier-answers.yml)")
    parser.add_argument("--wheel", metavar="<file>", help="the release's wheel (default: built from the release "
                                                          "commit as gov release builds it)")


def run(root: Path, args, config: dict) -> dict:
    from gov.cli.errors import GovError
    from gov.install import pin
    try:
        return pin.install(Path(root), args.version, source=args.source, wheel=args.wheel)
    except pin.InstallRefused as exc:
        raise GovError("INSTALL_REFUSED", str(exc), {"reason": exc.reason}) from None
