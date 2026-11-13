"""S5 scale (success-5), S6 measure (success-6), S11 the standard (success-11), F7 (failure-7); I3, I4: the A9 record's
``scale``, ``measure`` and ``standard`` blocks and the stage's ``STANDARD_DEPARTURE``.

The standard (I3): ``fabric.STANDARD = {reranker: "Qwen3-Reranker-0.6B", reranker_service: "shared", pool: <retrieval.yaml's
pool: block as Gov OS ships it>, bundle_tokens: 6000, widen: "sections"}``. A departure is a setting of the adopted
repository's ``retrieval.yaml`` that differs from it, stated under ``fabric.STANDARD``'s own names (``pool`` removed,
``reranker`` another, ``bundle_tokens`` another): the stage is not ok (``STANDARD_DEPARTURE``) unless ``--decision DEC-n``
is given, which the record then cites.
"""

from __future__ import annotations

import hashlib

import pytest
import yaml

import w2_88_support as W

DECISION = "DEC-9999"
VARIANTS = {"pool-off": "pool", "second-reranker": "reranker", "bundle-budget": "bundle"}


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
    """The proposal file (a CIT-P form) is written for an over-budget figure and only then; the planted over-budget case
    has no seam in the Interface (package P-1), so this holds the record and the file to each other."""
    nine = worlds.a9("default")
    record = nine.record()
    scale = record["scale"]
    over = scale["vector_scan_ms"] > scale["budget_ms"]
    proposal = nine.out / "SCALE-PROPOSAL.md"
    assert proposal.is_file() == over, f"vector_scan_ms {scale['vector_scan_ms']} vs budget_ms {scale['budget_ms']}: SCALE-PROPOSAL.md present={proposal.is_file()}"


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
