"""F3 and F4.

F3: a search made before ``DECLARATION.json`` and ``USED`` exist (W2-170); the store rebuilt during an attempt. Verify: the
planted run's call ledger: no ``search`` entry earlier than the file times of ``DECLARATION.json`` and ``USED``; S4's
planted store change stops the attempt with no rebuild call in the ledger (that case is in ``test_w2_171_s4_fault.py``).

F4: the shared Ollama servers or the reranker service touched other than by their ordinary query calls. Verify: a planted
run with stub servers on stand-in ports: their request logs hold only query calls, and no stop, restart, model load or
unload call; no process of either server is signalled. The stubs are processes of their own
(``ollama_rerank_stub.py``: two HTTP servers on free loopback ports, and a unix-socket server for ``rerank.sock``), logging
each request and each signal; the planted ``gov`` reaches them at ``OLLAMA_HOST``, ``GOV_QUERY_OLLAMA_HOST`` and
``$HOME/.cache/gov-os/rerank.sock`` (the runner reads no address and passes the environment on unchanged).
The reranker's socket case is skipped, with the reason named, where the sandbox forbids ``AF_UNIX`` sockets.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import w2_171_pool as P
import w2_171_scenario as S
import w2_171_world as W

STUB = W.HERE / "ollama_rerank_stub.py"


def epoch(text: str) -> float:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc).timestamp()


def test_f3_no_search_is_earlier_than_the_declaration_and_used(make_world):
    world = make_world("judged:five")
    declaration, used = (world.run_dir / "DECLARATION.json").stat().st_mtime, (world.run_dir / "USED").stat().st_mtime
    searches = world.events("search")
    assert len(searches) > 80 and {e["phase"] for e in searches} >= {"ready", "control", "attempt", "later"}
    for event in searches:
        assert epoch(event["at"]) >= max(declaration, used), event
    ledger = world.ledger()
    first_search = min(i for i, e in enumerate(ledger) if e["event"] == "search")
    names = [e["event"] for e in ledger]
    assert names.index("declaration") < names.index("used") < first_search
    assert ledger[first_search]["phase"] == "ready", "the probe is the first search"


def test_f3_the_planted_gov_is_only_ever_asked_to_retrieve(make_world):
    """No rebuild, no store command, no restart: every call of a whole run (measure and judge) is a retrieve (or the
    measure's own version probe)."""
    world = make_world("judged:five")
    assert {c["argv"][0] for c in world.gov_calls()} <= {"retrieve", "--version"}


@pytest.mark.parametrize("name", ["DC-PIN", "DC-STORE", "DC-PREFLIGHT", "DC-DROPS"])
def test_f3_a_refused_declaration_makes_no_search_and_its_code_passes_through_measure(world, name):
    S.SCENARIOS["five"].install(world)
    gov, store = world.gov, world.store
    if name == "DC-PIN":
        gov = world.gov_unpinned
    elif name == "DC-STORE":
        store = world.base / "other-store.db"
        import sqlite3
        conn = sqlite3.connect(store)
        conn.execute("CREATE TABLE fingerprints (head TEXT NOT NULL, code TEXT, records TEXT, kind TEXT NOT NULL)")
        conn.execute("INSERT INTO fingerprints VALUES ('0000000000000000000000000000000000000000', 'c', 'r', 'k')")
        conn.commit()
        conn.close()
    elif name == "DC-PREFLIGHT":
        (world.run_dir / "PREFLIGHT.json").unlink()
    else:
        (world.run_dir / "DROPS.json").unlink()
    run = world.run("measure", *world.measure_flags(gov=gov, store=store))
    assert run.code == 1 and name in run.lines, run
    assert world.gov_calls() == [] and not (world.run_dir / "USED").exists() and not (world.run_dir / "DECLARATION.json").exists()
    assert not world.events("search") and not list(world.run_dir.glob("control-*"))


# -- F4 ---------------------------------------------------------------------------------------------------------------
class Stubs:
    def __init__(self, folder: Path, sock: Path | None = None):
        self.folder = folder
        folder.mkdir(parents=True, exist_ok=True)
        self.process = subprocess.Popen([sys.executable, str(STUB), str(folder), *([str(sock)] if sock else [])],
                                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        deadline = time.monotonic() + 15
        while not (folder / "ports.json").exists():
            assert self.process.poll() is None, self.process.stderr.read().decode()
            assert time.monotonic() < deadline, "the stand-in servers did not start"
            time.sleep(0.05)
        self.ports = json.loads((folder / "ports.json").read_text())

    def log(self, name: str) -> list[dict]:
        path = self.folder / name
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def close(self):
        self.process.kill()
        self.process.wait(timeout=10)


@pytest.fixture
def stubs(tmp_path):
    made = []

    def make(sock=None):
        made.append(Stubs(tmp_path / "stubs", sock))
        return made[-1]
    yield make
    for stub in made:
        stub.close()


def _run_everything(world, stems=None):
    S.SCENARIOS["five"].install(world)
    return world.measure(), world.judge()


def test_f4_the_ollama_stand_ins_get_only_query_calls_and_no_signal(world, stubs):
    stub = stubs()
    env = {"OLLAMA_HOST": f"127.0.0.1:{stub.ports['a']}", "GOV_QUERY_OLLAMA_HOST": f"127.0.0.1:{stub.ports['b']}"}
    S.SCENARIOS["five"].install(world)
    measured, judged = world.measure(env=env), world.judge(env=env)
    assert measured.code == 0 and judged.code == 0, (measured, judged)
    searches = [c for c in world.gov_calls() if c["argv"][0] == "retrieve"]
    assert len(searches) > 80
    for name in ("a", "b"):
        requests = stub.log(f"{name}.log")
        assert requests and all(r["method"] == "POST" and r["path"] == "/api/embed" for r in requests), requests[:3]
        assert not [r for r in requests if "keep_alive" in r["keys"] or "stream" in r["keys"]], "no load or unload"
        assert len(requests) == len(searches), "one ordinary query call for each search, nothing else"
    assert stub.log("signals.log") == [] and stub.process.poll() is None, "no process of either server is signalled"
    assert {c["argv"][0] for c in world.gov_calls()} <= {"retrieve", "--version"}


def test_f4_the_reranker_socket_gets_only_query_calls_and_stays_up(make_world, stubs):
    try:
        socket.socket(socket.AF_UNIX).close()
    except PermissionError:
        pytest.skip("this sandbox forbids AF_UNIX sockets: the reranker stand-in cannot be made here; run outside it")
    home = Path(tempfile.mkdtemp(prefix="w171-")) / "h"          # short: a unix socket path is limited to 107 bytes
    sock = home / ".cache" / "gov-os" / "rerank.sock"
    sock.parent.mkdir(parents=True)
    world = make_world("prepared")
    stub = stubs(sock)
    S.SCENARIOS["five"].install(world)
    measured, judged = world.measure(home=home), world.judge(home=home)
    assert measured.code == 0 and judged.code == 0, (measured, judged)
    requests = stub.log("rerank.log")
    searches = [c for c in world.gov_calls() if c["argv"][0] == "retrieve"]
    assert requests and all(r == {"op": "rerank"} for r in requests) and len(requests) == len(searches)
    assert stub.log("signals.log") == [] and stub.process.poll() is None and sock.exists()
