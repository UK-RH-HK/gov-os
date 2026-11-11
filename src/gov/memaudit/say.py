"""The only printer of the memory audit's tools (Interface section 1; S5, F1).

A line holds ids, counts, codes and digests only. ``say`` refuses, before anything is printed, a line that holds the
sets root's path followed by a slash or one of the folder words below, and prints in its place the fixed refusal; the
subcommand then exits 4. Standard error, when a line goes there too, carries the same single line.
"""

from __future__ import annotations

import os
import sys

REFUSAL = "REFUSED: a line that names a sets-root folder was not printed"
FOLDER_WORDS = ("fixtures/", "runs/", "indep-walls/", "hidden")


def _roots(sets_root) -> list[str]:
    if sets_root is None:
        return []
    given = os.path.abspath(os.path.expanduser(str(sets_root)))
    return list(dict.fromkeys([os.path.realpath(given), given]))


def refused(line: str, sets_root=None) -> bool:
    """Whether ``line`` names a sets-root folder."""
    if any(word in line for word in FOLDER_WORDS):
        return True
    return any(root.rstrip("/") + "/" in line for root in _roots(sets_root))


def _write(text: str, err: bool) -> None:
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
    if err:
        sys.stderr.write(text + "\n")
        sys.stderr.flush()


def say(line, sets_root=None, *, err: bool = False) -> tuple[str, dict]:
    """Print the one ``line`` (on standard error too when ``err``); ``("ok", {"printed": 1, "refused": 0})``. A line
    that names a sets-root folder is not printed: the refusal is printed on both streams and the word is ``usage``
    (the subcommand's exit 4)."""
    text = str(line)
    if "\n" in text or "\r" in text or refused(text, sets_root):
        _write(REFUSAL, True)
        return "usage", {"printed": 0, "refused": 1}
    _write(text, err)
    return "ok", {"printed": 1, "refused": 0}
