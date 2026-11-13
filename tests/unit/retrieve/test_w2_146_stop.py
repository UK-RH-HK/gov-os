"""Builder tests for the stop on a declared id form (W2-146; DEC-1071 (5), DEC-1099 (2), DEC-900).

Regression evidence only (DEC-136). A repository's path map declares id forms the built-in shape does not read; a
question that names one that exists nowhere stops with ``UNRESOLVED_IDS``, and one that is present as a whole token on
a line of the index is retrieved as before. The store is built in a temporary repository with invented ids (DEC-322);
the semantic route and the reranker are replaced, so no endpoint and no model is asked.
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import closure, store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval import retrieve as retrieve_module  # noqa: E402
from gov.retrieve import command  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")

FORMS = [
    {"name": "bare", "pattern": r"ZQ\d+"},
    {"name": "lower", "pattern": r"bug\d+"},
    {"name": "under", "pattern": r"[A-Z]{2}_\d+"},
    {"name": "dotted", "pattern": r"[A-Z]+-\d+(?:\.\d+)+"},
    {"name": "spaced", "pattern": r"PX \d+"},
]
HELD = ["ZQ41", "bug7", "KV_12", "SPEC-4.2", "PX 41"]       # each on a line of the index
GONE = ["ZQ99", "bug99", "KV_99", "SPEC-9.9", "PX 99"]      # each nowhere
PAIRS = list(zip(HELD, GONE, strict=True))


def _write_map(root: Path, forms) -> None:
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    path_map.pop("id_forms", None)
    if forms is not None:
        path_map["id_forms"] = forms
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")


def _plant(tmp_path: Path, monkeypatch, forms) -> Path:
    git = ["git", "-C", str(tmp_path), "-c", "user.name=unit", "-c", "user.email=unit@example.invalid"]
    subprocess.run([*git, "init", "-q"], check=True)
    (tmp_path / "governance/project").mkdir(parents=True)
    _write_map(tmp_path, forms)
    shutil.copy2(REPO / "template/.gitleaks.toml", tmp_path / ".gitleaks.toml")
    (tmp_path / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for number in (1, 2, 3):
        (tmp_path / f"note{number}.md").write_text(f"# Note {number}\n\nWhat the harbour decides, pier {number}.\n",
                                                   encoding="utf-8")
    lines = [f"The pilot logged {token} against the harbour tide." for token in HELD]
    (tmp_path / "held.md").write_text("# Held\n\n" + "\n".join(lines) + "\nAnd DEC-41 for the harbour.\n",
                                      encoding="utf-8")
    subprocess.run([*git, "add", "-A"], check=True)
    subprocess.run([*git, "commit", "-q", "-m", "fixture"], check=True)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    hits = [{"chunk_id": chunk["chunk_id"], "path": chunk["path"]} for chunk in lexical.chunks(tmp_path)]
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None,
                                                                       "hits": hits})
    monkeypatch.setattr(retrieve_module, "rerank", lambda _query, candidates, _reranker=None: candidates)  # no model
    monkeypatch.setattr(closure, "_symbol", lambda *_args: None)  # no code-graph tool is asked
    return tmp_path


@pytest.fixture()
def root(tmp_path, monkeypatch):
    return _plant(tmp_path, monkeypatch, FORMS)


def _ask(root, query, ids=(), ticket=None):
    return command.run(root, argparse.Namespace(query=query, ticket=ticket, ids=list(ids), radius=0, batch_size=None,
                                                bundle_budget=None, continuation=None), {})


@pytest.mark.parametrize("held, gone", PAIRS, ids=[gone for _, gone in PAIRS])
def test_a_declared_form_id_that_exists_nowhere_is_the_stated_gap(root, held, gone):
    for query in (gone, f"What did the pilot log as {gone} at the harbour?"):
        bundle = _ask(root, query)
        assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["evidence"] == [], (query, bundle)
        assert bundle["gaps"] == [{"id": gone, "reason": "UNRESOLVED"}] and bundle["continuation"] is None
        assert bundle["batches"] == [{"size": 0}] and bundle["facets"]["lexical"]["available"] is True


@pytest.mark.parametrize("held, gone", PAIRS, ids=[held for held, _ in PAIRS])
def test_a_declared_form_id_present_as_a_whole_token_is_retrieved_as_before(root, held, gone):
    for query in (held, f"What did the pilot log as {held} at the harbour?"):
        bundle = _ask(root, query)
        assert bundle["stopping_reason"] != "UNRESOLVED_IDS" and bundle["evidence"], (query, bundle)


@pytest.mark.parametrize("held, gone", PAIRS, ids=[held for held, _ in PAIRS])
def test_one_named_id_that_exists_means_the_request_is_retrieved_as_before(root, held, gone):
    bundle = _ask(root, f"What did the pilot log as {gone} and as {held}?")
    assert bundle["stopping_reason"] != "UNRESOLVED_IDS" and bundle["evidence"]


def test_a_declared_form_id_and_a_built_in_id_that_exist_nowhere_are_both_gaps(root):
    bundle = _ask(root, "What do ZQ99, DEC-9999 and PX 99 say?")
    assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["evidence"] == []
    assert [gap["id"] for gap in bundle["gaps"]] == ["ZQ99", "DEC-9999", "PX 99"]  # in the question's order


def test_a_prefix_of_a_held_id_is_not_that_id(root):
    # "PX 4" is in the line of "PX 41" as a string, but not as a whole token
    bundle = _ask(root, "What did the pilot log as PX 4?")
    assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["gaps"] == [{"id": "PX 4", "reason": "UNRESOLVED"}]


def test_a_dotted_id_is_stopped_whole_not_answered_by_its_fragment(root):
    bundle = _ask(root, "What did the pilot log as SPEC-4.3?")  # SPEC-4.2 is held; SPEC-4 alone is no line's token
    assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["gaps"] == [{"id": "SPEC-4.3",
                                                                                "reason": "UNRESOLVED"}]


@pytest.mark.parametrize("held, gone", PAIRS, ids=[gone for _, gone in PAIRS])
def test_an_id_and_a_ticket_of_a_declared_form_that_exist_nowhere_are_the_stated_gap(root, held, gone):
    for ids, ticket in (([gone], None), ([], gone)):
        bundle = _ask(root, "What did the pilot log at the harbour?", ids, ticket)
        assert bundle["stopping_reason"] == "UNRESOLVED_IDS" and bundle["evidence"] == []
        assert [gap["id"] for gap in bundle["gaps"]] == [gone] and bundle["continuation"] is None


def test_a_given_id_that_is_no_declared_form_is_a_symbol_name_as_before(root):
    bundle = _ask(root, "What did the pilot log as ZQ99?", ids=["resize"])
    assert bundle["stopping_reason"] != "UNRESOLVED_IDS" and bundle["evidence"]


def test_with_no_form_declared_the_same_question_is_retrieved_as_before(tmp_path, monkeypatch):
    plain = _plant(tmp_path, monkeypatch, None)
    for gone in GONE:
        bundle = _ask(plain, f"What did the pilot log as {gone} at the harbour?")
        if gone == "SPEC-9.9":  # the built-in shape reads its fragment: SPEC-9 exists nowhere, so today's stop fires
            assert bundle["gaps"] == [{"id": "SPEC-9", "reason": "UNRESOLVED"}]
        else:
            assert bundle["stopping_reason"] != "UNRESOLVED_IDS", gone
    assert _ask(plain, "What does DEC-9999 decide?")["stopping_reason"] == "UNRESOLVED_IDS"  # the built-in shape's


def test_a_malformed_form_is_config_invalid_before_any_search(root, monkeypatch):
    _write_map(root, [FORMS[0], {"name": "broken", "pattern": "ZQ(\\d+"}])
    monkeypatch.setattr(lexical, "search", lambda *_a, **_k: pytest.fail("searched before the forms were read"))
    with pytest.raises(GovError) as raised:
        _ask(root, "What did the pilot log as ZQ99?")
    assert raised.value.code == "CONFIG_INVALID" and "id_forms[1]" in raised.value.message


def test_a_malformed_form_makes_gov_retrieve_exit_1(root, capsys):
    from gov.cli.main import main

    _write_map(root, [{"name": "bare"}])
    code = main(["retrieve", "--json", "--root", str(root), "What did the pilot log as ZQ99?"])
    out, err = capsys.readouterr()
    assert code == 1 and "CONFIG_INVALID" in out + err and "Traceback" not in err, (code, out, err)


def test_nowhere_reads_the_forms_once(root, monkeypatch):
    calls = []
    real = lexical.id_forms
    monkeypatch.setattr(lexical, "id_forms", lambda place: calls.append(place) or real(place))
    assert command._nowhere(root, "What do ZQ99 and PX 99 say?", ["bug99"]) is not None
    assert calls == [root]
