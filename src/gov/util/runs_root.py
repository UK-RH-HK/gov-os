"""The durable scratch root ``~/gov-os-runs`` (W2-50, DEC-728; moved here by W2-150).

Moved from ``gov.guard.runs`` unchanged (DEC-1039 (2)), so that the secrets scan can name the root without importing
the guard; ``gov.guard.runs`` imports both names from here. The standard library only.
"""

from __future__ import annotations

import os

ROOT_NAME = "gov-os-runs"


def root() -> str | None:
    """The real path of ``~/gov-os-runs`` in the session's home, which need not exist; ``None`` without a home."""
    home = os.path.expanduser("~")
    if not os.path.isabs(home):
        return None
    return os.path.join(os.path.realpath(home), ROOT_NAME)
