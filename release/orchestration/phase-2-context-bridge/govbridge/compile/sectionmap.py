#!/usr/bin/env python3
"""Generic, format-aware section maps for a document's text (REPAIR_PLAN.md section 3; node R1-RM,
BR-DAG node R1-RM: "mandatory-input fidelity").

A **section** is a structurally-addressable span of a document, detected by SHAPE alone, never by a hard-coded
document name or heading text (OC-BR-02: generic, not bespoke):

* a Markdown **heading** run -- from a ``#``-prefixed line up to (but not including) the next heading at the same
  or a shallower level, or end of file;
* a YAML top-level (or dotted-path) **mapping key** -- from its ``key:`` line up to (but not including) the next
  sibling key, or end of file;
* one **entry** of a YAML sequence (a list item) -- most usefully a ``- id: ...`` record, addressed by its own
  ``id`` field when it has one, else by its position.

This module is used two ways by ``govbridge.compile.packet`` / ``govbridge.authority.resolver``:

1. when a mandatory item's full content exceeds the per-item cap and no selector narrows it, its FULL map (every
   section, in document order, with exact line ranges and a sha256 of each section's own text) is what the
   ``MANDATORY_PARTIAL_DELIVERY`` J notice discloses -- "everything a reader could ask for by name", never a
   silent, unmarked cut (REPAIR_PLAN.md section 3 rule 1);
2. to resolve a mandatory-input row's own declared ``keys``/``entries`` selectors to exact line spans, whether or
   not the item is oversize (REPAIR_PLAN.md section 3 rule 2) -- an unresolvable selector is reported back to the
   caller, which fails the whole row closed (never a silent partial match).

Placed under ``govbridge.compile`` (this node's mutation scope names this exact path) but kept a fully standalone
leaf module -- it imports nothing from ``govbridge.compile.packet`` or ``govbridge.authority.resolver``, so
``authority/resolver.py`` importing it (to resolve row selectors) creates no import cycle and does not reach into
``govbridge.lexical``/``.semantic``/``.code``/``.graph``/``.route`` (the one import boundary
``tests/authority/test_import_boundary.py`` actually enforces).
"""
from __future__ import annotations

import dataclasses
import re
from typing import Optional

import yaml

from govbridge.core.yamlutil import sha256_text

_HEADING_RE = re.compile(r"^(#{1,6})(\s+.*)?$")


@dataclasses.dataclass(frozen=True)
class Section:
    kind: str  # "heading" | "yaml_key" | "yaml_entry"
    name: str  # heading text, dotted key path, or "<under>[<entry_id>]"
    line_start: int  # 1-based, inclusive
    line_end: int  # 1-based, inclusive
    sha256: str  # sha256 of the exact text slice this section covers (its own content, independently re-readable)
    entry_id: Optional[str] = None  # yaml_entry only: the entry's own `id` scalar, or its position if it has none

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _slice_text(lines: list, line_start: int, line_end: int) -> str:
    return "".join(lines[line_start - 1:line_end])


def _heading_level(line: str) -> Optional[int]:
    m = _HEADING_RE.match(line.rstrip("\n"))
    if not m:
        return None
    return len(m.group(1))


def markdown_sections(text: str) -> list:
    """Every heading run, in document order. A run at level N ends right before the next heading whose level is
    <= N (a subsection is nested INSIDE its parent's span, matching how a reader would name "the section starting
    at this heading")."""
    lines = text.splitlines(keepends=True)
    headings = []
    for i, raw in enumerate(lines, start=1):
        level = _heading_level(raw)
        if level is not None:
            headings.append((i, level, raw.lstrip("#").strip()))
    sections = []
    for idx, (start, level, title) in enumerate(headings):
        end = len(lines)
        for nxt_start, nxt_level, _ in headings[idx + 1:]:
            if nxt_level <= level:
                end = nxt_start - 1
                break
        body = _slice_text(lines, start, end)
        sections.append(Section(kind="heading", name=title or f"(heading at line {start})", line_start=start,
                                 line_end=end, sha256=sha256_text(body)))
    return sections


def _compose(text: str):
    try:
        return yaml.compose(text, Loader=yaml.SafeLoader)
    except yaml.YAMLError:
        return None


def _node_start_1based(node) -> int:
    return node.start_mark.line + 1


def _node_end_1based(node) -> int:
    """1-based, INCLUSIVE end line of ``node``'s own span. A block-style value's ``end_mark`` lands at column 0 of
    the line right after its content (an EXCLUSIVE 0-based boundary, which equals the 1-based inclusive end
    directly); an inline scalar's ``end_mark`` lands mid-line, on its own last content line (a 0-based line index
    that needs ``+ 1`` to become the 1-based inclusive end)."""
    if node.end_mark.column == 0:
        return node.end_mark.line
    return node.end_mark.line + 1


def _mapping_pairs(node):
    return node.value if isinstance(node, yaml.MappingNode) else []


def yaml_key_sections(text: str, keys: Optional[list] = None) -> list:
    """Top-level YAML mapping keys as sections, in document order (``keys`` is None), or exactly the dotted paths
    named in ``keys`` (a name absent from the document is simply omitted -- the caller detects that by comparing
    the requested names against the returned sections' own ``name``s, per REPAIR_PLAN.md section 3 rule 2's
    "fails closed"). A dotted path (``a.b``) resolves through nested mappings; the returned span always covers
    KEY + VALUE together."""
    root = _compose(text)
    if root is None or not isinstance(root, yaml.MappingNode):
        return []
    lines = text.splitlines(keepends=True)

    def _one(dotted: str) -> Optional[Section]:
        node = root
        key_node = val_node = None
        for part in dotted.split("."):
            if not isinstance(node, yaml.MappingNode):
                return None
            found = None
            for k, v in node.value:
                if str(k.value) == part:
                    found = (k, v)
                    break
            if found is None:
                return None
            key_node, val_node = found
            node = val_node
        l1, l2 = _node_start_1based(key_node), _node_end_1based(val_node)
        return Section(kind="yaml_key", name=dotted, line_start=l1, line_end=l2,
                        sha256=sha256_text(_slice_text(lines, l1, l2)))

    if keys is None:
        out = []
        for k, v in root.value:
            l1, l2 = _node_start_1based(k), _node_end_1based(v)
            out.append(Section(kind="yaml_key", name=str(k.value), line_start=l1, line_end=l2,
                                sha256=sha256_text(_slice_text(lines, l1, l2))))
        return out

    out = []
    for dotted in keys:
        sec = _one(str(dotted))
        if sec is not None:
            out.append(sec)
    return out


def _find_node(root, under: Optional[str]):
    node = root
    if not under:
        return node
    for part in under.split("."):
        if not isinstance(node, yaml.MappingNode):
            return None
        found = None
        for k, v in node.value:
            if str(k.value) == part:
                found = v
                break
        if found is None:
            return None
        node = found
    return node


def yaml_entry_sections(text: str, under: Optional[str] = None) -> list:
    """Every entry of the YAML sequence at ``under`` (dotted path; None means the document root, when the document
    IS itself a sequence). ``entry_id`` is the entry's own ``id`` scalar key when it is a mapping with one, else
    its position (``"0"``, ``"1"``, ...) -- the ``entries`` selector's "an id range of record ids" (REPAIR_PLAN.md
    section 3 rule 2), generically, for any YAML list, never one hard-coded document shape."""
    root = _compose(text)
    if root is None:
        return []
    seq = _find_node(root, under)
    if not isinstance(seq, yaml.SequenceNode):
        return []
    lines = text.splitlines(keepends=True)
    out = []
    for idx, item in enumerate(seq.value):
        entry_id = str(idx)
        for k, v in _mapping_pairs(item):
            if str(k.value) == "id":
                entry_id = str(v.value)
                break
        l1, l2 = _node_start_1based(item), _node_end_1based(item)
        name = f"{under + '.' if under else ''}[{entry_id}]"
        out.append(Section(kind="yaml_entry", name=name, line_start=l1, line_end=l2,
                            sha256=sha256_text(_slice_text(lines, l1, l2)), entry_id=entry_id))
    return out


_MARKDOWN_EXTS = (".md", ".markdown")
_YAML_EXTS = (".yaml", ".yml")


def _extension_of(path: Optional[str]) -> str:
    if not path:
        return ""
    base = path.rsplit("/", 1)[-1]
    if "." not in base:
        return ""
    return "." + base.rsplit(".", 1)[-1].lower()


def whole_map(text: str, path: Optional[str]) -> list:
    """Every detected section, in document order, dispatched purely on ``path``'s extension (never on sniffing
    content, which a governance record's free-form prose could fool): YAML top-level keys for ``.yaml``/``.yml``,
    Markdown headings otherwise. Returns ``[]`` (honest, no structure claimed) when the format has no headings and
    is not YAML -- the caller then discloses the item by exact reference alone, never a guess at internal shape."""
    ext = _extension_of(path)
    if ext in _YAML_EXTS:
        return yaml_key_sections(text)
    return markdown_sections(text)


def select(sections: list, names: list) -> tuple:
    """``(selected, unresolved)`` -- ``selected`` in the order ``names`` was given, ``unresolved`` lists every name
    with no matching section (REPAIR_PLAN.md section 3 rule 2: "an unresolvable selector fails closed")."""
    by_name = {s.name: s for s in sections}
    selected, unresolved = [], []
    for n in names:
        s = by_name.get(n)
        if s is None:
            unresolved.append(n)
        else:
            selected.append(s)
    return selected, unresolved
