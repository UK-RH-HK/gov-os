"""The governance checks of a close (KPI S4, CAP-38.d; DEC-454; DEC-455; DEC-476).

A ticket whose commits change a governance file closes only on checks run at the commit being closed
(DEC-454: "re-runs the checks at HEAD through W1-26's runner and refuses on any hard-block red. It trusts no
recorded result"). ``gov close`` holds no baseline and is strict for every project (DEC-476): any red
hard-block check refuses, whoever declared it and whatever made it red. The refusal is a finding about the
ticket's work (DEC-455 names "the governance checks"): exit code 3, counted, a dependent repair ticket.

Every project here declares its own checks (``project_with_checks``; README, "Round 6"): the kernel's
declarations are not copied, so no check is red for a reason of the test project. Each check's command
measures the project itself. Every case asks W1-26's runner (``gov check --json``) for the state of the
checks right before the close, and fails there when the project is not what the case is about.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-gvc1"
WBS = "W1-govchecks"

SETTINGS = "governance/project/settings.yaml"
NOTES = "governance/project/notes.yaml"
CHECKS = support.CHECKS_REL
KERNEL = "template/governance/kernel"

# The project's own checks. Each command reads the project; none is a constant.
README_PRESENT = support.declared_check("readme-present", "test -s README.md")
SETTINGS_STRICT = support.declared_check("settings-strict", f"grep -qx 'mode: strict' {SETTINGS}",
                                         family="path-map compliance")
LICENSE_PRESENT = support.declared_check("license-present", "test -s LICENSE", family="graph integrity")
LICENSE_WANTED = support.declared_check("license-wanted", "test -s LICENSE", severity=support.WARNING,
                                        family="graph integrity")
ABSENT_COMMAND = "no-such-program-w1-30"
TOOL_ABSENT = support.declared_check("tool-absent", f"{ABSENT_COMMAND} --verify", family="index freshness")
TOOL_ABSENT_WARNING = support.declared_check("tool-absent", f"{ABSENT_COMMAND} --verify",
                                             severity=support.WARNING, family="index freshness")
NEVER_ENDS = support.declared_check("never-ends", "sleep 120", family="index freshness")

# The limit the time-limit case gives the close (settlement 13), in seconds.
LIMIT = ("--timeout", "8")


def _declaration(check_id, command, severity):
    return (f'id: "{check_id}"\nfamily: "mutation scope"\ntier: "G1"\nseverity: "{severity}"\n'
            f'command: "{command}"\n')


def _ready(project, files):
    """The ticket's work, with ``files`` changed by its engineer, and the checkpoint: returns ``HEAD``."""
    support.start_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n", **files})
    return support.checkpointed(project, TICKET)


def _refused_naming(run, interface, check_id):
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert check_id in support.error_text(error), f"the answer does not name the check {check_id}\n{run.describe()}"
    return error


def _one_red(project, sandbox, check_id):
    """The fixture: by W1-26's runner, ``check_id`` is the one red hard-block check at the commit being closed."""
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == [check_id], f"the fixture is wrong: the red hard-block checks are {red}, not [{check_id!r}]"


def _none_red(project, sandbox):
    """The fixture: by W1-26's runner, no hard-block check is red at the commit being closed. Returns the
    runner's entries."""
    entries = support.checks_at_head(project, sandbox)
    assert support.red_hard_blocks(entries) == [], \
        f"the fixture is wrong: hard-block checks are red: {support.red_hard_blocks(entries)}"
    return entries


# --------------------------------------------------------------------------
# 1. Any red hard-block check refuses (DEC-454, DEC-476)
# --------------------------------------------------------------------------

def test_a_red_hard_block_check_the_ticket_declared_refuses_the_close(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT)
    _ready(project, {f"{CHECKS}/changelog-present.yaml": _declaration("changelog-present", "test -s CHANGELOG.md",
                                                                      support.HARD_BLOCK)})
    _one_red(project, sandbox, "changelog-present")

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming(run, interface, "changelog-present")
    support.assert_not_closed(project, TICKET)


def test_a_red_hard_block_check_the_ticket_did_not_touch_refuses_the_close(project_with_checks, sandbox, interface):
    """The red check is the project's from its first commit; the ticket adds another declaration, green."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _ready(project, {f"{CHECKS}/feature-present.yaml": _declaration("feature-present",
                                                                    "test -s src/example/feature.py",
                                                                    support.HARD_BLOCK)})
    _one_red(project, sandbox, "license-present")

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming(run, interface, "license-present")
    support.assert_not_closed(project, TICKET)


def test_a_red_hard_block_check_refuses_a_ticket_whose_governance_change_declares_no_check(
        project_with_checks, sandbox, interface):
    """The ticket changes a file under ``governance/project/`` and no check declaration."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _ready(project, {NOTES: "note: one\n"})
    _one_red(project, sandbox, "license-present")

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming(run, interface, "license-present")
    support.assert_not_closed(project, TICKET)


def test_a_failing_check_of_severity_warning_refuses_nothing(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_WANTED)
    _ready(project, {NOTES: "note: one\n"})
    entries = _none_red(project, sandbox)
    assert entries["license-wanted"]["status"] != support.GREEN, \
        "the fixture is wrong: the warning check does not fail"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_a_refusal_for_a_red_check_is_counted(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _ready(project, {NOTES: "note: one\n"})
    _one_red(project, sandbox, "license-present")

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming(run, interface, "license-present")
    assert support.iteration_count(project.root, TICKET) == 1, \
        f"the close refused for a red check is not counted as one iteration\n{run.describe()}"


def test_a_refusal_for_a_red_check_opens_a_dependent_repair_ticket(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    _ready(project, {NOTES: "note: one\n"})
    _one_red(project, sandbox, "license-present")

    run = support.run_close(project, sandbox, TICKET)

    _refused_naming(run, interface, "license-present")
    support.assert_dependent_repair_ticket(project, TICKET, run)


# --------------------------------------------------------------------------
# 2. The green path: the close record names the commit and every check's status
# --------------------------------------------------------------------------

def _green_project(project_with_checks):
    """Two hard-block checks that are green, and a warning check that fails."""
    project = project_with_checks(README_PRESENT, SETTINGS_STRICT, LICENSE_WANTED)
    project.write(SETTINGS, "mode: strict\n")
    project.commit("the project's settings", who=support.ORCHESTRATOR)
    return project


def test_a_governance_changing_ticket_closes_when_no_hard_block_check_is_red(project_with_checks, sandbox, interface):
    project = _green_project(project_with_checks)
    _ready(project, {NOTES: "note: one\n"})
    entries = _none_red(project, sandbox)
    assert {entries[name]["status"] for name in ("readme-present", "settings-strict")} == {support.GREEN}, \
        f"the fixture is wrong: the project's hard-block checks are not green: {support.statuses(entries)}"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_the_close_record_names_the_commit_being_closed(project_with_checks, sandbox, interface):
    project = _green_project(project_with_checks)
    support.start_ticket(project, TICKET, WBS)
    changed = support.engineer_commit(project, TICKET, {"src/example/feature.py": "# feature\n",
                                                        NOTES: "note: one\n"})
    head = support.checkpointed(project, TICKET)
    assert head != changed, "the fixture is wrong: the governance file was changed in the commit being closed"
    _none_red(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    front = support.the_close_record(project, TICKET)
    assert front.get(support.CHECK_COMMIT_KEY) == head, \
        f"the close record names {front.get(support.CHECK_COMMIT_KEY)!r} as the commit of the checks, not {head}"


def test_the_close_record_states_every_checks_status_as_run_at_that_commit(project_with_checks, sandbox, interface):
    project = _green_project(project_with_checks)
    _ready(project, {NOTES: "note: one\n"})
    expected = support.statuses(_none_red(project, sandbox))
    assert expected["license-wanted"] == support.YELLOW and expected["settings-strict"] == support.GREEN, \
        f"the fixture is wrong: {expected}"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    recorded = support.recorded_check_statuses(support.the_close_record(project, TICKET))
    assert recorded == expected, \
        f"the close record states {recorded}; W1-26's runner gave {expected} at the commit being closed"


# A file under each prefix that counts as a governance file (settlement 5).
GOVERNANCE_FILES = {
    f"{KERNEL}/checks/": (f"{CHECKS}/feature-present.yaml",
                          _declaration("feature-present", "test -s src/example/feature.py", support.WARNING)),
    f"{KERNEL}/schemas/": (f"{KERNEL}/schemas/sample.schema.json", '{"type": "object"}\n'),
    "governance/project/": (NOTES, "note: one\n"),
    f"{KERNEL}/hooks/": (f"{KERNEL}/hooks/sample-hook.sh", "#!/bin/sh\nexit 0\n"),
    f"{KERNEL}/skills/": (f"{KERNEL}/skills/sample/SKILL.md",
                          '---\nname: sample\ndescription: A sample skill.\nversion: "1.0.0"\n---\n# sample\n\nText.\n'),
    f"{KERNEL}/policies/": (f"{KERNEL}/policies/sample-policy.md", "# A sample policy\n\nText.\n"),
    f"{KERNEL}/roles/": (f"{KERNEL}/roles/sample-role.md", "# A sample role\n\nText.\n"),
}
assert set(GOVERNANCE_FILES) == set(support.GOVERNANCE_PREFIXES)


@pytest.mark.parametrize("prefix", sorted(GOVERNANCE_FILES))
def test_a_change_under_each_governance_prefix_has_the_checks_run(prefix, project_with_checks, sandbox, interface):
    project = _green_project(project_with_checks)
    rel, text = GOVERNANCE_FILES[prefix]
    head = _ready(project, {rel: text})
    _none_red(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    front = support.the_close_record(project, TICKET)
    assert front.get(support.CHECK_COMMIT_KEY) == head, \
        f"a change of {rel} did not have the checks run at the commit being closed: " \
        f"{support.CHECK_COMMIT_KEY} is {front.get(support.CHECK_COMMIT_KEY)!r}"


# --------------------------------------------------------------------------
# 3. No governance file changed: no check result is needed and none is claimed
# --------------------------------------------------------------------------

def _no_governance_change(project_with_checks, sandbox):
    """A project with a red hard-block check, and a ticket that changes no governance file."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    support.build_ticket(project, TICKET, WBS)
    _one_red(project, sandbox, "license-present")
    return project


def test_a_ticket_that_changes_no_governance_file_needs_no_check_result(project_with_checks, sandbox, interface):
    project = _no_governance_change(project_with_checks, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"


def test_the_close_record_of_a_ticket_that_changes_no_governance_file_claims_no_check_result(
        project_with_checks, sandbox, interface):
    project = _no_governance_change(project_with_checks, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    front = support.the_close_record(project, TICKET)
    claimed = {key: front[key] for key in (support.CHECK_COMMIT_KEY, support.CHECK_RESULT_KEY) if front.get(key)}
    assert not claimed, f"the close record claims a check result although no governance file changed: {claimed}"


# --------------------------------------------------------------------------
# 5. A check that cannot run: never a close
# --------------------------------------------------------------------------

def test_a_hard_block_check_whose_command_is_absent_refuses_the_close(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, TOOL_ABSENT)
    _ready(project, {NOTES: "note: one\n"})

    run = support.run_close(project, sandbox, TICKET)

    error = _refused_naming(run, interface, "tool-absent")
    assert ABSENT_COMMAND in support.error_text(error), \
        f"the answer does not say which command is absent\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_warning_check_whose_command_is_absent_refuses_the_close(project_with_checks, sandbox, interface):
    """A warning check that ran and failed refuses nothing; one that could not run measured nothing."""
    project = project_with_checks(README_PRESENT, TOOL_ABSENT_WARNING)
    _ready(project, {NOTES: "note: one\n"})
    _none_red(project, sandbox)

    run = support.run_close(project, sandbox, TICKET)

    error = _refused_naming(run, interface, "tool-absent")
    assert ABSENT_COMMAND in support.error_text(error), \
        f"the answer does not say which command is absent\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_check_over_its_time_limit_refuses_the_close(project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, NEVER_ENDS)
    _ready(project, {NOTES: "note: one\n"})

    run = support.run_close(project, sandbox, TICKET, *LIMIT)

    error = _refused_naming(run, interface, "never-ends")
    assert "time" in support.error_text(error).lower(), \
        f"the answer does not give the time limit as the reason\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
