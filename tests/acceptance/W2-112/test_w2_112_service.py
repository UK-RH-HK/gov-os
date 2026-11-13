"""KPI success 1 and failure 2: one reranker process serves every session (DEC-979 item 4, P-RERANKER-1).

The same pinned model, revision and environment as today (ADR-0002 §2, DEC-397), listening on a local socket in
the user's own folder (mode 0600, no network port), started on demand by the first search that needs it under a
lock (two searches starting together start one service), ending itself after a set idle time. Failure: two
services started at once, or a socket another user can open.

Every case runs in its own temporary ``HOME`` with the stand-in reranker environment (``w2_112_support``); the
service is seen from outside: the socket, the processes that carry that ``HOME``, and the stand-in model's log.
"""

from __future__ import annotations

import os
import stat
import time

import w2_112_support as support
from w2_112_support import candidates, check_scored, query_of, raised


def test_nothing_is_started_before_a_search_needs_the_reranker(box):
    # Importing the module and a rerank of nothing start no service and load no model (W1-19's lazy load).
    report = box.search(query_of("empty"), [])
    assert raised(report) is None, f"a rerank of nothing raised: {raised(report)}"
    assert report["result"] == [], f"a rerank of nothing returned {report['result']!r}"
    assert box.sockets() == [], f"a socket was made although nothing needed the reranker: {box.sockets()}"
    assert box.events("load") == [], "the model was loaded although nothing was to be reranked"
    assert support.processes_of(box.home) == [], \
        f"processes were left running although nothing needed the reranker: {support.processes_of(box.home)}"


def test_the_first_search_starts_one_service_that_outlives_it_and_serves_the_next_session(box):
    first, given = query_of("first"), candidates("first", 6)
    report = box.search(first, given)
    assert raised(report) is None, f"the first search raised: {raised(report)}"
    check_scored(report["result"], first, given, "the first search")
    holders = [record["pid"] for record in box.live_loads()]
    assert len(holders) == 1, \
        (f"after the first search ended, {len(holders)} live processes hold the model ({holders}): the first search "
         f"is expected to start one service that stays up for every other session (a private reranker ends with its "
         f"search){support.note()}")
    service = holders[0]
    assert service != report["pid"], "the model is held by the search's own process, not by a service"

    second, other = query_of("second"), candidates("second", 5)
    again = box.search(second, other)
    assert raised(again) is None, f"the second search raised: {raised(again)}"
    check_scored(again["result"], second, other, "the second search")
    assert box.scorers_of(second) == {service}, \
        f"the second session was scored by {box.scorers_of(second)}, not by the one service {service}"
    assert len(box.loads()) == 1, f"the model was loaded {len(box.loads())} times for two sessions: one is expected"


def test_the_service_runs_the_pinned_model_from_the_reranker_environment_offline(box):
    # The same pinned model, revision and environment as today (ADR-0002 §2, DEC-397); offline, as today.
    query, given = query_of("pins"), candidates("pins", 4)
    report = box.search(query, given)
    assert raised(report) is None, f"the search raised: {raised(report)}"
    loads = box.loads()
    assert loads, "no model was loaded for a search that had candidates to rerank"
    for record in loads:
        assert record["model"] == support.MODEL, f"the model loaded is {record['model']!r}, not {support.MODEL}"
        assert record["revision"] == support.REVISION, \
            f"the revision loaded is {record['revision']!r}, not {support.REVISION} (given as revision=)"
        assert os.path.realpath(record["prefix"]) == os.path.realpath(box.venv), \
            f"the model was loaded in {record['prefix']}, not in the reranker environment {box.venv} (DEC-397)"
        assert record["hf_hub_offline"] == "1", "the model was loaded without HF_HUB_OFFLINE=1: it could be fetched"
    services = [record for record in loads if support.alive(record["pid"])]
    assert len(services) == 1, \
        f"no service holds the pinned model after the search ended ({len(services)} live holders)"


def test_the_socket_is_in_the_users_folder_the_users_alone_and_there_is_no_network_port(box):
    box.warm()
    sockets = box.sockets()
    assert sockets == [box.socket], \
        f"the service's socket is not the one P-RERANKER-1 names (~/{support.SOCKET_REL}): {sockets}"
    status = box.socket.lstat()
    assert stat.S_ISSOCK(status.st_mode), f"{box.socket} is not a Unix socket"
    assert status.st_uid == os.getuid(), f"the socket belongs to uid {status.st_uid}, not to the user"
    mode = stat.S_IMODE(status.st_mode)
    assert mode & 0o077 == 0, f"the socket's mode is {oct(mode)}: another user can open it (0600 is asked)"
    assert mode & 0o600 == 0o600, f"the socket's mode is {oct(mode)}: its owner cannot use it"
    service = box.service()
    assert service, "no process holds the socket"
    for pid in support.processes_of(box.home):
        assert support.network_sockets(pid) == [], \
            f"process {pid} of the service holds a network socket: {support.network_sockets(pid)} (none is allowed)"


def test_two_searches_starting_together_start_one_service(box):
    box.config(load_delay=0.5)  # a slow start widens the race the lock closes
    tags = ("left", "right")
    reports = box.together([{"query": query_of(tag), "candidates": candidates(tag, 5)} for tag in tags])
    for tag, report in zip(tags, reports):
        assert raised(report) is None, f"search {tag} raised: {raised(report)}"
        check_scored(report["result"], query_of(tag), candidates(tag, 5), f"search {tag}")
    loads = box.loads()
    assert len(loads) == 1, \
        f"two searches starting together loaded the model {len(loads)} times ({[r['pid'] for r in loads]}): one"
    assert len(box.sockets()) <= 1 and len(support.listening(box.socket)) == 1, \
        f"not exactly one service listens: socket files {box.sockets()}, listening {support.listening(box.socket)}"
    scorers = box.scorers_of(query_of("left")) | box.scorers_of(query_of("right"))
    assert scorers == {loads[0]["pid"]}, f"the two searches were scored by {scorers}, not by the one service"


def test_the_service_ends_itself_after_its_idle_time_and_the_next_search_starts_it_again(boxes):
    idle = 4.0
    box = boxes(settings={support.IDLE_SETTING: idle})
    service = box.warm("idle-0")
    # Two more searches, each less than the idle time after the one before, the last more than the idle time
    # after the first: the idle time counts from the last request, so the same service answers all three.
    for number in (1, 2):
        time.sleep(idle * 0.6)
        query, given = query_of(f"idle-{number}"), candidates(f"idle-{number}", 3)
        report = box.search(query, given)
        assert raised(report) is None, f"search {number} raised: {raised(report)}"
        check_scored(report["result"], query, given, f"search {number}")
        assert box.scorers_of(query) == {service}, \
            f"search {number}, {idle * 0.6:.1f} s after the one before, was not answered by the same service"
    last = time.monotonic()
    deadline = last + idle + 20.0
    while time.monotonic() < deadline and (support.processes_of(box.home) or box.answers()):
        time.sleep(0.25)
    left = support.processes_of(box.home)
    assert not left and not box.answers(), \
        (f"the service did not end itself {time.monotonic() - last:.0f} s after its last request with "
         f"{support.IDLE_SETTING}={idle:g}: processes {left}, socket answering: {box.answers()}")
    query, given = query_of("idle-after"), candidates("idle-after", 3)
    report = box.search(query, given)
    assert raised(report) is None, f"the search after the idle end raised: {raised(report)}"
    check_scored(report["result"], query, given, "the search after the idle end")
    live = box.live_loads()
    assert len(live) == 1 and live[0]["pid"] != service, \
        f"the next search did not start a new service on demand after the idle end: live holders {live}"


def test_after_the_service_died_a_later_search_starts_a_new_one_and_never_a_second(box):
    killed = box.warm("before")
    box.kill_service()
    later = []
    for number in (1, 2):
        query, given = query_of(f"after-{number}"), candidates(f"after-{number}", 4)
        report = box.search(query, given)
        assert raised(report) is None, f"search {number} after the service died raised: {raised(report)}"
        check_scored(report["result"], query, given, f"search {number} after the service died")
        later.append(query)
        assert len(support.listening(box.socket)) <= 1, "two services listen at once"
    live = [record["pid"] for record in box.live_loads()]
    assert len(live) == 1 and live[0] != killed, \
        f"no new service was started on demand after the first one died (live holders of the model: {live})"
    assert box.scorers_of(later[-1]) == {live[0]}, "the last search was not answered by the new service"
