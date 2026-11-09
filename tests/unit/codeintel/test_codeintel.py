"""Builder tests for the codebase-memory wrapper (W1-16).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: when the filter cannot decide, the earlier index is gone and
none is built; the tool is given the staged folder, the repository's home and
the repository's daemon directory, not the caller's (DEC-338); before every call
the tool is told, in the same home and daemon directory, to keep its UI off, and
a refusal of that fails the call (DEC-362); that directory
is short, and one that is not the user's own is refused; a file whose path
holds a secret is not
staged; a root that is no top level of a git repository, or whose
``.gov-runtime`` is a link, is refused with nothing written or deleted; and a
tool that reports an error is not an empty answer; one load of the graph asks
both queries, pages included, in one start of the tool, and a session that
fails or hangs is a refusal (DEC-561). The codebase-memory binary is not run: a stand-in script on
``PATH`` records how it is called. Every repository is a temporary directory,
and so is the place of the daemon directories: nothing is left in ``/tmp``.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import codeintel  # noqa: E402

MAP = "namespaces:\n  everything: {paths: ['**'], memory_class: governance}\n"
PLANTED = "_".join(["W116", "UNIT", "CAN" + "ARY", "6TR1"])
# A stand-in for the binary: it writes its arguments and two variables of its environment next to itself.
STAND_IN = ("#!/bin/sh\n"
            "here=$(dirname \"$0\")\n"
            "printf '%s\\n' \"$@\" \"$CBM_CACHE_DIR\" \"$CBM_RUNTIME_DIR\" > \"$here/call.txt\"\n"
            "echo \"$1 $2 $3 $4|$CBM_CACHE_DIR|$CBM_RUNTIME_DIR\" >> \"$here/calls.txt\"\n"  # every call, in order
            "[ ! -e \"$here/refuse-$1\" ] || exit 1\n"
            "cat \"$here/answer.json\"\n")


SOCKET_TAIL = len(f"/cbm-daemon-{os.getuid()}/cbm-{'0' * 16}.sock.pending")  # the tool's socket under its folder


@pytest.fixture(autouse=True)
def daemon_base(tmp_path, monkeypatch):
    """The daemon directories in this test's folder: no test session's folder, no launched session's (W2-56 S1)."""
    monkeypatch.delenv(codeintel.BASE_ENV, raising=False)
    monkeypatch.delenv(codeintel.LAUNCH_TMP_ENV, raising=False)
    monkeypatch.setattr(codeintel, "DAEMON_BASE", tmp_path / "daemons")
    return tmp_path / "daemons"


def _repository(root):
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for rel, text in {"governance/project/path-map.yaml": MAP, "app/clean.py": "def clean():\n    return 1\n",
                      "app/planted.py": f"def {PLANTED}():\n    return 2\n", ".gitignore": ".gov-runtime/\n"}.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text, encoding="utf-8")
    return root


def _stand_in(tmp_path, monkeypatch, answer):
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / codeintel.TOOL).write_text(STAND_IN, encoding="utf-8")
    (tools / codeintel.TOOL).chmod(0o755)
    (tools / "answer.json").write_text(json.dumps(answer), encoding="utf-8")
    monkeypatch.setenv("PATH", str(tools), prepend=":")
    return tools / "call.txt"


def test_no_index_is_left_when_the_filter_cannot_decide(tmp_path):
    root = _repository(tmp_path / "repo")  # no .gitleaks.toml: the filter raises
    earlier = codeintel.home(root) / "code.db"
    earlier.parent.mkdir(parents=True)
    earlier.write_text("an earlier index", encoding="utf-8")
    with pytest.raises(RuntimeError):
        codeintel.index(root)
    assert not (root / codeintel.BASE_REL).exists()


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
def test_the_tool_is_given_the_staged_files_the_home_and_the_repositorys_daemon_directory(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    call = _stand_in(tmp_path, monkeypatch, {"isError": False, "content": [{"type": "text", "text": "{}"}]})
    monkeypatch.setenv("CBM_RUNTIME_DIR", str(tmp_path / "runtime"))
    codeintel.index(root)
    *_, tool, arguments, cache, runtime = call.read_text(encoding="utf-8").splitlines()
    staged = root / codeintel.BASE_REL / "files"
    assert tool == "index_repository" and json.loads(arguments)["repo_path"] == str(staged)
    assert cache == str(codeintel.home(root)) and runtime == str(codeintel.daemon_dir(root))
    assert codeintel.daemon_dir(root).is_dir() and not (tmp_path / "runtime").exists()
    files = sorted(path.relative_to(staged).as_posix() for path in staged.rglob("*") if path.is_file())
    assert files == [".gitignore", ".gitleaks.toml", "app/clean.py", "governance/project/path-map.yaml"]


def test_the_ui_is_turned_off_in_the_home_before_every_call_and_a_refusal_fails_the_call(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    answer = {"isError": False, "content": [{"type": "text", "text": "{\"projects\": []}"}]}
    call = _stand_in(tmp_path, monkeypatch, answer)
    monkeypatch.setenv("CBM_RUNTIME_DIR", str(tmp_path / "runtime"))
    places = f"|{codeintel.home(root)}|{codeintel.daemon_dir(root)}"
    assert codeintel.projects(root) == [] and codeintel.projects(root) == []
    first, second, third, fourth = call.with_name("calls.txt").read_text(encoding="utf-8").splitlines()
    assert first == third == "config set ui_enabled false" + places  # in the repository's home, not the caller's
    assert second == fourth == "cli --quiet --json list_projects" + places
    call.with_name("refuse-config").touch()
    with pytest.raises(RuntimeError):
        codeintel.projects(root)
    assert call.with_name("calls.txt").read_text(encoding="utf-8").splitlines()[4:] == [first]  # no cli call after it


def test_the_daemon_directory_is_short_and_one_per_repository(tmp_path, monkeypatch):
    monkeypatch.setattr(codeintel, "DAEMON_BASE", Path(f"/tmp/gov-cbm-{os.getuid()}"))  # the place outside a test
    first, second = codeintel.daemon_dir(tmp_path / "one"), codeintel.daemon_dir(tmp_path / "two")
    assert first != second and first.parent == second.parent == Path(f"/tmp/gov-cbm-{os.getuid()}")
    assert len(str(first)) <= 107 - SOCKET_TAIL
    assert not first.exists() and not second.exists()


def test_a_test_sessions_folder_holds_its_daemon_directories(tmp_path, monkeypatch):
    """W2-56 S1: ``GOV_CBM_BASE`` (the conftest's folder for one test session) comes first, whatever else is set."""
    monkeypatch.setenv(codeintel.BASE_ENV, str(tmp_path / "session"))
    monkeypatch.setenv(codeintel.LAUNCH_TMP_ENV, "/tmp/gov-launch-abcd1234/claude-1000")
    assert codeintel.daemon_dir(tmp_path / "one").parent == tmp_path / "session"


@pytest.mark.parametrize("given", ("/tmp/gov-launch-abcd1234", "/tmp/gov-launch-abcd1234/claude-1000",
                                   "/tmp/gov-launch-abcd1234/claude-1000/"))
def test_a_launched_sessions_daemon_directory_is_under_its_own_temp_folder(tmp_path, monkeypatch, given):
    """W2-56 S1, D-12: found from CLAUDE_CODE_TMPDIR (the launcher's folder, or the CLI's claude-<uid> in it), whatever
    TMPDIR says; short enough for the tool's socket."""
    monkeypatch.setenv(codeintel.LAUNCH_TMP_ENV, given)
    monkeypatch.setenv("TMPDIR", "/tmp/gov-launch-abcd1234/claude-1000/pytest/deeper")
    made = codeintel.daemon_dir(tmp_path / "one")
    assert made.parent == Path("/tmp/gov-launch-abcd1234") / codeintel.LAUNCH_SUB
    assert len(str(made)) + SOCKET_TAIL <= 107


@pytest.mark.parametrize("given", ("", "relative/gov-launch-x", "/tmp/claude-1000", "/tmp/other/claude-1000/deep"))
def test_outside_a_launched_session_the_default_place_holds(monkeypatch, tmp_path, daemon_base, given):
    monkeypatch.setenv(codeintel.LAUNCH_TMP_ENV, given)
    assert codeintel.daemon_dir(tmp_path / "one").parent == daemon_base


def test_a_test_sessions_folder_is_short_and_made_in_the_launched_sessions_folder(tmp_path, monkeypatch):
    launched = tmp_path / "gov-launch-abcd1234"
    launched.mkdir()
    monkeypatch.setenv(codeintel.LAUNCH_TMP_ENV, str(launched / "claude-1000"))
    made = codeintel.make_session_base()
    assert made.parent == launched and made.is_dir() and len(made.name) == 4
    older = "/tmp/gov-launch-engineer-abcd1234"  # an engineer's folder of the older name (role and 8 letters)
    assert len(older) + len("/cxyz") + 17 + SOCKET_TAIL <= 107


def test_the_running_suite_has_a_folder_of_its_own_and_no_code_graph_tool_on_path(monkeypatch):
    """W2-56 S1, through tests/conftest.py: this session's folder is named, and the real tool is off PATH here."""
    monkeypatch.undo()
    base = os.environ.get(codeintel.BASE_ENV)
    assert base and Path(base).is_dir()
    assert shutil.which(codeintel.TOOL) is None


def test_a_daemon_directory_that_is_not_the_users_own_is_refused(tmp_path, daemon_base):
    root = _repository(tmp_path / "repo")
    daemon_base.mkdir()
    (tmp_path / "elsewhere").mkdir()
    codeintel.daemon_dir(root).symlink_to(tmp_path / "elsewhere", target_is_directory=True)
    with pytest.raises(RuntimeError):
        codeintel.projects(root)
    assert not list((tmp_path / "elsewhere").iterdir())


@pytest.mark.skipif(shutil.which("gitleaks") is None, reason="gitleaks is not on PATH")
def test_a_file_whose_path_holds_a_secret_is_not_staged(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    shutil.copy2(REPO / "template/.gitleaks.toml", root / ".gitleaks.toml")
    for rel in (f"app/{PLANTED}.py", f"web/{PLANTED}/panel.py", "web/beside.py"):  # clean content, all three
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text("def other():\n    return 3\n", encoding="utf-8")
    _stand_in(tmp_path, monkeypatch, {"isError": False, "content": [{"type": "text", "text": "{}"}]})
    codeintel.index(root)
    staged = root / codeintel.BASE_REL / "files"
    assert not [path for path in staged.rglob("*") if PLANTED in path.name]
    assert (staged / "web/beside.py").is_file() and (staged / "app/clean.py").is_file()


def test_a_root_that_is_no_top_level_of_a_repository_is_refused_and_nothing_changes(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    plain = tmp_path / "plain"
    earlier = codeintel.home(plain) / "code.db"
    earlier.parent.mkdir(parents=True)
    earlier.write_text("an earlier index", encoding="utf-8")
    call = _stand_in(tmp_path, monkeypatch, {"isError": False, "content": [{"type": "text", "text": "{}"}]})
    for refused in (root / "app", plain):
        with pytest.raises(RuntimeError):
            codeintel.index(refused)
        with pytest.raises(RuntimeError):
            codeintel.projects(refused)
    assert not (root / "app/.gov-runtime").exists() and earlier.read_text(encoding="utf-8") == "an earlier index"
    assert not call.exists()  # the tool was never run


def test_a_gov_runtime_that_is_a_link_is_refused(tmp_path):
    root = _repository(tmp_path / "repo")
    outside = tmp_path / "outside"
    outside.mkdir()
    (root / ".gov-runtime").symlink_to(outside, target_is_directory=True)
    with pytest.raises(RuntimeError):
        codeintel.index(root)
    assert not list(outside.iterdir()) and (root / ".gov-runtime").is_symlink()


def test_an_error_of_the_tool_is_not_an_empty_answer(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    _stand_in(tmp_path, monkeypatch, {"isError": True, "content": [{"type": "text", "text": "{\"error\": \"x\"}"}]})
    with pytest.raises(RuntimeError):
        codeintel.definitions(root, "clean")
    with pytest.raises(RuntimeError):
        codeintel.projects(root)


# A stand-in that is also a server on its standard input and output: every start of it is a line of starts.txt.
# It answers two rows at a time, so that a query of the graph has pages.
SERVER = (f"#!{sys.executable}\n"
          "import json, os, sys, time\n"
          "here = os.path.dirname(os.path.abspath(__file__))\n"
          "with open(here + '/starts.txt', 'a') as log:\n"
          "    print(' '.join(sys.argv[1:]), os.environ['CBM_CACHE_DIR'], os.environ['CBM_RUNTIME_DIR'], sep='|', file=log)\n"
          "if sys.argv[1:2] == ['config']:\n"
          "    sys.exit(0)\n"
          "if os.path.exists(here + '/refuse'):\n"
          "    sys.exit(7)\n"
          "with open(here + '/rows.json') as handle:\n"
          "    rows = json.load(handle)\n"
          "for line in sys.stdin:\n"
          "    asked = json.loads(line)\n"
          "    if 'id' not in asked:\n"
          "        continue\n"
          "    result = {'protocolVersion': asked['params'].get('protocolVersion'), 'capabilities': {}}\n"
          "    if asked['method'] == 'tools/call':\n"
          "        if os.path.exists(here + '/hang'):\n"
          "            time.sleep(60)\n"
          "        given = asked['params']['arguments']\n"
          "        kind, at = 'edges' if 'type(r)' in given['query'] else 'nodes', given['offset']\n"
          "        page = {'rows': rows[kind][at:at + 2], 'has_more': at + 2 < len(rows[kind])}\n"
          "        result = {'isError': False, 'content': [{'type': 'text', 'text': json.dumps(page)}]}\n"
          "    print(json.dumps({'jsonrpc': '2.0', 'id': asked['id'], 'result': result}), flush=True)\n")


def _server(tmp_path, monkeypatch, root):
    """The stand-in server on ``PATH``, with a graph of four functions of one staged file. Returns its folder."""
    staged = root / codeintel.BASE_REL / "files/app/flow.py"
    staged.parent.mkdir(parents=True)
    staged.touch()
    key = "code.app.flow."
    rows = {"nodes": [[key + name, name, "Function", "app/flow.py"] for name in ("top", "mid", "leaf", "side")],
            "edges": [[key + "top", "CALLS", key + "mid"], [key + "top", "CALLS", key + "leaf"],
                      [key + "side", "CALLS", key + "leaf"]]}
    tools = tmp_path / "tools"
    tools.mkdir()
    (tools / codeintel.TOOL).write_text(SERVER, encoding="utf-8")
    (tools / codeintel.TOOL).chmod(0o755)
    (tools / "rows.json").write_text(json.dumps(rows), encoding="utf-8")
    monkeypatch.setenv("PATH", str(tools), prepend=":")
    return tools


def test_one_load_of_the_graph_asks_both_queries_and_their_pages_in_one_start_of_the_tool(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    tools = _server(tmp_path, monkeypatch, root)
    monkeypatch.setenv("CBM_CACHE_DIR", str(tmp_path / "cache"))
    monkeypatch.setenv("CBM_RUNTIME_DIR", str(tmp_path / "runtime"))
    assert [entry["name"] for entry in codeintel.callers(root, "leaf")] == ["top", "side"]  # the second page of each
    assert [entry["name"] for entry in codeintel.dead_code(root)] == ["top", "side"]  # kept by the process: no start
    places = f"|{codeintel.home(root)}|{codeintel.daemon_dir(root)}"  # the repository's, not the caller's
    # The UI is turned off first, then one server is started: no ``cli`` call, and no second server.
    assert (tools / "starts.txt").read_text(encoding="utf-8").splitlines() == ["config set ui_enabled false" + places,
                                                                               places]
    assert not (tmp_path / "cache").exists() and not (tmp_path / "runtime").exists()


def test_a_session_that_fails_or_hangs_is_a_refusal_and_no_answer_is_kept(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    tools = _server(tmp_path, monkeypatch, root)
    monkeypatch.setattr(codeintel, "_ANSWER_S", 0.5)
    (tools / "refuse").touch()  # the server ends at once with exit code 7
    with pytest.raises(RuntimeError, match=r"exit code 7\b"):
        codeintel.callers(root, "leaf")
    (tools / "refuse").rename(tools / "hang")  # the server answers no tool: it is killed after the time limit
    with pytest.raises(RuntimeError, match=r"exit code -9\b"):
        codeintel.callers(root, "leaf")
    (tools / "hang").unlink()
    assert [entry["name"] for entry in codeintel.callers(root, "leaf")] == ["top", "side"]


def test_callees_are_the_functions_a_symbol_calls_in_the_form_of_callers(tmp_path, monkeypatch):
    root = _repository(tmp_path / "repo")
    staged = root / codeintel.BASE_REL / "files/app/flow.py"
    staged.parent.mkdir(parents=True)
    staged.touch()
    key = "code.app.flow."
    nodes = [[key + name, name, "Function", "app/flow.py"] for name in ("top", "mid", "leaf", "side")]
    edges = [[key + "top", "CALLS", key + "mid"], [key + "top", "CALLS", key + "leaf"],
             [key + "side", "CALLS", key + "leaf"], [key + "top", "USAGE", key + "side"]]
    monkeypatch.setattr(codeintel, "_rows", lambda _root, query: edges if "type(r)" in query else nodes)
    assert [entry["name"] for entry in codeintel.callees(root, "top")] == ["mid", "leaf"]  # a use is no call
    assert codeintel.callees(root, "top")[0] == codeintel.callers(root, "leaf")[0] | {"name": "mid"}  # one entry shape
    assert codeintel.callees(root, "leaf") == [] and codeintel.callees(root, "no_such_symbol") == []
    assert [entry["name"] for entry in codeintel.callers(root, "leaf")] == ["top", "side"]
