"""S4 and F3: the set is declared in the sets root's own path map (Interface 7), as one ``evaluation_sets.<A>`` entry
of ``memory-verdict-2``'s shape with its five roles, every other byte kept, so that ``gov.retrieval.measure`` accepts
it; the planted repository is never written (``git status`` empty after every subcommand); a run's file-access log
shows no open of the true home's ``gov-os-eval`` or ``gov-os-runs``.

The file-access log: ``w2_170_open_log.py`` installs ``sys.addaudithook`` for ``open``, ``os.*`` and
``subprocess.Popen`` events, writes them to a file, then runs ``gov.memaudit`` with ``runpy``.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import textwrap

import pytest
import yaml

import w2_170_world as W

ENTRY = {"visible": [], "hidden": [f"fixtures/evaluation/{W.AUDIT}/hidden/**"], "measures": {"roles": list(W.ROLES)}}
FLOW_ENTRY = (f"  {W.AUDIT}: {{visible: [], hidden: [\"fixtures/evaluation/{W.AUDIT}/hidden/**\"], "
              f"measures: {{roles: [engineer, research, product-spec, independent-test-designer, "
              f"independent-auditor]}}}}\n")


def _ready(world, *, drops=()):
    world.write_set(W.clean_specs())
    assert world.preflight().code == 0
    world.write_notes(2, {q: ("reject", "R1-WRONG") for q in drops})
    assert world.void().code == 0


def _inserted(old: str, new: str) -> list[str]:
    """The lines ``new`` adds to ``old`` as one contiguous block, every other byte kept; fails otherwise."""
    a, b = old.splitlines(keepends=True), new.splitlines(keepends=True)
    assert len(b) > len(a), "the map gained no line"
    prefix = next((i for i, (x, y) in enumerate(zip(a, b)) if x != y), len(a))
    suffix = next((i for i, (x, y) in enumerate(zip(reversed(a), reversed(b))) if x != y), len(a))
    assert prefix + suffix >= len(a), "the map's other bytes were not kept, or more than one place changed"
    k = min(prefix, len(a))
    assert b[:k] + b[k + len(b) - len(a):] == a
    return b[k:k + len(b) - len(a)]


def _roles_entry(entry):
    assert set(entry) == {"visible", "hidden", "measures"}, entry
    assert entry["visible"] == [] and entry["hidden"] == ENTRY["hidden"], entry
    assert set(entry["measures"]) == {"roles"}, entry
    roles = entry["measures"]["roles"]
    assert sorted(roles) == sorted(W.ROLES) and len(roles) == 5, roles      # five, never six (Interface 10.2)
    assert "orchestrator" not in roles


def test_s4_the_sets_root_map_gains_exactly_one_entry_and_keeps_every_other_byte(world):
    _ready(world)
    old = world.sets_map.read_text(encoding="utf-8")
    run = world.declare()
    assert run.code == 0, run
    new = world.sets_map.read_text(encoding="utf-8")
    block = yaml.safe_load(textwrap.dedent("".join(_inserted(old, new))))
    assert isinstance(block, dict) and set(block) == {W.AUDIT}, block      # the inserted lines are the entry alone
    _roles_entry(block[W.AUDIT])
    from gov.util.parts import evaluation_sets
    sets = evaluation_sets(str(world.sets))
    _roles_entry(sets[W.AUDIT])
    before = yaml.safe_load(old)
    after = yaml.safe_load(new)
    assert after["evaluation_sets"].pop(W.AUDIT)
    assert after == before


def test_s4_an_equal_entry_already_present_is_left_as_it_is(world):
    text = W.SETS_MAP.replace("  # the last comment inside the block\n",
                              "  # the last comment inside the block\n" + FLOW_ENTRY)
    world.sets_map.write_text(text, encoding="utf-8")
    _ready(world)
    run = world.declare()
    assert run.code == 0, run
    assert world.sets_map.read_text(encoding="utf-8") == text
    assert (world.run_dir / "USED").exists()


_MAP_FAULTS = {
    "a-different-entry": lambda w: w.sets_map.write_text(W.SETS_MAP.replace(
        "  # the last comment inside the block\n", "  # the last comment inside the block\n" + FLOW_ENTRY.replace(
            "product-spec, ", "")), encoding="utf-8"),
    "no-map": lambda w: w.sets_map.unlink(),
    "no-evaluation-sets-block": lambda w: w.sets_map.write_text("# a map without the block\nversion: 1\n",
                                                                 encoding="utf-8"),
    "a-map-that-is-not-yaml": lambda w: w.sets_map.write_text(f"evaluation_sets: [{W.EWORD}\n  : :\n",
                                                               encoding="utf-8"),
}


@pytest.mark.parametrize("fault", sorted(_MAP_FAULTS))
def test_s4_dc_map_refuses_and_writes_nothing(world, fault):
    _ready(world)
    _MAP_FAULTS[fault](world)
    before = W.snapshot(world.sets, world.launch)
    run = world.declare()
    assert run.code == 1, run
    assert any(x.startswith("DC-MAP") for x in run.lines), run
    assert W.snapshot(world.sets, world.launch) == before
    assert W.EWORD not in run.out + run.err


def test_f3_the_planted_repository_is_unwritten_after_every_subcommand(world):
    assert world.git_status() == ""
    world.write_set(W.clean_specs())
    steps = [("preflight", world.preflight), ("void", None), ("declare", world.declare),
             ("declare again", world.declare)]
    for name, step in steps:
        if name == "void":
            world.write_notes(2, {"q27": ("reject", "R1-WRONG")})
            step = world.void
        run = step()
        assert run.code in (0, 3), (name, run)
        assert world.git_status() == "", name
    assert (world.run_dir / "USED").exists()


def test_f3_a_refused_declaration_leaves_the_repository_unwritten(make_world):
    world = make_world("pool_off")
    _ready(world)
    assert world.declare().code == 1
    assert world.git_status() == ""


def test_s4_the_measure_accepts_the_declared_set_from_the_sets_root_s_map(world, tmp_path):
    _ready(world, drops=("q27",))
    before = world.measure(tmp_path / "kept-before")
    assert "not declared" in before.stderr, before.stderr
    assert world.declare().code == 0
    after = world.measure(tmp_path / "kept-after")
    # declared, covered by its hidden glob, every question loaded: the run stops only at the first call, which
    # has no kept output (no retriever is ever started)
    assert "kept outputs end before" in after.stderr, after.stderr
    assert "not declared" not in after.stderr and "do not cover" not in after.stderr, after.stderr


def _logged_run(world, home, log, sub, flags, env=None):
    argv = [sys.executable, str(W.HERE / "w2_170_open_log.py"), str(log), sub, *flags]
    done = subprocess.run(argv, cwd=world.work, env=W.child_env(home, env), capture_output=True, text=True,
                          timeout=120)
    entries = [line.split("\t", 1) for line in log.read_text(encoding="utf-8").splitlines() if "\t" in line]
    return done, entries


def _true_root_opens(paths, repo_root):
    """The logged paths at or under the true sets root or runs folder that are not of the repository under test.

    W2-179: the nightly's clone lives under ``~/gov-os-runs``, so the repository's own source, tests and stores are
    not a runs-folder open. Both sides are compared in one normal form, ``os.path.realpath`` (symlinks resolved, ``..``
    collapsed), so a symlinked or ``..`` spelling can neither carry a true-root path past the filter nor keep a
    repository path in it; a path that does not exist is normalised by its spelling, and nothing is opened.
    """
    own = os.path.realpath(str(repo_root))
    return [p for p in paths if (W.at_or_under(p, W.TRUE_SETS) or W.at_or_under(p, W.TRUE_RUNS))
            and not W.at_or_under(os.path.realpath(p), own)]


def test_f3_a_run_s_file_access_log_shows_no_open_of_the_true_sets_root_or_runs_folders(world, tmp_path):
    # W2-179 (F1): the repository's root, derived from this file's location (W.HERE, not the current directory, which
    # is the planted repository, and not an environment variable), must be narrower than every true root: an
    # exclusion that covered the true home, the runs folder or the sets root (or an ancestor of one) passes everything
    repo_root = W.HERE.parents[2]
    for true_root in (W.TRUE_HOME, W.TRUE_RUNS, W.TRUE_SETS):
        for form in (str(true_root), os.path.realpath(str(true_root))):
            assert not W.at_or_under(form, repo_root) and not W.at_or_under(form, os.path.realpath(str(repo_root))), (
                "the repository root covers a true root", str(repo_root), form)
    # the default runs folder is ~/gov-os-runs: a planted home holds one, so the run needs it and finds it there
    home = tmp_path / "home-with-runs"
    shutil.copytree(world.launch, home / "gov-os-runs")
    world.write_set(W.clean_specs(), selection=False)
    done, entries = _logged_run(world, home, tmp_path / "preflight.log", "preflight", world.pf_flags(runs_dir=False))
    assert done.returncode == 0, (done.stdout, done.stderr)
    world.write_notes(2, {"q27": ("reject", "R1-WRONG")})
    done2, entries2 = _logged_run(world, home, tmp_path / "void.log", "void", world.void_flags())
    assert done2.returncode == 0, (done2.stdout, done2.stderr)
    done3, entries3 = _logged_run(world, home, tmp_path / "declare.log", "declare", world.dc_flags())
    assert done3.returncode == 0, (done3.stdout, done3.stderr)
    every = entries + entries2 + entries3
    reached = _true_root_opens([p for _, p in every], repo_root)
    assert reached == [], reached
    assert any(W.at_or_under(p, world.hidden) for _, p in entries), "the log saw no planted question opened"
    assert any(W.at_or_under(p, home / "gov-os-runs") for _, p in entries), "~ was not the planted home"
