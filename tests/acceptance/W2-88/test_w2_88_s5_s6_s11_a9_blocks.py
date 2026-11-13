"""S5 scale (success-5), S6 measure (success-6), S11 the standard (success-11), F7 (failure-7); I3, I4: the A9 record's
``scale``, ``measure`` and ``standard`` blocks and the stage's ``STANDARD_DEPARTURE``.

The standard (I3, as decided by P-W2-88-B-1: DEC-1157 (3), (12)): ``fabric.STANDARD = {reranker: "Qwen3-Reranker-0.6B",
reranker_service: "shared", pool: <retrieval.yaml's pool: block as Gov OS ships it>, bundle_tokens: 6000, widen: "sections"}``.
A departure is a setting that differs from it: the stage is not ok (``STANDARD_DEPARTURE``) unless ``--decision DEC-n`` is given,
which the record then cites. What departs where (B-1.2, B-1.4):

- **the pool** departs through the repository's ``retrieval.yaml`` in force: the whole ``pool:`` block is the standard, a key that
  differs (a value changed, a key missing or added, or no block) is a departure ``{setting: "pool", value: <the file's block, or
  false when there is none or meaning_uncut is not true>}``;
- **the reranker and the bundle** are the pin's constants (``gov.retrieval.rerank.MODEL`` (its last ``/`` part),
  ``rerank.CACHE_REL``/``SOCKET`` (``"shared"`` when they are ``.cache/gov-os``/``rerank.sock``, else ``"<CACHE_REL>/<SOCKET>"``) and
  ``gov.retrieval.retrieve.BUNDLE_BUDGET``): ``fabric.settings_of(doc)`` reads them, ``fabric.departures(doc)`` names a departing one,
  ``fabric.read_standard(root, decisions)`` refuses it (``STANDARD_DEPARTURE``, the setting in ``details["settings"]``) without a
  decision and returns the block citing the decision with one; a ``retrieval.yaml`` in force holding a top-level ``rerank`` or ``bundle``
  key is refused ``CONFIG_INVALID`` naming the key, before any store is built, whatever the ``--decision`` (``gov.config.loader`` may
  refuse it first: either is the decided behaviour).

The departure is named in ``departures`` by ``fabric.STANDARD``'s own name (``pool``, ``reranker``, ``reranker_service``,
``bundle_tokens``). The planted over-budget (S5, ``--budget-ms``), unmeasured-scan (RV1-2) and low-measure (S6, ``--questions``) cases
are at the end of each section (P-1, the engineer's seams 1 and 2; the scan seam ``fabric.vector_scan``).
"""

from __future__ import annotations

import hashlib
import json
import math
import re

import pytest
import yaml

import w2_88_support as W
import store_hash

DECISION = "DEC-9999"
VARIANTS = {"pool-off": "pool", "pool-depth": "pool"}               # departures through retrieval.yaml (the pool only, B-1.2)
POOL_VALUES = {"pool-off": False, "pool-depth": "route_depth"}       # the departure's ``value``: false, or the file's block
PIN_KEYS = {"second-reranker": "rerank", "bundle-budget": "bundle"}  # keys the pin owns: CONFIG_INVALID naming the key
SHIPPED = yaml.safe_load(W.RETRIEVAL_SRC.read_text(encoding="utf-8"))


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
    value = departures[0].get("value")
    if variant == "pool-off":           # B-1.4: false where meaning_uncut is not true
        assert value is False, f"a pool whose meaning_uncut is off is {{setting: pool, value: false}}: {departures}"
    else:                                # the file's own block, with the key that differs
        assert isinstance(value, dict) and value.get("route_depth") == 5, f"the departure does not carry the file's pool block: {departures}"


# ---- B-1.2: the reranker and the bundle are the pin's constants; a retrieval.yaml key for them is CONFIG_INVALID ----

@pytest.mark.parametrize("decided", [False, True], ids=["no-decision", "with-decision"])
@pytest.mark.parametrize("variant", sorted(PIN_KEYS))
def test_s11_f7_a_rerank_or_bundle_key_is_config_invalid_naming_it_and_no_decision_makes_it_ok(worlds, variant, decided):
    """B-1.2 (a decided-behaviour revision, DEC-1157 (12)): a ``retrieval.yaml`` in force holding a top-level ``rerank`` or ``bundle`` key
    is refused ``CONFIG_INVALID``, the key named (and in ``details["keys"]`` when A9 raises it), before any store is built; a ``--decision``
    does not make it ok; nothing is written in the repository's tree. (``gov.config.loader`` refuses the key on the CLI path today: it
    may refuse first with its own ``CONFIG_INVALID`` naming it, which is the decided behaviour too.)"""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, f"pin-key-{variant}-{decided}", W.retrieval_variant(variant))
    head = W.head(adoption.project)
    run = adoption.a9(adoption.box.base / "out", *(("--decision", DECISION) if decided else ()))
    W.assert_refused(run, "CONFIG_INVALID", f"A9 with a retrieval.yaml holding {PIN_KEYS[variant]}: and decision={decided}")
    assert PIN_KEYS[variant] in W.error_text(run), f"the refusal does not name the key {PIN_KEYS[variant]!r}: {W.error_text(run)}"
    keys = (run.error.get("details") or {}).get("keys")
    if keys is not None:
        assert PIN_KEYS[variant] in keys, f"details['keys'] is {keys!r}, the key is {PIN_KEYS[variant]!r}"
    assert not (adoption.project / ".gov-runtime/store.db").exists(), "a store was built before the key was refused"
    assert W.head(adoption.project) == head and W.git(adoption.project, "status", "--porcelain") == "", "a refused A9 wrote in the repository"


# ---- B-1.2, in-process: the pin's constants (rerank.MODEL, rerank.SOCKET, retrieve.BUNDLE_BUDGET) -------------------

CONSTANTS = {   # name -> (module, constant, planted value, setting named, the setting's value)
    "another-reranker-model": ("gov.retrieval.rerank", "MODEL", "Org/Other-Reranker", "reranker", "Other-Reranker"),
    "a-second-reranker-socket": ("gov.retrieval.rerank", "SOCKET", "private.sock", "reranker_service", ".cache/gov-os/private.sock"),
    "another-bundle-budget": ("gov.retrieval.retrieve", "BUNDLE_BUDGET", 4000, "bundle_tokens", 4000),
}


def plant_constant(monkeypatch, name):
    import importlib
    module, constant, value, setting, expected = CONSTANTS[name]
    monkeypatch.setattr(importlib.import_module(module), constant, value)
    return setting, expected


def setting_names(details) -> list:
    """The names in ``details["settings"]`` (a list of names, or of items holding a ``setting``)."""
    items = (details or {}).get("settings") or []
    return [i if isinstance(i, str) else (i or {}).get("setting") for i in items]


def standard_root(box):
    """A planted adoption (no chain run) whose tracked retrieval.yaml is Gov OS's as shipped: the root ``read_standard`` reads."""
    return W.plant_adoption(box)


def test_s11_the_pins_constants_as_they_stand_are_the_standard_and_no_departure(monkeypatch):
    """GUARD: with the pin's constants untouched, ``settings_of`` reads the standard's four settings and nothing departs."""
    from gov.adopt import fabric
    from gov.retrieval import rerank, retrieve
    settings = fabric.settings_of(SHIPPED)
    assert settings["reranker"] == rerank.MODEL.rsplit("/", 1)[-1] == fabric.STANDARD["reranker"], settings
    assert settings["bundle_tokens"] == retrieve.BUNDLE_BUDGET == fabric.STANDARD["bundle_tokens"], settings
    assert settings["reranker_service"] == "shared" == fabric.STANDARD["reranker_service"], settings
    assert settings["widen"] == "sections", settings
    assert fabric.departures(SHIPPED) == [], f"the pin's own constants are named as departures: {fabric.departures(SHIPPED)}"


@pytest.mark.parametrize("name", sorted(CONSTANTS))
def test_s11_f7_a_pin_constant_that_departs_is_named_by_departures_with_its_value(monkeypatch, name):
    from gov.adopt import fabric
    setting, expected = plant_constant(monkeypatch, name)
    assert fabric.settings_of(SHIPPED)[setting] == expected, f"settings_of does not read {setting} from the constant: {fabric.settings_of(SHIPPED)}"
    found = [d for d in fabric.departures(SHIPPED) if d.get("setting") == setting]
    assert len(found) == 1, f"fabric.departures does not name {setting}: {fabric.departures(SHIPPED)}"
    assert str(found[0].get("value")) == str(expected), f"the departure's value is {found[0].get('value')!r}, not {expected!r}"
    assert len(fabric.departures(SHIPPED)) == 1, f"only {setting} departs: {fabric.departures(SHIPPED)}"


@pytest.mark.parametrize("name", sorted(CONSTANTS))
def test_s11_f7_read_standard_refuses_a_pin_constant_that_departs_without_a_decision(monkeypatch, box, name):
    from gov.adopt import fabric
    from gov.cli.errors import GovError
    setting, _ = plant_constant(monkeypatch, name)
    with pytest.raises(GovError) as raised:
        fabric.read_standard(standard_root(box), [])
    assert raised.value.code == "STANDARD_DEPARTURE", f"{raised.value.code} for a departing {setting}"
    assert setting in setting_names(raised.value.details), f"details['settings'] is {raised.value.details.get('settings')!r}, not naming {setting}"


@pytest.mark.parametrize("form", ["{d}", "{d}:{s}"], ids=["decision", "decision-for-setting"])
@pytest.mark.parametrize("name", sorted(CONSTANTS))
def test_s11_f7_read_standard_with_a_decision_returns_the_block_citing_it(monkeypatch, box, name, form):
    from gov.adopt import fabric
    setting, _ = plant_constant(monkeypatch, name)
    block = fabric.read_standard(standard_root(box), [form.format(d="DEC-1", s=setting)])
    found = [d for d in block["departures"] if d.get("setting") == setting]
    assert len(found) == 1 and found[0].get("decision") == "DEC-1", f"the block's departures: {block['departures']}"


# ---- B-1.4 (RV1-1): the pool is the whole shipped block --------------------------------------------------------------

def without(block, key):
    return {k: v for k, v in block.items() if k != key}


POOLS = {   # name -> (the document, the departure's value: a block, or False)
    "a-value-changed": ({"pool": {**SHIPPED["pool"], "route_depth": 5}}, {**SHIPPED["pool"], "route_depth": 5}),
    "a-key-missing": ({"pool": without(SHIPPED["pool"], "per_file_first10")}, without(SHIPPED["pool"], "per_file_first10")),
    "a-key-added": ({"pool": {**SHIPPED["pool"], "extra_depth": 3}}, {**SHIPPED["pool"], "extra_depth": 3}),
    "no-block": ({"routing": SHIPPED["routing"]}, False),
    "meaning-off": ({"pool": {**SHIPPED["pool"], "meaning_uncut": False}}, False),
}


def test_s11_f7_a_pool_block_equal_to_the_shipped_one_is_no_departure():
    from gov.adopt import fabric
    assert fabric.departures({"pool": dict(SHIPPED["pool"])}) == [], "a pool equal to the shipped block is named as a departure"
    assert fabric.departures(SHIPPED) == []
    assert fabric.STANDARD["pool"] == SHIPPED["pool"], "STANDARD.pool is not the whole pool: block as Gov OS ships it"


@pytest.mark.parametrize("name", sorted(POOLS))
def test_s11_f7_a_pool_differing_from_the_shipped_block_in_any_key_is_a_departure_with_its_value(name):
    from gov.adopt import fabric
    document, expected = POOLS[name]
    found = [d for d in fabric.departures(document) if d.get("setting") == "pool"]
    assert len(found) == 1, f"fabric.departures({sorted(document)}) does not name the pool: {fabric.departures(document)}"
    if expected is False:
        assert found[0].get("value") is False, f"value is {found[0].get('value')!r}: false where there is no block or meaning_uncut is not true"
    else:
        assert found[0].get("value") == expected, f"value is {found[0].get('value')!r}, the file's block is {expected!r}"


# ---- S5: scale ------------------------------------------------------------------------------------------------

def test_s5_the_record_holds_a_query_time_per_route_and_the_vector_scan_against_the_budget(worlds):
    scale = worlds.a9("default").record().get("scale")
    assert isinstance(scale, dict), f"scale: {scale!r}"
    routes = scale.get("routes")
    assert isinstance(routes, dict) and len(routes) >= 3, f"scale.routes holds a query time for each route (record, lexical, vectors): {routes!r}"
    assert all(isinstance(v, (int, float)) and v >= 0 for v in routes.values()), routes
    scan = scale.get("vector_scan_ms")
    if scan is None:      # RV1-2: a figure only when the semantic route answered available: true; else null, and the reason says why
        assert str(scale.get("vector_scan_reason") or "").strip(), \
            f"scale.vector_scan_ms is null and scale.vector_scan_reason does not say why: {scale!r}"
    else:
        assert isinstance(scan, (int, float)) and not isinstance(scan, bool) and scan >= 0, f"scale.vector_scan_ms: {scan!r}"
    assert isinstance(scale.get("budget_ms"), (int, float)) and scale["budget_ms"] > 0, "scale.budget_ms (the retrieve budget) is not a figure"
    assert scale.get("envelope"), "scale.envelope (DEC-078's) is not stated"


def test_s5_a_proposal_exists_exactly_when_a_figure_is_over_the_budget(worlds):
    """The proposal file (a CIT-P form) is written for an over-budget figure and only then: this holds the record and the file
    to each other on the default budget (``fabric.RETRIEVE_BUDGET_MS``); the planted over-budget and unmeasured cases follow. An
    unmeasured scan (``vector_scan_ms`` null) is never compared with the budget (RV1-2)."""
    nine = worlds.a9("default")
    record = nine.record()
    scale = record["scale"]
    scan = scale.get("vector_scan_ms")
    over = scan is not None and scan > scale["budget_ms"]
    proposal = nine.out / "SCALE-PROPOSAL.md"
    assert proposal.is_file() == over, f"vector_scan_ms {scan} vs budget_ms {scale['budget_ms']}: SCALE-PROPOSAL.md present={proposal.is_file()}"


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


def scale_run(worlds, name, scan, *, budget=1):
    """A fork of the planted adoption at A8, A9 run in the child with ``--budget-ms <budget>`` and the scan seam
    ``fabric.vector_scan`` replaced by the stand-in ``scan`` (RV1-2); returns ``(adoption, run, process, out)``."""
    nine = worlds.a9("a8-for-forks", run_a9=False)
    nine.need_chain()
    adoption = W.fork(nine, name)
    out = adoption.box.base / "scale-out"
    run, done = W.run_a9_child(adoption, out, "--budget-ms", str(budget), scan=scan)
    W.assert_offered(run, "A9")
    assert "unrecognized arguments" not in done.stderr, f"gov adopt --lite --stage A9 does not take --budget-ms\n{run.describe()}"
    return adoption, run, done, out


def test_s5_a_measured_scan_over_a_budget_of_one_millisecond_is_recorded_proposed_and_no_store_file_changes(worlds):
    """P-1 (a), revised for RV1-2: ``gov adopt --lite --stage A9 --budget-ms 1`` with the semantic route's reply planted through the
    seam (``fabric.vector_scan`` answers ``available: True`` after 0.05 s: a measured scan over the budget). The ``scale`` block
    records ``budget_ms`` 1 and a ``vector_scan_ms`` over it; ``<out>/SCALE-PROPOSAL.md`` (a CIT-P form) holds the figure; the stage
    stays ok (a figure over the budget is a proposal, never a failure); and no store file changes: what is compared is the sha256 of
    ``.gov-runtime/store.db`` and of every file under ``.gov-runtime/codeintel/`` (``store_hash``, SQLite's side files left out), taken
    the moment ``gov.rebuild.command.run`` returns (the build is done) and again once the stage's process has ended (the scale step,
    the proposal and the record are done)."""
    adoption, run, done, out = scale_run(worlds, "scale-measured", "slow")
    W.assert_ok(run, "A9 with --budget-ms 1 (a figure over the budget is a proposal, no failure)")
    scale = W.a9_record(adoption.project, run)["scale"]
    assert scale.get("budget_ms") == 1, f"scale.budget_ms is {scale.get('budget_ms')!r}, the planted budget is 1"
    scan = scale.get("vector_scan_ms")
    assert isinstance(scan, (int, float)) and scan > 1, f"scale.vector_scan_ms is {scan!r}: a planted scan of 0.05 s is a figure over 1 ms"
    proposal = out / "SCALE-PROPOSAL.md"
    assert proposal.is_file(), f"vector_scan_ms {scan} is over budget_ms 1 and no {proposal.name} is written under --out"
    text = proposal.read_text(encoding="utf-8")
    assert_cit_p_form(text)
    assert any(re.search(rf"(?<![\d.]){re.escape(form)}(?!\d)", text) for form in figure_forms(scan, 1)), \
        f"the proposal does not hold the measured figure ({scan} ms; forms {figure_forms(scan, 1)})"
    after_build = W.stderr_json(done, "store-hash-after-build:")
    assert after_build, ("the plant did not take: no store hash was taken after gov.rebuild.command.run returned "
                         f"(A9 runs it in full, in-process: I3)\n{run.describe()}")
    assert ".gov-runtime/store.db" in after_build, f"no store.db after the build: {sorted(after_build)}"
    after_stage = store_hash.digest(adoption.project)
    changed = sorted(name for name in set(after_build) | set(after_stage) if after_build.get(name) != after_stage.get(name))
    assert not changed, f"the over-budget proposal changed store files (sha256 after the build vs after the stage): {changed}"


@pytest.mark.parametrize("scan,why", [("unavailable", "FACET_UNAVAILABLE: planted"), ("raises", "RuntimeError")],
                         ids=["route-unavailable", "route-raises"])
def test_s5_a_scan_that_did_not_run_is_null_with_its_reason_and_is_never_compared_with_the_budget(worlds, scan, why):
    """RV1-2: ``scale.vector_scan_ms`` is a figure only when the semantic route answered ``available: true``. The route answers
    unavailable (its ``reason``) or raises (the error's name): ``vector_scan_ms`` is null, ``scale.vector_scan_reason`` names why, the
    stage is ok, and a null scan is never compared with the budget (budget 1 ms): no ``SCALE-PROPOSAL.md``. The routes' times are
    recorded and not compared (they are over 1 ms and write no proposal)."""
    adoption, run, done, out = scale_run(worlds, f"scale-{scan}", scan)
    W.assert_ok(run, f"A9 with --budget-ms 1 and a semantic route that {scan} (an unmeasured scan is no failure)")
    scale = W.a9_record(adoption.project, run)["scale"]
    assert "vector_scan_ms" in scale and scale["vector_scan_ms"] is None, \
        f"scale.vector_scan_ms is {scale.get('vector_scan_ms')!r}: a scan the route did not answer is no figure (null)"
    assert why in str(scale.get("vector_scan_reason") or ""), f"scale.vector_scan_reason is {scale.get('vector_scan_reason')!r}, not naming {why!r}"
    assert scale.get("budget_ms") == 1
    routes = scale.get("routes")
    assert isinstance(routes, dict) and len(routes) >= 3 and all(isinstance(v, (int, float)) for v in routes.values()), routes
    assert not (out / "SCALE-PROPOSAL.md").exists(), "a scan that did not run was compared with the budget: SCALE-PROPOSAL.md is written"


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
