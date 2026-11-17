"""Builder tests for the decisions of batch 4 (DEC-311, DEC-313).

Regression evidence only (DEC-136): the forms the acceptance tests leave to the builder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard.decide import _UNRESOLVABLE, _extract_bash_write_targets  # noqa: E402
from gov.launch import launcher  # noqa: E402


# -- DEC-313 ---------------------------------------------------------------
# Emergency 2 (0.1.2): the bypass, the added directory and the repository settings keys no longer refuse.

@pytest.mark.parametrize("args", (["--permission-mode", "acceptEdits"], ["--permission-mode=plan"],
                                  ["-p", "no --add-dir and no --permission-mode bypassPermissions"]))
def test_a_harmless_mode_and_a_prompt_pass(args):
    launcher._check_cli_args(args)


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
