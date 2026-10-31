"""W2-11, KPI 6 (DEC-866): the briefs, the orchestration skill and its copies, the orchestrator role file and its
copies teach no superseded rule; the same check fails on planted files (the failure line)."""
from __future__ import annotations

import pytest

import w2_11_support as s


def test_every_swept_file_is_there():
    expected = [*s.BRIEF_RELS, *s.ROLE_RELS, s.SKILL_REL, *(f"{c}/orchestration/SKILL.md" for c in s.COPY_ROOTS)]
    missing = [rel for rel in expected if not (s.REPO_ROOT / rel).is_file()]
    assert not missing, f"missing: {missing}"


@pytest.mark.parametrize("rel", s.supersession_files())
def test_the_file_teaches_no_superseded_rule(rel):
    found = s.superseded_teachings(s.read(rel))
    assert not found, f"{rel} still teaches:\n" + "\n".join(f"  {f}" for f in found)


@pytest.mark.parametrize("rel", [s.SKILL_REL, f"{s.TEMPLATES}/brief-lead.md"])
def test_dec_460s_citation_for_naming_the_model_stays(rel):
    assert s.stated(s.read(rel), [r"\bDEC-460\b", r"model"]), f"{rel} no longer cites DEC-460 for the model"


PLANTED = {
    "LEAD_CHECKPOINT": "A lead returns DONE, PACKAGES, ESCALATION or LEAD_CHECKPOINT (DEC-236).",
    "context limit": "At about <context limit> tokens, write the checkpoint and return.",
    "listing refusal": "- Run no glob, no search and no listing over `governance/project/`: name the files one "
                       "by one (DEC-508).",
    "held-out names": "- Never type the held-out file's path; the guard refuses any call that names a held-out "
                      "path (DEC-162).",
    "fixed ceiling": "- A stated ceiling holds: at most `<ceiling>` tickets in flight (DEC-235).",
    "owner batch": "- The owner commits the decision record with `Role: owner`, in the next batch.",
}
CURRENT = ("- Reads are open (DEC-820); refused only: secrets, the held-out material's contents, the counterpart's "
           "work on the same ticket and the hidden half of an evaluation set.\n\n"
           "- No fixed number of tickets in flight: as many as the gate and the limits allow (DEC-847).\n\n"
           "- A checkpoint at every handover (DEC-837). The owner's decisions are recorded by the orchestrator's "
           "decision-record commits (DEC-861).\n")


PLANTED_IN = (f"{s.TEMPLATES}/brief-lead.md", f"{s.COPY_ROOTS[1]}/orchestration/SKILL.md", s.ROLE_RELS[3])


@pytest.mark.parametrize("kind", sorted(PLANTED))
def test_a_planted_file_that_still_teaches_the_old_rule_fails(tmp_path, kind):
    rel = PLANTED_IN[sorted(PLANTED).index(kind) % len(PLANTED_IN)]   # a template, a skill copy, a role copy
    planted = tmp_path / rel
    planted.parent.mkdir(parents=True)
    planted.write_text(f"# Planted\n\n{CURRENT}\n{PLANTED[kind]}\n", encoding="utf-8")
    assert s.supersession_files(tmp_path) == [rel], "the swept file list does not reach the planted file"
    assert s.superseded_teachings(planted.read_text(encoding="utf-8")), f"the check passed a file teaching {kind}"


def test_a_file_stating_only_the_current_rules_passes(tmp_path):
    assert not s.superseded_teachings(f"# Current\n\n{CURRENT}"), "the check refuses the current rules"
