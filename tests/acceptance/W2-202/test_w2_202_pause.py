"""A5 (L2 §3 A5): the pause, and the settings ``gov adopt --facts`` writes.

Success lines 8 (A5 S1) and 9 (A5 S2), failure line 5 (A5 F1). README, "The planted runs": paused, paused_detached,
and the adopted repositories.
"""

from __future__ import annotations

import json

import pytest
import yaml

import w2_202_support as support
from w2_202_support import A, kit

PAUSED = "PROJECT_PAUSED"


@pytest.fixture(scope="module")
def paused(landing):
    return landing("paused")


# -- success line 8 (A5 S1) ---------------------------------------------------------------------------------------

def test_while_the_project_is_paused_the_queue_refuses_with_project_paused_and_exit_1(paused):
    kit.refusal(paused.run, PAUSED, kit.EXIT_REFUSED_TO_RUN)
    assert paused.extra["frozen_after"] == "frozen", "the queue lifted the freeze"


def test_while_paused_nothing_is_written_and_the_branch_and_the_ticket_are_as_they_were(paused):
    kit.refusal(paused.run, PAUSED, kit.EXIT_REFUSED_TO_RUN)
    support.unchanged(paused.before, paused.extra["paused_after"])
    assert paused.extra["runtime_after"] == paused.extra["runtime_before"], \
        f"the paused queue wrote under .gov-runtime/: {paused.extra['runtime_after']}"
    assert kit.status_at(paused.root, paused.old_head, A.id) == "open"


def test_after_the_freeze_is_lifted_the_queue_lands(paused):
    kit.refusal(paused.run, PAUSED, kit.EXIT_REFUSED_TO_RUN)
    result = kit.answer(paused.extra["lifted"]["run"], kit.EXIT_LANDED)
    assert result.get("landed") == [A.id]
    head = kit.rev(paused.root, "main")
    assert head == result.get("head") != paused.old_head
    assert kit.is_ancestor(paused.root, paused.tips[A.id], head)
    assert kit.status_at(paused.root, head, A.id) == "closed"


# -- failure line 5 (A5 F1) ---------------------------------------------------------------------------------------

def test_with_neither_settings_file_and_the_root_on_main_the_queue_lands_onto_main(paused):
    """The paused project holds neither ``queue.yaml`` nor ``close.yaml`` and its root is on ``main``: once the
    freeze is lifted the landing goes onto ``main`` (the pause check changes nothing of how the branch is found)."""
    kit.refusal(paused.run, PAUSED, kit.EXIT_REFUSED_TO_RUN)
    result = kit.answer(paused.extra["lifted"]["run"], kit.EXIT_LANDED)
    assert result.get("onto") == "main" and result.get("base") == paused.old_head
    for rel in (support.QUEUE_YAML_REL, support.CLOSE_YAML_REL):
        assert kit.show(paused.root, result["head"], rel) is None and not (paused.root / rel).exists(), rel
    front = kit.close_record(paused, result["head"], A.id)
    assert front.get("onto") == "main"


def test_with_no_setting_and_no_branch_the_queue_is_integration_unknown_as_before(landing):
    """A detached root with no ``queue.yaml`` and no ``--onto``: paused it is ``PROJECT_PAUSED`` (the freeze is read
    first); with the freeze lifted it is ``INTEGRATION_UNKNOWN``, exit 1, nothing written, as before."""
    detached = landing("paused_detached")
    kit.refusal(detached.run, PAUSED, kit.EXIT_REFUSED_TO_RUN)
    support.unchanged(detached.before, detached.extra["paused_after"])
    lifted = detached.extra["lifted"]
    kit.refusal(lifted["run"], "INTEGRATION_UNKNOWN", kit.EXIT_REFUSED_TO_RUN)
    support.unchanged(lifted["before"], lifted["after"])
    assert not (detached.root / "docs" / "close").exists()


# -- success line 9 (A5 S2) ---------------------------------------------------------------------------------------

def adopt(tmp_path, name, files=None):
    """``gov adopt --facts`` in a fresh git repository on ``main`` holding ``files``: the repository."""
    project = tmp_path / name
    (project / ".tickets").mkdir(parents=True)
    (project / "README.md").write_text("# An adopted project\n", encoding="utf-8")
    for rel, text in (files or {}).items():
        (project / rel).parent.mkdir(parents=True, exist_ok=True)
        (project / rel).write_text(text, encoding="utf-8")
    kit.git(project, "init", "-q", "-b", "main")
    done = support.run_gov(project, "adopt", "--facts", env=kit.base_env(tmp_path / f"{name}-env"), timeout=300)
    assert done["code"] == 0 and json.loads(done["stdout"]).get("ok") is True, \
        f"fixture: gov adopt --facts failed\n{support.said(done)}"
    assert (project / support.FACTS_REL).is_file(), f"fixture: gov adopt --facts wrote no {support.FACTS_REL}"
    return project


def test_gov_adopt_facts_writes_queue_yaml_with_the_integration_branch_and_the_work_branch_form(tmp_path):
    project = adopt(tmp_path, "adopted")
    written = project / support.QUEUE_YAML_REL
    assert written.is_file(), f"gov adopt --facts wrote no {support.QUEUE_YAML_REL}"
    data = yaml.safe_load(written.read_text(encoding="utf-8"))
    assert isinstance(data, dict), f"{support.QUEUE_YAML_REL} is not a mapping: {data!r}"
    assert data.get("integration") == "main", f"integration: {data.get('integration')!r}"
    assert data.get("work_branch") == "{ticket}", f"work_branch: {data.get('work_branch')!r}"


def test_gov_adopt_facts_writes_no_close_yaml_and_leaves_a_present_queue_yaml_as_it_is(tmp_path):
    fresh = adopt(tmp_path, "fresh")
    assert (fresh / support.QUEUE_YAML_REL).is_file(), f"gov adopt --facts wrote no {support.QUEUE_YAML_REL}"
    assert not (fresh / support.CLOSE_YAML_REL).exists(), "gov adopt --facts wrote a close.yaml"
    own = '# the project\'s own\nintegration: develop\nwork_branch: "feature/{wbs}"\n'
    held = adopt(tmp_path, "held", {support.QUEUE_YAML_REL: own})
    assert (held / support.QUEUE_YAML_REL).read_text(encoding="utf-8") == own, "a present queue.yaml was changed"
    assert not (held / support.CLOSE_YAML_REL).exists(), "gov adopt --facts wrote a close.yaml"
