"""Held-out paths (W1-47, DEC-162, DEC-215, DEC-218): the list in ``governance/project/held-out.yaml``.

Moved from ``gov.guard.heldout`` when the guard was retired (EMERGENCY-2 6.1); the guard's rule that refused a call
naming a held-out path went with it. The step that wrote one ``Read`` deny rule per held-out path into the generated
settings (DEC-635) is retired too (W2-208, EMERGENCY-2 2.7: a hidden set is protected by the transcript scan, not by a
deny); ``gov update`` takes the lines it wrote out of a project's settings (``gov.update.core.legacy_lines``). No
message of this module carries a path.
"""

from __future__ import annotations

import os

# The duplicate-key YAML reader is ``gov.util.parts``'s: one source (W2-150 S6, DEC-1109 (2)).
from gov.util.parts import load_yaml_unique

CONFIG_REL = "governance/project/held-out.yaml"
CONFIG_KEY = "held_out_paths"
SETTINGS_REL = ".claude/settings.json"


class HeldOutError(Exception):
    """``held-out.yaml`` exists and is not of the stated shape (DEC-218)."""


def load_held_out(project_root: str) -> list[str]:
    """Return the held-out paths; ``[]`` when the project has no such file.

    A file that cannot be read, or that does not hold a non-empty list of
    absolute paths under ``held_out_paths``, raises ``HeldOutError``
    (DEC-218).
    """
    path = os.path.join(project_root, CONFIG_REL)
    if not os.path.lexists(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
        # W2-111 (DEC-1187): parsed once in the process for the same file and
        # text; a changed text is parsed again, and a file that refuses is not
        # kept (it refuses each time).  Each caller gets its own list.
        kept = _PARSED.get((path, text))
        if kept is not None:
            return list(kept)
        data = load_yaml_unique(text)
    except Exception:
        # The parser's own message may quote the file: fixed text only.
        raise HeldOutError(f"{CONFIG_REL} cannot be read") from None
    paths = data.get(CONFIG_KEY) if isinstance(data, dict) else None
    if not isinstance(paths, list) or not paths:
        raise HeldOutError(f"{CONFIG_REL} holds no list under {CONFIG_KEY}")
    for p in paths:
        if (not isinstance(p, str) or not p.startswith("/")
                or not p.rstrip("/") or "\n" in p):
            raise HeldOutError(
                f"{CONFIG_REL}: an entry of {CONFIG_KEY} is not an absolute path")
    kept = [p.rstrip("/") for p in paths]
    if len(_PARSED) >= _MOST_KEPT:
        _PARSED.clear()
    _PARSED[(path, text)] = kept
    return list(kept)


# W2-111 (DEC-1187): the held-out lists parsed in this process, by the file's
# path and text; in memory only, never on disk.
_PARSED: dict = {}
_MOST_KEPT = 16
