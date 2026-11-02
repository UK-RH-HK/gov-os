"""KPI success 4 and failure 1: if the service is down, the search falls back (DEC-979 item 4, DEC-374).

If the service is down (it cannot start, does not answer within about 2 s, or answers with an error), the search
falls back to a private reranker as today; where that cannot start either (a sandboxed worker, the memory floor
reached), the fused order is kept and nothing is scored (DEC-374); a search never fails or hangs because of the
service; each fallback is logged. The central case: the service killed mid-run.

Failure: a search that fails, hangs, or returns another session's scores because of the service.

The bundle's marking ``rerank: unavailable`` and ``gov status``'s count are outside W2-112's paths:
``test_w2_112_surfaces.py``. The memory floor is the machine's state and is not planted here.
"""

from __future__ import annotations

import re
import time

import pytest

import w2_112_support as support
from w2_112_support import (FakeService, candidates, check_scored, check_unranked, query_of, raised)


def _block_the_service(box):
    """The service cannot start: its socket's folder cannot be made (a plain file holds its name)."""
    folder = box.socket.parent
    folder.parent.mkdir(parents=True, exist_ok=True)
    folder.write_text("not a folder: the W2-112 tests keep the service from starting\n", encoding="utf-8")


def _fell_back(box, report, query, given, who):
    assert raised(report) is None, f"{who} raised: {raised(report)}"
    assert report["seconds"] <= support.FALLBACK_S, \
        f"{who} took {report['seconds']:.1f} s; with the service down it is to answer within {support.FALLBACK_S:g} s"
    check_scored(report["result"], query, given, who)


def test_when_the_service_cannot_start_the_search_falls_back_to_a_private_reranker(box):
    _block_the_service(box)
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
    # "silent": the connection is taken and the request read, and nothing is ever answered; the time limit is set
    # short, as an answer that never comes is the time limit's case too.
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
    for tag, session in zip(tags, sessions):
        report = session.wait()
        # Measured from the kill: how long each search still waited once its service was gone.
        _fell_back(box, {**report, "seconds": max(0.0, report.get("ended", killed_at) - killed_at)},
                   query_of(tag), candidates(tag, 6), f"search {tag}, in flight when the service was killed")
    assert len(support.listening(box.socket)) <= 1, "two services listen at once after the kill"
    assert len(box.live_loads()) <= 1, f"more than one model is held after the kill: {box.live_loads()}"


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


def test_each_fallback_is_logged(box):
    _block_the_service(box)
    since = time.time()
    query, given = query_of("logged"), candidates("logged", 4)
    report = box.search(query, given)
    _fell_back(box, report, query, given, "the search whose service cannot start")
    found = support.traces(box, report, since)
    pattern = re.compile(r"rerank|fall|fell|unavailable|private", re.IGNORECASE)
    assert any(pattern.search(trace) for trace in found), \
        ("the fallback left no trace: no logging record, nothing on standard error and no file under HOME "
         f"mentions it (seen: {found!r})")[:1500]
