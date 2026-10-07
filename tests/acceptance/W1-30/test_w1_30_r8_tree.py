"""The tree a close measures is the commit it records (DEC-487, first behaviour).

"With any tracked file changed or any untracked, not ignored file present, ``gov close`` refuses before it
measures and names the paths. It is not a finding about the ticket's work: not counted, no repair ticket."

Every project here is committed as the suite commits it; then one file differs from the commit and the close
runs. Each case is a way the review found in which the measured tree was better than the recorded commit: the
tests, the ticket's profile, the governance files and the probed source are read from the working tree, and
the close record names ``HEAD``.

Held in every refusal: the answer names the path; the exit code is neither 0 nor 3 (3 is a finding, DEC-470);
nothing is closed; the ticket's count stays 0; no repair ticket is opened. A file git ignores refuses nothing.
"""

import pytest

import w1_30_support as support

TICKET = "PROJ-tree"
WBS = "W1-tree"
FEATURE = "src/example/feature.py"
NOTES = "governance/project/notes.yaml"

README_PRESENT = support.declared_check("readme-present", "test -s README.md")
LICENSE_PRESENT = support.declared_check("license-present", "test -s LICENSE", family="graph integrity")

# What pytest reads from the project's root before any test: every test function "passes" without being called.
EVERY_TEST_PASSES = (
    "import pytest\n\n\n"
    "@pytest.hookimpl(tryfirst=True)\n"
    "def pytest_pyfunc_call(pyfuncitem):\n"
    "    return True\n"
)


def _refused_for_the_tree(project, sandbox, interface, *paths):
    assert sorted(project.waiting_paths()) == sorted(paths), \
        f"the fixture is wrong: the working tree differs from the commit in {project.waiting_paths()}"
    head = support.head_of(project)

    run = support.run_close(project, sandbox, TICKET)

    text = support.error_text(support.refused_without_a_finding(run, interface))
    for rel in paths:
        assert rel in text, f"the refusal does not name {rel}\n{run.describe()}"
    support.assert_not_closed(project, TICKET)
    support.assert_nothing_counted(project, TICKET, run)
    support.assert_no_repair_ticket(project, run, TICKET)
    assert support.head_of(project) == head


def test_an_uncommitted_edit_that_makes_the_failing_acceptance_test_pass_refuses(project, sandbox, interface):
    """The committed acceptance test fails; the working tree's copy passes."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    rel = f"tests/acceptance/{WBS}/test_fail.py"
    project.write(rel, "def test_fail():\n    assert True\n")
    _refused_for_the_tree(project, sandbox, interface, rel)


def test_an_untracked_file_at_the_root_that_makes_every_test_pass_refuses(project, sandbox, interface):
    """The committed acceptance test fails; a file git does not know makes the test runner pass it."""
    support.build_ticket(project, TICKET, WBS, failing=True)
    project.write("conftest.py", EVERY_TEST_PASSES)
    _refused_for_the_tree(project, sandbox, interface, "conftest.py")


@pytest.mark.parametrize("profile_line", ["profile: STANDARD\n", ""], ids=["lowered", "removed"])
def test_an_uncommitted_edit_of_the_ticket_file_that_takes_the_full_profile_away_refuses(
        profile_line, project, sandbox, interface):
    """The committed ticket is FULL and has no probe record; the working tree's ticket file is not FULL."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    rel = support.ticket_path(TICKET)
    text = (project.root / rel).read_text(encoding="utf-8")
    assert text.count("profile: FULL\n") == 1, "the fixture is wrong: the ticket file has no FULL profile line"
    project.write(rel, text.replace("profile: FULL\n", profile_line))
    _refused_for_the_tree(project, sandbox, interface, rel)


def test_an_uncommitted_governance_change_refuses_where_a_hard_block_check_is_red(
        project_with_checks, sandbox, interface):
    """A hard-block check is red; the governance file was changed and not committed, so no commit of the
    ticket changed a governance file."""
    project = project_with_checks(README_PRESENT, LICENSE_PRESENT)
    support.build_ticket(project, TICKET, WBS)
    red = support.red_hard_blocks(support.checks_at_head(project, sandbox))
    assert red == ["license-present"], f"the fixture is wrong: the red hard-block checks are {red}"
    project.write(NOTES, "note: one\n")
    _refused_for_the_tree(project, sandbox, interface, NOTES)


def test_source_changed_after_the_probed_commit_and_not_committed_refuses(project, sandbox, interface):
    """The probe record names the commit that was probed; the source in the working tree is another."""
    support.build_ticket(project, TICKET, WBS, profile="FULL")
    project.add_probe(TICKET)
    project.commit("the probe record", who=support.ORCHESTRATOR)
    project.write(FEATURE, "# rewritten after the probe\n")
    _refused_for_the_tree(project, sandbox, interface, FEATURE)


def test_a_file_git_ignores_refuses_nothing(project, sandbox, interface):
    """The converse: an ignored file differs from no commit, and the ticket closes."""
    project.write(".gitignore", ".gov-runtime/\nlocal-state/\n")
    project.commit("what the project ignores", who=support.ORCHESTRATOR)
    support.build_ticket(project, TICKET, WBS)
    project.write("local-state/notes.txt", "a note of this machine\n")
    assert project.waiting_paths() == [], "the fixture is wrong: git does not ignore the file"

    run = support.run_close(project, sandbox, TICKET)

    support.result_of(run, interface)
    assert support.ticket_status(project.root, TICKET) == "closed"
