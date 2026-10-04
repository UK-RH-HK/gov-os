"""The pre-index secret filter and the secrets-indexing check (W1-15; DEC-285 to DEC-290).

``indexable(root, paths)`` is what every indexer calls before chunking: it returns
the paths the indexer may read. ``stores_with_secrets(root)`` is the subject of the
secrets-indexing family check. Both run the gitleaks binary with the rules of the
project's ``.gitleaks.toml`` (DEC-287) over content given on standard input, so a
path allowlist never applies (DEC-290) and no report is written. The file's other
allowlists and its disabled rules are left out of the scan (DEC-298). Whatever cannot be
decided raises or is left out; nothing is let through undecided.
"""

from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.config.loader import load_config

CONFIG_REL = ".gitleaks.toml"
RUNTIME_REL = ".gov-runtime"
GOVERNANCE = "governance"
_LEAKS, _TIMEOUT_S = 3, 60

__all__ = ["indexable", "stores_with_secrets"]


def _toml(value) -> str:
    """``value`` as one TOML value: tables inline, the rest as JSON writes it."""
    if isinstance(value, dict):
        return "{" + ", ".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def _rules(root: Path) -> str:
    """The rules of ``.gitleaks.toml`` as TOML, without what shelters a secret (DEC-298).

    Allowlists, of the file and of each rule, and disabled rules are left out. Raises unless
    the file holds rules: a scan without rules finds nothing, which is no verdict.
    """
    try:
        config = tomllib.loads((Path(root) / CONFIG_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise RuntimeError(f"{CONFIG_REL} cannot be read: {error}") from None
    if not (config.get("rules") or config.get("extend", {}).get("useDefault") is True):
        raise RuntimeError(f"{CONFIG_REL} holds no rules: nothing can be decided")
    for table in (config, *config.get("rules", [])):
        table.pop("allowlist", None)
        table.pop("allowlists", None)
    config.get("extend", {}).pop("disabledRules", None)
    return "\n".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in config.items())


def _holds_secret(rules: str, content: bytes) -> bool:
    """Whether gitleaks finds a secret in ``content`` by ``rules``. Raises when gitleaks cannot run or does not decide."""
    if b"\0" in content:  # UTF-16 text: the same content without its zero bytes is scanned too
        content += b"\n" + content.replace(b"\0", b"")
    # The rules go by the environment, so no file of them is written; a configuration path there would win over them.
    env = {key: value for key, value in os.environ.items() if key != "GITLEAKS_CONFIG"}
    # The leading newline keeps gitleaks from skipping content it would take for a binary file.
    done = subprocess.run(
        ["gitleaks", "stdin", "--no-banner", "--redact",
         "--ignore-gitleaks-allow", "--gitleaks-ignore-path", "/dev/null", "--log-level", "error",
         "--exit-code", str(_LEAKS)],
        input=b"\n" + content, capture_output=True, timeout=_TIMEOUT_S, env=env | {"GITLEAKS_CONFIG_TOML": rules})
    if done.returncode not in (0, _LEAKS):
        raise RuntimeError(f"gitleaks could not scan with {CONFIG_REL} (exit code {done.returncode})")
    return done.returncode == _LEAKS


def _matches(rel: str, pattern: str) -> bool:
    """``*`` stays inside one folder, ``**`` crosses folders (the language of the path map)."""
    parts = [re.escape(part).replace(r"\*", "[^/]*") for part in pattern.split("**")]
    return re.fullmatch(".*".join(parts), rel) is not None


def _governance(namespaces: dict, rel: str) -> bool:
    """Whether ``rel`` has a namespace and every namespace it matches is governance memory."""
    classes = [entry.get("memory_class") for entry in namespaces.values()
               if any(_matches(rel, pattern) for pattern in entry["paths"])]
    return bool(classes) and all(item == GOVERNANCE for item in classes)


def indexable(root: Path, paths: list[str]) -> list[str]:
    """The sub-list of ``paths`` an indexer may read, in the order asked (DEC-285)."""
    root = Path(root).resolve()
    rules = _rules(root)
    namespaces = load_config(root)["path-map.yaml"]["namespaces"]

    def allowed(rel: str) -> bool:
        try:  # a link is judged by what it points to: its namespace and its content
            real = (root / rel).resolve(strict=True)
            target = real.relative_to(root).as_posix()
            content = real.read_bytes()
        except (OSError, ValueError, RuntimeError):  # no file, a link loop, or a place outside the root
            return False
        if not (_governance(namespaces, rel) and _governance(namespaces, target)):
            return False
        return not _holds_secret(rules, content)

    with ThreadPoolExecutor() as pool:
        verdicts = list(pool.map(allowed, dict.fromkeys(paths)))
    return [rel for rel, verdict in zip(dict.fromkeys(paths), verdicts) if verdict]


def _store_content(path: Path) -> bytes:
    """What a derived store holds: the bytes of the file and, for a SQLite file, its rows as text too."""
    content = path.read_bytes()  # deleted rows and the text of views are in the bytes
    if not content.startswith(b"SQLite format 3\0"):
        return content
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        tables = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        rows = (row for name in tables for row in connection.execute(f'SELECT * FROM "{name}"'))
        text = "\n".join(" ".join(str(value) for value in row) for row in rows)
        return content + b"\n" + text.encode("utf-8", "replace")
    finally:
        connection.close()


def stores_with_secrets(root: Path) -> list[str]:
    """Every file under ``.gov-runtime/`` whose content holds a secret, as project-relative paths (DEC-290)."""
    root = Path(root)
    rules = _rules(root)
    if not os.path.lexists(root / RUNTIME_REL):
        return []

    def refuse(error: OSError) -> None:
        raise error  # a folder that cannot be entered is not a store without a secret

    # Linked folders are followed; a file that cannot be read raises.
    files = sorted(Path(folder) / name
                   for folder, _, names in os.walk(root / RUNTIME_REL, onerror=refuse, followlinks=True)
                   for name in names)
    return [path.relative_to(root).as_posix() for path in files if _holds_secret(rules, _store_content(path))]
