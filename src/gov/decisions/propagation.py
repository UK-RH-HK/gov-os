"""Supersession propagates (W2-55; DEC-866 items 2 to 4): what still enforces a superseded or changed decision.

``check_propagation(root)`` reads the register (``gov.decisions.register``) and the searched places of ``HEAD``:
``tests/``, ``src/``, ``template/``, the project's prompts and briefs, the path map, and the ticket files that are
not closed (a closed ticket is a record; the register and the other records are not searched). A line enforces an
old decision where it

- cites a superseded entry's id, in a file that cites none of the entries that superseded it, or
- holds one of the values a superseded or changed entry records (``- **Values:** "300000"``); a changed entry's id
  alone tells no part and is no finding.

A file the old entry, or an entry that superseded or changed it, keeps with a reason (``- **Kept:** <path> —
<reason>``) gives no finding for that old entry. A finding is ``ENFORCES_SUPERSEDED`` with ``ids`` ``[old, new]``,
one per new entry, and ``paths`` the place; an empty list passes. ``python3 -m gov.decisions.propagation``, in a
project root, prints the findings and exits 1 when there are any or the register cannot be read.
"""

from __future__ import annotations

import posixpath
import sys
from pathlib import Path

from gov.decisions.checker import _finding
from gov.decisions.register import ids, read

SEARCHED = ("tests/", "src/", "template/", "governance/project/prompts/", "governance/project/briefs/")
SEARCHED_FILES = ("governance/project/path-map.yaml",)
TICKETS = ".tickets"


def _searched(root: Path, register_path: str) -> list[tuple[str, str]]:
    """``(path, text)`` of every searched file of ``HEAD`` that is UTF-8 text."""
    from gov.store.loader import _frontmatter, _git, _tree

    tree = _tree(root)
    paths = [path for path, (mode, kind, _) in tree.items() if kind == "blob" and mode != "120000"
             and path != register_path and (path.startswith(SEARCHED) or path in SEARCHED_FILES
                                            or (posixpath.dirname(path) == TICKETS and path.endswith(".md")))]
    out = _git(root, "cat-file", "--batch", stdin="".join(f"{tree[path][2]}\n" for path in paths).encode())
    files, position = [], 0
    for path in paths:
        header_end = out.index(b"\n", position)
        size = int(out[position:header_end].split()[2])
        blob, position = out[header_end + 1:header_end + 1 + size], header_end + size + 2
        try:
            text = blob.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if "\0" in text:
            continue
        if posixpath.dirname(path) == TICKETS:
            try:
                front = _frontmatter(text)
            except ValueError:
                front = None  # a ticket whose state cannot be read is searched
            if isinstance(front, dict) and front.get("status") == "closed":
                continue
        files.append((path, text))
    return files


def check_propagation(root: Path) -> list[dict]:
    """The places that still enforce a superseded or changed decision, in a fixed order; an empty list passes."""
    root = Path(root)
    register = read(root)
    if register is None:
        return []
    by_id = {entry["id"]: entry for entry in register["entries"]}
    olds = {**{old: ("changed", new) for old, new in register["changed"].items()},
            **{old: ("superseded", new) for old, new in register["superseded"].items()}}
    kept = {old: {path for record_id in [old, *new] if record_id in by_id for path in by_id[record_id]["kept"]}
            for old, (_, new) in olds.items()}
    values = {old: by_id[old]["values"] for old in olds if by_id[old]["values"]}
    found = []
    for path, text in _searched(root, register["path"]):
        cited = set(ids(text))
        lines = text.split("\n")
        for old, (how, new) in olds.items():
            if path in kept[old] or not (old in cited or old in values):
                continue
            citing = how == "superseded" and old in cited and not cited & set(new)
            for number, line in enumerate(lines, 1):
                hits = [f"cites {old}"] if citing and old in ids(line) else []
                hits += [f"holds {value!r}" for value in values.get(old, ()) if value in line]
                for successor in (new or [None]) if hits else ():
                    by = f"{how} by {successor}" if successor else f"{how}, with no successor named"
                    found.append((number, _finding("ENFORCES_SUPERSEDED", [old] + ([successor] if successor else []),
                                                   [path], f"{path}:{number} {' and '.join(hits)}: it still "
                                                   f"enforces {old}, {by}")))
    found.sort(key=lambda item: (item[1]["code"], item[1]["ids"], item[1]["paths"], item[0]))
    return [finding for _, finding in found]


def main() -> int:
    from gov.cli.errors import GovError

    try:
        found = check_propagation(Path.cwd())
    except GovError as exc:
        print(f"supersession propagation: {exc.code}: {exc.message}")
        return 1
    for finding in found:
        print(f"{finding['code']}: {finding['message']}")
    print(f"supersession propagation: {len(found)} finding(s)" if found else "supersession propagation: green")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
