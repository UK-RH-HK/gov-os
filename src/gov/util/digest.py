"""The SHA-256 digests the Gov OS records, as hexadecimal text (DEC-1039 (2), P1-6; INVENTORY-TESTS-CODE-1 §6b item 5)."""

from __future__ import annotations

import hashlib
from pathlib import Path


def sha256(data: bytes) -> str:
    """The SHA-256 of ``data``."""
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str | None:
    """The SHA-256 of the file ``path``'s bytes; None when it cannot be read."""
    try:
        return sha256(Path(path).read_bytes())
    except OSError:
        return None
