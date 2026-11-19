"""A repository's own memory-audit configuration, ``governance/project/memory-audit.yaml`` (W2-204 I1, I2; S1-S3, F4).

The domain table, the subsystem table, the categories with their quotas, the spread rule, the paths left unread and the
control set are the repository's, never a constant of this package: every step loads them here, and a repository
without the file is refused (no silent default). ``load(repo, commit=None)`` resolves the file named by the environment
variable ``MEMAUDIT_CONFIG`` when it is set and not empty (a trial before a commit), else the blob at ``commit``, else
the file in ``repo``'s working tree. A fault raises ``ConfigError``; its ``line`` is what ``say`` prints, and it names a
key path and a fixed reason only, never the file's text. Only the first fault is named.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from pathlib import Path

from gov.memaudit.common import GitError, blob_at, git, z_list

PATH = "governance/project/memory-audit.yaml"
ENV = "MEMAUDIT_CONFIG"
APART = "nonexistent-id"
NONE = "none"
MISSING = "MA-CONFIG-MISSING"
TOP = ("version", "repository", "half_size", "categories", "domains", "subsystems", "spread", "exclude", "control")
REQUIRED = ("version", "repository", "half_size", "categories", "domains", "subsystems", "control")
# the spread rule when the file states none: 4 of 40 for a domain, 10 of 40 for a subsystem, scaled to the half
DEFAULT_SPREAD = (4, 10, 40)
MIN_KEPT = (36, 40)  # a half is delivered and kept at 36 of 40 or more, scaled to the half's size


class ConfigError(Exception):
    """The file is absent or faulty: ``code`` is the line's first word, ``detail`` the rest."""

    def __init__(self, code: str, detail: str = ""):
        super().__init__(code)
        self.code, self.detail = code, detail

    @property
    def line(self) -> str:
        return f"{self.code} {self.detail}" if self.detail else self.code


def missing() -> ConfigError:
    return ConfigError(MISSING, f"write {PATH}")


def _form(path: str, reason: str) -> ConfigError:
    return ConfigError("MA-CONFIG-FORM", f"{path}: {reason}")


def _key(path: str) -> ConfigError:
    return ConfigError("MA-CONFIG-KEY", path)


# ---- the patterns (as ``tables._matches``)

def matches(path: str, pattern: str) -> bool:
    """A pattern ending ``/**`` matches anything below its folder, a ``*`` stays inside one name, a bare name is that
    file."""
    below = pattern.endswith("/**")
    stem = pattern[:-3] if below else pattern
    if "*" not in stem:
        return path.startswith(stem + "/") if below else path == stem
    rx = "".join("[^/]*" if c == "*" else re.escape(c) for c in stem) + ("/.*" if below else "")
    return re.fullmatch(rx, path, re.S) is not None


def matches_any(path, patterns) -> bool:
    return isinstance(path, str) and any(matches(path, p) for p in patterns)


# ---- the loaded form

@dataclass(frozen=True)
class Category:
    name: str
    count: int
    about: str = ""


@dataclass(frozen=True)
class Domain:
    name: str
    paths: list


@dataclass(frozen=True)
class Subsystem:
    """A path row (``paths``) or a record-key row (``record_key``, ``values``)."""
    name: str
    paths: list | None = None
    record_key: str | None = None
    values: list | None = None


@dataclass(frozen=True)
class Spread:
    domain_min: int
    subsystem_max: int


@dataclass(frozen=True)
class Control:
    set: str
    part: str
    size: int
    baseline: object  # an integer, or the word ``first``
    spread: int


@dataclass(frozen=True)
class Config:
    version: int
    repository: str
    half_size: int
    categories: list
    domains: list
    subsystems: list
    spread: Spread
    exclude: list
    control: Control | None  # None: ``control: none``

    # ---- names and counts
    @property
    def quotas(self) -> dict:
        return {c.name: c.count for c in self.categories}

    @property
    def domain_names(self) -> list:
        return [d.name for d in self.domains]

    @property
    def subsystem_names(self) -> list:
        return [s.name for s in self.subsystems]

    @property
    def min_kept(self) -> int:
        """The fewest questions a half may hold: ceil(36 n / 40) of its size."""
        return -(-MIN_KEPT[0] * self.half_size // MIN_KEPT[1])

    def domain_min(self, n: int) -> int:
        """A domain needs at least ceil(domain_min x n / half_size) of n questions (integer arithmetic)."""
        return -(-self.spread.domain_min * n // self.half_size)

    def subsystem_max(self, n: int) -> int:
        """A subsystem may hold at most floor(subsystem_max x n / half_size) of n questions."""
        return self.spread.subsystem_max * n // self.half_size

    def excluded(self, path) -> bool:
        return matches_any(path, self.exclude)

    @property
    def record_keyed(self) -> bool:
        return any(s.record_key is not None for s in self.subsystems)


# ---- validation: the first fault only

def _int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _text(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _strings(v, path: str, *, empty: bool = False) -> list:
    if not isinstance(v, list) or (not v and not empty):
        raise _form(path, "not a list of strings")
    for i, x in enumerate(v):
        if not _text(x):
            raise _form(f"{path}[{i}]", "not a string")
    return list(v)


def _rows(v, path: str, *, empty: bool) -> list:
    if not isinstance(v, list) or (not v and not empty):
        raise _form(path, "not a list of rows")
    for i, row in enumerate(v):
        if not isinstance(row, dict) or not all(isinstance(k, str) for k in row):
            raise _form(f"{path}[{i}]", "not a mapping")
    return v


def _row(row: dict, path: str, known, required) -> None:
    for k in row:
        if k not in known:
            raise _key(f"{path}.{k}")
    for k in required:
        if k not in row:
            raise _form(f"{path}.{k}", "missing")


def _name(row: dict, path: str) -> str:
    if "name" in row and not _text(row["name"]):
        raise _form(f"{path}.name", "not a string")
    return row.get("name")


def _categories(v) -> list:
    out = []
    for i, row in enumerate(_rows(v, "categories", empty=False)):
        at = f"categories[{i}]"
        for k in row:
            if k not in ("name", "count", "about"):
                raise _key(f"{at}.{k}")
        _name(row, at)
        if "count" in row and (not _int(row["count"]) or row["count"] < 0):
            raise _form(f"{at}.count", "not a count")
        if "about" in row and not isinstance(row["about"], str):
            raise _form(f"{at}.about", "not a string")
        _row(row, at, ("name", "count", "about"), ("name", "count"))
        out.append(Category(row["name"], row["count"], row.get("about", "")))
    return out


def _domains(v) -> list:
    out = []
    for i, row in enumerate(_rows(v, "domains", empty=False)):
        at = f"domains[{i}]"
        for k in row:
            if k not in ("name", "paths"):
                raise _key(f"{at}.{k}")
        _name(row, at)
        if "paths" in row:
            _strings(row["paths"], f"{at}.paths")
        _row(row, at, ("name", "paths"), ("name", "paths"))
        out.append(Domain(row["name"], list(row["paths"])))
    return out


def _subsystems(v) -> list:
    out = []
    for i, row in enumerate(_rows(v, "subsystems", empty=True)):
        at = f"subsystems[{i}]"
        for k in row:
            if k not in ("name", "paths", "record_key", "values"):
                raise _key(f"{at}.{k}")
        _name(row, at)
        if "paths" in row:
            _strings(row["paths"], f"{at}.paths")
        if "record_key" in row and not _text(row["record_key"]):
            raise _form(f"{at}.record_key", "not a string")
        if "values" in row:
            _strings(row["values"], f"{at}.values")
        if "name" not in row:
            raise _form(f"{at}.name", "missing")
        by_path, by_key = "paths" in row, "record_key" in row or "values" in row
        if by_path and by_key:
            raise _form(at, "paths and a record key in one row")
        if not by_path and not by_key:
            raise _form(f"{at}.paths", "missing")
        if by_key:
            for k in ("record_key", "values"):
                if k not in row:
                    raise _form(f"{at}.{k}", "missing")
            out.append(Subsystem(row["name"], record_key=row["record_key"], values=list(row["values"])))
        else:
            out.append(Subsystem(row["name"], paths=list(row["paths"])))
    return out


def _spread(v) -> Spread:
    if not isinstance(v, dict) or not all(isinstance(k, str) for k in v):
        raise _form("spread", "not a mapping")
    for k in v:
        if k not in ("domain_min", "subsystem_max"):
            raise _key(f"spread.{k}")
        if not _int(v[k]) or v[k] < 0:
            raise _form(f"spread.{k}", "not a count")
    for k in ("domain_min", "subsystem_max"):
        if k not in v:
            raise _form(f"spread.{k}", "missing")
    return Spread(v["domain_min"], v["subsystem_max"])


def _control(v) -> Control | None:
    if v == NONE:
        return None
    if not isinstance(v, dict) or not all(isinstance(k, str) for k in v):
        raise _form("control", "not a mapping or none")
    known = ("set", "part", "size", "baseline", "spread")
    for k in v:
        if k not in known:
            raise _key(f"control.{k}")
        value = v[k]
        if k in ("set", "part") and not _text(value):
            raise _form(f"control.{k}", "not a string")
        if k == "size" and (not _int(value) or value < 1):
            raise _form("control.size", "not a count")
        if k == "spread" and (not _int(value) or value < 0):
            raise _form("control.spread", "not a count")
        if k == "baseline" and not ((_int(value) and value >= 0) or value == "first"):
            raise _form("control.baseline", "not an integer or first")
    for k in known:
        if k not in v:
            raise _form(f"control.{k}", "missing")
    return Control(v["set"], v["part"], v["size"], v["baseline"], v["spread"])


def _unique(rows, path: str) -> None:
    seen = set()
    for i, row in enumerate(rows):
        if row.name in seen:
            raise _form(f"{path}[{i}].name", "a duplicate name")
        seen.add(row.name)


def parse(raw: bytes) -> Config:
    """The file's bytes as a ``Config``; the first fault raises (the tracked files are not looked at here)."""
    from gov.util.parts import load_yaml_unique
    try:
        doc = load_yaml_unique(raw.decode("utf-8"))
    except Exception:  # noqa: BLE001: the parser's own words would carry the file's text
        raise _form("", "not readable as YAML") from None
    if not isinstance(doc, dict) or not all(isinstance(k, str) for k in doc):
        raise _form("", "not a mapping")
    got = {}
    for k, v in doc.items():
        if k not in TOP:
            raise _key(k)
        if k == "version":
            if v != 1 or not _int(v):
                raise _form("version", "not 1")
        elif k == "repository":
            if not _text(v):
                raise _form("repository", "not a string")
        elif k == "half_size":
            if not _int(v) or v < 1:
                raise _form("half_size", "not a count")
        elif k == "categories":
            v = _categories(v)
        elif k == "domains":
            v = _domains(v)
        elif k == "subsystems":
            v = _subsystems(v)
        elif k == "spread":
            v = _spread(v)
        elif k == "exclude":
            v = _strings(v, "exclude", empty=True)
        elif k == "control":
            v = _control(v)
        got[k] = v
    for k in REQUIRED:
        if k not in got:
            raise _form(k, "missing")
    for k in ("categories", "domains", "subsystems"):
        _unique(got[k], k)
    for k in ("domains", "subsystems"):  # ``none`` is the count of the questions no row holds
        if NONE in [row.name for row in got[k]]:
            raise _form(k, "none is not a name")
    half = got["half_size"]
    if APART not in [c.name for c in got["categories"]]:
        raise _form("categories", f"{APART} absent")
    total = sum(c.count for c in got["categories"])
    if total != half:
        raise ConfigError("MA-CONFIG-QUOTA", f"sum {total} of {half}")
    spread = got.get("spread")
    if spread is None:
        d, s, per = DEFAULT_SPREAD
        spread = Spread(-(-d * half // per), s * half // per)
    return Config(version=1, repository=got["repository"], half_size=half, categories=got["categories"],
                  domains=got["domains"], subsystems=got["subsystems"], spread=spread,
                  exclude=got.get("exclude") or [], control=got["control"])


# ---- loading

def _raw(repo, commit) -> bytes:
    named = os.environ.get(ENV)
    if named:
        try:
            return Path(os.path.expanduser(named)).read_bytes()
        except OSError:
            raise missing() from None
    if repo is None:
        raise missing()
    if commit is not None:
        try:
            raw = blob_at(repo, commit, PATH)
        except GitError:
            raw = None
    else:
        try:
            raw = (Path(repo) / PATH).read_bytes()
        except OSError:
            raw = None
    if raw is None:
        raise missing()
    return raw


def check_domains(config: Config, repo, tree: str) -> None:
    """``MA-CONFIG-DOMAIN-EMPTY <name>`` for the first domain no tracked file of ``tree`` matches."""
    tracked = z_list(git(repo, "ls-tree", "-r", "--name-only", "-z", tree))
    for d in config.domains:
        if not any(matches_any(path, d.paths) for path in tracked):
            raise ConfigError("MA-CONFIG-DOMAIN-EMPTY", d.name)


def load(repo, commit=None, *, tree=None) -> Config:
    """The repository's configuration (see the module's text for where the file is taken from). With ``commit`` (or
    ``tree``, a revision whose tracked files are looked at while the file is the working tree's) every domain must
    match a tracked file there."""
    config = parse(_raw(repo, commit))
    at = commit if commit is not None else tree
    if at is not None and repo is not None:
        check_domains(config, repo, at)
    return config


def recorded(repo, commit):
    """``commit`` when it is a 40-hex commit ``repo`` holds (a step that reads the audit commit from its own record:
    ``void``, ``judge``), else None."""
    from gov.memaudit.common import HEX40, git_code
    if repo is None or not isinstance(commit, str) or not HEX40.fullmatch(commit):
        return None
    return commit if git_code(repo, "cat-file", "-e", f"{commit}^{{commit}}") == 0 else None


def current() -> Config:
    """The configuration of the repository the process stands in (``MEMAUDIT_CONFIG`` first): for a caller that has
    no ``--repo``."""
    from gov.memaudit.common import UsageError, toplevel
    try:
        top = toplevel()
    except UsageError:
        top = None
    return load(top)
