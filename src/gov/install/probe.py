"""What doctor's section ``install`` reads (W2-18): an environment's installed gov, and where a package was imported.

- ``distribution(env)``: the ``gov`` distribution installed in the environment's own site-packages, ``None`` without
  one; ``editable`` is true where its ``direct_url.json`` says ``dir_info.editable``.
- ``source_tree(package)``: whether an imported ``gov`` package folder is a source tree's ``src/gov`` (a folder
  ``src/`` beside a ``pyproject.toml``).
"""

from __future__ import annotations

import json
import os
from pathlib import Path


def site_packages(env) -> list[Path]:
    return sorted(Path(env).glob("lib/python*/site-packages"))


def _name(info: Path) -> str | None:
    try:
        for line in (info / "METADATA").read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("name:"):
                return line.split(":", 1)[1].strip().lower().replace("_", "-")
            if not line.strip():
                break
    except (OSError, UnicodeDecodeError):
        return None
    return None


def distribution(env) -> dict | None:
    """``{"path", "editable", "url"}`` of the ``gov`` distribution in ``env``'s site-packages, or ``None``."""
    for site in site_packages(env):
        for info in sorted(site.glob("*.dist-info")):
            if _name(info) != "gov":
                continue
            editable, url = False, None
            try:
                direct = json.loads((info / "direct_url.json").read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError, ValueError):
                direct = None
            if isinstance(direct, dict):
                url = direct.get("url")
                dir_info = direct.get("dir_info")
                editable = isinstance(dir_info, dict) and dir_info.get("editable") is True
            return {"path": str(info), "editable": editable, "url": url, "site": str(site)}
    return None


def source_tree(package) -> bool:
    """Whether the package folder is ``<tree>/src/gov`` with ``<tree>/pyproject.toml``."""
    package = Path(os.path.realpath(package))
    return package.parent.name == "src" and (package.parent.parent / "pyproject.toml").is_file()
