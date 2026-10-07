"""Where ``gov close`` finds the ticket tool (round 9; DEC-492, first point).

DEC-492: ``gov close`` "finds the ticket tool on PATH as well as at the kernel path". Until this round it
looked only at the installed kernel's place (``governance/kernel/bin/tk``), so a project that has the tool on
``PATH`` alone (this one, before adoption) could close no ticket and open no repair ticket.

Each case states both places before the close:

| the kernel's place | ``PATH``              | the case                                                    |
|--------------------|-----------------------|-------------------------------------------------------------|
| no tool            | the tool              | a clean ticket closes; a refused close opens its repair ticket |
| the tool           | a tool that fails     | the kernel's is used: the ticket closes, the other was never started |
| a tool that fails  | the tool              | the kernel's is used: the close fails, the other was never started |
| no tool            | no tool               | the answer says so; nothing is closed                        |

The tool on ``PATH`` is a copy of the kernel's in a folder of its own, first on a ``PATH`` that holds no other
``tk`` (``support.path_with_tool``). Where the case is about which tool was used, the tool on ``PATH`` writes a
line to a file outside the project every time it is started. A project "without the tool at the kernel's
place" has it removed by the owner before the ticket's first commit, so the removal is no commit of the
ticket's range.
"""

import re

import w1_30_support as support

TICKET = "PROJ-tool"
WBS = "W1-tool"
NAMES_THE_TOOL = re.compile(r"\btk\b|ticket tool", re.IGNORECASE)

FAILING_TOOL = "#!/bin/sh\necho 'planted: this ticket tool fails' >&2\nexit 7\n"


def _recording(marker, then):
    """A ticket tool that writes its arguments to ``marker`` and then does ``then`` (a shell line)."""
    return f'#!/bin/sh\necho "$@" >> "{marker}"\n{then}\n'


def _no_tool_at_the_kernels_place(project):
    (project.root / support.TOOL_REL).unlink()
    project.commit("the project has no ticket tool at the kernel's place", who=support.OWNER)


def _tool_at_the_kernels_place(project, script):
    (project.root / support.TOOL_REL).write_text(script, encoding="utf-8")
    project.commit("the project's ticket tool", who=support.OWNER)


def _close(project, sandbox, monkeypatch, path):
    """The close with ``path`` as ``PATH``. The store is loaded first, as ``support.run_close`` does."""
    support.load_store(project, sandbox)
    monkeypatch.setenv("PATH", path)
    return support.run_close(project, sandbox, TICKET, store=False)


def _nothing_says_closed(project, run):
    assert support.ticket_status(project.root, TICKET) == "in_progress", \
        f"the ticket's status is {support.ticket_status(project.root, TICKET)!r}\n{run.describe()}"
    saying = support.records_saying_closed(project.root, TICKET)
    assert not saying, f"the close failed and these say the ticket closed: {saying}\n{run.describe()}"


# --------------------------------------------------------------------------
# 1. The tool on PATH only
# --------------------------------------------------------------------------

def test_a_clean_ticket_closes_where_the_ticket_tool_is_on_path_only(project, sandbox, interface, monkeypatch, tmp_path):
    _no_tool_at_the_kernels_place(project)
    support.build_ticket(project, TICKET, WBS)
    path, _ = support.path_with_tool(tmp_path / "bin", tmp_path / "path")
    assert not (project.root / support.TOOL_REL).exists(), "the fixture is wrong: the kernel's place holds a tool"

    run = _close(project, sandbox, monkeypatch, path)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", \
        f"the ticket's status is {support.ticket_status(project.root, TICKET)!r} after a close that succeeded"
    assert len(support.close_records(project.root, TICKET)) == 1, "the close left no close record"


def test_a_refused_close_opens_its_repair_ticket_where_the_ticket_tool_is_on_path_only(
        project, sandbox, interface, monkeypatch, tmp_path):
    _no_tool_at_the_kernels_place(project)
    support.build_ticket(project, TICKET, WBS, failing=True)
    path, tool = support.path_with_tool(tmp_path / "bin", tmp_path / "path")
    assert not (project.root / support.TOOL_REL).exists(), "the fixture is wrong: the kernel's place holds a tool"

    run = _close(project, sandbox, monkeypatch, path)

    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert "test_fail" in text, f"the answer does not name the failing test\n{run.describe()}"
    support.assert_dependent_repair_ticket(project, TICKET, run, script=tool)
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the refusal is counted {support.iteration_count(project.root, TICKET)} times\n{run.describe()}"


# --------------------------------------------------------------------------
# 2. Both places hold a tool: the kernel's is the one used
# --------------------------------------------------------------------------

def test_the_kernels_ticket_tool_is_used_where_path_holds_another(project, sandbox, interface, monkeypatch, tmp_path):
    """The kernel's place holds the tool; the one on ``PATH`` fails whatever it is asked, and records that it
    was started."""
    support.build_ticket(project, TICKET, WBS)
    marker = tmp_path / "the-tool-on-path-was-started"
    path, _ = support.path_with_tool(tmp_path / "bin", tmp_path / "path", script=_recording(marker, "exit 7"))
    assert (project.root / support.TOOL_REL).is_file(), "the fixture is wrong: the kernel's place holds no tool"

    run = _close(project, sandbox, monkeypatch, path)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    assert not marker.exists(), \
        f"the ticket tool on PATH was started although the kernel's exists: {marker.read_text(encoding='utf-8')!r}"


def test_a_failing_kernel_ticket_tool_is_not_replaced_by_the_one_on_path(
        project, sandbox, interface, monkeypatch, tmp_path):
    """The kernel's place holds a tool that fails; the one on ``PATH`` works and records that it was started.
    The kernel's is the one used, so the close fails as the tool did and the other is never started."""
    _tool_at_the_kernels_place(project, FAILING_TOOL)
    support.build_ticket(project, TICKET, WBS)
    marker = tmp_path / "the-tool-on-path-was-started"
    working = tmp_path / "tk-as-it-was"
    working.write_bytes(support.KERNEL_TOOL.read_bytes())
    working.chmod(0o755)
    path, _ = support.path_with_tool(tmp_path / "bin", tmp_path / "path",
                                     script=_recording(marker, f'exec "{working}" "$@"'))

    run = _close(project, sandbox, monkeypatch, path)

    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != support.EXIT_OK, \
        f"gov close reports success although the kernel's ticket tool fails\n{run.describe()}"
    assert not marker.exists(), \
        f"the ticket tool on PATH was started although the kernel's exists: {marker.read_text(encoding='utf-8')!r}"
    _nothing_says_closed(project, run)


# --------------------------------------------------------------------------
# 3. Neither place holds a tool: the answer says so
# --------------------------------------------------------------------------

def test_the_answer_says_so_where_the_ticket_tool_is_at_neither_place(
        project, sandbox, interface, monkeypatch, tmp_path):
    _no_tool_at_the_kernels_place(project)
    support.build_ticket(project, TICKET, WBS)
    path = support.path_without(support.TOOL_NAME, tmp_path / "path")

    run = _close(project, sandbox, monkeypatch, path)

    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != support.EXIT_OK, \
        f"gov close reports success although no ticket tool is reachable\n{run.describe()}"
    assert NAMES_THE_TOOL.search(support.error_text(envelope["error"])), \
        f"the answer does not say that the ticket tool is absent\n{run.describe()}"
    _nothing_says_closed(project, run)
