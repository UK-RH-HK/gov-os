"""Shared deterministic utilities: IO, hashing, glob matching, ids, time."""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Iterable

import yaml


class GovError(Exception):
    """Base error with a stable machine code."""

    code = "GOV_ERROR"

    def __init__(self, message: str, code: str | None = None, details: dict | None = None):
        super().__init__(message)
        if code:
            self.code = code
        self.details = details or {}


class _Dumper(yaml.SafeDumper):
    pass


def _str_presenter(dumper, data):
    if "\n" in data:
        return dumper.represent_scalar("tag:yaml.org,2002:str", data, style="|")
    return dumper.represent_scalar("tag:yaml.org,2002:str", data)


_Dumper.add_representer(str, _str_presenter)


def read_yaml(path: Path | str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_yaml(path: Path | str, data: Any) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, Dumper=_Dumper, sort_keys=False, allow_unicode=True, default_flow_style=False)


def read_json(path: Path | str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, data: Any, sort_keys: bool = True) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=sort_keys, ensure_ascii=False)
        f.write("\n")


def read_text(path: Path | str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def write_text(path: Path | str, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def sha256_text(s: str) -> str:
    return sha256_bytes(s.encode("utf-8"))


def sha256_file(path: Path | str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def canonical_json(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False, default=str)


def hash_obj(data: Any) -> str:
    return sha256_text(canonical_json(data))


def hash_tree(root: Path, rel_to: Path | None = None, exclude: Iterable[str] = ()) -> tuple[str, dict[str, str]]:
    """Deterministic hash of a directory tree: returns (tree_hash, {relpath: filehash})."""
    root = Path(root)
    rel_to = rel_to or root
    files: dict[str, str] = {}
    ex = list(exclude)
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(rel_to).as_posix()
        if any(glob_match(pat, rel) for pat in ex):
            continue
        files[rel] = sha256_file(p)
    return hash_obj(files), files


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).replace(microsecond=0).isoformat()


def today() -> str:
    return _dt.date.today().isoformat()


def new_session_id() -> str:
    return "S-" + uuid.uuid4().hex[:12]


_GLOB_CACHE: dict[str, re.Pattern] = {}


def glob_to_regex(pattern: str) -> re.Pattern:
    """Convert a gitignore-like glob (supports **, *, ?) into a compiled regex matching posix paths."""
    if pattern in _GLOB_CACHE:
        return _GLOB_CACHE[pattern]
    pat = pattern.strip()
    if pat.endswith("/"):
        pat += "**"
    i = 0
    out = []
    while i < len(pat):
        c = pat[i]
        if c == "*":
            if pat[i : i + 3] == "**/":
                out.append("(?:.*/)?")
                i += 3
                continue
            if pat[i : i + 2] == "**":
                out.append(".*")
                i += 2
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == ".":
            out.append(r"\.")
        elif c in "+()[]{}^$|\\":
            out.append("\\" + c)
        else:
            out.append(c)
        i += 1
    rx = re.compile("^" + "".join(out) + "$")
    _GLOB_CACHE[pattern] = rx
    return rx


def glob_match(pattern: str, path: str) -> bool:
    path = path.replace(os.sep, "/").lstrip("./")
    if pattern.startswith("./"):
        pattern = pattern[2:]
    if glob_to_regex(pattern).match(path):
        return True
    # A pattern without a slash matches a basename anywhere (gitignore semantics)
    if "/" not in pattern.rstrip("/") and glob_to_regex("**/" + pattern).match(path):
        return True
    return False


def deep_get(d: Any, dotted: str, default: Any = None) -> Any:
    cur = d
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return default
    return cur


def deep_set(d: dict, dotted: str, value: Any) -> None:
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        if part not in cur or not isinstance(cur[part], dict):
            cur[part] = {}
        cur = cur[part]
    cur[parts[-1]] = value


def deep_delete(d: dict, dotted: str) -> bool:
    parts = dotted.split(".")
    cur = d
    for part in parts[:-1]:
        if not isinstance(cur, dict) or part not in cur:
            return False
        cur = cur[part]
    if isinstance(cur, dict) and parts[-1] in cur:
        del cur[parts[-1]]
        return True
    return False


def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def next_id(prefix: str, existing: Iterable[str], width: int = 4) -> str:
    mx = 0
    rx = re.compile(rf"^{re.escape(prefix)}-(\d+)$")
    for e in existing:
        m = rx.match(str(e))
        if m:
            mx = max(mx, int(m.group(1)))
    return f"{prefix}-{mx + 1:0{width}d}"


def is_text_file(path: Path, sniff: int = 2048) -> bool:
    try:
        with open(path, "rb") as f:
            b = f.read(sniff)
    except OSError:
        return False
    if b"\x00" in b:
        return False
    return True


def rel(path: Path, root: Path) -> str:
    return Path(path).resolve().relative_to(Path(root).resolve()).as_posix()
