"""Every commit since the ticket's first is somebody's (DEC-487, third behaviour; made exact by DEC-490).

"A commit after the ticket's first commit that names no task at all refuses the close (its work was measured
by no ticket); a commit of the ticket without a role refuses like one without ``Implements:``; a root commit
and a merge commit are judged with the paths they bring."

**Which commits that name no task refuse (DEC-490).** "Among the commits after the ticket's first, one that
names no task refuses the close when it changes the ticket's acceptance tests, a path inside the ticket's
allowed paths, or the ticket's own file: that is work on this ticket which no ticket measured. One that changes
a governance file has the governance checks run, as a ticket commit would. After the probed commit, one that
changes a path inside the ticket's allowed paths makes the probe stale. Any other task-less commit (a decision
record, a checkpoint, a probe record, another folder) refuses nothing. A commit that names another ticket is
that ticket's."

So what refuses is what the commit changes, not who made it or which role it carries. Each case's commit
changes one kind of path and nothing else:

- the ticket's acceptance test (weakened so that it passes): with no trailer, with the engineer's role alone,
  with the orchestrator's role alone. Refused, a finding (exit code 3) that names the commit and says "task".
- a new file inside the ticket's allowed paths; the ticket's own file (its FULL profile lowered, no probe
  record). Refused the same way.
- a governance file outside the ticket's paths: the governance checks run. Where a hard-block check is red the
  close is refused and names the check; where all are green the ticket closes and its close record names the
  commit the checks ran at.
- the source inside the ticket's allowed paths, after the probed commit: refused, the commit named (as work no
  ticket measured, and as a probe made stale; the case holds neither word alone).
- a file in a folder that is none of the ticket's (a source folder outside its allowed paths, a folder of
  notes): refuses nothing, the ticket closes.

A file "outside the ticket's paths" is by itself no reason to refuse: round 8's first two cases added one
beside the weakened test, and no longer do. A commit that names another ticket is that ticket's and refuses
nothing here.

The suite's projects all hold commits without a task after the ticket's first one: the orchestrator's
(``Role: orchestrator``: the checkpoint, the probe record, a repair ticket's file) and the owner's
(``Role: owner``: decision records). None changes one of the three kinds of path, and every case that closes
holds that they refuse nothing.

The merge: a side-branch commit without trailers, merged by a merge commit that carries the ticket's trailers.
What it brings is judged: the governance file has the checks run, the source rewrite makes the probe stale.
The first commit: a ticket commit without a parent has paths like any other.
"""

import re

import pytest

import w1_30_support as support

TICKET = "PROJ-cmts"
WBS = "W1-cmts"
OTHER, OTHER_WBS = "PROJ-othr", "W1-othr"
FEATURE = "src/example/feature.py"
INSIDE = "src/example/more.py"
OUTSIDE = "src/other/outside.py"
NOTES = "governance/project/notes.yaml"
INSTALLED = "governance/kernel/hooks/planted-hook.sh"
PASSING = "def test_fail():\n    assert True\n"
ACCEPTANCE_TEST = f"tests/acceptance/{WBS}/test_fail.py"

README_PRESENT = support.declared_check("readme-present", "test -s README.md")
LICENSE_PRESENT = support.declared_check("license-present", "test -s LICENSE", family="graph integrity")


def _refused_naming(project, sandbox, interface, *any_of, word=None):
    """Refused with exit code 3; the answer names one of ``any_of`` (and holds ``word``); nothing is closed."""
    run = support.run_close(project, sandbox, TICKET)
    text = support.error_text(support.refused(run, interface, support.EXIT_CHECK_FAILED))
    assert any(name in text for name in any_of), f"the refusal names none of {any_of}\n{run.describe()}"
    if word:
        assert re.search(word, text, re.IGNORECASE), f"the refusal does not say {word!r}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    return run


def _one_red(project, sandbox, check_id="license-present"):
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == [check_id], f"the fixture is wrong: the red hard-block checks are {red}, not [{check_id!r}]"


def _probed(project):
    """The probe record of the commit at ``HEAD``, committed by the orchestrator."""
    project.add_probe(TICKET)
    project.commit("the probe record", who=support.ORCHESTRATOR)


# --------------------------------------------------------------------------
# Commits that name no task
# --------------------------------------------------------------------------

def _changed_by(project, commit):
    """The paths ``commit`` changes."""
    out = support.git(project.root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", commit)
    return sorted(rel for rel in out.split("\n") if rel)


def _task_less(project, commit, *paths):
    """The fixture's commit names no task and changes ``paths`` only."""
    assert commit not in support.ticket_commits(project.root, TICKET)
    assert _changed_by(project, commit) == sorted(paths), \
        f"the fixture is wrong: the commit changes {_changed_by(project, commit)}"


def test_a_commit_without_trailers_that_weakens_the_acceptance_test_refuses(project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, failing=True)
    commit = support.no_trailers_commit(project, "tidy up", {ACCEPTANCE_TEST: PASSING})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, ACCEPTANCE_TEST)
    _refused_naming(project, sandbox, interface, commit[:7], word="task")


def test_a_commit_with_the_engineers_role_and_no_task_refuses(project, sandbox, interface):
    """The same change of the acceptance test, with ``Role: engineer`` alone."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    project.write(ACCEPTANCE_TEST, PASSING)
    commit = project.commit("tidy up", who=support.IMPLEMENTER, trailers=(support.ENGINEER_ROLE,), exact=True)
    support.checkpointed(project, TICKET)
    _task_less(project, commit, ACCEPTANCE_TEST)
    _refused_naming(project, sandbox, interface, commit[:7], word="task")


def test_a_commit_with_the_orchestrators_role_and_no_task_that_weakens_the_acceptance_test_refuses(
        project, sandbox, interface):
    """The same change of the acceptance test, made as the orchestrator makes its commits (``Role:
    orchestrator`` alone, as the checkpoint's commit that follows it): the role lifts nothing."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    project.write(ACCEPTANCE_TEST, PASSING)
    commit = project.commit("tidy up", who=support.ORCHESTRATOR, exact=True)
    support.checkpointed(project, TICKET)
    _task_less(project, commit, ACCEPTANCE_TEST)
    _refused_naming(project, sandbox, interface, commit[:7], word="task")


def test_a_commit_without_trailers_that_adds_a_file_inside_the_tickets_allowed_paths_refuses(
        project, sandbox, interface):
    """The ticket is green; the commit adds a source file under ``src/example/``, the ticket's allowed paths."""
    support.build_ticket(project, TICKET, WBS)
    commit = support.no_trailers_commit(project, "one more file", {INSIDE: "# inside the ticket's paths\n"})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, INSIDE)
    _refused_naming(project, sandbox, interface, commit[:7], word="task")


def test_a_commit_without_trailers_that_changes_the_tickets_own_file_refuses(project, sandbox, interface):
    """The ticket is FULL and has no probe record; the commit lowers the profile in the ticket's file."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    rel = support.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    assert text.count("profile: FULL\n") == 1, "the fixture is wrong: the ticket file has no FULL profile line"
    commit = support.no_trailers_commit(project, "the profile", {rel: text.replace("profile: FULL\n", "profile: STANDARD\n")})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, rel)
    _refused_naming(project, sandbox, interface, commit[:7], word="task")


def test_a_commit_without_trailers_that_changes_a_governance_file_refuses_where_a_check_is_red(
        project_with_checks, sandbox, interface):
    """A hard-block check is red; no commit of the ticket changed a governance file, the other commit did.
    The governance checks run as for a ticket commit: the refusal names the red check."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    support.build_ticket(project, TICKET, WBS)
    commit = support.no_trailers_commit(project, "a note", {NOTES: "note: one\n"})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, NOTES)
    _one_red(project, sandbox)
    _refused_naming(project, sandbox, interface, "license-present")


def test_a_commit_without_trailers_that_changes_a_governance_file_has_the_checks_run(
        project_with_checks, sandbox, interface):
    """Every check is green: the commit refuses nothing, and the close record names the commit being closed as
    the commit the checks ran at, as it does after a ticket commit under a governance prefix."""
    project = project_with_checks(README_PRESENT)
    support.build_ticket(project, TICKET, WBS)
    commit = support.no_trailers_commit(project, "a note", {NOTES: "note: one\n"})
    head = support.checkpointed(project, TICKET)
    _task_less(project, commit, NOTES)
    assert support.red_hard_blocks(support.checks_at_head(project, sandbox)) == [], "the fixture is wrong: a check is red"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    front = support.the_close_record(project, TICKET)
    assert front.get(support.CHECK_COMMIT_KEY) == head, \
        f"the governance file of a commit without a task did not have the checks run at the commit being " \
        f"closed: {support.CHECK_COMMIT_KEY} is {front.get(support.CHECK_COMMIT_KEY)!r}"


def test_a_commit_without_trailers_that_rewrites_the_source_after_the_probed_commit_refuses(
        project, sandbox, interface):
    """The source is inside the ticket's allowed paths: work no ticket measured, and the probe is stale."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    _probed(project)
    commit = support.no_trailers_commit(project, "rewrite", {FEATURE: "# rewritten after the probe\n"})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, FEATURE)
    _refused_naming(project, sandbox, interface, commit[:7])


@pytest.mark.parametrize("rel", [OUTSIDE, "notes/meeting.txt"],
                         ids=["a source folder outside the ticket's paths", "a folder of notes"])
def test_a_commit_without_trailers_that_changes_only_a_folder_that_is_none_of_the_tickets_refuses_nothing(
        rel, project, sandbox, interface):
    """The converse: the folder holds none of the ticket's acceptance tests, is not inside its allowed paths,
    holds neither its file nor a governance file."""
    support.build_ticket(project, TICKET, WBS)
    commit = support.no_trailers_commit(project, "elsewhere", {rel: "# none of the ticket's\n"})
    support.checkpointed(project, TICKET)
    _task_less(project, commit, rel)
    assert not rel.startswith(support.GOVERNANCE_PREFIXES + (support.ACCEPTANCE_PREFIX, support.TICKETS_PREFIX,
                                                             "src/example/"))

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    front = support.the_close_record(project, TICKET)
    claimed = {key: front[key] for key in (support.CHECK_COMMIT_KEY, support.CHECK_RESULT_KEY) if front.get(key)}
    assert not claimed, f"the close record claims a check result although no governance file changed: {claimed}"


def test_a_commit_that_names_another_ticket_refuses_nothing(project, sandbox, interface):
    """The converse: between this ticket's commits lies the work of another ticket, inside that ticket's paths
    and with its trailers."""
    support.build_ticket(project, TICKET, WBS)
    project.add_ticket(OTHER, OTHER_WBS, allowed_paths=["src/other/**"])
    project.add_passing_test(OTHER_WBS)
    project.write(OUTSIDE, "# the other ticket's work\n")
    theirs = project.commit("the other ticket's work", who=support.IMPLEMENTER, trailers=support.trailers_of(OTHER))
    support.engineer_commit(project, TICKET, {FEATURE: "# feature, second commit\n"})
    support.checkpointed(project, TICKET)
    assert theirs not in support.ticket_commits(project.root, TICKET)
    assert support.judged_by_w1_50(project, sandbox, [theirs]) == [], \
        "the fixture is wrong: the other ticket's commit is outside its own paths"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
    assert support.ticket_status(project.root, OTHER) == "in_progress"


# --------------------------------------------------------------------------
# A commit of the ticket without a role
# --------------------------------------------------------------------------

def test_a_commit_of_the_ticket_without_a_role_refuses(project, sandbox, interface):
    """``Task`` and ``Implements`` are present, ``Role`` is not: the commit widens the ticket's own allowed
    paths in the ticket file and adds a file under the installed kernel."""
    support.build_ticket(project, TICKET, WBS)
    rel = support.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    assert "- src/example/**\n" in text, "the fixture is wrong: the ticket file does not list its paths as expected"
    project.write(rel, text.replace("- src/example/**\n", "- src/example/**\n- governance/kernel/**\n"))
    project.write(INSTALLED, "#!/bin/sh\nexit 0\n")
    commit = project.commit("more room", who=support.IMPLEMENTER,
                            trailers=(f"Task: {TICKET}", "Implements: CAP-01"), exact=True)
    support.checkpointed(project, TICKET)
    assert commit in support.ticket_commits(project.root, TICKET)
    _refused_naming(project, sandbox, interface, commit[:7], word="role")


# --------------------------------------------------------------------------
# Merges and the first commit
# --------------------------------------------------------------------------

def _merged_side_commit(project, files):
    """A side-branch commit without trailers that writes ``files``, merged into ``main`` by a merge commit
    with the ticket's trailers. Returns ``(side commit, merge commit)``."""
    support.git(project.root, "checkout", "-q", "-b", "side")
    side = support.no_trailers_commit(project, "work on the side", files)
    support.git(project.root, "checkout", "-q", "main")
    message = "merge the side branch\n\n" + "\n".join(support.trailers_of(TICKET)) + "\n"
    support.git(project.root, "merge", "-q", "--no-ff", "--no-gpg-sign", "-m", message, "side",
                who=support.IMPLEMENTER)
    merge = support.head_of(project)
    parents = support.git(project.root, "rev-list", "--parents", "-n", "1", merge).split()
    assert len(parents) == 3 and side in parents, "the fixture is wrong: HEAD is not a merge of the side commit"
    assert merge in support.ticket_commits(project.root, TICKET), \
        "the fixture is wrong: the merge commit does not carry the ticket's trailers"
    return side, merge


def test_a_merge_with_the_tickets_trailers_that_brings_a_governance_file_refuses_where_a_check_is_red(
        project_with_checks, sandbox, interface):
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    support.build_ticket(project, TICKET, WBS)
    side, merge = _merged_side_commit(project, {NOTES: "note: one\n"})
    support.checkpointed(project, TICKET)
    _one_red(project, sandbox)
    _refused_naming(project, sandbox, interface, "license-present", side[:7], merge[:7])


def test_a_merge_with_the_tickets_trailers_that_brings_a_source_rewrite_after_the_probed_commit_refuses(
        project, sandbox, interface):
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    _probed(project)
    side, merge = _merged_side_commit(project, {FEATURE: "# rewritten on the side, after the probe\n"})
    support.checkpointed(project, TICKET)
    _refused_naming(project, sandbox, interface, side[:7], merge[:7])


class _ProjectBornWithItsTicket(support.Project):
    """A project whose first commit is a commit of the ticket: it carries the ticket's trailers and the
    orchestrator's role, so W1-50's judgement passes every path in it but an acceptance test, and it holds
    none. The project's own check declarations and a file under ``governance/project/`` are among its paths."""

    def _init_minimal(self):
        support.git(self.root, "init", "-q", "-b", "main")
        self.write("README.md", "# A project\n")
        self.write(".gitignore", ".gov-runtime/\n")
        self.write("pyproject.toml", (support.REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))
        support.shutil.copytree(support.REPO_ROOT / "src", self.root / "src")
        self._copy_kernel_templates()
        self.write(f"docs/adr/{support.BASE_SOURCE}.md",
                   support.decision(support.BASE_SOURCE, "ACTIVE", title="The base decision"))
        self.write(support.ticket_path(TICKET), support.ticket_text(TICKET, WBS))
        self.write(FEATURE, "# feature\n")
        self.write(NOTES, "note: one\n")
        self.first = self._commit("the project and the ticket's work", support.ORCHESTRATOR,
                                  support.trailers_of(TICKET, role="orchestrator"))
        self.write(f"tests/acceptance/{WBS}/README.md", f"# {WBS}\n")
        self.add_passing_test(WBS)
        self._commit("acceptance tests", support.TEST_DESIGNER,
                     support.trailers_of(TICKET, role="independent-test-designer"))


def test_the_paths_of_a_ticket_commit_that_is_the_first_commit_are_judged(built, tmp_path, sandbox, interface):
    """The first commit brings governance files and a hard-block check is red: the checks run."""
    project = _ProjectBornWithItsTicket(tmp_path / "project", checks=[README_PRESENT, LICENSE_PRESENT])
    support.checkpointed(project, TICKET)
    assert support.git(project.root, "rev-list", "--max-parents=0", "HEAD").split() == [project.first]
    commits = support.ticket_commits(project.root, TICKET)
    assert project.first in commits
    assert support.judged_by_w1_50(project, sandbox, commits) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the governance checks are not the only reason"
    _one_red(project, sandbox)
    _refused_naming(project, sandbox, interface, "license-present")
