"""W2-187 I11 (S11): ``memaudit_cron.sh --repo`` runs the maintenance pass, the standing run and the fresh cycle in order, when
due, with a stub interpreter that answers the subcommands from a plan and logs each call. Nothing real starts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import git_env, run

WRAPPER = Path(__file__).resolve().parents[3] / "governance/project/orchestration/tools/memaudit_cron.sh"
SHIM = '''#!%(python)s
import json, os, sys
here = os.path.dirname(os.path.realpath(__file__))
plan = json.load(open(os.path.join(here, "plan.json")))
args = sys.argv[1:]
sub = args[2:]
key = " ".join(sub[:2]) if sub[:1] == ["standing"] else sub[0] + (" --fresh" if "--fresh" in sub else "")
with open(os.path.join(here, "calls.jsonl"), "a") as f:
    f.write(json.dumps({"key": key, "argv": args, "cwd": os.getcwd()}) + "\\n")
spec = plan.get(key, {})
for line in spec.get("lines", []):
    print(line)
sys.exit(spec.get("exit", 0))
'''
KEY = "adopted-0a1b2c3d"


class Cron:
    def __init__(self, tmp_path):
        self.tmp = tmp_path
        env = git_env(tmp_path)
        self.repo = tmp_path / "adopted"
        run("git", "init", "-q", "-b", "main", str(self.repo), env=env)
        self.bin = tmp_path / "shim"
        self.bin.mkdir()
        self.py = self.bin / "py"
        self.py.write_text(SHIM % {"python": sys.executable}, encoding="utf-8")
        self.py.chmod(0o755)
        self.runs, self.sets = tmp_path / "runs", tmp_path / "sets"
        self.plan({"standing live": {"lines": [f"KEY {KEY}", "LIVE memory-standing-20261111"], "exit": 0},
                   "due": {"lines": ["MODE weekly", "DUE yes next 2026-11-16", "REASON active"], "exit": 0},
                   "due --fresh": {"lines": ["MODE fresh", "DUE yes next 2026-11-16", "REASON 28d"], "exit": 0},
                   "standing run": {"lines": ["STANDING 2026-W47 right 76 of 80: passes"], "exit": 0},
                   "run": {"lines": [], "exit": 0}})

    def plan(self, changes):
        path = self.bin / "plan.json"
        doc = json.loads(path.read_text()) if path.exists() else {}
        doc.update(changes)
        path.write_text(json.dumps(doc))

    def wrapper(self, *args, cwd=None, push=None):
        env = {"PATH": "/usr/bin:/bin", "HOME": str(self.tmp), "GOV_MEMAUDIT_PYTHON": str(self.py),
               "GOV_MEMAUDIT_SETS_ROOT": str(self.sets), "GOV_INDEP_RUNS_DIR": str(self.runs),
               "GOV_MEMAUDIT_GATE": "the-gate --check", "GOV_MEMAUDIT_NOW": "2026-11-16T21:00:00Z"}
        if push is not None:
            env["GOV_MEMAUDIT_PUSH"] = push
        return subprocess.run(["bash", str(WRAPPER), *args], capture_output=True, text=True, env=env,
                              cwd=cwd or self.tmp)

    def keys(self):
        log = self.bin / "calls.jsonl"
        return [json.loads(x)["key"] for x in log.read_text().splitlines()] if log.exists() else []

    def calls(self):
        return [json.loads(x) for x in (self.bin / "calls.jsonl").read_text().splitlines()]

    def log(self, folder=KEY):
        path = self.runs / "indep" / "memaudit" / folder / "cron.log" if folder else self.runs / "indep/memaudit/cron.log"
        return [json.loads(x) for x in path.read_text().splitlines()]

    def audit_log(self, folder=KEY):
        """The log lines of the audit steps: the push step's own line (mode ``push``) is read apart."""
        return [x for x in self.log(folder) if x["mode"] != "push"]


@pytest.fixture
def cron(tmp_path):
    return Cron(tmp_path)


def test_a_due_standing_run_and_a_due_fresh_set_run_in_that_order_from_one_call(cron):
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 0, done.stderr
    assert cron.keys() == ["standing live", "due", "due --fresh", "maintain", "standing run", "run", "push"]
    run_call = cron.calls()[-2]["argv"]
    assert run_call[run_call.index("--gate-cmd") + 1] == "the-gate --check"
    assert cron.calls()[4]["argv"][cron.calls()[4]["argv"].index("--gate-cmd") + 1] == "the-gate --check"
    assert all(Path(c["cwd"]).resolve() == cron.repo.resolve() for c in cron.calls())  # it went to the repository
    row = cron.audit_log()[-1]
    assert set(row) == {"at", "due", "mode", "reason", "started", "exit"}
    assert (row["due"], row["started"], row["exit"]) == (True, True, 0) and row["mode"] == "weekly"
    assert "STANDING 2026-W47 right 76 of 80: passes" in done.stdout


def test_nothing_runs_when_neither_is_due(cron):
    cron.plan({"due": {"lines": ["MODE monthly", "DUE no next 2026-12-14", "REASON stable"], "exit": 1},
               "due --fresh": {"lines": ["MODE fresh", "DUE no next 2026-12-14", "REASON wait"], "exit": 1}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 0
    assert cron.keys() == ["standing live", "due", "due --fresh"]
    row = cron.log()[-1]
    assert (row["due"], row["started"], row["exit"], row["mode"], row["reason"]) == (False, False, 0, "monthly", "stable")


def test_a_miss_runs_the_maintenance_pass_again_at_once_in_the_same_cycle(cron):
    cron.plan({"standing run": {"lines": ["STANDING 2026-W47 right 70 of 80: misses"], "exit": 0}})
    cron.wrapper("--repo", str(cron.repo))
    assert cron.keys() == ["standing live", "due", "due --fresh", "maintain", "standing run", "maintain", "run", "push"]


def test_only_the_standing_run_is_due_and_the_exit_is_the_last_started_steps(cron):
    cron.plan({"due --fresh": {"lines": ["DUE no"], "exit": 1}, "standing run": {"lines": ["x"], "exit": 2}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert cron.keys() == ["standing live", "due", "due --fresh", "maintain", "standing run", "push"]
    assert done.returncode == 2 and cron.audit_log()[-1]["exit"] == 2


def test_only_the_fresh_set_is_due(cron):
    cron.plan({"due": {"lines": ["DUE no"], "exit": 1}, "run": {"lines": [], "exit": 3}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert cron.keys() == ["standing live", "due", "due --fresh", "maintain", "run", "push"] and done.returncode == 3


def test_a_failing_due_is_logged_and_stops_with_its_code(cron):
    cron.plan({"due --fresh": {"lines": [], "exit": 4}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 4 and cron.keys() == ["standing live", "due", "due --fresh"]
    assert (cron.log()[-1]["started"], cron.log()[-1]["exit"]) == (False, 4)


def test_without_a_live_set_it_is_todays_path_due_then_run(cron):
    cron.plan({"standing live": {"lines": [f"KEY {KEY}", "LIVE none"], "exit": 1}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 0 and cron.keys() == ["standing live", "due", "run"]
    assert cron.log()[-1]["started"] is True  # the log is the key folder's, from the KEY line
    cron.plan({"due": {"lines": ["MODE weekly", "DUE no", "REASON x"], "exit": 1}})
    cron.wrapper("--repo", str(cron.repo))
    assert cron.keys()[-2:] == ["standing live", "due"]
    assert cron.log()[-1]["started"] is False


def test_when_standing_live_names_no_key_the_log_is_the_machines_old_place(cron):
    cron.plan({"standing live": {"lines": [], "exit": 4}})
    cron.wrapper("--repo", str(cron.repo))
    assert cron.keys() == ["standing live", "due", "run"]
    assert cron.log(None)[-1]["started"] is True


def test_the_repository_defaults_to_the_current_directorys_top_level(cron):
    sub = cron.repo / "docs"
    sub.mkdir()
    cron.wrapper(cwd=sub)
    assert Path(cron.calls()[0]["cwd"]).resolve() == cron.repo.resolve()
    assert cron.calls()[0]["argv"][-2:] == ["--repo", str(cron.repo.resolve())] or "--repo" in cron.calls()[0]["argv"]


def test_the_wrapper_names_no_cron_table_and_its_syntax_holds():
    text = WRAPPER.read_text()
    assert "crontab" not in text
    assert subprocess.run(["bash", "-n", str(WRAPPER)]).returncode == 0


# ---- S12: the weekly scan and push is the last step

def test_the_push_is_the_last_step_its_line_is_logged_with_the_step_push_and_the_six_keys(cron):
    cron.plan({"push": {"lines": ["PUSH pushed origin main 0123456789ab"], "exit": 0}})
    done = cron.wrapper("--repo", str(cron.repo), push="origin main")
    assert done.returncode == 0 and cron.keys()[-2:] == ["run", "push"]
    argv = cron.calls()[-1]["argv"]
    assert argv[argv.index("--repo") + 1] == str(cron.repo) and argv[argv.index("--sets-root") + 1] == str(cron.sets)
    assert done.stdout.splitlines()[-1] == "PUSH pushed origin main 0123456789ab"
    audit, row = cron.log()[-2:]
    assert set(row) == {"at", "due", "mode", "reason", "started", "exit"} == set(audit)
    assert (row["mode"], row["reason"], row["started"], row["exit"]) == ("push", "pushed origin main 0123456789ab", True, 0)
    assert audit["mode"] == "weekly"  # the audit's own line is as it was


@pytest.mark.parametrize("line, code, started", [("PUSH blocked: findings 2", 1, True),
                                                  ("PUSH blocked: scan failed timeout", 1, True),
                                                  ("PUSH failed: git push exit 128", 2, True)])
def test_a_blocked_or_failed_push_is_named_by_reason_only_and_never_changes_the_wrappers_exit(cron, line, code, started):
    cron.plan({"push": {"lines": [line], "exit": code}, "run": {"lines": [], "exit": 0}})
    done = cron.wrapper("--repo", str(cron.repo), push="origin main")
    assert done.returncode == 0  # the exit stays the audit steps'
    row = cron.log()[-1]
    assert (row["mode"], row["reason"], row["started"], row["exit"]) == ("push", line.removeprefix("PUSH "), started, code)


def test_no_declaration_is_said_on_the_output_and_adds_no_log_line(cron):
    cron.plan({"push": {"lines": ["PUSH none: no declaration"], "exit": 0}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 0 and done.stdout.splitlines()[-1] == "PUSH none: no declaration"
    assert [x["mode"] for x in cron.log()] == ["weekly"]  # the cycle's one line, as before


def test_the_push_follows_the_audit_steps_that_ran_whatever_exit_they_gave(cron):
    cron.plan({"due --fresh": {"lines": ["DUE no"], "exit": 1}, "standing run": {"lines": ["x"], "exit": 2}})
    done = cron.wrapper("--repo", str(cron.repo))
    assert done.returncode == 2 and cron.keys()[-2:] == ["standing run", "push"]


def test_a_cycle_where_nothing_is_due_or_due_fails_runs_no_push(cron):
    cron.plan({"due": {"lines": ["DUE no"], "exit": 1}, "due --fresh": {"lines": ["DUE no"], "exit": 1}})
    cron.wrapper("--repo", str(cron.repo), push="origin main")
    assert "push" not in cron.keys() and [x["mode"] for x in cron.log()] == [""]
    cron.plan({"due": {"lines": [], "exit": 4}})
    cron.wrapper("--repo", str(cron.repo), push="origin main")
    assert "push" not in cron.keys()


def test_maintain_alone_never_runs_the_push(cron):
    assert WRAPPER.read_text().count("gov.memaudit push") == 1  # one call, in the step the cycle's ends run
    cron.wrapper("--repo", str(cron.repo))
    assert cron.keys().index("push") > max(i for i, k in enumerate(cron.keys()) if k in ("maintain", "standing run", "run"))


def test_todays_path_runs_the_push_only_when_the_cron_line_declares_it(cron):
    cron.plan({"standing live": {"lines": [f"KEY {KEY}", "LIVE none"], "exit": 1}})
    cron.wrapper("--repo", str(cron.repo))
    assert cron.keys() == ["standing live", "due", "run"] and len(cron.log()) == 1  # byte for byte as before
    cron.wrapper("--repo", str(cron.repo), push="origin main")
    assert cron.keys()[-3:] == ["due", "run", "push"] and cron.log()[-1]["mode"] == "push"
