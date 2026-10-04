"""KPI failure 2: graph content depends on file order or time. With KPI success 1: the same digest twice.

The digest is of the store's logical content (package DP-4), so the tests compare it across stores whose files were
written at different times, in different places and by different processes. Each comparison is made twice: by the
digest, and by the content the queries return.
"""

from __future__ import annotations

import os
import time

import pytest

import w1_10_support as support


def _age(root, seconds):
    """Set the modification time of every file of the working tree back by ``seconds``."""
    for folder, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in (".git", ".gov-runtime")]
        for name in files:
            path = os.path.join(folder, name)
            stamp = os.stat(path).st_mtime - seconds
            os.utime(path, (stamp, stamp))


def test_a_later_load_gives_the_same_digest(api, repo):
    first = api.load(repo.root)["digest"]
    time.sleep(1.1)  # a load time stored to the second would differ
    assert api.load(repo.root)["digest"] == first


def test_a_load_into_a_new_store_gives_the_same_digest(api, repo):
    first = api.load(repo.root)["digest"]
    (repo.root / support.STORE_REL).unlink()
    assert api.load(repo.root)["digest"] == first


def test_a_clone_elsewhere_gives_the_same_digest_and_content(api, graph, base, tmp_path):
    """Another path, older files, another time zone and another hash seed: the same graph."""
    other = support.clone(base.root, tmp_path / "somewhere" / "else" / "project")
    _age(other, 400 * 24 * 3600)
    env = {"TZ": "Pacific/Kiritimati", "PYTHONHASHSEED": "4242"}
    assert api.load(other, **env)["digest"] == graph.summary["digest"]
    assert api.dump(other, **env) == api.dump(graph.root, PYTHONHASHSEED="1")


@pytest.mark.parametrize("seed", ["0", "1", "987654"])
def test_the_digest_does_not_depend_on_the_hash_seed(api, graph, repo, seed):
    assert api.load(repo.root, PYTHONHASHSEED=seed)["digest"] == graph.summary["digest"]


def test_the_order_the_files_were_written_in_does_not_change_the_graph(api, graph, tmp_path):
    """The same commits, with the files created on disk in the opposite order."""
    reverse = tmp_path / "reverse"
    commits = support.build_fixture(reverse, reverse=True)
    assert commits == graph.commits, "the two fixtures are not the same commits; the comparison would mean nothing"
    assert api.load(reverse)["digest"] == graph.summary["digest"]
    assert api.dump(reverse) == api.dump(graph.root)


def test_a_store_loaded_again_after_a_commit_equals_a_new_store(api, repo, tmp_path):
    """Loading over an older store and loading from nothing give the same graph."""
    api.load(repo.root)
    support.git(repo.root, "rm", "-q", "docs/adr/ADR-0006-sixth.md")
    support.write(repo.root, "docs/adr/ADR-0008-new.md",
                  support.record("ADR-0008", "decision", "ACTIVE", "New", supersedes=["ADR-0001"]))
    support.commit(repo.root, "one decision out, one in", support.LATER, trailers=[f"Task: {support.TICKET}"])
    again = api.load(repo.root)["digest"]
    fresh = support.clone(repo.root, tmp_path / "fresh")
    assert api.load(fresh)["digest"] == again
    assert api.dump(fresh) == api.dump(repo.root)


def _status_changes(root):
    support.write(root, "docs/adr/ADR-0006-sixth.md", support.record("ADR-0006", "decision", "ACTIVE", "Sixth"))
    support.commit(root, "the same subject", support.LATER)


def _edge_added(root):
    support.write(root, "docs/adr/ADR-0006-sixth.md",
                  support.record("ADR-0006", "decision", "PROPOSED", "Sixth", depends_on=["ADR-0001"]))
    support.commit(root, "the same subject", support.LATER)


def _commit_with_trailer(root):
    support.commit(root, "the same subject", support.LATER, trailers=[f"Task: {support.TICKET}"])


@pytest.mark.parametrize("change", [_status_changes, _edge_added, _commit_with_trailer],
                         ids=["a status changes", "an edge is added", "a commit with a trailer is added"])
def test_the_digest_changes_when_the_content_changes(api, repo, change):
    """A digest that never changes would pass every test above."""
    before = api.load(repo.root)["digest"]
    change(repo.root)
    after = api.load(repo.root)["digest"]
    assert after != before
    assert api.digest(repo.root) == after
