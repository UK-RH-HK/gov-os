"""fresh80_reader.py on the planted set: resume, the brake, the call run once more, items 17 and 18's counts, the
nonexistent-id question by category, the dry mode, no hidden path printed; and readiness review F6: the prompt, schema,
grader, cap and cut byte-identical to e2_run.py's."""
import hashlib
import json
import math
import sys
from pathlib import Path

import pytest

import f80lib as L
import fresh80_reader as RD
from helpers import FakeClaude, clean, make_attempt, reader, rows, setup

E2_FILE = L.D4B / "e2_run.py"


# ---- F6: byte identity with e2_run.py

def _e2_module():
    """e2_run.py itself, executed without its main() (as e3sa_run.py loads e3_run.py)."""
    src = E2_FILE.read_text().replace("\nmain()\n", "\n")
    mod = type(sys)("e2")
    exec(compile(src, "e2_run.py", "exec"), mod.__dict__)
    return mod


def test_f6_prompt_strings_are_e2s_byte_for_byte():
    e2 = _e2_module()
    assert hashlib.sha256(E2_FILE.read_bytes()).hexdigest() == L.E2_SHA256
    for name in ("READER_SYS", "GRADER_SYS"):
        mine, theirs = getattr(RD, name), getattr(e2, name)
        assert hashlib.sha256(mine.encode()).hexdigest() == hashlib.sha256(theirs.encode()).hexdigest()
    for name in ("READER_SCHEMA", "GRADER_SCHEMA"):
        assert json.dumps(getattr(RD, name), sort_keys=False) == json.dumps(getattr(e2, name), sort_keys=False)
    assert RD.CAP == e2.CAP == 3
    assert "may be incomplete" in RD.READER_SYS
    b = [[("a.md", 1, 2, "t1")], [("b.md", 3, 4, "t2")]]
    assert RD.prompt_of("Q?", b) == e2.prompt_of("Q?", b)
    assert RD.prompt_of.__code__.co_code == e2.prompt_of.__code__.co_code
    assert RD.outcome.__code__.co_code == e2.outcome.__code__.co_code


def test_f6_a_changed_e2_file_is_refused(tmp_path):
    f = tmp_path / "e2_run.py"
    f.write_text(E2_FILE.read_text().replace("may be incomplete", "might be incomplete"))
    with pytest.raises(SystemExit):
        L.e2_parts(f)


def test_f6_attempt_loop_sends_e2s_prompts(planted, monkeypatch):
    """The same question through e2_run.py's own one() and through the reader's: the same prompts, in order, the
    same verdict and answered_at, so the A1/A2/A3 cut reads the same."""
    att = make_attempt(planted)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    qs = {q["id"]: q for q in L.load(planted["root"], planted["clone"])}
    q = qs["v03"]  # a first-call miss: it searches again
    first = L.kept_doc(att / "kept", 3)["result"]
    e2 = _e2_module()
    sent_e2, sent_me = [], []

    def e2_claude(model, system, schema, prompt, budget, cwd):
        sent_e2.append((model, system, prompt))
        out = json.loads(FakeClaude()(["--system-prompt", system, "--model", model], prompt, cwd))["structured_output"]
        return {"wall_s": 0, "cost_usd": 0}, out
    e2.claude = e2_claude
    e2.search = lambda words: e2.items_of(L.search(words, planted["clone"])[0])
    e2.hit = lambda item, q: L.hit(item, q)
    e2.text_of = lambda p, a, b: L.text_of(planted["clone"], p, a, b)
    monkeypatch.setattr(L, "GOV", str(planted["gov"]))
    q2 = dict(q, first=att / "kept/00003.json", kind="spent")
    r_e2 = e2.one(q2, str(planted["base"]), 99)
    fake = FakeClaude()

    def mine(argv, prompt, cwd):
        sent_me.append((argv[argv.index("--model") + 1], argv[argv.index("--system-prompt") + 1], prompt))
        return fake(argv, prompt, cwd)
    monkeypatch.setattr(L, "_run_claude", mine)
    run = planted["base"] / "mine"
    run.mkdir()
    ledger = L.Ledger(run)
    r_me = RD.one(q, first, run, planted["clone"], L.Brake(99, ledger), ledger)
    assert sent_me == sent_e2
    assert (r_me["final_verdict"], r_me["answered_at"]) == (r_e2["final_verdict"], r_e2["answered_at"])
    for cut in (1, 2, 3):
        assert RD.outcome(r_me, cut) == e2.outcome(r_e2, cut)


# ---- the run

def test_full_run_counts_and_nonexistent_id(planted, monkeypatch, capsys):
    make_attempt(planted)
    fake = FakeClaude(cite_outside={"v09"})
    setup(planted, monkeypatch, fake)
    assert reader(planted) == 0
    out = capsys.readouterr().out
    clean(out, planted)
    r = rows(planted)
    assert len(r) == 80
    assert r["v80"]["apart"] and r["v80"]["first_stopping_reason"] == "UNRESOLVED_IDS"
    assert r["v80"]["first_gaps_name_ids"] is True
    assert sum(1 for x in r.values() if x["apart"]) == 1
    assert sum(RD.outcome(x, 1)["right"] for x in r.values() if not x["apart"]) == 69
    assert sum(RD.outcome(x, 2)["right"] for x in r.values() if not x["apart"]) == 79
    s = json.loads((planted["root"] / "runs/fresh-80/reader/summary.json").read_text())
    assert s["citations_outside"] == 1 and s["right_only_by_a_citation_outside"] == 0
    assert s["search_failures"] == 0 and s["searches"] == 10
    plan = json.loads((planted["root"] / "runs/fresh-80/reader/plan.json").read_text())
    assert plan["apart"] == ["v80"] and len(plan["main"]) == 79


def test_search_failures_counted_and_named(planted, monkeypatch, capsys):  # item 17
    make_attempt(planted)
    monkeypatch.setenv("FAKE_SEARCH_FAIL", "v03,v11")
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    out = capsys.readouterr().out
    # each asks twice (attempts 1 and 2 search again; the cap ends it at 3): 4 failures, named by id
    assert "search_failures: 4" in out and "search_failure_ids: ['v03', 'v11']" in out
    r = rows(planted)
    assert r["v03"]["search_failures"] == 2 and r["v03"]["searches"][0]["ok"] is False
    assert r["v03"]["gold_in_bundle"] == [False, False, False]  # a failed search's bundle is empty, as in E2
    assert r["v03"]["final_verdict"] == "not_found"


def test_search_classifies_failures(planted, monkeypatch):
    monkeypatch.setattr(L, "GOV", str(planted["gov"]))
    res, ok, why, by = L.search("again v01", planted["clone"])
    assert ok and res["evidence"] and by == "service"
    monkeypatch.setenv("FAKE_SEARCH_FAIL", "v01")
    res, ok, why, by = L.search("again v01", planted["clone"])
    assert not ok and res == {} and "exit 1" in why
    res, ok, why, by = L.search("where is DEC-99999", planted["clone"])  # a stated gap is no failure
    assert ok and res["stopping_reason"] == "UNRESOLVED_IDS"
    monkeypatch.delenv("FAKE_SEARCH_FAIL")
    monkeypatch.setenv("FAKE_DEGRADE_SEARCH", "v02")  # a route down: a failed search (code review F1)
    res, ok, why, by = L.search("again v02", planted["clone"])
    assert not ok and res == {} and why == "route semantic unavailable"


def test_resume_never_runs_a_question_again(planted, monkeypatch, capsys):  # item 16
    make_attempt(planted)
    fake = FakeClaude(cost=0.05)
    setup(planted, monkeypatch, fake)
    reader(planted, "--projection", "0.1")  # brake 0.2: stops early
    first = rows(planted)
    assert 0 < len(first) < 80
    stamps = {k: (planted["root"] / f"runs/fresh-80/reader/{k}.json").stat().st_mtime_ns for k in first}
    spent1 = L.Ledger(planted["root"] / "runs/fresh-80/reader").total
    fake2 = FakeClaude(cost=0.05)
    setup(planted, monkeypatch, fake2)
    reader(planted, "--projection", "100")
    out = capsys.readouterr().out
    allr = rows(planted)
    assert len(allr) == 80
    for k, t in stamps.items():  # untouched
        assert (planted["root"] / f"runs/fresh-80/reader/{k}.json").stat().st_mtime_ns == t
    seen = {p for _, p in fake2.prompts}
    for k in first:
        assert not any(f"planted question {k} " in p or f"planted question {k}:" in p for p in seen)
    assert L.Ledger(planted["root"] / "runs/fresh-80/reader").total > spent1  # the ledger carries over
    clean(out, planted)


def test_brake_stops_new_questions(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude(cost=1.0))
    rc = reader(planted, "--projection", "2")  # brake 4 USD; each question costs at least 3
    out = capsys.readouterr().out
    assert rc == 1 and "STOPPED: the runaway brake" in out
    s = json.loads((planted["root"] / "runs/fresh-80/reader/summary.json").read_text())
    assert s["rows"] < 80 and s["brake_usd"] == 4 and "brake" in s["stopped"]
    # no question started after the spend passed the brake: at most the 4 workers' questions in flight overshoot
    assert s["rows"] <= 2 + RD.WORKERS


def test_call_run_once_more(planted, monkeypatch, capsys):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude(garbage_once={"v01"}))
    reader(planted)
    r = rows(planted)
    assert r["v01"]["calls_retried"] == 1 and r["v01"]["final_verdict"] == "answer"
    assert r["v01"]["attempts"][0]["retried"] is True


def test_dry_makes_no_call(planted, monkeypatch, capsys):
    make_attempt(planted)
    fake = FakeClaude()
    setup(planted, monkeypatch, fake)
    assert reader(planted, "--dry") == 0
    out = capsys.readouterr().out
    assert fake.calls == 0 and "questions 80" in out and "apart by category 1" in out and "first bundles loaded 80" in out
    assert not (planted["root"] / "runs/fresh-80/reader").exists()
    clean(out, planted)


def test_refused_without_hold(planted, monkeypatch):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    monkeypatch.setattr(L, "hold_on", lambda: False)
    assert reader(planted) == 2


def test_say_refuses_a_hidden_path(planted, capsys):
    L.guard_root(planted["root"])
    with pytest.raises(SystemExit):
        L.say(f"look at {planted['root']}/runs/fresh-80/reader")
    with pytest.raises(SystemExit):
        L.say("fixtures/evaluation/memory-verdict-2/hidden")
    L.say("counts 3")


def test_refused_unpinned(planted, monkeypatch):
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    monkeypatch.setattr(L, "pinned", lambda: False)
    assert reader(planted) == 2


def test_pin_check(tmp_path, monkeypatch):
    f = tmp_path / "a.py"
    f.write_text("x")
    pin = tmp_path / "PIN"
    monkeypatch.setattr(L, "HERE", tmp_path)
    monkeypatch.setattr(L, "PIN_FILE", pin)
    assert not L.pinned()
    pin.write_text(hashlib.sha256(b"x").hexdigest() + "  a.py\n")
    assert L.pinned()
    f.write_text("y")
    assert not L.pinned()


# ---- round 1's fixes

@pytest.mark.parametrize("result,why", [
    ({"evidence": [1], "rerank": {"by": "service"}, "facets": {"lexical": {"available": True},
                                                              "semantic": {"available": True}}}, None),
    ({"evidence": [1], "rerank": {"by": "private"}, "facets": {"lexical": {"available": True},
                                                              "semantic": {"available": True}}}, "reranker private"),
    ({"evidence": [1], "rerank": {"by": "unavailable"}, "facets": {"lexical": {"available": True},
                                                                  "semantic": {"available": True}}}, "reranker unavailable"),
    ({"evidence": [1], "rerank": {"by": "service"}, "facets": {"lexical": {"available": True}}}, "route semantic missing"),
    ({"evidence": [1], "rerank": {"by": "service"}, "facets": {"lexical": {"available": False},
                                                              "semantic": {"available": True}}}, "route lexical unavailable"),
    ({"evidence": [1], "rerank": {"by": "service"}, "pool": {"fallback": {"by": "unavailable"}},
      "facets": {"lexical": {"available": True}, "semantic": {"available": True}}}, "pool fallback"),
    ({"stopping_reason": "UNRESOLVED_IDS", "evidence": [], "facets": {}}, None),
    ({"no": "bundle"}, "no bundle"),
])
def test_degraded(result, why):  # code review F1
    assert L.degraded(result) == why


def test_degraded_later_search_counted(planted, monkeypatch, capsys):  # code review F1, item 17
    make_attempt(planted)
    monkeypatch.setenv("FAKE_DEGRADE_SEARCH", "v03")
    setup(planted, monkeypatch, FakeClaude())
    reader(planted)
    out = capsys.readouterr().out
    r = rows(planted)
    assert r["v03"]["search_failures"] == 2 and r["v03"]["searches"][0]["why"] == "route semantic unavailable"
    assert r["v03"]["searches"][0]["rerank_by"] == "service"
    assert "search_failure_ids: ['v03']" in out and "route semantic unavailable" in out


def test_reader_refused_without_the_act(planted, monkeypatch, capsys):  # readiness-7 F1
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    (planted["main"] / ".claude/hooks/pretooluse.py").write_text("# none\n")
    assert reader(planted) == 2
    assert "ACT-GUARD-SETS-1 is not applied" in capsys.readouterr().out
    assert not (planted["root"] / "runs/fresh-80/reader").exists()


def test_reader_refused_when_the_digest_moved(planted, monkeypatch, capsys):  # readiness-7 F6
    from helpers import preflight_json
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    preflight_json(planted)
    f = planted["hidden"] / "v02.yaml"
    f.write_text(f.read_text() + "\n")
    rc = L.run_tool("reader", RD.main, ["--sets-root", str(planted["root"]), "--clone", str(planted["clone"])])
    assert rc == 2 and "digest" in capsys.readouterr().out


def test_traceback_goes_to_the_run_folder(planted, monkeypatch, capsys):  # readiness-7 F10
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())

    def boom(sets_root, qs):
        raise ValueError(f"cannot read {qs[0]['question']}")
    monkeypatch.setattr(RD, "firsts", boom)
    assert reader(planted) == 1
    out = capsys.readouterr().out
    assert "ERROR: ValueError" in out and "planted question" not in out
    err = (planted["root"] / "runs/fresh-80/reader.err").read_text()
    assert "planted question v01" in err and "Traceback" in err


def test_reader_lock(planted, monkeypatch, capsys):  # code review R3
    import fcntl
    make_attempt(planted)
    setup(planted, monkeypatch, FakeClaude())
    d = planted["root"] / "runs/fresh-80/reader"
    d.mkdir(parents=True)
    held = open(d / ".lock", "w")
    fcntl.flock(held, fcntl.LOCK_EX)
    assert reader(planted) == 2 and "lock" in capsys.readouterr().out
    held.close()


def test_live_check(planted, monkeypatch, capsys, tmp_path):  # code review R1
    import f80_check as C
    log = tmp_path / "rerank.log"
    log.write_text("2026-11-08T00:00:00+0000\tREADY\tpid 4242 device cuda:0\n")
    args = ["live", "--clone", str(planted["clone"]), "--gov", str(planted["gov"]), "--log", str(log)]
    pin_cmd = "python -I /x/pin-bcea09060ebc/lib/python3.12/site-packages/gov/retrieval/rerank_service.py Q"
    monkeypatch.setattr(C, "_cmdline", lambda pid: pin_cmd if pid == "4242" else "")
    assert C.main(args) == 0
    monkeypatch.setattr(C, "_cmdline", lambda pid: "")  # the service gone
    assert C.main(args) == 1
    monkeypatch.setattr(C, "_cmdline", lambda pid: pin_cmd.replace("pin-bcea09060ebc", "pin-other"))
    assert C.main(args) == 1
    monkeypatch.setattr(C, "_cmdline", lambda pid: pin_cmd)
    gov = tmp_path / "gov_down.py"  # the probe answered without the reranker
    gov.write_text("#!/usr/bin/env python3\nimport json\nprint(json.dumps({'ok': True, 'result': {'evidence': [1], "
                   "'rerank': {'by': 'unavailable'}, 'facets': {'lexical': {'available': True}, "
                   "'semantic': {'available': True}}}}))\n")
    gov.chmod(0o755)
    args[4] = str(gov)
    assert C.main(args) == 1
    assert "a probe search answered as declared: no (reranker unavailable)" in capsys.readouterr().out
