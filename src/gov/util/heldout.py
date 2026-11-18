"""Held-out paths (W1-47, DEC-162, DEC-215, DEC-218): the list in ``governance/project/held-out.yaml`` and the
``Read`` deny rules ``gov adapters`` writes from it into the generated settings (DEC-635).

Moved from ``gov.guard.heldout`` when the guard was retired (EMERGENCY-2 6.1); the guard's rule that refused a call
naming a held-out path went with it. No message of this module carries a path.
"""

from __future__ import annotations

import json
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


def write_read_rules(project_root: str, settings_path: str | None = None) -> int:
    """Write one ``Read`` deny rule per held-out path into a settings file
    and return how many were added.  Prints nothing (DEC-218)."""
    paths = load_held_out(project_root)
    if not paths:
        raise HeldOutError(f"{CONFIG_REL} does not exist")
    settings_path = settings_path or os.path.join(project_root, SETTINGS_REL)
    with open(settings_path, encoding="utf-8") as f:
        settings = json.load(f)
    deny = settings.setdefault("permissions", {}).setdefault("deny", [])
    added = 0
    for p in paths:
        rule = f"Read(/{p}/**)"  # //<path> is the absolute form in a rule
        if rule not in deny:
            deny.append(rule)
            added += 1
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(settings, indent=2) + "\n")
    return added


if __name__ == "__main__":
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    print(f"{write_read_rules(root)} Read deny rule(s) added to {SETTINGS_REL}")
