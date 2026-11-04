"""W2-32 S7 (G1, DEC-1066): the models read the whole chunk, and parent expansion keeps its expanded parents across
continuations, so no span is sent twice. Regression evidence only (DEC-136): the embedder, the reranker and the
semantic route are stand-ins; no model is started. Each store is in a temporary git repository.
"""
from __future__ import annotations

import shutil
import sqlite3
import struct
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import store  # noqa: E402
from gov.config import models  # noqa: E402
from gov.retrieval import chunking, fusion, lexical, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
LONG = "".join(f"line {n:02d} of the kiln notes, firing order and glaze.\n" for n in range(21))  # about 1,100
TAIL = "the apprentice fires the bowls\n"  # past character 1,000 of its chunk, as Q10's gold is


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def test_each_model_reads_the_whole_chunk_up_to_its_own_named_limit():
    # the reranker: up to one request's size bound (DEC-1067 (f)), above the chunker's MAX_CHARS
    from gov.retrieval import rerank
    assert fusion.RERANK_CHARS == fusion.RERANK_LIMIT_CHARS == rerank.MAX_REQUEST_CHARS == 24_000
    assert chunking.READ_CHARS > 24575 > fusion.RERANK_LIMIT_CHARS > chunking.MAX_CHARS
    # the embedder: within its server's 4,096-token context with margin (DEC-1067; review F-4)
    assert semantic.EMBED_CHARS == semantic.EMBED_LIMIT_CHARS == 10_000 >= chunking.MAX_CHARS


# --- the embedder ----------------------------------------------------------------------------------------------------

@pytest.fixture()
def project(tmp_path, monkeypatch):
    endpoint = {"sent": []}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": PINNED}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 4, "size_vram": 4}]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [[float(len(text)), 1.0] for text in body["input"]]}

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: connection.create_function(
        "vec_distance_cosine", 2, lambda a, b: abs(struct.unpack("2f", a)[0] - struct.unpack("2f", b)[0])))
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))
    root = tmp_path / "repo"
    (root / "governance/project").mkdir(parents=True)
    (root / ".gitignore").write_text(".gov-runtime/\n")
    (root / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n")
    (root / "open").mkdir()
    (root / "open/kiln.md").write_text(LONG + TAIL)
    (root / "open/line.md").write_text("x" * 3000 + "\n")  # one line, longer than MAX_CHARS
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c")
    return root, endpoint


def test_the_embedder_reads_each_chunk_whole(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    texts = {chunk["chunk_id"]: chunk for chunk in lexical.chunks(root) if chunk["path"].startswith("open/")}
    whole = [(root / c["path"]).read_text().splitlines(keepends=True)[c["start_line"] - 1:c["end_line"]]
             for c in texts.values()]
    assert sorted(endpoint["sent"]) == sorted("".join(lines) for lines in whole)
    assert any(TAIL in text and len(text) > 1000 for text in endpoint["sent"])
    assert "x" * 3000 + "\n" in endpoint["sent"]
    assert semantic.manifest(root)["embed_chars"] == semantic.EMBED_LIMIT_CHARS


def test_a_store_built_under_the_old_cut_is_stale_and_embedded_again_in_full(project):
    root, endpoint = project
    semantic.refresh(root)
    connection = sqlite3.connect(root / STORE_REL)
    connection.execute("UPDATE semantic_pin SET value = '512' WHERE key = ?", (semantic.CUT_KEY,))
    connection.commit()
    connection.close()
    assert semantic.search(root, "kiln", refresh=False)["reason"] == "stale"
    endpoint["sent"].clear()
    report = semantic.refresh(root)
    assert report["available"] is True
    embedded = [chunk for chunk in lexical.chunks(root) if chunk["path"].startswith("open/")]
    # every chunk again (S1's full re-embed): sent, or served by W2-126's cache, as the texts are the same here
    assert len(endpoint["sent"]) + report["vector_cache"]["hits"] == len(embedded) == 2  # kiln.md, line.md


# --- the reranker ----------------------------------------------------------------------------------------------------

def test_the_reranker_reads_each_chunk_whole_in_the_fusion(monkeypatch):
    text = LONG + TAIL
    hits = [{"chunk_id": "a", "path": "open/kiln.md", "start_line": 1, "end_line": 22, "parent_id": "p"}]
    seen = []
    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": hits})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": False, "hits": []})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": text} for hit in fused])
    fusion.search(Path("unused"), "who fires the bowls", limit=None,
                  reranker=lambda: lambda query, texts: seen.extend(texts) or [1.0] * len(texts))
    assert seen == [f"[path: open/kiln.md]\n{text}"] and TAIL in seen[0]


# --- retrieve: the whole chunk, and no parent sent twice across continuations ---------------------------------------

needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
PHRASE = "heron ledger"


@pytest.fixture()
def repository(tmp_path, monkeypatch):
    """One long section that holds the phrase in its first and its last chunk, so two children of one parent."""
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    filler = "".join(f"Line {n:03d} of a long section, kept to fill several chunks of text.\n" for n in range(60))
    (root / "long.md").write_text(f"# Long\n\nThe {PHRASE} opens.\n{filler}The {PHRASE} closes.\n", encoding="utf-8")
    for number in (1, 2, 3):  # short notes rank first, so the long section's two chunks come in different calls
        (root / f"note{number}.md").write_text(f"# Note {number}\n\nThe {PHRASE} of pier {number}.\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    lexical.refresh(root)
    store.load(root)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return root


def _calls(root, reranker=lambda: None, budget=1_000_000):
    bundles, token = [], None
    while True:
        bundle = retrieve(root, PHRASE, batch_size=1, radius=0, bundle_budget=budget, continuation=token,
                          reranker=reranker)
        bundles.append(bundle)
        token = bundle["continuation"]
        if token is None or len(bundles) > 10:
            return bundles


@needs_gitleaks
def test_a_parent_expanded_in_one_call_is_not_sent_again_by_a_later_one(repository):
    bundles = _calls(repository)
    calls_of_long = [n for n, b in enumerate(bundles) for item in [*b["evidence"], *b["repeats"]]
                     if item["path"] == "long.md"]
    assert len(set(calls_of_long)) == 2, f"the two children are not in two calls: {calls_of_long}"
    sent = [(item["path"], item["start_line"], item["end_line"]) for b in bundles for item in b["evidence"]]
    assert len(sent) == len(set(sent)), f"a span came back in a later call: {sent}"
    expanded = [entry["parent_id"] for b in bundles for entry in b["expansions"]]
    assert len(expanded) == len(set(expanded)) == 1  # the one parent, expanded once across the calls
    # a span inside one an earlier call sent is a repeat too: it is not sent, and is named
    for n, bundle in enumerate(bundles):
        earlier = [(i["path"], i["start_line"], i["end_line"]) for b in bundles[:n] for i in b["evidence"]]
        for item in bundle["evidence"]:
            assert not any(path == item["path"] and first <= item["start_line"] and item["end_line"] <= last
                           for path, first, last in earlier), f"call {n + 1} sends {item['path']}:" \
                f"{item['start_line']}-{item['end_line']}, within a span sent earlier"
    repeats = [item for b in bundles for item in b["repeats"]]
    assert [item["path"] for item in repeats] == ["long.md"] and repeats[0]["parent_id"] == expanded[0]


@needs_gitleaks
def test_a_token_from_before_s7_is_still_read(repository):
    import base64
    import json
    tokens = [b["continuation"] for b in _calls(repository) if b["continuation"]]
    payloads = [json.loads(base64.urlsafe_b64decode(token)) for token in tokens]
    assert any(p["x"] for p in payloads)  # the expanded parent is carried
    payload = next(p for p in payloads if p["x"])
    del payload["x"]
    old = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode()
    assert retrieve(repository, PHRASE, batch_size=1, bundle_budget=1_000_000, continuation=old,
                    reranker=lambda: None)["evidence"]


@needs_gitleaks
def test_the_reranker_reads_the_whole_chunk_in_retrieve(repository):
    seen = []
    retrieve(repository, PHRASE, bundle_budget=1_000_000,
             reranker=lambda: lambda query, texts: seen.extend(texts) or [1.0] * len(texts))
    chunks = {(c["start_line"], c["end_line"]) for c in lexical.chunks(repository, "long.md")}
    lines = (repository / "long.md").read_text().splitlines(keepends=True)
    wanted = {f"[path: long.md]\n{''.join(lines[a - 1:b])}" for a, b in chunks}
    long = [text for text in seen if text.startswith("[path: long.md]")]
    assert long and set(long) <= wanted and any(len(text) > 600 for text in long)


# --- DEC-1067: the embedder's limit named, the reranker's requests capped, no span sent twice either way ----------

def test_a_chunk_above_the_embedder_s_limit_is_embedded_from_its_first_part_and_named(project, capsys):
    root, endpoint = project
    (root / "open/huge.md").write_text("y" * 12_000 + "\n")  # one line above EMBED_LIMIT_CHARS
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "huge")
    report = semantic.refresh(root)
    assert report["available"] is True
    assert "y" * semantic.EMBED_LIMIT_CHARS in endpoint["sent"]  # its first part, never silently longer
    assert not any(len(text) > semantic.EMBED_LIMIT_CHARS for text in endpoint["sent"])
    assert "x" * 3000 + "\n" in endpoint["sent"]  # a chunk under the limit is still sent whole
    assert report["cut"] == {"limit": 10_000, "count": 1, "paths": ["open/huge.md"]}
    assert "open/huge.md" in capsys.readouterr().err


def test_no_chunk_over_the_limit_is_reported_as_none(project):
    root, _ = project
    assert semantic.refresh(root)["cut"] == {"limit": 10_000, "count": 0, "paths": []}


@pytest.mark.parametrize("pool", [1, 15, 16, 17, 30, 33, 100])
def test_no_request_to_the_reranker_carries_more_than_16_texts(pool):
    from gov.retrieval import rerank
    sizes = []

    def score(query, texts):
        sizes.append(len(texts))
        return [float(text) for text in texts]  # the text is its own score

    given = [{"chunk_id": str(n), "text": str(n)} for n in range(pool)]
    ranked = rerank.rerank("q", given, lambda: score)
    assert rerank.MAX_REQUEST_TEXTS == 16 and all(size <= 16 for size in sizes) and sum(sizes) == pool
    assert len(sizes) == -(-pool // 16)
    assert [c["chunk_id"] for c in ranked] == [str(n) for n in reversed(range(pool))]  # combined in order
    assert [c["rerank_score"] for c in ranked] == [float(n) for n in reversed(range(pool))]


def test_the_shared_service_is_asked_at_most_16_texts_at_a_time(tmp_path, monkeypatch):
    from gov.retrieval import rerank
    interpreter = tmp_path / rerank.PYTHON_REL
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text("")
    monkeypatch.setenv("HOME", str(tmp_path))
    asked = []
    monkeypatch.setattr(rerank, "_ask", lambda interpreter, query, texts: asked.append(len(texts))
                        or ([1.0] * len(texts), "cuda:0"))
    rerank.rerank("q", [{"chunk_id": str(n), "text": str(n)} for n in range(40)])
    assert asked == [16, 16, 8] and rerank.last_outcome()["by"] == "service"


def test_one_batch_that_fails_leaves_every_candidate_unscored():
    from gov.retrieval import rerank
    calls = []

    def score(query, texts):
        calls.append(len(texts))
        if len(calls) == 2:
            raise BrokenPipeError("the reranker died")
        return [1.0] * len(texts)

    given = [{"chunk_id": str(n), "text": str(n)} for n in range(20)]
    assert rerank.rerank("q", given, lambda: score) == given and rerank.last_outcome()["by"] == "unavailable"


@needs_gitleaks
def test_a_later_parent_leaves_out_the_lines_an_earlier_call_sent_as_a_child(repository):
    """Review F-5 (DEC-1067 order (2)): the other direction. The long section's first child goes alone in call 2
    (the budget holds no expansion there), and its parent is expanded in call 3 without that child's lines."""
    from gov.retrieval.retrieve import _tokens
    dry = _calls(repository, budget=0)  # no expansion: which child of the long section goes first
    order = [item for b in dry for item in b["evidence"] if item["path"] == "long.md"]
    assert len(order) == 2 and order[0]["chunk_id"] != order[1]["chunk_id"]
    first, later = order
    parent = lexical.parent(repository, lexical.chunks(repository, "long.md")[0]["parent_id"])
    lines = (repository / "long.md").read_text().splitlines(keepends=True)

    def size(a, b):
        return _tokens("".join(lines[a - 1:b]))

    whole = size(parent["start_line"], parent["end_line"])
    runs = [(parent["start_line"], first["start_line"] - 1), (first["end_line"] + 1, parent["end_line"])]
    budget = sum(size(a, b) for a, b in runs if a <= b)  # the later child widened to the parent less the first
    assert budget < whole  # so the first child, with its parent whole, does not fit
    bundles = _calls(repository, budget=budget)
    expansions = [e for b in bundles for e in b["expansions"]]
    assert len(expansions) == 1 and expansions[0]["chunk_id"] == later["chunk_id"]
    assert expansions[0]["left_out"] == [[first["start_line"], first["end_line"]]]
    seen = {}
    for n, bundle in enumerate(bundles):
        for item in bundle["evidence"]:
            for line in range(item["start_line"], item["end_line"] + 1):
                assert (item["path"], line) not in seen, \
                    f"{item['path']}:{line} sent in calls {seen.get((item['path'], line))} and {n + 1}"
                seen[(item["path"], line)] = n + 1
    held = {line for (path, line) in seen if path == "long.md"}
    assert held == set(range(parent["start_line"], parent["end_line"] + 1))  # every line of the parent, once


@needs_gitleaks
def test_a_token_from_before_dec_1067_without_its_children_is_still_read(repository):
    import base64
    import json
    tokens = [b["continuation"] for b in _calls(repository) if b["continuation"]]
    payload = json.loads(base64.urlsafe_b64decode(tokens[-1]))
    assert "c" in payload
    del payload["c"]
    old = base64.urlsafe_b64encode(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()).decode()
    assert retrieve(repository, PHRASE, batch_size=1, bundle_budget=1_000_000, continuation=old,
                    reranker=lambda: None) is not None


# --- the left-out lines named once (the CTO's red after 82dcb360) ---------------------------------------------------

@pytest.mark.parametrize("spans, merged", [
    ([(16, 31), (30, 45)], [(16, 45)]),  # neighbouring chunks share their overlap lines: one run, each line once
    ([(16, 29), (30, 45)], [(16, 29), (30, 45)]),  # a child that ends one line before the next begins: both, as sent
    ([(30, 45), (16, 31)], [(16, 45)]),  # in any order
    ([(10, 40), (12, 20)], [(10, 40)]),  # one inside another
    ([], []),
])
def test_the_left_out_spans_name_each_line_once(spans, merged):
    from gov.retrieval.retrieve import _merged
    assert _merged(spans) == merged


@pytest.fixture()
def almanac(tmp_path, monkeypatch):
    """A section of three overlapping chunks, the phrase in each, and four short notes that rank first."""
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (root / "docs").mkdir()
    body = "".join(f"Line {n:02d}: the {PHRASE} entry.\n" if n % 7 == 0 else
                   f"Line {n:02d} of plain filler prose in the almanac section text.\n" for n in range(45))
    (root / "docs/almanac.md").write_text("# Almanac\n" + body, encoding="utf-8")
    for number in range(4):
        (root / f"docs/note{number}.md").write_text(f"# Note {number}\n\nThe {PHRASE} of pier {number}.\n",
                                                    encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    lexical.refresh(root)
    store.load(root)
    monkeypatch.setattr(semantic, "search", lambda *_args, **_kwargs: {"available": True, "reason": None, "hits": []})
    return root


@needs_gitleaks
def test_overlapping_children_sent_earlier_are_left_out_of_a_later_parent_as_one_run(almanac):
    chunks = [(c["start_line"], c["end_line"]) for c in lexical.chunks(almanac, "docs/almanac.md")]
    assert len(chunks) == 3 and chunks[0][1] >= chunks[1][0]  # the chunker's overlap: neighbours share lines
    bundles = _calls(almanac, budget=300)  # no expansion fits until the last child's turn
    expansions = [e for b in bundles for e in b["expansions"]]
    assert len(expansions) == 1
    left_out = expansions[0]["left_out"]
    earlier = [(i["start_line"], i["end_line"]) for b in bundles[:-1] for i in b["evidence"]
               if i["path"] == "docs/almanac.md"]
    assert sorted(earlier) == chunks[:2]  # the two children sent alone, each its own lines
    assert left_out == [[chunks[0][0], chunks[1][1]]]  # one run: every line they sent, each named once
    named = [line for first, last in left_out for line in range(first, last + 1)]
    assert len(named) == len(set(named))
    later = [line for i in bundles[-1]["evidence"] if i["path"] == "docs/almanac.md"
             for line in range(i["start_line"], i["end_line"] + 1)]
    assert later and not set(later) & set(named)  # nothing left out is sent again
    assert set(later) | set(named) == set(range(1, chunks[-1][1] + 1))  # the parent whole, across the calls


RECORD = frozenset({"chunk_id", "path", "start_line", "end_line", "parent_id", "reason"})  # a span left out, named


@needs_gitleaks
def test_the_converse_direction_s_left_out_spans_are_span_records_as_the_first_direction_s(almanac):
    """The CTO's red after 28a3f5e9: each span an earlier call sent as a child, left out of a later parent, is named
    in ``repeats`` as a record of its own (path, lines, reason), exactly as a chunk left out for lying inside an
    earlier parent is (the next case), outside the evidence and the expansion records."""
    from gov.retrieval.retrieve import EARLIER_CHILD
    bundles = _calls(almanac, budget=300)
    earlier = [i for b in bundles[:-1] for i in b["evidence"] if i["path"] == "docs/almanac.md"]
    converse = [r for b in bundles for r in b["repeats"] if r["reason"] == EARLIER_CHILD]
    named = sorted((r["path"], r["start_line"], r["end_line"]) for r in converse)
    assert named == sorted((i["path"], i["start_line"], i["end_line"]) for i in earlier)  # one each, as sent
    assert {r["chunk_id"] for r in converse} == {i["chunk_id"] for i in earlier}
    expansion = [e for b in bundles for e in b["expansions"]][0]
    assert all(r["parent_id"] == expansion["parent_id"] and frozenset(r) == RECORD for r in converse)
    later = {(i["path"], i["start_line"], i["end_line"]) for i in bundles[-1]["evidence"]}
    assert not later & set(named)  # named, not sent


@needs_gitleaks
def test_the_first_direction_s_spans_are_span_records_of_the_same_form(repository):
    from gov.retrieval.retrieve import IN_EARLIER_PARENT
    first = [r for b in _calls(repository) for r in b["repeats"]]
    assert first and all(r["reason"] == IN_EARLIER_PARENT and frozenset(r) == RECORD for r in first)



# --- DEC-1067 (f): the size bound on every request, beside the count -------------------------------------------------

def _recorder(log):
    def score(query, texts):
        log.append((len(texts), sum(len(query) + len(text) for text in texts)))
        return [float(len(text)) for text in texts]  # longer is better: the unbatched order is known
    return score


@pytest.mark.parametrize("lengths", [[100] * 40, [9_000] * 5, [5_000, 20_000, 3_000, 23_000, 1_000],
                                     [23_990, 23_990], [40_000], [1] * 3])
def test_no_request_is_above_16_texts_or_24000_characters_and_the_order_is_the_unbatched_one(lengths):
    from gov.retrieval import rerank
    query, log = "who fires the bowls", []
    given = [{"chunk_id": str(n), "text": "x" * length} for n, length in enumerate(lengths)]
    ranked = rerank.rerank(query, given, lambda: _recorder(log))
    assert all(texts <= 16 and chars <= rerank.MAX_REQUEST_CHARS for texts, chars in log)
    assert sum(texts for texts, _ in log) == len(lengths)
    room = rerank.MAX_REQUEST_CHARS - len(query)
    expected = sorted(range(len(lengths)), key=lambda n: -min(lengths[n], room))  # one request, as if unbatched
    assert [c["chunk_id"] for c in ranked] == [str(n) for n in expected]


def test_a_pool_is_split_into_the_fewest_requests_meeting_both_bounds():
    from gov.retrieval import rerank
    query = "q" * 10
    pairs = lambda lengths: [(last - first, sum(len(query) + n for n in lengths[first:last]))  # noqa: E731
                             for first, last, _ in rerank.requests(query, ["x" * n for n in lengths])]
    assert pairs([100] * 40) == [(16, 1760), (16, 1760), (8, 880)]  # the count binds
    assert pairs([9_000] * 5) == [(2, 18020), (2, 18020), (1, 9010)]  # the size binds
    assert pairs([5_000, 20_000, 3_000]) == [(1, 5010), (2, 23020)]
    assert pairs([]) == []


def test_one_chunk_above_the_budget_is_read_up_to_it():
    from gov.retrieval import rerank
    query = "who fires the bowls"
    [(first, last, texts)] = rerank.requests(query, ["y" * 40_000])
    assert (first, last) == (0, 1) and len(query) + len(texts[0]) == rerank.MAX_REQUEST_CHARS


def test_the_shared_service_and_a_private_reranker_are_each_asked_within_both_bounds(tmp_path, monkeypatch):
    import functools
    from gov.retrieval import rerank
    interpreter = tmp_path / rerank.PYTHON_REL
    interpreter.parent.mkdir(parents=True)
    interpreter.write_text("")
    monkeypatch.setenv("HOME", str(tmp_path))
    service, private = [], []

    def ask(interpreter, query, texts):
        service.append(sum(len(query) + len(text) for text in texts))
        if len(service) > 1:
            raise TimeoutError("timed out")  # the second request falls back to the private reranker
        return [1.0] * len(texts), "cuda:0"

    @functools.lru_cache(maxsize=None)
    def started(interpreter):
        return (lambda query, texts: private.append(sum(len(query) + len(t) for t in texts)) or [2.0] * len(texts)), \
            "cuda:0", None

    monkeypatch.setattr(rerank, "_ask", ask)
    monkeypatch.setattr(rerank, "_started", started)
    rerank.rerank("q", [{"chunk_id": str(n), "text": "z" * 9_000} for n in range(6)])
    assert service and private and all(chars <= rerank.MAX_REQUEST_CHARS for chars in service + private)


def test_the_fusion_reads_a_chunk_up_to_the_budget(monkeypatch):
    hits = [{"chunk_id": "a", "path": "open/huge.md", "start_line": 1, "end_line": 1, "parent_id": "p"}]
    seen = []
    monkeypatch.setattr(fusion.lexical, "search", lambda root, query, refresh: {"available": True, "hits": hits})
    monkeypatch.setattr(fusion.semantic, "search", lambda root, query, refresh: {"available": False, "hits": []})
    monkeypatch.setattr(fusion, "_records", lambda root, fused: [{**hit, "text": "w" * 30_000} for hit in fused])
    fusion.search(Path("unused"), "q", limit=None,
                  reranker=lambda: lambda query, texts: seen.extend(texts) or [1.0] * len(texts))
    assert len(seen) == 1 and len("q") + len(seen[0]) <= 24_000
