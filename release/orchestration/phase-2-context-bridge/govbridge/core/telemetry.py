"""The local telemetry writer (ARCHITECTURE.md section 8.3). Local rows go to
``$GOV_BRIDGE_HOME/telemetry/<kind>.jsonl`` (kind in {builds, packets, receipts, queries, coverage}); a later stage
(node I1) commits selected rows into ``release/orchestration/phase-2-context-bridge/telemetry/index/*.jsonl``. This
module only writes the local rows -- it never writes into the committed domain, and it is the only writer of
``llm_invocations`` (always 0 for anything core builds, since no step here invokes a model).
"""
from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from govbridge.core.store import gov_bridge_home
from govbridge.core.yamlutil import canonical_json, sha256_text

VALID_KINDS = {"builds", "packets", "receipts", "queries", "coverage"}


def telemetry_dir() -> Path:
    d = gov_bridge_home() / "telemetry"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_row(kind: str, row: dict[str, Any]) -> Path:
    if kind not in VALID_KINDS:
        raise ValueError(f"unknown telemetry kind {kind!r}; expected one of {sorted(VALID_KINDS)}")
    path = telemetry_dir() / f"{kind}.jsonl"
    record = dict(row)
    record.setdefault("written_at", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    line = json.dumps(record, sort_keys=True)
    fd = os.open(str(path), os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o644)
    try:
        os.write(fd, (line + "\n").encode("utf-8"))
    finally:
        os.close(fd)
    return path


def build_id(manifest_sha256: str, trigger: str) -> str:
    return sha256_text(canonical_json({"manifest_sha256": manifest_sha256, "trigger": trigger,
                                        "t": time.time_ns()}))[:16]


def read_rows(kind: str) -> list[dict]:
    path = telemetry_dir() / f"{kind}.jsonl"
    if not path.exists():
        return []
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out
