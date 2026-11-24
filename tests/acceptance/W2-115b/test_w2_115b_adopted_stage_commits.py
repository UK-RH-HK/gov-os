"""Fix D7 (DEC-1227): a repository adopted with ``gov adopt --lite`` lands through ``gov queue`` with the stage commits
in the branch's range (README, "Fix: adopted repositories land (D7)").

These are pins, green on the base by design: nothing refuses the stage commits (trailer-less by design, W1-41), so
nothing was built. A later change that starts asking them for trailers, or that lets a stage subject through for a
change to the acceptance tests, turns them red.

Public interfaces only: ``python3 -m gov.cli.main adopt|queue ... --root <project> --json`` with this worktree's
``src/`` on ``PYTHONPATH``, the git state of the planted repository (commit subjects, trailers, changed paths).
Each planted project is built once per session, under a file lock in pytest's shared folder (as ``conftest._shared``).
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import shutil
import subprocess
import sys
import traceback
from pathlib import Path

import pytest

import w2_115b_support as support
from w2_115b_support import ENGINEER, ORCHESTRATOR, Planted, Ticket, module_rel

pytestmark = pytest.mark.skipif(shutil.which("gitleaks") is None,
                                reason="gitleaks is not installed: gov adopt's stage A0 sets up .gitleaks.toml")

# The adoption ticket's places (the shape of W2-81's adoption ticket): what the stage commits write that code places.
ADOPTION_PLACES = ("governance/adoption/**", ".gitleaks.toml", ".gitignore")
STAGES = ("A0", "A1", "A2")
SUBJECTS = {"A0": "gov adopt --lite A0: safety baseline", "A1": "gov adopt --lite A1: inventory",
            "A2": "gov adopt --lite A2: classification"}
A1_RECORD = "governance/adoption/A1-inventory.md"
CHANGED = "# CHANGED by the ticket\nVALUE = 2\n"
WORK = "work"

ADOPTED = Ticket("PROJ-adop", "F-ad", ["widget"], extra_allowed=ADOPTION_PLACES)


# --------------------------------------------------------------------------
# Building the planted adopted projects
# --------------------------------------------------------------------------

def run_gov(project, folder, *args):
    """``gov <args> --root <project> --json`` as a program: ``{"code", "stdout", "stderr"}``."""
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", *args, "--root", str(project.root), "--json"],
                          cwd=str(project.root), env=support.base_env(folder / "env-adopt"), capture_output=True,
                          text=True, timeout=support.GOV_TIMEOUT_S, stdin=subprocess.DEVNULL)
    return {"code": done.returncode, "stdout": done.stdout, "stderr": done.stderr}


def adopt(project, folder, stage):
    """One adoption stage, run by the tool on the branch checked out; it must succeed (a broken fixture is no red)."""
    done = run_gov(project, folder, "adopt", "--lite", "--stage", stage, "--role", "orchestrator")
    assert done["code"] == 0, f"fixture: gov adopt --lite --stage {stage} exited {done['code']}\n{done['stdout']}" \
                              f"\n{done['stderr']}"
    return done


def plant_adopted(folder, ticket=ADOPTED):
    """A project with ``ticket`` whose branch ``work`` holds the stages A0, A1 and A2 as the tool committed them, on
    the branch checked out at the root. Returns ``(project, [stage commit ids])``."""
    p = Planted(folder / "project", folder / "told", tickets=(ticket,))
    p.branch_from(WORK)
    for stage in STAGES:
        adopt(p, folder, stage)
    stages = support.git(p.root, "rev-list", "--reverse", f"{p.base}..HEAD").split()
    assert [support.git(p.root, "log", "-1", "--format=%s", c).strip() for c in stages] == \
        [SUBJECTS[s] for s in STAGES], "fixture: the stage commits are not A0, A1 and A2"
    return p, stages


def build_landed(folder, ticket=ADOPTED):
    """The branch: A0, A1, A2 by the tool, then one feature commit (the widget) with ``Task:`` and ``Role: engineer``;
    ``gov queue <ticket>=work``."""
    p, stages = plant_adopted(folder, ticket)
    feature = p.work(ticket, {module_rel("widget"): CHANGED})
    p.record_branch(ticket, WORK)
    p.home()
    support.self_check(p, {p.tips[ticket.id]: {ticket.node: "passed", support.USES_WIDGET_NODE: "passed"}})
    old_head, before = support.rev(p.root, "main"), p.state()
    run = support.run_queue(p, f"{ticket.id}={WORK}", env_folder=folder / "env-queue")
    return support.landing_data(p, run, "main", old_head, before, stages=stages, feature=feature, ticket=ticket.id)


def build_edited(folder):
    """The same branch to A2, then a hand edit of A1's record committed with ``Role: orchestrator`` and ``Task:``; the
    next stage, ``AS``, is run (``gov adopt --lite --stage AS``): it must refuse."""
    p, stages = plant_adopted(folder)
    p.commit("a hand edit of the inventory", ORCHESTRATOR, [f"Task: {ADOPTED.id}", "Role: orchestrator"],
             {A1_RECORD: (p.root / A1_RECORD).read_text(encoding="utf-8") + "\nA line written by hand.\n"})
    edit, before = support.rev(p.root, "HEAD"), p.state()
    run = run_gov(p, folder, "adopt", "--lite", "--stage", "AS", "--role", "orchestrator")
    return support.landing_data(p, run, WORK, edit, before, stages=stages, edit=edit)


def build_stage_subject(folder):
    """A branch of the ticket: its engineer commit (the widget), then a commit with a stage's subject and no trailer
    that adds a file under ``tests/acceptance/``; ``gov queue <ticket>=topic``."""
    p = Planted(folder / "project", folder / "told", tickets=(ADOPTED,))
    p.branch_from("topic/ad")
    p.work(ADOPTED, {module_rel("widget"): CHANGED})
    offending = p.commit(SUBJECTS["A0"], ENGINEER, [], {f"{ADOPTED.acceptance}test_ad_more.py":
                                                        "def test_more():\n    assert True\n"})
    p.record_branch(ADOPTED, "topic/ad")
    p.home()
    old_head, before = support.rev(p.root, "main"), p.state()
    run = support.run_queue(p, f"{ADOPTED.id}=topic/ad", env_folder=folder / "env-queue")
    return support.landing_data(p, run, "main", old_head, before, offending=offending)


def shared(factory, name, build):
    """The planted run ``name``, built once per session under a lock (xdist workers and cases read the same run)."""
    base = factory.getbasetemp()
    if os.environ.get("PYTEST_XDIST_WORKER"):
        base = base.parent
    folder = base / f"w2-115b-adopted-{name}"
    with open(base / f"w2-115b-adopted-{name}.lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        done, broken = folder / "landing.json", folder / "broken.txt"
        if broken.is_file():
            raise AssertionError(f"the planted run {name} could not be built:\n{broken.read_text()}")
        if done.is_file():
            return support.Landing(json.loads(done.read_text(encoding="utf-8")))
        if folder.exists():
            shutil.rmtree(folder)
        folder.mkdir(parents=True)
        try:
            data = build(folder)
        except BaseException:
            broken.write_text(traceback.format_exc(), encoding="utf-8")
            raise
        done.write_text(json.dumps(data), encoding="utf-8")
        return support.Landing(data)


@pytest.fixture(scope="session")
def adopted_landing(tmp_path_factory):
    return shared(tmp_path_factory, "landed", build_landed)


@pytest.fixture(scope="session")
def edited(tmp_path_factory):
    return shared(tmp_path_factory, "edited", build_edited)


@pytest.fixture(scope="session")
def stage_subject(tmp_path_factory):
    return shared(tmp_path_factory, "stage-subject", build_stage_subject)


# --------------------------------------------------------------------------
# Success lines 14 and 15: the adopted repository lands; what the stage commits write is told
# --------------------------------------------------------------------------

def test_the_stage_commits_carry_no_role_and_no_task_trailer(adopted_landing):
    """The premise, read from git: A0, A1 and A2 are the tool's commits and name no role and no ticket."""
    root, stages = adopted_landing.root, adopted_landing.extra["stages"]
    assert len(stages) == 3
    for commit in stages:
        body = support.git(root, "log", "-1", "--format=%B", commit)
        assert not re.search(r"^(Role|Task):", body, re.MULTILINE), f"{commit[:12]} carries a trailer:\n{body}"
        names = [line.split(":", 1)[0] for line in support.trailers(root, commit)]
        assert "Role" not in names and "Task" not in names, f"{commit[:12]} trailers: {names}"
    feature = support.trailers(root, adopted_landing.extra["feature"])
    assert f"Task: {adopted_landing.extra['ticket']}" in feature and "Role: engineer" in feature


def test_a_branch_of_stage_commits_and_a_feature_commit_lands_and_closes(adopted_landing):
    result = support.answer(adopted_landing.run, support.EXIT_LANDED)
    tid = adopted_landing.extra["ticket"]
    assert result.get("landed") == [tid], support.describe(adopted_landing.run)
    assert result.get("refused") == [] and result.get("culprits") == [], support.describe(adopted_landing.run)
    root, head = adopted_landing.root, support.rev(adopted_landing.root, "main")
    assert support.status_at(root, head, tid) == "closed"
    closes = support.assert_landed_through_close_commits(adopted_landing, result, "main", adopted_landing.old_head)
    assert set(closes) == {tid} and closes[tid] == support.rev(root, head)
    for commit in adopted_landing.extra["stages"] + [adopted_landing.extra["feature"]]:
        assert support.is_ancestor(root, commit, head), f"{commit[:12]} is not under the integration head"
    support.assert_closed_iff_merged(adopted_landing, "main")


def test_a_path_a_stage_commit_wrote_outside_the_ticket_s_places_is_a_notice_and_the_exit_is_0(adopted_landing):
    result = support.answer(adopted_landing.run, support.EXIT_LANDED)
    a0 = adopted_landing.extra["stages"][0]
    wrote = set(support.changed_paths(adopted_landing.root, a0))
    places = (".gitleaks.toml", ".gitignore")
    outside = {p for p in wrote if not p.startswith("governance/adoption/") and p not in places}
    assert outside, f"fixture: A0 wrote nothing outside the ticket's places: {sorted(wrote)}"
    notices = [n for n in result.get("path_notices") or [] if n.get("commit") == a0]
    assert notices, f"no path notice for A0's commit {a0[:12]}: {result.get('path_notices')}"
    assert {n.get("path") for n in notices} <= wrote, f"a notice names a path A0 did not write: {notices}"
    assert {n.get("path") for n in notices} & outside, f"no notice names an A0 path outside the places: {notices}"
    assert all(n.get("ticket") == adopted_landing.extra["ticket"] for n in notices)
    assert result.get("refused") == [] and result.get("landed") == [adopted_landing.extra["ticket"]]


# --------------------------------------------------------------------------
# Success line 16: a hand edit of a stage record is caught by gov adopt, not by trailers
# --------------------------------------------------------------------------

def test_a_hand_edit_of_a_stage_record_is_refused_by_the_next_stage_as_adopt_chain_broken(edited):
    run = edited.run
    assert run["code"] != 0, f"the stage ran over a hand-edited record: exit 0\n{run['stdout']}"
    try:
        envelope = json.loads(run["stdout"])
    except ValueError:
        raise AssertionError(f"no JSON envelope on stdout\n{run['stdout']}\n{run['stderr']}") from None
    assert envelope.get("ok") is False and envelope.get("command") == "adopt", envelope
    error = envelope.get("error") or {}
    assert error.get("code") == "ADOPT_CHAIN_BROKEN", envelope
    assert "A2-classification.md" in (error.get("message") or ""), f"the record that no longer stands: {error}"


def test_the_refused_stage_commits_nothing(edited):
    assert support.rev(edited.root, "HEAD") == edited.extra["edit"], "HEAD moved"
    assert support.git(edited.root, "rev-parse", "--abbrev-ref", "HEAD").strip() == WORK
    assert edited.state() == edited.before, "the refusal changed the repository"
    assert not support.git(edited.root, "status", "--porcelain").strip()


# --------------------------------------------------------------------------
# Failure line 4: a stage's subject buys nothing for a change to the acceptance tests
# --------------------------------------------------------------------------

def test_a_stage_subject_commit_that_adds_an_acceptance_test_is_refused_and_nothing_lands(stage_subject):
    run = stage_subject.run
    result = support.answer(run, support.EXIT_NOT_ALL_LANDED)
    tid = ADOPTED.id
    found = [r for r in result.get("refused") or [] if r.get("ticket") == tid]
    assert len(found) == 1, f"{tid} is not refused once: {support.describe(run)}"
    assert found[0].get("code") == "TEST_AUTHOR_REFUSED", found[0]
    offending = stage_subject.extra["offending"]
    assert offending in (found[0].get("commits") or []), f"the commit is not named: {found[0]}"
    assert result.get("landed") == [] and result.get("head") is None
    assert support.rev(stage_subject.root, "main") == stage_subject.old_head, "the integration branch moved"
    assert support.heads(stage_subject.state()) == support.heads(stage_subject.before), "a branch moved"
    assert support.status_at(stage_subject.root, "main", tid) == "open"
    assert not support.is_ancestor(stage_subject.root, stage_subject.tips[tid], "main")
