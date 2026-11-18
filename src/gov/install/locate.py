"""The git common dir of the repository holding a folder, found without a subprocess (W2-18).

Walking up from the folder, the first ``.git`` decides: a folder is the git dir (its ``commondir`` file, where there is
one, names the common dir relative to it); a file says ``gitdir: <path>`` (relative to the file's folder), and that
git dir's ``commondir`` file names the common dir (a linked worktree). The answer is a real absolute path.
"""

from __future__ import annotations

import os
from pathlib import Path

PIN_REL = "gov"


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read().strip()
    except (OSError, UnicodeDecodeError):
        return None


def _common_of(git_dir: str) -> str:
    named = _read(os.path.join(git_dir, "commondir"))
    return os.path.join(git_dir, named) if named else git_dir


def common_dir(start) -> Path | None:
    """The git common dir of the repository holding ``start``, or ``None`` outside any repository."""
    folder = os.path.abspath(os.fspath(start))
    while True:
        dot = os.path.join(folder, ".git")
        if os.path.isdir(dot):
            return Path(os.path.realpath(_common_of(dot)))
        if os.path.isfile(dot):
            text = _read(dot) or ""
            if text.startswith("gitdir:"):
                git_dir = os.path.join(folder, text[len("gitdir:"):].strip())
                return Path(os.path.realpath(_common_of(git_dir)))
            return None
        parent = os.path.dirname(folder)
        if parent == folder:
            return None
        folder = parent


def pin_root(common) -> Path:
    """``<common>/gov``: the pin's folder."""
    return Path(common) / PIN_REL
