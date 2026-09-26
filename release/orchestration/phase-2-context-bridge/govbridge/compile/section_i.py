#!/usr/bin/env python3
"""OBS-BR-07 (RC-9, CAUSE_ANALYSIS.md): "the task inputs are not in the packet... the query set and the answers
and receipt schemas travel outside the packet, in orchestrator-copied files." REPAIR_PLAN.md section 6: "Section I
carries the task's query set (instantiated) and the answers and receipt schemas, verbatim and by hash."

``govbridge.compile.packet`` (out of this node's mutation scope) already builds section I's own
``{objective, mutation_scope, prohibitions}`` item (``_build_i_item``). This module never replaces or edits that
-- it ADDS a second, PINNED section-I item carrying the task inputs, and re-finalises the packet (a fresh
``manifest_sha256``/``packet_sha256``/read tokens/``packet_id``) around the EXACT SAME ``sections``/``queries_log``
/``drops`` ``compile_packet`` already computed. Nothing here re-implements resolution, routing or budgeting; it
only calls back into ``govbridge.compile.render``'s own, already-generic ``build_manifest``/``render_packet``
(the same two functions ``compile_packet`` itself calls) with one more item appended.
"""
from __future__ import annotations

import json
import os
from typing import Optional

from govbridge.authority import classes as classesmod
from govbridge.compile import render as rendermod
from govbridge.compile.packet import PacketItem, sort_key
from govbridge.core.yamlutil import sha256_text

SCHEMA_RELPATHS = {
    "answers": os.path.join("ARCHITECTURE", "schemas", "answers.yaml"),
    "receipt": os.path.join("ARCHITECTURE", "schemas", "receipt.yaml"),
}


def _domain_path(rel: str) -> str:
    from govbridge import GOV_BRIDGE_DOMAIN
    return os.path.join(GOV_BRIDGE_DOMAIN, rel)


def _read_schema(name: str) -> dict:
    path = _domain_path(SCHEMA_RELPATHS[name])
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    return {"path": path, "text": text, "sha256": sha256_text(text)}


def instantiated_query_set(task_spec: dict, repo: Optional[str] = None) -> list:
    """The task's OWN query set, fully instantiated (REPAIR_PLAN.md section 2.1, node R1-GA1) -- ``[]`` for a task
    spec that declares no ``queries`` at all (e.g. a control task). Raises
    ``govbridge.gather.instantiate.QueryNotExecutable`` on the first entry that cannot be made executable -- the
    SAME "never a silent skip" discipline ``gather`` itself applies, rather than this module inventing a second,
    quieter one for section I."""
    from govbridge import GOV_BRIDGE_DOMAIN
    from govbridge.gather import instantiate as instmod

    raw = task_spec.get("queries")
    doc = instmod.load_query_set(raw, repo=repo, base_dir=GOV_BRIDGE_DOMAIN)
    return instmod.instantiate_all(doc)


def build_task_inputs_item(task_spec: dict, repo: Optional[str] = None) -> PacketItem:
    queries = instantiated_query_set(task_spec, repo=repo)
    queries_text = json.dumps(queries, indent=1, sort_keys=True)
    answers_schema = _read_schema("answers")
    receipt_schema = _read_schema("receipt")

    body = json.dumps({
        "instantiated_queries": {"count": len(queries), "sha256": sha256_text(queries_text), "queries": queries},
        "answers_schema": answers_schema,
        "receipt_schema": receipt_schema,
    }, indent=1, sort_keys=True)
    content_sha = sha256_text(body)

    return PacketItem(
        unit_kind="section", unit_id="I.task_inputs", section="I", delivery="PINNED", cls=None,
        lifecycle=classesmod.LIFECYCLE_ACTIVE, version_status=None, ref=None, commit=None, path=None, blob=None,
        line_start=None, line_end=None, text=body, content_sha256=content_sha, by_reference=False,
        route="task_spec", raw_score=None, rank=None, fused_score=None, edge_path=(), reason=(
            "OBS-BR-07 (RC-9): the instantiated query set and the answers/receipt schemas, verbatim and by hash "
            "-- carried IN the packet instead of travelling as orchestrator-copied files"),
        banner=None, source_sha256=content_sha, delivered_sha256=content_sha,
    )


def with_task_inputs_in_section_i(result: dict, task_spec: dict, repo: Optional[str] = None) -> dict:
    """Given ``govbridge.compile.packet.compile_packet``'s own return dict, returns a NEW dict of the same shape
    whose section I additionally carries ``build_task_inputs_item``, with a freshly finalised manifest/packet."""
    old_manifest = result["manifest"]
    sections = {k: list(v) for k, v in result["sections"].items()}
    sections.setdefault("I", [])
    sections["I"] = sorted(sections["I"] + [build_task_inputs_item(task_spec, repo=repo)], key=sort_key)

    manifest = rendermod.build_manifest(
        task_spec_sha256=old_manifest["task_spec_sha256"], view_rows=old_manifest["view"],
        build_manifest_sha256=old_manifest["build_manifest_sha256"],
        bridge_code_tree=old_manifest["bridge_code_tree"], config_sha256=old_manifest["config_sha256"],
        budget_profile=old_manifest["budget_profile"], retrieval_exclusions=old_manifest["retrieval_exclusions"],
        status=old_manifest["status"], sections=sections, queries_log=result["queries_log"],
        drops_by_section=result["drops"], notices=old_manifest["notices"],
    )
    manifest, rendered, packet_id = rendermod.render_packet(manifest, sections, result["queries_log"],
                                                             result["drops"])

    new_result = dict(result)
    new_result.update({
        "sections": sections, "manifest": manifest, "rendered": rendered,
        "packet_sha256": manifest["packet_sha256"], "manifest_sha256": manifest["manifest_sha256"],
        "packet_id": packet_id,
    })
    return new_result
