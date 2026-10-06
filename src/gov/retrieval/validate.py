"""Evidence-bundle validator (W1-22, CAP-57.a)."""
from __future__ import annotations

import hashlib
from pathlib import Path

REASONS = frozenset({
    "CLOSURE_COMPLETE", "SATURATED", "DEPTH_LIMIT_REACHED",
    "BUDGET_EXHAUSTED_WITH_GAPS", "FACET_UNAVAILABLE", "UNRESOLVED_IDS",
})


def validate(root: Path, bundle: dict) -> dict:
    root, errors = Path(root), []
    reason = bundle.get("stopping_reason")
    if reason is None:
        errors.append({"code": "MISSING_STOPPING_REASON",
                       "message": "bundle has no stopping_reason"})
    elif reason not in REASONS:
        errors.append({"code": "INVALID_STOPPING_REASON",
                       "message": f"stopping_reason {reason!r} is not one of the six fixed reasons"})
    for i, item in enumerate(bundle.get("evidence", [])):
        rel = item.get("path", "")
        target = root / rel
        if not target.is_file():
            errors.append({"code": "FILE_NOT_FOUND",
                           "message": f"evidence[{i}]: {rel} does not exist under root",
                           "index": i, "path": rel})
            continue
        lines = target.read_bytes().splitlines(keepends=True)
        start, end = item.get("start_line", 1), item.get("end_line", len(lines))
        if start < 1 or end > len(lines) or start > end:
            span = b""
        else:
            span = b"".join(lines[start - 1:end])
        if item.get("sha256") != hashlib.sha256(span).hexdigest():
            errors.append({"code": "HASH_MISMATCH",
                           "message": f"evidence[{i}]: sha256 does not match the cited span",
                           "index": i, "path": rel})
        text = item.get("text", "")
        if text and text not in span.decode("utf-8", "replace"):
            errors.append({"code": "TEXT_NOT_FOUND",
                           "message": f"evidence[{i}]: quoted text not found in the cited lines",
                           "index": i, "path": rel})
    return {"valid": not errors, "errors": errors}
