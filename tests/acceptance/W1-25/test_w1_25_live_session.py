"""W1-25 -- a real fresh session, given only the resume brief, states the ticket, its inputs and the next step.

KPI success 2 [CAP-20.a, CAP-37.f] and KPI success 4 [CAP-38.b] say "a fresh
session" and "a session with only the latest checkpoint and the SessionStart
output". Recommended option of DP-6, its live part, after DEC-232: one short
real headless session per run, ``local_only``, on the cheapest model, with a
turn limit and no tool. Another answer to DP-6 removes this file.

**Cost and needs.** One session with the real CLI at ``~/.local/bin/claude``
(DEC-205) and the caller's own credentials and network. It starts in an empty
temporary directory, so it has no repository to read: the brief printed by
``gov checkpoint --resume`` is all it gets. The SessionStart hook that will
inject that brief (W1-49, W1-29) does not exist on this branch; the brief is
passed as the prompt. Leave it out with ``-m "not local_only"``.

A run in which the model does not answer in the asked form fails with that
reason and is repeated; it is not a finding against the command (DEC-232).
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import w1_25_support as support

pytestmark = pytest.mark.local_only

CLI = Path.home() / ".local/bin/claude"
SESSION_TIMEOUT_S = 240.0
NOT_INHERITED = ("GOV_ROLE", "GOV_TICKET", "CLAUDECODE", "CLAUDE_CODE_ENTRYPOINT", "CLAUDE_PROJECT_DIR",
                 "CLAUDE_CODE_SSE_PORT")
QUESTION = (
    "\n\nYou are a fresh session. The text above is everything you have. Use no tool. Answer with exactly three "
    "lines and nothing else:\nTICKET: <the ticket id>\nINPUTS: <the ids of the inputs, separated by commas>\n"
    "NEXT: <the next step, word for word>"
)


@pytest.fixture(scope="module")
def answer(built, interface, tmp_path_factory):
    """The answer of one real session that was given the resume brief of a checkpoint made here."""
    import shutil

    base = tmp_path_factory.mktemp("w1-25-live-session")
    project = base / "repo"
    shutil.copytree(built, project, symlinks=True)
    sandbox = support.cli_support.make_sandbox(base / "sandbox")
    written = support.cli_support.run_gov(project, sandbox, *support.write_args(inputs=(support.INPUT_REL,)))
    path = support.checkpoint_path(project, support.succeeded(written, interface))
    brief = support.cli_support.run_gov(project, sandbox, "checkpoint", "--resume", "--ticket", support.TICKET)
    assert brief.returncode == 0 and brief.stdout.strip(), brief.describe()
    if not CLI.is_file():
        pytest.fail("a real session needs ~/.local/bin/claude on this machine", pytrace=False)
    empty = base / "empty"
    empty.mkdir()
    env = {key: value for key, value in os.environ.items() if key not in NOT_INHERITED}
    done = subprocess.run([str(CLI), "-p", brief.stdout + QUESTION, "--model", "haiku", "--max-turns", "2"],
                          cwd=str(empty), env=env, capture_output=True, text=True, timeout=SESSION_TIMEOUT_S,
                          stdin=subprocess.DEVNULL)
    lines = {name.strip(): value.strip() for name, _, value in
             (line.partition(":") for line in done.stdout.splitlines()) if value}
    if done.returncode != 0 or not {"TICKET", "INPUTS", "NEXT"} <= set(lines):
        pytest.fail(f"the session did not answer in the asked form (exit code {done.returncode}); repeat the run\n"
                    f"{done.stdout[-800:]}\n{done.stderr[-400:]}", pytrace=False)
    return lines, support.inputs_of(support.frontmatter(path))


def test_the_session_states_the_ticket(answer):
    lines, _ = answer
    assert support.TICKET in lines["TICKET"], lines


def test_the_session_states_the_inputs(answer):
    lines, inputs = answer
    missing = [str(item["id"]) for item in inputs if str(item["id"]) not in lines["INPUTS"]]
    assert not missing, f"the session does not name the inputs {missing}: {lines}"


def test_the_session_states_the_recorded_next_step(answer):
    lines, _ = answer
    assert support.NEXT_STEP in lines["NEXT"], lines
