#!/usr/bin/env python3
"""Manifest assembly, packet rendering and the packet hash chain (ARCHITECTURE.md section 7.4,
``schemas/packet-manifest.yaml``). Canonical JSON, sorted keys, no timestamps -- the compile timestamp goes to
telemetry, never into anything hashed.

Hash order (no circularity): each section's ``section_sha256`` is computed over its rendered BODY, which never
includes a read token; the whole manifest's ``manifest_sha256`` is computed over the manifest with
``manifest_sha256``/``packet_sha256`` set to null (reusing ``govbridge.core.manifest.manifest_sha256`` -- the exact
same rule, so this module has no competing hash convention); each section's read token is DERIVED from that
finished ``manifest_sha256`` and printed as the section's last rendered line; only THEN is ``packet_sha256`` taken
over the full rendered bytes (bodies plus read-token lines). The manifest itself is never given to the worker, only
the rendered packet -- so a token can never be copied out of the manifest instead of earned by reading the section.
"""
from __future__ import annotations

import hashlib
from typing import Optional

from govbridge.core.manifest import manifest_sha256 as _core_manifest_sha256
from govbridge.core.yamlutil import canonical_json, sha256_text

SECTION_LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")

SECTION_TITLES = {
    "A": "MANDATORY AUTHORITATIVE INPUTS",
    "B": "SYSTEM PURPOSE / WHY",
    "C": "DIRECT DEPENDENCY / IMPACT CONTEXT",
    "D": "RELEVANT ACTIVE DECISIONS",
    "E": "RELEVANT HISTORICAL / SUPERSEDED DECISIONS",
    "F": "FAILED APPROACHES / LESSONS",
    "G": "CODE / TEST / ENFORCEMENT SURFACES",
    "H": "SUPPLEMENTARY RETRIEVED CONTEXT",
    "I": "TASK CONTRACT / MUTATION SCOPE",
    "J": "COMPLETION / EVIDENCE OBLIGATIONS",
}

D_SUBBLOCK_TITLES = {
    "D.1": "D.1 -- RELEVANT ACTIVE DECISIONS",
    "D.2": "D.2 -- OWNER DIRECTION TO TEST (not yet authority)",
    "D.3": "D.3 -- HYPOTHESIS TO TEST (no classificatory force)",
}


def item_manifest_row(item) -> dict:
    return {
        "item_id": item.item_id,
        "unit": {"kind": item.unit_kind, "id": item.unit_id},
        "delivery": item.delivery,
        "authority_class": item.cls,
        "lifecycle": item.lifecycle,
        "version_status": item.version_status,
        "source": {"ref": item.ref, "commit": item.commit, "path": item.path, "blob": item.blob,
                   "line_start": item.line_start, "line_end": item.line_end},
        "content_sha256": item.content_sha256,
        "bytes": item.bytes_len(),
        "by_reference": item.by_reference,
        "route": item.route,
        "score": {"raw": item.raw_score, "rank": item.rank, "fused": item.fused_score},
        "edge_path": list(item.edge_path),
        "banner": item.banner,
    }


def _render_item_body(item) -> str:
    lines = [f"- unit: {item.unit_kind}:{item.unit_id}  (delivery={item.delivery}, route={item.route}, "
             f"class={item.cls}, lifecycle={item.lifecycle})"]
    if item.path:
        loc = item.path
        if item.commit:
            loc += f"@{item.commit}"
        if item.line_start is not None:
            loc += f":{item.line_start}-{item.line_end}"
        lines.append(f"  source: {loc}")
    if item.banner:
        lines.append(f"  [{item.banner}]")
    if item.reason:
        lines.append(f"  reason: {item.reason}")
    body = (item.text or "").rstrip("\n")
    if body:
        lines.append(body)
    return "\n".join(lines) + "\n"


def _drop_footer(d: list) -> Optional[str]:
    """``d``: either G's COMPACT drop-GROUP list (``govbridge.compile.budgets.compact_drops`` --
    ``[{tier, count, bytes, dropped_ids_sha256, sample_ids}, ...]``, BR-AR-0015 reopening defect 4) or any other
    section's unchanged raw per-ITEM drop list (``[{item_id, unit, reason, score, bytes, tier}, ...]``, one entry
    per dropped item -- the shape node B6's own test_budget_pressure, one of the six named ARCHITECTURE.md
    section 5.3 invariant tests, asserts for H). A compact group carries its own "count"; a raw item does not, so
    it counts as exactly one. Either way this aggregates to one summary line. None when nothing was dropped."""
    if not d:
        return None
    total_count = sum(g.get("count", 1) for g in d)
    total_bytes = sum(g["bytes"] for g in d)
    return f"[{total_count} items / {total_bytes} bytes omitted: see manifest]"


def _render_section_body(letter: str, sub_items: dict, queries_log: dict, drops: dict) -> str:
    """``sub_items``: for D, ``{"D.1": [...], "D.2": [...], "D.3": [...]}``; for every other letter,
    ``{letter: [...]}`` (one entry). Returns the section body text WITHOUT its read-token line."""
    out = [f"## {letter}. {SECTION_TITLES[letter]}", ""]
    if letter == "D":
        for sub in ("D.1", "D.2", "D.3"):
            items = sub_items.get(sub, [])
            out.append(f"### {D_SUBBLOCK_TITLES[sub]}")
            out.append("")
            qlist = queries_log.get(sub, [])
            if qlist:
                out.append(f"queries: {canonical_json(qlist)}")
            if not items:
                out.append("(none)")
            for item in items:
                out.append(_render_item_body(item))
            footer = _drop_footer(drops.get(sub, []))
            if footer:
                out.append(footer)
            out.append("")
    else:
        items = sub_items.get(letter, [])
        qlist = queries_log.get(letter, [])
        if qlist:
            out.append(f"queries: {canonical_json(qlist)}")
        if not items:
            out.append("(none)")
        for item in items:
            out.append(_render_item_body(item))
        footer = _drop_footer(drops.get(letter, []))
        if footer:
            out.append(footer)
    return "\n".join(out).rstrip() + "\n"


def build_manifest(*, task_spec_sha256: str, view_rows: list, build_manifest_sha256: Optional[str],
                    bridge_code_tree: Optional[str], config_sha256: dict, budget_profile: str,
                    retrieval_exclusions: list, status: str, sections: dict, queries_log: dict,
                    drops_by_section: dict, notices: list) -> dict:
    """``sections``: ``{"A": [...], ..., "D.1": [...], "D.2": [...], "D.3": [...], ..., "J": [...]}``. Builds the
    ``govbridge-packet-manifest/1`` document with ``manifest_sha256``/``packet_sha256`` left null (filled by
    ``finalize``)."""
    manifest_sections = {}
    for letter in SECTION_LETTERS:
        if letter == "D":
            sub_map = {"D.1": sections.get("D.1", []), "D.2": sections.get("D.2", []), "D.3": sections.get("D.3", [])}
            body = _render_section_body("D", sub_map, queries_log, drops_by_section)
            manifest_sections["D"] = {
                "title": SECTION_TITLES["D"],
                "subblocks": {
                    sub: {"title": D_SUBBLOCK_TITLES[sub], "queries": queries_log.get(sub, []),
                          "items": [item_manifest_row(i) for i in items],
                          "dropped": drops_by_section.get(sub, [])}
                    for sub, items in sub_map.items()
                },
                "queries": [],
                "items": [],
                "dropped": [],
                "section_sha256": sha256_text(body),
            }
        else:
            items = sections.get(letter, [])
            body = _render_section_body(letter, {letter: items}, queries_log, drops_by_section)
            manifest_sections[letter] = {
                "title": SECTION_TITLES[letter],
                "queries": queries_log.get(letter, []),
                "items": [item_manifest_row(i) for i in items],
                "dropped": drops_by_section.get(letter, []),
                "section_sha256": sha256_text(body),
            }

    manifest = {
        "packet_schema": "govbridge-packet-manifest/1",
        "task_spec_sha256": task_spec_sha256,
        "view": view_rows,
        "build_manifest_sha256": build_manifest_sha256,
        "bridge_code_tree": bridge_code_tree,
        "config_sha256": config_sha256,
        "budget_profile": budget_profile,
        "retrieval_exclusions": list(retrieval_exclusions or []),
        "status": status,
        "sections": manifest_sections,
        "notices": notices,
        "manifest_sha256": None,
        "packet_sha256": None,
    }
    return manifest


def render_packet(manifest: dict, sections: dict, queries_log: dict, drops_by_section: dict) -> tuple:
    """Finalises ``manifest`` in place (fills ``manifest_sha256``/``packet_sha256``) and returns
    ``(manifest, rendered_text, packet_id)``. Must be called exactly once, after ``build_manifest``, with the SAME
    ``sections``/``queries_log``/``drops_by_section`` used to build it (their section bodies are re-rendered here to
    attach each section's read token as its literal last line)."""
    m_sha = _core_manifest_sha256(manifest)
    manifest["manifest_sha256"] = m_sha

    parts = [f"# Context packet\n\nmanifest_sha256: {m_sha}\nstatus: {manifest['status']}\n"]
    for letter in SECTION_LETTERS:
        if letter == "D":
            sub_map = {"D.1": sections.get("D.1", []), "D.2": sections.get("D.2", []), "D.3": sections.get("D.3", [])}
            body = _render_section_body("D", sub_map, queries_log, drops_by_section)
        else:
            items = sections.get(letter, [])
            body = _render_section_body(letter, {letter: items}, queries_log, drops_by_section)
        read_token = hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
        parts.append(body.rstrip("\n") + f"\nread_token: {read_token}\n")

    rendered = "\n".join(parts)
    packet_sha = sha256_text(rendered)
    manifest["packet_sha256"] = packet_sha
    packet_id = packet_sha[:16]
    return manifest, rendered, packet_id
