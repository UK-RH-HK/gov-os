"""R2-F3 (W2-116 pass 2b, P-W2-116-S2-INTERFACE Q3 (a)): the continuation token carries the folder of the store it was
made on, and is refused on another folder even at the same commit.

Regression evidence only (MR-3). The stores are planted in temporary git repositories as W2-138's are (the lexical
route only, the reranker a stand-in; no vectors, no model); a copy of a store is a second folder at the same commit,
as the integration store's two halves are at one head.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.cli.main import main  # noqa: E402
from gov.launch import store as session_store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402

from tests.unit.retrieval.test_w2_138_store import WORD, _head, _plant  # noqa: E402


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
def halves(tmp_path):
    """Two folders at the same commit (the second a copy of the first), and a link to the first."""
    first = _plant(tmp_path / "stores" / "store-a", "the planted files").resolve()
    second = tmp_path / "stores" / "store-b"
    shutil.copytree(first, second, symlinks=True)
    link = tmp_path / "stores" / "store"
    link.symlink_to(first)
    return first, second.resolve(), link


def _token(root) -> str:
    token = retrieve.retrieve(root, WORD, batch_size=1)["continuation"]
    assert token, "premise: the planted search has a second page"
    return token


def _payload(token: str) -> dict:
    return json.loads(base64.urlsafe_b64decode(token))


def _encode(payload: dict) -> str:
    return base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode()


def test_the_token_carries_the_resolved_folder_it_was_made_on(halves):
    first, _, link = halves
    assert _payload(_token(first))["f"] == str(first)
    assert _payload(_token(link))["f"] == str(first), "made through the link: the half the link pointed at"


def test_premise_the_two_folders_are_at_one_commit(halves):
    first, second, _ = halves
    assert _head(first) == _head(second)
    assert retrieve.store_of(first)["commit"] == retrieve.store_of(second)["commit"]


def test_a_token_replayed_on_another_folder_at_the_same_commit_is_refused_naming_both(halves):
    first, second, _ = halves
    token = _token(first)
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(second, WORD, batch_size=1, continuation=token)
    error = raised.value
    assert error.code == "CONTINUATION_INVALID"
    assert "another store" in error.message and str(first) in error.message and str(second) in error.message
    assert error.details == {"token_root": str(first), "store_root": str(second)}


def test_a_token_pages_on_the_same_folder_as_before(halves):
    first, _, link = halves
    assert retrieve.retrieve(first, WORD, batch_size=1, continuation=_token(first))["evidence"]
    assert retrieve.retrieve(link, WORD, batch_size=1, continuation=_token(link))["evidence"]
    assert retrieve.retrieve(first, WORD, batch_size=1, continuation=_token(link))["evidence"], "link and half: one folder"


def test_a_token_made_through_the_link_is_refused_after_a_switch_to_the_other_half(halves):
    first, second, link = halves
    token = _token(link)
    switched = link.with_name(".switch")
    switched.symlink_to(second)
    os.replace(switched, link)  # the refresh switches the link between page 1 and page 2
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(link, WORD, batch_size=1, continuation=token)
    assert raised.value.code == "CONTINUATION_INVALID" and raised.value.details["token_root"] == str(first)


def test_a_token_without_the_mark_is_refused_as_one_made_before_it(halves):
    first, _, _ = halves
    payload = _payload(_token(first))
    del payload["f"]
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(first, WORD, batch_size=1, continuation=_encode(payload))
    assert raised.value.code == "CONTINUATION_INVALID" and "folder" in raised.value.message


def test_a_token_that_names_another_commit_is_still_refused_for_its_commit_first(halves):
    first, _, _ = halves
    payload = _payload(_token(first))
    payload["s"] = "0" * 40
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(first, WORD, batch_size=1, continuation=_encode(payload))
    assert raised.value.details == {"token_commit": "0" * 40, "store_commit": _head(first)}


def test_the_command_refuses_it_through_the_envelope_and_pages_on_the_same_folder(halves, capsys):
    first, second, link = halves
    assert main(["retrieve", "--json", "--root", str(link), "--batch-size", "1", WORD]) == 0
    token = json.loads(capsys.readouterr().out)["result"]["continuation"]
    assert main(["retrieve", "--json", "--root", str(link), "--batch-size", "1", "--continue", token, WORD]) == 0
    capsys.readouterr()
    assert main(["retrieve", "--json", "--root", str(second), "--batch-size", "1", "--continue", token, WORD]) == 1
    error = json.loads(capsys.readouterr().out)["error"]
    assert error["code"] == "CONTINUATION_INVALID" and error["details"]["token_root"] == str(first)
