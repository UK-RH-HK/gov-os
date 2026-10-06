"""KPI success 7: for a ticket whose scope matches a committed failure or lesson record, the bundle returns that
record ahead of implementation evidence [CAP-14.a]; and CAP-41's acceptance line: not for an out-of-scope ticket.

The record types are ``failure`` and ``lesson`` (the kernel schemas of W1-08). A record's scope matches a ticket
when a typed edge of the record graph joins them: here ``constrains: [<ticket id>]`` on the record (package
DP-5). The records' own words are not in the question and no vector is made of them, so only their scope can
bring them into a bundle.
"""

from __future__ import annotations

import pytest

import w1_21_support as support

pytestmark = pytest.mark.needs("gitleaks", "sqlite_vec")

AHEAD = {"a failure record": support.FAILURE, "a lesson record": support.LESSON}


def ask(api, project, ollama, **kwargs):
    """The question finds the implementation (``app/pool.py``), and the stand-in reranker scores it highest."""
    outcome = api.outcome(project, support.CODE_PHRASE, host=ollama.host, favour=[support.CODE_PHRASE.split()[0]],
                          reranker=support.RERANKER, batch_size=support.BATCH_LARGE, radius=support.RADIUS_FULL,
                          **kwargs)
    return support.check_bundle(outcome.value(), root=project)


@pytest.mark.parametrize("kind", AHEAD, ids=list(AHEAD))
def test_a_record_in_the_tickets_scope_is_returned(api, project, ollama, kind):
    bundle = ask(api, project, ollama, ticket=support.TICKET_IN_SCOPE)
    assert AHEAD[kind] in support.paths(bundle), f"{AHEAD[kind]} is in the ticket's scope and is not in the bundle"


def test_failure_and_lesson_records_come_ahead_of_implementation_evidence(api, project, ollama):
    """Ahead of everything else the bundle cites, whatever the reranker scored highest."""
    bundle = ask(api, project, ollama, ticket=support.TICKET_IN_SCOPE)
    kinds = [support.record_type(project, item[support.E_PATH]) for item in bundle[support.K_EVIDENCE]]
    assert support.POOL in support.paths(bundle), "the implementation the question asks for is not cited"
    ahead = [index for index, kind in enumerate(kinds) if kind in support.AHEAD_TYPES]
    rest = [index for index, kind in enumerate(kinds) if kind not in support.AHEAD_TYPES]
    assert len(ahead) >= 2 and rest, kinds
    assert max(ahead) < min(rest), \
        f"a failure or lesson record stands behind other evidence; the record types in order: {kinds}"


@pytest.mark.parametrize("kwargs", [{"ticket": support.TICKET_OUT_OF_SCOPE}, {}],
                         ids=["an out-of-scope ticket", "no ticket"])
@pytest.mark.parametrize("kind", AHEAD, ids=list(AHEAD))
def test_a_record_out_of_scope_is_not_returned(api, project, ollama, kind, kwargs):
    bundle = ask(api, project, ollama, **kwargs)
    assert support.POOL in support.paths(bundle)
    assert AHEAD[kind] not in support.paths(bundle), f"{AHEAD[kind]} is returned outside its scope"


def test_the_records_come_ahead_in_a_small_first_batch_too(api, project, ollama):
    """Batches of two with one follow-up round: the scoped records are in the first bundle, not behind a
    continuation ("before any implementation step", CAP-14)."""
    bundle = support.check_bundle(api.retrieve(project, support.CODE_PHRASE, host=ollama.host, batch_size=2,
                                               radius=support.RADIUS_LITE, ticket=support.TICKET_IN_SCOPE),
                                  root=project)
    assert {support.FAILURE, support.LESSON} <= set(support.paths(bundle)), support.paths(bundle)
