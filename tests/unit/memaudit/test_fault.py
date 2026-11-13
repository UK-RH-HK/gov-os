"""S4, F3, F4: the fault rule's parts, the wrapper and the ledger lock, without a measure."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import threading
from pathlib import Path

import pytest

from gov.memaudit import events, fault, ledger, wrapper

GOOD = {"stopping_reason": "SATURATED", "evidence": [{"path": "a", "start_line": 1, "end_line": 2, "text": "t"}],
        "facets": {"lexical": {"available": True}, "semantic": {"available": True}}, "rerank": {"by": "service"}}


def variant(**kw):
    out = json.loads(json.dumps(GOOD))
    for k, v in kw.items():
        out[k] = v
    return out


@pytest.mark.parametrize("result,why", [
    (GOOD, None),
    (None, "no bundle"), ({}, "no bundle"), ({"evidence": "x"}, "no bundle"),
    (variant(facets={"semantic": {"available": True}}), "route lexical missing"),
    (variant(facets={"lexical": {"available": True}}), "route semantic missing"),
    (variant(facets={"lexical": {"available": False}, "semantic": {"available": True}}), "route lexical unavailable"),
    (variant(facets={"lexical": {"available": True}, "semantic": {"available": False}}), "route semantic unavailable"),
    (variant(rerank={"by": "private"}), "reranker private"),
    (variant(rerank={"by": "unavailable"}), "reranker unavailable"),
    (variant(rerank=None), "reranker None"),
    (variant(pool={"fallback": True}), "pool fallback"),
    (variant(pool={"fallback": False}), None),
    # an empty bundle with UNRESOLVED_IDS is the stated gap, no degradation; an empty bundle otherwise needs no rerank
    ({"stopping_reason": "UNRESOLVED_IDS", "evidence": []}, None),
    (variant(evidence=[], rerank=None), None),
    (variant(evidence=[], facets={}), "route lexical missing"),
])
def test_degraded_is_the_fresh_80s_rule_on_a_kept_result(result, why):
    assert fault.degraded(result) == why


@pytest.mark.parametrize("rc,doc,ok,word", [
    (0, {"ok": True, "result": GOOD}, True, None),
    (1, {"ok": True, "result": GOOD}, False, "exit"),
    (0, {"ok": False, "result": GOOD}, False, "no bundle"),
    (0, {"ok": True}, False, "no bundle"),
    (0, {"ok": True, "result": variant(rerank={"by": "private"})}, False, "reranker"),
    (0, {"ok": True, "result": variant(facets={})}, False, "route"),
    (0, {"ok": True, "result": variant(pool={"fallback": True})}, False, "pool"),
])
def test_answered_names_why_a_search_was_not_answered_as_declared(rc, doc, ok, word):
    assert fault.answered(rc, json.dumps(doc)) == (ok, word)
    assert fault.answered(0, "not json") == (False, "no bundle")


LINES = ("families: contract (4 members)\nmeasure: set s, part hidden\n"
         "q01 (hidden): hit@5 yes (first gold rank 1), in the bundle yes; full evidence yes (1 of 1 pieces); 1 calls\n"
         "q02 (hidden): hit@5 no (first gold rank -), in the bundle no; full evidence no (0 of 1 pieces); 2 calls; family hits: 1\n"
         "total: hit@5 1 of 2 (50.0 %, floor 85); full evidence 1 of 2 (50.0 %, target 99 %)\n")


def test_parse_reads_the_measures_own_question_lines():
    got = fault.parse(LINES)
    assert got["families"] == "families: contract (4 members)" and got["total"] is True
    assert got["questions"] == [
        {"id": "q01", "part": "hidden", "hit5": True, "rank": 1, "bundle": True, "full": True, "calls": 1},
        {"id": "q02", "part": "hidden", "hit5": False, "rank": None, "bundle": False, "full": False, "calls": 2}]


def folder_of(tmp_path, text=LINES, kept=3, result=GOOD):
    (tmp_path / "kept").mkdir()
    (tmp_path / "measure.txt").write_text(text)
    for i in range(1, kept + 1):
        (tmp_path / "kept" / f"{i:05d}.json").write_text(json.dumps({"ok": True, "result": result}))
    (tmp_path / "kept" / ".n").write_text("3\n")
    return tmp_path


FAM = "families: contract (4 members)"


def test_an_attempt_is_whole_when_every_condition_of_item_12_holds(tmp_path):
    assert fault.not_whole(folder_of(tmp_path), 2, FAM) is None


@pytest.mark.parametrize("n,fam,text,kept,cause", [
    (3, FAM, LINES, 3, "whole"),                                    # the question lines are not n
    (2, "families: none", LINES, 3, "whole"),                       # the families line is not the control's
    (2, FAM, LINES.replace("(hidden)", "(visible)", 1), 3, "whole"),  # a line of another part
    (2, FAM, LINES.replace("total:", "t:"), 3, "whole"),            # no total line
    (2, FAM, LINES.replace("families:", "fam:"), 3, "whole"),       # no families line
    (2, FAM, LINES, 2, "whole"),                                    # the kept files are not the sum of the calls
    (2, FAM, LINES, 4, "whole"),
])
def test_an_attempt_not_whole_names_whole(tmp_path, n, fam, text, kept, cause):
    assert fault.not_whole(folder_of(tmp_path, text, kept), n, fam) == cause


def test_a_degraded_kept_output_is_degraded_and_whole_is_judged_first(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir()
    b.mkdir()
    bad = variant(rerank={"by": "private"})
    assert fault.not_whole(folder_of(a, result=bad), 2, FAM) == "degraded"
    assert fault.not_whole(folder_of(b, result=bad), 3, FAM) == "whole"


# ---- the wrapper

def fake_gov(tmp_path, body="print('{}')"):
    exe = tmp_path / "realgov"
    exe.write_text(f"#!{sys.executable}\nimport sys, os\n{body}\n")
    exe.chmod(0o755)
    return exe


def test_install_writes_a_python_file_mode_700_whole(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    path = wrapper.install(run, tmp_path / "realgov")
    assert path == run / "gov" and stat.S_IMODE(path.stat().st_mode) == 0o700
    assert path.read_text().startswith(f"#!{sys.executable}\n") and not list(run.glob(".*.tmp"))
    assert wrapper.install(run, tmp_path / "other").read_text().count("other") == 1  # rewritten whole


def test_the_wrapper_keeps_each_retrieve_output_and_appends_its_event_before_it_returns(tmp_path):
    run = tmp_path / "run"
    run.mkdir()
    keep = run / "kept"
    keep.mkdir()
    (keep / ".n").write_text("0\n")
    real = fake_gov(tmp_path, "import json\nprint(json.dumps({'ok': True, 'result': {'evidence': [], 'facets': "
                              "{'lexical': {'available': True}, 'semantic': {'available': True}}}}))")
    shim = wrapper.install(run, real)
    env = {**os.environ, "GOV_AUDIT_RUN": str(run), "GOV_AUDIT_PHASE": "attempt", "GOV_AUDIT_ATTEMPT": "2",
           "GOV_KEEP": str(keep), "GOV_MS": str(run / "ms"), "PYTHONPATH": str(Path(wrapper.__file__).parents[2])}
    out = [subprocess.run([str(shim), "retrieve", "a question", "--json"], env=env, capture_output=True, text=True)
           for _ in range(2)]
    assert [o.returncode for o in out] == [0, 0] and json.loads(out[0].stdout)["ok"] is True
    assert sorted(p.name for p in keep.glob("*.json")) == ["00001.json", "00002.json"]
    assert (keep / "00001.json").read_text() == out[0].stdout
    ev = ledger.read(run)
    assert [(e["event"], e["phase"], e["attempt"], e["call"], e["qid"], e["rc"], e["ok"]) for e in ev] == [
        ("search", "attempt", 2, 1, None, 0, True), ("search", "attempt", 2, 2, None, 0, True)]
    assert len((run / "ms").read_text().split()) == 2


def test_a_non_retrieve_call_is_the_wrapped_govs_own(tmp_path):
    real = fake_gov(tmp_path, "print('version ' + ' '.join(sys.argv[1:]))")
    run = tmp_path / "run"
    run.mkdir()
    shim = wrapper.install(run, real)
    env = {**os.environ, "GOV_AUDIT_RUN": str(run), "PYTHONPATH": str(Path(wrapper.__file__).parents[2])}
    done = subprocess.run([str(shim), "--version"], env=env, capture_output=True, text=True)
    assert done.stdout == "version --version\n" and not (run / "ledger.jsonl").exists()


def test_the_wrapped_govs_standard_error_goes_to_a_file_of_the_run_folder(tmp_path):
    real = fake_gov(tmp_path, "sys.stderr.write('a fake complaint\\n')\nprint('{}')")
    run = tmp_path / "run"
    run.mkdir()
    shim = wrapper.install(run, real)
    env = {**os.environ, "GOV_AUDIT_RUN": str(run), "GOV_AUDIT_PHASE": "ready",
           "PYTHONPATH": str(Path(wrapper.__file__).parents[2])}
    done = subprocess.run([str(shim), "retrieve", "q", "--json"], env=env, capture_output=True, text=True)
    assert done.stderr == "" and "a fake complaint" in (run / "gov.err").read_text()
    ev = ledger.read(run)
    assert [(e["phase"], e["call"], e["ok"]) for e in ev] == [("ready", None, False)]  # no bundle: not answered as declared


# ---- the ledger lock

def test_four_writers_never_interleave_a_line_or_repeat_a_seq(tmp_path):
    def worker(w):
        for i in range(25):
            events.append(tmp_path, "spend", call=f"w{w}", qid=f"q{i}", usd=0.01, total=0)
    threads = [threading.Thread(target=worker, args=(w,)) for w in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    lines = (tmp_path / "ledger.jsonl").read_text().splitlines()
    assert len(lines) == 100 and all(json.loads(x) for x in lines)
    assert [json.loads(x)["seq"] for x in lines] == list(range(1, 101))
    assert abs(events.spent(tmp_path) - 1.0) < 1e-9
