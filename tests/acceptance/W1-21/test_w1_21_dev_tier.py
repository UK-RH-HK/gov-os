"""KPI success 3 (the RETR-A-04 and RETR-X-02 dev runs produce multi-batch bundles) [CAP-16.b] and the measure
behind KPI success 5 (the dev query set meets its recorded hit@5 and forbidden-citation baselines) [CAP-38.b].

Every case clones a dev tier (``GOV_DEV_TIERS``, by default ``~/gov-os-workbench/synthetic``) into a temporary
directory and indexes the clone, so all are ``local_only``. Two kinds:

* with the stand-in endpoint and no reranker: the form of the dev runs (batches, merge, stopping reason, checked
  citations, the missing id). No model runs.
* with the real models (``needs("ollama", "reranker")``): what is found. RETR-A-04's two files, mean hit@5 at or
  above the pass line of 80 (DEC-414), and the forbidden citations.

RETR-A-04 is scenarios/a-dev.yaml's question and its two files. RETR-X-02 (scenarios/x-dev.yaml) asks for a
record neither programme has, and for "a question spanning three locations" without naming one: the cases take
every dev query whose gold answer names three or more ``must_cite`` paths. Its context-size half is W1-36's.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

import w1_21_support as support

pytestmark = [pytest.mark.local_only, pytest.mark.needs("gitleaks", "sqlite_vec")]

REAL = pytest.mark.needs("ollama", "reranker")
DEV_RUN = {"radius": support.RADIUS_FULL}   # the default batch size: the KPI is about the dev runs as they are


def _tiers(tmp_path_factory, label, build):
    roots = {}
    for programme, tier in support.TIERS.items():
        root = support.clone_tier(tier, tmp_path_factory.mktemp(f"w1-21-{label}-{tier}") / tier)
        if root is None:
            pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
        _, semantic, _ = build(root)
        assert semantic["available"], f"the vectors of {tier} were not built: {semantic!r}"
        roots[programme] = root
    return roots


@pytest.fixture(scope="module")
def queries():
    found = support.dev_queries()
    if found is None:
        pytest.skip(f"no dev query set at {support.QUERY_SET} (GOV_DEV_TIERS)")
    return found


@pytest.fixture(scope="module")
def tiers(api, ollama, tmp_path_factory):
    """``programme -> root`` of the two tiers, indexed through the stand-in endpoint. No model runs."""
    return _tiers(tmp_path_factory, "stand-in", lambda root: api.build(root, ollama.host))


@pytest.fixture(scope="module")
def real_tiers(api, tmp_path_factory):
    """The same with this machine's Ollama and the pinned embedder."""
    return _tiers(tmp_path_factory, "real", lambda root: api.build(root, env=api.real_env()))


def ask_all(api, root, asked, env, **kwargs):
    """One process for all the questions of a tier: ``[bundle, ...]`` in the order asked."""
    outcome = api.run([(support.RETRIEVE, support.FUNCTION, [support.path_arg(root), query["query"]], kwargs)
                       for query in asked], env=env, timeout=support.MEASURE_TIMEOUT_S)
    return [support.check_bundle(outcome.value(index), root=root) for index in range(len(asked))]


def front_status(root, rel):
    """The ``status`` of the frontmatter of ``rel``, None when the file has none."""
    path = Path(root) / rel
    if path.suffix != ".md" or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        return None
    try:
        front = yaml.safe_load(text[4:text.index("\n---\n", 4)])
    except yaml.YAMLError:
        return None
    return str(front.get("status")) if isinstance(front, dict) and front.get("status") is not None else None


# ---- the form of the dev runs; no model

def test_retr_a_04_gives_a_bundle_of_several_batches(api, tiers, ollama):
    bundle = support.check_bundle(api.retrieve(tiers["A"], support.RETR_A_04_QUESTION, host=ollama.host, **DEV_RUN),
                                  root=tiers["A"])
    assert len(bundle[support.K_BATCHES]) > 1, f"RETR-A-04 was gathered in one batch: {bundle[support.K_BATCHES]!r}"
    assert bundle[support.K_EVIDENCE], "RETR-A-04 cites nothing"
    assert type(bundle[support.K_MERGE].get(support.M_CANDIDATES)) is int


@pytest.mark.parametrize("programme", sorted(support.TIERS))
def test_retr_x_02_a_record_that_does_not_exist_is_a_stated_gap(api, tiers, ollama, programme):
    """The scenario's word is NOT_FOUND, which is not a stopping reason of the fixed list: the id is a gap and
    the reason is UNRESOLVED_IDS, or FACET_UNAVAILABLE where the code tool that would look for it as a symbol is
    not installed (package DP-6). No evidence carries the id."""
    root = tiers[programme]
    bundle = support.check_bundle(api.retrieve(root, f"What does {support.RETR_X_02_MISSING_ID} decide?",
                                               host=ollama.host, ids=[support.RETR_X_02_MISSING_ID], **DEV_RUN),
                                  root=root)
    assert support.RETR_X_02_MISSING_ID in support.gap_names(bundle), bundle[support.K_GAPS]
    assert bundle[support.K_REASON] in (support.UNRESOLVED_IDS, support.FACET_UNAVAILABLE), bundle[support.K_REASON]
    assert all(item[support.E_ID] != support.RETR_X_02_MISSING_ID for item in bundle[support.K_EVIDENCE]), \
        "an evidence item was made up for the missing id"


@pytest.mark.parametrize("programme", sorted(support.TIERS))
def test_retr_x_02_a_question_spanning_three_locations_shows_batches_merge_and_reason(api, tiers, ollama, queries,
                                                                                      programme):
    asked = [query for query in queries if query["programme"] == programme
             and len(query["gold"]["must_cite"]) >= support.RETR_X_02_LOCATIONS]
    assert asked, f"the dev query set has no question of programme {programme} that spans three locations"
    bundles = ask_all(api, tiers[programme], asked, api.scratch_env(ollama.host), **DEV_RUN)
    for query, bundle in zip(asked, bundles):
        assert len(bundle[support.K_BATCHES]) > 1, f"{query['id']} was gathered in one batch"
        merge = bundle[support.K_MERGE]
        assert type(merge.get(support.M_CANDIDATES)) is int and type(merge.get(support.M_DUPLICATES)) is int and \
            isinstance(merge.get(support.M_RERANKED), bool), f"{query['id']}: the merge is not shown: {merge!r}"
        assert len({item[support.E_PATH] for item in bundle[support.K_EVIDENCE]}) >= support.RETR_X_02_LOCATIONS, \
            f"{query['id']} spans three locations and the bundle cites fewer"


@pytest.mark.parametrize("programme", sorted(support.TIERS))
def test_no_file_whose_frontmatter_says_superseded_is_cited_on_a_dev_tier(api, tiers, ollama, queries, programme):
    """KPI failure 2 on the dev tiers, whose decisions carry ``status`` and no ``type`` (package DP-4). Whatever
    the stand-in vectors return, a file that says SUPERSEDED is in no bundle."""
    root = tiers[programme]
    asked = [query for query in queries if query["programme"] == programme]
    bundles = ask_all(api, root, asked, api.scratch_env(ollama.host), **DEV_RUN)
    cited = {rel: query["id"] for query, bundle in zip(asked, bundles) for rel in support.paths(bundle)}
    wrong = {rel: asked_by for rel, asked_by in cited.items() if (front_status(root, rel) or "").upper() == "SUPERSEDED"}
    assert not wrong, f"cited although its frontmatter says SUPERSEDED: {wrong}"


# ---- what is found; the real models

@REAL
def test_retr_a_04_finds_and_cites_both_implementations(api, real_tiers):
    outcome = api.run([(support.RETRIEVE, support.FUNCTION,
                        [support.path_arg(real_tiers["A"]), support.RETR_A_04_QUESTION], DEV_RUN)],
                      env=api.real_env(), timeout=support.MEASURE_TIMEOUT_S)
    bundle = support.check_bundle(outcome.value(), root=real_tiers["A"])
    missing = set(support.RETR_A_04_EXPECTED) - set(support.paths(bundle))
    assert not missing, f"RETR-A-04 does not cite {sorted(missing)}; cited: {support.paths(bundle)[:12]}"
    assert len(bundle[support.K_BATCHES]) > 1 and bundle[support.K_MERGE].get(support.M_RERANKED) is True


@pytest.fixture(scope="module")
def measured(api, real_tiers, queries):
    """``[(query, bundle), ...]`` over the 52 dev queries, each tier in one process."""
    pairs = []
    for programme, root in real_tiers.items():
        asked = [query for query in queries if query["programme"] == programme]
        pairs += list(zip(asked, ask_all(api, root, asked, api.real_env(), **DEV_RUN)))
    return pairs


@REAL
def test_the_dev_query_set_meets_the_hit_at_5_pass_line(measured):
    """S0b2's method (DEC-380): the first five distinct paths against ``must_cite``, a percentage per class, the
    mean of the ten classes; at or above 80 on the dev tiers (DEC-414)."""
    scored, missed = {}, []
    for query, bundle in measured:
        hit = bool(set(query["gold"]["must_cite"]) & set(support.first_paths(bundle)))
        scored.setdefault(query["class"], []).append(hit)
        if not hit:
            missed.append(query["id"])
    mean, per_class = support.mean_hit_at_5(scored)
    support.MEASURED.append(f"mean hit@5 of gov.retrieval.retrieve: {mean:.2f} (pass line "
                            f"{support.HIT_AT_5_PASS_LINE:.0f}); per class {per_class}; missed {sorted(missed)}")
    assert mean >= support.HIT_AT_5_PASS_LINE, \
        f"mean hit@5 is {mean:.2f}, below the pass line of {support.HIT_AT_5_PASS_LINE:.0f}; missed: {sorted(missed)}"


@REAL
def test_the_dev_query_set_meets_the_forbidden_citation_baseline(measured):
    """S0b2 counted, per query, a ``must_not_cite`` path among the first five distinct paths: 5 for R1. The
    baseline here is 2 (package DP-7): the two b-dev files that no frontmatter marks."""
    forbidden = [(query["id"], rel) for query, bundle in measured
                 for rel in support.first_paths(bundle) if rel in query["gold"]["must_not_cite"]]
    support.MEASURED.append(f"forbidden citations in the first five of gov.retrieval.retrieve: {len(forbidden)} "
                            f"(baseline {support.FORBIDDEN_BASELINE}): {forbidden}")
    assert len(forbidden) <= support.FORBIDDEN_BASELINE, f"{len(forbidden)} forbidden citations: {forbidden}"


@REAL
def test_every_measured_bundle_was_reranked_from_both_routes(measured):
    for query, bundle in measured:
        assert bundle[support.K_FACETS][support.ROUTE_SEMANTIC]["available"] is True, query["id"]
        assert bundle[support.K_MERGE].get(support.M_RERANKED) is True, f"{query['id']}: nothing was reranked"
