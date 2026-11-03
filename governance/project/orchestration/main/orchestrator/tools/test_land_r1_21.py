"""land.py under R1-21 (DEC-1052): after a queue run lands a ticket, the structural pass runs on the new head (base: the
head before the run), its lines go to the landing's log and, when a family is not ok or the pass could not run, one
inbox item in the dispatcher's form. A notice only: the landing's exit code is unchanged. The file under test:
LAND_UNDER_TEST, default land.candidate.py beside this file while it exists, else land.py (once promoted).

    TMPDIR=/tmp/gov-os-emg-r121 PYTHONPATH= python3 -m pytest -q -p no:cacheprovider \
        -o tmp_path_retention_policy=failed test_land_r1_21.py
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
UNDER_TEST = Path(os.environ.get("LAND_UNDER_TEST") or (HERE / "land.candidate.py" if (HERE / "land.candidate.py").is_file()
                                                        else HERE / "land.py"))
C, BEFORE = "c" * 40, "b" * 40
NOTICE_OUT = ("schema: ok\ngraph: NOTICE 1 finding: DAEO-x depends on DAEO-gone which does not exist\n"
              "portability: skipped (no change)\nstructural pass at dddddddddddd: NOTICE in graph (7 of 8 families "
              "ok), 8.5 s; a notice, not a refusal\n")
OK_OUT = "schema: ok\nportability: skipped (no change)\nstructural pass at dddddddddddd: all 8 families ok, 8.5 s\n"


@pytest.fixture
def land():
    spec = importlib.util.spec_from_file_location("land_under_test_r1_21", UNDER_TEST)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def env(land, tmp_path, monkeypatch):
    """A landing whose queue run lands W2-1 (or ejects it: env.eject()); every command faked except the record files."""
    root = tmp_path / "root"
    (root / "governance/project/orchestration/closes").mkdir(parents=True)
    (root / "governance/project/secrets.yaml").write_text("scan: off\n")
    ls = tmp_path / "load_sensitive.txt"
    ls.write_text("# none\n")
    q = tmp_path / "q"
    st = SimpleNamespace(calls=[], out=NOTICE_OUT, rc=0, raise_=None, inbox=tmp_path / "inbox", q=q, land_ejects=False)

    def fake(cmd, **kw):
        cmd = [str(c) for c in cmd]
        st.calls.append(cmd)
        if any(c.endswith("structural_pass.py") for c in cmd):
            if st.raise_:
                raise st.raise_
            return SimpleNamespace(returncode=st.rc, stdout=st.out, stderr="")
        if "run" in cmd[2:4]:  # the queue run: it lands W2-1 (or ejects it)
            rec = tmp_path / "rec.json"
            rec.write_text(json.dumps({"base": BEFORE, "head": "d" * 40}))
            sub = "ejected" if st.land_ejects else "landed"
            (q / sub).mkdir(parents=True, exist_ok=True)
            (q / sub / "W2-1.json").write_text(json.dumps(
                {"commit": C, "merge": "d" * 40, "landed_at": "2999-01-01 00:00:00", "record": str(rec),
                 "reason": "a red"}))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def fake_git(*a):
        return BEFORE if a[:2] == ("rev-parse", land.INTEGRATION) else C
    monkeypatch.setattr(land, "ROOT", root)
    monkeypatch.setattr(land, "QUEUE", q)
    monkeypatch.setattr(land, "LOAD_SENSITIVE", ls)
    monkeypatch.setattr(land, "INBOX", st.inbox)
    monkeypatch.setattr(land, "sh", fake)
    monkeypatch.setattr(land, "subprocess", SimpleNamespace(run=fake))
    monkeypatch.setattr(land, "git", fake_git)
    monkeypatch.setattr(land, "ticket_of", lambda w2: ("DAEO-x", "STANDARD"))
    monkeypatch.setattr(land, "precheck", lambda *a: ([], "r"))
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1"])
    return st


def run_main(land, capsys):
    with pytest.raises(SystemExit) as e:
        land.main()
    return e.value.code, capsys.readouterr().out


def passes(st):
    return [c for c in st.calls if any(x.endswith("structural_pass.py") for x in c)]


def items(st):
    return sorted(st.inbox.glob("*.txt")) if st.inbox.is_dir() else []


def test_a_landed_batch_calls_the_pass_on_the_new_head_and_a_notice_becomes_one_inbox_item(land, env, capsys):
    code, out = run_main(land, capsys)
    assert code == 0, out
    assert "CLOSED W2-1" in out
    calls = passes(env)
    assert len(calls) == 1, env.calls
    assert calls[0][1:] == [str(land.STRUCTURAL), str(land.ROOT), BEFORE]
    assert out.index("CLOSED W2-1") < out.index("structural pass: schema: ok")  # after the close commit
    assert "structural pass: graph: NOTICE 1 finding" in out and "structural pass: structural pass at dddd" in out
    got = items(env)
    assert len(got) == 1 and re.fullmatch(r"\d{8}-\d{6}-structural-notice\.txt", got[0].name), got
    body = got[0].read_text()
    head = body.splitlines()
    assert head[0].startswith("log: ") and head[1].startswith("Structural: after the landing of W2-1 (base bbbbbbbbbbbb)")
    assert head[2] == "status: structural pass at dddddddddddd: NOTICE in graph (7 of 8 families ok), 8.5 s; a " \
                      "notice, not a refusal"
    assert "DAEO-gone" in body
    assert f"notice -> inbox/{got[0].name}" in out


def test_all_ok_goes_to_the_log_and_writes_no_item(land, env, capsys):
    env.out = OK_OUT
    code, out = run_main(land, capsys)
    assert code == 0 and len(passes(env)) == 1
    assert "structural pass: structural pass at dddddddddddd: all 8 families ok" in out
    assert items(env) == []


def test_nothing_landed_runs_no_pass(land, env, capsys):
    env.land_ejects = True
    code, out = run_main(land, capsys)
    assert "not landed" in out and passes(env) == [] and items(env) == []


def test_check_only_runs_no_pass(land, env, capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["land.py", "W2-1", "--check"])
    land.main()
    assert passes(env) == [] and items(env) == []


@pytest.mark.parametrize("how", ["exit", "timeout", "oserror"])
def test_a_pass_that_cannot_run_is_one_item_and_the_landing_stands(land, env, capsys, how):
    if how == "exit":
        env.rc, env.out = 2, "structural pass could not run: /x is not the top of a git work tree\n"
    elif how == "timeout":
        env.raise_ = subprocess.TimeoutExpired("structural_pass.py", 150)
    else:
        env.raise_ = OSError("no such interpreter")
    code, out = run_main(land, capsys)
    assert code == 0 and "CLOSED W2-1" in out
    got = items(env)
    assert len(got) == 1
    status = got[0].read_text().splitlines()[2]
    assert status.startswith("status: the structural pass could not run"), status
    assert {"exit": "not the top of a git work tree", "timeout": "did not end within 150 s",
            "oserror": "no such interpreter"}[how] in status


def test_a_landing_that_failed_its_close_still_gets_the_pass_and_keeps_exit_6(land, env, capsys, monkeypatch):
    real = land.sh

    def tk_fails(cmd, **kw):
        r = real(cmd, **kw)
        return SimpleNamespace(returncode=1, stdout="", stderr="tk broke") if cmd[:2] == ["tk", "close"] else r
    monkeypatch.setattr(land, "sh", tk_fails)
    code, out = run_main(land, capsys)
    assert code == 6 and "LANDED BUT NOT CLOSED" in out
    assert len(passes(env)) == 1 and len(items(env)) == 1


def test_inbox_items_are_never_overwritten(land, env):
    a = land.inbox_item("structural-notice", "one\n")
    b = land.inbox_item("structural-notice", "two\n")
    assert a != b and a.read_text() == "one\n" and b.read_text() == "two\n"


def test_the_call_runs_the_real_pass_on_a_planted_tree(land, tmp_path, monkeypatch, capsys):
    """End to end: the real structural_pass.py on a planted clean tree with one dangling dependency."""
    import test_structural_pass as tsp
    repo = tsp.plant(tmp_path)
    base = tsp.git(repo, "rev-parse", "HEAD")
    (repo / ".tickets/DAEO-t003.md").write_text(tsp.ticket("DAEO-t003", ["DAEO-gone"]))
    tsp.commit_all(repo, "a dangling dependency")
    monkeypatch.setattr(land, "ROOT", repo)
    monkeypatch.setattr(land, "INBOX", tmp_path / "inbox")
    monkeypatch.setenv("PYTHONPATH", "")
    item = land.structural_notice(base, ["W2-1"])
    out = capsys.readouterr().out
    assert "structural pass: graph: NOTICE" in out and "structural pass: portability: skipped" in out, out
    assert item is not None and "DAEO-gone" in item.read_text()
