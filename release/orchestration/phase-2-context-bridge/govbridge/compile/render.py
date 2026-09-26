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
import re
from typing import Optional

from govbridge.core.manifest import manifest_sha256 as _core_manifest_sha256
from govbridge.core.yamlutil import canonical_json, sha256_text

SECTION_LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")

_SECTION_HEADING_RE = re.compile(r"(?m)^## ([A-J])\. ")

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
        # BR-DAG node R1-RM (REPAIR_PLAN.md section 3 rule 4): ``source_sha256`` is the SAME value as
        # ``content_sha256`` above under its honest name (the resolver's own record, for a MANDATORY item);
        # ``delivered_sha256`` is the sha256 of what this row's rendered body ACTUALLY contains. They coincide
        # except for a partially-delivered mandatory item (see the ``MANDATORY_PARTIAL_DELIVERY`` notice) -- a
        # receipt that acknowledges ``inputs_consumed`` by ``content_sha256``/``source_sha256`` is acknowledging
        # the SOURCE record's identity, never claiming it read bytes that were never delivered.
        "source_sha256": getattr(item, "source_sha256", None),
        "delivered_sha256": getattr(item, "delivered_sha256", None),
        # BR-DAG-AMEND reopening ("packet verify cannot detect silent truncation"): the THIRD, independent
        # measurement -- what the row DECLARES (whole file, anchored slice, or the ordered selector parts),
        # recomputable from Git alone (``resolver.declared_parts``). ``packet verify`` recomputes this fresh and
        # only then checks delivered_sha256 against it (directly, or via a notice's tiled ranges).
        "declared_sha256": getattr(item, "declared_sha256", None),
        "declared_bytes": getattr(item, "declared_bytes", None),
        "is_directory": getattr(item, "is_directory", False),
        "directory_members": list(getattr(item, "directory_members", ()) or ()),
        "bytes": item.bytes_len(),
        "by_reference": item.by_reference,
        "route": item.route,
        "score": {"raw": item.raw_score, "rank": item.rank, "fused": item.fused_score},
        "edge_path": list(item.edge_path),
        "banner": item.banner,
        # REPAIR_DAG node R1-GA3 (REPAIR_PLAN.md section 2.8): "per-item tags: the query ids and facets each item
        # serves, so an agent can find 'the tests for query X'". () for anything not produced by
        # govbridge.gather (section A, I, J, and every seed-derived B/C/F/G item) -- unchanged by this node.
        "query_ids": list(getattr(item, "query_ids", ()) or ()),
        "facet_tags": list(getattr(item, "facet_tags", ()) or ()),
    }


def item_body_marker(unit_kind: str, unit_id: str, tag: str) -> str:
    """BR-DAG-AMEND-R1-10: the smallest item-delimiting format this module adds -- an exact, unambiguous marker
    line bracketing ONE item's DELIVERED BODY ONLY (never the metadata lines above it). It embeds only
    ``unit_kind``/``unit_id`` -- both already printed, verbatim, on the item's own ``- unit: ...`` line one line
    above -- and never the internal ``item_id`` hash (``govbridge/demo/grade.py`` documents, and relies on, "the
    ONLY identifier actually printed in the rendered packet text... never the hash"; this stays true). ``tag`` is
    ``"body-begin"`` or ``"body-end"``."""
    return f"<!-- govbridge:item {tag} {unit_kind}:{unit_id} -->"


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
    # REPAIR_DAG node R1-GA3 (REPAIR_PLAN.md section 2.8): per-item query/facet tags, printed only when present
    # (a seed-derived item, or anything from section A/I/J, carries neither -- this line never appears for those,
    # so their own rendered body is byte-for-byte unchanged by this node) -- outside the body-marker pair below,
    # so it never perturbs the delivered-body re-extraction/recomposition check.
    query_ids = tuple(getattr(item, "query_ids", ()) or ())
    facet_tags = tuple(getattr(item, "facet_tags", ()) or ())
    if query_ids or facet_tags:
        lines.append(f"  queries: {list(query_ids)}  facets: {list(facet_tags)}")
    body = (item.text or "").rstrip("\n")
    # BR-DAG-AMEND-R1-10 (routed from BR-AR-0022's open issue): bracket the delivered body with an exact,
    # unambiguous marker pair so `packet verify`/`receipt check` can re-extract precisely this substring from the
    # RENDERED packet (never the manifest's own claim) and independently recompute its hash -- catching a renderer
    # that drops or mangles content the compiler already hashed correctly. Always present (even for an empty
    # body), so extraction never has to guess whether a body line was omitted.
    lines.append(item_body_marker(item.unit_kind, item.unit_id, "body-begin"))
    lines.append(body)
    lines.append(item_body_marker(item.unit_kind, item.unit_id, "body-end"))
    return "\n".join(lines) + "\n"


def extract_section_text(rendered: str, letter: str) -> Optional[str]:
    """The raw text of section ``letter``'s own body -- from its ``"## {letter}. "`` heading up to (but not
    including) the next section heading, or the end of the packet for the last section. The same boundary rule
    ``tests/compile/test_compile_outage.py``/``test_compile_budget_pressure.py`` already use via
    ``rendered.index("## A.")``/``rendered.index("## B.")``, generalised to any letter and to a letter with no
    following section. ``None`` if this rendered text has no such heading at all."""
    starts = [(m.group(1), m.start()) for m in _SECTION_HEADING_RE.finditer(rendered)]
    for i, (found_letter, pos) in enumerate(starts):
        if found_letter == letter:
            end = starts[i + 1][1] if i + 1 < len(starts) else len(rendered)
            return rendered[pos:end]
    return None


def extract_item_delivered_body(rendered: str, letter: str, unit_kind: str, unit_id: str) -> tuple:
    """BR-DAG-AMEND-R1-10: ``(found, body, ambiguous)``. Locates the UNIQUE ``body-begin``/``body-end`` marker pair
    ``_render_item_body`` wrote for ``(unit_kind, unit_id)`` inside section ``letter``'s own rendered text (never
    the whole packet -- the same unit could legitimately be retrieved into a different section too), and returns
    exactly the bytes between them: the identical string ``_render_item_body`` built as ``body``, so hashing it
    with the SAME rule the compiler used reproduces the compiler's own value whenever the render was honest.

    ``found=False`` when no marker pair exists at all (the renderer never emitted this item); ``ambiguous=True``
    when MORE than one marker pair for the same ``(unit_kind, unit_id)`` is found in that section -- re-extraction
    is then meaningless and the caller must treat it as a verify failure, never silently pick one."""
    section_text = extract_section_text(rendered, letter)
    if section_text is None:
        return False, None, False
    begin = item_body_marker(unit_kind, unit_id, "body-begin")
    end = item_body_marker(unit_kind, unit_id, "body-end")
    begin_positions = [m.start() for m in re.finditer(re.escape(begin), section_text)]
    if not begin_positions:
        return False, None, False
    if len(begin_positions) > 1:
        return True, None, True
    b_start = begin_positions[0] + len(begin)
    e_pos = section_text.find(end, b_start)
    if e_pos == -1:
        return False, None, False
    body = section_text[b_start:e_pos]
    # `_render_item_body` joins its `lines` list with "\n", so exactly one "\n" separates the begin marker from
    # the body and the body from the end marker (even when the body itself is the empty string) -- strip exactly
    # that one leading/trailing newline, never more, so a genuinely blank first/last body line is preserved.
    if body.startswith("\n"):
        body = body[1:]
    if body.endswith("\n"):
        body = body[:-1]
    return True, body, False


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
