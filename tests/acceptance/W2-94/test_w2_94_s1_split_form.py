"""W2-94, KPI success 1 (S1) -- the set's count, its fields, the recorded draw, the two halves and the release.

S1: "Between 10 and 20 questions ... after writing, a recorded seeded draw, stratified by category, splits the set into a
development half (`hidden/visible/`) and a hidden half ... the owner's release step (`release_visible.sh`) then copies
the development half into `visible/` Verify: a planted stand-in set: a count outside 10 to 20 is refused; the record
holds the seed and the draw; the two halves each hold half (within one) with each category in both halves; the release
step copies exactly the development half into `visible/` and refuses a second release".

Driven through ``fixtures/evaluation/examin/check_gold.py`` on planted stand-ins (``w2_94_support``). The release
step's refusal of a second release is the owner's operator's record, not tested here (README).
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_cases as c  # noqa: E402
import w2_94_support as s  # noqa: E402


@pytest.mark.parametrize("count,visible,hidden", [(10, 5, 5), (20, 10, 10), (14, 7, 7), (13, 6, 7)],
                         ids=["ten", "twenty", "fourteen", "thirteen-odd"])
@pytest.mark.parametrize("seed", [20260900, 20260901], ids=["even-seed", "odd-seed"])
def test_s1_a_good_set_is_accepted_with_its_counts_printed(tmp_path, count, visible, hidden, seed):
    world = s.build(tmp_path, count=count, seed=seed)
    run = s.run_check(world)
    assert run.returncode == 0, run.describe()
    assert run.lines == [f"{count} questions ({visible} visible, {hidden} hidden); draw ok; release ok",
                         f"{count} of {count} hold"], run.describe()


def test_s1_before_the_release_step_the_set_is_accepted_with_the_release_pending(tmp_path):
    world = s.build(tmp_path, count=10, release=False)
    run = s.run_check(world)
    assert run.returncode == 0, run.describe()
    assert run.lines[0] == "10 questions (5 visible, 5 hidden); draw ok; release pending", run.describe()
    assert not world.released_dir.exists() and not world.record.exists()


@pytest.mark.parametrize("count,code", [(9, "COUNT_BELOW_MIN"), (21, "COUNT_ABOVE_MAX"), (4, "COUNT_BELOW_MIN")])
def test_s1_a_count_outside_ten_to_twenty_is_refused(tmp_path, count, code):
    world = s.build(tmp_path, count=count)
    run = s.run_check(world)
    assert run.returncode == 2, run.describe()
    assert s.has(run, "REFUSED", code), run.describe()
    assert not any("hold" in line for line in run.lines), "a refused set is not counted as holding"


@pytest.mark.parametrize("name", sorted(c.S1_FORM))
def test_s1_a_question_with_a_missing_or_bad_field_is_refused(tmp_path, name):
    build_kwargs, case, rc = c.S1_FORM[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    for words in expected:
        assert s.has(run, *words), f"{name}: no line begins {' '.join(words)}\n{run.describe()}"
    assert not any("hold" in line for line in run.lines), "a refused set is not counted as holding"


@pytest.mark.parametrize("name", sorted(c.S1_DRAW))
def test_s1_a_draw_or_halves_that_break_the_split_are_reported(tmp_path, name):
    build_kwargs, case, rc = c.S1_DRAW[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    expected, kwargs = case(world)
    world.rerelease()   # so that the release is not what fails: only the draw or the halves are broken
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    for words in expected:
        assert s.has(run, *words), f"{name}: no line begins FAIL {' '.join(words)}\n{run.describe()}"
    assert "draw FAIL" in run.lines[0] or expected[0][0] == "set", run.describe()
    assert "release ok" in run.lines[0], run.describe()
    assert s.question_failures(run) == {}, "the source checks of the questions still hold"


@pytest.mark.parametrize("name", sorted(c.S1_DRAW_LITERAL))
def test_s1_a_draw_in_the_literal_seed_form_with_a_break_is_reported_by_its_code(tmp_path, name):
    """W2-94 GOLD (iii): the literal ``SEED+k=`` form keeps every rule of the digit form; ``SEED+K=``, ``SEED+<k>=`` and
    any other spelling is a bad line."""
    build_kwargs, case, rc = c.S1_DRAW_LITERAL[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    expected, kwargs = case(world)
    world.rerelease()
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    for words in expected:
        assert s.has(run, *words), f"{name}: no line begins FAIL {' '.join(words)}\n{run.describe()}"
    assert "draw FAIL" in run.lines[0] and "release ok" in run.lines[0], run.describe()
    assert s.question_failures(run) == {}, "the source checks of the questions still hold"


@pytest.mark.parametrize("name", sorted(c.S1_DRAW_FORMS))
def test_s1_a_draw_written_in_the_literal_seed_form_or_mixed_is_accepted(tmp_path, name):
    build_kwargs, case, rc = c.S1_DRAW_FORMS[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    case(world)
    assert "SEED+k=" in world.draw.read_text(encoding="utf-8"), "the planted draw holds a literal line"
    run = s.run_check(world)
    assert run.returncode == rc, run.describe()
    assert run.lines == ["10 questions (5 visible, 5 hidden); draw ok; release ok", "10 of 10 hold"], run.describe()


@pytest.mark.parametrize("count,visible,hidden", [(10, 5, 5), (20, 10, 10), (13, 6, 7)], ids=["ten", "twenty", "thirteen-odd"])
@pytest.mark.parametrize("seed", [20260900, 20260901], ids=["even-seed", "odd-seed"])
def test_s1_a_set_whose_draw_is_wholly_literal_is_accepted_for_either_seed_parity(tmp_path, count, visible, hidden, seed):
    world = s.build(tmp_path, count=count, seed=seed)
    c._literal_all(world)
    assert all("SEED+k=" in line for line in world.draw_lines()), world.draw_lines()
    run = s.run_check(world)
    assert run.returncode == 0, run.describe()
    assert run.lines == [f"{count} questions ({visible} visible, {hidden} hidden); draw ok; release ok",
                         f"{count} of {count} hold"], run.describe()


def test_s1_a_category_in_one_half_only_is_reported_though_the_halves_are_equal(tmp_path):
    world = s.build(tmp_path, count=10)
    c._category_in_one_half(world)
    world.rerelease()
    run = s.run_check(world)
    assert s.has(run, "draw", "CATEGORY_IN_ONE_HALF"), run.describe()
    assert not s.has(run, "draw", "HALVES_UNBALANCED"), f"the halves are 5 and 5\n{run.describe()}"
    assert run.lines[0].startswith("10 questions (5 visible, 5 hidden)"), run.describe()


def test_s1_halves_that_differ_by_one_are_accepted_and_by_two_reported(tmp_path):
    world = s.build(tmp_path, count=13)
    assert world.visible_ids and len(world.hidden_ids) - len(world.visible_ids) == 1
    assert s.run_check(world).returncode == 0
    world.move_half(world.visible_ids[0])
    world.rerelease()
    run = s.run_check(world)
    assert run.returncode == 1 and s.has(run, "draw", "HALVES_UNBALANCED"), run.describe()


@pytest.mark.parametrize("name", sorted(c.S1_RELEASE))
def test_s1_a_visible_folder_that_is_not_the_development_half_is_reported(tmp_path, name):
    build_kwargs, case, rc = c.S1_RELEASE[name]
    world = s.build(tmp_path, count=10, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    for words in expected:
        assert s.has(run, *words), f"{name}: no line begins FAIL {' '.join(words)}\n{run.describe()}"
    assert "release FAIL" in run.lines[0], run.describe()
    assert "draw ok" in run.lines[0], run.describe()


def test_s1_a_released_folder_that_is_the_development_half_byte_for_byte_is_accepted(tmp_path):
    world = s.build(tmp_path, count=10)
    names = sorted(p.name for p in world.released_dir.iterdir())
    assert names == sorted(p.name for p in world.dev_dir.iterdir()), "the planted release copies the development half"
    assert not any(p.name in names for p in world.hidden_dir.glob("q*.yaml")), "no measured-half file is released"
    run = s.run_check(world)
    assert run.returncode == 0 and "release ok" in run.lines[0], run.describe()


def test_s1_the_draw_must_name_the_halves_by_the_briefs_rule(tmp_path):
    """The record holds the seed and the draw: with an even SEED+k the first question of the pair is the visible one."""
    world = s.build(tmp_path, count=10, seed=20260900)
    lines = world.draw_lines()
    assert lines[0].split()[3] == "odd" and lines[1].split()[3] == "even", lines   # SEED+1 odd, SEED+2 even
    assert lines[0].endswith("visible=q02 hidden=q01") and lines[1].endswith("visible=q03 hidden=q04"), lines
    assert s.run_check(world).returncode == 0
