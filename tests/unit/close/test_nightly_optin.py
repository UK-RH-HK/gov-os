"""Builder tests of the nightly's ``--optin`` (W2-209 S11, RELEASE-ON-BEHALF G2; DEC-1220 (1))."""
from __future__ import annotations

import os

import pytest

from gov.cli.errors import GovError
from gov.close import nightly


def test_the_union_of_the_option_and_the_callers_variable_is_sorted_and_drops_none():
    assert nightly.optin_names(["weekly"], {"GOV_TESTS_OPTIN": "lifted"}) == ["lifted", "weekly"]
    assert nightly.optin_names(None, {"GOV_TESTS_OPTIN": " breadth, lifted ,,"}) == ["breadth", "lifted"]
    assert nightly.optin_names(["weekly", "weekly"], {}) == ["weekly"]
    assert nightly.optin_names(None, {}) == []
    assert nightly.optin_names(None, {"GOV_TESTS_OPTIN": ""}) == []


def test_a_name_the_test_configuration_does_not_know_is_refused_before_anything_runs(tmp_path):
    with pytest.raises(GovError) as raised:
        nightly.night(tmp_path, "main", optin=["bogus"])
    assert "bogus" in raised.value.message
    assert not (tmp_path / "docs").exists() and not (tmp_path / nightly.RUNTIME_DIR).exists()


def test_the_command_line_refuses_an_unknown_name_with_a_usage_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as raised:
        nightly.main(["main", "--root", str(tmp_path), "--optin", "bogus"])
    assert raised.value.code == 2
    assert "bogus" in capsys.readouterr().err


def test_the_runs_environment_carries_the_union_and_the_callers_value_is_put_back(monkeypatch):
    monkeypatch.setenv("GOV_TESTS_OPTIN", "lifted")
    with nightly.optin_environment(["weekly"]):
        assert os.environ["GOV_TESTS_OPTIN"] == "lifted,weekly"
    assert os.environ["GOV_TESTS_OPTIN"] == "lifted"
    monkeypatch.setenv("GOV_TESTS_OPTIN", "")
    with nightly.optin_environment([]):
        assert "GOV_TESTS_OPTIN" not in os.environ
    assert os.environ["GOV_TESTS_OPTIN"] == ""
