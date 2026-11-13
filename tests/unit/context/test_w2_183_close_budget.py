"""``close_budget``: the close's context ceiling is the project's setting, or the default (W2-183; DEC-1165, DEC-1027)."""
from __future__ import annotations

import pytest

from gov.cli.errors import GovError
from gov.context import DEFAULT_BUDGET, SUPPLEMENTARY_CAP, close_budget

KEY = "budgets.close_context_tokens"


def _facts(tmp_path, text):
    folder = tmp_path / "governance" / "project"
    folder.mkdir(parents=True)
    (folder / "facts.yaml").write_text(text, encoding="utf-8")
    return tmp_path


def test_the_constants_are_the_decided_ones():
    assert SUPPLEMENTARY_CAP == 6000
    assert DEFAULT_BUDGET == 6000


def test_the_setting_is_read(tmp_path):
    root = _facts(tmp_path, "budgets:\n  brief: 4000\n  close_context_tokens: 65536\n")
    assert close_budget(root) == 65536


def test_no_facts_file_gives_the_default(tmp_path):
    assert close_budget(tmp_path) == DEFAULT_BUDGET


def test_a_missing_root_gives_the_default():
    assert close_budget(tmp_path_missing()) == DEFAULT_BUDGET


def tmp_path_missing():
    from pathlib import Path
    return Path("/no-such-project")


@pytest.mark.parametrize("text", [
    "other: 1\n",
    "budgets:\n",
    "budgets: []\n",
    "budgets:\n  brief: 4000\n",
    "",
])
def test_no_mapping_or_no_key_gives_the_default(tmp_path, text):
    assert close_budget(_facts(tmp_path, text)) == DEFAULT_BUDGET


@pytest.mark.parametrize("value", ["0", "-5", '"many"', "2.5", "true", "false", '"65536"', "null", "[1]"])
def test_a_setting_that_is_not_a_positive_whole_number_refuses_by_name(tmp_path, value):
    root = _facts(tmp_path, f"budgets:\n  close_context_tokens: {value}\n")
    with pytest.raises(GovError) as raised:
        close_budget(root)
    assert raised.value.code == "CONTEXT_SETTING_INVALID"
    assert KEY in raised.value.message
    assert raised.value.details["key"] == KEY and "value" in raised.value.details


def test_the_refusal_names_the_value(tmp_path):
    root = _facts(tmp_path, 'budgets:\n  close_context_tokens: "many"\n')
    with pytest.raises(GovError) as raised:
        close_budget(root)
    assert "many" in raised.value.message and raised.value.details["value"] == "many"


@pytest.mark.parametrize("text", ["budgets: [unclosed\n", "- a\n- b\n", "just text\n", "key: : :\n"])
def test_a_facts_file_that_is_not_a_readable_mapping_refuses_by_name(tmp_path, text):
    with pytest.raises(GovError) as raised:
        close_budget(_facts(tmp_path, text))
    assert raised.value.code == "CONTEXT_SETTING_INVALID"
    assert "facts.yaml" in raised.value.message


def test_a_facts_file_that_is_not_utf8_refuses_by_name(tmp_path):
    root = _facts(tmp_path, "")
    (root / "governance" / "project" / "facts.yaml").write_bytes(b"\xff\xfe\x00bad")
    with pytest.raises(GovError) as raised:
        close_budget(root)
    assert raised.value.code == "CONTEXT_SETTING_INVALID"
