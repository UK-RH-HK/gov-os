"""Round 13, piece 2: ``gov close`` calls the counter (DEC-495, fourth point; DEC-491).

DEC-495: "The share reaches the close record through a small W1-30 follow-up once W1-31 is merged." DEC-491:
"The caller names the sessions of a ticket [...] The close record's own tokens are counted by a re-measure
after the close." The counter "outputs counts only and never content".

**Proposed (README, round 13, settlements 25 and 26).**

- The caller names the ticket's sessions as it names them to ``gov telemetry``: ``gov close <ticket>
  --ticket-session <session id>[=<role>]``, once for each session. No command is added.
- The close record's frontmatter and the JSON result of a close both hold ``governance_share``: a map with
  exactly ``measured``, ``estimated`` and ``total``, each the counter's figure (a fraction of 1) or the string
  ``not measured``. With no session named, or where the counter could not measure, the three say
  ``not measured`` and the ticket closes all the same, with exit code 0.

The close record is written first and the share is measured after it: the counter says "not measured" of a
ticket whose close record does not exist yet (``tests/acceptance/W1-31/README.md``, "Records"), so a measured
share in the record is only there when the record was.

**No session log of this machine is read.** Every close here runs with ``HOME`` and ``CLAUDE_CONFIG_DIR`` in
temporary folders. The session logs are the ones the telemetry suite's support writes in the specimens' forms
(``w1_31_support.full_logs``), given to the close the way that suite gives them to ``gov telemetry``. Every
text of those logs carries ``MARK-``; none of it may be in the record or in anything the close prints.
"""

import os
import shutil
import sys
from pathlib import Path

import pytest

import w1_30_support as support

_W1_31 = str(Path(__file__).resolve().parents[1] / "W1-31")
if _W1_31 not in sys.path:
    sys.path.insert(0, _W1_31)

import w1_31_support as telemetry  # noqa: E402

TICKET = "PROJ-shar"
WBS = "W1-shar"
SESSION_OPTION = "--ticket-session"
SHARE_KEY = "governance_share"
SHARE_PARTS = ("measured", "estimated", "total")
NOT_MEASURED = "not measured"
ALL_NOT_MEASURED = {part: NOT_MEASURED for part in SHARE_PARTS}
# The close record is counted among the governance text, and the lines that state the share are written into
# it after the measure: a later measure differs from the recorded one by those lines, and by no more.
RECORD_LINES_TOLERANCE = 0.02


@pytest.fixture()
def logs(tmp_path):
    """The folder ``CLAUDE_CONFIG_DIR`` names, with the telemetry suite's three sessions written into it: two
    of the ticket and one of other work."""
    folder = tmp_path / "claude-config"
    (folder / "projects").mkdir(parents=True)
    for log in telemetry.full_logs():
        log.write(folder)
    return folder


def _ticket_with_instruction_files(project, failing=False):
    """A ticket ready for its close in a project that holds what the counter's estimate stands on: the two
    roles' files and the root instruction files, committed by the owner before the ticket's work."""
    for role in (telemetry.ROLE_A, telemetry.ROLE_B):
        project.write(f"{telemetry.ROLE_FILES_REL}/{role}.md",
                      telemetry.pad(f"---\nname: {role}\n---\n\n# {role}\n\nDo the work of the {role} role.\n"))
    for rel in telemetry.ROOT_INSTRUCTION_FILES:
        project.write(rel, telemetry.pad("# Governance\n\nWork on one ticket. Stay inside its allowed paths.\n"))
    project.commit("instruction files", who=support.OWNER)
    support.build_ticket(project, TICKET, WBS, failing=failing)


def _environment(sandbox, logs, with_ccusage=True):
    """The environment of a close that may measure: the suite's, the temporary session logs, and ccusage on
    ``PATH`` (``with_ccusage=False``: a ``PATH`` without it)."""
    env = {**support.sandbox_env(sandbox), "CLAUDE_CONFIG_DIR": str(logs)}
    if with_ccusage:
        env["PATH"] = f"{telemetry.ccusage_dir()}{os.pathsep}{env['PATH']}"
    else:
        env["PATH"] = support.path_without("ccusage", sandbox.home / "path-without-ccusage")
    assert str(Path.home()) != env["HOME"] and Path(env["HOME"]).is_relative_to(sandbox.home.parent), \
        "the fixture is wrong: the close would run with the real home"
    return env


def _named(*sessions):
    return [argument for session in sessions for argument in (SESSION_OPTION, session)]


def _share_of(holder, where):
    share = holder.get(SHARE_KEY)
    assert isinstance(share, dict) and sorted(share) == sorted(SHARE_PARTS), \
        f"{where} does not state the governance share under {SHARE_KEY!r} as a map of {SHARE_PARTS}: {share!r}"
    return share


def _closed_with_share(project, run, interface):
    """The ticket closed with exit code 0; returns the share the record states, which the result states too."""
    result = support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    share = _share_of(support.the_close_record(project, TICKET), "the close record")
    assert _share_of(result, "the result") == share, \
        f"the result and the close record state different shares\n{run.describe()}"
    return share


@pytest.fixture()
def ccusage():
    if telemetry.ccusage_dir() is None:
        pytest.skip("ccusage is not installed on this machine: the counter cannot measure a session's tokens")


# --------------------------------------------------------------------------
# Measured
# --------------------------------------------------------------------------

def test_the_close_record_states_the_share_of_the_sessions_the_caller_names(project, sandbox, interface, logs,
                                                                            ccusage):
    _ticket_with_instruction_files(project)
    env = _environment(sandbox, logs)

    run = support.run_close(project, sandbox, TICKET, *_named(*telemetry.ROLED), env=env)

    share = _closed_with_share(project, run, interface)
    for part in SHARE_PARTS:
        assert telemetry.is_number(share[part]) and 0 < share[part] < 1, \
            f"the {part} share is {share[part]!r}, not a fraction the counter measured\n{run.describe()}"
    assert share["total"] == pytest.approx(share["measured"] + share["estimated"], abs=1e-6)

    # The counter itself, asked afterwards of the same project, sessions and logs.
    after = telemetry.record(telemetry.run_telemetry(project, sandbox, logs, *telemetry.ROLED, ticket=TICKET))
    assert telemetry.is_count(after["governance_tokens"]["close_records"]), \
        "the fixture is wrong: the counter does not count the close record"
    assert share["estimated"] == pytest.approx(telemetry.share(after, "estimated"), abs=1e-9), \
        "the estimated share in the record is not the counter's"
    assert share["measured"] == pytest.approx(telemetry.share(after, "measured"), abs=RECORD_LINES_TOLERANCE), \
        "the measured share in the record is not the counter's, measured after the record was written"


@pytest.mark.parametrize("failing", [False, True], ids=["a close that passes", "a close that is refused"])
def test_no_text_of_a_session_is_in_the_record_or_in_what_the_close_prints(failing, project, sandbox, interface,
                                                                           logs, ccusage):
    """Counts only, never content: every text of the session logs carries ``MARK-``."""
    _ticket_with_instruction_files(project, failing=failing)
    assert telemetry.MARK in "".join(path.read_text(encoding="utf-8") for path in logs.rglob("*.jsonl")), \
        "the fixture is wrong: the session logs hold no marked text"

    run = support.run_close(project, sandbox, TICKET, *_named(*telemetry.ROLED), env=_environment(sandbox, logs))

    if failing:
        support.refused(run, interface, support.EXIT_CHECK_FAILED)
    else:
        support.result_of(run, interface)
    assert telemetry.MARK not in run.stdout + run.stderr, f"the close printed text of a session\n{run.describe()}"
    written = [path for path in project.root.rglob("*")
               if path.is_file() and ".git" not in path.relative_to(project.root).parts[:1]
               and "src" not in path.relative_to(project.root).parts[:1]]
    holding = [str(path.relative_to(project.root)) for path in written
               if telemetry.MARK.encode() in path.read_bytes()]
    assert not holding, f"files of the project hold text of a session after the close: {holding}"


# --------------------------------------------------------------------------
# Not measured: said by name, and the close is not refused for it
# --------------------------------------------------------------------------

def test_without_a_session_named_the_share_is_not_measured_and_the_ticket_closes(project, sandbox, interface,
                                                                                 logs):
    _ticket_with_instruction_files(project)

    run = support.run_close(project, sandbox, TICKET, env=_environment(sandbox, logs))

    assert _closed_with_share(project, run, interface) == ALL_NOT_MEASURED, \
        f"no session was named, and the record states a share\n{run.describe()}"


@pytest.mark.parametrize("why", ["ccusage is not on PATH", "a named session has no log"])
def test_a_counter_that_cannot_measure_does_not_refuse_the_close(why, project, sandbox, interface, logs):
    _ticket_with_instruction_files(project)
    if why == "ccusage is not on PATH":
        env = _environment(sandbox, logs, with_ccusage=False)
        assert shutil.which("ccusage", path=env["PATH"]) is None
        sessions = telemetry.ROLED
    else:
        if telemetry.ccusage_dir() is None:
            pytest.skip("ccusage is not installed on this machine")
        env = _environment(sandbox, logs)
        sessions = (telemetry.named(telemetry.SESSION_NOWHERE, telemetry.ROLE_A),)

    run = support.run_close(project, sandbox, TICKET, *_named(*sessions), env=env)

    assert _closed_with_share(project, run, interface) == ALL_NOT_MEASURED, \
        f"the counter could not measure ({why}), and the record states a share\n{run.describe()}"


def test_a_part_the_counter_did_not_measure_says_so_beside_the_part_it_measured(project, sandbox, interface, logs,
                                                                                ccusage):
    """The sessions are named without their roles: the counter measures the logs and cannot estimate the
    instruction files (DEC-507). The record states each part as the counter gave it."""
    _ticket_with_instruction_files(project)

    run = support.run_close(project, sandbox, TICKET, *_named(telemetry.SESSION_A, telemetry.SESSION_B),
                            env=_environment(sandbox, logs))

    share = _closed_with_share(project, run, interface)
    assert telemetry.is_number(share["measured"]) and 0 < share["measured"] < 1, \
        f"the measured share is {share['measured']!r}\n{run.describe()}"
    assert (share["estimated"], share["total"]) == (NOT_MEASURED, NOT_MEASURED), \
        f"no role was named, and the record states an estimate or a total: {share}\n{run.describe()}"
