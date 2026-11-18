"""Success line 7: nothing project-specific (README, "The planted runs": feature and onto; the refusals plant a
project of their own)."""

from __future__ import annotations

import re

import pytest

import w2_115b_support as support
from w2_115b_support import A, module_rel

PROJECT_WORDS = ("w2/", "integrate", "DAEO-", "/home/")


def test_the_queue_s_code_names_no_project():
    folder = support.QUEUE_SRC
    assert folder.is_dir(), f"there is no {folder.relative_to(support.REPO_ROOT)}/"
    files = [p for p in sorted(folder.rglob("*")) if p.is_file() and "__pycache__" not in p.parts]
    assert any(p.suffix == ".py" for p in files), "src/gov/queue/ holds no Python file"
    found = [f"{p.relative_to(support.REPO_ROOT)}:{n}: {line.strip()}"
             for p in files for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1)
             if any(word in line for word in PROJECT_WORDS)]
    assert found == [], "the queue's code names this project:\n" + "\n".join(found)


# -- the settings: queue.yaml's integration branch and work branch form, --onto -------------------------------

@pytest.fixture(scope="module")
def feature(landing):
    return landing("feature")


def test_queue_yaml_on_main_with_feature_branches_lands(feature):
    result = support.answer(feature.run, support.EXIT_LANDED)
    assert result.get("onto") == "main" and result.get("landed") == [A.id]
    assert support.parents(feature.root, result["tested"]) == [feature.old_head, feature.tips[A.id]]
    support.assert_landed_through_close_commits(feature, result, "main", feature.old_head)
    assert support.status_at(feature.root, "main", A.id) == "closed"


def test_feature_closed_exactly_when_merged(feature):
    support.envelope(feature.run)
    support.assert_closed_iff_merged(feature, "main")


@pytest.fixture(scope="module")
def onto(landing):
    return landing("onto")


def test_onto_and_the_ticket_form_land_on_the_named_branch(onto):
    result = support.answer(onto.run, support.EXIT_LANDED)
    assert result.get("onto") == "release" and result.get("landed") == [A.id]
    support.assert_landed_through_close_commits(onto, result, "release", onto.old_head)
    assert support.rev(onto.root, "main") == onto.extra["main"], "main moved: --onto names release"
    assert support.git(onto.root, "symbolic-ref", "--short", "HEAD").strip() == "main"
    assert support.git(onto.root, "status", "--porcelain") == ""
    assert support.status_at(onto.root, "release", A.id) == "closed"


def test_onto_closed_exactly_when_merged(onto):
    support.envelope(onto.run)
    support.assert_closed_iff_merged(onto, "release")
    support.assert_closed_iff_merged(onto, "main")


# -- neither setting: refused before anything, nothing changed ------------------------------------------------

def assert_refused_unchanged(project, run, code, before, onto):
    support.refusal(run, code, support.EXIT_REFUSED_TO_RUN)
    assert project.state() == before, "the refused queue changed the project"
    assert not (project.root / "docs" / "close").exists()
    support.assert_closed_iff_merged(project, onto)


def test_a_detached_root_with_no_onto_and_no_queue_yaml_is_integration_unknown(planted):
    project = planted()
    project.plant_branch(A, "topic/aa", [({module_rel("widget"): "# CHANGED\n"}, "engineer", True)])
    project.checkout("--detach", "main")
    before = project.state()
    run = support.run_queue(project, f"{A.id}=topic/aa")
    assert_refused_unchanged(project, run, "INTEGRATION_UNKNOWN", before, "main")


@pytest.mark.parametrize("case", ["no_form", "no_such_branch", "form_names_no_branch"])
def test_a_ticket_without_a_work_branch_is_branch_unknown(planted, case):
    project = planted(queue_yaml='integration: main\nwork_branch: "feature/{wbs}"\n'
                      if case == "form_names_no_branch" else None)
    project.plant_branch(A, "topic/aa", [({module_rel("widget"): "# CHANGED\n"}, "engineer", True)])
    before = project.state()
    args = [f"{A.id}=topic/none"] if case == "no_such_branch" else [A.id]
    run = support.run_queue(project, *args)
    assert_refused_unchanged(project, run, "BRANCH_UNKNOWN", before, "main")
    assert re.search(r"BRANCH_UNKNOWN", run["stderr"])
