"""The landing's path map coverage (W2-206 fix PM-1 to PM-3; DEC-1244): the checker of ``gov check``
(``gov.check.pathmap.check``) on the merged tree, read against the paths each candidate adds."""

from __future__ import annotations

from pathlib import Path

import yaml

from gov.check import pathmap

NONE, TWO = "PATH_NO_NAMESPACE", "PATH_MULTIPLE_NAMESPACES"


def judge(tree: Path, changes: list[tuple[str, list[str], bool]]) -> tuple[list[dict], str | None]:
    """``(refused entries, count line)`` of the tree checked out at ``tree``; ``changes``: each candidate's
    ``(ticket, paths it adds, whether it changes the map)``. One entry per refused candidate. The line is None
    where the tree is no Gov OS project or its map cannot be used."""
    if not (tree / pathmap.PROJECT_REL).is_dir():
        return [], None
    findings = pathmap.check(tree)
    unusable = [f for f in findings if f["code"] not in (NONE, TWO)]
    if unusable:
        why = unusable[0]
        return [{"ticket": ticket, "code": why["code"], "paths": added or [pathmap.PATH_MAP_REL],
                 "reason": f"{why['message']}: the paths it adds ({', '.join(added) or 'none'}) and its change of "
                           "the map cannot be judged"}
                for ticket, added, changed in changes if added or changed], None
    from gov.queue.command import _git

    tracked = [p for p in _git(tree, "ls-files", "-z").split("\0") if p]
    held = {f["path"]: f for f in findings}
    none = {p for p, f in held.items() if f["code"] == NONE}
    line = f"path map: {len(tracked)} tracked, {len(none)} in none, {len(held) - len(none)} in two"
    entries = []
    for ticket, added, _ in changes:
        bad = sorted(p for p in added if p in held)
        if bad:
            entries.append({"ticket": ticket, "code": held[bad[0]]["code"], "paths": bad,
                            "reason": "; ".join(_reason(tree, held[p], tracked, none) for p in bad)})
    return entries, line


def _reason(tree: Path, finding: dict, tracked: list[str], none: set[str]) -> str:
    """What to do about one path: the line to add, or the namespaces and patterns that both hold it."""
    path = finding["path"]
    if finding["code"] == TWO:
        data = yaml.safe_load((tree / pathmap.PATH_MAP_REL).read_text(encoding="utf-8"))
        both = ", ".join(f"{name} ({', '.join(repr(p) for p in patterns if pathmap._matches(path, p))})"
                         for name, patterns in pathmap._namespaces(data) if name in finding["namespaces"])
        return f"{path} is held by more than one namespace of {pathmap.PATH_MAP_REL}: {both}"
    folder = path.rpartition("/")[0]
    placed = any(p.startswith(f"{folder}/") and p not in none for p in tracked)
    add = path if not folder or placed else f"{folder}/**"
    return f"{path} is held by no namespace: add the line - \"{add}\" under a namespace's paths in {pathmap.PATH_MAP_REL}"
