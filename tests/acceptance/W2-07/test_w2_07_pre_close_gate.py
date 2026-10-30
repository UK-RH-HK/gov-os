"""KPI 5, KPI 6 and failure KPI 2 (its pre-close and disk part): DEC-868's pre-close gate inside ``gov close``, and
the disk floor of DEC-898.

KPI 5: "The pre-close gate inside gov close: it collects every suite it will run, in one process, as it runs them;
it runs gov check with no commit since the rebuild; and it checks that the ticket's checkpoint is fresh. Any failure
refuses at once, before any test runs [DEC-868]." DEC-868 item 3: "any gate failure refuses at once, naming its
cause, before any test runs, and spends no ratchet attempt."

KPI 6: "Before its regression, gov close reads the shared disk's free space and free inodes (W2-20's reading once it
lands; until then the floors 100 GiB and 10,000,000 inodes from the configuration) and refuses below either floor,
naming the reading [DEC-898]." The card: "Below the floor it refuses at once, naming the reading, and spends no
attempt."

Failure KPI 2: "A collection error, a RED gov check, a stale checkpoint, ... or a disk below the floor refused only
after the regression."

As in the commit gates' cases, the project holds two telling tests (the ticket's acceptance test and a regression
test). For the disk floor, the KPI says "before its regression": that case holds that the regression test did not
run; the other cases hold that no test ran. The floors are set through the path map (README, assumption A2), far
above any disk, so that the case does not depend on this machine.
"""

import pytest
import yaml

import w2_07_support as support

TICKET, WBS = "PROJ-pcg1", "W9-pcg1"
BROKEN = "def test_w207_broken(\n    # the closing parenthesis is missing\n"


def _assert_refused_before(project, sandbox, interface, which=None):
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface)
    support.assert_no_test_ran(project, run, which)
    support.assert_no_attempt_spent(project, TICKET, run)
    support.base.assert_not_closed(project, TICKET)
    return run, error


@pytest.mark.parametrize("where", ["regression", "acceptance"])
def test_a_collection_error_in_any_suite_refuses_before_any_test(where, project, sandbox, interface):
    """A test file that cannot be imported, in the regression (``tests/unit/``) or in the ticket's own acceptance
    folder: collecting every suite the close runs finds it before any test runs."""
    support.with_regression_mark(project)
    if where == "regression":
        project.write("tests/unit/test_w207_broken.py", BROKEN)
        project.setup_commit("a broken regression test")
        support.ready_ticket(project, TICKET, WBS)
    else:
        support.create_ticket(project, TICKET, WBS)
        project.write(f"tests/acceptance/{WBS}/test_w207_broken.py", BROKEN)
        project.commit("a broken acceptance test", who=support.TEST_DESIGNER,
                       trailers=support.trailers_of(TICKET, role="independent-test-designer"), exact=True)
        support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})
        support.checkpointed(project, TICKET)
    run, error = _assert_refused_before(project, sandbox, interface)
    assert support.names(error, "collect"), f"the refusal does not name the collection error\n{run.describe()}"
    assert support.names(error, "test_w207_broken"), f"the refusal does not name the broken file\n{run.describe()}"


def test_a_red_gov_check_refuses_before_any_test(project, sandbox, interface):
    """The project declares a hard-block check that is RED. The ticket's commits change no governance file, so
    today's close does not run the checks at all (DEC-480); the pre-close gate runs ``gov check`` on every close."""
    project.add_check("w207-red", "false")
    project.setup_commit("a check that is red")
    support.with_regression_mark(project)
    support.ready_ticket(project, TICKET, WBS)
    check = support.base.run_check(project, sandbox)
    assert check.returncode == support.EXIT_CHECK_FAILED, f"the fixture is wrong: gov check is not RED\n{check.describe()}"
    run, error = _assert_refused_before(project, sandbox, interface)
    assert support.names(error, "w207-red"), f"the refusal does not name the red check\n{run.describe()}"


def _stale_checkpoint(project, ticket):
    """A checkpoint of the ticket written long ago (W1-30's watchdog case: older than the 240-minute limit)."""
    cp_id = f"CP-{ticket}-0001"
    front = {"id": cp_id, "type": "checkpoint", "status": "ACTIVE", "state_class": "NARRATIVE",
             "title": f"{ticket} at task-start", "task": ticket, "task_status": "open", "trigger": "stop",
             "next_action": "implement the feature", "created": "2026-09-01T00:00:00Z",
             "inputs": [{"id": ticket, "version": "abc1234", "hash": "sha256:" + "a" * 64}]}
    text = "---\n" + yaml.safe_dump(front, sort_keys=False) + f"---\n\n# {cp_id}\n\n## Next action\n\nimplement\n"
    project.write(f"docs/checkpoints/{ticket}/{cp_id}.md", text)
    return project.commit("an old checkpoint", who=support.ORCHESTRATOR, trailers=("Role: orchestrator",), exact=True)


def test_a_stale_checkpoint_refuses_before_any_test(project, sandbox, interface):
    support.with_regression_mark(project)
    support.create_ticket(project, TICKET, WBS)
    support.work(project, TICKET, {"src/example/feature.py": "# feature\n"})
    _stale_checkpoint(project, TICKET)
    run, error = _assert_refused_before(project, sandbox, interface)
    assert "CHECKPOINT_STALE" in support.codes_of(error) or (
        support.names(error, "checkpoint") and support.names_any(error, "stale", "fresh")), \
        f"the refusal does not name the stale checkpoint\n{run.describe()}"


@pytest.mark.parametrize("floor", ["space", "inodes"])
def test_a_disk_below_a_floor_refuses_before_the_regression_naming_the_reading(floor, project, sandbox, interface):
    """The floor the path map sets is far above what any disk has free; the other floor stays low."""
    free_gib, free_inodes = support.free_on_disk(project.root)
    huge = {"space": 10 ** 9, "inodes": 10 ** 15}[floor]
    assert huge > (free_gib if floor == "space" else free_inodes), "the fixture is wrong: the disk is above the floor"
    key = support.FLOOR_GIB_KEY if floor == "space" else support.FLOOR_INODES_KEY
    project.set_path_map(**{key: huge})
    support.with_regression_mark(project)
    support.ready_ticket(project, TICKET, WBS)
    run, error = _assert_refused_before(project, sandbox, interface, which=[support.REGRESSION_MARK])
    word = ("inode",) if floor == "inodes" else ("disk", "space", "gib")
    assert support.names_any(error, *word), f"the refusal does not name the {floor} reading\n{run.describe()}"
    assert support.names(error, "free"), f"the refusal does not state what is free\n{run.describe()}"
