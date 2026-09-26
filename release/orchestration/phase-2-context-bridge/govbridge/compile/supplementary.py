#!/usr/bin/env python3
"""Supplementary packets (REPAIR_PLAN.md section 2.9, OBS-BR-06; REPAIR_DAG.yaml node R1-RS -- repairing RC-6:
"there are no supplementary packets... query outputs are raw JSON... the bootstrap inlines the whole packet").

Every query command (``search``, ``why``, ``impact``, ``history``, ``exact``, ``state``, ``gather``) can now be
asked to write ONE supplementary packet directory (``manifest.json``, ``packet.md``, ``meta.json``, ``task_spec.
yaml``) under ``--out``, in EXACTLY the same on-disk shape ``govbridge compile --out DIR`` already writes, so the
SAME ``govbridge packet verify DIR`` / ``govbridge receipt check --packet DIR`` tools cover it too. This module
is generic over which command produced the JSON result (OC-BR-02): it normalises whatever RouteHit-shaped hits or
graph Edge-shaped hops a command's result carries into one uniform item shape, then:

* **collapses occurrences** -- a unit retrieved at many refs (run-1 measured up to 98 per hit, CAUSE_ANALYSIS.md
  RC-6: 406,501 bytes of near-duplicate per-ref metadata) is delivered as ONE canonical occurrence plus a per-ref
  IDENTITY SUMMARY (a count and a sha256 over the sorted ref names) -- never a second occurrence row per ref;
* **deduplicates by item id** against the main packet and every earlier supplementary packet in the same run
  (``dedup_ids``) -- a unit already delivered elsewhere is kept (never silently hidden) but reduced to a bare
  reference pointer, never a second full copy of its content;
* **budgets** the result to a small, per-command byte profile (``COMMAND_PROFILE_BYTES`` below) via
  ``govbridge.compile.budgets.enforce_section`` -- the SAME budget-dropping code the main packet's own sections
  use, so a supplementary packet can never grow into a second unbounded dump.

Every item lands in section H (``SUPPLEMENTARY RETRIEVED CONTEXT`` -- render.py's own, pre-existing letter for
exactly this kind of content) with ``delivery="RETRIEVED"``; a supplementary packet never carries authority
(``validate.verify_supplementary_packet`` refuses a MANDATORY/PINNED item or a non-empty section A). An item's
resolved ``authority_class``/``lifecycle`` (when the underlying hit had one) is kept as INFORMATION in its
rendered text, never used to decide placement -- a supplementary packet has no ladder/placement rules of its own
beyond "evidence only," so there is nothing here that could conflict with ``validate.verify_placement``.
"""
from __future__ import annotations

import json
from typing import Iterable, Optional

from govbridge.authority import classes as classesmod
from govbridge.compile import budgets as budgetsmod
from govbridge.compile import render as rendermod
from govbridge.compile.packet import PacketItem, sort_key
from govbridge.core.yamlutil import canonical_json, sha256_text

#: REPAIR_PLAN.md section 2.9: "budgeted (a per-command profile)". Deliberately small and SEPARATE from
#: config/budgets.yaml's own compile profiles (that file is out of this node's mutation scope, and its profiles
#: bound the MAIN packet, a different artifact) -- a supplementary packet is meant to stay a bounded ADDENDUM to
#: it, never a second unbounded dump (CAUSE_ANALYSIS.md RC-6 measured 1,063,203 raw bytes for run-1's own 104
#: uncontrolled command outputs).
COMMAND_PROFILE_BYTES = {
    "search": 40 * 1024,
    "why": 40 * 1024,
    "impact": 40 * 1024,
    "history": 40 * 1024,
    "exact": 40 * 1024,
    "state": 16 * 1024,
    "gather": 60 * 1024,
}
DEFAULT_PROFILE_BYTES = 40 * 1024


def profile_bytes_for(command: str) -> int:
    return COMMAND_PROFILE_BYTES.get(command, DEFAULT_PROFILE_BYTES)


# -----------------------------------------------------------------------------------------------------------
# Step 1: normalise a command's own JSON result into a flat list of {unit_kind, unit_id, route, text,
# authority_class, lifecycle, occurrences: [...], reason} dicts -- generic per command, never per query text or
# subject (OC-BR-02).
# -----------------------------------------------------------------------------------------------------------

def _occ_from_route_occurrence(o: dict) -> dict:
    return {"ref": o.get("ref"), "commit": o.get("commit"), "path": o.get("path"),
            "line_start": o.get("line_start"), "line_end": o.get("line_end"),
            "version_status": o.get("version_status")}


def _items_from_route_hits(hits: Iterable[dict]) -> list:
    """``search``'s ``hits_by_route`` (every route, flattened) and ``gather``'s own ``merged`` list are BOTH
    ``govbridge.route.router.RouteHit.to_dict()``-shaped -- one generic extraction covers both commands. The same
    unit hit by more than one route/round is merged into ONE row, its occurrences concatenated (occurrence
    collapse then reduces THOSE to one canonical occurrence plus a ref summary, in ``_collapse_occurrences``)."""
    seen: dict = {}
    for h in hits:
        if not isinstance(h, dict):
            continue
        key = (h.get("unit_kind") or "unit", h.get("unit_id") or "?")
        occs = [_occ_from_route_occurrence(o) for o in (h.get("occurrences") or []) if isinstance(o, dict)]
        if key in seen:
            seen[key]["occurrences"].extend(occs)
            continue
        seen[key] = {
            "unit_kind": key[0], "unit_id": key[1], "route": h.get("route"), "text": h.get("text") or "",
            "authority_class": h.get("authority_class"), "lifecycle": h.get("lifecycle"),
            "occurrences": occs, "reason": None,
        }
    return list(seen.values())


def _parse_occurrence_string(s: Optional[str]) -> dict:
    """``"path@commit"`` or ``"path@commit:L1-L2"`` -> ``{path, commit, line_start, line_end}`` -- the exact shape
    ``govbridge.graph.edges.Edge.evidence_occurrence`` uses."""
    if not s or "@" not in s:
        return {"path": None, "commit": None, "line_start": None, "line_end": None}
    path, _, rest = s.partition("@")
    commit, _, lines = rest.partition(":")
    l1 = l2 = None
    if lines:
        parts = lines.split("-", 1)
        try:
            l1 = int(parts[0])
            l2 = int(parts[1]) if len(parts) > 1 else l1
        except ValueError:
            l1 = l2 = None
    return {"path": path or None, "commit": commit or None, "line_start": l1, "line_end": l2}


def _items_from_edges(edges: Iterable[dict]) -> list:
    """``why``/``impact``/``history`` all surface ``govbridge.graph.edges.Edge.to_dict()`` rows (directly, or one
    layer down inside a ``{status, hops}`` stage block / a ``{edge, ...}`` entry). An edge has no ``unit_id`` of
    its own, so this synthesises one, deterministically, from its own (src, type, dst) -- the same edge reached
    twice (from two different stages/hops) collapses to one row via that same synthesised id."""
    seen: dict = {}
    for e in edges:
        if not isinstance(e, dict) or e.get("type") is None:
            continue
        unit_id = f"{e.get('type')}:{e.get('src')}->{e.get('dst')}"
        occ = _parse_occurrence_string(e.get("evidence_occurrence"))
        occ["ref"] = None
        key = ("edge", unit_id)
        text = e.get("note") or f"{e.get('src')} --{e.get('type')}--> {e.get('dst')} ({e.get('derivation')})"
        if key in seen:
            seen[key]["occurrences"].append(occ)
            continue
        seen[key] = {"unit_kind": "edge", "unit_id": unit_id, "route": "graph", "text": text,
                     "authority_class": None, "lifecycle": None, "occurrences": [occ],
                     "reason": e.get("derivation")}
    return list(seen.values())


def _items_from_why(result: dict) -> list:
    edges = []
    for block in (result.get("stages") or {}).values():
        edges.extend(block.get("hops") or [])
    return _items_from_edges(edges)


def _items_from_impact(result: dict) -> list:
    edges = []
    for unit_edges in (result.get("graph") or {}).values():
        edges.extend(unit_edges or [])
    edges.extend(result.get("code") or [])
    return _items_from_edges(edges)


def _items_from_history(result: dict) -> list:
    edges = []
    for entry in (result.get("entries") or []):
        if entry.get("edge"):
            edges.append(entry["edge"])
    edges.extend(result.get("deleted_in") or [])
    return _items_from_edges(edges)


def _items_from_exact(subcmd: str, result: dict) -> list:
    if subcmd == "show":
        if result.get("error") or result.get("excluded"):
            return []
        occ = {"ref": result.get("ref"), "commit": result.get("commit"), "path": result.get("path"),
               "line_start": result.get("line_start"), "line_end": result.get("line_end")}
        return [{"unit_kind": "occurrence", "unit_id": f"{result.get('path')}@{result.get('commit')}",
                 "route": "exact", "text": result.get("text") or "", "authority_class": None, "lifecycle": None,
                 "occurrences": [occ], "reason": "exact show"}]
    if subcmd == "grep":
        return [
            {"unit_kind": "line", "unit_id": f"{h.get('path')}:{h.get('line')}", "route": "exact",
             "text": h.get("text") or "", "authority_class": None, "lifecycle": None,
             "occurrences": [{"ref": result.get("ref"), "commit": result.get("commit"), "path": h.get("path"),
                               "line_start": h.get("line"), "line_end": h.get("line")}],
             "reason": "exact grep"}
            for h in (result.get("hits") or [])
        ]
    if subcmd == "id":
        out = [
            {"unit_kind": "line", "unit_id": f"{h.get('path')}:{h.get('line')}", "route": "exact",
             "text": h.get("text") or "", "authority_class": None, "lifecycle": None,
             "occurrences": [{"ref": result.get("ref"), "commit": result.get("commit"), "path": h.get("path"),
                               "line_start": h.get("line"), "line_end": h.get("line")}],
             "reason": "exact id mention"}
            for h in (result.get("mention_sites") or [])
        ]
        out.extend(
            {"unit_kind": "definition", "unit_id": f"{d.get('path')}:{d.get('line_start')}", "route": "exact",
             "text": "", "authority_class": None, "lifecycle": None,
             "occurrences": [{"ref": None, "commit": d.get("commit"), "path": d.get("path"),
                               "line_start": d.get("line_start"), "line_end": d.get("line_end")}],
             "reason": "exact id definition"}
            for d in (result.get("definition_sites") or [])
        )
        return out
    if subcmd == "path":
        out = []
        if result.get("resolved"):
            out.append({"unit_kind": "path", "unit_id": result["resolved"], "route": "exact", "text": "",
                        "authority_class": None, "lifecycle": None,
                        "occurrences": [{"ref": result.get("ref"), "commit": result.get("commit"),
                                         "path": result["resolved"], "line_start": None, "line_end": None}],
                        "reason": "exact path resolve"})
        out.extend(
            {"unit_kind": "path", "unit_id": c, "route": "exact", "text": "", "authority_class": None,
             "lifecycle": None, "occurrences": [{"ref": result.get("ref"), "commit": result.get("commit"),
                                                  "path": c, "line_start": None, "line_end": None}],
             "reason": "exact path candidate"}
            for c in (result.get("candidates") or [])
        )
        return out
    return []


def _items_from_state(result: dict) -> list:
    if result.get("excluded"):
        return []
    unit_id = f"{result.get('alias')}#{result.get('key_path')}"
    occ = {"ref": None, "commit": result.get("commit"), "path": result.get("path"),
           "line_start": result.get("line_start"), "line_end": result.get("line_end")}
    text = json.dumps(result.get("value"), indent=1, sort_keys=True, default=str)
    return [{"unit_kind": "state_key", "unit_id": unit_id, "route": "state", "text": text,
             "authority_class": None, "lifecycle": None, "occurrences": [occ], "reason": "state get"}]


def extract_items(command: str, result: dict, subcmd: Optional[str] = None) -> list:
    """The one dispatcher every caller uses -- ``command`` is the query command name (``search``, ``why``,
    ``impact``, ``history``, ``exact``, ``state``, ``gather``); ``subcmd`` disambiguates ``exact``'s own
    ``show``/``grep``/``id``/``path``."""
    if command in ("search", "gather"):
        hits = result.get("merged") if command == "gather" else [
            h for hits in (result.get("hits_by_route") or {}).values() for h in hits]
        return _items_from_route_hits(hits or [])
    if command == "why":
        return _items_from_why(result)
    if command == "impact":
        return _items_from_impact(result)
    if command == "history":
        return _items_from_history(result)
    if command == "exact":
        return _items_from_exact(subcmd or "show", result)
    if command == "state":
        return _items_from_state(result)
    return []


# -----------------------------------------------------------------------------------------------------------
# Step 2: occurrence collapse + item-id dedup -> PacketItem, then budget + render exactly like the main packet.
# -----------------------------------------------------------------------------------------------------------

def item_id_key(unit_kind: str, unit_id: str) -> str:
    """The SAME ``"{kind}:{id}"`` shape a main-packet caller already has on hand (``manifest['sections'][letter]
    ['items'][*]['unit']`` -- ``{"kind": ..., "id": ...}``), so a caller can build ``dedup_ids`` straight from an
    already-compiled manifest with no extra bookkeeping of its own."""
    return f"{unit_kind}:{unit_id}"


def _collapse_occurrences(occurrences: list) -> tuple:
    """``(canonical_occurrence, ref_summary)`` -- REPAIR_DAG.yaml node R1-RS's own "occurrence collapse"
    deliverable (CAUSE_ANALYSIS.md RC-6: "each search hit lists every occurrence across 98 refs"). The canonical
    occurrence (``version_status == "CANONICAL"``, else simply the first -- both deterministic, never re-ordered
    by score) is kept in full; every OTHER ref this same unit occurs at is reduced to a count and a sha256 over
    its sorted, deduplicated ref names -- never a second occurrence row per ref."""
    if not occurrences:
        return {}, {"occurrence_count": 0, "distinct_refs": 0, "refs_sha256": sha256_text("")}
    canonical = next((o for o in occurrences if o.get("version_status") == "CANONICAL"), occurrences[0])
    refs = sorted({o.get("ref") for o in occurrences if o.get("ref")})
    return canonical, {
        "occurrence_count": len(occurrences), "distinct_refs": len(refs),
        "refs_sha256": sha256_text("\n".join(refs)),
    }


def _to_packet_item(raw: dict, dedup_ids: set) -> tuple:
    """``(PacketItem, was_deduped: bool)``. ``dedup_ids``: ``"{kind}:{id}"`` strings already present in the main
    packet or an earlier supplementary packet THIS run wrote -- REPAIR_PLAN.md section 2.9: "deduplicated against
    the main packet and earlier supplementary packets, by item id". A deduped unit is never silently hidden (its
    row, and its occurrence summary, still appear) -- only its full text body is replaced with a bare reference."""
    unit_kind, unit_id = raw["unit_kind"], raw["unit_id"]
    key = item_id_key(unit_kind, unit_id)
    canonical, ref_summary = _collapse_occurrences(raw.get("occurrences") or [])
    deduped = key in dedup_ids

    lines = []
    if ref_summary["occurrence_count"] > 1:
        lines.append(f"[{ref_summary['occurrence_count']} occurrence(s) across {ref_summary['distinct_refs']} "
                      f"distinct ref(s); refs_sha256={ref_summary['refs_sha256']}]")
    if raw.get("authority_class") or raw.get("lifecycle"):
        lines.append(f"[resolved authority_class={raw.get('authority_class')} lifecycle={raw.get('lifecycle')}]")
    if deduped:
        lines.append(f"[already delivered as {key} in the main packet or an earlier supplementary packet in this "
                      f"run -- by reference only, never duplicated]")
    else:
        text_body = raw.get("text") or ""
        if text_body:
            lines.append(text_body)
    body = "\n".join(lines) if lines else ""
    content_sha = sha256_text(body)

    item = PacketItem(
        unit_kind=unit_kind, unit_id=unit_id, section="H", delivery="RETRIEVED", cls=None,
        lifecycle=classesmod.LIFECYCLE_UNKNOWN, version_status=canonical.get("version_status"),
        ref=canonical.get("ref"), commit=canonical.get("commit"), path=canonical.get("path"), blob=None,
        line_start=canonical.get("line_start"), line_end=canonical.get("line_end"), text=body,
        content_sha256=content_sha, by_reference=deduped, route=raw.get("route") or "supplementary",
        raw_score=None, rank=None, fused_score=None, edge_path=(), reason=raw.get("reason"), banner=None,
        source_sha256=content_sha, delivered_sha256=content_sha,
    )
    return item, deduped


def build_supplementary_packet(command: str, result: dict, task_spec: dict, *, subcmd: Optional[str] = None,
                                dedup_ids: Optional[Iterable[str]] = None,
                                budget_bytes: Optional[int] = None) -> dict:
    """The one entry point every ``--out``-capable CLI command uses. Returns
    ``{"manifest", "rendered", "packet_id", "packet_sha256", "manifest_sha256", "item_count", "deduped_count",
    "dropped_count"}``. Never raises on an empty result -- an empty H section is a well-formed, verifiable, empty
    supplementary packet."""
    dedup_ids = set(dedup_ids or ())
    raw_items = extract_items(command, result, subcmd=subcmd)

    items, deduped_count = [], 0
    for raw in raw_items:
        item, was_deduped = _to_packet_item(raw, dedup_ids)
        items.append(item)
        if was_deduped:
            deduped_count += 1
    items.sort(key=sort_key)

    profile = budgetsmod.BudgetProfile(
        name=f"supplementary-{command}", total_bytes=budget_bytes or profile_bytes_for(command),
        section_caps_bytes={"H": budget_bytes or profile_bytes_for(command)}, per_item_cap_bytes=24 * 1024,
        rrf_k=60, graph_neighbour_depth=1, parent_expansion_top_n=3, max_slice_chars=1600,
        section_header_bytes=1024, g_fanout={},
    )
    kept, drops = budgetsmod.enforce_section("H", items, profile)
    drops_by_section = budgetsmod.compact_drops(drops, compact_sections=())

    task_spec_sha256 = sha256_text(canonical_json(task_spec))
    manifest = rendermod.build_manifest(
        task_spec_sha256=task_spec_sha256, view_rows=[], build_manifest_sha256=None, bridge_code_tree=None,
        config_sha256={}, budget_profile=f"supplementary-{command}",
        retrieval_exclusions=task_spec.get("retrieval_exclusions") or [], status="OK",
        sections={"H": kept}, queries_log={}, drops_by_section=drops_by_section,
        notices=[{"type": "SUPPLEMENTARY_PACKET", "command": command, "subcmd": subcmd,
                  "item_count": len(raw_items), "deduped_count": deduped_count, "dropped_count": len(drops)}],
    )
    manifest, rendered, packet_id = rendermod.render_packet(manifest, {"H": kept}, {}, drops_by_section)

    return {
        "manifest": manifest, "rendered": rendered, "packet_id": packet_id,
        "packet_sha256": manifest["packet_sha256"], "manifest_sha256": manifest["manifest_sha256"],
        "item_count": len(raw_items), "deduped_count": deduped_count, "dropped_count": len(drops),
    }


def write_supplementary_packet(out_dir: str, built: dict, task_spec: dict) -> dict:
    """Writes ``built`` (``build_supplementary_packet``'s own return value) to ``out_dir`` in EXACTLY the shape
    ``govbridge compile --out DIR`` already writes (``manifest.json``, ``packet.md``, ``task_spec.yaml``,
    ``meta.json``), so ``govbridge packet verify DIR`` / ``govbridge receipt check --packet DIR`` need no special
    case for a supplementary packet -- ``meta.json``'s own ``packet_kind: "supplementary"`` is how they tell the
    two apart. Returns the written ``meta.json`` dict."""
    import yaml
    from pathlib import Path

    d = Path(out_dir)
    d.mkdir(parents=True, exist_ok=True)
    (d / "packet.md").write_text(built["rendered"], encoding="utf-8")
    (d / "manifest.json").write_text(json.dumps(built["manifest"], indent=1, sort_keys=True), encoding="utf-8")
    (d / "task_spec.yaml").write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")
    meta = {
        "packet_kind": "supplementary", "status": "OK", "packet_id": built["packet_id"],
        "packet_sha256": built["packet_sha256"], "manifest_sha256": built["manifest_sha256"],
        "item_count": built["item_count"], "deduped_count": built["deduped_count"],
        "dropped_count": built["dropped_count"],
    }
    (d / "meta.json").write_text(json.dumps(meta, indent=1, sort_keys=True), encoding="utf-8")
    return meta
