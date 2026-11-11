"""S5, S6, F1: the command line, the one printer and the test map's placement."""

from __future__ import annotations

import pytest
import yaml

from gov.memaudit import layout
from gov.memaudit.common import UsageError
from gov.memaudit.say import REFUSAL, say

from .conftest import AUDIT, SRC


@pytest.mark.parametrize("sub", ["preflight", "void", "declare"])
def test_each_subcommand_prints_its_usage_with_help_and_exits_0(plant, sub):
    done = plant.cli(sub, "--help")
    assert done.returncode == 0 and done.stdout.startswith("usage: ") and "--sets-root" in done.stdout


def test_an_argparse_error_exits_4_with_one_line_and_no_value(plant):
    done = plant.cli("preflight", "--sets-root", str(plant.root / "fixtures/x"))
    assert done.returncode == 4
    assert done.stdout == "ERROR: UsageError\n" and done.stderr == "ERROR: UsageError\n"
    assert plant.cli("nosuch").returncode == 4


@pytest.mark.parametrize("audit", ["memory-audit-2026111", "fresh-80", "memory-audit-20261111/../x"])
def test_an_audit_name_of_another_form_exits_4(plant, audit):
    args = plant.void_args()
    args[args.index("--audit") + 1] = audit
    assert plant.cli(*args).returncode == 4


def test_a_sets_root_that_is_not_a_directory_or_inside_the_walls_exits_4(plant):
    walls = plant.tmp / "indep-walls/w"
    walls.mkdir(parents=True)
    for root in (plant.tmp / "nothing", walls):
        args = plant.void_args()
        args[args.index("--sets-root") + 1] = str(root)
        assert plant.cli(*args).returncode == 4


def test_a_runs_dir_inside_the_sets_root_exits_4(plant):
    args = plant.preflight_args()
    args[args.index("--runs-dir") + 1] = str(plant.root / "runs")
    assert plant.cli(*args).returncode == 4
    assert not (plant.run_dir / "PREFLIGHT.json").exists()


def test_an_unresolved_commit_exits_4(plant):
    assert plant.cli(*plant.preflight_args("0" * 40)).returncode == 4


def test_say_refuses_a_line_naming_a_sets_root_folder(tmp_path, capsys):
    for line in (f"{tmp_path}/x", "a fixtures/b", "the runs/ folder", "indep-walls/x", "hidden"):
        assert say(line, tmp_path) == ("usage", {"printed": 0, "refused": 1})
    out = capsys.readouterr()
    assert out.out.splitlines() == [REFUSAL] * 5 and out.err.splitlines() == [REFUSAL] * 5
    assert say("PF-COUNT ok", tmp_path) == ("ok", {"printed": 1, "refused": 0})
    assert capsys.readouterr().out == "PF-COUNT ok\n"


def test_an_unexpected_error_is_one_line_with_its_class_only(plant, monkeypatch, capsys):
    from gov.memaudit import __main__ as cli, drops

    def boom(*a, **k):
        raise KeyError("a question's text zephyr")
    monkeypatch.setattr(drops, "apply", boom)
    assert cli.main(plant.void_args()) == 4
    out = capsys.readouterr()
    assert out.out == "ERROR: KeyError\n" and out.err == "ERROR: KeyError\n"


def test_layout_derives_every_path_inside_the_root(plant):
    p = layout.paths(str(plant.root), AUDIT)
    assert p["hidden"] == plant.hidden and p["dropped"] == plant.hidden / "dropped"
    assert p["run"] == plant.run_dir and p["pool"] == plant.root / "fixtures/evaluation/memory-pool/hidden"
    assert not layout.is_used(str(plant.root), AUDIT)
    with pytest.raises(UsageError):
        layout.paths(str(plant.root), "memory-audit-x")


def test_the_test_map_places_the_package_and_its_tests():
    from pathlib import Path

    from gov.close.select import _any, match
    root = Path(SRC).parent
    doc = yaml.safe_load((root / "governance/project/test-map.yaml").read_text())
    change = "src/gov/memaudit/preflight.py"
    assert not _any(change, doc["shared_core"])
    suites = [s for c in doc["couplings"] if any(match(change, p) for p in c["paths"]) for s in c["suites"]]
    assert suites == ["tests/unit/memaudit/"]
    assert (root / suites[0]).is_dir()
