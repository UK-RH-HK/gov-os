#!/usr/bin/env python3
"""The authority/lifecycle classifier (ARCHITECTURE.md section 5.2), in precedence order, failing closed:

1. mandatory_bridge_inputs items -- the class is the item's class, exactly; a section-anchored item never inherits
   its file's class (unanchored lines are UNCLASSIFIED, scoped to that section).
2. Registry entries (config/authority-registry.yaml) -- section_anchors, supersessions (scope WHOLE flips the
   `to` id's lifecycle via the fixed vocabulary table; any other scope only adds a "partially superseded" note),
   lifecycle_overrides.
3. Structured metadata -- YAML `status`/`supersedes`/`superseded_by`/`amends`/`in_effect`/`approval_state`; markdown
   header-table rows `| Status |`, `| Supersedes |`, `| Authorises |`.
4. Registry `class_rules` (glob -> class; never an ACTIVE lifecycle).
5. Otherwise: class UNCLASSIFIED, lifecycle UNKNOWN.

Conflicts fail closed (the less authoritative class/lifecycle wins); this module imports nothing from
govbridge.lexical/.semantic/.code/.graph/.route (tests/authority/test_import_boundary.py enforces this with `ast`).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.authority import registry as registrymod
from govbridge.authority import records as recordsmod
from govbridge.core import gitobj, view as viewmod
from govbridge.core.yamlutil import load_yaml_text

LADDER_RANK = {c.name: c.rank for c in classesmod.LADDER}


def _class_rank(cls: Optional[str]) -> int:
    """Lower is MORE authoritative; used to fail closed on a CLASS_CONFLICT (the less authoritative class wins).
    A non-ladder class always loses to a ladder class (ARCHITECTURE.md section 5.2: "non-ladder beats ladder")."""
    if cls is None:
        return 1_000_000
    spec = classesmod.ALL_CLASSES.get(cls)
    if spec is None:
        return 1_000_000
    if spec.ladder:
        return spec.rank
    return 900_000  # any non-ladder class: "less authoritative" than every ladder class


@dataclasses.dataclass
class Classification:
    unit: str
    cls: Optional[str]
    lifecycle: str
    derivation: str
    notes: list
    path: Optional[str] = None
    commit: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    conflict: Optional[str] = None  # "CLASS_CONFLICT" | "LIFECYCLE_CONFLICT" | None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


def _load_mandatory_items(repo: Optional[str] = None, view_path: Optional[str] = None,
                           resolved_view=None) -> dict:
    if resolved_view is not None:
        resolved = resolved_view
    else:
        from govbridge import GOV_BRIDGE_DOMAIN
        import os
        view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
        vc = viewmod.load_view(view_path)
        resolved = viewmod.resolve_view(vc, repo=repo)
    commit = resolved.ref_commit("records")
    text = gitobj.read_path(commit, classesmod.BRIDGE_STATE_PATH, repo=repo)
    doc = load_yaml_text(text.decode("utf-8"))
    items = {}
    for item in doc["mandatory_bridge_inputs"]["items"]:
        items[item["id"]] = item
    return items


def _apply_supersession_to_lifecycle(sup: registrymod.Supersession) -> Optional[tuple]:
    """(lifecycle, note) for the `to` side of a supersession, or None if the scope leaves lifecycle unchanged
    (anything other than scope WHOLE only adds a note)."""
    if sup.is_whole:
        lifecycle = classesmod.map_lifecycle_word(sup.cite.quote) or classesmod.LIFECYCLE_SUPERSEDED
        if lifecycle == classesmod.LIFECYCLE_UNKNOWN:
            lifecycle = classesmod.LIFECYCLE_SUPERSEDED
        return lifecycle, f"superseded by {sup.from_id} (scope: WHOLE, REGISTRY_CITED)"
    return None


def classify(unit: str, path: Optional[str] = None, commit: Optional[str] = None,
             line_start: Optional[int] = None, line_end: Optional[int] = None,
             reg: Optional[registrymod.Registry] = None, mandatory_items: Optional[dict] = None,
             repo: Optional[str] = None, view_path: Optional[str] = None,
             pre_text: Optional[str] = None) -> Classification:
    """Classify ``unit`` (a record id). ``path``/``commit``/``line_start``/``line_end`` narrow the occurrence when
    the caller already knows a definition site (e.g. from ``records.py``); when absent, the classifier still applies
    every id-keyed rule (mandatory items, section_anchors by item_id, supersessions, lifecycle_overrides) and, if a
    definition site is needed and not given, looks one up via ``records.py``'s definition rules at the ``records``
    ref (bounded to that one id's occurrence, never a whole-corpus scan). ``pre_text`` lets a caller that has
    ALREADY read ``path``'s content this build (govbridge.authority.layer, from records.scan_ref's own pass) hand
    it over instead of paying for a second Git read of the same blob; the classification logic applied to it is
    identical either way -- this is a caller-side read-reuse, never a different code path."""
    if reg is None:
        reg = registrymod.load(registrymod._default_registry_path(), verify_commit="records", view_path=view_path,
                                repo=repo)
    if mandatory_items is None:
        mandatory_items = _load_mandatory_items(repo=repo, view_path=view_path)

    notes: list = []
    cls: Optional[str] = None
    lifecycle = classesmod.LIFECYCLE_UNKNOWN
    derivation = "UNCLASSIFIED"
    conflict = None

    # rule 1: mandatory_bridge_inputs items -- class is the item's class, exactly.
    if unit in mandatory_items:
        cls = mandatory_items[unit]["class"]
        derivation = "MANDATORY_BRIDGE_INPUT"

    # rule 1 (section-scoping): a request for a whole anchored file, or a line outside every anchor, is UNCLASSIFIED.
    anchor_by_id = reg.anchor_by_item_id(unit)
    if anchor_by_id is not None:
        if cls is None:
            cls = anchor_by_id.cls
        if path is None:
            path = anchor_by_id.path
        line_start, line_end = anchor_by_id.line_start, anchor_by_id.line_end
        derivation = "REGISTRY_CITED" if derivation == "UNCLASSIFIED" else derivation
        notes.append(f"section-anchored: {anchor_by_id.heading!r} lines {line_start}-{line_end}")
    elif path is not None:
        anchors_here = reg.anchors_for_path(path)
        if anchors_here:
            if line_start is not None:
                hit = reg.anchor_for_line(path, line_start)
                if hit is not None and (line_end is None or reg.anchor_for_line(path, line_end) is hit):
                    if cls is None:
                        cls = hit.cls
                    derivation = "REGISTRY_CITED" if derivation == "UNCLASSIFIED" else derivation
                else:
                    cls = "UNCLASSIFIED"
                    derivation = "REGISTRY_CITED"
                    notes.append(f"line {line_start} falls outside every section_anchor of {path}; section-scoped")
            else:
                # a whole-file request on a file that has section anchors: the file is not uniformly one class
                # (ARCHITECTURE.md section 5.2 rule 1: the file-level class never flows into a section).
                cls = "UNCLASSIFIED"
                derivation = "REGISTRY_CITED"
                note = reg.unanchored_notes.get(path)
                notes.append(note or f"{path} has section-anchored items; a whole-file request is UNCLASSIFIED")

    # rule 3: structured metadata (only if we have, or can find, a definition occurrence).
    resolved_path, resolved_commit = path, commit
    doc_for_metadata = None
    if resolved_path is None:
        found = _find_definition(unit, repo=repo, view_path=view_path)
        if found is not None:
            resolved_path, resolved_commit, line_start, line_end = found
    if resolved_commit is None and resolved_path is not None:
        from govbridge import GOV_BRIDGE_DOMAIN
        import os
        vp = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
        vc = viewmod.load_view(vp)
        rv = viewmod.resolve_view(vc, repo=repo)
        resolved_commit = rv.ref_commit("records")

    if resolved_path is not None and resolved_commit is not None:
        if pre_text is not None:
            decoded = pre_text
        else:
            text = gitobj.read_path(resolved_commit, resolved_path, repo=repo)
            decoded = text.decode("utf-8", "replace") if text is not None else None
        if decoded is not None:
            if resolved_path.endswith((".yaml", ".yml")):
                try:
                    doc_for_metadata = load_yaml_text(decoded)
                except Exception:
                    doc_for_metadata = None
                if isinstance(doc_for_metadata, dict) and doc_for_metadata.get("id") == unit:
                    lc = _lifecycle_from_yaml_metadata(doc_for_metadata)
                    if lc is not None:
                        lifecycle, meta_note = lc
                        derivation = "EXACT_METADATA"
                        notes.append(meta_note)
                    if cls is None:
                        cls = None  # class still comes from class_rules below (rule 4), not from metadata
            elif resolved_path.endswith(".md"):
                lc = _lifecycle_from_md_header_table(decoded, unit)
                if lc is not None:
                    lifecycle, meta_note = lc
                    derivation = "EXACT_METADATA" if derivation == "UNCLASSIFIED" else derivation
                    notes.append(meta_note)

    # rule 2: registry supersessions/lifecycle_overrides RESTRICT whatever we have so far.
    override = reg.lifecycle_override_for(unit)
    if override is not None:
        lifecycle = override.lifecycle
        if override.cls is not None:
            cls = override.cls
        derivation = "REGISTRY_CITED"
        notes.append(f"lifecycle_override: {override.cite.path}:{override.cite.line} {override.cite.quote!r}")

    for sup in reg.supersessions_to(unit):
        applied = _apply_supersession_to_lifecycle(sup)
        if applied is not None:
            lifecycle, note = applied
            derivation = "REGISTRY_CITED"
            notes.append(note)
        else:
            notes.append(f"partially superseded by {sup.from_id} (scope: {sup.scope}, REGISTRY_CITED)")
    for sup in reg.supersessions_from(unit):
        notes.append(f"supersedes {sup.to_id} (scope: {sup.scope}, REGISTRY_CITED)")

    # rule 4: class_rules (path glob), only if no class assigned yet.
    if cls is None and resolved_path is not None:
        rule = reg.class_for_path(resolved_path)
        if rule is not None:
            cls = rule.cls
            derivation = "CLASS_RULE" if derivation == "UNCLASSIFIED" else derivation

    if cls is None:
        cls = "UNCLASSIFIED"

    return Classification(unit=unit, cls=cls, lifecycle=lifecycle, derivation=derivation, notes=notes,
                           path=resolved_path, commit=resolved_commit, line_start=line_start, line_end=line_end,
                           conflict=conflict)


def _lifecycle_from_yaml_metadata(doc: dict) -> Optional[tuple]:
    in_effect = doc.get("in_effect")
    mapped = classesmod.map_in_effect(in_effect) if in_effect is not None else None
    status = doc.get("status")
    approval_state = doc.get("approval_state")
    for source_name, source_val in (("status", status), ("approval_state", approval_state)):
        if isinstance(source_val, str):
            mapped_from_status = classesmod.map_lifecycle_word(source_val)
            if mapped_from_status != classesmod.LIFECYCLE_UNKNOWN:
                sup_by = doc.get("superseded_by")
                note = f"{source_name}: {source_val!r}" + (f" (superseded_by {sup_by})" if sup_by else "")
                return mapped_from_status, note
    if mapped is not None:
        return mapped, f"in_effect: {in_effect!r}"
    return None


def _lifecycle_from_md_header_table(text: str, unit: str) -> Optional[tuple]:
    lines = text.splitlines()
    for ln in lines[:40]:  # the header table is always at the top of an owner record
        stripped = ln.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) != 2:
            continue
        field = cells[0].strip().lower()
        if field == "status":
            mapped = classesmod.map_lifecycle_word(cells[1])
            return mapped, f"Status: {cells[1]!r}"
    return None


def _find_definition(unit: str, repo: Optional[str] = None, view_path: Optional[str] = None) -> Optional[tuple]:
    """A bounded lookup for one id's definition occurrence, reusing git grep (never a whole-tree census) plus
    records.py's rules to pick the definition among the hits. fixtures/** is never a definition (ARCHITECTURE.md
    section 2). When several files carry a candidate definition, the STRONGEST rule wins (the id-grammar's
    definition_rules order is itself a precedence order: yaml_top_id is far stronger evidence than file_stem)."""
    from govbridge.core import pathrules
    from govbridge import GOV_BRIDGE_DOMAIN
    import os

    view_path = view_path or os.path.join(GOV_BRIDGE_DOMAIN, "config", "canonical-view.yaml")
    vc = viewmod.load_view(view_path)
    rv = viewmod.resolve_view(vc, repo=repo)
    commit = rv.ref_commit("records")
    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    rule_order = [r["id"] for r in grammar.definition_rules]
    fixtures_glob = grammar.fixtures_glob

    hits = gitobj.git_grep(unit, commit, repo=repo)
    seen_paths: set = set()
    candidates: list = []  # (rule_rank, path, line_start, line_end)
    for path, _line, _text in hits:
        if path in seen_paths or pathrules.glob_match(path, fixtures_glob):
            continue
        seen_paths.add(path)
        blob = gitobj.blob_at(commit, path, repo=repo)
        if blob is None:
            continue
        raw = gitobj.read_blob(blob, repo=repo)
        if raw is None:
            continue
        try:
            decoded = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if path.endswith((".yaml", ".yml")):
            defs = recordsmod.extract_definitions_yaml(decoded, path, grammar)
        elif path.endswith(".md"):
            defs = recordsmod.extract_definitions_markdown(decoded, path, grammar)
        else:
            defs = []
        defs += recordsmod.extract_definitions_file_stem(path, grammar, decoded.count("\n") + 1)
        for d in defs:
            if d.id == unit:
                rank = rule_order.index(d.rule) if d.rule in rule_order else len(rule_order)
                candidates.append((rank, path, d.line_start, d.line_end))

    if not candidates:
        return None
    candidates.sort(key=lambda c: c[0])
    _, path, line_start, line_end = candidates[0]
    return path, commit, line_start, line_end


def show_many(unit_ids: list, repo: Optional[str] = None, view_path: Optional[str] = None) -> dict:
    reg = registrymod.load(registrymod._default_registry_path(), verify_commit="records", view_path=view_path,
                            repo=repo)
    mandatory_items = _load_mandatory_items(repo=repo, view_path=view_path)
    out = {}
    for unit in unit_ids:
        c = classify(unit, reg=reg, mandatory_items=mandatory_items, repo=repo, view_path=view_path)
        out[unit] = c.to_dict()
    return out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.lifecycle")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("show")
    s.add_argument("ids", nargs="+")
    s.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    args = p.parse_args(argv)

    if args.cmd == "show":
        result = show_many(args.ids)
        print(json.dumps(result, indent=1, sort_keys=True))
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
