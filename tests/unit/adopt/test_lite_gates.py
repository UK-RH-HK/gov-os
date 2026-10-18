"""Builder tests for the lite A7 and A10 gates of ``gov adopt --lite`` (W2-52). Regression evidence only (MR-3).

The projects and the stages come from W1-41's builder tests (``test_adopt``), with the same two replacements. For
A10 two more are replaced, and named where they are: the rebuild (``gov.rebuild.command.run``) and the canaries
(``gov.retrieval.canary.run_canaries``). The acceptance cases hold all of them as they are.
"""
from __future__ import annotations

import pytest
import yaml

from gov.adopt import lite_gates, project
from gov.cli.errors import GovError

from .test_adopt import PATHS, VERDICT, commit, config, planned, proposal, refused, root, sh, stage, verdict, write

__all__ = ["root"]  # the fixture, used by every case
GATE_VERDICT = "audit/gate-verdict.md"


def after_a6(root, conf=None):
    if conf is None:
        planned(root)
    verdict(root)
    stage(root, "A5", verdict=VERDICT, **({"conf": conf} if conf else {}))
    stage(root, "A6", **({"conf": conf} if conf else {}))


def gate_verdict(root, gate, verdict="pass", session="auditor-7", role="independent-auditor", leave_out=(),
                 named=None):
    checked = [{"record": project.record_path(stage),
                "sha256": project.sha256((root / project.record_path(stage)).read_bytes())}
               for stage in lite_gates.CHECKED[gate] if stage not in leave_out]
    head = {"id": "AV-7", "type": "evidence", "status": "ACTIVE", "state_class": "EVIDENCE", "stage": named or gate,
            "verdict": verdict, "auditor_session": session, "checked": checked}
    write(root, GATE_VERDICT, "---\n" + yaml.safe_dump(head) + "---\n\n# AV-7\n")
    commit(root, f"{gate}: the auditor's record", *([f"Role: {role}"] if role else []))


def conditions(root, gate):
    return project.frontmatter((root / lite_gates.record_path(gate)).read_text(encoding="utf-8"))["conditions"]


def test_a7_passes_on_the_auditors_pass_with_its_own_record_and_conditions_met(root):
    after_a6(root)
    gate_verdict(root, "A7")
    before = project.tree(root)
    result = stage(root, "A7", verdict=GATE_VERDICT)
    rel = lite_gates.record_path("A7")
    assert result["record"] == rel and rel.startswith(project.FOLDER + "/") and rel not in before
    assert {k: v for k, v in project.tree(root).items() if k != rel} == before and project.dirty(root) == []
    head = project.frontmatter((root / rel).read_text(encoding="utf-8"))
    assert head["stage"] == "A7" and head["result"] == "pass" and head["auditor"]["session"] == "auditor-7"
    assert [item["state"] for item in head["conditions"]] == ["met"]
    text = (root / rel).read_text(encoding="utf-8")
    assert all(word in text for word in ("Wave 3", "CAP-44.k", "CAP-47.a"))


@pytest.mark.parametrize("verdict_word", ["fail", "pass_with_findings"])
def test_an_auditors_verdict_that_is_not_pass_commits_a_failing_record(root, verdict_word):
    after_a6(root)
    gate_verdict(root, "A7", verdict=verdict_word)
    error = refused("GATE_NOT_PASSED", root, "A7", verdict=GATE_VERDICT)
    assert error.details["record"] == lite_gates.record_path("A7") and project.dirty(root) == []
    states = [item["state"] for item in conditions(root, "A7")]
    assert states == ["not met"] and "accepted" not in states


def test_a_move_undone_after_a6_fails_a7(root):
    after_a6(root)
    sh(root, "mv", "pkg/util.py", "lib/util.py")
    commit(root, "moved back")
    gate_verdict(root, "A7")
    error = refused("GATE_NOT_PASSED", root, "A7", verdict=GATE_VERDICT)
    assert "pkg/util.py" in error.message and "lib/util.py" in error.message


def test_a_path_map_changed_after_a5_fails_a7(root):
    after_a6(root)
    rel = project.record_path("A3")
    write(root, rel, (root / rel).read_text(encoding="utf-8") + "\nedited\n")
    commit(root, "the path map, changed")
    gate_verdict(root, "A7")
    assert "path_map_hash" in refused("GATE_NOT_PASSED", root, "A7", verdict=GATE_VERDICT).message


@pytest.mark.parametrize("how, code", [
    (lambda root: sh(root, "rm", "-q", project.record_path("A6")), "STAGE_MISSING"),
    (lambda root: gate_verdict(root, "A7", leave_out=("A4",)), "VERDICT_INCOMPLETE"),
    (lambda root: gate_verdict(root, "A7", role="engineer"), "VERDICT_NOT_INDEPENDENT"),
    (lambda root: gate_verdict(root, "A7", session="adopter"), "VERDICT_NOT_INDEPENDENT"),
    (lambda root: gate_verdict(root, "A7", named="A5"), "VERDICT_OTHER_STAGE"),
    (lambda root: None, "RECORD_MISSING"),
])
def test_what_the_gate_stands_on_or_an_auditors_record_that_is_no_pass_refuses_and_writes_nothing(root, how, code):
    after_a6(root)
    how(root)
    if project.dirty(root):
        commit(root, "the case")
    tree = project.tree(root)
    refused(code, root, "A7", verdict=GATE_VERDICT)
    assert project.tree(root) == tree and project.dirty(root) == []


def test_a_gate_writes_over_no_record(root):
    after_a6(root)
    gate_verdict(root, "A7")
    stage(root, "A7", verdict=GATE_VERDICT)
    gate_verdict(root, "A7", session="auditor-8")
    tree = project.tree(root)
    assert refused("GATE_RECORDED", root, "A7", verdict=GATE_VERDICT).details["record"] == lite_gates.record_path("A7")
    assert project.tree(root) == tree


STORE = "legacy/memory/index.md"


@pytest.mark.parametrize("canary_hits", [True, False])
def test_a10_checks_the_retirement_the_rebuild_and_the_canaries(root, monkeypatch, canary_hits):
    from gov.rebuild import command
    from gov.retrieval import canary

    write(root, STORE, "# Legacy memory\n")
    commit(root, "a store")
    conf = config(paths=(*PATHS, "legacy/**", "governance/**"))
    for name in ("A0", "A1", "A2"):
        stage(root, name, conf=conf)
    stage(root, "A3", conf=conf, map=proposal(root, {"path": STORE, "action": "RETIRE", "kind": "memory-store"}))
    stage(root, "A4", conf=conf)
    after_a6(root, conf)
    stage(root, "A8", conf=conf)
    # Replaced: the rebuild and the canaries (the acceptance cases run both).
    stores = {"lexical": {"status": "recreated"}, "semantic": {"status": "recreated"}}
    monkeypatch.setattr(command, "run", lambda root, args, config: {"digest": "d" * 64, "stores": stores})
    monkeypatch.setattr(canary, "run_canaries", lambda root: {
        "lexical": {"passed": True, "status": "AVAILABLE", "misses": []},
        "semantic": {"passed": canary_hits, "status": "AVAILABLE" if canary_hits else "FACET_UNAVAILABLE",
                     "misses": [] if canary_hits else ["q"]}})
    gate_verdict(root, "A10")
    if canary_hits:
        assert stage(root, "A10", conf=conf, verdict=GATE_VERDICT)["digest"] == "d" * 64
    else:
        with pytest.raises(GovError) as caught:
            stage(root, "A10", conf=conf, verdict=GATE_VERDICT)
        assert caught.value.code == "ADOPT_GATE_NOT_PASSED" and "semantic" in caught.value.message
    states = [item["state"] for item in conditions(root, "A10")]
    assert states == (["met", "met"] if canary_hits else ["not met", "met"])
    text = (root / lite_gates.record_path("A10")).read_text(encoding="utf-8")
    assert all(word in text for word in ("d" * 64, STORE, "A9", "CAP-49", "CAP-47.a", "CAP-44.k"))
