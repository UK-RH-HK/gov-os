"""KPI success 3: definitions, references, callers, impact and dead code on the dev tiers [CAP-12.a].

Each dev tier is cloned into a temporary directory, adopted (a path map that
classes all of it as governance memory, the template's gitleaks configuration)
and indexed through the wrapper. The questions of ``questions.yaml`` are asked,
one symbol per language is renamed in the clone, the clone is indexed again and
the questions are asked again with the new names. The tiers themselves are
never written to.

The question set is the test designer's (README, package DP-1): the set of the
S0b2 C1 baseline is not in this repository.
"""

from __future__ import annotations

import pytest

import w1_16_support as support

pytestmark = pytest.mark.local_only

QUESTIONS = support.load_questions()["tiers"]
TIERS = list(QUESTIONS)
PHASES = ("before", "after")
LANGUAGES = ("rust", "python", "typescript")
THRESHOLD = 0.60
TIER = pytest.mark.parametrize("tier", TIERS)
PHASE = pytest.mark.parametrize("phase", PHASES)


def _scores(tier_runs, phase):
    """``(tier, symbol, language, kind, hit)`` for every callers and impact question of both tiers."""
    rows = []
    for tier in TIERS:
        run = tier_runs(tier)
        for entry in run.spec["symbols"]:
            symbol = run.name(phase, entry["symbol"])
            for kind in ("callers", "impact"):
                answer = support.entries(run.answer(phase, kind, symbol), f"{kind}({symbol})", run.repo.root)
                hit = support.hit_at(answer, run.pairs(phase, entry[kind]))
                rows.append((tier, symbol, entry["language"], kind, hit))
    return rows


# --------------------------------------------------------------------------
# The premise: the expected answers are what the source of the tiers says
# --------------------------------------------------------------------------

@TIER
def test_the_expected_answers_stand_in_the_source_of_the_tier(tier, tmp_path):
    """Passes before W1-16: it reads a clone of the tier, not the wrapper. No expected answer comes from the tool."""
    clone = support.clone_tier(tier, tmp_path / "tier")
    if clone is None:
        pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
    spec = QUESTIONS[tier]
    wrong = []
    for entry in spec["symbols"]:
        for kind in ("callers", "impact"):
            for path, name in entry[kind]:
                if not support.holds_word(clone, path, name):
                    wrong.append(f"{kind} of {entry['symbol']}: {name} is not in {path}")
        for path, _ in entry["callers"]:
            if not support.holds_word(clone, path, entry["symbol"]):
                wrong.append(f"callers of {entry['symbol']}: {path} does not use it")
    for kind in ("definitions", "references"):
        for entry in spec[kind]:
            wrong += [f"{kind} of {entry['symbol']}: not in {path}" for path in entry["paths"]
                      if not support.holds_word(clone, path, entry["symbol"])]
    sources = [rel for rel in support.tracked(clone) if rel.endswith(support.CODE_SUFFIXES)]
    for path, name in spec["dead"]:
        users = [rel for rel in sources if support.holds_word(clone, rel, name)]
        if users != [path]:
            wrong.append(f"dead {name}: stands in {users}, expected only {path}")
    for path, name in spec["live"]:
        if not support.holds_word(clone, path, name):
            wrong.append(f"live {name}: not in {path}")
    for old, new in spec["renames"].items():
        if any(support.holds_word(clone, rel, new) for rel in sources):
            wrong.append(f"rename {old}: the new name {new} already stands in the tier")
    assert not wrong, "\n".join(wrong)


def test_the_question_set_covers_the_three_languages():
    """Passes before W1-16: callers and impact are asked in Rust, Python and TypeScript, and each has a rename."""
    asked = {entry["language"] for spec in QUESTIONS.values() for entry in spec["symbols"]}
    assert asked == set(LANGUAGES)
    renamed = {entry["language"] for spec in QUESTIONS.values() for entry in spec["symbols"]
               if entry["symbol"] in spec["renames"]}
    assert renamed == set(LANGUAGES), f"no rename in: {sorted(set(LANGUAGES) - renamed)}"


# --------------------------------------------------------------------------
# Callers and impact: hit@5 >= 60 %, before and after the rename
# --------------------------------------------------------------------------

@PHASE
def test_callers_and_impact_hit_at_five_is_at_least_sixty_percent(tier_runs, phase):
    rows = _scores(tier_runs, phase)
    hits = [row for row in rows if row[4]]
    missed = [f"{tier}: {kind}({symbol})" for tier, symbol, _, kind, hit in rows if not hit]
    assert len(hits) / len(rows) >= THRESHOLD, \
        f"{phase} the rename: hit@5 is {len(hits)} of {len(rows)}; missed: {missed}"


@PHASE
@pytest.mark.parametrize("kind", ["callers", "impact"])
def test_callers_and_impact_are_answered_in_every_language(tier_runs, phase, kind):
    """Across Rust, Python and TypeScript: no language is carried by the other two."""
    rows = [row for row in _scores(tier_runs, phase) if row[3] == kind]
    without = [language for language in LANGUAGES
               if not any(hit for _, _, asked, _, hit in rows if asked == language)]
    assert not without, f"{phase} the rename: no {kind} question is answered in {without}"


@TIER
def test_a_renamed_symbol_is_answered_under_its_new_name_only(tier_runs, tier):
    """After the rename the index follows: the new name has the callers the old one had, the old name has none."""
    run = tier_runs(tier)
    for entry in run.spec["symbols"]:
        old = entry["symbol"]
        if old not in run.spec["renames"]:
            continue
        new = run.spec["renames"][old]
        answer = support.entries(run.answer("after", "callers", new), f"callers({new})", run.repo.root)
        assert support.hit_at(answer, run.pairs("after", entry["callers"])), \
            f"{tier}: callers({new}) does not reach an expected caller after the rename: {answer[:5]}"
        assert run.answer("after", "callers", old) == [], f"{tier}: {old} still has callers after the rename"
        assert run.answer("after", "definitions", old) == [], f"{tier}: {old} is still defined after the rename"


# --------------------------------------------------------------------------
# Definitions, references and dead code
# --------------------------------------------------------------------------

@TIER
@PHASE
def test_definitions_name_every_file_that_defines_the_symbol(tier_runs, tier, phase):
    run = tier_runs(tier)
    wrong = []
    for entry in run.spec["definitions"]:
        symbol = run.name(phase, entry["symbol"])
        answer = support.entries(run.answer(phase, "definitions", symbol), f"definitions({symbol})", run.repo.root)
        missing = [path for path in entry["paths"] if (path, symbol) not in answer]
        if missing:
            wrong.append(f"definitions({symbol}) lacks {missing}; answered {answer[:8]}")
    assert not wrong, f"{tier}, {phase} the rename:\n" + "\n".join(wrong)


@TIER
@PHASE
def test_references_name_every_file_with_a_call_site(tier_runs, tier, phase):
    """CAP-12 acceptance: references to a function return every call site, before and after a rename."""
    run = tier_runs(tier)
    wrong = []
    for entry in run.spec["references"]:
        symbol = run.name(phase, entry["symbol"])
        answer = support.entries(run.answer(phase, "references", symbol), f"references({symbol})", run.repo.root)
        paths = {path for path, _ in answer}
        missing = [path for path in entry["paths"] if path not in paths]
        if missing:
            wrong.append(f"references({symbol}) lacks {missing}; answered {sorted(paths)[:8]}")
    assert not wrong, f"{tier}, {phase} the rename:\n" + "\n".join(wrong)


@TIER
@PHASE
def test_dead_code_names_the_unreferenced_functions_and_no_live_one(tier_runs, tier, phase):
    run = tier_runs(tier)
    answer = support.entries(run.answer(phase, "dead_code"), "dead_code()", run.repo.root)
    missing = [pair for pair in run.pairs(phase, run.spec["dead"]) if pair not in answer]
    assert not missing, f"{tier}, {phase} the rename: dead code lacks {missing}"
    alive = [pair for pair in run.pairs(phase, run.spec["live"]) if pair in answer]
    assert not alive, f"{tier}, {phase} the rename: functions that are called are reported dead: {alive}"
