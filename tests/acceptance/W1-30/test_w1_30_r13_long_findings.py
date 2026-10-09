"""Round 13, piece 5: the repair ticket of a refused close whose findings are too long for one argument
(DEC-569: "the repair ticket of a refused close whose findings are too long for one argument").

Today the findings go to the ticket tool as one command-line argument. The operating system carries about
128 KiB in one argument; a close with very many findings ends with "Argument list too long" and opens no repair
ticket.

What is held (README, round 13, piece 5):

- The repair ticket is opened whatever the findings' length, through the ticket tool as before: the project's
  tool is started for it, the ticket depends on the refused one by the tool's own answer, and where the tool
  fails no ticket file is written by any other means.
- What the repair ticket does not hold of the findings is said: in the ticket (a line with the word "cut" and
  the number of findings left out) and in the answer (``repair_ticket_findings_cut``, proposed, that number).
  A ticket that holds every finding says nothing of the kind, and the answer's number is 0 or absent.
- The answer still names every finding, or says how many it left out (``findings_cut``, proposed).

The findings: one acceptance file with ``CASES`` failing cases, each with an id of its own that is ``ID_LENGTH``
characters long, so the findings are several hundred thousand bytes.
"""

import re

import pytest

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-long"
WBS = "W1-long"
CASES = 1200
ID_LENGTH = 300
# One argument of a command carries less than this on Linux (32 pages of 4 KiB).
ONE_ARGUMENT = 131072

# Proposed names (settlement 29).
TICKET_CUT_KEY = "repair_ticket_findings_cut"
ANSWER_CUT_KEY = "findings_cut"

FAILING_TOOL = "#!/bin/sh\necho 'planted: the ticket tool fails' >&2\nexit 7\n"


def _case_id(number):
    head = f"case{number:04d}-"
    return head + "x" * (ID_LENGTH - len(head))


IDS = [_case_id(number) for number in range(CASES)]
MANY_FAILING = (
    "import pytest\n\n\n"
    f"IDS = ['case%04d-' % n + 'x' * ({ID_LENGTH} - 9) for n in range({CASES})]\n\n\n"
    "@pytest.mark.parametrize('given', IDS, ids=IDS)\n"
    "def test_many(given):\n"
    "    assert False, 'planted failure'\n"
)


def _recording(marker):
    """The kernel's ticket tool behind a line that writes down, each time it is started, what it was asked."""
    return f'#!/bin/sh\necho "$1" >> "{marker}"\nexec "{support.KERNEL_TOOL}" "$@"\n'


def _project_with_long_findings(root, tool):
    """A ticket whose acceptance file has ``CASES`` failing cases; ``tool`` is the project's ticket tool, put
    there by the owner before the ticket's first commit."""
    project = support.Project(root)
    (project.root / support.TOOL_REL).write_text(tool, encoding="utf-8")
    project.commit("the project's ticket tool", who=support.OWNER)
    project.add_ticket(TICKET, WBS)
    project.write(f"tests/acceptance/{WBS}/test_many.py", MANY_FAILING)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)
    return project


@pytest.fixture(scope="module")
def refused_close(built, interface, tmp_path_factory):
    """One refused close of the project, for the cases of this file that read what it left."""
    base = tmp_path_factory.mktemp("w1-30-long-findings")
    marker = base / "tool-started"
    project = _project_with_long_findings(base / "project", _recording(marker))
    run = support.run_close(project, cli_support.make_sandbox(base / "sandbox"), TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    text = support.error_text(error)
    assert IDS[0] in text and len(text.encode()) > 2 * ONE_ARGUMENT, \
        f"the fixture is wrong: the findings are not longer than one argument carries ({len(text.encode())} bytes)"
    return project, run, error, marker


def _short(run):
    """The run without its several hundred thousand bytes of output."""
    return f"gov {' '.join(run.args)}: exit code {run.returncode}, {len(run.stdout)} characters of output"


def _repair_ticket_text(project):
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[path.name for path in repairs]}"
    return repairs[0].read_text(encoding="utf-8")


def test_a_refused_close_with_very_long_findings_opens_its_repair_ticket_through_the_ticket_tool(refused_close):
    project, run, error, marker = refused_close
    said = str((error.get("details") or {}).get("repair_ticket"))
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"no repair ticket was opened; the answer says of it: {said[:300]!r}\n{_short(run)}"
    assert said == repairs[0].stem, f"the answer does not name the repair ticket {repairs[0].stem}: {said[:300]!r}"
    started = marker.read_text(encoding="utf-8").split() if marker.is_file() else []
    assert "create" in started, f"the project's ticket tool was not asked to create the ticket: {started}"
    tree = support.tk(project, "dep", "tree", repairs[0].stem).splitlines()
    assert tree and repairs[0].stem in tree[0], f"the ticket tool does not know the repair ticket: {tree}"
    assert any(TICKET in line for line in tree[1:]), \
        f"by the ticket tool the repair ticket does not depend on {TICKET}: {tree}"
    assert support.iteration_count(project.root, TICKET) == 1, "the refusal is not counted once"


def test_what_the_repair_ticket_does_not_hold_of_the_findings_is_said_in_it_and_in_the_answer(refused_close):
    project, run, error, _ = refused_close
    text = _repair_ticket_text(project)
    left_out = sum(1 for case in IDS if case[:9] not in text)
    stated = (error.get("details") or {}).get(TICKET_CUT_KEY, 0)
    assert isinstance(stated, int) and not isinstance(stated, bool), f"{TICKET_CUT_KEY} is no number: {stated!r}"
    assert stated == left_out, \
        f"the repair ticket leaves out {left_out} of {CASES} findings and the answer says {stated} ({TICKET_CUT_KEY})"
    saying = [line for line in text.splitlines() if re.search(r"\bcut\b", line, re.IGNORECASE)]
    if left_out:
        assert any(re.search(rf"\b{left_out}\b", line) for line in saying), \
            f"the repair ticket leaves out {left_out} findings and no line of it says so: {saying[:5]}"
    else:
        assert not saying, f"the repair ticket holds every finding and says something was cut: {saying[:5]}"


def test_the_answer_names_every_finding_or_says_how_many_it_left_out(refused_close):
    _, run, error, _ = refused_close
    text = support.error_text(error)
    left_out = sum(1 for case in IDS if case[:9] not in text)
    stated = (error.get("details") or {}).get(ANSWER_CUT_KEY, 0)
    assert isinstance(stated, int) and not isinstance(stated, bool), f"{ANSWER_CUT_KEY} is no number: {stated!r}"
    assert stated == left_out, \
        f"the answer leaves out {left_out} of {CASES} findings and says {stated} ({ANSWER_CUT_KEY})\n{_short(run)}"


def test_with_very_long_findings_and_a_failing_ticket_tool_no_ticket_file_is_written(built, interface, tmp_path):
    """As today for short findings (``test_no_repair_file_is_written_when_the_ticket_tool_fails``): whatever
    carries the findings to the tool, nothing writes a ticket file in the tool's place."""
    project = _project_with_long_findings(tmp_path / "project", FAILING_TOOL)

    run = support.run_close(project, cli_support.make_sandbox(tmp_path / "sandbox"), TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert not support.other_tickets(project.root, TICKET), \
        f"a ticket file was written although the ticket tool failed: {support.other_tickets(project.root, TICKET)}"
    said = str((error.get("details") or {}).get("repair_ticket"))
    assert re.search(r"\btk\b|ticket tool|not opened", said, re.IGNORECASE), \
        f"the answer does not say that no repair ticket was opened: {said[:300]!r}"
    assert support.untracked_paths(project) == [], \
        f"the refused close left files in the project: {support.untracked_paths(project)}"
