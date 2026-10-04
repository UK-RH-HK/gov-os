"""Builder tests for the command-module convention of ``gov.cli.main`` (DEC-317).

Regression evidence only (DEC-136). A stand-in ``pause`` module is written
to a temporary package directory; ``src/gov/pause/`` is not created. The
stand-in was ``checkpoint`` until W1-25 built that command; it has to be a
reserved command that is not built yet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

import gov  # noqa: E402
from gov.cli import main as cli  # noqa: E402

PAUSE = '''
from gov.cli.errors import GovError
ACT_PATHS = (".gov-runtime/pauses/**",)
EXIT_CODES = {3: "verification failed"}

def add_arguments(parser):
    parser.add_argument("--watch", action="store_true")
    parser.add_argument("--resume", metavar="<id>")

def run(root, args, config):
    if args.resume == "error":
        raise GovError("PAUSE_UNVERIFIED", "not verified", {"id": args.resume}, exit_code=3)
    if args.resume == "undeclared":
        raise GovError("PAUSE_OTHER", "other", exit_code=4)
    if args.resume == "bare-int":
        return 3
    if args.watch:
        return {"watch": True}, 3
    return {"resume": args.resume}
'''


@pytest.fixture
def package(tmp_path, monkeypatch):
    """A package directory beside ``src/gov``, with the files of the commands built today."""
    for rel in ("cli/commands/status.py", "cli/commands/check.py", "launch/command.py"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text("", encoding="utf-8")
    monkeypatch.setattr(cli, "PACKAGE", tmp_path)
    monkeypatch.setattr(gov, "__path__", [*gov.__path__, str(tmp_path)])
    yield tmp_path
    for name in [name for name in sys.modules if name.startswith("gov.pause")]:
        del sys.modules[name]


def _pause(package, text):
    (package / "pause").mkdir()
    (package / "pause" / "__init__.py").write_text("", encoding="utf-8")
    (package / "pause" / "command.py").write_text(text, encoding="utf-8")


def _run(capsys, root, *args):
    code = cli.main([*args, "--json", "--root", str(root)])
    return code, json.loads(capsys.readouterr().out)


def test_a_module_alone_builds_a_reserved_command_with_its_arguments_and_exit_code(package, tmp_path, capsys):
    _pause(package, PAUSE)
    assert _run(capsys, tmp_path, "pause", "--resume", "c1") == (
        0, {"ok": True, "command": "pause", "result": {"resume": "c1"}, "session": ""})
    code, envelope = _run(capsys, tmp_path, "pause", "--watch")
    assert code == 3 and envelope["ok"] is True and envelope["result"] == {"watch": True}
    code, envelope = _run(capsys, tmp_path, "pause", "--resume", "error")
    assert code == 3 and envelope["error"]["code"] == "PAUSE_UNVERIFIED"
    loaded = cli._load(cli._known()["pause"], True)
    assert loaded.act_paths == (".gov-runtime/pauses/**",) and loaded.exit_codes == (3,) and loaded.cls == "act"


def test_an_exit_code_the_module_does_not_declare_ends_as_1(package, tmp_path, capsys):
    _pause(package, PAUSE)
    code, envelope = _run(capsys, tmp_path, "pause", "--resume", "undeclared")
    assert code == 1 and envelope["error"]["code"] == "PAUSE_OTHER"
    code, envelope = _run(capsys, tmp_path, "pause", "--resume", "bare-int")
    assert code == 1 and envelope["error"]["code"] == cli.MODULE_INVALID


def test_an_argument_the_module_does_not_declare_is_a_usage_error(package, tmp_path, capsys):
    _pause(package, PAUSE)
    for args in (["pause", "--no-such-option"], ["pause", "--", "x"]):
        with pytest.raises(SystemExit) as stop:
            cli.main(args)
        assert stop.value.code == 2


def test_without_a_module_the_command_stays_reserved(package, tmp_path, capsys):
    code, envelope = _run(capsys, tmp_path, "pause", "--watch")
    assert code == 1 and envelope["error"]["code"] == "NOT_IMPLEMENTED"


@pytest.mark.parametrize("text", (
    "raise RuntimeError('broken')\n",
    "import sys\nsys.exit(0)\n",
    "import no_such_module_w1_46\n",
    "RUN = 1\n",
    "EXIT_CODES = {1: 'mine'}\ndef run(root, args, config):\n    return {}\n",
    "EXIT_CODES = {2: 'mine'}\ndef run(root, args, config):\n    return {}\n",
    "EXIT_CODES = [3]\ndef run(root, args, config):\n    return {}\n",
    "ACT_PATHS = 'docs/**'\ndef run(root, args, config):\n    return {}\n",
    "def add_arguments(parser):\n    parser.add_argument('--json')\ndef run(root, args, config):\n    return {}\n",
), ids=("raises", "exits", "import-error", "no-run", "declares-1", "declares-2", "codes-not-a-dict",
        "act-paths-not-a-tuple", "argument-conflict"))
def test_a_faulty_module_fails_its_own_command_and_no_other(package, tmp_path, capsys, text):
    _pause(package, text)
    code, envelope = _run(capsys, tmp_path, "pause", "--watch")
    assert code == 1 and envelope["ok"] is False and envelope["error"]["code"] == cli.MODULE_INVALID
    code, envelope = _run(capsys, tmp_path, "status")
    assert code == 0 and envelope["ok"] is True
    code, envelope = _run(capsys, tmp_path, "close")
    assert code == 1 and envelope["error"]["code"] == "NOT_IMPLEMENTED"
    with pytest.raises(SystemExit) as stop:
        cli.main(["--help"])
    assert stop.value.code == 0 and "pause" in capsys.readouterr().out


def test_a_faulty_module_does_not_let_gov_launch_skip_a_refusal(package, tmp_path, capsys):
    _pause(package, "import sys\nsys.exit(0)\n")
    code = cli.main(["launch", "engineer", "DAEO-none", "--json", "--root", str(tmp_path), "--",
                     "--dangerously-skip-permissions"])
    envelope = json.loads(capsys.readouterr().out)
    assert code == 1 and envelope["error"]["code"] == "LAUNCH_REFUSED"
    assert "gov.pause.command" not in sys.modules, "a command that was not named had its module imported"


def test_a_read_command_may_not_declare_act_paths(package, tmp_path, capsys):
    (package / "cli" / "commands" / "doctor.py").write_text("", encoding="utf-8")
    module = type(sys)("gov.cli.commands.doctor")
    module.run, module.ACT_PATHS = (lambda root, args, config: {}), ("docs/**",)
    sys.modules[module.__name__] = module
    try:
        code, envelope = _run(capsys, tmp_path, "doctor")
    finally:
        del sys.modules[module.__name__]
    assert code == 1 and envelope["error"]["code"] == cli.MODULE_INVALID


def test_gov_launch_is_found_through_its_module_and_keeps_its_usage(capsys):
    assert "launch" in cli._known() and "launch" not in {command.name for command in cli.COMMANDS}
    loaded = cli._load(cli._known()["launch"], False)
    assert loaded.fault is None and loaded.passthrough and loaded.child_exit_code
    with pytest.raises(SystemExit) as stop:
        cli.main(["launch"])
    assert stop.value.code == 2 and "gov launch <role> <ticket>" in capsys.readouterr().err
