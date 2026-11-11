"""S6: the package is wired in. ``governance/project/test-map.yaml`` (this tree's own) places ``src/gov/memaudit/**``
so that ``gov close``'s scoped selection (``gov.close.select.plan``) for a planted change under ``src/gov/memaudit/``
names ``tests/unit/memaudit/`` and not the full suite; each subcommand prints its usage with ``--help`` and exits 0;
argparse's errors exit 4 (Interface 1 and 5); the Python entry points of Interface 8 exist for W2-171 and W2-172.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

import w2_170_world as W


@pytest.mark.parametrize("sub", ["preflight", "void", "declare"])
def test_s6_each_subcommand_prints_its_usage_with_help_and_exits_0(world, sub):
    run = world.run(sub, "--help")
    assert run.code == 0, run
    assert "usage" in run.out.lower(), run
    assert "--sets-root" in run.out and "--audit" in run.out, run


@pytest.mark.parametrize("argv", [
    ["preflight", "--sets-root", "S", "--audit", W.AUDIT, "--no-such-flag", "x"],
    ["void", "--sets-root", "S"],
    ["no-such-subcommand"],
    [],
], ids=["unknown-flag", "missing-audit", "unknown-subcommand", "no-subcommand"])
def test_s6_argparse_errors_exit_4(world, argv):
    argv = [str(world.sets) if a == "S" else a for a in argv]
    run = world.run(*argv)
    assert run.code == 4, run
    assert "Traceback" not in run.out + run.err


def test_s6_the_scoped_selection_for_a_change_under_src_gov_memaudit_names_tests_unit_memaudit(tmp_path):
    map_text = (W.TREE / "governance" / "project" / "test-map.yaml").read_text(encoding="utf-8")
    home = tmp_path / "home"
    home.mkdir()
    repo, _ = W.plant_select_repo(tmp_path, map_text, home)
    from gov.close.select import plan
    selected = plan(repo, "W2-170", ticket="DAEO-61vm")
    targets = [t["target"].rstrip("/") for t in selected["selected"]]
    assert selected["changed"] == ["src/gov/memaudit/core.py"], selected["changed"]
    assert selected["scope"] == "scoped", selected["why_full"]
    assert "tests" not in targets, targets                       # not the full suite
    assert "tests/unit/memaudit" in targets, targets


def test_s6_the_entry_points_for_w2_171_and_w2_172_exist(world):
    probe = ("import importlib, sys\n"
             "need = {'layout': ['paths', 'is_used'], 'preflight': ['run'], 'drops': ['apply'],\n"
             "        'declare': ['declare'], 'say': ['say'], 'ledger': ['append']}\n"
             "missing = [f'{m}.{n}' for m, names in need.items() for n in names\n"
             "           if not callable(getattr(importlib.import_module('gov.memaudit.' + m), n, None))]\n"
             "print(' '.join(missing) or 'all')\n")
    done = subprocess.run([sys.executable, "-c", probe], cwd=world.work, env=W.child_env(world.home),
                          capture_output=True, text=True, timeout=60)
    assert done.returncode == 0, done.stderr[-2000:]
    assert done.stdout.strip() == "all", done.stdout
