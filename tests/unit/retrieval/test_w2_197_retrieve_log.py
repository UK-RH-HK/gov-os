"""Unit tests of ``gov retrieve``'s memory-use line (W2-197 S8, F2; DAEO-3d3o), on a planted store."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from gov.cli.main import main

GIT_ENV = {"GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
QUERY = "where is the juniper lantern kept"


def git(folder: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(folder), "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", *args],
                   check=True, capture_output=True, env={"PATH": "/usr/bin:/bin", "HOME": str(folder), **GIT_ENV})


@pytest.fixture(autouse=True)
def stand_ins(monkeypatch):
    """No gitleaks, embedder or reranker: the secret filter, the semantic route and the reranker stand in (W2-138's)."""
    from gov.retrieval import lexical, semantic
    from gov.retrieval import retrieve as retrieve_module

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda _root: False)
    monkeypatch.setattr(retrieve_module, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve_module, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture(scope="module")
def store(tmp_path_factory) -> Path:
    from gov import store as records
    from gov.retrieval import lexical

    root = tmp_path_factory.mktemp("w2-197-store") / "store"
    files = {".gitignore": ".gov-runtime/\n",
             "governance/project/path-map.yaml": "namespaces: {}\ndecision_register: decisions/REGISTER.md\n",
             "decisions/REGISTER.md": "# Decision register\n\n### DEC-101 — The juniper rule\n- **Status:** ACCEPTED\n",
             "notes/juniper.md": "# The juniper note\n\nThe juniper lantern is kept in the north drawer.\n",
             "notes/fennel.md": "# The fennel note\n\nThe fennel lantern hangs by the door.\n"}
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    git(root, "init", "-q", "-b", "main")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "c1")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(lexical, "indexable", lambda _root, paths: list(paths))
        lexical.refresh(root)
        records.load(root)
    return root


@pytest.fixture
def log(tmp_path, monkeypatch) -> Path:
    for name in ("GOV_ROLE", "GOV_TICKET", "GOV_SESSION", "GOV_STORE"):
        monkeypatch.delenv(name, raising=False)
    path = tmp_path / "memory-use.jsonl"
    monkeypatch.setenv("GOV_MEMORY_LOG", str(path))
    return path


def lines(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.exists() else []


def run(capsys, *argv) -> tuple[int, str]:
    capsys.readouterr()
    code = main([str(arg) for arg in argv])
    return code, capsys.readouterr().out


def test_a_search_appends_one_line_with_every_field(store, log, capsys):
    code, out = run(capsys, "retrieve", "--root", store, "--json", "--role", "research", "--ticket", "DEC-101",
                    "--session", "s-1", QUERY)
    assert code == 0
    result = json.loads(out)["result"]
    [line] = lines(log)
    assert line["command"] == "retrieve" and line["role"] == "research" and line["ticket"] == "DEC-101"
    assert line["session"] == "s-1" and line["search_number"] == 1
    assert line["query_sha256"] == hashlib.sha256(QUERY.encode()).hexdigest()[:16] and QUERY not in json.dumps(line)
    assert line["stop_reason"] == result["stopping_reason"] and line["items"] == len(result["evidence"]) > 0
    assert line["characters"] == sum(len(item["text"]) for item in result["evidence"])
    assert isinstance(line["latency_ms"], int) and line["latency_ms"] >= 0
    assert line["refusal"] is None and line["store_commit"] == result["store"]["commit"]
    assert line["reranked"] is result["merge"]["reranked"]


def test_role_ticket_and_session_come_from_the_environment(store, log, capsys, monkeypatch):
    monkeypatch.setenv("GOV_ROLE", "product-spec")
    monkeypatch.setenv("GOV_TICKET", "DAEO-zz02")
    monkeypatch.setenv("GOV_SESSION", "s-env")
    run(capsys, "retrieve", "--root", store, QUERY)
    run(capsys, "retrieve", "--root", store, QUERY + " again")
    first, second = lines(log)
    assert (first["role"], first["ticket"], first["session"]) == ("product-spec", "DAEO-zz02", "s-env")
    assert (first["search_number"], second["search_number"]) == (1, 2)


def test_a_refused_search_is_logged_with_its_code_and_exits_as_before(tmp_path, log, capsys):
    code, out = run(capsys, "retrieve", "--root", tmp_path / "no-store", "--json", QUERY)
    assert code == 1 and json.loads(out)["error"]["code"] == "STORE_MISSING"
    [line] = lines(log)
    assert line["refusal"] == "STORE_MISSING" and line["items"] == 0 and line["stop_reason"] is None
    assert line["session"] is None and line["search_number"] is None


def test_a_stated_gap_is_logged_as_unresolved_ids(store, log, capsys):
    code, out = run(capsys, "retrieve", "--root", store, "--json", "what does DEC-999999 say")
    assert code == 0 and json.loads(out)["result"]["stopping_reason"] == "UNRESOLVED_IDS"
    assert lines(log)[0]["refusal"] == "UNRESOLVED_IDS"


def test_an_unwritable_log_changes_neither_output_nor_exit(store, tmp_path, log, capsys, monkeypatch):
    ok = run(capsys, "retrieve", "--root", store, QUERY)
    refused = run(capsys, "retrieve", "--root", tmp_path / "no-store", QUERY)
    folder = tmp_path / "a-folder"
    folder.mkdir()
    monkeypatch.setenv("GOV_MEMORY_LOG", str(folder))
    assert run(capsys, "retrieve", "--root", store, QUERY) == ok
    assert run(capsys, "retrieve", "--root", tmp_path / "no-store", QUERY) == refused
