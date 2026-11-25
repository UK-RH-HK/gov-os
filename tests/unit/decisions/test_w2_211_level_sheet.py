"""W2-211 regression: the level rule, the below-level judgement and the sheet's parser (the acceptance cases are the KPIs)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.decisions import level, sheet  # noqa: E402


@pytest.mark.parametrize("facts, want", [
    ({"touches": ["own-ticket"], "reversible": "yes", "inside": "worktree"}, "P3"),
    ({"touches": ["own-ticket"], "reversible": "no", "inside": "worktree"}, "P2"),
    ({"touches": ["own-ticket"], "reversible": "no", "inside": "repository"}, "P1"),
    ({"touches": ["kernel-text"], "reversible": "yes", "inside": "worktree"}, "P2"),
    ({"touches": ["own-ticket", "spec"], "reversible": "yes", "inside": "worktree"}, "P1"),
    ({"touches": ["own-ticket"], "reversible": "yes", "inside": "worktree", "rounds": 3}, "P1"),
    ({"touches": ["own-ticket"], "reversible": "yes", "inside": "worktree", "rounds": 2}, "P3"),
    ({"touches": ["own-ticket"], "reversible": "yes", "inside": "worktree", "emergency": "yes"}, "emergency"),
])
def test_level_is_the_highest_of_touches_and_place(facts, want):
    assert level.compute_level(facts)["level"] == want


def test_an_unknown_touches_word_is_refused_by_name():
    with pytest.raises(level.LevelError) as raised:
        level.compute_level({"touches": ["bogus"], "reversible": "yes", "inside": "worktree"})
    assert raised.value.code == "LEVEL_FACT_INVALID" and "bogus" in raised.value.message


@pytest.mark.parametrize("decider, verdict", [("owner (chat, 2026-11-24)", "pass"), ("CTO", "fail"), ("lead", "fail"),
                                              (None, "fail")])
def test_a_p1_record_passes_only_when_the_owner_decided(decider, verdict):
    facts = {"touches": ["spec"], "reversible": "yes", "inside": "worktree"}
    assert level.judge_entry(facts, decider)["verdict"] == verdict


def test_a_cto_passes_p2_and_a_lead_does_not_and_no_facts_is_unstated():
    p2 = {"touches": ["shared-code"], "reversible": "yes", "inside": "worktree"}
    assert level.judge_entry(p2, "orchestrator")["verdict"] == "pass"
    assert level.judge_entry(p2, "lead")["verdict"] == "fail"
    assert level.judge_entry({}, "lead")["verdict"] == "unstated"


def test_the_shipped_table_is_the_code_default():
    import yaml

    table = yaml.safe_load((REPO / "governance/project/escalation.yaml").read_text())
    assert level.load_table(REPO) == {**level.DEFAULT_TABLE, **table, "place": {"yes": table["place"]["yes"], "no": table["place"]["no"]}}
    assert table == level.DEFAULT_TABLE


def test_a_note_keeps_its_characters_and_loses_only_its_line_breaks():
    note = 'a | "b" é 😀\nsecond\r\nthird'
    text = sheet.write_sheet("B-1", "sha256:ab", "2026-11-24T00:00:00Z", [("DP-1", "a", note), ("DP-2", "skip", None)])
    assert len(text.splitlines()) == 8
    parsed = sheet.parse_sheet(text)
    assert parsed["lines"][0]["note"] == 'a | "b" é 😀 second third' and parsed["lines"][1]["letter"] == "skip"


@pytest.mark.parametrize("wrap", ["fence", "quote", "crlf", "around"])
def test_the_parser_reads_a_sheet_the_chat_wrapped(wrap):
    text = sheet.write_sheet("B-1", "sha256:ab", "2026-11-24T00:00:00Z", [("DP-1", "b", 'say "hi"'), ("DP-2", "skip", None)])
    wrapped = {"fence": f"```\n{text}```\n", "quote": "".join(f"> {row}\n" for row in text.splitlines()),
               "crlf": text.replace("\n", "\r\n"), "around": f"Here you go:\n{text}\nThanks.\n"}[wrap]
    assert sheet.parse_sheet(wrapped)["lines"] == sheet.parse_sheet(text)["lines"]


@pytest.mark.parametrize("bad", ["GOV-ANSWERS 1\nbatch: B\nhash: h\nanswered: a\ncount: 2\nDP-1: a\nEND\n",
                                 "GOV-ANSWERS 2\nbatch: B\n", "no block here"])
def test_a_count_that_does_not_match_or_no_block_is_refused(bad):
    with pytest.raises(sheet.SheetError):
        sheet.parse_sheet(bad)
