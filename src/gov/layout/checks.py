"""The plan against the repository before any move: every item exactly once (SL-7), each destination where the
standard puts it (SL-9), imports whole and destinations free and unshared (SL-10, SL-12), and the stoppers."""

from __future__ import annotations

import os
import posixpath
from collections import defaultdict

from gov.layout.plan import Line, finding
from gov.layout.repo import Repo
from gov.layout.rules import destination, fits, package_roots, under
from gov.layout.standard import ASK, Standard

_STAY = ("ignored-root", "declared")  # kinds that move whatever the class never
_FORCED = ("hidden-set", "secret")  # classes a rule gives also inside an import


def ancestors(path: str):
    """``path`` and each folder above it, the path first."""
    parts = path.split("/")
    return ("/".join(parts[:depth]) for depth in range(len(parts), 0, -1))


def covering(lines: list[Line], paths) -> dict[str, list[Line]]:
    """For each of ``paths``, the lines at it or above it; each line is told the items it covers."""
    at = defaultdict(list)
    for line in lines:
        at[line.path].append(line)
    covered = {}
    for path in sorted(paths):
        covered[path] = sorted((line for head in ancestors(path) for line in at.get(head, ())),
                               key=lambda line: line.number)
        for line in covered[path]:
            line.items.append(path)
    return covered


def rule_class(repo: Repo, path: str, kind: str) -> str | None:
    """The class a rule alone gives the item, else None."""
    if repo.hidden(path):
        return "hidden-set"
    if kind in ("file", "ignored-root") and repo.std.secret_name(path):
        return "secret"
    if repo.visible(path):
        return "evaluation"
    fixed = repo.std.fixed_class(path)
    if fixed:
        return fixed
    return "generated" if kind == "ignored-root" and repo.std.generated_root(path) else None


def coverage(repo: Repo, covered: dict[str, list[Line]], lines: list[Line]) -> list[dict]:
    found = []
    for path, over in covered.items():
        kind = repo.items[path]
        rule = rule_class(repo, path, kind)
        if not over:
            more = {"rule_class": rule} if rule else {}
            found.append(finding("LAYOUT_GAP", None, path, "no plan line covers this item"
                                 + (f"; a rule classes it: {rule}" if rule else ""), **more))
            continue
        if len(over) > 1:
            found.append(finding("LAYOUT_DOUBLE", over[-1].number, path,
                                 f"{len(over)} lines cover this item: {over[0].path} and {over[-1].path}",
                                 other=over[0].path if over[0].path != path else over[-1].path))
        if rule is None:
            continue
        for line in over:
            if line.cls == rule or not (line.cls == ASK or line.cls in repo.std.classes):
                continue
            if repo.std.whole(line.cls) and rule not in _FORCED:
                continue
            if rule == "generated" and line.path != path:  # a folder line covers what a generator left below it
                continue
            found.append(finding("LAYOUT_RULE_CLASS", line.number, path,
                                 f"a rule classes this item {rule}, not as this line does", rule_class=rule))
    return found


def kinds(repo: Repo, lines: list[Line]) -> list[dict]:
    """A line that names nothing, and a kind that does not match what it names."""
    found = []
    for line in lines:
        if not repo.exists(line.path):
            found.append(finding("LAYOUT_NO_ITEM", line.number, line.path, "the repository holds nothing here"))
            continue
        item = repo.items.get(line.path)
        folder = not repo.is_file(line.path) and any(path != line.path and under(path, line.path)
                                                      for path in line.items)
        if folder:
            held = {repo.items[path] for path in line.items}
            fitting = {"folder"} if "file" in held else {"untracked", "folder"} if "untracked" not in held else {
                "untracked"}
            if item:  # a declared or ignored folder that is itself an item
                fitting.add(item)
        else:
            fitting = {item}
        if line.kind and line.kind not in fitting:
            found.append(finding("LAYOUT_INVALID", line.number, line.path,
                                 f"kind does not match the item, which is {' or '.join(sorted(map(str, fitting)))}",
                                 field="kind"))
    return found


def _common(folders: list[str]) -> str:
    return posixpath.commonpath(folders) if folders and all(folders) else ""


def place(repo: Repo, std: Standard, lines: list[Line]) -> list[dict]:
    """Says of each line whether it moves and where the standard puts it; the findings for a destination elsewhere."""
    imported = [line.path for line in lines if std.whole(line.cls)]
    roots = package_roots([path for path, kind in repo.items.items() if kind == "file"], imported)
    for line in lines:
        known = line.cls == ASK or line.cls in std.classes
        line.pinned = known and (
            not std.moves(line.cls) or line.kind in _STAY or repo.protected(line.path) or repo.visible(line.path)
            or std.fixed_class(line.path) is not None or any(under(line.path, root) for root in roots)
            # a folder that holds a tool-fixed file stays, so the file does
            or not std.whole(line.cls) and any(repo.items[path] != "ignored-root" and std.fixed_class(path)
                                               for path in line.items))
    imports = defaultdict(list)
    for line in lines:
        if std.whole(line.cls) and not line.pinned:
            imports[line.name].append(line)
    for name, same in imports.items():
        top = std.classes[same[0].cls]["destination"].replace("{import}", name)
        outside = [line for line in same if not under(line.path, top)] or same
        root = _common([posixpath.dirname(line.path) if repo.is_file(line.path) else line.path for line in outside])
        for line in same:
            line.root = root
    found = []
    for line in lines:
        if line.cls != ASK and line.cls not in std.classes:
            continue
        line.expected = line.path if line.pinned else destination(
            std, line.cls, line.path, line.text("stale_class"), line.name, line.root)
        line.moving = line.expected != line.path and bool(line.dest) and line.dest != line.path
        unjudged = std.stale(line.cls) and line.text("stale_class") not in std.stale_classes
        if line.dest and not unjudged and not fits(line.expected, line.dest):
            found.append(finding("LAYOUT_DESTINATION", line.number, line.path,
                                 f"the standard puts it at {line.expected}", expected=line.expected))
    return found


def imports_whole(repo: Repo, std: Standard, lines: list[Line], covered: dict[str, list[Line]]) -> list[dict]:
    """One import, one class, moved whole (L5)."""
    imports = defaultdict(list)
    for line in lines:
        if std.whole(line.cls) and line.name:
            imports[line.name].append(line)
    found = []

    def fault(line: Line, other: str, why: str) -> None:
        found.append(finding("LAYOUT_IMPORT", line.number, line.path, f"import {line.name or '-'}: {why}: "
                             f"{line.path} and {other}", other=other))

    for name, same in imports.items():
        same.sort(key=lambda line: line.path)
        top = std.classes[same[0].cls]["destination"].replace("{import}", name)
        inside = [line for line in lines if under(line.path, top) and line.name != name
                  and line.kind not in _STAY]
        for line in [*same[1:], *inside]:
            if line.cls != same[0].cls:
                fault(line, same[0].path, "two classes in one import")
        moving = [line for line in same if line.kind not in _STAY and line.dest]
        starts = {}  # where each line's destination says the import began
        for line in moving:
            if under(line.path, top):
                continue
            rest = line.dest[len(top) + 1:] if under(line.dest, top) else None
            if rest is None or rest and not line.path.endswith("/" + rest):
                if len(same) > 1:
                    fault(line, next(each.path for each in same if each is not line), "not moved whole")
                continue
            starts[line.path] = line.path[:-len(rest) - 1] if rest else line.path
        if len(set(starts.values())) > 1:
            first = next(line for line in moving if line.path in starts)
            for line in moving:
                if line.path in starts and starts[line.path] != starts[first.path]:
                    fault(line, first.path, "its lines move it apart")
        root = next((line.root for line in same if line.root), "")
        if root and (len(same) > 1 or not repo.is_file(same[0].path)):
            for path, over in covered.items():
                if under(path, root) and repo.items[path] in ("file", "untracked") and over \
                        and not any(std.whole(line.cls) for line in over):
                    fault(over[0], same[0].path, "a part of its tree is classed apart")
    return found


def targets(repo: Repo, lines: list[Line]) -> list[dict]:
    """Two items with one destination, and a destination the repository already holds."""
    found, by = [], defaultdict(list)
    for line in lines:
        if line.dest:
            by[line.dest].append(line)
    for dest, same in by.items():
        same.sort(key=lambda line: (line.moving, line.path))
        for line in same[1:]:
            if line.path != same[0].path:
                found.append(finding("LAYOUT_TARGET_TAKEN", line.number, line.path,
                                     f"one destination, {dest}, for {same[0].path} and {line.path}",
                                     other=same[0].path))
    for line in lines:
        if line.moving and (repo.exists(line.dest) or any(repo.is_file(head) for head in ancestors(line.dest))
                            or os.path.lexists(repo.root / line.dest)):
            found.append(finding("LAYOUT_TARGET_TAKEN", line.number, line.path,
                                 f"{line.path} would move to {line.dest}, which already exists", other=line.dest))
    return found


def stoppers(repo: Repo, covered: dict[str, list[Line]]) -> tuple[list[dict], str | None]:
    """``(the stoppers, why the secrets filter did not run)``: a hidden set inside the tree and a tracked secret."""
    why: dict[str, tuple[str, dict]] = {}

    def stop(path: str, message: str, **more) -> None:
        said, extra = why.get(path, (message, {}))
        why[path] = said, extra | more

    for path, over in covered.items():
        kind = repo.items[path]
        if repo.hidden(path):
            stop(path, "a registered hidden set lies inside the tree: its repository's CTO moves it to the sets root")
        elif any(line.cls == "hidden-set" for line in over):
            stop(path, "classed as a hidden set, which never lies inside a tree")
        if kind == "file" and repo.std.secret_name(path):
            stop(path, "a tracked file with a secret's name: the owner removes it and rotates the secret")
        elif kind == "file" and any(line.cls == "secret" for line in over):
            stop(path, "a tracked file classed as a secret: the owner removes it and rotates the secret")
    for path in repo.hidden_ignored:
        root = next((head for head in ancestors(path) if head in repo.items), path)
        stop(root, "a registered hidden set lies inside the tree: its repository's CTO moves it to the sets root")
    held, off = repo.secrets()
    for path, rule in held:
        stop(path, f"the secrets filter finds a secret (rule {rule}): the owner removes and rotates it", rule=rule)
    return [finding("LAYOUT_STOPPER", covered[path][0].number if covered.get(path) else None, path, message, **more)
            for path, (message, more) in why.items()], off
