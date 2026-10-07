"""Stale check evidence (KPI S4, CAP-38.d).

"A ticket that changes governance files cannot close on check results recorded for another commit or inputs
hash: gov close re-runs the checks or rejects the stale green evidence."

What that sentence means in a project (README, "Stale evidence"): W1-26's runner writes no result into the
project, so the only check result a close can stand on is the one of its own run at the commit being closed
(DEC-454: "re-runs the checks at HEAD ... It trusts no recorded result"). Measured here: a check that was
green at another commit, or at this commit before what it reads changed, and is red when the close runs,
refuses; a check that was red at another commit and is green at the commit being closed does not, and the
close record states the status of the commit being closed. No source gives a rule about how often or in
which commits of the ticket a governance file changed: a declaration changed twice, green at closing, closes.

Every project declares its own checks (``project_with_checks``); the green evidence of each case is the
answer of ``gov check --json`` itself, with the commit in its ``provenance``.
"""

import w1_30_support as support

TICKET = "PROJ-stl1"
WBS = "W1-stale"

SETTINGS = "governance/project/settings.yaml"
NOTES = "governance/project/notes.yaml"
MAINTENANCE = "local-state/maintenance"
FEATURE = {"src/example/feature.py": "# feature\n"}

README_PRESENT = support.declared_check("readme-present", "test -s README.md")
SETTINGS_STRICT = support.declared_check("settings-strict", f"grep -qx 'mode: strict' {SETTINGS}",
                                         family="path-map compliance")
NOT_IN_MAINTENANCE = support.declared_check("not-in-maintenance", f"test ! -e {MAINTENANCE}",
                                            family="recovery/rebuild")

STRICT = "mode: strict\nlevel: 2\n"
LOOSE = "mode: loose\nlevel: 2\n"


def _settings_project(project_with_checks):
    project = project_with_checks(README_PRESENT, SETTINGS_STRICT)
    project.write(SETTINGS, "mode: strict\n")
    project.commit("the project's settings", who=support.ORCHESTRATOR)
    return project


def _status_at(project, sandbox, check_id, commit):
    """The status W1-26's runner gives ``check_id`` now, with ``commit`` as the commit of that result."""
    entry = support.checks_at_head(project, sandbox)[check_id]
    assert entry["provenance"]["commit"] == commit, \
        f"the fixture is wrong: the runner's result is for {entry['provenance']['commit']}, not {commit}"
    return entry["status"]


def _red_then_green(project_with_checks, sandbox):
    """``settings-strict`` is red at the ticket's first commit and green at the commit being closed."""
    project = _settings_project(project_with_checks)
    support.start_ticket(project, TICKET, WBS)
    first = support.engineer_commit(project, TICKET, {**FEATURE, SETTINGS: LOOSE})
    assert _status_at(project, sandbox, "settings-strict", first) == support.RED, \
        "the fixture is wrong: the check is not red at the ticket's first commit"
    support.engineer_commit(project, TICKET, {SETTINGS: STRICT})
    head = support.checkpointed(project, TICKET)
    assert _status_at(project, sandbox, "settings-strict", head) == support.GREEN, \
        "the fixture is wrong: the check is not green at the commit being closed"
    assert support.red_hard_blocks(support.checks_at_head(project, sandbox)) == []
    return project, head


def test_a_check_green_at_an_earlier_commit_and_red_at_the_commit_being_closed_refuses(
        project_with_checks, sandbox, interface):
    project = _settings_project(project_with_checks)
    support.start_ticket(project, TICKET, WBS)
    first = support.engineer_commit(project, TICKET, {**FEATURE, SETTINGS: STRICT})
    # The green evidence of another commit: the runner's own answer at the ticket's first commit.
    entries = support.checks_at_head(project, sandbox)
    assert support.red_hard_blocks(entries) == [] and _status_at(project, sandbox, "settings-strict", first) == \
        support.GREEN, "the fixture is wrong: the checks are not green at the ticket's first commit"
    support.engineer_commit(project, TICKET, {SETTINGS: LOOSE})
    head = support.checkpointed(project, TICKET)
    assert _status_at(project, sandbox, "settings-strict", head) == support.RED, \
        "the fixture is wrong: the check is not red at the commit being closed"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "settings-strict" in support.error_text(error), f"the answer does not name the red check\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_check_red_at_an_earlier_commit_and_green_at_the_commit_being_closed_closes(
        project_with_checks, sandbox, interface):
    project, _ = _red_then_green(project_with_checks, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_the_close_record_states_the_status_of_the_commit_being_closed_not_an_earlier_one(
        project_with_checks, sandbox, interface):
    project, head = _red_then_green(project_with_checks, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    front = support.the_close_record(project, TICKET)
    stated = (front.get(support.CHECK_COMMIT_KEY), support.recorded_check_statuses(front).get("settings-strict"))
    assert stated == (head, support.GREEN), \
        f"the close record states {stated} for settings-strict; at the commit being closed it is {(head, support.GREEN)}"


def test_a_check_green_at_this_commit_before_what_it_reads_changed_refuses(project_with_checks, sandbox, interface):
    """The same commit, other inputs: the check reads a file git does not track."""
    project = project_with_checks(README_PRESENT, NOT_IN_MAINTENANCE)
    project.write(".gitignore", ".gov-runtime/\nlocal-state/\n")
    project.commit("the project's untracked state", who=support.ORCHESTRATOR)
    support.start_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {**FEATURE, NOTES: "note: one\n"})
    head = support.checkpointed(project, TICKET)
    # The green evidence of this very commit.
    assert support.red_hard_blocks(support.checks_at_head(project, sandbox)) == [] and \
        _status_at(project, sandbox, "not-in-maintenance", head) == support.GREEN, \
        "the fixture is wrong: the checks are not green at the commit being closed"
    project.write(MAINTENANCE, "since today\n")
    assert support.head_of(project) == head and project.waiting_paths() == [], \
        "the fixture is wrong: the change of the check's input is visible to git"
    assert _status_at(project, sandbox, "not-in-maintenance", head) == support.RED, \
        "the fixture is wrong: the check is not red after its input changed"

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "not-in-maintenance" in support.error_text(error), \
        f"the answer does not name the red check\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_declaration_changed_in_two_commits_and_green_at_the_commit_being_closed_closes(
        project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT)
    declaration = f"{support.CHECKS_REL}/feature-present.yaml"
    text = ('id: "feature-present"\nfamily: "mutation scope"\ntier: "G1"\nseverity: "{severity}"\n'
            'command: "test -s src/example/feature.py"\n')
    support.start_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {**FEATURE, declaration: text.format(severity=support.WARNING)})
    support.engineer_commit(project, TICKET, {declaration: text.format(severity=support.HARD_BLOCK)})
    support.checkpointed(project, TICKET)
    changes = support.git(project.root, "log", "--format=%H", "--", declaration).split()
    entries = support.checks_at_head(project, sandbox)
    assert len(changes) == 2 and support.red_hard_blocks(entries) == [] and \
        (entries["feature-present"]["severity"], entries["feature-present"]["status"]) == \
        (support.HARD_BLOCK, support.GREEN), "the fixture is wrong"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
