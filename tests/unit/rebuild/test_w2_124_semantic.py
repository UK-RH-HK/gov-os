"""W2-124: ``gov rebuild`` fails named where the semantic store was asked for and not recreated (S1), is not asked for
where nothing is embedded (S2), and names every store not built (S5). Stand-ins for every store: no embedder runs."""
from __future__ import annotations

import argparse

import pytest

from gov.cli.errors import GovError
from gov.rebuild.command import add_arguments, run


def _args(*given):
    parser = argparse.ArgumentParser()
    add_arguments(parser)
    return parser.parse_args(list(given))


EMBEDDED = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "embedded"}}}}
NOT_EMBEDDED = {"path-map.yaml": {"namespaces": {"all": {"paths": ["**"], "embedding_policy": "not embedded"}}}}


class Embedder:
    """What the semantic store's refresh does, and how often it was asked."""

    def __init__(self):
        self.calls = 0
        self.does = lambda: {"available": True}

    def __call__(self, root):
        self.calls += 1
        return self.does()


@pytest.fixture()
def embedder(monkeypatch):
    stand_in, remembered = Embedder(), []
    monkeypatch.setattr("gov.store.load", lambda root: {"digest": "d"})
    monkeypatch.setattr("gov.retrieval.lexical.refresh", lambda root: {})
    monkeypatch.setattr("gov.retrieval.semantic.refresh", stand_in)
    monkeypatch.setattr("gov.retrieval.semantic.manifest", lambda root: {"embedder": "stand-in"})
    monkeypatch.setattr("gov.codeintel.index", lambda root: None)
    monkeypatch.setattr("gov.rebuild.seed.remember", lambda root, built_by: remembered.append(built_by))
    stand_in.remembered = remembered
    return stand_in


def _unavailable():
    return {"available": False, "reason": "the embedding endpoint is unavailable"}


def _hangs():
    raise TimeoutError("the embedding endpoint did not answer within its timeout")


def _fails_part_way():
    raise RuntimeError("the embedder failed at chunk 3 of 7")


@pytest.mark.parametrize("does, reason", [(_unavailable, "endpoint is unavailable"), (_hangs, "did not answer"),
                                          (_fails_part_way, "failed at chunk 3")])
def test_s1_a_semantic_store_asked_for_and_not_recreated_fails_named(tmp_path, embedder, does, reason):
    embedder.does = does
    with pytest.raises(GovError) as raised:
        run(tmp_path, _args(), EMBEDDED)
    error = raised.value
    assert error.code == "REBUILD_FAILED" and error.exit_code == 1
    assert "store: semantic" in error.message and reason in error.message
    assert error.details["store"] == "semantic" and reason in error.details["reason"]
    stores = error.details["stores"]
    assert stores["semantic"]["status"] == "not_recreated" and stores["lexical"] == {"status": "recreated"}
    assert embedder.calls == 1


def test_s1_a_failed_rebuild_leaves_no_warm_base_record(tmp_path, embedder):
    embedder.does = _unavailable
    with pytest.raises(GovError):
        run(tmp_path, _args(), EMBEDDED)
    assert embedder.remembered == []
    embedder.does = lambda: {"available": True}
    assert run(tmp_path, _args(), EMBEDDED)["stores"]["semantic"] == {"status": "recreated"}
    assert embedder.remembered == ["stand-in"]


@pytest.mark.parametrize("does", [_unavailable, _hangs, _fails_part_way])
def test_s1_no_embeddings_skips_the_store_and_is_ok_and_says_so(tmp_path, embedder, does):
    embedder.does = does
    result = run(tmp_path, _args("--no-embeddings"), EMBEDDED)
    semantic = result["stores"]["semantic"]
    assert (semantic["status"], semantic["requested"]) == ("not_recreated", False)
    assert "--no-embeddings" in semantic["reason"] and embedder.calls == 0
    assert result["complete"] is True and result["not_built"] == []


@pytest.mark.parametrize("config", [NOT_EMBEDDED, {}], ids=["no embedded namespace", "no path map"])
def test_s2_a_project_with_nothing_to_embed_is_not_asked_and_no_embedder_runs(tmp_path, embedder, config):
    embedder.does = _unavailable
    result = run(tmp_path, _args(), config)
    semantic = result["stores"]["semantic"]
    assert (semantic["status"], semantic["requested"]) == ("not_recreated", False)
    assert "not asked for" in semantic["reason"] and embedder.calls == 0
    assert "semantic" not in [item["store"] for item in result["not_built"]]


def test_s2_the_reason_of_a_path_map_with_no_embedded_namespace_names_it(tmp_path, embedder):
    reason = run(tmp_path, _args(), NOT_EMBEDDED)["stores"]["semantic"]["reason"]
    assert reason.startswith("no namespace is embedded")


def test_s5_a_complete_rebuild_says_so(tmp_path, embedder):
    result = run(tmp_path, _args(), EMBEDDED)
    assert result["complete"] is True and result["not_built"] == []


def test_s5_no_path_map_names_the_lexical_index_and_stays_ok(tmp_path, embedder):
    """W2-26 finding 2: a clone with no path map answers (ok) and now says it is not complete, naming the stores."""
    result = run(tmp_path, _args(), {})
    assert result["complete"] is False
    assert [item["store"] for item in result["not_built"]] == ["lexical"]
    assert "no path map" in result["not_built"][0]["reason"]
    assert result["stores"]["lexical"]["status"] == "not_recreated"


def test_s5_no_path_map_also_names_the_code_index_that_built_nothing(tmp_path, embedder, monkeypatch):
    def refuse(root):
        raise KeyError("path-map.yaml")

    monkeypatch.setattr("gov.codeintel.index", refuse)
    named = {item["store"]: item["reason"] for item in run(tmp_path, _args(), {})["not_built"]}
    assert sorted(named) == ["codeintel", "lexical"] and "no path map" in named["codeintel"]


def test_s5_no_gitleaks_file_names_the_store_that_was_refused_for_it(tmp_path, embedder, monkeypatch):
    def refused(root):
        raise RuntimeError(".gitleaks.toml cannot be read: no such file")

    monkeypatch.setattr("gov.codeintel.index", refused)
    result = run(tmp_path, _args(), EMBEDDED)
    assert result["complete"] is False
    assert [(item["store"], ".gitleaks.toml" in item["reason"]) for item in result["not_built"]] == [("codeintel", True)]


def test_s5_a_store_the_path_map_calls_for_and_not_built_is_named_with_its_reason(tmp_path, embedder, monkeypatch):
    def broken(root):
        raise RuntimeError("the code index tool failed (exit code 2)")

    monkeypatch.setattr("gov.codeintel.index", broken)
    (tmp_path / ".gitleaks.toml").write_text("title = 'x'\n", encoding="utf-8")
    result = run(tmp_path, _args(), EMBEDDED)
    assert result["not_built"] == [{"store": "codeintel", "reason": "the code index tool failed (exit code 2)"}]
    assert result["complete"] is False


def test_s5_a_store_that_was_not_asked_for_is_never_not_built(tmp_path, embedder):
    for given, config in (("--no-embeddings", EMBEDDED), (None, NOT_EMBEDDED)):
        result = run(tmp_path, _args(*([given] if given else [])), config)
        assert result["stores"]["semantic"]["requested"] is False
        assert result["not_built"] == [] and result["complete"] is True
