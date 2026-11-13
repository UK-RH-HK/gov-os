"""W2-20 S7 (DEC-1001 (d)): a rebuild excludes only another rebuild of the same tree; each tree its own lock."""
from __future__ import annotations

import fcntl
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.rebuild import watch  # noqa: E402


def test_each_tree_has_its_own_default_lock(tmp_path, monkeypatch):
    monkeypatch.delenv(watch.ENV_LOCK, raising=False)
    one, two = tmp_path / "one", tmp_path / "two"
    one.mkdir()
    two.mkdir()
    _, lock_one, source = watch.settings(one)
    _, lock_two, _ = watch.settings(two)
    assert source == watch.FROM_DEFAULT and lock_one != lock_two
    assert lock_one == watch.tree_lock(one) and lock_one.startswith("/tmp/gov-os-rebuild-")
    assert watch.settings(one)[1] == lock_one  # the same tree, the same lock


def test_a_link_to_a_tree_takes_the_trees_lock(tmp_path):
    tree = tmp_path / "tree"
    tree.mkdir()
    (tmp_path / "link").symlink_to(tree)
    assert watch.tree_lock(tmp_path / "link") == watch.tree_lock(tree)


def test_a_rebuild_of_another_tree_is_not_excluded_while_one_tree_is_held(tmp_path, monkeypatch):
    monkeypatch.setattr(watch, "LOCK", str(tmp_path / "gov-os-rebuild.lock"))
    one, two = tmp_path / "one", tmp_path / "two"
    held = os.open(watch.tree_lock(one), os.O_RDWR | os.O_CREAT)
    fcntl.flock(held, fcntl.LOCK_EX)
    try:
        fd, part = watch.take(watch.tree_lock(two), watch.FROM_DEFAULT)  # taken at once: no wait
        assert fd is not None and part["wait_s"] == 0.0 and part["holder"] is None
        os.close(fd)
        same = os.open(watch.tree_lock(one), os.O_RDWR)
        try:
            fcntl.flock(same, fcntl.LOCK_EX | fcntl.LOCK_NB)
            raise AssertionError("the same tree's lock was not held")
        except BlockingIOError:
            pass
        finally:
            os.close(same)
    finally:
        os.close(held)


def test_the_override_and_a_trees_own_setting_still_win(tmp_path, monkeypatch):
    monkeypatch.setenv(watch.ENV_LOCK, str(tmp_path / "mine.lock"))
    assert watch.settings(tmp_path)[1:] == (str(tmp_path / "mine.lock"), watch.FROM_ENV)
