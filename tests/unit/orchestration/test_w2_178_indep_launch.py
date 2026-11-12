"""W2-178: the engineer's unit tests for the auditor's copy of a set (indep_launch.py; S1 and F1-F3).

W2-170's Interface (DEC-1101 (2)): the auditor's copy of a set leaves out the files under its `hidden/dropped/` folder;
the writer's (round 2) and the checker's copies are unchanged. Every set here is planted under tmp_path (W2-149's
World: its own sets root, HOME, repository and stub `claude`); no real sets root, hidden half, run folder or session.
"""
import os

import pytest

from test_w2_149_indep_launch import World, indep_launch, SET, assert_counts, nothing_built, tree_hash

FILES = {
    "q01.yaml": "question one\n",
    "sub/q03.yaml": "question three\n",
    "dropped/q02.yaml": "dropped two\n",
    "dropped/x/q04.yaml": "dropped four, nested\n",
    "dropped/x/y/q05.yaml": "dropped five, deeper\n",
    "dropped.yaml": "a name that only starts like the folder\n",
    "sub/dropped/q06.yaml": "a dropped folder below another folder is not hidden/dropped/\n",
}
ALL = sorted(FILES)
LEFT_OUT = sorted(r for r in FILES if r.startswith("dropped/"))
KEPT = sorted(r for r in FILES if r not in LEFT_OUT)


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


def rels(plan):
    """The destinations of a plan under input/set, as set-relative paths (the plan's sources checked as they go)."""
    out = []
    for src, dst in plan:
        if dst.startswith("input/set/"):
            out.append(dst[len("input/set/"):])
    return sorted(out)


def plan(w, kind, rnd=None, audit=None, set_name=SET):
    return indep_launch.plan_inputs(kind, rnd, str(w.sets), set_name, audit)


def plant_misses(w, audit="e0"):
    (w.sets / "runs" / audit).mkdir(parents=True, exist_ok=True)
    (w.sets / "runs" / audit / "misses.jsonl").write_text('{"id": "m1"}\n')


def planted_copy_in_wall(w, counts):
    return tree_hash(w.wall(counts) / "input" / "set")


# -- S1: the plan --------------------------------------------------------------------------------------------------
def test_the_auditors_plan_leaves_out_every_file_under_hidden_dropped_at_any_depth(w):
    w.plant_set(FILES)
    plant_misses(w)
    got = rels(plan(w, "auditor", audit="e0"))
    assert got == KEPT
    assert not [r for r in got if r.split("/")[0] == "dropped"]


def test_the_auditors_other_files_are_the_sources_as_before_and_misses_still_staged(w):
    hidden = w.plant_set(FILES)
    plant_misses(w)
    pl = plan(w, "auditor", audit="e0")
    for r in KEPT:
        assert (str(hidden / r), os.path.join("input", "set", r)) in pl
    assert (str(w.sets / "runs" / "e0" / "misses.jsonl"), "input/misses.jsonl") in pl
    assert len(pl) == len(KEPT) + 1


def test_a_dropped_folder_below_another_folder_and_a_name_that_only_starts_with_dropped_stay(w):
    w.plant_set(FILES)
    plant_misses(w)
    got = rels(plan(w, "auditor", audit="e0"))
    assert "sub/dropped/q06.yaml" in got and "dropped.yaml" in got and "sub/q03.yaml" in got


def test_a_plain_file_named_dropped_is_not_the_folder_and_stays(w):
    w.plant_set({"q01.yaml": "one\n", "dropped": "a file, not a folder\n"})
    plant_misses(w)
    assert rels(plan(w, "auditor", audit="e0")) == ["dropped", "q01.yaml"]


def test_the_checkers_plan_and_the_writers_round_two_plan_keep_the_dropped_files(w):
    w.plant_set(FILES)
    (w.sets / "fixtures" / "evaluation" / SET / "XCHECK-r1.md").write_text("notes\n")
    assert rels(plan(w, "checker")) == ALL
    assert rels(plan(w, "writer", rnd=2)) == ALL
    assert indep_launch.plain_files(str(w.sets / "fixtures" / "evaluation" / SET / "hidden")) == ALL


def test_a_set_with_no_dropped_folder_stages_exactly_as_before(w):
    plain = {k: v for k, v in FILES.items() if not k.startswith("dropped/")}
    w.plant_set(plain)
    plant_misses(w)
    assert rels(plan(w, "auditor", audit="e0")) == sorted(plain) == rels(plan(w, "checker"))


# -- the refusals keep their meaning -------------------------------------------------------------------------------
def test_an_auditors_set_that_is_only_dropped_files_refuses_10_input_as_an_empty_set_does(w):
    w.plant_set({"dropped/q02.yaml": "only a dropped one\n", "dropped/x/q04.yaml": "and another\n"})
    plant_misses(w)
    with pytest.raises(indep_launch.Refuse) as e:
        plan(w, "auditor", audit="e0")
    assert (e.value.code, e.value.word) == (10, "input")
    assert rels(plan(w, "checker")) == ["dropped/q02.yaml", "dropped/x/q04.yaml"]  # not empty for the others


def test_a_link_inside_the_dropped_folder_still_refuses_10_input_for_the_auditor(w):
    hidden = w.plant_set(FILES)
    plant_misses(w)
    os.symlink(str(hidden / "q01.yaml"), str(hidden / "dropped" / "link.yaml"))
    with pytest.raises(indep_launch.Refuse) as e:
        plan(w, "auditor", audit="e0")
    assert (e.value.code, e.value.word) == (10, "input")


def test_a_linked_folder_inside_the_dropped_folder_still_refuses_10_input_for_the_auditor(w):
    hidden = w.plant_set(FILES)
    plant_misses(w)
    os.symlink(str(hidden / "sub"), str(hidden / "dropped" / "folder-link"))
    with pytest.raises(indep_launch.Refuse) as e:
        plan(w, "auditor", audit="e0")
    assert (e.value.code, e.value.word) == (10, "input")


# -- S1 and F1 end to end: the walls ---------------------------------------------------------------------------------
def test_the_auditors_wall_copy_has_no_dropped_file_and_every_other_file_byte_identical(w):
    hidden = w.plant_set(FILES)
    plant_misses(w)
    rc, counts, p = w.launch("auditor", audit="e0", seed=3, dry=True)
    assert rc == 0, (counts, p.stderr)
    assert_counts(counts, 0, "dry")
    copy = w.wall(counts) / "input" / "set"
    want = {r: open(hidden / r, "rb").read() for r in KEPT}
    got = {os.path.relpath(os.path.join(d, n), copy): open(os.path.join(d, n), "rb").read()
           for d, _ds, ns in os.walk(copy) for n in ns}
    assert got == want
    assert not (copy / "dropped").exists()
    assert sorted(os.listdir(w.wall(counts) / "input")) == ["misses.jsonl", "selection.json", "set"]


def test_the_checkers_and_the_writers_round_two_wall_copies_hold_every_file_dropped_ones_too(w):
    hidden = w.plant_set(FILES)
    (hidden.parent / "XCHECK-r1.md").write_text("notes\n")
    want = {r: open(hidden / r, "rb").read() for r in ALL}
    for kind, kw in (("checker", {}), ("writer", {"rnd": 2})):
        rc, counts, p = w.launch(kind, seed=3, dry=True, **kw)
        assert rc == 0, (kind, counts, p.stderr)
        copy = w.wall(counts) / "input" / "set"
        got = {os.path.relpath(os.path.join(d, n), copy): open(os.path.join(d, n), "rb").read()
               for d, _ds, ns in os.walk(copy) for n in ns}
        assert got == want, kind
        assert open(copy / "dropped" / "x" / "y" / "q05.yaml").read() == FILES["dropped/x/y/q05.yaml"]


def test_the_auditors_set_of_only_dropped_files_builds_nothing_10(w):
    w.plant_set({"dropped/q02.yaml": "only a dropped one\n"})
    plant_misses(w)
    before = tree_hash(w.sets)
    rc, counts, _ = w.launch("auditor", audit="e0", seed=3, dry=True)
    assert rc == 10, counts
    assert_counts(counts, 10, "refused")
    assert counts["reason"] == "input"
    assert tree_hash(w.sets) == before
    nothing_built(w)
