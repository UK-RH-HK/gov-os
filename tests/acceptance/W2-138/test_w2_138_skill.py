"""S5: the retrieval skill's step 5 gains one line: compare each item's sha256 with the same lines in your own tree;
if they differ, read the store's text with ``git show <commit>:<path>``, and never cite the store's line numbers as
your tree's (README).

A text check of ``template/governance/kernel/skills/retrieval/SKILL.md`` (the generated ``.claude`` copy follows at
the lift's re-pin ACT, not here): step 5 is the text from the line starting ``5.`` to the line starting ``6.``,
read case-insensitively with its white space folded. And the skills check (``gov.check.skill_validator``) still
finds nothing in the file.
"""

from __future__ import annotations

import re

import w2_138_support as support

SKILL = support.REPO / "template/governance/kernel/skills/retrieval/SKILL.md"


def _step_5() -> str:
    text = SKILL.read_text(encoding="utf-8")
    found = re.search(r"^5\.(.*?)^6\.", text, re.S | re.M)
    assert found, f"premise: {SKILL} has a step 5 followed by a step 6"
    return " ".join(found.group(1).split()).lower()


def test_s5_step_5_tells_the_worker_to_compare_each_item_s_sha256_with_its_own_tree():
    step = _step_5()
    assert "sha256" in step and "own tree" in step, (
        f"step 5 does not tell the worker to compare an item's sha256 with the same lines in its own tree: {step!r}")
    assert "same lines" in step, f"step 5 does not say the comparison is with the same lines: {step!r}"


def test_s5_step_5_names_result_store_commit_and_git_show_of_the_store_s_text():
    step = _step_5()
    assert "result.store.commit" in step, f"step 5 does not name result.store.commit: {step!r}"
    assert re.search(r"git show\s+\S*commit\S*:\S*path", step), (
        f"step 5 does not say to read the store's text with `git show <commit>:<path>`: {step!r}")


def test_s5_step_5_says_never_cite_the_store_s_line_numbers_as_your_tree_s():
    step = _step_5()
    assert re.search(r"never\b[^.]*\bcite\b[^.]*line numbers", step), (
        f"step 5 does not say never to cite the store's line numbers as your tree's: {step!r}")


def test_s5_guard_step_5_keeps_its_checks_of_the_bundle():
    step = _step_5()
    for phrase in ("stopping reason", "`id`", "`sha256`", "superseded"):
        assert phrase in step, f"step 5 lost {phrase!r}: {step!r}"


def test_s5_guard_the_skills_check_finds_nothing_in_the_retrieval_skill():
    from gov.check.skill_validator import validate_file

    assert validate_file(SKILL) == [], f"the skills check's findings in {SKILL}"
