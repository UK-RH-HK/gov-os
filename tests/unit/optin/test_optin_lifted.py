"""The opt-in suites (DEC-1061, D-4's cut; T-10): ``tests/conftest.py`` leaves every entry of
``tests/optin-<name>*.txt`` out of a run unless the run opts in to ``<name>`` (``--optin=<name>`` or
``GOV_TESTS_OPTIN=<name>``): ``lifted`` (the switched-off features) and ``breadth`` (tier 2's cap and the
representatives' other rows; the CTO's P-1 (b)), each alone or both (``lifted,breadth``).

The mechanism is shown on a planted tree that carries a copy of the root conftest and a list of its own, so the
real lists can change without changing these cases; the real lists are checked only for entries that name nothing.
"""
from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parents[2]
REPO = TESTS.parent

PLANTED = '''
import pytest

def test_kept():
    pass

def test_listed():
    pass

@pytest.mark.parametrize("n", [1, 2, 3])
def test_rows(n):
    pass

@pytest.mark.parametrize("n", ["a", "b"])
def test_one_row_listed(n):
    pass

class TestGroup:
    def test_in_class(self):
        pass

    @pytest.mark.parametrize("n", [1, 2])
    def test_class_rows(self, n):
        pass
'''

LISTING = """# planted list
tests/lifted/  # a whole folder
tests/some/test_file.py  # a whole file
tests/a/test_a.py::test_one_row_listed[b]  # one row
"""
LISTING_PART = """# a second lifted list (as part A's optin-lifted-guard.txt)
tests/a/test_a.py::TestGroup::test_in_class  # one method
"""
BREADTH = """# planted breadth list
tests/a/test_a.py::test_listed  # one function past the cap
"""
BREADTH_PART = """# a second breadth list (as part A's optin-lifted-guard-breadth.txt)
rep: tests/a/test_a.py  # one row per parametrised function
"""


@pytest.fixture
def planted(tmp_path):
    root = tmp_path / "repo"
    (root / "tests" / "a").mkdir(parents=True)
    (root / "tests" / "lifted").mkdir()
    (root / "tests" / "some").mkdir()
    (root / "pyproject.toml").write_text("[project]\nname = 'planted'\n")
    shutil.copy(TESTS / "conftest.py", root / "tests" / "conftest.py")
    (root / "tests" / "a" / "test_a.py").write_text(PLANTED)
    (root / "tests" / "lifted" / "test_l.py").write_text("def test_l():\n    pass\n")
    (root / "tests" / "some" / "test_file.py").write_text("def test_f():\n    pass\n")
    (root / "tests" / "some" / "test_other.py").write_text("def test_o():\n    pass\n")
    (root / "tests" / "optin-lifted.txt").write_text(LISTING)
    (root / "tests" / "optin-lifted-guard.txt").write_text(LISTING_PART)
    (root / "tests" / "optin-lifted-breadth.txt").write_text(BREADTH)
    (root / "tests" / "optin-lifted-guard-breadth.txt").write_text(BREADTH_PART)
    return root


def collected(root, *args, env_extra=None):
    env = {key: value for key, value in os.environ.items() if key != "GOV_TESTS_OPTIN"}
    env.update(env_extra or {})
    done = subprocess.run([sys.executable, "-m", "pytest", "tests", "--collect-only", "-q", "-p", "no:cacheprovider",
                           "-p", "no:xdist", *args], cwd=str(root), env=env, capture_output=True, text=True, timeout=120)
    assert done.returncode in (0, 5), f"collection failed ({done.returncode}):\n{done.stdout}\n{done.stderr}"
    ids = {line.strip().split("::", 1)[1] if "::" in line else line.strip()
           for line in done.stdout.splitlines() if "::" in line}
    files = {line.strip().split("::", 1)[0] for line in done.stdout.splitlines() if "::" in line}
    return ids, files, done.stdout


EVERY = {"test_kept", "test_listed", "test_rows[1]", "test_rows[2]", "test_rows[3]", "test_one_row_listed[a]",
         "test_one_row_listed[b]", "TestGroup::test_in_class", "TestGroup::test_class_rows[1]",
         "TestGroup::test_class_rows[2]", "test_l", "test_f", "test_o"}
LIFTED = {"test_l", "test_f", "test_one_row_listed[b]", "TestGroup::test_in_class"}
# breadth's ``rep:`` would also leave out test_one_row_listed[b] (a second row); lifted names it, so a run that opts in
# to lifted collects it (a case an opted-in list names is collected whole)
BREADTH_ONLY = {"test_listed", "test_rows[2]", "test_rows[3]", "TestGroup::test_class_rows[2]"}


def test_a_run_that_does_not_opt_in_leaves_every_listed_case_out_and_keeps_the_rest(planted):
    ids, files, out = collected(planted)
    assert files == {"tests/a/test_a.py", "tests/some/test_other.py"}, out
    assert ids == EVERY - LIFTED - BREADTH_ONLY == {"test_kept", "test_rows[1]", "test_one_row_listed[a]",
                                                    "TestGroup::test_class_rows[1]", "test_o"}, out
    assert "deselected" in out, out


@pytest.mark.parametrize("how", ["option", "environment"])
def test_opting_in_to_lifted_collects_its_cases_and_still_leaves_breadth_out(planted, how):
    args, extra = ((["--optin=lifted"], None) if how == "option" else ([], {"GOV_TESTS_OPTIN": "lifted"}))
    ids, _, out = collected(planted, *args, env_extra=extra)
    assert ids == EVERY - BREADTH_ONLY, out


@pytest.mark.parametrize("how", ["option", "environment"])
def test_opting_in_to_breadth_collects_its_cases_and_still_leaves_lifted_out(planted, how):
    args, extra = ((["--optin=breadth"], None) if how == "option" else ([], {"GOV_TESTS_OPTIN": "breadth"}))
    ids, _, out = collected(planted, *args, env_extra=extra)
    assert ids == EVERY - LIFTED, out


@pytest.mark.parametrize("args, extra", [(["--optin=lifted,breadth"], None), (["--optin=lifted", "--optin=breadth"], None),
                                         ([], {"GOV_TESTS_OPTIN": "lifted,breadth"}),
                                         (["--optin=breadth"], {"GOV_TESTS_OPTIN": "lifted"})],
                         ids=["option-comma", "option-twice", "environment", "option-and-environment"])
def test_opting_in_to_both_collects_every_case(planted, args, extra):
    ids, _, out = collected(planted, *args, env_extra=extra)
    assert ids == EVERY, out
    assert "deselected" not in out, out


def test_another_opt_in_name_opts_in_to_nothing(planted):
    ids, _, out = collected(planted, "--optin=other", env_extra={"GOV_TESTS_OPTIN": "elsewhere"})
    assert ids == EVERY - LIFTED - BREADTH_ONLY, out


def test_a_case_named_by_its_node_id_on_the_command_line_is_run(planted):
    """A nested run or a caller that names a case by its node id gets it, whatever the lists say; a file or a folder
    named on the command line does not opt in."""
    ids, _, out = collected(planted, "tests/a/test_a.py::test_listed", "tests/a/test_a.py::test_rows",
                            "tests/lifted/test_l.py")
    # (the helper also names ``tests``: the default run's cases plus the two named ones; test_l stays out)
    assert ids == (EVERY - LIFTED - BREADTH_ONLY) | {"test_listed", "test_rows[2]", "test_rows[3]"}, out


def _root_conftest():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_root_conftest_for_optin", TESTS / "conftest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("name, suite", [("optin-lifted.txt", "lifted"), ("optin-lifted-guard.txt", "lifted"),
                                         ("optin-lifted-breadth.txt", "breadth"),
                                         ("optin-lifted-guard-breadth.txt", "breadth")])
def test_each_list_belongs_to_its_suite_by_its_name(name, suite):
    assert _root_conftest().optin_name(Path(name)) == suite


def _functions(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.ClassDef):
            names |= {f"{node.name}::{item.name}" for item in node.body
                      if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))}
            names.add(node.name)
    return names


def test_every_entry_of_the_real_lists_names_a_test_path_or_function_that_exists():
    sys.path.insert(0, str(TESTS))
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("_root_conftest_for_optin", TESTS / "conftest.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(TESTS))
    entries = module.optin_entries(TESTS)
    assert entries, "no opt-in list holds an entry"
    stale = []
    for kind, target, listing in entries:
        path, _, rest = target.partition("::")
        where = REPO / path.rstrip("/")
        if not path.startswith("tests/") or not where.exists():
            stale.append(f"{listing}: {target} (no such path)")
        elif rest and re.sub(r"\[.*$", "", rest) not in _functions(where):
            stale.append(f"{listing}: {target} (no such function)")
    assert not stale, "entries that name nothing:\n" + "\n".join(stale)
