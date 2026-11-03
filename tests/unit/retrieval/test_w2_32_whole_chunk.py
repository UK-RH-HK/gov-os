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


def test_the_cut_is_above_every_chunk_the_chunker_makes():
    assert semantic.EMBED_CHARS == fusion.RERANK_CHARS == chunking.READ_CHARS >= chunking.MAX_CHARS
    assert chunking.READ_CHARS > 24575  # this repository's longest one-line chunk


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
    assert semantic.manifest(root)["embed_chars"] == chunking.READ_CHARS


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


def _calls(root, reranker=lambda: None):
    bundles, token = [], None
    while True:
        bundle = retrieve(root, PHRASE, batch_size=1, radius=0, bundle_budget=1_000_000, continuation=token,
                          reranker=reranker)
        bundles.append(bundle)
        token = bundle["continuation"]
        if token is None or len(bundles) > 10:
            return bundles


@needs_gitleaks
def test_a_parent_expanded_in_one_call_is_not_sent_again_by_a_later_one(repository):
    bundles = _calls(repository)
    calls_of_long = [n for n, b in enumerate(bundles) for item in b["evidence"] if item["path"] == "long.md"]
    assert len(set(calls_of_long)) == 2, f"the two children are not in two calls: {calls_of_long}"
    sent = [(item["path"], item["start_line"], item["end_line"]) for b in bundles for item in b["evidence"]]
    assert len(sent) == len(set(sent)), f"a span came back in a later call: {sent}"
    expanded = [entry["parent_id"] for b in bundles for entry in b["expansions"]]
    assert len(expanded) == len(set(expanded)) == 1  # the one parent, expanded once across the calls


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
