"""Kernel payload: build from the canonical repo, install into a consumer, verify immutability."""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from govos import FRAMEWORK_NAME, VERSION
from govos.runtime.util import GovError, hash_obj, hash_tree, now_iso, read_json, read_yaml, sha256_file, write_json

KERNEL_MANIFEST = "KERNEL_MANIFEST.json"
CANONICAL_ROOT = Path(__file__).resolve().parents[2]


def canonical_framework_dir() -> Path:
    return CANONICAL_ROOT / "framework"


def resolve_kernel_source(source: str | Path | None) -> Path:
    """Accepts: None (bundled framework/), a canonical repo root, a framework/ dir, a built release dir, or a kernel dir."""
    if source is None:
        return canonical_framework_dir()
    src = Path(source).resolve()
    if (src / "KERNEL.yaml").exists():
        return src
    if (src / "kernel" / "KERNEL.yaml").exists():
        return src / "kernel"
    if (src / "framework" / "KERNEL.yaml").exists():
        return src / "framework"
    raise GovError(f"No kernel payload found at {src}", "KERNEL_SOURCE_NOT_FOUND")


def kernel_meta(kernel_dir: Path) -> dict[str, Any]:
    return read_yaml(kernel_dir / "KERNEL.yaml")


def payload_files(kernel_dir: Path) -> dict[str, str]:
    """Hash all payload files (excluding the manifest itself)."""
    _, files = hash_tree(kernel_dir, exclude=[KERNEL_MANIFEST])
    return files


def build_manifest(kernel_dir: Path) -> dict[str, Any]:
    meta = kernel_meta(kernel_dir)
    files = payload_files(kernel_dir)
    manifest = {
        "framework": meta.get("framework", FRAMEWORK_NAME),
        "version": str(meta.get("version", VERSION)),
        "files": files,
        "payload_hash": hash_obj(files),
        "schema_versions": meta.get("schema_versions", {}),
        "cli_version": str(meta.get("cli_version", VERSION)),
        "runtime_version": str(meta.get("runtime_version", VERSION)),
        "adapter_versions": meta.get("adapter_versions", {}),
        "supported_from_versions": [str(v) for v in meta.get("supported_from_versions", [])],
    }
    return manifest


def stage_payload(source_dir: Path, dest: Path, migrations_dir: Path | None = None) -> None:
    """Copy the kernel payload into dest (a fresh directory)."""
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    meta = kernel_meta(source_dir)
    for d in meta.get("payload_dirs", []):
        src = source_dir / d
        if not src.exists() and d == "migrations":
            cand = migrations_dir or (source_dir.parent / "migrations")
            if cand.exists():
                src = cand
        if src.exists():
            shutil.copytree(src, dest / d)
    shutil.copy2(source_dir / "KERNEL.yaml", dest / "KERNEL.yaml")


def install_kernel(source: str | Path | None, governance_dir: Path) -> dict[str, Any]:
    src = resolve_kernel_source(source)
    dest = governance_dir / "kernel"
    stage_payload(src, dest)
    manifest = build_manifest(dest)
    manifest["built_at"] = now_iso()
    write_json(dest / KERNEL_MANIFEST, manifest)
    return manifest


def read_manifest(kernel_dir: Path) -> dict[str, Any]:
    p = kernel_dir / KERNEL_MANIFEST
    if not p.exists():
        raise GovError("Kernel manifest missing", "KERNEL_MANIFEST_MISSING")
    return read_json(p)


def manifest_hash(manifest: dict[str, Any]) -> str:
    return hash_obj({k: manifest[k] for k in ("framework", "version", "files", "payload_hash") if k in manifest})


def verify_kernel(kernel_dir: Path) -> dict[str, Any]:
    """Compare on-disk payload with the manifest. Returns {ok, modified, missing, added}."""
    manifest = read_manifest(kernel_dir)
    actual = payload_files(kernel_dir)
    expected = manifest.get("files", {})
    modified = sorted(p for p in expected if p in actual and actual[p] != expected[p])
    missing = sorted(p for p in expected if p not in actual)
    added = sorted(p for p in actual if p not in expected)
    return {"ok": not (modified or missing or added), "modified": modified, "missing": missing, "added": added,
            "payload_hash": manifest.get("payload_hash"), "version": manifest.get("version")}
