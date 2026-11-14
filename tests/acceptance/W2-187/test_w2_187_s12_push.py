"""S12 and F7: the weekly secret scan and push (DEC-1182 (2); Interface I13, read with I11).

``python3 -m gov.memaudit push --sets-root R [--repo D] [--gitleaks EXE]``, declared by ``GOV_MEMAUDIT_PUSH="<remote> <branch>"``
(absent or empty: no push). One scan, ``gitleaks detect --source <repo> --no-banner --redact --report-format json --report-path
<a 0600 file outside the repository>``; the report's entries are counted and the report deleted. One stdout line:
``PUSH none: no declaration`` (exit 0), ``PUSH pushed <remote> <branch> <12 hex>`` (0), ``PUSH blocked: findings <k>`` (1),
``PUSH blocked: scan failed <word>`` (1), ``PUSH failed: git push exit <c>`` (2; git's output in a 0600 file in the key folder,
never printed). The same line is the last line of the cycle's latest ``DIGEST.txt`` in the key folder and one more ``cron.log``
line (the six keys, the step ``push``). The wrapper calls it as its last step, only when a standing or fresh step started that
cycle; ``maintain`` never scans; ``push.py`` holds the only gitleaks call; A9's ACT.md step 6 states the order.

Everything is planted: a repository, a bare remote, a fake gitleaks (a script on a planted path), no real scan. Readings the
Interface leaves open (each is in the case's docstring): the ``push`` command itself writes the digest line and the ``cron.log`` line
when a push is declared (a no-declaration ``push`` writes nothing, I13's note, DEC-1157 (3));
"the step named push" is the value of the ``mode`` or the ``reason`` key; the scan-failed reason is one word; a ``PUSH`` line with no
digest to hold it is not tested; the wrapper's exit with ``push`` last is not tested.
"""

from __future__ import annotations

import os
import re
import shutil
import time
from pathlib import Path

import pytest

import w2_187_maintain as M
import w2_187_push as P
import w2_187_world as W
from w2_187_push import SECRET


@pytest.fixture
def pw(tmp_path):
    return P.PushWorld(tmp_path / "pw")


def line_of(run) -> str:
    """The one stdout line of a push run."""
    assert len(run.lines) == 1, run
    return run.lines[0]


def check_logged(world, line: str, code: int, *, before_cron: int = 1) -> None:
    """The line is the last of the latest digest (an older digest, and the lines before it, are untouched) and one more
    ``cron.log`` line carries the six keys and the step ``push``."""
    lines = world.digest_lines()
    assert lines[-1] == line and lines[:-1] == P.WEEK_DIGEST, lines
    assert world.digest_lines("2026-W45") == P.OLD_DIGEST, "an older digest is not the cycle's"
    cron = world.cron_lines()
    assert len(cron) == before_cron + 1, cron
    last = cron[-1]
    assert set(last) == P.CRON_KEYS, last
    assert "push" in (last["mode"], last["reason"]), last
    assert last["exit"] == code, last


def nothing_leaked(world, run) -> None:
    """The planted secret is in no printed line, ``cron.log``, ``DIGEST.txt`` or file under the key folder or the sets root."""
    for text in (run.out, run.err):
        assert SECRET not in text and P.NOISE not in text, text
    assert P.secret_hits(world.folder, world.sets) == []


# -- the clean scan: one scan, then the push -------------------------------------------------------------------------------------------
def test_s12_a_clean_scan_of_the_repository_is_followed_by_the_push_of_its_head(pw):
    assert pw.remote_head() == pw.first
    run = pw.push(declared=pw.declare())
    assert run.code == 0, run
    assert line_of(run) == f"PUSH pushed {pw.remote} main {pw.head[:12]}", run
    assert pw.remote_head() == pw.head, "the remote's branch equals the repository's head"
    (call,) = pw.fake.calls()
    P.check_scan_argv(call, pw.repo)
    P.check_report_path(call, pw.repo)
    assert not os.path.exists(call["path"]), "the report is deleted"
    assert P.no_stray_files(pw.tmp) == [], "no report or temporary file is left"
    nothing_leaked(pw, run)


def test_s12_the_push_line_is_the_last_line_of_the_latest_digest_and_cron_log_gains_one_push_line(pw):
    run = pw.push(declared=pw.declare())
    assert run.code == 0, run
    check_logged(pw, line_of(run), 0)


def test_s12_the_scan_runs_before_the_push_and_the_remote_is_untouched_while_it_runs(pw):
    """A scan that is still running has pushed nothing: the fake reads the remote's branch when it is called."""
    pw.fake.plan(entries=0, exit=0, probe=str(pw.remote))
    run = pw.push(declared=pw.declare())
    assert run.code == 0, run
    assert (pw.fake.folder / "seen.txt").read_text().strip() == pw.first, "the remote still held the first commit during the scan"
    assert pw.remote_head() == pw.head


def test_s12_the_binary_is_the_flag_else_the_environments_else_the_path(pw, tmp_path):
    env_fake = P.Fake(tmp_path / "gl" / "env", label="env")
    flag_fake = P.Fake(tmp_path / "gl" / "flag", label="flag")
    path_fake = P.Fake(tmp_path / "gl" / "pathdir", label="path")
    # the flag beats the environment
    run = pw.push(declared=pw.declare(), gitleaks=env_fake.exe, flag=flag_fake.exe)
    assert run.code == 0, run
    assert len(flag_fake.calls()) == 1 and env_fake.calls() == []
    # the environment beats the path
    path = f"{pw.nogl}{os.pathsep}{path_fake.folder}"
    run = pw.push(declared=pw.declare(), gitleaks=env_fake.exe, path=path)
    assert run.code == 0, run
    assert len(env_fake.calls()) == 1 and path_fake.calls() == []
    # neither: the program named gitleaks on the path
    run = pw.push(declared=pw.declare(), gitleaks=None, path=path)
    assert run.code == 0, run
    assert len(path_fake.calls()) == 1


# -- failure-7 and success-12: a scan that finds anything, fails or cannot run blocks the push -------------------------------------------
@pytest.mark.parametrize("k", [1, 3])
def test_s12_a_scan_with_findings_blocks_the_push_names_the_count_and_never_the_secret(pw, k):
    """Exit 1 and ``k`` report entries each holding the planted secret (the fake also prints it on its stdout and stderr)."""
    pw.fake.plan(entries=k, exit=1)
    run = pw.push(declared=pw.declare())
    assert run.code == 1, run
    assert line_of(run) == f"PUSH blocked: findings {k}", run
    assert pw.remote_head() == pw.first, "the remote is unchanged"
    (call,) = pw.fake.calls()
    assert not os.path.exists(call["path"]), "the report is deleted"
    assert P.no_stray_files(pw.tmp) == []
    nothing_leaked(pw, run)
    check_logged(pw, f"PUSH blocked: findings {k}", 1)


def exit_two(pw):
    pw.fake.plan(entries=0, exit=2)
    return pw.push(declared=pw.declare()), None


def no_binary_by_flag(pw):
    return pw.push(declared=pw.declare(), gitleaks=None, flag=pw.base / "no-such-dir" / "gitleaks"), None


def no_binary_on_path(pw):
    return pw.push(declared=pw.declare(), gitleaks=None), None


def too_slow(pw):
    pw.fake.plan(entries=2, exit=1, sleep=40)
    began = time.monotonic()
    run = pw.push(declared=pw.declare(), extra={"GOV_MEMAUDIT_SCAN_TIMEOUT_S": "2"}, timeout=120)
    return run, time.monotonic() - began


@pytest.mark.parametrize("how", [exit_two, no_binary_by_flag, no_binary_on_path, too_slow],
                         ids=["exit-2", "missing-by-flag", "missing-on-path", "timeout"])
def test_s12_a_scan_that_fails_or_cannot_run_blocks_the_push_and_is_named_by_one_reason_word(pw, how):
    run, seconds = how(pw)
    assert run.code == 1, run
    assert re.fullmatch(r"PUSH blocked: scan failed \S+", line_of(run)), run
    assert pw.remote_head() == pw.first, "the remote is unchanged"
    if seconds is not None:
        assert seconds < 60, f"a scan past GOV_MEMAUDIT_SCAN_TIMEOUT_S=2 was waited for {seconds:.0f} s"
    nothing_leaked(pw, run)
    check_logged(pw, line_of(run), 1)


def test_s12_the_failure_words_are_never_the_findings_form(pw):
    """A failed scan is not counted as findings: ``scan failed`` on exit 2, ``findings`` only on exit 1 with entries."""
    pw.fake.plan(entries=2, exit=2)
    run = pw.push(declared=pw.declare())
    assert run.code == 1 and "findings" not in line_of(run) and "scan failed" in line_of(run), run
    assert pw.remote_head() == pw.first


# -- no declaration: neither step runs, and it says so ----------------------------------------------------------------------------------
@pytest.mark.parametrize("declared", [None, ""], ids=["unset", "empty"])
def test_s12_a_repository_with_no_declaration_runs_neither_step_and_says_so(pw, make_world, declared):
    """I13's note (DEC-1157 (3)): a push is declared when the scan or the push starts; a ``push`` with no declaration prints its
    line, exits 0 and writes nothing (no ``cron.log`` line, no digest line, no file), so W2-172 S9's one-line ``cron.log`` holds.
    Through the wrapper the line reaches the wrapper's own stdout, and the push step writes nothing."""
    before_folder, before_tmp = W.tree_state(pw.folder), W.tree_state(pw.tmp)
    run = pw.push(declared=declared)
    assert run.code == 0, run
    assert line_of(run) == "PUSH none: no declaration", run
    assert pw.fake.calls() == [], "gitleaks is not called"
    assert pw.remote_head() == pw.first, "nothing is pushed"
    assert W.tree_state(pw.folder) == before_folder, "nothing is written: no cron.log line, no digest line, no file in the key folder"
    assert len(pw.cron_lines()) == 1
    assert pw.digest_lines() == P.WEEK_DIGEST and pw.digest_lines("2026-W45") == P.OLD_DIGEST
    assert W.tree_state(pw.tmp) == before_tmp, "no report or temporary file is made"
    assert W.tree_state(pw.sets) == {}, "nothing under the sets root"
    # through the wrapper: a cycle in which an audit step started, the real ``push`` (the shim sends it to the real interpreter)
    world = make_world(link=False)
    world.plant_plan("shim187_plan.json", plan(live=False, standing=True))
    fake = P.Fake(world.base / "gl" / "fake")
    digest = world.mem / "standing" / W.STD / "2026-W47" / "DIGEST.txt"
    digest.parent.mkdir(parents=True)
    digest.write_text("STANDING x\n", encoding="utf-8")
    env = {"GOV_MEMAUDIT_GITLEAKS": str(fake.exe)}
    if declared is not None:
        env["GOV_MEMAUDIT_PUSH"] = declared
    done = P.run_wrapper(world, world.base / "bin" / "py_shim187", env=env)
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert "PUSH none: no declaration" in done.stdout.splitlines(), f"the wrapper's own stdout: {done.stdout!r}"
    assert fake.calls() == [], "the wrapper calls no gitleaks"
    assert digest.read_text(encoding="utf-8") == "STANDING x\n", "the push step adds no digest line"
    crons = [line for path in world.runs_env.rglob("cron.log") for line in world.jsonl_file(path)]
    assert len(crons) == 1 and "push" not in (crons[0]["mode"], crons[0]["reason"]), crons
    assert not any(b"PUSH" in p.read_bytes() for p in world.runs_env.rglob("*") if p.is_file()), "nothing under the runs folder names PUSH"


# -- a push that fails ---------------------------------------------------------------------------------------------------------------------
def test_s12_a_remote_that_refuses_the_push_is_exit_2_and_gits_output_is_kept_in_a_0600_file_never_printed(pw):
    P.reject_pushes(pw.remote)
    before = pw.key_files()
    run = pw.push(declared=pw.declare())
    assert run.code == 2, run
    assert line_of(run) == "PUSH failed: git push exit 1", run
    assert len(pw.fake.calls()) == 1, "the scan was clean and ran once"
    assert pw.remote_head() == pw.first
    for text in (run.out, run.err):
        assert P.HOOK not in text and "remote:" not in text and "error:" not in text and "hint:" not in text, text
    kept = [Path(p) for p in pw.key_files() - before if P.HOOK in Path(p).read_text(errors="replace")]
    assert len(kept) == 1, "git's own output is in one new file of the key folder"
    assert (kept[0].stat().st_mode & 0o777) == 0o600
    check_logged(pw, "PUSH failed: git push exit 1", 2)


def test_s12_a_declared_remote_that_does_not_exist_is_a_failed_push_not_a_crash(pw):
    before = pw.key_files()
    run = pw.push(declared=pw.declare(pw.base / "no-such-remote.git"))
    assert run.code == 2, run
    assert line_of(run) == "PUSH failed: git push exit 128", run
    assert "fatal" not in run.err and "does not appear" not in run.err and "does not appear" not in run.out
    new = [Path(p) for p in pw.key_files() - before if (Path(p).stat().st_mode & 0o777) == 0o600 and Path(p).stat().st_size]
    assert new, "git's output is kept in a 0600 file of the key folder"
    check_logged(pw, "PUSH failed: git push exit 128", 2)


# -- the optional real scan ---------------------------------------------------------------------------------------------------------------
INSTALLED = shutil.which("gitleaks")


@pytest.mark.skipif(INSTALLED is None, reason="no gitleaks on the path")
def test_s12_an_installed_gitleaks_passes_a_clean_repository_and_stops_a_planted_key(pw):
    """One scan each way with the installed program (skipped where ``shutil.which`` finds no gitleaks). The planted key is an AWS access key id form."""
    key = "AKIAQ3RT7XWNB5KLMP2D"
    assert key[:4] == "AKIA" and len(key) == 20
    run = pw.push(declared=pw.declare(), gitleaks=INSTALLED)
    assert run.code == 0 and line_of(run) == f"PUSH pushed {pw.remote} main {pw.head[:12]}", run
    (pw.repo / "config.env").write_text(f"aws_access_key_id = {key}\n", encoding="utf-8")
    P.git(pw.repo, pw.home, "add", "-A")
    P.git(pw.repo, pw.home, "commit", "-q", "-m", "a key")
    blocked_head = pw.remote_head()
    run = pw.push(declared=pw.declare(), gitleaks=INSTALLED)
    assert run.code == 1 and re.fullmatch(r"PUSH blocked: findings [1-9]\d*", line_of(run)), run
    assert pw.remote_head() == blocked_head, "the remote is unchanged"
    for text in (run.out, run.err):
        assert key not in text
    for path in pw.folder.rglob("*"):
        assert not path.is_file() or key.encode() not in path.read_bytes()


# -- the wrapper: push is the last step of a weekly cycle in which an audit step started --------------------------------------------
KEY = "repo-0123abcd"
DUE_YES, DUE_NO = ["MODE weekly", "DUE yes next 2026-11-16", "REASON start"], ["MODE monthly", "DUE no next 2026-12-01", "REASON stable"]
FRESH_YES, FRESH_NO = ["MODE fresh", "DUE yes next 2026-11-16", "REASON 28d"], ["MODE fresh", "DUE no next 2026-12-14", "REASON wait"]


def plan(*, standing=True, fresh=True, misses=False, live=True, push_exit=0):
    return {
        "standing live": {"lines": [f"KEY {KEY}", f"LIVE {W.STD}" if live else "LIVE none"], "exit": 0 if live else 1},
        "due": {"lines": DUE_YES if standing else DUE_NO, "exit": 0 if standing else 1},
        "due --fresh": {"lines": FRESH_YES if fresh else FRESH_NO, "exit": 0 if fresh else 1},
        "maintain": {"lines": ["MAINTAIN 1 store x 2 layout x 3 links 0 4 unindexed 0 5 not_found 0 second 0 6 reanchor 0"], "exit": 0},
        "standing run": {"lines": [f"STANDING 2026-W47 right {75 if misses else 80} of 80: {'misses' if misses else 'passes'}"],
                         "exit": 0},
        "run": {"lines": ["STARTED"], "exit": 0},
        "push": {"lines": ["PUSH none: no declaration"], "exit": push_exit},
    }


def cycle(make_world, spec, *, env=None):
    world = make_world(link=False)
    world.plant_plan("shim187_plan.json", spec)
    shim = P.install_push_shim(world)
    fake = P.Fake(world.base / "gl" / "fake")
    done = P.run_wrapper(world, shim, env={"GOV_MEMAUDIT_GITLEAKS": str(fake.exe), **(env or {})})
    return world, done, fake


def keys(world):
    return [c["key"] for c in world.jsonl("shim187_calls.jsonl")]


@pytest.mark.parametrize("standing,fresh,misses,expected", [
    (True, True, True, ["standing live", "due", "due --fresh", "maintain", "standing run", "maintain", "run", "push"]),
    (True, True, False, ["standing live", "due", "due --fresh", "maintain", "standing run", "run", "push"]),
    (True, False, True, ["standing live", "due", "due --fresh", "maintain", "standing run", "maintain", "push"]),
    (True, False, False, ["standing live", "due", "due --fresh", "maintain", "standing run", "push"]),
    (False, True, False, ["standing live", "due", "due --fresh", "maintain", "run", "push"]),
])
def test_s12_the_wrapper_ends_a_cycle_in_which_an_audit_step_started_with_one_push(make_world, standing, fresh, misses, expected):
    world, done, fake = cycle(make_world, plan(standing=standing, fresh=fresh, misses=misses))
    assert keys(world) == expected, (keys(world), done.stderr)
    assert fake.calls() == [], "the wrapper itself calls no gitleaks: the push step does"
    push = [c for c in world.jsonl("shim187_calls.jsonl") if c["key"] == "push"][0]
    argv = push["argv"]
    assert argv[:3] == ["-m", "gov.memaudit", "push"], argv
    assert argv[argv.index("--sets-root") + 1] == str(world.sets)
    assert argv[argv.index("--repo") + 1] in (str(world.repo), os.path.realpath(world.repo)), argv
    assert push["cwd"] == os.path.realpath(world.repo)


@pytest.mark.parametrize("live", [True, False], ids=["live-set", "no-live-set"])
def test_s12_a_cycle_where_nothing_was_due_calls_neither_the_push_nor_gitleaks(make_world, live):
    world, done, fake = cycle(make_world, plan(standing=False, fresh=False, live=live),
                              env={"GOV_MEMAUDIT_PUSH": "somewhere main"})
    assert done.returncode == 0, (done.stdout, done.stderr)
    assert "push" not in keys(world), keys(world)
    assert fake.calls() == []


def test_s12_with_no_live_set_todays_path_also_ends_with_the_push_after_its_run(make_world):
    world, done, _ = cycle(make_world, plan(live=False, standing=True))
    assert keys(world) == ["standing live", "due", "run", "push"], (keys(world), done.stderr)


def test_s12_end_to_end_a_due_cycle_scans_once_and_pushes_and_a_cycle_with_nothing_due_does_neither(make_world, tmp_path):
    """The wrapper with the real ``push`` (the other cases' shim sends it to the real interpreter): a declared bare remote, the
    planted ``run`` that starts, the fake gitleaks."""
    for due, pushed in ((True, True), (False, False)):
        world = make_world(link=False)
        spec = plan(live=False, standing=due)
        world.plant_plan("shim187_plan.json", spec)
        remote = P.make_remote(tmp_path / f"remote-{due}.git", world.home)
        fake = P.Fake(world.base / "gl" / "fake")
        digest = world.mem / "standing" / W.STD / "2026-W47" / "DIGEST.txt"
        digest.parent.mkdir(parents=True)
        digest.write_text("STANDING x\n", encoding="utf-8")
        branch = world.repo_git("rev-parse", "--abbrev-ref", "HEAD").strip()
        head = world.repo_git("rev-parse", "HEAD").strip()
        shim = world.base / "bin" / "py_shim187"      # W2-187's own shim: it sends ``push`` to the real interpreter
        done = P.run_wrapper(world, shim, env={"GOV_MEMAUDIT_GITLEAKS": str(fake.exe),
                                               "GOV_MEMAUDIT_PUSH": f"{remote} {branch}"})
        assert done.returncode == 0, (done.stdout, done.stderr)
        assert len(fake.calls()) == (1 if pushed else 0)
        assert P.remote_head(remote, world.home, branch) == (head if pushed else None)
        if pushed:
            assert digest.read_text().splitlines()[-1] == f"PUSH pushed {remote} {branch} {head[:12]}"


# -- F7: no scan and no push at a refresh or a close ---------------------------------------------------------------------------------------
def test_f7_the_maintenance_pass_never_scans_not_even_at_a_refresh_and_never_pushes(make_world, tmp_path):
    world = make_world(standing=True)
    head = M.behind(world, 2)
    M.plan_rebuild(world, advance_to=head)
    remote = P.make_remote(tmp_path / "remote-m.git", world.home)
    fake = P.Fake(world.base / "gl" / "fake")
    run = world.maintain(env={"GOV_MEMAUDIT_GITLEAKS": str(fake.exe), "GOV_MEMAUDIT_PUSH": f"{remote} main"})
    assert run.code == 0 and world.link_head() == head, "the store was refreshed in this pass"
    assert len(M.rebuild_calls(world)) == 1
    assert fake.calls() == [], "a refresh is not a scan"
    assert P.remote_head(remote, world.home, "main") is None and not any(x.startswith("PUSH") for x in run.lines)


def test_f7_a_standing_run_never_scans_or_pushes_at_its_close(make_world, tmp_path):
    world = make_world(std="pass", standing=True)
    remote = P.make_remote(tmp_path / "remote-s.git", world.home)
    fake = P.Fake(world.base / "gl" / "fake")
    run = world.standing_run(gate=world.gate_stub, env={"GOV_MEMAUDIT_GITLEAKS": str(fake.exe),
                                                       "GOV_MEMAUDIT_PUSH": f"{remote} main"})
    assert run.code == 0, run
    assert fake.calls() == [] and P.remote_head(remote, world.home, "main") is None
    assert not any(x.startswith("PUSH") for x in run.lines)


def test_f7_push_py_holds_the_only_gitleaks_call_of_the_cycle_the_wrapper_names_none():
    modules = sorted((W.SRC / "gov" / "memaudit").glob("*.py"))
    push = W.SRC / "gov" / "memaudit" / "push.py"
    assert push.is_file(), "src/gov/memaudit/push.py"
    assert "gitleaks" in push.read_text(encoding="utf-8").lower(), "push.py is where the scan is"
    others = [m.name for m in modules if m != push and P.module_calls_gitleaks(m)]
    assert others == [], f"a module other than push.py runs gitleaks: {others}"
    assert not P.wrapper_names_gitleaks(W.WRAPPER), "the wrapper reaches gitleaks only through the push step"


def test_f7_the_wrapper_runs_no_scan_and_no_push_of_its_own():
    text = W.WRAPPER.read_text(encoding="utf-8")
    assert not re.search(r"\bgit\s+(-C\s+\S+\s+)?push\b", text), "the push is the module's, after its scan"


# -- A9: ACT.md's step 6 states the order and how the push is declared ---------------------------------------------------------------------
def test_s12_acts_step_6_states_the_order_of_the_cycle_and_how_the_push_is_declared_and_calls_no_crontab(make_world):
    world = make_world(link=False)
    text, sets_root = P.walls_act_text(world, str(world.repo))
    row = P.squash(P.step6_text(text))
    assert P.squash(P.STEP6_SENTENCE) in row, row
    assert "0 21 * * 1" in row, "step 6 is still the cron line"
    assert world.crontab_calls() == "" and not os.path.exists(sets_root), "text only: no crontab read, no folder made"
