"""Tests for spend.py (DAEO-sdxk, 2026-11-10; DEC-1091): one unit, old lines readable, the brake record-only.

    python3 -m pytest -q -p no:cacheprovider .gov-runtime/scratch/orchestrator/tools/test_spend.py

ORCH and SPEND point at tmp folders: the live log, brake folder and inbox are never written.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

TOOL = Path(__file__).resolve().parent / "spend.py"
LIVE = Path("/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/spend.jsonl")
spec = importlib.util.spec_from_file_location("spend_under_test", TOOL)
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def run(tmp_path, *args):
    env = dict(os.environ, ORCH=str(tmp_path / "orch"), SPEND=str(tmp_path / "orch/log/spend.jsonl"))
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env, timeout=60)


def test_old_shapes_get_the_one_schema_and_no_mixed_sum():
    big = S.normal({"at": "2026-11-09 19:45", "what": "W2-149 independent test designer", "kind": "worker",
                    "tokens": 17057921, "cost": "10.10 USD (session total_cost_usd)", "note": "80 cases"})
    assert tuple(big) == S.KEYS and big["cost_usd"] == 10.10 and big["orig_tokens"] == 17057921
    assert big["output_tokens"] is None and big["cache_read_tokens"] is None  # the source does not say which kind
    split = S.normal({"at": "a", "what": "w", "kind": "worker", "tokens": {"input": 74, "cache_creation": 156367,
                      "cache_read": 4390118, "output": 41334}, "cost_usd": 2.96, "cost_source": "the session"})
    assert (split["input_tokens"], split["output_tokens"], split["cache_read_tokens"],
            split["cache_creation_tokens"], split["cost_usd"]) == (74, 41334, 4390118, 156367, 2.96)
    agent = S.normal({"at": "a", "what": "w", "kind": "agent", "tokens": 136162, "tool_uses": 44, "duration_s": 197,
                      "cost": "not measured (subscription; no per-run price)"})
    assert agent["cost_usd"] is None and agent["orig_cost"].startswith("not measured")
    assert agent["extra"] == {"tool_uses": 44, "duration_s": 197}
    e2 = S.normal({"at": "a", "what": "E2", "kind": "experiment", "experiment": "E2", "cost_usd": 21.95,
                   "projection_usd": 25, "brake_usd": 50, "stopped": None, "projected_138_usd": "25 to 31"})
    assert e2["projection_usd"] == 25 and e2["extra"] == {"experiment": "E2", "brake_usd": 50, "stopped": None,
                                                         "projected_138_usd": "25 to 31"}
    for line in (big, split, agent, e2):
        assert S.normal(json.loads(json.dumps(line))) == line  # idempotent


def test_the_real_log_normalises_on_a_copy_with_every_line_kept(tmp_path):
    (tmp_path / "orch/log").mkdir(parents=True)
    copy = tmp_path / "orch/log/spend.jsonl"
    shutil.copy(LIVE, copy)
    before = copy.read_bytes()
    raw = [json.loads(x) for x in before.decode().splitlines() if x.strip()]
    r = run(tmp_path, "normalise")
    assert r.returncode == 0, r.stderr
    assert copy.read_bytes() == before  # without --swap nothing is replaced
    norm = [json.loads(x) for x in (tmp_path / "orch/log/spend.jsonl.norm").read_text().splitlines()]
    assert len(norm) == len(raw) and all(tuple(n) == S.KEYS for n in norm)
    for o, n in zip(raw, norm):
        assert n["at"] == o.get("at") and n["what"] == o.get("what")  # each line's own text is kept
        if "tokens" in o:
            assert n["orig_tokens"] == o["tokens"]
        if "cost" in o:
            assert n["orig_cost"] == o["cost"]
    r = run(tmp_path, "normalise", "--swap")
    assert r.returncode == 0, r.stderr
    [orig] = (tmp_path / "orch/log").glob("spend.jsonl.orig-*")
    assert orig.read_bytes() == before and len(copy.read_text().splitlines()) == len(raw)
    assert run(tmp_path, "normalise", "--swap").returncode != 0  # a second swap the same day keeps the first orig


def test_record_and_brake_by_hand_and_no_projection_never_brakes(tmp_path):
    assert run(tmp_path, "record", "--what", "W2-1 helper", "--kind", "agent", "--wbs", "W2-1", "--cost-usd",
               "50").returncode == 0
    assert "no ticket past" in run(tmp_path, "check").stdout  # no projection: never braked
    run(tmp_path, "record", "--what", "W2-2 a", "--kind", "launched", "--wbs", "W2-2", "--cost-usd", "3",
        "--projection-usd", "2", "--output-tokens", "10", "--cache-read-tokens", "99")
    assert "no ticket past" in run(tmp_path, "check").stdout
    run(tmp_path, "record", "--what", "W2-2 b", "--kind", "launched", "--wbs", "W2-2", "--cost-usd", "1.5")
    out = run(tmp_path, "check").stdout
    assert out.startswith("BRAKE W2-2: W2-2 has spent 4.50 USD") and "brake at 4.00" in out
    [item] = (tmp_path / "orch/dispatch/inbox").glob("*-spend-brake.txt")
    assert "W2: W2-2\n" in item.read_text() and "never an alarm to the owner" in item.read_text()
    assert "BRAKED" in run(tmp_path, "sum").stdout
    assert run(tmp_path, "clear", "W2-2", "--projection-usd", "3").returncode == 0
    assert "W2-2: 0.00 USD" in run(tmp_path, "sum").stdout and "projection 5.00" in run(tmp_path, "sum").stdout
    lines = [json.loads(x) for x in (tmp_path / "orch/log/spend.jsonl").read_text().splitlines()]
    assert all(tuple(x) == S.KEYS for x in lines) and [x["kind"] for x in lines][-2:] == ["brake", "brake-clear"]


def test_the_brief_budget(tmp_path):
    for text, want in (("---\nbudget_usd: 4\n---\n", "4"), ("projection_usd: 2.5\n", "2.5"),
                       ("Your budget is about 6 USD.\n", "6"), ("The projection: $12.5 USD\n", "12.5"),
                       ("---\nbudget_usd: 0\n---\n", ""), ("no money words\n", "")):
        b = tmp_path / "b.md"
        b.write_text(text)
        assert run(tmp_path, "brief-budget", str(b)).stdout.strip() == want, text
