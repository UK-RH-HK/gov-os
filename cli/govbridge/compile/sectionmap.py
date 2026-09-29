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
    kind: str  # "heading" | "yaml_key" | "yaml_entry" | "md_entry" | "preamble"
    name: str  # heading text, dotted key path, "<under>[<entry_id>]", or "(preamble)"
    line_start: int  # 1-based, inclusive
    line_end: int  # 1-based, inclusive
    sha256: str  # sha256 of the exact text slice this section covers (its own content, independently re-readable)
    nbytes: int = 0  # UTF-8 byte length of that same exact text slice
    entry_id: Optional[str] = None  # an entry's own `id` (YAML key or matched Markdown token), or position

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _slice_text(lines: list, line_start: int, line_end: int) -> str:
    return "".join(lines[line_start - 1:line_end])


def _section_of(kind: str, name: str, lines: list, line_start: int, line_end: int,
                 entry_id: Optional[str] = None) -> "Section":
    body = _slice_text(lines, line_start, line_end)
    return Section(kind=kind, name=name, line_start=line_start, line_end=line_end, sha256=sha256_text(body),
                   nbytes=len(body.encode("utf-8")), entry_id=entry_id)


def _heading_level(line: str) -> Optional[int]:
    m = _HEADING_RE.match(line.rstrip("\n"))
    if not m:
        return None
    return len(m.group(1))


def _md_headings(text: str) -> tuple:
    """``(lines, headings)`` -- ``headings`` is ``[(line_no_1based, level, title)]`` for every ATX heading line."""
    lines = text.splitlines(keepends=True)
    headings = []
    for i, raw in enumerate(lines, start=1):
        level = _heading_level(raw)
        if level is not None:
            headings.append((i, level, raw.lstrip("#").strip()))
    return lines, headings


def markdown_sections(text: str) -> list:
    """Every heading run, in document order. A run at level N ends right before the next heading whose level is
    <= N (a subsection is nested INSIDE its parent's span, matching how a reader would name "the section starting
    at this heading"). NESTED spans OVERLAP by construction (a level-1 run contains its level-2 children) -- fine
    for "give me the section named X", wrong for a non-overlapping TILING (see ``flat_tiling`` for that)."""
    lines, headings = _md_headings(text)
    sections = []
    for idx, (start, level, title) in enumerate(headings):
        end = len(lines)
        for nxt_start, nxt_level, _ in headings[idx + 1:]:
            if nxt_level <= level:
                end = nxt_start - 1
                break
        sections.append(_section_of("heading", title or f"(heading at line {start})", lines, start, end))
    return sections


def _match_id_token(title: str, id_patterns: Optional[list]) -> Optional[str]:
    for pat in (id_patterns or ()):
        m = pat.match(title)
        if m:
            return m.group(0)
    return None


def markdown_flat_tiling(text: str, id_patterns: Optional[list] = None) -> list:
    """A FLAT (non-overlapping, gap-free) decomposition of a Markdown document -- unlike ``markdown_sections``,
    whose nested spans OVERLAP (a level-1 run contains its level-2 children) by design. Used wherever a partial
    mandatory delivery's disclosed ranges must exactly TILE the document (REPAIR_PLAN.md section 3 rule 1/2; the
    "id-range reopening": a coverage check built on overlapping regions could pass while hiding a real gap).

    Every heading -- at EVERY level, not one chosen level -- gets its own region, covering only its OWN direct
    content: from its heading line up to (but not including) its first CHILD heading (a heading at a deeper
    level, still within its own nested span), or to the end of its own span if it has no child. A "(preamble)"
    region covers whatever precedes the very first heading. This partitions the WHOLE document exhaustively for
    ANY heading structure -- uniform (every "## Part N" a sibling) or mixed (some headings have nested
    subsections, some do not) -- with no gaps and no overlaps, unlike a single fixed "pick one level" rule, which
    breaks as soon as a document mixes depths.

    A heading whose title begins with a token matched by ``id_patterns`` (``config/id-grammar.yaml``'s
    mention_patterns -- the ``entries`` selector's generic "an id-range of record ids", extended to Markdown) is
    returned as kind ``"md_entry"`` with ``entry_id`` set to the matched token; the common real shape is a level-2
    ledger heading such as "## P2-L-0046 -- ..." (``PHASE_LEDGER.md``), but any level works."""
    lines, headings = _md_headings(text)
    if not headings:
        return [_section_of("heading", "(whole document)", lines, 1, len(lines))] if lines else []

    n = len(lines)
    spans = []  # (start, level, title, end) -- end per markdown_sections' own nested-aware rule
    for idx, (start, level, title) in enumerate(headings):
        end = n
        for nxt_start, nxt_level, _ in headings[idx + 1:]:
            if nxt_level <= level:
                end = nxt_start - 1
                break
        spans.append((start, level, title, end))

    out = []
    if spans[0][0] > 1:
        out.append(_section_of("preamble", "(preamble)", lines, 1, spans[0][0] - 1))
    for idx, (start, level, title, end) in enumerate(spans):
        own_end = end
        if idx + 1 < len(headings):
            nxt_start, nxt_level, _ = headings[idx + 1]
            if nxt_start <= end and nxt_level > level:
                own_end = nxt_start - 1  # a CHILD heading follows -- our own content stops right before it
        entry_id = _match_id_token(title, id_patterns)
        out.append(_section_of(("md_entry" if entry_id else "heading"), title, lines, start, own_end,
                                entry_id=entry_id))
    return out


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
        return _section_of("yaml_key", dotted, lines, l1, l2)

    if keys is None:
        out = []
        for k, v in root.value:
            l1, l2 = _node_start_1based(k), _node_end_1based(v)
            out.append(_section_of("yaml_key", str(k.value), lines, l1, l2))
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
        out.append(_section_of("yaml_entry", name, lines, l1, l2, entry_id=entry_id))
    return out


def yaml_flat_tiling(text: str, entries_under: Optional[str] = None) -> list:
    """A flat, non-overlapping decomposition of a YAML document's top-level keys (PyYAML's block-style node marks
    are contiguous by construction, so this is already gap-free) -- except that, when ``entries_under`` names one
    of those keys, that ONE key's region is REPLACED by its own entry sub-regions (``yaml_entry_sections``),
    giving entry-level tiling exactly where an ``entries`` selector needs it, and key-level tiling everywhere
    else."""
    sections = yaml_key_sections(text)
    if not entries_under:
        return sections
    out = []
    for s in sections:
        if s.name == entries_under:
            out.extend(yaml_entry_sections(text, under=entries_under))
        else:
            out.append(s)
    return out


def flat_tiling(text: str, path: Optional[str], entries_under: Optional[str] = None,
                 id_patterns: Optional[list] = None) -> list:
    """The generic, non-overlapping, gap-free reference a partial mandatory delivery's disclosed
    delivered+undelivered ranges must exactly cover (BR-DAG-AMEND reopening, "packet verify cannot detect silent
    truncation": the check needs a TILING reference, never ``markdown_sections``'s possibly-nested/overlapping
    spans). Dispatched purely on ``path``'s extension: YAML top-level keys (with ``entries_under`` expanded into
    entries) for ``.yaml``/``.yml``, Markdown's flat heading tiling (``markdown_flat_tiling``) otherwise."""
    ext = _extension_of(path)
    if ext in _YAML_EXTS:
        return yaml_flat_tiling(text, entries_under=entries_under)
    return markdown_flat_tiling(text, id_patterns=id_patterns)


def entries_of(text: str, path: Optional[str], under: Optional[str] = None,
                id_patterns: Optional[list] = None) -> list:
    """Every entry of the document, in DOCUMENT ORDER -- REPAIR_PLAN.md section 3 rule 2's "entries (an id range
    of record ids)", generically over both shapes a mandatory item's occurrence may take: a YAML sequence's list
    items (``under``, a dotted key path to the sequence) and a Markdown document's id-prefixed headings
    (``id_patterns`` -- ``config/id-grammar.yaml``'s mention_patterns; a level-2 ledger heading such as
    "## P2-L-0046 -- ..." is the common real shape, but any level works, generically, via
    ``markdown_flat_tiling``)."""
    ext = _extension_of(path)
    if ext in _YAML_EXTS:
        return yaml_entry_sections(text, under=under)
    return [s for s in markdown_flat_tiling(text, id_patterns=id_patterns) if s.entry_id is not None]


def select_entry_range(entries: list, start, end) -> tuple:
    """``(selected, ok)`` -- ``entries`` MUST already be in document order (as ``entries_of`` returns them). The
    slice from the entry whose ``entry_id == start`` through the entry whose ``entry_id == end``, inclusive, in
    DOCUMENT ORDER -- never by string/lexicographic comparison (a "reopening" fix: entry ids are not guaranteed
    to sort the way they appear in the document). ``ok`` is False (``selected`` is ``[]``) when either id is
    missing, or ``start`` does not precede (or equal) ``end`` in document order -- REPAIR_PLAN.md section 3 rule
    2's "fails closed", generalised from existence to POSITION."""
    ids = [e.entry_id for e in entries]
    try:
        i = ids.index(str(start))
        j = ids.index(str(end))
    except ValueError:
        return [], False
    if i > j:
        return [], False
    return entries[i:j + 1], True


_MARKDOWN_EXTS = (".md", ".markdown")
_YAML_EXTS = (".yaml", ".yml")


def _extension_of(path: Optional[str]) -> str:
    if not path:
        return ""
    base = path.rsplit("/", 1)[-1]
    if "." not in base:
        return ""
    return "." + base.rsplit(".", 1)[-1].lower()


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
