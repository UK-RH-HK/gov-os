"""Builder cases for ``gov launch``'s RUBRIC-2 options in ``gov.launch.command`` (W2-184, interface 7.2a; the CTO's
P-W2-184-2 (a)): ``--reason``, ``--trial`` and ``--owner-named`` before ``--`` reach ``launcher.launch`` as keywords,
the usage line names them, ``--plan`` does not read them, and a word after ``--`` stays a CLI argument."""

from __future__ import annotations

import argparse

import pytest

from gov.cli import main as cli
from gov.launch import command, launcher


def _parse(argv: list[str], passthrough: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    args = parser.parse_args(argv)
    args.passthrough = passthrough
    return args


@pytest.fixture
def seen(monkeypatch):
    calls = []
    monkeypatch.setattr(launcher, "launch",
                        lambda root, role, ticket, cli_args, **kw: calls.append((role, ticket, cli_args, kw)) or 0)
    monkeypatch.setattr(launcher, "plan", lambda root, role, ticket: calls.append(("plan", role, ticket)) or 0)
    return calls


def test_the_three_options_reach_the_launcher_as_keywords(seen, tmp_path):
    args = _parse(["engineer", "T-1", "--reason", "a deep check", "--trial", "trial-1", "--owner-named", "DEC-1010"],
                  ["-p", "Do the work."])
    assert command.run(tmp_path, args, {}) == 0
    assert seen == [("engineer", "T-1", ["-p", "Do the work."],
                     {"gate_override": None, "gpu_need_mib": None, "reason": "a deep check", "trial": "trial-1",
                      "owner_named": "DEC-1010"})]


@pytest.mark.parametrize("option, key", [("--reason", "reason"), ("--trial", "trial"),
                                         ("--owner-named", "owner_named")])
def test_each_option_alone_reaches_the_launcher_and_the_others_stay_absent(seen, tmp_path, option, key):
    assert command.run(tmp_path, _parse(["engineer", "T-1", option, "v"]), {}) == 0
    [(_, _, cli_args, kw)] = seen
    assert cli_args == [] and kw[key] == "v"
    assert all(kw.get(other) is None for other in ("reason", "trial", "owner_named") if other != key)


def test_an_empty_value_is_passed_on_for_the_launcher_to_refuse(seen, tmp_path):
    args = _parse(["engineer", "T-1", "--reason", "", "--trial", "", "--owner-named", ""])
    command.run(tmp_path, args, {})
    [(_, _, _, kw)] = seen
    assert (kw["reason"], kw["trial"], kw["owner_named"]) == ("", "", "")


def test_without_the_options_the_launcher_gets_no_new_keyword(seen, tmp_path):
    command.run(tmp_path, _parse(["engineer", "T-1"]), {})
    [(_, _, _, kw)] = seen
    assert kw == {"gate_override": None, "gpu_need_mib": None}


def test_plan_does_not_read_the_three_options(seen, tmp_path):
    args = _parse(["--plan", "engineer", "T-1", "--reason", "r", "--trial", "t", "--owner-named", "DEC-1"])
    assert command.run(tmp_path, args, {}) == 0
    assert seen == [("plan", "engineer", "T-1")]


def test_the_usage_line_names_the_three_options():
    parser = argparse.ArgumentParser()
    command.add_arguments(parser)
    usage = parser.format_usage()
    for word in ("--reason", "--trial", "--owner-named", "--plan", "--gate-override", "--gpu-need-mib", "--"):
        assert word in usage
    assert usage.index("--owner-named") < usage.index("[-- <CLI arguments>]")


def test_through_gov_the_options_before_the_double_dash_are_taken_and_after_it_passed_through(seen, tmp_path):
    code = cli.main(["launch", "engineer", "T-1", "--owner-named", "DEC-1010", "--root", str(tmp_path), "--",
                     "-p", "x", "--owner-named", "DEC-2020", "--reason", "after", "--trial", "t2"])
    assert code == 0
    [(_, _, cli_args, kw)] = seen
    assert kw["owner_named"] == "DEC-1010" and kw.get("reason") is None and kw.get("trial") is None
    assert cli_args == ["-p", "x", "--owner-named", "DEC-2020", "--reason", "after", "--trial", "t2"]


def test_through_gov_a_bad_call_prints_the_usage_naming_the_options(capsys):
    with pytest.raises(SystemExit) as stop:
        cli.main(["launch"])
    err = capsys.readouterr().err
    assert stop.value.code == 2
    for word in ("--reason", "--trial", "--owner-named"):
        assert word in err
