"""W2-88 run 8b, the CTO's P2 under DEC-338: a runtime folder whose socket path would pass 107 bytes is moved short.

Regression evidence only (DEC-136). ``codebase-memory-mcp`` 0.11.0 puts its socket at
``<CBM_RUNTIME_DIR>/cbm-daemon-<uid>/cbm-<16 hex>.sock`` (its daemon's pending name ``.sock.pending`` is counted too),
and a socket path holds at most 107 bytes: over it the tool fails ("secure CLI coordination could not be created
(endpoint)"). ``daemon_dir`` keeps every folder whose socket fits where W2-56 puts it, byte for byte; a longer one is
replaced by ``/tmp/gov-cbm-<uid>/<12 hex of the sha256 of the long folder's real path>``, made 0700; a short folder
that cannot be made, or is still too long, is refused by name (``CODEGRAPH_RUNTIME_PATH_TOO_LONG``).
"""
from __future__ import annotations

import hashlib
import os
import stat
from pathlib import Path

import pytest

from gov import codeintel
from gov.adopt import fabric
from gov.cli.errors import GovError

TAIL = f"/cbm-daemon-{os.getuid()}/cbm-{'0' * 16}.sock.pending"  # counted independently of the module


@pytest.fixture(autouse=True)
def places(tmp_path, monkeypatch):
    """No launched session's folder and no mark; the short folders' place is the real one unless a case moves it."""
    monkeypatch.delenv(codeintel.BASE_ENV, raising=False)
    monkeypatch.delenv(codeintel.LAUNCH_TMP_ENV, raising=False)
    monkeypatch.setattr(codeintel, "DAEMON_BASE", tmp_path / "daemons")
    monkeypatch.setattr(codeintel, "SHORT_BASE", Path(f"/tmp/gov-cbm-{os.getuid()}"))


def _sha(text: str, width: int) -> str:
    return hashlib.sha256(os.fsencode(text)).hexdigest()[:width]


def _base_for(socket_length: int) -> str:
    """An absolute base whose daemon folder's socket path is ``socket_length`` bytes."""
    stem = "/tmp/w288-"
    pad = socket_length - len(stem) - 17 - len(TAIL)  # 17: "/" and the 16 hex of the repository's folder
    return stem + "b" * pad


def test_the_socket_rule_counts_the_tools_own_names():
    assert codeintel.SOCKET_MAX == 107
    assert codeintel.socket_length(Path("/r")) == len("/r" + TAIL)


def test_a_short_base_keeps_its_folder_byte_for_byte(tmp_path, monkeypatch):
    root = tmp_path / "one"
    for base in ("/tmp/s", _base_for(107)):  # a short one, and one whose socket is exactly at the limit
        monkeypatch.setenv(codeintel.BASE_ENV, base)
        made = codeintel.daemon_dir(root)
        assert str(made) == f"{base}/{_sha(str(root.resolve()), 16)}"
        assert len(os.fsencode(str(made) + TAIL)) <= 107


def test_a_long_base_gets_the_short_per_session_folder(tmp_path, monkeypatch):
    root = tmp_path / "one"
    base = _base_for(108)  # one byte over
    monkeypatch.setenv(codeintel.BASE_ENV, base)
    long = f"{base}/{_sha(str(root.resolve()), 16)}"
    made = codeintel.daemon_dir(root)
    assert str(made) == f"/tmp/gov-cbm-{os.getuid()}/{_sha(os.path.realpath(long), 12)}"
    assert len(os.fsencode(str(made) + TAIL)) <= 107


def test_two_long_bases_get_two_folders(tmp_path, monkeypatch):
    root = tmp_path / "one"
    found = set()
    for base in (str(tmp_path / ("x" * 90)), str(tmp_path / ("y" * 90))):
        monkeypatch.setenv(codeintel.BASE_ENV, base)
        found.add(codeintel.daemon_dir(root))
    assert len(found) == 2 and all(made.parent == Path(f"/tmp/gov-cbm-{os.getuid()}") for made in found)


def test_the_short_folder_is_made_0700_under_the_users_own_folder(tmp_path, monkeypatch):
    """The short folder made by ``_daemon_dir``: here under a test folder, with the limit set so that it fits and the
    long one does not (the real ``/tmp`` is not written by a unit case)."""
    short_base = tmp_path / "s"
    monkeypatch.setattr(codeintel, "SHORT_BASE", short_base)
    monkeypatch.setattr(codeintel, "SOCKET_MAX", codeintel.socket_length(short_base / ("0" * 12)))
    monkeypatch.setenv(codeintel.BASE_ENV, str(tmp_path / ("x" * 40)))
    made = codeintel._daemon_dir(tmp_path / "one")
    assert made.parent == short_base and len(made.name) == 12 and made.is_dir()
    assert stat.S_IMODE(made.stat().st_mode) == 0o700 and stat.S_IMODE(short_base.stat().st_mode) == 0o700
    assert not (tmp_path / ("x" * 40)).exists()  # the long folder is not made


def test_a_short_folder_still_too_long_is_refused_by_name(tmp_path, monkeypatch):
    short_base = tmp_path / ("z" * 120)
    monkeypatch.setattr(codeintel, "SHORT_BASE", short_base)
    monkeypatch.setenv(codeintel.BASE_ENV, str(tmp_path / ("x" * 90)))
    with pytest.raises(codeintel.RuntimePathTooLong) as caught:
        codeintel._daemon_dir(tmp_path / "one")
    said = str(caught.value)
    assert said.startswith("CODEGRAPH_RUNTIME_PATH_TOO_LONG") and caught.value.code == "CODEGRAPH_RUNTIME_PATH_TOO_LONG"
    short = codeintel.daemon_dir(tmp_path / "one")
    assert str(short) in said and str(codeintel.socket_length(short)) in said and "107" in said
    assert not short_base.exists()


@pytest.mark.parametrize("kind", ("file", "link"))
def test_a_short_folder_that_cannot_be_made_is_refused_by_name(tmp_path, monkeypatch, kind):
    if kind == "file":
        (tmp_path / "f").write_text("", encoding="utf-8")
        short_base = tmp_path / "f" / "s"  # under a regular file: no folder can be made
    else:
        (tmp_path / "elsewhere").mkdir()
        short_base = tmp_path / "s"
        short_base.symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    monkeypatch.setattr(codeintel, "SHORT_BASE", short_base)
    monkeypatch.setattr(codeintel, "SOCKET_MAX", codeintel.socket_length(short_base / ("0" * 12)))
    long_base = tmp_path / ("x" * 40)
    monkeypatch.setenv(codeintel.BASE_ENV, str(long_base))
    with pytest.raises(codeintel.RuntimePathTooLong) as caught:
        codeintel._daemon_dir(tmp_path / "one")
    assert str(caught.value).startswith("CODEGRAPH_RUNTIME_PATH_TOO_LONG") and str(long_base) in str(caught.value)
    if kind == "link":
        assert not list((tmp_path / "elsewhere").iterdir())


def test_a9_shows_the_refusals_name(tmp_path, monkeypatch):
    """``fabric`` maps the codeintel refusal to a GovError of the same code, not a bare FABRIC_INCOMPLETE."""
    monkeypatch.setattr(codeintel, "SHORT_BASE", tmp_path / ("z" * 120))
    monkeypatch.setenv(codeintel.BASE_ENV, str(tmp_path / ("x" * 90)))
    with pytest.raises(codeintel.RuntimePathTooLong) as caught:
        codeintel._daemon_dir(tmp_path / "one")
    error = fabric.runtime_too_long(caught.value)
    assert isinstance(error, GovError) and error.code == "CODEGRAPH_RUNTIME_PATH_TOO_LONG"
    assert error.details["limit"] == 107 and error.details["length"] == caught.value.length
    assert error.details["path"] == str(caught.value.path)
