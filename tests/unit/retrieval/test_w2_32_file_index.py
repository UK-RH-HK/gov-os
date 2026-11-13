"""W2-32, DEC-1068 M1: a file-level index beside the chunk index, behind ``file_level_index`` in ``rebuild.yaml``
(absent: off, today's index and answers). Regression evidence only (DEC-136): the embedder is a stand-in whose
vector counts the word "glaze" in the text, so nearness has a meaning; no model is started. Each store is in a
temporary git repository.
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
from gov.cli.errors import GovError  # noqa: E402
from gov.config import loader, models  # noqa: E402
from gov.retrieval import lexical, semantic  # noqa: E402
from gov.retrieval.retrieve import retrieve  # noqa: E402
from gov.store import STORE_REL  # noqa: E402

PINNED = models.DEFAULT_REVISION + "0" * 52
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
DECOYS = 35  # more than the chunk route's TOP_K of 30, each with a chunk nearer the question than the target's
FILLER = "".join(f"Line {n:02d} of the studio's plain notes on the shelves and the tables.\n" for n in range(20))
TARGET = "# Recipes\nThe celadon batch, mixed wet.\n## Firing\nThe kiln at cone six.\n"


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _settings(root: Path, text: str | None) -> None:
    path = root / "governance/project/rebuild.yaml"
    if text is None:
        path.unlink(missing_ok=True)
    else:
        path.write_text(text)


def _vector(text: str) -> list[float]:
    return [float(min(text.lower().count("glaze"), 3)), 1.0]


@pytest.fixture()
def project(tmp_path, monkeypatch):
    endpoint = {"sent": []}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": PINNED}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 4, "size_vram": 4}]}
        endpoint["sent"] += body["input"]
        return {"embeddings": [_vector(text) for text in body["input"]]}

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic.ollama, "ensure_query_available", lambda: {"available": True})
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None: connection.create_function(
        "vec_distance_cosine", 2, lambda a, b: abs(struct.unpack("2f", a)[0] - struct.unpack("2f", b)[0])))
    monkeypatch.setenv("GOV_VECTOR_CACHE_DIR", str(tmp_path / "machine-cache"))
    root = tmp_path / "repo"
    (root / "governance/project").mkdir(parents=True)
    (root / ".gitignore").write_text(".gov-runtime/\n")
    (root / "governance/project/path-map.yaml").write_text(
        "namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n")
    (root / "open").mkdir()
    for n in range(DECOYS):  # an opening without the word, then a chunk with it once
        (root / f"open/decoy-{n:02d}.md").write_text(FILLER + f"The glaze shelf {n}.\n")
    (root / "open/glaze.md").write_text(TARGET)  # the word in its path alone
    _git(root, "init", "-q", "-b", "main")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c")
    return root, endpoint


def _store_tables(root: Path) -> dict:
    connection = sqlite3.connect(root / STORE_REL)
    try:
        tables = {name for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
        pins = dict(connection.execute("SELECT key, value FROM semantic_pin"))
        vectors = sorted(connection.execute("SELECT chunk_id, embedding FROM semantic_vector"))
    finally:
        connection.close()
    return {"tables": tables, "pins": pins, "vectors": vectors}


# --- the setting -----------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("text, on", [(None, False), ("embed_headers: true\n", False),
                                      ("file_level_index: false\n", False), ("file_level_index: true\n", True)])
def test_the_setting_is_off_unless_written_true(tmp_path, text, on):
    (tmp_path / "governance/project").mkdir(parents=True)
    _settings(tmp_path, text)
    assert loader.index_flag(tmp_path, "file_level_index") is on
    assert semantic.file_level_on(tmp_path) is on


@pytest.mark.parametrize("value", ["yes", "1", "'true'", "on"])
def test_any_other_value_is_refused_by_the_loader_naming_the_key(tmp_path, value):
    (tmp_path / "governance/project").mkdir(parents=True)
    _settings(tmp_path, f"file_level_index: {value}\n")
    for read in (loader.load_config, lambda root: loader.index_flag(root, "file_level_index")):
        with pytest.raises(GovError) as raised:
            read(tmp_path)
        assert raised.value.code == "CONFIG_INVALID"
        assert raised.value.details == {"file": "governance/project/rebuild.yaml", "key": "file_level_index"}


def test_this_repository_does_not_switch_it_on():
    assert semantic.file_level_on(REPO) is False


# --- the index -------------------------------------------------------------------------------------------------------

def test_off_the_store_and_the_embedder_s_input_are_today_s(project):
    root, endpoint = project
    assert semantic.refresh(root)["available"] is True
    state = _store_tables(root)
    assert "semantic_file_vector" not in state["tables"] and semantic.FILE_KEY not in state["pins"]
    assert not any(text.startswith("[path: ") for text in endpoint["sent"])  # only the chunks were sent
    assert semantic.manifest(root)[semantic.FILE_KEY] is False
    assert semantic.file_search(root, "glaze")["reason"] == semantic.FILE_OFF


def test_on_each_embedded_file_gets_one_vector_of_its_path_headings_and_opening(project):
    root, endpoint = project
    _settings(root, "file_level_index: true\n")
    assert semantic.refresh(root)["available"] is True
    assert "[path: open/glaze.md]\n[headings: Recipes | Firing]\n" + TARGET in endpoint["sent"]
    # no heading: the line left out; the opening is the file's first 1,200 characters across its chunks, each line once
    assert f"[path: open/decoy-00.md]\n{FILLER[:semantic.OPENING_CHARS]}" in endpoint["sent"]
    assert len(FILLER) > semantic.OPENING_CHARS and "glaze" not in FILLER
    connection = sqlite3.connect(root / STORE_REL)
    paths = sorted(path for (path,) in connection.execute("SELECT path FROM semantic_file_vector"))
    connection.close()
    assert paths == sorted([*(f"open/decoy-{n:02d}.md" for n in range(DECOYS)), "open/glaze.md"])
    assert semantic.manifest(root)[semantic.FILE_KEY] is True
    assert semantic.search(root, "glaze", refresh=False)["available"] is True


def test_the_file_route_finds_a_file_the_chunk_route_does_not_and_expands_it_to_its_best_chunks(project):
    root, _ = project
    _settings(root, "file_level_index: true\n")
    semantic.refresh(root)
    chunk_route = semantic.search(root, "glaze", refresh=False)["hits"]
    assert len(chunk_route) == semantic.TOP_K and not any(h["path"] == "open/glaze.md" for h in chunk_route)
    files = semantic.file_search(root, "glaze")
    assert files["available"] is True
    first = files["hits"][:semantic.FILE_CHUNKS]
    assert [h["path"] for h in first] == ["open/glaze.md"] * semantic.FILE_CHUNKS
    assert first[0]["file_distance"] == 0.0
    assert len({h["path"] for h in files["hits"]}) == semantic.FILE_TOP
    assert len(files["hits"]) == semantic.FILE_TOP * semantic.FILE_CHUNKS


@pytest.mark.parametrize("first, then", [(None, "file_level_index: true\n"), ("file_level_index: true\n", None)])
def test_switching_marks_the_store_stale_and_the_next_build_rebuilds_the_file_vectors_alone(project, first, then):
    root, endpoint = project
    _settings(root, first)
    semantic.refresh(root)
    chunks_before = _store_tables(root)["vectors"]
    _settings(root, then)
    assert semantic.search(root, "glaze", refresh=False)["reason"] == "stale"
    endpoint["sent"].clear()
    assert semantic.refresh(root)["available"] is True
    assert _store_tables(root)["vectors"] == chunks_before  # the chunk vectors untouched
    sent_files = [text for text in endpoint["sent"] if text.startswith("[path: ")]
    assert len(sent_files) == (DECOYS + 1 if then else 0) and len(endpoint["sent"]) == len(sent_files)
    assert ("semantic_file_vector" in _store_tables(root)["tables"]) is bool(then)
    assert semantic.search(root, "glaze", refresh=False)["available"] is True


def test_a_changed_file_has_its_file_vector_made_again_and_no_other(project):
    root, endpoint = project
    _settings(root, "file_level_index: true\n")
    semantic.refresh(root)
    (root / "open/glaze.md").write_text(TARGET + "## Cooling\nSlowly.\n")
    _git(root, "commit", "-qam", "changed")
    endpoint["sent"].clear()
    semantic.refresh(root)
    files = [text for text in endpoint["sent"] if text.startswith("[path: ")]
    assert files == ["[path: open/glaze.md]\n[headings: Recipes | Firing | Cooling]\n" + TARGET + "## Cooling\nSlowly.\n"]


def test_a_refused_setting_refuses_the_build_and_the_search_by_name(project):
    root, endpoint = project
    semantic.refresh(root)
    endpoint["sent"].clear()
    _settings(root, "file_level_index: yes\n")
    for report in (semantic.refresh(root), semantic.search(root, "glaze", refresh=False),
                   semantic.file_search(root, "glaze")):
        assert report["available"] is False and report["error"] == "CONFIG_INVALID"
    assert endpoint["sent"] == []


# --- retrieve: the file route fused beside the others ---------------------------------------------------------------

needs_gitleaks = pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")


@pytest.fixture()
def repository(tmp_path, monkeypatch):
    root = tmp_path
    (root / "governance/project").mkdir(parents=True)
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    (root / "governance/project/path-map.yaml").write_text(yaml.safe_dump(path_map), encoding="utf-8")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    (root / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    (root / "kiln.md").write_text("# Kiln\n\nThe kiln is fired at cone six.\n", encoding="utf-8")
    (root / "studio.md").write_text("# Studio\n\nThe studio opens at nine.\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "fixture")
    lexical.refresh(root)
    store.load(root)
    asked = []
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": True, "reason": None, "hits": []})
    studio = next(c for c in lexical.chunks(root) if c["path"] == "studio.md")

    def files(root, query, refresh=False):
        asked.append(query)
        return {"available": True, "reason": None, "hits": [{**studio, "distance": 0.0, "file_distance": 0.0}]}

    monkeypatch.setattr(semantic, "file_search", files)
    return root, asked, studio


@needs_gitleaks
def test_retrieve_asks_no_file_route_with_the_setting_off(repository):
    root, asked, _ = repository
    bundle = retrieve(root, "kiln", reranker=lambda: None)
    assert asked == [] and semantic.FILE_FACET not in bundle["facets"]


@needs_gitleaks
def test_retrieve_fuses_the_file_route_s_hits_with_the_setting_on(repository):
    root, asked, studio = repository
    _settings(root, "file_level_index: true\n")
    bundle = retrieve(root, "kiln", reranker=lambda: None)
    assert asked == ["kiln"] and bundle["facets"][semantic.FILE_FACET] == {"available": True, "reason": None}
    assert studio["chunk_id"] in {item["chunk_id"] for item in bundle["evidence"]}  # reached by the file route alone
