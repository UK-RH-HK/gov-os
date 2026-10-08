"""A close that fails at its last step, a stale record store, the installed kernel (DEC-487).

**The last step.** "A close that fails at its last step leaves no record that says the ticket closed." The
ticket is green and clean; the ticket tool fails when it is asked to close the ticket, or the close record
cannot be written. In both the ticket stays in progress and nothing in the tree says it closed: no close record
with status ACTIVE, no checkpoint of the ticket whose next action is "ticket closed"
(``support.records_saying_closed``).

**A stale record store.** "A record store older than the commit being closed refuses (the context would be
built from superseded records); the answer names ``gov rebuild``." The store is loaded; then the owner's
commit supersedes the decision the ticket names as its source; the close runs without a reload. The case holds
afterwards, with the store loaded again, that ``gov context`` answers ``BLOCKED`` for the ticket: so the store
the close read hid it. DEC-490: the case holds the behaviour only (refused, ``gov rebuild`` named, nothing
closed), and the refusal is "could not measure": exit code 1, not counted, no repair ticket. How the store's
freshness is told is the engineer's (a mark the store or the runtime already keeps).

**The installed kernel.** "The installed kernel counts as governance files: a ticket commit under
``governance/kernel/`` runs the checks, as one under the template's kernel does." A hard-block check is red and
the ticket's commit adds a file under ``governance/kernel/``: refused, the check named. The green side is the
eighth form of ``test_a_change_under_each_governance_prefix_has_the_checks_run`` (governance_checks).
"""

import shutil

import w1_30_support as support

TICKET = "PROJ-last"
WBS = "W1-last"
TOOL = "governance/kernel/bin/tk"
INSTALLED = "governance/kernel/hooks/sample-hook.sh"

README_PRESENT = support.declared_check("readme-present", "test -s README.md")
LICENSE_PRESENT = support.declared_check("license-present", "test -s LICENSE", family="graph integrity")


def _nothing_says_closed(project, run):
    assert support.ticket_status(project.root, TICKET) == "in_progress", \
        f"the ticket's status is {support.ticket_status(project.root, TICKET)!r}\n{run.describe()}"
    saying = support.records_saying_closed(project.root, TICKET)
    assert not saying, f"the close failed and these say the ticket closed: {saying}\n{run.describe()}"


def test_a_ticket_tool_that_fails_on_closing_leaves_nothing_that_says_the_ticket_closed(
        project, sandbox, interface, monkeypatch, tmp_path):
    """The project's ticket tool does everything but ``close``; ``PATH`` holds no other ticket tool."""
    support.build_ticket(project, TICKET, WBS)
    working = tmp_path / "tk-as-it-was"
    shutil.copy2(project.root / TOOL, working)
    (project.root / TOOL).write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "close" ]; then echo "planted: the ticket tool fails on closing" >&2; exit 7; fi\n'
        f'exec "{working}" "$@"\n', encoding="utf-8")
    project.commit("the ticket tool", who=support.ORCHESTRATOR)
    monkeypatch.setenv("PATH", support.path_without("tk", tmp_path / "path"))
    support.load_store(project, sandbox)

    run = support.run_close(project, sandbox, TICKET, store=False)

    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode != support.EXIT_OK, \
        f"gov close reports success although the ticket tool failed on closing\n{run.describe()}"
    _nothing_says_closed(project, run)


def test_a_close_record_that_cannot_be_written_leaves_nothing_that_says_the_ticket_closed(
        project, sandbox, interface, tmp_path):
    """As ``test_close_record_unwritable_ticket_stays_open``: a twin project's close names where the record
    goes, and a file stands where the record's folder would be."""
    twin = support.Project(tmp_path / "twin")
    support.build_ticket(twin, TICKET, WBS)
    record = support.result_of(support.run_close(twin, sandbox, TICKET), interface)["close_record"]

    support.build_ticket(project, TICKET, WBS)
    folder = (project.root / record).parent
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.write_text("a file where the folder of the close record goes\n", encoding="utf-8")
    project.commit("a file where the folder of the close record goes", who=support.ORCHESTRATOR)

    run = support.run_close(project, sandbox, TICKET)

    support.refused(run, interface, support.EXIT_GOV_ERROR)
    _nothing_says_closed(project, run)


def test_a_record_store_older_than_the_commit_being_closed_refuses_and_names_the_rebuild(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS)
    support.load_store(project, sandbox)
    assert project.gov(sandbox, "context", TICKET, "--json").envelope()["ok"] is True, \
        "the fixture is wrong: the ticket's context cannot be built before the owner's commit"
    project.add_decision(support.BASE_SOURCE, "SUPERSEDED", title="The base decision", superseded_by="DEC-newer")
    project.add_decision("DEC-newer", "ACTIVE", title="The decision that replaces it", supersedes=[support.BASE_SOURCE])
    project.commit("the owner supersedes the base decision", who=support.OWNER)

    run = support.run_close(project, sandbox, TICKET, store=False)

    closed = support.ticket_status(project.root, TICKET)
    saying = support.records_saying_closed(project.root, TICKET)
    support.load_store(project, sandbox)
    error = support.context_error(project, sandbox, TICKET)
    assert error["code"] == "BLOCKED" and support.BASE_SOURCE in support.error_text(error), \
        f"the fixture is wrong: with the store loaded again gov context gives {error}"

    error = support.refused_without_a_finding(run, interface)   # "could not measure": exit code 1 (DEC-490)
    assert "gov rebuild" in support.error_text(error), f"the answer does not name gov rebuild\n{run.describe()}"
    assert closed == "in_progress" and not saying, f"status {closed!r}; saying closed: {saying}\n{run.describe()}"
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)


def test_a_ticket_commit_under_the_installed_kernel_refuses_where_a_hard_block_check_is_red(
        project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    support.start_ticket(project, TICKET, WBS)
    commit = support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n",
                                                        INSTALLED: "#!/bin/sh\nexit 0\n"})
    support.checkpointed(project, TICKET)
    assert support.judged_by_w1_50(project, sandbox, [commit]) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the governance checks are not the only reason"
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == ["license-present"], f"the fixture is wrong: the red hard-block checks are {red}"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "license-present" in support.error_text(error), f"the answer does not name the red check\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
