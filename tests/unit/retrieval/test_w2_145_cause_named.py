"""SANDBOX-1 B2 (DEC-1167 (7)), within W2-145's scope (DEC-1088 (6)): when the cache folder already exists as the
sandbox binds it (read-only), `_connect` does not mkdir or chmod it, so the error a search reports is the socket's own
(EPERM), not the folder's EROFS that hid it (rerank.log: 399 sandboxed FALLBACK lines naming the read-only folder)."""

from __future__ import annotations

import errno
from pathlib import Path

import pytest

from gov.retrieval import rerank


class _RefusedSocket:
    def __init__(self, *args, **kwargs):
        raise PermissionError(errno.EPERM, "Operation not permitted")


@pytest.fixture
def readonly_cache(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    folder = rerank._cache()
    folder.mkdir(parents=True)
    folder.chmod(0o700)

    def refuse(self, *args, **kwargs):
        raise OSError(errno.EROFS, "Read-only file system", str(self))

    monkeypatch.setattr(Path, "mkdir", refuse)
    monkeypatch.setattr(Path, "chmod", refuse)
    monkeypatch.setattr(rerank.socket, "socket", _RefusedSocket)
    return folder


def test_an_existing_cache_folder_is_not_touched_so_the_socket_refusal_is_the_error(readonly_cache):
    with pytest.raises(PermissionError) as raised:
        rerank._connect("python3")
    assert raised.value.errno == errno.EPERM


def test_a_missing_cache_folder_is_still_made(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(rerank.socket, "socket", _RefusedSocket)
    folder = rerank._cache()
    assert not folder.exists()
    with pytest.raises(PermissionError):
        rerank._connect("python3")
    assert folder.is_dir() and folder.stat().st_mode & 0o777 == 0o700


def test_a_cache_folder_with_a_wider_mode_is_narrowed(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setattr(rerank.socket, "socket", _RefusedSocket)
    folder = rerank._cache()
    folder.mkdir(parents=True)
    folder.chmod(0o755)
    with pytest.raises(PermissionError):
        rerank._connect("python3")
    assert folder.stat().st_mode & 0o777 == 0o700
