"""The registered hooks of a project (DEC-525).

``python3 -m gov.guard.hooks`` prints one JSON array: event, matcher and
command of every hook command in the project's settings file, in the
file's order.  A deny value inside a command is redacted, and so is a path
a deny rule carries, absolute or from the home folder (DEC-548, DEC-553);
nothing else of the file is printed, so no session opens the file for its
hooks.
"""

from __future__ import annotations

import json
import os
import re
import sys

from gov.guard.heldout import SETTINGS_REL

REDACTED = "[redacted]"
# A deny rule that carries an absolute path, Tool(//<path>), or one spelled
# from the home folder, Tool(~/<path>), and the path without its tail
# (DEC-548, DEC-553).
_PATH_RE = re.compile(r"\w+\(\s*([/~])(/[^*]*[^*/])(?:/\*\*|/)?\)\Z")


def _paths(deny: list[str]) -> set[str]:
    """The paths the deny rules carry.  One spelled from the home folder
    is held as written and with the home folder in its place (DEC-553)."""
    home = (os.environ.get("HOME") or "").rstrip("/")
    out: set[str] = set()
    for value in deny:
        m = _PATH_RE.match(value)
        if m and m.group(1) == "/":
            out.add(m.group(2))
        elif m:
            out.add("~" + m.group(2))
            if home:
                out.add(home + m.group(2))
    return out


def listing(settings) -> list[dict]:
    """One row per hook command of *settings*, a parsed settings file."""
    if not isinstance(settings, dict):
        return []
    permissions = settings.get("permissions")
    deny = permissions.get("deny") if isinstance(permissions, dict) else None
    deny = [d for d in deny if isinstance(d, str) and d] if isinstance(
        deny, list) else []
    # The longest path first: one may be the first characters of another.
    deny += sorted(_paths(deny), key=len, reverse=True)
    hooks = settings.get("hooks")
    rows: list[dict] = []
    for event, groups in (hooks.items() if isinstance(hooks, dict) else ()):
        for group in (groups if isinstance(groups, list) else ()):
            if not isinstance(group, dict):
                continue
            matcher = group.get("matcher")
            entries = group.get("hooks")
            for entry in (entries if isinstance(entries, list) else ()):
                command = entry.get("command") if isinstance(entry, dict) else None
                if not isinstance(command, str):
                    continue
                for value in deny:
                    command = command.replace(value, REDACTED)
                rows.append({"event": event,
                             "matcher": matcher if isinstance(matcher, str) else "",
                             "command": command})
    return rows


def main() -> int:
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    try:
        with open(os.path.join(root, SETTINGS_REL), encoding="utf-8") as f:
            settings = json.load(f)
    except Exception:
        # The parser's own message may quote the file: fixed text only.
        print(f"{SETTINGS_REL} cannot be read", file=sys.stderr)
        return 1
    print(json.dumps(listing(settings), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
