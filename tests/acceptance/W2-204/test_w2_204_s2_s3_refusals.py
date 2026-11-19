"""S2 and S3: no silent default, and the file's failure lines. A repository without the file, or with a file that has
one fault, is refused at every step with exit 1 and one line; nothing is written and no search or model call starts."""

from __future__ import annotations

import re

import pytest

import w2_204_support as K
from w2_204_support import HIDDEN, VISIBLE, W171

HOLDS_WORD, NAME_WORD = "zorblaxquint", "Vexmoorquay"   # planted in the faulty files' own text
FREE_TAG = "20261119c"   # fresh: a tag whose halves' names are not in the sets root (else FR-NAME could come first)


def _delivered(world: K.World) -> None:
    """Both halves delivered and noted: there is something a step could read, write or leak."""
    world.make_step_store()
    for audit in (VISIBLE, HIDDEN):
        world.write_half(audit, K.clean_specs())
        world.write_notes(audit)
    world.install_plans()


def _without_the_file(world: K.World) -> str:
    W171.git(world.repo, "rm", "-q", K.CONFIG_REL, home=world.home)
    W171.git(world.repo, "commit", "-q", "-m", "no memory-audit.yaml", home=world.home)
    return W171.git(world.repo, "rev-parse", "HEAD", home=world.home).strip()


def _nothing_happened(world: K.World, before: dict) -> None:
    assert W171.snapshot(world.sets) == before, "the sets root changed"
    assert world.gov_calls() == [] and world.claude_calls() == [], "a search or a model call started"
    assert world.rebuilds() == [], "a store was built"
    assert not list(world.base.rglob("brief.md")), "a brief was written"


@pytest.mark.parametrize("entry", ["module", "cli"])
@pytest.mark.parametrize("step", K.STEPS)
def test_s2_a_repository_without_the_file_is_refused_at_every_step(world, step, entry):
    _delivered(world)
    commit = _without_the_file(world)
    before = W171.snapshot(world.sets)
    run = world.step(step, HIDDEN, entry=entry, commit=commit, tag=FREE_TAG)
    assert run.code == 1 and K.MISSING_LINE in run.lines, run
    assert [x for x in run.lines if x.startswith("MA-CONFIG")] == [K.MISSING_LINE], run
    _nothing_happened(world, before)


# -- S3: one fault each ---------------------------------------------------------------------------------------------
def _doc(**over) -> dict:
    doc = K.config_doc(repository=f"{NAME_WORD} Harbour", **over)
    doc["categories"][0]["about"] = f"a decision of the {HOLDS_WORD} board"
    return doc


def _categories(change) -> list:
    rows = _doc()["categories"]
    change(rows)
    return rows


def _row(key: str, **extra) -> list:
    rows = _doc()[key]
    rows[0].update(extra)
    return rows


FAULTS = {
    "quota": (_doc(categories=_categories(lambda rows: rows[0].update(count=7))), r"MA-CONFIG-QUOTA sum 41 of 40"),
    "domain-empty": (_doc(domains=[*_doc()["domains"], {"name": "ghost-wharf", "paths": ["nowhere/**"]}]),
                     r"MA-CONFIG-DOMAIN-EMPTY ghost-wharf"),
    "key-top": (_doc(colour="red"), r"MA-CONFIG-KEY colour"),
    "key-domain": (_doc(domains=_row("domains", colour="red")), r"MA-CONFIG-KEY domains\S*colour"),
    "key-subsystem": (_doc(subsystems=_row("subsystems", colour="red")), r"MA-CONFIG-KEY subsystems\S*colour"),
    "key-category": (_doc(categories=_row("categories", colour="red")), r"MA-CONFIG-KEY categories\S*colour"),
    "key-control": (_doc(control={**_doc()["control"], "colour": "red"}), r"MA-CONFIG-KEY control\.colour"),
    "form-yaml": (f"version: 1\nrepository: {NAME_WORD}\ncategories: [{HOLDS_WORD} unclosed\n", r"MA-CONFIG-FORM \S*: \S.*"),
    "form-type": (_doc(half_size="forty"), r"MA-CONFIG-FORM half_size: \S.*"),
    "form-missing": ({k: v for k, v in _doc().items() if k != "categories"}, r"MA-CONFIG-FORM categories: \S.*"),
    "form-apart": (_doc(categories=_categories(lambda rows: rows[-1].update(name="ghost-id"))),
                   r"MA-CONFIG-FORM categories\S*: \S.*"),
    "form-duplicate": (_doc(domains=[*_doc()["domains"], {"name": "decisions", "paths": ["records/tasks/**"]}]),
                       r"MA-CONFIG-FORM domains\S*: \S.*"),
    "form-baseline": (_doc(control={**_doc()["control"], "baseline": "soon"}), r"MA-CONFIG-FORM control\.baseline: \S.*"),
}


def _text(fault) -> str:
    return fault if isinstance(fault, str) else K.config_text(fault)


def _one_line(world: K.World, run: K.Call, pattern: str) -> None:
    """Exit 1 and one ``MA-CONFIG`` line of the stated form; no line holds a question, a path under the sets root or
    the file's own text."""
    named = [x for x in run.lines if x.startswith("MA-CONFIG")]
    assert run.code == 1 and len(named) == 1 and re.fullmatch(pattern, named[0]), (pattern, run)
    for word in (HOLDS_WORD, NAME_WORD, *K.planted_words(), str(world.sets) + "/"):
        assert word not in run.text, (word, run)


@pytest.mark.parametrize("name", sorted(FAULTS))
def test_s3_check_names_the_one_fault_of_the_repository_s_own_file(world, name):
    """The file of the working tree (no ``--commit``): each fault's line, exit 1, nothing of the file's text."""
    fault, pattern = FAULTS[name]
    (world.repo / K.CONFIG_REL).write_text(_text(fault), encoding="utf-8")
    before = W171.snapshot(world.sets)
    run = world.run("cli", "check", "--repo", world.repo)
    _one_line(world, run, pattern)
    assert W171.snapshot(world.sets) == before


@pytest.mark.parametrize("name", sorted(FAULTS))
def test_s3_a_step_names_the_same_fault_and_writes_nothing(world, name, tmp_path):
    """The trial form (``GOV_MEMAUDIT_CONFIG``): ``preflight`` on a delivered half refuses with the fault's line."""
    fault, pattern = FAULTS[name]
    trial = tmp_path / "trial.yaml"
    trial.write_text(_text(fault), encoding="utf-8")
    _delivered(world)
    before = W171.snapshot(world.sets)
    run = world.step("preflight", HIDDEN, entry="module", env={"GOV_MEMAUDIT_CONFIG": str(trial)})
    _one_line(world, run, pattern)
    _nothing_happened(world, before)


@pytest.mark.parametrize("entry", ["module", "cli"])
@pytest.mark.parametrize("step", K.STEPS)
def test_s3_every_step_refuses_a_faulty_file_with_exit_1(world, step, entry, tmp_path):
    fault, pattern = FAULTS["quota"]
    trial = tmp_path / "trial.yaml"
    trial.write_text(_text(fault), encoding="utf-8")
    _delivered(world)
    before = W171.snapshot(world.sets)
    run = world.step(step, HIDDEN, entry=entry, env={"GOV_MEMAUDIT_CONFIG": str(trial)}, tag=FREE_TAG)
    _one_line(world, run, pattern)
    _nothing_happened(world, before)


def test_s3_only_the_first_fault_is_named(world):
    doc = _doc(colour="red", control={**_doc()["control"], "baseline": "soon"})
    doc["categories"][0]["count"] = 7
    (world.repo / K.CONFIG_REL).write_text(K.config_text(doc), encoding="utf-8")
    run = world.run("cli", "check", "--repo", world.repo)
    assert run.code == 1 and len([x for x in run.lines if x.startswith("MA-CONFIG")]) == 1, run
    assert len(run.lines) == 1, run


@pytest.mark.parametrize("entry", ["module", "cli"])
def test_s3_a_file_without_a_fault_is_ok_and_check_prints_its_counts(world, entry, tmp_path):
    run = world.step("check", entry=entry)
    assert (run.code, run.lines) == (0, ["CONFIG ok half 40 categories 12 domains 5 subsystems 3 control second-control"]), run
    trial = tmp_path / "trial.yaml"
    trial.write_text(K.config_text(K.config_doc(control="none")), encoding="utf-8")
    run = world.step("check", entry=entry, env={"GOV_MEMAUDIT_CONFIG": str(trial)})
    assert (run.code, run.lines) == (0, ["CONFIG ok half 40 categories 12 domains 5 subsystems 3 control none"]), run
