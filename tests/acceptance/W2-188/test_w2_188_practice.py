"""W2-188, success 3 (and F3's section 9 half) -- `docs/research/W2-88-memory-practice.md`.

Places: section 3's `Consistency is the proof` bullet; section 5 item 6 (its last `The practice:` stretch); section 6
step 6; the new `## 9. The standing set (DEC-1179)` section at the end of the file. Phrases are looked for on the text
lower-cased, whitespace collapsed, backticks and bold marks dropped, except `A2` (a word, any case) and DEC-1179 (4)'s
text, which is compared whole (whitespace collapsed, case and markdown kept).
"""

from __future__ import annotations

import re

import w2_188_support as support


def _flat_section_9():
    return support.flat(support.section_9())


# ---------------------------------------------------------------- the three re-worded places


def test_s3_section_3s_confirmation_bullet_names_the_standing_set():
    regions = support.bullet_region(support.practice_section(3), r"Consistency is the proof")
    assert regions, "section 3 has no bullet that opens `Consistency is the proof`"
    assert "standing set" in support.flat(regions[0]), "section 3's confirmation bullet does not name the standing set"


def test_s3_section_5_item_6s_practice_lines_name_the_standing_set_and_that_it_never_chooses_or_judges_a_fix():
    regions = support.bullet_region(support.practice_section(5), r"Agreement between two tuned halves")
    assert regions, "section 5 has no item that opens `Agreement between two tuned halves`"
    body = support.flat(regions[0])
    at = body.rfind("the practice:")
    assert at >= 0, "section 5 item 6 has no `The practice:` line"
    practice = body[at:]
    lacking = [p for p in ("standing set", "never chooses or judges a fix") if p not in practice]
    assert not lacking, f"section 5 item 6's practice lines (after its last `The practice:`) lack: {lacking}"


def test_s3_section_6_still_passes_the_steps_matcher():
    """Guard (holds on the base): W2-88a's `check_steps` on section 6."""
    problems = support.check_steps(support.practice_section(6))
    assert not problems, f"check_steps on section 6: {problems}"


def test_s3_section_6_step_6_names_the_standing_set():
    stretch = support.stretch_between(support.practice_section(6), 6, 7)
    assert stretch is not None, "section 6 has no line starting `6.` followed by a line starting `7.`"
    assert "standing set" in support.flat(stretch), "section 6 step 6 does not name the standing set"


# ---------------------------------------------------------------- section 9


def test_s3_section_9_is_the_last_section_and_has_its_heading_once():
    text = support.read(support.PRACTICE_REL)
    found = support.heading_section(text, support.SECTION_9_TITLE, levels=(2,))
    assert len(found) == 1, f"`## 9. The standing set (DEC-1179)` stands {len(found)} times, not once"
    headings = [line for line in text.splitlines() if re.match(r"^## ", line)]
    assert headings[-1].strip() == "## 9. The standing set (DEC-1179)", f"the last `##` heading is {headings[-1]!r}"
    assert headings[-2].startswith("## 8."), f"section 9 does not follow section 8: it follows {headings[-2]!r}"


def test_s3_section_9_says_counts_only_and_that_the_set_never_chooses_or_judges_a_fix():
    body = _flat_section_9()
    lacking = [p for p in ("counts only", "never chooses or judges a fix") if p not in body]
    assert not lacking, f"section 9 lacks: {lacking}"


def test_s3_section_9_gives_the_method_the_reader_the_whole_bundle_search_again_once_and_a2():
    section = support.section_9()
    body = support.flat(section)
    lacking = []
    if "reader" not in body:
        lacking.append("the reader")
    if not re.search(r"\bwhole\b[^.;]{0,40}\bbundle\b|\bbundle\b[^.;]{0,40}\bwhole\b", body):
        lacking.append("the whole bundle")
    if not re.search(r"\bsearch\w*\s+again\s+once\b", body):
        lacking.append("search again once")
    if not re.search(r"\bA2\b", section, re.I):
        lacking.append("A2")
    assert not lacking, f"section 9's method lacks: {lacking}"


def test_s3_section_9_gives_the_e2_figures_115_and_128_of_138_and_e3s_114_against_84():
    body = _flat_section_9()
    lacking = []
    if not re.search(r"\be2\b", body):
        lacking.append("E2")
    for figure in ("115", "128", "138"):
        if not re.search(rf"\b{figure}\b", body):
            lacking.append(figure)
    if not re.search(r"\be3\b", body):
        lacking.append("E3")
    if not re.search(r"\b114\b.{0,80}?\b84\b", body, re.S):
        lacking.append("114 ... against ... 84 (within 80 characters)")
    assert not lacking, f"section 9's figures lack: {lacking}"


def test_s3_section_9_gives_the_bar_ceil_0_95_n():
    body = _flat_section_9()
    assert re.search(r"ceil\s*\(\s*0\.95\s*[x×*]?\s*n\s*\)|⌈\s*0\.95\s*[x×*]?\s*n\s*⌉", body), (
        "section 9 does not give the bar as `ceil(0.95 n)`")


def test_s3_section_9_says_a_stale_question_is_dropped_by_count():
    pieces = support.units(support.section_9())
    assert any(re.search(r"\bstale\w*\b", u) and re.search(r"\bcount\w*\b", u) for u in pieces), (
        "no sentence of section 9 holds both `stale` and `count`")


def test_s3_section_9_gives_the_monthly_check_with_its_two_5_point_rules():
    """Reading: the blocks (a paragraph or a list item with its sub-items) that name `fresh set` or `month`, leaving out
    the block of DEC-1179 (4) (it has a 5-point rule of its own), hold the word `month`, the words `fresh set` and at
    least two 5-point statements (`within 5 points`, `5 points below`, `5-point`, `five points`)."""
    blocks = [b for b in support.blocks(support.section_9()) if "below 95 %" not in support.flat(b)]
    chosen = [b for b in blocks if "fresh set" in support.flat(b) or "month" in support.flat(b)]
    joined = support.flat("\n\n".join(chosen))
    lacking = [p for p in ("fresh set", "month") if p not in joined]
    assert not lacking, f"section 9's monthly check lacks: {lacking}"
    count = support.five_point_count("\n\n".join(chosen))
    assert count >= 2, f"section 9's monthly check states {count} 5-point rule(s), not two"


def test_s3_section_9_says_w2_88_s10s_second_reranking_model_stays_forbidden_and_the_reader_is_not_one():
    body = _flat_section_9()
    problems = []
    found = list(re.finditer(r"\bsecond rerank\w*", body))
    if not found:
        problems.append("section 9 does not name the second reranking model")
    else:
        near = [body[max(0, m.start() - 200):m.end() + 200] for m in found]
        if not any("forbidden" in w and re.search(r"\bs10\b", w) and "w2-88" in w for w in near):
            problems.append("no sentence says W2-88 S10's second reranking model stays forbidden "
                            "(`W2-88`, `S10`, `second reranking model` and `forbidden` together)")
        if not any(re.search(r"\breader\b[^.;]{0,60}\b(?:is not|isn't|never|not)\b[^.;]{0,30}"
                             r"\b(?:one|a second|second|a rerank\w*)\b", w) for w in near):
            problems.append("section 9 does not say the reader is not one")
    assert not problems, "; ".join(problems)


def test_s3_the_register_records_dec_1179_4_as_pinned():
    """Guard (holds now): the register's text starts as expected, so an edit to it is noticed."""
    text = support.dec_1179_item_4()
    assert text.startswith(support.DEC_1179_4_START), f"DEC-1179 (4) in the register starts: {text[:80]!r}"
    assert text.endswith("."), f"DEC-1179 (4) in the register ends: {text[-40:]!r}"


def test_s3_section_9_holds_dec_1179_4_word_for_word():
    """The register's DEC-1179 (4), from `**Below 95 %:**` to its closing `.`, read at test time, stands in section 9
    (whitespace collapsed on both sides: the record wraps its lines; case and markdown kept)."""
    expected = support.collapse(support.dec_1179_item_4())
    assert expected in support.collapse(support.section_9()), (
        "section 9 does not hold DEC-1179 (4) word for word; expected: " + expected[:160] + "...")


# ---------------------------------------------------------------- F3 (section 9's half)


def test_f3_section_9_never_says_the_standing_set_may_choose_judge_adopt_or_reject_a_fix():
    bad = support.permission_violations(support.section_9())
    assert not bad, f"section 9 lets the standing set choose, judge, adopt or reject a fix: {bad}"


def test_f3_section_9_never_calls_the_reader_a_second_reranking_model():
    bad = support.second_reranker_misuse(support.section_9())
    assert not bad, f"section 9 names a second reranking model without refusing it: {bad}"
