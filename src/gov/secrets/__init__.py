"""The pre-index secret filter and the secrets-indexing check (W1-15; DEC-285 to DEC-290).

``indexable(root, paths)`` is what every indexer calls before chunking: it returns
the paths the indexer may read. ``stores_with_secrets(root)`` is the subject of the
secrets-indexing family check. ``path_holds_secret(root, path)`` judges a path name,
for an index that stores paths (DEC-339). All run the gitleaks binary with the rules of the
project's ``.gitleaks.toml`` (DEC-287) over content given on standard input, so a
path allowlist never applies (DEC-290) and no report is written. The file's other
allowlists and its disabled rules are left out of the scan (DEC-298), and a second scan with
the file's rules alone keeps the allowlist of gitleaks' defaults from sheltering them
(DEC-347). Whatever cannot be decided raises or is left out; nothing is let through undecided.

Each gitleaks run may take a minute plus a second a megabyte, so a store is decided whenever gitleaks
reads at 1 MB/s or faster (DEC-853). A store whose bytes were scanned clean before, by the same rule sets
and the same gitleaks, is not scanned again: the check's record of clean results says so, and the reuse
is labelled on standard error with the store's path and digest. A finding is never recorded.
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import threading
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from gov.config.loader import load_config
from gov.guard.runs import root as runs_root

CONFIG_REL = ".gitleaks.toml"
RUNTIME_REL = ".gov-runtime"
RECORD_REL = f"{RUNTIME_REL}/secrets-clean.json"  # the clean results, by digest (DEC-853)
GOVERNANCE = "governance"
_LEAKS, _TIMEOUT_S = 3, 60
_FLOOR = 1_000_000  # bytes a second: the slowest gitleaks a store must still be decided at (DEC-853)
_LARGE = 64 << 20  # a file of this size or more is read and scanned at most two at a time, for memory
_FORM = 1  # the form of the record and of what a scan reads; another form is never trusted

__all__ = ["indexable", "path_holds_secret", "stores_with_secrets"]


def _toml(value) -> str:
    """``value`` as one TOML value: tables inline, the rest as JSON writes it."""
    if isinstance(value, dict):
        return "{" + ", ".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in value.items()) + "}"
    if isinstance(value, list):
        return "[" + ", ".join(_toml(item) for item in value) + "]"
    return json.dumps(value, ensure_ascii=False)


def _rules(root: Path) -> tuple[str, ...]:
    """The rules of ``.gitleaks.toml`` as TOML, without what shelters a secret (DEC-298).

    Allowlists, of the file and of each rule, and disabled rules are left out. Raises unless
    the file holds rules: a scan without rules finds nothing, which is no verdict. Where the file
    extends other rules, its own rules follow alone as a second configuration (DEC-347): the
    allowlist of gitleaks' defaults, which ``extend`` lays over every rule, is not in it.
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
    # A rule with no expression of its own only changes a rule it extends: alone, gitleaks refuses the file for it.
    alone = [rule for rule in config.get("rules", []) if rule.get("regex") or rule.get("path")]
    configs = [config, {"rules": alone}] if alone and "extend" in config else [config]
    return tuple("\n".join(f"{json.dumps(key)} = {_toml(item)}" for key, item in each.items()) for each in configs)


def _holds_secret(rules: tuple[str, ...], content: bytes) -> bool:
    """Whether gitleaks finds a secret in ``content`` by any of ``rules``. Raises when gitleaks cannot run or does not decide."""
    # The leading newline keeps gitleaks from skipping content it would take for a binary file.
    parts = [b"\n", content]
    if b"\0" in content:  # UTF-16 text: the same content without its zero bytes is scanned too
        parts += [b"\n", content.replace(b"\0", b"")]
    data = b"".join(parts)  # one copy, read by every scan
    # The rules go by the environment, so no file of them is written; a configuration path there would win over them.
    env = {key: value for key, value in os.environ.items() if key != "GITLEAKS_CONFIG"}
    for each in rules:  # clean only when every scan ran and found nothing
        done = subprocess.run(
            ["gitleaks", "stdin", "--no-banner", "--redact",
             "--ignore-gitleaks-allow", "--gitleaks-ignore-path", "/dev/null", "--log-level", "error",
             "--exit-code", str(_LEAKS)],
            input=data, capture_output=True, timeout=_TIMEOUT_S + len(data) / _FLOOR,
            env=env | {"GITLEAKS_CONFIG_TOML": each})
        if done.returncode not in (0, _LEAKS):
            raise RuntimeError(f"gitleaks could not scan with {CONFIG_REL} (exit code {done.returncode})")
        if done.returncode == _LEAKS:
            return True
    return False


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


def path_holds_secret(root: Path, path: str) -> bool:
    """Whether the name of ``path`` holds a secret: the whole path and each of its names, judged as content is."""
    return _holds_secret(_rules(root), os.fsencode("\n".join([path, *Path(path).parts])))


def _store_content(path: Path, content: bytes | None = None) -> bytes:
    """What a derived store holds: the bytes of the file (``content``, read if not given) and, for a SQLite file, its rows as text too."""
    if content is None:
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


def _scanner(rules: tuple[str, ...]) -> str | None:
    """What decides a scan besides the content: the rule sets, the gitleaks ``PATH`` finds, and the scan's form.

    None when no gitleaks is found; the scan then raises, and nothing is reused or recorded.
    """
    found = shutil.which("gitleaks")
    if found is None:
        return None
    with open(found, "rb") as handle:
        binary = hashlib.file_digest(handle, "sha256").hexdigest()
    return hashlib.sha256(json.dumps([_FORM, list(rules), binary]).encode()).hexdigest()


def _check(body: dict) -> str:
    """The digest a record carries of its own body: a record damaged in any way no longer matches it."""
    return hashlib.sha256(json.dumps(body, sort_keys=True).encode()).hexdigest()


def _trusted(root: Path, scanner: str | None) -> set[str]:
    """The digests of the bytes the record holds as clean for ``scanner``.

    Empty when the record is missing, unreadable, damaged, of another form or of another scanner: then every store is scanned.
    """
    if scanner is None:
        return set()
    try:
        record = json.loads((root / RECORD_REL).read_text(encoding="utf-8"))
        body = {key: record[key] for key in ("form", "scanner", "clean")}
        if (set(record) != {*body, "check"} or record["check"] != _check(body) or body["form"] != _FORM
                or body["scanner"] != scanner or not isinstance(body["clean"], list)
                or not all(isinstance(each, str) and re.fullmatch("[0-9a-f]{64}", each) for each in body["clean"])):
            return set()
    except (OSError, ValueError, KeyError, TypeError):
        return set()
    return set(body["clean"])


def _record(root: Path, scanner: str, clean: set[str]) -> None:
    """Replaces the record in one step, so an interrupted run leaves the old record or the new one, never part of one.

    A record that cannot be written is left out: the next run scans in full.
    """
    body = {"form": _FORM, "scanner": scanner, "clean": sorted(clean)}
    path = root / RECORD_REL
    temporary = None
    try:
        handle, temporary = tempfile.mkstemp(dir=path.parent, prefix=".secrets-clean.", suffix=".part")
        with os.fdopen(handle, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(body | {"check": _check(body)}))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError:
        if temporary is not None:
            with contextlib.suppress(OSError):
                os.unlink(temporary)


def stores_with_secrets(root: Path) -> list[str]:
    """Every file under ``.gov-runtime/`` whose content holds a secret, as project-relative paths (DEC-290)."""
    root = Path(root)
    rules = _rules(root)
    if not os.path.lexists(root / RUNTIME_REL):
        return []

    def refuse(error: OSError) -> None:
        raise error  # a folder that cannot be entered is not a store without a secret

    # DEC-728, DEC-743 3: a link into ~/gov-os-runs is not followed; nothing there is this repository's.
    # The runtime folder's own files are scanned, also in a clone that lies there, and (DEC-751 2) a link
    # whose target stays inside the project being scanned is followed there too.
    runs, runtime, project = runs_root(), os.path.realpath(root / RUNTIME_REL), os.path.realpath(root)

    def followed(path: str) -> bool:
        real = os.path.realpath(path)
        within = lambda top: real == top or real.startswith(top + os.sep)  # noqa: E731
        return runs is None or within(runtime) or within(project) or not within(runs)

    # Linked folders elsewhere are followed; a file that cannot be read raises.
    files = []
    for folder, folders, names in os.walk(root / RUNTIME_REL, onerror=refuse, followlinks=True):
        folders[:] = [name for name in folders if followed(os.path.join(folder, name))]
        files += [Path(folder) / name for name in names if followed(os.path.join(folder, name))]
    files.sort()
    # DEC-853: a store's bytes once scanned clean by the same scanner are not scanned again.
    scanner = _scanner(rules)
    trusted, clean, reused = _trusted(root, scanner), set(), {}
    large = threading.BoundedSemaphore(2)

    def judge(path: Path) -> bool:
        with large if path.stat().st_size >= _LARGE else contextlib.nullcontext():
            content = path.read_bytes()
            digest = hashlib.sha256(content).hexdigest()
            if digest in trusted:
                reused[path] = digest
            elif _holds_secret(rules, _store_content(path, content)):
                return True  # a finding is never recorded
            clean.add(digest)
            return False

    # Every file is read and judged, the largest first, as many at a time as there are processors, so a large
    # store is neither started last nor slowed by more runs than the machine runs at once. The first file that
    # cannot be decided raises, and then nothing is recorded.
    by_size = sorted(files, key=lambda path: -path.stat().st_size)
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 1) as pool:
        verdicts = dict(zip(by_size, pool.map(judge, by_size)))
    for path, digest in sorted(reused.items()):  # the label names the store and the digest, never content
        print(f"secrets-indexing: clean result reused, not scanned again: {path.relative_to(root).as_posix()} "
              f"sha256 {digest}", file=sys.stderr)
    if scanner is not None:
        _record(root, scanner, clean)
    return [path.relative_to(root).as_posix() for path in files if verdicts[path]]
