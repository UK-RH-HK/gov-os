"""W2-32 S8 (G3, DEC-1067 (a)): routing by question type. A question that names a symbol has the code route's first
hits ahead after the rerank; a question that names a record has that record's best chunks ahead; each half behind
its own setting in ``governance/project/retrieval.yaml``, both off by default (today's order, byte for byte).

Regression evidence only (DEC-136): the store is real (a temporary repository); the record route, the closure, the
code route and the code route's distances are stand-ins, so each case says what the question names; the reranker
is given (it ranks the notes highest, so a move ahead shows); the semantic route is unavailable. No model starts.
"""
from __future__ import annotations

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
from gov.retrieval import lexical, retrieve as retrieve_module, routing, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
PHRASE = "heron ledger"
RECORD = "DAEO-rout"
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
CODE = "".join(f"def step_{n}():  # the {PHRASE} step {n}\n    return {n}\n\n\n" for n in range(4))
SECTIONS = "".join(f"## Part {n}\n\nThe {PHRASE}, part {n} of the record.\n\n" for n in range(4))


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


@pytest.fixture()
def project(tmp_path, monkeypatch):
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (root / "src").mkdir()
    (root / "src/steps.py").write_text(CODE, encoding="utf-8")
    (root / "rec.md").write_text(f"# The record\n\n{SECTIONS}", encoding="utf-8")
    for number in range(3):
        (root / f"note{number}.md").write_text(f"# Note {number}\n\nThe {PHRASE} of pier {number}.\n")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    lexical.refresh(root)
    store.load(root)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": False, "reason": "off", "hits": []})
    chunks = lexical.chunks(root)
    code = [c for c in chunks if c["path"] == "src/steps.py"]
    record = [c for c in chunks if c["path"] == "rec.md"]
    assert len(code) >= 3 and len(record) >= 3
    state = {"symbol": False, "record": False, "distance": {}}

    def code_route(root_, query, chunks_):
        if not state["symbol"]:
            return None  # the question names no symbol
        return [{**c, "routes": ["code"]} for c in code], {"available": True, "reason": None}

    real_graph = retrieve_module._graph

    def graph(root_):
        record_of, not_current, types = real_graph(root_)
        return {**record_of, "rec.md": RECORD}, not_current, {**types, RECORD: "ticket"}

    monkeypatch.setattr(retrieve_module.code_route, "route", code_route)
    monkeypatch.setattr(retrieve_module.graph_route, "start_ids",
                        lambda root_, query, known: [RECORD] if state["record"] else [])
    monkeypatch.setattr(retrieve_module.closures, "closure",
                        lambda root_, start, depth: {"closure": [{"id": RECORD}], "facets": {"code": "ok"}, "gaps": []})
    monkeypatch.setattr(retrieve_module, "_graph", graph)
    monkeypatch.setattr(semantic, "distances", lambda root_, query, ids: dict(state["distance"]) or None)
    return root, code, record, state


def _score(query, texts):
    """The notes first, then the record's sections by part number (higher better), then the code by step (lower)."""
    def one(text):
        head = text.splitlines()[0]
        if "note" in head:
            return 100.0
        if "rec.md" in head:
            return 50.0 + max((float(w) for w in text.replace(",", " ").split() if w.isdigit()), default=0.0)
        return 10.0 - float(text.split("step_")[1][0]) if "step_" in text else 0.0
    return [one(text) for text in texts]


def _ask(root, **settings):
    path = root / "governance/project/retrieval.yaml"
    if settings:
        path.write_text(yaml.safe_dump({"routing": settings}), encoding="utf-8")
    elif path.exists():
        path.unlink()
    return retrieve(root, PHRASE, batch_size=30, bundle_budget=0, reranker=lambda: _score)


def _order(bundle):
    return [item["chunk_id"] for item in bundle["evidence"]]


def test_off_is_today_s_order_byte_for_byte(project):
    root, code, record, state = project
    state.update(symbol=True, record=True, distance={c["chunk_id"]: n for n, c in enumerate(reversed(code))})
    before = json.dumps(_ask(root), sort_keys=True)
    assert json.dumps(_ask(root, code_first=0, named_first=0), sort_keys=True) == before
    assert "routing" not in json.loads(before)


def test_a_question_naming_a_symbol_has_the_code_route_s_first_2_ahead_by_cosine(project):
    root, code, record, state = project
    state.update(symbol=True, distance={c["chunk_id"]: n for n, c in enumerate(reversed(code))})  # the last nearest
    base = _order(_ask(root))
    bundle = _ask(root, code_first=2)
    expected = [code[-1]["chunk_id"], code[-2]["chunk_id"]]
    assert _order(bundle)[:2] == expected and bundle["routing"] == {"code": expected}
    assert _order(bundle)[2:] == [cid for cid in base if cid not in expected]  # the rest in the rerank's order


def test_with_no_vector_the_code_route_keeps_its_own_order(project):
    root, code, record, state = project
    state.update(symbol=True, distance={})
    assert _order(_ask(root, code_first=2))[:2] == [code[0]["chunk_id"], code[1]["chunk_id"]]


def test_a_question_naming_no_symbol_is_left_as_it_is(project):
    root, code, record, state = project
    base = _order(_ask(root))
    bundle = _ask(root, code_first=2)
    assert _order(bundle) == base and bundle["routing"] == {"code": []}


def test_a_question_naming_a_record_has_its_2_best_chunks_ahead_by_the_reranker(project):
    root, code, record, state = project
    state.update(record=True)
    base = _order(_ask(root))
    bundle = _ask(root, named_first=2)
    scores = dict(zip([c["chunk_id"] for c in record],
                      _score("q", [f"[path: rec.md]\n{lexical_text(root, c)}" for c in record])))
    expected = sorted(scores, key=lambda cid: -scores[cid])[:2]
    assert _order(bundle)[:2] == expected and bundle["routing"] == {"named": expected}
    assert _order(bundle)[2:] == [cid for cid in base if cid not in expected]


def test_a_question_naming_no_record_is_left_as_it_is(project):
    root, code, record, state = project
    base = _order(_ask(root))
    assert _order(_ask(root, named_first=2)) == base


def test_a_question_naming_both_has_the_code_route_s_first_then_the_record_s(project):
    root, code, record, state = project
    state.update(symbol=True, record=True, distance={c["chunk_id"]: n for n, c in enumerate(code)})
    bundle = _ask(root, code_first=2, named_first=2)
    order = _order(bundle)
    assert order[:2] == [code[0]["chunk_id"], code[1]["chunk_id"]]
    assert order[2:4] == bundle["routing"]["named"] and len(bundle["routing"]["named"]) == 2
    assert all(cid in {c["chunk_id"] for c in record} for cid in order[2:4])


@pytest.mark.parametrize("text, key", [("routing: {code_first: -1}\n", "routing.code_first"),
                                       ("routing: {named_first: two}\n", "routing.named_first"),
                                       ("routing: {named_first: true}\n", "routing.named_first"),
                                       ("routing: {front: 2}\n", "routing.front"),
                                       ("fusion: {k: 60}\n", "fusion")])
def test_an_invalid_setting_is_config_invalid_naming_the_key(tmp_path, text, key):
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/retrieval.yaml").write_text(text, encoding="utf-8")
    with pytest.raises(GovError) as raised:
        routing.settings(tmp_path)
    assert raised.value.code == "CONFIG_INVALID" and raised.value.details["key"] == key


def test_no_file_or_an_empty_one_is_off(tmp_path):
    assert routing.settings(tmp_path) == {"code_first": 0, "named_first": 0}
    (tmp_path / "governance/project").mkdir(parents=True)
    (tmp_path / "governance/project/retrieval.yaml").write_text("# nothing yet\n", encoding="utf-8")
    assert routing.settings(tmp_path) == {"code_first": 0, "named_first": 0}


def test_a_route_s_first_are_cut_before_the_page_is_looked_at():
    page = [{"chunk_id": cid} for cid in ("a", "b", "c")]
    assert routing.firsts(["z", "c", "b"], 2) == ["z", "c"]
    moved, ids = routing.ahead(page, routing.firsts(["z", "c", "b"], 2))
    assert [c["chunk_id"] for c in moved] == ["c", "a", "b"] and ids == ["c"]  # z is not on the page; b is not 2nd


def lexical_text(root, chunk):
    lines = (Path(root) / chunk["path"]).read_text().splitlines(keepends=True)
    return "".join(lines[chunk["start_line"] - 1:chunk["end_line"]])
