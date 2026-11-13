"""KPI 7 (DEC-1042 item 4, P-W2-123-4): the bounded retry of a rebuild's chunk embedding (W2-123, DEC-1026) also
covers a transient server error (HTTP 5xx) and a reset or refused connection, within the same bound, and still fails
closed after its last try.

The bound is W2-123's: ``len(RETRY_WAITS_S) + 1`` tries of one chunk batch request, a wait of ``RETRY_WAITS_S`` before
each later try, each try under ``TIMEOUT_S``; after the last failed try the stage stops (no later batch is sent) and
``refresh`` reports ``FACET_UNAVAILABLE`` with a reason that begins with ``NO_EMBEDDING``; a search without refresh
then finds the store stale. Only what KPI 7 adds is tested here; W2-123's own time-out cases stay in
``tests/acceptance/W2-123/test_w2_123_retry.py``.

How the cases run (README): ``semantic.refresh`` (then, where named, ``semantic.search(..., refresh=False)``) in a
child process whose ``PYTHONPATH`` is this repository's ``src/`` (DEC-732), with ``TIMEOUT_S`` and ``RETRY_WAITS_S``
lowered in the child before the call; the environment is the suite's ``Box`` (its own HOME, cache folder, no
``ollama`` on PATH). The embedder is a stand-in on a loopback port (``Flaky``) that numbers chunk batches by their
texts and fails a chosen batch's first tries as the case says: an HTTP 5xx, a reset connection (the request read,
then the socket closed with RST), a held request (no answer within ``TIMEOUT_S``), or a refused connection (the
listening socket closed, so nothing listens, then opened again on the same port). Nothing else is reached.
"""

from __future__ import annotations

import json
import socket
import struct
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import w2_126_support as S

TIMEOUT_S = 1.0                 # the lowered per-request timeout (a held try is given up after it)
RETRY_WAITS_S = (0.25, 0.75)    # the lowered waits before the 2nd and 3rd try
TRIES = len(RETRY_WAITS_S) + 1
REFUSED_WAITS_S = (2.0, 3.0)    # the refused-then-answered case: longer waits, so the listener is back before try 2
DOWN_S = 1.0                    # ... and nothing listens for this long after batch 0's answer
HOLD_S = 10.0                   # how long a held try is held: far past TIMEOUT_S
EARLY_S = 0.05                  # a gap between two tries may be this much shorter than its wait (and timeout)
LATE_S = 1.5                    # ... and this much longer (scheduling)

MARKER = "w2126retry"           # every chunk text holds one ``w2126retryNNN``; no other text sent holds it
FILES, SECTIONS = 2, 40         # 80 chunks: at BATCH 32, three chunk batch requests
ALL_MARKERS = {f"{MARKER}{index:03d}" for index in range(FILES * SECTIONS)}


def corpus():
    return {f"notes/part-{part}.md": "".join(
        f"## Section {MARKER}{index:03d}\n\nThe {MARKER}{index:03d} section keeps one line of its own.\n\n"
        for index in range(part * SECTIONS, (part + 1) * SECTIONS)) for part in range(FILES)}


# --------------------------------------------------------------------------
# The stand-in embedder that fails as the case says
# --------------------------------------------------------------------------

class Flaky:
    """An Ollama endpoint on a loopback port. ``plan[n]``: the outcomes of chunk batch ``n``'s first tries, each
    ``"500"``/``"503"``/``"400"`` (that HTTP status at once), ``"reset"``, ``"held"``, ``"not-json"`` or
    ``"no-vector"``; later tries are answered. ``down_after``: once batch ``down_after`` is answered and then the
    device read that follows it (``/api/ps``) is answered, the listening socket is closed before that answer is
    sent, so the next connection (the next batch's first try) is refused; it is opened again on the same port after
    ``down_s`` seconds (never, when ``down_s`` is None). ``ps``: ``"answer"`` (the model on the GPU) or ``"reset"``
    (every ``/api/ps`` connection reset: the device can never be read). ``ps_reads`` counts the ``/api/ps`` requests.

    Rewrite-Reason: DEC-1065 (1) (the device is read, never assumed): after each batch the device is read from
    ``/api/ps`` and an unreadable read is retried as the request is (W2-32's S10, F-2). The listener used to close
    right after batch ``down_after``'s answer, so the refusal fell on that device read, not on the next batch as the
    cases mean; it now closes once the device read after the batch is answered too."""

    def __init__(self, plan=None, down_after=None, down_s=None, ps="answer"):
        self.plan, self.down_after, self.down_s, self.ps = dict(plan or {}), down_after, down_s, ps
        self.armed, self.ps_reads = False, 0
        self.lock, self.release = threading.Lock(), threading.Event()
        self.batches, self.tries = [], []   # each batch's texts; every chunk batch try {"batch", "try", "at", "outcome"}
        self.down_at = None
        self.server = self._listen(0)
        self.port = self.server.server_address[1]
        self.host = f"127.0.0.1:{self.port}"

    def _listen(self, port):
        flaky = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                route = self.path.split("?")[0].rstrip("/")
                outcome, status, payload = flaky.reply(route, asked)
                if outcome == "held":
                    flaky.release.wait(HOLD_S)
                    self.close_connection = True
                    return
                if outcome == "reset":
                    self.close_connection = True
                    self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER, struct.pack("ii", 1, 0))
                    self.connection.close()
                    return
                if outcome == "go-down":
                    flaky.go_down()
                try:
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Content-Length", str(len(payload)))
                    self.end_headers()
                    self.wfile.write(payload)
                except OSError:
                    pass

            do_GET = do_POST = do_HEAD = answer

            def log_message(self, *args):
                pass

            def handle(self):
                try:
                    super().handle()
                except OSError:
                    pass

        server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        server.daemon_threads = True
        server.block_on_close = False
        threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
        return server

    def reply(self, route, asked):
        model = {"name": S.MODEL, "model": S.MODEL, "digest": S.REVISION_1, "size": 639150000}
        if route == "/api/version":
            return "answered", 200, json.dumps({"version": "0.35.0"}).encode()
        if route == "/api/tags":
            return "answered", 200, json.dumps({"models": [model]}).encode()
        if route == "/api/ps":
            # Rewrite-Reason: W2-32's S10 (DEC-1065): the model on the GPU
            with self.lock:
                self.ps_reads += 1
                going = self.armed and self.down_at is None
            if self.ps == "reset":
                return "reset", 0, b""
            payload = json.dumps({"models": [{**model, "size_vram": model["size"]}]}).encode()
            return ("go-down" if going else "answered"), 200, payload
        if route != "/api/embed":
            return "answered", 404, b'{"error": "not found"}'
        given = asked.get("input", "")
        texts = [given] if isinstance(given, str) else [str(text) for text in given]
        answer = json.dumps({"model": S.MODEL, "embeddings": [S.vector_of(text, S.REVISION_1, 64)
                                                              for text in texts]}).encode()
        if not any(MARKER in text for text in texts):
            return "answered", 200, answer
        with self.lock:
            key = tuple(texts)
            if key not in self.batches:
                self.batches.append(key)
            batch = self.batches.index(key)
            number = 1 + sum(1 for entry in self.tries if entry["batch"] == batch)
            planned = self.plan.get(batch, [])
            outcome = planned[number - 1] if number <= len(planned) else "answered"
            self.tries.append({"batch": batch, "try": number, "at": time.monotonic(), "outcome": outcome})
        if outcome in ("500", "503", "400"):
            return outcome, int(outcome), json.dumps({"error": "the runner failed"}).encode()
        if outcome == "not-json":
            return outcome, 200, b"this is not JSON"
        if outcome == "no-vector":
            return outcome, 200, b'{"embeddings": []}'
        if outcome == "answered" and batch == self.down_after and self.down_at is None:
            self.armed = True  # down once the device read that follows this answer is answered (DEC-1065 (1))
        return outcome, 200, answer

    def go_down(self):
        """Nothing listens from now: the serving loop is stopped and the listening socket closed (this answer is
        still sent on its own connection); after ``down_s`` a new listener is opened on the same port."""
        self.server.shutdown()
        self.server.socket.close()
        self.down_at = time.monotonic()
        if self.down_s is not None:
            def back():
                time.sleep(self.down_s)
                self.server = self._listen(self.port)
            threading.Thread(target=back, daemon=True).start()

    def tries_of(self, batch):
        return [entry for entry in self.tries if entry["batch"] == batch]

    def outcomes_of(self, batch):
        return [entry["outcome"] for entry in self.tries_of(batch)]

    def answered_markers(self):
        found = set()
        for entry in self.tries:
            if entry["outcome"] in ("answered", "go-down"):
                for text in self.batches[entry["batch"]]:
                    found.update(word for word in text.split() if word.startswith(MARKER))
        return {word[:len(MARKER) + 3] for word in found}

    def close(self):
        self.release.set()
        try:
            self.server.shutdown()
            self.server.server_close()
        except OSError:
            pass


# --------------------------------------------------------------------------
# The child: refresh (and a search without refresh) with the two settings lowered
# --------------------------------------------------------------------------

_DRIVER = r'''
import json, sys
from gov.retrieval import semantic

request = json.loads(sys.stdin.read())
semantic.TIMEOUT_S = float(request["timeout_s"])
semantic.RETRY_WAITS_S = tuple(request["waits_s"])
out = {"no_embedding": semantic.NO_EMBEDDING, "refresh": semantic.refresh(request["root"])}
if request.get("question"):
    out["search"] = semantic.search(request["root"], request["question"], refresh=False)
sys.stdout.write("\n" + json.dumps(out, default=repr) + "\n")
'''


def run(box, root, waits=RETRY_WAITS_S, question=None):
    """The child's results, and the monotonic time at which it ended."""
    script = box.workdir / "w2_126_retry_driver.py"
    script.write_text(_DRIVER, encoding="utf-8")
    request = {"root": str(root), "timeout_s": TIMEOUT_S, "waits_s": list(waits), "question": question}
    try:
        done = subprocess.run([sys.executable, str(script)], input=json.dumps(request), capture_output=True,
                              text=True, env=box.env(), cwd=str(box.workdir / "elsewhere"),
                              timeout=S.CALL_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"the driver did not end within {S.CALL_TIMEOUT_S:.0f} s") from None
    ended = time.monotonic()
    assert done.returncode == 0, f"the driver failed (exit {done.returncode}):\n{done.stderr[-6000:]}"
    return json.loads(done.stdout.strip().splitlines()[-1]), ended


@pytest.fixture
def place(tmp_path):
    reason = S.lacking()
    if reason:
        pytest.skip(reason)
    made = []

    def make(**settings):
        flaky = Flaky(**settings)
        made.append(flaky)
        return S.Box(tmp_path / "box", flaky), flaky, S.plant(tmp_path / "project", corpus=corpus())

    yield make
    for flaky in made:
        flaky.close()


def retried(report):
    """The report's ``retries`` (W2-123's R3): one entry per chunk batch request tried more than once."""
    assert "retries" in report, f"refresh's report has no `retries`: {report}"
    return report["retries"]


def gaps(tries):
    return [later["at"] - earlier["at"] for earlier, later in zip(tries, tries[1:])]


def least_gap(outcome, wait):
    """The least time from a try with this outcome to the next: its wait, after the timeout if it was held."""
    return wait + (TIMEOUT_S if outcome == "held" else 0.0) - EARLY_S


# --------------------------------------------------------------------------
# Success: a transient failure, then an answer
# --------------------------------------------------------------------------

@pytest.mark.parametrize("failure", ("500", "503", "reset"))
def test_a_transient_failure_then_an_answer_is_tried_again_and_the_stage_is_built(place, failure):
    """*Red on the base.* Batch 0's first try fails (HTTP 500, HTTP 503, or the connection reset), the second is
    answered: it is tried again after the first wait, the build goes on to every later batch, the stage is built and
    ``retries`` states the request (2 tries, the first wait, embedded). The base sends the batch once and ends the
    stage with ``NO_EMBEDDING``."""
    box, flaky, project = place(plan={0: [failure]})
    out, _ = run(box, project)
    report = out["refresh"]
    assert flaky.outcomes_of(0) == [failure, "answered"], \
        f"after a {failure}, the batch was not tried again exactly once: {flaky.tries_of(0)}; report {report}"
    [gap] = gaps(flaky.tries_of(0))
    assert least_gap(failure, RETRY_WAITS_S[0]) <= gap <= RETRY_WAITS_S[0] + LATE_S, \
        f"the second try came {gap:.2f} s after the first, not after the first wait ({RETRY_WAITS_S[0]} s)"
    assert report["available"] is True and report["state"] != "FACET_UNAVAILABLE", report
    assert flaky.answered_markers() == ALL_MARKERS, "the build did not go on to every later batch after the retry"
    entries = retried(report)
    assert len(entries) == 1 and entries[0].get("tries") == 2 and entries[0].get("embedded") is True \
        and entries[0].get("waits_s") == [pytest.approx(RETRY_WAITS_S[0], abs=0.1)], report


def test_a_refused_connection_then_an_answer_is_tried_again_and_the_stage_is_built(place):
    """*Red on the base.* Once batch 0 is answered nothing listens for ``DOWN_S`` (1 s), so batch 1's first try is
    refused; the listener is back before the first wait (2 s) ends, and the second try is answered: the stage is
    built, every chunk embedded, ``retries`` states one request of 2 tries, embedded. The base ends the stage at the
    refusal: batch 1 never reaches the stand-in."""
    box, flaky, project = place(down_after=0, down_s=DOWN_S)
    out, _ = run(box, project, waits=REFUSED_WAITS_S)
    report = out["refresh"]
    assert flaky.down_at is not None, ("the case's set-up: the stand-in never went down (it goes down once batch 0 "
                                       f"and the device read after it are answered): {flaky.tries_of(0)}, "
                                       f"{flaky.ps_reads} device reads (DEC-1065 (1))")
    assert flaky.outcomes_of(1) == ["answered"], \
        f"batch 1 did not reach the stand-in once after its refused try: {flaky.tries_of(1)}; report {report}"
    late = flaky.tries_of(1)[0]["at"] - flaky.down_at
    assert late >= REFUSED_WAITS_S[0] - EARLY_S, \
        f"batch 1 came {late:.2f} s after nothing listened: no wait after a refused try ({REFUSED_WAITS_S[0]} s)"
    assert report["available"] is True and report["state"] != "FACET_UNAVAILABLE", report
    assert flaky.answered_markers() == ALL_MARKERS, "not every chunk was embedded"
    entries = retried(report)
    assert len(entries) == 1 and entries[0].get("tries") == 2 and entries[0].get("embedded") is True, report


# --------------------------------------------------------------------------
# Failure: still failing closed after the last try, within the same bound
# --------------------------------------------------------------------------

FAILING = {"500": ["500"] * TRIES, "503": ["503"] * TRIES, "reset": ["reset"] * TRIES,
           "mixed": ["held", "500", "reset"]}


@pytest.mark.parametrize("failure", sorted(FAILING))
def test_a_transient_failure_at_every_try_fails_closed_after_the_last_try_within_the_bound(place, failure):
    """*Red on the base.* Batch 0 is answered; batch 1 fails at every try (HTTP 500, HTTP 503, reset, or a mix of a
    time-out, a 500 and a reset, which share the one bound): exactly ``TRIES`` tries, the waits between them, then no
    later batch; ``refresh`` reports ``FACET_UNAVAILABLE`` with a reason beginning ``NO_EMBEDDING``; ``retries``
    states ``TRIES`` tries, not embedded; a search without refresh finds the store stale, no hit. The base sends batch
    1 once."""
    box, flaky, project = place(plan={1: FAILING[failure]})
    out, ended = run(box, project, question="which note keeps one line of its own")
    report, answer = out["refresh"], out["search"]
    tries = flaky.tries_of(1)
    assert [entry["outcome"] for entry in tries] == FAILING[failure], \
        f"the batch that kept failing was not tried exactly {TRIES} times: {tries}; report {report}"
    for index, (gap, wait) in enumerate(zip(gaps(tries), RETRY_WAITS_S)):
        least = least_gap(tries[index]["outcome"], wait)
        assert least <= gap <= least + EARLY_S + LATE_S, \
            f"try {index + 2} came {gap:.2f} s after try {index + 1}, not after its wait ({wait} s)"
    assert len(flaky.batches) == 2, f"a later batch was sent after the last failed try: {len(flaky.batches)} batches"
    bound = sum(RETRY_WAITS_S) + (TIMEOUT_S if "held" in FAILING[failure] else 0.0) + 2 * LATE_S
    assert ended - tries[0]["at"] <= bound, \
        f"from the first try to the end took {ended - tries[0]['at']:.2f} s (bound {bound:.2f} s)"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert str(report.get("reason") or "").startswith(out["no_embedding"]), report
    entries = retried(report)
    assert entries and entries[-1].get("tries") == TRIES and entries[-1].get("embedded") is False, report
    assert answer["available"] is False and answer["state"] == "FACET_UNAVAILABLE", answer
    assert answer["reason"] == "stale" and answer.get("hits") == [], answer


def test_a_refused_connection_at_every_try_fails_closed_after_the_last_try_within_the_bound(place):
    """*Red on the base.* Once batch 0 is answered nothing listens again: batch 1 is refused at every try. The stage
    waits both waits (so it tried again), ends within the bound, reports ``FACET_UNAVAILABLE`` with a reason beginning
    ``NO_EMBEDDING`` and ``retries`` states ``TRIES`` tries, not embedded. The base ends at the first refusal, at
    once, with no ``retries`` entry."""
    box, flaky, project = place(down_after=0, down_s=None)
    out, ended = run(box, project)
    report = out["refresh"]
    assert flaky.down_at is not None, ("the case's set-up: the stand-in never went down (it goes down once batch 0 "
                                       f"and the device read after it are answered): {flaky.tries_of(0)}, "
                                       f"{flaky.ps_reads} device reads (DEC-1065 (1))")
    took = ended - flaky.down_at
    assert took >= sum(RETRY_WAITS_S) - EARLY_S, \
        f"the stage ended {took:.2f} s after nothing listened: it did not wait {sum(RETRY_WAITS_S)} s to try again"
    assert took <= sum(RETRY_WAITS_S) + TRIES * TIMEOUT_S + 2 * LATE_S, \
        f"the stage ended {took:.2f} s after nothing listened: beyond the bound"
    assert len(flaky.batches) == 1, f"a batch reached a stand-in that no longer listens: {len(flaky.batches)}"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert str(report.get("reason") or "").startswith(out["no_embedding"]), report
    entries = retried(report)
    assert entries and entries[-1].get("tries") == TRIES and entries[-1].get("embedded") is False, report


def _cache_rows(box):
    """The rows of every table of the machine-wide cache's files (the case's own folder)."""
    import sqlite3
    total = 0
    for path in sorted(box.cache_dir.glob("*.db")) if box.cache_dir.is_dir() else []:
        connection = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            for (name,) in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'").fetchall():
                total += connection.execute(f'SELECT count(*) FROM "{name}"').fetchone()[0]
        finally:
            connection.close()
    return total


def _stored(project):
    import sqlite3
    try:
        return S.store_vectors(project)
    except sqlite3.Error:  # no vector table: nothing stored
        return {}


def test_a_device_read_that_never_answers_fails_closed_and_stores_nothing(place):
    """DEC-1065 (1) (the device is read, never assumed; W2-32's S10, F-2): every ``/api/ps`` connection is reset, so
    the device of batch 0's vectors can never be read. The read is tried again (more than once); then the stage fails
    closed, named ``EMBEDDER_DEVICE_UNREAD``: no later batch is sent, no vector is stored in the store or the
    machine-wide cache, and the stage is not reported built.

    Rewrite-Reason: DEC-1065 (1) (the device is read, never assumed): a row added for the read the rule adds."""
    box, flaky, project = place(ps="reset")
    out, _ = run(box, project)
    report = out["refresh"]
    assert flaky.outcomes_of(0) == ["answered"], f"the case's set-up: batch 0 was not answered once: {flaky.tries}"
    assert flaky.ps_reads >= 2, f"the device read was not tried again ({flaky.ps_reads} read)"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert "EMBEDDER_DEVICE_UNREAD" in json.dumps(report), f"the refusal is not named EMBEDDER_DEVICE_UNREAD: {report}"
    assert len(flaky.batches) == 1, f"a later batch was sent after the device could not be read: {len(flaky.batches)}"
    assert _stored(project) == {}, f"vectors of an unread device were stored: {len(_stored(project))}"
    assert _cache_rows(box) == 0, "vectors of an unread device were cached"


# --------------------------------------------------------------------------
# Edge: what KPI 7 does not cover is still not retried
# --------------------------------------------------------------------------

def test_a_client_error_is_not_retried_and_the_stage_ends_at_once(place):
    """*Green on the base (a guard).* An HTTP 400 is not a transient server error: batch 0 is sent once, no later
    batch, ``FACET_UNAVAILABLE`` with exactly ``NO_EMBEDDING``, ``retries`` empty. W2-123's not-JSON and no-vector
    cases hold the same for a malformed answer."""
    box, flaky, project = place(plan={0: ["400"] * TRIES})
    out, _ = run(box, project)
    report = out["refresh"]
    assert flaky.outcomes_of(0) == ["400"], f"an HTTP 400 was tried again: {flaky.tries_of(0)}"
    assert len(flaky.batches) == 1, f"a later batch was sent: {len(flaky.batches)} batches"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert report["reason"] == out["no_embedding"], report
    assert retried(report) == [], report
