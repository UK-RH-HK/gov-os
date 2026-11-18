"""The ``allowed_paths`` grammar and the shell-glob test, shared by the close, the plan and memory (W2-150).

Moved from ``gov.guard.decide`` unchanged (DEC-1039 (2), DEC-1109 (2)), so that the record store can classify a
commit's paths without importing the guard; ``ACCEPTANCE`` and ``_is_under_acceptance`` followed when the guard was
retired (EMERGENCY-2 6.1). The standard library only.
"""

from __future__ import annotations

import re

ACCEPTANCE = "tests/acceptance"


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


def _is_under_acceptance(relpath: str) -> bool:
    """True when *relpath* is the acceptance-test folder or lies in it."""
    return relpath == ACCEPTANCE or relpath.startswith(ACCEPTANCE + "/")
