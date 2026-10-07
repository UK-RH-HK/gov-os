"""The probe gate reads the repository (KPI S7; DEC-137: "the reviewer wrote nothing to the repository").

A commit of the ticket that carries the reviewer's role refuses the close wherever it lies and whatever else it
says: before the probed commit as well as after it, and with no ``Session`` trailer as well as with one.

The reviewer's commit in these cases is empty: it changes no path, so W1-50's judgement of the ticket's commits
has no finding (each case holds that first) and the only thing wrong with the ticket is that the reviewer made a
commit of it. The same project without that commit closes (``test_full_ticket_closes_with_valid_probe``).

A git failure while the probe's commits are read is a refusal, never "no such commits": in the last case ``git``
fails for every call that names the probed commit, in a project that otherwise closes.

The exit code of a refusal by the probe gate is not a subject here: no source read for this suite gives it
(README, packages).
"""

import os
import re
import shutil

import w1_30_support as support

TICKET = "PROJ-prbc"
WBS = "W1-prbc"
REVIEWER_ROLE = "independent-auditor"
REVIEWER_SESSION = "reviewer-001"
NAMES_THE_REVIEWER = re.compile(r"reviewer|" + REVIEWER_ROLE, re.IGNORECASE)


def _reviewer_commit(project, *more_trailers):
    """An empty commit of the ticket with the reviewer's role; its trailers are otherwise those of a commit
    of the ticket (KPI S1: ``Implements`` and ``Task``)."""
    return project.commit("the reviewer's commit", who=support.REVIEWER,
                          trailers=support.trailers_of(TICKET, role=REVIEWER_ROLE) + more_trailers, exact=True)


def _probe(project):
    """The probe record of the commit at HEAD, then a fresh checkpoint; returns the probed commit."""
    probed = support.git(project.root, "rev-parse", "HEAD").strip()
    project.add_probe(TICKET, probed_commit=probed, reviewer_session=REVIEWER_SESSION)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    return probed


def _fresh_checkpoint(project):
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)


def _refused_for_the_reviewers_commit(project, sandbox, interface, commit):
    assert support.judged_by_w1_50(project, sandbox, support.ticket_commits(project.root, TICKET)) == [], \
        "the fixture is wrong: W1-50's judgement has a finding, so the probe gate is not the only reason"
    run = support.run_close(project, sandbox, TICKET)
    envelope = support.envelope_of(run, interface)
    assert envelope["ok"] is False, f"gov close was not refused\n{run.describe()}"
    text = support.error_text(envelope["error"])
    assert NAMES_THE_REVIEWER.search(text), \
        f"the refusal does not say a commit of the ticket carries the reviewer's role\n{run.describe()}"
    assert commit[:7] in text, f"the refusal does not name the commit {commit[:7]}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)


def test_a_reviewer_commit_before_the_probed_commit_refuses(project, sandbox, interface):
    """The reviewer's commit, naming its session, lies before the probed commit."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    commit = _reviewer_commit(project, f"Session: {REVIEWER_SESSION}")
    _fresh_checkpoint(project)
    _probe(project)
    _refused_for_the_reviewers_commit(project, sandbox, interface, commit)


def test_a_reviewer_commit_before_the_probed_commit_that_names_no_session_refuses(project, sandbox, interface):
    """The same commit with no ``Session`` trailer: the role alone refuses."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    commit = _reviewer_commit(project)
    _fresh_checkpoint(project)
    _probe(project)
    _refused_for_the_reviewers_commit(project, sandbox, interface, commit)


def test_a_reviewer_commit_after_the_probed_commit_that_names_no_session_refuses(project, sandbox, interface):
    """The reviewer's commit, with no ``Session`` trailer, follows the probed commit."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    _probe(project)
    commit = _reviewer_commit(project)
    _fresh_checkpoint(project)
    _refused_for_the_reviewers_commit(project, sandbox, interface, commit)


def test_a_git_failure_while_the_probes_commits_are_read_refuses(project, sandbox, interface, monkeypatch,
                                                                 tmp_path):
    """The project closes as it is. A ``git`` first on ``PATH`` fails, as git does (exit code 128), for every
    call that names the probed commit, which is not a commit of the ticket; every other call goes to git."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    probed = _probe(project)
    _fresh_checkpoint(project)
    assert probed not in support.ticket_commits(project.root, TICKET)

    calls = tmp_path / "failed-git-calls"
    folder = tmp_path / "failing-git"
    folder.mkdir()
    wrapper = folder / "git"
    wrapper.write_text(
        "#!/bin/sh\n"
        'for argument in "$@"; do\n'
        '  case "$argument" in\n'
        f'    *{probed[:7]}*) echo "$@" >> "{calls}"; echo "fatal: planted git failure" >&2; exit 128 ;;\n'
        "  esac\n"
        "done\n"
        f'exec "{shutil.which("git")}" "$@"\n', encoding="utf-8")
    wrapper.chmod(0o755)
    support.load_store(project, sandbox)
    monkeypatch.setenv("PATH", str(folder) + os.pathsep + os.environ["PATH"])

    run = support.run_close(project, sandbox, TICKET, store=False)
    monkeypatch.undo()
    assert calls.is_file(), \
        f"this case measured nothing: gov close gave git no call that names the probed commit\n{run.describe()}"
    support.refused(run, interface, support.EXIT_GOV_ERROR)
    support.assert_not_closed(project, TICKET)
