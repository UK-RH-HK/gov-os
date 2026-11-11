"""A launched session's search and the shared reranker (W2-112, W2-145), through the session's own environment.

S8: a session started by `gov launch` can connect to the shared reranker service's socket and gets its answers; the
path comes from the same setting the service uses [DEC-1035].
S11: a sandboxed session's search that the shared service does not answer (W2-145: the order kept, named unavailable,
one FALLBACK line, unranked) is counted where the service's other FALLBACK lines are, so `gov status` shows it
[changed, DEC-1097 (8)].
F5: a sandboxed search answered unranked while the service runs; an unranked sandboxed search that `gov status` does
not count.

The stand-in session runs one search's rerank (``gov.retrieval.rerank.default_reranker()``) with its own environment,
under a planted ``HOME``: its reranker interpreter file, and either a stand-in service on the planted socket or none.
What the stand-in cannot show is the operating system's part (the sandbox's refusal of the socket or the log); the
settings-level cases (``test_w2_56_sandbox_block.py``) and the CTO's measurement (S10) show that. These two show that
the session's environment (S5's cleaning) still leads its search to the service's socket and its FALLBACK line to the
log ``gov status`` reads (``gov.retrieval.rerank.status``, the function ``gov status``'s ``reranker`` part calls).
"""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_56_support as s
import w2_56_sandbox_support as sb

SEARCH = ("import json\nfrom gov.retrieval import rerank\nscore = rerank.default_reranker()\n"
          "values = score('w56 question', ['alpha', 'beta', 'gamma']) if score else None\n"
          "print(json.dumps({'values': values, 'outcome': rerank.last_outcome()}))\n")


def _status(box) -> dict:
    code = "import json\nfrom gov.retrieval.rerank import status\nprint(json.dumps(status()))\n"
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=s.base_environment(box),
                          timeout=s.COMMAND_TIMEOUT_S)
    assert done.returncode == 0, f"gov's reranker status could not be read:\n{done.stderr[-1200:]}"
    return json.loads(done.stdout.strip().splitlines()[-1])


def test_s8_a_search_in_the_launched_session_reaches_the_planted_service_and_is_ranked():
    why = sb.unix_sockets_refused_here()
    if why:
        pytest.skip(f"this run's own sandbox refuses Unix sockets ({why}): the CTO runs it outside the sandbox")
    base = sb.short_base("w56-")
    if base is None:
        pytest.skip("no short folder can be made for the planted socket (107 bytes)")
    service = None
    try:
        box = s.make_box(base)
        if len(sb.reranker_socket(box.home)) > 100:
            pytest.skip(f"the planted socket path is too long here: {sb.reranker_socket(box.home)}")
        sb.project(box)
        sb.plant_interpreter(box.home, "#!/bin/sh\nexit 0\n")
        service = sb.StandInService(sb.reranker_socket(box.home))
        s.set_plan(box, [sb.python_step("search", SEARCH)])
        sb.started(s.run_launch(box, s.ENGINEER, s.T.tk))
        found = sb.step_json(box, "search")
        assert found["outcome"]["by"] == "service", f"the session's search was not answered by the service: {found}"
        assert found["values"] == [3.0, 2.0, 1.0], f"the session's search did not get the service's scores: {found}"
        assert len(service.requests) == 1, f"the planted service got {len(service.requests)} requests, not 1"
        assert _status(box)["fallbacks"] == 0, "a ranked search was counted as a fallback"
    finally:
        if service is not None:
            service.close()
        sb.remove(base)


def test_s11_an_unranked_search_in_the_launched_session_is_counted_where_gov_status_counts(tmp_path):
    box = s.make_box(tmp_path)
    sb.project(box)
    sb.plant_interpreter(box.home)       # no service listens; the one that starts ends at once (exit 78)
    s.set_plan(box, [sb.python_step("search", SEARCH)])
    sb.started(s.run_launch(box, s.ENGINEER, s.T.tk))
    found = sb.step_json(box, "search")
    assert found["values"] is None and found["outcome"]["by"] == "unavailable", (
        f"the session's search was not left unranked and named: {found}")
    status = _status(box)
    assert status["fallbacks"] == 1, (
        f"gov status counts {status['fallbacks']} fallbacks after the session's one unranked search: {status}")
