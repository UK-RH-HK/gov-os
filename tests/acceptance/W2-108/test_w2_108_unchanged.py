"""KPI 2 (DEC-969, DEC-860): every answer is unchanged. For the same store and tree, each retrieval call returns the
same bundle, facets and stopping reason as before, item for item, on a planted repository and on this
repository's store.

Failure line: any bundle, facet or stopping reason different from before for the same store and tree.

"Before" is shown from outside: each call made alone in a fresh process, where nothing can have been remembered,
against the same call made later in one process that has already made many calls (README, "Every answer
unchanged").
"""

from __future__ import annotations

import pytest

import w2_108_support as S


def fresh_answers(driver, root, steps, **run):
    """Each step in a process of its own."""
    return [driver.run(root, [step], **run).values()[0] for step in steps]


def warm_answers(driver, root, steps, warm_up, **run):
    """``warm_up`` and then ``steps`` twice, all in one process: the answers of the second pass."""
    values = driver.run(root, [*warm_up, *steps, *steps], **run).values()
    first, second = values[len(warm_up):len(warm_up) + len(steps)], values[len(warm_up) + len(steps):]
    for number, (one, two) in enumerate(zip(first, second)):
        assert S.answer_of(one) == S.answer_of(two), \
            f"step {number}: two calls in one process answered differently\n{one}\n{two}"
    return second


def assert_same(steps, fresh, warm):
    # Rewrite-Reason: DEC-1061 (R-1): compared without W2-126's vector-cache counters (S.answer_of).
    for step, alone, later in zip(steps, fresh, warm):
        alone, later = S.answer_of(alone), S.answer_of(later)
        what = f"{step['module']}.{step['function']}{tuple(step['args'][1:])}"
        if isinstance(alone, dict) and "stopping_reason" in alone:
            assert later["stopping_reason"] == alone["stopping_reason"], what
            assert later["facets"] == alone["facets"], what
            assert later["evidence"] == alone["evidence"], what
        elif isinstance(alone, dict) and "state" in alone:
            assert S.facet(later) == S.facet(alone), what
        assert later == alone, f"{what}: the answer of a process that had made many calls differs from the answer " \
                               f"of a fresh process\nfresh: {alone}\nlater: {later}"


def planted_steps():
    return [S.lexical_freshness(),
            *[S.lexical_search(question) for question in S.QUESTIONS],
            *[S.semantic_search(question) for question in S.QUESTIONS],
            *[S.retrieve(question) for question in S.QUESTIONS],
            S.retrieve(S.PHRASE, batch_size=1),
            S.retrieve(S.QUESTIONS[1], batch_size=2, radius=2)]


WARM_UP = [S.retrieve(S.QUESTIONS[3]), S.semantic_search(S.QUESTIONS[2]), S.lexical_freshness(),
           S.lexical_search(S.PHRASE), S.retrieve(S.QUESTIONS[1]), S.semantic_search(S.QUESTIONS[0])]


def test_planted_answers_are_unchanged(planted, driver, embedder):
    steps = planted_steps()
    fresh = fresh_answers(driver, planted, steps, host=embedder.host)
    assert fresh[0] == {"status": S.FRESH, "stale": []}
    assert all(answer["state"] == S.AVAILABLE for answer in fresh[1:1 + 2 * len(S.QUESTIONS)]), fresh
    assert any(answer["hits"] for answer in fresh[1:1 + len(S.QUESTIONS)]), "no lexical hit: the case is empty"
    assert all(answer["hits"] for answer in fresh[1 + len(S.QUESTIONS):1 + 2 * len(S.QUESTIONS)]), fresh
    assert any(answer["evidence"] for answer in fresh[1 + 2 * len(S.QUESTIONS):]), "no evidence: the case is empty"
    warm = warm_answers(driver, planted, steps, WARM_UP, host=embedder.host)
    assert_same(steps, fresh, warm)


def test_planted_continuation_is_unchanged(planted, driver, embedder):
    """A paged question: the second batch, asked with the first batch's token, is the same in a warm process."""
    first = driver.run(planted, [S.retrieve(S.PHRASE, batch_size=1)], host=embedder.host).values()[0]
    token = first["continuation"]
    assert token, f"the first batch named no continuation: the case is empty\n{first}"
    step = S.retrieve(S.PHRASE, batch_size=1, continuation=token)
    fresh = fresh_answers(driver, planted, [step], host=embedder.host)
    warm = warm_answers(driver, planted, [step], WARM_UP, host=embedder.host)
    assert_same([step], fresh, warm)


def test_planted_unavailable_answers_are_unchanged(planted, driver, embedder):
    """An index made stale by an uncommitted edit (DEC-342, DEC-344): the same unavailable facets and stopping
    reason, fresh or late."""
    S.write(planted, S.TIDES, "# Tides\n\nThe tide tables were moved to the harbour office.\n")
    steps = [S.lexical_freshness(), S.lexical_search(S.PHRASE), S.semantic_search(S.QUESTIONS[2]),
             S.retrieve(S.QUESTIONS[2])]
    fresh = fresh_answers(driver, planted, steps, host=embedder.host)
    assert fresh[0] == {"status": S.STALE, "stale": [S.TIDES]}
    assert S.facet(fresh[1]) == (False, S.UNAVAILABLE, S.STALE)
    assert S.facet(fresh[2]) == (False, S.UNAVAILABLE, S.STALE)
    assert fresh[3]["stopping_reason"] == S.UNAVAILABLE
    warm = warm_answers(driver, planted, steps, WARM_UP, host=embedder.host)
    assert_same(steps, fresh, warm)


def test_no_commit_answers_are_unchanged(no_commit, driver, embedder):
    """A repository with no commit yet: the same answers, fresh or late."""
    steps = [S.lexical_freshness(), *[S.lexical_search(question) for question in S.QUESTIONS[:2]],
             *[S.semantic_search(question) for question in S.QUESTIONS[1:3]]]
    fresh = fresh_answers(driver, no_commit, steps, host=embedder.host)
    assert fresh[0] == {"status": S.FRESH, "stale": []}
    warm_up = [S.semantic_search(S.QUESTIONS[0]), S.lexical_freshness(), S.lexical_search(S.QUESTIONS[3])]
    warm = warm_answers(driver, no_commit, steps, warm_up, host=embedder.host)
    assert_same(steps, fresh, warm)


# --------------------------------------------------------------------------
# This repository's store (README, "This repository's store")
# --------------------------------------------------------------------------

def repo_steps():
    return [S.lexical_freshness(),
            *[S.lexical_search(question) for question in S.REPO_QUESTIONS[:3]],
            S.semantic_search(S.REPO_QUESTIONS[3]),
            *[S.retrieve(question) for question in S.REPO_QUESTIONS],
            S.retrieve(S.REPO_QUESTIONS[0], ticket=S.REPO_TICKET)]


REPO_WARM_UP = [S.retrieve(S.REPO_QUESTIONS[2]), S.semantic_search(S.REPO_QUESTIONS[1]), S.lexical_freshness(),
                S.retrieve(S.REPO_QUESTIONS[3], ticket=S.REPO_TICKET)]


def test_this_repositorys_answers_are_unchanged(repo_store, driver):
    steps = repo_steps()
    env = S.repo_env(driver)
    fresh = fresh_answers(driver, repo_store, steps, env=env)
    assert any(answer["hits"] for answer in fresh[1:4] if answer["available"]) or fresh[0]["status"] != S.FRESH, \
        f"a fresh index found none of {S.REPO_QUESTIONS[:3]}: the case is empty"
    warm = warm_answers(driver, repo_store, steps, REPO_WARM_UP, env=env)
    assert_same(steps, fresh, warm)


def test_this_repositorys_semantic_answers_are_unchanged(repo_store, driver):
    """The vectors' answers on this repository's store; skipped, with the facet's reason, where no embedder
    answers."""
    env = S.repo_env(driver)
    probe = driver.run(repo_store, [S.semantic_search(S.REPO_QUESTIONS[3])], env=env).values()[0]
    if not probe["available"]:
        pytest.skip(f"the semantic facet of {repo_store} is unavailable here ({probe['reason']}): no embedder "
                    f"answers, or the store holds no current vectors")
    steps = [S.semantic_search(question) for question in S.REPO_QUESTIONS] \
        + [S.retrieve(question) for question in S.REPO_QUESTIONS[2:]]
    fresh = fresh_answers(driver, repo_store, steps, env=env)
    assert all(answer["hits"] for answer in fresh[:len(S.REPO_QUESTIONS)]), "the vectors answered nothing"
    warm = warm_answers(driver, repo_store, steps, REPO_WARM_UP, env=env)
    assert_same(steps, fresh, warm)


def test_this_repositorys_context_packet_is_unchanged(repo_store, driver):
    """The context packet of one ticket (``gov.context.context``), fresh or after many retrieval calls."""
    step = S.call(S.CONTEXT, "context", "{root}", S.REPO_TICKET)
    env = S.repo_env(driver)
    fresh = fresh_answers(driver, repo_store, [step], env=env)
    warm = warm_answers(driver, repo_store, [step], REPO_WARM_UP, env=env)
    assert warm[0] == fresh[0], f"the context packet of {S.REPO_TICKET} differs after many retrieval calls"
