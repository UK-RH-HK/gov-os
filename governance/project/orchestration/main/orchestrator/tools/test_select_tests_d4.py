"""D-4's cut in select_tests.py (DEC-1061 item 9): T-7's helper exceptions (helper_exceptions.txt), T-10's opt-in
suite `lifted` left out and named (left_out_lifted, lifted_reached), and an empty selection (nothing_to_run).

Each case plants its own tree; the last ones read the real lists beside the tool and in GOV_TEST_TREE (default: this
repository's root). Run: PYTHONPATH=<tree>/src python3 -m pytest -q -p no:cacheprovider tools/test_select_tests_d4.py"""
import importlib.util
import os
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
TREE = Path(os.environ.get("GOV_TEST_TREE", HERE.parents[3]))


@pytest.fixture
def st():
    pytest.importorskip("gov.close.select")
    path = HERE / "select_tests.candidate.py"
    path = path if path.is_file() else HERE / "select_tests.py"
    spec = importlib.util.spec_from_file_location("select_tests_d4_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def plant(root, files):
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)


def sel(*targets, reason="OWN"):
    return [{"target": t, "why": [{"reason": reason}]} for t in targets]


# -- T-7: a listed helper reaches only the suites that import it directly
HELPER = "tests/acceptance/W1-07/w1_07_support.py"
HELPER_TREE = {
    HELPER: "def run_gov():\n    pass\n",
    "tests/acceptance/W1-07/test_w1_07_a.py": "import w1_07_support\n\ndef test_a():\n    pass\n",
    # a direct importer, in both import forms
    "tests/acceptance/W2-10/test_w2_10_a.py": "from w1_07_support import run_gov\n\ndef test_b():\n    pass\n",
    "tests/acceptance/W2-11/w2_11_support.py": "def f():\n    import os, w1_07_support\n",
    "tests/acceptance/W2-11/test_w2_11_a.py": "def test_c():\n    pass\n",
    # reaches it only through another suite's helper, which imports it
    "tests/acceptance/W1-30/w1_30_support.py": "import w1_07_support\n",
    "tests/acceptance/W1-30/test_w1_30_a.py": "import w1_30_support\n\ndef test_d():\n    pass\n",
    "tests/acceptance/W2-01/test_w2_01_a.py": "import w1_30_support\n\ndef test_e():\n    pass\n",
    # names it in text only: no import
    "tests/acceptance/W2-12/test_w2_12_a.py": "KNOWN = 'w1_07_support.py::copy'\n\ndef test_f():\n    pass\n",
}


def test_a_listed_helper_reaches_only_the_suites_that_import_it(st, tmp_path):
    plant(tmp_path, HELPER_TREE)
    from gov.close import select
    suites = select._suites(tmp_path)
    product = select._helper_reach(tmp_path, suites, [HELPER])
    assert set(product) == {"tests/acceptance/W2-10/", "tests/acceptance/W2-11/", "tests/acceptance/W1-30/",
                            "tests/acceptance/W2-01/"}  # the product follows W2-01 -> w1_30_support -> the helper
    dropped = []
    narrowed = st.narrow_helper_reach(select._helper_reach, [HELPER], dropped)(tmp_path, suites, [HELPER])
    assert set(narrowed) == {"tests/acceptance/W2-10/", "tests/acceptance/W2-11/", "tests/acceptance/W1-30/"}
    assert dropped == [{"suite": "tests/acceptance/W2-01/", "helper": HELPER}]
    assert st.importers(tmp_path, HELPER) == {"tests/acceptance/W2-10/", "tests/acceptance/W2-11/",
                                              "tests/acceptance/W1-30/", "tests/acceptance/W1-07/"}


def test_a_helper_not_listed_keeps_the_product_s_reach(st, tmp_path):
    plant(tmp_path, HELPER_TREE)
    from gov.close import select
    suites = select._suites(tmp_path)
    other = "tests/acceptance/W1-30/w1_30_support.py"
    dropped = []
    narrowed = st.narrow_helper_reach(select._helper_reach, [HELPER], dropped)(tmp_path, suites, [other])
    assert narrowed == select._helper_reach(tmp_path, suites, [other]) and dropped == []


def test_the_real_helper_list_names_existing_helpers_with_reasons(st):
    entries = st.helper_exceptions()
    assert entries, "helper_exceptions.txt is empty or absent"
    assert HELPER in [e for e, _ in entries]
    for entry, why in entries:
        assert why, f"{entry}: no reason"
        assert (TREE / entry).is_file() and not Path(entry).name.startswith("test_"), f"{entry}: no such helper"


# -- T-10: the opt-in suite `lifted`
LIFTED_TREE = {
    "tests/unit/a/test_x.py": "def test_one():\n    pass\n",
    "tests/unit/close/test_gates.py": "def test_g():\n    pass\n",
    "tests/unit/close/test_core.py": "def test_k():\n    pass\n\ndef test_lifted_case():\n    pass\n",
    "tests/acceptance/W2-07/test_w2_07_a.py": "def test_a():\n    pass\n",
    "tests/acceptance/W2-70/test_b.py": "def test_b():\n    pass\n",
    "tests/optin-lifted.txt": "# header  # with a hash\n\ntests/acceptance/W2-07/  # the strict close\n"
                              "tests/unit/close/test_gates.py  # the close's gates\n"
                              "tests/unit/close/test_core.py::test_lifted_case  # one case\n",
    "tests/optin-lifted-guard.txt": "tests/acceptance/W2-70/test_b.py::test_b  # the full guard\n"
                                    "rep: tests/unit/a/test_x.py::test_one  # one parameter kept\n",
    "tests/optin-lifted-breadth.txt": "tests/unit/a/test_x.py  # breadth, never `lifted`\n",
}


def test_the_lifted_lists_are_every_optin_lifted_list_but_the_breadth_ones(st, tmp_path):
    plant(tmp_path, LIFTED_TREE)
    assert [p.name for p in st.lifted_lists(tmp_path)] == ["optin-lifted-guard.txt", "optin-lifted.txt"]
    entries, reps = st.lifted_entries(tmp_path)
    assert [e for e, _ in entries] == ["tests/acceptance/W2-70/test_b.py::test_b", "tests/acceptance/W2-07",
                                       "tests/unit/close/test_gates.py", "tests/unit/close/test_core.py::test_lifted_case"]
    assert reps == ["tests/unit/a/test_x.py::test_one"]
    assert st.lifted_entries(tmp_path / "none") == (None, [])


def test_a_lifted_entry_is_left_out_and_named_as_reached(st, tmp_path):
    plant(tmp_path, LIFTED_TREE)
    scope = {"selected": sel("tests/acceptance/W2-07", reason="OWN") + sel("tests/unit", reason="UNIT"),
             "ignore": [], "deselect": []}
    out = st.leave_out_lists(tmp_path, scope, [])
    assert [s["target"] for s in scope["selected"]] == ["tests/unit/a", "tests/unit/close/test_core.py::test_k"]
    assert all({"reason": "LIFTED_SPLIT", "from": "tests/unit"} in s["why"] for s in scope["selected"])
    assert {d["entry"] for d in out["left_out_lifted"]} == {
        "tests/acceptance/W2-07", "tests/unit/close/test_gates.py", "tests/unit/close/test_core.py::test_lifted_case"}
    assert out["lifted_reached"] == [
        {"entry": "tests/acceptance/W2-07", "targets": ["tests/acceptance/W2-07"], "selected_by": ["OWN"]},
        {"entry": "tests/unit/close/test_gates.py", "targets": ["tests/unit"], "selected_by": ["UNIT"]},
        {"entry": "tests/unit/close/test_core.py::test_lifted_case", "targets": ["tests/unit"],
         "selected_by": ["UNIT"]}]
    assert out["lifted_run"]["report_only"] and out["lifted_run"]["pytest_args"][0] == "--optin=lifted"
    assert "tests/acceptance/W2-07" in out["lifted_run"]["pytest_args"]
    assert "tests/acceptance/W2-07" in scope["ignore"] and "tests/unit/close/test_gates.py" in scope["ignore"]
    assert "tests/unit/close/test_core.py::test_lifted_case" in scope["deselect"]
    assert out["nothing_to_run"] is False


def test_nothing_left_to_run_is_said_with_an_empty_target_list(st, tmp_path):
    plant(tmp_path, LIFTED_TREE)
    scope = {"selected": sel("tests/acceptance/W2-07", "tests/unit/close/test_gates.py"), "ignore": [],
             "deselect": []}
    out = st.leave_out_lists(tmp_path, scope, [])
    assert out["nothing_to_run"] is True and scope["selected"] == []
    assert {d["entry"] for d in out["lifted_reached"]} == {"tests/acceptance/W2-07", "tests/unit/close/test_gates.py"}


def test_a_selection_reaching_no_lifted_entry_is_unchanged(st, tmp_path):
    plant(tmp_path, LIFTED_TREE)
    s = sel("tests/unit/a", "tests/acceptance/W2-70/test_b.py::test_other")
    scope = {"selected": list(s), "ignore": [], "deselect": []}
    out = st.leave_out_lists(tmp_path, scope, [])
    assert scope["selected"] == s and out["lifted_reached"] == [] and out["lifted_run"] is None


def test_the_nightly_list_and_the_lifted_list_apply_one_after_the_other(st, tmp_path):
    plant(tmp_path, LIFTED_TREE)
    scope = {"selected": sel("tests/acceptance/W2-70", "tests/acceptance/W2-07"), "ignore": [], "deselect": []}
    out = st.leave_out_lists(tmp_path, scope, [("tests/acceptance/W2-70/test_b.py", "runs gitleaks")])
    assert scope["selected"] == [] and out["nothing_to_run"] is True
    assert [d["entry"] for d in out["left_out_nightly_only"]] == ["tests/acceptance/W2-70/test_b.py"]
    assert [d["entry"] for d in out["lifted_reached"]] == ["tests/acceptance/W2-07"]


def test_every_former_nightly_only_entry_is_in_the_tree_s_lifted_list(st):
    """T-10: nightly_only.txt's entries moved into the opt-in suite `lifted`, none dropped (checked against the
    tree's lists; skipped where the list before the move is not beside the tool)."""
    before = HERE / "nightly_only.txt.pre-d4"
    if not before.is_file():
        pytest.skip("no nightly_only.txt.pre-d4 beside the tool")
    lifted, _ = st.lifted_entries(TREE)
    assert lifted, f"no lifted list in {TREE}"
    names = [e for e, _ in lifted]

    def covered(entry):
        return any(entry == e or entry.startswith(e + "/") or entry.startswith(e + "::") for e in names)

    missing = [e for e, _ in st.nightly_only(before) if (TREE / e.partition("::")[0]).exists() and not covered(e)]
    assert not missing, f"left the nightly list but in no lifted list: {missing}"
