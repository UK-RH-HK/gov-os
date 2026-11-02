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
    block = _stacked(monkeypatch, tmp_path, [1, 1, 30] + [1] * 27, room=12)
    assert [item["id"] for item in block["supplementary"]] == ["R-0", "R-1"]
    assert [item["id"] for item in block["further_batch"]] == [f"R-{n}" for n in range(2, 10)]  # its batch's rest
    assert len(block["further_batch"]) <= max(batch["limit"] for batch in block["supplementary_batches"])


def test_what_is_left_names_only_items_a_batch_read(monkeypatch, tmp_path):
    # the second batch is smaller than the first (two tokens of room left): what is left ends where it ends
    block = _stacked(monkeypatch, tmp_path, [1] * 9 + [2, 5] + [1] * 19, room=13)
    assert [(len(batch["items"]), batch["limit"]) for batch in block["supplementary_batches"]] == [(10, 10), (2, 2)]
    assert len(block["supplementary"]) == 10
    assert [item["id"] for item in block["further_batch"]] == ["R-10", "R-11"]
    sequence = _sequence(block)
    assert block["further_batch"] == sequence[sequence.index(block["further_batch"][0]):]


def _left(block):
    return [item["id"] for item in block["further_batch"]]


def test_room_that_ends_on_a_batch_s_last_item_names_the_next_items_one_batch_long(monkeypatch, tmp_path):
    # DEC-1025 item 2: the room ends exactly on a stacked item and ranked items remain
    block = _stacked(monkeypatch, tmp_path, [1] * 30, room=3)
    assert [item["id"] for item in block["supplementary"]] == ["R-0", "R-1", "R-2"]
    assert block["supplementary_batches"] == [{"items": [{"id": f"R-{n}", "path": f"f{n}.md"} for n in range(3)],
                                               "limit": 3}]  # no further batch is taken for them
    assert block["further_batch"] == [{"id": f"R-{n}", "path": f"f{n}.md"} for n in range(3, 6)]
    assert block["dropped"] == [{"id": f"R-{n}", "reason": "budget exceeded"} for n in range(3, 6)]


def test_room_that_ends_on_a_later_batch_names_at_most_the_largest_limit(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 40, room=12)  # a batch of 10, then one of 2: the room is 0
    assert [(len(batch["items"]), batch["limit"]) for batch in block["supplementary_batches"]] == [(10, 10), (2, 2)]
    assert len(block["supplementary"]) == 12
    assert _left(block) == [f"R-{n}" for n in range(12, 22)]
    assert [entry["id"] for entry in block["dropped"]] == _left(block)


def test_room_that_ends_inside_a_batch_names_the_rest_of_it(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [2, 3, 1, 1, 1], room=5)
    assert [item["id"] for item in block["supplementary"]] == ["R-0", "R-1"]
    assert _left(block) == ["R-2", "R-3", "R-4"] and [entry["id"] for entry in block["dropped"]] == _left(block)


def test_room_that_ends_with_the_evidence_names_nothing(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 3, room=3)
    assert len(block["supplementary"]) == 3 and block["further_batch"] == [] and block["dropped"] == []


def test_no_room_takes_no_batch_and_names_the_first_batch_size_of_items(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 15, room=0)
    assert block["supplementary_batches"] == [] and block["supplementary"] == []
    assert _left(block) == [f"R-{n}" for n in range(supplementary.BATCH_SIZE)]
    assert block["dropped"] == [{"id": f"R-{n}", "reason": "budget exceeded"} for n in range(supplementary.BATCH_SIZE)]


def test_no_room_and_fewer_items_than_a_batch_names_them_all(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 4, room=0)
    assert block["supplementary_batches"] == [] and _left(block) == ["R-0", "R-1", "R-2", "R-3"]


def test_no_room_and_no_evidence_names_nothing(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [], room=0)
    assert block["supplementary_batches"] == [] and block["further_batch"] == [] and block["dropped"] == []


def test_a_packet_whose_mandatory_part_fills_the_ceiling_names_what_it_left(project):
    full = ctx.context(project, "TK-1")
    mandatory = full["tokens"] - sum(item["tokens"] for item in full["supplementary"])
    packet = ctx.context(project, "TK-1", budget=mandatory)
    assert packet["tokens"] == mandatory and packet["supplementary"] == []
    assert packet["supplementary_batches"] == []
    assert packet["further_batch"] == [{"id": item["id"], "path": item["path"]} for item in full["supplementary"]]
    assert packet["dropped"] == sorted(({"id": item["id"], "reason": "budget exceeded"} for item in full["supplementary"]),
                                       key=lambda entry: (entry["id"], entry["reason"]))


def _sequence(block):
    return [item for batch in block["supplementary_batches"] for item in batch["items"]]


def test_each_batch_is_named_with_the_items_it_read_and_its_limit(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 25, room=100)
    assert [(len(batch["items"]), batch["limit"]) for batch in block["supplementary_batches"]] \
        == [(10, 10), (10, 10), (5, 10)]
    assert _sequence(block) == [{"id": item["id"], "path": item["path"]} for item in block["supplementary"]]


def test_evidence_that_ends_on_a_full_batch_shows_a_last_batch_with_fewer_items(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [1] * 10, room=100)
    assert [(len(batch["items"]), batch["limit"]) for batch in block["supplementary_batches"]] == [(10, 10), (0, 10)]
    assert block["further_batch"] == []


def test_the_batches_hold_the_rank_order_through_the_item_left_out(monkeypatch, tmp_path):
    block = _stacked(monkeypatch, tmp_path, [3, 10, 1, 1], room=5)
    sequence = _sequence(block)
    assert sequence[:len(block["supplementary"])] == [{"id": "R-0", "path": "f0.md"}]
    assert sequence[len(block["supplementary"])] == block["further_batch"][0]
    assert all(len(batch["items"]) <= batch["limit"] <= 5 for batch in block["supplementary_batches"])


def test_the_batches_are_in_the_packet_and_its_hash(project):
    packet = ctx.context(project, "TK-1")
    assert [item["path"] for item in _sequence(packet)] == ["notes/a-planted.md", "notes/b-planted.md"]
    assert packet["supplementary_batches"][0]["limit"] == supplementary.BATCH_SIZE
    assert ctx.context(project, "TK-1")["supplementary_batches"] == packet["supplementary_batches"]


def test_a_failed_lookup_has_no_batch_and_is_named(project):
    _commit(project, {"notes/new.md": "# New\n"})
    packet = ctx.context(project, "TK-1")
    assert packet["supplementary_batches"] == [] and packet["dropped"][0]["reason"] == "the lexical index is stale"


DEPENDENCY = ("---\nid: TK-0\ntype: task\nstatus: closed\ntitle: the dependency\nkpis:\n  success:\n"
              "  - its one line\n---\n# TK-0\n\n")


def _with_dependency(project, body):
    _commit(project, {".tickets/TK-0.md": DEPENDENCY + body,
                      ".tickets/TK-1.md": TICKET.replace("sources: [DEC-101, CAP-1]",
                                                         "sources: [DEC-101, CAP-1]\ndeps: [TK-0]")})
    _build(project)
    return ctx.context(project, "TK-1")


def test_a_dependency_counts_by_its_front_matter_and_keeps_its_file_hash(project):
    import hashlib
    packet = _with_dependency(project, "A short body.\n")
    item = next(item for item in packet["mandatory"] if item["id"] == "TK-0")
    text = (project / ".tickets/TK-0.md").read_bytes()
    assert item["sha256"] == hashlib.sha256(text).hexdigest()
    assert item["tokens"] == _tokens("id: TK-0\nstatus: closed\ntitle: the dependency\n- its one line\n")
    assert packet["ticket_text"] == (project / ".tickets/TK-1.md").read_text(encoding="utf-8")


def test_a_dependency_body_never_moves_the_tokens_nor_passes_the_ceiling(project):
    short = _with_dependency(project, "A short body.\n")
    large = _with_dependency(project, "word " * 40000)  # 50,000 tokens of body
    assert large["tokens"] == short["tokens"] <= large["budget"]["limit"]
    dep = [next(item for item in packet["mandatory"] if item["id"] == "TK-0") for packet in (short, large)]
    assert dep[0]["tokens"] == dep[1]["tokens"] and dep[0]["sha256"] != dep[1]["sha256"]


# S5, an emptied mandatory file (DEC-1025 item 1): the store is built from HEAD, the working tree's file is emptied after


def _blocked(project, rel, **kwargs):
    with pytest.raises(GovError) as raised:
        ctx.context(project, "TK-1", **kwargs)
    error = raised.value
    assert error.code == "BLOCKED", error.code
    assert error.details["unreadable"] == rel[1] and error.details["file"] == rel[0]
    assert rel[1] in error.message and rel[0] in error.message and "empty" in error.message
    return error


@pytest.mark.parametrize("content", ["", " ", "\n", " \t\n\n\t  \n"])
def test_an_emptied_capability_file_blocks_and_is_never_read(project, content):
    (project / "docs/CAP-1.md").write_text(content, encoding="utf-8")
    _blocked(project, ("docs/CAP-1.md", "CAP-1"))


@pytest.mark.parametrize("kwargs", [{"brief": True}, {"brief": True, "dry_run": True}, {"dry_run": True}])
def test_an_emptied_file_blocks_the_brief_and_the_dry_run_and_writes_no_brief(project, kwargs):
    (project / "docs/CAP-1.md").write_text("  \n", encoding="utf-8")
    _blocked(project, ("docs/CAP-1.md", "CAP-1"), **kwargs)
    assert not (project / ".gov-runtime" / "scratch" / "context").exists()


@pytest.mark.parametrize("content", ["", "\n\t \n"])
def test_an_emptied_dependency_ticket_blocks_and_is_never_read(project, content):
    _with_dependency(project, "A short body.\n")
    (project / ".tickets/TK-0.md").write_text(content, encoding="utf-8")
    _blocked(project, (".tickets/TK-0.md", "TK-0"))


def test_an_emptied_file_exits_non_zero_from_the_command(project, capsys, monkeypatch):
    from gov.cli.main import main
    from gov.config import loader
    monkeypatch.setattr(loader, "load_config", lambda root: {})  # the fixture's path map is a store's, not a project's
    (project / "docs/CAP-1.md").write_text("", encoding="utf-8")
    for extra in ([], ["--brief"], ["--brief", "--dry-run"]):
        assert main(["context", "TK-1", *extra, "--json", "--root", str(project)]) != 0
        envelope = json.loads(capsys.readouterr().out)
        assert envelope["ok"] is False and envelope["error"]["code"] == "BLOCKED", envelope["error"]
        assert envelope["error"]["details"]["unreadable"] == "CAP-1"


def test_a_file_with_text_after_whitespace_is_still_read(project):
    (project / "docs/CAP-1.md").write_text("\n\n  A capability, its front matter gone.\n", encoding="utf-8")
    item = next(item for item in ctx.context(project, "TK-1")["mandatory"] if item["id"] == "CAP-1")
    assert item["tokens"] == _tokens("\n\n  A capability, its front matter gone.\n")
