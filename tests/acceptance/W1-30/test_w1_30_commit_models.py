"""The models of the ticket's commits in the close record (DEC-460 "Each session's model is recorded in close
records", as DEC-470 settles it until launch records carry the model).

The close record lists, for each of the ticket's commits, its role and the model named in its
``Co-Authored-By`` trailer, exactly as read. A commit without such a line is listed with "not measured". No
model is guessed and no commit is left out.

What the cases read in the close record's frontmatter: one list whose entries each hold ``commit`` (the
commit's id, whole or shortened to seven characters or more), ``role`` (the value of the commit's ``Role``
trailer) and ``model``. The name of the list is the implementation's; the three keys are settled here (README,
settlement 11).

"Exactly as read": the name written in the line, with nothing changed, added or mapped to a model id. The line
``Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>`` gives ``Claude Opus 4.6 (1M context)``;
the whole value of the line, address included, is accepted as well.

The ticket's commits are those whose trailers hold ``Task: <ticket>``: here the test designer's commit of the
acceptance test and the engineer's commit of the source file. Each case holds first that W1-50's judgement of
them has no finding, so the co-author lines are the only thing the case is about.
"""

import w1_30_support as support

TICKET = "PROJ-mdls"
WBS = "W1-mdls"
NOT_MEASURED = "not measured"
DESIGNER = "independent-test-designer"
ENGINEER = "engineer"
ADDRESS = "<noreply@anthropic.com>"
DESIGNER_MODEL = "Claude Opus 4.6 (1M context)"
ENGINEER_MODEL = "Claude Opus 5.5"


def _line(model):
    return f"Co-Authored-By: {model} {ADDRESS}"


def _ticket_of_two_roles(project, sandbox, designer_model, engineer_model):
    """The ticket's work by the roles that may do it; a commit whose model is None carries no co-author line.
    Returns ``{role: commit}`` of the ticket's two commits."""
    project.add_ticket(TICKET, WBS)
    project._commit("ticket files", support.ORCHESTRATOR, support.ORCHESTRATOR["trailers"],
                    [support.TICKETS_PREFIX])
    commits = {}
    for role, who, model, write in (
            (DESIGNER, support.TEST_DESIGNER, designer_model, lambda: project.add_passing_test(WBS)),
            (ENGINEER, support.IMPLEMENTER, engineer_model,
             lambda: project.write("src/example/feature.py", "# feature\n"))):
        write()
        trailers = support.trailers_of(TICKET, role=role) + ((_line(model),) if model else ())
        commits[role] = project._commit(f"the work of the {role}", who, trailers)
    project.add_checkpoint(TICKET)
    project.commit("checkpoint", who=support.ORCHESTRATOR)

    assert support.ticket_commits(project.root, TICKET) == [commits[DESIGNER], commits[ENGINEER]], \
        "the fixture is wrong: the ticket's commits are not the designer's and the engineer's"
    for role, model in ((DESIGNER, designer_model), (ENGINEER, engineer_model)):
        read = support.git(project.root, "log", "-1", "--format=%(trailers:key=Co-Authored-By,valueonly)",
                           commits[role]).strip()
        assert read == (f"{model} {ADDRESS}" if model else ""), f"the fixture is wrong: git reads {read!r}"
    assert support.judged_by_w1_50(project, sandbox, list(commits.values())) == [], \
        "the fixture is wrong: W1-50's judgement of the ticket's commits has a finding"
    return commits


def _listed(project, sandbox, interface):
    """Close the ticket; the close record's list of commits with their roles and models."""
    run = support.run_close(project, sandbox, TICKET)
    support.result_of(run, interface)
    records = support.close_records(project.root, TICKET)
    assert len(records) == 1, f"one close record is expected, found {[rel for rel, _ in records]}"
    rel, front = records[0]
    lists = [value for value in front.values()
             if isinstance(value, list) and value
             and all(isinstance(entry, dict) and {"commit", "role", "model"} <= set(entry) for entry in value)]
    assert len(lists) == 1, (
        f"the close record {rel} holds {len(lists)} lists whose entries each have commit, role and model; "
        f"one is expected (DEC-470). Its keys: {sorted(front)}")
    return lists[0]


def _entry_of(listed, commit):
    """The one entry of ``commit``; a listed id is the whole id or its first seven characters or more."""
    found = [entry for entry in listed
             if len(str(entry["commit"])) >= 7 and commit.startswith(str(entry["commit"]))]
    assert len(found) == 1, f"the commit {commit[:10]} is listed {len(found)} times: {listed}"
    return found[0]


def _names(entry, model):
    """The entry's model is the name as read, or the whole value of the line."""
    return str(entry["model"]).strip() in (model, f"{model} {ADDRESS}")


def test_commits_of_two_roles_are_listed_with_their_roles_and_models(project, sandbox, interface):
    """Two commits, two roles, two different model lines: each is listed with its own role and its own model,
    exactly as read."""
    commits = _ticket_of_two_roles(project, sandbox, DESIGNER_MODEL, ENGINEER_MODEL)
    listed = _listed(project, sandbox, interface)
    for role, model in ((DESIGNER, DESIGNER_MODEL), (ENGINEER, ENGINEER_MODEL)):
        entry = _entry_of(listed, commits[role])
        assert entry["role"] == role, f"the commit of the {role} is listed with the role {entry['role']!r}"
        assert _names(entry, model), \
            f"the commit of the {role} is listed with the model {entry['model']!r}, its line names {model!r}"


def test_no_commit_of_the_ticket_is_left_out_and_no_other_is_listed(project, sandbox, interface):
    """The list holds the ticket's commits, each once, and nothing else (the orchestrator's commits of the
    ticket file and of the checkpoint carry no ``Task`` trailer: they are not the ticket's)."""
    commits = _ticket_of_two_roles(project, sandbox, DESIGNER_MODEL, ENGINEER_MODEL)
    listed = _listed(project, sandbox, interface)
    for commit in commits.values():
        _entry_of(listed, commit)
    assert len(listed) == len(commits), f"the list holds {len(listed)} entries for {len(commits)} commits: {listed}"


def test_a_commit_without_a_co_author_line_is_listed_as_not_measured(project, sandbox, interface):
    """The engineer's commit carries no ``Co-Authored-By`` line: it is listed, with its role, and its model is
    "not measured". The model of the other commit is not given to it."""
    commits = _ticket_of_two_roles(project, sandbox, DESIGNER_MODEL, None)
    listed = _listed(project, sandbox, interface)
    entry = _entry_of(listed, commits[ENGINEER])
    assert entry["role"] == ENGINEER, f"the commit without the line is listed with the role {entry['role']!r}"
    assert entry["model"] == NOT_MEASURED, \
        f"the commit without a co-author line is listed with the model {entry['model']!r}, not {NOT_MEASURED!r}"


def test_a_commit_with_a_co_author_line_beside_one_without_keeps_its_model(project, sandbox, interface):
    """In the same ticket the designer's commit, which has the line, is listed with the model it names."""
    commits = _ticket_of_two_roles(project, sandbox, DESIGNER_MODEL, None)
    listed = _listed(project, sandbox, interface)
    entry = _entry_of(listed, commits[DESIGNER])
    assert entry["role"] == DESIGNER and _names(entry, DESIGNER_MODEL), \
        f"the designer's commit is listed as {entry}, its line names {DESIGNER_MODEL!r}"
