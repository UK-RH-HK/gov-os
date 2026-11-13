"""Every search result names the store it answered from; the store is resolved once per search; a continuation names
both commits when refused; each item's sha256 is the hash of its own lines at the store's commit (W2-138 S1-S4,
DEC-1090 (3)).

Regression evidence only (DEC-136). The stores are planted in temporary git repositories, built with the secret filter
replaced, no vectors and no model: the lexical route only, the reranker a stand-in. A link points at a store as the
integration store's link does; the switch is made by the lexical route's stand-in, between the facets' reads.
"""
from __future__ import annotations

import base64
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.cli.main import main  # noqa: E402
from gov.launch import store as session_store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
WORD = "quillwort"
FILES = {
    "docs/one.md": f"# One\n\nThe {WORD} rule opens the file.\n\n## More\n\nNothing else here.\n",
    "docs/two.md": f"# Two\r\n\r\nA {WORD} line ends in CRLF.\r\nThe next line too.\r\n",
    "docs/three.md": f"# Three\n\nThe last {WORD} line has no newline at its end.",
    "docs/four.md": f"# Four\n\nA fourth {WORD} note.\n",
}


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True,
                          env={**_ENV, "HOME": str(root)}).stdout


def _plant(root: Path, message: str) -> Path:
    for rel, text in {".gitignore": ".gov-runtime/\n", **FILES}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(text.encode("utf-8"))
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)
    lexical.refresh(root)
    store.load(root)
    return root


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD").decode().strip()


@pytest.fixture(autouse=True)
def _stand_ins(monkeypatch):
    for name in (session_store.ENV, "GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    monkeypatch.setattr(retrieve, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})


@pytest.fixture()
def stores(tmp_path):
    """Two stores of the same files built at two commits, and a link to the first."""
    first = _plant(tmp_path / "stores" / "store-a", "the planted files")
    second = _plant(tmp_path / "stores" / "store-b", "the planted files, built again")
    link = tmp_path / "stores" / "store"
    link.symlink_to(first)
    return first.resolve(), second.resolve(), link


def _cli(capsys, *argv) -> dict:
    assert main(["retrieve", "--json", *argv]) == 0
    envelope = json.loads(capsys.readouterr().out)
    assert envelope["ok"], envelope
    return envelope["result"]


# S1: the store named -------------------------------------------------------------------------------------------------

def test_s1_the_json_result_names_the_commit_the_store_was_built_at_and_its_folder(stores, capsys):
    first, _, link = stores
    built = _head(first)
    _git(first, "commit", "-q", "--allow-empty", "-m", "the folder moves on after the build")
    assert _head(first) != built
    result = _cli(capsys, "--root", str(link), WORD)
    assert result["store"] == {"commit": built, "root": str(first)}  # the fingerprint's head, the link resolved
    assert result["evidence"], "premise: the planted search finds evidence"


def test_s1_the_text_form_opens_with_the_store_line(stores, capsys):
    first, _, link = stores
    assert main(["retrieve", "--root", str(link), WORD]) == 0
    out = capsys.readouterr().out
    line, rest = out.split("\n", 1)
    assert line == f"store: {_head(first)[:12]} ({first})"
    assert json.loads(rest)["store"]["commit"] == _head(first)


def test_s1_the_session_variable_form_names_the_store_too(stores, capsys, monkeypatch, tmp_path):
    first, _, link = stores
    monkeypatch.setenv(session_store.ENV, str(link))
    worktree = tmp_path / "worktree"
    worktree.mkdir()
    monkeypatch.chdir(worktree)
    assert _cli(capsys, WORD)["store"] == {"commit": _head(first), "root": str(first)}


def test_s1_the_stated_gap_names_the_store(stores, capsys):
    first, _, link = stores
    result = _cli(capsys, "--root", str(link), "what does DEC-9999 say")
    assert result["stopping_reason"] == "UNRESOLVED_IDS" and result["store"]["commit"] == _head(first)


def test_s1_a_folder_with_no_store_names_no_commit(tmp_path):
    assert retrieve.store_of(tmp_path) == {"commit": None, "root": str(tmp_path)}


# S2: one folder per search -------------------------------------------------------------------------------------------

@pytest.mark.parametrize("form", ["--root", "GOV_STORE", "direct"])
def test_s2_every_facet_reads_the_folder_resolved_at_the_start_across_a_switch(stores, capsys, monkeypatch, tmp_path,
                                                                               form):
    first, second, link = stores
    opened, search = [], lexical.search

    def lexical_route(root, query, **kwargs):
        opened.append(("lexical", os.path.realpath(root)))
        switched = link.with_name(".switch")
        switched.symlink_to(second)
        os.replace(switched, link)  # the refresh switches the link while this search runs
        return search(root, query, **kwargs)

    def meaning_route(root, query, **_):
        opened.append(("semantic", os.path.realpath(root)))
        return {"available": False, "reason": "off", "hits": []}

    monkeypatch.setattr(lexical, "search", lexical_route)
    monkeypatch.setattr(semantic, "search", meaning_route)
    if form == "--root":
        result = _cli(capsys, "--root", str(link), WORD)
    elif form == "GOV_STORE":
        monkeypatch.setenv(session_store.ENV, str(link))
        monkeypatch.chdir(tmp_path)
        result = _cli(capsys, WORD)
    else:
        result = retrieve.retrieve(link, WORD)
    assert opened == [("lexical", str(first)), ("semantic", str(first))]
    assert os.path.realpath(link) == str(second)  # the switch happened
    if form != "direct":  # the command names the store; a direct call's bundle is today's
        assert result["store"] == {"commit": _head(first), "root": str(first)}
    assert result["evidence"]


# S3: the continuation names both commits -----------------------------------------------------------------------------

def _first_page(root) -> str:
    token = retrieve.retrieve(root, WORD, batch_size=1)["continuation"]
    assert token, "premise: the planted search has a second page"
    return token


def test_s3_a_token_carries_its_store_commit_and_pages_on_the_same_store(stores):
    first, _, _ = stores
    token = _first_page(first)
    assert json.loads(base64.urlsafe_b64decode(token))["s"] == _head(first)
    assert retrieve.retrieve(first, WORD, batch_size=1, continuation=token)["evidence"]


def test_s3_a_token_replayed_on_another_store_names_both_commits(stores):
    first, second, _ = stores
    token = _first_page(first)
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(second, WORD, batch_size=1, continuation=token)
    error = raised.value
    assert error.code == "CONTINUATION_INVALID"
    assert _head(first)[:12] in error.message and _head(second)[:12] in error.message
    assert error.details == {"token_commit": _head(first), "store_commit": _head(second)}


def test_s3_the_command_refuses_it_through_the_envelope(stores, capsys):
    first, second, _ = stores
    token = _first_page(first)
    assert main(["retrieve", "--json", "--root", str(second), "--batch-size", "1", "--continue", token, WORD]) == 1
    error = json.loads(capsys.readouterr().out)["error"]
    assert error["code"] == "CONTINUATION_INVALID" and error["details"]["token_commit"] == _head(first)


def test_s3_a_token_made_before_w2_138_is_refused_as_such(stores):
    first, _, _ = stores
    payload = json.loads(base64.urlsafe_b64decode(_first_page(first)))
    del payload["s"]
    old = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode()
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(first, WORD, batch_size=1, continuation=old)
    assert raised.value.code == "CONTINUATION_INVALID" and "made before W2-138" in raised.value.message


@pytest.mark.parametrize("token", [base64.urlsafe_b64encode(b"[1, 2]").decode(), "not a token"])
def test_s3_a_token_that_is_no_object_is_refused(stores, token):
    first, _, _ = stores
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(first, WORD, batch_size=1, continuation=token)
    assert raised.value.code == "CONTINUATION_INVALID"


# S4: each item's hash is its lines at the store's commit -------------------------------------------------------------

def test_s4_every_item_s_sha256_is_its_lines_at_the_named_commit(stores, capsys):
    first, _, link = stores
    result = _cli(capsys, "--root", str(link), WORD)
    commit, items = result["store"]["commit"], result["evidence"]
    assert {item["path"] for item in items} >= {"docs/two.md", "docs/three.md"}, "premise: the CRLF and no-LF files"
    for item in items:
        lines = _git(first, "show", f"{commit}:{item['path']}").splitlines(keepends=True)
        span = b"".join(lines[item["start_line"] - 1:item["end_line"]])
        assert item["sha256"] == hashlib.sha256(span).hexdigest(), item["path"]
