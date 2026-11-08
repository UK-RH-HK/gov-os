"""run_measure.sh on the planted set: one shot (USED), the control, the fault rule, GOV_STORE refused (S6), no rebuild
and the store's sha256 (S7), integrate's head and the store log recorded (S5), no hidden path printed. Each test
runs a temporary copy with one stubs line (the fake gov, a pass-through heavy slot, a stub backstop, a planted hold
and store log) and checks that the copy less that line is run_measure.sh, byte for byte."""
import json
import os
import subprocess
from pathlib import Path

import pytest

TOOLS = Path(__file__).resolve().parent.parent
SCRIPT = TOOLS / "run_measure.sh"
MARK = "# --- the stubs line (tests only: test_run_measure.py runs a copy with one line here; the copy less it is this file)\n"


def stubbed(planted, tmp: Path, hold="FRESH-80 HOLD (test)\n") -> Path:
    stub = tmp / "stub"
    stub.mkdir(exist_ok=True)
    (stub / "heavy.sh").write_text('#!/usr/bin/env bash\nexec "$@"\n')
    (stub / "backstop.sh").write_text("#!/usr/bin/env bash\nexec sleep 600\n")
    (stub / "hold.txt").write_text(hold)
    (stub / "store.log").write_text("line before\n")
    line = (f'CLONE={planted["clone"]}; GOV={planted["gov"]}; HEAVY={stub}/heavy.sh; BACKSTOP={stub}/backstop.sh; '
            f'ISLOG={stub}/store.log; HOLD={stub}/hold.txt; TMPD={tmp}/tmpd; REPO={planted["main"]}; '
            f'LIVE_LOG={stub}/rerank.log; pinned() {{ true; }}; '
            # the clone check needs HEAD c00d525f (tested in test_preflight); the live check is tested in python
            # (test_live_check); here it fails only when FAKE_LIVE_DOWN names a file that exists and attempt-1 does
            f'check() {{ [ "$1" = clone ] && return 0; if [ "$1" = live ]; then [ -n "${{FAKE_LIVE_DOWN:-}}" ] && '
            f'[ -e "$FAKE_LIVE_DOWN" ] && [ -d "$RUNS/attempt-1" ] && return 1; return 0; fi; '
            f'"$PINPY" "$F/f80_check.py" "$@" 2>> "$ERRF"; }}\n')
    src = SCRIPT.read_text()
    assert src.count(MARK) == 1
    copy = src.replace(MARK, MARK + line)
    assert copy.replace(line, "", 1) == src  # the copy less the stubs line is the file
    out = tmp / "run_measure.copy.sh"
    out.write_text(copy)
    return out


def preflight_ok(planted, declared=True):
    import f80lib as L
    from conftest import declare
    runs = planted["root"] / "runs/fresh-80"
    runs.mkdir(parents=True, exist_ok=True)
    (runs / "preflight.json").write_text(json.dumps({"all_ok": True, "at": "test",
                                                     "item1": {"sha256": L.set_digest(planted["root"])}}))
    if declared:
        declare(planted)


def run(planted, tmp, *args, env=None, hold="FRESH-80 HOLD (test)\n"):
    e = {k: v for k, v in os.environ.items() if k not in ("GOV_STORE", "GOV_TICKET", "GOV_ROLE")}
    e.update(env or {})
    p = subprocess.run(["bash", str(stubbed(planted, tmp, hold)), "--sets-root", str(planted["root"]), *args],
                       capture_output=True, text=True, env=e, start_new_session=True, timeout=600)
    return p


def clean_output(p, planted):
    for line in (p.stdout + p.stderr).splitlines():
        assert str(planted["root"]) + "/" not in line, line
        assert "memory-verdict-2/" not in line and "fresh-80/" not in line, line
        assert "planted question" not in line, line


def test_refuses_when_used(planted, tmp_path):
    preflight_ok(planted)
    runs = planted["root"] / "runs/fresh-80"
    (runs / "USED").write_text("used\n")
    before = sorted(x.name for x in runs.iterdir())
    p = run(planted, tmp_path)
    assert p.returncode == 2
    assert "REFUSED" in p.stdout and "USED" in p.stdout
    assert sorted(x.name for x in runs.iterdir()) == before  # nothing written
    clean_output(p, planted)


def test_refuses_gov_store_and_writes_nothing(planted, tmp_path):  # reviewer 1 S6
    preflight_ok(planted)
    p = run(planted, tmp_path, env={"GOV_STORE": "/somewhere"})
    assert p.returncode == 2 and "GOV_STORE" in p.stdout
    runs = planted["root"] / "runs/fresh-80"
    assert sorted(x.name for x in runs.iterdir()) == ["preflight.json"]


def test_no_rebuild_in_the_script():  # reviewer 1 S7
    src = SCRIPT.read_text()
    for word in ("rebuild_pinned", "--seed", "W2-00-store.lock", "gov-os-d4b-rebuild.lock"):
        assert word not in src
    assert 'env -u GOV_STORE -u GOV_TICKET GOV_ROLE=orchestrator' in src


def test_refuses_without_hold_or_preflight(planted, tmp_path):
    p = run(planted, tmp_path)  # no preflight.json
    assert p.returncode == 2 and "pre-flight" in p.stdout
    preflight_ok(planted)
    p = run(planted, tmp_path, hold="something else\n")
    assert p.returncode == 2 and "hold" in p.stdout
    assert not (planted["root"] / "runs/fresh-80/USED").exists()


def test_full_run_counts_attempt_1(planted, tmp_path):
    preflight_ok(planted)
    store = planted["clone"] / ".gov-runtime/store.db"
    sha0 = __import__("hashlib").sha256(store.read_bytes()).hexdigest()
    p = run(planted, tmp_path)
    assert p.returncode == 0, p.stdout + p.stderr
    runs = planted["root"] / "runs/fresh-80"
    assert (runs / "USED").is_file()
    assert (runs / "COUNTS").read_text().strip() == "attempt-1"
    assert (runs / "attempt-1/DONE").is_file() and not (runs / "attempt-2").exists()
    assert len(list((runs / "attempt-1/kept").glob("[0-9]*.json"))) == 80
    assert "hit@5 34" in p.stdout  # the control
    assert "attempt-1: searches by rerank.by: None 1, service 79; answered otherwise than declared: 0 (none)" in p.stdout
    rec = (runs / "record-1.txt").read_text()
    assert f"store_before {sha0}" in rec and f"store_after {sha0}" in rec  # S7: the store untouched
    assert "integrate before" in p.stdout and "unchanged" in p.stdout  # S5
    assert "0 new line(s)" in p.stdout
    clean_output(p, planted)
    # a second start is refused: the measure never runs twice
    p2 = run(planted, tmp_path)
    assert p2.returncode == 2 and "USED" in p2.stdout


def test_one_restart_into_a_new_folder(planted, tmp_path):
    preflight_ok(planted)
    flag = tmp_path / "fail-once"
    flag.write_text("x")
    p = run(planted, tmp_path, env={"FAKE_FAIL_ONCE": str(flag)})
    assert p.returncode == 0, p.stdout
    runs = planted["root"] / "runs/fresh-80"
    assert (runs / "attempt-1/FAULT").is_file()
    assert (runs / "COUNTS").read_text().strip() == "attempt-2"
    assert "one restart, from the start" in p.stdout
    clean_output(p, planted)


def test_second_fault_stops(planted, tmp_path):
    preflight_ok(planted)
    p = run(planted, tmp_path, env={"FAKE_FAIL_ALWAYS": "1"})
    assert p.returncode == 1
    runs = planted["root"] / "runs/fresh-80"
    assert (runs / "STOPPED").is_file() and not (runs / "COUNTS").exists()
    assert (runs / "attempt-1/FAULT").is_file() and (runs / "attempt-2/FAULT").is_file()
    # and --restart is refused now
    p2 = run(planted, tmp_path, "--restart")
    assert p2.returncode == 2


def test_store_change_is_a_fault_that_stops(planted, tmp_path):  # reviewer 1 (3)
    preflight_ok(planted)
    store = planted["clone"] / ".gov-runtime/store.db"
    p = run(planted, tmp_path, env={"FAKE_TOUCH_STORE": str(store)})
    assert p.returncode == 1
    runs = planted["root"] / "runs/fresh-80"
    assert "store changed" in (runs / "attempt-1/FAULT").read_text()
    assert (runs / "STOPPED").is_file() and not (runs / "attempt-2").exists()


def test_control_out_of_range_stops_before_the_80(planted, tmp_path):
    preflight_ok(planted)
    vis = planted["root"] / "fixtures/evaluation/memory-retrieval/visible"
    for k in ("c01", "c02", "c03"):  # 31 hit: outside 34 +- 2
        f = vis / f"{k}.yaml"
        f.write_text(f.read_text().replace("[hit]", "[miss]"))
    p = run(planted, tmp_path)
    assert p.returncode == 1 and "the control failed" in p.stdout
    runs = planted["root"] / "runs/fresh-80"
    assert not (runs / "USED").exists() and not (runs / "attempt-1").exists()


def test_degraded_search_is_a_fault_then_one_restart(planted, tmp_path):  # code review F1
    preflight_ok(planted)
    flag = tmp_path / "degrade-once"
    flag.write_text("x")
    p = run(planted, tmp_path, env={"FAKE_DEGRADE_ONCE": str(flag)})
    assert p.returncode == 0, p.stdout
    runs = planted["root"] / "runs/fresh-80"
    assert "answered otherwise than declared: 1 (reranker unavailable 1)" in p.stdout
    assert (runs / "attempt-1/FAULT").is_file() and (runs / "COUNTS").read_text().strip() == "attempt-2"
    assert len(list(runs.glob("control-*"))) == 2  # the control again before the restart (review R1)
    clean_output(p, planted)


def test_no_restart_into_the_same_outage(planted, tmp_path):  # code review R1
    preflight_ok(planted)
    flag, down = tmp_path / "degrade-once", tmp_path / "live-down"
    flag.write_text("x")
    down.write_text("x")
    env = {"FAKE_DEGRADE_ONCE": str(flag), "FAKE_LIVE_DOWN": str(down)}
    p = run(planted, tmp_path, env=env)
    runs = planted["root"] / "runs/fresh-80"
    assert p.returncode == 1 and "no restart into the same outage" in p.stdout
    assert (runs / "attempt-1/FAULT").is_file() and not (runs / "attempt-2").exists()
    assert not (runs / "STOPPED").exists() and not (runs / "COUNTS").exists()
    down.unlink()  # the servers are back: the one --restart
    p2 = run(planted, tmp_path, "--restart", env=env)
    assert p2.returncode == 0, p2.stdout
    assert (runs / "COUNTS").read_text().strip() == "attempt-2"


def test_restart_when_used_but_nothing_started(planted, tmp_path):  # code review R9
    preflight_ok(planted)
    runs = planted["root"] / "runs/fresh-80"
    (runs / "USED").write_text("used\n")
    p = run(planted, tmp_path, "--restart")
    assert p.returncode == 0, p.stdout
    assert (runs / "COUNTS").read_text().strip() == "attempt-1"


def test_refused_without_the_act(planted, tmp_path):  # readiness-7 F1
    preflight_ok(planted)
    m = planted["main"] / "governance/project/path-map.yaml"
    m.write_text(m.read_text().replace("sets_root_hidden:", "other_block:"))
    p = run(planted, tmp_path)
    assert p.returncode == 2 and "ACT-GUARD-SETS-1 is not applied" in p.stdout
    runs = planted["root"] / "runs/fresh-80"
    assert sorted(x.name for x in runs.iterdir()) == ["preflight.json"]
    h = planted["main"] / ".claude/hooks/pretooluse.py"
    m.write_text(m.read_text().replace("other_block:", "sets_root_hidden:"))
    h.write_text("# no rule\n")
    p = run(planted, tmp_path)
    assert p.returncode == 2 and "ACT-GUARD-SETS-1 is not applied" in p.stdout


def test_refused_declaration_blank_uncommitted_or_digest_moved(planted, tmp_path):  # readiness-7 F6, F12
    from conftest import declare
    preflight_ok(planted, declared=False)
    declare(planted, blanks=True)
    p = run(planted, tmp_path)
    assert p.returncode == 2 and "declaration" in p.stdout and "blanks left 1" in p.stdout
    declare(planted, commit=False)  # filled, not committed
    p = run(planted, tmp_path)
    assert p.returncode == 2 and "committed no" in p.stdout
    declare(planted)
    f = planted["hidden"] / "v01.yaml"
    f.write_text(f.read_text() + "\n")  # a late change after the pre-flight and the declaration
    p = run(planted, tmp_path)
    assert p.returncode == 2 and "its digest is the set's now no" in p.stdout
    assert not (planted["root"] / "runs/fresh-80/USED").exists()
