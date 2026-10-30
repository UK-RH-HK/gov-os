"""The routes of the serial-only list and the close's serial phase (``gov.close.serial``, W2-57 run 2)."""
from __future__ import annotations

import pytest

from gov.close import serial
from gov.close.pytest_plugin import gov_close_serial_only as serial_only


def _list(tmp_path, text: str | bytes):
    path = tmp_path / serial_only.LIST_REL
    path.parent.mkdir(parents=True)
    (path.write_bytes if isinstance(text, bytes) else path.write_text)(text)
    return tmp_path


def test_a_nightly_entry_is_left_out_and_a_serial_one_kept_in_order(tmp_path):
    root = _list(tmp_path, "# a comment line: nightly: not an entry\n"
                           "tests/a.py::test_one  # serial: latency: alone\n"
                           "tests/b.py  # nightly: live-session: a real session\n"
                           "tests/c.py::test_two  # serial: race: raced\n")
    assert serial.nightly(root) == {"tests/b.py"}
    assert serial.phase(root, ["tests/c.py::test_two", "tests/b.py", "tests/a.py::test_one"]) == [
        "tests/c.py::test_two", "tests/a.py::test_one"]


@pytest.mark.parametrize("line", [
    "tests/d.py",  # no comment
    "tests/d.py  # weekly: real-model: an unknown first word",
    "tests/d.py  # Nightly: real-model: not the word itself",
    "tests/d.py  # nightly real-model without its colon",
    "tests/d.py  #",
])
def test_an_entry_whose_route_cannot_be_read_stays_in_the_serial_phase(tmp_path, line):
    root = _list(tmp_path, line + "\n")
    assert serial.nightly(root) == set()
    assert serial.phase(root, ["tests/d.py"]) == ["tests/d.py"]


def test_an_entry_a_second_line_keeps_serial_stays(tmp_path):
    root = _list(tmp_path, "tests/e.py  # nightly: real-model: x\ntests/e.py  # serial: latency: y\n")
    assert serial.phase(root, ["tests/e.py"]) == ["tests/e.py"]


def test_every_entry_nightly_leaves_the_serial_phase_empty(tmp_path):
    root = _list(tmp_path, "tests/f.py  # nightly: real-model: x\ntests/g.py::t  #  nightly : live-session: y\n")
    assert serial.phase(root, ["tests/f.py", "tests/g.py::t"]) == []


def test_without_a_list_nothing_is_routed(tmp_path):
    assert serial.nightly(tmp_path) == set()
    assert serial.phase(tmp_path, ["tests/h.py"]) == ["tests/h.py"]


def test_a_list_that_is_no_utf8_text_is_never_read_as_no_list(tmp_path):
    root = _list(tmp_path, b"tests/i.py  # nightly: caf\xe9\n")
    with pytest.raises(UnicodeDecodeError):
        serial.phase(root, ["tests/i.py"])


def test_the_entries_are_the_plugins_own(tmp_path):
    root = _list(tmp_path, "  tests/j.py::test_k   # nightly: real-model: x\n")
    assert serial_only.entries(root) == ["tests/j.py::test_k"]
    assert serial.nightly(root) == {"tests/j.py::test_k"}
