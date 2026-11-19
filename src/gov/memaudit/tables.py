"""The governing domain and the subsystem of a question, by the repository's own tables (``config``; Interface section
4 of W2-170, W2-204 I2). A domain row and a path subsystem row are matched on the question's first source path, a
record-key subsystem row on the front matter of that file; top to bottom, the first match wins: a pattern ending in
``/**`` matches anything below its folder, a ``*`` stays inside one name, a bare name matches that file. ``none`` counts
toward no minimum and no maximum. No table is a constant here: each comes from the configuration the caller loaded."""

from __future__ import annotations

from pathlib import Path

from gov.memaudit import config as _config
from gov.memaudit.common import blob_at

NONE = "none"
APART = "nonexistent-id"  # the one category scored apart (the matcher, the scores and the pool name it too)
_matches = _config.matches
FRONT = "---"


def classify(path: str | None, table) -> str:
    """The first row ``(name, patterns)`` of ``table`` whose pattern matches ``path``; ``none`` when no row does."""
    if isinstance(path, str):
        for name, patterns in table:
            if any(_matches(path, p) for p in patterns):
                return name
    return NONE


def front_matter(raw: bytes | None) -> dict:
    """The YAML mapping between the file's first line ``---`` and the next ``---`` line; ``{}`` when it has none."""
    import yaml
    if not raw:
        return {}
    lines = raw.decode("utf-8", "replace").splitlines()
    if not lines or lines[0].strip() != FRONT:
        return {}
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == FRONT), None)
    if end is None:
        return {}
    try:
        doc = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return {}
    return doc if isinstance(doc, dict) else {}


def reader(repo, commit=None):
    """``path -> bytes or None``: the file at ``commit`` in ``repo`` (the working tree's when there is no commit), read
    once each."""
    cache: dict = {}

    def read(path: str):
        if path not in cache:
            try:
                if commit is not None:
                    cache[path] = blob_at(repo, commit, path)
                else:
                    target = (Path(repo) / path).resolve()
                    inside = str(target).startswith(str(Path(repo).resolve()) + "/")
                    cache[path] = target.read_bytes() if inside and target.is_file() else None
            except Exception:  # noqa: BLE001: a file that cannot be read has no front matter
                cache[path] = None
        return cache[path]
    return read


def domain_of(path, config) -> str:
    return classify(path, [(d.name, d.paths) for d in config.domains])


def subsystem_of(path, config, at=None) -> str:
    """The first subsystem row that holds the question: a path row by ``path``, a record-key row by the value of its
    key in the front matter of the file ``at(path)`` gives (no ``at``: such a row holds nothing)."""
    if not isinstance(path, str):
        return NONE
    front = None
    for row in config.subsystems:
        if row.record_key is None:
            if any(_matches(path, p) for p in row.paths):
                return row.name
            continue
        if at is None:
            continue
        if front is None:
            front = front_matter(at(path))
        value = front.get(row.record_key)
        if value is not None and not isinstance(value, (dict, list)) and str(value) in row.values:
            return row.name
    return NONE


def domain_min(n: int, config) -> int:
    """A domain needs at least ceil(domain_min x n / half_size) questions (integer arithmetic; 4 of 40 for Gov OS)."""
    return config.domain_min(n)


def subsystem_max(n: int, config) -> int:
    """A subsystem may hold at most floor(subsystem_max x n / half_size) questions (10 of 40 for Gov OS)."""
    return config.subsystem_max(n)


def spread(first_paths: list[str | None], config, at=None) -> tuple[dict, dict]:
    """The domain and subsystem counts (every name, ``none`` included) of the questions' first source paths."""
    domains = {name: 0 for name in [*config.domain_names, NONE]}
    subsystems = {name: 0 for name in [*config.subsystem_names, NONE]}
    for path in first_paths:
        domains[domain_of(path, config)] += 1
        subsystems[subsystem_of(path, config, at)] += 1
    return domains, subsystems


def thin_domains(domains: dict, n: int, config) -> list[str]:
    return [name for name in config.domain_names if domains.get(name, 0) < config.domain_min(n)]


def heavy_subsystems(subsystems: dict, n: int, config) -> list[str]:
    return [name for name in config.subsystem_names if subsystems.get(name, 0) > config.subsystem_max(n)]


def __getattr__(name: str):
    """``QUOTAS``, ``DOMAINS``, ``SUBSYSTEMS`` and their name lists, as an in-process reader of the old constants sees
    them: the tables of the repository the process stands in (``config.current``), never a fixed copy."""
    if name in ("QUOTAS", "DOMAINS", "SUBSYSTEMS", "DOMAIN_NAMES", "SUBSYSTEM_NAMES"):
        now = _config.current()
        return {"QUOTAS": now.quotas, "DOMAINS": [(d.name, tuple(d.paths)) for d in now.domains],
                "SUBSYSTEMS": [(s.name, tuple(s.paths or ())) for s in now.subsystems],
                "DOMAIN_NAMES": now.domain_names, "SUBSYSTEM_NAMES": now.subsystem_names}[name]
    raise AttributeError(name)
