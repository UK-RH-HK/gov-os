"""W2-123 run 2 (DEC-1026, DEC-1015 item 4): a rebuild's embedding request that times out is retried, bounded.

The KPI line (the first success line of DAEO-qzrq): "A rebuild's embedding request that times out behind other
clients on the shared server is retried, bounded (at most three tries with a growing wait, each try under the existing
per-request timeout), and the semantic stage still ends not_recreated, named, after the last failed try: never a
partial store reported as built; the tries and waits are stated in the rebuild's result".

The tests use only the lead's interface (README, "Run 2: the retry"), every name in ``gov.retrieval.semantic``:
``TIMEOUT_S``, ``RETRY_WAITS_S``, ``NO_EMBEDDING``, ``refresh(root)`` (its ``retries``), ``search(root, q,
refresh=False)`` and ``gov rebuild --json``'s ``stores.semantic``.

How they run (DEC-732): ``refresh`` and ``search`` are called in the pytest process, on the ``gov`` it imports, with
``TIMEOUT_S`` and ``RETRY_WAITS_S`` lowered by ``monkeypatch``; ``gov rebuild --json`` runs in a child
``sys.executable`` whose ``PYTHONPATH`` is the pytest process's own (``w2_123_support.code_path``), through a launcher
that lowers the same two attributes and then calls ``gov.cli.main.main``. Every test gives ``HOME``, ``OLLAMA_HOST``,
``GOV_QUERY_OLLAMA_HOST`` (free loopback ports it picks) and ``GOV_OLLAMA_BIN`` (a planted executable that starts
nothing). The shared runner is a stand-in on 127.0.0.1 (``Runner``) that answers the model list and ``/api/embed``
and holds back its answer to a chosen batch for its first tries, longer than the lowered timeout. Nothing is sent to
127.0.0.1:11434 or :11435 and the real ``ollama`` is never run.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest
import yaml

import w2_123_support as support

REPO_ROOT = support.REPO_ROOT
PATH_MAP_REL = "governance/project/path-map.yaml"
GITLEAKS_TEMPLATE_REL = "template/.gitleaks.toml"

TIMEOUT_S = 1.0               # the lowered per-request timeout: R3's reason writes it "1 s"
RETRY_WAITS_S = (0.25, 0.75)  # the lowered waits before the 2nd and 3rd try: growing
TRIES = len(RETRY_WAITS_S) + 1
HOLD_S = 10.0                 # how long the stand-in holds back an answer it holds: far longer than TIMEOUT_S
EARLY_S = 0.05                # a gap between two tries may be this much shorter than the timeout and the wait
LATE_S = 1.5                  # ... and this much longer (scheduling); a try that waited HOLD_S is far beyond it
CHILD_TIMEOUT_S = 180.0

FILES = 80                    # chunks (Markdown sections): with BATCH 32, at least three batch requests
SECTIONS = 40                 # sections per file: two files, so the secret filter scans few files
MARKER = "w2123chunk"         # every chunk text holds one ``w2123chunkNNN``; no other text sent holds it
DIMENSIONS = 16
# The digest the stand-in's model list reports. Rewrite-Reason: W2-32's S2 (DEC-1064): a revision that no pin names
# fails closed, so each planted project pins this one in its models.yaml (W2-32's interface); the retry is unchanged.
DIGEST = "4f" + "0123456789abcdef" * 3 + "0123456789ab"
MODELS_REL = "governance/project/models.yaml"


# --------------------------------------------------------------------------
# The stand-in shared runner
# --------------------------------------------------------------------------

class Runner:
    """The shared runner at OLLAMA_HOST: a loopback endpoint on a port the test picked. It answers ``/api/version``,
    ``/api/tags`` (the model with a digest), ``/api/ps`` and ``/api/embed``. A chunk batch is an ``/api/embed``
    request whose texts hold the marker; batches are numbered 0, 1, 2 … in the order their texts are first seen, so
    a try of the same request is the same batch. ``holds[n]``: the first that many tries of batch ``n`` are held back
    (the body is read, then nothing is answered for ``HOLD_S``). ``fail``: every chunk batch fails at once instead,
    as ``http-error``, ``not-json`` or ``no-vector``. Any other embed request is answered at once."""

    def __init__(self, port, holds=None, fail=None):
        self.holds, self.fail = dict(holds or {}), fail
        self.tries = []          # every chunk batch try: {"batch", "try", "at", "outcome"}
        self.batches = []        # each batch's texts, by number
        self.lock, self.release = threading.Lock(), threading.Event()
        runner = self

        class Handler(BaseHTTPRequestHandler):
            def answer(self):
                length = int(self.headers.get("Content-Length") or 0)
                body = self.rfile.read(length) if length else b""
                try:
                    asked = json.loads(body) if body else {}
                except ValueError:
                    asked = {}
                route = self.path.split("?")[0].rstrip("/")
                status, reply = runner.reply(route, asked)
                if reply is None:  # held: no answer at all, until long after the timeout
                    runner.release.wait(HOLD_S)
                    self.close_connection = True
                    return
                payload = reply if isinstance(reply, bytes) else json.dumps(reply).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            do_GET = do_POST = do_HEAD = answer

            def log_message(self, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.server.daemon_threads = True
        self.server.block_on_close = False
        self.host = f"127.0.0.1:{port}"
        threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True).start()

    def reply(self, route, asked):
        model = {"name": semantic_module().MODEL, "model": semantic_module().MODEL,
                 "digest": DIGEST, "size": 639150000}
        if route == "/api/version":
            return 200, {"version": "0.35.0"}
        if route == "/api/tags":
            return 200, {"models": [model]}
        if route == "/api/ps":
            return 200, {"models": [{**model, "size_vram": 0}]}
        if route != "/api/embed":
            return 404, {"error": "not found"}
        given = asked.get("input", "")
        texts = [given] if isinstance(given, str) else [str(text) for text in given]
        if not any(MARKER in text for text in texts):
            return 200, {"embeddings": [vector(text) for text in texts]}
        with self.lock:
            key = tuple(texts)
            if key not in self.batches:
                self.batches.append(key)
            batch = self.batches.index(key)
            number = 1 + sum(1 for entry in self.tries if entry["batch"] == batch)
            held = number <= self.holds.get(batch, 0)
            outcome = "held" if held else self.fail or "answered"
            self.tries.append({"batch": batch, "try": number, "at": time.monotonic(), "outcome": outcome})
        if held:
            return 200, None
        if self.fail == "http-error":
            return 500, {"error": "the runner failed"}
        if self.fail == "not-json":
            return 200, b"this is not JSON"
        if self.fail == "no-vector":
            return 200, {"embeddings": []}
        return 200, {"embeddings": [vector(text) for text in texts]}

    def tries_of(self, batch):
        return [entry for entry in self.tries if entry["batch"] == batch]

    def answered_markers(self):
        """The chunks whose vectors the runner returned."""
        found = set()
        for entry in self.tries:
            if entry["outcome"] == "answered":
                found.update(re.findall(MARKER + r"\d{3}", " ".join(self.batches[entry["batch"]])))
        return found

    def sent_markers(self):
        return set(re.findall(MARKER + r"\d{3}", " ".join(" ".join(texts) for texts in self.batches)))

    def close(self):
        self.release.set()
        self.server.shutdown()
        self.server.server_close()


def vector(text):
    digest = hashlib.sha256(str(text).encode()).digest()
    raw = [(byte - 127.5) / 127.5 for byte in digest[:DIMENSIONS]]
    norm = sum(value * value for value in raw) ** 0.5 or 1.0
    return [value / norm for value in raw]


def semantic_module():
    """The module under test, as the pytest process imports it (DEC-732)."""
    from gov.retrieval import semantic
    return semantic


# --------------------------------------------------------------------------
# The project and the environment
# --------------------------------------------------------------------------

_NAMESPACE_FIELDS = {
    "sensitivity": "internal",
    "permitted_roles": ["orchestrator", "product-spec", "independent-test-designer", "engineer",
                        "independent-auditor", "research"],
    "retention": "kept in git history", "export_policy": "allowed",
    "provenance": "written by the W2-123 tests", "deletion_rebuild": "authoritative; restored from git only",
}
ALL_MARKERS = {f"{MARKER}{index:03d}" for index in range(FILES)}


def git(project, *args):
    env = {"PATH": "/usr/bin:/bin", "HOME": str(project), "LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1",
           "GIT_AUTHOR_NAME": "W2-123 tests", "GIT_AUTHOR_EMAIL": "w2-123@example.invalid",
           "GIT_COMMITTER_NAME": "W2-123 tests", "GIT_COMMITTER_EMAIL": "w2-123@example.invalid",
           "GIT_AUTHOR_DATE": "2026-11-02T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-11-02T12:00:00+00:00"}
    done = subprocess.run(["git", "-C", str(project), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {' '.join(args)} failed in {project}:\n{done.stderr}"


def make_project(project):
    """A temporary git repository: a path map with ``notes/**`` embedded and nothing else, the kernel's gitleaks
    rules, and two notes of ``SECTIONS`` short Markdown sections each, every section one chunk holding its own
    marker."""
    project = Path(project)
    (project / "notes").mkdir(parents=True)
    git(project, "init", "-q", "-b", "main")
    document = yaml.safe_load((REPO_ROOT / PATH_MAP_REL).read_text(encoding="utf-8"))
    keep = {key: document[key] for key in ("state_class", "capabilities", "policies", "systems") if key in document}
    spaces = {"top": (["*"], "not embedded"), "notes": (["notes/**"], "embedded")}
    keep["namespaces"] = {name: {"paths": patterns, "memory_class": "governance", **_NAMESPACE_FIELDS,
                                 "embedding_policy": policy} for name, (patterns, policy) in spaces.items()}
    (project / PATH_MAP_REL).parent.mkdir(parents=True)
    (project / PATH_MAP_REL).write_text(yaml.safe_dump(keep, sort_keys=False), encoding="utf-8")
    (project / MODELS_REL).write_text(yaml.safe_dump(  # the stand-in's revision, pinned (W2-32's S2)
        {"embedder": {"model": semantic_module().MODEL, "revision": DIGEST}}, sort_keys=False), encoding="utf-8")
    shutil.copy2(REPO_ROOT / GITLEAKS_TEMPLATE_REL, project / ".gitleaks.toml")
    (project / ".gitignore").write_text(".gov-runtime/\n", encoding="utf-8")
    for part in range(FILES // SECTIONS):
        (project / "notes" / f"part-{part}.md").write_text("".join(
            f"## Section {MARKER}{index:03d}\n\nThe {MARKER}{index:03d} section keeps one line of its own.\n\n"
            for index in range(part * SECTIONS, (part + 1) * SECTIONS)), encoding="utf-8")
    git(project, "add", "-A")
    git(project, "commit", "-q", "-m", "the fixture")
    return project


class Place:
    """One test's HOME, ports, planted executable and stand-in runner."""

    def __init__(self, root):
        self.root = Path(root)
        for name in ("home", "tmp", "bin", "elsewhere", "site"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        self.port = support.free_port()
        self.query_port = support.free_port({self.port})
        self.planted = self.root / "planted" / "ollama"
        self.planted.parent.mkdir()
        self.planted.write_text(f"#!/bin/sh\necho \"$@\" >> '{self.root / 'planted-ran'}'\nexit 1\n",
                                encoding="utf-8")
        self.planted.chmod(0o755)
        self.runner = None

    def serve(self, holds=None, fail=None):
        self.runner = Runner(self.port, holds=holds, fail=fail)
        return self.runner

    def settings(self):
        return {"HOME": str(self.root / "home"), "OLLAMA_HOST": f"127.0.0.1:{self.port}",
                "GOV_QUERY_OLLAMA_HOST": f"127.0.0.1:{self.query_port}", "GOV_OLLAMA_BIN": str(self.planted)}

    def child_env(self):
        """The environment of the rebuild's child: built from scratch, with ``sqlite_vec`` linked in (the scratch
        HOME has no user site folder), and a PATH with git and gitleaks and no ``ollama``."""
        paths = [support.code_path()]
        spec = importlib.util.find_spec("sqlite_vec")
        if spec is not None and spec.origin:
            source = Path(spec.origin).parent if spec.submodule_search_locations else Path(spec.origin)
            link = self.root / "site" / source.name
            if not link.is_symlink():
                link.symlink_to(source, target_is_directory=source.is_dir())
            paths.append(str(self.root / "site"))
        for tool in ("git", "gitleaks"):
            found = shutil.which(tool)
            if found:
                wrapper = self.root / "bin" / tool
                wrapper.write_text(f'#!/bin/sh\nexec "{found}" "$@"\n', encoding="utf-8")
                wrapper.chmod(0o755)
        env = {"PATH": f"{self.root / 'bin'}:/usr/bin:/bin", "TMPDIR": str(self.root / "tmp"), "LC_ALL": "C.UTF-8",
               "GIT_CONFIG_NOSYSTEM": "1", "PYTHONPATH": os.pathsep.join(paths), "PYTHONDONTWRITEBYTECODE": "1",
               **{k: v for k, v in os.environ.items() if k == "GOV_REBUILD_LOCK"}, **self.settings()}
        return env

    def close(self):
        if self.runner is not None:
            self.runner.close()


@pytest.fixture()
def place(tmp_path, monkeypatch):
    """This test's place, its settings in the pytest process's environment, ``TIMEOUT_S`` and ``RETRY_WAITS_S``
    lowered in the module under test."""
    place = Place(tmp_path / "place")
    for key, value in place.settings().items():
        monkeypatch.setenv(key, value)
    semantic = semantic_module()
    monkeypatch.setattr(semantic, "TIMEOUT_S", TIMEOUT_S)
    monkeypatch.setattr(semantic, "RETRY_WAITS_S", RETRY_WAITS_S, raising=False)
    try:
        yield place
    finally:
        place.close()


def expected_reason():
    """R3's reason after the last failed try, for the lowered settings."""
    waits = ", ".join(f"{wait:g} s" for wait in RETRY_WAITS_S)
    return (f"{semantic_module().NO_EMBEDDING}: the request timed out at all {TRIES} tries "
            f"(each under {TIMEOUT_S:g} s; waits {waits})")


LAUNCHER = """\
import json, sys
import gov.retrieval.semantic as semantic
semantic.TIMEOUT_S = float(sys.argv[1])
semantic.RETRY_WAITS_S = tuple(json.loads(sys.argv[2]))
import gov.cli.main as entry
sys.argv = ["gov", *sys.argv[3:]]
sys.exit(entry.main(sys.argv[1:]))
"""


def rebuild(place, project):
    """``gov rebuild --json --root <project>`` in a child, with the two attributes lowered; its envelope."""
    launcher = place.root / "launch_rebuild.py"
    launcher.write_text(LAUNCHER, encoding="utf-8")
    argv = [sys.executable, str(launcher), repr(TIMEOUT_S), json.dumps(list(RETRY_WAITS_S)),
            "rebuild", "--json", "--root", str(project)]
    try:
        done = subprocess.run(argv, cwd=str(place.root / "elsewhere"), env=place.child_env(), capture_output=True,
                              text=True, timeout=CHILD_TIMEOUT_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        raise AssertionError(f"gov rebuild did not end within {CHILD_TIMEOUT_S:.0f} s") from None
    described = f"exit code {done.returncode}\nstdout:\n{done.stdout[-4000:]}\nstderr:\n{done.stderr[-4000:]}"
    try:
        envelope = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"gov rebuild --json did not print one JSON envelope\n{described}") from None
    return envelope, described


def gaps(tries):
    return [later["at"] - earlier["at"] for earlier, later in zip(tries, tries[1:])]


# --------------------------------------------------------------------------
# The tests
# --------------------------------------------------------------------------

def test_with_no_request_timed_out_the_stage_is_built_and_retries_is_an_empty_list(place, tmp_path):
    """*Red.* Every batch answers at once: the stage is built, every chunk was embedded, each batch was sent once, and
    ``retries`` is an empty list (R3). The base code reports no ``retries``."""
    project = make_project(tmp_path / "project")
    runner = place.serve()
    report = semantic_module().refresh(project)
    assert report["available"] is True, report
    assert len(runner.batches) >= 3, f"the fixture needs at least three batch requests: {len(runner.batches)}"
    assert runner.answered_markers() == ALL_MARKERS, "not every chunk of the fixture was embedded"
    assert all(entry["try"] == 1 for entry in runner.tries), f"a batch was sent twice: {runner.tries}"
    assert "retries" in report, f"refresh's report has no `retries` (R3): {report}"
    assert report["retries"] == [], report


def test_a_request_that_times_out_once_is_tried_again_after_the_first_wait_and_the_stage_is_built(place, tmp_path):
    """*Red.* The first batch is held back once, past the lowered timeout: it is tried again, answers on its second
    try, and the build goes on to every later batch. ``retries`` names that one request: 2 tries, the first wait,
    embedded. The base code sends the batch once and ends the stage with the bare reason."""
    project = make_project(tmp_path / "project")
    runner = place.serve(holds={0: 1})
    report = semantic_module().refresh(project)
    assert [entry["outcome"] for entry in runner.tries_of(0)] == ["held", "answered"], \
        f"the timed-out batch was not tried again exactly once: {runner.tries_of(0)}; report {report}"
    assert report["available"] is True and report["state"] != "FACET_UNAVAILABLE", report
    assert runner.answered_markers() == ALL_MARKERS, "the build did not go on to every later batch after the retry"
    assert report.get("retries") == [{"tries": 2, "waits_s": [pytest.approx(RETRY_WAITS_S[0], abs=0.1)],
                                      "embedded": True}], report


def test_a_request_that_times_out_twice_is_tried_a_third_time_after_a_longer_wait_and_the_stage_is_built(
        place, tmp_path):
    """*Red.* The first batch is held back twice: three tries, with both waits, the second longer than the first;
    the third answers and the stage is built. The base code sends the batch once."""
    project = make_project(tmp_path / "project")
    runner = place.serve(holds={0: 2})
    report = semantic_module().refresh(project)
    assert [entry["outcome"] for entry in runner.tries_of(0)] == ["held", "held", "answered"], \
        f"the timed-out batch was not tried three times: {runner.tries_of(0)}; report {report}"
    assert report["available"] is True, report
    assert runner.answered_markers() == ALL_MARKERS, "the build did not go on to every later batch after the retry"
    retries = report.get("retries")
    assert retries == [{"tries": 3, "waits_s": [pytest.approx(wait, abs=0.1) for wait in RETRY_WAITS_S],
                        "embedded": True}], report
    assert retries[0]["waits_s"][1] > retries[0]["waits_s"][0], f"the waits do not grow: {retries}"


def test_each_try_waits_no_longer_than_the_timeout_and_the_waits_between_tries_are_taken(place, tmp_path):
    """*Red.* Held back far longer than the lowered timeout (``HOLD_S``), each try is given up after ``TIMEOUT_S``:
    the time between two tries of the request is its timeout and the wait before the next try, and no more than
    ``LATE_S`` beyond, so the run's time is bounded by the tries and the waits. The base code never sends a second
    try."""
    project = make_project(tmp_path / "project")
    runner = place.serve(holds={0: 2})
    started = time.monotonic()
    semantic_module().refresh(project)
    ended = time.monotonic()
    tries = runner.tries_of(0)
    assert len(tries) == TRIES, f"the batch was not tried {TRIES} times: {tries}"
    for index, (gap, wait) in enumerate(zip(gaps(tries), RETRY_WAITS_S), start=1):
        assert gap >= TIMEOUT_S + wait - EARLY_S, \
            f"try {index + 1} came {gap:.2f} s after try {index}: before its timeout ({TIMEOUT_S} s) and wait ({wait} s)"
        assert gap <= TIMEOUT_S + wait + LATE_S, \
            f"try {index + 1} came {gap:.2f} s after try {index}: try {index} waited longer than {TIMEOUT_S} s"
    bound = (TRIES - 1) * TIMEOUT_S + sum(RETRY_WAITS_S) + 2 * LATE_S
    assert ended - tries[0]["at"] <= bound, \
        f"from the first try to the end of the refresh took {ended - tries[0]['at']:.2f} s (bound {bound:.2f} s; " \
        f"the refresh began {tries[0]['at'] - started:.2f} s before the first try)"


def test_after_the_last_failed_try_refresh_reports_the_tries_and_the_waits_and_sends_no_later_batch(place, tmp_path):
    """*Red.* The second batch is held back at every try (the first answers): three tries, then the stage stops.
    ``refresh`` reports ``FACET_UNAVAILABLE`` with R3's reason, naming the tries, the timeout and the waits, and
    ``retries`` names the request, not embedded. No later batch is sent. The base code sends the batch once and
    gives the bare ``NO_EMBEDDING``."""
    project = make_project(tmp_path / "project")
    runner = place.serve(holds={1: 3})
    report = semantic_module().refresh(project)
    assert [entry["outcome"] for entry in runner.tries_of(1)] == ["held"] * TRIES, \
        f"the batch that kept timing out was not tried {TRIES} times: {runner.tries_of(1)}; report {report}"
    assert len(runner.batches) == 2, f"a later batch was sent after the last failed try: {len(runner.batches)} batches"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert report["reason"] == expected_reason(), report
    assert report.get("retries") == [{"tries": TRIES, "waits_s": [pytest.approx(wait, abs=0.1)
                                                                  for wait in RETRY_WAITS_S], "embedded": False}], \
        report


def test_after_the_last_failed_try_the_rebuild_states_the_tries_and_waits_and_no_partial_store_is_reported_built(
        place, tmp_path):
    """*Red.* Through ``gov rebuild --json`` (a child, the two attributes lowered): the first batch answers, the
    second times out at all three tries, no later batch is sent; the semantic stage is ``not_recreated`` with R3's
    reason, so the tries and waits are stated in the rebuild's result. The vectors of the first batch may stay, but
    the store is not reported as built: a search without refresh reports ``FACET_UNAVAILABLE``, ``stale``, no hit.
    The base code tries once and states the bare ``NO_EMBEDDING``."""
    project = make_project(tmp_path / "project")
    runner = place.serve(holds={1: 3})
    envelope, described = rebuild(place, project)
    assert envelope.get("ok") is True, described
    semantic_stage = envelope["result"]["stores"]["semantic"]
    assert [entry["outcome"] for entry in runner.tries_of(1)] == ["held"] * TRIES, \
        f"the batch that kept timing out was not tried {TRIES} times: {runner.tries_of(1)}; {semantic_stage}"
    assert len(runner.batches) == 2, f"a later batch was sent after the last failed try: {len(runner.batches)} batches"
    assert runner.sent_markers() < ALL_MARKERS
    assert semantic_stage.get("status") == "not_recreated", semantic_stage
    assert semantic_stage.get("reason") == expected_reason(), semantic_stage
    answer = semantic_module().search(project, "which note keeps one line of its own", refresh=False)
    assert answer["available"] is False and answer["state"] == "FACET_UNAVAILABLE", answer
    assert answer["reason"] == "stale" and answer.get("hits") == [], answer


# Rewrite-Reason: P-W2-123-4 (W2-126's KPI 7, DEC-1042 item 4): the bounded retry also covers a transient server
# error (HTTP 5xx). The ``http-error`` case (an HTTP 500 sent once, not retried) left this list and is the case
# below, revised to KPI 7: tried within the same bound, failing closed after its last try.
@pytest.mark.parametrize("failure", ("not-json", "no-vector"))
def test_a_failure_that_is_not_a_time_out_ends_the_stage_at_once_without_a_retry(place, tmp_path, failure):
    """*Red on ``retries`` only.* The first batch fails at once (an answer that is not JSON, an answer without a
    vector for each text): it is sent once, no later batch is sent, the reason is exactly ``NO_EMBEDDING`` as today
    and ``retries`` is an empty list. The base code already sends once with that reason; it reports no
    ``retries``."""
    project = make_project(tmp_path / "project")
    runner = place.serve(fail=failure)
    report = semantic_module().refresh(project)
    assert len(runner.tries) == 1, f"a failure that is not a time-out was tried again: {runner.tries}"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert report["reason"] == semantic_module().NO_EMBEDDING, report
    assert report.get("retries") == [], f"`retries` is not an empty list (R3): {report}"


def test_a_server_error_at_every_try_is_tried_within_the_bound_and_the_stage_ends_unavailable(place, tmp_path):
    """Rewrite-Reason: P-W2-123-4. Was ``test_a_failure_that_is_not_a_time_out_ends_the_stage_at_once_without_a_retry
    [http-error]`` (an HTTP 500 sent once, never retried); W2-126's KPI 7 (DEC-1042 item 4) puts a transient server
    error under the same bounded retry. *Red on ``w2/integrate`` at the merge of W2-123.* Every chunk batch answers HTTP
    500: the first batch is tried exactly ``TRIES`` times, after each wait in turn, then the stage stops (no later
    batch); ``FACET_UNAVAILABLE`` with a reason that begins with ``NO_EMBEDDING`` (KPI 7 does not fix its wording);
    ``retries`` names the request: ``TRIES`` tries, the waits, not embedded."""
    project = make_project(tmp_path / "project")
    runner = place.serve(fail="http-error")
    report = semantic_module().refresh(project)
    tries = runner.tries_of(0)
    assert len(tries) == TRIES, f"the batch that answered HTTP 500 was not tried {TRIES} times: {tries}; {report}"
    for index, (gap, wait) in enumerate(zip(gaps(tries), RETRY_WAITS_S), start=1):
        assert wait - EARLY_S <= gap <= wait + LATE_S, \
            f"try {index + 1} came {gap:.2f} s after try {index}, not after its wait ({wait} s)"
    assert len(runner.batches) == 1, f"a later batch was sent after the last failed try: {len(runner.batches)} batches"
    assert report["available"] is False and report["state"] == "FACET_UNAVAILABLE", report
    assert str(report.get("reason") or "").startswith(semantic_module().NO_EMBEDDING), report
    retries = report.get("retries")
    assert isinstance(retries, list) and len(retries) == 1, f"`retries` does not name the request: {report}"
    assert retries[0].get("tries") == TRIES and retries[0].get("embedded") is False \
        and retries[0].get("waits_s") == [pytest.approx(wait, abs=0.1) for wait in RETRY_WAITS_S], report
