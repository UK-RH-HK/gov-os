"""Round 14: which commits after the probed one make the probe gate refuse (DEC-581).

DEC-581: "The probe gate refuses only for commits after the probed one that change files inside the ticket's
``allowed_paths`` or its acceptance tests."

Until this round a commit of the ticket after the probed commit refused for every path outside ``tests/`` and
``docs/probes/``. The rule turns that around in both directions:

- **Looser.** A commit of the ticket after the probed one that changes only files outside the ticket's allowed
  paths and outside its acceptance tests refuses nothing: the orchestrator's residual notes, the probe record
  itself, a register entry, a checkpoint record, each in a commit that names the ticket.
- **Stricter.** "Its acceptance tests" are the folder the close runs for the ticket,
  ``tests/acceptance/<the ticket's wbs id>/`` (README, settlement 7). A commit of the ticket after the probed
  one that changes a file there refuses; until this round ``tests/`` at large never refused.

A commit that changes one file inside and one outside refuses, and the finding names the inside file.

**Settled here, the stricter reading (README, round 14, settlements 33 to 35):**

- the ticket's own ticket file counts with the ticket's work, as DEC-490 counts it for a commit that names no
  task: a commit of the ticket after the probed one that changes it refuses, as today;
- a merge commit of the ticket after the probed one is judged by what it changes itself: one that is not the
  merge of the probed commit by every path it brings to its first parent, the merge of the probed commit
  (DEC-505) by every path that is at the merge not what it is at the probed commit. An acceptance test changed
  in a merge commit itself is W1-50's finding already, whoever made the merge; no case of this file adds one;
- whose commits are judged is unchanged: the ticket's own, and those that name no task (DEC-490).

The projects: a FULL ticket whose engineer's commit is probed; the later commits follow; the orchestrator's
probe record (in a commit that names no ticket, unless the case says otherwise) and its checkpoint come last.
Each later commit is made by a role W1-50's judgement passes for its paths, and each case holds that first, so
that the probe gate is the only gate with something to say.

The probe gate's finding is read where the close states it today: the refusal itself when it is the only
finding (``error.code`` is ``PROBE_INVALID``), else the one of ``error.details.parts`` with that code.
"""

import json

import pytest

import w1_30_support as support

TICKET = "PROJ-prlc"
WBS = "W1-prlc"
OTHER_WBS = "W1-prlo"
PROBE_INVALID = "PROBE_INVALID"
FEATURE = "src/example/feature.py"
ACCEPTANCE = f"tests/acceptance/{WBS}/"
ACCEPTANCE_TEST = f"{ACCEPTANCE}test_pass.py"
TICKET_FILE = support.ticket_path(TICKET)
# Files of the orchestrator's outside the ticket's allowed paths and outside its acceptance tests; none is a
# governance file, so the governance checks of a close are not run for them.
NOTES = "docs/residuals.md"
REGISTER_KEY = "decision_register"
REGISTER = "records/decision-log.md"
PROBE_RECORD = f"docs/probes/{TICKET}/PR-{TICKET}.md"
CHECKPOINTS = f"docs/checkpoints/{TICKET}/"
BRANCH = "work"

ENGINEER = support.trailers_of(TICKET)
ORCHESTRATOR = support.trailers_of(TICKET, role="orchestrator")
DESIGNER = support.trailers_of(TICKET, role="independent-test-designer")


# --------------------------------------------------------------------------
# The projects
# --------------------------------------------------------------------------

@pytest.fixture()
def project(built, tmp_path):
    """A project whose path map names a register file (DEC-473, DEC-479), with one entry of the owner's from
    before the ticket's first commit."""
    project = support.Project(tmp_path / "project", settings={**support.SUITE_SETTINGS, REGISTER_KEY: REGISTER})
    project.write(REGISTER, "# Decisions\n\n" + _entry("DEC-100"))
    project.commit("the register", who=support.OWNER)
    return project


def _entry(decision):
    return f"### {decision} — A decision\n- **Status:** ACCEPTED (orchestrator, delegated)\n- **Decision:** A fixture.\n\n"


def _probed_work(project):
    """The ticket's work by the roles that may do it; returns the engineer's commit, the one that is probed."""
    project.add_ticket(TICKET, WBS, profile="FULL")
    project.add_passing_test(WBS)
    project.write(FEATURE, "# feature\n")
    return project.commit("implement", who=support.IMPLEMENTER, trailers=ENGINEER)


def _recorded_and_checkpointed(project, probed, record_names_the_ticket=False):
    """The orchestrator's probe record of ``probed`` and its checkpoint, committed after everything else.
    Returns the commit of the record."""
    project.add_probe(TICKET, probed_commit=probed)
    record = project.commit("the probe record", who=support.ORCHESTRATOR,
                            trailers=ORCHESTRATOR if record_names_the_ticket else None, exact=True)
    support.checkpointed(project, TICKET)
    return record


def _changed_by(project, commit):
    """The paths ``commit`` changes against its first parent."""
    out = support.git(project.root, "diff", "--name-only", f"{commit}^", commit)
    return sorted(rel for rel in out.split("\n") if rel)


def _inside_the_tickets_work(rel):
    """Inside the ticket's allowed paths (``src/example/**``) or in its acceptance folder."""
    return rel.startswith(("src/example/", ACCEPTANCE))


def _of_the_ticket(project, sandbox, probed, *commits):
    """The fixture's later commits name the ticket, follow the probed commit, and W1-50's judgement of the
    ticket's commits has no finding: no other gate of the close has a reason of its own."""
    ticket_commits = support.ticket_commits(project.root, TICKET)
    after = support.git(project.root, "rev-list", f"{probed}..HEAD").split()
    for commit in commits:
        assert commit in ticket_commits, f"the fixture is wrong: {commit[:7]} does not name the ticket"
        assert commit in after, f"the fixture is wrong: {commit[:7]} does not follow the probed commit"
    assert support.judged_by_w1_50(project, sandbox, ticket_commits) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the probe gate is not the only reason"


def _closes(project, sandbox, interface):
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    return support.the_close_record(project, TICKET)


def _the_probe_gates_finding(project, sandbox, interface):
    """The close is refused with a finding (exit code 3), nothing is closed, and one of its findings is the
    probe gate's. Returns ``(finding, run)``: the finding as one object with its ``message`` and its details."""
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    support.assert_not_closed(project, TICKET)
    details = error.get("details") or {}
    if error.get("code") == PROBE_INVALID:
        return {"message": error.get("message", ""), "commit": details.get("commit"), "path": details.get("path")}, run
    parts = [part for part in details.get("parts") or [] if part.get("code") == PROBE_INVALID]
    assert len(parts) == 1, f"the refusal holds {len(parts)} findings of the probe gate, not one\n{run.describe()}"
    return parts[0], run


def _refused_for(project, sandbox, interface, commit, inside, outside=()):
    """Refused by the probe gate; its finding names ``commit`` and the path ``inside``, and none of ``outside``."""
    finding, run = _the_probe_gates_finding(project, sandbox, interface)
    text = json.dumps(finding, ensure_ascii=False)
    assert commit[:7] in text, f"the probe gate's finding does not name the commit {commit[:7]}\n{run.describe()}"
    assert inside in text, f"the probe gate's finding does not name {inside}\n{run.describe()}"
    for rel in outside:
        assert rel not in text, \
            f"the probe gate's finding names {rel}, a file outside the ticket's work, as what refuses\n{run.describe()}"


def _orchestrators_commit(project, message, files):
    """One commit with the orchestrator's role that names the ticket and writes ``files``; returns its id."""
    for rel, text in files.items():
        project.write(rel, text)
    return project.commit(message, who=support.ORCHESTRATOR, trailers=ORCHESTRATOR, exact=True)


def _notes(project):
    return _orchestrators_commit(project, "residual notes", {NOTES: "# Residuals of the ticket\n"})


def _register_entry(project):
    text = (project.root / REGISTER).read_text(encoding="utf-8")
    return _orchestrators_commit(project, "a delegated decision", {REGISTER: text + _entry("DEC-101")})


def _checkpoint_record(project):
    project.add_checkpoint(TICKET)
    return project.commit("a checkpoint", who=support.ORCHESTRATOR, trailers=ORCHESTRATOR, exact=True)


# --------------------------------------------------------------------------
# 1. Outside both: does not refuse
# --------------------------------------------------------------------------

@pytest.mark.parametrize("later, changes", [(_notes, NOTES), (_register_entry, REGISTER),
                                            (_checkpoint_record, CHECKPOINTS)],
                         ids=["the orchestrator's notes", "a register entry", "a checkpoint record"])
def test_a_commit_of_the_ticket_after_the_probed_one_outside_its_work_does_not_refuse(
        later, changes, project, sandbox, interface):
    """The commit names the ticket and changes one file, outside the ticket's allowed paths and outside its
    acceptance tests."""
    probed = _probed_work(project)
    commit = later(project)
    _recorded_and_checkpointed(project, probed)
    paths = _changed_by(project, commit)
    assert len(paths) == 1 and paths[0].startswith(changes) and not _inside_the_tickets_work(paths[0]), \
        f"the fixture is wrong: the commit changes {paths}"
    _of_the_ticket(project, sandbox, probed, commit)

    record = _closes(project, sandbox, interface)

    assert commit in [entry["commit"] for entry in record["commits"]], \
        "the close record does not list the later commit among the ticket's commits"


def test_the_probe_record_in_a_commit_that_names_the_ticket_does_not_refuse(project, sandbox, interface):
    """The record is committed by the orchestrator's role alone, as the gate asks, in a commit that carries
    the ticket's ``Task`` and ``Implements`` too."""
    probed = _probed_work(project)
    record = _recorded_and_checkpointed(project, probed, record_names_the_ticket=True)
    assert _changed_by(project, record) == [PROBE_RECORD]
    _of_the_ticket(project, sandbox, probed, record)

    _closes(project, sandbox, interface)


def test_several_commits_of_the_ticket_after_the_probed_one_outside_its_work_do_not_refuse(
        project, sandbox, interface):
    """What the orchestrator leaves after a probe: notes, a decision, a checkpoint, the record, one after the
    other and each in a commit that names the ticket."""
    probed = _probed_work(project)
    commits = [_notes(project), _register_entry(project), _checkpoint_record(project)]
    commits.append(_recorded_and_checkpointed(project, probed, record_names_the_ticket=True))
    for commit in commits:
        assert not any(_inside_the_tickets_work(rel) for rel in _changed_by(project, commit))
    _of_the_ticket(project, sandbox, probed, *commits)

    record = _closes(project, sandbox, interface)

    listed = [entry["commit"] for entry in record["commits"]]
    assert all(commit in listed for commit in commits), \
        "the close record does not list every later commit among the ticket's commits"


# --------------------------------------------------------------------------
# 2. Inside the allowed paths: refuses
# --------------------------------------------------------------------------

def test_a_commit_of_the_ticket_after_the_probed_one_inside_its_allowed_paths_refuses(project, sandbox, interface):
    probed = _probed_work(project)
    commit = support.engineer_commit(project, TICKET, {FEATURE: "# rewritten after the probe\n"})
    _recorded_and_checkpointed(project, probed)
    assert _changed_by(project, commit) == [FEATURE]
    _of_the_ticket(project, sandbox, probed, commit)
    _refused_for(project, sandbox, interface, commit, FEATURE)


# --------------------------------------------------------------------------
# 3. The ticket's acceptance tests: refuses
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rel, text", [(f"{ACCEPTANCE}test_more.py", "def test_more():\n    assert True\n"),
                                       (ACCEPTANCE_TEST, "def test_pass():\n    pass\n")],
                         ids=["a case added", "a case changed"])
def test_a_commit_of_the_ticket_after_the_probed_one_in_its_acceptance_tests_refuses(
        rel, text, project, sandbox, interface):
    """The test designer's commit, with the ticket's trailers, in the folder the close runs for the ticket: the
    reviewer probed the code against other tests than the close runs."""
    probed = _probed_work(project)
    project.write(rel, text)
    commit = project.commit("the acceptance tests, again", who=support.TEST_DESIGNER, trailers=DESIGNER, exact=True)
    _recorded_and_checkpointed(project, probed)
    assert _changed_by(project, commit) == [rel]
    _of_the_ticket(project, sandbox, probed, commit)
    _refused_for(project, sandbox, interface, commit, rel)


# --------------------------------------------------------------------------
# 4. One inside and one outside: refuses, for the inside file
# --------------------------------------------------------------------------

def test_a_commit_that_changes_one_file_inside_and_one_outside_refuses_for_the_inside_file(
        project, sandbox, interface):
    """One commit of the orchestrator's with the ticket's trailers: its notes and the ticket's source. The
    notes come first in the order of the paths; they are not what refuses."""
    probed = _probed_work(project)
    commit = _orchestrators_commit(project, "notes, and a fix on the way",
                                   {NOTES: "# Residuals of the ticket\n", FEATURE: "# rewritten after the probe\n"})
    _recorded_and_checkpointed(project, probed)
    assert _changed_by(project, commit) == [NOTES, FEATURE]
    _of_the_ticket(project, sandbox, probed, commit)
    _refused_for(project, sandbox, interface, commit, FEATURE, outside=[NOTES])


# --------------------------------------------------------------------------
# 5. Under tests/, and neither inside the allowed paths nor in the ticket's acceptance folder
# --------------------------------------------------------------------------

def test_a_commit_of_the_ticket_in_another_acceptance_folder_does_not_refuse(project, sandbox, interface):
    """The test designer's commit, with this ticket's trailers, adds a case to the acceptance folder of another
    work package. By the rule's words the probe gate has no finding; W1-50's judgement has none either (an
    acceptance test is the test designer's), so the ticket closes, as today. README, round 14, package P-2."""
    probed = _probed_work(project)
    rel = f"tests/acceptance/{OTHER_WBS}/test_theirs.py"
    project.write(rel, "def test_theirs():\n    assert True\n")
    commit = project.commit("a case elsewhere", who=support.TEST_DESIGNER, trailers=DESIGNER, exact=True)
    _recorded_and_checkpointed(project, probed)
    assert _changed_by(project, commit) == [rel] and not _inside_the_tickets_work(rel)
    _of_the_ticket(project, sandbox, probed, commit)

    _closes(project, sandbox, interface)


# --------------------------------------------------------------------------
# Settled: the ticket's own file
# --------------------------------------------------------------------------

def test_a_commit_of_the_ticket_after_the_probed_one_that_changes_its_ticket_file_refuses(
        project, sandbox, interface):
    """Settlement 33, the stricter reading (package P-1): the ticket file says what the ticket's paths and its
    profile are; a commit of the ticket that changes it after the probe refuses, as today."""
    probed = _probed_work(project)
    text = (project.root / TICKET_FILE).read_text(encoding="utf-8")
    commit = _orchestrators_commit(project, "a note in the ticket", {TICKET_FILE: text + "\nA note.\n"})
    _recorded_and_checkpointed(project, probed)
    assert _changed_by(project, commit) == [TICKET_FILE]
    _of_the_ticket(project, sandbox, probed, commit)
    _refused_for(project, sandbox, interface, commit, TICKET_FILE)


# --------------------------------------------------------------------------
# Settled: a merge commit after the probed one is judged by what it changes itself
# --------------------------------------------------------------------------

def _merge(project, head, edit=None):
    """The orchestrator merges ``head`` into ``main`` with a merge commit that carries the ticket's trailers.
    ``edit`` (``{path: text}``) is written into the merge itself. Returns the merge commit."""
    support.git(project.root, "checkout", "-q", "main")
    message = "merge\n\n" + "\n".join(ORCHESTRATOR) + "\n"
    support.git(project.root, "merge", "-q", "--no-ff", "--no-commit", head, who=support.ORCHESTRATOR)
    for rel, text in (edit or {}).items():
        project.write(rel, text)
    support.git(project.root, "add", "-A", who=support.ORCHESTRATOR)
    support.git(project.root, "commit", "-q", "--no-gpg-sign", "-m", message, who=support.ORCHESTRATOR)
    merge = support.head_of(project)
    assert len(support.git(project.root, "rev-list", "--parents", "-n", "1", merge).split()) == 3, \
        "the fixture is wrong: HEAD is not a merge commit"
    return merge


def _parents(project, commit):
    return support.git(project.root, "rev-list", "--parents", "-n", "1", commit).split()[1:]


def test_a_merge_after_the_probed_commit_that_brings_only_files_outside_the_tickets_work_does_not_refuse(
        project, sandbox, interface):
    """The ticket is probed on ``main``. The orchestrator's notes are written on a branch, in a commit that
    names the ticket, and merged with a merge commit that names it too. The merge is not the merge of the
    probed commit; what it brings is the notes."""
    probed = _probed_work(project)
    support.git(project.root, "checkout", "-q", "-b", BRANCH)
    notes = _notes(project)
    merge = _merge(project, BRANCH)
    _recorded_and_checkpointed(project, probed)
    assert _parents(project, merge) == [probed, notes], "the fixture is wrong: the merge is another one"
    assert _changed_by(project, merge) == [NOTES]
    _of_the_ticket(project, sandbox, probed, notes, merge)

    _closes(project, sandbox, interface)


def _work_on_a_branch(project):
    """The ticket's work on its branch, ``main`` staying where it was; returns the head of the branch."""
    support.git(project.root, "checkout", "-q", "-b", BRANCH)
    return _probed_work(project)


def test_the_merge_of_the_probed_commit_with_a_file_outside_the_tickets_work_added_in_it_does_not_refuse(
        project, sandbox, interface):
    """DEC-505's merge: the head merged is the probed commit. The orchestrator writes its notes into the merge
    itself. On the ticket's allowed paths and in its acceptance folder the merge is the probed commit."""
    probed = _work_on_a_branch(project)
    merge = _merge(project, BRANCH, edit={NOTES: "# Residuals of the ticket\n"})
    _recorded_and_checkpointed(project, probed)
    assert _parents(project, merge)[1] == probed
    assert support.git(project.root, "diff", "--name-only", probed, merge).split() == [NOTES]
    _of_the_ticket(project, sandbox, probed, merge)

    _closes(project, sandbox, interface)
