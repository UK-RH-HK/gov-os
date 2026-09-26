"""REPAIR_DAG.yaml node R1-RS: OBS-BR-07 (RC-9) -- "section I carries the task's instantiated query set and the
answers and receipt schemas, verbatim and by hash"; and "the bootstrap references the packet by id and hash and
does not inline it" (RC-9: run-1's bootstrap was 282,782 bytes and contained the whole packet).
"""
from __future__ import annotations

import json

import yaml

from govbridge.compile import bootstrap as bootstrapmod
from govbridge.compile import packet as packetmod
from govbridge.compile import section_i as section_i_mod
from govbridge.compile import validate as validatemod
from govbridge.core.yamlutil import sha256_text
from govbridge.route.router import RouteSet


# ---------------------------------------------------------------------------------------------------------------
# section_i.py directly
# ---------------------------------------------------------------------------------------------------------------

def test_instantiated_query_set_expands_class_subject_entries(tmp_path):
    # `queries` (schemas/task-spec.yaml: "path | list") is a PATH here -- the shape a real task spec uses to
    # carry a query_classes/subjects table (govbridge.gather.instantiate.load_query_set only expands a dict-shaped
    # document when it is loaded FROM such a path; a literal inline dict is not one of its three accepted forms).
    qs_path = tmp_path / "queries.yaml"
    qs_path.write_text(yaml.safe_dump({
        "query_classes": {"why": "why does {subject} matter"},
        "subjects": {"s1": "CX-0001"},
        "queries": [{"id": "Q1", "class": "why", "subject": "s1"}, {"id": "Q2", "text": "literal text"}],
    }, sort_keys=False), encoding="utf-8")
    task_spec = {"queries": str(qs_path)}
    queries = section_i_mod.instantiated_query_set(task_spec)
    assert queries == [
        {"id": "Q1", "text": "why does CX-0001 matter", "routes": None, "target_section": None, "kind": None,
         "class": "why", "subject": "s1", "facets": None},
        {"id": "Q2", "text": "literal text", "routes": None, "target_section": None, "kind": None, "class": None,
         "subject": None, "facets": None},
    ]


def test_instantiated_query_set_empty_for_no_queries():
    assert section_i_mod.instantiated_query_set({}) == []


def test_build_task_inputs_item_carries_schemas_verbatim_and_by_hash():
    task_spec = {"queries": [{"id": "Q1", "text": "literal"}]}
    item = section_i_mod.build_task_inputs_item(task_spec)
    assert item.section == "I"
    assert item.delivery == "PINNED"
    body = json.loads(item.text)

    answers_path = section_i_mod._domain_path(section_i_mod.SCHEMA_RELPATHS["answers"])
    with open(answers_path, encoding="utf-8") as fh:
        answers_text = fh.read()
    assert body["answers_schema"]["text"] == answers_text
    assert body["answers_schema"]["sha256"] == sha256_text(answers_text)

    receipt_path = section_i_mod._domain_path(section_i_mod.SCHEMA_RELPATHS["receipt"])
    with open(receipt_path, encoding="utf-8") as fh:
        receipt_text = fh.read()
    assert body["receipt_schema"]["text"] == receipt_text
    assert body["receipt_schema"]["sha256"] == sha256_text(receipt_text)

    assert body["instantiated_queries"]["queries"] == [
        {"id": "Q1", "text": "literal", "routes": None, "target_section": None, "kind": None, "class": None,
         "subject": None, "facets": None},
    ]
    assert body["instantiated_queries"]["count"] == 1
    assert item.content_sha256 == sha256_text(item.text)


def test_with_task_inputs_in_section_i_adds_one_item_and_stays_verifiable(fixture_repo, view_path, registry_path,
                                                                            task_spec_factory):
    task_spec = task_spec_factory(view_path, queries=[{"id": "Q1", "text": "why does CX-0001 matter"}])
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK
    before_i_count = len(result["manifest"]["sections"]["I"]["items"])
    before_a = result["manifest"]["sections"]["A"]["items"]

    enriched = section_i_mod.with_task_inputs_in_section_i(result, task_spec, repo=str(fixture_repo.root))
    after_i = enriched["manifest"]["sections"]["I"]["items"]
    assert len(after_i) == before_i_count + 1
    assert any(row["unit"]["id"] == "I.task_inputs" for row in after_i)
    # section A (authority) is untouched by this enrichment.
    assert enriched["manifest"]["sections"]["A"]["items"] == before_a
    # the packet is re-finalised (new hashes), and still passes every check, including R1-10's rendered-body one.
    assert enriched["manifest"]["manifest_sha256"] != result["manifest"]["manifest_sha256"]
    problems = validatemod.verify_packet(enriched["manifest"], task_spec, repo=str(fixture_repo.root),
                                          registry_path=registry_path, rendered=enriched["rendered"])
    assert problems == []
    assert "why does CX-0001 matter" in enriched["rendered"]


# ---------------------------------------------------------------------------------------------------------------
# bootstrap.py: reference, never inline.
# ---------------------------------------------------------------------------------------------------------------

def test_bootstrap_references_packet_instead_of_inlining_it(fixture_repo, view_path, registry_path,
                                                               task_spec_factory):
    task_spec = task_spec_factory(view_path, seeds=["CX-0001"],
                                   queries=[{"id": "Q1", "text": "why does CX-0001 matter"}])
    brief, result = bootstrapmod.compile_brief(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                                registry_path=registry_path)
    assert result["status"] == packetmod.STATUS_OK

    # the packet's own identity is named...
    assert result["packet_sha256"] in brief
    assert result.get("packet_id") in brief
    # ...but the packet's OWN section bodies are never embedded (RC-9: run-1's bootstrap inlined the whole thing).
    assert "## A. MANDATORY AUTHORITATIVE INPUTS" not in brief
    assert "## J. COMPLETION / EVIDENCE OBLIGATIONS" not in brief
    assert len(brief.encode("utf-8")) < len(result["rendered"].encode("utf-8"))

    # every other prelude section is unchanged.
    assert "## Where you are" in brief
    assert "## Context and checkpoint protocol" in brief
    assert "## Your receipt" in brief

    # OBS-BR-07: the task inputs (query set + schemas) are still reachable -- inside the packet's own section I,
    # not lost by no longer inlining the packet.
    i_rows = result["manifest"]["sections"]["I"]["items"]
    assert any(row["unit"]["id"] == "I.task_inputs" for row in i_rows)


def test_bootstrap_with_packet_out_names_the_directory(fixture_repo, view_path, registry_path, task_spec_factory):
    task_spec = task_spec_factory(view_path)
    brief, result = bootstrapmod.compile_brief(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                                registry_path=registry_path, packet_out="/tmp/some-packet-dir")
    assert "/tmp/some-packet-dir" in brief
    assert "## A. MANDATORY AUTHORITATIVE INPUTS" not in brief


def test_bootstrap_cli_out_writes_the_same_packet_it_references(fixture_repo, view_path, registry_path,
                                                                   task_spec_factory, tmp_path, monkeypatch):
    from govbridge.compile import bootstrap as bootstrapcli

    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
    task_spec_path = tmp_path / "task-spec.yaml"
    import yaml
    task_spec = task_spec_factory(view_path)
    task_spec_path.write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")

    out_dir = tmp_path / "boot-pkt"
    rc = bootstrapcli.main([str(task_spec_path), "--fake-routes", "--registry", registry_path, "--repo",
                             str(fixture_repo.root), "--out", str(out_dir)])
    assert rc == 0
    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["packet_kind"] == "main"

    from govbridge import cli
    rc_verify = cli.main(["packet", "verify", str(out_dir), "--repo", str(fixture_repo.root)])
    assert rc_verify == 0


def test_cli_bootstrap_output_is_well_under_the_packet_size(fixture_repo, view_path, registry_path,
                                                               task_spec_factory, tmp_path, monkeypatch):
    """Mirrors the DAG's own acceptance check: ``govbridge bootstrap <spec> | wc -c`` is "well under the packet
    size, because the packet is referenced, not inlined"."""
    from govbridge import cli
    import yaml

    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
    task_spec = task_spec_factory(view_path, seeds=["CX-0001"])
    task_spec_path = tmp_path / "task-spec.yaml"
    task_spec_path.write_text(yaml.safe_dump(task_spec, sort_keys=False), encoding="utf-8")

    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = cli.main(["bootstrap", str(task_spec_path), "--fake-routes", "--registry", registry_path, "--repo",
                       str(fixture_repo.root)])
    assert rc == 0
    brief_bytes = len(buf.getvalue().encode("utf-8"))

    # the equivalent compiled packet, for comparison.
    from govbridge.compile import packet as packetmod
    result = packetmod.compile_packet(task_spec, routes=RouteSet(), repo=str(fixture_repo.root),
                                       registry_path=registry_path)
    packet_bytes = len(result["rendered"].encode("utf-8"))
    assert brief_bytes < packet_bytes
