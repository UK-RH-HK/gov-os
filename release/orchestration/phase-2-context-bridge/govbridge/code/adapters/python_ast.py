"""Wrapper around the existing Python AST ``code_intel`` plugin (REUSE, DAG node B3;
``capabilities/python/govos_capabilities/code_intel_python_ast.py``). The plugin file itself is never edited and
never copied into ``capabilities/``: this module reads its bytes -- and its small ``plugin.py``/``__init__.py``
package dependencies -- straight out of Git at the canonical view's ``records`` ref (ARCHITECTURE.md section 1.2,
config/canonical-view.yaml), materialises them read-only into this run's own isolated store
(``govbridge.core.store.store_root()``, so parallel builders never collide, BR-DAG-AMEND-1), and runs the plugin as
an ordinary ``gov-capability/1`` subprocess -- exactly the invocation ARCHITECTURE.md section 9 describes ("The
bridge invokes plugins directly, as subprocesses speaking gov-capability/1"). Nothing here re-implements or patches
the plugin's Python logic.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

from govbridge import GOV_BRIDGE_DOMAIN
from govbridge.core import gitobj, store, view as viewmod
from govbridge.core.yamlutil import sha256_bytes

PACKAGE_FILES = ("__init__.py", "plugin.py", "code_intel_python_ast.py")
PLUGIN_REL_PATH = "capabilities/python/govos_capabilities/code_intel_python_ast.py"
_PACKAGE_DIR = "capabilities/python/govos_capabilities"


class PluginUnavailable(RuntimeError):
    """The plugin's blob (or a package dependency it needs) could not be located at the requested ref."""


def _default_view_path(repo: Optional[str] = None) -> str:
    return str(Path(GOV_BRIDGE_DOMAIN) / "config" / "canonical-view.yaml")


def records_commit(view_path: Optional[str] = None, repo: Optional[str] = None) -> str:
    """The commit the canonical view's ``records`` (primary) ref currently names -- "the records commit" the
    handoff refers to. Generic: reads config/canonical-view.yaml rather than naming a ref literally."""
    vc = viewmod.load_view(view_path or _default_view_path(repo))
    resolved = viewmod.resolve_view(vc, repo=repo)
    primary = next(r for r in vc.refs if r.role == "primary")
    ref = resolved.named[primary.name]
    return ref.commit


def plugin_blob_id(commit: Optional[str] = None, repo: Optional[str] = None) -> str:
    """The Git blob id of ``code_intel_python_ast.py`` at ``commit`` (default: the records commit). Recorded by
    every caller so provenance names the exact bytes that ran (BR-HO-0005 notes: "Record its blob id")."""
    commit = commit or records_commit(repo=repo)
    blob = gitobj.blob_at(commit, PLUGIN_REL_PATH, repo=repo)
    if blob is None:
        raise PluginUnavailable(f"{PLUGIN_REL_PATH} not found at {commit}")
    return blob


def _materialise(commit: str, repo: Optional[str]) -> Path:
    """Write the plugin package's blobs, unmodified, into this run's own isolated store -- never into the
    repository's own capabilities/ tree. Skips the write if a prior call already materialised this exact commit's
    blobs (content-addressed by their sha256, so a stale copy is never reused silently)."""
    blobs = {}
    for name in PACKAGE_FILES:
        rel = f"{_PACKAGE_DIR}/{name}"
        oid = gitobj.blob_at(commit, rel, repo=repo)
        if oid is None:
            raise PluginUnavailable(f"{rel} not found at {commit}")
        data = gitobj.read_blob(oid, repo=repo)
        if data is None:
            raise PluginUnavailable(f"blob {oid} for {rel} could not be read")
        blobs[name] = (oid, data)

    fingerprint = sha256_bytes(b"\x1f".join(oid.encode() for oid, _ in blobs.values()))
    dest_root = store.store_root() / "code" / "python_ast_plugin" / fingerprint
    package_dir = dest_root / "govos_capabilities"
    marker = dest_root / ".materialised"
    if marker.exists():
        return dest_root
    package_dir.mkdir(parents=True, exist_ok=True)
    for name, (_, data) in blobs.items():
        (package_dir / name).write_bytes(data)
    marker.write_text(fingerprint, encoding="utf-8")
    return dest_root


def run(source: str, path: str, language: str = "python", commit: Optional[str] = None,
        repo: Optional[str] = None, timeout: float = 30.0) -> dict:
    """Run the reused plugin, unmodified, from its blob at ``commit`` (default: the records commit), as a
    ``gov-capability/1`` subprocess. Returns the parsed JSON response (``{protocol, ok, provider, outputs}`` or
    ``{protocol, ok, provider, error}``) plus ``blob`` (the plugin's own blob id, for provenance) and ``commit``."""
    commit = commit or records_commit(repo=repo)
    plugin_dir = _materialise(commit, repo)
    blob = plugin_blob_id(commit, repo=repo)

    request = {
        "protocol": "gov-capability/1", "capability": "code_intel", "request_id": None,
        "inputs": {"source": source, "path": path, "language": language},
    }
    env = dict(os.environ)
    env["PYTHONPATH"] = str(plugin_dir)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    proc = subprocess.run(
        [sys.executable, "-m", "govos_capabilities.code_intel_python_ast"],
        input=json.dumps(request).encode("utf-8"),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=str(plugin_dir), env=env, timeout=timeout,
    )
    if proc.returncode != 0:
        return {
            "protocol": "gov-capability/1", "ok": False,
            "provider": {"id": "python-ast", "version": "unknown"},
            "error": {"code": "PLUGIN_PROCESS_ERROR",
                      "message": proc.stderr.decode("utf-8", "replace")[-2000:]},
            "blob": blob, "commit": commit,
        }
    response = json.loads(proc.stdout.decode("utf-8"))
    response["blob"] = blob
    response["commit"] = commit
    return response
