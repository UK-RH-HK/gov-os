"""KPI success 1 and failure "a stage's time missing": the output and the record give every stage's time.

``gov rebuild --json``'s ``timing`` gives ``record_s``, ``lexical_s``, ``secrets_s``, ``semantic_s``,
``codeintel_s``, ``compaction_s`` and ``total_s``, every one a number, also for a stage that did not run; the record
``.gov-runtime/rebuild/record.json`` (named by the result's ``record``) holds the same times, the lock part, the
threshold and whether the rebuild was slow (DEC-939 item 2, row W2-L451).
"""

from __future__ import annotations

import contextlib
import hashlib
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

import w2_76_support as support

pytestmark = support.needs_tools

# A stage's time may be rounded; the secrets filter's time is compared with the two stages it runs inside with this
# much room for rounding each.
ROUNDING_S = 0.11

MODEL = "qwen3-embedding:0.6b"
DIGEST = "ac6da0dfba84" + hashlib.sha256(b"w2-76 stand-in").hexdigest()[:52]   # ADR-0002's pin: the default
DIMENSIONS = 1024


def _vector(text):
    vector = [0.0] * DIMENSIONS
    for word in re.findall(r"[a-z0-9]+", str(text).lower()):
        vector[int.from_bytes(hashlib.sha256(word.encode()).digest()[:4], "big") % DIMENSIONS] += 1.0
    return vector if any(vector) else [1.0] + [0.0] * (DIMENSIONS - 1)


@contextlib.contextmanager
def _healthy_endpoint():
    """Ollama's HTTP interface on a loopback port, reporting the pinned model on the GPU and embedding with a
    stand-in; yields its ``host:port``. Rewrite-Reason: DEC-1027 C (the rebuild refuses an embedded namespace with no
    embedder); P1-L (a), DEC-1150 (3): a full rebuild of an embedded project needs an endpoint that answers."""
    entry = {"name": MODEL, "model": MODEL, "digest": DIGEST, "size": 639150000,
             "details": {"family": "qwen3", "parameter_size": "595.78M", "quantization_level": "Q8_0"}}

    class Handler(BaseHTTPRequestHandler):
        def answer(self):
            length = int(self.headers.get("Content-Length") or 0)
            try:
                asked = json.loads(self.rfile.read(length).decode("utf-8", "replace")) if length else {}
            except ValueError:
                asked = {}
            route, status = self.path.split("?")[0].rstrip("/"), 200
            if route == "/api/version":
                reply = {"version": "0.35.0"}
            elif route == "/api/tags":
                reply = {"models": [entry]}
            elif route == "/api/ps":
                reply = {"models": [{**entry, "size_vram": entry["size"]}]}
            elif route == "/api/show":
                reply = {"details": entry["details"], "capabilities": ["embedding"],
                         "model_info": {"general.architecture": "qwen3", "qwen3.embedding_length": DIMENSIONS}}
            elif route in ("/api/embed", "/api/embeddings"):
                given = asked.get("input", asked.get("prompt", ""))
                texts = [given] if isinstance(given, str) else list(given)
                reply = ({"model": MODEL, "embeddings": [_vector(text) for text in texts]} if route == "/api/embed"
                         else {"embedding": _vector(texts[0] if texts else "")})
            else:
                reply, status = {}, 404
            payload = json.dumps(reply).encode()
            try:
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
            except OSError:
                pass

        do_GET = do_POST = do_HEAD = do_DELETE = answer

        def log_message(self, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()
    try:
        yield f"127.0.0.1:{server.server_address[1]}"
    finally:
        server.shutdown()
        server.server_close()


def _number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


@pytest.mark.parametrize("form", [("--no-embeddings",), ()], ids=["no-embeddings", "full"])
def test_every_stage_timed_in_output_and_record(box, lock, env, form):
    project = support.make_project(box, "project", lock)

    if form:
        run = support.rebuild(project, env, *form)
    else:  # the full rebuild stays full (its semantic stage timed); it is given an endpoint that answers (DEC-1027 C)
        with _healthy_endpoint() as host:
            run = support.rebuild(project, {**env, "OLLAMA_HOST": host, "GOV_QUERY_OLLAMA_HOST": host}, *form)

    assert run.returncode == 0 and run.envelope().get("ok") is True, f"the rebuild did not succeed\n{run.describe()}"
    result = run.result
    if not form:
        assert (result.get("stores") or {}).get("semantic", {}).get("status") == "recreated", \
            f"the full rebuild did not run its semantic stage\n{run.describe()}"
    timing = result.get("timing")
    assert isinstance(timing, dict), f"the result has no timing\n{run.describe()}"
    missing = [key for key in support.STAGE_KEYS if key not in timing]
    assert not missing, f"stage times missing from the output's timing: {missing}\n{run.describe()}"
    not_numbers = {key: timing[key] for key in support.STAGE_KEYS if not _number(timing[key]) or timing[key] < 0}
    assert not not_numbers, f"stage times that are not non-negative numbers: {not_numbers}"
    assert not [key for key in timing if "wait" in key], f"the lock's wait is in timing: {timing}"
    assert timing["secrets_s"] <= timing["lexical_s"] + timing["codeintel_s"] + 2 * ROUNDING_S, \
        f"the secrets filter, which runs inside the lexical and code-index stages, took longer than both: {timing}"
    for key in support.STAGE_KEYS:
        assert timing[key] <= timing["total_s"] + ROUNDING_S, f"{key} is longer than total_s: {timing}"
    assert timing["total_s"] <= run.seconds + 1.0, f"total_s is longer than the whole run ({run.seconds:.1f} s)"

    assert result.get("slow") is False and result.get("slow_after_s") == 600, \
        f"a rebuild under its threshold says slow: false with slow_after_s\n{run.describe()}"
    assert result.get("watchdog_faults") == [], f"watchdog_faults is not an empty list\n{run.describe()}"
    assert result.get("record") == support.RECORD_REL, f"the result does not name the record\n{run.describe()}"

    record, text = support.read_record(project)
    assert record is not None, f"no whole record at {support.RECORD_REL} after the rebuild (read: {text!r:.300})"
    assert record.get("timing") == timing, \
        f"the record's stage times differ from the output's: {record.get('timing')} against {timing}"
    assert record.get("lock") == result.get("lock"), "the record's lock part differs from the output's"
    assert record.get("slow_after_s") == 600 and record.get("slow") is False, \
        "the record does not hold the threshold and whether the rebuild was slow"
    assert not support.LONG_HEX.search(text), \
        f"the record holds an uncut run of 13 or more hex digits: {support.LONG_HEX.search(text).group(0)}"


def test_a_stage_that_did_not_run_still_has_its_time(box, lock, env):
    """With ``--no-embeddings`` the semantic stage does not run, and the code index has no tool here: both keep their
    time (0 for a stage that did not run) and their store entry says why, as today."""
    project = support.make_project(box, "project", lock)

    run = support.rebuild(project, env, "--no-embeddings")

    assert run.returncode == 0, run.describe()
    timing = run.result.get("timing") or {}
    stores = run.result.get("stores") or {}
    assert timing.get("semantic_s") == 0, f"the semantic stage did not run; its time must be 0: {timing}"
    assert (stores.get("semantic") or {}).get("status") == "not_recreated" and stores["semantic"].get("reason"), \
        f"the semantic store entry no longer says why it was not recreated: {stores}"
    assert _number(timing.get("codeintel_s")), f"the code index's time is missing: {timing}"
    assert (stores.get("codeintel") or {}).get("reason"), f"the code index's entry no longer says why: {stores}"


def test_lock_part_of_a_rebuild_on_a_free_lock(box, lock, env):
    """The result and the record carry ``lock`` apart from ``timing``; on a free lock the wait is 0.0 and the lock is
    free again once the rebuild has ended."""
    project = support.make_project(box, "project", lock)

    run = support.rebuild(project, env, "--no-embeddings")

    assert run.returncode == 0, run.describe()
    part = run.result.get("lock")
    assert isinstance(part, dict), f"the result has no lock part\n{run.describe()}"
    assert [key for key in support.LOCK_KEYS if key not in part] == [], f"the lock part lacks keys: {part}"
    assert part["path"] == str(lock), f"the lock part does not name the configured lock: {part}"
    assert part["wait_s"] == 0.0 and part["held_by_caller"] is False, f"a free lock: no wait, not the caller's: {part}"
    for key in ("taken_at", "released_at"):
        assert isinstance(part[key], str) and support.ISO_UTC_MICRO.match(part[key]), \
            f"{key} is not UTC ISO 8601 with microseconds: {part[key]!r}"
    assert support.iso(part["taken_at"]) <= support.iso(part["released_at"])
    assert abs((support.iso(part["released_at"]) - support.iso(part["taken_at"])) - run.result["timing"]["total_s"]) \
        <= 2.0, f"total_s is not the time from the lock taken to the end: {part} {run.result['timing']}"
    assert lock.exists() and support.lock_is_free(lock), "the lock is still held after the rebuild ended"
