"""S2: the AS record lists every spec (path, title, wave, status), each built, partly built or not built with evidence,
the tickets done or not by wave, specs with no code, code with no spec, and each gap as one question with a place for the
answer. The cases read the committed record's front matter (the keys the lead's brief states), never its body."""

from __future__ import annotations

import re

import pytest

import w2_192_support as support

base = support.base
ALPHA, BETA, OMEGA, GAMMA_PY = support.ALPHA, support.BETA, support.OMEGA, support.GAMMA_PY


def front(audited):
    support.audit_ok(audited)
    return support.as_front(audited.root)


def spec_entry(audited, path):
    found = support.by_path(front(audited).get("specs") or [])
    assert path in found, f"the record's specs hold no entry for {path}: {sorted(found)}"
    return found[path]


def test_s2_the_specs_found_are_exactly_the_planted_ones(audited):
    found = support.by_path(front(audited).get("specs") or [])
    assert set(found) == set(support.SPECS), f"specs found: {sorted(found)}"
    paths = [item.get("path") for item in front(audited)["specs"]]
    assert len(paths) == len(set(paths)), f"a spec is listed twice: {paths}"


@pytest.mark.parametrize("path", sorted(support.SPECS), ids=lambda p: p.rsplit("/", 1)[1])
def test_s2_each_spec_carries_its_title_wave_and_status_as_it_states_them(audited, path):
    _, title, wave, status, _ = support.SPECS[path]
    entry = spec_entry(audited, path)
    assert entry.get("title") == title, f"{path}: title {entry.get('title')!r}"
    assert str(entry.get("wave")) == str(wave), f"{path}: wave {entry.get('wave')!r}"
    assert entry.get("status") == status, f"{path}: status {entry.get('status')!r}"


@pytest.mark.parametrize("path", sorted(support.BUILT), ids=lambda p: f"{p.rsplit('/', 1)[1]}-{support.BUILT[p].replace(' ', '-')}")
def test_s2_each_spec_is_classed_built_partly_built_or_not_built(audited, path):
    entry = spec_entry(audited, path)
    assert entry.get("built") == support.BUILT[path], f"{path}: built is {entry.get('built')!r}"


def test_s2_the_built_spec_has_code_test_and_commit_evidence(audited):
    evidence = spec_entry(audited, ALPHA).get("evidence")
    assert isinstance(evidence, dict), f"{ALPHA}: evidence is {evidence!r}"
    assert support.ALPHA_PY in (evidence.get("code") or []), f"{ALPHA}: code evidence {evidence.get('code')!r}"
    assert support.TEST_ALPHA in (evidence.get("tests") or []), f"{ALPHA}: tests evidence {evidence.get('tests')!r}"
    commits = evidence.get("commits") or []
    touching = base.git(audited.root, "log", "--format=%H", "--", support.ALPHA_PY).split()
    assert len(touching) == 1, "planting fault: more than one commit touches src/alpha.py"
    assert any(isinstance(c, str) and len(c) >= 7 and touching[0].startswith(c) for c in commits), \
        f"{ALPHA}: no commit evidence names the commit that touched {support.ALPHA_PY} ({touching[0][:12]}): {commits!r}"


def test_s2_the_partly_built_spec_names_the_code_it_has_and_not_the_code_it_lacks(audited):
    evidence = spec_entry(audited, BETA).get("evidence")
    assert isinstance(evidence, dict), f"{BETA}: evidence is {evidence!r}"
    assert support.BETA_PY in (evidence.get("code") or []), f"{BETA}: code evidence {evidence.get('code')!r}"
    assert support.BETA_EXTRA_PY not in (evidence.get("code") or []), \
        f"{BETA}: {support.BETA_EXTRA_PY} is no tracked file and is no evidence of code"


def test_s2_every_item_of_evidence_is_backed_by_the_repository(audited):
    """Each code and test path is tracked at HEAD; each commit is a hash of at least 7 characters that resolves."""
    tracked = set(base.git(audited.root, "ls-files").split("\n"))
    for path in support.SPECS:
        evidence = spec_entry(audited, path).get("evidence")
        assert isinstance(evidence, dict), f"{path}: evidence is {evidence!r}"
        for key in ("code", "tests", "commits"):
            assert isinstance(evidence.get(key), list), f"{path}: evidence.{key} is {evidence.get(key)!r}, not a list"
        for rel in [*evidence["code"], *evidence["tests"]]:
            assert rel in tracked, f"{path}: evidence names {rel}, which is no tracked file"
        for commit in evidence["commits"]:
            assert isinstance(commit, str) and re.fullmatch(r"[0-9a-f]{7,40}", commit), f"{path}: commit {commit!r}"
            found = base.git(audited.root, "rev-parse", "--verify", "--quiet", f"{commit}^{{commit}}", check=False)
            assert found.strip(), f"{path}: commit {commit} resolves to no commit"


def test_s2_the_tickets_found_are_listed_done_or_not_by_wave(audited):
    found = support.by_path(front(audited).get("tickets") or [], key="id")
    assert set(found) == set(support.TICKETS), f"tickets found: {sorted(found)}"
    for ident, (status, wave) in support.TICKETS.items():
        item = found[ident]
        assert str(item.get("wave")) == str(wave), f"{ident}: wave {item.get('wave')!r}"
        assert item.get("done") is (status == "closed"), f"{ident}: done is {item.get('done')!r} for status {status}"


def test_s2_the_top_level_code_modules_are_listed(audited):
    modules = front(audited).get("modules")
    assert isinstance(modules, list) and set(modules) == support.MODULES, f"modules: {modules!r}"
    assert len(modules) == len(set(modules)), f"a module is listed twice: {modules!r}"


def test_s2_specs_with_no_code_and_code_with_no_spec_are_listed(audited):
    record = front(audited)
    assert set(record.get("specs_without_code") or []) == {OMEGA}, f"specs_without_code: {record.get('specs_without_code')!r}"
    assert set(record.get("code_without_spec") or []) == {GAMMA_PY}, f"code_without_spec: {record.get('code_without_spec')!r}"


def test_s2_each_gap_is_listed_once_as_one_question_with_a_place_for_the_answer(audited):
    gaps = front(audited).get("gaps")
    assert isinstance(gaps, list) and all(isinstance(item, dict) for item in gaps), f"gaps: {gaps!r}"
    subjects = [item.get("subject") for item in gaps]
    assert sorted(subjects) == sorted(support.GAPS), f"gap subjects {subjects}, expected {sorted(support.GAPS)}"
    for item in gaps:
        question = item.get("question")
        assert isinstance(question, str) and question.strip(), f"{item.get('subject')}: question is {question!r}"
        assert "answer" in item, f"{item.get('subject')}: the gap holds no place (key answer) for the owner's answer"


def test_s2_a_built_spec_and_a_specified_module_raise_no_gap(audited):
    subjects = {item.get("subject") for item in front(audited).get("gaps") or []}
    assert ALPHA not in subjects and support.ALPHA_PY not in subjects, f"the built spec is a gap: {sorted(subjects)}"
    assert support.BETA_PY not in subjects, f"a module a spec names is a gap: {sorted(subjects)}"
