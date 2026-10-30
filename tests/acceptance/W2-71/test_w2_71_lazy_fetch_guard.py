"""Run 2 (DEC-911 item 4, KPI 4; the orchestrator's decision P1-MORNING-2026-10-29 items 2 and 3).

**The control (item 3, unchanged behaviour):** in a full clone, over ``file://``, of a bare source built from scratch,
with its ordinary remote (no promisor, no filter, no extension), a commit of the clone's own history after the rule's
keyword is still no finding of the check and still passes the filter, and nothing is fetched. A control has the test
itself run ``git fetch origin``: the counter sees it, so the zero during the runs means something. Guards, green today.

**The second guard (item 2):** every git process the check or the filter starts to look up objects runs with
``GIT_NO_LAZY_FETCH`` set to true in its environment. A recording ``git`` first on ``PATH`` records each call's
arguments, whether a 40-hex string stood in its arguments or its standard input, and that variable, then runs the real
git unchanged. In a full clone where the exemption holds, at least one call is recorded, at least one of them looks
up objects, and every call that looks up objects carries the variable. Which calls look up objects is
``w2_71_support.looks_up_objects`` (README): ``git config`` never; any other call when a candidate stands in its
arguments or input, or when it is one of git's object readers. Red on run 1's code: its lookups do not carry it.

Note: the git of this machine (2.43.0 as packaged here) honours ``GIT_NO_LAZY_FETCH`` (measured: "lazy fetching
disabled", no request); the decision's item 1, not this guard, is what the partial-clone cases test.
"""

from __future__ import annotations

import os
import re
import subprocess

import pytest

import w2_71_support as support

pytestmark = [support.needs_gitleaks, support.needs_git, pytest.mark.local_only]

KEYWORD_CASES = {"vendor-keyword": support.VENDOR, "prefix-keyword": support.PREFIX}


def _quote_own_commit(root, head):
    check_rels, filter_rels = {}, {}
    for name, keyword in KEYWORD_CASES.items():
        line = support.vendor_line(keyword, head)
        check_rels[name] = f".gov-runtime/scratch/own-commit-{name}.log"
        support.write(root / check_rels[name], "a lead's review log\n" + line)
        filter_rels[name] = f"docs/own-commit-{name}.md"
        support.write(root / filter_rels[name], "# A review\n\n" + line)
    return check_rels, filter_rels


# ---- the control: a full clone with its ordinary remote --------------------------------------------------------------

class Control:
    def __init__(self, sandbox):
        self.clone = support.make_clone(sandbox, "full-clone", label="full")
        root = self.clone.root
        self.old_blob = support.git(self.clone.seed.root, "rev-parse", f"{self.clone.seed.first}:src/notes.txt").strip()
        self.check_rels, self.filter_rels = _quote_own_commit(root, self.clone.head)
        self.random_check_rel, self.random_filter_rel = ".gov-runtime/scratch/random.log", "docs/random.md"
        random_line = support.vendor_line(support.VENDOR, support.hex_of("run-2-full-clone-random"))
        support.write(root / self.random_check_rel, "a lead's review log\n" + random_line)
        support.write(root / self.random_filter_rel, "# A review\n\n" + random_line)
        env = support.base_environment(sandbox)
        self.config_code, self.config = support.config_list(root, env)
        self.objects_before = support.local_objects(root)
        before = self.clone.request_count()
        self.check = support.run_check(sandbox, root, env=env)
        after_check = self.clone.request_count()
        self.filter = support.run_filter(sandbox, root, sorted([*self.filter_rels.values(), self.random_filter_rel]),
                                         env=env)
        after_filter = self.clone.request_count()
        self.check_requests, self.filter_requests = after_check - before, after_filter - after_check
        self.objects_after = support.local_objects(root)
        # the control: the test's own fetch from the remote goes through the counter
        support.git(root, "fetch", "-q", "origin")
        self.control_requests = self.clone.request_count() - after_filter


@pytest.fixture(scope="module")
def control(module_sandbox):
    return Control(module_sandbox)


def test_premise_the_control_clone_is_a_full_clone_with_an_ordinary_remote(control):
    lines = control.config
    partial_keys = [line.split("=", 1)[0] for line in lines
                    if line.split("=", 1)[0] in ("extensions.partialclone", "remote.origin.promisor",
                                                 "remote.origin.partialclonefilter")]
    remote = any(line.startswith("remote.origin.url=file://") for line in lines)
    full = control.old_blob in control.objects_before and control.clone.head in control.objects_before
    assert control.config_code == 0 and not partial_keys and remote and full, (
        f"the control clone: partial-clone keys {partial_keys}; a file:// remote: {remote}; every object held: {full}")


def test_premise_the_counter_sees_a_fetch_in_the_full_clone(control):
    assert control.control_requests >= 1, (f"the test's own fetch reached the remote {control.control_requests} "
                                           "times: the counter does not count")


@pytest.mark.parametrize("name", list(KEYWORD_CASES))
def test_in_a_full_clone_a_commit_of_its_own_history_is_still_no_finding_of_the_check(control, name):
    rel = control.check_rels[name]
    assert control.check.ended, f"the check did not end\n{control.check.describe()}"
    named, random_named = control.check.names(rel), control.check.names(control.random_check_rel)
    assert random_named, f"the check does not name the random id's file: it did not judge\n{control.check.describe()}"
    assert not named, (f"in a full clone with an ordinary remote the check reports {rel} (a commit of its own history "
                       f"after the rule's keyword) as a finding\n{control.check.describe()}")


@pytest.mark.parametrize("name", list(KEYWORD_CASES))
def test_in_a_full_clone_a_commit_of_its_own_history_still_passes_the_filter(control, name):
    rel = control.filter_rels[name]
    assert not control.filter.passes(control.random_filter_rel), (
        f"the filter lets the random id's page through\n{control.filter.describe()}")
    assert control.filter.passes(rel), (f"in a full clone with an ordinary remote the filter leaves out {rel}\n"
                                        f"{control.filter.describe()}")


def test_in_a_full_clone_the_check_fetches_nothing(control):
    assert control.check_requests == 0, f"the check's run reached the remote {control.check_requests} times"


def test_in_a_full_clone_the_filter_fetches_nothing(control):
    added = len(control.objects_after - control.objects_before)
    assert control.filter_requests == 0 and added == 0, (
        f"the filter's run reached the remote {control.filter_requests} times; objects added by the runs: {added}")


# ---- the second guard: object lookups carry GIT_NO_LAZY_FETCH --------------------------------------------------------

def test_premise_the_recording_git_records_as_said(sandbox):
    repo = support.make_repo(sandbox, "recorder-self-test", label="recorder")
    folder, log = support.recording_git(sandbox, "recorder-self-test-git")
    git = str(folder / "git")
    plain = support.base_environment(sandbox)
    off = dict(plain, **{support.NO_LAZY_FETCH: "1"})
    runs = [
        subprocess.run([git, "-C", str(repo.root), "cat-file", "-e", f"{repo.head}^{{commit}}"], env=off,
                       capture_output=True, text=True, timeout=60),
        subprocess.run([git, "-C", str(repo.root), "config", "--list"], env=plain, capture_output=True, text=True,
                       timeout=60),
        subprocess.run([git, "-C", str(repo.root), "cat-file", "--batch-check"], env=plain, input=repo.head + "\n",
                       capture_output=True, text=True, timeout=60),
        subprocess.run([git, "-C", str(repo.root), "rev-parse", "--git-dir"], env=plain, capture_output=True,
                       text=True, timeout=60),
    ]
    answered = [run.returncode == 0 for run in runs] + ["commit" in runs[2].stdout, bool(runs[1].stdout.strip())]
    calls = support.read_git_calls(log)
    lookups = [support.looks_up_objects(call) for call in calls]
    carried = [support.carries_no_lazy_fetch(call) for call in calls]
    masked = re.search(r"[0-9a-fA-F]{40}", log.read_text(encoding="utf-8")) is None
    ok = (all(answered) and len(calls) == 4 and lookups == [True, False, True, False]
          and carried == [True, False, False, False] and masked)
    assert ok, (f"the recording git: answered {answered}; {len(calls)} calls; lookups {lookups}; carried {carried}; "
                f"its log holds no whole hash: {masked}")


class Guard:
    """A full clone where the exemption holds; the check and the filter run each through a recording git."""

    def __init__(self, sandbox):
        self.clone = support.make_clone(sandbox, "guard-clone", label="guard")
        root = self.clone.root
        self.check_rels, self.filter_rels = _quote_own_commit(root, self.clone.head)
        env = support.base_environment(sandbox)
        check_git, self.check_log = support.recording_git(sandbox, "guard-recording-git-check")
        filter_git, self.filter_log = support.recording_git(sandbox, "guard-recording-git-filter")
        self.check = support.run_check(sandbox, root, env=support.base_environment(
            sandbox, path=f"{check_git}{os.pathsep}{env['PATH']}"))
        self.filter = support.run_filter(sandbox, root, sorted(self.filter_rels.values()), env=support.base_environment(
            sandbox, path=f"{filter_git}{os.pathsep}{env['PATH']}"))


@pytest.fixture(scope="module")
def guard(module_sandbox):
    return Guard(module_sandbox)


def test_through_the_recording_git_the_check_still_exempts_the_commit(guard):
    named = [rel for rel in guard.check_rels.values() if guard.check.names(rel)]
    assert guard.check.returncode == 0 and not named, (f"through the recording git the check names {named}\n"
                                                       f"{guard.check.describe()}")


def test_through_the_recording_git_the_filter_still_passes_the_commit(guard):
    left_out = [rel for rel in guard.filter_rels.values() if not guard.filter.passes(rel)]
    assert not left_out, f"through the recording git the filter leaves out {left_out}\n{guard.filter.describe()}"


def _judge(calls, who):
    lookups = [call for call in calls if support.looks_up_objects(call)]
    bare = sorted(support.git_subcommand(call.get("args", [])) for call in lookups
                  if not support.carries_no_lazy_fetch(call))
    ok = bool(calls) and bool(lookups) and not bare
    return ok, (f"{who}: {len(calls)} git calls recorded, {len(lookups)} look up objects, "
                f"{len(bare)} of them without {support.NO_LAZY_FETCH} set to true: {bare}")


def test_every_git_call_of_the_check_that_looks_up_objects_carries_git_no_lazy_fetch(guard):
    assert guard.check.ended, f"the check did not end\n{guard.check.describe()}"
    ok, message = _judge(support.read_git_calls(guard.check_log), "the check")
    assert ok, message


def test_every_git_call_of_the_filter_that_looks_up_objects_carries_git_no_lazy_fetch(guard):
    assert guard.filter.ended, f"the filter did not end\n{guard.filter.describe()}"
    ok, message = _judge(support.read_git_calls(guard.filter_log), "the filter")
    assert ok, message
