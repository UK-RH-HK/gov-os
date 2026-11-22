"""Stand-ins and runners for the W2-22 cases: ``gov doctor`` on a scratch repository with a stand-in Claude Code CLI
and VS Code extension (the approach of W1-27's ``test_w1_27_drift.py``).

Nothing here touches the installed CLI, the installed extension or this machine's home: the stand-in ``claude`` is a
shell script in the case's own ``bin`` folder, put first on the ``PATH`` ``gov`` runs with; the stand-in extension
lies under the case's ``HOME/.vscode-server/extensions``. ``gov doctor`` runs with this worktree's code (DEC-732).
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
import sys
from pathlib import Path

_W1_27 = str(Path(__file__).resolve().parents[1] / "W1-27")
_W1_07 = str(Path(__file__).resolve().parents[1] / "W1-07")
for _folder in (_W1_27, _W1_07):
    if _folder not in sys.path:
        sys.path.insert(0, _folder)

import w1_07_support as base  # noqa: E402
import w1_27_support as w1_27  # noqa: E402
import w2_67_codegraph as codegraph  # noqa: E402

REPO_ROOT = base.REPO_ROOT
MINIMUM = "2.1.285"   # doctor's minimum Claude Code version (W1-48, DEC-210)


def write_cli(sandbox, version: str) -> str:
    """A stand-in ``claude`` answering ``version`` in the sandbox's bin folder; its sha256."""
    path = sandbox.bin / "claude"
    path.write_text(f"#!/bin/sh\necho '{version}'\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IEXEC)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_extension(sandbox, version: str) -> str:
    """A stand-in active VS Code extension at ``version`` under the sandbox home; its bundled binary's sha256."""
    extensions = sandbox.home / ".vscode-server" / "extensions"
    folder = extensions / f"anthropic.claude-code-{version}"
    (folder / "resources" / "native-binary").mkdir(parents=True, exist_ok=True)
    (extensions / "extensions.json").write_text(json.dumps([{
        "identifier": {"id": "anthropic.claude-code"}, "version": version, "location": {"path": str(folder)},
    }]), encoding="utf-8")
    (folder / "package.json").write_text(json.dumps({"name": "claude-code", "version": version}), encoding="utf-8")
    binary = folder / "resources" / "native-binary" / "claude"
    binary.write_text(f"#!/bin/sh\necho 'ext {version}'\n", encoding="utf-8")
    binary.chmod(binary.stat().st_mode | stat.S_IEXEC)
    return hashlib.sha256(binary.read_bytes()).hexdigest()


def doctor(tmp_path, sandbox, monkeypatch, *args, registry: str | None = None):
    """``gov doctor <args>`` on a small committed repository of the case's own, the sandbox's bin first on the
    ``PATH``. ``registry``: the tools section of a tool registry to commit (None: no registry entry at all, so Claude
    Code has no pinned version). Returns the run."""
    project = tmp_path / "repo"
    project.mkdir()
    w1_27.git(project, "init", "-q", "-b", "main")
    w1_27.write_path_map(project, w1_27.minimal_valid_path_map())   # commits
    if registry is not None:
        w1_27.write_tool_registry(project, registry)
    monkeypatch.setenv("PATH", f"{sandbox.bin}{os.pathsep}{os.environ.get('PATH', '/usr/bin:/bin')}")
    return w1_27.run_gov_with_code(REPO_ROOT, project, sandbox, "doctor", *args)


def claude_code_registry(version: str, sha256: str) -> str:
    return w1_27.tool_entry_yaml("claude code", version, sha256, install="echo test", uninstall="echo test",
                                 date="2026-01-01", approved_by="test")


def envelope(run) -> dict:
    return base.Run.envelope(run)


def section(run) -> dict:
    """The ``claude_code`` section: in ``result`` when doctor is healthy, else in ``error.details`` (exit 3)."""
    env = envelope(run)
    found = env.get("result") if env.get("ok") is True else (env.get("error") or {}).get("details")
    part = (found or {}).get("claude_code") if isinstance(found, dict) else None
    assert isinstance(part, dict), f"gov doctor reported no claude_code section\n{run.describe()}"
    return part
