"""What the moves of a plan ask of the files that name them (L4, SL-11): a document's mention is rewritten, a mention
in code, tests or configuration holds the item, and a mention in the path map, the kit, an import, a generated file or
a tool-written record is kept as it is."""

from __future__ import annotations

from gov.layout.plan import Line
from gov.layout.references import links, mentions, resolve
from gov.layout.repo import Repo
from gov.layout.rules import under
from gov.layout.standard import Standard
from gov.util.parts import PATH_MAP_REL

REWRITE, HOLD, KEPT = "rewrite", "hold", "kept"


def _imported(std: Standard, line: Line | None, path: str) -> bool:
    return under(path, "imports") or line is not None and std.whole(line.cls)


def treatment(repo: Repo, std: Standard, line: Line | None, path: str) -> str:
    """What a mention in the file ``path`` (covered by ``line``) asks."""
    if (path == PATH_MAP_REL or std.fixed_class(path) == "kit" or _imported(std, line, path)
            or line is not None and line.cls in ("kit", "generated")
            or any(under(path, top) for top in std.record_paths)):
        return KEPT
    return REWRITE if path.endswith(std.document_suffixes) else HOLD


def scan(repo: Repo, std: Standard, line_of, targets: dict[str, bool]):
    """``(file, its line, mentioned path, target)`` of each time a tracked file names a path of ``targets``."""
    for path, text in repo.texts(path for path in repo.blobs if path != repo.plan_rel):
        line = line_of(path)
        document = path.endswith(std.document_suffixes) and not _imported(std, line, path)
        for mentioned, item in mentions(text, path, targets, document=document, exists=repo.exists):
            yield path, line, mentioned, item


def own_links(repo: Repo, std: Standard, paths: dict[str, Line]):
    """``(document, link target, the path it resolves to)`` of each relative or rooted link of the documents
    ``paths`` that are rewritten."""
    wanted = [path for path, line in paths.items()
              if path in repo.blobs and treatment(repo, std, line, path) == REWRITE]
    for path, text in repo.texts(wanted):
        for _, _, raw in links(text):
            target = resolve(path, raw) if raw else None
            if target is not None:
                yield path, raw, target


def held_items(found: list, repo: Repo, std: Standard, moving: dict[str, Line]) -> dict[str, set[str]]:
    """Each moving item held, with the files that hold it; an import's lines are held together."""
    held: dict[str, set[str]] = {}
    for path, line, _, item in found:
        if treatment(repo, std, line, path) == HOLD:
            held.setdefault(item, set()).add(path)
    for item, by in list(held.items()):
        if std.whole(moving[item].cls):
            for other, line in moving.items():
                if std.whole(line.cls) and line.name == moving[item].name:
                    held.setdefault(other, set()).update(by)
    return held


def judge(repo: Repo, std: Standard, lines: list[Line], covered: dict[str, list[Line]]) -> tuple[list, list, list]:
    """``(rewrites, held, kept)`` of the plan, before any move."""
    moving = {line.path: line for line in lines if line.moving}
    targets = {path: not repo.is_file(path) for path in moving}

    def line_of(path: str) -> Line | None:
        return covered[path][0] if covered.get(path) else None

    found = list(scan(repo, std, line_of, targets))
    held = held_items(found, repo, std, moving)

    def holder(path: str) -> bool:
        """Whether ``path`` is a held item or lies in one."""
        return any(under(path, item) for item in held)

    def new(path: str) -> str:
        for item, line in moving.items():
            if item not in held and under(path, item):
                return line.dest + path[len(item):]
        return path

    rewrites, kept = set(), set()
    for path, line, mentioned, item in found:
        how = treatment(repo, std, line, path)
        if item in held or how == HOLD:
            continue
        if how == KEPT:
            kept.add((path, mentioned, new(mentioned)))
        elif not holder(path):
            rewrites.add((path, mentioned, new(mentioned)))
    # a moving document's own links: their relation changes with its place
    documents = {path: over[0] for path, over in covered.items() if over and over[0].moving and not holder(path)}
    for path, _, target in own_links(repo, std, documents):
        if repo.exists(target) and not holder(target):
            rewrites.add((path, target, new(target)))

    def listed(entries: set) -> list[dict]:
        return [{"path": path, "target": target, "new": where} for path, target, where in sorted(entries)]

    return (listed(rewrites), [{"path": item, "by": by} for item in sorted(held) for by in sorted(held[item])],
            listed(kept))
