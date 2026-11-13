"""Unit tests for the two fingerprints of a commit in their new home, gov.store.loader (W2-150, DEC-136; S5).

Moved from ``gov.close.fingerprint``, whose builder cases (tests/unit/close/test_fingerprint.py) stay on the old
name. A planted repository only, made here; nothing of this repository's history is read.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from gov.store import loader

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_REL = "template/governance/kernel/schemas/test-map.schema.json"
MAP = 'version: 1\nshared_core: ["src/core/**"]\nrecord_only:\n  - "docs/close/**.md"\n  - "governance/project/**"\n'


def _git(root, *args):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args],
                          check=True, capture_output=True, text=True, env=env).stdout


@pytest.fixture()
def repo(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    return root


def _commit(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "c")


def _project(root):
    _commit(root, {SCHEMA_REL: (REPO_ROOT / SCHEMA_REL).read_text(encoding="utf-8"), loader.TEST_MAP_REL: MAP,
                   "src/a.py": "A = 1\n", "docs/close/T/CL-1.md": "one\n", loader.PATH_MAP_REL: "namespaces: {}\n"})
    return loader.of_commit(root)


def test_the_places_are_the_close_s(repo):
    assert loader.TEST_MAP_REL == "governance/project/test-map.yaml"
    assert loader.SCHEMA_RELS == tuple(f"{d}/test-map.schema.json" for d in loader.SCHEMA_DIRS)
    assert {loader.PATH_MAP_REL, loader.TEST_MAP_REL, *loader.SCHEMA_RELS} == loader.ALWAYS_CODE


def test_a_record_only_commit_moves_the_records_print_alone(repo):
    before = _project(repo)
    assert before["code"].startswith(loader.PREFIX) and before["records"].startswith(loader.PREFIX)
    _commit(repo, {"docs/close/T/CL-2.md": "two\n"})
    after = loader.of_commit(repo)
    assert after["code"] == before["code"] and after["records"] != before["records"]


def test_a_code_commit_and_the_always_code_files_move_the_code_print(repo):
    before = _project(repo)
    _commit(repo, {loader.PATH_MAP_REL: "namespaces: {x: {}}\n"})  # matched by record_only, yet code
    moved = loader.of_commit(repo)
    assert moved["code"] != before["code"] and moved["records"] == before["records"]
    _commit(repo, {"src/a.py": "A = 2\n"})
    assert loader.of_commit(repo)["code"] != moved["code"]


def test_the_prints_are_the_sorted_tree_lines(repo):
    prints = _project(repo)
    lines = [line for line in _git(repo, "ls-tree", "-r", "-z", "--full-tree", "HEAD").split("\0") if line]
    records = [line for line in lines if line.endswith("\tdocs/close/T/CL-1.md")]
    assert prints["records"] == loader._print_of(records)
    assert prints["code"] == loader._print_of([line for line in lines if line not in records])


def test_what_cannot_be_computed_is_none(repo):
    assert loader.of_commit(repo) is None  # no commit
    _commit(repo, {"src/a.py": "A = 1\n"})
    assert loader.of_commit(repo) is None  # no test map
    _commit(repo, {loader.TEST_MAP_REL: "- a list, not a map\n"})
    assert loader.of_commit(repo) is None


def test_the_old_name_is_the_same_function(repo):
    from gov.close import fingerprint, select

    assert fingerprint.of_commit is loader.of_commit and fingerprint.ALWAYS_CODE is loader.ALWAYS_CODE
    assert select.MAP_REL == loader.TEST_MAP_REL and select.SCHEMA_NAME == loader.TEST_MAP_SCHEMA
    assert _project(repo) == fingerprint.of_commit(repo)
