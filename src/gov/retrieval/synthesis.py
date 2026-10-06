"""Hierarchical synthesis notes (W1-23, CAP-15.f, DEC-080).

Deterministic, cited, hash-checked synthesis notes derived from evidence.
No model calls. Notes group evidence by directory, cite source ids and
sha256 hashes, and disclose unresolved evidence (gaps).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

TOKEN_CHARS = 4
NOTES_REL = Path(".gov-runtime") / "synthesis" / "notes.json"


def _tokens(text: str) -> int:
    return -(-len(text) // TOKEN_CHARS)


def synthesize(root, evidence, budget, *, gaps=None) -> dict:
    root = Path(root)

    file_hashes: dict[str, str] = {}
    for item in evidence:
        rel = item["path"]
        if rel not in file_hashes:
            file_hashes[rel] = hashlib.sha256((root / rel).read_bytes()).hexdigest()

    groups: dict[str, list] = {}
    for item in evidence:
        parent = str(Path(item["path"]).parent)
        groups.setdefault(parent, []).append(item)

    notes = []
    for group_name in sorted(groups):
        citations = []
        for item in groups[group_name]:
            citations.append({
                "source_id": item["id"],
                "source_sha256": item["sha256"],
                "file_sha256": file_hashes[item["path"]],
                "path": item["path"],
                "start_line": item["start_line"],
                "end_line": item["end_line"],
            })
        citations.sort(key=lambda c: (c["path"], c["start_line"], c["end_line"], c["source_id"]))
        notes.append({"group": group_name, "citations": citations})

    unresolved = []
    if gaps:
        for gap in gaps:
            unresolved.append({"id": gap["id"], "reason": gap["reason"]})

    result = {"notes": notes, "unresolved": unresolved}

    notes_path = root / NOTES_REL
    notes_path.parent.mkdir(parents=True, exist_ok=True)
    notes_path.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    return result


def validate_notes(root) -> dict:
    root = Path(root)
    notes_path = root / NOTES_REL

    if not notes_path.is_file():
        return {"valid": False, "errors": [{"source_id": "",
                                             "code": "NOTES_NOT_FOUND",
                                             "message": "no synthesis notes found"}]}

    data = json.loads(notes_path.read_text(encoding="utf-8"))
    errors = []

    for group in data.get("notes", []):
        for citation in group.get("citations", []):
            source_id = citation["source_id"]
            rel = citation["path"]
            path = root / rel

            if not path.is_file():
                errors.append({"source_id": source_id, "code": "FILE_NOT_FOUND",
                               "message": f"cited file {rel} does not exist"})
                continue

            file_bytes = path.read_bytes()

            if "file_sha256" in citation:
                actual_file = hashlib.sha256(file_bytes).hexdigest()
                if actual_file != citation["file_sha256"]:
                    errors.append({"source_id": source_id, "code": "HASH_MISMATCH",
                                   "message": f"file hash mismatch for {source_id}"})
                    continue

            lines = file_bytes.splitlines(keepends=True)
            start, end = citation["start_line"], citation["end_line"]

            if start < 1 or end > len(lines) or start > end:
                errors.append({"source_id": source_id, "code": "OUT_OF_RANGE",
                               "message": f"line range {start}-{end} out of bounds"})
                continue

            span = b"".join(lines[start - 1:end])
            actual = hashlib.sha256(span).hexdigest()

            if actual != citation["source_sha256"]:
                errors.append({"source_id": source_id, "code": "HASH_MISMATCH",
                               "message": f"sha256 mismatch for {source_id}"})

    return {"valid": not errors, "errors": errors}
