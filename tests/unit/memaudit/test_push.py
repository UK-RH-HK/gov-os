"""W2-187 I13 (S12, F7): the weekly secret scan and push on a planted repository, a bare remote under ``tmp_path`` and a fake
scanner script (never the real scanner, the network or the real sets root)."""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

from gov.memaudit import schedule

from .conftest import SRC, git_env, run

FAKE = '''#!%(python)s
import json, os, stat, sys, time
here = os.path.dirname(os.path.realpath(__file__))
plan = json.load(open(os.path.join(here, "plan.json")))
args = sys.argv[1:]
path = args[args.index("--report-path") + 1]
with open(os.path.join(here, "calls.jsonl"), "a") as f:
    f.write(json.dumps({"argv": args, "mode": stat.S_IMODE(os.stat(path).st_mode), "cwd": os.getcwd(),
                        "name": os.path.basename(__file__)}) + "\\n")
if plan.get("sleep"):
    time.sleep(plan["sleep"])
if plan.get("report") is not None:
    open(path, "w").write(plan["report"])
else:
    open(path, "w").write(json.dumps([{"RuleID": "r", "Match": plan.get("secret", "x"), "Secret": "REDACTED"}
                                      for _ in range(plan.get("entries", 0))]))
sys.stderr.write(plan.get("secret", "") + "\\n")
sys.exit(plan.get("exit", 0))
'''
SECRET = "sk-PLANTEDSECRETvalue0123456789"


class World:
    def __init__(self, tmp: Path):
        self.tmp = tmp
        self.env = git_env(tmp)
        self.repo = tmp / "adopted"
        self.bare = tmp / "remote.git"
        run("git", "init", "-q", "--bare", "-b", "main", str(self.bare), env=self.env)
        run("git", "init", "-q", "-b", "main", str(self.repo), env=self.env)
        (self.repo / "a.md").write_text("a\n")
        run("git", "add", "-A", cwd=self.repo, env=self.env)
        run("git", "commit", "-q", "-m", "one", cwd=self.repo, env=self.env)
        run("git", "remote", "add", "origin", str(self.bare), cwd=self.repo, env=self.env)
        self.head = run("git", "rev-parse", "HEAD", cwd=self.repo, env=self.env).stdout.strip()
        self.sets, self.runs = tmp / "sets", tmp / "runs"
        self.sets.mkdir()
        self.bin = self.fake(tmp / "bin")
        self.state = schedule.state_dir(self.runs, self.repo)

    def fake(self, folder: Path, name="gitleaks") -> Path:
        folder.mkdir(exist_ok=True)
        exe = folder / name
        exe.write_text(FAKE % {"python": sys.executable}, encoding="utf-8")
        exe.chmod(0o755)
        (folder / "plan.json").write_text("{}")
        return folder

    def plan(self, folder=None, **plan):
        (folder or self.bin).joinpath("plan.json").write_text(json.dumps(plan))

    def calls(self, folder=None):
        log = (folder or self.bin) / "calls.jsonl"
        return [json.loads(x) for x in log.read_text().splitlines()] if log.exists() else []

    def digest(self, name="memory-audit-20261111"):
        path = self.state / name / "DIGEST.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("STANDING x\nVERDICT y\n")
        return path

    def push(self, *args, declare="origin main", path=None, extra_env=None):
        env = {"PATH": f"{path or self.bin}:/usr/bin:/bin", "HOME": str(self.tmp), "PYTHONPATH": SRC,
               "GOV_INDEP_RUNS_DIR": str(self.runs), "TMPDIR": str(self.tmp), **(extra_env or {})}
        if declare is not None:
            env["GOV_MEMAUDIT_PUSH"] = declare
        return subprocess.run([sys.executable, "-m", "gov.memaudit", "push", "--sets-root", str(self.sets),
                               "--repo", str(self.repo), *args], capture_output=True, text=True, env=env, cwd=self.tmp)

    def remote_head(self):
        done = subprocess.run(["git", "-C", str(self.bare), "rev-parse", "--verify", "-q", "refs/heads/main"],
                              capture_output=True, text=True, env=self.env)
        return done.stdout.strip() or None

    def everything_written(self):
        return "".join(p.read_text(errors="replace") for p in (self.tmp.rglob("*")) if p.is_file()
                       and ".git" not in p.parts and "objects" not in p.parts and p.suffix != ".pyc"
                       and p.name not in {"gitleaks", "plan.json", "calls.jsonl"} and "bare" not in p.name)


@pytest.fixture
def world(tmp_path):
    return World(tmp_path)


def test_a_clean_scan_pushes_the_branch_once_and_names_it_in_one_line_and_the_digest(world):
    digest = world.digest()
    done = world.push()
    assert done.returncode == 0, done.stderr
    assert done.stdout == f"PUSH pushed origin main {world.head[:12]}\n" and done.stderr == ""
    assert world.remote_head() == world.head
    calls = world.calls()
    assert len(calls) == 1
    argv = calls[0]["argv"]
    assert argv[:7] == ["detect", "--source", str(world.repo), "--no-banner", "--redact", "--report-format", "json"]
    assert argv[7] == "--report-path" and len(argv) == 9
    report = Path(argv[8])
    assert calls[0]["mode"] == 0o600 and not str(report.resolve()).startswith(str(world.repo.resolve()) + "/")
    assert not report.exists()  # counted, then deleted
    assert digest.read_text().splitlines()[-1] == done.stdout.strip() and digest.read_text().startswith("STANDING x\n")
    log = world.state / "PUSH.log"
    assert stat.S_IMODE(log.stat().st_mode) == 0o600 and "main" in log.read_text()
    assert "To " not in done.stdout + done.stderr  # git's own output is never printed


def test_the_latest_digest_of_the_key_folder_gets_the_line_a_standing_weeks_included(world):
    old = world.digest()
    week = world.state / "standing/memory-standing-20261111/2026-W47/DIGEST.txt"
    week.parent.mkdir(parents=True)
    week.write_text("STANDING s\n")
    os.utime(old, (1, 1))
    assert world.push().returncode == 0
    assert week.read_text().splitlines()[-1].startswith("PUSH pushed ") and "PUSH" not in old.read_text()


def test_a_scan_that_finds_something_blocks_the_push_and_no_text_of_a_finding_is_written(world):
    digest = world.digest()
    world.plan(entries=3, secret=SECRET, exit=1)
    done = world.push()
    assert done.returncode == 1 and done.stdout == "PUSH blocked: findings 3\n"
    assert world.remote_head() is None  # the remote is unchanged
    assert digest.read_text().splitlines()[-1] == "PUSH blocked: findings 3"
    assert SECRET not in done.stdout + done.stderr + world.everything_written()
    assert not Path(world.calls()[0]["argv"][8]).exists()


def test_a_report_with_entries_is_a_finding_whatever_the_exit(world):
    world.plan(entries=1, exit=0)
    done = world.push()
    assert done.returncode == 1 and done.stdout == "PUSH blocked: findings 1\n" and world.remote_head() is None


@pytest.mark.parametrize("plan, word", [({"exit": 2}, "exit"), ({"exit": 126, "entries": 2}, "exit"),
                                         ({"exit": 1, "report": ""}, "report"), ({"exit": 1, "entries": 0}, "report"),
                                         ({"exit": 0, "report": "not json"}, "report")])
def test_a_scan_that_fails_blocks_the_push_with_a_reason_word_only(world, plan, word):
    world.plan(secret=SECRET, **plan)
    done = world.push()
    assert done.returncode == 1 and done.stdout == f"PUSH blocked: scan failed {word}\n", done.stdout
    assert world.remote_head() is None and SECRET not in done.stdout + done.stderr + world.everything_written()


def test_a_scan_past_the_timeout_blocks_the_push(world):
    world.plan(sleep=30)
    done = world.push(extra_env={"GOV_MEMAUDIT_SCAN_TIMEOUT_S": "0.5"})
    assert done.returncode == 1 and done.stdout == "PUSH blocked: scan failed timeout\n"
    assert world.remote_head() is None
    assert not list(world.tmp.glob("scan-*.json"))  # the report is deleted whatever happened


def test_no_scanner_blocks_the_push_named(world):
    done = world.push(path=world.tmp / "nowhere")  # nothing named gitleaks on PATH
    assert done.returncode == 1 and done.stdout == "PUSH blocked: scan failed missing\n" and world.remote_head() is None
    done = world.push("--gitleaks", str(world.tmp / "no-such-binary"))
    assert done.returncode == 1 and done.stdout == "PUSH blocked: scan failed missing\n"


def test_the_binary_is_the_flag_else_the_environment_else_the_one_on_path(world):
    other = world.fake(world.tmp / "other", name="scanner-env")
    third = world.fake(world.tmp / "third", name="scanner-flag")
    assert world.push(extra_env={"GOV_MEMAUDIT_GITLEAKS": str(other / "scanner-env")}).returncode == 0
    assert [c["name"] for c in world.calls(other)] == ["scanner-env"] and world.calls() == []
    run("git", "commit", "-q", "--allow-empty", "-m", "two", cwd=world.repo, env=world.env)
    assert world.push("--gitleaks", str(third / "scanner-flag"),
                      extra_env={"GOV_MEMAUDIT_GITLEAKS": str(other / "scanner-env")}).returncode == 0
    assert [c["name"] for c in world.calls(third)] == ["scanner-flag"] and len(world.calls(other)) == 1
    assert world.push().returncode == 0 and len(world.calls()) == 1  # PATH's own


@pytest.mark.parametrize("declare", [None, "", "   "])
def test_no_declaration_runs_neither_the_scan_nor_the_push_and_says_so(world, declare):
    digest = world.digest()
    done = world.push(declare=declare)
    assert done.returncode == 0 and done.stdout == "PUSH none: no declaration\n"
    assert world.calls() == [] and world.remote_head() is None
    assert digest.read_text() == "STANDING x\nVERDICT y\n", "a no-declaration push writes nothing (I13 (2))"
    assert not (world.state / "cron.log").exists() and not (world.state / "PUSH.log").exists()


@pytest.mark.parametrize("declare", ["origin", "origin main extra", "--force main", "origin --delete"])
def test_a_declaration_that_is_not_a_remote_and_a_branch_is_usage_and_nothing_runs(world, declare):
    done = world.push(declare=declare)
    assert done.returncode == 4 and world.calls() == [] and world.remote_head() is None


def test_a_push_git_refuses_is_exit_2_its_output_kept_in_a_private_file_never_printed(world):
    run("git", "remote", "set-url", "origin", str(world.tmp / "no-such-remote.git"), cwd=world.repo, env=world.env)
    done = world.push()
    assert done.returncode == 2 and done.stdout == "PUSH failed: git push exit 128\n" and done.stderr == ""
    log = world.state / "PUSH.log"
    assert stat.S_IMODE(log.stat().st_mode) == 0o600 and "fatal" in log.read_text()
    assert len(world.calls()) == 1  # scanned once, then pushed once


def test_without_a_digest_the_step_still_answers(world):
    done = world.push()
    assert done.returncode == 0 and not list(world.state.glob("**/DIGEST.txt"))


def test_a_repository_inside_the_sets_root_is_usage(world):
    done = subprocess.run([sys.executable, "-m", "gov.memaudit", "push", "--sets-root", str(world.tmp), "--repo",
                           str(world.repo)], capture_output=True, text=True, cwd=world.tmp,
                          env={"PATH": f"{world.bin}:/usr/bin:/bin", "PYTHONPATH": SRC, "GOV_MEMAUDIT_PUSH": "origin main",
                               "HOME": str(world.tmp), "GOV_INDEP_RUNS_DIR": str(world.runs)})
    assert done.returncode == 4 and world.calls() == [] and world.remote_head() is None


def test_this_module_holds_the_only_scanner_call_of_the_audit_and_the_wrapper():
    folder = Path(__file__).resolve().parents[3] / "src/gov/memaudit"
    wrapper = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/memaudit_cron.sh"
    others = [p.name for p in sorted(folder.glob("*.py")) if p.name != "push.py" and "gitleaks" in p.read_text().lower()]
    assert others == [] and "gitleaks" not in wrapper.read_text().lower()
    assert (folder / "push.py").read_text().count('"detect"') == 1


def cron_rows(world, name="cron.log"):
    path = world.state / name
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []


@pytest.mark.parametrize("plan, line, code", [({}, "PUSH pushed origin main", 0),
                                              ({"entries": 2, "exit": 1}, "PUSH blocked: findings 2", 1),
                                              ({"exit": 2}, "PUSH blocked: scan failed exit", 1)])
def test_a_declared_push_writes_its_own_cron_log_line_with_the_six_keys_and_the_step_push(world, plan, line, code):
    world.digest()
    world.plan(**plan)
    done = world.push(extra_env={"GOV_MEMAUDIT_NOW": "2026-11-16T21:00:00Z"})
    assert done.returncode == code
    (row,) = cron_rows(world)
    assert set(row) == {"at", "due", "mode", "reason", "started", "exit"}
    assert (row["at"], row["due"], row["mode"], row["started"], row["exit"]) == ("2026-11-16T21:00:00Z", True, "push", True, code)
    assert done.stdout.startswith(line) and row["reason"] == done.stdout.strip().removeprefix("PUSH ")


def test_a_push_that_git_refuses_is_logged_with_exit_2(world):
    run("git", "remote", "set-url", "origin", str(world.tmp / "no-such-remote.git"), cwd=world.repo, env=world.env)
    done = world.push()
    assert done.returncode == 2
    assert [(r["mode"], r["exit"], r["reason"]) for r in cron_rows(world)] == [("push", 2, "failed: git push exit 128")]


def test_the_wrapper_may_name_the_log_the_line_goes_to(world):
    elsewhere = world.tmp / "elsewhere" / "cron.log"
    elsewhere.parent.mkdir()
    done = world.push(extra_env={"GOV_MEMAUDIT_CRON_LOG": str(elsewhere)})
    assert done.returncode == 0 and not (world.state / "cron.log").exists()
    assert [json.loads(x)["mode"] for x in elsewhere.read_text().splitlines()] == ["push"]


def test_a_usage_fault_writes_no_log_line(world):
    assert world.push(declare="origin").returncode == 4 and not (world.state / "cron.log").exists()
