"""Unit tests for the context packet's dropped list: one order whatever order the retrieval returns (W2-54, DEC-768).

W2-04 (DEC-860): the stack stops at the first ranked item that does not fit, so what is kept is a prefix of the rank,
and the items that were not stacked are named in rank order under ``further_batch``.
"""

from __future__ import annotations

import gov.context as ctx
from gov.retrieval import supplementary

DECISION = {"id": "DEC-1", "type": "decision", "status": "ACTIVE", "path": "docs/decisions/DEC-1.md"}
TICKET = "---\nid: TK-1\ntitle: a ticket\nsources: [DEC-1]\n---\n# TK-1\n"
EVIDENCE = [
    {"id": "DEC-9", "text": "n" * 40, "path": "docs/decisions/DEC-9.md"},
    {"id": "ADR-2", "text": "a" * 40, "path": "docs/adr/ADR-2.md"},
    {"id": "ADR-2", "text": "b" * 40, "path": "docs/adr/ADR-2b.md"},
    {"id": "DEC-3", "text": "c" * 8, "path": "docs/decisions/DEC-3.md"},
    {"id": "c0ffee", "text": "d" * 40, "path": "README.md"},
]


def _packet(monkeypatch, tmp_path, evidence, room):
    """The packet whose supplementary block is stacked from ``evidence`` in the order given, with ``room`` tokens."""
    (tmp_path / ".tickets").mkdir(exist_ok=True)
    (tmp_path / ".tickets" / "TK-1.md").write_text(TICKET, encoding="utf-8")
    ranked = []
    for number, item in enumerate(evidence):
        (tmp_path / item["path"]).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / item["path"]).write_text(item["text"], encoding="utf-8")
        ranked.append({"id": item["id"], "path": item["path"], "chunk_id": str(number), "start_line": 1,
                       "end_line": 1})
    monkeypatch.setattr(ctx, "_record_map", lambda root: {"DEC-1": DECISION})
    monkeypatch.setattr(ctx, "_supersedes_edges", lambda root: set())
    monkeypatch.setattr(ctx, "external_references", lambda root: {})
    monkeypatch.setattr(ctx, "_read_record", lambda root, record, ticket: ("0" * 64, "x" * 40))
    monkeypatch.setattr(supplementary, "_ranked", lambda *args: (list(ranked), None))
    return ctx.context(tmp_path, "TK-1", budget=ctx._tokens(TICKET) + 10 + room)


def test_every_item_dropped_gives_one_dropped_list_under_any_order(monkeypatch, tmp_path):
    first = _packet(monkeypatch, tmp_path, EVIDENCE, room=5)
    second = _packet(monkeypatch, tmp_path, EVIDENCE[::-1], room=5)
    third = _packet(monkeypatch, tmp_path, EVIDENCE[2:] + EVIDENCE[:2], room=5)
    assert first["supplementary"] == []
    assert len(first["dropped"]) == len(EVIDENCE)
    assert first["dropped"] == second["dropped"] == third["dropped"]


def test_the_dropped_list_is_sorted_by_id_then_reason(monkeypatch, tmp_path):
    packet = _packet(monkeypatch, tmp_path, EVIDENCE, room=5)
    ids = [entry["id"] for entry in packet["dropped"]]
    assert ids == sorted(ids) == ["ADR-2", "ADR-2", "DEC-3", "DEC-9", "c0ffee"]


def test_what_is_kept_is_the_rank_up_to_the_first_item_that_does_not_fit(monkeypatch, tmp_path):
    # room for the first 10-token item; the next does not fit, so the 2-token one after it is not stacked either
    packet = _packet(monkeypatch, tmp_path, EVIDENCE, room=12)
    assert [item["id"] for item in packet["supplementary"]] == ["DEC-9"]
    assert [entry["id"] for entry in packet["dropped"]] == ["ADR-2", "ADR-2", "DEC-3", "c0ffee"]
    assert [item["path"] for item in packet["further_batch"]] == [item["path"] for item in EVIDENCE[1:]]


def test_a_real_difference_still_changes_the_hash(monkeypatch, tmp_path):
    first = _packet(monkeypatch, tmp_path, EVIDENCE, room=5)
    fewer = _packet(monkeypatch, tmp_path, EVIDENCE[1:], room=5)
    assert first["hash"] != fewer["hash"]


def test_a_failed_lookup_is_kept_as_one_entry(monkeypatch, tmp_path):
    def broken(*args):
        raise RuntimeError("no index")
    packet = _packet(monkeypatch, tmp_path, EVIDENCE, room=5)
    monkeypatch.setattr(supplementary, "_ranked", broken)
    failed = ctx.context(tmp_path, "TK-1", budget=ctx._tokens(TICKET) + 15)
    assert failed["dropped"] == [{"id": "supplementary", "reason": "the lookup failed: no index"}]
    assert failed["further_batch"] == [] and failed["hash"] != packet["hash"]
