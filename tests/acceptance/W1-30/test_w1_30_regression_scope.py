"""A2 under W2-66's path-scoped regression (DEC-880 item 2, I2 F9; W2-66's README, "Interface").

``test_w1_30_close.py::test_regression_includes_other_acceptance_folders`` holds the full run's case: a project
without a test map runs everything, and another ticket's red folder blocks the close. These are the scoped
cases. Each project has a test map and a base (a green nightly record naming the commit that holds the other
ticket and its folder), and the ticket changes ``src/example/feature.py``:

- the other ticket's paths overlap the change: the scoped close runs its folder, and a red there blocks it;
- they do not: the scoped close leaves the folder out, and its evidence names it and why;
- ``gov close --full`` runs the folder whatever the change, and a red there blocks it.
"""

import json

import pytest
import yaml

import w1_30_support as support

TICKET = "PROJ-aaaa"
WBS = "W1-test"
OTHER, OTHER_WBS = "PROJ-oooo", "W1-other"
OTHER_FOLDER = f"tests/acceptance/{OTHER_WBS}"
OTHER_TEST = f"{OTHER_FOLDER}/test_other.py"
TEST_MAP_REL = "governance/project/test-map.yaml"
TEST_MAP = {
    "version": 1,
    "shared_core": ["src/gov/close/**", support.PATH_MAP_REL, TEST_MAP_REL],
    "record_only": [".tickets/**", "docs/checkpoints/**", "docs/close/**", "docs/probes/**",
                    "docs/DECISION_REGISTER.md", "docs/plan/*.md", "governance/project/orchestration/**.md"],
    "record_reading": [],
    "every_close": [],
    "couplings": [],
}


def _scoped_project(project, sandbox, other_paths, other_red):
    """The other ticket and its folder, and the test map, at the base; a green record naming it; then the
    ticket's work and checkpoint."""
    project.write(support.ticket_path(OTHER), support.ticket_text(OTHER, OTHER_WBS, allowed_paths=other_paths,
                                                                  status="closed"))
    project.write(OTHER_TEST, "def test_other():\n    assert False, 'other ticket fails'\n" if other_red else
                  "def test_other():\n    assert True\n")
    project.write(TEST_MAP_REL, yaml.safe_dump(TEST_MAP, sort_keys=False))
    base = project.commit("the other ticket and the test map", who=support.OWNER, trailers=())
    record = {"branch": "main", "head": base, "tree": support.git(project.root, "rev-parse", "HEAD^{tree}").strip(),
              "scope": "full", "verdict": "green", "base": None, "junit_xml": [], "failures": [], "packages": []}
    project.write(f"docs/close/nightly/NR-20261001T000000Z-{base[:12]}.json", json.dumps(record) + "\n")
    project.commit("the nightly run's record", who=support.ORCHESTRATOR)
    project.add_ticket(TICKET, WBS)
    project.add_passing_test(WBS)
    project.write("src/example/feature.py", "# feature\n")
    project.commit("implement", who=support.IMPLEMENTER, trailers=support.trailers_of(TICKET))
    support.checkpointed(project, TICKET)


def _evidence(run, holder):
    evidence = (holder or {}).get("evidence")
    assert isinstance(evidence, dict), f"the close states no evidence block\n{run.describe()}"
    return evidence


def test_a_selected_folder_of_another_ticket_runs_and_blocks_the_scoped_close_when_red(project, sandbox,
                                                                                         interface):
    _scoped_project(project, sandbox, other_paths=["src/example/**"], other_red=True)
    run = support.run_close(project, sandbox, TICKET)
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert OTHER_TEST in json.dumps(error), f"the refusal does not name the other ticket's failing test\n{run.describe()}"
    evidence = _evidence(run, error.get("details"))
    assert evidence.get("scope") == "scoped", f"the close is not stated scoped: {evidence}"
    selected = [e for e in evidence.get("selected") or [] if str(e.get("target", "")).rstrip("/") == OTHER_FOLDER]
    assert selected and any(w.get("reason") == "OVERLAP" and w.get("ticket") == OTHER for w in selected[0]["why"]), \
        f"the other folder is not named as selected for its ticket's overlap: {evidence.get('selected')}"


def test_a_scoped_close_that_leaves_another_ticket_s_folder_out_names_it_and_why(project, sandbox, interface):
    _scoped_project(project, sandbox, other_paths=["src/elsewhere/**"], other_red=False)
    run = support.run_close(project, sandbox, TICKET)
    result = support.result_of(run, interface)
    evidence = _evidence(run, result)
    assert evidence.get("scope") == "scoped", f"the close is not stated scoped: {evidence}"
    left = [e for e in evidence.get("left_out") or []
            if str(e.get("target", "")).rstrip("/") in (OTHER_FOLDER, OTHER_TEST)]
    assert left and any(w.get("reason") == "NOT_REACHED" for w in left[0].get("why") or []), \
        f"the left-out folder is not named with why: {evidence.get('left_out')}"
    assert support.the_close_record(project, TICKET).get("evidence") == evidence, \
        "the close record does not hold the evidence the result states"


@pytest.mark.parametrize("other_paths", [["src/example/**"], ["src/elsewhere/**"]], ids=["overlapping", "unreached"])
def test_a_full_close_runs_another_ticket_s_folder_whatever_the_change_and_blocks_when_red(project, sandbox, interface,
                                                                                            other_paths):
    _scoped_project(project, sandbox, other_paths=other_paths, other_red=True)
    run = support.run_close(project, sandbox, TICKET, "--full")
    error = support.refused(run, interface, support.EXIT_CHECK_FAILED)
    assert OTHER_TEST in json.dumps(error), f"the refusal does not name the other ticket's failing test\n{run.describe()}"
    assert _evidence(run, error.get("details")).get("scope") == "full", "the --full close is not stated full"
