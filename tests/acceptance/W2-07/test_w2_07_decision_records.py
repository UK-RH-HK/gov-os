"""KPI 3 as amended, the round-2 KPI and failure KPIs 3 and 4: the commits the work-without-a-task gate counts as
measured [DEC-896 item 1, DEC-923 item 2, DEC-906].

KPI 3: "A decision-record commit that changes only governance records (DEC-891's records: .tickets/,
docs/checkpoints/, docs/close/, docs/probes/, the register, the plan files, governance/project/orchestration/; and
the prompts, the briefs and the path map) and names an ACCEPTED decision, the owner's or a delegated one, also when
that decision was later superseded or changed, counts as measured for the work-without-a-task gate; a
decision-record commit that names no decision ever ACCEPTED, or changes any other path, still counts as unmeasured."

Round-2 KPI: "the work-without-a-task gate also counts as measured a commit that the owner-committed lists name,
acceptance_exemptions or accepted_history, each under its ACCEPTED owner decision, read as the trailer gate and
W1-01 read them; a Role: owner trailer alone measures nothing (DEC-906: a trailer is only text until W2-44)."

Failure KPI 3: "A decision-record commit outside an ACCEPTED decision counted as measured."
Failure KPI 4: "A commit counted as measured by its Role: owner trailer alone, or a code, test or kernel commit
counted as measured that no owner-committed list names."

The shape is W2-58's refused close (I2 F13): its allowed paths name the path map, and decision-record commits
(``Task: decision-record``, a ``Task:`` that names no ticket, DEC-500) changed the path map in its range, so the
close refused ``WORK_WITHOUT_TASK`` (DEC-490). A decision-record commit here is written as this repository writes
them: its subject names the decision ("Decision record DEC-…"), with ``Implements: DEC-…`` in its final trailer
block beside ``Task: decision-record`` and the role of whoever committed it. The orchestrator records the owner's
and its own delegated decisions (``Role: orchestrator``, DEC-861); ``Role: owner`` is written only where a case
shows what that trailer does, which is nothing on its own (DEC-923 item 2, DEC-906).

The owner-committed lists are the path map's ``accepted_history`` (DEC-734: ``{commit, decision}``, the decision an
ACCEPTED owner decision of the register whose text names the commit; the trailer gate takes a full or an
abbreviated id) and ``acceptance_exemptions`` (DEC-906 item 2: ``{commit, decision}``, W1-01 matches the whole id
only, the decision a ``DEC-<n>``). Their entries are the owner's own ``Role: owner`` commits outside any ticket
(DEC-891, DEC-906).
"""

import pytest

import w2_07_support as support

TICKET, WBS = "PROJ-dcrd", "W9-dcrd"
WORK_WITHOUT_TASK = "WORK_WITHOUT_TASK"
HISTORY_REFUSED = "ACCEPTED_HISTORY_REFUSED"
FEATURE = "src/example/feature.py"
ALLOWED = ("src/example/**", support.PATH_MAP_REL)
# A ticket the owner's listed commits change the work of: code and tests in its allowed paths, not the path map (the
# owner's list entries change the path map outside the ticket's work).
LISTED_ALLOWED = ("src/example/**", "tests/unit/w207/**")


def _ticket(project, allowed=ALLOWED):
    support.create_ticket(project, TICKET, WBS, allowed_paths=allowed)
    support.work(project, TICKET, {FEATURE: "# feature\n"})


def _decision_record(project, decision=None, status=support.OWNER_ACCEPTED, also=None, role="orchestrator",
                     path_map=True):
    """A decision-record commit in the ticket's range, by ``role`` (``orchestrator`` or ``owner``). With
    ``path_map`` the path map gains the close's time limit (a path of the ticket); with ``decision`` the register
    gains its entry (``status``) and the commit names it. ``also`` (``{path: text}``) is written in the same commit.
    Returns the commit."""
    if path_map:
        project.settings["close_timeout"] = 900
        project.write(support.PATH_MAP_REL, support.path_map_text(project.settings))
    if decision is not None:
        project.register_entry(decision, status, "The close's time limit is 900 seconds in this project.")
    for rel, text in (also or {}).items():
        project.write(rel, text)
    trailers = ["Task: decision-record"]
    if decision is not None:
        trailers.append(f"Implements: {decision}")
        subject = f"Decision record {decision}: the close's time limit"
    else:
        subject = "Register tidy: the close's time limit"
    trailers.append(f"Role: {role}")
    who = support.OWNER if role == "owner" else support.ORCHESTRATOR
    return project.commit(subject, who=who, trailers=tuple(trailers), exact=True)


def _restated(project, decision, new_status, by, note=""):
    """Later, a decision record of ``by`` (the register alone, no path of the ticket) restates ``decision``'s status
    line as ``new_status`` (and ``note`` after its basis), and adds ``by``'s own entry."""
    text = (project.root / support.REGISTER).read_text(encoding="utf-8")
    line = f"### {decision} — A decision of the fixture\n- **Status:** "
    start = text.index(line) + len(line)
    end = text.index("\n", start)
    project.write(support.REGISTER, text[:start] + f"{new_status} · **Basis:** the fixture{note}" + text[end:])
    project.register_entry(by, support.OWNER_ACCEPTED, f"It changes {decision}.")
    return project.commit(f"Decision record {by}: {decision} restated", who=support.ORCHESTRATOR,
                          trailers=("Task: decision-record", f"Implements: {by}", "Role: orchestrator"), exact=True)


def _changed(project, commit):
    return sorted(support.git(project, "show", "--name-only", "--format=", commit).split())


def _closes(project, sandbox, interface):
    run = support.run_close(project, sandbox, TICKET)
    support.closed(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed", f"the ticket is not closed\n{run.describe()}"


def _refused_as_unmeasured(project, sandbox, interface, commit, causes=(WORK_WITHOUT_TASK,)):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    assert any(cause in support.codes_of(error) or support.names(error, cause) for cause in causes), \
        f"the close was not refused for work without a task ({' or '.join(causes)})\n{run.describe()}"
    assert support.names(error, commit[:12]), f"the refusal does not name the unmeasured commit\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Measured by its decision: governance records only, under a decision ever ACCEPTED (KPI 3)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("status", [support.OWNER_ACCEPTED, support.DELEGATED_ACCEPTED],
                         ids=["owner-decision", "delegated-decision"])
def test_a_decision_record_of_governance_records_under_an_accepted_decision_counts_as_measured(status, project,
                                                                                              sandbox, interface):
    """The orchestrator's record (``Role: orchestrator``: no trailer of the owner's) of the path map and the
    register, under an ACCEPTED decision: the owner's, or a delegated one (DEC-903's form, 8f56ada1's shape)."""
    _ticket(project)
    record = _decision_record(project, "DEC-501", status=status)
    assert _changed(project, record) == sorted([support.PATH_MAP_REL, support.REGISTER]), "the fixture is wrong"
    assert "Role: owner" not in support.git(project, "show", "-s", "--format=%B", record), "the fixture is wrong"
    support.checkpointed(project, TICKET)
    _closes(project, sandbox, interface)


@pytest.mark.parametrize("later", ["superseded", "changed"])
def test_a_decision_record_under_a_decision_later_superseded_or_changed_counts_as_measured(later, project, sandbox,
                                                                                          interface):
    """The record was made under an ACCEPTED owner decision; a later decision superseded it (DEC-876's status form,
    65039414's shape) or changed it (a ``Changed by`` note on its status line)."""
    _ticket(project)
    record = _decision_record(project, "DEC-504")
    if later == "superseded":
        _restated(project, "DEC-504", support.superseded("DEC-599"), "DEC-599")
    else:
        _restated(project, "DEC-504", support.OWNER_ACCEPTED, "DEC-598",
                  note=" · **Changed by:** DEC-598: the close's time limit is 600 seconds")
    assert _changed(project, record) == sorted([support.PATH_MAP_REL, support.REGISTER]), "the fixture is wrong"
    support.checkpointed(project, TICKET)
    _closes(project, sandbox, interface)


def test_a_decision_record_that_changes_the_closing_tickets_own_file_counts_as_measured(project, sandbox, interface):
    """``.tickets/`` is a record (DEC-891): the register and the closing ticket's own file (its work), under an
    ACCEPTED owner decision (8d625805's shape)."""
    _ticket(project)
    rel = support.base.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    record = _decision_record(project, "DEC-505", path_map=False,
                              also={rel: text + "\nAmended under DEC-505: the close's time limit.\n"})
    assert _changed(project, record) == sorted([rel, support.REGISTER]), "the fixture is wrong"
    support.checkpointed(project, TICKET)
    _closes(project, sandbox, interface)


@pytest.mark.parametrize("rel", [
    "docs/checkpoints/PROJ-othr/README.md",
    "docs/close/PROJ-othr/README.md",
    "docs/probes/PROJ-othr/README.md",
    "governance/project/orchestration/packages/P-W9-dcrd.md",
    "governance/project/prompts/w9-orchestrator.md",
    "governance/project/briefs/LEAD-w9-common.md",
    "docs/plan/WAVE_9_WBS.md",
], ids=["checkpoints", "close", "probes", "orchestration", "prompts", "briefs", "plan"])
def test_a_decision_record_that_also_changes_another_governance_record_counts_as_measured(rel, project, sandbox,
                                                                                         interface):
    """Each of the other governance records of KPI 3, beside the path map and the register."""
    _ticket(project)
    record = _decision_record(project, "DEC-506", also={rel: "# A record of the fixture\n"})
    assert _changed(project, record) == sorted([support.PATH_MAP_REL, support.REGISTER, rel]), "the fixture is wrong"
    support.checkpointed(project, TICKET)
    _closes(project, sandbox, interface)


# --------------------------------------------------------------------------
# Unmeasured: no decision ever ACCEPTED, or a path that is not a record, whatever the trailer (failure KPIs 3, 4)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("status", [support.PROPOSED, support.REJECTED, support.superseded("DEC-599", was="PROPOSED")],
                         ids=["proposed", "rejected", "superseded-never-accepted"])
def test_a_decision_record_naming_a_decision_that_is_not_accepted_counts_as_unmeasured(status, project, sandbox,
                                                                                      interface):
    """Failure KPI 3: the decision it names was never ACCEPTED; the owner's trailer does not make up for it."""
    _ticket(project)
    record = _decision_record(project, "DEC-502", status=status, role="owner")
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)


def test_a_decision_record_naming_no_decision_counts_as_unmeasured(project, sandbox, interface):
    """Failure KPI 3: ``Task: decision-record`` and ``Role: owner``, and no decision named anywhere in the commit."""
    _ticket(project)
    record = _decision_record(project, None, role="owner")
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)


@pytest.mark.parametrize("role", ["orchestrator", "owner"])
@pytest.mark.parametrize("rel, text", [
    ("src/example/feature.py", "# feature, changed by a decision record\n"),
    ("tests/unit/test_w207_by_a_record.py", "def test_w207_by_a_record():\n    assert True\n"),
    ("template/governance/kernel/skills/w207/SKILL.md", "---\nname: w207\nversion: \"1.0.0\"\n---\n# w207\n"),
    ("docs/assessment/2026-10/W9-report.md", "# An assessment report\n"),
], ids=["code", "tests", "kernel", "assessment"])
def test_a_decision_record_that_also_changes_any_other_path_counts_as_unmeasured(rel, text, role, project, sandbox,
                                                                                interface):
    """Any path that is not a record (code, tests, the kernel, ``docs/assessment/``: 611955fa's shape) keeps the
    record unmeasured under an ACCEPTED owner decision; with ``Role: owner`` and no list naming it, failure KPI 4."""
    _ticket(project)
    record = _decision_record(project, "DEC-503", also={rel: text}, role=role)
    support.checkpointed(project, TICKET)
    _refused_as_unmeasured(project, sandbox, interface, record)


# --------------------------------------------------------------------------
# Measured by an owner-committed list, whatever paths it changes (the round-2 KPI)
# --------------------------------------------------------------------------

LISTED_PATHS = {
    "code": (FEATURE, "# feature, changed by the owner\n"),
    "tests": ("tests/unit/w207/test_w207_by_the_owner.py", "def test_w207_by_the_owner():\n    assert True\n"),
}


def _owners_commit(project, decision, which):
    """The owner's own decision-record commit (c9a08678's shape: ``Role: owner``) of a path of the ticket's work that
    is not a record (``which``: code or tests); it names ``decision``. Returns the commit."""
    rel, text = LISTED_PATHS[which]
    project.write(rel, text)
    return project.commit(f"Owner decision {decision}: {rel}", who=support.OWNER,
                          trailers=("Task: decision-record", f"Implements: {decision}", "Role: owner"), exact=True)


def _listed(project, key, commit, decision, status=support.OWNER_ACCEPTED, given=None):
    """The register gains ``decision``'s entry (``status``), whose text names ``commit`` by its full id, and the
    path map's ``key`` gains ``{commit: given or commit, decision}``: the owner's own ``Role: owner`` commit outside
    any ticket (DEC-891, DEC-906)."""
    project.register_entry(decision, status, f"The commit {commit} is accepted under this decision.")
    project.settings[key] = list(project.settings.get(key) or []) + [{"commit": given or commit,
                                                                       "decision": decision}]
    project.write(support.PATH_MAP_REL, support.path_map_text(project.settings))
    return project.setup_commit(f"the path map's {key}: {decision}")


@pytest.mark.parametrize("which", sorted(LISTED_PATHS))
@pytest.mark.parametrize("key, given", [
    (support.ACCEPTED_KEY, "full"),
    (support.ACCEPTED_KEY, "abbreviated"),
    (support.EXEMPTIONS_KEY, "full"),
], ids=["accepted_history", "accepted_history-abbreviated-id", "acceptance_exemptions"])
def test_a_commit_an_owner_committed_list_names_under_its_accepted_owner_decision_counts_as_measured(
        key, given, which, project, sandbox, interface):
    """The round-2 KPI: a listed commit is measured whatever paths it changes. ``accepted_history`` is read as the
    trailer gate reads it (DEC-734: a full or an abbreviated id), ``acceptance_exemptions`` as W1-01 reads it (the
    whole id)."""
    _ticket(project, allowed=LISTED_ALLOWED)
    owners = _owners_commit(project, "DEC-510", which)
    _listed(project, key, owners, "DEC-510", given=owners[:12] if given == "abbreviated" else None)
    support.checkpointed(project, TICKET)
    _closes(project, sandbox, interface)


@pytest.mark.parametrize("key, status, given", [
    (support.ACCEPTED_KEY, support.DELEGATED_ACCEPTED, "full"),
    (support.ACCEPTED_KEY, support.PROPOSED, "full"),
    (support.EXEMPTIONS_KEY, support.DELEGATED_ACCEPTED, "full"),
    (support.EXEMPTIONS_KEY, support.PROPOSED, "full"),
    (support.EXEMPTIONS_KEY, support.OWNER_ACCEPTED, "abbreviated"),
], ids=["accepted_history-delegated", "accepted_history-proposed", "acceptance_exemptions-delegated",
        "acceptance_exemptions-proposed", "acceptance_exemptions-abbreviated-id"])
def test_a_list_entry_outside_the_lists_reading_measures_nothing(key, status, given, project, sandbox, interface):
    """The lists' own limits: an entry whose decision is not an ACCEPTED owner decision, or (W1-01's reading) an
    ``acceptance_exemptions`` entry that names the commit by an abbreviated id, measures nothing. The trailer gate
    refuses an ``accepted_history`` entry outside DEC-734's form itself (``ACCEPTED_HISTORY_REFUSED``), and the
    rule fixes no order between the two gates: either cause is the refusal, naming the commit."""
    _ticket(project, allowed=LISTED_ALLOWED)
    owners = _owners_commit(project, "DEC-511", "code")
    _listed(project, key, owners, "DEC-511", status=status, given=owners[:12] if given == "abbreviated" else None)
    support.checkpointed(project, TICKET)
    causes = (WORK_WITHOUT_TASK, HISTORY_REFUSED) if key == support.ACCEPTED_KEY else (WORK_WITHOUT_TASK,)
    _refused_as_unmeasured(project, sandbox, interface, owners, causes=causes)
