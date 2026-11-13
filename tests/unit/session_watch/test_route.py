"""P-W2-159-1 (a): a hyphenated command maps to its underscore folder, in the command line and in the recorded list."""

from __future__ import annotations

from gov.cli import main as cli
from gov.check import commands


def test_a_hyphenated_name_finds_its_underscore_folder():
    assert cli._module_name("session-watch") == "gov.session_watch.command"
    assert "session-watch" in cli._known() and "session_watch" not in cli._known()
    assert cli._module_name("dispatch") == "gov.dispatch.command"  # a name without a hyphen is unchanged
    assert cli._module_name("no-such-command") is None


def test_the_command_is_declared_by_its_module():
    command = cli._load(cli._known()["session-watch"], reserved=False)
    assert command.fault is None and command.child_exit_code and command.cls == "act"
    assert command.act_paths == (".gov-runtime/session-watch/**", ".gov-runtime/dispatch/inbox/**")


def test_session_watch_is_recorded_and_its_module_is_looked_up_in_the_underscore_folder(tmp_path):
    assert "session-watch" in commands.RECORDED_GOV_COMMANDS and "session-watch" in commands.GOV_COMMANDS
    for command in commands.GOV_COMMANDS:
        (tmp_path / "src" / "gov" / command.replace("-", "_")).mkdir(parents=True, exist_ok=True)
        (tmp_path / "src" / "gov" / command.replace("-", "_") / "command.py").write_text("")
    (tmp_path / "src" / "gov" / "lock").mkdir()
    (tmp_path / "src" / "gov" / "lock" / "__main__.py").write_text("")
    assert commands.check(tmp_path) == []
    (tmp_path / "src" / "gov" / "session_watch" / "command.py").unlink()
    assert [f["command"] for f in commands.check(tmp_path)] == ["session-watch"]


def _plant_every_command(root, folder_of):
    for command in commands.GOV_COMMANDS:
        folder = root / "src" / "gov" / folder_of(command)
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "command.py").write_text("")
    (root / "src" / "gov" / "lock").mkdir(exist_ok=True)
    (root / "src" / "gov" / "lock" / "__main__.py").write_text("")


def test_the_existence_check_takes_the_underscore_folder_alone_and_finds_no_folder(tmp_path):
    _plant_every_command(tmp_path, lambda command: command.replace("-", "_"))
    assert not (tmp_path / "src" / "gov" / "session-watch").exists()  # the underscore folder alone
    assert commands.check(tmp_path) == []
    # a folder of the command's own name, as it is, passes as well
    own = tmp_path / "own"
    _plant_every_command(own, lambda command: command)
    assert commands.check(own) == []
    # no folder at all: a finding
    (tmp_path / "src" / "gov" / "session_watch" / "command.py").unlink()
    assert [f["command"] for f in commands.check(tmp_path)] == ["session-watch"]
