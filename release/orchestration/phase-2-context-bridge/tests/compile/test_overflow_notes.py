"""REPAIR_DAG.yaml node R1-GA3 acceptance (REPAIR_PLAN.md section 2.8/2.9/2.10, OD-BR-06 section 4): "when merged
evidence exceeds the profile: evidence notes (the R1-RN schema) plus supplementary packets (R1-RS). The main
packet keeps the mandatory sources, the notes and each facet's top items; nothing is silently discarded."

A synthetic fixture with far more gathered evidence than a tiny H budget can hold: every item that does not fit
must be accounted for by an R1-RN hierarchical evidence note (grounded claims, re-verified fresh from Git by
``govbridge.notes.validate``) and an R1-RS supplementary packet (re-verified by
``govbridge.compile.validate.verify_supplementary_packet``) -- never simply gone. Every id here is OV-* (OVerflow),
unrelated to Review-8/Phase-2 (OC-BR-02); this file reuses ``tests/compile/conftest.py``'s shared fixture
repo/view/registry.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

from govbridge.compile import packet as packetmod
from govbridge.compile import validate as validatemod
from govbridge.notes import validate as notesvalidatemod
from govbridge.route.router import RouteHit, RouteOccurrence, RouteSet

N = 60


def _commit_overflow_fixture(fixture_repo) -> tuple:
    lines = [f"line number {i} of the overflow fixture, some real retrievable content" for i in range(N)]
    text = "\n".join(lines) + "\n"
    path_rel = "src/overflow_fixture.txt"
    (fixture_repo.root / path_rel).parent.mkdir(parents=True, exist_ok=True)
    (fixture_repo.root / path_rel).write_text(text, encoding="utf-8")
    subprocess.run(["git", "-C", str(fixture_repo.root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(fixture_repo.root), "-c", "user.email=t@example.com", "-c", "user.name=t",
                     "commit", "-q", "-m", "overflow fixture: a many-line file"],
                    check=True, capture_output=True)
    commit = subprocess.run(["git", "-C", str(fixture_repo.root), "rev-parse", "HEAD"],
                             check=True, capture_output=True, text=True).stdout.strip()
    return path_rel, commit, lines


def _fake_lexical(path_rel: str, commit: str, lines: list):
    pool = [
        RouteHit(unit_id=f"OV-{i:04d}", unit_kind="chunk", route="lexical", rank=i + 1,
                 occurrences=(RouteOccurrence(ref="records", commit=commit, path=path_rel,
                                               version_status="CANONICAL", line_start=i + 1, line_end=i + 1),),
                 text=lines[i], authority_class="EVIDENCE", lifecycle="ACTIVE")
        for i in range(len(lines))
    ]

    def _route(text=None, k=8, offset=0, exclude=None, exclude_counter=None, page_info_out=None, **kw):
        page = pool[offset:offset + k]
        if page_info_out is not None:
            next_off = offset + len(page)
            page_info_out["next_offset"] = next_off if next_off < len(pool) else None
        return list(page)
    return _route


def _write_facets(tmp_path: Path) -> str:
    p = tmp_path / "ov-facets.yaml"
    p.write_text(f"""schema: govbridge-facets/1
default_batch_size: {N}
default_target_items: {N}
default_max_rounds: 2
default_threads: 1
facets:
  ov:
    routes: [lexical]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.1
    target_items: {N}
class_facets: {{}}
""", encoding="utf-8")
    return str(p)


def _write_budgets(tmp_path: Path, h_cap_kb: int = 1) -> str:
    p = tmp_path / "ov-budgets.yaml"
    p.write_text(f"""schema: govbridge-budgets/1
rrf_k: 60
graph_neighbour_depth: 1
parent_expansion_top_n: 3
max_slice_chars: 1600
per_item_cap_kb: 24
section_header_bytes: 256
profiles:
  ov-tiny:
    total_kb: 50
    section_caps_kb: {{A: null, B: 1, C: 1, D: 1, E: 1, F: 1, G: 1, H: {h_cap_kb}, I: 3, J: 3}}
    g_fanout: {{}}
gather:
  max_items_per_query: 5000
  max_bytes_per_query: 20000000
  wall_time_budget_seconds: 60
""", encoding="utf-8")
    return str(p)


def _task_spec(view_path: str, budget_profile: str) -> dict:
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-OV", "role": "test", "objective": "x",
        "view": view_path, "required_inputs": [], "seeds": [],
        "queries": [{"id": "OV-Q1", "text": "overflow fixture query text", "routes": ["lexical"]}],
        "mutation_scope": [], "prohibitions": [], "required_checks": [],
        "completion_vocabulary": ["ANSWERED"], "budget_profile": budget_profile,
    }


def test_overflow_produces_a_valid_note_and_a_valid_supplementary_packet(fixture_repo, view_path, registry_path,
                                                                          tmp_path):
    path_rel, commit, lines = _commit_overflow_fixture(fixture_repo)
    routes = RouteSet(lexical=_fake_lexical(path_rel, commit, lines))
    facets_path = _write_facets(tmp_path)
    budgets_path = _write_budgets(tmp_path, h_cap_kb=1)
    task_spec = _task_spec(view_path, "ov-tiny")

    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path, budgets_path=budgets_path,
                                       facets_path=facets_path)
    assert result["status"] in (packetmod.STATUS_OK, packetmod.STATUS_BLOCKED_BUDGET)

    kept_ids = {i.unit_id for i in result["sections"]["H"]}
    assert 0 < len(kept_ids) < N, (
        f"the tiny H cap must keep SOME but not ALL {N} items -- otherwise nothing overflowed to test against "
        f"(kept {len(kept_ids)})"
    )

    # the evidence note: built, and independently re-verified fresh from Git (never trusting its own claims).
    assert "OV-Q1" in result["evidence_notes"], "an overflowing query must get an evidence note"
    note = result["evidence_notes"]["OV-Q1"]
    verdict = notesvalidatemod.validate_note(note, repo=str(fixture_repo.root))
    assert verdict["status"] == "PASS", verdict["problems"]
    assert note["claims"], "at least one overflow item must be groundable into a claim"

    # the supplementary packet: built, and independently re-verified (never authority, never a hand-moved item).
    assert "OV-Q1" in result["supplementary_packets"], "an overflowing query must get a supplementary packet"
    supp = result["supplementary_packets"]["OV-Q1"]
    problems = validatemod.verify_supplementary_packet(supp["manifest"])
    assert problems == [], problems

    # nothing silently discarded: every overflow item is grounded in a note claim, named in the note's own
    # unresolved list, or present in the supplementary packet.
    note_source_ids = {s["item_id"] for c in note["claims"] for s in c["sources"]}
    note_unresolved_ids = {u.get("unit_id") for u in note["unresolved"]}
    supp_ids = {row["unit"]["id"] for row in supp["manifest"]["sections"]["H"]["items"]}
    overflow_ids = {f"OV-{i:04d}" for i in range(N)} - kept_ids
    accounted = note_source_ids | note_unresolved_ids | supp_ids
    assert overflow_ids <= accounted, sorted(overflow_ids - accounted)

    # J discloses the overflow itself, both that it happened and by how much.
    overflow_notices = [n for n in result["manifest"]["notices"]
                         if n["type"] == "EVIDENCE_OVERFLOW" and n["query_id"] == "OV-Q1"]
    assert overflow_notices, result["manifest"]["notices"]
    assert overflow_notices[0]["overflow_item_count"] == len(overflow_ids)
    assert overflow_notices[0]["supplementary_packet_sha256"] == supp["packet_sha256"]


def test_no_overflow_means_no_note_and_no_supplementary_packet(fixture_repo, view_path, registry_path, tmp_path):
    """A generous budget that fits every gathered item produces NEITHER artifact -- overflow shaping never fires
    speculatively."""
    path_rel, commit, lines = _commit_overflow_fixture(fixture_repo)
    small_n = 3
    routes = RouteSet(lexical=_fake_lexical(path_rel, commit, lines[:small_n]))
    facets_path = tmp_path / "ov-facets-small.yaml"
    facets_path.write_text(f"""schema: govbridge-facets/1
default_batch_size: {small_n}
default_target_items: {small_n}
default_max_rounds: 2
default_threads: 1
facets:
  ov:
    routes: [lexical]
    scope_classes: null
    lifecycle_scope: null
    extra_terms: []
    min_share: 0.1
    target_items: {small_n}
class_facets: {{}}
""", encoding="utf-8")
    task_spec = _task_spec(view_path, "bounded-builder")  # the real, generous default profile

    result = packetmod.compile_packet(task_spec, routes=routes, repo=str(fixture_repo.root),
                                       registry_path=registry_path, facets_path=str(facets_path))
    assert result["status"] == packetmod.STATUS_OK
    assert result["evidence_notes"] == {}
    assert result["supplementary_packets"] == {}
    assert not any(n["type"] == "EVIDENCE_OVERFLOW" for n in result["manifest"]["notices"])
