"""W2-32 S11 (DEC-1071 (2), DEC-1074 (5)): the candidate pool, v456. Five query-time settings under ``pool:`` in
``governance/project/retrieval.yaml``, each absent or 0 today's behaviour; the loader refuses an invalid value with
CONFIG_INVALID naming ``pool.<key>``.

Regression evidence only (DEC-136): the keyword index is real (a temporary repository); the meaning route, the record
route and the reranker are stand-ins (the reranker scores by a digest of each text, so its order is known here). No
model starts.
"""
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.retrieval import authority, lexical, pool, rerank as rerank_module, retrieve as retrieve_module, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
PHRASE = "heron ledger"
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
NOTES = 48
LONG_NOTES = 6  # notes of one 5,000-character line: the padded bound binds before the 16 texts do


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _score(text: str) -> float:
    return int(hashlib.sha256(text.encode()).hexdigest()[:8], 16) / 16 ** 8


class Reranker:
    """A stand-in reranker: each request's texts recorded; a text naming ``multi.md`` scores above the rest."""

    def __init__(self):
        self.requests: list[tuple[str, list[str]]] = []

    def __call__(self):
        def score(query, texts):
            self.requests.append((query, list(texts)))
            return [(10.0 if "[path: multi.md]" in text else 0.0) + _score(text) for text in texts]
        return score

    def texts(self) -> list[str]:
        return [text for _, texts in self.requests for text in texts]


@pytest.fixture()
def project(tmp_path, monkeypatch):
    return _project(tmp_path, monkeypatch, LONG_NOTES)


@pytest.fixture()
def short_project(tmp_path, monkeypatch):
    """The same notes, none of them long: the pool's 40 go in three requests of at most 16."""
    return _project(tmp_path, monkeypatch, 0)


def _project(tmp_path, monkeypatch, long_notes):
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    path_map.pop("retrieval_authority", None)  # no authority lift: the rerank's order is the stand-in's
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for number in range(NOTES):
        filler = "x" * 5000 if number < long_notes else "plain words"
        (root / f"note{number:02}.md").write_text(f"# Note {number}\n\nThe {PHRASE} of pier {number}. {filler}\n"
                                                  f"A ledger, and a heron by it.\n", encoding="utf-8")
    sections = "".join(f"## Part {n}\n\nThe {PHRASE}, part {n}.\n\n" for n in range(6))
    (root / "multi.md").write_text(f"# Multi\n\n{sections}", encoding="utf-8")
    lines = "".join(f"The {PHRASE} line {n:02}, {'w' * 80}\n" for n in range(40))
    (root / "big.md").write_text(f"# Big\n\n## Long\n\n{lines}", encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    lexical.refresh(root)
    store.load(root)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": False, "reason": "off", "hits": []})
    monkeypatch.setattr(retrieve_module.graph_route, "start_ids", lambda root_, query, known: [])
    fused_lists = []
    real_rrf = retrieve_module.rrf

    def rrf(routes, **kwargs):
        fused_lists.append({"routes": {name: list(hits) for name, hits in routes.items()}})
        out = real_rrf(routes, **kwargs)
        fused_lists[-1]["fused"] = [hit["chunk_id"] for hit in out]
        return out

    monkeypatch.setattr(retrieve_module, "rrf", rrf)
    return root, fused_lists


def _settings(root, pool_block=None, routing=None):
    path = root / "governance/project/retrieval.yaml"
    document = {**({"pool": pool_block} if pool_block is not None else {}),
                **({"routing": routing} if routing is not None else {})}
    if document:
        path.write_text(yaml.safe_dump(document), encoding="utf-8")
    elif path.exists():
        path.unlink()


def _ask(root, reranker, query=PHRASE, **kwargs):
    kwargs.setdefault("batch_size", 100)
    kwargs.setdefault("bundle_budget", 0)
    return retrieve(root, query, reranker=reranker, **kwargs)


def _ids(bundle):
    return [item["chunk_id"] for item in bundle["evidence"]]


def _all_pages(root, reranker, **kwargs):
    """Every call's evidence, the continuation followed to the end."""
    order, token = [], None
    while True:
        bundle = _ask(root, reranker, continuation=token, **kwargs)
        order += _ids(bundle)
        token = bundle["continuation"]
        if token is None:
            return order


# ---- the loader


@pytest.mark.parametrize("key,value", [
    ("meaning_uncut", "yes"), ("meaning_uncut", 1), ("meaning_uncut", None), ("drop_nested", "true"),
    ("drop_nested", 2), ("route_depth", -1), ("route_depth", True), ("route_depth", 2.5), ("route_depth", "60"),
    ("rerank_depth", -40), ("rerank_depth", False), ("per_file_first10", "2"), ("per_file_first10", [2]),
    ("unknown_key", 1)])
def test_an_invalid_value_is_config_invalid_naming_the_key(tmp_path, key, value):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/retrieval.yaml").write_text(yaml.safe_dump({"pool": {key: value}}),
                                                                encoding="utf-8")
    with pytest.raises(GovError) as raised:
        pool.settings(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and raised.value.details["key"] == f"pool.{key}"
    assert f"pool.{key}" in raised.value.message


def test_a_pool_that_is_no_map_is_config_invalid(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/retrieval.yaml").write_text("pool: 3\n", encoding="utf-8")
    with pytest.raises(GovError) as raised:
        pool.settings(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and raised.value.details["key"] == "pool"


@pytest.mark.parametrize("text", [None, "routing:\n  code_first: 2\n", "pool:\n", "pool: {}\n",
                                  "pool:\n  meaning_uncut: 0\n  route_depth: 0\n  rerank_depth: 0\n"
                                  "  per_file_first10: 0\n  drop_nested: 0\n",
                                  "pool:\n  meaning_uncut: false\n  drop_nested: false\n"])
def test_absent_or_0_is_off(tmp_path, text):
    (tmp_path / "governance/project").mkdir(parents=True)
    if text is not None:
        (tmp_path / "governance/project/retrieval.yaml").write_text(text, encoding="utf-8")
    assert pool.settings(tmp_path) == {"meaning_uncut": False, "route_depth": 0, "rerank_depth": 0,
                                       "per_file_first10": 0, "drop_nested": False}


def test_v456_s_values_are_read(tmp_path):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/retrieval.yaml").write_text(
        "pool:\n  meaning_uncut: true\n  route_depth: 60\n  rerank_depth: 40\n  per_file_first10: 2\n"
        "  drop_nested: true\n", encoding="utf-8")
    assert pool.settings(tmp_path) == {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40,
                                       "per_file_first10": 2, "drop_nested": True}


def test_an_invalid_pool_stops_the_search_before_any_route(project, monkeypatch):
    root, fused_lists = project
    _settings(root, {"rerank_depth": -1})
    asked = []
    monkeypatch.setattr(lexical, "search", lambda *a, **k: asked.append(a) or {})
    with pytest.raises(GovError) as raised:
        _ask(root, Reranker())
    assert raised.value.details["key"] == "pool.rerank_depth" and not asked and not fused_lists


# ---- the pure parts


def test_capped_holds_the_first_10_to_n_a_file_and_loses_none():
    items = [{"id": n, "path": "a" if n < 8 else f"f{n}"} for n in range(16)]
    out = pool.capped(items, 2)
    assert [item["id"] for item in out] == [0, 1, 8, 9, 10, 11, 12, 13, 14, 15, 2, 3, 4, 5, 6, 7]
    assert sorted(item["id"] for item in out) == list(range(16))
    assert pool.capped(items, 0) == items


def test_without_nested_drops_an_item_inside_an_earlier_one_of_the_same_file():
    evidence = [{"path": "a", "start_line": 1, "end_line": 20}, {"path": "b", "start_line": 2, "end_line": 5},
                {"path": "a", "start_line": 3, "end_line": 9}, {"path": "a", "start_line": 15, "end_line": 25},
                {"path": "b", "start_line": 2, "end_line": 5}]
    kept, nested = pool.without_nested(evidence)
    assert kept == [evidence[0], evidence[1], evidence[3]] and nested == [evidence[2], evidence[4]]


# ---- absent or 0: today's behaviour


@pytest.mark.parametrize("block", [{}, {"meaning_uncut": False, "route_depth": 0, "rerank_depth": 0,
                                        "per_file_first10": 0, "drop_nested": False},
                                   {"meaning_uncut": 0, "drop_nested": 0}])
def test_absent_or_0_returns_today_s_bundle_byte_for_byte(project, block):
    root, _ = project
    for routing in (None, {"phrasings": True}):
        _settings(root, None, routing)
        first, before = Reranker(), None
        before = json.dumps(_ask(root, first, bundle_budget=6000, batch_size=10), sort_keys=True)
        _settings(root, block, routing)
        second = Reranker()
        assert json.dumps(_ask(root, second, bundle_budget=6000, batch_size=10), sort_keys=True) == before
        assert second.requests == first.requests and "pool" not in json.loads(before)


# ---- route_depth


def test_route_depth_is_each_search_s_depth_never_a_module_s(project, monkeypatch):
    root, fused_lists = project
    asked = []
    monkeypatch.setattr(semantic, "search", lambda root_, query, refresh=True, **kwargs: asked.append(kwargs) or
                        {"available": False, "reason": "off", "hits": []})
    query = "the ledger of a heron"  # no chunk holds it whole: the keyword route's words alone rank its chunks
    _settings(root, None)
    _ask(root, Reranker(), query)
    today = fused_lists[-1]["routes"]["lexical"]
    _settings(root, {"route_depth": 5})
    _ask(root, Reranker(), query)
    assert len(today) == lexical.TOP_K == 30 and len(fused_lists[-1]["routes"]["lexical"]) == 5
    assert asked == [{}, {"top_k": 5}] and semantic.TOP_K == 30
    _settings(root, {"route_depth": 45})
    _ask(root, Reranker(), query)
    assert len(fused_lists[-1]["routes"]["lexical"]) == 45 and lexical.TOP_K == 30


def test_the_keyword_search_takes_its_depth(project):
    root, _ = project
    query = "the ledger of a heron"
    assert len(lexical.search(root, query, refresh=False)["ranked"]) == 30
    assert len(lexical.search(root, query, refresh=False, top_k=7)["ranked"]) == 7
    assert lexical.search(root, query, refresh=False, top_k=0) == lexical.search(root, query, refresh=False)


# ---- meaning_uncut


def _meaning_stand_in(root, monkeypatch, asked):
    chunk_list = lexical.chunks(root)

    def search(root_, query, refresh=True, top_k=None):
        asked.append(query)
        depth = top_k or semantic.TOP_K
        start = 0 if len(asked) % 2 else 25  # the two phrasings overlap in 5 chunks
        return {"available": True, "reason": None,
                "hits": [{**chunk, "distance": n / 100} for n, chunk in enumerate(chunk_list[start:start + depth])]}
    monkeypatch.setattr(semantic, "search", search)
    return chunk_list


def test_meaning_uncut_keeps_the_phrasings_fused_list_whole(project, monkeypatch):
    root, fused_lists = project
    asked = []
    _meaning_stand_in(root, monkeypatch, asked)
    query = "the ledger of the heron?"  # two phrasings: the question and its content words
    _settings(root, None, {"phrasings": True})
    _ask(root, Reranker(), query)
    assert len(asked) == 2 and len(fused_lists[-1]["routes"]["semantic"]) == 30
    cut = fused_lists[-1]["routes"]["semantic"]
    _settings(root, {"meaning_uncut": True}, {"phrasings": True})
    _ask(root, Reranker(), query)
    whole = fused_lists[-1]["routes"]["semantic"]
    assert len(whole) == 55 and whole[:30] == cut
    _settings(root, {"route_depth": 40}, {"phrasings": True})
    _ask(root, Reranker(), query)
    assert len(fused_lists[-1]["routes"]["semantic"]) == 40  # cut back to the route's depth
    _settings(root, {"route_depth": 40, "meaning_uncut": True}, {"phrasings": True})
    _ask(root, Reranker(), query)
    assert len(fused_lists[-1]["routes"]["semantic"]) == 65


# ---- rerank_depth


def _pool_order(root, fused, scores_of, depth, cap=0):
    """The harness's v456 order, worked out here: the first ``depth`` fused, by the stand-in's score (ties as fused),
    held to ``cap`` a file in the first 10, then the rest as fused."""
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)}
    head = [cid for cid in fused[:depth] if cid in chunks]
    ranked = sorted(head, key=lambda cid: -scores_of[cid])
    if cap:
        ranked = [item["chunk_id"] for item in pool.capped([{"chunk_id": cid, "path": chunks[cid]["path"]}
                                                            for cid in ranked], cap)]
    return ranked + [cid for cid in fused if cid not in ranked]


def _scores_of(root, reranker):
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)}
    out = {}
    for cid, chunk in chunks.items():
        body = b"".join((root / chunk["path"]).read_bytes().splitlines(keepends=True)
                        [chunk["start_line"] - 1:chunk["end_line"]])
        text = retrieve_module._rerank_text(chunk, body)
        out[cid] = reranker()(PHRASE, [text])[0]
    return out


def test_rerank_depth_reranks_the_first_n_once_and_cuts_every_page_from_that_order(project):
    root, fused_lists = project
    _settings(root, {"rerank_depth": 12})
    reranker = Reranker()
    first = _ask(root, reranker, batch_size=4)  # radius 0: 8 a call, so the 12 span two calls
    assert len(reranker.texts()) == 12 and first["pool"]["reranked"] == 12
    assert first["rerank"]["by"] == "given" and first["merge"]["reranked"]
    fused = fused_lists[-1]["fused"]
    expected = _pool_order(root, fused, _scores_of(root, Reranker()), 12)
    pages = _all_pages(root, reranker, batch_size=4)
    assert pages == expected and len(set(pages)) == len(fused)
    calls = len(fused_lists) - 1
    assert calls > 2  # the question's continuations, each a new call
    assert len(reranker.texts()) == 12 * 2  # one pass of the 12 a question (asked twice here), never a call's own


def test_the_pool_s_requests_stay_under_the_padded_bound(project):
    root, _ = project
    _settings(root, {"rerank_depth": 60})
    reranker = Reranker()
    _ask(root, reranker)
    assert len(reranker.texts()) == 60
    for query, texts in reranker.requests:
        assert 0 < len(texts) <= rerank_module.MAX_REQUEST_TEXTS
        assert len(texts) * max(len(query) + len(text) for text in texts) <= rerank_module.MAX_REQUEST_CHARS
    assert any(len(texts) < rerank_module.MAX_REQUEST_TEXTS for _, texts in reranker.requests[:-1])  # the long ones


def test_the_pool_is_lifted_by_authority_before_the_cut(project, monkeypatch):
    root, fused_lists = project
    seen = []

    def reranked(self, ranked):
        seen.append(len(ranked))
        return list(reversed(ranked))
    monkeypatch.setattr(authority.Order, "reranked", reranked)
    _settings(root, {"rerank_depth": 6})
    bundle = _ask(root, Reranker())
    expected = _pool_order(root, fused_lists[-1]["fused"], _scores_of(root, Reranker()), 6)
    assert seen == [6] and _ids(bundle)[:6] == list(reversed(expected[:6]))


def test_a_pool_rerank_that_fails_falls_back_to_the_per_page_path_of_that_call(project):
    root, fused_lists = project
    _settings(root, {"rerank_depth": 10})
    calls = []

    def broken():
        def score(query, texts):
            calls.append(len(texts))
            raise BrokenPipeError("the stand-in died")
        return score
    bundle = _ask(root, broken)
    # the pool's first request failed; the page then asked on its own (today's path), and failed too
    assert len(calls) == 2 and bundle["pool"]["order"] == "per-page" and bundle["pool"]["reranked"] == 0
    assert bundle["pool"]["fallback"]["by"] == "unavailable" and "died" in bundle["pool"]["fallback"]["reason"]
    assert bundle["rerank"]["by"] == "unavailable" and "died" in bundle["rerank"]["reason"]
    assert not bundle["merge"]["reranked"] and _ids(bundle) == fused_lists[-1]["fused"]


class FailsFirst(Reranker):
    """The stand-in, its first request failing (the pool's), the later ones scored."""

    def __call__(self):
        scored = super().__call__()

        def score(query, texts):
            if not self.requests:
                self.requests.append((query, list(texts)))
                raise BrokenPipeError("the stand-in died once")
            return scored(query, texts)
        return score


def test_a_failed_pool_ranks_each_page_on_its_own_and_the_question_s_cut_stays_whole(project):
    root, fused_lists = project
    _settings(root, {"rerank_depth": 10})
    first = _ask(root, FailsFirst(), batch_size=4)
    fused = fused_lists[-1]["fused"]
    assert first["pool"]["order"] == "per-page" and "died once" in first["pool"]["fallback"]["reason"]
    assert first["merge"]["reranked"] and first["rerank"]["by"] == "given"  # the page scored on its own
    reranker = FailsFirst()
    order, token, pages = [], None, []
    while True:
        bundle = _ask(root, reranker, batch_size=4, continuation=token)
        pages.append(bundle)
        order += _ids(bundle)
        token = bundle["continuation"]
        if token is None:
            break
    assert len(pages) > 2 and sorted(order) == sorted(fused) and len(set(order)) == len(order)  # none lost or twice
    assert all(page["pool"]["order"] == "per-page" for page in pages)
    assert all("fallback" not in page["pool"] for page in pages[1:])  # a later call never asks the pool
    # the later calls' requests are their own pages' only (today's path), never the pool's 10 again
    failed = len(reranker.requests[0][1])  # the pool's first request, the one that failed
    assert len(reranker.texts()) == failed + sum(len(page["evidence"]) for page in pages)
    assert all(page["merge"]["reranked"] for page in pages)


# ---- the continuation carries the pool's order (round 2)


def _tree(*roots):
    return {str(path): (path.stat().st_size, path.stat().st_mtime_ns)
            for root in roots for path in Path(root).rglob("*") if path.is_file()}


def test_a_question_with_three_continuations_sends_one_pass_and_writes_nothing(short_project, tmp_path_factory,
                                                                                 monkeypatch):
    root, fused_lists = short_project
    home = tmp_path_factory.mktemp("home")
    monkeypatch.setenv("HOME", str(home))
    _settings(root, {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40, "per_file_first10": 2,
                     "drop_nested": True})
    _ask(root, Reranker())
    total = len(fused_lists[-1]["fused"])
    batch_size = -(-total // 8)  # radius 0: two batches a call, so four calls in all
    reranker = Reranker()
    first = _ask(root, reranker, batch_size=batch_size)
    after_first = list(reranker.requests)
    assert first["pool"]["order"] == "first" and first["pool"]["reranked"] == 40
    assert len(after_first) <= 3 and len(reranker.texts()) == 40  # one pass: three requests of at most 16
    for query, texts in after_first:  # the padded bound on every request
        assert 0 < len(texts) <= rerank_module.MAX_REQUEST_TEXTS
        assert len(texts) * max(len(query) + len(text) for text in texts) <= rerank_module.MAX_REQUEST_CHARS
    before = _tree(root, home)
    token, later = first["continuation"], []
    while token is not None:
        bundle = _ask(root, reranker, batch_size=batch_size, continuation=token)
        later.append(bundle)
        token = bundle["continuation"]
    assert len(later) == 3  # three continuations
    assert reranker.requests == after_first  # not one request more
    assert _tree(root, home) == before  # nothing written by a continuation
    assert all(page["pool"]["order"] == "carried" and page["pool"]["reranked"] == 40 for page in later)
    assert all(page["rerank"]["by"] == "given" and page["merge"]["reranked"] for page in later)
    expected = _pool_order(root, fused_lists[-1]["fused"], _scores_of(root, Reranker()), 40, cap=2)
    order = _ids(first) + [cid for page in later for cid in _ids(page)]
    assert [cid for cid in expected if cid in set(order)] == order  # every page cut from the one order


def test_the_token_s_pool_part_is_bounded(project):
    root, _ = project
    _settings(root, {"rerank_depth": 40})
    token = _ask(root, Reranker(), batch_size=4)["continuation"]
    carried = json.loads(base64.urlsafe_b64decode(token))["p"]
    assert set(carried) == {"h", "o", "b", "d"} and len(carried["h"]) == pool.DIGEST_CHARS
    assert sorted(carried["o"]) == list(range(40))  # 40 positions, no chunk text or id
    _settings(root, None)
    assert "p" not in json.loads(base64.urlsafe_b64decode(_ask(root, Reranker(), batch_size=4)["continuation"]))


def _forged(token, **pool_part):
    payload = json.loads(base64.urlsafe_b64decode(token))
    payload["p"] = {**payload["p"], **pool_part} if pool_part.pop("_keep", True) else pool_part
    return base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()


@pytest.mark.parametrize("change", [{"h": "0" * 16}, {"o": [1, 0] + list(range(2, 39))}, {"o": [0] * 40},
                                    {"o": list(range(41))}, {"o": "0,1"}, {"o": [True] * 40}, {"h": 3}, {"b": None},
                                    {"_keep": False, "h": "0" * 16}])
def test_a_token_whose_pool_does_not_match_the_question_is_refused(project, change):
    root, _ = project
    _settings(root, {"rerank_depth": 40})
    token = _ask(root, Reranker(), batch_size=4)["continuation"]
    forged = _forged(token, **change)
    reranker = Reranker()
    with pytest.raises(GovError) as raised:
        _ask(root, reranker, batch_size=4, continuation=forged)
    assert raised.value.code == "CONTINUATION_INVALID" and not reranker.requests


def test_a_token_from_another_question_or_other_pool_settings_is_refused(project):
    root, _ = project
    _settings(root, {"rerank_depth": 40})
    token = _ask(root, Reranker(), batch_size=4)["continuation"]
    with pytest.raises(GovError) as raised:
        _ask(root, Reranker(), "ledger", batch_size=4, continuation=token)
    assert raised.value.code == "CONTINUATION_INVALID"
    _settings(root, {"rerank_depth": 30})  # another pool: its candidates are not the token's
    with pytest.raises(GovError) as raised:
        _ask(root, Reranker(), batch_size=4, continuation=token)
    assert raised.value.code == "CONTINUATION_INVALID" and "pool" in raised.value.message


# ---- per_file_first10


def _per_file(bundle, first=10):
    counts = {}
    for item in bundle["evidence"][:first]:
        counts[item["path"]] = counts.get(item["path"], 0) + 1
    return counts


@pytest.mark.parametrize("block", [{"per_file_first10": 2}, {"per_file_first10": 2, "rerank_depth": 40}])
def test_per_file_first10_holds_the_first_10_and_keeps_the_rest_after(project, block):
    root, _ = project
    _settings(root, {"rerank_depth": block.get("rerank_depth", 0)} if "rerank_depth" in block else None)
    plain = _ask(root, Reranker())
    assert _per_file(plain)["multi.md"] > 2  # the stand-in scores multi.md's chunks first
    _settings(root, block)
    capped = _ask(root, Reranker())
    assert max(_per_file(capped).values()) <= 2 and sorted(_ids(capped)) == sorted(_ids(plain))
    held_back = [cid for cid in _ids(plain)[:10] if cid not in _ids(capped)[:10]]
    assert held_back and _ids(capped)[10:] == [cid for cid in _ids(plain) if cid not in _ids(capped)[:10]]


@pytest.mark.parametrize("rerank_depth", [0, 40])
def test_per_file_first10_holds_after_the_routing_moved_hits_ahead(project, monkeypatch, rerank_depth):
    """The review's F2: S8's code route moves two more of multi.md's chunks ahead; the cap holds the first 10 after."""
    root, _ = project
    chunks = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root)}
    scores_of = _scores_of(root, Reranker())
    multi = sorted((cid for cid, chunk in chunks.items() if chunk["path"] == "multi.md"), key=lambda c: -scores_of[c])
    lead = multi[2:] + multi[:2]  # the code route's order: its first two are not the two the cap keeps first
    monkeypatch.setattr(retrieve_module.code_route, "route",
                        lambda root_, query, chunks_: ([chunks_[cid] for cid in lead], {"available": True,
                                                                                         "reason": None}))
    monkeypatch.setattr(semantic, "distances", lambda *a, **k: None)  # the code route's own order kept
    routing = {"code_first": 2}
    _settings(root, {"rerank_depth": rerank_depth} if rerank_depth else None, routing)
    uncapped = _ask(root, Reranker())
    assert _ids(uncapped)[:2] == lead[:2] and _per_file(uncapped)["multi.md"] > 2
    _settings(root, {"rerank_depth": rerank_depth, "per_file_first10": 2}, routing)
    bundle = _ask(root, Reranker())
    assert _ids(bundle)[:2] == lead[:2] and bundle["routing"]["code"] == lead[:2]  # the routed hits first
    assert max(_per_file(bundle).values()) <= 2  # and the first 10 held after them
    assert sorted(_ids(bundle)) == sorted(_ids(uncapped))  # none lost


def test_a_pooled_page_the_routing_left_unchanged_keeps_the_pool_s_order(project, monkeypatch):
    """The cap in the pool's order only (the harness's ``_final``): a later page of it is not capped again."""
    root, fused_lists = project
    _settings(root, {"rerank_depth": 40, "per_file_first10": 2})
    pages = _all_pages(root, Reranker(), batch_size=4)
    expected = _pool_order(root, fused_lists[-1]["fused"], _scores_of(root, Reranker()), 40, cap=2)
    assert pages == expected


# ---- drop_nested


def test_drop_nested_leaves_out_an_item_inside_an_earlier_one(project):
    root, _ = project
    _settings(root, None)
    plain = _ask(root, Reranker(), bundle_budget=10 ** 6)
    kept, nested = pool.without_nested(plain["evidence"])
    assert nested  # big.md's section expanded to its parent, then another of its children sent alone
    _settings(root, {"drop_nested": True})
    bundle = _ask(root, Reranker(), bundle_budget=10 ** 6)
    assert bundle["evidence"] == kept
    assert bundle["pool"]["nested"] == [{key: item[key] for key in ("chunk_id", "path", "start_line", "end_line")}
                                        for item in nested]


# ---- v456 together


def test_v456_together_gives_the_harness_s_order(project):
    root, fused_lists = project
    _settings(root, {"meaning_uncut": True, "route_depth": 60, "rerank_depth": 40, "per_file_first10": 2,
                     "drop_nested": True})
    reranker = Reranker()
    bundle = _ask(root, reranker)
    fused = fused_lists[-1]["fused"]
    assert len(fused_lists[-1]["routes"]["lexical"]) > 30
    expected = _pool_order(root, fused, _scores_of(root, Reranker()), 40, cap=2)
    kept, _ = pool.without_nested([item for item in bundle["evidence"]])
    assert _ids(bundle) == [cid for cid in expected if cid in set(_ids(bundle))] and bundle["evidence"] == kept
    assert len(reranker.texts()) == 40 and bundle["pool"]["settings"]["rerank_depth"] == 40
