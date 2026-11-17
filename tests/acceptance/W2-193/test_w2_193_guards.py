"""F1: a red the change brings is never excused in any new route: a test of a colliding suite (S1) and a module that
fails to import only with the change (S2), each green at the base, still refuse ``RED_CAUSED``. (S3's and S4's routes
have their own cases: ``test_w2_193_base.py`` and ``test_w2_193_base_run.py``.) ``--base`` is the initial commit.

Red on the base: the colliding suite's test never runs (its module is a collection error in the shared process), so
it is not judged against a base where it passes; the module's alone runs are ``absent`` both ways (its node id is
not found), so its reason says ``absent`` instead of the failure it has.
"""

import w2_193_support as support


def test_a_red_in_a_colliding_suite_green_at_the_base_refuses(tmp_path, sandbox):
    """F1 (S1's route): the kit copy's ``test_g20_layout`` reads the widget the change breaks (the legacy suite's
    passes). Refused with RED_CAUSED naming its node id, the ticket stays open, no repair ticket names it, and it
    ran at the base, where it passed."""
    told = tmp_path / "project-told"
    files = {**support.suite_files(support.LEGACY, "legacy", told,
                                   {"g19_determinism": support.USES_BUILD_TREE, "g20_layout": support.USES_BUILD_TREE}),
             **support.suite_files(support.KIT, "kit", told,
                                   {"g19_determinism": support.USES_BUILD_TREE, "g20_layout": support.NOT_BROKEN}),
             **support.own_suite_files(told)}
    made = support.project(tmp_path, files=files)
    base = made.initial
    support.work(made, text="# the widget, CHANGED BROKEN\n")
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox, "--base", base)

    node = support.node(support.KIT, "g20_layout")
    support.assert_caused(made, run, before, node)
    runs = support.calls(support.base_side(support.told_runs(told, "kit-g20_layout")))
    assert runs and all(r["ok"] for r in runs), f"{node} was not judged against the base, where it passes: {runs}"


def test_a_module_that_fails_to_import_only_with_the_change_refuses_with_its_failure_not_absent(tmp_path, sandbox):
    """F1 (S2's route): a W2-bb module imports a missing module only when the widget is broken, and the change
    breaks it. Refused with RED_CAUSED naming the module, the failure named ``ModuleNotFoundError`` and never
    ``absent``; the ticket stays open; the module was imported at the base (its run alone there)."""
    told = tmp_path / "project-told"
    rel = f"{support.BB}/test_bb_imports.py"
    made = support.project(tmp_path, files={rel: support.telling(rel, "bb-imports", told, support.PASS,
                                                                 name="test_bb_imports",
                                                                 at_import=support.FAILS_TO_IMPORT_WHEN_BROKEN)})
    base = made.initial
    support.work(made, text="# the widget, CHANGED BROKEN\n")
    made.ready(sandbox)
    before = support.tickets(made)
    run = support.close(made, sandbox, "--base", base)

    said = support.assert_refused(run, support.RED_CAUSED)
    assert rel in said, f"the refusal does not name the module {rel}\n{run.describe()}"
    assert "ModuleNotFoundError" in said, f"the refusal does not name the module's failure\n{run.describe()}"
    assert "absent" not in said.lower(), f"the module's red was judged absent\n{run.describe()}"
    assert made.ticket_status() == "in_progress", "the ticket closed with a red its change caused"
    assert not support.repair_tickets_naming(made, before, rel), "a repair ticket names a red the change caused"
    imports = support.base_side(support.told_runs(told, "bb-imports"))
    assert imports, f"the module was not run alone at the base: {imports}"
