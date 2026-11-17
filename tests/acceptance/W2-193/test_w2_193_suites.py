"""S1: colliding suites run each in its own pytest process; no collection error or import collision comes from running
them together; every test of each suite is collected and run.

The planted adopted project: a legacy suite (``governance/scripts/tests/``) and its kit copy
(``governance/framework/kit/governance/scripts/tests/``), neither a package, with the same module names and a
``conftest.py`` each whose ``build_tree`` the modules import by name (``from conftest import build_tree``); the
ticket's own suite has a ``conftest.py`` of its own without it. The widget change reaches both suites (a coupling of
the test map), so the scoped close selects all three. Every planted test passes when its suite is collected alone.

Red on the base: the close runs the selection in one pytest process; the modules of both suites import the last
``conftest`` loaded (the ticket suite's) or collide by name, so each is a collection error, judged the change's: the
close refuses ``RED_CAUSED`` (no green base) and the planted tests never run.
"""

import pytest

import w2_193_support as support

STEMS = ("g19_determinism", "g20_layout")


def _pids(made, label):
    runs = support.calls(support.head_side(support.told_runs(made.told, label)))
    return {r["run_pid"] for r in runs}, runs


def _assert_no_collision(made, run, suites, colliding):
    """The close passed; its record's runs hold no error and its reds no import failure; each planted test of each
    suite ran on the change and passed; each pair of ``colliding`` folders ran in different pytest processes."""
    support.assert_closed(made, run)
    front = support.record(made)
    runs = front.get("runs")
    assert isinstance(runs, list) and runs, f"the close record names no runs: {front.get('runs')!r}"
    errors = sum(int(r.get("errors") or 0) for r in runs if isinstance(r, dict))
    assert errors == 0, f"the scoped close's runs hold {errors} collection error(s): {runs}"
    imports = [r for r in support.reds_of(front) if "Import" in str(r.get("failure_type")) or
               "ImportError" in str(r.get("reason"))]
    assert not imports, f"the record names an import failure among its reds: {imports}"
    processes = {}
    for folder, prefix, stems in suites:
        seen = set()
        for stem in stems:
            pids, calls = _pids(made, f"{prefix}-{stem}")
            assert calls, f"{support.node(folder, stem)} was not run by the close"
            assert all(c["ok"] for c in calls), f"{support.node(folder, stem)} failed: {calls}"
            seen |= pids
        processes[folder] = seen
    for one, other in colliding:
        shared = processes[one] & processes[other]
        assert not shared, f"{one} and {other} collide but ran in the same pytest process {sorted(shared)}"


def test_the_legacy_suite_and_its_kit_copy_run_in_their_own_processes_and_every_test_runs(tmp_path, sandbox):
    """S1 (EXAMIN's form): same module names, ``from conftest import build_tree`` in each module, and the ticket's
    own suite with its own ``conftest.py``: no collection error, no ImportError, every planted test ran and passed,
    and the legacy suite, the kit copy and the ticket's own suite ran in three different processes."""
    told = tmp_path / "project-told"
    modules = {stem: support.USES_BUILD_TREE for stem in STEMS}
    files = {**support.suite_files(support.LEGACY, "legacy", told, modules),
             **support.suite_files(support.KIT, "kit", told, modules),
             **support.own_suite_files(told)}
    made = support.project(tmp_path, files=files)
    support.work(made)
    made.ready(sandbox)
    run = support.close(made, sandbox)
    _assert_no_collision(made, run, [(support.LEGACY, "legacy", STEMS), (support.KIT, "kit", STEMS),
                                     (support.OWN, "own", ("aa",))],
                         [(support.LEGACY, support.KIT), (support.LEGACY, support.OWN), (support.KIT, support.OWN)])


@pytest.mark.parametrize("form", ["same_module_name", "conftest_by_name"])
def test_each_form_of_collision_alone_runs_its_suites_in_separate_processes(tmp_path, sandbox, form):
    """S1, each form alone: ``same_module_name``, two suites holding ``test_g19_determinism.py`` and no
    ``conftest.py`` at all; ``conftest_by_name``, the legacy suite's modules import ``build_tree`` from ``conftest``
    by name while the kit copy (other module names, no import of ``conftest``) and the ticket's own suite also hold
    a ``conftest.py``. The close passes with no collection error, every planted test ran, and the legacy suite ran
    in a process apart from the kit copy's (and, in the second form, from the ticket suite's). Whether the kit copy
    and the ticket suite, whose modules import no ``conftest``, share a process is left open."""
    told = tmp_path / "project-told"
    if form == "same_module_name":
        legacy = {"g19_determinism": support.PASS}
        kit = {"g19_determinism": support.PASS}
        files = {**support.suite_files(support.LEGACY, "legacy", told, legacy, conftest=False,
                                       imports_conftest=False),
                 **support.suite_files(support.KIT, "kit", told, kit, conftest=False, imports_conftest=False)}
    else:
        legacy = {"g19_determinism": support.USES_BUILD_TREE}
        kit = {"k40_other_name": support.PASS}
        files = {**support.suite_files(support.LEGACY, "legacy", told, legacy),
                 **support.suite_files(support.KIT, "kit", told, kit, imports_conftest=False)}
        # the kit copy's conftest.py has no build_tree: loaded last, it is what a shared process's modules import
        files[f"{support.KIT}/conftest.py"] = "OTHER = 'the kit copy has its own conftest, without build_tree'\n"
        files.update(support.own_suite_files(told))
    made = support.project(tmp_path, files=files)
    support.work(made)
    made.ready(sandbox)
    run = support.close(made, sandbox)
    suites = [(support.LEGACY, "legacy", tuple(legacy)), (support.KIT, "kit", tuple(kit))]
    colliding = [(support.LEGACY, support.KIT)]
    if form == "conftest_by_name":
        suites.append((support.OWN, "own", ("aa",)))
        colliding.append((support.LEGACY, support.OWN))
    _assert_no_collision(made, run, suites, colliding)
