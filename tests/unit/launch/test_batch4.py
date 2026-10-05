"""Builder tests for the decisions of batch 4 (DEC-311, DEC-313, DEC-315, DEC-316).

Regression evidence only (DEC-136): the forms the acceptance tests leave to the builder.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets  # noqa: E402
from gov.launch import launcher  # noqa: E402


# -- DEC-313 ---------------------------------------------------------------

@pytest.mark.parametrize("args", (
    ["--dangerously-skip-permissions"], ["-p", "x", "--allow-dangerously-skip-permissions"],
    ["--permission-mode", "bypassPermissions", "-p", "x"], ["--permission-mode=bypassPermissions"],
    ["--add-dir", "/x"], ["--add-dir=/x"], ["--add-dir"],
))
def test_a_bypass_or_an_added_directory_refuses(args):
    with pytest.raises(GovError):
        launcher._check_cli_args(args)


@pytest.mark.parametrize("args", (["--permission-mode", "acceptEdits"], ["--permission-mode=plan"],
                                  ["-p", "no --add-dir and no --permission-mode bypassPermissions"]))
def test_a_harmless_mode_and_a_prompt_pass(args):
    launcher._check_cli_args(args)


GUARD = {"hooks": {"PreToolUse": [{"hooks": [{"type": "command", "command": f"python3 {launcher.GUARD_HOOK}"}]}]}}


@pytest.mark.parametrize("permissions, refused", (
    ({"defaultMode": "bypassPermissions"}, True), ({"additionalDirectories": []}, True),
    ({"additionalDirectories": ["/x"]}, True), ("bypassPermissions", True), (None, True),
    ({"defaultMode": "acceptEdits"}, False), ({}, False),
))
@pytest.mark.parametrize("rel", launcher.REPO_SETTINGS)
def test_the_matching_settings_keys_refuse_in_both_files(tmp_path, rel, permissions, refused):
    (tmp_path / ".claude").mkdir()
    (tmp_path / launcher.REPO_SETTINGS[0]).write_text(json.dumps(GUARD), encoding="utf-8")
    data = {**(GUARD if rel == launcher.REPO_SETTINGS[0] else {}), "permissions": permissions}
    (tmp_path / rel).write_text(json.dumps(data), encoding="utf-8")
    if refused:
        with pytest.raises(GovError):
            launcher._check_repository_settings(tmp_path)
    else:
        launcher._check_repository_settings(tmp_path)


# -- DEC-315 ---------------------------------------------------------------

def test_the_three_trees_are_denied_by_a_literal_rule_and_a_pattern(tmp_path):
    rules = launcher._tree_rules(tmp_path, "engineer")
    for tree in ("tests/acceptance", ".tickets", ".claude"):
        assert f"Edit(/{tmp_path}/{tree})" in rules and f"Edit(/{tmp_path}/{tree}/**)" in rules


def test_the_test_designer_has_no_rule_for_the_acceptance_tests(tmp_path):
    rules = launcher._tree_rules(tmp_path, "independent-test-designer")
    assert len(rules) == 4 and not any("tests" in rule[len(str(tmp_path)):] for rule in rules)


# -- DEC-316 ---------------------------------------------------------------

def test_the_dropped_host_is_in_neither_list():
    for rel in (launcher.KERNEL_ALLOWLIST_REL, launcher.PROJECT_ALLOWLIST_REL):
        assert "cdn-lfs.huggingface.co" not in launcher._hosts(REPO, rel)


# -- DEC-311: the destination of ln ------------------------------------------

@pytest.mark.parametrize("command, target", (
    ("ln -s a b", "b"), ("ln a b", "b"), ("ln -sfn a b", "b"), ("ln -s a b dir", "dir"),
    ("ln -s ../elsewhere/a", "a"), ("/bin/ln a b", "b"),
))
def test_the_destination_of_ln_is_a_write_target(tmp_path, command, target):
    # Since DEC-334 the source of a hard link follows the destination.
    assert _extract_bash_write_targets(command, str(tmp_path))[0] == str(tmp_path / target)


@pytest.mark.parametrize("command", (
    "ln -t dir a", "ln -st dir a", "ln --target-directory=dir a", "ln --target-directory dir a", "ln --t=dir a",
    "ln -s a -- b", "ln -s a $NO_SUCH_VARIABLE_W1_46/b",
))
def test_an_ln_form_the_guard_does_not_follow_is_refused(tmp_path, command):
    assert _UNRESOLVABLE in _extract_bash_write_targets(command, str(tmp_path))


def test_ln_with_no_operand_writes_nothing(tmp_path):
    assert _extract_bash_write_targets("ln --help", str(tmp_path)) is None
