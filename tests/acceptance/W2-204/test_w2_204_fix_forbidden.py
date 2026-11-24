"""The fix under the closed ticket DAEO-ma4q (W2-204): the strict forbidden-citation rule in the product's own grading
(owner decision DEC-1227 D5 (a)); the ticket's last section, lines S1 to S4 of the fix (named ``fix-S1`` to ``fix-S4``
in the README's map).

The rule is W2-81's (``tests/acceptance/W2-81/w2_81_score.py``): a citation is right when a cited place holds a gold
line and no cited path is one of the question's forbidden paths (path equality); an answer is right only when the
grade is ``correct`` and the citation is right. Public interfaces only: ``gov memaudit preflight|brief|fresh`` as child
processes and the files a run leaves (``FIGURES.json``, ``misses.jsonl``, the reader's rows); in process, the interface
the fix names: ``gov.memaudit.preflight.form_ok``, ``gov.memaudit.matcher.questions``, ``forbidden_cited`` and
``citation_right``. W2-81's scorer is loaded by path and never edited; the reader and the graders are W2-171's fakes.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

import w2_204_stages as ST
import w2_204_support as K
from w2_204_support import HALVES, HIDDEN, VISIBLE

A, B, C, D = K.SPARE_CODE[:4]            # app/core/x1.py .. x4.py: real files, never a question's source
OTHER = "archive/old.md"                  # a real file that is neither gold nor forbidden anywhere
NEAR_A, NEAR_B = "app/core/x10.py", "app/core/x1.pyc"   # not equal to A, though A is a prefix of both
GOLD = "gold"

_SCORE_PATH = K.ACCEPT / "W2-81" / "w2_81_score.py"


def w2_81():
    """W2-81's scorer, loaded by its path: the reference of the rule."""
    spec = importlib.util.spec_from_file_location("w2_81_score_loaded_by_w2_204_fix", _SCORE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def w81_right(gold: tuple, forbidden, cites, grade, verdict: str = "answer") -> bool:
    """W2-81's ``judge_question`` on one planted case: ``gold`` is ``(path, line)``."""
    question = SimpleNamespace(id="x-q01", sources=[(gold[0], gold[1], "")], forbidden=list(forbidden))
    reader = {"verdict": verdict, "citations": [tuple(c) for c in cites], "attempts": 1}
    return w2_81().judge_question(question, reader, grade)["right"]


# -- the planted run of the product's judge path ---------------------------------------------------------------------
# One case per question: ``forbidden`` is the field written in the question file (None: the field is left out),
# ``cites`` what the fake reader cites (``GOLD`` is the question's first gold place), ``grade`` the fake graders' grade.
CASES = {
    HIDDEN: {   # exactly one forbidden-cited answer (q05): S4's "one"
        "q05": {"forbidden": [A], "cites": [GOLD, A], "grade": "correct"},        # gold and forbidden: wrong
        "q06": {"forbidden": [B], "cites": [GOLD], "grade": "correct"},           # a list, never cited: right
        "q08": {"forbidden": [C], "cites": [GOLD], "grade": "wrong"},             # wrong grade, gold cited: wrong
        "q09": {"forbidden": [D], "cites": [GOLD, OTHER], "grade": "correct"},    # another path beside gold: right
    },
    VISIBLE: {
        "q05": {"forbidden": [A], "cites": [A], "grade": "correct"},              # forbidden alone: wrong
        "q06": {"forbidden": [A], "cites": [GOLD, A], "grade": "wrong"},          # both and a wrong grade: wrong
        "q07": {"forbidden": [A, B], "cites": [B, GOLD], "grade": "correct"},     # the list's second path, first cited
        "q08": {"forbidden": [A], "cites": [GOLD], "grade": "correct"},           # right
        "q10": {"forbidden": None, "cites": [GOLD, A], "grade": "correct"},       # no list: A is an ordinary path
        "q40": {"forbidden": [A], "cites": [A], "grade": "not_found", "verdict": "not_found"},  # the apart question
    },
}
EXPECTED_MISSES = {HIDDEN: {"q05": "incomplete", "q08": "wrong"},
                   VISIBLE: {"q05": "incomplete", "q06": "wrong", "q07": "incomplete"}}
# (citation_right, forbidden_cited) of the rows the cases name; every other row is (True, False), q40 (False, False)
EXPECTED_ROWS = {
    HIDDEN: {"q05": (False, True), "q06": (True, False), "q08": (True, False), "q09": (True, False)},
    VISIBLE: {"q05": (False, True), "q06": (False, True), "q07": (False, True), "q08": (True, False),
              "q10": (True, False), "q40": (False, False)},
}


def _cite(doc: dict, token: str) -> dict:
    if token == GOLD:
        path, (first, last) = doc["sources"][0]["path"], doc["sources"][0]["lines"]
        return {"path": path, "start_line": first, "end_line": min(last, first + 3)}
    return {"path": token, "start_line": 1, "end_line": 2}


def _forbidden_run(folder: Path) -> dict:
    world = K.build(folder / "w")
    calls = ST._start(world)
    for audit, _ in HALVES:
        specs = K.clean_specs()
        for spec in specs:
            case = CASES[audit].get(spec["id"])
            if case and case["forbidden"] is not None:
                spec["extra"] = {"forbidden": list(case["forbidden"])}
        world.write_half(audit, specs)
        world.write_notes(audit)
    world.install_plans(control_hits=17)
    state = world.state / "claude_plan.json"
    plan = json.loads(state.read_text(encoding="utf-8"))
    planted = {}
    for audit, _ in HALVES:
        planted[audit] = {}
        for qid, doc in world.docs(audit).items():
            entry, case = plan["q"][doc["question"]], CASES[audit].get(qid)
            if case:
                entry["reader"][0]["citations"] = [_cite(doc, t) for t in case["cites"]]
                entry["reader"][0]["verdict"] = case.get("verdict", "answer")
                entry["grader"], entry["check"] = [case["grade"]], [case["grade"]]
            reader, source = entry["reader"][0], doc["sources"][0]
            planted[audit][qid] = {
                "forbidden": doc.get("forbidden", []), "gold": [source["path"], source["lines"][0]],
                "grade": entry["grader"][0], "verdict": reader["verdict"], "category": doc["category"],
                "cites": [[c["path"], c["start_line"], c["end_line"]] for c in reader["citations"]]}
    state.write_text(json.dumps(plan), encoding="utf-8")
    ST._transcripts(world, leak=False)
    calls["final"] = world.fresh()
    return {"calls": calls, "planted": planted}


ST.BUILDS["forbidden"] = _forbidden_run


def judged(stage, name: str = "forbidden"):
    run = stage(name)
    assert run["final"].code == 0, run["final"]
    return run


def misses_of(run, audit: str) -> dict:
    path = run.world.run_dir(audit) / "misses.jsonl"
    assert path.is_file(), f"no misses.jsonl for {audit}: {run['final']!r}"
    return {m["id"]: m for m in map(json.loads, path.read_text(encoding="utf-8").splitlines()) if m}


def row_of(run, audit: str, qid: str) -> dict:
    path = run.world.run_dir(audit) / "reader" / f"{qid}.json"
    assert path.is_file(), f"no row for {audit} {qid}: {run['final']!r}"
    return json.loads(path.read_text(encoding="utf-8"))


def figures_of(run, audit: str) -> dict:
    path = run.world.run_dir(audit) / "FIGURES.json"
    assert path.is_file(), f"no FIGURES.json for {audit}: {run['final']!r}"
    return json.loads(path.read_text(encoding="utf-8"))


# -- in-process: the questions the product loads ---------------------------------------------------------------------
ENTRY = {"visible": [], "hidden": [f"fixtures/evaluation/{HIDDEN}/hidden/**"], "measures": {"roles": ["no-such-role-w2-204"]}}
GOLD_Q07 = ("records/tasks/T-07.md", 6, 9)     # a place holding q07's first gold line (its lines are [6, 11])
GOLD_Q08 = ("records/tasks/T-08.md", 6, 9)
UNIT_FORBIDDEN = {"q07": [A, B], "q40": [A]}


class Loaded:
    def __init__(self, base: Path):
        self.world = world = K.build(base / "w")
        specs = K.clean_specs()
        for spec in specs:
            if spec["id"] in UNIT_FORBIDDEN:
                spec["extra"] = {"forbidden": list(UNIT_FORBIDDEN[spec["id"]])}
        world.write_half(HIDDEN, specs)
        from gov.memaudit import matcher
        self.questions = {q["id"]: q for q in matcher.questions(world.sets, HIDDEN, "hidden", world.repo, default=ENTRY)}


@pytest.fixture(scope="module")
def loaded(tmp_path_factory) -> Loaded:
    return Loaded(tmp_path_factory.mktemp("w2-204-fix-forbidden"))


# ==== S1: a question may name forbidden sources ======================================================================
def _clean_doc(world: K.World) -> dict:
    specs = {s["id"]: s for s in K.clean_specs()}
    return world.question_doc("h", specs["q07"])


VALID_FIELDS = {"absent": None, "empty-list": [], "one-path": [A], "two-paths": [A, B]}
MALFORMED_FIELDS = {"a-string": A, "a-mapping": {"path": A}, "a-number": 5, "a-bool": True, "an-empty-item": [""],
                    "an-empty-item-after-a-path": [A, ""], "a-number-item": [3], "a-null-item": [None],
                    "a-list-item": [[A]], "a-mapping-item": [{"path": A}]}


@pytest.mark.parametrize("name", sorted(VALID_FIELDS))
def test_fix_s1_form_ok_accepts_the_field_and_its_absence(world, name):
    from gov.memaudit import preflight
    doc = _clean_doc(world)
    if VALID_FIELDS[name] is not None:
        doc["forbidden"] = copy.deepcopy(VALID_FIELDS[name])
    assert preflight.form_ok(doc, "q07", K.CATEGORY_NAMES) is True, name


@pytest.mark.parametrize("name", sorted(MALFORMED_FIELDS))
def test_fix_s1_form_ok_refuses_a_malformed_field(world, name):
    from gov.memaudit import preflight
    doc = _clean_doc(world)
    doc["forbidden"] = copy.deepcopy(MALFORMED_FIELDS[name])
    assert preflight.form_ok(doc, "q07", K.CATEGORY_NAMES) is False, name


def _half_with(world: K.World, field) -> None:
    specs = K.clean_specs()
    for spec in specs:
        if spec["id"] in ("q05", "q07", "q09") and field is not None:
            spec["extra"] = {"forbidden": copy.deepcopy(field)}
    world.write_half(HIDDEN, specs)


@pytest.mark.parametrize("name", sorted(VALID_FIELDS))
def test_fix_s1_a_set_with_or_without_the_field_passes_the_pre_flight(world, name):
    _half_with(world, VALID_FIELDS[name])
    run = world.step("preflight", HIDDEN)
    assert run.code == 0 and "PF-FORM ok" in run.lines, run
    assert not [x for x in run.lines if x.startswith("PF-") and " refused" in x], run


@pytest.mark.parametrize("name", sorted(MALFORMED_FIELDS))
def test_fix_s1_a_malformed_field_is_pf_form_naming_the_question(world, name):
    specs = K.clean_specs()
    next(s for s in specs if s["id"] == "q07")["extra"] = {"forbidden": copy.deepcopy(MALFORMED_FIELDS[name])}
    next(s for s in specs if s["id"] == "q11")["extra"] = {"forbidden": [B]}   # a good field beside it is no fault
    world.write_half(HIDDEN, specs)
    run = world.step("preflight", HIDDEN)
    form = [x for x in run.lines if x.startswith("PF-FORM")]
    assert run.code == 1 and len(form) == 1 and form[0].split() == ["PF-FORM", "refused", "1", "q07"], run


def test_fix_s1_two_malformed_fields_name_both_questions(world):
    specs = K.clean_specs()
    next(s for s in specs if s["id"] == "q07")["extra"] = {"forbidden": A}
    next(s for s in specs if s["id"] == "q09")["extra"] = {"forbidden": [A, ""]}
    next(s for s in specs if s["id"] == "q11")["extra"] = {"forbidden": [B]}   # a good one beside them
    world.write_half(HIDDEN, specs)
    run = world.step("preflight", HIDDEN)
    form = [x for x in run.lines if x.startswith("PF-FORM")]
    assert run.code == 1 and len(form) == 1, run
    words = form[0].split()
    assert words[:3] == ["PF-FORM", "refused", "2"] and sorted(words[3:]) == ["q07", "q09"], run


def test_fix_s1_the_loaded_question_holds_its_forbidden_paths(loaded):
    assert loaded.questions["q07"]["forbidden"] == UNIT_FORBIDDEN["q07"]
    assert loaded.questions["q40"]["forbidden"] == UNIT_FORBIDDEN["q40"]


def test_fix_s1_a_question_without_the_field_loads_an_empty_list(loaded):
    assert loaded.questions["q08"]["forbidden"] == []
    assert all(q["forbidden"] == [] for qid, q in loaded.questions.items() if qid not in UNIT_FORBIDDEN)


# ==== S2: citing a forbidden source makes the answer wrong ============================================================
def test_fix_s2_matcher_forbidden_cited_is_path_equality(loaded):
    from gov.memaudit import matcher
    q07, q08 = loaded.questions["q07"], loaded.questions["q08"]
    for cites, want in (([(A, 1, 3)], True), ([(B, 50, 60)], True), ([GOLD_Q07, (A, 1, 3)], True),
                        ([(OTHER, 1, 2), (B, 1, 1)], True), ([GOLD_Q07], False), ([(OTHER, 1, 2)], False),
                        ([], False), ([(NEAR_A, 1, 3)], False), ([(NEAR_B, 1, 3)], False)):
        assert matcher.forbidden_cited(q07, cites) is want, cites
    assert matcher.forbidden_cited(q08, [(A, 1, 3), (B, 1, 3)]) is False, "no list: nothing is forbidden"


def test_fix_s2_matcher_citation_right_is_gold_cited_and_no_forbidden_cited(loaded):
    from gov.memaudit import matcher
    repo, q07, q08, q40 = loaded.world.repo, loaded.questions["q07"], loaded.questions["q08"], loaded.questions["q40"]
    for cites, want in (([GOLD_Q07], True), ([(A, 1, 3)], False), ([GOLD_Q07, (A, 1, 3)], False),
                        ([(B, 1, 3), GOLD_Q07], False), ([GOLD_Q07, (OTHER, 1, 2)], True), ([], False),
                        ([(OTHER, 1, 2)], False), ([GOLD_Q07, (NEAR_A, 1, 3)], True)):
        assert matcher.citation_right(repo, q07, cites) is want, cites
    assert matcher.citation_right(repo, q08, [GOLD_Q08, (A, 1, 3)]) is True, "no list: as before"
    assert matcher.citation_right(repo, q08, [(A, 1, 3)]) is False
    for cites in ([], [(A, 1, 3)], [("records/decisions.md", 3, 3)]):
        assert matcher.citation_right(repo, q40, cites) is False, "an apart question has no right citation"


def test_fix_s2_matcher_citation_right_is_the_old_gold_test_less_a_forbidden_citation(loaded):
    """One function holds the rule: it equals ``cited`` and not ``forbidden_cited``, apart questions apart."""
    from gov.memaudit import matcher
    repo = loaded.world.repo
    options = ([GOLD_Q07], [(A, 1, 3)], [GOLD_Q07, (A, 1, 3)], [(OTHER, 1, 2)], [], [GOLD_Q07, (OTHER, 1, 2)])
    for q in (loaded.questions["q07"], loaded.questions["q08"], loaded.questions["q40"]):
        for cites in options:
            want = (not q["apart"]) and matcher.cited(repo, q, cites) and not matcher.forbidden_cited(q, cites)
            assert matcher.citation_right(repo, q, cites) is want, (q["id"], cites)


def test_fix_s2_planted_correct_and_gold_cited_is_right(stage):
    run = judged(stage)
    for audit, qids in ((HIDDEN, ("q06", "q09", "q01", "q30")), (VISIBLE, ("q08", "q01"))):
        missed = misses_of(run, audit)
        for qid in qids:
            row = row_of(run, audit, qid)
            assert qid not in missed and row["citation_right"] is True and row["forbidden_cited"] is False, (audit, qid)


def test_fix_s2_planted_correct_and_forbidden_cited_alone_is_wrong(stage):
    run = judged(stage)
    row = row_of(run, VISIBLE, "q05")
    assert "q05" in misses_of(run, VISIBLE) and row["citation_right"] is False and row["forbidden_cited"] is True


def test_fix_s2_planted_correct_with_gold_and_forbidden_cited_is_wrong(stage):
    run = judged(stage)
    for audit, qid in ((HIDDEN, "q05"), (VISIBLE, "q07")):   # q07 cites the list's second path before the gold
        row = row_of(run, audit, qid)
        assert (row["grades"]["grader"]["grade"], row["grades"]["check"]["grade"]) == ("correct", "correct")
        assert qid in misses_of(run, audit), (audit, qid)
        assert row["citation_right"] is False and row["forbidden_cited"] is True, (audit, qid)
        assert misses_of(run, audit)[qid]["outcome"] == "incomplete", "correct, but not right: the citation"


def test_fix_s2_planted_wrong_grade_with_gold_cited_is_wrong_and_forbidden_cited_is_what_was_cited(stage):
    run = judged(stage)
    for audit, qid, cited_forbidden in ((HIDDEN, "q08", False), (VISIBLE, "q06", True)):
        row = row_of(run, audit, qid)
        assert qid in misses_of(run, audit) and misses_of(run, audit)[qid]["outcome"] == "wrong", (audit, qid)
        assert row["forbidden_cited"] is cited_forbidden, (audit, qid)


def test_fix_s2_planted_a_question_without_a_list_is_graded_as_before(stage):
    run = judged(stage)
    row = row_of(run, VISIBLE, "q10")   # cites the gold and the path another question lists: no list here
    assert "q10" not in misses_of(run, VISIBLE) and row["citation_right"] is True and row["forbidden_cited"] is False


def test_fix_s2_planted_an_apart_question_is_unchanged(stage):
    run = judged(stage)
    row = row_of(run, VISIBLE, "q40")   # not found, though the reader cited a path its list names
    assert row["apart"] is True and row["forbidden_cited"] is False and row["citation_right"] is False
    assert "q40" not in misses_of(run, VISIBLE), "an apart question is right when the answer is not found"


def test_fix_s2_the_planted_misses_are_exactly_the_cases_that_cite_a_forbidden_path_or_are_graded_wrong(stage):
    run = judged(stage)
    for audit, want in EXPECTED_MISSES.items():
        assert {i: m["outcome"] for i, m in misses_of(run, audit).items()} == want, audit
    for audit, rows in EXPECTED_ROWS.items():
        for qid, pair in rows.items():
            row = row_of(run, audit, qid)
            assert (row["citation_right"], row["forbidden_cited"]) == pair, (audit, qid)


def test_fix_s2_parity_the_product_and_w2_81_agree_on_every_planted_question(stage):
    """W2-81's ``judge_question`` and the product's verdict (a question is a miss, or it is right) on the same gold,
    forbidden paths, citations and grade. The apart question has no counterpart in W2-81 and is left out."""
    run = judged(stage)
    differ, compared, wrong_by_forbidden = [], 0, 0
    for audit, _ in HALVES:
        missed = misses_of(run, audit)
        for qid, case in run.record["planted"][audit].items():
            if case["category"] == "nonexistent-id":
                continue
            theirs = w81_right(tuple(case["gold"]), case["forbidden"], case["cites"], case["grade"], case["verdict"])
            ours = qid not in missed
            compared += 1
            wrong_by_forbidden += (not theirs) and case["grade"] == "correct" and bool(case["forbidden"]) \
                and any(c[0] in case["forbidden"] for c in case["cites"])
            if theirs != ours:
                differ.append((audit, qid, theirs, ours))
    assert compared == 78 and wrong_by_forbidden == 3, (compared, wrong_by_forbidden)
    assert not differ, f"W2-81 and the product differ on (audit, id, W2-81 right, product right): {differ}"


def test_fix_s2_parity_matcher_citation_right_agrees_with_w2_81_over_citations_and_grades(loaded):
    from gov.memaudit import matcher
    repo = loaded.world.repo
    cases = {"q07": (GOLD_Q07, UNIT_FORBIDDEN["q07"]), "q08": (GOLD_Q08, [])}
    options = ([GOLD_Q07], [GOLD_Q08], [(A, 1, 3)], [(B, 1, 3)], [GOLD_Q07, (A, 1, 3)], [(A, 1, 3), GOLD_Q07],
               [GOLD_Q08, (A, 1, 3)], [GOLD_Q07, (OTHER, 1, 2)], [GOLD_Q07, (NEAR_A, 1, 3)], [(OTHER, 1, 2)], [])
    differ = []
    for qid, (gold, forbidden) in cases.items():
        for cites in options:
            for grade in ("correct", "wrong", "not_found"):
                theirs = w81_right((gold[0], gold[1]), forbidden, cites, grade)
                ours = grade == "correct" and matcher.citation_right(repo, loaded.questions[qid], cites)
                if theirs != ours:
                    differ.append((qid, cites, grade, theirs, ours))
    assert not differ, f"(id, citations, grade, W2-81, product): {differ}"


# ==== S3: the question writer is told to name the forbidden sources ===================================================
class Briefs:
    def __init__(self, base: Path):
        self.world = world = K.build(base / "w")
        self.out = {"writer": base / "sessions" / "writer-1", "checker": base / "sessions" / "checker-1"}
        self.writer_call = world.brief("writer", HIDDEN, self.out["writer"])
        world.write_half(HIDDEN, K.clean_specs())
        world.write_notes(HIDDEN, 1)
        self.checker_call = world.brief("checker", HIDDEN, self.out["checker"])

    def text(self, kind: str) -> str:
        path = self.out[kind] / "brief.md"
        assert path.is_file(), f"no brief.md in the {kind} folder: {getattr(self, kind + '_call')!r}"
        return path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def briefs(tmp_path_factory) -> Briefs:
    return Briefs(tmp_path_factory.mktemp("w2-204-fix-briefs"))


def _form_block(text: str) -> list[str]:
    """The lines of the fenced ``yaml`` block that holds the question form (the one naming ``naive_answer:``)."""
    lines = text.splitlines()
    at = next((i for i, x in enumerate(lines) if x.strip().startswith("naive_answer:")), None)
    assert at is not None, "the writer brief's question form has no naive_answer line"
    start = max(i for i in range(at) if lines[i].strip().startswith("```"))
    end = next(i for i in range(at, len(lines)) if lines[i].strip() == "```")
    return lines[start + 1:end]


def test_fix_s3_the_writer_brief_s_question_form_shows_the_optional_forbidden_field(briefs):
    assert briefs.writer_call.code == 0, briefs.writer_call
    block = _form_block(briefs.text("writer"))
    assert any(x.strip().startswith("forbidden:") for x in block), "the form's yaml block has no `forbidden:` line"


def test_fix_s3_the_writer_brief_tells_the_writer_to_name_the_stale_sources(briefs):
    text = briefs.text("writer")
    prose = "\n".join(x for x in text.splitlines() if not x.strip().startswith("forbidden:"))
    assert re.search(r"(?is)forbidden.{0,400}\b(stale|superseded|legacy)\b|\b(stale|superseded|legacy)\b.{0,400}forbidden",
                     prose), "no rule ties `forbidden` to the stale, superseded or legacy source"
    assert re.search(r"(?is)\bforbidden\b.{0,300}\b(name|list|put|write|set)\w*|\b(name|list|put|write|set)\w*.{0,300}\bforbidden\b",
                     prose), "the rule does not tell the writer to name them"
    assert prose.lower().count("forbidden") >= 2, "the field is named in the form and in a rule"


def test_fix_s3_the_writer_brief_says_a_forbidden_source_is_never_also_a_gold_source(briefs):
    text = briefs.text("writer")
    assert re.search(r"(?is)\bforbidden\b.{0,250}\b(never|not|no)\b.{0,120}\bgold\b|"
                     r"\bgold\b.{0,250}\b(never|not|no)\b.{0,120}\bforbidden\b", text), \
        "no sentence says a forbidden source is not a gold source"


def test_fix_s3_the_checker_brief_names_the_optional_forbidden_field_in_its_input_form(briefs):
    assert briefs.checker_call.code == 0, briefs.checker_call
    text = briefs.text("checker")
    at = text.index("naive_answer")
    assert "forbidden" in text[max(0, at - 300):at + 300], "the input form's sentence does not name `forbidden`"
    assert re.search(r"`forbidden`", text), "the field is not named as a field"


# Rewrite-Reason: DEC-1227 D5 and DEC-1232 (6): the guard is D5's, that D5's own change left the pinned prompts and the
# model-call wrapper alone. It compared the whole ``template/`` tree with the merge base, so any other fix that changes
# ``template/`` legitimately (F1's connectors, F11, F14's lead role file) turned it red. It now pins the two files D5
# must not change, found through their modules, by sha256: both are byte for byte what they were before D5's first commit.
D5_UNTOUCHED = {
    "gov.memaudit.prompts": "086b7da4634c457fe042c2719db618fdcf4b940ef1317b519991455ed1bfa85d",
    "gov.memaudit.claude": "5521803fc544cccc0c525edfbc7434101ec5591b75560704866ab123e683f27a",
}


@pytest.mark.parametrize("module", sorted(D5_UNTOUCHED))
def test_fix_s3_guard_kernel_template_prompts_and_claude_are_the_merge_base_s_files(module):
    """Guard (green on the base): the pinned prompts (``gov.memaudit.prompts``) and the model-call wrapper
    (``gov.memaudit.claude``), found through their modules, are byte for byte the files D5 was told not to change.
    ``template/`` as a whole is no part of the guard: other fixes change it."""
    spec = importlib.util.find_spec(module)
    assert spec is not None and spec.origin, f"{module} is not importable"
    digest = hashlib.sha256(Path(spec.origin).read_bytes()).hexdigest()
    assert digest == D5_UNTOUCHED[module], (
        f"{module} ({spec.origin}) is not the file D5 left alone: sha256 {digest}; a change to it belongs to its own "
        f"ticket, which moves this pin")


# ==== S4: the record says it ==========================================================================================
def test_fix_s4_a_run_with_one_forbidden_cited_answer_counts_one_and_names_the_rule(stage):
    figures = figures_of(judged(stage), HIDDEN)
    assert figures["forbidden_rule"] == "strict"
    assert figures["misses"]["forbidden_cited"] == 1
    assert figures["misses"]["forbidden_cited"] <= figures["misses"]["total"] == 2


def test_fix_s4_the_forbidden_cited_misses_are_counted_apart_from_the_others(stage):
    """The visible half: three forbidden-cited misses (one with a wrong grade), the apart question not among them."""
    run = judged(stage)
    figures = figures_of(run, VISIBLE)
    assert figures["forbidden_rule"] == "strict"
    assert figures["misses"]["total"] == 3 and figures["misses"]["forbidden_cited"] == 3
    assert set(figures["misses"]["by_outcome"]) == {"wrong", "incomplete", "not_found"}
    assert figures["misses"]["by_outcome"] == {"wrong": 1, "incomplete": 2, "not_found": 0}
    hidden = figures_of(run, HIDDEN)["misses"]
    assert hidden["by_outcome"] == {"wrong": 1, "incomplete": 1, "not_found": 0}, "keys and sums are as before"


@pytest.mark.parametrize("name", ["right", "misses"])
def test_fix_s4_a_run_with_none_gives_zero_and_the_key_is_there(stage, name):
    run = stage(name)
    assert run["final"].code == 0, run["final"]
    for audit, _ in HALVES:
        figures = figures_of(run, audit)
        assert figures["forbidden_rule"] == "strict", (name, audit)
        assert "forbidden_cited" in figures["misses"] and figures["misses"]["forbidden_cited"] == 0, (name, audit)
        assert figures["misses"]["forbidden_cited"] <= figures["misses"]["total"]


VERDICT = re.compile(r"FRESH VERDICT hidden right (\d+) of (\d+) \((\d+(?:\.\d+)?) %\): (passes|misses)")
BESIDE = re.compile(r"FRESH BESIDE visible right (\d+) of (\d+)")


def test_fix_s4_the_run_s_printed_verdict_lines_count_the_strict_rule_in_their_old_form(stage):
    """The two verdict lines keep their form (counts only, no word of the rule); their numbers are the strict ones: 38
    of the hidden 40 (q05 cites a forbidden path, q08 is graded wrong) and 37 of the visible 40."""
    final = judged(stage)["final"]
    verdict = [m for m in map(VERDICT.fullmatch, final.lines[-2:]) if m]
    beside = [m for m in map(BESIDE.fullmatch, final.lines[-2:]) if m]
    assert len(verdict) == 1 and len(beside) == 1, final
    assert (verdict[0][1], verdict[0][2]) == ("38", "40") and (beside[0][1], beside[0][2]) == ("37", "40"), final
    assert not [x for x in final.lines if "forbidden" in x.lower() or "strict" in x.lower()], final


def test_fix_s4_counts_only_no_text_path_or_answer_reaches_a_line_or_the_figures(stage):
    run = judged(stage)
    shown = "\n".join(call.text for call in run.calls.values())
    secret = [*K.planted_words(), A, B, C, D]
    assert [w for w in secret if w in shown] == [], "a planted word or a forbidden path reached a printed line"
    for audit, _ in HALVES:
        text = (run.world.run_dir(audit) / "FIGURES.json").read_text(encoding="utf-8")
        assert [w for w in secret if w in text] == [], f"{audit}: FIGURES.json holds a word or a path"
        assert "forbidden_cited" in text
