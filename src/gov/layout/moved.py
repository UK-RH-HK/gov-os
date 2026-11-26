"""The repository after the hand moves, against the same plan (SL-14). No earlier run is kept: what was held is read
from what code names now, and the plan says the rest."""

from __future__ import annotations

from gov.layout import CannotRun
from gov.layout.checks import ancestors
from gov.layout.namespaces import policies, study_memory
from gov.layout.plan import Line, finding
from gov.layout.repo import Repo
from gov.layout.references import resolve
from gov.layout.rewrites import KEPT, REWRITE, held_items, moved_to, own_links, scan, treatment
from gov.layout.rules import under
from gov.layout.standard import ASK, Standard
from gov.util.parts import PATH_MAP_REL, load_yaml_unique
from gov.util.patterns import _match_pattern


def check(repo: Repo, std: Standard, lines: list[Line]) -> tuple[list, list, list]:
    """``(findings, held, kept)`` of the moved repository; each line is told the items that are its own now."""
    for line in lines:
        line.moving = (std.moves(line.cls) and line.kind not in ("declared", "ignored-root")
                       and bool(line.dest) and line.dest != line.path)
    moving = {line.path: line for line in lines if line.moving}
    at = _places(lines)

    def line_of(path: str) -> Line | None:
        return next((at[head] for head in ancestors(path) if head in at), None)

    targets = {path: _folder(repo, line) for path, line in moving.items()}
    found = list(scan(repo, std, line_of, targets))
    held = held_items(found, repo, std, moving)
    for path in repo.items:
        line = line_of(path)
        if line is not None:
            line.items.append(path)
    faults = _moves(repo, lines, held)
    faults += _unplanned(repo, lines)
    faults += _stale(repo, std, found, held, moving, line_of)
    faults += _map(repo, std, lines, line_of)
    kept = sorted({(path, mentioned) for path, line, mentioned, item in found
                   if item not in held and treatment(repo, std, line, path) == KEPT})
    return (faults, [{"path": item, "by": by} for item in sorted(held) for by in sorted(held[item])],
            [{"path": path, "target": mentioned, "new": moved_to(moving, mentioned)} for path, mentioned in kept])


def _places(lines: list[Line]) -> dict[str, Line]:
    """The line of each place: a destination first, else a line's own path."""
    at = {line.path: line for line in lines}
    at.update({line.dest: line for line in lines if line.dest})
    return at


def _folder(repo: Repo, line: Line) -> bool:
    if line.kind == "folder":
        return True
    return line.kind == "untracked" and not repo.is_file(line.dest) and not repo.is_file(line.path)


def _moves(repo: Repo, lines: list[Line], held: dict) -> list[dict]:
    found = []

    def fault(line: Line, why: str) -> None:
        found.append(finding("LAYOUT_MOVE", line.number, line.path, why, other=line.dest))

    for line in lines:
        old, new = repo.exists(line.path), line.dest != line.path and repo.exists(line.dest)
        if line.path in held:
            if new:
                fault(line, f"held (code names it), yet moved to {line.dest}")
            elif not old:
                fault(line, "held, and no longer where it was")
        elif line.moving:
            if old:
                fault(line, f"not moved: {line.path} is still there, planned to {line.dest}")
            if not new:
                fault(line, f"nothing is at its destination {line.dest}")
        elif not old and line.kind != "declared":
            fault(line, "it stays by the plan, and is not where it was")
    return found


def _unplanned(repo: Repo, lines: list[Line]) -> list[dict]:
    planned = {line.path for line in lines} | {line.dest for line in lines if line.dest}
    return [finding("LAYOUT_MOVE", None, path, "no plan line names this item or a folder above it")
            for path, kind in sorted(repo.items.items())
            if kind in ("file", "untracked") and not any(head in planned for head in ancestors(path))]


def _stale(repo: Repo, std: Standard, found: list, held: dict, moving: dict, line_of) -> list[dict]:
    """A rewrite the plan listed that was not made: a document still naming an old path, or a moved document's link
    still written from its old place."""
    stale = set()
    for path, line, mentioned, item in found:
        if item not in held and treatment(repo, std, line, path) == REWRITE and not any(
                under(path, each) for each in held):
            stale.add((path, mentioned))
    before = {}  # each moved document's old path
    for path in repo.blobs:
        line = line_of(path)
        if line is not None and line.moving and line.path not in held and under(path, line.dest):
            before[path] = line.path + path[len(line.dest):]
    for path, raw, target in own_links(repo, std, {path: line_of(path) for path in before}):
        old = resolve(before[path], raw)
        if old and old != target and not repo.exists(target) and not any(under(old, each) for each in held) \
                and (repo.exists(old) or any(under(old, each) for each in moving)):
            stale.add((path, old))
    return [finding("LAYOUT_MOVE", None, path, f"{path} still names the old path of {target}", other=target)
            for path, target in sorted(stale)]


def _map(repo: Repo, std: Standard, lines: list[Line], line_of) -> list[dict]:
    """The repository's own path map against the classes the plan gives (M1, M2)."""
    try:
        document = load_yaml_unique((repo.root / PATH_MAP_REL).read_text(encoding="utf-8"))
        spaces = {name: (entry, list(entry["paths"])) for name, entry in document["namespaces"].items()}
    except Exception as error:  # noqa: BLE001 - whatever keeps the map from being read, nothing is judged by it
        raise CannotRun(f"{PATH_MAP_REL} cannot be read for its namespaces: {type(error).__name__}") from None
    imports: dict[str, list[Line]] = {}
    for line in lines:
        if std.whole(line.cls) and line.name:
            imports.setdefault(line.name, []).append(line)
    studies = study_memory(repo, std, imports)
    found = []
    for path, kind in sorted(repo.items.items()):
        if kind not in ("file", "submodule") and path != repo.plan_rel:
            continue
        places = [path, path + "/"] if kind == "submodule" else [path]
        over = sorted(name for name, (_, globs) in spaces.items()
                      if any(_match_pattern(place, glob) for place in places for glob in globs))
        line = line_of(path)
        number = line.number if line else None
        if len(over) != 1:
            found.append(finding("LAYOUT_MAP", number, path,
                                 "the path map places it in " + (", ".join(over) if over else "no namespace")))
            continue
        if line is None or line.cls == ASK or line.cls not in std.classes:
            continue
        memory = studies[line.name][1] if line.name in studies and std.whole(line.cls) else std.classes[line.cls][
            "memory"]
        wrong = _policy_faults(spaces[over[0]][0], memory,
                               line.text("stale_class") if std.stale(line.cls) else None)
        if wrong:
            found.append(finding("LAYOUT_MAP", number, path,
                                 f"namespace {over[0]} does not hold the policy of class {line.cls}: {wrong}",
                                 other=over[0]))
    return found


def _policy_faults(entry: dict, memory: str, stale: str | None) -> str:
    """What of the namespace ``entry`` is not as ``memory`` and ``stale`` ask; empty when all is."""
    wanted = policies(memory)
    lexical, embedding = entry.get("lexical_policy", "indexed"), entry.get("embedding_policy")
    product = entry.get("memory_class") == "product"  # the indexer never reads it: out of memory
    wrong = []
    if not (memory == "out" and product):
        if product:
            wrong.append("memory_class is product")
        if (lexical == "not indexed") != (wanted["lexical_policy"] == "not indexed"):
            wrong.append(f"lexical_policy must be {wanted['lexical_policy']}")
        if embedding != wanted["embedding_policy"]:
            wrong.append(f"embedding_policy must be {wanted['embedding_policy']}")
    if entry.get("stale_class") != stale:
        wrong.append(f"stale_class must be {stale or 'absent'}")
    return "; ".join(wrong)
