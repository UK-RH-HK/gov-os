"""KPI success 4 and failure 1, as revised by W2-145 (DEC-1048 (5)): if the service is down, the search goes on
unranked, named, and never starts a private reranker (DEC-979 item 4, DEC-374, DEC-1046 (1)).

If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search
keeps the fused order and nothing is scored (DEC-374), named: ``last_outcome()`` is by ``unavailable`` with the
service's failure. No private reranker is started in its place (W2-145 S1, S2: a client cannot tell a service that
is down from one it cannot reach, so a private fallback could load beside a running service). A search never fails
or hangs because of the service; each such search is logged, in a file under ``~/.cache/gov-os/`` (DEC-1034 item
3), as unranked, never as private. The central case: the service killed mid-run.

A session that cannot create or reach the Unix socket (the launch sandbox) goes on unranked exactly as for a service
that is down, quickly and without an error (DEC-1034 item 4).

Failure: a search that fails, hangs, or returns another session's scores because of the service.

Rewrite-Reason: DEC-1048 (5) (W2-145's test designer, DAEO-2tfd). Each case here asserted a private reranker's
answer (or, where none could start, the order given); each now asserts the order given, named, with no model loaded
by anyone but the shared service. W2-145's own cases hold the exact bounds and every failure kind; these keep
W2-112's KPI 4 under its new premise. The bundle's ``rerank: unavailable`` and ``gov status``'s count are in
``test_w2_112_bundle.py``.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_112_support as support
from w2_112_support import (FakeService, candidates, check_named_unavailable, check_scored_or_unranked, check_unranked,
                            query_of, raised)


def _went_on_unranked(box, report, given, who, reason=None):
    assert raised(report) is None, f"{who} raised: {raised(report)}"
    assert report["seconds"] <= support.UNRANKED_S, \
        f"{who} took {report['seconds']:.1f} s; with the service down it is to answer within {support.UNRANKED_S:g} s"
    check_unranked(report["result"], given, who)
    check_named_unavailable(report, who, reason)


def test_when_the_service_cannot_start_the_search_goes_on_unranked_and_starts_no_private_reranker(box):
    box.block_service()
    query, given = query_of("blocked"), candidates("blocked", 6)
    report = box.search(query, given)
    _went_on_unranked(box, report, given, "the search whose service cannot start")
    assert box.loads() == [], f"a model was loaded although no service could start: {box.loads()}"
    assert box.live_loads() == [], f"a model is still held after the search ended: {box.live_loads()}"


def test_when_the_services_model_cannot_load_the_search_goes_on_unranked_named(box):
    box.config(fail_loads=1)  # the first load under this HOME fails: the service's
    query, given = query_of("noload"), candidates("noload", 6)
    report = box.search(query, given)
    _went_on_unranked(box, report, given, "the search whose service could not load its model")
    attempts = len(list((box.state / "attempts").glob("*")))
    assert attempts == 1 and box.loads() == [], \
        (f"after the service's load failed, {attempts} loads were attempted and {box.loads()} succeeded: no private "
         "reranker may try in its place")


@pytest.mark.parametrize("how", ["full", "silent"])
def test_a_service_that_does_not_answer_leaves_the_search_unranked(boxes, how):
    # "full": nothing takes the connection (its queue is full), so it cannot be made within about 2 s.
    # "silent": the connection is taken and the request read, and nothing is ever answered: the request's time
    # limit bounds it (set short here).
    box = boxes(settings={support.TIMEOUT_SETTING: 3})
    fake = FakeService(box.socket, how)
    try:
        query, given = query_of(f"fake-{how}"), candidates(f"fake-{how}", 5)
        report = box.search(query, given)
        _went_on_unranked(box, report, given, f"the search whose service does not answer ({how})")
        assert box.loads() == [], f"a model was loaded although the service at the socket never answered: {box.loads()}"
    finally:
        fake.close()


@pytest.mark.parametrize("how", ["error", "garbage"])
def test_a_service_that_answers_with_an_error_leaves_the_search_unranked(box, how):
    fake = FakeService(box.socket, how)
    try:
        query, given = query_of(f"fake-{how}"), candidates(f"fake-{how}", 5)
        report = box.search(query, given)
        _went_on_unranked(box, report, given, f"the search whose service answers with an error ({how})")
        assert box.loads() == [], f"a model was loaded although the service at the socket answered: {box.loads()}"
    finally:
        fake.close()


def test_a_service_whose_model_fails_answers_with_an_error_and_the_search_goes_on_unranked(box):
    service = box.warm()
    box.for_pid(service, predict_error=True)
    query, given = query_of("broken"), candidates("broken", 6)
    report = box.search(query, given)
    _went_on_unranked(box, report, given, "the search whose service failed to score")
    assert box.scorers_of(query) <= {service}, \
        f"the search's texts were scored by {box.scorers_of(query) - {service}}, not the service: a private reranker"
    assert support.strays(box, [service]) == [], f"a private reranker loaded the model: {support.strays(box, [service])}"


def test_a_service_killed_mid_run_leaves_every_search_answered(box):
    service = box.warm()
    box.for_pid(service, predict_delay=3.0)  # long enough for the searches to be waiting on it when it dies
    tags = [f"k{number}" for number in range(5)]
    barrier = box.work / "killed"
    sessions = [box.start({"query": query_of(tag), "candidates": candidates(tag, 6), "barrier": str(barrier)})
                for tag in tags]
    deadline = time.monotonic() + support.HUNG_S
    while len(list(box.work.glob("killed.ready-*"))) < len(sessions) and time.monotonic() < deadline:
        time.sleep(0.01)
    begun = len(box.events("predict-begin"))
    (box.work / "killed.go").touch()
    deadline = time.monotonic() + 30
    while len(box.events("predict-begin")) == begun and time.monotonic() < deadline:
        time.sleep(0.02)
    assert len(box.events("predict-begin")) > begun, "the service never began to score the searches"
    killed_at = time.time()
    victims = box.kill_service()
    assert service in victims, f"the service {service} was not found to be killed: {victims}"
    # Every search in flight goes on unranked, named (W2-145: no private reranker takes over); none fails, none
    # hangs, none gets another's scores. A later search may start a new shared service; nothing else loads.
    outcomes = {}
    for tag, session in zip(tags, sessions):
        report = session.wait()
        who = f"search {tag}, in flight when the service was killed"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        after = max(0.0, report.get("ended", killed_at) - killed_at)
        assert after <= support.UNRANKED_S, f"{who} still waited {after:.1f} s after the kill"
        outcomes[tag] = check_scored_or_unranked(report["result"], query_of(tag), candidates(tag, 6), who)
        if outcomes[tag] == "unranked":
            check_named_unavailable(report, who)
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"a reranker was loaded on the CPU after the kill: {on_cpu}"
    assert support.strays(box, [service]) == [], \
        f"a private reranker loaded the model after the kill: {support.strays(box, [service])}"
    assert len(support.listening(box.socket)) <= 1, "two services listen at once after the kill"


@pytest.mark.parametrize("why", ["no reranker environment", "no model loads"])
def test_where_no_reranker_can_load_the_order_given_is_kept_unscored(boxes, why):
    if why == "no reranker environment":  # a sandboxed worker
        box = boxes(environment=False)
    else:
        box = boxes()
        box.config(fail_all_loads=True)
    query, given = query_of("none"), candidates("none", 6)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with {why}: {raised(report)}"
    assert report["seconds"] <= support.UNRANKED_S, f"the search took {report['seconds']:.1f} s with {why}"
    check_unranked(report["result"], given, f"the search with {why}")
    assert support.outcome_of(report).get("by") == "unavailable", f"not named unavailable: {support.outcome_of(report)}"
    if why == "no reranker environment":
        assert support.processes_of(box.home) == [], \
            f"with no reranker environment, processes were left running: {support.processes_of(box.home)}"
    else:
        attempts = len(list((box.state / "attempts").glob("*")))
        assert attempts <= 1, f"{attempts} loads were attempted for one search: the service's, and no private's"


def test_a_session_that_cannot_make_a_unix_socket_goes_on_unranked_quickly_without_an_error(box):
    # The launch sandbox refuses socket(AF_UNIX) with EPERM (P-W2-112-T2). Here only the session's own Python
    # refuses it; the search goes on unranked exactly as for a service that is down, quickly and without an error
    # (DEC-1034 item 4), and starts no private reranker (W2-145).
    box.refuse_unix_sockets()
    query, given = query_of("sandboxed"), candidates("sandboxed", 6)
    report = box.search(query, given)
    _went_on_unranked(box, report, given, "the search of a session that cannot make a Unix socket")
    assert box.scorers_of(query) == set() and box.loads() == [], \
        f"the session's texts were scored ({box.scorers_of(query)}) or a model loaded ({box.loads()})"


def test_each_fallback_is_logged_under_the_users_cache_folder(box):
    box.block_service()
    since = time.time()
    query, given = query_of("logged"), candidates("logged", 4)
    report = box.search(query, given)
    _went_on_unranked(box, report, given, "the search whose service cannot start")
    found = box.cache_texts(since)
    pattern = re.compile(r"unranked|unavailable", re.IGNORECASE)
    assert any(pattern.search(text) for text in found), \
        (f"the unranked search was not logged in a file under ~/{support.CACHE_REL}/ (DEC-1034 item 3); files "
         f"written there since the search began: {found!r}")[:1500]
    assert not any(re.search(r"private", text, re.IGNORECASE) for text in found), \
        f"the log names a private reranker (W2-145: there is none): {found!r}"[:1500]
