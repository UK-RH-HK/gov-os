"""Unit tests of the brief's memory block (W2-197 S1, S2, S8, F1, F2; DAEO-3d3o): gov.brief.memory and its use by
gov brief, on a planted brief repository and a planted store (no gitleaks, embedder or reranker: stand-ins)."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from gov.brief import memory
from gov.brief.build import build
from gov.cli.main import main

GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
T0 = """---
name: brief
version: 1.0.0
role: any
---
# Your assignment
Ticket {ID}: {TITLE}.
## What memory holds for this ticket
{MEMORY_BLOCK}
## Commit
{SUBJECT}
"""
ROLE = "---\nname: {stem}\nversion: 1.0.0\nrole: {role}\n---\n# Role\nRun {{CMD:accept}}.\n"
FACTS = """paths:
  tree: '/w/{{W2}}'
  tests_tree: '/w/{{W2}}-tests'
{store_line}commands:
  accept: {{run: 'gov accept {{W2}}', check: 'gov accept --help'}}
budgets: {{brief: 4000}}
ready: {{new_since: "2026-11-10"}}
"""
KEYS = "keys: [ID, W2, TITLE, SUBJECT, MEMORY_BLOCK, TREE, TESTS_TREE, WORKTREES]\n"
FRONT = {"id": "DAEO-mm01", "external-ref": "W2-901", "status": "open", "created": "2026-11-01T10:00:00Z",
         "title": "the juniper lantern", "role": "engineer", "allowed_paths": ["src/x/**"],
         "non_goals": ["nothing else"], "kpis": {"success": [{"line": "S1 works", "verify": "a test"}]}}
STORE_FILES = {
    ".gitignore": ".gov-runtime/\n",
    "governance/project/path-map.yaml": "namespaces: {}\ndecision_register: decisions/REGISTER.md\n",
    "decisions/REGISTER.md": "# Decision register\n\n### DEC-101 — The juniper rule\n- **Status:** ACCEPTED\n",
    "notes/juniper.md": "# The juniper note\n\nThe juniper lantern is kept in the north drawer.\n",
    "notes/lantern.md": "\n\n   The lantern note starts after blank lines: " + "juniper " * 30 + "\n",
}


def git(folder: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(folder), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": str(folder), **GIT_ENV})


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch, tmp_path):
    from gov.retrieval import lexical, semantic
    from gov.retrieval import retrieve as retrieve_module

    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_SESSION", "GOV_STORE"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("GOV_MEMORY_LOG", str(tmp_path / "memory-use.jsonl"))
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)
    monkeypatch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture(scope="module")
def store(tmp_path_factory) -> Path:
    from gov import store as records
    from gov.retrieval import lexical

    root = tmp_path_factory.mktemp("w2-197-brief-store") / "store"
    for rel, text in STORE_FILES.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "c1")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda _root, paths: list(paths))
        lexical.refresh(root)
        records.load(root)
    return root.resolve()


def plant(tmp_path: Path, front: dict | None = None, body: str = "# Heading of the body\n\nSummary.\n",
          store_tree: str | None = None) -> Path:
    root = tmp_path / "repo"
    templates = root / "template/governance/kernel/templates"
    templates.mkdir(parents=True)
    (root / ".tickets").mkdir()
    (root / "governance/project").mkdir(parents=True)
    (templates / "brief.md").write_text(T0, encoding="utf-8")
    (templates / "keys.yaml").write_text(KEYS, encoding="utf-8")
    for stem, role in (("role-engineer", "engineer"), ("role-test-designer", "independent-test-designer")):
        (templates / f"{stem}.md").write_text(ROLE.format(stem=stem, role=role), encoding="utf-8")
    store_line = f"  store_tree: '{store_tree}'\n" if store_tree else ""
    (root / "governance/project/facts.yaml").write_text(FACTS.format(store_line=store_line), encoding="utf-8")
    text = "---\n" + json.dumps(front or FRONT) + "\n---\n" + body
    (root / ".tickets/DAEO-mm01.md").write_text(text, encoding="utf-8")
    return root


# --- the query and the store --------------------------------------------------------------------------------------

def test_query_is_the_title_else_the_first_heading_else_the_id():
    assert memory.query_of({"title": " the title "}, "# A heading\n", "DAEO-x") == "the title"
    assert memory.query_of({}, "text\n## Not this\n# A heading  \n# Second\n", "DAEO-x") == "A heading"
    assert memory.query_of({"title": ""}, "no heading here\n", "DAEO-x") == "DAEO-x"


def test_store_is_the_flag_then_gov_store_then_facts_then_the_root(tmp_path, monkeypatch):
    root = tmp_path / "root"
    assert memory.store_root(root, "/flag", "/facts") == Path("/flag")
    monkeypatch.setenv("GOV_STORE", "/env-store")
    assert memory.store_root(root, None, "/facts") == Path("/env-store")
    monkeypatch.delenv("GOV_STORE")
    assert memory.store_root(root, None, "/facts") == Path("/facts")
    assert memory.store_root(root, None, "{UNFILLED}/x") == root
    assert memory.store_root(root, None, None) == root


# --- the block ----------------------------------------------------------------------------------------------------

def gathered(**over) -> dict:
    base = {"store": "/s", "commit": "a" * 40, "query": "the juniper lantern", "stop_reason": "SATURATED",
            "reranked": True, "refusal": None, "detail": None,
            "items": [{"rank": 1, "path": "notes/a.md", "start_line": 1, "end_line": 3, "id": "c1", "line": "# A"},
                      {"rank": 2, "path": "DEC-1", "start_line": 4, "end_line": 9, "id": "DEC-1", "line": "x" * 100}]}
    return {**base, **over}


def test_block_names_the_store_query_count_stop_reason_and_rerank_then_the_index_and_two_commands():
    text = memory.block(gathered(), "DAEO-mm01")
    lines = text.split("\n")
    assert "aaaaaaaaaaaa" in lines[0] and "/s" in lines[0] and '"the juniper lantern"' in lines[0]
    assert "2 items" in lines[0] and "SATURATED" in lines[0] and "reranked true" in lines[0]
    fence = lines.index("```")
    assert lines[fence + 1:fence + 3] == ["1. notes/a.md:1-3 c1 # A", "2. DEC-1:4-9 DEC-1 " + "x" * 100]
    assert lines[fence + 3] == "```"
    assert 'gov retrieve --root /s --ticket DAEO-mm01 "the juniper lantern"' in text
    assert 'gov retrieve --root /s "<your question>"' in text


def test_block_of_a_refusal_says_memory_not_reached_and_keeps_both_commands():
    text = memory.block(gathered(refusal="STORE_MISSING", detail="no store\nat /s", commit=None, items=[],
                                 stop_reason=None, reranked=False), "DAEO-mm01")
    assert text.startswith("Memory not reached: STORE_MISSING no store at /s.\n") and "```" not in text
    assert "--ticket DAEO-mm01" in text and '"<your question>"' in text


def test_the_commands_quote_a_query_so_the_shell_passes_it_whole():
    text = memory.block(gathered(query='run `gov x` for "$HOME"'), "DAEO-mm01")
    assert r'--ticket DAEO-mm01 "run \`gov x\` for \"\$HOME\""' in text


def test_the_first_line_is_the_first_non_empty_one_cut_to_100_characters(store):
    found = memory.gather(store, "lantern note starts after blank lines", "DAEO-mm01", "engineer")
    line = next(item["line"] for item in found["items"] if item["path"] == "notes/lantern.md")
    assert line.startswith("The lantern note starts") and len(line) == 100


# --- the retrieval ------------------------------------------------------------------------------------------------

def test_gather_is_the_librarys_bundle_for_the_role_and_ticket(store, monkeypatch):
    from gov.retrieval.retrieve import retrieve, store_of

    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    found = memory.gather(store, "the juniper lantern", "DAEO-mm01", "engineer")
    assert os.environ["GOV_ROLE"] == "orchestrator" and "GOV_TICKET" not in os.environ  # restored
    monkeypatch.setenv("GOV_ROLE", "engineer")
    monkeypatch.setenv("GOV_TICKET", "DAEO-mm01")
    bundle = retrieve(store, "the juniper lantern", ticket="DAEO-mm01", role="engineer")
    assert [(i["path"], i["start_line"], i["end_line"], i["id"]) for i in bundle["evidence"]] == \
        [(i["path"], i["start_line"], i["end_line"], i["id"]) for i in found["items"]] != []
    assert [item["rank"] for item in found["items"]] == list(range(1, len(found["items"]) + 1))
    assert found["commit"] == store_of(store, "engineer")["commit"] and len(found["commit"]) == 40
    assert found["refusal"] is None
    assert found["characters"] == sum(len(item["text"]) for item in bundle["evidence"])


def test_gather_of_a_missing_store_is_a_refusal_never_an_error(tmp_path):
    found = memory.gather(tmp_path / "none", "q", "DAEO-mm01", "engineer")
    assert found["refusal"] == "STORE_MISSING" and found["items"] == [] and found["detail"]


# --- gov brief ----------------------------------------------------------------------------------------------------

def test_build_fills_the_block_and_gives_the_same_bytes_twice(tmp_path, store):
    root = plant(tmp_path)
    first = build(root, "engineer", "DAEO-mm01", store=str(store))
    second = build(root, "engineer", "DAEO-mm01", store=str(store))
    assert first["brief"] == second["brief"] and first["findings"] == []
    assert "## What memory holds for this ticket\nStore " in first["brief"]
    assert " notes/juniper.md:1-3 " in first["brief"] and "{MEMORY_BLOCK}" not in first["brief"]
    assert first["memory"]["query"] == "the juniper lantern" and "latency_ms" not in first["memory"]
    spent = {}
    build(root, "engineer", "DAEO-mm01", store=str(store), spent=spent)
    assert isinstance(spent["latency_ms"], int)


def test_build_takes_the_store_from_the_facts_file(tmp_path, store):
    root = plant(tmp_path, store_tree=str(store))
    assert build(root, "engineer", "DAEO-mm01")["memory"]["store"] == str(store)


def test_not_reranked_is_a_warning_never_a_refusal(tmp_path, store):
    out = build(plant(tmp_path), "engineer", "DAEO-mm01", store=str(store))
    assert out["findings"] == [] and "reranked false" in out["brief"]
    assert [w["code"] for w in out["warnings"]] == ["MEMORY_UNAVAILABLE"]


def test_a_ticket_not_ready_is_refused_and_runs_no_retrieval(tmp_path, store):
    out = build(plant(tmp_path, front={**FRONT, "allowed_paths": []}), "engineer", "DAEO-mm01", store=str(store))
    assert ("ALLOWED_PATHS_EMPTY", "DAEO-mm01") in [(f["code"], f["detail"]) for f in out["findings"]]
    assert out["memory"] is None


def run(capsys, *argv) -> tuple[int, str, str]:
    capsys.readouterr()
    code = main([str(arg) for arg in argv])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def test_command_with_a_missing_store_prints_the_brief_warns_and_logs(tmp_path, capsys):
    root = plant(tmp_path)
    code, out, err = run(capsys, "brief", "engineer", "DAEO-mm01", "--root", root, "--store", tmp_path / "none",
                         "--session", "s-9")
    assert code == 0 and "Memory not reached: STORE_MISSING " in out
    assert "gov brief: MEMORY_UNAVAILABLE " in err
    [line] = [json.loads(text) for text in (tmp_path / "memory-use.jsonl").read_text().splitlines()]
    assert (line["command"], line["role"], line["ticket"], line["session"]) == ("brief", "engineer", "DAEO-mm01", "s-9")
    assert line["refusal"] == "STORE_MISSING" and line["search_number"] == 1


def test_command_json_carries_the_memory(tmp_path, store, capsys):
    root = plant(tmp_path)
    code, out, _ = run(capsys, "brief", "independent-test-designer", "DAEO-mm01", "--root", root, "--store", store,
                       "--json")
    found = json.loads(out)["result"]["memory"]
    assert code == 0 and set(found) == {"store", "commit", "query", "stop_reason", "reranked", "refusal", "items"}
    assert set(found["items"][0]) == {"rank", "path", "start_line", "end_line", "id"}


def test_command_output_is_the_same_with_an_unwritable_log(tmp_path, store, capsys, monkeypatch):
    root = plant(tmp_path)
    before = run(capsys, "brief", "engineer", "DAEO-mm01", "--root", root, "--store", store)
    folder = tmp_path / "a-folder"
    folder.mkdir()
    monkeypatch.setenv("GOV_MEMORY_LOG", str(folder))
    assert run(capsys, "brief", "engineer", "DAEO-mm01", "--root", root, "--store", store)[:2] == before[:2]
