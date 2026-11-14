"""W2-188, success 1 and success 2 (and F3's step-6 half) -- A9's step 6 and the paragraph after step 7, in the three
copies of the adopt skill.

"Step 6's stretch" is the text from the line starting `6.` to the line starting `7.` inside A9's section. Phrases are
looked for on the stretch lower-cased, whitespace collapsed, backticks and bold marks dropped (a faithful rendering may
bold a word), so `95 %` is the literal with one space.
"""

from __future__ import annotations

import re

import w2_188_support as support


def _each_copy_missing(phrases):
    """``{rel: [phrases missing from step 6's stretch]}`` for the copies that lack any."""
    out = {}
    for rel in support.ALL_REL:
        body = support.flat(support.step6_stretch(rel))
        lacking = [phrase for phrase in phrases if phrase not in body]
        if lacking:
            out[rel] = lacking
    return out


# ---------------------------------------------------------------- S1


def test_s1_step_6_names_the_standing_set_judged_every_week_on_the_same_questions():
    missing = _each_copy_missing(["standing set", "every week", "same questions"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_s1_step_6_gives_the_bar_95_percent_and_says_counts_only():
    missing = _each_copy_missing(["95 %", "counts only"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_s1_step_6_says_it_never_chooses_or_judges_a_fix():
    missing = _each_copy_missing(["never chooses or judges a fix"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_s1_step_6_says_a_fresh_set_each_month_checks_for_fitting_and_a_fitted_set_is_replaced():
    missing = _each_copy_missing(["fresh set", "month", "fitted", "replaced"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_s1_step_6_cites_dec_1179():
    missing = _each_copy_missing(["dec-1179"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_s1_step_6_says_a_miss_is_never_re_run_in_the_same_week_nor_re_scored():
    """Reading: the ticket's S1 says it in words but its Verify list does not name it, so each form is read loosely:
    `same week`, a re-run (`re-run`, `rerun`, `run again`) and a re-score (`re-scored`, `rescored`, `scored again`)."""
    problems = {}
    for rel in support.ALL_REL:
        body = support.flat(support.step6_stretch(rel))
        lacking = []
        if "same week" not in body:
            lacking.append("same week")
        if not re.search(r"\bre-?run\w*|\brun again\b|\bran again\b", body):
            lacking.append("a re-run (re-run / rerun / run again)")
        if not re.search(r"\bre-?scor\w*|\bscored again\b|\bscore again\b|\bscoring again\b", body):
            lacking.append("a re-score (re-scored / rescored / scored again)")
        if lacking:
            problems[rel] = lacking
    assert not problems, f"step 6 does not say a miss is never re-run in the same week nor re-scored: {problems}"


def test_s1_the_steps_matcher_finds_no_problem_in_a9_of_each_copy():
    """Guard (holds on the base): W2-88a's `check_steps` on A9's region of each copy (step 6 keeps `declare`, `measure`,
    `the verdict set`, `once`; the seven steps stay in order)."""
    problems = {}
    for rel in support.ALL_REL:
        found = support.check_steps(support.a9_text(support.read(rel), rel))
        if found:
            problems[rel] = found
    assert not problems, f"check_steps on A9's region: {problems}"


def test_s1_a9_still_points_to_the_practice_record_in_each_copy():
    """Guard (holds on the base): W2-88a's `check_pointer` on A9's region of each copy."""
    problems = {rel: support.check_pointer(support.a9_text(support.read(rel), rel)) for rel in support.ALL_REL}
    problems = {rel: found for rel, found in problems.items() if found}
    assert not problems, f"check_pointer on A9's region: {problems}"


def test_s1_step_6_keeps_the_declare_anchor_and_stays_clear_of_step_7s_anchor():
    """Guard (holds on the base; I2): step 6 opens with `Declare`, no word starting `declar` stands in steps 1 to 5, and
    step 7's anchor (`record...every|each|all...method`) does not occur in step 6."""
    problems = []
    for rel in support.ALL_REL:
        a9 = support.a9_text(support.read(rel), rel)
        stretch = support.step6_stretch(rel)
        if not re.match(r"^\s*6\.\s+\W*declare\b", stretch, re.I):
            problems.append(f"{rel}: step 6 does not open with `Declare`")
        earlier = support.stretch_between(a9, 1, 6) or ""
        if re.search(r"\bdeclar\w*", support.flat(earlier)):
            problems.append(f"{rel}: a word starting `declar` stands in steps 1 to 5")
        step_7_anchor = support.a88.STEPS[6][2]
        if re.search(step_7_anchor, support.flat(stretch), re.S):
            problems.append(f"{rel}: step 7's anchor occurs inside step 6")
    assert not problems, "; ".join(problems)


# ---------------------------------------------------------------- S2


def test_s2_one_paragraph_stands_between_step_7_and_the_verify_heading_in_each_copy():
    """One non-empty paragraph, a blank line before it (after step 7) and a blank line after it (before the heading)."""
    problems = []
    for rel in support.ALL_REL:
        lines = support.paragraph_after_step_7(support.read(rel))
        if lines is None:
            problems.append(f"{rel}: no step 7 line followed by the `## Verify clauses for adopted tickets` heading")
            continue
        text = "\n".join(lines).strip()
        if not text:
            problems.append(f"{rel}: nothing stands between step 7 and the Verify heading")
            continue
        if len(re.split(r"\n\s*\n", text)) != 1:
            problems.append(f"{rel}: more than one paragraph stands between step 7 and the Verify heading")
        if lines[0].strip() or lines[-1].strip():
            problems.append(f"{rel}: the paragraph is not set off by a blank line on each side")
    assert not problems, "; ".join(problems)


def test_s2_the_paragraph_holds_cron_act_operator_never_installs_and_95_percent():
    problems = {}
    for rel in support.ALL_REL:
        lines = support.paragraph_after_step_7(support.read(rel))
        raw = "\n".join(lines or [])
        body = support.flat(raw)
        lacking = []
        if "cron" not in body:
            lacking.append("cron")
        if not re.search(r"\bACTs?\b", raw):
            lacking.append("ACT (capitals, as a word)")
        if "operator" not in body:
            lacking.append("operator")
        if "never installs" not in body and "never installed" not in body:
            lacking.append("never installs / never installed")
        if "95 %" not in body:
            lacking.append("95 %")
        if lacking:
            problems[rel] = lacking
    assert not problems, f"the paragraph after step 7 lacks, by copy: {problems}"


def test_s2_the_paragraph_points_to_section_9_of_the_practice_record():
    """I3: the paragraph says a fall below 95 % is handled as the practice record's section 9 states."""
    problems = []
    for rel in support.ALL_REL:
        body = support.flat("\n".join(support.paragraph_after_step_7(support.read(rel)) or []))
        if not re.search(r"(?:\bsection|§)\s*9\b", body) or "practice record" not in body:
            problems.append(rel)
    assert not problems, f"no pointer to `the practice record's section 9` in the paragraph of: {problems}"


# ---------------------------------------------------------------- F3 (step 6's half)


def test_f3_step_6_holds_never_chooses_or_judges_a_fix_and_counts_only():
    missing = _each_copy_missing(["never chooses or judges a fix", "counts only"])
    assert not missing, f"step 6 lacks these phrases, by copy: {missing}"


def test_f3_step_6_never_says_the_standing_set_may_choose_judge_adopt_or_reject_a_fix():
    """Guard (holds on the base): see the README's reading; a statement is a violation when it is not negated."""
    problems = {}
    for rel in support.ALL_REL:
        bad = support.permission_violations(support.step6_stretch(rel))
        if bad:
            problems[rel] = bad
    assert not problems, f"step 6 lets the standing set choose, judge, adopt or reject a fix: {problems}"


def test_f3_step_6_never_calls_the_reader_a_second_reranking_model():
    """Guard (holds on the base): a mention of a second reranking model must be negated or called forbidden."""
    problems = {}
    for rel in support.ALL_REL:
        bad = support.second_reranker_misuse(support.step6_stretch(rel))
        if bad:
            problems[rel] = bad
    assert not problems, f"step 6 names a second reranking model without refusing it: {problems}"
