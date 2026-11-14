"""W2-94, KPI success 4 (S4) and failure 3 (F3) -- every gold source exists at the copy's recorded commit and holds the
answer.

S4: "Every gold source exists at the copy's recorded commit and holds the answer Verify: a counts-only script, written by
the ticket's independent test designer and run by the CTO with `--sets-root` ..., prints only counts and ids: for each
question, its gold source exists at the copy's recorded commit and holds the answer ("n of n hold"); a planted source
that is absent or does not hold its answer is reported by id". F3: "A gold source that does not hold its answer.
Verify: the S4 script on a planted source that does not hold its answer reports that question's id as failing".

The stand-in copy's first commit is the recorded commit; its scaffold commit and working tree hold files that are absent
or different at the first commit, and the script must judge the first commit only. The planted question q07 is broken
one way at a time; the other nineteen must still hold.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_94_cases as c  # noqa: E402
import w2_94_support as s  # noqa: E402


def test_s4_a_good_set_holds_n_of_n(tmp_path):
    world = s.build(tmp_path, count=20)
    run = s.run_check(world)
    assert run.returncode == 0, run.describe()
    assert run.lines == ["20 questions (10 visible, 10 hidden); draw ok; release ok", "20 of 20 hold"], run.describe()


@pytest.mark.parametrize("name", sorted(c.S4_BREAKS))
def test_s4_a_source_that_is_absent_or_does_not_hold_its_answer_is_reported_by_id(tmp_path, name):
    build_kwargs, case, rc = c.S4_BREAKS[name]
    world = s.build(tmp_path, count=20, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    assert "19 of 20 hold" in run.lines, f"{name}\n{run.describe()}"
    assert s.question_failures(run) == dict(expected), f"{name}: exactly q07 fails, by its reason\n{run.describe()}"
    assert run.lines[0] == "20 questions (10 visible, 10 hidden); draw ok; release ok", "only the sources failed"


@pytest.mark.parametrize("name", sorted(c.S4_HOLDS))
def test_s4_a_hyphen_digit_word_that_is_not_id_shaped_and_a_path_by_its_segments_hold(tmp_path, name):
    """W2-94 GOLD (i) and (ii): ``level-2`` is not an identifier token; an id-shaped word the span has holds; a path
    token whose segments occur in order in the spans holds (the same case in `S4_BREAKS` fails when out of order)."""
    build_kwargs, case, rc = c.S4_HOLDS[name]
    world = s.build(tmp_path, count=20, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, f"{name}\n{run.describe()}"
    assert run.lines == ["20 questions (10 visible, 10 hidden); draw ok; release ok", "20 of 20 hold"], f"{name}\n{run.describe()}"
    assert s.question_failures(run) == {}, f"{name}\n{run.describe()}"


@pytest.mark.parametrize("name", sorted(c.NONEXISTENT_BREAKS))
def test_s4_a_nonexistent_question_whose_name_exists_or_whose_source_is_bad_is_reported(tmp_path, name):
    build_kwargs, case, rc = c.NONEXISTENT_BREAKS[name]
    world = s.build(tmp_path, count=20, **build_kwargs)
    expected, kwargs = case(world)
    run = s.run_check(world, **kwargs)
    assert run.returncode == rc, run.describe()
    assert "19 of 20 hold" in run.lines, f"{name}\n{run.describe()}"
    assert s.question_failures(run) == dict(expected), f"{name}\n{run.describe()}"


def test_s4_the_nonexistent_questions_hold_when_their_names_are_nowhere_at_the_commit(tmp_path):
    """The asked names occur in the scaffold commit and in the working tree, never at the recorded commit: they hold."""
    text = f"NAMES = ['{s.ghost(19)}', '{s.ghost(20)}']\n"
    world = s.build(tmp_path, count=20, extra_worktree={f"docs/{s.WORD}later.md": text})
    assert s.ghost(19) in (world.copy / f"docs/{s.WORD}later.md").read_text(encoding="utf-8")
    run = s.run_check(world)
    assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", run.describe()


def test_s4_a_nonexistent_question_may_point_at_an_existing_file(tmp_path):
    world = s.build(tmp_path, count=20)
    world.edit("q19", lambda d: d.update(question=f"Where is `{s.ghost(19)}` defined in `{s.LOCATOR}`?"))
    run = s.run_check(world)
    assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", run.describe()


def test_s4_an_alternatives_entry_with_one_good_alternative_holds(tmp_path):
    for order in ("bad-first", "good-first"):
        world = s.build(tmp_path / order, count=20)
        good = {"path": s.source_path(7), "heading": f"## {s.WORD}heading07", "lines": [3, 5]}
        bad = {"path": f"docs/{s.WORD}nowhere.md", "lines": [1, 2]}
        world.edit("q07", lambda d: d.update(sources=[[bad, good] if order == "bad-first" else [good, bad]]))
        run = s.run_check(world)
        assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", f"{order}\n{run.describe()}"


def test_s4_two_sources_that_together_hold_the_answer_hold(tmp_path):
    """The answer's two identifiers are on lines 4 and 5: each source alone lacks one, the union holds both."""
    world = s.build(tmp_path, count=20)
    world.edit("q07", lambda d: d.update(sources=[{"path": s.source_path(7), "lines": [4, 4]},
                                                  {"path": s.source_path(7), "lines": [5, 5]}]))
    run = s.run_check(world)
    assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", run.describe()


def test_s4_a_prose_answer_that_the_span_states_holds(tmp_path):
    world = s.build(tmp_path, count=20)
    world.edit("q07", lambda d: d.update(gold_answer="The routine reads the configuration value and returns the "
                                                     "result to its caller."))
    run = s.run_check(world)
    assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", run.describe()


def test_s4_an_answer_that_names_its_own_source_file_holds(tmp_path):
    """A span does not repeat the name of the file it is in: the source's path, whole or by its file name, is held."""
    for named in (s.source_path(7), f"{s.WORD}src07.md"):
        world = s.build(tmp_path / named.replace("/", "_"), count=20)
        world.edit("q07", lambda d: d.update(gold_answer=f"It is in `{named}`: `{s.WORD}func07_run` returns {s.WORD}ans07."))
        run = s.run_check(world)
        assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", f"{named}\n{run.describe()}"


def test_s4_the_source_is_judged_at_the_recorded_commit_not_the_scaffold_commit(tmp_path):
    """docs/...changed.md has 3 lines at the recorded commit and 10 (with the answer's word) in the scaffold commit and
    the working tree: lines [1, 3] and an answer in the first 3 lines hold; the later text does not count."""
    world = s.build(tmp_path, count=20)
    world.edit("q07", lambda d: (d["sources"][0].update(path=s.CHANGED, lines=[1, 3], heading=None),
                                 d.update(gold_answer="It is `beta`.")))
    run = s.run_check(world)
    assert run.returncode == 0 and run.lines[1] == "20 of 20 hold", run.describe()
    assert "later line 4" in (world.copy / s.CHANGED).read_text(encoding="utf-8"), "the planted copy's file changed"


def test_s4_several_broken_questions_are_each_reported_by_id(tmp_path):
    world = s.build(tmp_path, count=20)
    world.source("q03", path=f"docs/{s.WORD}nowhere.md")
    world.source("q07", lines=[3, 99])
    world.source("q12", heading="## no such heading")
    run = s.run_check(world)
    assert run.returncode == 1 and "17 of 20 hold" in run.lines, run.describe()
    assert s.question_failures(run) == {"q03": "SOURCE_PATH_ABSENT", "q07": "SPAN_OUT_OF_FILE",
                                        "q12": "HEADING_NOT_FOUND"}, run.describe()


def test_s4_a_question_in_the_development_half_is_checked_like_one_in_the_measured_half(tmp_path):
    world = s.build(tmp_path, count=20)
    visible_id, hidden_id = world.visible_ids[0], world.hidden_ids[0]
    world.source(visible_id, lines=[3, 99])
    world.source(hidden_id, lines=[3, 99])
    run = s.run_check(world)
    assert s.question_failures(run) == {visible_id: "SPAN_OUT_OF_FILE", hidden_id: "SPAN_OUT_OF_FILE"}, run.describe()


def test_s4_the_check_writes_nothing(tmp_path):
    """Read only: the sets root, the copy (its git folder too) and the home are unchanged after a run, a failing one
    included."""
    world = s.build(tmp_path, count=20)
    world.source("q07", lines=[3, 99])
    before = world.snapshot()
    run = s.run_check(world)
    assert run.returncode == 1, run.describe()
    after = world.snapshot()
    assert after == before, sorted(set(after.items()) ^ set(before.items()))[:6]
