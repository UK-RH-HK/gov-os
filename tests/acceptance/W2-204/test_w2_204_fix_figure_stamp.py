"""The fix under the closed ticket DAEO-ma4q (W2-204), F15 of fixes-015a: the memory measure's figure carries its stamp
(audit 4 A-9; DEC-1225 (4)); the lines are named ``success-17`` to ``success-19`` in the README's map.

* S17: ``FIGURES.json`` stamps ``release``, ``commit``, ``reader_model``, ``grader_models``, ``forbidden_rule`` and
  ``questions_with_forbidden`` (a count), and the printed verdict says the stamp too.
* S18: ``declare`` never refuses a set with no ``forbidden`` list: one NOTICE line, exit 0, ``forbidden_lists`` counted.
* S19: a figure without the stamp is never compared with one that has it; the comparison reports the two are not
  comparable and names the missing stamp (the one comparison the measure has: the standing set's check against fitting).

Builds on D5 (``e2/d5-memaudit-strict``): a question may carry a ``forbidden`` list and the rule is ``strict``. The
planted run is the folder's own (public interfaces: ``gov memaudit`` as child processes and the files they leave); the
comparison case calls the one function that compares, ``gov.memaudit.standing.drift``, in process.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

import w2_204_stages as ST
import w2_204_support as K
from w2_204_support import HALVES, HIDDEN, VISIBLE

STAMP = ("release", "commit", "reader_model", "grader_models", "forbidden_rule", "questions_with_forbidden")
LISTED = ("q05", "q06", "q07")                      # the questions the planted run gives a forbidden list
FORBIDDEN_PATH = K.SPARE_CODE[0]


def _with_lists(specs: list[dict], listed=LISTED) -> list[dict]:
    for spec in specs:
        if spec["id"] in listed:
            spec["extra"] = {"forbidden": [FORBIDDEN_PATH]}
    return specs


def _stamped_run(folder: Path) -> dict:
    world = K.build(folder / "w")
    calls = ST._start(world)
    for audit, _ in HALVES:
        world.write_half(audit, _with_lists(K.clean_specs()))
        world.write_notes(audit)
    world.install_plans(control_hits=17)
    ST._transcripts(world, leak=False)
    calls["final"] = world.fresh()
    return {"calls": calls}


ST.BUILDS["figure-stamp"] = _stamped_run


def figures_of(run, audit: str) -> dict:
    path = run.world.run_dir(audit) / "FIGURES.json"
    assert path.is_file(), f"no FIGURES.json for {audit}: {run['final']!r}"
    return json.loads(path.read_text(encoding="utf-8"))


# -- S17 ------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("audit", [a for a, _ in HALVES])
def test_s17_figures_json_carries_the_six_stamp_keys(stage, audit):
    run = stage("figure-stamp")
    assert run["final"].code == 0, run["final"]
    figures = figures_of(run, audit)
    missing = [key for key in STAMP if key not in figures]
    assert not missing, f"FIGURES.json lacks the stamp key(s) {missing}"


@pytest.mark.parametrize("audit", [a for a, _ in HALVES])
def test_s17_the_stamp_values_are_the_runs_own(stage, audit):
    run = stage("figure-stamp")
    figures = figures_of(run, audit)
    assert isinstance(figures.get("release"), str) and re.fullmatch(r"\d+\.\d+\.\d+\S*", figures["release"]), \
        f"release is not a version: {figures.get('release')!r}"
    assert figures.get("commit") == run.world.audit_commit, "commit is not the audit commit"
    assert isinstance(figures.get("reader_model"), str) and figures["reader_model"], figures.get("reader_model")
    graders = figures.get("grader_models")
    assert isinstance(graders, list) and graders and all(isinstance(g, str) and g for g in graders), graders
    assert figures.get("forbidden_rule") == "strict"
    count = figures.get("questions_with_forbidden")
    assert type(count) is int and count == len(LISTED), f"questions_with_forbidden {count!r}, planted {len(LISTED)}"


def test_s17_the_printed_verdict_says_the_stamp(stage):
    run = stage("figure-stamp")
    figures = figures_of(run, HIDDEN)
    text = run["final"].text
    for value in (figures["release"], figures["commit"][:12], figures["reader_model"], "strict"):
        assert value in text, f"the printed verdict does not say {value!r}"
    assert re.search(r"questions_with_forbidden\D{0,3}%d\b" % len(LISTED), text) or \
        re.search(r"forbidden\D{0,40}\b%d\b" % len(LISTED), text), "the printed verdict does not count the lists"


# -- S18 ------------------------------------------------------------------------------------------------------------
def _declare(world, specs):
    world.prepare(HIDDEN, specs)
    return world.step("declare", HIDDEN)


NOTICE = ("NOTICE DC-FORBIDDEN-NONE: no question carries a forbidden list; "
          "the strict rule grades as the lenient rule would")


def _declaration(world) -> dict:
    path = world.run_dir(HIDDEN) / "DECLARATION.json"
    assert path.is_file(), "no DECLARATION.json"
    return json.loads(path.read_text(encoding="utf-8"))


def test_s18_declare_notices_and_goes_on_when_no_question_carries_a_list(world):
    run = _declare(world, K.clean_specs())
    assert run.code == 0, run
    assert run.lines.count(NOTICE) == 1, f"the notice is not exactly one line: {run.text!r}"
    assert "DC-FORBIDDEN:" not in run.text and "DC-FORBIDDEN " not in run.text.replace(NOTICE, ""), run.text
    assert (world.run_dir(HIDDEN) / "USED").exists(), "a noticed declaration wrote no USED"
    assert _declaration(world).get("forbidden_lists") == 0


def test_s18_declare_goes_on_when_one_question_carries_a_list(world):
    run = _declare(world, _with_lists(K.clean_specs(), ("q05",)))
    assert run.code == 0 and "DC-FORBIDDEN" not in run.text, run
    assert not [x for x in run.lines if "NOTICE" in x], f"a notice with a list present: {run.text!r}"
    assert (world.run_dir(HIDDEN) / "USED").exists()
    assert _declaration(world).get("forbidden_lists") == 1


# -- S19 ------------------------------------------------------------------------------------------------------------
def _plant_standing(state: Path, stamped: bool) -> None:
    rows = [{"event": "declared", "set": "memory-standing-20261101"}]
    (state / "STANDING.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    stamp = {"release": "0.1.5", "commit": "a" * 40, "reader_model": "m", "grader_models": ["m"],
             "forbidden_rule": "strict", "questions_with_forbidden": 3} if stamped else {}
    lines = [{"kind": "standing", "set": "memory-standing-20261101", "measured": True, "passes": True, "pct": 80.0,
              **stamp} for _ in range(4)]   # S = 80; a fresh F of 95 would be STALE (15 apart) if compared
    (state / "HISTORY.jsonl").write_text("".join(json.dumps(r) + "\n" for r in lines), encoding="utf-8")


def _fresh_figure(stamped: bool) -> dict:
    figure = {"n": 40, "verdict": {"right": 38}}
    if stamped:
        figure.update(release="0.1.5", commit="b" * 40, reader_model="m", grader_models=["m"],
                      forbidden_rule="strict", questions_with_forbidden=3)
    return figure


@pytest.mark.parametrize("lines_stamped, fresh_stamped", [(True, False), (False, True)])
def test_s19_a_figure_without_the_stamp_is_not_compared_with_one_that_has_it(tmp_path, lines_stamped, fresh_stamped):
    from gov.memaudit import standing

    _plant_standing(tmp_path, lines_stamped)
    result = standing.drift(tmp_path, _fresh_figure(fresh_stamped))
    assert result.get("comparable") is False, f"the two were compared: {result!r}"
    assert result.get("word") is None, f"a drift word was given across the stamp: {result!r}"
    named = result.get("missing")
    assert isinstance(named, list) and named and set(named) <= set(STAMP), f"no missing stamp named: {result!r}"
    assert not [x for x in standing.history(tmp_path) if x.get("kind") == "drift"], "a drift line was written"
    assert standing.live(tmp_path) is not None, "the set was retired by a comparison that should not be made"


def test_s19_guard_two_stamped_figures_are_compared_as_before(tmp_path):
    from gov.memaudit import standing

    _plant_standing(tmp_path, True)
    result = standing.drift(tmp_path, _fresh_figure(True))
    assert result["word"] == "STANDING_STALE" and result.get("comparable", True) is not False, result
