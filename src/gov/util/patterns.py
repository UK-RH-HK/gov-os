"""The ``allowed_paths`` grammar and the shell-glob test, shared by the guard, the close and memory (W2-150).

Moved from ``gov.guard.decide`` unchanged (DEC-1039 (2), DEC-1109 (2)), so that the record store can classify a
commit's paths without importing the guard; ``gov.guard.decide`` imports both names from here. The standard library
only: the guard's hook imports this module on every call.
"""

from __future__ import annotations

import re


def _match_pattern(relpath: str, pattern: str) -> bool:
    parts = pattern.split("**")
    segs = [re.escape(p).replace(r"\*", "[^/]*") for p in parts]
    rx = "^" + ".*".join(segs)
    if pattern.endswith("**"):
        rx += ".*"
    return bool(re.match(rx + "$", relpath))


def _has_glob(s: str) -> bool:
    """True when *s* contains shell glob characters."""
    return '*' in s or '?' in s or '[' in s
