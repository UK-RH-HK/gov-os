"""S6: nothing project-specific in the code; planted tests for the refusals the line names.

The refusals S6 names, and where each is planted (the full node ids are in README.md):
an uncommitted claim (test_s2_start_rules.py), a shut gate (test_s2_start_rules.py), no room for a peak
(test_s3_peaks.py), a running ticket, an unread return, a malformed list line (test_s2_start_rules.py), a hung command
and a crash after a launch (this file). The review record and the switch-over of this repository's dispatcher are the
CTO's, at the last close: not tested here.

Readings fixed by the brief: a missing or malformed value the pass needs is a configuration error: exit 2, the key
named; no default may name this repository's branches, paths or ticket ids; every external command, git included, is
limited to ``command_timeout_s``, and a timeout is a failed check naming the command, never a hung pass; the log name
is in ``started.txt`` before the launch command is spawned, so a pass killed after the launch never starts that log
again. A hung ``git`` is a stub ``git`` first on the child's ``PATH`` (the brief's form): the dispatcher runs git by
its name.
"""

from __future__ import annotations

import re

import pytest

import w2_121_support as support
from w2_121_support import TREE, explain, wait_for

DISPATCH = TREE / "src" / "gov" / "dispatch"
FORBIDDEN_TEXT = ("w2/integrate", "w2/W2-", "/home/usain", "gov-os-worktrees", "Dynamic-Agentic-Engineering-OS",
                  ".gov-runtime/scratch/orchestrator")
FORBIDDEN_PATTERNS = (r"DAEO-[0-9a-z]{4}", r"W2-[0-9]+")
TIMED_OUT = r"(?i)time[ds]?[- ]?out|timed out"


def test_s6_the_dispatcher_code_names_none_of_this_repositorys_branches_paths_or_ticket_ids():
    assert DISPATCH.is_dir(), f"{DISPATCH} does not exist: the dispatcher is not built"
    files = [f for f in sorted(DISPATCH.rglob("*")) if f.is_file() and "__pycache__" not in f.parts]
    assert any(f.name == "command.py" for f in files), "src/gov/dispatch/command.py does not exist"
    hits = []
    for file in files:
        for number, line in enumerate(file.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if any(word in line for word in FORBIDDEN_TEXT) or any(re.search(pat, line) for pat in FORBIDDEN_PATTERNS):
                hits.append(f"{file.relative_to(TREE)}:{number}: {line.strip()}")
    assert not hits, f"{len(hits)} line(s) of the dispatcher code name this repository:\n" + "\n".join(hits[:20])


@pytest.mark.parametrize("key", ["integration_branch", "max_leads", "stagger_s", "cpu_band"])
def test_s6_a_missing_configuration_value_is_exit_2_and_names_the_key(project, key):
    p = project
    entry = p.add_ticket(901)
    p.cfg_drop(key)
    p.ready(entry)
    r = p.tick()
    assert r.code == 2, r
    assert key in r.out + r.err, f"the configuration error does not name {key}\n{r}"
    p.settle(0.5)
    assert p.launches() == []


@pytest.mark.parametrize("key, value", [("max_leads", "many"), ("stagger_s", -5), ("cpu_band", "wide"),
                                        ("launch_command", "gov launch lead"), ("notifier_command", "notify-send")])
def test_s6_a_malformed_configuration_value_is_exit_2_and_names_the_key(project, key, value):
    p = project
    entry = p.add_ticket(901)
    p.cfg(**{key: value})
    p.ready(entry)
    r = p.tick()
    assert r.code == 2, r
    assert key in r.out + r.err, f"the configuration error does not name {key}\n{r}"
    p.settle(0.5)
    assert p.launches() == []


def test_s6_no_dispatch_yaml_is_a_configuration_error(project):
    p = project
    p.ready(p.add_ticket(901))
    p.raw_config = "<absent>"
    r = p.tick()
    assert r.code == 2, r
    assert re.search(r"dispatch\.yaml|integration_branch", r.out + r.err), r
    p.settle(0.5)
    assert p.launches() == []


def test_s6_a_dispatch_yaml_that_is_not_yaml_is_a_configuration_error(project):
    p = project
    p.ready(p.add_ticket(901))
    p.raw_config = "dispatch: [unclosed\n  integration_branch: : :\n"
    r = p.tick()
    assert r.code == 2, r
    assert "dispatch.yaml" in r.out + r.err, r


def test_s6_the_integration_branch_is_the_configured_one_not_a_default(project):
    p = project
    entry = p.add_ticket(901)
    support.git(p.root, "branch", "-m", "integ", "trunk-line")
    p.cfg(integration_branch="trunk-line")
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    assert p.launched_logs() == [entry.log]


def test_s6_a_hung_git_ends_the_pass_in_bounded_time_with_the_check_named_as_failed(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(command_timeout_s=1)
    p.ready(entry)
    p.hung_git()
    r = p.tick(timeout=60)
    assert r.seconds < 40, f"the pass took {r.seconds:.0f}s with every git call hung for 8s and command_timeout_s 1\n{r}"
    p.settle()
    assert p.launches() == [], "a session started although the claim could not be checked"
    status = p.status_text() if (p.state / "status.txt").is_file() else ""
    said = status + r.out + r.err
    assert re.search(TIMED_OUT, said) and "git" in said, f"the hung git is not named as a failed check\n{explain(p, r)}"


def test_s6_a_hung_notifier_ends_the_pass_in_bounded_time_with_the_command_named(project):
    p = project
    entry = p.add_ticket(901)
    p.cfg(unread_escalate_s=1, command_timeout_s=1)
    p.set_exit(0)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.wait_exit_file(entry.log)
    assert p.tick().code == 0  # the item is written
    p.set_notify_sleep(8)
    ran = {}

    def escalated():
        r = p.tick(timeout=60)
        if p.notifies():
            ran["run"] = r
            return True
        return False

    wait_for(escalated, 20, 0.5, "the notifier to be run")
    r = ran["run"]
    assert r.seconds < 40, f"the pass waited for a hung notifier ({r.seconds:.0f}s)\n{r}"
    said = (p.status_text() if (p.state / "status.txt").is_file() else "") + r.out + r.err
    assert re.search(TIMED_OUT, said), f"the hung notifier is not named as a failed check\n{explain(p, r)}"


def test_s6_a_pass_killed_after_the_launch_never_starts_that_log_again(project):
    p = project
    entry = p.add_ticket(901)
    p.set_sleep(4)
    p.ready(entry)
    proc = p.tick_popen()
    p.wait_launches(1)  # the launch command has run
    proc.kill()  # the pass dies before it can write anything more
    proc.wait(timeout=30)
    r = p.tick()
    assert r.code == 0, r
    p.settle(1.5)
    assert p.launched_logs() == [entry.log], f"the log was started again: {p.launched_logs()}"
    assert p.started().count(entry.log) == 1, p.started()
