"""Where the ticket files live and the guard's line reader of their front matter (W2-150).

``TICKETS_REL`` moved from ``gov.tasks.tickets`` and ``_parse_frontmatter`` from ``gov.guard.decide``, both
unchanged (DEC-1039 (2), DEC-1109 (2)); the old modules import them from here. The standard library only: the guard's
hook imports this module on every call.
"""

from __future__ import annotations

import re

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
