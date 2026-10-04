"""Support code for the W1-18 acceptance tests (standard library only).

W1-18 builds the on-demand lifecycle of the stack's only daemon (Ollama) and the
lexical fallback. The module has no ``gov`` command yet (W1-19 and W1-21 consume
it), and its sources do not fix its public interface: see the decision package in
``README.md``. This first batch therefore holds only what needs no interface:

- **Where the module lives.** The ticket's ``allowed_paths`` give
  ``src/gov/retrieval/ollama*``; nothing else is assumed about it.
- **Unit files.** The repository is asked, through ``git ls-files`` with three
  pathspecs, for service, socket and timer units, tracked or untracked and not
  ignored. No other file is listed or read.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
MODULE_DIR_REL = "src/gov/retrieval"
MODULE_GLOB = "ollama*"
# An always-on daemon on this stack would be a systemd unit (the registry row: "run on demand, no systemd unit").
UNIT_PATHSPECS = ("*.service", "*.socket", "*.timer")


class ModuleMissing(AssertionError):
    """The Ollama lifecycle module does not exist yet."""


def module_paths(root=REPO_ROOT):
    """What the ticket's ``allowed_paths`` pattern matches in the source tree, bytecode left out."""
    found = sorted(path for path in (Path(root) / MODULE_DIR_REL).glob(MODULE_GLOB) if path.name != "__pycache__")
    if not found:
        raise ModuleMissing(
            f"the Ollama lifecycle module does not exist: nothing matches {MODULE_DIR_REL}/{MODULE_GLOB}")
    return found


def unit_files(root=REPO_ROOT):
    """Service, socket and timer units in the working tree (tracked, or untracked and not ignored)."""
    listing = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard", "--",
         *UNIT_PATHSPECS],
        capture_output=True, text=True, check=True,
    ).stdout
    return sorted(Path(root) / rel for rel in listing.split("\0") if rel)


def mentions_ollama(path):
    """True when the unit's name or its text names Ollama."""
    if "ollama" in path.name.lower():
        return True
    if not path.is_file():
        return False
    return "ollama" in path.read_text(encoding="utf-8", errors="replace").lower()
