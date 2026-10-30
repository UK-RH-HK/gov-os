"""Unit tests for the context packet's dropped list: one order whatever order the retrieval returns (W2-54, DEC-768)."""

from __future__ import annotations

import gov.context as ctx
import gov.retrieval.retrieve as retrieve_module

DECISION = {"id": "DEC-1", "type": "decision", "status": "ACTIVE", "path": "docs/decisions/DEC-1.md"}
EVIDENCE = [
    {"id": "DEC-9", "text": "n" * 40, "path": "docs/decisions/DEC-9.md"},
    {"id": "ADR-2", "text": "a" * 40, "path": "docs/adr/ADR-2.md"},
    {"id": "ADR-2", "text": "b" * 40, "path": "docs/adr/ADR-2.md"},
    {"id": "DEC-3", "text": "c" * 8, "path": "docs/decisions/DEC-3.md"},
    {"id": "c0ffee", "text": "d" * 40, "path": "README.md"},
]


def _packet(monkeypatch, evidence, budget):
    monkeypatch.setattr(ctx, "_ticket_mandatory_ids", lambda root, ticket: ["DEC-1"])
    monkeypatch.setattr(ctx, "_ticket_source_ids", lambda root, ticket: ["DEC-1"])
    monkeypatch.setattr(ctx, "_record_map", lambda root: {"DEC-1": DECISION})
    monkeypatch.setattr(ctx, "_supersedes_edges", lambda root: set())
    monkeypatch.setattr(ctx, "external_references", lambda root: {})
    monkeypatch.setattr(ctx, "_read_record", lambda root, record, ticket: ("0" * 64, "x" * 40))
    monkeypatch.setattr(ctx, "_supplementary_query", lambda root, ticket: "query")
    monkeypatch.setattr(retrieve_module, "retrieve", lambda root, query, ticket=None: {"evidence": list(evidence)})
    return ctx.context("/nonexistent", "TK-1", budget=budget)


def test_every_item_dropped_gives_one_packet_under_any_order(monkeypatch):
    first = _packet(monkeypatch, EVIDENCE, budget=5)
    second = _packet(monkeypatch, EVIDENCE[::-1], budget=5)
    third = _packet(monkeypatch, EVIDENCE[2:] + EVIDENCE[:2], budget=5)
    assert first["supplementary"] == []
    assert len(first["dropped"]) == len(EVIDENCE)
    assert first["dropped"] == second["dropped"] == third["dropped"]
    assert first["hash"] == second["hash"] == third["hash"]


def test_the_dropped_list_is_sorted_by_id_then_reason(monkeypatch):
    packet = _packet(monkeypatch, EVIDENCE, budget=5)
    ids = [entry["id"] for entry in packet["dropped"]]
    assert ids == sorted(ids) == ["ADR-2", "ADR-2", "DEC-3", "DEC-9", "c0ffee"]


def test_what_is_kept_still_follows_the_retrieval_s_rank(monkeypatch):
    # 10 mandatory tokens of a budget of 22: room for one 10-token item, then the 2-token one
    packet = _packet(monkeypatch, EVIDENCE, budget=22)
    assert [item["id"] for item in packet["supplementary"]] == ["DEC-9", "DEC-3"]
    assert [entry["id"] for entry in packet["dropped"]] == ["ADR-2", "ADR-2", "c0ffee"]


def test_a_real_difference_still_changes_the_hash(monkeypatch):
    first = _packet(monkeypatch, EVIDENCE, budget=5)
    fewer = _packet(monkeypatch, EVIDENCE[1:], budget=5)
    assert first["hash"] != fewer["hash"]


def test_a_failed_lookup_is_kept_as_one_entry(monkeypatch):
    def broken(root, query, ticket=None):
        raise RuntimeError("no index")
    packet = _packet(monkeypatch, EVIDENCE, budget=5)
    monkeypatch.setattr(retrieve_module, "retrieve", broken)
    failed = ctx.context("/nonexistent", "TK-1", budget=5)
    assert failed["dropped"] == [{"id": "supplementary", "reason": "the lookup failed: no index"}]
    assert failed["hash"] != packet["hash"]
