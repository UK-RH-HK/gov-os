"""What a close's regression run selects (W2-66; DEC-880 item 2, DEC-889 items 1 and 2, DEC-896 item 2).

A close runs what its change can reach: the ticket's own suite, ``tests/unit``, the acceptance suite of every
ticket whose ``allowed_paths`` match a changed path, a suite holding a changed file or importing a changed helper,
each declared coupling's suites, ``record_reading``, and ``every_close`` when a ``record_only`` path is in the
change (DEC-1050, T-4). The change is every path changed since the base, the newest commit a green record names
that is ``HEAD`` or an ancestor of it.

Anything unknown or unreadable widens to the full regression, never less: a changed path under the shared core
(``SHARED_CORE``), one nothing places (``UNPLACED``), a test map that is missing or invalid
(``TEST_MAP_MISSING``, ``TEST_MAP_UNREADABLE``), a selected map target the head does not hold
(``UNRESOLVED_TARGET``, DEC-912 item 3), no base (``BASE_UNKNOWN``) and ``--full`` (``FULL_ASKED``).

The selection keeps the full run's form: ``pytest tests`` with ``--ignore=`` for what is left out and
``--deselect=`` where a target is finer than a file.
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from gov.close.repo import git as _git
# W2-150: the test map's places live with the fingerprints in gov.store.loader; the names stay this module's
from gov.store.loader import SCHEMA_DIRS
from gov.store.loader import TEST_MAP_REL as MAP_REL
from gov.store.loader import TEST_MAP_SCHEMA as SCHEMA_NAME

DEFAULT_PER_TEST_TIMEOUT = 900
DEFAULT_DISTRIBUTION = "load"
RETENTION_POLICY = "failed"  # DEC-905: every test run's tmp_path_retention_policy; a failing test's folder stays
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

def _green_records(root: Path) -> list[tuple[str, str]]:
    """``(record path, head)`` of each green record of the tree: full closes' ``evidence.head``, green nights'
    ``head``."""
    from gov.tasks.tickets import frontmatter

    root = Path(root)
    named = []
    for path in sorted((root / "docs" / "close").glob("*/CL-*.md")):
        evidence = (frontmatter(path) or {}).get("evidence")
        if isinstance(evidence, dict) and evidence.get("scope") == "full" and isinstance(evidence.get("head"), str):
            named.append((path.relative_to(root).as_posix(), evidence["head"]))
    for path in sorted((root / NIGHTLY_REL).glob("*.json")):
        try:
            night = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(night, dict) and night.get("verdict") == "green" and isinstance(night.get("head"), str):
            named.append((path.relative_to(root).as_posix(), night["head"]))
    return named


def _green_heads(root: Path) -> list[str]:
    """The commits the green records of the tree name: full closes' ``evidence.head``, green nights' ``head``."""
    return list(dict.fromkeys(head for _, head in _green_records(root)))


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
    """Every path changed since ``since``, read as the close's commit reader reads (``gov.close.repo``): NUL-separated,
    unquoted and without rename detection, so a moved file is in the change at the path it left and the one it
    reached."""
    names = _git(root, "-c", "core.quotePath=false", "diff", "-z", "--no-renames", "--name-only", since, "HEAD")
    return sorted(set(filter(None, names.split("\0"))))


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


def suite_folder(root: Path, front: dict, wbs: str) -> str:
    """A ticket's suite: its acceptance folder as W2-07's gate reads it (``gates.acceptance_folder``: the folder
    its file declares in ``acceptance_tests.path``, DEC-892, else ``tests/acceptance/<wbs>/``), relative to the
    project, ending in ``/``."""
    from gov.close.gates import acceptance_folder

    folder = acceptance_folder(root, front, wbs)
    try:
        return folder.relative_to(root).as_posix().rstrip("/") + "/"
    except ValueError:  # an absolute path elsewhere: the default folder's name, which then holds no test
        return f"{ACCEPTANCE}/{wbs}/"


def has_suite(root: Path, folder: str) -> bool:
    """Whether the folder holds a test file (``test_*.py``) the regression run reaches: one under ``tests/``. A
    folder elsewhere is no suite, so the ticket's paths place nothing and a change to them runs everything."""
    from gov.close.gates import has_tests

    return folder.startswith(FULL_TARGET + "/") and ".." not in folder.split("/") \
        and has_tests(Path(root) / folder)


def _tickets(root: Path) -> list[tuple[str, str, list, str, bool]]:
    """``(id, wbs, allowed_paths, suite, has_suite)`` of every ticket of the project, any wave."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    found = []
    for path in sorted((Path(root) / TICKETS_REL).glob("*.md")):
        front = frontmatter(path) or {}
        patterns = front.get("allowed_paths") or []
        if not isinstance(patterns, list):
            patterns = []
        tid = str(front.get("id") or path.stem)
        wbs = str(front.get("wbs_id") or front.get("external-ref") or tid)
        folder = suite_folder(root, front, wbs)
        found.append((tid, wbs, [p for p in patterns if isinstance(p, str)], folder, has_suite(root, folder)))
    return found


def _own(tickets: list, ticket: str | None, wbs: str) -> str:
    """The closing ticket's suite: the acceptance folder of its ticket file (found by its id, else by its WBS
    id), else ``tests/acceptance/<wbs>/``."""
    mine = [t for t in tickets if t[0] == ticket] if ticket is not None else []
    mine = mine or [t for t in tickets if t[1] == wbs]
    return mine[0][3] if mine else f"{ACCEPTANCE}/{wbs}/"


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
# The map's targets at the head
# ---------------------------------------------------------------------------

def unresolved(root: Path, targets: list[str]) -> list[tuple[str, str]]:
    """``(target, detail)`` for each target the tree closed (``HEAD`` as committed) does not hold: ``FILE_GONE``
    where its file or folder is not there, ``CASE_GONE`` where its file is there and holds no case its node id
    names, or cannot be read as Python. A node id (or its beginning) resolves through the names its file defines:
    ``f::test_x[p]``, ``f::test_x``, ``f::TestC`` and ``f::TestC::test_m``."""
    if not targets:
        return []
    files = set(filter(None, _git(root, "-c", "core.quotePath=false", "ls-tree", "-r", "-z", "--name-only",
                                  "HEAD").split("\0")))
    found = []
    for target in targets:
        path, _, case = target.partition("::")
        path = _norm(path)
        if path not in files and not (not case and any(f.startswith(path + "/") for f in files)):
            found.append((target, "FILE_GONE"))
        elif case and not _holds(_committed(root, path), [re.sub(r"\[.*\]$", "", n) for n in case.split("::")]):
            found.append((target, "CASE_GONE"))
    return found


def _committed(root: Path, path: str) -> ast.Module | None:
    """The file as ``HEAD`` holds it, parsed; None where it cannot be read or parsed."""
    try:
        return ast.parse(_git(root, "show", f"HEAD:./{path}", ok=(0, 128)))
    except (UnicodeDecodeError, SyntaxError, ValueError):
        return None


def _holds(node, names: list[str]) -> bool:
    """Whether ``node``'s body defines ``names[0]``, and that definition, a class, ``names[1:]`` in turn."""
    if node is None:
        return False
    for child in getattr(node, "body", []):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and child.name == names[0]:
            return len(names) == 1 or (isinstance(child, ast.ClassDef) and _holds(child, names[1:]))
        if len(names) == 1 and names[0] in _bound(child):
            return True
    return False


def _bound(node) -> set[str]:
    """The names a statement binds other than by ``def`` or ``class``: assignments and imports."""
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return {(a.asname or a.name).split(".")[0] for a in node.names}
    targets = node.targets if isinstance(node, ast.Assign) else [node.target] if isinstance(node, ast.AnnAssign) \
        else []
    return {t.id for t in targets if isinstance(t, ast.Name)}


# ---------------------------------------------------------------------------
# The plan
# ---------------------------------------------------------------------------

def plan(root: Path, wbs: str, *, full_asked: bool = False, ticket: str | None = None) -> dict:
    """What the close's regression run selects, and the evidence of it (the scope's part of the block). The
    closing ticket is ``ticket`` (its id), else the ticket of ``wbs``."""
    root = Path(root)
    tickets = _tickets(root)
    own = _own(tickets, ticket, wbs)
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

    if ".." not in own.split("/") and (root / own).is_dir():  # every target named exists in the tree closed
        select(own, {"reason": "OWN"})
    if test_map is not None:
        core = [p for p in paths if _any(p, test_map.get("shared_core"))]
        if core:
            why_full.append({"reason": "SHARED_CORE", "paths": core})
        couplings = test_map.get("couplings") or []
        # a ticket without a suite maps a path to no suite: its allowed_paths place nothing
        unplaced = [p for p in paths if p not in core and not (
            suite_of(p) or _any(p, test_map.get("record_only"))
            or any(_any(p, c["paths"]) for c in couplings) or any(t[4] and _any(p, t[2]) for t in tickets))]
        if unplaced:
            why_full.append({"reason": "UNPLACED", "paths": unplaced})
        # DEC-912 item 3: a selected map target the tree closed does not hold (renamed or gone) runs everything
        mapped = [t for c in couplings if any(_any(p, c["paths"]) for p in paths) for t in c["suites"]]
        mapped += list(test_map.get("every_close") or []) + list(test_map.get("record_reading") or [])
        why_full.extend({"reason": "UNRESOLVED_TARGET", "target": target, "detail": detail}
                        for target, detail in unresolved(root, list(dict.fromkeys(mapped))))

    if why_full:
        select(FULL_TARGET, {"reason": "FULL"})
        return {"scope": "full", "why_full": why_full, "base": since, "head": head, "tree": tree, "changed": paths,
                "selected": _listed(selected), "left_out": [], "ignore": [own], "deselect": [],
                "per_test_timeout": timeout, "distribution": distribution,
                "tmp_path_retention_policy": RETENTION_POLICY}

    suites = _suites(root)
    select(UNIT, {"reason": "UNIT"})
    for tid, _, patterns, folder, held_tests in tickets:
        hit = [p for p in paths if _any(p, patterns)]
        if hit and held_tests:
            select(folder, {"reason": "OVERLAP", "ticket": tid, "paths": hit})
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
    # DEC-1050 (T-4): every_close joins the selection only when a record-only path is in the change (a code change
    # alone leaves it to the full suite); record_reading, without W2-54's whole gov check (the map), joins every one
    if any(_any(p, test_map.get("record_only")) for p in paths):
        for target in test_map.get("every_close") or []:
            select(target, {"reason": "EVERY_CLOSE"})
    for target in test_map.get("record_reading") or []:
        select(target, {"reason": "RECORD_READING"})

    ignore, deselect, left_out = _form(root, own, suites, list(selected))
    return {"scope": "scoped", "why_full": [], "base": since, "head": head, "tree": tree, "changed": paths,
            "selected": _listed(selected), "left_out": left_out, "ignore": ignore, "deselect": deselect,
            "per_test_timeout": timeout, "distribution": distribution,
            "tmp_path_retention_policy": RETENTION_POLICY}


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
                # pytest deselects by the id's beginning: a name that begins a target's is kept, so it runs too
                if not any(case.startswith(name) for case in cases):
                    deselect.append(f"{file}::{name}")
                    left_out.append({"target": f"{file}::{name}", "why": not_reached})
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


# ---------------------------------------------------------------------------
# The scoped selection (W2-115 S2, S3; DEC-953 item 4, DEC-968, DEC-1001 (a))
# ---------------------------------------------------------------------------
#
# The scoped close's one selection, also printed by ``gov close --select``: the ticket's own suite and every suite
# its change can reach, never the full suite. The change is the ticket's own: the paths of HEAD's commits whose
# trailers hold ``Task: <ticket>`` (merges bring no path of their own). For each changed path:
#   - a coupling that names it selects its suites (the map's explicit word, for any path);
#   - a record place (``record_only``) or a governance-overlay path (``governance/project/``, ``.gov-runtime/``)
#     selects nothing else by itself; records in the change select ``record_reading``;
#   - a test file selects itself; another file of a test folder (a helper, a conftest) selects its folder;
#   - a path a ticket with a suite holds in its ``allowed_paths`` selects that suite;
#   - a Python module selects every test file that imports it, directly or through other modules, or names it
#     (``python -m <module>``): the import graph; a shared-core path is read the same way, never as "everything".
# A code path that none of these reaches is unmapped: the selection is refused (``SelectionRefused``), never
# widened. So is an unreadable test map, a selected target the head does not hold, and a target that would be the
# whole of ``tests/``.

GOVERNANCE_OVERLAY = ("governance/project/", ".gov-runtime/")
SELECTION_REFUSED = "SELECTION_REFUSED"
PYTEST_OPTIONS = ["-p", "no:cacheprovider", "-o", f"tmp_path_retention_policy={RETENTION_POLICY}",
                  "-o", "junit_family=xunit1"]
_SKIP_DIRS = {".git", ".gov-runtime", "node_modules", "__pycache__", ".venv", "venv", ".tox", ".mypy_cache"}


class SelectionRefused(Exception):
    """A selection that cannot be made; ``reason`` says why (S2: never widened)."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _is_test_file(rel: str) -> bool:
    name = rel.rsplit("/", 1)[-1]
    return name.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def ticket_change(root: Path, ticket: str) -> tuple[list[str], str | None]:
    """``(paths, base)``: every path the ticket's own commits change, and the head without them: the first parent
    of the oldest of its non-merge commits (None when it has none)."""
    from gov.close.repo import ticket_commits

    commits = ticket_commits(Path(root), ticket)
    own = [c for c in commits if len(c["parents"]) <= 1]
    paths = sorted({p for c in own for p in c["paths"]})
    oldest = own[-1] if own else None
    base_commit = oldest["parents"][0] if oldest and oldest["parents"] else None
    return paths, base_commit


def _module_of(rel: str) -> str | None:
    """The dotted module a Python file is: under ``src/`` relative to it, else relative to the project."""
    if not rel.endswith(".py"):
        return None
    parts = rel[:-3].split("/")
    if parts[0] == "src" and len(parts) > 1:
        parts = parts[1:]
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts) if parts and all(p.isidentifier() for p in parts) else None


def _python_files(root: Path) -> list[str]:
    found = []
    for path in sorted(Path(root).rglob("*.py")):
        rel = path.relative_to(root)
        if any(part in _SKIP_DIRS for part in rel.parts[:-1]):
            continue
        found.append(rel.as_posix())
    return found


def _imported(rel: str, tree: ast.Module) -> set[str]:
    """Every dotted name a file's imports may mean: ``a.b.c`` and each of its beginnings, ``from a import b`` as
    ``a.b`` and ``a``; relative imports resolved against the file's own package."""
    package = (_module_of(rel) or "").split(".")
    if not rel.endswith("__init__.py"):
        package = package[:-1]
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                anchor = package[:len(package) - (node.level - 1)] if node.level - 1 <= len(package) else []
                module = ".".join(anchor + ([node.module] if node.module else []))
            else:
                module = node.module or ""
            if module:
                names.add(module)
                names.update(f"{module}.{alias.name}" for alias in node.names if alias.name != "*")
    out = set()
    for name in names:
        parts = name.split(".")
        out.update(".".join(parts[:i]) for i in range(1, len(parts) + 1))
    return out


def import_reach(root: Path, changed_modules: list[str]) -> dict[str, set[str]]:
    """For each changed module, the test files (relative paths) that import it, directly or through other files,
    or name it as text (a ``python -m`` call). Test helpers are reached by their bare name as well."""
    root = Path(root)
    files = _python_files(root)
    modules: dict[str, str] = {}
    for rel in files:
        name = _module_of(rel)
        if name:
            modules.setdefault(name, rel)
        if rel.startswith("tests/"):  # a helper beside its tests is imported by its bare name
            modules.setdefault(rel.rsplit("/", 1)[-1][:-3], rel)
    importers: dict[str, set[str]] = {}
    texts: dict[str, str] = {}
    for rel in files:
        try:
            text = (root / rel).read_text(encoding="utf-8")
            tree = ast.parse(text)
        except (OSError, UnicodeDecodeError, SyntaxError, ValueError):
            continue
        if _is_test_file(rel):
            texts[rel] = text
        for name in _imported(rel, tree):
            target = modules.get(name)
            if target and target != rel:
                importers.setdefault(target, set()).add(rel)
    found = {}
    for module in changed_modules:
        start = modules.get(module)
        seen, todo = set(), [start] if start else []
        while todo:
            current = todo.pop()
            for importer in importers.get(current, ()):
                if importer not in seen:
                    seen.add(importer)
                    todo.append(importer)
        hits = {rel for rel in seen if _is_test_file(rel)}
        hits |= {rel for rel, text in texts.items() if "." in module and module in text}
        found[module] = hits
    return found


def _within(target: str, other: str) -> bool:
    """Whether ``target`` lies inside the folder or file ``other`` names (and is not it)."""
    t, o = _norm(target.partition("::")[0]), _norm(other.partition("::")[0])
    if t == o:
        return "::" in target and "::" not in other
    return t.startswith(o + "/")


def _bookkeeping(root: Path, ticket: str, paths: list[str]) -> bool:
    """Whether every record place of ``paths`` is only bookkeeping (S2, the governance-alone rule): the ticket's own
    ticket file, its own close record or checkpoint, or a green record (written after the head it names, so always
    in the change counted from that head). Read narrowly: another ticket's file or record, and any other record
    place, is a record change."""
    from gov.tasks.tickets import TICKETS_REL

    green = {rec for rec, _ in _green_records(root)}
    own = (f"docs/close/{ticket}/", f"docs/checkpoints/{ticket}/")
    return all(p == f"{TICKETS_REL}/{ticket}.md" or p.startswith(own) or p in green for p in paths)


def scoped(root: Path, ticket: str) -> dict:
    """The scoped selection of ``ticket``: ``{"ticket", "suites", "pytest_options", "changed", "why", "base",
    "head"}``; ``SelectionRefused`` with its reason where it cannot be made."""
    from gov.tasks.tickets import TICKETS_REL, frontmatter

    root = Path(root)
    front = frontmatter(root / TICKETS_REL / f"{ticket}.md")
    if front is None:
        raise SelectionRefused(f"{ticket} is not a ticket of this project")
    wbs = str(front.get("wbs_id") or front.get("external-ref") or ticket)
    test_map, why_not = load_map(root)
    if test_map is None:
        raise SelectionRefused(f"the test map {MAP_REL} cannot be read ({why_not}): no selection is made blind")
    own_paths, base_commit = ticket_change(root, ticket)
    # the change is what the head holds that no green record has tested: everything since the newest green record
    # (the strict close's base), with the ticket's own commits; a ticket's own commits alone without a green record
    green = base(root)
    paths = sorted(set(own_paths) | set(changed(root, green))) if green else own_paths
    tickets = _tickets(root)
    couplings = test_map.get("couplings") or []
    why: dict[str, list[str]] = {}

    def select(target: str, reason: str) -> None:
        why.setdefault(target, [])
        if reason not in why[target]:
            why[target].append(reason)

    own = suite_folder(root, front, wbs)
    # records or governance files alone select only record_reading, or nothing (S2: "and nothing else"); any other
    # change, and a ticket without a change of its own, runs the ticket's own suite
    records_only = bool(paths) and all(_any(p, test_map.get("record_only")) or p.startswith(GOVERNANCE_OVERLAY)
                                       for p in paths)
    if not records_only:
        if has_suite(root, own):
            select(own, "OWN")
    records, code, placed, modules = [], [], {}, {}
    for p in paths:
        hit = False
        for c in couplings:
            if _any(p, c.get("paths")):
                for suite in c.get("suites") or []:
                    select(suite, f"COUPLING {p}")
                hit = True
        if _any(p, test_map.get("record_only")):
            records.append(p)
            continue
        if p.startswith(GOVERNANCE_OVERLAY):
            continue
        code.append(p)
        if suite_of(p) is not None or p.startswith(FULL_TARGET + "/"):
            if _is_test_file(p):
                select(p, "TEST_CHANGED")
                hit = True
            elif p.rsplit("/", 1)[0] not in (FULL_TARGET, ACCEPTANCE):
                select(p.rsplit("/", 1)[0] + "/", f"TEST_FOLDER {p}")
                hit = True
        for tid, _, patterns, folder, held in tickets:
            if held and _any(p, patterns):
                select(folder, f"OVERLAP {tid} {p}")
                hit = True
        stem = p.rsplit("/", 1)[-1][:-3] if p.endswith(".py") else ""
        module = _module_of(p) or (stem if p.startswith(FULL_TARGET + "/") and stem.isidentifier() else None)
        if module:
            modules[module] = p
        placed[p] = hit
    if modules:
        reach = import_reach(root, list(modules))
        for module, p in modules.items():
            for rel in reach.get(module, ()):
                select(rel, f"IMPORTS {p}")
                placed[p] = True
    unplaced = [p for p, hit in placed.items() if not hit]
    if unplaced:
        raise SelectionRefused(f"{len(unplaced)} changed path(s) nothing maps to a suite (no coupling, no ticket "
                               f"with a suite holds them, no test imports them): {', '.join(sorted(unplaced))}")
    governance = [p for p in paths if p.startswith(GOVERNANCE_OVERLAY) and not _any(p, test_map.get("record_only"))]
    if records and not code and governance and _bookkeeping(root, ticket, records):
        # S2: governance files select nothing by themselves; the ticket's own bookkeeping beside them (its ticket
        # file, its close record and checkpoint, the green records the change is counted from) is no record change
        records = []
    if records:
        for target in test_map.get("record_reading") or []:
            select(target, "RECORD_READING")
        if code:
            for target in test_map.get("every_close") or []:
                select(target, "EVERY_CLOSE")
    whole = [t for t in why if _norm(t) in (FULL_TARGET, ACCEPTANCE, "", ".")]
    if whole:
        raise SelectionRefused(f"the selection would run the whole of {', '.join(whole)}: the full suite runs only "
                               "in the nightly; name the reached suites in the test map's couplings")
    gone = unresolved(root, list(why))
    if gone:
        raise SelectionRefused("the head does not hold a selected target: "
                               + ", ".join(f"{t} ({d})" for t, d in gone))
    suites = sorted(t for t in why if not any(_within(t, o) for o in why if o != t))
    return {"ticket": ticket, "suites": suites, "pytest_options": pytest_options(test_map),
            "changed": paths, "own": own_paths, "green_base": green, "records_only": records_only, "why": {t: why[t] for t in suites}, "base": base_commit,
            "head": _git(root, "rev-parse", "HEAD").strip()}


def pytest_options(test_map: dict | None) -> list[str]:
    """The options every scoped run takes besides its targets: no cache, the retention policy, JUnit's node
    files, and the test map's per-test limit (``--timeout``, pytest-timeout's), so a test that hangs fails as a
    timeout (S4) instead of ending the whole run. The same on every machine whatever the caller's environment: where
    the runs' interpreter lacks pytest-timeout, pytest refuses the option and the run does not complete (fail closed,
    as the strict close's ``TIMEOUT_PLUGIN_ABSENT``)."""
    return list(PYTEST_OPTIONS) + [f"--timeout={settings(test_map)[0]}"]
