"""W2-128 round 2b (S11 and S14; round 2a's review F1-F4 and its F5 link notice): the orchestration skill's lifted
or expired rules (F2), the test-design skill's read-rule citation (F4) and the checkpoint template's empty example
``task:`` (README, "Round 2b"). F1 (the template's rulesync orchestrator role), F3 (round 2a's two strengthened
cases), the versions (1.2.0) and the guards are revisions of ``test_w2_128_round2a.py``'s cases (DEC-866).

Sources: DEC-511 as changed by DEC-1057 (R-6: no committed ``gov checkpoint`` record per round); DEC-963 item 1 (one
writer per tree) in place of DEC-254's interim rule; DEC-820 (reads are open but for its four refusals);
``contract.yaml`` CAP-38.c (independent test authorship), not CAP-38.b (governance test families) or DEC-136.
"""

from __future__ import annotations

import re

import pytest

import w2_128_support as s
from test_w2_128_links import _judge
from test_w2_128_round2a import NEG, ORCHESTRATION, PERMIT, TEST_DESIGN, clauses, now, section

CHECKPOINT_TEMPLATE = "template/governance/kernel/templates/checkpoint.md"


def body(rel: str) -> str:
    return s.split(now(rel))[1]


# --- F2: the orchestration skill's lifted or expired rules -----------------------------------------------------------

def test_s11_f2_orchestration_requires_no_gov_checkpoint_record_per_round_on_dec_511():
    text = body(ORCHESTRATION)
    required = [line for line in clauses(text)
                if re.search(r"\bround", line, re.I) and "checkpoint" in line.lower()
                and "gov checkpoint" in line and not NEG.search(line) and not PERMIT.search(line)]
    assert not required, f"the orchestration skill still requires a gov checkpoint record per round: {required}"
    alone = [unit[:100] for unit in s.units(text) if re.search(r"DEC-511\b", unit) and "DEC-1057" not in unit]
    assert not alone, f"the orchestration skill cites DEC-511 without DEC-1057, which lifted it (R-6): {alone}"


def test_s11_f2_one_writer_per_tree_cites_dec_963_not_dec_254():
    text = body(ORCHESTRATION)
    assert not re.search(r"DEC-254\b", text), "the orchestration skill still cites DEC-254 (an expired interim rule)"
    writers = [unit for unit in s.units(text)
               if re.search(r"\bwrit\w*\s+sessions?\b|\bone\s+writer\b|\bsingle\s+writer\b", unit, re.I)
               and re.search(r"\btrees?\b|\bworktrees?\b", unit, re.I)]
    assert writers, "the orchestration skill no longer states the one-writer-per-tree rule (DEC-963 item 1)"
    uncited = [unit[:100] for unit in writers if not re.search(r"DEC-963\b", unit)]
    assert not uncited, f"the one-writer-per-tree line does not cite DEC-963: {uncited}"


def test_s11_f2_no_bar_on_reading_another_sessions_folders():
    found = [line for line in clauses(body(ORCHESTRATION))
             if re.search(r"\b(?:an)?other\s+session", line, re.I) and re.search(r"\bread\b", line, re.I)
             and NEG.search(line) and not PERMIT.search(line)
             and not re.search(r"counterpart|same ticket", line, re.I)]
    assert not found, f"the orchestration skill still forbids reading another session's folders (DEC-820): {found}"


# --- F4: the test-design read rule's citation --------------------------------------------------------------------------

def test_s11_f4_test_design_read_rule_cites_cap_38c_not_cap_38b_or_dec_136():
    rule = section(now(TEST_DESIGN), "read")
    assert re.search(r"CAP-38\.c\b", rule), "the read rule does not cite CAP-38.c (independent test authorship)"
    wrong = [cited for cited in ("CAP-38.b", "DEC-136") if re.search(re.escape(cited) + r"(?![\w.])", rule)]
    assert not wrong, f"the read rule still cites {wrong} for working from the spec and its KPIs"


# --- The link notice (review F5): the checkpoint template's example task ----------------------------------------------

def test_s14_checkpoint_template_task_is_empty_with_a_comment_to_fill_it():
    text = now(CHECKPOINT_TEMPLATE)
    front, _ = s.split(text)
    assert isinstance(front, dict) and "task" in front, "checkpoint.md's front matter has no task: key"
    assert front["task"] in (None, ""), f"checkpoint.md's example task: is {front['task']!r}, not empty"
    lines = [line for line in text.split("\n") if line.startswith("task:")]
    assert len(lines) == 1 and "#" in lines[0] and re.search(r"\bid\b|ticket|DAEO", lines[0].split("#", 1)[1]), \
        f"checkpoint.md's task: line carries no comment saying to fill it with the ticket's id: {lines}"


@pytest.mark.parametrize("rel", [CHECKPOINT_TEMPLATE, "governance/kernel/templates/checkpoint.md"],
                         ids=["template", "adopted"])
def test_s14_gov_links_on_a_tree_holding_the_checkpoint_template_gives_no_unknown_id(tmp_path, rel):
    # The template as it stands, unfilled, at its own path (this repository's, then an adopted project's)
    answer, code, stderr = _judge(tmp_path, rel, now(CHECKPOINT_TEMPLATE))
    assert isinstance(answer, dict) and answer.get("ok"), f"gov links could not judge the planted tree (exit {code}): {stderr}"
    unknown = [f"{f.get('ids')} line {f.get('line')}" for f in answer["result"]["findings"]
               if f.get("path") == rel and f.get("code") == "UNKNOWN_ID"]
    assert not unknown, f"gov links gives UNKNOWN_ID on the checkpoint template at {rel}: {unknown}"
