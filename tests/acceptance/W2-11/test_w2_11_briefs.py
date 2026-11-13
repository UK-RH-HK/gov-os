"""W2-11: the orchestration skill (KPI lines 1-5, 12, 13, 15, 17 of the README); the five brief templates' cases
are retired, the templates being one-line pointers (DEC-1137 (1))."""
from __future__ import annotations

import re

import pytest

import w2_11_support as s

RETURN_FILES = (s.SKILL_REL,)


def _text(rel):
    return s.read(rel)


# KPI 1 [AR-5, AR-6] ----------------------------------------------------------------------------------------------

@pytest.mark.parametrize("rel", RETURN_FILES)
def test_the_twelve_fields_come_first_payload_after_and_two_refusals_stop(rel):
    text = _text(rel)
    missing = [label for label in s.TWELVE if not re.search(rf"\b{label}\b", text)]
    assert not missing, f"{rel} does not name the return fields {missing}"
    assert s.stated(text, [r"payload", r"after", r"field"]), f"{rel}: no statement puts the payload after the fields"
    assert s.stated(text, [r"\btwo\b|twice", r"identical|same", r"refus", r"\bstop", r"return|say so"]), (
        f"{rel}: no statement says to stop after two identical refusals and return")


# KPI 2 [DEC-866]: Policy 2's read rule and the decision-record rule ----------------------------------------------

@pytest.mark.parametrize("rel", RETURN_FILES)
def test_policy_2_reads_open_with_its_refusals(rel):
    text = _text(rel)
    assert s.cites(text, "DEC-820"), f"{rel} does not cite DEC-820"
    assert s.stated(text, [r"\bread", r"\bopen\b|freely"]), f"{rel} does not say that reads are open"
    for idea in (r"secret", r"held-out"):
        assert s.stated(text, [r"\bread|refus|never", idea]), f"{rel}: the refusal of {idea!r} is not stated"


@pytest.mark.parametrize("rel", RETURN_FILES)
def test_the_owners_decisions_are_recorded_by_decision_record_commits(rel):
    text = _text(rel)
    assert s.cites(text, "DEC-861"), f"{rel} does not cite DEC-861"
    assert s.stated(text, [r"decision-record", r"owner"]), (
        f"{rel}: no statement says the owner's decisions are recorded by decision-record commits")


# KPI 3 [F-m1, W2-L268] ---------------------------------------------------------------------------------------------

def test_the_audit_brief_of_the_orchestration_skill_states_dec_430():
    texts = s.folder_texts(f"{s.SKILLS}/orchestration")
    assert any(s.stated(text, [r"\bDEC-430\b", r"audit"]) for text in texts.values()), (
        "the orchestration skill states no audit brief rule with DEC-430")


# KPI 5 [W2-L256] ------------------------------------------------------------------------------------------------

def test_identity_through_the_settings_argument_is_not_cited_to_dec_183():
    loose = [x for x in s.stated(_text(s.SKILL_REL), [r"settings", r"identit"]) if s.cites(x, "DEC-183")]
    assert not loose, f"DEC-371 superseded DEC-183 for launched roles; still cited: {loose}"


def test_dec_486_is_not_cited_for_the_stops_short_block():
    loose = [x for x in s.stated(_text(s.SKILL_REL), [r"phone|short block"]) if s.cites(x, "DEC-486")]
    assert not loose, f"DEC-486 covers the closed count only; still cited for the block: {loose}"


# KPI 12, G15: the judgement rules in the kernel ------------------------------------------------------------------

@pytest.mark.parametrize("rel", [f"{s.SKILLS}/audit/SKILL.md"])
def test_the_judgement_rules_stand_word_for_word(rel):
    text = s.plain(_text(rel))
    for phrase in ('"Can an honest agent hit this in ordinary work?"', '"Does it fail open or lose work?"',
                   "Ordinary work: yes|no, because", "Consequence: fails open|loses work|other"):
        assert phrase.strip('"') in text, f"{rel} does not carry, word for word: {phrase}"
    assert s.stated(_text(rel), [r"\bno\b", r"\brow\b", r"never a round|not a round"]), (
        f"{rel} does not say that a finding marked no is a row, never a round")


# KPI 15, DEC-791 (ii): the standing decisions distilled, one case per group --------------------------------------

DISTILLED = {
    "launch forms": ("DEC-715", "DEC-731"), "rebuilds": ("DEC-719",),
    "code under test and the probe record": ("DEC-732", "DEC-733"), "parallelism": ("DEC-847",),
    "the merge rule": ("DEC-750", "DEC-754", "DEC-757"), "the lists only shrink": ("DEC-766", "DEC-768"),
    "guard holes as rows": ("DEC-779",), "closes and the report line": ("DEC-780", "DEC-787"),
}


@pytest.mark.parametrize("group", sorted(DISTILLED))
def test_the_kernel_states_the_distilled_decisions(group):
    corpus = "\n".join(s.folder_texts(f"{s.SKILLS}/orchestration").values())
    missing = [d for d in DISTILLED[group] if not s.cites(corpus, d)]
    assert not missing, f"the orchestration skill does not state {group}: {missing}"


# KPI 17: nothing scoped to this repository in the kernel files ---------------------------------------------------

def _kernel_files():
    rels = [s.SKILL_TEMPLATE_REL]
    for name in ("orchestration", "test-design", "qa-review", "audit"):
        rels += s.folder_texts(f"{s.SKILLS}/{name}")
    return [rel for rel in dict.fromkeys(rels) if (s.REPO_ROOT / rel).is_file()]


@pytest.mark.parametrize("rel", _kernel_files())
def test_no_id_or_path_of_this_repository_in_a_kernel_file(rel):
    hits = sorted({m.group(0) for m in s.REPOSITORY_SCOPED.finditer(_text(rel))})
    assert not hits, f"{rel} holds this repository's own ids or paths: {hits}"
