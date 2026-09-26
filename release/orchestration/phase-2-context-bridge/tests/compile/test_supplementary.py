"""REPAIR_DAG.yaml node R1-RS: supplementary packets for every query command (search/why/impact/history/exact/
state/gather), occurrence collapse, and dedup against the main packet and earlier supplementary packets
(REPAIR_PLAN.md section 2.9, OBS-BR-06; repairing RC-6). Synthetic fixtures only (REPAIR-1 rule 2) -- every result
dict here is a small, hand-built stand-in for what each command's own library function already returns, in that
function's own real shape (``RouteHit.to_dict()``, ``Edge.to_dict()``, ``exact``'s own result dicts, ``state``'s
``StateLookupResult.to_dict()``), never a live index or a real corpus.
"""
from __future__ import annotations

import json

import pytest

from govbridge.compile import receipt as receiptmod
from govbridge.compile import supplementary as suppmod
from govbridge.compile import validate as validatemod

TASK_SPEC = {"schema": "govbridge-task-spec/1", "task_id": "T-SUPP", "retrieval_exclusions": []}


def _hit(unit_id, unit_kind="record", route="lexical", text="content", occurrences=None, authority_class="EVIDENCE",
         lifecycle="ACTIVE"):
    return {
        "unit_id": unit_id, "unit_kind": unit_kind, "route": route, "rank": 1, "delivery": "RETRIEVED",
        "occurrences": occurrences if occurrences is not None else [
            {"ref": "records", "commit": "deadbeef", "path": f"spec/{unit_id}.yaml", "version_status": "CANONICAL",
             "line_start": 1, "line_end": 3},
        ],
        "text": text, "authority_class": authority_class, "lifecycle": lifecycle, "edge_path": [], "tier": None,
        "resolution": None,
    }


# ---------------------------------------------------------------------------------------------------------------
# search / gather (RouteHit-shaped) -- occurrence collapse and dedup.
# ---------------------------------------------------------------------------------------------------------------

def test_search_supplementary_packet_is_verifiable():
    result = {"text": "q", "routes": ["lexical"], "hits_by_route": {"lexical": [_hit("REC-A"), _hit("REC-B")]},
              "fused": [], "excluded_hits": 0}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC)
    assert built["item_count"] == 2
    assert built["deduped_count"] == 0
    problems = validatemod.verify_supplementary_packet(built["manifest"])
    assert problems == []
    assert "## H." in built["rendered"]
    assert built["manifest"]["sections"]["A"]["items"] == []


def test_occurrence_collapse_keeps_one_row_plus_a_ref_summary():
    many_refs = [
        {"ref": f"ref-{i}", "commit": "deadbeef", "path": "spec/REC-A.yaml",
         "version_status": "CANONICAL" if i == 0 else "EQUIVALENT", "line_start": 1, "line_end": 3}
        for i in range(5)
    ]
    result = {"hits_by_route": {"lexical": [_hit("REC-A", occurrences=many_refs)]}}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC)
    items = built["manifest"]["sections"]["H"]["items"]
    assert len(items) == 1
    assert "5 occurrence(s) across 5 distinct ref(s)" in built["rendered"]
    # no hit carries more than one occurrence ROW: the rendered body names exactly one `source:` location line.
    body_lines = [ln for ln in built["rendered"].splitlines() if ln.strip().startswith("source:")]
    assert len(body_lines) == 1


def test_dedup_against_main_packet_delivers_by_reference_only():
    result = {"hits_by_route": {"lexical": [_hit("REC-A", text="the full text a worker must not see twice")]}}
    dedup_ids = {suppmod.item_id_key("record", "REC-A")}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC, dedup_ids=dedup_ids)
    assert built["deduped_count"] == 1
    assert "the full text a worker must not see twice" not in built["rendered"]
    assert "by reference only" in built["rendered"]
    problems = validatemod.verify_supplementary_packet(built["manifest"])
    assert problems == []


def test_same_unit_hit_by_two_routes_merges_to_one_item():
    result = {"hits_by_route": {
        "lexical": [_hit("REC-A", route="lexical")],
        "semantic": [_hit("REC-A", route="semantic",
                           occurrences=[{"ref": "records2", "commit": "deadbeef", "path": "spec/REC-A.yaml",
                                         "version_status": "EQUIVALENT", "line_start": 1, "line_end": 3}])],
    }}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC)
    assert built["item_count"] == 1
    assert "2 occurrence(s)" in built["rendered"]


def test_gather_supplementary_packet_reuses_route_hit_shape():
    result = {"merged": [_hit("REC-G1"), _hit("REC-G2")], "merged_sha256": "x", "telemetry": {}}
    built = suppmod.build_supplementary_packet("gather", result, TASK_SPEC)
    assert built["item_count"] == 2
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_supplementary_packet_stays_within_its_command_profile():
    hits = [_hit(f"REC-{i}", text="x" * 2000) for i in range(200)]
    result = {"hits_by_route": {"lexical": hits}}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC)
    assert len(built["rendered"].encode("utf-8")) <= suppmod.profile_bytes_for("search") + 4096  # + header slack
    assert built["dropped_count"] > 0


# ---------------------------------------------------------------------------------------------------------------
# why / impact / history (Edge-shaped).
# ---------------------------------------------------------------------------------------------------------------

def _edge(src, etype, dst, occurrence="spec/X.yaml@deadbeef:1-2", note=None):
    return {"src": src, "type": etype, "dst": dst, "derivation": "TEST_DERIVATION",
            "evidence_occurrence": occurrence, "evidence_line": 1, "note": note}


def test_why_supplementary_packet_from_stage_hops():
    result = {"seed": "CX-0001", "excluded_hits": 0, "stages": {
        "requirement": {"status": "PRESENT", "hops": [_edge("CX-0001", "MENTIONS", "REQ-1")]},
        "purpose": {"status": "MISSING: purpose", "hops": []},
    }}
    built = suppmod.build_supplementary_packet("why", result, TASK_SPEC)
    assert built["item_count"] == 1
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_impact_supplementary_packet_from_graph_and_code_edges():
    result = {"seed": "sym", "max_depth": 2,
              "graph": {"OTHER": [_edge("sym", "DEFINES", "OTHER")]},
              "code": [_edge("sym", "CALLS", "other_fn", occurrence=None)], "excluded_hits": 0}
    built = suppmod.build_supplementary_packet("impact", result, TASK_SPEC)
    assert built["item_count"] == 2
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_history_supplementary_packet_from_entries_and_deleted():
    result = {"seed": "CX-0001", "entries": [{"edge": _edge("CX-0001", "MENTIONS", "CX-RES-0001"), "kind": "lesson"}],
              "deleted_in": [_edge("old_sym", "DELETED_IN", "c1")], "excluded_hits": 0}
    built = suppmod.build_supplementary_packet("history", result, TASK_SPEC)
    assert built["item_count"] == 2
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


# ---------------------------------------------------------------------------------------------------------------
# exact (show/grep/id/path) and state.
# ---------------------------------------------------------------------------------------------------------------

def test_exact_show_supplementary_packet():
    result = {"ref": "records", "commit": "deadbeef", "path": "spec/X.yaml", "blob": "b1", "size": 10,
              "corpus_rule": "r1", "corpus_effect": "INCLUDE", "excluded_hits": 0, "excluded": False,
              "text": "hello world", "text_sha256": "x", "line_start": None, "line_end": None}
    built = suppmod.build_supplementary_packet("exact", result, TASK_SPEC, subcmd="show")
    assert built["item_count"] == 1
    assert "hello world" in built["rendered"]
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_exact_show_excluded_yields_no_item():
    result = {"excluded": True, "path": "spec/X.yaml", "commit": "deadbeef", "ref": "records"}
    built = suppmod.build_supplementary_packet("exact", result, TASK_SPEC, subcmd="show")
    assert built["item_count"] == 0


def test_exact_grep_supplementary_packet():
    result = {"ref": "records", "commit": "deadbeef", "query": "CX", "excluded_skipped": 0, "excluded_hits": 0,
              "hits": [{"path": "spec/X.yaml", "line": 3, "text": "CX-0001 appears here"},
                       {"path": "spec/Y.yaml", "line": 7, "text": "CX-0002 appears here"}]}
    built = suppmod.build_supplementary_packet("exact", result, TASK_SPEC, subcmd="grep")
    assert built["item_count"] == 2
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_exact_id_supplementary_packet_mentions_and_definitions():
    result = {"ref": "records", "commit": "deadbeef", "mention_sites": [{"path": "spec/X.yaml", "line": 2,
                                                                          "text": "CX-0001"}],
              "definition_sites": [{"path": "spec/decisions/CX-0001.yaml", "commit": "deadbeef", "line_start": 1,
                                     "line_end": 5}],
              "note": "definition site resolved"}
    built = suppmod.build_supplementary_packet("exact", result, TASK_SPEC, subcmd="id")
    assert built["item_count"] == 2
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_exact_path_supplementary_packet_resolved_and_ambiguous():
    result = {"ref": "records", "commit": "deadbeef", "suffix": "X.yaml", "resolved": "spec/X.yaml",
              "ambiguous": False}
    built = suppmod.build_supplementary_packet("exact", result, TASK_SPEC, subcmd="path")
    assert built["item_count"] == 1

    ambiguous_result = {"ref": "records", "commit": "deadbeef", "suffix": "X.yaml",
                         "candidates": ["a/X.yaml", "b/X.yaml"], "ambiguous": True}
    built2 = suppmod.build_supplementary_packet("exact", ambiguous_result, TASK_SPEC, subcmd="path")
    assert built2["item_count"] == 2


def test_state_supplementary_packet():
    result = {"alias": "bridge", "key_path": "lifecycle_id", "value": "L-1", "path": "ORCH.yaml",
              "commit": "deadbeef", "blob": "b1", "line_start": 4, "line_end": 4, "seal_status": "SEAL_OK",
              "recorded_state_hash": "h", "computed_state_hash": "h", "last_changed_commit": "deadbeef",
              "last_changed_date": "2026-01-01", "excluded": False, "excluded_hits": 0}
    built = suppmod.build_supplementary_packet("state", result, TASK_SPEC)
    assert built["item_count"] == 1
    assert validatemod.verify_supplementary_packet(built["manifest"]) == []


def test_state_excluded_yields_no_item():
    result = {"alias": "bridge", "key_path": "secret", "excluded": True, "excluded_hits": 1}
    built = suppmod.build_supplementary_packet("state", result, TASK_SPEC)
    assert built["item_count"] == 0


# ---------------------------------------------------------------------------------------------------------------
# on-disk round trip: write_supplementary_packet -> govbridge.compile.validate reads it back the same way
# `govbridge packet verify DIR` will.
# ---------------------------------------------------------------------------------------------------------------

def test_write_supplementary_packet_round_trips_on_disk(tmp_path):
    result = {"hits_by_route": {"lexical": [_hit("REC-A")]}}
    built = suppmod.build_supplementary_packet("search", result, TASK_SPEC)
    meta = suppmod.write_supplementary_packet(str(tmp_path / "s1"), built, TASK_SPEC)
    assert meta["packet_kind"] == "supplementary"
    assert meta["packet_sha256"] == built["packet_sha256"]

    d = tmp_path / "s1"
    assert (d / "packet.md").exists()
    manifest_on_disk = json.loads((d / "manifest.json").read_text(encoding="utf-8"))
    assert manifest_on_disk["packet_sha256"] == built["packet_sha256"]
    assert validatemod.verify_supplementary_packet(manifest_on_disk) == []


# ---------------------------------------------------------------------------------------------------------------
# `govbridge receipt check` covers supplementary packets; omitting one fails.
# ---------------------------------------------------------------------------------------------------------------

def _minimal_main_manifest():
    from govbridge.compile import render as rendermod
    manifest = rendermod.build_manifest(
        task_spec_sha256="x", view_rows=[], build_manifest_sha256=None, bridge_code_tree=None, config_sha256={},
        budget_profile="bounded-builder", retrieval_exclusions=[], status="OK", sections={}, queries_log={},
        drops_by_section={}, notices=[],
    )
    manifest, rendered, _ = rendermod.render_packet(manifest, {}, {}, {})
    return manifest, rendered


def _real_main_packet(fixture_repo, view_path, registry_path, task_spec_factory):
    from govbridge.compile import packet as packetmod
    from govbridge.route.router import RouteSet
    task_spec = task_spec_factory(view_path)
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    return task_spec, result


def test_receipt_check_fails_when_a_supplementary_packet_is_omitted(fixture_repo, view_path, registry_path,
                                                                       task_spec_factory):
    import hashlib
    task_spec, main = _real_main_packet(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = main["manifest"]
    result = {"hits_by_route": {"lexical": [_hit("REC-A")]}}
    supp_built = suppmod.build_supplementary_packet("search", result, task_spec)

    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
    receipt = {
        "context_packet_hash": manifest["packet_sha256"],  # the supplementary packet's OWN hash is NOT listed
        "manifest_sha256": manifest["manifest_sha256"], "read_tokens": read_tokens,
        "inputs_consumed": [f"{r['unit']['id']}@{r['content_sha256']}" for r in manifest["sections"]["A"]["items"]],
        "items_relied_on": [], "external_reads": [], "outputs_produced": [], "decisions_applied": [],
        "acceptance_evidence": [], "deviations": [], "unresolved": [],
    }
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path,
                            rendered=main["rendered"], supplementary=[{"label": "s1", "manifest": supp_built["manifest"]}])
    assert out["status"] == "FAIL"
    assert any("supplementary packet" in p and "not acknowledged" in p for p in out["problems"]), out["problems"]


def test_receipt_check_passes_when_every_supplementary_packet_is_acknowledged(fixture_repo, view_path,
                                                                                 registry_path, task_spec_factory):
    import hashlib
    task_spec, main = _real_main_packet(fixture_repo, view_path, registry_path, task_spec_factory)
    manifest = main["manifest"]
    result = {"hits_by_route": {"lexical": [_hit("REC-A")]}}
    supp_built = suppmod.build_supplementary_packet("search", result, task_spec)

    m_sha = manifest["manifest_sha256"]
    read_tokens = {letter: hashlib.sha256((m_sha + letter).encode()).hexdigest()[:12]
                   for letter in ("A", "B", "C", "D", "E", "F", "G", "H", "I", "J")}
    receipt = {
        "context_packet_hash": [manifest["packet_sha256"], supp_built["packet_sha256"]],
        "manifest_sha256": [manifest["manifest_sha256"], supp_built["manifest_sha256"]],
        "read_tokens": read_tokens,
        "inputs_consumed": [f"{r['unit']['id']}@{r['content_sha256']}" for r in manifest["sections"]["A"]["items"]],
        "items_relied_on": [], "external_reads": [], "outputs_produced": [], "decisions_applied": [],
        "acceptance_evidence": [], "deviations": [], "unresolved": [],
    }
    out = receiptmod.check(manifest, receipt, task_spec, repo=str(fixture_repo.root), registry_path=registry_path,
                            rendered=main["rendered"], supplementary=[{"label": "s1", "manifest": supp_built["manifest"]}])
    assert out["status"] == "PASS", out["problems"]


# ---------------------------------------------------------------------------------------------------------------
# supplementary packets never carry authority.
# ---------------------------------------------------------------------------------------------------------------

def test_verify_supplementary_packet_refuses_mandatory_delivery():
    manifest, _ = _minimal_main_manifest()
    manifest["sections"]["A"]["items"] = [{
        "item_id": "x", "unit": {"kind": "record", "id": "X"}, "delivery": "MANDATORY", "authority_class": "OWNER_DECISION",
        "lifecycle": "ACTIVE", "content_sha256": "x",
    }]
    problems = validatemod.verify_supplementary_packet(manifest)
    assert any("non-empty" in p for p in problems)


# ---------------------------------------------------------------------------------------------------------------
# end to end through the real CLI (`govbridge search --out`), with a controlled RouteSet -- hermetic (no live
# index), but exercising the real cmd_search -> supplementary.build_supplementary_packet -> write ->
# `govbridge packet verify` path.
# ---------------------------------------------------------------------------------------------------------------

def test_cli_search_out_writes_a_verifiable_supplementary_packet(tmp_path, monkeypatch):
    from govbridge import cli
    from govbridge.route import real_routes as real_routesmod
    from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet

    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)

    def fixed_lexical(text=None, seeds=None, k=8, exclude=None, exclude_counter=None, **_kw):
        return [
            RouteHit(unit_id="REC-CLI-A", unit_kind="record", route="lexical", rank=1,
                     occurrences=(RouteOccurrence(ref="records", commit="deadbeef", path="spec/REC-CLI-A.yaml",
                                                   version_status="CANONICAL"),),
                     text="cli fixture content A", authority_class="EVIDENCE", lifecycle="ACTIVE"),
        ]

    monkeypatch.setattr(real_routesmod, "build_real_routes",
                         lambda **_kw: RouteSet(lexical=fixed_lexical))

    out_dir = tmp_path / "s1"
    rc = cli.main(["search", "cli fixture query", "--route", "lexical", "--out", str(out_dir)])
    assert rc == 0
    assert (out_dir / "manifest.json").exists()
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["packet_kind"] == "supplementary"
    assert "packet_sha256" in meta

    rc_verify = cli.main(["packet", "verify", str(out_dir)])
    assert rc_verify == 0
