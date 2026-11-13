"""S1: the pre-flight's ten checks, one planted defect per check, each refused with its own code (Interface 3);
the clean set ends ``PRE-FLIGHT: every check as expected`` with exit 0; the scale of section 4 at 36 to 40; the
domain and subsystem tables by first source path; ``PF-DRAWN`` from a planted ``selection.json`` and from the lists
derived from ``indep/AUDITS.log`` and ``indep/SEEDS.log`` (seed hash checked), and the lists that cannot be had.

Driven as ``python3 -m gov.memaudit preflight --sets-root <root> --audit <A> --repo <repo> --commit <A's commit>
--runs-dir <launch log>`` in a child process; a planted world under TMPDIR (``w2_170_world``).
"""

from __future__ import annotations

import json
import shutil

import pytest

import w2_170_world as W


def _refused(run, code):
    blocks, _ = W.pf_blocks(run.out)
    assert code in blocks, (code, run)
    assert blocks[code]["word"] == "refused", (code, run)
    assert run.code == 1, run
    assert run.last == W.FINAL_NOT, run
    return blocks


def _only(run, code):
    """``code`` refused and every other of the ten ok: each defect is refused by its own code."""
    blocks = _refused(run, code)
    others = {c: blocks.get(c, {}).get("word") for c in W.CODES if c != code}
    assert all(word == "ok" for word in others.values()), (code, others, run)
    return blocks


def _clean(run):
    blocks, order = W.pf_blocks(run.out)
    assert run.code == 0, run
    assert run.last == W.FINAL_OK, run
    assert order == list(W.CODES), (order, run)
    assert all(blocks[c]["word"] == "ok" for c in W.CODES), run
    return blocks


# -- the clean set ------------------------------------------------------------------------------------------------
def test_s1_the_clean_set_passes_every_check_and_ends_with_the_exact_line(world):
    world.write_set(W.clean_specs())
    run = world.preflight()
    _clean(run)
    doc = world.json_of("PREFLIGHT.json")
    assert doc["ok"] is True
    text = json.dumps(doc)
    assert all(code in text for code in W.CODES), text


def test_s1_a_refused_check_prints_one_line_per_code_in_the_kpi_order_and_writes_ok_false(world):
    specs = W.clean_specs()
    W.by_id(specs, "q08")["commit"] = world.base_commit
    world.write_set(specs)
    run = world.preflight()
    blocks, order = W.pf_blocks(run.out)
    assert order == list(W.CODES), (order, run)
    assert blocks["PF-COMMIT"]["n"] == 1 and blocks["PF-COMMIT"]["ids"] == ["q08"], run
    assert world.json_of("PREFLIGHT.json")["ok"] is False


def test_s1_an_empty_dropped_folder_is_not_a_stray_folder(world):
    world.write_set(W.clean_specs())
    world.dropped.mkdir()
    _clean(world.preflight())


def test_s1_an_absent_pool_folder_is_an_empty_pool(world):
    world.write_set(W.clean_specs())
    shutil.rmtree(world.pool.parent)
    _clean(world.preflight())


# -- 1 PF-COUNT ---------------------------------------------------------------------------------------------------
def test_s1_pf_count_refuses_fewer_than_36_files(world):
    world.write_set(W.without(W.clean_specs(), "q27", "q28", "q29", "q33", "q34"))
    _refused(world.preflight(), "PF-COUNT")


@pytest.mark.parametrize("stray", ["notes.txt", "extra/"])
def test_s1_pf_count_refuses_a_stray_file_or_folder_in_hidden(world, stray):
    world.write_set(W.clean_specs())
    if stray.endswith("/"):
        (world.hidden / stray).mkdir()
    else:
        (world.hidden / stray).write_text("a stray file\n", encoding="utf-8")
    _refused(world.preflight(), "PF-COUNT")


# -- 2 PF-FORM ----------------------------------------------------------------------------------------------------
_FORM = {
    "extra-key": {"extra": {"note": "a key the form does not have"}},
    "id-not-the-stem": {"extra": {"id": "q99"}},
    "empty-question": {"extra": {"question": ""}},
    "empty-gold-answer": {"extra": {"gold_answer": ""}},
    "unknown-category": {"extra": {"category": "decisions"}},
    "unknown-drawn": {"extra": {"drawn": "both"}},
    "commit-not-40-hex": {"extra": {"commit": "abc123"}},
    "drawn-missing": {"drop_keys": ["drawn"]},
    "sources-empty": {"extra": {"sources": []}},
    "source-without-path": {"extra": {"sources": [{"heading": "## Section c8", "lines": [3, 8]}]}},
    "lines-reversed": {"extra": {"sources": [{"path": "docs/contract/c8.md", "lines": [8, 3]}]}},
    "lines-from-zero": {"extra": {"sources": [{"path": "docs/contract/c8.md", "lines": [0, 3]}]}},
    "lines-three-numbers": {"extra": {"sources": [{"path": "docs/contract/c8.md", "lines": [3, 4, 5]}]}},
    "lines-not-integers": {"extra": {"sources": [{"path": "docs/contract/c8.md", "lines": [3, "8"]}]}},
    "keyword-not-bool": {"extra": {"keyword": "yes"}},
    "naive-answer-not-text": {"extra": {"naive_answer": 3}},
    "a-list-not-a-mapping": {"raw": "- id: q08\n- question: a list\n"},
    "not-yaml": {"raw": "id: q08\nquestion: [an unclosed list\n"},
}


@pytest.mark.parametrize("defect", sorted(_FORM))
def test_s1_pf_form_refuses_a_file_not_in_the_writer_brief_s_form(world, defect):
    specs = W.clean_specs()
    W.by_id(specs, "q08").update(_FORM[defect])
    world.write_set(specs)
    blocks = _refused(world.preflight(), "PF-FORM")
    assert "q08" in blocks["PF-FORM"]["ids"], blocks["PF-FORM"]


def test_s1_the_optional_keyword_and_naive_answer_pass_the_form(world):
    specs = W.clean_specs()
    W.by_id(specs, "q20")["extra"] = {"keyword": False}
    W.by_id(specs, "q02")["extra"] = {"naive_answer": "an older answer"}
    world.write_set(specs)
    _clean(world.preflight())


# -- 3 PF-COMMIT --------------------------------------------------------------------------------------------------
def test_s1_pf_commit_refuses_a_commit_other_than_the_audit_commit(world):
    specs = W.clean_specs()
    W.by_id(specs, "q08")["commit"] = world.base_commit
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-COMMIT")
    assert blocks["PF-COMMIT"]["ids"] == ["q08"]


# -- 4 PF-QUOTA ---------------------------------------------------------------------------------------------------
def test_s1_pf_quota_refuses_a_category_off_its_quota_and_names_no_id(world):
    specs = W.clean_specs()
    W.by_id(specs, "q20")["category"] = "decision"          # decision 7, exact-string 3
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-QUOTA")
    text = blocks["PF-QUOTA"]["text"]
    assert blocks["PF-QUOTA"]["ids"] == [], text
    assert "decision" in text and "exact-string" in text, text


@pytest.mark.parametrize("n", [36, 37, 38, 39])
def test_s1_pf_quota_reads_at_most_for_36_to_39_files(world, n):
    removed = ["q23", "q24", "q25", "q26"][:40 - n]
    world.write_set(W.without(W.clean_specs(), *removed))
    _clean(world.preflight())


def test_s1_pf_quota_refuses_a_count_over_its_quota_at_38_files(world):
    specs = W.without(W.clean_specs(), "q23", "q24")
    W.by_id(specs, "q20")["category"] = "decision"
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-QUOTA")
    assert blocks["PF-QUOTA"]["ids"] == []


# -- 5 PF-SPREAD and section 4's scale ---------------------------------------------------------------------------
def test_s1_pf_spread_refuses_a_domain_under_4(world):
    specs = W.repoint(W.clean_specs(), "q08", W.SPARE_LESSON)
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert "domain contract 3" in blocks["PF-SPREAD"]["text"]
    assert blocks["PF-SPREAD"]["ids"] == []


def test_s1_pf_spread_refuses_a_subsystem_over_10(world):
    specs = W.clean_specs()
    for qid, path in zip(["q23", "q24", "q25", "q26", "q27", "q28", "q29"], W.SPARE_RETRIEVAL):
        W.repoint(specs, qid, path)
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert "subsystem retrieval 11" in blocks["PF-SPREAD"]["text"]
    assert blocks["PF-SPREAD"]["ids"] == []


def _scaled(n: int, retrieval: int) -> list[dict]:
    """``n`` files (guard questions removed first), the retrieval subsystem holding ``retrieval``."""
    specs = W.without(W.clean_specs(), *["q23", "q24", "q25", "q26"][:40 - n])
    movable = [s["id"] for s in specs if W.subsystem_of(W.first_path(s["sources"])) in ("guard", "close",
                                                                                        "checkpoint")]
    for qid, path in zip(movable[:retrieval - 4], W.SPARE_RETRIEVAL):
        W.repoint(specs, qid, path)
    assert W.kept_counts(specs)[1]["retrieval"] == retrieval
    return specs


@pytest.mark.parametrize("n", [36, 37, 38, 39, 40])
def test_s1_the_scale_lets_a_subsystem_hold_its_scaled_maximum(world, n):
    world.write_set(_scaled(n, W.most_subsystem(n)))
    _clean(world.preflight())


@pytest.mark.parametrize("n", [36, 37, 38, 39, 40])
def test_s1_the_scale_refuses_one_over_the_scaled_maximum(world, n):
    over = W.most_subsystem(n) + 1
    world.write_set(_scaled(n, over))
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert f"subsystem retrieval {over}" in blocks["PF-SPREAD"]["text"]


@pytest.mark.parametrize("n", [36, 40])
def test_s1_the_scale_needs_4_of_a_domain_at_36_and_at_40(world, n):
    specs = W.repoint(W.without(W.clean_specs(), *["q23", "q24", "q25", "q26"][:40 - n]), "q08", W.SPARE_LESSON)
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert "domain contract 3" in blocks["PF-SPREAD"]["text"]


def test_s1_the_domain_is_the_first_source_s_never_a_later_one(world):
    specs = W.repoint(W.clean_specs(), "q08", W.SPARE_LESSON, keep_old=True)   # c8 stays as the second entry
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert "domain contract 3" in blocks["PF-SPREAD"]["text"]


def test_s1_a_charter_first_source_counts_for_the_contract_domain(world):
    world.write_set(W.repoint(W.clean_specs(), "q08", W.SPARE_CHARTER))
    _clean(world.preflight())


def test_s1_a_kernel_hook_first_source_counts_for_the_guard_subsystem(world):
    specs = W.clean_specs()
    movable = ["q19", "q20", "q21", "q22", "q27", "q28", "q29"]           # retrieval and close, to the hooks
    for qid, path in zip(movable, W.SPARE_HOOKS):
        W.repoint(specs, qid, path)
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SPREAD")
    assert "subsystem guard 11" in blocks["PF-SPREAD"]["text"]


# -- 6 PF-DRAWN ---------------------------------------------------------------------------------------------------
def test_s1_pf_drawn_refuses_a_changed_question_whose_source_is_not_in_selection_json_s_changed(world):
    selection = world.selection(changed=[p for p in world.changed if p != ".tickets/T-15.md"])
    world.write_set(W.clean_specs(), selection=selection)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == ["q15"]


def test_s1_pf_drawn_refuses_a_sample_question_whose_source_is_not_in_selection_json_s_sample(world):
    selection = world.selection(sample=[p for p in world.sample if p != "docs/plan/p13.md"])
    world.write_set(W.clean_specs(), selection=selection)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == ["q13"]


def test_s1_pf_drawn_never_checks_a_drawn_none_question(world):
    selection = world.selection(changed=[p for p in world.changed if p != "docs/DECISION_REGISTER.md"])
    world.write_set(W.clean_specs(), selection=selection)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == ["q01", "q02", "q03", "q04", "q05", "q06"]   # q39, q40: drawn none


def test_s1_pf_drawn_derives_the_lists_from_the_launch_log_when_selection_json_is_absent(world):
    world.write_set(W.clean_specs(), selection=False)
    _clean(world.preflight())


def test_s1_pf_drawn_from_the_derived_lists_refuses_a_question_off_its_list(world):
    specs = W.clean_specs()
    W.by_id(specs, "q13")["drawn"] = "changed"      # p13 did not change since the last audit
    world.write_set(specs, selection=False)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == ["q13"]


def test_s1_selection_json_is_read_first_when_present(world):
    selection = world.selection(changed=[p for p in world.changed if p != ".tickets/T-15.md"])
    world.write_set(W.clean_specs(), selection=selection)      # the launch log alone would accept q15
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == ["q15"]


def _drawn_from_lists(world) -> list[str]:
    return sorted(s["id"] for s in W.clean_specs() if world.drawn_of(s) in ("changed", "sample"))


_NO_LISTS = {
    "seed-hash-differs": lambda w: [W.seeds_line(commit=w.audit_commit, seed_sha256=W.sha_bytes(b"1\n"))],
    "no-matching-line": lambda w: [W.seeds_line(commit=w.audit_commit, round=2),
                                   W.seeds_line(commit=w.audit_commit, dry=True),
                                   W.seeds_line(commit=w.audit_commit, kind="checker"),
                                   W.seeds_line(commit=w.audit_commit, set=W.EARLIER)],
    "two-matching-lines": lambda w: [W.seeds_line(commit=w.audit_commit),
                                     W.seeds_line(commit=w.audit_commit, run="writer-again")],
}


@pytest.mark.parametrize("case", sorted(_NO_LISTS))
def test_s1_pf_drawn_names_every_drawn_question_when_the_lists_cannot_be_had(world, case):
    W.write_launch_log(world.launch, world.base_commit, world.audit_commit, seeds=_NO_LISTS[case](world))
    world.write_set(W.clean_specs(), selection=False)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == _drawn_from_lists(world)
    assert "q39" not in blocks["PF-DRAWN"]["ids"] and "q40" not in blocks["PF-DRAWN"]["ids"]


def test_s1_with_no_audits_log_nothing_is_changed_and_every_changed_question_is_named(world):
    W.write_launch_log(world.launch, world.base_commit, world.audit_commit, audits=False)
    world.write_set(W.clean_specs(), selection=False)
    blocks = _only(world.preflight(), "PF-DRAWN")
    assert blocks["PF-DRAWN"]["ids"] == sorted(s["id"] for s in W.clean_specs() if world.drawn_of(s) == "changed")


# -- 7 PF-SOURCE --------------------------------------------------------------------------------------------------
_SOURCE = {
    "path-missing-at-the-commit": ("q11", lambda s: s["sources"].append(W.source("docs/plan/gone.md", heading=None,
                                                                                 lines=(1, 2)))),
    "path-only-in-a-later-commit": ("q14", lambda s: s["sources"].append(W.source(W.LATE_FILE, heading=None,
                                                                                  lines=(1, 2)))),
    "heading-not-found-lines-outside": ("q12", lambda s: s["sources"].__setitem__(
        0, W.source("docs/plan/p12.md", heading="## Nowhere", lines=(3, 99)))),
    "heading-not-found-lines-absent": ("q12", lambda s: s["sources"].__setitem__(
        0, W.source("docs/plan/p12.md", heading="## Nowhere", lines=None))),
    "no-heading-lines-outside": ("q14", lambda s: s["sources"].__setitem__(
        0, W.source("docs/plan/p14.md", heading=None, lines=(3, 99)))),
}


@pytest.mark.parametrize("case", sorted(_SOURCE))
def test_s1_pf_source_refuses_a_source_not_found_at_the_audit_commit(world, case):
    qid, change = _SOURCE[case]
    specs = W.clean_specs()
    change(W.by_id(specs, qid))
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-SOURCE")
    assert blocks["PF-SOURCE"]["ids"] == [qid]


def test_s1_a_heading_not_found_with_lines_inside_passes_and_is_counted_re_anchored(world):
    specs = W.clean_specs()
    W.by_id(specs, "q12")["sources"][0] = W.source("docs/plan/p12.md", heading="## Nowhere", lines=(3, 8))
    world.write_set(specs)
    _clean(world.preflight())
    counts = W.find_key(world.json_of("PREFLIGHT.json"), r"re.?anchored")
    assert counts == [1], counts


# -- 8 PF-EVALNS --------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("namespace", sorted(W.EVAL_SOURCES))
def test_s1_pf_evalns_refuses_a_source_in_an_evaluation_namespace(world, namespace):
    specs = W.clean_specs()
    W.by_id(specs, "q16")["sources"].append(W.source(W.EVAL_SOURCES[namespace], heading=None, lines=(1, 2)))
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-EVALNS")
    assert blocks["PF-EVALNS"]["ids"] == ["q16"]


def test_s1_pf_evalns_refuses_an_evaluation_source_given_as_an_alternative(world):
    specs = W.clean_specs()
    spec = W.by_id(specs, "q17")
    spec["sources"] = [[spec["sources"][0], W.source(W.EVAL_SOURCES["evaluation-sources"], heading=None,
                                                     lines=(1, 2))]]
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-EVALNS")
    assert blocks["PF-EVALNS"]["ids"] == ["q17"]


# -- 9 PF-DUPPOOL -------------------------------------------------------------------------------------------------
def _pool_question(world, name, sources):
    doc = {"id": "q09", "question": "An earlier question.", "gold_answer": "An earlier answer.",
           "sources": sources, "commit": world.audit_commit, "category": "plan", "drawn": "sample"}
    (world.pool / name).write_text(W.yaml.safe_dump(doc, sort_keys=False), encoding="utf-8")


@pytest.mark.parametrize("form", ["the-same-mapping", "a-list-of-one-alternative"])
def test_s1_pf_duppool_refuses_a_gold_source_set_equal_to_a_pool_question_s(world, form):
    specs = W.clean_specs()
    src = W.by_id(specs, "q13")["sources"][0]
    _pool_question(world, f"{W.EARLIER}-q09.yaml", [src] if form == "the-same-mapping" else [[src]])
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-DUPPOOL")
    assert blocks["PF-DUPPOOL"]["ids"] == ["q13"]


def test_s1_pf_duppool_compares_sets_not_orders(world):
    specs = W.clean_specs()
    reg = {"path": "docs/DECISION_REGISTER.md", "heading": "### DEC-12 — the rule of item 12",
           "lines": [W.REGISTER_AT[12], W.REGISTER_AT[12] + 1]}
    spec = W.by_id(specs, "q18")
    spec["sources"] = [spec["sources"][0], reg]
    _pool_question(world, f"{W.EARLIER}-q09.yaml", [reg, spec["sources"][0]])
    world.write_set(specs)
    blocks = _only(world.preflight(), "PF-DUPPOOL")
    assert blocks["PF-DUPPOOL"]["ids"] == ["q18"]


def test_s1_pf_duppool_lets_a_pool_question_with_other_lines_pass(world):
    specs = W.clean_specs()
    src = dict(W.by_id(specs, "q13")["sources"][0], lines=[3, 7])
    _pool_question(world, f"{W.EARLIER}-q09.yaml", [src])
    world.write_set(specs)
    _clean(world.preflight())


# -- 10 PF-IDEXISTS -----------------------------------------------------------------------------------------------
def _ask(world, question):
    specs = W.clean_specs()
    W.by_id(specs, "q40")["question"] = question
    world.write_set(specs)
    return world.preflight()


def test_s1_pf_idexists_refuses_a_nonexistent_id_question_whose_id_exists_at_the_commit(world):
    blocks = _only(_ask(world, "What does decision DEC-12 decide?"), "PF-IDEXISTS")
    assert blocks["PF-IDEXISTS"]["ids"] == ["q40"]


def test_s1_pf_idexists_matches_whole_tokens_only(world):
    _clean(_ask(world, "What does decision DEC-99 decide?"))       # the register holds DEC-999, not DEC-99


def test_s1_pf_idexists_looks_at_the_audit_commit_not_the_tree(world):
    _clean(_ask(world, "What does decision DEC-777 decide?"))      # named only in a later commit


def test_s1_a_nonexistent_id_question_with_no_id_token_is_counted_and_not_refused(world):
    _clean(_ask(world, "Which decision number lies past the last one recorded?"))
    counts = W.find_key(world.json_of("PREFLIGHT.json"), r"no.?token")
    assert counts == [1], counts
