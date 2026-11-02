"""KPI success 2 and failure 1: many sessions at once (DEC-979 item 4, P-RERANKER-1).

20 concurrent searches are answered by that one process, each with its own scores for its own texts, in arrival
order, with a cap on a request's texts and a time limit per request. Failure: a search that fails, hangs, or
returns another session's scores because of the service.

Each session's texts are its own (its tag is in every text), and the stand-in model's score is a function of the
query and the text alone, so a score that belongs to another session or another text cannot pass for this one.
Arrival order and the cap are read on the service's own socket, with P-RERANKER-1's one-line request
``[query, [text, ...]]``.
"""

from __future__ import annotations

import threading
import time

import w2_112_support as support
from w2_112_support import (ask, candidates, check_scored, check_scored_or_unranked, is_scores, query_of, raised,
                            score)

GPU_ROOM = {"present": True, "total": 16 * support.GIB, "free": 14 * support.GIB, "name": "Stand-in GPU"}


def test_twenty_concurrent_searches_are_answered_by_one_process_each_with_its_own_scores(boxes):
    box = boxes(gpu=GPU_ROOM)
    box.config(load_delay=0.3, predict_delay=0.05)
    tags = [f"c{number:02d}" for number in range(20)]
    started = time.monotonic()
    reports = box.together([{"query": query_of(tag), "candidates": candidates(tag, 12)} for tag in tags])
    for tag, report in zip(tags, reports):
        assert raised(report) is None, f"concurrent search {tag} raised: {raised(report)}"
        check_scored(report["result"], query_of(tag), candidates(tag, 12), f"concurrent search {tag}")
    loads = box.loads()
    assert len(loads) == 1, \
        (f"20 concurrent searches loaded the model {len(loads)} times (processes {[r['pid'] for r in loads]}): one "
         "process is to answer them all")
    service = loads[0]["pid"]
    strays = {tag: box.scorers_of(query_of(tag)) for tag in tags if box.scorers_of(query_of(tag)) != {service}}
    assert not strays, f"searches were scored by another process than the one service {service}: {strays}"
    assert support.alive(service), "the service did not stay up after the searches"
    assert len([record for record in loads if record["device"] == "cuda"]) <= 1 and len(box.on_gpu()) <= 1, \
        f"more than one copy of the model on the GPU: {box.on_gpu()}"
    assert time.monotonic() - started < support.HUNG_S


def test_requests_are_answered_in_arrival_order(box):
    box.warm()
    box.config(predict_delay=0.4)  # each scoring call holds the model, so the requests behind it queue
    tags = [f"q{number}" for number in range(6)]
    answers, errors = {}, {}

    def client(number, tag):
        time.sleep(number * 0.15)
        texts = [item["text"] for item in candidates(tag, 3)]
        try:
            answers[tag] = (texts, ask(box.socket, query_of(tag), texts, timeout=60))
        except OSError as error:
            errors[tag] = repr(error)

    threads = [threading.Thread(target=client, args=(number, tag)) for number, tag in enumerate(tags)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join(90)
    assert not errors, f"requests on the service's socket failed: {errors}"
    for tag in tags:
        texts, answer = answers[tag]
        assert is_scores(answer, len(texts)), f"request {tag} was answered {answer!r}, not one score per text"[:400]
        wanted = [score(query_of(tag), text) for text in texts]
        assert all(abs(got - want) <= support.TOLERANCE for got, want in zip(answer, wanted)), \
            f"request {tag} got {answer}, its own texts score {wanted}: another request's scores"
    calls = [record for record in box.events("predict-begin")]
    first_call = {}
    for index, record in enumerate(calls):
        for query in record.get("queries", []):
            first_call.setdefault(query, index)
    order = [first_call.get(query_of(tag)) for tag in tags]
    assert None not in order, f"some requests were never scored by the model: {dict(zip(tags, order))}"
    assert order == sorted(order), \
        (f"the requests were not scored in the order they arrived ({tags}, 0.15 s apart): the model call that "
         f"first scored each was {order}")


def test_a_request_over_the_cap_is_refused_and_the_service_keeps_answering(box):
    box.warm()
    texts = [f"text {number}" for number in range(support.OVER_CAP)]
    try:
        answer = ask(box.socket, query_of("cap"), texts, timeout=30)
    except (OSError, TimeoutError) as error:
        answer = f"refused by the connection: {error!r}"
    assert not is_scores(answer, len(texts)), \
        f"a request of {support.OVER_CAP} texts was scored in full: there is no cap on a request's texts"
    small = [item["text"] for item in candidates("after-cap", 4)]
    again = ask(box.socket, query_of("after-cap"), small, timeout=30)
    assert is_scores(again, len(small)) and all(
        abs(got - score(query_of("after-cap"), text)) <= support.TOLERANCE for got, text in zip(again, small)), \
        f"after refusing a request over the cap, the service answered {again!r} to a normal one"[:400]


def test_a_search_with_more_texts_than_the_cap_still_answers(box):
    box.warm()
    query, given = query_of("big"), candidates("big", support.OVER_CAP)
    report = box.search(query, given)
    assert raised(report) is None, f"a search over the cap raised: {raised(report)}"
    check_scored_or_unranked(report["result"], query, given, "the search over the cap")


def test_a_request_past_its_time_limit_does_not_hold_the_search(boxes):
    limit = 3.0
    box = boxes(settings={support.TIMEOUT_SETTING: limit})
    service = box.warm()
    box.for_pid(service, predict_delay=60)  # the service's model now takes a minute to score
    query, given = query_of("slow"), candidates("slow", 5)
    report = box.search(query, given)
    assert raised(report) is None, f"a search whose request ran past its time limit raised: {raised(report)}"
    assert report["seconds"] <= limit + support.FALLBACK_S, \
        (f"a search whose request ran past its time limit ({support.TIMEOUT_SETTING}={limit:g}) took "
         f"{report['seconds']:.1f} s")
    # The service did not answer in time, and a private reranker can start here: the search falls back to it.
    check_scored(report["result"], query, given, "the search past its time limit")
    assert box.scorers_of(query) - {service}, \
        "no private reranker scored the search's texts, yet the slow service had not finished scoring them"
