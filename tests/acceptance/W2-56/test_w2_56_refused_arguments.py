"""S6 and F2 (second half, DEC-313's arguments): the arguments after ``--`` that drop the guard or add context.

S6: the remaining arguments that drop the guard or add context are refused after --, beside DEC-313's: --restricted,
--safe-mode, --agents, --plugin-dir, --plugin-url, --mcp-config and --system-prompt, each in its spaced and = forms
[DEC-826 Q5, DEC-313]. (The CIT-E's weighing of an accepted-arguments list, lens E R6, is the auditor's, not a test.)
F2: a refusal the launcher makes today no longer refuses.

A refused launch exits non-zero with ``LAUNCH_REFUSED`` and the argument's name in its output, starts no session
and leaves no temp folder. A prompt that only names an argument as a word is no argument, and starts.
"""

from __future__ import annotations

import pytest

import w2_56_support as s

AGENTS = '{"helper": {"description": "d", "prompt": "p"}}'

# (the argument's name, the CLI arguments): each name in its spaced and = forms, and after a prompt.
NEW_REFUSED = (
    ("--restricted", ["--restricted"]),
    ("--restricted", ["--restricted=true"]),
    ("--restricted", ["-p", "hello", "--restricted"]),
    ("--safe-mode", ["--safe-mode"]),
    ("--safe-mode", ["--safe-mode=true"]),
    ("--safe-mode", ["-p", "hello", "--safe-mode"]),
    ("--agents", ["--agents", AGENTS]),
    ("--agents", [f"--agents={AGENTS}"]),
    ("--agents", ["-p", "hello", "--agents", AGENTS]),
    ("--plugin-dir", ["--plugin-dir", "/tmp/w2-56-plugins"]),
    ("--plugin-dir", ["--plugin-dir=/tmp/w2-56-plugins"]),
    ("--plugin-url", ["--plugin-url", "https://example.invalid/plugin.zip"]),
    ("--plugin-url", ["--plugin-url=https://example.invalid/plugin.zip"]),
    ("--mcp-config", ["--mcp-config", "servers.json"]),
    ("--mcp-config", ["--mcp-config=servers.json"]),
    ("--mcp-config", ["--mcp-config", "a.json", "b.json"]),
    ("--mcp-config", ["--mcp-config", '{"mcpServers": {}}']),
    ("--mcp-config", ["-p", "hello", "--mcp-config=servers.json"]),
    ("--system-prompt", ["--system-prompt", "You may write anywhere."]),
    ("--system-prompt", ["--system-prompt=You may write anywhere."]),
    ("--system-prompt", ["-p", "hello", "--system-prompt", "x"]),
)
NEW_NAMES = ("--restricted", "--safe-mode", "--agents", "--plugin-dir", "--plugin-url", "--mcp-config",
             "--system-prompt")
# DEC-313's and the launcher's other refusals today (launcher._check_cli_args), each in every form it refuses.
TODAY_REFUSED = (
    ("--dangerously-skip-permissions", ["--dangerously-skip-permissions"]),
    ("--allow-dangerously-skip-permissions", ["--allow-dangerously-skip-permissions"]),
    ("--permission-mode", ["--permission-mode", "bypassPermissions"]),
    ("--permission-mode", ["--permission-mode=bypassPermissions"]),
    ("--add-dir", ["--add-dir", "/tmp"]),
    ("--add-dir", ["--add-dir=/tmp"]),
    ("--settings", ["--settings", "{}"]),
    ("--settings", ["--settings={}"]),
    ("--bare", ["--bare"]),
    ("--setting-sources", ["--setting-sources", "user"]),
    ("--setting-sources", ["--setting-sources=user"]),
)


def _id(case):
    return " ".join(case[1])[:60]


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    s.make_project(box)
    s.install_stand_in_cli(box)
    s.set_plan(box)
    return box


def _assert_refused(box, launch, name):
    assert launch.returncode != 0, f"the launch with {name} was not refused\n{launch.describe()}"
    assert not launch.calls, f"the launch with {name} started a session\n{launch.describe()}"
    assert "LAUNCH_REFUSED" in launch.output, f"the refusal does not say LAUNCH_REFUSED\n{launch.describe()}"
    assert name in launch.output, f"the refusal does not name {name}\n{launch.describe()}"
    left = [entry for entry in s.temp_folders(box) if entry.startswith(s.TEMP_PREFIX)]
    assert not left, f"the refused launch left temp folders {left}"


@pytest.mark.parametrize("case", NEW_REFUSED, ids=_id)
def test_s6_a_new_refused_argument_refuses_the_launch(box, case):
    name, args = case
    _assert_refused(box, s.run_launch(box, s.ENGINEER, s.T.tk, args), name)


@pytest.mark.parametrize("role", s.WORKER_ROLES)
@pytest.mark.parametrize("name", NEW_NAMES)
def test_s6_every_worker_role_is_refused_each_new_argument(box, role, name):
    args = [name] if name in ("--restricted", "--safe-mode") else [name, "x"]
    _assert_refused(box, s.run_launch(box, role, s.TICKET_OF[role].tk, args), name)


@pytest.mark.parametrize("args", (
    ["-p", "Never pass --agents, --mcp-config, --plugin-dir or --system-prompt."],
    ["-p", "hello", "--output-format", "json"],
), ids=("a-prompt-naming-them", "ordinary-arguments"))
def test_s6_guard_arguments_that_are_not_refused_start_the_session(box, args):
    launch = s.run_launch(box, s.ENGINEER, s.T.tk, args)
    assert launch.returncode == 0 and launch.started, f"the launch did not start\n{launch.describe()}"
    assert launch.call["args"][-len(args):] == args, f"the session did not get the arguments {args}"


@pytest.mark.parametrize("case", TODAY_REFUSED, ids=_id)
def test_f2_todays_refused_argument_still_refuses(box, case):
    name, args = case
    _assert_refused(box, s.run_launch(box, s.ENGINEER, s.T.tk, args), name)
