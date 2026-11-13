"""S5 scale (success-5), S6 measure (success-6), S11 the standard (success-11), F7 (failure-7); I3, I4: the A9 record's
``scale``, ``measure`` and ``standard`` blocks and the stage's ``STANDARD_DEPARTURE``.

The standard (I3): ``fabric.STANDARD = {reranker: "Qwen3-Reranker-0.6B", reranker_service: "shared", pool: <retrieval.yaml's
pool: block as Gov OS ships it>, bundle_tokens: 6000, widen: "sections"}``. A departure is a setting of the adopted
repository's ``retrieval.yaml`` that differs from it: the stage is not ok (``STANDARD_DEPARTURE``) unless ``--decision DEC-n``
is given, which the record then cites. The keys of ``retrieval.yaml`` for each setting are the engineer's (P-10, P-W2-88-TD-1):
``pool`` -> the ``pool:`` block (off: ``pool.meaning_uncut: false``); ``reranker_service`` -> ``rerank.service`` (absent:
``shared``; ``private`` is a second reranker); ``bundle_tokens`` -> ``bundle.tokens`` (absent: 6000). The departure is named in
``departures`` by ``fabric.STANDARD``'s own name (``pool``, ``reranker_service``, ``bundle_tokens``: the cases look for the word
``pool``, ``reranker`` or ``bundle``, which each contains). The planted over-budget (S5, ``--budget-ms``) and low-measure (S6,
``--questions``) cases are at the end of each section (P-1, the engineer's seams 1 and 2).
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
import sys

import pytest
import yaml

import w2_88_support as W
import store_hash

DECISION = "DEC-9999"
VARIANTS = {"pool-off": "pool", "second-reranker": "reranker", "bundle-budget": "bundle"}
VALUES = {"second-reranker": "private", "bundle-budget": "4000"}   # the planted value, in the departure's ``value``


# ---- S11: the standard ---------------------------------------------------------------------------------------

def test_s11_fabric_states_the_standard():
    from gov.adopt import fabric
    standard = fabric.STANDARD
    assert standard["reranker"] == "Qwen3-Reranker-0.6B" and standard["reranker_service"] == "shared"
    assert standard["bundle_tokens"] == 6000 and standard["widen"] == "sections"
    shipped = yaml.safe_load(W.RETRIEVAL_SRC.read_text(encoding="utf-8"))
    assert standard["pool"] == shipped["pool"], "STANDARD.pool is not retrieval.yaml's pool: block as Gov OS ships it"


def test_s11_the_record_names_the_four_settings_the_pin_the_embedder_the_reranker_and_the_digest(worlds):
    nine = worlds.a9("default")
    standard = nine.record().get("standard")
    assert isinstance(standard, dict), f"standard: {standard!r}"
    for key in ("reranker", "reranker_service", "pool", "bundle_tokens", "widen", "gov_pin", "embedder",
                "retrieval_yaml_sha256", "departures"):
        assert key in standard, f"standard.{key} is not in the record"
    assert standard["reranker"] == "Qwen3-Reranker-0.6B" and standard["reranker_service"] == "shared"
    assert standard["bundle_tokens"] == 6000 and standard["widen"] == "sections" and standard["pool"], standard
    assert standard["embedder"], "the embedder is not named"
    planted = (nine.project / "governance/project/retrieval.yaml").read_bytes()
    assert standard["retrieval_yaml_sha256"] == hashlib.sha256(planted).hexdigest(), "retrieval_yaml_sha256 is not the file's digest"
    assert standard["departures"] == [], f"the standard's own settings were named as departures: {standard['departures']}"


@pytest.mark.parametrize("variant", sorted(VARIANTS))
def test_s11_f7_a_departure_is_named_and_the_stage_is_not_ok_without_a_decision(worlds, variant):
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, f"depart-{variant}", W.retrieval_variant(variant))
    run = adoption.a9(adoption.box.base / "out")
    W.assert_refused(run, "STANDARD_DEPARTURE", f"A9 with {variant} and no decision id")
    assert VARIANTS[variant] in W.error_text(run).lower(), f"the refusal does not name the setting ({VARIANTS[variant]}): {W.error_text(run)}"


@pytest.mark.parametrize("variant", sorted(VARIANTS))
def test_s11_f7_a_departure_with_the_owners_decision_is_ok_and_cites_it(worlds, variant):
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, f"decided-{variant}", W.retrieval_variant(variant))
    run = adoption.a9(adoption.box.base / "out", "--decision", DECISION)
    W.assert_offered(run, "A9")
    assert run.returncode == 0 and run.envelope().get("ok") is True, f"A9 with {variant} and --decision {DECISION}\n{run.describe()}"
    departures = W.a9_record(adoption.project, run)["standard"]["departures"]
    assert len(departures) == 1, f"one departure expected: {departures}"
    assert VARIANTS[variant] in str(departures[0].get("setting", "")).lower(), departures
    assert departures[0].get("decision") == DECISION, f"the decision id is not cited: {departures}"
    if variant in VALUES:
        assert VALUES[variant] in str(departures[0].get("value", "")).lower(), \
            f"the departure does not carry the planted value ({VALUES[variant]}): {departures}"


# ---- S5: scale ------------------------------------------------------------------------------------------------

def test_s5_the_record_holds_a_query_time_per_route_and_the_vector_scan_against_the_budget(worlds):
    scale = worlds.a9("default").record().get("scale")
    assert isinstance(scale, dict), f"scale: {scale!r}"
    routes = scale.get("routes")
    assert isinstance(routes, dict) and len(routes) >= 3, f"scale.routes holds a query time for each route (record, lexical, vectors): {routes!r}"
    assert all(isinstance(v, (int, float)) and v >= 0 for v in routes.values()), routes
    assert isinstance(scale.get("vector_scan_ms"), (int, float)) and scale["vector_scan_ms"] >= 0
    assert isinstance(scale.get("budget_ms"), (int, float)) and scale["budget_ms"] > 0, "scale.budget_ms (the retrieve budget) is not a figure"
    assert scale.get("envelope"), "scale.envelope (DEC-078's) is not stated"


def test_s5_a_proposal_exists_exactly_when_a_figure_is_over_the_budget(worlds):
    """The proposal file (a CIT-P form) is written for an over-budget figure and only then: this holds the record and the file
    to each other on the default budget (``fabric.RETRIEVE_BUDGET_MS``); the planted over-budget case is the next one."""
    nine = worlds.a9("default")
    record = nine.record()
    scale = record["scale"]
    over = scale["vector_scan_ms"] > scale["budget_ms"]
    proposal = nine.out / "SCALE-PROPOSAL.md"
    assert proposal.is_file() == over, f"vector_scan_ms {scale['vector_scan_ms']} vs budget_ms {scale['budget_ms']}: SCALE-PROPOSAL.md present={proposal.is_file()}"


def ledger(count: int = 150) -> dict:
    """``count`` small notes of the harbour's embedded namespace (``docs/**``), so the vector scan has more than a handful of
    vectors to pass over (a scan of 1 ms is then over a budget of 1 ms with room)."""
    return {f"docs/ledger/entry-{n:03d}.md":
            f"# Ledger entry {n}\n\n" + f"The harbour master recorded tide {n * 7 % 23} and berth {n * 13 % 31} for vessel {n}.\n" * 6
            for n in range(count)}


def figure_forms(value: float, budget: int) -> list:
    """The spellings of a millisecond figure a proposal may print (the budget's own digit is not a figure of the scan)."""
    forms = {str(value), f"{value:.1f}", f"{value:.2f}", f"{value:.3f}", str(round(value)), str(math.ceil(value))}
    return sorted(form for form in forms if form != str(budget))


def assert_cit_p_form(text: str) -> None:
    """A CIT-P form: a title, the name CIT-P, and sections for the evidence (the measure) and the proposal."""
    assert re.search(r"^# \S", text, re.MULTILINE), "the proposal has no title (a `# ` heading)"
    assert re.search(r"CIT-P", text, re.IGNORECASE), "the proposal does not name its form (CIT-P)"
    headings = re.findall(r"^#{2,3} +(.+)$", text, re.MULTILINE)
    assert any(re.search(r"evidence|measure|trigger|figure", h, re.IGNORECASE) for h in headings), f"no evidence section: {headings}"
    assert any(re.search(r"proposal|option|impact|what changes", h, re.IGNORECASE) for h in headings), f"no proposal section: {headings}"


def test_s5_a_budget_of_one_millisecond_is_recorded_over_and_proposed_and_no_store_file_changes(worlds):
    """P-1 (a): ``gov adopt --lite --stage A9 --budget-ms 1`` plants a retrieve budget no scan can keep to. The ``scale`` block
    records ``budget_ms`` 1 and a ``vector_scan_ms`` over it; ``<out>/SCALE-PROPOSAL.md`` (a CIT-P form) holds the figure; the
    stage stays ok (a figure over the budget is a proposal, never a failure); and no store file changes: what is compared is the
    sha256 of ``.gov-runtime/store.db`` and of every file under ``.gov-runtime/codeintel/`` (``store_hash``, SQLite's side files
    left out), taken the moment ``gov.rebuild.command.run`` returns (the build is done) and again once the stage's process has
    ended (the scale step, the proposal and the record are done)."""
    nine = worlds.a9("scale-wide", run_a9=False, plant_options={"extra": ledger()})
    nine.need_chain()
    out = nine.box.base / "budget-out"
    done = subprocess.run([sys.executable, str(W.HERE / "a9_hash_stores.py"), "adopt", "--lite", "--stage", "A9", "--out", str(out),
                           "--budget-ms", "1", "--json", "--session", W.SESSION], cwd=str(nine.project), env=nine.adoption.env(),
                          capture_output=True, text=True, timeout=900, stdin=subprocess.DEVNULL)
    run = W.S124.Run(("adopt", "--lite", "--stage", "A9", "--budget-ms", "1"), done.returncode, done.stdout, done.stderr, 0.0)
    W.assert_offered(run, "A9")
    assert "unrecognized arguments" not in done.stderr, f"gov adopt --lite --stage A9 does not take --budget-ms\n{run.describe()}"
    W.assert_ok(run, "A9 with --budget-ms 1 (a figure over the budget is a proposal, no failure)")
    scale = W.a9_record(nine.project, run)["scale"]
    assert scale.get("budget_ms") == 1, f"scale.budget_ms is {scale.get('budget_ms')!r}, the planted budget is 1"
    scan = scale.get("vector_scan_ms")
    assert isinstance(scan, (int, float)) and scan > 1, \
        f"scale.vector_scan_ms is {scan!r}: not over the planted budget of 1 ms (the adoption holds 150+ embedded notes)"
    proposal = out / "SCALE-PROPOSAL.md"
    assert proposal.is_file(), f"vector_scan_ms {scan} is over budget_ms 1 and no {proposal.name} is written under --out"
    text = proposal.read_text(encoding="utf-8")
    assert_cit_p_form(text)
    assert any(re.search(rf"(?<![\d.]){re.escape(form)}(?!\d)", text) for form in figure_forms(scan, 1)), \
        f"the proposal does not hold the measured figure ({scan} ms; forms {figure_forms(scan, 1)})"
    hashed = [line for line in done.stderr.splitlines() if line.startswith("store-hash-after-build:")]
    assert hashed, ("the plant did not take: no store hash was taken after gov.rebuild.command.run returned "
                    f"(A9 runs it in full, in-process: I3)\n{run.describe()}")
    after_build = json.loads(hashed[-1].split(":", 1)[1])
    assert ".gov-runtime/store.db" in after_build, f"no store.db after the build: {sorted(after_build)}"
    after_stage = store_hash.digest(nine.project)
    changed = sorted(name for name in set(after_build) | set(after_stage) if after_build.get(name) != after_stage.get(name))
    assert not changed, f"the over-budget proposal changed store files (sha256 after the build vs after the stage): {changed}"


# ---- S6: measure ----------------------------------------------------------------------------------------------

def test_s6_the_record_holds_the_measure_and_a_residual_is_named_with_its_cause(worlds):
    nine = worlds.a9("default")
    run = nine.need_a9()
    assert run.returncode == 0, f"a low (or absent) measure made the stage not ok: no bar\n{run.describe()}"
    measure = nine.record().get("measure")
    assert isinstance(measure, dict), f"measure: {measure!r}"
    for key in ("right_e2e", "wrong_claims", "hit_at_5"):
        assert key in measure, f"measure.{key} is not in the record"
    residuals = measure.get("residuals")
    assert isinstance(residuals, list), f"measure.residuals: {residuals!r}"
    for item in residuals:
        assert isinstance(item, dict) and str(item.get("name", "")).strip() and str(item.get("cause", "")).strip(), \
            f"a residual is named with its cause: {item!r}"


def test_s6_the_record_names_no_proof_repository_as_having_run_the_full_practice(worlds):
    import json
    text = json.dumps(worlds.a9("default").record(), default=str)
    for word in ("S12", "S13", "S14"):
        assert word not in text, f"the record mentions {word}: no proof repository runs the full practice here"


QUESTION_WORD = "zephyrquorn"      # unique to the planted questions: nothing the stage writes may hold it


def planted_questions(path):
    """A question set in the form A9 takes (``--questions <file>``, the engineer's seam 2) whose gold paths can never be
    retrieved: none of them is a tracked file of the planted adoption."""
    document = {"form": "w2-88-questions/1", "questions": [
        {"id": "q01", "question": f"Where does the harbour keep the {QUESTION_WORD} tide ledger?",
         "gold": ["docs/never-tracked-one.md"]},
        {"id": "q02", "question": f"Which file names the {QUESTION_WORD} mooring rule?",
         "gold": ["docs/never-tracked-two.md", "lib/never_tracked.py"]},
        {"id": "q03", "question": f"Who signs the {QUESTION_WORD} berth plan?", "gold": ["archive/never-tracked.md"]},
    ]}
    path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")
    return path


def test_s6_a_question_set_whose_gold_is_never_retrieved_is_a_named_residual_and_no_failure(worlds):
    """P-1 (b): ``--questions <file>`` (outside the project) whose gold paths are tracked nowhere: the stage stays ok (no bar),
    ``measure.hit_at_5`` (and ``right_e2e``) is 0, ``wrong_claims`` is 0 (no forbidden path was planted), ``measure.residuals``
    names the shortfall with its cause, and nothing the stage writes holds a question's text (records name questions by id):
    a unique word of the planted questions is searched for in every committed record and every file under ``--out``."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, "questions-fork")
    questions = planted_questions(nine.box.base / "questions.yaml")
    assert not str(questions).startswith(str(adoption.project)), "the question file lies inside the project"
    out = adoption.box.base / "questions-out"
    run = adoption.a9(out, "--questions", str(questions))
    W.assert_offered(run, "A9")
    assert "unrecognized arguments" not in run.stderr, f"gov adopt --lite --stage A9 does not take --questions\n{run.describe()}"
    W.assert_ok(run, "A9 with a question set that no retrieval can meet (a low figure is no failure: no bar)")
    measure = W.a9_record(adoption.project, run)["measure"]
    assert measure.get("hit_at_5") is not None and measure["hit_at_5"] == 0, f"measure.hit_at_5 is {measure.get('hit_at_5')!r}, not 0"
    assert measure.get("right_e2e") is not None and measure["right_e2e"] == 0, f"measure.right_e2e is {measure.get('right_e2e')!r}, not 0"
    assert measure.get("wrong_claims") == 0, f"measure.wrong_claims is {measure.get('wrong_claims')!r}: no forbidden path was planted"
    residuals = measure.get("residuals")
    assert isinstance(residuals, list) and residuals, f"measure.residuals names no shortfall: {residuals!r}"
    for item in residuals:
        assert isinstance(item, dict) and str(item.get("name", "")).strip() and str(item.get("cause", "")).strip(), \
            f"a residual is named with its cause: {item!r}"
    assert not any(item.get("name") == "questions" for item in residuals), \
        f"a question set was given, yet a residual says none was: {residuals}"
    assert any(re.search(r"hit|gold|retriev|miss|recall|rank", f"{item['name']} {item['cause']}", re.IGNORECASE) for item in residuals), \
        f"no residual names the retrieval shortfall (hit@5 is 0): {residuals}"
    held = {}
    for rel in W.git(adoption.project, "ls-files", "governance/adoption").splitlines():
        held[rel] = W.git(adoption.project, "show", f"HEAD:{rel}").encode()
    held.update(W.all_text(out))
    assert any(name.startswith("governance/adoption/") for name in held) and len(held) >= 2, "the run left nothing to search"
    assert not [name for name, data in held.items() if QUESTION_WORD.encode() in data], \
        "a question's text is in a record or an output (records name questions by id only)"
