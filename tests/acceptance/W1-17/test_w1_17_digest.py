"""KPI failure 2: the rebuild digest differs between two runs. With KPI success 3: the index digest.

The digest is of the index's logical content (compare DEC-276), so it is compared across stores written at
different times, in different places and by different processes. A digest that never changes would pass those
comparisons, so the last tests change the content and expect another digest.
"""

from __future__ import annotations

import os
import shutil
import time

import pytest

import w1_17_support as support


def _age(root, seconds):
    """Set the modification time of every file of the working tree back by ``seconds``."""
    for folder, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in (".git", ".gov-runtime")]
        for name in files:
            path = os.path.join(folder, name)
            stamp = os.stat(path).st_mtime - seconds
            os.utime(path, (stamp, stamp))


def test_the_digest_of_the_index_is_the_one_the_refresh_reported(api, indexed):
    assert api.digest(indexed.root) == indexed.report["digest"]


def test_a_rebuild_after_the_derived_state_is_deleted_gives_the_same_digest(api, repo):
    """Delete ``.gov-runtime/`` and build again, more than a second later."""
    first = api.refresh(repo)["digest"]
    shutil.rmtree(repo / support.RUNTIME_REL)
    time.sleep(1.1)  # a build time stored to the second would differ
    second = api.refresh(repo)
    assert set(support.CORPUS) <= set(second["indexed"]), "the rebuild did not index the corpus again"
    assert second["digest"] == first


def test_a_build_elsewhere_gives_the_same_digest(api, indexed, base, tmp_path):
    """Another path, older files, another time zone and another hash seed: the same index."""
    other = support.clone(base, tmp_path / "somewhere" / "else" / "project")
    _age(other, 400 * 24 * 3600)
    report = api.refresh(other, TZ="Pacific/Kiritimati", PYTHONHASHSEED="4242")
    assert report["digest"] == indexed.report["digest"]
    assert api.digest(other, PYTHONHASHSEED="1") == indexed.report["digest"]


def _a_line_changes(root):
    support.write(root, support.RUNBOOK, support.RUNBOOK_TEXT.replace("drains", "empties"))


def _a_file_is_added(root):
    support.write(root, "notes/added.md", "# Added\n\nA new note.\n")


def _a_file_is_removed(root):
    support.git(root, "rm", "-q", support.CLIENT)


def _a_file_is_renamed(root):
    support.git(root, "mv", support.CLIENT, "app/renamed.ts")


@pytest.mark.parametrize("change", [_a_line_changes, _a_file_is_added, _a_file_is_removed, _a_file_is_renamed],
                         ids=["a line changes", "a file is added", "a file is removed", "a file is renamed"])
def test_the_digest_changes_when_the_tracked_content_changes(api, repo, change):
    before = api.refresh(repo)["digest"]
    change(repo)
    support.commit(repo, "the content changes")
    after = api.refresh(repo)["digest"]
    assert after != before
    assert api.digest(repo) == after
