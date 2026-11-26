"""The Node folder a product test run puts on its ``PATH`` (W2-20 fix SP-1, SP-2).

It is read from the tool registry of the tree under test, the entry named exactly ``node``: the folder of its install
line's ``PATH=<folder>:$PATH`` prefix (``$HOME`` and ``~`` from this process's HOME), else the nvm folder of its
pinned version. It counts only where it holds ``node``; where there is none, the reason says so and a run keeps the
``PATH`` it has.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

REGISTRY = "governance/project/tool-registry.yaml"


def node_prefix(root) -> dict:
    """``{"prefix", "version", "reason"}`` for the tree ``root``: the folder, or None and why."""
    def none(reason: str, version: str | None = None) -> dict:
        return {"prefix": None, "version": version, "reason": reason}

    path = Path(root) / REGISTRY
    if not path.is_file():
        return none(f"no node: there is no {REGISTRY}")
    try:
        import yaml
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as error:  # noqa: BLE001 - a registry that cannot be read gives no node, named
        return none(f"no node: {REGISTRY} cannot be read ({type(error).__name__})")
    tools = data.get("tools") if isinstance(data, dict) else None
    entry = next((e for e in tools if isinstance(e, dict) and e.get("name") == "node"), None) \
        if isinstance(tools, list) else None
    if entry is None:
        return none(f"no node: {REGISTRY} has no entry named node")
    version = str(entry.get("version") or "") or None
    home = os.path.expanduser("~")
    given = re.search(r"PATH=([^:]+):\$PATH", str(entry.get("install") or ""))
    if given:
        folder = Path(os.path.expanduser(given.group(1).replace("$HOME", home)))
    elif version:
        folder = Path(home) / ".nvm" / "versions" / "node" / ("v" + version.lstrip("v")) / "bin"
    else:
        return none(f"no node: the node entry of {REGISTRY} pins no version")
    if not (folder / "node").is_file():
        return none(f"node {version or '(no version)'} is not installed: there is no node in {folder}", version)
    return {"prefix": str(folder), "version": version, "reason": None}


def with_node(env: dict, root) -> dict:
    """A copy of ``env`` with the Node folder of the tree ``root`` first on ``PATH``; unchanged where there is none."""
    out = dict(env)
    prefix = node_prefix(root)["prefix"]
    if prefix:
        path = out.get("PATH", os.defpath)
        if path.split(os.pathsep)[0] != prefix:
            out["PATH"] = prefix + os.pathsep + path if path else prefix
    return out
