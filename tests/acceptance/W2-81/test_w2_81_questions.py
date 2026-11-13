"""The visible question half: at least 10 per repository, of several kinds, resolving to real evidence for any seed."""

from __future__ import annotations

from collections import Counter

import w2_81_build as build
import w2_81_questions as questions
from w2_81_words import DEFAULT_SEED

EXPECTED = (*build.SHAPES, build.CLEAN)


def _planted_sources(manifest):
    """The planted sources no answer may cite: stale specs, superseded plans, dead files under current names."""
    out = set()
    for entry in manifest["planted"]:
        ev = entry["evidence"]
        if entry["kind"] == "stale-spec":
            out.add(ev["stale"])
        elif entry["kind"] == "superseded-plan":
            out.add(ev["plan"])
        elif entry["kind"] == "misleading-name" and not ev["live"]:
            out.add(entry["paths"][0])
    return out


def _check(ground):
    for name in EXPECTED:
        built = ground[name]
        asked = questions.resolve(questions.load_set(questions.VISIBLE / f"{name}.yaml"), built.manifest, built.root,
                                  "visible")
        assert len(asked) >= 10, f"{name}: {len(asked)} questions"
        assert len({q.category for q in asked}) >= 5, f"{name}: {Counter(q.category for q in asked)}"
        planted = _planted_sources(built.manifest)
        for q in asked:
            for path, line, holds in q.sources:
                text = (built.root / path).read_text(encoding="utf-8").splitlines()
                assert holds in text[line - 1], f"{q.id}: {path} line {line}"
                assert path not in planted, f"{q.id}: a gold source is a planted source"
            assert set(q.forbidden) <= planted, f"{q.id}: a forbidden citation is not a planted source"
        cited = {p for q in asked for p in q.forbidden}
        stale_or_superseded = {e["evidence"].get("stale") or e["evidence"].get("plan")
                               for e in built.manifest["planted"] if e["kind"] in ("stale-spec", "superseded-plan")}
        assert stale_or_superseded <= cited, f"{name}: a stale spec or superseded plan no question forbids"


def test_the_visible_half_holds_a_set_per_repository_and_nothing_else():
    assert sorted(questions.sets_in(questions.VISIBLE)) == sorted(EXPECTED)
    ids = [q["id"] for s in questions.sets_in(questions.VISIBLE).values() for q in s["questions"]]
    assert len(ids) == len(set(ids)), "a question id is given twice"


def test_the_questions_resolve_at_the_default_seed(ground):
    assert ground["python-app"].manifest["seed"] == DEFAULT_SEED
    _check(ground)


def test_the_questions_resolve_at_another_seed(run_folder):
    other = build.build_all(run_folder, DEFAULT_SEED + 7)
    _check(other)
    build.remove(run_folder)


def test_a_question_whose_source_is_not_in_the_repository_is_refused_naming_its_id_only(ground):
    built = ground["rust-workspace"]
    broken = {"form": questions.FORM, "repository": "rust-workspace", "questions": [
        {"id": "rust-workspace-x01", "category": "what-value", "question": "What is the secret plan of {product}?",
         "gold_answer": "nothing", "sources": [{"path": "Cargo.toml", "holds": "no such line anywhere"}]}]}
    try:
        questions.resolve(broken, built.manifest, built.root, "hidden")
    except questions.QuestionError as refused:
        assert "rust-workspace-x01" in str(refused) and "secret plan" not in str(refused)
    else:
        raise AssertionError("a question whose gold source is not there was resolved")
    unknown = {**broken, "questions": [{**broken["questions"][0], "sources": [{"path": "{nothing}", "holds": "x"}]}]}
    try:
        questions.resolve(unknown, built.manifest, built.root, "hidden")
    except questions.QuestionError as refused:
        assert "rust-workspace-x01" in str(refused)
    else:
        raise AssertionError("a template naming no fact was resolved")
