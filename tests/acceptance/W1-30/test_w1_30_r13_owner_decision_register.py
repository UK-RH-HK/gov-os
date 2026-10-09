"""Round 13, piece 6: the owner's decision may be an entry of the project's register file (DEC-483).

DEC-483: "W1-30's escalation path reads the owner's decision from decision files, not from a register file such
as this repository's." DEC-473: "A decision is recorded either as a decision file, or as an entry of a register
file that the project names in one line of configuration [...] With no register file named, decision files
alone count. [...] a level-3 heading ``### DEC-<digits>`` at the start of a line, followed by a space, a colon
or a dash and the title. A heading inside a fenced code block does not count." DEC-479: the register is named
by the key ``decision_register`` of the project's path map.

After an escalation, ``gov close <ticket> --owner-decision <id>`` accepts a decision file as today, and also
an entry of the named register. What DEC-487 asks of a decision file, an entry must meet in the form an entry
can state it (README, round 13, settlement 30; the stricter reading throughout):

| a decision file (today)                                   | a register entry                                          |
|-----------------------------------------------------------|-----------------------------------------------------------|
| one committed decision record of that id                  | exactly one entry heading of that id, outside fenced blocks, in the named register of the commit being closed |
| its status is ACTIVE                                      | the entry holds a status line, ``**Status:** ACCEPTED`` (the first word after the label), before the next heading |
| the owner's: the commit that set it ACTIVE carries ``Role: owner`` and no other role (W1-11) | the owner's: the commit that brought the entry's heading into the register carries ``Role: owner`` and no other role (package P-2) |
| recorded after the escalation began                       | the register of the commit at which the escalation began does not hold the entry's heading |
| not used for an escalation of this ticket before          | the same                                                  |

How a case holds "lifted": the close given the decision runs the tests and is refused for the failing one
(exit code 3). "Not lifted": it stays blocked (exit code 4), and so does the close after it.
"""

import w1_30_support as support

TICKET = "PROJ-ownr"
WBS = "W1-ownr"
REGISTER_KEY = "decision_register"
# The register of these projects. No file of this repository has this path.
REGISTER = "records/decision-log.md"
# A file with the form of a register that no configuration names.
NOT_NAMED = "records/other-log.md"
ACCEPTED = "ACCEPTED (owner, 2026-10-09)"
BOTH_ROLES = ("Role: owner", "Role: orchestrator")


def entry(decision, status=ACCEPTED, title="Continue the ticket"):
    """A register entry: its heading (DEC-473) and, with ``status``, its status line."""
    lines = [f"### {decision} — {title}"]
    if status is not None:
        lines.append(f"- **Status:** {status}")
    lines.append("- **Decision:** A fixture.")
    return "\n".join(lines) + "\n\n"


def _project(tmp_path, named=True):
    """A project whose path map names the register (``named``), holding the register with one old entry from
    before the ticket's first commit, and an escalated ticket."""
    settings = dict(support.SUITE_SETTINGS)
    if named:
        settings[REGISTER_KEY] = REGISTER
    project = support.Project(tmp_path / "project", settings=settings)
    for rel in (REGISTER, NOT_NAMED):
        project.write(rel, "# Decisions\n\n" + entry("DEC-100", title="An earlier decision of the owner"))
    project.commit("the register", who=support.OWNER)
    return project


def _escalated(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    support.escalate(project, sandbox, interface, TICKET)


def _record(project, text, rel=REGISTER, who=support.OWNER, trailers=None):
    """``text`` is appended to the register and committed by ``who``."""
    path = project.root / rel
    project.write(rel, path.read_text(encoding="utf-8") + text)
    return project.commit("record decisions", who=who, trailers=trailers, exact=trailers is not None)


def _lifted_by(project, sandbox, interface, decision):
    """The close given ``decision`` ran: it is refused for the failing acceptance test, exit code 3."""
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", decision)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert "test_fail" in support.error_text(error), f"the close did not run the tests\n{run.describe()}"
    support.commit_what_a_refusal_left(project)
    return run


def _not_lifted_by(project, sandbox, interface, decision, why):
    run = support.run_close(project, sandbox, TICKET, "--owner-decision", decision)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False and run.returncode == support.EXIT_BLOCKED, \
        f"{why}: the close given {decision} does not stay blocked (exit code 4)\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    support.commit_what_a_refusal_left(project)


# --------------------------------------------------------------------------
# New: an entry of the named register lifts the escalation
# --------------------------------------------------------------------------

def test_an_accepted_entry_the_owner_recorded_after_the_escalation_lifts_it(built, tmp_path, sandbox, interface):
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)
    _record(project, entry("DEC-501"))

    _lifted_by(project, sandbox, interface, "DEC-501")

    assert support.iteration_count(project.root, TICKET) == 1, \
        "the escalation was lifted and the refusal after it is not the first of a new count"


def test_an_entry_that_lifted_one_escalation_lifts_no_second(built, tmp_path, sandbox, interface):
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)
    _record(project, entry("DEC-501"))
    _lifted_by(project, sandbox, interface, "DEC-501")
    for _ in range(2):
        support.refused(support.run_close(project, sandbox, TICKET), interface, support.EXIT_CHECK_FAILED)
        support.commit_what_a_refusal_left(project)
    support.refused(support.run_close(project, sandbox, TICKET), interface, support.EXIT_BLOCKED)

    _not_lifted_by(project, sandbox, interface, "DEC-501", "an entry lifted a second escalation")
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "an entry used before")


# --------------------------------------------------------------------------
# As today, and what an entry must be
# --------------------------------------------------------------------------

def test_a_decision_file_lifts_the_escalation_of_a_project_that_names_a_register(built, tmp_path, sandbox,
                                                                                  interface):
    """As today: the register is named and the owner's decision is a decision file."""
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)
    project.add_decision("DEC-file", "ACTIVE", title="Continue")
    project.commit("the owner's decision", who=support.OWNER)

    _lifted_by(project, sandbox, interface, "DEC-file")


def test_with_no_register_named_an_entry_lifts_nothing(built, tmp_path, sandbox, interface):
    """The path map names no register: the file with the form of one is no register."""
    project = _project(tmp_path, named=False)
    _escalated(project, sandbox, interface)
    _record(project, entry("DEC-501"))
    _record(project, entry("DEC-501"), rel=NOT_NAMED)

    _not_lifted_by(project, sandbox, interface, "DEC-501", "an entry of a register no configuration names")
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "no register is named")


def test_an_entry_of_a_file_the_path_map_does_not_name_lifts_nothing(built, tmp_path, sandbox, interface):
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)
    _record(project, entry("DEC-502"), rel=NOT_NAMED)

    _not_lifted_by(project, sandbox, interface, "DEC-502", "an entry of another file than the named register")
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "an entry of another file")


def test_an_entry_recorded_before_the_escalation_began_lifts_none(built, tmp_path, sandbox, interface):
    """``DEC-100`` is in the register from before the ticket's first commit: accepted, the owner's."""
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)

    _not_lifted_by(project, sandbox, interface, "DEC-100", "an entry older than the escalation lifted it")
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "an entry older than the escalation")


def test_an_entry_that_is_not_one_accepted_entry_of_the_owner_lifts_nothing(built, tmp_path, sandbox, interface):
    """Each form is recorded after the escalation began and is given in turn; none lifts. The last entry is as
    it must be and lifts: the register of this project is read."""
    project = _project(tmp_path)
    _escalated(project, sandbox, interface)
    _record(project, "```\n" + entry("DEC-601") + "```\n\n"
            + entry("DEC-602", status="PROPOSED")
            + entry("DEC-603", status=None)
            + entry("DEC-604", status="SUPERSEDED by DEC-700; was ACCEPTED (owner, 2026-10-01)")
            + entry("DEC-605") + entry("DEC-605", title="The same id again")
            + f"#### DEC-606 — A heading of another level\n- **Status:** {ACCEPTED}\n\n")
    _record(project, entry("DEC-607"), who=support.ORCHESTRATOR)
    _record(project, entry("DEC-608"), trailers=BOTH_ROLES)
    _record(project, entry("DEC-609"), trailers=())
    _record(project, entry("DEC-610"))
    forms = {
        "DEC-601": "a heading inside a fenced block",
        "DEC-602": "an entry whose status is PROPOSED",
        "DEC-603": "an entry without a status line",
        "DEC-604": "an entry that is superseded",
        "DEC-605": "an id two entries carry",
        "DEC-606": "a heading that is not of level 3",
        "DEC-607": "an entry the orchestrator's commit recorded",
        "DEC-608": "an entry recorded by a commit with the owner's role and another",
        "DEC-609": "an entry recorded by a commit without a role",
        "DEC-999": "an id no entry carries",
    }
    for decision, form in forms.items():
        _not_lifted_by(project, sandbox, interface, decision, form)
    support.assert_escalation_in_force(project, sandbox, interface, TICKET, "none of the entries qualifies")

    _lifted_by(project, sandbox, interface, "DEC-610")
