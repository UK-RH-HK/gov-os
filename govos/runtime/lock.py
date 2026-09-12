"""framework.lock: exact installed release/version/hash."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from govos import CLI_VERSION, FRAMEWORK_NAME
from govos.runtime.kernel import manifest_hash
from govos.runtime.util import GovError, now_iso, read_yaml, write_yaml

LOCK_SCHEMA_VERSION = "1.0.0"


def write_lock(path: Path, manifest: dict[str, Any], source: str, release_commit: str | None = None) -> dict[str, Any]:
    lock = {
        "framework": FRAMEWORK_NAME,
        "version": manifest["version"],
        "release_commit": release_commit or "unknown",
        "release_hash": manifest["payload_hash"],
        "source": source,
        "installed_at": now_iso(),
        "kernel_manifest_hash": manifest_hash(manifest),
        "cli_version": CLI_VERSION,
        "schema_versions": manifest.get("schema_versions", {}),
        "lock_schema_version": LOCK_SCHEMA_VERSION,
    }
    write_yaml(path, lock)
    return lock


def read_lock(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise GovError(f"framework.lock missing at {path}", "LOCK_MISSING")
    return read_yaml(path) or {}


def parse_version(v: str) -> tuple[int, int, int]:
    core = str(v).split("-")[0].split("+")[0]
    parts = core.split(".")
    while len(parts) < 3:
        parts.append("0")
    return tuple(int(p) for p in parts[:3])  # type: ignore[return-value]


def compatibility(lock_version: str, cli_version: str = CLI_VERSION) -> dict[str, Any]:
    lv, cv = parse_version(lock_version), parse_version(cli_version)
    if lv[0] != cv[0]:
        return {"compatible": False, "reason": "major version mismatch between installed kernel and gov CLI"}
    if lv[:2] != cv[:2]:
        return {"compatible": True, "reason": "minor version differs; run gov update --check", "warning": True}
    return {"compatible": True, "reason": "match"}
