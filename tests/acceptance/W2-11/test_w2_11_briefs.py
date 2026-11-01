"""W2-11: the five brief templates and the orchestration skill (KPI lines 1-5, 12, 13, 15, 17 of the README)."""
from __future__ import annotations

import json
import re

import pytest

import w2_11_support as s

RETURN_FILES = (*s.BRIEF_RELS, s.SKILL_REL)


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
    counterpart = {"brief-test-designer.md": r"implementation", "brief-engineer.md": r"acceptance[- ]tests?"}
    name = rel.rsplit("/", 1)[-1]
    if name in counterpart:
        assert s.stated(text, [r"never read|not read|does not read", counterpart[name]]), (
            f"{rel}: Policy 2 (c), the counterpart's work, is not stated")


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


# KPI 4 [W2-L257] -----------------------------------------------------------------------------------------------

def test_the_launcher_command_is_a_command_not_a_code_span():
    text = _text(f"{s.TEMPLATES}/brief-lead.md")
    assert "<launcher command>" not in text, "brief-lead.md still has the <launcher command> placeholder"
    block_lines, prose, fence = [], [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fence = not fence
            continue
        (block_lines if fence or line.startswith("    ") else prose).append(line.strip())
    assert any(line.startswith("gov launch ") for line in block_lines), (
        "brief-lead.md states no `gov launch ...` command line in a command block")
    spans = [span for line in prose for span in re.findall(r"`([^`]+)`", line) if "gov launch" in span]
    assert not spans, f"brief-lead.md still gives the launcher command in a code span: {spans}"


# KPI 5 [W2-L258, W2-L256] --------------------------------------------------------------------------------------

STATE_CLASSES = {"AUTHORITATIVE", "DERIVED", "NARRATIVE", "EVIDENCE", "HISTORICAL", "UNKNOWN_OR_CONFLICTING"}


@pytest.mark.parametrize("rel", s.BRIEF_RELS)
def test_the_brief_template_carries_record_frontmatter(rel):
    schema = json.loads(s.read(f"{s.KERNEL}/schemas/common.schema.json"))
    front, _ = s.split_frontmatter(_text(rel))
    assert front is not None, f"{rel} has no YAML record frontmatter"
    required = schema["$defs"]["frontmatter"]["required"]
    missing = [key for key in required if not front.get(key)]
    assert not missing, f"{rel}: the record frontmatter lacks {missing}"
    assert front["state_class"] in STATE_CLASSES, f"{rel}: state_class {front['state_class']!r} is not a class"


def test_identity_through_the_settings_argument_is_not_cited_to_dec_183():
    loose = [x for x in s.stated(_text(s.SKILL_REL), [r"settings", r"identit"]) if s.cites(x, "DEC-183")]
    assert not loose, f"DEC-371 superseded DEC-183 for launched roles; still cited: {loose}"


def test_dec_486_is_not_cited_for_the_stops_short_block():
    loose = [x for x in s.stated(_text(s.SKILL_REL), [r"phone|short block"]) if s.cites(x, "DEC-486")]
    assert not loose, f"DEC-486 covers the closed count only; still cited for the block: {loose}"


# KPI 12, G15: the judgement rules in the kernel ------------------------------------------------------------------

@pytest.mark.parametrize("rel", [f"{s.TEMPLATES}/brief-reviewer.md", f"{s.SKILLS}/audit/SKILL.md"])
def test_the_judgement_rules_stand_word_for_word(rel):
    text = s.plain(_text(rel))
    for phrase in ('"Can an honest agent hit this in ordinary work?"', '"Does it fail open or lose work?"',
                   "Ordinary work: yes|no, because", "Consequence: fails open|loses work|other"):
        assert phrase.strip('"') in text, f"{rel} does not carry, word for word: {phrase}"
    assert s.stated(_text(rel), [r"\bno\b", r"\brow\b", r"never a round|not a round"]), (
        f"{rel} does not say that a finding marked no is a row, never a round")


# KPI 13, G14: the lead brief carries the common brief's role-independent rules -----------------------------------

LEAD_RULES = {
    "gov retrieve first": ("DEC-836", [r"gov retrieve"]),
    "retrieval in batches": ("DEC-860", [r"batch"]),
    "small code-graph queries": ("DEC-859", [r"code[- ]graph"]),
    # DEC-534: in the language-neutral form; no language's variable name is required (DEC-992, P-W2-11-7).
    "the code under test per command": ("DEC-732", [r"\btests?\b", r"verif", r"worktree", r"\bown\b",
                                                    r"\bsrc\b|source|code under test", r"per[- ]command",
                                                    r"session"]),
    "the scratch budget and TMPDIR": ("DEC-898", [r"TMPDIR"]),
    "a checkpoint at every handover": ("DEC-837", [r"checkpoint", r"handover"]),
    "the work order in parallel": ("DEC-959", [r"parallel", r"test designer", r"engineer|implementer"]),
    "brief_gaps in the return": ("DEC-943", [r"brief_gaps", r"return"]),
}


@pytest.mark.parametrize("rule", sorted(LEAD_RULES))
def test_the_lead_brief_carries_the_role_independent_rule(rule):
    decision, ideas = LEAD_RULES[rule]
    text = _text(f"{s.TEMPLATES}/brief-lead.md")
    found = s.cites(text, decision) and bool(s.stated(text, ideas))
    assert found, f"brief-lead.md does not state {rule} ({decision})"


# KPI 15, DEC-791 (ii): the standing decisions distilled, one case per group --------------------------------------

DISTILLED = {
    "launch forms": ("DEC-715", "DEC-731"), "rebuilds": ("DEC-719",),
    "code under test and the probe record": ("DEC-732", "DEC-733"), "parallelism": ("DEC-847",),
    "the merge rule": ("DEC-750", "DEC-754", "DEC-757"), "the lists only shrink": ("DEC-766", "DEC-768"),
    "guard holes as rows": ("DEC-779",), "closes and the report line": ("DEC-780", "DEC-787"),
}


@pytest.mark.parametrize("group", sorted(DISTILLED))
def test_the_kernel_states_the_distilled_decisions(group):
    corpus = "\n".join([*s.folder_texts(f"{s.SKILLS}/orchestration").values(), *map(_text, s.BRIEF_RELS)])
    missing = [d for d in DISTILLED[group] if not s.cites(corpus, d)]
    assert not missing, f"the orchestration skill and the briefs do not state {group}: {missing}"


# KPI 17: nothing scoped to this repository in the kernel files ---------------------------------------------------

def _kernel_files():
    rels = [*s.BRIEF_RELS, s.SKILL_TEMPLATE_REL]
    for name in ("orchestration", "test-design", "qa-review", "audit"):
        rels += s.folder_texts(f"{s.SKILLS}/{name}")
    return [rel for rel in dict.fromkeys(rels) if (s.REPO_ROOT / rel).is_file()]


@pytest.mark.parametrize("rel", _kernel_files())
def test_no_id_or_path_of_this_repository_in_a_kernel_file(rel):
    hits = sorted({m.group(0) for m in s.REPOSITORY_SCOPED.finditer(_text(rel))})
    assert not hits, f"{rel} holds this repository's own ids or paths: {hits}"
