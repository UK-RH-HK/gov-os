"""The archived decision register: its ids and headings, and nothing else of it (W2-203; EMERGENCY-2 11.3).

The archive is the file the path map of ``HEAD`` names under ``decision_register_archive``, read from ``HEAD``'s
objects as the store's loader reads the register. Its entries are history: no record, no register entry, no chunk of
memory. The code reads it only to know that a decision id existed, so that a kept entry, a ticket, a test or a commit
that names an archived decision still resolves. An id is a heading of the loader's entry grammar outside fenced
blocks and HTML comments (the loader's own scan): no status line is asked of history, so an entry the loader would
refuse as a record (DEC-027, DEC-974) is an archived id all the same; an id under two headings is one id, with its
first heading.

An archive the path map does not name, or that ``HEAD`` does not hold as a file of text, is no archive (None): the
archive is optional, and its absence refuses nothing.
"""

from __future__ import annotations

from pathlib import Path

ARCHIVE_KEY = "decision_register_archive"


def ids_in(text: str) -> dict[str, str]:
    """``id -> heading`` of the entry headings of an archive's ``text``, in the file's order."""
    from gov.store.loader import _ENTRY, _headings

    lines, found = text.split("\n"), {}
    for number in _headings(lines)[1]:
        entry = _ENTRY.match(lines[number])
        if entry:
            found.setdefault(entry.group(1), lines[number].rstrip())
    return found


def named(path_map) -> str | None:
    """The archive's path a parsed path map names; None where it names none (or no path)."""
    value = path_map.get(ARCHIVE_KEY) if isinstance(path_map, dict) else None
    return value if isinstance(value, str) and value.strip() else None


def of_tree(root: Path, tree: dict) -> dict[str, str] | None:
    """``id -> heading`` of the archive that ``tree`` (the loader's ``_tree`` of ``HEAD``) holds; None for none."""
    import yaml

    from gov.store.loader import PATH_MAP_REL, _file

    try:
        path = named(yaml.safe_load(_file(root, tree, PATH_MAP_REL) or ""))
    except yaml.YAMLError:
        return None
    text = _file(root, tree, path) if path else None
    return None if text is None else ids_in(text)


def read(root: Path) -> dict[str, str] | None:
    """``id -> heading`` of the archive ``HEAD`` holds; None where the path map names none or ``HEAD`` holds none."""
    from gov.store.loader import _tree

    root = Path(root)
    return of_tree(root, _tree(root))
