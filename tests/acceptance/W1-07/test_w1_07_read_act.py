"""KPI success 2 [CAP-27.a] and failure 1: read commands never mutate; no command writes outside its act paths.

The read/act class has no public surface in this ticket (DEC-187), so it is
tested by behaviour: what a command leaves behind in the project, in git and
outside the project.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

import w1_07_support as support

DEV_TIERS = Path(os.environ.get("GOV_DEV_TIERS", "~/gov-os-workbench/synthetic")).expanduser()
DEV_TIER = "a-dev"


def _state(project, sandbox):
    return {
        "porcelain": support.porcelain(project),
        "git": support.git_state(project),
        "tree": support.snapshot(project),
        "home": support.snapshot(sandbox.home, skip=()),
        "elsewhere": support.snapshot(sandbox.elsewhere, skip=()),
    }


def _assert_unchanged(before, after, run):
    assert after["porcelain"] == before["porcelain"], \
        f"git status --porcelain changed:\n{after['porcelain']}\n{run.describe()}"
    assert after["git"] == before["git"], f"HEAD or a ref moved\n{run.describe()}"
    changed = support.snapshot_difference(before["tree"], after["tree"])
    assert not changed, f"files changed in the project: {changed}\n{run.describe()}"
    for place in ("home", "elsewhere"):
        changed = support.snapshot_difference(before[place], after[place])
        assert not changed, f"files changed outside the project ({place}): {changed}\n{run.describe()}"


@pytest.mark.parametrize("args", support.READ_COMMANDS, ids=support.label)
@pytest.mark.parametrize("json_flag", [("--json",), ()], ids=["json", "plain"])
def test_a_read_command_leaves_git_status_empty(gov, project, interface, args, json_flag):
    """CAP-27's acceptance line, command by command."""
    assert support.porcelain(project) == "", "the fixture project is not clean"
    run = gov(*args, *json_flag)
    assert run.returncode in interface.exit_codes, run.describe()
    assert support.porcelain(project) == "", \
        f"gov {support.label(args)} left changes:\n{support.porcelain(project)}\n{run.describe()}"


@pytest.mark.parametrize("args", support.READ_COMMANDS, ids=support.label)
def test_a_read_command_changes_no_file_and_no_ref(gov, project, sandbox, interface, args):
    before = _state(project, sandbox)
    run = gov(*args, "--json")
    assert run.returncode in interface.exit_codes, run.describe()
    _assert_unchanged(before, _state(project, sandbox), run)


@pytest.mark.parametrize("args", support.READ_COMMANDS, ids=support.label)
def test_a_read_command_leaves_uncommitted_work_as_it_was(gov, project, sandbox, interface, args):
    (project / "README.md").write_text("changed, not committed\n", encoding="utf-8")
    (project / "untracked-note.txt").write_text("untracked\n", encoding="utf-8")
    before = _state(project, sandbox)
    assert before["porcelain"] != ""
    run = gov(*args, "--json")
    assert run.returncode in interface.exit_codes, run.describe()
    _assert_unchanged(before, _state(project, sandbox), run)


def test_a_read_command_with_root_writes_neither_in_the_project_nor_where_it_runs(gov, project, sandbox, interface):
    before = _state(project, sandbox)
    run = gov("status", "--json", "--root", str(project), cwd=sandbox.elsewhere)
    assert run.returncode in interface.exit_codes, run.describe()
    _assert_unchanged(before, _state(project, sandbox), run)


@pytest.mark.parametrize("args", support.EVERY_INVOCATION + (("--help",),), ids=support.label)
def test_no_command_writes_outside_its_act_paths(request, sandbox, interface, args):
    """Failure 1. No command built at W1-07 declares an act path, and a command not yet built does nothing."""
    # Revised after implementation: W1-27's rebuild recreates the lexical index through its owner
    # and its secrets filter (DEC-440); the size of the copied tree, not the behaviour, made the
    # case time out.
    if args[0] in support.TREE_SENSITIVE_COMMANDS:
        gov = request.getfixturevalue("small_gov")
        project = request.getfixturevalue("small_project")
    else:
        gov = request.getfixturevalue("gov")
        project = request.getfixturevalue("project")
    before = _state(project, sandbox)
    run = gov(*args) if args == ("--help",) else gov(*args, "--json")
    assert run.returncode in interface.exit_codes, run.describe()
    after = _state(project, sandbox)
    assert after["porcelain"] == before["porcelain"], \
        f"git status --porcelain changed:\n{after['porcelain']}\n{run.describe()}"
    assert after["git"] == before["git"], f"HEAD or a ref moved\n{run.describe()}"
    changed = support.snapshot_difference(before["tree"], after["tree"])
    assert not changed, f"files changed in the project: {changed}\n{run.describe()}"
    changed = support.snapshot_difference(before["elsewhere"], after["elsewhere"])
    assert not changed, f"files changed outside the project (elsewhere): {changed}\n{run.describe()}"
    # DEC-429: gov pause writes a freeze mirror under ~/.local/state/gov-os/<key>/freeze.
    home_changed = support.snapshot_difference(before["home"], after["home"])
    if args[0] == "pause":
        non_mirror = [d for d in home_changed if not support.is_freeze_mirror_entry(d)]
        assert not non_mirror, \
            f"gov pause wrote to home outside .local/state/gov-os/: {non_mirror}\n{run.describe()}"
        assert any("/freeze" in d for d in home_changed), \
            f"gov pause did not create the freeze mirror (DEC-429)\n{run.describe()}"
    else:
        assert not home_changed, \
            f"files changed outside the project (home): {home_changed}\n{run.describe()}"


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
def test_a_command_refused_for_invalid_configuration_writes_nothing(gov, project, sandbox, args):
    path_map = project / support.PATH_MAP_REL
    path_map.parent.mkdir(parents=True, exist_ok=True)
    path_map.write_text("- a list\n- not a map\n", encoding="utf-8")
    support.commit_all(project, "an invalid path-map")
    before = _state(project, sandbox)
    run = gov(*args, "--json")
    _assert_unchanged(before, _state(project, sandbox), run)


@pytest.mark.local_only
@pytest.mark.parametrize("args", support.READ_COMMANDS, ids=support.label)
def test_a_read_command_leaves_a_dev_tier_clone_clean(cli, sandbox, tmp_path, interface, args):
    """The same on a project that is not the Gov OS: a clone of a dev tier, never the tier itself."""
    tier = DEV_TIERS / DEV_TIER
    if not (tier / ".git").exists():
        pytest.skip(f"no dev tier at {tier} (GOV_DEV_TIERS)")
    clone = tmp_path / "tier"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(tier), str(clone)], check=True, capture_output=True)
    before = _state(clone, sandbox)
    run = support.run_gov_with_code(cli, clone, sandbox, *args, "--json")
    assert run.returncode in interface.exit_codes, run.describe()
    after = _state(clone, sandbox)
    assert after["porcelain"] == before["porcelain"] == "", \
        f"git status --porcelain is not empty:\n{after['porcelain']}\n{run.describe()}"
    _assert_unchanged(before, after, run)
