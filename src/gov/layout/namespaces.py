"""The namespaces the standard and a plan imply (SL-12): one per class, one per stale class of the archive, one per
import; a study import's by its size in chunks."""

from __future__ import annotations

from collections import defaultdict

from gov.layout.checks import ancestors
from gov.layout.plan import Line, finding
from gov.layout.repo import Repo
from gov.layout.standard import ASK, Standard
from gov.retrieval.chunking import chunk_file

_STUDY = "import-study"


def name_of(std: Standard, line: Line) -> str:
    if std.whole(line.cls):
        return f"import-{line.name}"
    return f"{line.cls}-{line.text('stale_class')}" if std.stale(line.cls) else line.cls


def policies(memory: str) -> dict:
    return {"lexical_policy": "not indexed" if memory == "out" else "indexed",
            "embedding_policy": "embedded" if memory == "embedded" else "not embedded"}


def study_memory(repo: Repo, std: Standard, imports: dict[str, list[Line]]) -> dict[str, tuple[int, str]]:
    """``(chunks, memory)`` of each study import: by meaning within the ceiling of one import and of all of them
    together (taken in the order of their names), else by keyword."""
    found, total = {}, 0
    for name, same in sorted(imports.items()):
        if same[0].cls != _STUDY:
            continue
        paths = sorted({path for line in same for path in line.items})
        chunks = sum(len(chunk_file(path, repo.blobs.get(path, ""), text)[1]) for path, text in repo.texts(paths))
        within = (chunks <= std.ceiling["import_chunks"]
                  and total + chunks <= std.ceiling["repository_chunks"])
        total += chunks if within else 0
        found[name] = chunks, std.classes[_STUDY]["memory"] if within else "keyword"
    return found


def compile_map(repo: Repo, std: Standard, lines: list[Line], held: set[str]) -> tuple[list, list, list]:
    """``(namespaces, imports, faults)``. A line of a known class (ask apart) places its destination, a held one its
    own path too, where it stays."""
    lines = sorted((line for line in lines if line.cls in std.classes and line.dest),
                   key=lambda line: (line.path, line.dest, line.cls))
    imports = defaultdict(list)
    for line in lines:
        if std.whole(line.cls) and line.name:
            imports[line.name].append(line)
    studies = study_memory(repo, std, imports)
    spaces: dict[str, dict] = {}

    def space(name: str, memory: str, stale: str | None = None) -> set:
        return spaces.setdefault(name, {"paths": set(), **policies(memory), "stale_class": stale})["paths"]

    for stale in std.stale_classes:
        archive = next(name for name in std.classes if std.stale(name))
        space(f"{archive}-{stale}", std.classes[archive]["memory"], stale).add(f"{archive}/{stale}/**")
    claims = defaultdict(list)  # each destination's lines
    for line in lines:
        if line.kind == "declared" and not repo.exists(line.path):
            continue
        name = name_of(std, line)
        memory = studies[line.name][1] if line.cls == _STUDY and line.name in studies else std.classes[line.cls][
            "memory"]
        paths = space(name, memory, line.text("stale_class") or None if std.stale(line.cls) else None)
        folder = not repo.is_file(line.path) and (line.kind in ("folder", "untracked")
                                                  or line.kind == "ignored-root" and (repo.root / line.path).is_dir())
        for place in [line.dest, *([line.path] if line.path in held else [])]:
            top = f"imports/{line.name}" if std.whole(line.cls) else None
            if top and (place == top or place.startswith(top + "/")):
                paths.add(f"{top}/**")
            else:
                paths.add(f"{place}/**" if folder else place)
        if line.kind not in ("ignored-root", "declared"):
            claims[line.path if line.path in held else line.dest].append(line)
    faults = _overlaps(std, claims)
    listed = [{"name": name, **entry, "paths": sorted(entry["paths"])} for name, entry in sorted(spaces.items())]
    brought = [{"name": name, "class": same[0].cls, "chunks": studies.get(name, (None, None))[0],
                "namespace": f"import-{name}",
                "embedding_policy": spaces[f"import-{name}"]["embedding_policy"]}
               for name, same in sorted(imports.items()) if f"import-{name}" in spaces]
    return listed, brought, faults


def _overlaps(std: Standard, claims: dict[str, list[Line]]) -> list[dict]:
    """A destination two namespaces claim: two lines at it or one below the other, and a line of another class in an
    archive or an import folder."""
    found = []
    imports = {f"imports/{line.name}": f"import-{line.name}"
               for same in claims.values() for line in same if std.whole(line.cls)}
    archives = {f"{name}/{stale}": f"{name}-{stale}" for name in std.classes if std.stale(name)
                for stale in std.stale_classes}
    for dest, same in sorted(claims.items()):
        for line in same:
            own = name_of(std, line)
            others = [(other.path, name_of(std, other)) for head in ancestors(dest) for other in claims.get(head, ())
                      if other is not line and name_of(std, other) != own]
            others += [(head, claimed) for head in ancestors(dest)
                       for claimed in [archives.get(head) or imports.get(head)] if claimed and claimed != own]
            if others and line.cls != ASK:
                other, claimed = others[0]
                found.append(finding("LAYOUT_MAP", line.number, line.path,
                                     f"{dest} would lie in two namespaces, {own} and {claimed}: {line.path} and "
                                     f"{other}", other=other))
    return found
