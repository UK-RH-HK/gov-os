"""``gov queue --dry-run``'s out folder (W2-206; L2 section 3, A6 S1), in the form ``gov close --verify`` wrote its
own, so ``gov wait <out>/verify.exit`` returns the dry run's exit code: ``select.json`` (the selection),
the run files (``parallel.xml``, ``serial.xml``: the selection's run on the merged result), ``summary.txt`` (one
line) and, last, ``verify.exit`` (the exit code and a newline, written whole: a temporary file moved into place).

The default folder is ``.gov-runtime/queue/dry/<T>/``, the tickets joined by ``+`` where there are several.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

DRY_DIR = ".gov-runtime/queue/dry"
RUN_FILES = ("parallel.xml", "serial.xml")
FILES = ("verify.exit", "verify.exit.tmp", "summary.txt", "select.json", *RUN_FILES)


def out_dir(root: Path, given: list[str], out: str | None) -> Path:
    """``--out`` (a relative one from the caller's folder), else the default folder of these tickets."""
    if out:
        path = Path(out)
        return path if path.is_absolute() else Path.cwd() / path
    names = [re.sub(r"[^A-Za-z0-9._-]", "_", g.partition("=")[0]) or "_" for g in given]
    return Path(root) / DRY_DIR / "+".join(names)


def selection_object(tickets: list[str], suites: list[str], options: list[str]) -> dict:
    """The selection as ``--select`` prints it: ``tickets``, and ``ticket`` too for one ticket (with ``suites`` and
    ``pytest_options``, ``gov close --select``'s object); ``suites``; ``pytest_options``."""
    named = {"ticket": tickets[0]} if len(tickets) == 1 else {}
    return {**named, "tickets": list(tickets), "suites": list(suites), "pytest_options": list(options)}


class Out:
    """The out folder of one dry run: an earlier run's files are removed first, so ``verify.exit`` is there only
    once this run ended."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.folder.mkdir(parents=True, exist_ok=True)
        for name in FILES:
            if (self.folder / name).exists():
                (self.folder / name).unlink()

    def selection(self, chosen: dict) -> None:
        (self.folder / "select.json").write_text(json.dumps(chosen) + "\n", encoding="utf-8")

    def runs(self, made: Path) -> None:
        """The run files of the run made in ``made``, where it wrote them."""
        for name in RUN_FILES:
            if (Path(made) / name).is_file():
                shutil.copyfile(Path(made) / name, self.folder / name)

    def finish(self, line: str, code: int) -> int:
        (self.folder / "summary.txt").write_text(line + "\n", encoding="utf-8")
        (self.folder / "verify.exit.tmp").write_text(f"{code}\n", encoding="utf-8")
        (self.folder / "verify.exit.tmp").replace(self.folder / "verify.exit")
        return code
