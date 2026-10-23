"""What a close's regression run selects (W2-66; DEC-880 item 2, DEC-889 items 1 and 2, DEC-896 item 2).

A close runs what its change can reach: the ticket's own suite, ``tests/unit``, the acceptance suite of every
ticket whose ``allowed_paths`` match a changed path, a suite holding a changed file or importing a changed helper,
each declared coupling's suites, ``every_close`` and ``record_reading``. The change is every path changed since the
base, the newest commit a green record names that is ``HEAD`` or an ancestor of it.

Anything unknown or unreadable widens to the full regression, never less: a changed path under the shared core
(``SHARED_CORE``), one nothing places (``UNPLACED``), a test map that is missing or invalid
(``TEST_MAP_MISSING``, ``TEST_MAP_UNREADABLE``), no base (``BASE_UNKNOWN``) and ``--full`` (``FULL_ASKED``).

The selection keeps the full run's form: ``pytest tests`` with ``--ignore=`` for what is left out and
``--deselect=`` where a target is finer than a file.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from gov.close.repo import git as _git

MAP_REL = "governance/project/test-map.yaml"
SCHEMA_NAME = "test-map.schema.json"
SCHEMA_DIRS = ("template/governance/kernel/schemas", "governance/kernel/schemas")
DEFAULT_PER_TEST_TIMEOUT = 900
DEFAULT_DISTRIBUTION = "load"
NIGHTLY_REL = "docs/close/nightly"
UNIT = "tests/unit"
ACCEPTANCE = "tests/acceptance"
FULL_TARGET = "tests"


def match(path: str, pattern: str) -> bool:
    """``allowed_paths``' grammar, as the close reads it (``gov.guard.decide``)."""
    from gov.guard.decide import _match_pattern
    return _match_pattern(path, pattern)


def _any(path: str, patterns) -> bool:
    return any(match(path, p) for p in patterns or [])


# ---------------------------------------------------------------------------
# The test map
# ---------------------------------------------------------------------------

def _schema(root: Path) -> dict | None:
    """The map's schema: the project's kernel's, else the one beside this package's own kernel."""
    places = [Path(root) / d / SCHEMA_NAME for d in SCHEMA_DIRS]
    places.append(Path(__file__).resolve().parents[3] / SCHEMA_DIRS[0] / SCHEMA_NAME)
    for place in places:
        try:
            return json.loads(place.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
    return None


def load_map(root: Path) -> tuple[dict | None, str | None]:
    """``(map, None)``, or ``(None, reason)`` where the map is missing or cannot be read as a valid map."""
    import yaml

    path = Path(root) / MAP_REL
    if not path.is_file():
        return None, "TEST_MAP_MISSING"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, yaml.YAMLError):
        return None, "TEST_MAP_UNREADABLE"
    if not isinstance(data, dict):
        return None, "TEST_MAP_UNREADABLE"
    schema = _schema(root)
    if schema is None:  # nothing to judge it by is not a valid map
        return None, "TEST_MAP_UNREADABLE"
    try:
        import jsonschema
        jsonschema.Draft202012Validator(schema).validate(data)
    except Exception:  # noqa: BLE001 - an invalid map, or a schema that cannot judge it: both run everything
        return None, "TEST_MAP_UNREADABLE"
    return data, None


def settings(test_map: dict | None) -> tuple[float, str]:
    """``(per_test_timeout, distribution)``: the map's, else the defaults."""
    test_map = test_map or {}
    return (test_map.get("per_test_timeout", DEFAULT_PER_TEST_TIMEOUT),
            test_map.get("distribution", DEFAULT_DISTRIBUTION))


# ---------------------------------------------------------------------------
# The base and the change
# ---------------------------------------------------------------------------

def _green_heads(root: Path) -> list[str]:
    """The commits the green records of the tree name: full closes' ``evidence.head``, green nights' ``head``."""
    from gov.tasks.tickets import frontmatter

    named = []
    for path in sorted((Path(root) / "docs" / "close").glob("*/CL-*.md")):
        evidence = (frontmatter(path) or {}).get("evidence")
        if isinstance(evidence, dict) and evidence.get("scope") == "full" and isinstance(evidence.get("head"), str):
            named.append(evidence["head"])
    for path in sorted((Path(root) / NIGHTLY_REL).glob("*.json")):
        try:
            night = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(night, dict) and night.get("verdict") == "green" and isinstance(night.get("head"), str):
            named.append(night["head"])
    return list(dict.fromkeys(named))


def is_ancestor(root: Path, commit: str, of: str = "HEAD") -> bool:
    return _git(root, "merge-base", "--is-ancestor", commit, of, ok=(0, 1), code=True) == 0


def full_id(root: Path, given: str) -> str | None:
    """``given`` where it is the full id of a commit of the repository."""
    if not re.fullmatch(r"[0-9a-f]{40}", given or ""):
        return None
    found = _git(root, "rev-parse", "--verify", "--quiet", given + "^{commit}", ok=(0, 1)).strip()
    return found if found == given else None


def newest(root: Path, commits) -> str | None:
    """The newest of ``commits`` by ancestry: the one none of the others descends from (the deepest)."""
    best, depth = None, -1
    for commit in commits:
        count = int(_git(root, "rev-list", "--count", commit).strip() or 0)
        if count > depth:
            best, depth = commit, count
    return best


def base(root: Path) -> str | None:
    """The newest commit a green record names that is ``HEAD`` or an ancestor of it; None when there is none."""
    commits = [c for c in (full_id(root, given) for given in _green_heads(root)) if c and is_ancestor(root, c)]
    return newest(root, commits)


def changed(root: Path, since: str) -> list[str]:
    return sorted(set(filter(None, _git(root, "diff", "--name-only", since, "HEAD").splitlines())))


# ---------------------------------------------------------------------------
# Suites, tickets and helpers
# ---------------------------------------------------------------------------

def _norm(target: str) -> str:
    return target.rstrip("/")


def suite_of(path: str) -> str | None:
    """The suite folder holding ``path``: ``tests/unit``, or ``tests/acceptance/<x>/``."""
    if path.startswith(UNIT + "/"):
        return UNIT
    parts = path.split("/")
    if len(parts) > 3 and "/".join(parts[:2]) == ACCEPTANCE:
        return f"{ACCEPTANCE}/{parts[2]}/"
    return None


def _tickets(root: Path) -> list[tuple[str, str, list]]:
    """``(id, wbs, allowed_paths)`` of every ticket of the project, any wave."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    found = []
    for path in sorted((Path(root) / TICKETS_REL).glob("*.md")):
        front = frontmatter(path) or {}
        patterns = front.get("allowed_paths") or []
        if not isinstance(patterns, list):
            continue
        tid = str(front.get("id") or path.stem)
        wbs = str(front.get("wbs_id") or front.get("external-ref") or tid)
        found.append((tid, wbs, [p for p in patterns if isinstance(p, str)]))
    return found


def _suites(root: Path) -> list[str]:
    folder = Path(root) / ACCEPTANCE
    return sorted(f"{ACCEPTANCE}/{d.name}/" for d in folder.iterdir()
                  if d.is_dir() and not d.name.startswith((".", "__"))) if folder.is_dir() else []


def _imports(path: Path) -> set[str]:
    """The top-level module names a Python file imports."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return set()
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
            names.add(node.module.split(".")[0])
    return names


def _helper(name: str) -> bool:
    return name.endswith(".py") and not name.startswith("test_") and name != "conftest.py" \
        and name != "__init__.py"


def _helper_reach(root: Path, suites: list[str], changed_paths: list[str]) -> dict[str, set[str]]:
    """For each suite, the changed helpers of other suites it imports, directly or through another helper."""
    root = Path(root)
    helpers = {}  # module name -> its path, for every helper module of a suite folder
    for suite in suites:
        for path in sorted((root / suite).glob("*.py")):
            if _helper(path.name):
                helpers.setdefault(path.stem, path.relative_to(root).as_posix())
    reaches = {name: {helpers[name]} & set(changed_paths) for name in helpers}
    imports = {name: _imports(root / rel) & set(helpers) for name, rel in helpers.items()}
    grew = True
    while grew:  # what a helper reaches through the helpers it imports
        grew = False
        for name, imported in imports.items():
            more = set().union(*(reaches[i] for i in imported)) - reaches[name] if imported else set()
            if more:
                reaches[name] |= more
                grew = True
    found = {}
    for suite in suites:
        own = {p.stem for p in (root / suite).glob("*.py")}
        names = set().union(*(_imports(p) for p in (root / suite).rglob("*.py"))) & set(helpers)
        hit = set().union(*(reaches[n] for n in names - own)) if names - own else set()
        hit -= {p for p in hit if suite_of(p) == suite}
        if hit:
            found[suite] = hit
    return found


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def plan(root: Path, wbs: str, *, full_asked: bool = False) -> dict:
    """What the close's regression run selects, and the evidence of it (the scope's part of the block)."""
    root = Path(root)
    own = f"{ACCEPTANCE}/{wbs}/"
    test_map, map_reason = load_map(root)
    timeout, distribution = settings(test_map)
    head = _git(root, "rev-parse", "HEAD").strip()
    tree = _git(root, "rev-parse", "HEAD^{tree}").strip()
    since = base(root)
    paths = changed(root, since) if since else []

    why_full = []
    if full_asked:
        why_full.append({"reason": "FULL_ASKED"})
    if map_reason:
        why_full.append({"reason": map_reason})
    if since is None:
        why_full.append({"reason": "BASE_UNKNOWN"})

    selected: dict[str, list[dict]] = {}

    def select(target: str, why: dict):
        key = _norm(target)
        entry = next((k for k in selected if _norm(k) == key), target)
        selected.setdefault(entry, [])
        if why not in selected[entry]:
            selected[entry].append(why)

    select(own, {"reason": "OWN"})
    if test_map is not None:
        core = [p for p in paths if _any(p, test_map.get("shared_core"))]
        if core:
            why_full.append({"reason": "SHARED_CORE", "paths": core})
        tickets = _tickets(root)
        couplings = test_map.get("couplings") or []
        unplaced = [p for p in paths if not (
            suite_of(p) or _any(p, test_map.get("record_only"))
            or any(_any(p, c["paths"]) for c in couplings) or any(_any(p, t[2]) for t in tickets))]
        if unplaced:
            why_full.append({"reason": "UNPLACED", "paths": unplaced})

    if why_full:
        select(FULL_TARGET, {"reason": "FULL"})
        return {"scope": "full", "why_full": why_full, "base": since, "head": head, "tree": tree, "changed": paths,
                "selected": _listed(selected), "left_out": [], "ignore": [own], "deselect": [],
                "per_test_timeout": timeout, "distribution": distribution}

    suites = _suites(root)
    select(UNIT, {"reason": "UNIT"})
    for tid, twbs, patterns in tickets:
        hit = [p for p in paths if _any(p, patterns)]
        if hit and f"{ACCEPTANCE}/{twbs}/" in suites:
            select(f"{ACCEPTANCE}/{twbs}/", {"reason": "OVERLAP", "ticket": tid, "paths": hit})
    held = {}
    for p in paths:
        if suite_of(p):
            held.setdefault(suite_of(p), []).append(p)
    for suite, hit in held.items():
        if suite == UNIT or suite in suites:
            select(suite, {"reason": "TEST_CHANGED", "paths": hit})
    for suite, hit in sorted(_helper_reach(root, suites, paths).items()):
        for helper in sorted(hit):
            select(suite, {"reason": "HELPER", "path": helper, "paths": [helper]})
    for c in couplings:
        hit = [p for p in paths if _any(p, c["paths"])]
        if hit:
            for suite in c["suites"]:
                select(suite, {"reason": "COUPLING", "paths": hit, "coupling": c["why"]})
    for target in test_map.get("every_close") or []:
        select(target, {"reason": "EVERY_CLOSE"})
    for target in test_map.get("record_reading") or []:
        select(target, {"reason": "RECORD_READING"})

    ignore, deselect, left_out = _form(root, own, suites, list(selected))
    return {"scope": "scoped", "why_full": [], "base": since, "head": head, "tree": tree, "changed": paths,
            "selected": _listed(selected), "left_out": left_out, "ignore": ignore, "deselect": deselect,
            "per_test_timeout": timeout, "distribution": distribution}


def _listed(selected: dict) -> list[dict]:
    return [{"target": target, "why": why} for target, why in selected.items()]


def _form(root: Path, own: str, suites: list[str], targets: list[str]):
    """``(ignore, deselect, left_out)``: what ``pytest tests`` leaves out so that it runs the targets alone.

    An acceptance suite no target reaches is ignored whole; one some targets reach in part has its other test
    files ignored, and, where a target names a case of a file, the file's other top-level tests deselected."""
    root = Path(root)
    ignore, deselect, left_out = [own], [], []
    not_reached = [{"reason": "NOT_REACHED"}]
    for suite in suites:
        if suite == own:
            continue
        inside = [_norm(t) for t in targets if _norm(t) == _norm(suite) or t.startswith(suite)]
        if _norm(suite) in inside:
            continue
        if not inside:
            ignore.append(suite)
            left_out.append({"target": suite, "why": not_reached})
            continue
        files = {t.partition("::")[0] for t in inside}
        for path in sorted((root / suite).rglob("test_*.py")):
            rel = path.relative_to(root).as_posix()
            if rel in files or any(rel.startswith(f + "/") for f in files):
                continue
            ignore.append(rel)
            left_out.append({"target": rel, "why": not_reached})
        for file in sorted(files):
            cases = [t.partition("::")[2] for t in inside if t.partition("::")[0] == file]
            if "" in cases or not (root / file).is_file():
                continue  # the whole file runs
            for name in _top_level_tests(root / file):
                if not any(case == name or case.startswith(name + "::") or case.startswith(name + "[")
                           or case.startswith(name) for case in cases):
                    deselect.append(f"{file}::{name}")
    return ignore, deselect, left_out


def _top_level_tests(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
        return []
    return [node.name for node in tree.body
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"))
            or (isinstance(node, ast.ClassDef) and node.name.startswith("Test"))]


def runs(entry: str, ignore: list[str], deselect: list[str]) -> bool:
    """Whether the regression run so formed runs the case or file ``entry`` names (a serial-only entry)."""
    file = entry.partition("::")[0]
    if any(file == _norm(i) or file.startswith(_norm(i) + "/") for i in ignore):
        return False
    return not any(entry == d or entry.startswith(d + "::") or entry.startswith(d + "[") for d in deselect)
