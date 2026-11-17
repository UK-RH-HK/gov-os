"""S6 and F2 (second half): the arguments after ``--`` that add context or replace the launcher's settings.

S6: the arguments that add context are refused after --: --agents, --plugin-dir, --plugin-url, --mcp-config and
--system-prompt, each in its spaced and = forms [DEC-826 Q5]. (The CIT-E's weighing of an accepted-arguments list,
lens E R6, is the auditor's, not a test.)
F2: a refusal the launcher makes today no longer refuses.

Emergency 2 (release 0.1.2, EMERGENCY-2 2.2): --restricted, --safe-mode, the no-prompt mode, --add-dir and --bare are
no longer refused, and their cases are retired.

A refused launch exits non-zero with ``LAUNCH_REFUSED`` and the argument's name in its output, starts no session
and leaves no temp folder. A prompt that only names an argument as a word is no argument, and starts.
"""

from __future__ import annotations

import pytest

import w2_56_support as s

AGENTS = '{"helper": {"description": "d", "prompt": "p"}}'

# (the argument's name, the CLI arguments): each name in its spaced and = forms, and after a prompt.
NEW_REFUSED = (
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
NEW_NAMES = ("--agents", "--plugin-dir", "--plugin-url", "--mcp-config", "--system-prompt")
# The launcher's other refusals today (launcher._check_cli_args), each in every form it refuses.
TODAY_REFUSED = (
    ("--settings", ["--settings", "{}"]),
    ("--settings", ["--settings={}"]),
    ("--setting-sources", ["--setting-sources", "user"]),
    ("--setting-sources", ["--setting-sources=user"]),
)


def _id(case):
    return " ".join(case[1])[:60]


# W2-60a (DAEO-cv58; P-3, DEC-1156 (7)): gov launch refuses a project without the role's role file, its version line
# and its default line; the fixture plants one per worker role, so that check is never what refuses a launch here.
ROLE_FILES = {f"template/governance/kernel/roles/{role}.md": (
    f"# {role} role (W2-56 fixture)\n\n- **Version:** 1.0.0\n"
    "- **Launch default:** model claude-opus-5-5, effort high\n") for role in s.WORKER_ROLES}


@pytest.fixture
def box(tmp_path):
    box = s.make_box(tmp_path)
    s.make_project(box, extra=ROLE_FILES)
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
    _assert_refused(box, s.run_launch(box, role, s.TICKET_OF[role].tk, [name, "x"]), name)


@pytest.mark.parametrize("args", (
    ["-p", "Never pass --agents, --mcp-config, --plugin-dir or --system-prompt."],
    ["-p", "hello", "--output-format", "json"],
), ids=("a-prompt-naming-them", "ordinary-arguments"))
def test_s6_guard_arguments_that_are_not_refused_start_the_session(box, args):
    launch = s.run_launch(box, s.ENGINEER, s.T.tk, args)
    assert launch.returncode == 0 and launch.started, f"the launch did not start\n{launch.describe()}"
    tmpdir = launch.call["env"].get("TMPDIR") or (launch.settings().get("env") or {}).get("TMPDIR")
    assert _caller_args_then_appended_pair(launch.call["args"], args, s.ENGINEER, tmpdir), (
        f"the session did not get the arguments {args}, followed by nothing or by the one appended pair: "
        f"{launch.call['args']}")


def _caller_args_then_appended_pair(argv, args, role, tmpdir):
    """True when ``args`` are one contiguous, ordered run in ``argv`` followed by nothing or by exactly
    ``--append-system-prompt-file <session TMPDIR>/role-<role>.md``: since W2-60a (P-4 (A)) the one appended file is
    the role file's text then the role template's, written in the session's temp folder (W2-153's S1 placed it last,
    DEC-1050; DEC-866)."""
    argv, args = list(argv), list(args)
    if argv[-len(args):] == args:
        return True
    if len(argv) < len(args) + 2 or argv[-len(args) - 2:-2] != args or argv[-2] != "--append-system-prompt-file":
        return False
    head, sep, name = argv[-1].replace("\\", "/").rpartition("/")
    return bool(sep and tmpdir and head == tmpdir.rstrip("/") and name == f"role-{role}.md")


@pytest.mark.parametrize("case", TODAY_REFUSED, ids=_id)
def test_f2_todays_refused_argument_still_refuses(box, case):
    name, args = case
    _assert_refused(box, s.run_launch(box, s.ENGINEER, s.T.tk, args), name)
