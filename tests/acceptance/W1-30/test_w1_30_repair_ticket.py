"""The repair ticket of a failing close (KPI S2 "a failure opens a dependent repair ticket" [CAP-31.b]; KPI S6
"the repair ticket records it").

The repair ticket is opened through the project's ticket tool (``governance/kernel/bin/tk``, W1-09). When the
tool is absent, or present and failing, nothing was opened: no file is written in its place by any other means,
and the answer says so beside the finding that made the close fail. When the tool works, the dependency is read
back through the tool, in the KPI's direction: the repair ticket is the dependent one, it depends on the ticket
whose close failed.

The absent tool is absent everywhere: the project's script is removed and ``PATH`` holds no ``tk`` (W1-09's
suite builds its environment the same way).
"""

import re

import w1_30_support as support

cli_support = support.cli_support

TICKET = "PROJ-rprt"
WBS = "W1-rprt"
TOOL = "governance/kernel/bin/tk"
NAMES_THE_TOOL = re.compile(r"\btk\b|ticket tool", re.IGNORECASE)


def _failing_close_without_a_working_tool(project, sandbox, interface, monkeypatch, tmp_path, script):
    """A ticket with a failing acceptance test; the ticket tool is removed (``script`` None) or replaced."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    tool = project.root / TOOL
    if script is None:
        tool.unlink()
    else:
        tool.write_text(script, encoding="utf-8")
    project.commit("the ticket tool", who=support.ORCHESTRATOR)
    monkeypatch.setenv("PATH", support.path_without("tk", tmp_path / "path"))
    support.load_store(project, sandbox)
    before = cli_support.snapshot(project.root)
    run = support.run_close(project, sandbox, TICKET, store=False)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    difference = cli_support.snapshot_difference(before, cli_support.snapshot(project.root))
    return run, error, [line for line in difference if not COUNTED_OR_CACHE.search(line)]


FAILING_TOOL = "#!/bin/sh\necho 'planted: the ticket tool fails' >&2\nexit 7\n"


def test_no_repair_file_is_written_when_the_ticket_tool_is_absent(project, sandbox, interface, monkeypatch, tmp_path):
    run, _, difference = _failing_close_without_a_working_tool(project, sandbox, interface, monkeypatch, tmp_path, None)
    assert difference == [], f"the failing close wrote files although no ticket could be opened: {difference}"


def test_the_answer_names_the_absent_ticket_tool_beside_the_finding(project, sandbox, interface, monkeypatch, tmp_path):
    run, error, _ = _failing_close_without_a_working_tool(project, sandbox, interface, monkeypatch, tmp_path, None)
    text = support.error_text(error)
    assert "test_fail" in text, f"the answer does not name the failing test\n{run.describe()}"
    assert NAMES_THE_TOOL.search(text), \
        f"the answer does not say that no repair ticket was opened because the ticket tool is absent\n{run.describe()}"


def test_no_repair_file_is_written_when_the_ticket_tool_fails(project, sandbox, interface, monkeypatch, tmp_path):
    run, _, difference = _failing_close_without_a_working_tool(project, sandbox, interface, monkeypatch, tmp_path,
                                                               FAILING_TOOL)
    assert difference == [], f"the failing close wrote files although the ticket tool failed: {difference}"


def test_the_answer_names_the_failing_ticket_tool_beside_the_finding(project, sandbox, interface, monkeypatch, tmp_path):
    run, error, _ = _failing_close_without_a_working_tool(project, sandbox, interface, monkeypatch, tmp_path, FAILING_TOOL)
    text = support.error_text(error)
    assert "test_fail" in text, f"the answer does not name the failing test\n{run.describe()}"
    assert NAMES_THE_TOOL.search(text), \
        f"the answer does not say that no repair ticket was opened because the ticket tool failed\n{run.describe()}"


def test_the_ticket_tool_shows_the_repair_ticket_depending_on_the_failed_ticket(project, sandbox, interface):
    """``tk dep tree <repair ticket>`` lists the failed ticket under the repair ticket."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    run = support.run_close(project, sandbox, TICKET)
    support.refused(run, interface, support.EXIT_CHECK_FAILED)
    repairs = support.other_tickets(project.root, TICKET)
    assert len(repairs) == 1, f"one repair ticket is expected, found {[p.name for p in repairs]}\n{run.describe()}"
    tree = support.tk(project, "dep", "tree", repairs[0].stem).splitlines()
    assert tree and repairs[0].stem in tree[0], f"tk does not know the repair ticket: {tree}"
    assert any(TICKET in line for line in tree[1:]), \
        f"by the ticket tool the repair ticket does not depend on {TICKET}: {tree}"


def test_the_ticket_tool_does_not_show_the_failed_ticket_depending_on_the_repair_ticket(project, sandbox, interface):
    """The other direction is not written: ``tk dep tree <failed ticket>`` lists nothing under it."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    run = support.run_close(project, sandbox, TICKET)
    support.refused(run, interface, support.EXIT_CHECK_FAILED)
    tree = support.tk(project, "dep", "tree", TICKET).splitlines()
    assert len(tree) == 1 and TICKET in tree[0], \
        f"by the ticket tool the failed ticket depends on something after its failing close: {tree}"
