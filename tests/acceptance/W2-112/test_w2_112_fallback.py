"""KPI success 4 and failure 1: if the service is down, the search falls back (DEC-979 item 4, DEC-374).

If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search
falls back to a private reranker (through the GPU slot rule, KPI 7: ``test_w2_112_slots.py``); where that cannot
start either (a sandboxed worker, the memory floor reached), the fused order is kept and nothing is scored
(DEC-374); a search never fails or hangs because of the service; each fallback is logged, in a file under
``~/.cache/gov-os/`` (DEC-1034 item 3). The central case: the service killed mid-run. "About 2 s" bounds the
connection; the answer is bounded by the request's time limit (DEC-1034 item 3).

A session that cannot create or reach the Unix socket (the launch sandbox) falls back exactly as for a service that
is down, quickly and without an error (DEC-1034 item 4: the ticket builds for P-W2-112-T2 (c)).

Failure: a search that fails, hangs, or returns another session's scores because of the service.

Each box has the stand-in GPU with room and both GPU slots free, so a private reranker can start unless a case
says otherwise. The bundle's ``rerank: unavailable`` and ``gov status``'s count are in ``test_w2_112_bundle.py``.
The memory floor is the machine's state and is not planted here.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_112_support as support
from w2_112_support import (FakeService, candidates, check_scored, check_scored_or_unranked, check_unranked, query_of,
                            raised)


def _fell_back(box, report, query, given, who):
    assert raised(report) is None, f"{who} raised: {raised(report)}"
    assert report["seconds"] <= support.FALLBACK_S, \
        f"{who} took {report['seconds']:.1f} s; with the service down it is to answer within {support.FALLBACK_S:g} s"
    check_scored(report["result"], query, given, who)


def test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker(box):
    box.block_service()
    query, given = query_of("blocked"), candidates("blocked", 6)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search whose service cannot start")
    assert box.live_loads() == [], \
        f"a model is still held after the search ended: {box.live_loads()} (a private reranker ends with its search)"


def test_when_the_services_model_cannot_load_the_search_still_gets_a_private_rerankers_answer(box):
    box.config(fail_loads=1)  # the first load under this HOME fails: the one the service tries first
    query, given = query_of("noload"), candidates("noload", 6)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search whose service could not load its model")


@pytest.mark.parametrize("how", ["full", "silent"])
def test_a_service_that_does_not_answer_is_passed_over(boxes, how):
    # "full": nothing takes the connection (its queue is full), so it cannot be made within about 2 s.
    # "silent": the connection is taken and the request read, and nothing is ever answered: the request's time
    # limit bounds it (set short here).
    box = boxes(settings={support.TIMEOUT_SETTING: 3})
    fake = FakeService(box.socket, how)
    try:
        query, given = query_of(f"fake-{how}"), candidates(f"fake-{how}", 5)
        report = box.search(query, given)
        _fell_back(box, report, query, given, f"the search whose service does not answer ({how})")
    finally:
        fake.close()


@pytest.mark.parametrize("how", ["error", "garbage"])
def test_a_service_that_answers_with_an_error_is_passed_over(box, how):
    fake = FakeService(box.socket, how)
    try:
        query, given = query_of(f"fake-{how}"), candidates(f"fake-{how}", 5)
        report = box.search(query, given)
        _fell_back(box, report, query, given, f"the search whose service answers with an error ({how})")
    finally:
        fake.close()


def test_a_service_whose_model_fails_answers_with_an_error_and_the_search_falls_back(box):
    service = box.warm()
    box.for_pid(service, predict_error=True)
    query, given = query_of("broken"), candidates("broken", 6)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search whose service failed to score")
    assert box.scorers_of(query) - {service}, "no private reranker scored the search, yet the service failed"


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
    # Five searches fall back at once and there are two GPU slots: each one is answered by a private reranker on a
    # slot, or waits for one and goes on unranked (KPI 7). None fails, none hangs, none gets another's scores.
    bound = support.SLOT_WAIT_S + support.FALLBACK_S
    outcomes = {}
    for tag, session in zip(tags, sessions):
        report = session.wait()
        who = f"search {tag}, in flight when the service was killed"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        after = max(0.0, report.get("ended", killed_at) - killed_at)
        assert after <= bound, f"{who} still waited {after:.1f} s after the kill (bound {bound:g} s)"
        outcomes[tag] = check_scored_or_unranked(report["result"], query_of(tag), candidates(tag, 6), who)
    assert "scored" in outcomes.values(), \
        f"no search in flight was answered by a private reranker after the kill, with GPU slots free: {outcomes}"
    on_cpu = [record["pid"] for record in box.loads() if record["device"] == "cpu"]
    assert on_cpu == [], f"a reranker was loaded on the CPU after the kill (KPI 7 forbids it): {on_cpu}"
    assert len(support.listening(box.socket)) <= 1, "two services listen at once after the kill"


@pytest.mark.parametrize("why", ["no reranker environment", "no model loads"])
def test_where_no_private_reranker_can_start_either_the_order_given_is_kept_unscored(boxes, why):
    if why == "no reranker environment":  # a sandboxed worker
        box = boxes(environment=False)
    else:
        box = boxes()
        box.config(fail_all_loads=True)
    query, given = query_of("none"), candidates("none", 6)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised with {why}: {raised(report)}"
    assert report["seconds"] <= support.FALLBACK_S, f"the search took {report['seconds']:.1f} s with {why}"
    check_unranked(report["result"], given, f"the search with {why}")
    if why == "no reranker environment":
        assert support.processes_of(box.home) == [], \
            f"with no reranker environment, processes were left running: {support.processes_of(box.home)}"


def test_a_session_that_cannot_make_a_unix_socket_falls_back_quickly_without_an_error(box):
    # The launch sandbox refuses socket(AF_UNIX) with EPERM (P-W2-112-T2). Here only the session's own Python
    # refuses it; the search must fall back exactly as for a service that is down (a private reranker on a free
    # GPU slot), quickly and without an error (DEC-1034 item 4).
    box.refuse_unix_sockets()
    query, given = query_of("sandboxed"), candidates("sandboxed", 6)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search of a session that cannot make a Unix socket")
    scorers = box.scorers_of(query)
    box.live_loads()  # let the session's private reranker end
    assert scorers and not any(support.alive(pid) for pid in scorers), \
        f"the session's texts were scored by a process that is still running ({scorers}): not its private reranker"


def test_each_fallback_is_logged_under_the_users_cache_folder(box):
    box.block_service()
    since = time.time()
    query, given = query_of("logged"), candidates("logged", 4)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search whose service cannot start")
    found = box.cache_texts(since)
    pattern = re.compile(r"rerank|fall|fell|unavailable|private", re.IGNORECASE)
    assert any(pattern.search(text) for text in found), \
        (f"the fallback was not logged in a file under ~/{support.CACHE_REL}/ (DEC-1034 item 3); files written "
         f"there since the search began: {found!r}")[:1500]
