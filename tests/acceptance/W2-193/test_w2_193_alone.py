"""S2: a red's alone re-run uses a node id pytest resolves in the clone: a collection error is re-run as its module
file, a test as its own node id; no red whose test exists is judged absent because its id could not be found.

The planted adopted project (S1's legacy suite and kit copy) holds, in the kit copy, a module that fails to import
(``test_g30_import.py``: a missing module, a collection error) and a failing test in a nested folder
(``nested/deeper/test_g31_nested.py``); both are red at the base, ``--base`` the initial commit, with the same
failure type. Each planted module tells one line when it is imported and each test one line when it runs.

Red on the base: the collection error's node id is built as ``<file>::<dotted module>``, which pytest cannot find
(exit 4): its alone runs are ``absent`` both ways and it is judged the change's, so the close refuses ``RED_CAUSED``;
the suites also collide in one process (S1).
"""

import w2_193_support as support

IMPORT_STEM = "g30_import"
NESTED_REL = f"{support.KIT}/nested/deeper/test_g31_nested.py"
NESTED_NODE = f"{NESTED_REL}::test_g31_nested"


def test_a_collection_error_and_a_nested_test_are_each_re_run_by_an_id_pytest_resolves(tmp_path, sandbox):
    """S2: the close passes (both reds are red at the base with the same failure type). The module that fails to
    import is recorded by its module file, not caused, its reason not ``absent``, and it was imported on the change
    (the selection's run and its run alone) and at the base (its run alone there). The nested test is recorded by
    its own node id, not caused, its reason not ``absent``, and it ran on the change (the selection's run and its
    run alone) and at the base."""
    told = tmp_path / "project-told"
    modules = {"g19_determinism": support.USES_BUILD_TREE}
    files = {**support.suite_files(support.LEGACY, "legacy", told, modules),
             **support.suite_files(support.KIT, "kit", told,
                                   {**modules, IMPORT_STEM: ("import", support.FAILS_TO_IMPORT)}),
             NESTED_REL: support.telling(NESTED_REL, "kit-g31-nested", told, support.KNOWN_RED,
                                         name="test_g31_nested", reached=True),
             **support.own_suite_files(told)}
    made = support.project(tmp_path, files=files)
    base = made.initial
    support.work(made)
    made.ready(sandbox)
    run = support.close(made, sandbox, "--base", base)

    support.assert_closed(made, run)
    front = support.record(made)

    module = support.module_file(support.KIT, IMPORT_STEM)
    entry = support.red_entry_of_module(front, module)
    assert entry.get("caused") is False, f"the module that fails to import at the base too is the change's: {entry}"
    assert "absent" not in str(entry.get("reason")).lower(), f"the collection error was judged absent: {entry}"
    imports = support.told_runs(told, f"kit-{IMPORT_STEM}")
    assert len(support.head_side(imports)) >= 2, \
        f"the module was not imported on the change by the selection's run and its run alone: {imports}"
    assert support.base_side(imports), f"the module was not run alone at the base (never imported there): {imports}"

    nested = support.red_entry(front, NESTED_NODE)
    assert nested.get("caused") is False, f"the nested test, red at the base too, is the change's: {nested}"
    assert "absent" not in str(nested.get("reason")).lower(), f"the nested test was judged absent: {nested}"
    calls = support.calls(support.told_runs(told, "kit-g31-nested"))
    assert len(support.head_side(calls)) >= 2, \
        f"the nested test did not run on the change in the selection and once more alone: {calls}"
    assert support.base_side(calls), f"the nested test was not run alone at the base: {calls}"
