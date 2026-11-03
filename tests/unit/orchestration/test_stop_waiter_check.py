"""The CTO's Stop hook that names an unarmed inbox waiter (DEC-1027 E)."""
import json
import os
import subprocess
import sys
from pathlib import Path

HOOK = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/stop_waiter_check.py"
CTO = "07f25884-0000-0000-0000-000000000000"


def run(tmp_path, *, session=CTO, active=False, procs=(), standby=False, registered=True, raw=None):
    orch = tmp_path / "orch"
    (orch / "log").mkdir(parents=True, exist_ok=True)
    if registered:
        (orch / "log/cto-session.txt").write_text(CTO + "\n")
    if standby:
        (orch / "log/cto-standby.txt").write_text("on purpose\n")
    ps = tmp_path / "ps.txt"
    ps.write_text("\n".join(procs) + "\n")
    env = dict(os.environ, GOV_STOPCHECK_ORCH=str(orch), GOV_STOPCHECK_PS=str(ps))
    stdin = raw if raw is not None else json.dumps({"session_id": session, "stop_hook_active": active})
    out = subprocess.run([sys.executable, "-E", str(HOOK)], input=stdin, capture_output=True, text=True, env=env,
                         timeout=30)
    assert out.returncode == 0
    return out.stdout.strip()


def test_the_cto_with_no_waiter_is_blocked_with_the_command(tmp_path):
    answer = json.loads(run(tmp_path, procs=["python3 something else"]))
    assert answer["decision"] == "block"
    assert "inbox_wait_quiet.sh" in answer["reason"] and "DEC-1027 E" in answer["reason"]


def test_an_armed_waiter_of_either_kind_lets_the_turn_end(tmp_path):
    assert run(tmp_path, procs=["bash /x/tools/inbox_wait_quiet.sh"]) == ""
    assert run(tmp_path, procs=["bash /x/tools/inbox_wait.sh"]) == ""


def test_another_session_is_never_blocked(tmp_path):
    assert run(tmp_path, session="someone-else") == ""


def test_a_declared_stand_by_is_never_blocked(tmp_path):
    assert run(tmp_path, standby=True) == ""


def test_it_never_blocks_twice_in_a_row(tmp_path):
    assert run(tmp_path, active=True) == ""


def test_no_registered_session_or_bad_input_says_nothing(tmp_path):
    assert run(tmp_path, registered=False) == ""
    assert run(tmp_path, raw="not json") == ""
