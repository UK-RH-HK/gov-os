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
    assert "W2-2: 0.00 USD" in run(tmp_path, "sum").stdout and "projection 3.00" in run(tmp_path, "sum").stdout  # the clear sets it (review finding 1)
    lines = [json.loads(x) for x in (tmp_path / "orch/log/spend.jsonl").read_text().splitlines()]
    assert all(tuple(x) == S.KEYS for x in lines) and [x["kind"] for x in lines][-2:] == ["brake", "brake-clear"]


def test_the_brief_budget(tmp_path):
    for text, want in (("---\nbudget_usd: 4\n---\n", "4"), ("projection_usd: 2.5\n", "2.5"),
                       ("Your budget is about 6 USD.\n", "6"), ("The projection: $12.5 USD\n", "12.5"),
                       ("---\nbudget_usd: 0\n---\n", ""), ("no money words\n", "")):
        b = tmp_path / "b.md"
        b.write_text(text)
        assert run(tmp_path, "brief-budget", str(b)).stdout.strip() == want, text


def test_r1_relaunching_a_budgeted_brief_does_not_raise_the_brake(tmp_path):
    """Review finding 1: the ticket's projection is its latest projection_usd, not a sum over its launches."""
    for i in range(2):
        run(tmp_path, "record", "--what", f"W2-5 launch {i}", "--kind", "launched", "--wbs", "W2-5", "--cost-usd",
            "1.9", "--projection-usd", "1")
    out = run(tmp_path, "check").stdout
    assert out.startswith("BRAKE W2-5: W2-5 has spent 3.80 USD") and "brake at 2.00" in out
    run(tmp_path, "clear", "W2-5")
    for i in range(2):
        run(tmp_path, "record", "--what", f"W2-5 relaunch {i}", "--kind", "launched", "--wbs", "W2-5",
            "--cost-usd", "1.2", "--projection-usd", "1")
    assert run(tmp_path, "check").stdout.startswith("BRAKE W2-5: W2-5 has spent 2.40 USD")  # after a clear: afresh
    run(tmp_path, "clear", "W2-5", "--projection-usd", "10")
    run(tmp_path, "record", "--what", "W2-5 big", "--kind", "launched", "--wbs", "W2-5", "--cost-usd", "15")
    assert "no ticket past" in run(tmp_path, "check").stdout  # the clear's projection sets it: 15 < 20
    assert "projection 10.00" in run(tmp_path, "sum").stdout


def test_r6_a_number_before_its_label_is_still_a_cost():
    d = S.normal({"at": "a", "what": "w", "kind": "worker", "cost": "total_cost_usd 3.90 as the CLI reports it"})
    assert d["cost_usd"] == 3.90
    already = {k: None for k in S.KEYS}
    already.update(at="a", what="w", kind="worker", orig_cost="total_cost_usd 2.97 as the CLI reports it")
    assert S.normal(already)["cost_usd"] == 2.97  # a normal line with a lost cost is repaired


def test_r8_the_brake_file_is_created_once_even_when_it_appeared_meanwhile(tmp_path):
    run(tmp_path, "record", "--what", "W2-6", "--kind", "launched", "--wbs", "W2-6", "--cost-usd", "5",
        "--projection-usd", "1")
    (tmp_path / "orch/log/brake").mkdir(parents=True)
    (tmp_path / "orch/log/brake/W2-6.json").write_text("{}")  # another check won the race
    assert "no ticket past" in run(tmp_path, "check").stdout
    assert not list((tmp_path / "orch/dispatch/inbox").glob("*")) if (tmp_path / "orch/dispatch/inbox").exists() else True


# RUBRIC-2 (DEC-1120 (3)): model, class, tier and promoted in the one schema; add-helper for in-session helpers

OLD17 = {"at": "2026-11-09 10:00", "what": "old normal line", "kind": "launched", "ticket": "T-o", "wbs": "W2-97",
         "role": "engineer", "cost_usd": 1.0, "cost_source": "x", "input_tokens": None, "output_tokens": 5,
         "cache_read_tokens": None, "cache_creation_tokens": None, "projection_usd": 4.0, "note": None,
         "orig_tokens": None, "orig_cost": None, "extra": {"effort": "high"}}


def last_line(tmp_path):
    return json.loads((tmp_path / "orch/log/spend.jsonl").read_text().splitlines()[-1])


def test_rubric2_the_schema_has_four_new_keys_and_an_old_line_stays_valid():
    assert S.KEYS[-4:] == ("model", "class", "tier", "promoted") and S.KEYS[:17] == S.BASE_KEYS and len(S.KEYS) == 21
    old = S.normal(dict(OLD17))
    assert tuple(old) == S.KEYS and (old["model"], old["class"], old["tier"], old["promoted"]) == (None,) * 4
    assert old["extra"] == {"effort": "high"} and old["orig_tokens"] is None  # nothing moved into extra
    assert {k: old[k] for k in S.BASE_KEYS} == OLD17  # every old field unchanged
    assert S.normal(json.loads(json.dumps(old))) == old  # idempotent
    # a free-form old line and a partial one are as before, with the new keys null
    free = S.normal({"at": "a", "what": "w", "kind": "worker", "tokens": 5, "cost": "2.00 USD (x)"})
    assert tuple(free) == S.KEYS and free["cost_usd"] == 2.0 and free["model"] is None and free["tier"] is None
    # a normal line that names a model without a tier gets the tier derived
    d = dict(old, model="claude-haiku-5")
    assert S.normal(d)["tier"] == "haiku"


def test_rubric2_tier_of_the_model_name():
    for model, tier in (("claude-opus-5-5", "opus"), ("claude-sonnet-5-5", "sonnet"), ("claude-haiku-5", "haiku"),
                        ("Sonnet", "sonnet"), ("some-other-model", "other"), ("", None), (None, None)):
        assert S.tier_of(model) == tier, model


def test_rubric2_record_and_from_log_carry_the_fields(tmp_path):
    log = tmp_path / "r.json"
    log.write_text(json.dumps({"type": "result", "total_cost_usd": 2.5, "session_id": "s",
                               "usage": {"output_tokens": 9}}) + "\n")
    r = run(tmp_path, "from-log", str(log), "--what", "w", "--kind", "launched", "--model", "claude-sonnet-5-5",
            "--class", "C2", "--promoted", "fail-open finding", "--effort", "high", "--role", "engineer")
    assert r.returncode == 0, r.stderr
    d = last_line(tmp_path)
    assert tuple(d) == S.KEYS and (d["model"], d["class"], d["tier"], d["promoted"]) == (
        "claude-sonnet-5-5", "C2", "sonnet", "fail-open finding")
    assert d["cost_usd"] == 2.5 and d["extra"]["effort"] == "high" and d["extra"]["session_id"] == "s"
    # the old call (no model, no class) still works and has the new keys as null
    assert run(tmp_path, "from-log", str(log), "--what", "w2", "--kind", "launched").returncode == 0
    d = last_line(tmp_path)
    assert (d["model"], d["class"], d["tier"], d["promoted"]) == (None,) * 4 and d["cost_usd"] == 2.5
    assert run(tmp_path, "record", "--what", "w3", "--kind", "agent", "--model", "opus", "--class", "C3").returncode == 0
    d = last_line(tmp_path)
    assert (d["model"], d["class"], d["tier"]) == ("opus", "C3", "opus")
    r = run(tmp_path, "record", "--what", "w4", "--kind", "agent", "--class", "C9")
    assert r.returncode != 0 and "invalid choice" in r.stderr  # a class outside C0..C3 is refused


def test_rubric2_add_helper_logs_an_in_session_helper_in_the_same_schema(tmp_path):
    r = run(tmp_path, "add-helper", "--what", "RUBRIC-2 spend tools", "--role", "product-spec", "--model",
            "claude-sonnet-5-5", "--effort", "high", "--class", "C1", "--ticket", "W2-1", "--wbs", "W2-1",
            "--cost-usd", "1.25", "--output-tokens", "100", "--cache-read-tokens", "5000",
            "--cache-creation-tokens", "300", "--input-tokens", "12", "--promoted", "two failed reviews")
    assert r.returncode == 0, r.stderr
    d = last_line(tmp_path)
    assert tuple(d) == S.KEYS and d == json.loads(r.stdout)
    assert (d["kind"], d["what"], d["role"], d["ticket"], d["wbs"]) == ("agent", "RUBRIC-2 spend tools",
                                                                        "product-spec", "W2-1", "W2-1")
    assert (d["model"], d["class"], d["tier"], d["promoted"]) == ("claude-sonnet-5-5", "C1", "sonnet",
                                                                   "two failed reviews")
    assert (d["cost_usd"], d["cost_source"], d["output_tokens"], d["cache_read_tokens"], d["cache_creation_tokens"],
            d["input_tokens"]) == (1.25, "given", 100, 5000, 300, 12)
    assert d["extra"] == {"effort": "high"}
    # no cost known: null, never a made-up number; not promoted: null
    assert run(tmp_path, "add-helper", "--what", "w", "--role", "research", "--model", "claude-haiku-5", "--effort",
               "low", "--class", "C0").returncode == 0
    d = last_line(tmp_path)
    assert (d["cost_usd"], d["promoted"], d["tier"], d["wbs"]) == (None, None, "haiku", None)
    # the cost counts for the ticket (the brake) like any other line's
    assert "W2-1: 1.25 USD" in run(tmp_path, "sum").stdout


def test_rubric2_add_helper_refuses_what_every_spawn_must_name(tmp_path):
    full = ["--what", "w", "--role", "research", "--model", "claude-sonnet-5-5", "--effort", "high", "--class", "C1"]
    assert run(tmp_path, "add-helper", *full).returncode == 0
    for drop in ("--model", "--effort", "--class", "--role", "--what"):
        args = list(full)
        i = args.index(drop)
        del args[i:i + 2]
        r = run(tmp_path, "add-helper", *args)
        assert r.returncode != 0 and "required" in r.stderr, drop
    r = run(tmp_path, "add-helper", *full[:-1], "C4")
    assert r.returncode != 0 and "invalid choice" in r.stderr
    r = run(tmp_path, "add-helper", *full, "--promoted", " ")
    assert r.returncode != 0 and "--promoted is empty" in r.stderr
    assert len((tmp_path / "orch/log/spend.jsonl").read_text().splitlines()) == 1  # only the good one was written


def test_rubric2_a_log_of_old_and_new_lines_is_read_summed_and_normalised(tmp_path):
    (tmp_path / "orch/log").mkdir(parents=True)
    path = tmp_path / "orch/log/spend.jsonl"
    path.write_text(json.dumps(OLD17) + "\n" + json.dumps({"at": "a", "what": "free", "kind": "agent",
                                                           "tokens": 5, "cost": "2.00 USD (x)", "wbs": "W2-97"}) + "\n")
    assert run(tmp_path, "add-helper", "--what", "h", "--role", "research", "--model", "claude-sonnet-5-5",
               "--effort", "high", "--class", "C1", "--wbs", "W2-97", "--cost-usd", "0.5").returncode == 0
    assert "W2-97: 3.50 USD" in run(tmp_path, "sum").stdout  # 1.00 + 2.00 + 0.50, old and new counted alike
    assert [ln["what"] for ln in S.load(path)] == ["old normal line", "free", "h"]
    raw = [json.loads(x) for x in path.read_text().splitlines()]
    assert len(raw[0]) == 17 and len(raw[2]) == 21  # old lines are never rewritten by an append
    # a reader that ignores the new keys still sees the old fields of every line
    for line in raw:
        assert {"at", "what", "kind", "cost_usd"} <= set(S.normal(line)) and "tokens" not in S.normal(line)
    r = run(tmp_path, "normalise")
    assert r.returncode == 0, r.stderr
    norm = [json.loads(x) for x in (tmp_path / "orch/log/spend.jsonl.norm").read_text().splitlines()]
    assert len(norm) == 3 and all(tuple(n) == S.KEYS for n in norm)
    assert norm[2]["model"] == "claude-sonnet-5-5" and norm[0]["model"] is None


def test_row159_separate_briefs_each_bring_their_projection(tmp_path):
    """Row 159 (DEC-1140 (2)): three runs of one W2, each within its own projection, do not trip the brake."""
    for name in ("merge", "restore", "designer"):
        run(tmp_path, "record", "--what", f"W2-6 {name}", "--kind", "launched", "--wbs", "W2-6", "--cost-usd", "3",
            "--projection-usd", "2", "--extra", f"log=/x/lead/log/{name}.json")
    assert run(tmp_path, "check").stdout.startswith("spend check: no ticket past twice")


def test_row159_a_relaunched_brief_counts_once(tmp_path):
    """Row 159 keeps review finding 1: the same brief relaunched (launch_worker's -2 suffix) adds no projection."""
    for log in ("eng.json", "eng-2.json", "eng-3.json"):
        run(tmp_path, "record", "--what", "W2-7 eng", "--kind", "launched", "--wbs", "W2-7", "--cost-usd", "1.5",
            "--projection-usd", "1", "--extra", f"log=/x/lead/log/{log}")
    out = run(tmp_path, "check").stdout
    assert out.startswith("BRAKE W2-7: W2-7 has spent 4.50 USD") and "brake at 2.00" in out
