"""Fix I-17: ``gov update``/``gov install`` without ``--wheel`` must take a release's own wheel.

A release cut by a gov whose builder predates F3 holds a wheel without ``gov/_build_info.py``; a rebuild by today's
builder adds that file and hashes otherwise. The install route must still find the manifest's wheel: from the cut
wheel kept at ``<home>/.local/share/gov-os/wheels/<commit12>/`` when its hash matches, else by a rebuild of that
builder's variant. A wheel whose hash is not the manifest's is still refused.
"""
import hashlib
from pathlib import Path

import pytest

from gov import release
from gov.install import pin
from .conftest import git, new_source, write_version


def _legacy_release(base: Path):
    """A release whose manifest wheel is built the way a pre-F3 builder builds it (no build info)."""
    source = new_source(base)
    write_version(source, "1.0.0")
    git(source, "add", "-A")
    git(source, "commit", "-q", "-m", "version 1.0.0")
    commit = git(source, "rev-parse", "HEAD").strip()
    wheel = release._wheel(source, commit, build_info=False)
    assert wheel["sha256"] != release._wheel(source, commit)["sha256"]
    return source, {"commit": commit, "wheel": wheel}


def test_rebuild_finds_the_wheel_a_pre_f3_builder_cut(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    source, manifest = _legacy_release(tmp_path)
    folder = tmp_path / "out"
    folder.mkdir()
    path = pin.wheel_for(source, "1.0.0", manifest, None, folder)
    assert hashlib.sha256(path.read_bytes()).hexdigest() == manifest["wheel"]["sha256"]


def test_the_cut_wheel_kept_in_the_share_is_taken_when_its_hash_matches(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    source, manifest = _legacy_release(tmp_path)
    kept = home / ".local/share/gov-os/wheels" / manifest["commit"][:12]
    kept.mkdir(parents=True)
    release._wheel(source, manifest["commit"], keep=kept, build_info=False)
    out = tmp_path / "out"
    out.mkdir()
    path = pin.wheel_for(source, "1.0.0", manifest, None, out)
    assert path.parent == kept


def test_a_kept_wheel_with_another_hash_is_not_taken_and_a_wrong_manifest_still_refuses(tmp_path, monkeypatch):
    home = tmp_path / "home"
    monkeypatch.setenv("HOME", str(home))
    source, manifest = _legacy_release(tmp_path)
    kept = home / ".local/share/gov-os/wheels" / manifest["commit"][:12]
    kept.mkdir(parents=True)
    (kept / manifest["wheel"]["name"]).write_bytes(b"tampered")
    out = tmp_path / "out"
    out.mkdir()
    path = pin.wheel_for(source, "1.0.0", manifest, None, out)
    assert path.parent == out
    bad = {**manifest, "wheel": {**manifest["wheel"], "sha256": "0" * 64}}
    with pytest.raises(pin.InstallRefused) as refused:
        pin.wheel_for(source, "1.0.0", bad, None, out)
    assert refused.value.reason == "wheel"
