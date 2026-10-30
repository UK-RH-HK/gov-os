"""KPI 1, KPI 6 and failure KPI 7: ``gov close``'s own trailer gate reads the project's ``trailers_base``.

KPI 1 [DEC-704, W2-M238, W2-M250]: "gov close's own trailer gate reads the project's trailers_base and does not
judge commits before it." DEC-704's case: a ticket commit before the base (a-dev's ``540004a``, the lead's
commit that created the ticket file, without ``Implements:``) refused the close with ``TRAILER_MISSING``; the
same gate refused W1-42 for six KPI-line commits before this repository's base and for its claim commit.

KPI 6 [W2-M251, W2-M266]: "The ticket-creating commit and clone path maps without a trailers base are judged as
the base rule says, and the output names the base used." The base rule is DEC-482's: "a project may record a
trailers base, and only commits after it are judged; with none, the whole history." The part of the line on a
ticket-creating commit *after* the base, or in a project with no base, is a package (README, P-1); the cases
here hold what every reading shares. W2-M266: "A base move is reported with the number of commits it takes
out of judgement."

Failure KPI 7: "A commit after the base without Task:, Role: or Implements: still refuses."

The project: ``PROJ-base`` is created and worked on; the owner records the base as the project's adoption
boundary would be (a commit of its own), and the path map names it (DEC-479: the present path map is read).
"""

import json

import pytest

import w2_01_support as support

TICKET, WBS = "PROJ-base", "W1-base"
FEATURE = "src/example/feature.py"


def _boundary(project, name="boundary"):
    """The owner's commit that is the project's base (an adoption's last commit); returns it."""
    project.write(f"docs/{name}.md", f"# {name}\n")
    return project.commit(name, who=support.OWNER, trailers=("Task: setup", "Role: owner"), exact=True)


def _early(project, shape):
    """The ticket's commits before the base, in the shape W1-42 and DEC-704 show; returns the offending one."""
    if shape == "creating commit without Implements":          # DEC-704's 540004a
        return support.create_ticket(project, TICKET, WBS, trailers=support.merge_form(TICKET))
    if shape == "claim commit with Task: only":                 # W1-42's 93bcb247
        return support.create_ticket(project, TICKET, WBS, trailers=(f"Task: {TICKET}",))
    support.create_ticket(project, TICKET, WBS)                 # W1-42's six KPI-line commits
    return support.engineer_commit(project, TICKET, {"src/example/early.py": "# early\n"},
                                   trailers=(f"Task: {TICKET}", "Role: engineer"))


SHAPES = ("creating commit without Implements", "claim commit with Task: only",
          "engineer commit without Implements")


def _ready(project):
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})
    return support.checkpointed(project, TICKET)


# --------------------------------------------------------------------------
# KPI 1 (and KPI 6, the creating commit before the base): commits before the base are not judged
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shape", SHAPES)
def test_a_ticket_commit_before_the_base_does_not_refuse_the_close(shape, project, sandbox, interface):
    early = _early(project, shape)
    base = _boundary(project)
    project.set_path_map(**{support.BASE_KEY: base})
    _ready(project)

    run = support.run_close(project, sandbox, TICKET)

    assert not support.mentions(run.envelope().get("error") or {}, early), \
        f"the commit {early[:12]} before the base {base[:12]} is judged\n{run.describe()}"
    support.closed(run, interface)
    assert support.base.ticket_status(project.root, TICKET) == "closed"


@pytest.mark.parametrize("length", (40, 8), ids=("the full id", "an abbreviated id"))
def test_the_close_names_the_base_it_used(length, project, sandbox, interface):
    """KPI 6: the output names the base used, as a full commit id under ``trailers_base``."""
    _early(project, SHAPES[0])
    base = _boundary(project)
    project.set_path_map(**{support.BASE_KEY: base[:length]})
    _ready(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    assert base in support.bases_named(result), \
        f"the close's answer does not name the base {base} under {support.BASE_FIELD!r}\n{run.describe()}"


def test_a_project_without_a_base_is_judged_whole_and_the_close_says_no_base_was_used(project, sandbox,
                                                                                       interface):
    """KPI 6, a clone's path map without a base: the whole history is judged (DEC-482), and the answer says that
    no base was used (``trailers_base`` present and null)."""
    support.create_ticket(project, TICKET, WBS)
    _ready(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    assert support.bases_named(result) == [None], \
        f"the answer does not say that no base was used ({support.BASE_FIELD!r}: null)\n{run.describe()}"


def test_before_and_after_the_base_only_the_commit_after_it_is_named(project, sandbox, interface):
    """Both together: the early commit is not judged, the later one without ``Implements:`` refuses."""
    early = _early(project, SHAPES[0])
    base = _boundary(project)
    project.set_path_map(**{support.BASE_KEY: base})
    late = support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"},
                                   trailers=(f"Task: {TICKET}", "Role: engineer"))
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    assert support.TRAILER_MISSING in support.codes_of(error) and \
        any("Implements" in text for text in support.statements_naming(error, late)), \
        f"the commit {late[:12]} after the base is not a TRAILER_MISSING finding\n{run.describe()}"
    assert not support.mentions(error, early), \
        f"the commit {early[:12]} before the base is judged\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# Failure KPI 7: a commit after the base without Task:, Role: or Implements: still refuses
# --------------------------------------------------------------------------

AFTER_THE_BASE = {
    "without Implements": ((f"Task: {TICKET}", "Role: engineer"), "Implements"),
    "without Role": ((f"Task: {TICKET}", f"Implements: {support.CAPABILITY}"), "Role"),
    "without Task": ((), None),
}


@pytest.mark.parametrize("missing", tuple(AFTER_THE_BASE))
def test_a_commit_after_the_base_without_a_trailer_still_refuses(missing, project, sandbox, interface):
    trailers, word = AFTER_THE_BASE[missing]
    base = _boundary(project)
    project.set_path_map(**{support.BASE_KEY: base})
    support.create_ticket(project, TICKET, WBS)
    support.engineer_commit(project, TICKET, {FEATURE: "# feature\n"})
    bad = support.engineer_commit(project, TICKET, {FEATURE: "# changed\n"}, trailers=trailers)
    support.checkpointed(project, TICKET)

    run = support.run_close(project, sandbox, TICKET)

    error = support.refused(run, interface)
    named = support.statements_naming(error, bad)
    assert named, f"the commit {bad[:12]} after the base ({missing}) is not named\n{run.describe()}"
    if word:
        assert any(word in text for text in named), \
            f"the finding on {bad[:12]} does not name the missing {word}: trailer\n{run.describe()}"
    support.base.assert_not_closed(project, TICKET)


# --------------------------------------------------------------------------
# KPI 6, W2-M266: a move of the base is reported with the number of commits it takes out of judgement
# --------------------------------------------------------------------------

def _moves(value):
    """Every object in ``value`` that holds ``commits_out_of_judgement``."""
    return support.cli_support.find_records(value, key=support.MOVED_COUNT_FIELD)


def _moved_project(project, first):
    """The base is first ``first`` (a commit, or None for no base), then moved to a later boundary with three
    commits between them. Returns (the new base, the earlier base, the commits it takes out of judgement)."""
    old = None
    if first:
        old = _boundary(project, "first-boundary")
        project.set_path_map(**{support.BASE_KEY: old})
    project.write("docs/between.md", "# between\n")
    project.commit("between", who=support.OWNER, trailers=("Task: setup", "Role: owner"), exact=True)
    new = _boundary(project, "second-boundary")
    project.set_path_map(**{support.BASE_KEY: new})
    count_range = f"{old}..{new}" if old else new
    count = int(support.git(project, "rev-list", "--count", count_range).strip())
    assert count >= 2, "the fixture is wrong: the move takes out fewer than two commits"
    return new, old, count


@pytest.mark.parametrize("first", (True, False), ids=("from an earlier base", "from no base"))
def test_the_traceability_check_reports_a_move_of_the_base_with_its_count(first, project, sandbox):
    new, old, count = _moved_project(project, first)
    support.create_ticket(project, "PROJ-done", "W1-done")
    support.engineer_commit(project, "PROJ-done", {"src/example/done.py": "# done\n"},
                            trailers=support.trailers_of("PROJ-done"))
    support.set_status(project, "PROJ-done", "closed")

    code, out, err = support.run_check_command(project, sandbox)

    answer = json.loads(out) if out.strip().startswith("{") else {}
    assert new in support.bases_named(answer), \
        f"the check's output does not name the base used, {new}, under {support.BASE_FIELD!r}:\n{out}\n{err}"
    moves = _moves(answer)
    assert len(moves) == 1 and moves[0][support.MOVED_COUNT_FIELD] == count, \
        f"the move of the base is not reported with {count} commits out of judgement:\n{out}\n{err}"
    said = support.text_of(moves[0])
    assert new in said and (old in said if old else True), \
        f"the report of the move does not name the bases it moved between:\n{out}"
    assert code == 0, f"a move of the base alone makes the check fail (exit code {code}):\n{out}\n{err}"


@pytest.mark.parametrize("first", (True, False), ids=("from an earlier base", "from no base"))
def test_the_close_reports_a_move_of_the_base_with_its_count(first, project, sandbox, interface):
    new, old, count = _moved_project(project, first)
    support.create_ticket(project, TICKET, WBS)
    _ready(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    moves = _moves(result)
    assert len(moves) == 1 and moves[0][support.MOVED_COUNT_FIELD] == count, \
        f"the close does not report the move of the base with {count} commits out of judgement\n{run.describe()}"
    assert new in support.text_of(moves[0]) and (old in support.text_of(moves[0]) if old else True), \
        f"the report of the move does not name the bases it moved between\n{run.describe()}"


def test_a_project_that_never_recorded_a_base_reports_no_move(project, sandbox, interface):
    """The other side: no path map of the project's history holds a base, so no move is reported."""
    support.create_ticket(project, TICKET, WBS)
    _ready(project)

    run = support.run_close(project, sandbox, TICKET)

    result = support.closed(run, interface)
    assert not _moves(result), f"a move of the base is reported where none was made\n{run.describe()}"
