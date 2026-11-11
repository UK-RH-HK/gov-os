"""KPI success 3, second half: retrieval latency stays within the retrieve budget on the dev tiers.

The budget is W1-19's warm-query budget: p95 at most 0.5 s (``WARM_P95_LIMIT_S``). Both cases are **latency cases
(DEC-372)**: run this file alone, never beside another suite; a case that fails under parallel load is re-run alone.

- ``test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget``: no model. Each dev tier is cloned
  into a temporary folder and rebuilt by ``gov rebuild --json`` with no embedding endpoint; one process asks three
  warm-up questions, then each question of the dev query set of that tier, through the lexical route alone.
- ``test_a_warm_retrieval_with_the_real_models_answers_within_the_budget``: the same through the fusion, with this
  machine's Ollama and reranker (``needs("ollama", "reranker")``), on the tiers the session's ``real_tiers`` built
  with the real embedder; the timed process runs nothing else.

Both clone the dev tiers (``GOV_DEV_TIERS``), so both are ``local_only``; each skips where a tier or the query set
is not on this machine.
"""

from __future__ import annotations

import pytest

import w2_13_support as support

pytestmark = [pytest.mark.local_only, pytest.mark.latency, pytest.mark.needs("git", "gitleaks", "sqlite_vec")]


def _tiers(box, tmp_path_factory, label):
    """Each dev tier cloned and rebuilt with no embedding endpoint: ``programme -> (root, its questions)``."""
    queries = support.dev_queries()
    if queries is None:
        pytest.skip(f"no dev query set at {support.QUERY_SET} (GOV_DEV_TIERS)")
    roots = {}
    for programme, tier in support.TIERS.items():
        root = support.clone_tier(tier, tmp_path_factory.mktemp(f"w2-13-{label}-{tier}") / tier)
        if root is None:
            pytest.skip(f"no dev tier at {support.DEV_TIERS / tier} (GOV_DEV_TIERS)")
        box.rebuild(root)
        roots[programme] = (root, [query["query"] for query in queries if query.get("programme") == programme])
    return roots


def _timed(box, roots, module, function, extra_args, kwargs, env=None):
    seconds = []
    for root, questions in roots.values():
        calls = [(module, function, [support.path_arg(root), text, *extra_args], kwargs)
                 for text in (*support.WARM_UP_QUESTIONS, *questions)]
        outcome = box.run(calls, env=env, timeout=support.MEASURE_TIMEOUT_S)
        for index in range(len(calls)):
            outcome.value(index)  # every question answered, none raised
        seconds += [outcome.seconds(index) for index in range(len(support.WARM_UP_QUESTIONS), len(calls))]
    return seconds


def _within_budget(seconds):
    assert len(seconds) >= 20, f"only {len(seconds)} questions were timed"
    slowest = [round(value, 3) for value in sorted(seconds)[-3:]]
    assert support.p95(seconds) <= support.WARM_P95_LIMIT_S, \
        f"warm p95 is {support.p95(seconds):.3f} s over {len(seconds)} questions (limit " \
        f"{support.WARM_P95_LIMIT_S} s; the three slowest: {slowest})"


def test_the_ranked_lexical_route_answers_a_warm_question_within_the_budget(box, tmp_path_factory):
    roots = _tiers(box, tmp_path_factory, "lexical")
    _within_budget(_timed(box, roots, support.LEXICAL, "search", [], {"refresh": False}))


@pytest.mark.needs("ollama", "reranker")
def test_a_warm_retrieval_with_the_real_models_answers_within_the_budget(box, real_tiers):
    queries = support.dev_queries()
    if queries is None:
        pytest.skip(f"no dev query set at {support.QUERY_SET} (GOV_DEV_TIERS)")
    roots = {programme: (root, [query["query"] for query in queries if query.get("programme") == programme])
             for programme, root in real_tiers.items()}
    env = box.real_env()
    _within_budget(_timed(box, roots, support.FUSION, "search", [None], {"refresh": False}, env=env))
