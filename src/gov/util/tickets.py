"""Where the ticket files live, the line reader of their front matter and the ticket loader (W2-150).

``TICKETS_REL`` moved from ``gov.tasks.tickets`` and ``_parse_frontmatter`` from ``gov.guard.decide``, both
unchanged (DEC-1039 (2), DEC-1109 (2)); ``_load_ticket`` moved from ``gov.guard.decide`` unchanged when the guard was
retired (EMERGENCY-2 6.1). The standard library only.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

TICKETS_REL = ".tickets"


def _parse_frontmatter(text: str) -> dict | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    result: dict = {}
    paths: list[str] = []
    in_paths = False
    for line in text[4:end].splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if re.match(r"^[a-zA-Z_][\w-]*:", line) and not line[0].isspace():
            in_paths = False
            key, _, val = line.partition(":")
            if key.strip() == "allowed_paths":
                in_paths = True
                continue
            result[key.strip()] = val.strip()
        elif in_paths and s.startswith("- "):
            e = s[2:].strip()
            if len(e) >= 2 and e[0] == e[-1] and e[0] in ("'", '"'):
                e = e[1:-1]
            paths.append(e)
        elif in_paths and not s.startswith("-"):
            in_paths = False
    result["allowed_paths"] = paths
    return result


def _load_ticket(root: str, tid: str) -> dict | None:
    """The front matter of the ticket ``tid`` names, by its file name (the ``tk`` id) or else by its ``wbs_id``;
    ``None`` when no ticket file gives it or it cannot be read."""
    if not tid or "/" in tid or os.sep in tid:
        return None
    d = Path(root) / TICKETS_REL
    if not d.is_dir():
        return None
    p = d / f"{tid}.md"
    if p.is_file():
        try:
            return _parse_frontmatter(p.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError):
            return None
    try:
        for p in sorted(d.glob("*.md")):
            if not p.is_file():
                continue
            try:
                fm = _parse_frontmatter(p.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                continue
            if fm and fm.get("wbs_id") == tid:
                return fm
    except OSError:
        pass
    return None
