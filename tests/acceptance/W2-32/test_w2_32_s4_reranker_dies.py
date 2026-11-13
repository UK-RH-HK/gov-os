"""S4: a reranker that dies after loading is reported, not raised [W2-M104; DEC-374].

W2-M104's closing condition: "A dead reranker yields the absent path or an envelope error, with a case." The absent
path is DEC-374's: the order given is kept, no candidate carries a score, and the outcome says the rerank was
unavailable and why (``last_outcome()``; ``rerank`` in a bundle; ``reranked`` false in the fusion's answer).

The dying rerankers load and then die at the first score: a real child process that prints its "loaded" line and
exits (a closed pipe, an empty answer), the same failure raised directly in each form a dead process gives, and the
default reranker started from a fake reranker environment in the scratch ``HOME``. No model is loaded.

Rewrite-Reason: DEC-1048 (5) (W2-145, DAEO-2tfd). The default reranker has no private worker any more: a search the
shared service cannot answer stays unranked, named, and never starts ``rerank_worker.py``. So the default reranker
that "dies after loading" is now the shared service that dies after accepting: the fake environment's interpreter,
asked to run ``rerank_service.py``, listens at the socket it is given, accepts the search's connection, reads its
request and dies without an answer. Its interpreter records every program it is asked to run: the cases also hold
that ``rerank_worker.py`` (the old dying worker, still planted) is never started. The scratch ``HOME`` of these cases
is a short folder of its own, as a Unix socket's path is at most 108 bytes; they need Unix sockets (outside the
launch sandbox).
"""

from __future__ import annotations

import json
import os
import shutil
import socket
import sys
import tempfile
from pathlib import Path

import pytest

import w2_32_support as s

DYING = ["dies-process", "dies:BrokenPipeError", "dies:ConnectionResetError", "dies:EOFError",
         "dies:JSONDecodeError", "dies:RuntimeError"]
CANDIDATES = [{"chunk_id": f"c{i}", "path": f"docs/{name}.md", "text": f"[path: docs/{name}.md]\n{name} note"}
              for i, name in enumerate(("harbour", "bakery", "orchard"))]
NOT_A_REASON = {None, "", "no rerank was asked", "nothing to rerank"}

# The fake reranker environment (DEC-397's path under HOME). Asked to run the shared service, it listens at the
# socket it is given (the third argument after the script), accepts one connection, reads the request and dies
# without answering. Asked to run the old private worker, it prints its "loaded" line and exits (a reranker dead
# after loading), which no search may start any more. Every program it is asked to run is one line of RECORD.
FAKE_PYTHON = """#!{python} -I
import json, os, socket, sys
args = sys.argv[1:]
with open({record}, "a", encoding="utf-8") as out:
    out.write(json.dumps(args) + "\\n")
script = next((arg for arg in args if arg.endswith(".py")), "")
if script.endswith("rerank_worker.py"):
    print('{{"device": "cpu"}}', flush=True)
    sys.exit(0)
if script.endswith("rerank_service.py"):
    path = args[args.index(script) + 3]
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(path)
    server.listen(8)
    server.settimeout(20)
    connection, _ = server.accept()
    connection.makefile("rb").readline()
    with open({record}, "a", encoding="utf-8") as out:
        out.write(json.dumps(["accepted and died"]) + "\\n")
    os._exit(1)
sys.exit(1)
"""


def _reported(outcome):
    assert outcome["by"] == "unavailable", f"a dead reranker is reported as unavailable: {outcome}"
    assert outcome.get("reason") not in NOT_A_REASON, f"the outcome says why the rerank was unavailable: {outcome}"


def _short_home(box):
    """A scratch ``HOME`` short enough for the service's socket path under it (108 bytes), for this case alone.

    With ``TMPDIR`` unset no folder qualifies (the temporary folder is ``/tmp`` itself, which takes no loose
    entries): the home is then made in a fresh private folder (mode 0700) directly under ``/tmp``, which
    ``_drop_home`` removes with it (D-10 run 1: the socket base refused ``/tmp`` itself)."""
    try:
        system_temp = tempfile.gettempdir()
    except OSError:  # no writable temporary folder at all: only the private folder is left to try
        system_temp = None
    starts = [Path(start) for start in (os.environ.get("TMPDIR"), system_temp) if start]
    for start in [folder for path in starts for folder in (path, *path.parents) if len(folder.parts) >= 3]:
        if len(str(start)) + 60 > 104 or start == s.ROOT or s.ROOT in start.parents:
            continue
        try:
            home = Path(tempfile.mkdtemp(prefix="w32h-", dir=start))
        except OSError:
            continue
        box.home = home
        return home
    try:  # no folder qualifies: a private one of our own, directly under /tmp
        private = Path(tempfile.mkdtemp(prefix="w32p-", dir="/tmp")).resolve()
        box.private_base = private
        box.home = Path(tempfile.mkdtemp(prefix="w32h-", dir=private))
    except OSError:
        pytest.fail("no temporary folder is short enough for a Unix socket's path under it, and no private folder "
                    "can be made under /tmp: set TMPDIR to a writable, shorter folder", pytrace=False)
    return box.home


def _drop_home(box):
    """Remove the scratch ``HOME`` and, when it had to be made in a private folder under ``/tmp``, that folder."""
    shutil.rmtree(box.home, ignore_errors=True)
    shutil.rmtree(getattr(box, "private_base", box.home), ignore_errors=True)


def _fake_reranker_environment(box):
    """The fake environment in a short scratch ``HOME``; the file that records the programs it is asked to run."""
    home = _short_home(box)
    record = box.workdir / "reranker-programs.jsonl"
    python = home / ".local/share/gov-os/reranker-venv/bin/python"
    python.parent.mkdir(parents=True, exist_ok=True)
    python.write_text(FAKE_PYTHON.format(python=sys.executable, record=json.dumps(str(record))), encoding="utf-8")
    python.chmod(0o755)
    return record


def _programs(record):
    try:
        return [json.loads(line) for line in record.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def _no_private_and_the_service_died_after_accepting(record):
    programs = _programs(record)
    workers = [args for args in programs if any(str(arg).endswith("rerank_worker.py") for arg in args)]
    assert workers == [], f"a private reranker (rerank_worker.py) was started: {workers} (DEC-1048 (5), W2-145)"
    try:
        socket.socket(socket.AF_UNIX, socket.SOCK_STREAM).close()
        refused = None
    except OSError as error:
        refused = f"this sandbox refuses Unix sockets ({error}): run these cases where they are allowed"
    assert ["accepted and died"] in programs, \
        (f"premise: the planted shared service never accepted the search's connection (programs: {programs})"
         + (f" [NOTE: {refused}]" if refused else ""))


@pytest.mark.parametrize("dying", DYING)
def test_rerank_with_a_reranker_that_dies_after_loading_keeps_the_order_and_reports_it(box, dying):
    data = box.call("rerank", query="tide tables", candidates=CANDIDATES, reranker=dying, times=2)
    answers = s.result(data)
    for answer in answers:  # the second search meets the same dead reranker
        assert [c["chunk_id"] for c in answer["ranked"]] == [c["chunk_id"] for c in CANDIDATES], \
            "the order given is kept"
        assert not any("rerank_score" in c for c in answer["ranked"]), "no candidate carries a score"
        _reported(answer["outcome"])


def test_the_default_reranker_whose_shared_service_dies_after_accepting_is_reported_not_raised(box):
    record = _fake_reranker_environment(box)
    try:
        data = box.call("rerank", query="tide tables", candidates=CANDIDATES, reranker=None, times=2)
        for answer in s.result(data):  # the second search meets a dead service again: it starts one, which dies
            assert [c["chunk_id"] for c in answer["ranked"]] == [c["chunk_id"] for c in CANDIDATES]
            assert not any("rerank_score" in c for c in answer["ranked"])
            _reported(answer["outcome"])
            assert "private" not in str(answer["outcome"].get("by")), answer["outcome"]
        _no_private_and_the_service_died_after_accepting(record)
    finally:
        _drop_home(box)


@pytest.mark.parametrize("dying", ["dies-process", "dies:EOFError"])
def test_the_fusion_with_a_dying_reranker_answers_unreranked_and_reports_it(project, box, standin, dying):
    box.built(project)
    data = box.call("fusion_search", root=str(project), query=s.QUESTIONS[0][0], limit=5, reranker=dying)
    answer = s.result(data)
    assert answer["hits"], "the fused hits are still returned"
    assert answer["reranked"] is False, answer["reranked"]
    _reported(answer["outcome"])
    s.no_traceback(data)


@pytest.mark.parametrize("dying", ["dies-process", "dies:EOFError", None])
def test_retrieve_with_a_dying_reranker_cites_its_evidence_and_reports_the_rerank_unavailable(
        project, box, standin, dying):
    box.built(project)
    record = _fake_reranker_environment(box) if dying is None else None  # the default: a service that dies
    try:
        question, gold = s.QUESTIONS[0]
        data = box.call("retrieve", root=str(project), query=question, reranker=dying)
        bundle = s.result(data)
        assert gold in s.first_paths(bundle["evidence"]), "the evidence is still cited"
        assert bundle["merge"]["reranked"] is False
        _reported(bundle["rerank"])
        s.no_traceback(data)
        if record is not None:
            _no_private_and_the_service_died_after_accepting(record)
    finally:
        if record is not None:
            _drop_home(box)
