"""S5: the exa-g6db case in miniature. No green record; the base already has reds in a legacy suite and in its
colliding kit copy (a failing test and a module that fails to import, in each); the ticket's trailered change fixes
one test of both suites and adds no red. ``gov close <ticket> --json`` exits 0, the ticket closes, the close record
is written, and it lists every base red ``caused: false``.

Red on the base: the suites run in one process and collide (S1), the collection errors' node ids are not found
alone (S2), and with no green record every red is the change's (DEC-1150 (2)): ``RED_CAUSED``.
"""

import w2_193_support as support

MODULES = {
    "g19_determinism": support.USES_BUILD_TREE_RED,   # red at the base and with the change (AssertionError)
    "g20_layout": support.USES_BUILD_TREE,           # green
    "g21_widget": support.FIXED_BY_CHANGE,           # red at the base, fixed by the change
    "g22_import": ("import", support.FAILS_TO_IMPORT),  # a module that fails to import, at the base too
}
BASE_REDS = [("legacy", support.LEGACY, "g19_determinism"), ("kit", support.KIT, "g19_determinism"),
             ("legacy", support.LEGACY, "g22_import"), ("kit", support.KIT, "g22_import")]


def test_the_exa_g6db_case_closes_with_every_base_red_not_caused(tmp_path, sandbox):
    """S5: exit 0, the ticket closed, the close record written; each of the four base reds (both suites' failing
    test and module that fails to import) is in the record, ``caused: false``; the test the change fixed is no red
    and passed on the change in both suites."""
    told = tmp_path / "project-told"
    files = {**support.suite_files(support.LEGACY, "legacy", told, MODULES),
             **support.suite_files(support.KIT, "kit", told, MODULES),
             **support.own_suite_files(told)}
    made = support.project(tmp_path, files=files)
    support.work(made, text="# the widget, CHANGED FIXED\n")
    made.ready(sandbox)
    run = support.close(made, sandbox)

    assert run.returncode == 0, f"gov close did not exit 0\n{run.describe()}"
    support.assert_closed(made, run)
    front = support.record(made)
    for prefix, folder, stem in BASE_REDS:
        entry = support.red_entry_of_module(front, support.module_file(folder, stem))
        assert entry.get("caused") is False, f"the base red {prefix} {stem} is recorded as the change's: {entry}"
    fixed = [r for r in support.reds_of(front) if "g21_widget" in str(r.get("test"))]
    assert not fixed, f"the test the change fixed is recorded as a red: {fixed}"
    for prefix in ("legacy", "kit"):
        calls = support.calls(support.head_side(support.told_runs(told, f"{prefix}-g21_widget")))
        assert calls and all(c["ok"] for c in calls), f"the {prefix} test the change fixed did not pass: {calls}"
