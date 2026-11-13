"""S4 (and failure line 2): a search the service cannot answer comes back without waiting for anything else, and
each such search writes one FALLBACK line naming the failure and "unranked" (DEC-374, DEC-1033, DEC-979 item 4).

- **The bounds**, timed over S1's planted kinds (``w2_145_support.KINDS``), by the search's own call time in its
  session: within ``CONNECT_S`` plus 1 s when nothing answers the socket (no connection within ``CONNECT_S``) or the
  socket is refused (EPERM); within ``CONNECT_S`` plus 1 s *of the refused start's end* when no service listens and
  its start is refused (the start itself is the shared service's: one that waits for a GPU slot, as S3 keeps, takes
  its own wait, which the planted interpreter records; what may not follow it is a second wait, a private's); within
  the request's time limit (``GOV_RERANK_TIMEOUT_S``, 3 s in every box) plus 1 s when the service does not answer or
  answers wrongly. Never the 20 s slot wait.
- **The log line:** exactly one line of ``~/.cache/gov-os/rerank.log`` of kind ``FALLBACK`` per such search (the
  second tab field, as ``gov status`` counts it), whose detail names the service's failure and says "unranked", and
  never "private".
- **A search that cannot write the log still searches** (``rerank.log`` is a folder): unranked, named, in its bound.
- **``gov status``'s reranker part** over a planted log (old lines, a private one among them, and new ones) and one
  real search's line: ``reranker.fallbacks`` counts every FALLBACK line, ``service_refusals`` every REFUSED line.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys

import pytest

import w2_145_support as support
from w2_145_support import BY_NAME, KIND_IDS, KINDS, Planted, box_for, candidates, check_unranked, query_of, raised


@pytest.mark.parametrize("kind", KINDS, ids=KIND_IDS)
def test_s4_an_unanswered_search_comes_back_within_its_bound_and_logs_one_fallback_line_unranked(boxes, kind):
    box = box_for(boxes, kind)
    planted = Planted(box, kind)
    try:
        query, given = query_of(f"s4-{kind.name}"), candidates(f"s4-{kind.name}", 6)
        report = box.search(query, given, env=planted.env)
        who = f"the search whose service is unreachable ({kind.name})"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        planted.premise()
        bound = support.bound_of(kind)
        if kind.bound == "start":
            late = report["ended"] - planted.service_end()
            assert late <= bound, \
                (f"{who} came back {late:.1f} s after the service's refused start ended (in all "
                 f"{report['seconds']:.1f} s): within CONNECT_S + 1 s = {bound:g} s, never waiting for anything else")
        else:
            assert report["seconds"] <= bound, \
                f"{who} took {report['seconds']:.1f} s: within {bound:g} s ({kind.bound} bound + 1 s)"
        lines = [detail for logged, detail in box.log_lines() if logged == "FALLBACK"]
        assert len(lines) == 1, f"{who} wrote {len(lines)} FALLBACK lines to rerank.log, one is expected: {lines}"
        detail = lines[0]
        assert re.search(r"\bunranked\b", detail, re.IGNORECASE), \
            f"{who}: its FALLBACK line does not say 'unranked': {detail!r}"
        assert not re.search(r"private", detail, re.IGNORECASE), \
            f"{who}: its FALLBACK line names a private reranker: {detail!r}"
        assert re.search(kind.reason, detail, re.IGNORECASE), \
            f"{who}: its FALLBACK line does not name the service's failure (/{kind.reason}/): {detail!r}"
    finally:
        planted.close()


# Kinds whose search starts no service: the service also writes rerank.log, so a refused start would end otherwise.
@pytest.mark.parametrize("name", ["socket-refused-eperm", "an-error-answer", "no-answer-within-the-time-limit"])
def test_s4_a_search_that_cannot_write_the_log_still_searches(boxes, name):
    kind = BY_NAME[name]
    box = box_for(boxes, kind)
    log = box.home / support.base.CACHE_REL / "rerank.log"
    log.mkdir(parents=True, mode=0o700)
    (log / "keep").write_text("the W2-145 tests: rerank.log cannot be written\n", encoding="utf-8")
    planted = Planted(box, kind)
    try:
        query, given = query_of(f"nolog-{name}"), candidates(f"nolog-{name}", 5)
        report = box.search(query, given, env=planted.env)
        who = f"the search that cannot write rerank.log ({name})"
        assert raised(report) is None, f"{who} raised: {raised(report)}"
        check_unranked(report["result"], given, who)
        outcome = report.get("outcome") or {}
        assert outcome.get("by") == "unavailable", f"{who}: last_outcome() is {outcome}"
        support.check_reason(outcome.get("reason"), kind, who)
        assert report["seconds"] <= support.bound_of(kind), f"{who} took {report['seconds']:.1f} s"
        support.check_no_private(box, report, who)
    finally:
        planted.close()


PLANTED_LOG = [
    ("FALLBACK", "the shared reranker did not answer (TimeoutError: timed out)\tprivate"),
    ("FALLBACK", "the shared reranker did not answer (ConnectionError: x)\tunavailable: the private reranker ended"),
    ("FALLBACK", "the shared reranker did not answer (PermissionError: [Errno 1])\tunranked"),
    ("REFUSED", "the shared reranker does not start: no GPU slot free within 20 s"),
    ("REFUSED", "the shared reranker does not start: the GPU has 1.0 GiB free"),
    ("READY", "pid 1 device cuda"),
    ("MEMORY", "allocated 1187 MiB, reserved 1534 MiB"),
    ("END", "pid 1 idle 900 s"),
]


def test_s4_gov_status_counts_every_unranked_search_as_a_fallback(boxes):
    kind = BY_NAME["socket-refused-eperm"]  # the one kind that needs no Unix socket: it runs anywhere
    box = box_for(boxes, kind)
    folder = box.home / support.base.CACHE_REL
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    (folder / "rerank.log").write_text(
        "".join(f"2026-11-09T10:00:0{number}+0000\t{logged}\t{detail}\n"
                for number, (logged, detail) in enumerate(PLANTED_LOG)), encoding="utf-8")
    planted = Planted(box, kind)
    try:
        query, given = query_of("status"), candidates("status", 4)
        report = box.search(query, given, env=planted.env)
        assert raised(report) is None, f"the search raised: {raised(report)}"
    finally:
        planted.close()
    planted_fallbacks = sum(1 for logged, _ in PLANTED_LOG if logged == "FALLBACK")
    refusals = sum(1 for logged, _ in PLANTED_LOG if logged == "REFUSED")
    done = subprocess.run([sys.executable, "-m", "gov.cli.main", "status", "--json", "--root", str(box.work)],
                          capture_output=True, text=True, env=box.env(), cwd=str(box.work), timeout=300,
                          stdin=subprocess.DEVNULL)
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        pytest.fail(f"gov status --json gave no JSON (exit {done.returncode}): {done.stderr[-1500:]}", pytrace=False)
    part = (answer.get("result") or {}).get("reranker")
    assert isinstance(part, dict), f"gov status --json has no reranker part: {done.stdout[:1500]}"
    assert part.get("fallbacks") == planted_fallbacks + 1, \
        (f"gov status counts {part.get('fallbacks')} fallbacks: the planted log holds {planted_fallbacks} FALLBACK "
         f"lines and the search wrote one more: {part}")
    assert part.get("service_refusals") == refusals, f"gov status counts {part.get('service_refusals')} refusals: {part}"
