"""W2-13 success S5: search respects role separation (DEC-1065 (2); DEC-1056, DEC-1063, DEC-1052 G-14).

KPI: gov retrieve's results (every route) and gov context's supplementary block are filtered by the caller's
role_paths (GOV_ROLE or --role, and GOV_TICKET; the same path checks as the guard's, from one product module): an
engineer never receives its own ticket's acceptance tests, a test designer never the ticket's new code; what is
filtered is named in the bundle (how many, by which rule), never dropped silently; no role_paths section means no
filter.

The planted projects and the guard's checks as these cases take them are in ``w2_13_roles_support.py``. Only the
keyword route answers (``gov rebuild --no-embeddings``, a dead embedder host): no model is started.
"""

from __future__ import annotations

import pytest

import w2_13_roles_support as roles

pytestmark = pytest.mark.needs("git", "gitleaks")

HOW = ("env", "flag")  # the role as GOV_ROLE, or as --role
OWN_GLOB = f"tests/acceptance/{roles.OWN_WBS}"


@pytest.fixture(scope="module")
def engineer_project(box, tmp_path_factory):
    """Project A, indexed (the record store and the lexical index)."""
    return roles.rebuild(box, roles.build_engineer_project(tmp_path_factory.mktemp("w2-13-s5-a") / "repo"))


@pytest.fixture(scope="module")
def unfiltered_project(box, tmp_path_factory):
    """Project A without a role_paths section, indexed."""
    return roles.rebuild(box, roles.build_engineer_project(tmp_path_factory.mktemp("w2-13-s5-c") / "repo",
                                                           role_paths=False))


@pytest.fixture(scope="module")
def designer_project(box, tmp_path_factory):
    """``(home, project B)``: the engineer's tree ``<home>/gov-os-worktrees/W9-01``, indexed under that home."""
    home = tmp_path_factory.mktemp("w2-13-s5-home")
    return home, roles.rebuild(box, roles.build_designer_project(home), home=home)


def _premise(paths, files, what):
    missing = sorted(set(files) - paths)
    assert not missing, f"premise: {what} with no role does not return {missing}; the case would prove nothing"


def _named(result, role, globs, what):
    found = roles.filter_records(result, roles.rules_for(role, *globs))
    assert found, (f"{what}: what the {role}'s filter held back is not named (how many, by which rule: "
                   f"role_paths, its entry or the glob) anywhere in the result; it must never be dropped "
                   f"silently\n{roles.shown(result)}")


# --------------------------------------------------------------------------
# The engineer: never its own ticket's acceptance tests
# --------------------------------------------------------------------------

@pytest.mark.parametrize("question", roles.QUESTIONS.values(), ids=list(roles.QUESTIONS))
@pytest.mark.parametrize("how", HOW)
def test_engineer_retrieve_returns_none_of_its_own_tickets_acceptance_tests(box, engineer_project, how, question):
    """An engineer's ``gov retrieve`` (GOV_TICKET its ticket) returns none of the files under its ticket's
    tests/acceptance/<WBS>/, names what it held back, and still returns another ticket's tests and the integrated
    code (unit tests included)."""
    root = engineer_project
    baseline = roles.retrieve(box, how, root, question, ticket_id=roles.OWN_ID)
    _premise(roles.evidence_paths(baseline), roles.OWN_TESTS, f"gov retrieve {question!r}")

    bundle = roles.retrieve(box, how, root, question, role=roles.ENGINEER, ticket_id=roles.OWN_ID)
    leaked = sorted(path for path in roles.bundle_paths(bundle) if path.startswith(OWN_GLOB + "/"))
    assert not leaked, f"the engineer of {roles.OWN_WBS} got its own acceptance tests: {leaked}\n{roles.shown(bundle)}"
    assert not roles.markers_in(bundle, roles.OWN_TESTS), \
        f"the text of {roles.OWN_WBS}'s acceptance tests is in the engineer's bundle\n{roles.shown(bundle)}"
    kept = {**roles.OTHER_TESTS, **roles.INTEGRATED}
    lost = sorted(set(kept) - roles.evidence_paths(bundle))
    assert not lost, f"the filter held back more than the ticket's tests: {lost} are gone\n{roles.shown(bundle)}"
    _named(bundle, roles.ENGINEER, (OWN_GLOB,), "gov retrieve")


@pytest.mark.parametrize("how", HOW)
def test_engineer_context_supplementary_holds_none_of_its_own_tickets_acceptance_tests(box, engineer_project, how):
    """An engineer's ``gov context <its ticket>``: the supplementary block returns none of the ticket's acceptance
    tests, names what it held back, and still returns another ticket's tests and the integrated code."""
    root = engineer_project
    baseline = roles.context(box, how, root, roles.OWN_ID, ticket_id=roles.OWN_ID)
    _premise(roles.stacked_paths(baseline), roles.OWN_TESTS, f"gov context {roles.OWN_ID}")

    packet = roles.context(box, how, root, roles.OWN_ID, role=roles.ENGINEER, ticket_id=roles.OWN_ID)
    leaked = sorted(path for path in roles.supplementary_paths(packet) if path.startswith(OWN_GLOB + "/"))
    assert not leaked, f"the engineer's supplementary block holds its own acceptance tests: {leaked}\n" \
                       f"{roles.shown(packet)}"
    assert not roles.markers_in(packet, roles.OWN_TESTS), \
        f"the text of {roles.OWN_WBS}'s acceptance tests is in the engineer's packet\n{roles.shown(packet)}"
    kept = {**roles.OTHER_TESTS, **roles.INTEGRATED}
    lost = sorted(set(kept) - roles.stacked_paths(packet))
    assert not lost, f"the filter held back more than the ticket's tests: {lost} are gone\n{roles.shown(packet)}"
    _named(packet, roles.ENGINEER, (OWN_GLOB,), "gov context")


def test_engineer_retrieve_holds_back_its_tickets_cases_revised_in_another_folder(box, engineer_project):
    """{ticket_tests} as the guard reads it: a file in another ticket's acceptance folder that a test designer's
    commit made for the engineer's ticket (``Task:`` the ticket) is held back too; that folder's other files are
    not."""
    root = engineer_project
    baseline = roles.retrieve(box, "env", root, roles.QUESTION, ticket_id=roles.OWN_ID)
    _premise(roles.evidence_paths(baseline), roles.LINKED_OWN, f"gov retrieve {roles.QUESTION!r}")

    bundle = roles.retrieve(box, "env", root, roles.QUESTION, role=roles.ENGINEER, ticket_id=roles.OWN_ID)
    leaked = sorted(set(roles.LINKED_OWN) & roles.bundle_paths(bundle))
    assert not leaked and not roles.markers_in(bundle, roles.LINKED_OWN), \
        f"the engineer got a case revised for its ticket in another folder: {leaked}\n{roles.shown(bundle)}"
    lost = sorted(set(roles.OTHER_TESTS) - roles.evidence_paths(bundle))
    assert not lost, f"that folder's own tests were held back too: {lost}\n{roles.shown(bundle)}"


def test_coordination_ticket_holds_back_its_own_folder_only(box, engineer_project):
    """For a ``class: coordination`` ticket {ticket_tests} is its own folder only: an engineer on it gets none of
    tests/acceptance/<its WBS>/, but does get the file a test designer's commit revised for it in another folder."""
    root = engineer_project
    baseline = roles.retrieve(box, "env", root, roles.QUESTION, ticket_id=roles.COORD_ID)
    _premise(roles.evidence_paths(baseline), {**roles.COORD_TESTS, **roles.LINKED_COORD},
             f"gov retrieve {roles.QUESTION!r}")

    bundle = roles.retrieve(box, "env", root, roles.QUESTION, role=roles.ENGINEER, ticket_id=roles.COORD_ID)
    own = f"tests/acceptance/{roles.COORD_WBS}/"
    leaked = sorted(path for path in roles.bundle_paths(bundle) if path.startswith(own))
    assert not leaked and not roles.markers_in(bundle, roles.COORD_TESTS), \
        f"the engineer of the coordination ticket got its own folder's tests: {leaked}\n{roles.shown(bundle)}"
    lost = sorted(set(roles.LINKED_COORD) - roles.evidence_paths(bundle))
    assert not lost, f"a coordination ticket's cases revised in other folders were held back: {lost}\n" \
                     f"{roles.shown(bundle)}"


# --------------------------------------------------------------------------
# The test designer: never the ticket's new code in the engineer's tree
# --------------------------------------------------------------------------

@pytest.mark.parametrize("how", HOW)
def test_designer_retrieve_returns_none_of_the_tickets_new_code(box, designer_project, how):
    """A test designer's ``gov retrieve`` in the engineer's tree (~/gov-os-worktrees/<WBS>, on w2/<WBS>) returns
    none of the files the branch adds under the ticket's allowed paths (its code, its unit tests, its document),
    names what it held back, and still returns the integrated code under the same paths and the rest."""
    home, root = designer_project
    baseline = roles.retrieve(box, how, root, roles.QUESTION, ticket_id=roles.OWN_ID, home=home)
    _premise(roles.evidence_paths(baseline), roles.NEW_CODE, f"gov retrieve {roles.QUESTION!r}")

    bundle = roles.retrieve(box, how, root, roles.QUESTION, role=roles.DESIGNER, ticket_id=roles.OWN_ID, home=home)
    leaked = sorted(set(roles.NEW_CODE) & roles.bundle_paths(bundle))
    assert not leaked and not roles.markers_in(bundle, roles.NEW_CODE), \
        f"the test designer got the ticket's new work: {leaked}\n{roles.shown(bundle)}"
    kept = {**roles.INTEGRATED, **roles.OTHER_NEW}
    lost = sorted(set(kept) - roles.evidence_paths(bundle))
    assert not lost, f"the filter held back integrated code or work outside the ticket's paths: {lost}\n" \
                     f"{roles.shown(bundle)}"
    _named(bundle, roles.DESIGNER, tuple(roles.ALLOWED), "gov retrieve")


def test_designer_retrieve_keeps_the_shared_test_files(box, designer_project):
    """The guard's (c3): the shared test files the designer needs for fixtures (``*support*.py``, ``conftest.py``)
    are no part of {ticket_impl}, new on the branch or not."""
    home, root = designer_project
    baseline = roles.retrieve(box, "env", root, roles.QUESTION, ticket_id=roles.OWN_ID, home=home)
    _premise(roles.evidence_paths(baseline), {**roles.NEW_SHARED, **roles.NEW_CODE},
             f"gov retrieve {roles.QUESTION!r}")

    bundle = roles.retrieve(box, "env", root, roles.QUESTION, role=roles.DESIGNER, ticket_id=roles.OWN_ID, home=home)
    assert not set(roles.NEW_CODE) & roles.bundle_paths(bundle), \
        f"the designer's filter is not in force: the ticket's new code came back\n{roles.shown(bundle)}"
    lost = sorted(set(roles.NEW_SHARED) - roles.evidence_paths(bundle))
    assert not lost, f"a shared test file was held back from the test designer: {lost}\n{roles.shown(bundle)}"


# --------------------------------------------------------------------------
# No role_paths section: no filter
# --------------------------------------------------------------------------

def test_no_role_paths_section_means_no_filter(box, engineer_project, unfiltered_project):
    """The same engineer's call in two projects that differ only in the path map: with the role_paths section its
    ticket's tests are held back; without it they come back and nothing is named as held back."""
    held = roles.retrieve(box, "env", engineer_project, roles.QUESTION, role=roles.ENGINEER, ticket_id=roles.OWN_ID)
    assert not set(roles.OWN_TESTS) & roles.bundle_paths(held), \
        f"with the section, the engineer's own tests came back\n{roles.shown(held)}"

    bundle = roles.retrieve(box, "env", unfiltered_project, roles.QUESTION, role=roles.ENGINEER,
                            ticket_id=roles.OWN_ID)
    lost = sorted(set(roles.OWN_TESTS) - roles.evidence_paths(bundle))
    assert not lost, f"with no role_paths section the engineer's call was filtered: {lost} are gone\n" \
                     f"{roles.shown(bundle)}"
    named = roles.filter_records(bundle, roles.rules_for(roles.ENGINEER, OWN_GLOB))
    assert not named, f"with no role_paths section, a filter is named: {named}"
