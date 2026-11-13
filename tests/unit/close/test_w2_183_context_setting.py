"""The close builds its context at the project's setting, and refuses a bad setting by name (W2-183; DEC-1165)."""
from __future__ import annotations

from unittest.mock import patch

import pytest

from gov.close.command import _build_context, _Finding

PACKET = {"hash": "ab" * 32, "mandatory": []}


def _project(tmp_path, setting_line):
    folder = tmp_path / "governance" / "project"
    folder.mkdir(parents=True)
    (folder / "facts.yaml").write_text(f"budgets:\n  brief: 4000\n{setting_line}", encoding="utf-8")
    return tmp_path


@pytest.mark.parametrize("line", [
    '  close_context_tokens: "65536"\n',
    "  close_context_tokens: true\n",
    "  close_context_tokens: 0\n",
    "  close_context_tokens: -5\n",
    '  close_context_tokens: "many"\n',
])
def test_a_bad_setting_refuses_and_the_context_is_never_built(tmp_path, line):
    root = _project(tmp_path, line)
    with patch("gov.context.context", return_value=PACKET) as built, \
            patch("gov.decisions.check", return_value=[]):
        with pytest.raises(_Finding) as raised:
            _build_context(root, "T-1")
    assert raised.value.code == "CONTEXT_FAILED"
    assert raised.value.details["context_error"] == "CONTEXT_SETTING_INVALID"
    assert raised.value.details["ticket"] == "T-1"
    assert "budgets.close_context_tokens" in raised.value.message
    built.assert_not_called()


def test_the_setting_is_the_budget_the_context_is_built_at(tmp_path):
    root = _project(tmp_path, "  close_context_tokens: 65536\n")
    with patch("gov.context.context", return_value=PACKET) as built, \
            patch("gov.decisions.check", return_value=[]):
        assert _build_context(root, "T-1") is PACKET
    built.assert_called_once_with(root, "T-1", budget=65536)


def test_no_setting_builds_at_the_default(tmp_path):
    root = _project(tmp_path, "")
    with patch("gov.context.context", return_value=PACKET) as built, \
            patch("gov.decisions.check", return_value=[]):
        _build_context(root, "T-1")
    built.assert_called_once_with(root, "T-1", budget=6000)
