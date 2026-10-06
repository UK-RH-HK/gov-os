"""Tests that the mirror-folder tripwire detects changes.

These tests exercise the detection logic from ``tests/acceptance/conftest.py``
on a stand-in folder, never the real ``~/.local/state/gov-os/``.

4 tests.
"""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

_ACCEPTANCE_CONFTEST = Path(__file__).resolve().parents[1] / "conftest.py"
_spec = importlib.util.spec_from_file_location("acceptance_conftest", _ACCEPTANCE_CONFTEST)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
_snapshot = _mod._snapshot


def test_snapshot_returns_none_for_missing_folder(tmp_path):
    """A folder that does not exist yields None."""
    assert _snapshot(str(tmp_path / "no-such-folder")) is None


def test_snapshot_detects_an_added_file(tmp_path):
    """Adding a file to the folder changes the listing."""
    folder = tmp_path / "mirror"
    folder.mkdir()
    before = _snapshot(str(folder))
    assert before is not None
    listing_before, _ = before

    (folder / "new-entry").write_text("x", encoding="utf-8")
    after = _snapshot(str(folder))
    listing_after, _ = after

    added = sorted(set(listing_after) - set(listing_before))
    assert added == ["new-entry"], f"expected ['new-entry'], got {added}"


def test_snapshot_detects_a_removed_file(tmp_path):
    """Removing a file from the folder changes the listing."""
    folder = tmp_path / "mirror"
    folder.mkdir()
    sentinel = folder / "sentinel"
    sentinel.write_text("x", encoding="utf-8")
    before = _snapshot(str(folder))
    listing_before, _ = before

    sentinel.unlink()
    after = _snapshot(str(folder))
    listing_after, _ = after

    removed = sorted(set(listing_before) - set(listing_after))
    assert removed == ["sentinel"], f"expected ['sentinel'], got {removed}"


def test_snapshot_listing_returns_to_normal_after_undo(tmp_path):
    """After adding and removing a file, the listing matches the original."""
    folder = tmp_path / "mirror"
    folder.mkdir()
    (folder / "stable").write_text("x", encoding="utf-8")
    before = _snapshot(str(folder))
    listing_before, _ = before

    added = folder / "transient"
    added.write_text("x", encoding="utf-8")
    mid = _snapshot(str(folder))
    assert sorted(mid[0]) != sorted(listing_before), "the add was not detected"

    added.unlink()
    after = _snapshot(str(folder))
    listing_after, _ = after
    assert sorted(listing_after) == sorted(listing_before), (
        f"listing did not return to normal: before={listing_before}, after={listing_after}"
    )
