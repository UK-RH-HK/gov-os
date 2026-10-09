"""Builder tests for DEC-574: the held-out check resolves no string longer
than the system path limit, and keeps the literal check.

Regression evidence only (DEC-136).  The held-out path is a made-up
stand-in in a temporary directory, and so is the home folder; no file of
this repository is read here.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))
from gov.guard import heldout  # noqa: E402
from gov.guard.decide import MOST_PATH, decide  # noqa: E402
from gov.guard.heldout import CONFIG_KEY, CONFIG_REL  # noqa: E402

LIMIT = os.pathconf("/", "PC_PATH_MAX")
HELD_OUT = "the call names a held-out path"


@pytest.fixture
def world(tmp_path, monkeypatch):
    """A temporary project whose stand-in held-out file lists a stand-in
    folder, a link to that folder, and a stand-in home with the same link."""
    project = tmp_path / "project"
    (project / os.path.dirname(CONFIG_REL)).mkdir(parents=True)
    (project / "docs").mkdir()
    stand_in = tmp_path / "elsewhere" / "stand-in"
    stand_in.mkdir(parents=True)
    (stand_in / "answers.md").write_text("x\n", encoding="utf-8")
    (project / CONFIG_REL).write_text(f"{CONFIG_KEY}:\n- {stand_in}\n", encoding="utf-8")
    link = tmp_path / "a-link"
    link.symlink_to(stand_in, target_is_directory=True)
    home = tmp_path / "home"
    home.mkdir()
    (home / "a-link").symlink_to(stand_in, target_is_directory=True)
    monkeypatch.setenv("HOME", str(home))
    return project, stand_in, link


def _padded(start, length):
    """*start*, the current folder repeated, then the way to the stand-in's
    file through the link: exactly *length* characters, no literal path."""
    end = "a-link/answers.md"
    room = length - len(start) - len(end)
    text = start + "./" * (room // 2) + "/" * (room % 2) + end
    assert len(text) == length
    return text


def _calls(project, text):
    return [
        ("Write", {"file_path": str(project / "docs" / "notes.md"), "content": text}),
        ("Edit", {"file_path": str(project / "docs" / "notes.md"), "old_string": text, "new_string": "x"}),
        ("mcp__notes__add", {"note": {"body": ["a first note", text]}}),
        ("Bash", {"command": "cat " + text}),
    ]


def _decide(project, tool_name, tool_input):
    return decide(tool_name=tool_name, tool_input=tool_input, project_root=str(project),
                  role="orchestrator", ticket_id=None, cwd=str(project))


def test_a_string_at_the_limit_is_resolved_and_one_past_it_is_not(world):
    project, stand_in, link = world
    for length, expected in [(LIMIT - 1, ("deny", HELD_OUT)), (LIMIT, ("deny", HELD_OUT)),
                             (LIMIT + 1, ("allow", ""))]:
        text = _padded(f"{link.parent}/", length)
        assert str(stand_in) not in text
        for tool, call in _calls(project, text):
            assert _decide(project, tool, call) == expected, (tool, length)


def test_a_long_string_with_the_literal_path_stays_refused(world):
    project, stand_in, _ = world
    for size in (LIMIT + 1, 100_000):
        for text in (f"{stand_in}" + "a/" * size, "a/" * size + f"{stand_in}/answers.md",
                     "a/" * size + f"\n{stand_in}\n" + "a/" * size):
            for tool, call in _calls(project, text)[:3]:
                assert _decide(project, tool, call) == ("deny", HELD_OUT), (tool, size)
    command = "echo " + "a/" * LIMIT + f" {stand_in}"
    assert _decide(project, "Bash", {"command": command}) == ("deny", HELD_OUT)


def test_a_string_is_past_the_limit_only_as_written_and_as_expanded(world, monkeypatch):
    project, stand_in, link = world
    home = os.environ["HOME"]
    # Under the limit as written, over it as expanded: resolved.
    for tool, call in [
        ("Write", {"file_path": str(project / "docs" / "notes.md"), "content": _padded("~/", LIMIT - 2)}),
        ("Bash", {"command": "cat " + _padded("$HOME/", LIMIT - 2)}),
    ]:
        assert LIMIT - 2 + len(home) > LIMIT
        assert _decide(project, tool, call) == ("deny", HELD_OUT), tool
    # Over it both ways: not resolved.
    for tool, call in [
        ("Write", {"file_path": str(project / "docs" / "notes.md"), "content": _padded("~/", LIMIT + 1)}),
        ("Bash", {"command": "cat " + _padded("$HOME/", LIMIT + 1)}),
    ]:
        assert _decide(project, tool, call) == ("allow", ""), tool
    # Over the limit as written, under it as expanded: resolved.
    monkeypatch.setenv("HOME", "/")
    word = "${HOME}" * 700 + f"{str(link).lstrip('/')}/answers.md"
    assert len(word) > LIMIT > len(word) - 700 * 6 and str(stand_in) not in word
    assert _decide(project, "Bash", {"command": "cat " + word}) == ("deny", HELD_OUT)


def test_a_command_of_short_words_is_judged_word_by_word(world):
    project, stand_in, link = world
    command = "echo " + "a/b " * (LIMIT // 2) + f"; cat {link}/answers.md"
    assert len(command) > LIMIT and str(stand_in) not in command
    assert _decide(project, "Bash", {"command": command}) == ("deny", HELD_OUT)
    assert _decide(project, "Bash", {"command": "echo " + "a/b " * (LIMIT // 2)}) == ("allow", "")


@pytest.mark.parametrize("reported", [-1, 0, OSError(), ValueError()])
def test_a_system_that_reports_no_limit_gives_the_guard_s_own(world, monkeypatch, reported):
    project, _, link = world

    def pathconf(path, name):
        if isinstance(reported, Exception):
            raise reported
        return reported

    monkeypatch.setattr(os, "pathconf", pathconf)
    assert heldout._path_limit() == MOST_PATH
    at, over = (_padded(f"{link.parent}/", n) for n in (MOST_PATH, MOST_PATH + 1))
    assert _decide(project, "mcp__notes__add", {"note": at}) == ("deny", HELD_OUT)
    assert _decide(project, "mcp__notes__add", {"note": over}) == ("allow", "")


def test_the_limit_is_the_system_s_and_is_asked_once_for_a_decision(world, monkeypatch):
    project, _, link = world
    asked = []
    monkeypatch.setattr(os, "pathconf", lambda path, name: asked.append(name) or 64)
    call = {"notes": ["docs/a", "docs/b", f"{link}/answers.md".rjust(65, "/")], "more": "docs/c"}
    assert _decide(project, "mcp__notes__add", call) == ("allow", "")
    assert asked == ["PC_PATH_MAX"]


@pytest.mark.parametrize("text", [
    "a/" * (512 * 1024), "a/b\n" * (256 * 1024), "../" * (340 * 1024), "~/" * (512 * 1024),
])
def test_a_megabyte_of_path_like_text_is_answered_at_once(world, text):
    project, stand_in, _ = world
    started = time.perf_counter()
    for tool, call in _calls(project, text)[:3]:
        assert _decide(project, tool, call) == ("allow", ""), tool
    call = {"file_path": str(project / "docs" / "notes.md"), "old_string": text,
            "new_string": text + str(stand_in)}
    assert _decide(project, "Edit", call) == ("deny", HELD_OUT)
    assert time.perf_counter() - started < 1.0


@pytest.mark.parametrize("call", [
    {}, {"content": None}, {"content": 7, "file_path": ["a"]}, {"content": "a\x00/" * 3000},
    {"content": "\udcff/" * 3000}, {"content": "~" * 5000}, {"content": "~nobody-of-that-name/" * 500},
])
def test_no_input_makes_the_check_raise(world, monkeypatch, call):
    project, stand_in, _ = world
    for home in (os.environ["HOME"], "", None):
        if home is None:
            monkeypatch.delenv("HOME")
        else:
            monkeypatch.setenv("HOME", home)
        for tool in ("Write", "Bash", "mcp__notes__add"):
            assert heldout.names_held_out(tool, dict(call), str(project), str(project),
                                          [str(stand_in)]) is False
    assert heldout.names_held_out("Bash", {"command": "cat '" + "a/" * 3000}, str(project),
                                  str(project), [str(stand_in)]) is False
