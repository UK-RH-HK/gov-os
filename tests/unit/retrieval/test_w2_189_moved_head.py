"""W2-189 (DAEO-kfn1): ``gov retrieve`` answers from the last good store when HEAD has moved past the store's commit,
leaves out the chunks of the tracked paths that changed since, and names the store's commit, the head and those paths
(DEC-1197 (2)(i), DEC-1090 (3), DEC-342, DEC-1068, DEC-820).

Regression evidence only (DEC-136). Each store is planted in a temporary git repository with the secret filter replaced;
no model and no embedder runs (the endpoint is a stand-in, ``_ready`` gives the connection a Python
``vec_distance_cosine``), and the reranker is a stand-in.
"""
from __future__ import annotations

import argparse
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
from gov.launch import store as session_store  # noqa: E402
from gov.retrieval import lexical, retrieve, semantic  # noqa: E402
from gov.store import loader  # noqa: E402
from gov.retrieve import command  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
MAP_REL = "governance/project/path-map.yaml"
KEEP, CHANGING, GONE, MOVED, WALLED = ("docs/keep.md", "docs/changing.md", "docs/gone.md", "docs/moved_from.md",
                                       "walled/secret.md")
FILES = {
    ".gitignore": ".gov-runtime/\n",
    KEEP: "# Keep\n\nThe quillwort rule stays as it was.\n",
    CHANGING: "# Changing\n\nThe heronword rule is written here.\n",
    GONE: "# Gone\n\nThe cormorant rule is written here.\n",
    MOVED: "# Moved\n\nThe ibisword rule is written here.\n",
    WALLED: "# Walled\n\nThe wagtail rule is written here.\n",
}
WORDS = {"keep": "quillwort", "changing": "heronword", "gone": "cormorant", "moved": "ibisword", "walled": "wagtail"}


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True,
                          env={**_ENV, "HOME": str(root)}).stdout.strip()


def _head(root: Path) -> str:
    return _git(root, "rev-parse", "HEAD")


def _commit(root: Path, message: str, files: dict | None = None, remove=()) -> None:
    for rel, text in (files or {}).items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    for rel in remove:
        (root / rel).unlink()
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)


@pytest.fixture(autouse=True)
def _stand_ins(monkeypatch):
    for name in (session_store.ENV, "GOV_ROLE", "GOV_TICKET"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "search", lambda *_a, **_k: {"available": True, "reason": None, "hits": []})
    monkeypatch.setattr(semantic, "file_level_on", lambda root: False)
    monkeypatch.setattr(retrieve, "rerank", lambda query, candidates, reranker=None: [dict(c) for c in candidates])
    monkeypatch.setattr(retrieve, "last_outcome", lambda: {"by": "none", "device": None, "reason": "stand-in"})
    lexical._FRESHNESS.clear()
    lexical._LISTED.clear()


@pytest.fixture()
def repo(tmp_path):
    """A repository with its store built at commit X; the caller moves HEAD past it."""
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, "the planted files", FILES)
    lexical.refresh(tmp_path)
    store.load(tmp_path)
    return tmp_path


def _move_on(root: Path) -> None:
    """Three commits after the build: a new record, a changed file and a file removed; one path changed twice."""
    _commit(root, "the adoption's record", {"governance/adoption/record.md": "# Record\n\nAn adoption record.\n"})
    _commit(root, "the rule is rewritten", {CHANGING: "# Changing\n\nThe rule is rewritten.\n"})
    _commit(root, "and again", {CHANGING: "# Changing\n\nThe rule is rewritten again.\n"}, remove=[GONE])
    _git(root, "mv", MOVED, "docs/moved_to.md")
    _git(root, "commit", "-q", "-m", "a rename")


def _paths(bundle) -> set:
    return {item["path"] for item in bundle["evidence"]}


# S2: the store named ---------------------------------------------------------------------------------------------------

def test_store_of_names_commit_head_and_the_sorted_unique_paths_changed_in_between(repo):
    built = _head(repo)
    _move_on(repo)
    named = retrieve.store_of(repo)
    assert named["commit"] == built and named["head"] == _head(repo) != built
    # the new record, the path changed twice (once), the removed path and both sides of the rename
    assert named["stale"] == ["docs/changing.md", "docs/gone.md", "docs/moved_from.md", "docs/moved_to.md",
                              "governance/adoption/record.md"]
    assert named["root"] == str(repo)


def test_store_of_at_head_gives_the_head_as_the_commit_and_no_stale_path(repo):
    named = retrieve.store_of(repo)
    assert named["commit"] == named["head"] == _head(repo) and named["stale"] == []


def test_an_empty_commit_moves_the_head_and_names_no_path(repo):
    _commit(repo, "nothing changes")
    named = retrieve.store_of(repo)
    assert named["head"] == _head(repo) != named["commit"] and named["stale"] == []


def test_untracked_and_ignored_files_are_never_stale(repo):
    _commit(repo, "a commit")
    (repo / "docs/untracked.md").write_text("never added\n", encoding="utf-8")
    (repo / ".gov-runtime").mkdir(exist_ok=True)
    (repo / ".gov-runtime/ignored.md").write_text("ignored\n", encoding="utf-8")
    assert retrieve.store_of(repo)["stale"] == []


def test_a_store_with_no_commit_named_gives_no_stale_path_from_commits(repo):
    connection = sqlite3.connect(repo / ".gov-runtime/store.db")
    with connection:
        connection.execute(f"DROP TABLE IF EXISTS {loader.FINGERPRINTS_TABLE}")
    connection.close()
    named = retrieve.store_of(repo)
    assert named["commit"] is None and named["head"] == _head(repo) and named["stale"] == []


# S1, S3, F1: answered from the store ------------------------------------------------------------------------------------

def test_lexical_answers_at_a_moved_head_leaving_out_the_chunks_of_stale_paths(repo):
    _move_on(repo)
    kept = lexical.search(repo, WORDS["keep"], refresh=False)
    assert kept["available"] is True and {hit["path"] for hit in kept["hits"]} == {KEEP}
    for word in (WORDS["changing"], WORDS["gone"], WORDS["moved"], "rule"):
        found = lexical.search(repo, word, refresh=False)
        assert found["available"] is True, found
        assert not {chunk["path"] for chunk in found["ranked"]} & {CHANGING, GONE, MOVED, "docs/moved_to.md"}
        assert not [hit for hit in found["hits"] if hit["path"] in (CHANGING, GONE, MOVED)]
    assert KEEP in {chunk["path"] for chunk in lexical.search(repo, "rule", refresh=False)["ranked"]}


def test_the_ranked_cut_is_filled_from_chunks_that_are_not_stale(repo):
    _commit(repo, "many rules", {f"docs/rules{n}.md": f"# R{n}\n\nrule rule rule number {n}\n" for n in range(40)})
    _commit(repo, "the older ones move", {f"docs/rules{n}.md": f"# R{n}\n\nrule rule rule changed {n}\n"
                                          for n in range(40)})
    found = lexical.search(repo, "rule number", refresh=False, top_k=5)
    assert found["available"] is True and all(chunk["path"] not in {f"docs/rules{n}.md" for n in range(40)}
                                              for chunk in found["ranked"])


def test_retrieve_at_a_moved_head_returns_the_unchanged_file_and_names_the_store(repo):
    built = _head(repo)
    _move_on(repo)
    bundle = retrieve.retrieve(repo, WORDS["keep"], reranker=lambda: None)
    assert bundle["stopping_reason"] != "FACET_UNAVAILABLE" and bundle["facets"]["lexical"]["available"] is True
    assert KEEP in _paths(bundle)
    assert bundle["store"]["commit"] == built and bundle["store"]["head"] == _head(repo)
    assert bundle["store"]["stale"] == retrieve.store_of(repo)["stale"]


@pytest.mark.parametrize("name", ["changing", "gone", "moved"])
def test_a_path_changed_deleted_or_renamed_since_the_commit_is_never_returned(repo, name):
    _move_on(repo)
    bundle = retrieve.retrieve(repo, WORDS[name], reranker=lambda: None)  # the deleted file is read by nobody
    assert not _paths(bundle) & {CHANGING, GONE, MOVED, "docs/moved_to.md"}
    assert "The rule is rewritten" not in str([item["text"] for item in bundle["evidence"]])


def test_a_phrase_planted_only_after_the_build_is_returned_from_no_file(repo):
    _commit(repo, "a phrase planted later", {KEEP: FILES[KEEP] + "\nThe zymurgy phrase arrives later.\n"})
    bundle = retrieve.retrieve(repo, "zymurgy", reranker=lambda: None)
    assert not bundle["evidence"] and KEEP in bundle["store"]["stale"]


def test_an_uncommitted_change_does_not_serve_the_old_text_as_current(repo):
    (repo / CHANGING).write_text("# Changing\n\nRewritten and not committed.\n", encoding="utf-8")
    bundle = retrieve.retrieve(repo, WORDS["changing"], reranker=lambda: None)
    assert CHANGING not in _paths(bundle)
    assert bundle["store"]["stale"] == []  # the store follows commits: nothing added for the working tree


def test_the_moved_head_through_the_command_names_the_store_in_its_result(repo):
    built = _head(repo)
    _move_on(repo)
    args = argparse.Namespace(ticket=None, ids=[], radius=0, batch_size=None, bundle_budget=None, continuation=None,
                              query=WORDS["keep"], root=str(repo), role=None)
    result = command.run(repo, args, {})
    assert result["store"]["commit"] == built and result["store"]["head"] == _head(repo)
    assert "governance/adoption/record.md" in result["store"]["stale"] and KEEP in _paths(result)


def test_the_stated_gap_at_a_moved_head_is_reached_and_carries_the_store(repo):
    _move_on(repo)
    args = argparse.Namespace(ticket=None, ids=[], radius=0, batch_size=None, bundle_budget=None, continuation=None,
                              query="DEC-4242", root=str(repo), role=None)
    result = command.run(repo, args, {})
    assert result["stopping_reason"] == "UNRESOLVED_IDS"
    assert result["store"]["head"] == _head(repo) and result["store"]["stale"]


def test_a_continuation_at_a_moved_head_is_taken_by_the_commit_not_the_head(repo):
    _commit(repo, "many", {f"docs/many{n}.md": f"# M{n}\n\nrule marker {n}\n" for n in range(12)})
    lexical.refresh(repo)
    store.load(repo)
    _commit(repo, "the head moves")
    first = retrieve.retrieve(repo, "rule marker", batch_size=2, reranker=lambda: None)
    assert first["continuation"] is not None
    second = retrieve.retrieve(repo, "rule marker", batch_size=2, continuation=first["continuation"],
                               reranker=lambda: None)
    assert second["store"]["commit"] == first["store"]["commit"]


# F2: the stores that stay unavailable ----------------------------------------------------------------------------------

def test_no_store_keeps_its_reason(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, "files only", FILES)
    assert lexical.search(tmp_path, "quillwort", refresh=False) == lexical._unavailable("missing")


def test_an_empty_store_keeps_its_reason_at_a_moved_head(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, "an empty tree")  # no tracked file: the index holds no chunk
    lexical.refresh(tmp_path)
    assert lexical.search(tmp_path, "quillwort", refresh=False)["reason"] == "empty"
    _commit(tmp_path, "a file", {"docs/a.md": "# A\n\nquillwort\n"})
    found = lexical.search(tmp_path, "quillwort", refresh=False)
    assert found["available"] is False and found["reason"] == "stale" and not found["hits"]


def test_a_corrupt_store_file_is_unreadable_at_a_moved_head(repo):
    _commit(repo, "the head moves")
    (repo / ".gov-runtime/store.db").write_bytes(b"this is not a database" * 400)
    found = lexical.search(repo, "quillwort", refresh=False)
    assert found["available"] is False and found["reason"] == "unreadable"
    assert retrieve.store_of(repo)["commit"] is None


@pytest.mark.parametrize("committed", [True, False])
def test_a_recipe_changed_store_stays_stale_and_names_the_store(repo, committed):
    built = _head(repo)
    (repo / "governance/project").mkdir(parents=True, exist_ok=True)
    (repo / "governance/project/rebuild.yaml").write_text("lexical_split_identifiers: true\n", encoding="utf-8")
    if committed:
        _commit(repo, "the recipe changes")
    else:
        _commit(repo, "the head moves")
    found = lexical.search(repo, "quillwort", refresh=False)
    assert found["available"] is False and found["reason"] == "stale" and not found["hits"]
    bundle = retrieve.retrieve(repo, "quillwort", reranker=lambda: None)
    assert bundle["stopping_reason"] == "FACET_UNAVAILABLE" and not bundle["evidence"]
    assert bundle["store"]["commit"] == built and bundle["store"]["head"] == _head(repo)


# the semantic facet ----------------------------------------------------------------------------------------------------

def test_the_semantic_status_follows_the_lexical_one_at_a_moved_head(tmp_path, monkeypatch):
    shown = {}

    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": "ac6da0dfba84" + "0" * 52}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 1, "size_vram": 1}]}
        return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}

    def distance(left, right):
        count = len(left) // 4
        return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))

    monkeypatch.undo()  # the autouse stand-ins give way to the real facets, with a stand-in endpoint
    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None:
                        connection.create_function("vec_distance_cosine", 2, distance))
    path_map = ("namespaces:\n  open: {paths: ['open/**'], embedding_policy: embedded}\n"
                "  closed: {paths: ['closed/**'], embedding_policy: not embedded}\n")
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, "planted", {".gitignore": ".gov-runtime/\n", MAP_REL: path_map, "open/pear.md": "pear trees\n",
                                  "open/plum.md": "plum trees\n"})
    assert semantic.refresh(tmp_path)["available"] is True
    lexical._FRESHNESS.clear()
    semantic._STATUS.clear()
    _commit(tmp_path, "the head moves and a file changes", {"open/plum.md": "plum orchards\n", "open/new.md": "kiwi\n"})
    shown["status"] = semantic._status(tmp_path)
    assert shown["status"] is None, shown
    found = semantic.search(tmp_path, "where is the pear", refresh=False)
    assert found["available"] is True and found["reason"] is None, found
    assert {hit["path"] for hit in found["hits"]} == {"open/pear.md"}  # the plum file changed: left out


# F3, DEC-1157 (12): a stale path the role is walled from is counted, never named ---------------------------------------

def _walled_repo(root: Path, monkeypatch, section) -> Path:
    path_map = yaml.safe_load((REPO / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    path_map["namespaces"] = {"notes": {**next(iter(path_map["namespaces"].values())), "paths": ["**"]}}
    path_map.pop("decision_register", None)
    path_map.pop("role_paths", None)
    if section is not None:
        path_map["role_paths"] = section
    files = {**FILES, MAP_REL: yaml.safe_dump(path_map)}
    _git(root, "init", "-q", "-b", "main")
    _commit(root, "the planted files", files)
    lexical.refresh(root)
    store.load(root)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    monkeypatch.delenv("GOV_TICKET", raising=False)
    return root


def _move_walled(root: Path) -> None:
    _commit(root, "a walled file and an open one change", {WALLED: "# Walled\n\nChanged.\n",
                                                           CHANGING: "# Changing\n\nChanged.\n"})


def test_a_stale_path_the_role_is_walled_from_is_not_named_but_counted(tmp_path, monkeypatch):
    _walled_repo(tmp_path, monkeypatch, {"engineer": {"reads_denied": ["walled/**"]}})
    _move_walled(tmp_path)
    monkeypatch.setenv("GOV_ROLE", "engineer")
    named = retrieve.store_of(tmp_path)
    assert WALLED not in named["stale"] and CHANGING in named["stale"] and named["stale_walled"] == 1
    bundle = retrieve.retrieve(tmp_path, WORDS["keep"], reranker=lambda: None)
    assert WALLED not in bundle["store"]["stale"] and bundle["store"]["stale_walled"] == 1
    assert WALLED not in str(bundle["store"])


def test_the_role_given_beside_the_environment_walls_the_stale_names_too(tmp_path, monkeypatch):
    _walled_repo(tmp_path, monkeypatch, {"engineer": {"reads_denied": ["walled/**"]}})
    _move_walled(tmp_path)
    assert retrieve.store_of(tmp_path)["stale"].count(WALLED) == 1  # no role: nothing is walled
    named = retrieve.store_of(tmp_path, "engineer")
    assert WALLED not in named["stale"] and named["stale_walled"] == 1
    again = retrieve.retrieve(tmp_path, WORDS["keep"], role="engineer", store=retrieve.store_of(tmp_path),
                              reranker=lambda: None)  # a store named without the role is walled again at the result
    assert WALLED not in again["store"]["stale"] and again["store"]["stale_walled"] == 1


def test_a_role_with_no_wall_sees_every_stale_path_and_no_count_of_withheld_ones(tmp_path, monkeypatch):
    _walled_repo(tmp_path, monkeypatch, {"engineer": {"reads_denied": ["walled/**"]}})
    _move_walled(tmp_path)
    monkeypatch.setenv("GOV_ROLE", "orchestrator")
    named = retrieve.store_of(tmp_path)
    assert WALLED in named["stale"] and named.get("stale_walled", 0) == 0


def test_a_wall_that_cannot_be_read_names_no_stale_path_only_the_count(tmp_path, monkeypatch):
    _walled_repo(tmp_path, monkeypatch, {"engineer": {"reads_denied": ["walled/**"]}})
    _move_walled(tmp_path)
    (tmp_path / MAP_REL).write_text("role_paths:\n  engineer: not-a-mapping\n", encoding="utf-8")
    monkeypatch.setenv("GOV_ROLE", "engineer")
    named = retrieve.store_of(tmp_path)
    assert named["stale"] == [] and named["stale_walled"] == 2  # fail closed: the store's own commit and head stand
    assert named["commit"] and named["head"] == _head(tmp_path)
    with pytest.raises(GovError) as raised:
        retrieve.retrieve(tmp_path, WORDS["keep"], reranker=lambda: None)
    assert raised.value.code == "ROLE_PATHS_UNREADABLE"


def test_the_text_line_names_the_commit_the_head_and_the_count(repo):
    built = _head(repo)
    _move_on(repo)
    line = retrieve.store_line(retrieve.store_of(repo))
    assert line.startswith(f"store: {built[:12]} (") and f"head {_head(repo)[:12]}" in line
    assert "5 stale path(s)" in line
    walled = retrieve.store_line({"commit": built, "head": _head(repo), "root": str(repo), "stale": ["a"],
                                  "stale_walled": 2})
    assert "1 stale path(s)" in walled and "2 stale path(s) not shown (walled)" in walled


def test_the_text_line_at_head_is_the_line_of_w2_138(repo):
    named = retrieve.store_of(repo)
    assert retrieve.store_line(named) == f"store: {_head(repo)[:12]} ({repo})"
    assert retrieve.store_line({"commit": None, "root": "/x"}) == "store: unknown (/x)"


def test_no_git_is_no_head_and_no_stale_path(tmp_path, monkeypatch):
    def refused(root, *args, **kwargs):
        raise GovError("INDEX_GIT_FAILED", "no git here")

    monkeypatch.setattr(lexical, "_git", refused)
    assert retrieve.store_of(tmp_path) == {"commit": None, "head": None, "stale": [], "root": str(tmp_path)}
