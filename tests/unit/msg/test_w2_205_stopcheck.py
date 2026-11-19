"""The Stop check (W2-205, RT-2): blocks only for an unread wake message, once per message id."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.dispatch import inbox  # noqa: E402
from gov.msg import stopcheck  # noqa: E402

ME = "worker:T-1:engineer"


@pytest.fixture
def home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv("GOV_MSG_ADDRESS", raising=False)
    return tmp_path / "home"


def test_an_unread_wake_blocks_once_with_its_text(home):
    inbox.send(ME, "wake", "the heavy job ended", sender="runtime", message_id="m1")
    first = stopcheck.check(ME)
    assert first["decision"] == "block" and "the heavy job ended" in first["reason"]
    assert stopcheck.check(ME) is None


def test_a_newer_wake_blocks_once_more_and_not_for_the_old_one_again(home):
    inbox.send(ME, "wake", "one", message_id="m1")
    assert stopcheck.check(ME) is not None
    inbox.send(ME, "wake", "two", message_id="m2")
    second = stopcheck.check(ME)
    assert "two" in second["reason"] and "one" not in second["reason"]
    assert stopcheck.check(ME) is None


def test_a_notice_or_a_relay_never_blocks(home):
    inbox.send(ME, "notice", "fyi")
    inbox.send(ME, "relay", "via the owner")
    assert stopcheck.check(ME) is None


def test_nothing_unread_passes(home):
    assert stopcheck.check(ME) is None


def test_no_address_passes_even_with_unread_wakes_elsewhere(home):
    inbox.send(ME, "wake", "hello")
    assert stopcheck.check(None) is None
    assert stopcheck.check("") is None


def test_an_address_that_is_none_passes(home):
    assert stopcheck.check("../x") is None


def test_a_wake_already_read_does_not_block(home):
    inbox.send(ME, "wake", "hello")
    inbox.read(ME)
    assert stopcheck.check(ME) is None


def test_the_check_does_not_move_the_read_mark(home):
    inbox.send(ME, "wake", "hello")
    stopcheck.check(ME)
    assert len(inbox.read(ME, peek=True)["messages"]) == 1


def test_the_address_defaults_to_the_environment(home, monkeypatch):
    monkeypatch.setenv("GOV_MSG_ADDRESS", ME)
    inbox.send(ME, "wake", "hello")
    assert stopcheck.check()["decision"] == "block"


def test_a_stop_seen_file_that_is_garbled_blocks_for_what_it_does_not_hold(home):
    inbox.send(ME, "wake", "hello", message_id="m1")
    (inbox.folder(ME) / stopcheck.SEEN).write_text("not json\n[1]\n")
    assert stopcheck.check(ME) is not None


def test_an_id_with_a_newline_is_still_once(home):
    inbox.send(ME, "wake", "hello", message_id="a\nb")
    assert stopcheck.check(ME) is not None
    assert stopcheck.check(ME) is None
