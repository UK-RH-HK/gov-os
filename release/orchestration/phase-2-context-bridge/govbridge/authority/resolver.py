#!/usr/bin/env python3
"""The mandatory-input resolver (ARCHITECTURE.md section 5.3 rule 1, section 7.1's ``required_inputs``,
``ARCHITECTURE/schemas/task-spec.yaml``). Section A of a packet is filled ONLY by this module.

``MandatoryItem`` is a frozen dataclass constructed only here -- no route, and no other module in this package,
builds one. Every ``required_inputs`` row is resolved to an exact occurrence (or set of occurrences, for a
``[*]``-suffixed state_ref) with a sha256 check against ``content_hash`` (path_form/id_form) or the row's own
recorded ``sha256`` (state_form, when the state row carries one); a missing input or a hash mismatch makes the
WHOLE resolution ``BLOCKED`` (W3/W4) -- a mandatory input is never partially satisfied.

Imports nothing from ``govbridge.lexical``/``.semantic``/``.code``/``.graph``/``.route`` (enforced by
tests/authority/test_import_boundary.py, an ``ast`` check).
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.authority import lifecycle as lifecyclemod
from govbridge.authority import registry as registrymod
from govbridge.core import gitobj, view as viewmod
from govbridge.core.yamlutil import canonical_json, load_yaml_file, load_yaml_text, sha256_bytes, sha256_text

STATUS_OK = "OK"
STATUS_BLOCKED = "BLOCKED"

def _load_state_aliases() -> dict:
    """The alias -> path table, moved to ``config/state-aliases.yaml`` (routed issue B5/BR-AR-0007: "hard-coded
    state aliases in resolver.py"; I1/BR-AR-0009 closes it, near-frozen-module carve-out: "moving hard-coded path
    constants into config"). Read once, at import time, from the domain's own config directory -- the same way
    every other bridge config file (corpus-rules.yaml, budgets.yaml, ...) is read off disk, never through Git."""
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    path = os.path.join(GOV_BRIDGE_DOMAIN, "config", "state-aliases.yaml")
    return dict(load_yaml_file(path)["aliases"])


STATE_ALIASES = _load_state_aliases()


def _load_id_mention_regexes() -> tuple:
    """Compiled ``config/id-grammar.yaml`` mention_patterns (REPAIR_PLAN.md section 3 rule 2's ``entries``
    selector, generalised to Markdown -- "a section whose heading begins with a token matched by
    config/id-grammar.yaml is an entry"). Read once, at import time, the same way ``STATE_ALIASES`` is -- this is
    real, repository-wide grammar data, never a fixture-overridable path. A lazy import of
    ``govbridge.authority.records`` (a PEER module in this same package, not a layering violation) avoids a
    module-load-time cost for callers that never touch a row with an ``entries`` selector."""
    from govbridge.authority import records as recordsmod
    grammar = recordsmod.load_grammar(recordsmod._default_grammar_path())
    return tuple(m["regex"] for m in grammar.mention_patterns)


ID_MENTION_REGEXES = _load_id_mention_regexes()

STATE_REF_RE = re.compile(r"^state:(?P<alias>[^#]+)#(?P<key>.+?)(?P<star>\[\*\])?$")
PATH_FORM_RE = re.compile(r"^(?P<path>[^@]+)@(?P<ref>[^:]+)(?::(?P<l1>\d+)(?:-(?P<l2>\d+))?)?$")


@dataclasses.dataclass(frozen=True)
class MandatoryItem:
    """Section A's only admissible unit (ARCHITECTURE.md section 5.3 rule 1). Frozen: never mutated after
    construction; no conversion function exists to or from RetrievedItem/DerivedItem.

    The fields below ``source_row`` are additive (BR-DAG node R1-RM, REPAIR_PLAN.md section 3) and default to
    "nothing declared" so every pre-existing construction of this dataclass keeps working unmodified:

    * ``is_directory``/``directory_members``: a by-reference directory item (``path`` ends ``/``) is expanded into
      a member manifest -- ``{path, blob, size, cls}`` per tracked file under it, sorted by path -- instead of
      carrying no content at all;
    * ``parts``: additional FULLY-RESOLVED sub-occurrences of the same mandatory item, one per declared selector
      match -- an extra ``paths`` entry (delivered in full, not merely existence-checked), a ``keys`` selector's
      matched YAML key, or an ``entries`` selector's matched list entries. Each part is
      ``{kind, name, path, commit, line_start, line_end, sha256}`` -- deliberately carrying no TEXT (resolver.py
      stays a pure identity/metadata module; ``govbridge.compile.packet`` reads the actual bytes, exactly as it
      already does for the primary occurrence);
    * ``unresolved_selectors``: never non-empty on a returned item -- a row whose ``keys``/``entries``/``paths``
      selector cannot be resolved BLOCKS the whole resolution instead (``resolve()``'s existing "a mandatory input
      is never partially satisfied" rule), so this field exists only for the internal helper that decides that;
      kept on the dataclass so a caller inspecting a blocked attempt (tests) sees exactly what failed.
    """
    id: str
    cls: str
    lifecycle: str
    path: Optional[str]
    commit: Optional[str]
    blob: Optional[str]
    line_start: Optional[int]
    line_end: Optional[int]
    sha256: Optional[str]
    reason: str
    source_row: str  # which required_inputs entry (its state_ref/id/path) produced this item
    is_directory: bool = False
    directory_members: tuple = ()
    parts: tuple = ()
    unresolved_selectors: tuple = ()

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclasses.dataclass
class ResolveResult:
    status: str
    items: list  # [MandatoryItem]
    blocked_reasons: list

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "items": [i.to_dict() for i in self.items],
            "blocked_reasons": self.blocked_reasons,
        }


def _resolve_view(view_path: str, repo: Optional[str] = None) -> "viewmod.ResolvedView":
    vc = viewmod.load_view(view_path)
    return viewmod.resolve_view(vc, repo=repo)


def _get_key_path(doc: dict, key_path: str):
    node = doc
    for part in key_path.split("."):
        if isinstance(node, dict):
            if part not in node:
                raise KeyError(f"{key_path!r}: no key {part!r}")
            node = node[part]
        else:
            raise KeyError(f"{key_path!r}: {part!r} is not inside a mapping")
    return node


def _load_state_doc(alias: str, resolved_view: "viewmod.ResolvedView", repo: Optional[str] = None) -> tuple:
    if alias not in STATE_ALIASES:
        raise ValueError(f"unknown state alias {alias!r} (known: {sorted(STATE_ALIASES)})")
    path = STATE_ALIASES[alias]
    classification = resolved_view.classify_occurrence(path, resolved_view.ref_commit("records"))
    commit = classification.canonical_commit
    text = gitobj.read_path(commit, path, repo=repo)
    if text is None:
        raise FileNotFoundError(f"{commit}:{path} not found")
    return load_yaml_text(text.decode("utf-8")), path, commit


def _sha256_of(path: str, commit: str, repo: Optional[str] = None) -> Optional[str]:
    blob = gitobj.blob_at(commit, path, repo=repo)
    if blob is None:
        return None
    raw = gitobj.read_blob(blob, repo=repo)
    if raw is None:
        return None
    return sha256_bytes(raw)


def _list_directory_members(commit: str, dirpath: str, reg: registrymod.Registry,
                             repo: Optional[str] = None) -> tuple:
    """REPAIR_PLAN.md section 3 rule 3: "a by-reference directory is expanded into a member manifest: path, blob,
    size and class." Every tracked file (never a subtree entry itself) under ``dirpath`` at ``commit``, classified
    the same generic way any other occurrence is (``Registry.class_for_path``'s glob rules) -- never a hard-coded
    per-directory rule."""
    prefix = dirpath.rstrip("/") + "/"
    members = []
    for entry in gitobj.ls_tree(commit, repo=repo):
        if entry.type != "blob" or not entry.path.startswith(prefix):
            continue
        rule = reg.class_for_path(entry.path)
        members.append({"path": entry.path, "blob": entry.oid, "size": entry.size,
                         "cls": (rule.cls if rule is not None else "UNCLASSIFIED")})
    members.sort(key=lambda m: m["path"])
    return tuple(members)


def _resolve_row_selectors(row: dict, path: str, commit: str, repo: Optional[str] = None) -> tuple:
    """REPAIR_PLAN.md section 3 rule 2: a mandatory-input row may declare ``keys`` (a list of dotted YAML key
    paths), ``entries`` (``{under?, ids?}`` or ``{under?, start, end}`` -- an id range/set within a YAML sequence)
    and/or multiple ``paths`` (every one delivered, not merely existence-checked). Returns
    ``(parts, unresolved)``; ``parts`` is a tuple of dicts (see ``MandatoryItem.parts``), in the order declared;
    ``unresolved`` names every selector that did not resolve -- the caller fails the WHOLE row closed on any of
    those (never a silent partial match).

    ``keys``/``entries`` are only ever treated as SELECTORS when they carry the structured shape this function
    expects (a list, and a mapping, respectively) -- a real ``mandatory_bridge_inputs`` row already uses
    ``entries`` as a free-text, human-readable annotation (e.g. ``entries: 'P2-L-0033..P2-L-0047 (...)'`` on
    ``PHASE-2-LEDGER-P2-L-0033-0047``, ORCHESTRATOR_STATE.yaml). That row is left completely alone: a
    non-structured ``entries``/``keys`` value is never a selector, never an error, and never resolves any part."""
    raw_keys = row.get("keys")
    raw_entries = row.get("entries")
    keys = raw_keys if isinstance(raw_keys, list) else None
    entries = raw_entries if isinstance(raw_entries, dict) else None
    raw_paths = row.get("paths")
    extra_paths = [p for p in raw_paths if p != path] if isinstance(raw_paths, list) else []

    if not keys and not entries and not extra_paths:
        return (), ()

    from govbridge.compile import sectionmap as sectionmapmod  # standalone leaf module; see its own docstring

    parts: list = []
    unresolved: list = []

    if keys or entries:
        raw = gitobj.read_path(commit, path, repo=repo)
        text = None
        if raw is not None:
            try:
                text = raw.decode("utf-8")
            except UnicodeDecodeError:
                text = None
        if text is None:
            unresolved.extend(f"keys:{k}" for k in (keys or []))
            if entries:
                unresolved.append("entries: source could not be read/decoded")
        else:
            if keys:
                found, missing = sectionmapmod.select(sectionmapmod.yaml_key_sections(text), list(keys))
                unresolved.extend(f"keys:{m}" for m in missing)
                for sec in found:
                    parts.append({"kind": "keys", "name": sec.name, "path": path, "commit": commit,
                                  "line_start": sec.line_start, "line_end": sec.line_end, "sha256": sec.sha256})
            if entries:
                # REPAIR_PLAN.md section 3 rule 2, generalised (reopening): `entries` works over BOTH a YAML
                # sequence (`under`, a dotted key path) and a Markdown document's id-prefixed headings (the real
                # PHASE-2-LEDGER-P2-L-0033-0047 shape) -- `entries_of` dispatches on `path`'s extension.
                # `{start, end}` is resolved in DOCUMENT ORDER (never lexicographically): `select_entry_range`.
                under = entries.get("under")
                all_entries = sectionmapmod.entries_of(text, path, under=under, id_patterns=ID_MENTION_REGEXES)
                ids = entries.get("ids")
                start, end = entries.get("start"), entries.get("end")
                if ids is not None:
                    by_id = {e.entry_id: e for e in all_entries}
                    order = {e.entry_id: idx for idx, e in enumerate(all_entries)}
                    chosen = []
                    for i in ids:
                        sec = by_id.get(str(i))
                        if sec is None:
                            unresolved.append(f"entries:{i}")
                        else:
                            chosen.append(sec)
                    chosen.sort(key=lambda s: order[s.entry_id])  # DOCUMENT order, whatever order `ids` declared
                elif start is not None and end is not None:
                    chosen, ok = sectionmapmod.select_entry_range(all_entries, start, end)
                    if not ok:
                        unresolved.append(f"entries:{start}-{end} (both ids must exist and {start} must precede "
                                           f"or equal {end} in DOCUMENT order, not lexicographic order)")
                else:
                    chosen = []
                    unresolved.append("entries: neither ids nor start/end declared")
                for sec in chosen:
                    parts.append({"kind": "entries", "name": sec.name, "path": path, "commit": commit,
                                  "line_start": sec.line_start, "line_end": sec.line_end, "sha256": sec.sha256})

    for extra in extra_paths:
        entry = gitobj.ls_tree_path(commit, extra.rstrip("/"), repo=repo)
        if entry is None:
            unresolved.append(f"paths:{extra}")
            continue
        if extra.endswith("/") or entry.type != "blob":
            unresolved.append(f"paths:{extra} (a directory is not a deliverable extra path)")
            continue
        parts.append({"kind": "paths", "name": extra, "path": extra, "commit": commit, "line_start": None,
                      "line_end": None, "sha256": _sha256_of(extra, commit, repo=repo)})

    return tuple(parts), tuple(unresolved)


def _read_git_slice(path: str, commit: str, l1: Optional[int], l2: Optional[int],
                     repo: Optional[str] = None) -> Optional[str]:
    """The text of ``path``@``commit`` (or lines ``l1``-``l2`` of it), or None -- never truncated (this module
    computes identity/metadata, not a bounded excerpt; ``govbridge.compile.packet`` owns budget-shaped reading).
    A small, deliberate duplicate of ``packet._read_excerpt``'s non-truncating half: resolver.py must not import
    packet.py (packet.py already imports resolver.py; the reverse would be circular)."""
    raw = gitobj.read_path(commit, path, repo=repo)
    if raw is None:
        return None
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return None
    if l1 is not None:
        lines = text.splitlines(keepends=True)
        l2 = l2 or l1
        text = "".join(lines[max(l1 - 1, 0):l2])
    return text


def _entries_under_from_parts(parts: tuple) -> Optional[str]:
    """Recovers an ``entries`` selector's own ``under`` value from an already-resolved ``entries``-kind part's
    ``name`` (``f"{under + '.' if under else ''}[{entry_id}]"`` -- see ``sectionmap.yaml_entry_sections``), so
    ``declared_regions`` below can re-expand the SAME key when it recomputes the item's declared span. Avoids
    adding a redundant field to ``MandatoryItem`` purely to carry a value already implicit in ``parts``."""
    for p in parts:
        if p["kind"] == "entries":
            prefix = p["name"].split("[", 1)[0]
            return prefix[:-1] if prefix.endswith(".") else (prefix or None)
    return None


def hash_pieces(pieces: "list") -> str:
    """The ONE canonical hash both ``declared_hash_and_bytes`` (below) and ``packet.item_from_mandatory``'s
    ``delivered_sha256`` use, so equality between the two is a meaningful, exact byte-level comparison rather than
    two independently-invented schemes that happen to look similar. Each piece is stripped of trailing newlines
    before joining (matching how every renderer in this package already ends a body -- ``rstrip("\\n")`` -- so a
    delivered piece's own trailing-newline convention never causes a spurious mismatch)."""
    return sha256_text("\n".join(p.rstrip("\n") for p in pieces))


def _total_lines(text: str) -> int:
    return len(text.splitlines())


def declared_parts(mi: "MandatoryItem", repo: Optional[str] = None) -> tuple:
    """The ORDERED list of raw pieces that constitute EXACTLY what this mandatory item's row DECLARES -- read
    fresh from Git, never trusted from a stored value (BR-DAG-AMEND reopening, "packet verify cannot detect
    silent truncation": RC-1's whole defect was a compiler that could cut a body while the manifest still claimed
    a hash for it; a check that trusts the compiler's own declared_sha256 catches nothing, so this function is the
    independent ground truth ``validate.py`` recomputes at verify time).

    * a directory item: ``()`` -- its declared form is its member manifest, checked separately;
    * a ``keys``/``entries`` selector (it narrows the PRIMARY occurrence itself): EXACTLY ``mi.parts``' own
      resolved sub-ranges, in the given order -- the row asked for precisely these, and delivering precisely
      these IS full, honest delivery (never "partial" relative to what was actually requested);
    * a ``paths``-only selector (nothing narrows the primary): the primary's own whole occurrence, plus one
      whole-file piece per additional declared path, in declaration order;
    * no selector at all: ONE piece -- the item's own occurrence (whole file, or its registry-anchored slice).

    Each piece is ``{path, commit, line_start, line_end, name, text, sha256, bytes}`` -- ``line_start``/
    ``line_end`` are always CONCRETE (a whole-file piece resolves to ``(1, total_lines)``, never ``(None, None)``),
    so a caller can do line-range arithmetic without a special case for "whole file"."""
    if mi.is_directory:
        return ()

    def _piece(path, commit, l1, l2, name):
        text = _read_git_slice(path, commit, l1, l2, repo=repo)
        if text is None:
            return None
        if l1 is None:
            l1, l2 = 1, _total_lines(text)
        return {"path": path, "commit": commit, "line_start": l1, "line_end": l2, "name": name, "text": text,
                "sha256": sha256_text(text), "bytes": len(text.encode("utf-8"))}

    narrowing_parts = [p for p in mi.parts if p["kind"] in ("keys", "entries")]
    path_parts = [p for p in mi.parts if p["kind"] == "paths"]

    pieces: list = []
    if narrowing_parts:
        for p in narrowing_parts:
            piece = _piece(p["path"], p["commit"], p["line_start"], p["line_end"], p["name"])
            if piece is not None:
                pieces.append(piece)
    else:
        if mi.path is not None and mi.commit is not None:
            piece = _piece(mi.path, mi.commit, mi.line_start, mi.line_end, "(primary)")
            if piece is not None:
                pieces.append(piece)
        for p in path_parts:
            piece = _piece(p["path"], p["commit"], p["line_start"], p["line_end"], p["name"])
            if piece is not None:
                pieces.append(piece)
    return tuple(pieces)


def declared_hash_and_bytes(parts: tuple) -> tuple:
    """``(declared_sha256, declared_bytes)`` from ``declared_parts``'s output -- ``hash_pieces`` over each part's
    own raw text, in order, and the sum of their byte lengths. ``(None, 0)`` for an empty part list (a directory
    item, or an occurrence that could not be read -- honest MISSING, never a fabricated hash)."""
    if not parts:
        return None, 0
    return hash_pieces([p["text"] for p in parts]), sum(p["bytes"] for p in parts)


def oversize_disclosure_map(mi: "MandatoryItem", repo: Optional[str] = None) -> tuple:
    """The FULL, FLAT structural tiling (``sectionmap.flat_tiling``) of a NO-SELECTOR mandatory item's own primary
    occurrence -- used ONLY for the oversize-with-no-selector disclosure (rule 1): the row declares the WHOLE
    file/slice as ONE piece (``declared_parts``), but a useful ``MANDATORY_PARTIAL_DELIVERY`` notice needs a finer
    breakdown (headings, or YAML keys) to be worth reading, and ``packet verify``'s coverage check needs that same
    breakdown to confirm nothing was silently dropped BETWEEN the disclosed ranges. Returns ``()`` for a directory
    item or a ``keys``/``entries``/``paths`` row (those never need this: see ``declared_parts``'s own docstring)."""
    if mi.is_directory or mi.parts:
        return ()
    if mi.path is None or mi.commit is None:
        return ()
    if mi.line_start is not None:
        # an ANCHORED item's flat_tiling would be computed against the SLICE's own local line numbers, not the
        # file's real ones -- re-verifying a disclosed range against Git would then read the wrong lines. No
        # current registry anchor is oversize (anchors are small, hand-placed subsections); until one is, this
        # case falls back to the coarser single-piece disclosure (declared_parts already covers correctness).
        return ()
    from govbridge.compile import sectionmap as sectionmapmod  # see _resolve_row_selectors: no import cycle
    text = _read_git_slice(mi.path, mi.commit, None, None, repo=repo)
    if text is None:
        return ()
    out = []
    for sec in sectionmapmod.flat_tiling(text, mi.path, id_patterns=ID_MENTION_REGEXES):
        out.append({"path": mi.path, "commit": mi.commit, "line_start": sec.line_start, "line_end": sec.line_end,
                    "name": sec.name, "sha256": sec.sha256, "bytes": sec.nbytes})
    return tuple(out)


def _one_mandatory_item(this_id: str, path: str, base_item_id: str, row: dict,
                         resolved_view: "viewmod.ResolvedView", reg: registrymod.Registry,
                         mandatory_items_index: dict, source_row: str, reason: str,
                         repo: Optional[str] = None) -> tuple:
    """Resolves ONE (id, path) pair to a MandatoryItem. ``this_id`` is what the returned item is identified by
    (the row's own id for a single-path row, or an ``id#pathN`` for the 2nd+ path of a multi-path row -- see
    ``_mandatory_item_from_row``); ``base_item_id`` is the row's real id, used for every registry/mandatory-items
    lookup (the registry and ``mandatory_bridge_inputs`` know nothing about a synthetic ``#pathN`` suffix).
    Returns (MandatoryItem_or_None, blocked_reason_or_None)."""
    expected_sha256 = row.get("sha256")
    commit_hint = row.get("commit")

    if commit_hint:
        commit = gitobj.resolve_commit(commit_hint, repo=repo) or commit_hint
    else:
        classification = resolved_view.classify_occurrence(path, resolved_view.ref_commit("records"))
        commit = classification.canonical_commit

    is_directory = path.endswith("/")
    entry = gitobj.ls_tree_path(commit, path.rstrip("/"), repo=repo)
    if entry is None:
        return None, f"{this_id}: {path} not found at {commit}"
    blob = entry.oid  # a tree id for a directory entry, a blob id otherwise -- both are valid Git object ids

    if expected_sha256 and not is_directory:
        actual = _sha256_of(path, commit, repo=repo)
        if actual != expected_sha256:
            return None, f"{this_id}: sha256 mismatch at {path}@{commit} (expected {expected_sha256}, got {actual})"

    cls = row.get("class")
    line_start = line_end = None
    anchor = reg.anchor_by_item_id(base_item_id)
    if anchor is not None:
        line_start, line_end = anchor.line_start, anchor.line_end
        if cls is None:
            cls = anchor.cls

    directory_members: tuple = ()
    parts: tuple = ()
    if is_directory:
        # a directory entry (e.g. REVIEW-8-PROBES' probes/P2-AR-0097/) carries no text to read metadata from; its
        # class is given by the row, and its lifecycle defaults ACTIVE (the task-spec's own default for a resolved
        # required_input) unless a registry entry restricts it. REPAIR_PLAN.md section 3 rule 3: expand it into a
        # member manifest instead of leaving it a bare, contentless pointer.
        override = reg.lifecycle_override_for(base_item_id)
        lifecycle = override.lifecycle if override is not None else classesmod.LIFECYCLE_ACTIVE
        if cls is None:
            cls = "UNCLASSIFIED"
        directory_members = _list_directory_members(commit, path, reg, repo=repo)
        # a declared row sha256 always wins (it is verified content, pinned by the task author); absent that, a
        # directory item is no longer left with source sha256=None (the exact run-1 pain point: "acknowledged as
        # 'ID@None' because the manifest carries no content_sha256 for this by-reference [item]") -- it gets a
        # real, deterministic identity hash over its own member manifest instead.
        sha256_val = expected_sha256 or (
            sha256_text(canonical_json([{"path": m["path"], "blob": m["blob"]} for m in directory_members]))
            if directory_members else None)
    else:
        classification = lifecyclemod.classify(base_item_id, path=path, commit=commit, line_start=line_start,
                                                line_end=line_end, reg=reg, mandatory_items=mandatory_items_index,
                                                repo=repo)
        if cls is None:
            cls = classification.cls
        lifecycle = classification.lifecycle
        sha256_val = expected_sha256 or _sha256_of(path, commit, repo=repo)
        # REPAIR_PLAN.md section 3 rule 2: the row's own declared `keys`/`entries`/multiple `paths` selectors,
        # resolved to exact sub-ranges. An unresolvable selector fails the WHOLE row closed -- "a mandatory input
        # is never partially satisfied" (this module's own docstring), the same discipline a missing path or a
        # sha256 mismatch already gets above.
        parts, unresolved = _resolve_row_selectors(row, path, commit, repo=repo)
        if unresolved:
            return None, f"{this_id}: selector(s) not resolvable at {path}@{commit}: {', '.join(unresolved)}"

    item = MandatoryItem(
        id=this_id, cls=cls, lifecycle=lifecycle, path=path, commit=commit, blob=blob,
        line_start=line_start, line_end=line_end, sha256=sha256_val,
        reason=reason, source_row=source_row, is_directory=is_directory, directory_members=directory_members,
        parts=parts,
    )
    return item, None


def _mandatory_item_from_row(row: dict, resolved_view: "viewmod.ResolvedView", reg: registrymod.Registry,
                              mandatory_items_index: dict, source_row: str, reason: str,
                              repo: Optional[str] = None) -> tuple:
    """Returns (MandatoryItem_or_None, blocked_reason_or_None) -- one item per row, whose PRIMARY occurrence is
    ``path`` (or ``paths[0]`` for a multi-path row). Routed issue B5/BR-AR-0007 OI-3 ("a multi-path mandatory item
    resolves only its first path") and REPAIR_PLAN.md section 3 rule 2 ("the resolver honours... multiple paths")
    are both closed inside ``_one_mandatory_item``'s call to ``_resolve_row_selectors``: EVERY listed path is
    verified to exist at the resolved commit AND delivered in full as one of the item's ``parts`` -- a missing
    second path still BLOCKS the whole row (a mandatory input is never partially satisfied), exactly as a missing
    primary path already does. This still yields exactly one MandatoryItem per row -- the extra paths (and any
    ``keys``/``entries`` selector matches) are additional, fully-resolved PARTS of that one item, never a second,
    separately-classified section-A entry (which would silently multiply a row's authority footprint)."""
    item_id = row.get("id") or source_row
    path = row.get("path")
    paths = row.get("paths")

    if path is None and paths:
        path = paths[0]  # the primary occurrence
    if path is None:
        anchor = reg.anchor_by_item_id(item_id)
        if anchor is not None:
            path = anchor.path

    if path is None:
        return None, f"{item_id}: no path, paths[] or registry section_anchor to resolve an occurrence from"

    item, blocked = _one_mandatory_item(item_id, path, item_id, row, resolved_view, reg, mandatory_items_index,
                                         source_row, reason, repo=repo)
    if item is None:
        return None, blocked

    return item, None


def resolve(task_spec: dict, repo: Optional[str] = None, registry_path: Optional[str] = None,
            resolved_view: "Optional[viewmod.ResolvedView]" = None) -> ResolveResult:
    """Resolves every ``required_inputs`` row of ``task_spec`` to ``MandatoryItem``s (or a ``blocked_reasons``
    entry). ``resolved_view``, when given, is used AS-IS instead of resolving ``task_spec["view"]`` live --
    BR-DAG-AMEND-R1-1's re-derivation at a packet's OWN RECORDED view (pinned refs/commits from its manifest,
    never the repository's moving tip) passes one in here; every other caller leaves it None and gets today's
    live-tip resolution. Passing the SAME resolved view into the registry load and the mandatory-items index below
    (rather than each re-resolving the view independently, as they did before) also closes a smaller, latent
    inconsistency: two live resolutions a few lines apart could, in principle, see two different tips."""
    view_path = task_spec["view"]
    from govbridge import GOV_BRIDGE_DOMAIN
    import os
    if not os.path.isabs(view_path):
        view_path = os.path.join(GOV_BRIDGE_DOMAIN, view_path) if not os.path.exists(view_path) else view_path
    if resolved_view is None:
        resolved_view = _resolve_view(view_path, repo=repo)
    reg = registrymod.load(registry_path or registrymod._default_registry_path(), verify_commit="records",
                            view_path=view_path, repo=repo, resolved_view=resolved_view)
    mandatory_items_index = lifecyclemod._load_mandatory_items(repo=repo, resolved_view=resolved_view)

    items: list = []
    blocked: list = []

    for entry in task_spec.get("required_inputs", []):
        reason = entry.get("reason", "")
        if "state_ref" in entry:
            m = STATE_REF_RE.match(entry["state_ref"])
            if not m:
                blocked.append(f"malformed state_ref: {entry['state_ref']!r}")
                continue
            alias, key_path, star = m.group("alias"), m.group("key"), m.group("star")
            try:
                doc, state_path, state_commit = _load_state_doc(alias, resolved_view, repo=repo)
                value = _get_key_path(doc, key_path)
            except (KeyError, ValueError, FileNotFoundError) as e:
                blocked.append(f"{entry['state_ref']}: {e}")
                continue
            rows = value if star else [value]
            if not isinstance(rows, list):
                rows = [rows]
            for idx, row in enumerate(rows):
                source_row = f"{entry['state_ref']}[{idx}]" if star else entry["state_ref"]
                if not isinstance(row, dict):
                    # a scalar/leaf value (e.g. contract_v3.sha256 alone) -- not expected from these three inputs,
                    # but handled generically: no occurrence to check beyond the state file that carries it.
                    blocked.append(f"{source_row}: not a mapping, cannot resolve an occurrence ({row!r})")
                    continue
                item, reason_blocked = _mandatory_item_from_row(
                    row, resolved_view, reg, mandatory_items_index, source_row, reason, repo=repo)
                if item is None:
                    blocked.append(reason_blocked)
                else:
                    items.append(item)

        elif "id" in entry:
            item_id = entry["id"]
            required_status = entry.get("required_status") or classesmod.LIFECYCLE_ACTIVE
            found = lifecyclemod._find_definition(item_id, repo=repo, view_path=view_path)
            anchor = reg.anchor_by_item_id(item_id)
            if found is None and anchor is None:
                blocked.append(f"{item_id}: no definition found (id_form required_input)")
                continue
            path, commit, line_start, line_end = found if found else (anchor.path, resolved_view.ref_commit("records"),
                                                                        anchor.line_start, anchor.line_end)
            classification = lifecyclemod.classify(item_id, path=path, commit=commit, line_start=line_start,
                                                     line_end=line_end, reg=reg,
                                                     mandatory_items=mandatory_items_index, repo=repo)
            if classification.lifecycle != required_status:
                blocked.append(f"{item_id}: lifecycle {classification.lifecycle} != required_status {required_status}")
                continue
            content_hash = entry.get("content_hash")
            actual = _sha256_of(path, commit, repo=repo) if path and commit else None
            if content_hash and actual != content_hash:
                blocked.append(f"{item_id}: content_hash mismatch (expected {content_hash}, got {actual})")
                continue
            blob = gitobj.blob_at(commit, path, repo=repo) if path and commit else None
            items.append(MandatoryItem(id=item_id, cls=classification.cls, lifecycle=classification.lifecycle,
                                        path=path, commit=commit, blob=blob, line_start=line_start,
                                        line_end=line_end, sha256=actual, reason=reason, source_row=f"id:{item_id}"))

        elif "path" in entry:
            m = PATH_FORM_RE.match(entry["path"])
            if not m:
                blocked.append(f"malformed path_form: {entry['path']!r}")
                continue
            path, ref = m.group("path"), m.group("ref")
            commit = resolved_view.ref_commit(ref) or gitobj.resolve_commit(ref, repo=repo)
            if commit is None:
                blocked.append(f"{entry['path']}: ref {ref!r} does not resolve")
                continue
            blob = gitobj.blob_at(commit, path, repo=repo)
            if blob is None:
                blocked.append(f"{entry['path']}: {path} not found at {commit}")
                continue
            content_hash = entry.get("content_hash")
            actual = _sha256_of(path, commit, repo=repo)
            if content_hash and actual != content_hash:
                blocked.append(f"{entry['path']}: content_hash mismatch (expected {content_hash}, got {actual})")
                continue
            l1 = int(m.group("l1")) if m.group("l1") else None
            l2 = int(m.group("l2")) if m.group("l2") else l1
            classification = lifecyclemod.classify(path, path=path, commit=commit, line_start=l1, line_end=l2,
                                                     reg=reg, mandatory_items=mandatory_items_index, repo=repo)
            # REPAIR_PLAN.md section 3 rule 2: a path_form entry may ALSO declare `keys`/`entries`/multiple
            # `paths` directly in the task spec (the same shape a bridge-state row uses), resolved the same way.
            parts, unresolved = _resolve_row_selectors(entry, path, commit, repo=repo)
            if unresolved:
                blocked.append(f"{entry['path']}: selector(s) not resolvable at {path}@{commit}: "
                                f"{', '.join(unresolved)}")
                continue
            items.append(MandatoryItem(id=path, cls=classification.cls, lifecycle=classification.lifecycle,
                                        path=path, commit=commit, blob=blob, line_start=l1, line_end=l2,
                                        sha256=actual, reason=reason, source_row=f"path:{entry['path']}",
                                        parts=parts))
        else:
            blocked.append(f"required_inputs entry has none of state_ref/id/path: {entry!r}")

    status = STATUS_BLOCKED if blocked else STATUS_OK
    return ResolveResult(status=status, items=items, blocked_reasons=blocked)


def resolve_file(task_spec_path: str, repo: Optional[str] = None) -> ResolveResult:
    task_spec = load_yaml_file(task_spec_path)
    return resolve(task_spec, repo=repo)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="govbridge.authority.resolver")
    p.add_argument("task_spec")
    p.add_argument("--json", action="store_true", help="present regardless (output is always JSON)")
    args = p.parse_args(argv)

    result = resolve_file(args.task_spec)
    print(json.dumps(result.to_dict(), indent=1, sort_keys=True))
    return 0 if result.status == STATUS_OK else 1


if __name__ == "__main__":
    sys.exit(main())
