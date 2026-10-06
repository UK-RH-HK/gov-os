"""KPI success 1 (paging with continuation) [CAP-16.a], KPI success 6 (the retrieval spend budget) [CAP-04.c,
CAP-16.c] and KPI failure 1 (a batch-size limit is reported as completeness).

Seven files hold one exact phrase and the semantic route adds the chunks that reach the vectors, so a question
for the phrase has more candidates than a small batch holds. A follow-up round is one more batch (package DP-2).
The cases ask with a bundle budget of 0, so no chunk is expanded to its parent and chunk ids can be compared.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")


def ask(api, project, ollama, **kwargs):
    kwargs.setdefault("bundle_budget", 0)  # no parent expansion: every cited chunk stands as it was found
    return support.check_bundle(api.retrieve(project, support.PHRASE, host=ollama.host, **kwargs), root=project)


def whole(api, project, ollama):
    """Everything there is to gather, in one large batch."""
    bundle = ask(api, project, ollama, batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL)
    assert bundle[support.K_CONTINUATION] is None and bundle[support.K_REASON] in support.NOTHING_LEFT, \
        f"one batch of {support.BATCH_LARGE} did not gather everything: {bundle[support.K_REASON]}"
    return bundle


# ---- batches

def test_a_small_batch_size_gives_several_batches_and_everything_is_gathered(api, project, ollama):
    bundle = ask(api, project, ollama, batch_size=3, radius=support.RADIUS_FULL)
    batches = bundle[support.K_BATCHES]
    assert len(batches) > 1, f"three candidates a batch and one batch: {batches!r}"
    for batch in batches:
        assert type(batch.get("size")) is int and 0 <= batch["size"] <= 3, \
            f"a batch does not say its size, or is larger than the batch size of 3: {batch!r}"
    assert set(support.PAGING) <= set(support.paths(bundle)), \
        "eight follow-up rounds of three were enough and a file that holds the phrase is not cited"
    assert bundle[support.K_CONTINUATION] is None and bundle[support.K_REASON] in support.NOTHING_LEFT
    assert {item[support.E_BATCH] for item in bundle[support.K_EVIDENCE]} - {1}, \
        "every cited chunk is said to come from the first batch"


def test_the_default_batch_size_is_ten(api, project, ollama):
    """DEC-422: ``batch_size=None`` uses 10. The fixture has more than 10 lexical chunks, so the first batch is
    full and the size is exactly 10."""
    bundle = ask(api, project, ollama, radius=support.RADIUS_FULL)
    batches = bundle[support.K_BATCHES]
    assert batches[0].get("size") == 10, \
        f"the default batch size is not 10: the first batch says {batches[0].get('size')!r}"


def test_the_batch_size_does_not_change_what_is_gathered(api, project, ollama):
    """The same evidence in batches of three as in one batch: the batch size is no completeness limit."""
    small = ask(api, project, ollama, batch_size=3, radius=support.RADIUS_FULL)
    assert set(support.chunk_ids(small)) == set(support.chunk_ids(whole(api, project, ollama)))


@pytest.mark.parametrize("batch_size", [1, 2, 4])
def test_a_batch_size_limit_is_never_reported_as_completeness(api, project, ollama, batch_size):
    """KPI failure 1. One follow-up round of a small batch cannot hold the seven files: the bundle must say that
    the budget ended it, list gaps and offer a continuation, never one of the reasons that say nothing is left."""
    bundle = ask(api, project, ollama, batch_size=batch_size, radius=support.RADIUS_LITE)
    limit = support.rounds_limit(bundle)
    assert len(bundle[support.K_BATCHES]) <= limit + 1, \
        f"{len(bundle[support.K_BATCHES])} batches with {limit} follow-up round(s) allowed"
    missing = set(support.PAGING) - set(support.paths(bundle))
    assert missing, "the fixture is too small for this case"
    assert bundle[support.K_REASON] == support.BUDGET_EXHAUSTED, \
        f"{len(missing)} files that hold the phrase are not cited and the bundle says {bundle[support.K_REASON]}"
    assert bundle[support.K_GAPS], "no gap is listed"
    assert bundle[support.K_CONTINUATION], "more is left and the bundle gives no continuation"


def test_the_gap_list_names_what_was_not_gathered(api, project, ollama):
    """DEC-034: "unresolved list disclosed". Each file that holds the phrase and is not cited is named by a gap."""
    bundle = ask(api, project, ollama, batch_size=2, radius=support.RADIUS_LITE)
    missing = set(support.PAGING) - set(support.paths(bundle))
    assert missing <= support.gap_names(bundle), \
        f"not cited and named by no gap: {sorted(missing - support.gap_names(bundle))}"


# ---- continuation

def test_the_continuation_neither_skips_nor_repeats(api, project, ollama):
    kwargs = {"host": ollama.host, "batch_size": 2, "radius": support.RADIUS_LITE, "bundle_budget": 0}
    bundles = support.follow(api, project, support.PHRASE, ask(api, project, ollama, batch_size=2,
                                                              radius=support.RADIUS_LITE), **kwargs)
    assert len(bundles) > 2, "the fixture is too small for this case"
    seen = [chunk for bundle in bundles for chunk in support.chunk_ids(bundle)]
    assert len(seen) == len(set(seen)), "a chunk is cited by two bundles of one continuation"
    everything = set(support.chunk_ids(whole(api, project, ollama)))
    assert set(seen) == everything, \
        f"the continuation skipped {len(everything - set(seen))} chunk(s) and added {len(set(seen) - everything)}"
    for bundle in bundles[:-1]:
        assert bundle[support.K_REASON] == support.BUDGET_EXHAUSTED, bundle[support.K_REASON]
    assert bundles[-1][support.K_REASON] in support.NOTHING_LEFT, bundles[-1][support.K_REASON]


def test_every_bundle_of_a_continuation_is_checked_against_the_bytes(api, project, ollama):
    kwargs = {"host": ollama.host, "batch_size": 4, "radius": support.RADIUS_LITE, "bundle_budget": 0}
    for bundle in support.follow(api, project, support.PHRASE, ask(api, project, ollama, batch_size=4,
                                                                  radius=support.RADIUS_LITE), **kwargs):
        support.check_bundle(bundle, root=project)


def test_a_continuation_that_is_no_token_is_refused(api, project, ollama):
    outcome = api.outcome(project, support.PHRASE, host=ollama.host, continuation="not-a-continuation")
    error = outcome.error()
    assert error is not None, f"a made-up continuation was answered: {outcome.calls[0]['value']!r}"
    assert error["type"] == "GovError" and error["code"], f"refused with {error!r}, not with a governance error"


def test_a_continuation_of_another_question_is_refused(api, project, ollama):
    """A token carries on the question it was given for. With another question it would skip or repeat."""
    token = ask(api, project, ollama, batch_size=2, radius=support.RADIUS_LITE)[support.K_CONTINUATION]
    outcome = api.outcome(project, support.DEDUP_PHRASE, host=ollama.host, batch_size=2,
                          radius=support.RADIUS_LITE, continuation=token)
    error = outcome.error()
    assert error is not None and error["type"] == "GovError" and error["code"], \
        f"the continuation of one question was accepted for another: {error!r}"


# ---- the retrieval spend budget

@pytest.mark.parametrize("radius", sorted(support.ROUNDS_BY_RADIUS))
def test_the_follow_up_rounds_scale_with_the_radius(api, project, ollama, radius):
    """LITE (R0, R1): 1; STANDARD (R2): 3; FULL (R3 and above): 8 (DEC-005, DEC-035; package DP-2)."""
    bundle = ask(api, project, ollama, batch_size=1, radius=radius)
    assert support.rounds_limit(bundle) == support.ROUNDS_BY_RADIUS[radius]


@pytest.mark.parametrize("radius", [0, 2, 3])
def test_reaching_the_spend_budget_ends_with_the_reason_and_the_gap_list(api, project, ollama, radius):
    """Batches of one: no radius has rounds enough. Never a silent truncation."""
    bundle = ask(api, project, ollama, batch_size=1, radius=radius)
    limit = support.rounds_limit(bundle)
    used = bundle[support.K_BUDGET][support.B_ROUNDS].get(support.B_USED)
    assert used == limit, f"{used!r} follow-up rounds used of {limit}, and more was left to gather"
    assert len(bundle[support.K_BATCHES]) == limit + 1
    assert len(bundle[support.K_EVIDENCE]) <= limit + 1
    assert bundle[support.K_REASON] == support.BUDGET_EXHAUSTED and bundle[support.K_GAPS]
    assert bundle[support.K_CONTINUATION]


def test_a_larger_radius_gathers_more(api, project, ollama):
    counts = [len(ask(api, project, ollama, batch_size=1, radius=radius)[support.K_EVIDENCE]) for radius in (0, 2, 3)]
    assert counts[0] < counts[1] < counts[2], f"cited at radius 0, 2 and 3: {counts}"


@pytest.mark.parametrize("bundle_budget", [support.BUDGET_SMALL, support.BUDGET_LARGE])
def test_the_spend_budget_is_separate_from_the_bundle_budget(api, project, ollama, bundle_budget):
    """The rounds are the radius's whatever the bundle may hold, and the bundle budget is the one given whatever
    the radius: two budgets, each with its own limit [CAP-04.c]."""
    for radius in (0, 2):
        bundle = ask(api, project, ollama, batch_size=1, radius=radius, bundle_budget=bundle_budget)
        assert support.rounds_limit(bundle) == support.ROUNDS_BY_RADIUS[radius]
        assert bundle[support.K_BUDGET][support.B_BUNDLE][support.B_LIMIT] == bundle_budget
        assert bundle[support.K_REASON] == support.BUDGET_EXHAUSTED, \
            f"the rounds ran out under a bundle budget of {bundle_budget} and the bundle says {bundle[support.K_REASON]}"
