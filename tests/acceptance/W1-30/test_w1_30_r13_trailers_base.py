"""Round 13, piece 7: a project may record a base commit for the trailers check (DEC-482).

DEC-482: "The check gets the same base-commit setting as the citations check (DEC-474, DEC-479): a project may
record a trailers base, and only commits after it are judged; with none, the whole history." DEC-479, for the
citations check: the key is an optional top-level key of the project's path map, "a commit id, full or
abbreviated"; "the configuration read is the project's present one"; "with a base recorded and no commit after
it, the check gives the unmeasured answer, never green".

**Proposed (README, round 13, settlement 31).** The key is ``trailers_base``, beside ``decision_register`` and
``decision_citations_base``. A base that is no commit of the project, or a commit the checked commit does not
descend from, or a name that is no commit id, is a finding of its own, ``TRAILERS_BASE_UNKNOWN``, and no commit
is judged: the check is never green for it.

The cases run ``gov check --json`` in a temporary project, as the suite's other cases of this check do
(``test_w1_30_traceability.py``), and read the entry of ``product-traceability-trailers``. This repository's
own path map is not read and not changed.

The project: ticket ``PROJ-olda`` was closed before the base, and its commits carry no ``Implements:``;
ticket ``PROJ-newa`` is closed after the base.
"""

import json

import pytest

import w1_30_support as support

CHECK = "product-traceability-trailers"
BASE_KEY = "trailers_base"
CITATIONS_BASE_KEY = "decision_citations_base"
BASE_UNKNOWN = "TRAILERS_BASE_UNKNOWN"
OLD, OLD_WBS = "PROJ-olda", "W1-olda"
NEW, NEW_WBS = "PROJ-newa", "W1-newa"
CAPABILITY = "CAP-01"
GOOD = (f"Task: {NEW}", "Role: engineer", f"Implements: {CAPABILITY}")
NO_IMPLEMENTS = (f"Task: {NEW}", "Role: engineer")


def _closed_ticket(project, ticket, wbs, trailers, source):
    """A ticket whose commits carry ``trailers``, closed by the owner. Returns the engineer's commit."""
    project.add_ticket(ticket, wbs)
    project.add_passing_test(wbs)
    project.write(source, "# feature\n")
    commit = project.commit(f"implement {ticket}", who=support.IMPLEMENTER, trailers=trailers)
    path = project.root / support.ticket_path(ticket)
    path.write_text(path.read_text(encoding="utf-8").replace("status: in_progress", "status: closed"),
                    encoding="utf-8")
    project.commit(f"close {ticket}", who=support.OWNER)
    return commit


def _old_work(project):
    """The capability's record and the ticket closed without ``Implements:``. Returns (its engineer's commit,
    the commit after its close: the base of most cases)."""
    project.add_decision(CAPABILITY, "ACTIVE")
    project.commit("the capability", who=support.OWNER)
    old = _closed_ticket(project, OLD, OLD_WBS, (f"Task: {OLD}", "Role: engineer"), "src/example/old.py")
    return old, support.git(project.root, "rev-parse", "HEAD").strip()


def _record(project, commit=True, **settings):
    """The project's path map gains ``settings`` beside the suite's own; committed by the owner, or left in the
    working tree (``commit=False``): the configuration read is the project's present one (DEC-479)."""
    project.write(support.PATH_MAP_REL, support.path_map_text({**support.SUITE_SETTINGS, **settings}))
    if commit:
        project.commit("the project's path map", who=support.OWNER)


def _entry(project, sandbox, interface):
    """The entry of the trailers check in the answer of ``gov check --json``."""
    run = support.run_check(project, sandbox)
    envelope = support.check_envelope_of(run, interface)
    result = envelope.get("result") or envelope.get("error", {}).get("details", {})
    entries = [check for check in support.checks_of(result) if check.get("id") == CHECK]
    assert len(entries) == 1, f"{CHECK} is not reported once: {[c.get('id') for c in support.checks_of(result)]}"
    return entries[0]


def _text(entry):
    return json.dumps(entry.get("findings", []))


# --------------------------------------------------------------------------
# With a base, only the commits after it are judged
# --------------------------------------------------------------------------

@pytest.mark.parametrize("length", (40, 8), ids=("the full id", "an abbreviated id"))
def test_commits_before_the_base_are_not_judged(length, project, sandbox, interface):
    """The old ticket's commits lack ``Implements:``; the ticket closed after the base is as it must be."""
    _, base = _old_work(project)
    _closed_ticket(project, NEW, NEW_WBS, GOOD, "src/example/new.py")
    _record(project, **{BASE_KEY: base[:length]})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "GREEN", \
        f"every commit after the base {base[:12]} carries its trailers and the check is not green: {entry}"


def test_a_commit_after_the_base_is_judged_and_one_before_it_is_not_named(project, sandbox, interface):
    old, base = _old_work(project)
    new = _closed_ticket(project, NEW, NEW_WBS, NO_IMPLEMENTS, "src/example/new.py")
    _record(project, **{BASE_KEY: base})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "RED", f"a commit after the base lacks Implements: and the check is not red: {entry}"
    assert new[:12] in _text(entry), f"the commit after the base, {new[:12]}, is not named: {entry}"
    assert old[:12] not in _text(entry) and OLD not in _text(entry), \
        f"a commit before the base ({old[:12]}, of {OLD}) is judged: {entry}"


def test_an_id_that_resolves_to_no_record_is_judged_after_the_base_only(project, sandbox, interface):
    """Both tickets name a capability no record holds: the finding is the later commit's alone."""
    project.add_decision(CAPABILITY, "ACTIVE")
    project.commit("the capability", who=support.OWNER)
    old = _closed_ticket(project, OLD, OLD_WBS, (f"Task: {OLD}", "Role: engineer", "Implements: CAP-gone"),
                         "src/example/old.py")
    base = support.git(project.root, "rev-parse", "HEAD").strip()
    new = _closed_ticket(project, NEW, NEW_WBS, (f"Task: {NEW}", "Role: engineer", "Implements: CAP-none"),
                         "src/example/new.py")
    _record(project, **{BASE_KEY: base})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "RED" and "CAP-none" in _text(entry) and new[:12] in _text(entry), \
        f"the unresolved id of the commit after the base is not a finding: {entry}"
    assert "CAP-gone" not in _text(entry) and old[:12] not in _text(entry), \
        f"a commit before the base is judged: {entry}"


# --------------------------------------------------------------------------
# With no trailers base, the whole history (as today)
# --------------------------------------------------------------------------

def test_the_base_of_the_citations_check_is_no_base_of_the_trailers_check(project, sandbox, interface):
    """As today: the project records the citations base only, and the trailers check judges every commit."""
    old, base = _old_work(project)
    _closed_ticket(project, NEW, NEW_WBS, GOOD, "src/example/new.py")
    _record(project, **{CITATIONS_BASE_KEY: base})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "RED" and old[:12] in _text(entry), \
        f"with no trailers base the old commit {old[:12]} is not judged: {entry}"


# --------------------------------------------------------------------------
# A base that is no commit the checked commit descends from
# --------------------------------------------------------------------------

def _no_commit(project, base):
    return "0123456789abcdef0123456789abcdef01234567"


def _a_commit_of_another_branch(project, base):
    support.git(project.root, "checkout", "-q", "-b", "aside", base)
    project.write("src/example/aside.py", "# aside\n")
    aside = project.commit("a commit of another branch", who=support.OWNER)
    support.git(project.root, "checkout", "-q", "main")
    return aside


def _a_branch_name(project, base):
    support.git(project.root, "branch", "beef", base)
    return "beef"


@pytest.mark.parametrize("recorded", (_no_commit, _a_commit_of_another_branch, _a_branch_name),
                         ids=("no commit of the project", "a commit the head does not descend from",
                              "a branch named in hex digits"))
def test_a_base_that_is_no_commit_before_the_head_is_a_finding_of_its_own(recorded, project, sandbox, interface):
    """Every commit of the history carries its trailers: without the base the check would be green."""
    project.add_decision(CAPABILITY, "ACTIVE")
    base = project.commit("the capability", who=support.OWNER)
    wrong = recorded(project, base)
    _closed_ticket(project, NEW, NEW_WBS, GOOD, "src/example/new.py")
    _record(project, **{BASE_KEY: wrong})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] != "GREEN", f"the base {wrong!r} is no commit before the head and the check is green"
    codes = [finding.get("code") for finding in entry.get("findings", [])]
    assert BASE_UNKNOWN in codes, f"no finding {BASE_UNKNOWN} for the base {wrong!r}: {entry}"
    assert BASE_KEY in _text(entry) and wrong[:12] in _text(entry), \
        f"the finding names neither the key {BASE_KEY!r} nor the value {wrong!r}: {entry}"


def test_a_base_that_is_no_commit_does_not_hide_the_history_behind_one_green(project, sandbox, interface):
    """The unknown base and a history with a commit lacking ``Implements:``: never green, the base is named."""
    _old_work(project)
    _record(project, **{BASE_KEY: "0123456789abcdef"})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "RED" and BASE_UNKNOWN in [f.get("code") for f in entry.get("findings", [])], \
        f"the unknown base is not a finding: {entry}"


# --------------------------------------------------------------------------
# A base with nothing after it
# --------------------------------------------------------------------------

def test_a_base_with_no_commit_after_it_gives_the_unmeasured_answer(project, sandbox, interface):
    """The base is the head itself; the path map that records it is the working tree's (DEC-479)."""
    _, base = _old_work(project)
    _record(project, commit=False, **{BASE_KEY: base})
    assert support.git(project.root, "rev-parse", "HEAD").strip() == base, "the fixture is wrong: a commit follows"

    entry = _entry(project, sandbox, interface)

    assert entry["status"] != "GREEN", f"no commit after the base and the check is green: {entry}"
    said = [finding for finding in entry.get("findings", []) if finding.get("unmeasured") is True]
    assert said and str(said[0].get("reason", "")).strip(), \
        f"not the unmeasured answer (\"unmeasured\": true and a reason): {entry}"
    assert OLD not in _text(entry), f"a commit before the base is judged: {entry}"


def test_a_base_after_which_no_closed_ticket_has_a_commit_is_never_green(project, sandbox, interface):
    """Commits follow the base and none is a closed ticket's: nothing was judged (package P-3)."""
    _, base = _old_work(project)
    _record(project, **{BASE_KEY: base})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] != "GREEN", \
        f"no commit of a closed ticket lies after the base, nothing was judged, and the check is green: {entry}"
    assert OLD not in _text(entry), f"a commit before the base is judged: {entry}"


def test_a_closed_ticket_without_any_commit_stays_a_finding_with_a_base(project, sandbox, interface):
    """As today (``NO_COMMITS``): the base takes commits out of the judgement, not a closed ticket that no
    commit of the history names. The old ticket, whose commits lie before the base, is no such finding."""
    _, base = _old_work(project)
    _closed_ticket(project, NEW, NEW_WBS, GOOD, "src/example/new.py")
    project.add_ticket("PROJ-bare", "W1-bare")
    path = project.root / support.ticket_path("PROJ-bare")
    path.write_text(path.read_text(encoding="utf-8").replace("status: in_progress", "status: closed"),
                    encoding="utf-8")
    project.commit("a ticket closed without a commit of its own", who=support.OWNER)
    _record(project, **{BASE_KEY: base})

    entry = _entry(project, sandbox, interface)

    assert entry["status"] == "RED" and "PROJ-bare" in _text(entry), \
        f"the closed ticket without a commit is not a finding: {entry}"
    assert OLD not in _text(entry), f"the ticket whose commits lie before the base is a finding: {entry}"
