"""W2-197 S1, S2, F1: the memory block gov brief puts into every brief (README, "The memory block").

Each case runs ``gov brief`` in this process on a repository holding this tree's templates and facts, against the
planted store; the block's items are compared with the library's own bundle for the same store, query, ticket and role
(``gov.retrieval.retrieve.retrieve``), never with a ranking computed here.
"""

from __future__ import annotations

import os
import re

import pytest

import w2_197_support as s


def _header(lines: list[str], commit: str) -> str:
    """The section's line naming the store's commit (12 hex), outside the fenced block."""
    hits = [line for line in s.outside_fence(lines) if commit[:12] in line]
    assert hits, f"no line of the memory section names the store's commit {commit[:12]}: {lines}"
    return hits[0]


def _check_block(text: str, bundle: dict, folder, query: str, commit: str) -> None:
    lines = s.section(text)
    header = _header(lines, commit)
    assert any(form in header for form in s.store_forms(folder)), f"the header line names no store folder: {header!r}"
    assert query in header, f"the header line does not name the query {query!r}: {header!r}"
    count = len(bundle["evidence"])
    assert re.search(rf"(?<![\w.]){count}(?![\w.])", header), f"the header line names no item count {count}: {header!r}"
    assert bundle["stopping_reason"] in header, \
        f"the header line names no stop reason {bundle['stopping_reason']}: {header!r}"
    assert "rerank" in header.lower(), f"the header line does not say whether the bundle was reranked: {header!r}"
    rows = s.index_rows(text)
    assert [row[:5] for row in rows] == s.expected_rows(bundle), (
        "the block's index lines are not the library's bundle, item for item and in rank order:\n"
        f"block: {[row[:5] for row in rows]}\nlibrary: {s.expected_rows(bundle)}")
    for row, item in zip(rows, bundle["evidence"]):
        shown, first = row[5].rstrip("…").rstrip(".").strip(), s.first_line(item)
        assert len(row[5]) <= 101 and first.startswith(shown) and (shown or not first), \
            f"item {row[0]}: {row[5]!r} is not the item's first non-empty line cut to 100 characters ({first!r})"
    whole, again = s.commands_of(folder, query)
    joined = "\n".join(lines)
    assert any(command in joined for command in whole), f"the block lacks the whole-bundle command {sorted(whole)[0]}"
    assert any(command in joined for command in again), f"the block lacks the search-again command {sorted(again)[0]}"


# --- S1: every role's brief holds the block --------------------------------------------------------------------------

@pytest.mark.parametrize("role", s.BRIEF_ROLES)
def test_s1_every_role_brief_holds_the_library_bundle_as_its_memory_block(role, store, repo, capsys, monkeypatch):
    run = s.brief(capsys, repo, role, "--store", store.folder)
    text = s.ok_brief(run)
    bundle = s.library_bundle(monkeypatch, store.folder, s.TITLE, role)
    assert bundle["evidence"], "the planted store gave the library no item: the fixture is wrong"
    _check_block(text, bundle, store.folder, s.TITLE, store.commit)


def test_s1_long_first_line_is_cut_to_100_characters(store, repo, capsys):
    text = s.ok_brief(s.brief(capsys, repo, "research", "--store", store.folder))
    rows = [row for row in s.index_rows(text) if row[1] == "notes/widget.md"]
    assert rows, "notes/widget.md (a first line over 100 characters) is not in the block"
    assert len(s.LONG_HEADING.strip()) > 100 and len(rows[0][5].rstrip("…").rstrip(".")) <= 100, \
        f"the first line is not cut to 100 characters: {rows[0][5]!r}"


def test_s1_two_runs_give_the_same_bytes(store, repo, capsys):
    first = s.ok_brief(s.brief(capsys, repo, "engineer", "--store", store.folder))
    second = s.ok_brief(s.brief(capsys, repo, "engineer", "--store", store.folder))
    assert s.SECTION in first, f"the brief has no section {s.SECTION!r}"
    assert first.encode() == second.encode(), "two runs of gov brief on the same store give other bytes"


def test_s1_json_result_memory_matches_the_library_bundle(store, repo, capsys, monkeypatch):
    run = s.brief(capsys, repo, "product-spec", "--store", store.folder, json_out=True)
    assert run.code == 0 and run.envelope().get("ok") is True, run.describe()
    memory = run.result.get("memory")
    assert isinstance(memory, dict), f"result.memory is not an object: {memory!r}; result keys {sorted(run.result)}"
    missing = [key for key in ("store", "commit", "query", "stop_reason", "reranked", "refusal", "items")
               if key not in memory]
    assert not missing, f"result.memory lacks {missing}: {memory}"
    bundle = s.library_bundle(monkeypatch, store.folder, s.TITLE, "product-spec")
    assert memory["store"] in s.store_forms(store.folder), f"result.memory.store is {memory['store']!r}"
    assert s.names_commit(memory["commit"], store.commit), f"result.memory.commit is {memory['commit']!r}"
    assert memory["query"] == s.TITLE, f"result.memory.query is {memory['query']!r}"
    assert memory["stop_reason"] == bundle["stopping_reason"], memory["stop_reason"]
    assert memory["reranked"] is bundle["merge"]["reranked"], memory["reranked"]
    assert memory["refusal"] is None, memory["refusal"]
    items = [(item.get("rank"), item.get("path"), item.get("start_line"), item.get("end_line"), str(item.get("id")))
             for item in memory["items"]]
    assert items == s.expected_rows(bundle), f"result.memory.items are not the library's bundle:\n{items}"
    assert s.SECTION in run.result.get("brief", ""), "result.brief lacks the memory section"


# --- S1: the query and the store chosen ------------------------------------------------------------------------------

@pytest.mark.parametrize("title, body, query", [
    (s.DROP, None, f"{s.TICKET_W2} {s.TITLE}"),
    (s.DROP, "No heading here, only a line.\n", s.TICKET_ID),
], ids=["no-title-first-heading", "no-title-no-heading-the-id"])
def test_s1_query_falls_back_to_the_first_heading_then_the_id(title, body, query, store, repo, capsys):
    repo.ticket(s.ready_front(title=title), body)
    run = s.brief(capsys, repo, "research", "--store", store.folder, json_out=True)
    assert run.code == 0, run.describe()
    memory = run.result.get("memory") or {}
    assert memory.get("query") == query, f"the query is {memory.get('query')!r}, not {query!r}"
    whole, _ = s.commands_of(store.folder, query)
    assert any(command in run.result.get("brief", "") for command in whole), \
        f"the brief lacks the whole-bundle command for {query!r}"


def _chosen(run) -> str:
    assert run.code == 0, run.describe()
    memory = run.result.get("memory")
    assert isinstance(memory, dict), f"result.memory is not an object: {memory!r}"
    return memory.get("store")


def test_s1_store_is_flag_then_gov_store_then_facts_then_root(store, tmp_path, capsys, monkeypatch):
    by_facts, by_env, by_flag = tmp_path / "by-facts", tmp_path / "by-env", tmp_path / "by-flag"
    repo = s.BriefRepo(tmp_path / "chosen", s.real_facts(store_tree=str(by_facts)))
    assert _chosen(s.brief(capsys, repo, "research", json_out=True)) in s.store_forms(by_facts), "facts' store_tree"
    monkeypatch.setenv("GOV_STORE", str(by_env))
    assert _chosen(s.brief(capsys, repo, "research", json_out=True)) in s.store_forms(by_env), "GOV_STORE over facts"
    assert _chosen(s.brief(capsys, repo, "research", "--store", by_flag, json_out=True)) in s.store_forms(by_flag), \
        "--store over GOV_STORE"
    monkeypatch.delenv("GOV_STORE")
    facts = s.real_facts(store_tree=s.DROP)
    facts["commands"]["retrieve"]["run"] = 'gov retrieve "<question>"'  # an adopted repository's form: no store_tree
    bare = s.BriefRepo(tmp_path / "bare", facts)
    assert _chosen(s.brief(capsys, bare, "research", json_out=True)) in s.store_forms(bare.root), \
        "with no flag, no GOV_STORE and no store_tree, the root"


def test_s1_facts_store_tree_is_filled_and_answers(store, tmp_path, capsys, monkeypatch):
    """facts.yaml's store_tree, its placeholders filled, names the planted store: the block holds its items."""
    facts = s.real_facts(store_tree="{MAIN}/" + os.path.basename(store.folder),
                         main=str(store.folder.parent))
    repo = s.BriefRepo(tmp_path / "facts-store", facts)
    text = s.ok_brief(s.brief(capsys, repo, "research"))
    bundle = s.library_bundle(monkeypatch, store.folder, s.TITLE, "research")
    assert [row[:5] for row in s.index_rows(text)] == s.expected_rows(bundle), \
        "the store named by facts.yaml's filled store_tree did not answer the block"


# --- S2: filtered for the brief's role -------------------------------------------------------------------------------

def _paths(text: str) -> set[str]:
    return {row[1] for row in s.index_rows(text)}


def test_s2_engineer_block_omits_its_ticket_acceptance_tests(store, repo, capsys):
    open_paths = _paths(s.ok_brief(s.brief(capsys, repo, "product-spec", "--store", store.folder)))
    assert s.ACCEPTANCE_FILE in open_paths, f"the planted acceptance file is not evidence for the query: {open_paths}"
    engineer = _paths(s.ok_brief(s.brief(capsys, repo, "engineer", "--store", store.folder)))
    assert engineer, "the engineer's block lists no item"
    leaked = sorted(path for path in engineer if path.startswith(f"tests/acceptance/{s.TICKET_W2}/"))
    assert not leaked, f"the engineer's block lists its ticket's acceptance tests: {leaked}"


def test_s2_test_designer_block_omits_the_implementation_paths(store, repo, capsys):
    open_paths = _paths(s.ok_brief(s.brief(capsys, repo, "product-spec", "--store", store.folder)))
    assert s.IMPL_FILE in open_paths, f"the planted implementation file is not evidence for the query: {open_paths}"
    designer = _paths(s.ok_brief(s.brief(capsys, repo, "independent-test-designer", "--store", store.folder)))
    assert designer, "the test designer's block lists no item"
    leaked = sorted(path for path in designer if path.startswith("src/widget/"))
    assert not leaked, f"the test designer's block lists the ticket's implementation paths: {leaked}"
    assert s.ACCEPTANCE_FILE in designer, "the test designer's block lost its own acceptance file"


# --- F1: memory not reached never refuses a brief --------------------------------------------------------------------

def test_f1_missing_store_prints_the_brief_with_the_not_reached_line(tmp_path, repo, capsys):
    missing = tmp_path / "no-store"
    run = s.brief(capsys, repo, "engineer", "--store", missing)
    text = s.ok_brief(run)
    found = s.not_reached(text)
    assert found and found[0][0] == "STORE_MISSING", f"the block does not say 'Memory not reached: STORE_MISSING ...': " \
                                                     f"{s.section(text)}"
    whole, again = s.commands_of(missing, s.TITLE)
    joined = "\n".join(s.section(text))
    assert any(c in joined for c in whole) and any(c in joined for c in again), \
        f"the not-reached block lacks the two commands: {s.section(text)}"
    warned = [line for line in run.err.splitlines() if re.match(r"^gov brief: MEMORY_UNAVAILABLE \S", line)]
    assert warned, f"stderr has no 'gov brief: MEMORY_UNAVAILABLE <detail>' line:\n{run.err}"
    assert "MEMORY_UNAVAILABLE" not in run.out, "the warning went to stdout"


def test_f1_missing_store_under_json_is_ok_with_the_refusal_named(tmp_path, repo, capsys):
    run = s.brief(capsys, repo, "lead", "--store", tmp_path / "no-store", json_out=True)
    assert run.code == 0 and run.envelope().get("ok") is True, run.describe()
    memory = run.result.get("memory") or {}
    assert memory.get("refusal") == "STORE_MISSING", f"result.memory.refusal is {memory.get('refusal')!r}"


def test_f1_unreadable_store_still_prints_the_brief(tmp_path, repo, capsys):
    bad = tmp_path / "bad-store"
    (bad / ".gov-runtime").mkdir(parents=True)
    (bad / ".gov-runtime/store.db").write_bytes(b"not a database " * 64)
    run = s.brief(capsys, repo, "engineer", "--store", bad)
    text = s.ok_brief(run)
    whole, again = s.commands_of(bad, s.TITLE)
    joined = "\n".join(s.section(text))
    assert any(c in joined for c in whole) and any(c in joined for c in again), \
        f"the block for an unreadable store lacks the two commands: {s.section(text)}"


def test_f1_a_ticket_not_ready_is_still_refused(tmp_path, repo, capsys):
    repo.ticket(s.ready_front(allowed_paths=[]))
    run = s.brief(capsys, repo, "engineer", "--store", tmp_path / "no-store", json_out=True)
    assert run.code != 0, f"a ticket that is not READY was briefed:\n{run.describe()}"
    error = run.envelope().get("error") or {}
    assert error.get("code") == "BRIEF_NOT_READY", f"the refusal is not BRIEF_NOT_READY: {error}"
