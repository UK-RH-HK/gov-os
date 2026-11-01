"""Builder tests for the bounded, reproducible context (W2-04; CAP-15.d, DEC-860, AR-1, AR-9).

Regression evidence only (DEC-136). Each project is a temporary git repository with its store and lexical index
built from its commit; the secret filter is replaced so no test needs gitleaks.
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import gov.context as ctx
from gov import records
from gov.cli.errors import GovError
from gov.retrieval import lexical, supplementary
from gov.store import load

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
REGISTER = ("# Register\n\n"
            "### DEC-101 — The first decision\n- **Status:** ACCEPTED\n\nThe first decision's text.\n\n"
            "### DEC-102 — The second decision\n- **Status:** ACCEPTED\n\nThe second decision's text.\n\n"
            "### DEC-103 — A retired decision\n- **Status:** RETIRED\n\nNo longer stands.\n")
TICKET = ("---\nid: TK-1\ntype: task\nstatus: open\ntitle: zebra ticket\nsources: [DEC-101, CAP-1]\n"
          "kpis:\n  success:\n  - the quokka line holds\n---\n# TK-1\n\nThe ticket's body.\n")
FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": "decision_register: docs/DECISION_REGISTER.md\n",
    "docs/DECISION_REGISTER.md": REGISTER,
    "docs/CAP-1.md": "---\nid: CAP-1\ntype: capability\nstatus: ACCEPTED\n---\n# CAP-1\n\nA capability.\n",
    ".tickets/TK-1.md": TICKET,
    "notes/a-planted.md": "# Planted\n\nthe quokka is found here and nowhere else\n",
    "notes/b-planted.md": "# Planted too\n\nanother quokka of equal weight\n",
}


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for args in (["add", "-A"], ["commit", "-q", "-m", "a change"]):
        subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                       env={**_ENV, "HOME": str(root)})


def _build(root):
    load(root)
    lexical.refresh(root)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    subprocess.run(["git", "-C", str(tmp_path), "init", "-q", "-b", "main"], check=True, capture_output=True, env=_ENV)
    _commit(tmp_path, FILES)
    _build(tmp_path)
    return tmp_path


def _tokens(text):
    return -(-len(text) // 4)


def test_the_ticket_text_is_whole_and_the_tokens_are_counted_within_the_ceiling(project):
    packet = ctx.context(project, "TK-1")
    assert packet["ticket_text"] == TICKET
    assert packet["tokens"] == packet["budget"]["used"] <= packet["budget"]["limit"] == 6000
    assert packet["tokens"] == _tokens(TICKET) + sum(item["tokens"] for item in packet["mandatory"]) \
        + sum(item["tokens"] for item in packet["supplementary"])


def test_a_decision_is_its_own_span_and_hash(project):
    entry = next(record for record in records.records(project) if record["id"] == "DEC-101")
    item = next(item for item in ctx.context(project, "TK-1")["mandatory"] if item["id"] == "DEC-101")
    assert item["sha256"] == item["constraint"] == entry["content_hash"]
    assert item["tokens"] == _tokens(entry["span"])
    _commit(project, {"docs/DECISION_REGISTER.md": REGISTER.replace("second decision's", "changed decision's")})
    _build(project)
    assert next(i for i in ctx.context(project, "TK-1")["mandatory"] if i["id"] == "DEC-101")["sha256"] \
        == entry["content_hash"]
    _commit(project, {"docs/DECISION_REGISTER.md": REGISTER.replace("first decision's", "changed decision's")})
    _build(project)
    assert next(i for i in ctx.context(project, "TK-1")["mandatory"] if i["id"] == "DEC-101")["sha256"] \
        != entry["content_hash"]


def test_over_the_ceiling_the_context_refuses_and_writes_no_brief(project):
    with pytest.raises(GovError) as raised:
        ctx.context(project, "TK-1", budget=50, brief=True)
    assert raised.value.code == "CONTEXT_OVER_CEILING"
    assert raised.value.details["ticket"] == "TK-1" and raised.value.details["limit"] == 50
    assert raised.value.details["mandatory_tokens"] > 50
    assert not (project / ".gov-runtime" / "scratch" / "context").exists()


def test_supplementary_items_never_take_the_packet_over_its_ceiling(project):
    mandatory = ctx.context(project, "TK-1", budget=6000)["tokens"]
    tight = ctx.context(project, "TK-1", budget=mandatory - 5)
    assert tight["tokens"] <= mandatory - 5


def test_a_retired_decision_does_not_satisfy_a_source(project):
    _commit(project, {".tickets/TK-1.md": TICKET.replace("DEC-101", "DEC-103")})
    _build(project)
    with pytest.raises(GovError) as raised:
        ctx.context(project, "TK-1")
    assert raised.value.code == "BLOCKED" and "DEC-103" in raised.value.message and "RETIRED" in raised.value.message


def test_a_register_entry_without_its_span_is_blocked_never_read_as_empty():
    record = {"id": "DEC-1", "type": "decision", "status": "ACCEPTED", "path": "docs/R.md", "in_register": True}
    with pytest.raises(GovError) as raised:
        ctx._read_record("/nonexistent", record, "TK-1")
    assert raised.value.code == "BLOCKED" and raised.value.details["unreadable"] == "DEC-1"
    assert "docs/R.md" in raised.value.message


def test_the_query_is_the_title_and_the_kpis_and_a_kpi_word_reaches_the_block(project):
    packet = ctx.context(project, "TK-1")
    assert packet["supplementary_query"] == "zebra ticket\nthe quokka line holds"
    assert [item["path"] for item in packet["supplementary"]] == ["notes/a-planted.md", "notes/b-planted.md"]
    assert packet["further_batch"] == []


def test_the_packet_is_the_same_whatever_order_the_index_answers_in(project, monkeypatch):
    first = ctx.context(project, "TK-1")
    search = lexical.search

    def reversed_search(root, query, refresh=True):
        answer = search(root, query, refresh=refresh)
        return {**answer, "hits": answer["hits"][::-1]}

    monkeypatch.setattr(lexical, "search", reversed_search)
    assert ctx.context(project, "TK-1")["hash"] == first["hash"]


def test_the_packet_is_the_same_in_another_process(project):
    script = "import sys, gov.context as c; print(c.context(sys.argv[1], 'TK-1')['hash'])"
    hashes = {subprocess.run([sys.executable, "-c", script, str(project)], capture_output=True, text=True,
                             env={"PATH": "/usr/bin:/bin", "PYTHONPATH": ":".join(sys.path),
                                  "PYTHONHASHSEED": seed}).stdout.strip() for seed in ("1", "2")}
    assert hashes == {ctx.context(project, "TK-1")["hash"]}


def test_an_index_that_does_not_answer_is_named_by_its_kind(project):
    _commit(project, {"notes/new.md": "# New\n"})  # the index is now stale against the tree
    packet = ctx.context(project, "TK-1")
    assert packet["supplementary"] == []
    assert packet["dropped"] == [{"id": "supplementary", "reason": "the lexical index is stale"}]


def test_invalid_synthesis_notes_are_never_presented_as_valid(project):
    notes = project / ".gov-runtime" / "synthesis" / "notes.json"
    notes.parent.mkdir(parents=True)
    notes.write_text(json.dumps({"notes": [{"citations": [{"source_id": "X", "path": "gone.md", "start_line": 1,
                                                            "end_line": 1, "source_sha256": "0"}]}]}), encoding="utf-8")
    assert ctx.context(project, "TK-1")["synthesis"] == {"valid": False, "codes": ["FILE_NOT_FOUND"]}
    notes.unlink()
    assert "synthesis" not in ctx.context(project, "TK-1")


def _stacked(monkeypatch, tmp_path, costs, room):
    """The block for ranked chunks of the given token costs, each a file of its own."""
    ranked = []
    for number, cost in enumerate(costs):
        rel = f"f{number}.md"
        (tmp_path / rel).write_text("x" * (cost * 4), encoding="utf-8")
        ranked.append({"id": f"R-{number}", "path": rel, "chunk_id": str(number), "start_line": 1, "end_line": 1})
    monkeypatch.setattr(supplementary, "_ranked", lambda *args: (ranked, None))
    return supplementary.stack(tmp_path, "title", [], room)


def test_the_stack_stops_at_the_first_item_that_does_not_fit(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [3, 10, 1, 1], room=5)
    assert [item["id"] for item in block["supplementary"]] == ["R-0"]
    assert [item["id"] for item in block["further_batch"]] == ["R-1", "R-2", "R-3"]
    assert block["further_batch"][0] == {"id": "R-1", "path": "f1.md"}


def test_the_next_batch_is_taken_while_room_is_left(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 25, room=100)
    assert len(block["supplementary"]) == 25 and block["further_batch"] == [] and block["dropped"] == []


def test_what_is_left_for_a_further_batch_is_at_most_one_batch(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 30, room=3)
    assert [item["id"] for item in block["supplementary"]] == ["R-0", "R-1", "R-2"]
    assert len(block["further_batch"]) == supplementary.BATCH_SIZE
    assert block["further_batch"][0]["id"] == "R-3"
