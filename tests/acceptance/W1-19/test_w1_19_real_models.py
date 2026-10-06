"""The measured KPI lines, with the real models: success 1 and 3 on the fixture, success 2 and failure 1 and 2 on
the dev tiers [CAP-10.a, CAP-18.a].

Every case here needs what the install packages of the README name: ``sqlite_vec``, the Ollama executable with
``qwen3-embedding:0.6b``, and for the dev-tier cases the Qwen3 reranker with its libraries. A case skips, with
the reason, when one is absent; nothing is installed or downloaded by a test (the Hugging Face libraries are held
offline). The calls run in this machine's own environment, so ``gov`` starts the real ``ollama serve`` and, as
DEC-261 decides, leaves it running.

The default reranker is a process of its own, started from ``~/.local/share/gov-os/reranker-venv`` (DEC-397). One
case holds that with the real reranker and no index; it needs neither Ollama nor ``sqlite_vec``.

**Run this file alone**, never beside another suite: the ticket is heavy, and the timed case is a latency case
(DEC-372).

The dev-tier measurement is taken once for the file (DEC-373): per tier, one process builds the index of a clone,
asks three warm-up questions, then asks each question of the dev query set once, timed, while the peak resident
memory of that process and of every process it starts (the Ollama daemon left out) is watched.

Mean hit@5 follows S0b2's own method (DEC-380): the first five distinct paths of each query against its
``must_cite``, a percentage per class, and the mean of the ten classes. The pass line is 80 on the dev tiers
(DEC-414); the measured mean, and where it stands against the S0b2 R1 baseline of 85, is shown in the terminal
summary whether the case passes or fails.
"""

from __future__ import annotations

import pytest

import w1_19_support as support

ROOT = support.path_arg
pytestmark = pytest.mark.local_only
EMBEDDER = pytest.mark.needs("gitleaks", "sqlite_vec", "ollama")
FULL = pytest.mark.needs("gitleaks", "sqlite_vec", "ollama", "reranker")


@EMBEDDER
def test_the_pinned_embedder_reaches_a_section_from_a_paraphrase_and_the_manifest_names_it(api, repo):
    env = api.real_env()
    outcome = api.run([(support.SEMANTIC, "refresh", (ROOT(repo),), {}),
                       (support.SEMANTIC, "search", (ROOT(repo), support.PARAPHRASE), {"refresh": False}),
                       (support.SEMANTIC, "manifest", (ROOT(repo),), {})], env=env, timeout=support.MEASURE_TIMEOUT_S)
    report, answer, manifest = outcome.values()
    assert support.check_facet(report, support.SEMANTIC_FACET)["available"] is True, \
        f"the vectors were not built with the real model: {report!r}"
    support.check_semantic(answer)
    heading = support.CORPUS[support.RUNBOOK].splitlines().index(support.PARAPHRASE_HEADING) + 1
    top = [(hit["path"], hit["start_line"]) for hit in answer["hits"][:5]]
    assert any(path == support.RUNBOOK and start >= heading for path, start in top), \
        f"the paraphrase did not reach the section it asks about in the first five results: {top}"
    assert manifest["embedder"]["model"] == support.EMBED_MODEL
    assert support.is_revision(manifest["embedder"]["revision"], support.EMBED_REVISION), \
        f"the manifest does not record the pinned revision {support.EMBED_REVISION}: {manifest['embedder']!r}"
    assert (manifest["reranker"]["model"], manifest["reranker"]["revision"]) == \
        (support.RERANK_MODEL, support.RERANK_REVISION)


RERANK_QUERY = "where is the quartz seam"
RERANK_CANDIDATES = [
    {"chunk_id": name, "path": f"notes/{name}.md", "start_line": 1, "end_line": 3, "parent_id": f"parent-of-{name}",
     "text": text}
    for name, text in (("plain", "Nothing of interest stands here."),
                       ("seam", "The quartz seam runs under the yard, east of the old kiln."),
                       ("tides", "The harbour pilot reads the tide tables at dawn."))
]


@pytest.mark.needs("reranker")
def test_the_default_reranker_is_a_process_of_its_own_started_from_the_reranker_environment(api):
    # DEC-397 and ADR-0002 §2. No `reranker` is given, in this machine's own environment: the default scores the
    # candidates in a process started with the interpreter of ~/.local/share/gov-os/reranker-venv, never one of the
    # workbench, and the calling process loads none of the reranker's libraries. How the two processes talk to each
    # other is not looked at.
    outcome = api.run([(support.RERANK, "rerank", (RERANK_QUERY, RERANK_CANDIDATES), {})], env=api.real_env(),
                      watch=True, timeout=support.MEASURE_TIMEOUT_S)
    call = outcome.calls[0]
    assert call["error"] is None, f"rerank raised with the default reranker: {call['error']}"
    ordered = outcome.value()
    assert sorted(entry["chunk_id"] for entry in ordered) == sorted(entry["chunk_id"] for entry in RERANK_CANDIDATES)
    scores = [entry.get("rerank_score") for entry in ordered]
    assert all(isinstance(score, float) for score in scores), \
        f"the default reranker scored nothing although its environment and its snapshot are here: {ordered!r}"
    assert scores == sorted(scores, reverse=True), f"the candidates are not in the order of their scores: {scores}"
    assert ordered[0]["chunk_id"] == "seam", \
        f"the pinned reranker does not put the one text that answers the question first: {ordered!r}"
    assert outcome.loads == 0, "the tests' stand-in reranker was used: it was not given"
    assert outcome.heavy_after_import == [] and call["heavy_after"] == [], \
        f"the calling process loaded {call['heavy_after'] or outcome.heavy_after_import}: the reranker is a " \
        "process of its own (ADR-0002 §2)"
    started = [peak["argv"] for peak in outcome.peaks if not peak["self"]]
    interpreter = support.reranker_python()
    assert any(support.started_from(peak, interpreter) for peak in outcome.peaks if not peak["self"]), \
        f"no process started with {interpreter} was seen under the calling process (DEC-397): {started}"
    for peak in outcome.peaks:
        if not peak["self"] and support.is_python(peak):
            assert support.started_from(peak, interpreter), \
                f"a Python process was started from another interpreter than {interpreter}: {peak['argv']}"
        assert not any(support.WORKBENCH_NAME in part for part in peak["argv"][:1]), \
            f"a process was started from the workbench, where the S0b2 environment lives (DEC-397): {peak['argv']}"


@pytest.fixture(scope="module")
def measured(api, tmp_path_factory):
    """``tier -> {"queries", "answers", "seconds", "peaks"}`` for the two dev tiers, one after the other."""
    queries = support.dev_queries()
    if queries is None:
        pytest.skip(f"no dev query set at {support.QUERY_SET} (GOV_DEV_TIERS)")
    results = {}
    for programme, tier in support.TIERS.items():
        root = support.clone_tier(tier, tmp_path_factory.mktemp(f"w1-19-{tier}") / tier)
        if root is None:
            pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
        asked = [query for query in queries if query["programme"] == programme]
        # The whole reranked list: S0b2 scores the first five distinct paths, which may lie beyond the fifth chunk.
        search = {"limit": None, "refresh": False}
        calls = [(support.SEMANTIC, "refresh", (ROOT(root),), {})]
        calls += [(support.FUSION, "search", (ROOT(root), text), search) for text in support.WARM_UP_QUERIES]
        calls += [(support.FUSION, "search", (ROOT(root), query["query"]), search) for query in asked]
        outcome = api.run(calls, env=api.real_env(), watch=True, timeout=support.MEASURE_TIMEOUT_S)
        values = outcome.values()
        assert support.check_facet(values[0], support.SEMANTIC_FACET)["available"] is True, \
            f"the vectors of {tier} were not built: {values[0]!r}"
        skip = 1 + len(support.WARM_UP_QUERIES)
        results[tier] = {
            "queries": asked,
            "answers": [support.check_fused(value) for value in values[skip:]],
            "seconds": [call["seconds"] for call in outcome.calls[skip:]],
            "peaks": outcome.peaks,
        }
    return results


def _scored(measured):
    """``class -> [hit or miss, ...]`` over every query of the class, both tiers together, and the misses by id.

    S0b2's own method (DEC-380; ``RESULTS.md`` §1): the first five distinct paths of each query against its
    ``must_cite``, a percentage per class, the mean of the ten classes. Its class sizes add up to all 52 queries, so
    the two queries that name no ``must_cite`` path count in their classes, and they cannot be hits.
    """
    scored, missed = {}, []
    for result in measured.values():
        for query, answer in zip(result["queries"], result["answers"]):
            hit = support.is_hit(query["gold"]["must_cite"], answer["hits"])
            scored.setdefault(query["class"], []).append(hit)
            if not hit:
                missed.append(query["id"])
    assert len(scored) == support.QUERY_CLASSES, \
        f"the dev query set has {len(scored)} classes, not the ten S0b2 took the mean of: {sorted(scored)}"
    return scored, missed


@FULL
def test_the_dev_query_set_mean_hit_at_5_is_at_or_above_the_pass_line_of_80(measured, record_property):
    # Success 2 and failure 1 are one line since DEC-414: at or above 80 on the dev tiers passes, below 80 fails.
    # The S0b2 R1 baseline of 85 is not a pass line here; where the mean stands against it is reported, not
    # asserted, for the Wave 1 exit run (W1-42) and for qualification, which re-measure it.
    scored, missed = _scored(measured)
    mean, per_class = support.mean_hit_at_5(scored)
    report = support.hit_at_5_report(mean, per_class, missed)
    support.HIT_AT_5_REPORT[:] = report   # the terminal summary, pass or fail
    print("\n".join(report))              # the case's own captured output (-rP, -s)
    record_property("w1_19_mean_hit_at_5", round(mean, 2))
    record_property("w1_19_hit_at_5_pass_line", support.HIT_AT_5_PASS_LINE)
    record_property("w1_19_hit_at_5_baseline", support.HIT_AT_5_BASELINE)
    record_property("w1_19_hit_at_5_against_baseline", round(mean - support.HIT_AT_5_BASELINE, 2))
    record_property("w1_19_hit_at_5_per_class", repr(per_class))
    record_property("w1_19_hit_at_5_missed", ", ".join(sorted(missed)))
    assert mean >= support.HIT_AT_5_PASS_LINE, \
        f"mean hit@5 over the ten classes is {mean:.2f}, below the pass line of " \
        f"{support.HIT_AT_5_PASS_LINE:.0f} on the dev tiers (DEC-414); against the S0b2 R1 baseline of " \
        f"{support.HIT_AT_5_BASELINE:.0f}: {mean - support.HIT_AT_5_BASELINE:+.2f} " \
        f"(per class: {per_class}; missed: {sorted(missed)})"


@FULL
def test_a_warm_query_answers_within_half_a_second_at_p95(measured):
    seconds = [value for result in measured.values() for value in result["seconds"]]
    assert len(seconds) >= 50, f"only {len(seconds)} queries were timed"
    slowest = sorted(seconds)[-3:]
    assert support.p95(seconds) <= support.WARM_P95_LIMIT_S, \
        f"warm p95 is {support.p95(seconds):.3f} s over {len(seconds)} queries " \
        f"(limit {support.WARM_P95_LIMIT_S} s; the three slowest: {[round(value, 3) for value in slowest]})"


@FULL
def test_the_rerank_process_stays_within_two_and_a_half_gigabytes(measured):
    for tier, result in measured.items():
        assert result["peaks"], f"no process was watched on {tier}"
        largest = result["peaks"][0]
        assert largest["hwm_kb"] * 1024 <= support.RERANK_RSS_LIMIT_BYTES, \
            f"on {tier} a process of the retrieval peaked at {largest['hwm_kb'] * 1024 / 1e9:.2f} GB of resident memory " \
            f"(limit 2.5 GB): {largest['argv']}"


@FULL
def test_every_answer_is_one_fused_list_from_both_routes_reranked(measured):
    for tier, result in measured.items():
        for query, answer in zip(result["queries"], result["answers"]):
            assert answer["facets"][support.SEMANTIC_FACET]["available"] is True, \
                f"{query['id']} on {tier}: the semantic facet was unavailable, the measure is of FTS alone"
            assert answer["reranked"] is True, f"{query['id']} on {tier}: the list was not reranked"
