"""Builder tests for W2-108: the lexical index's freshness and the vectors' status worked out once per store and tree
in a process (DEC-969).

Regression evidence only (DEC-136). Each project is a temporary git repository (DEC-322) with the secret filter
replaced; the endpoint is a stand-in and ``_ready`` gives the connection a Python ``vec_distance_cosine``, so no test
needs Ollama, ``sqlite_vec`` or gitleaks. A check is counted by the calls to the two functions that do its work:
``lexical._tracked`` (every tracked file hashed) and ``semantic._wanted`` (every chunk judged against the path map).
"""
from __future__ import annotations

import struct
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import lexical, semantic  # noqa: E402

_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid"}
PATH_MAP = """namespaces:
  open: {paths: ['open/**'], embedding_policy: embedded}
  closed: {paths: ['closed/**'], embedding_policy: not embedded}
"""
MAP_REL = "governance/project/path-map.yaml"
FILES = {".gitignore": ".gov-runtime/\n", MAP_REL: PATH_MAP, "open/pear.md": "pear trees\n",
         "open/plum.md": "plum trees\n", "closed/vault.md": "cobalt ledger\n"}


def _git(root, *args):
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env={**_ENV, "HOME": str(root)})


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "a change")


def _distance(left, right):
    count = len(left) // 4
    return sum(abs(a - b) for a, b in zip(struct.unpack(f"{count}f", left), struct.unpack(f"{count}f", right)))


def _settle():
    """Wait out the window in which a fresh stamp is not trusted, so that the next key can be kept."""
    time.sleep(2 * lexical.RACY_NS / 1e9)


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A repository whose store holds a fresh lexical index and fresh vectors, the counts of the two checks, and a
    function giving the answers of three calls, the semantic and lexical searches and both statuses."""
    def ask(path, body=None, host=None):
        if path == "/api/tags":
            return {"models": [{"name": semantic.MODEL, "digest": "ac6da0dfba84" + "0" * 52}]}
        if path == "/api/ps":
            return {"models": [{"name": semantic.MODEL, "size": 1, "size_vram": 1}]}
        return {"embeddings": [[float("pear" in text), float("plum" in text)] for text in body["input"]]}

    counts = {"tracked": 0, "wanted": 0, "ls-files": 0, "hash-object": 0}
    tracked, wanted, git = lexical._tracked, semantic._wanted, lexical._git

    def counted_git(root, *args, stdin=None):
        if args[0] in ("ls-files", "hash-object"):
            counts[args[0]] += 1
        return git(root, *args, stdin=stdin)

    def counted_tracked(root):
        counts["tracked"] += 1
        return tracked(root)

    def counted_wanted(root, connection):
        counts["wanted"] += 1
        return wanted(root, connection)

    monkeypatch.setattr(lexical, "indexable", lambda root, paths: list(paths))
    monkeypatch.setattr(semantic, "_ask", ask)
    monkeypatch.setattr(semantic, "_ready", lambda connection, ensure=None:
                        connection.create_function("vec_distance_cosine", 2, _distance))
    monkeypatch.setattr(lexical, "_tracked", counted_tracked)
    monkeypatch.setattr(semantic, "_wanted", counted_wanted)
    monkeypatch.setattr(lexical, "_git", counted_git)
    monkeypatch.setattr(lexical, "_FRESHNESS", {})
    monkeypatch.setattr(lexical, "_LISTED", {})
    monkeypatch.setattr(semantic, "_STATUS", {})
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, FILES)
    assert semantic.refresh(tmp_path)["available"] is True
    _settle()
    counts.update(dict.fromkeys(counts, 0))

    def answers():
        # the semantic answer without its ``vector_cache`` counts: they name what the machine-wide cache served,
        # which changes from the first call to the next (W2-126, DEC-1042); the answer itself must not
        searched = semantic.search(tmp_path, "where is the pear", refresh=False)
        return ({key: value for key, value in searched.items() if key != "vector_cache"},
                lexical.search(tmp_path, "trees", refresh=False), lexical.freshness(tmp_path),
                semantic._status(tmp_path))

    return tmp_path, counts, answers


def _afresh(answers):
    """The answers worked out with nothing remembered, as they were before W2-108."""
    lexical._FRESHNESS.clear()
    lexical._LISTED.clear()
    semantic._STATUS.clear()
    return answers()


def test_each_check_runs_once_over_many_calls_and_every_answer_is_unchanged(project):
    root, counts, answers = project
    first = answers()
    assert first[0]["available"] is True and first[0]["hits"] and first[1]["hits"] and first[3] is None
    assert all(answers() == first for _ in range(5))
    assert counts == {"tracked": 1, "wanted": 1, "ls-files": 2, "hash-object": 1}, \
        "a check was repeated within one process (the tracked files listed once for the key, once for the hashes)"
    assert _afresh(answers) == first


def test_a_file_added_to_the_index_and_not_committed_is_seen(project):
    root, counts, answers = project
    answers()
    (root / "open/quince.md").write_text("quince trees\n", encoding="utf-8")
    _git(root, "add", "open/quince.md")  # the head stays; the index changes
    added = answers()
    assert added[2] == {"status": "stale", "stale": ["open/quince.md"]} and added[3] == "stale"
    _settle()
    assert answers() == added == _afresh(answers)


def test_a_store_rebuilt_is_seen(project):
    root, counts, answers = project
    answers()
    (root / ".gov-runtime/store.db").unlink()
    assert answers()[2]["status"] == "missing" and answers()[3] == "missing"
    assert semantic.refresh(root)["available"] is True
    _settle()
    rebuilt = answers()
    assert rebuilt[3] is None and rebuilt[0]["hits"] and rebuilt == _afresh(answers)
    assert counts["tracked"] >= 2 and counts["wanted"] >= 2


def test_a_file_edited_and_not_committed_is_seen_at_once_and_after_a_while(project):
    root, counts, answers = project
    answers()
    (root / "open/plum.md").write_text("plum bowls\n", encoding="utf-8")  # the same size: only the content differs
    edited = answers()
    assert edited[2] == {"status": "stale", "stale": ["open/plum.md"]} and edited[3] == "stale"
    assert edited[0]["available"] is False and edited[1]["available"] is False
    _settle()
    assert answers() == edited == _afresh(answers)
    seen = dict(counts)
    assert all(answers() == edited for _ in range(3)) and counts == seen, "the unchanged edit was checked again"


def test_a_head_moved_is_a_new_key(project):
    root, counts, answers = project
    before = answers()
    _git(root, "commit", "-q", "--allow-empty", "-m", "the head moves, no file does")
    _settle()
    assert answers() == before
    assert counts["tracked"] == 2 and counts["wanted"] == 2, "a moved head did not give a fresh check"


def test_a_path_map_changed_outside_the_tracked_files_is_seen(project):
    root, counts, answers = project
    _git(root, "rm", "-q", "--cached", MAP_REL)
    _git(root, "commit", "-q", "-m", "the path map is no longer tracked")
    assert semantic.refresh(root)["available"] is True
    _settle()
    counts.update(tracked=0, wanted=0)
    assert answers()[3] is None and answers()[3] is None and counts["wanted"] == 1
    (root / MAP_REL).write_text(PATH_MAP.replace("not embedded", "embedded"), encoding="utf-8")
    _settle()
    assert lexical.freshness(root)["status"] == "fresh" and semantic._status(root) == "stale"
    assert counts["wanted"] == 2


def test_a_key_that_cannot_be_read_checks_every_time(project, monkeypatch):
    root, counts, answers = project
    _git(root, "update-ref", "-d", "refs/heads/main")  # HEAD names a branch that does not exist: no head to read
    for _ in range(3):
        assert lexical.freshness(root)["status"] == "fresh"
    assert counts["tracked"] == 3
    monkeypatch.setattr(lexical, "_store_stamp", lambda root: None)
    for _ in range(3):
        assert semantic._status(root) is None
    assert counts["wanted"] == 3


def test_a_stamp_too_recent_to_trust_gives_no_key(project):
    root, counts, answers = project
    assert lexical._stamps([root / "open/pear.md"]) is not None
    (root / "open/pear.md").write_text("pear trees\n", encoding="utf-8")
    assert lexical._stamps([root / "open/pear.md"]) is None
    assert lexical._stamps([root / "absent.md"]) == (None,)
