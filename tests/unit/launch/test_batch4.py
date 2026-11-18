"""Builder tests for the decisions of batch 4 (DEC-311, DEC-313).

Regression evidence only (DEC-136): the forms the acceptance tests leave to the builder.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.launch import launcher  # noqa: E402


# -- DEC-313 ---------------------------------------------------------------
# Emergency 2 (0.1.2): the bypass, the added directory and the repository settings keys no longer refuse.

@pytest.mark.parametrize("args", (["--permission-mode", "acceptEdits"], ["--permission-mode=plan"],
                                  ["-p", "no --add-dir and no --permission-mode bypassPermissions"]))
def test_a_harmless_mode_and_a_prompt_pass(args):
    launcher._check_cli_args(args)
