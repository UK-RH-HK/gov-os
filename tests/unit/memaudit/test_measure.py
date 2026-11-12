"""S1, S2, S4, F2, F3, F4: ``measure`` end to end on a planted sets root, repository and store, with a fake ``gov`` that
answers ``retrieve`` with planted ranks (never a real search, model or GPU)."""

from __future__ import annotations

import json
import os
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

from gov.memaudit import declare, ledger, measure, scores
from gov.memaudit.common import read_json

from .conftest import AUDIT
from .fakes import measure_args, prepare

PROBE = "what decides a close"


def snapshot(folder: Path) -> dict:
    return {str(p.relative_to(folder)): (p.stat().st_mtime_ns, p.stat().st_size) for p in sorted(folder.rglob("*"))
            if p.is_file()}


def events(plant, name=None) -> list[dict]:
    return [e for e in ledger.read(plant.run_dir) if name is None or e["event"] == name]


def expected_line(attempt: int, ranks: dict) -> str:
    rs = [r for qid, r in ranks.items() if qid != "q40"]  # q40 is the nonexistent-id question, apart
    n = len(rs)
    at = lambda k: sum(1 for r in rs if r is not None and r <= k)  # noqa: E731
    mrr = sum(1 / r for r in rs if r) / n
    got = sum(1 for r in rs if r is not None)
    return (f"RETRIEVAL attempt {attempt}: hit@5 {at(5)} of {n} ({scores.pct(at(5), n)}); hit@10 {at(10)}; "
            f"hit@20 {at(20)}; MRR {mrr:.4f}; in the first bundle {got}; full evidence {got}")


@pytest.mark.parametrize("sub", ["measure", "judge", "classes", "pool", "pool-import"])
def test_each_new_subcommand_prints_its_usage_with_help_and_exits_0(plant, sub):
    done = plant.cli(sub, "--help")
    assert done.returncode == 0 and done.stdout.startswith("usage: ") and "--sets-root" in done.stdout


def test_a_control_at_34_proceeds_and_the_attempt_counts_with_its_retrieval_line(plant):
    fake, ranks = prepare(plant, control_hits=34)
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 0, done.stdout
    out = done.stdout.splitlines()
    assert out[-1] == expected_line(1, ranks)
    assert (plant.run_dir / "COUNTS").read_text() == "attempt-1\n"
    assert (plant.run_dir / "attempt-1/DONE").is_file() and (plant.run_dir / "attempt-1/ENDED").is_file()
    assert not (plant.run_dir / "attempt-1/FAULT").exists() and not (plant.run_dir / "STOPPED").exists()
    assert (plant.run_dir / "control-1/measure.txt").is_file() and not (plant.run_dir / "attempt-2").exists()
    # the kept outputs: one per search, in call order, and the figures re-score from them with --kept
    kept = sorted(p.name for p in (plant.run_dir / "attempt-1/kept").glob("*.json"))
    assert kept == [f"{i:05d}.json" for i in range(1, 41)]
    before = snapshot(plant.run_dir)
    again = plant.cli("measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo",
                      str(plant.repo["path"]), "--kept", "1")
    assert again.returncode == 0 and again.stdout.splitlines() == [expected_line(1, ranks)]
    assert snapshot(plant.run_dir) == before  # writes nothing


def test_the_kept_flag_of_an_attempt_that_does_not_exist_is_ms_kept_exit_1_never_3(plant):
    prepare(plant)
    done = plant.cli("measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
                     "--kept", "1")
    assert done.returncode == 1 and done.stdout == "MS-KEPT\n"


def test_the_kept_flag_of_a_faulted_attempt_is_ms_kept_exit_1_with_no_retrieval_line_and_nothing_written(plant):
    # round 2, F-2 (Interface items 1 and 8): attempt-1 degraded (its kept count whole), attempt-2 counted
    fake, ranks = prepare(plant)
    fake.override(q_text(plant, "q05"), 1, rerank_by="private")
    fake.save()
    assert plant.cli(*measure_args(plant)).returncode == 0
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "degraded\n"
    assert len(list((plant.run_dir / "attempt-1/kept").glob("*.json"))) == 40  # whole by count, so only FAULT refuses it
    before, searched = snapshot(plant.run_dir), len(fake.calls())
    done = plant.cli("measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
                     "--kept", "1")
    assert done.returncode == 1 and done.stdout == "MS-KEPT\n" and "RETRIEVAL" not in done.stdout + done.stderr
    assert snapshot(plant.run_dir) == before and len(fake.calls()) == searched  # nothing written, nothing searched


def test_the_kept_flag_of_a_whole_attempt_still_re_scores_after_a_faulted_one(plant):
    fake, ranks = prepare(plant)
    fake.override(q_text(plant, "q05"), 1, rerank_by="private")
    fake.save()
    assert plant.cli(*measure_args(plant)).returncode == 0
    done = plant.cli("measure", "--sets-root", str(plant.root), "--audit", AUDIT, "--repo", str(plant.repo["path"]),
                     "--kept", "2")
    assert done.returncode == 0 and done.stdout.splitlines() == [expected_line(2, ranks)]


def test_a_control_at_33_proceeds(plant):
    prepare(plant, control_hits=33)
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 0, done.stdout
    ev = events(plant, "control")
    assert [(e["k"], e["hit5"], e["of"], e["last"], e["last_audit"], e["ok"]) for e in ev] == [(1, 33, 40, 34, None, True)]


def test_a_control_at_31_stops_before_the_audit_sets_first_search_and_leaves_used_as_written(plant):
    fake, _ = prepare(plant, control_hits=31)
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2
    out = done.stdout.splitlines()
    assert out[-1] == "STOPPED control" and any("control out of range" in line for line in out)
    assert (plant.run_dir / "STOPPED").read_text() == "control\n"
    assert not (plant.run_dir / "attempt-1").exists() and not (plant.run_dir / "COUNTS").exists()
    used = (plant.run_dir / "USED").read_text().split()
    assert used[1] == AUDIT and used[2] == declare.sha256_file(plant.run_dir / "DECLARATION.json")
    asked = {c["q"] for c in fake.calls()}
    assert not any(q["question"] in asked for q in plant.questions.values())  # the audit's set was never searched
    assert [e["ok"] for e in events(plant, "control")] == [False]
    assert events(plant, "stopped")[0]["cause"] == "control"
    assert plant.cli(*measure_args(plant)).returncode == 3  # used


def test_a_second_measure_is_refused_by_used_and_writes_nothing(plant):
    prepare(plant)
    assert plant.cli(*measure_args(plant)).returncode == 0
    before = snapshot(plant.run_dir)
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 3 and done.stdout == "USED\n"
    assert snapshot(plant.run_dir) == before


def test_the_control_compares_with_the_last_audits_figure(plant):
    runs = plant.root / "runs"
    for name, hit5 in (("memory-audit-20261014", 20), ("memory-audit-20261104", 30), ("memory-audit-20261118", 5)):
        (runs / name).mkdir(parents=True)
        (runs / name / "FIGURES.json").write_text(json.dumps({"control": {"hit5": hit5}}))
    (runs / "memory-audit-20261101").mkdir()  # no FIGURES.json: passed over
    p = {"root": plant.root.resolve(), "run": plant.root.resolve() / "runs" / AUDIT}
    assert measure.last_control(p) == (30, "memory-audit-20261104")  # the latest earlier one that has figures
    assert measure.last_control({**p, "run": p["root"] / "runs" / "memory-audit-20261010"}) == (34, None)


# ---- S4: the fault rule

def attempt_files(plant, n):
    return {p.name for p in (plant.run_dir / f"attempt-{n}").iterdir()}


def q_text(plant, qid):
    return plant.questions[qid]["question"]


def test_a_degraded_search_makes_the_attempt_not_whole_one_restart_then_it_passes(plant):
    fake, ranks = prepare(plant)
    fake.override(q_text(plant, "q05"), 1, rerank_by="private")  # the reranker not the shared service, attempt 1 only
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 0, done.stdout
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "degraded\n"
    assert not (plant.run_dir / "attempt-1/DONE").exists()
    assert (plant.run_dir / "attempt-2/DONE").is_file() and (plant.run_dir / "COUNTS").read_text() == "attempt-2\n"
    assert (plant.run_dir / "control-2/measure.txt").is_file()  # the ready check again before the restart
    assert done.stdout.splitlines()[-1] == expected_line(2, ranks)
    assert not any(line.startswith("RETRIEVAL attempt 1") for line in done.stdout.splitlines())  # a faulted attempt's figures are never printed
    assert [(e["n"], e["state"], e["cause"]) for e in events(plant, "attempt")] == [
        (1, "start", None), (1, "fault", "degraded"), (2, "start", None), (2, "done", None)]
    assert [e["attempt"] for e in events(plant, "counts")] == ["attempt-2"]


def test_two_faults_stop_the_audit_for_the_owner(plant):
    fake, _ = prepare(plant)
    fake.override(q_text(plant, "q05"), 1, rerank_by="private")
    fake.override(q_text(plant, "q07"), 2, lexical=False)  # a route unavailable, attempt 2
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED fault"
    assert (plant.run_dir / "STOPPED").read_text() == "fault\n"
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "degraded\n"
    assert (plant.run_dir / "attempt-2/FAULT").read_text() == "degraded\n"
    assert not (plant.run_dir / "COUNTS").exists() and not (plant.run_dir / "attempt-3").exists()


def test_a_measure_that_exits_non_zero_is_a_fault_of_cause_exit(plant):
    fake, _ = prepare(plant)
    fake.override(q_text(plant, "q03"), 1, exit=1)
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 0
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "exit\n"
    assert (plant.run_dir / "COUNTS").read_text() == "attempt-2\n"


def test_a_pool_fallback_is_degraded_too(plant):
    fake, _ = prepare(plant)
    fake.override(q_text(plant, "q09"), 1, pool_fallback=True)
    fake.save()
    assert plant.cli(*measure_args(plant)).returncode == 0
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "degraded\n"


def test_a_store_that_changed_during_the_attempt_stops_with_no_restart_and_no_rebuild(plant):
    fake, _ = prepare(plant)
    fake.override(q_text(plant, "q02"), 1, mutate_store=str(plant.store))
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED store"
    assert (plant.run_dir / "attempt-1/FAULT").read_text() == "store\n"
    assert (plant.run_dir / "STOPPED").read_text() == "store\n"
    assert not (plant.run_dir / "attempt-2").exists() and not (plant.run_dir / "control-2").exists()
    st = events(plant, "store")
    assert [e["same"] for e in st] == [False] and st[0]["sha256"] != read_json(plant.run_dir / "DECLARATION.json")["store_sha256"]
    # nothing but retrieve and version calls ever reached gov: no rebuild
    assert {tuple(c["argv"][:1]) for c in fake.calls()} == {("retrieve",)}


def test_a_probe_not_answered_as_declared_stops_before_anything_is_spent(plant):
    fake, _ = prepare(plant)
    fake.override(PROBE, 1, rerank_by="unavailable")
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED notready"
    assert [(e["ok"], e["why"]) for e in events(plant, "ready")] == [(False, "reranker")]
    assert not (plant.run_dir / "control-1").exists() and not (plant.run_dir / "attempt-1").exists()
    assert (plant.run_dir / "USED").is_file()


@pytest.mark.parametrize("override,why", [({"exit": 1}, "exit"), ({"lexical": False}, "route"),
                                          ({"pool_fallback": True}, "pool")])
def test_the_probe_names_why_it_was_not_answered_as_declared(plant, override, why):
    fake, _ = prepare(plant)
    fake.override(PROBE, 1, **override)
    fake.save()
    assert plant.cli(*measure_args(plant)).returncode == 2
    assert [e["why"] for e in events(plant, "ready")] == [why]


def test_no_restart_into_the_same_outage(plant):
    fake, _ = prepare(plant)
    fake.override(q_text(plant, "q05"), 1, rerank_by="private")
    fake.override(PROBE, 2, rerank_by="unavailable")  # the second probe: before the restart
    fake.save()
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED notready"
    assert (plant.run_dir / "attempt-1/FAULT").is_file()
    assert not (plant.run_dir / "control-2").exists() and not (plant.run_dir / "attempt-2").exists()


def test_a_missing_control_set_ends_the_ready_check_with_notready(plant):
    plant.cli(*plant.preflight_args())
    plant.notes({})
    assert plant.cli(*plant.void_args()).returncode == 0
    from .fakes import FakeGov, plant_audit
    fake = FakeGov(plant)
    plant_audit(plant, fake)  # memory-retrieval is not declared in the sets root's map
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED notready"


def test_a_control_set_folder_removed_after_its_map_entry_is_notready_not_a_control_figure(plant):
    import shutil
    prepare(plant)
    shutil.rmtree(plant.root / "fixtures/evaluation/memory-retrieval/visible")  # mapped, but its questions are gone
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 2 and done.stdout.splitlines()[-1] == "STOPPED notready"
    assert (plant.run_dir / "STOPPED").read_text() == "notready\n"
    assert not any(e["event"] == "control" for e in events(plant)) and not (plant.run_dir / "attempt-1").exists()


def test_a_set_that_changed_since_the_declaration_is_ms_digest_and_nothing_is_searched(plant, monkeypatch):
    fake, _ = prepare(plant)
    real = declare.declare

    def changed(*a, **k):
        done = real(*a, **k)
        (plant.hidden / "q01.yaml").write_text((plant.hidden / "q01.yaml").read_text() + "# edited\n")
        return done
    monkeypatch.setattr(declare, "declare", changed)
    monkeypatch.setenv("PYTHONPATH", os.environ.get("PYTHONPATH", ""))
    lines = []
    assert measure.run(plant.root, AUDIT, commit=plant.repo["head"], repo=plant.repo["path"], store=plant.store,
                       gov=plant.gov, emit=lines.append) == "refused"
    assert lines[-1] == "MS-DIGEST" and fake.calls() == []


# ---- F3, F4

def test_no_search_precedes_the_declaration_and_used_by_ledger_or_file_time(plant):
    prepare(plant)
    assert plant.cli(*measure_args(plant)).returncode == 0
    ev = events(plant)
    names = [e["event"] for e in ev]
    first_search = names.index("search")
    assert names.index("declaration") < names.index("used") < first_search
    t = lambda e: datetime.fromisoformat(e["at"].replace("Z", "+00:00")).timestamp()  # noqa: E731
    floor = max((plant.run_dir / "DECLARATION.json").stat().st_mtime, (plant.run_dir / "USED").stat().st_mtime)
    assert all(t(e) >= floor for e in ev if e["event"] == "search")
    searches = [e for e in ev if e["event"] == "search"]
    assert [e["phase"] for e in searches[:3]] == ["ready", "control", "control"]
    assert searches[0]["call"] is None and searches[1]["call"] == 1 and searches[-1]["phase"] == "attempt"
    assert searches[-1]["call"] == 40 and searches[-1]["attempt"] == 1 and all(e["ok"] for e in searches)
    assert [e["seq"] for e in ev] == list(range(1, len(ev) + 1))  # one lock: no seq twice, none missing
    # only numbers, ids and codes: no question word in the ledger
    assert "zephyr" not in (plant.run_dir / "ledger.jsonl").read_text() and "part" not in " ".join(
        str(v) for e in ev for v in e.values() if isinstance(v, str) and v.startswith("What"))


def test_the_children_get_the_environment_as_the_fresh_80_ran_it(plant, monkeypatch):
    fake, _ = prepare(plant)
    monkeypatch.setenv("GOV_STORE", "/should/not/reach")
    monkeypatch.setenv("GOV_TICKET", "T-1")
    done = plant.cli(*measure_args(plant))
    assert done.returncode == 0
    calls = fake.calls()
    assert {c["role"] for c in calls} == {"orchestrator"}
    assert {c["cwd"] for c in calls} == {str(plant.repo["path"].resolve())}
    # plant.cli builds its own environment: the unset form is checked by calling the runner's environment directly
    from gov.memaudit import runner
    env = runner.environment(plant.run_dir, "attempt", 1, plant.run_dir / "attempt-1")
    assert "GOV_STORE" not in env and "GOV_TICKET" not in env and env["GOV_ROLE"] == "orchestrator"


class _Stub(BaseHTTPRequestHandler):
    log: list = []

    def do_POST(self):  # noqa: N802
        self.log.append(("POST", self.path))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"{}")

    def do_GET(self):  # noqa: N802
        self.log.append(("GET", self.path))
        self.send_response(200)
        self.end_headers()

    def log_message(self, *a):
        pass


def test_the_shared_servers_are_reached_only_by_the_fake_gov_with_query_calls(plant, monkeypatch):
    """F4: a stub server on a stand-in port, reached only through the variables the real ``gov`` reads; its request log holds
    only query calls, and the runner starts, stops, loads and signals nothing."""
    fake, _ = prepare(plant)
    _Stub.log = []
    try:
        server = HTTPServer(("127.0.0.1", 0), _Stub)
    except OSError:
        pytest.skip("no loopback socket here")
    threading.Thread(target=server.serve_forever, daemon=True).start()
    host = f"http://127.0.0.1:{server.server_port}"
    exe = fake.bin / "gov"
    src = exe.read_text().replace("plan = json.load", "import urllib.request\nplan = json.load", 1).replace(
        "spec = dict(plan", "urllib.request.urlopen(urllib.request.Request(os.environ['OLLAMA_HOST'] + '/api/embed', "
                           "data=b'{}', method='POST')).read()\nspec = dict(plan", 1)
    exe.write_text(src)
    monkeypatch.setenv("OLLAMA_HOST", host)
    monkeypatch.setenv("GOV_QUERY_OLLAMA_HOST", host)
    try:
        # the stub's address passes on unchanged: plant.cli copies os.environ
        done = plant.cli(*measure_args(plant))
    finally:
        server.shutdown()
    assert done.returncode == 0, done.stdout
    assert _Stub.log and set(_Stub.log) == {("POST", "/api/embed")}
    assert len(_Stub.log) == len(fake.calls())  # one query call a search, nothing else


def test_no_module_of_the_measure_names_a_server_address_or_signals_a_process():
    root = Path(measure.__file__).parent
    banned = ("11434", "11435", "rerank.sock", "OLLAMA", "os.kill", "killpg", "signal.", ".terminate(", ".kill(",
              "api/pull", "api/delete", "keep_alive", "systemctl", "pkill", "pgrep")
    for src in sorted(root.glob("*.py")):
        if src.name in ("preflight.py", "declare.py", "drops.py", "layout.py", "common.py", "tables.py", "say.py",
                        "ledger.py", "__init__.py"):
            continue
        text = src.read_text(encoding="utf-8")
        assert not [w for w in banned if w in text], src.name


def test_only_the_matcher_imports_the_measures_private_names():
    import ast
    root = Path(measure.__file__).parent

    def imports_measure(tree) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == "gov.retrieval.measure":
                return True
            if isinstance(node, ast.ImportFrom) and node.module == "gov.retrieval" and any(
                    a.name == "measure" for a in node.names):
                return True
            if isinstance(node, ast.Import) and any(a.name == "gov.retrieval.measure" for a in node.names):
                return True
        return False
    importers = [src.name for src in sorted(root.glob("*.py")) if imports_measure(ast.parse(src.read_text()))]
    assert importers == ["matcher.py"]  # the measure itself runs as a child process, never imported elsewhere
