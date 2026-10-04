"""The pre-index secret filter and the secrets-indexing check (W1-15; DEC-285 to DEC-290).

``indexable(root, paths)`` is what every indexer calls before chunking: it returns
the paths the indexer may read. ``stores_with_secrets(root)`` is the subject of the
secrets-indexing family check. Both run the gitleaks binary with the rules of the
project's ``.gitleaks.toml`` (DEC-287) over content given on standard input, so a
path allowlist never applies (DEC-290) and no report is written. Whatever cannot be
decided raises or is left out; nothing is let through undecided.
"""

from __future__ import annotations

import re
import sqlite3
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.config.loader import load_config

CONFIG_REL = ".gitleaks.toml"
RUNTIME_REL = ".gov-runtime"
GOVERNANCE = "governance"
_LEAKS, _TIMEOUT_S = 3, 60

__all__ = ["indexable", "stores_with_secrets"]


def _holds_secret(root: Path, content: bytes) -> bool:
    """Whether gitleaks finds a secret in ``content``. Raises when gitleaks cannot run or does not decide."""
    # The leading newline keeps gitleaks from skipping content it would take for a binary file.
    done = subprocess.run(
        ["gitleaks", "stdin", "--config", str(Path(root) / CONFIG_REL), "--no-banner", "--redact",
         "--ignore-gitleaks-allow", "--gitleaks-ignore-path", "/dev/null", "--log-level", "error",
         "--exit-code", str(_LEAKS)],
        input=b"\n" + content, capture_output=True, timeout=_TIMEOUT_S)
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
    root = Path(root)
    namespaces = load_config(root)["path-map.yaml"]["namespaces"]

    def allowed(rel: str) -> bool:
        if rel.startswith("/") or ".." in rel.split("/") or not _governance(namespaces, rel):
            return False
        try:
            content = (root / rel).read_bytes()  # a link is judged by what it points to
        except OSError:
            return False
        return not _holds_secret(root, content)

    with ThreadPoolExecutor() as pool:
        verdicts = list(pool.map(allowed, dict.fromkeys(paths)))
    return [rel for rel, verdict in zip(dict.fromkeys(paths), verdicts) if verdict]


def _store_content(path: Path) -> bytes:
    """What a derived store holds: the rows of a SQLite file as text, the bytes of any other file."""
    with path.open("rb") as handle:
        if handle.read(16) != b"SQLite format 3\0":
            return path.read_bytes()
    connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    try:
        tables = [name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
        rows = (row for name in tables for row in connection.execute(f'SELECT * FROM "{name}"'))
        return "\n".join(" ".join(str(value) for value in row) for row in rows).encode("utf-8", "replace")
    finally:
        connection.close()


def stores_with_secrets(root: Path) -> list[str]:
    """Every file under ``.gov-runtime/`` whose content holds a secret, as project-relative paths (DEC-290)."""
    root = Path(root)
    files = sorted(path for path in (root / RUNTIME_REL).rglob("*") if path.is_file())
    return [path.relative_to(root).as_posix() for path in files if _holds_secret(root, _store_content(path))]
