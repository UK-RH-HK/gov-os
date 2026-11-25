"""W2-208 fix P0-3 (plan item 0-3; DAEO-kt8e "Fix: the kit carries the git hook; adopt, adapters and update install it").

Three groups: the kit's file (its text); the installers (`gov adopt`'s path, `gov adapters generate`, `gov update <B>`
write ``.git/hooks/reference-transaction``, executable and byte-equal, and the update record lists it); the hook at work
(a commit on the integration branch named in ``integration_refresh.branch`` refreshes the store in the background, a
failure leaves one inbox message, a ``.local`` file runs too, the hook never fails git). README: "P0-3".
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

import w2_208_p0_support as p0
import w2_208_support as support
from w2_116_support import Embedder


# --- the kit's file ----------------------------------------------------------------------------------------------------

def test_p0_3_the_kit_file_is_a_posix_sh_script_with_no_freeze_line_and_no_w2_integrate():
    text = p0.kit_bytes().decode("utf-8")
    assert re.match(r"#!\s*/(usr/)?bin/(env )?sh\b", text), f"the kit's hook does not start with a POSIX sh line: {text[:40]!r}"
    done = subprocess.run(["sh", "-n", str(p0.KIT_HOOK)], capture_output=True, text=True)
    assert done.returncode == 0, f"the kit's hook is not valid POSIX sh: {done.stderr}"
    assert "committed" in text, "the kit's hook does not act on the state `committed`"
    assert "act-in-progress" not in text, "the kit's hook still holds the operator's act-in-progress freeze line"
    assert not re.search(r"freeze", text, re.I), "the kit's hook still holds a freeze line"
    assert "w2/integrate" not in text, "the kit's hook names w2/integrate: the branch is read from configuration"
    assert "integration_refresh" in text or "rebuild.yaml" in text, (
        "the kit's hook does not read the integration branch from governance/project/rebuild.yaml")


# --- the installers ----------------------------------------------------------------------------------------------------

def test_p0_3_a_project_adopted_from_the_kit_holds_the_hook_equal_to_the_kits_file(adopted_at_b):
    p0.assert_installed(adopted_at_b, "the project adopted (copier copy, then `gov adapters generate`)")


def test_p0_3_gov_adapters_generate_writes_the_hook_back_when_it_is_gone(adopted_at_b, tmp_path):
    project = support.w217.w216.clone_folder(adopted_at_b, tmp_path / "product")
    sandbox = support.sandbox_at(tmp_path / "sandbox")
    hook = p0.installed(project)
    if hook.exists():
        hook.unlink()
    done = support.generate(project, sandbox)
    assert done.returncode == 0, f"`gov adapters generate` failed\n{done.describe()}"
    p0.assert_installed(project, "after `gov adapters generate`")


def _built(make):
    try:
        return make()
    except AssertionError as exc:
        message = f"W2-208 fixture could not be built (not the feature under test): {exc}"
    pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def updated_without_the_hook(examin_013, tmp_path_factory):
    """A copy of the project adopted at A1, its hook deleted, ``gov update B --json`` run in it."""
    def build(folder):
        project = support.w217.w216.clone_folder(examin_013, folder / "product")
        sandbox = support.sandbox_at(folder / "sandbox")
        hook = p0.installed(project)
        if hook.exists():
            hook.unlink()
        done = support.update(project, sandbox)
        return {"project": str(project), "run": support.run_to_json(done)}
    data = _built(lambda: support.shared(tmp_path_factory, "p0-3-updated-without-hook", build))
    return Path(data["project"]), support.run_from_json(data["run"])


def test_p0_3_gov_update_writes_the_hook_back_when_it_is_gone(updated_without_the_hook):
    project, run = updated_without_the_hook
    assert run.returncode == 0, f"premise: `gov update B` did not succeed\n{run.describe()}"
    p0.assert_installed(project, "after `gov update B` with the hook deleted")


def test_p0_3_the_update_record_lists_the_hook(updated_without_the_hook):
    project, run = updated_without_the_hook
    assert run.returncode == 0, f"premise: `gov update B` did not succeed\n{run.describe()}"
    path = Path(project) / f"governance/updates/{support.B}.json"
    assert path.is_file(), f"no update record {path.relative_to(project)}"
    record = json.loads(path.read_text(encoding="utf-8"))
    assert p0.HOOK_REL in json.dumps(record), f"the update record does not list {p0.HOOK_REL}: {json.dumps(record)[:1500]}"


# --- the hook at work --------------------------------------------------------------------------------------------------

@pytest.fixture
def embedder():
    stand_in = Embedder()
    yield stand_in
    stand_in.close()


@pytest.fixture
def questions():
    stand_in = Embedder()
    yield stand_in
    stand_in.close()


@pytest.fixture(params=["trunk", "main"])
def rig(request, tmp_path, embedder, questions):
    return p0.make_rig(tmp_path, request.param, embedder, questions)


def test_p0_3_a_commit_on_the_integration_branch_refreshes_the_store_in_the_background(rig):
    p0.install_kit_hook(rig)
    p0.build_store(rig)
    old = rig.head()
    rig.embedder.hold()                  # the refresh the hook starts cannot finish until the case lets it
    code, seconds = p0.git_commit(rig, "p0-fresh.md")
    assert code == 0, "the hook failed the commit"
    assert seconds < p0.QUICK_S, f"the commit waited {seconds:.0f} s: the hook did not refresh in the background"
    new = rig.head()
    assert new != old
    assert rig.embedder.asked.wait(60), "the hook started no refresh after a commit on the integration branch"
    assert rig.store_head() == old, "the store moved before its build finished"
    rig.embedder.release()
    assert p0.wait_for(lambda: rig.store_head() == new), (
        f"the store's commit is not the head {new[:12]} within {p0.WAIT_S:.0f} s\nlog:\n{rig.log_text()[-1500:]}")
    assert new[:12] in rig.log_text(), f"no log line at {p0.LOG_REL} names {new[:12]}\nlog:\n{rig.log_text()[-1500:]}"


def test_p0_3_a_commit_on_another_branch_refreshes_nothing(rig):
    p0.install_kit_hook(rig)
    for other in ("feature", "w2/integrate"):
        code, _ = p0.git_commit(rig, f"p0-{other.replace('/', '-')}.md", on=other)
        assert code == 0
        assert p0.stays_false(lambda: not p0.no_store_built(rig) or rig.embedder.requests > 0), (
            f"a commit on {other!r} (the integration branch is {rig.branch!r}) started a refresh\n{rig.log_text()[-800:]}")


def test_p0_3_only_the_state_committed_refreshes(rig):
    p0.install_kit_hook(rig)
    for state in ("prepared", "aborted"):
        assert p0.run_hook(rig, state, p0.ref_line(rig.branch)) == 0
    assert p0.stays_false(lambda: not p0.no_store_built(rig) or rig.embedder.requests > 0), (
        f"a state other than `committed` started a refresh\n{rig.log_text()[-800:]}")
    # no store and no record: the clock decides, so plant it past `latest` (10:00) and before `second` (18:00)
    noon = {**rig.child_env(), "GOV_NOW": p0.s2.at(p0.s2.DAY1, "12:00").isoformat()}
    assert p0.run_hook(rig, "committed", p0.ref_line(rig.branch), env=noon) == 0
    assert p0.wait_for(lambda: rig.store_head() == rig.head()), (
        f"the state `committed` on {rig.branch!r} refreshed nothing\nlog:\n{rig.log_text()[-800:]}")


def test_p0_3_a_planted_refresh_failure_leaves_exactly_one_inbox_message_across_its_retries(rig):
    p0.install_kit_hook(rig)
    p0.build_store(rig)
    broken = {"OLLAMA_HOST": p0.s116.closed_host()}
    code, _ = p0.git_commit(rig, "p0-fails.md", env=broken)
    assert code == 0, "the hook failed the commit"
    assert p0.wait_for(lambda: len(rig.messages()) >= 1), (
        f"a failed refresh left no message in the inbox ({rig.inbox}) within {p0.WAIT_S:.0f} s\nlog:\n{rig.log_text()[-1500:]}")
    assert "REBUILD_FAILED" in rig.log_text(), f"the log holds no REBUILD_FAILED\n{rig.log_text()[-1500:]}"
    assert p0.stays_false(lambda: len(rig.messages()) > 1, seconds=8), f"more than one message: {rig.messages()}"
    (address, message), = rig.messages()
    assert address == p0.CTO, f"the message is in the inbox of {address!r}, not of the CTO's address {p0.CTO!r}"
    assert message.get("kind") == "notice", f"the message's kind is {message.get('kind')!r}, not notice"
    # the fault removed, the next commit refreshes (a retry of the same work) and adds no message
    code, _ = p0.git_commit(rig, "p0-recovers.md")
    assert code == 0
    new = rig.head()
    assert p0.wait_for(lambda: rig.store_head() == new), f"the store did not reach {new[:12]}\n{rig.log_text()[-1500:]}"
    assert len(rig.messages()) == 1, f"a retry that succeeded added messages: {rig.messages()}"


def test_p0_3_a_local_hook_file_runs_with_the_same_arguments_and_stdin(rig):
    p0.install_kit_hook(rig)
    marker = rig.box.base / "local-marker"
    local = rig.project / p0.LOCAL_REL
    local.write_text(f"#!/bin/sh\nprintf '%s' \"$*\" > '{marker}.args'\ncat > '{marker}.stdin'\nexit 0\n", encoding="utf-8")
    local.chmod(0o755)
    lines = p0.ref_line("some-other-branch") + p0.ref_line("and-another", old="2" * 40, new="3" * 40)
    assert p0.run_hook(rig, "prepared", lines) == 0
    assert (Path(f"{marker}.args")).is_file(), "the hook did not run reference-transaction.local"
    assert Path(f"{marker}.args").read_text(encoding="utf-8") == "prepared", "the local file got other arguments"
    assert Path(f"{marker}.stdin").read_text(encoding="utf-8") == lines, "the local file got other stdin"


def test_p0_3_the_hook_never_fails_the_git_operation(rig):
    p0.install_kit_hook(rig)
    local = rig.project / p0.LOCAL_REL
    local.write_text("#!/bin/sh\nexit 7\n", encoding="utf-8")
    local.chmod(0o755)
    assert p0.run_hook(rig, "committed", p0.ref_line("other")) == 0, "a failing local file made the hook fail"
    local.unlink()
    bare = {"PATH": "/usr/bin:/bin", "HOME": str(rig.box.base / "empty-home")}
    os.makedirs(bare["HOME"], exist_ok=True)
    assert p0.run_hook(rig, "committed", p0.ref_line(rig.branch), env=bare) == 0, (
        "with no gov to run, the hook failed the git operation")
