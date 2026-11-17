"""Success 2 [CAP-43, W2-H021] and failure 1: `gov doctor --json`'s section `install` in a product repository."""

from __future__ import annotations

import json

import pytest
import yaml

import w2_18_support as s


def _lock_release(project):
    data = yaml.safe_load((project / "governance" / "framework.lock").read_text(encoding="utf-8"))
    return (data.get("release") or {}).get("version")


def test_doctor_fails_install_with_case_editable_when_the_pinned_gov_is_an_editable_install(
        adopted, releases, tmp_path, sandbox):
    project = s.copy_project(adopted, tmp_path / "product")
    source = s.flat_editable_source(releases, s.VERSION_A, tmp_path / "editable-gov")
    environment = s.plant_pin(project, releases, s.VERSION_A, sandbox, editable=source)
    direct = [json.loads(path.read_text(encoding="utf-8"))
              for path in s.site_packages(environment).glob("gov-*.dist-info/direct_url.json")]
    assert direct and direct[0].get("dir_info", {}).get("editable"), "the planted pin is not an editable install"
    result = s.doctor_from_pin(project, sandbox)
    s.assert_fails_with_case(result, "editable", "the pin's gov is an editable install")


def test_doctor_fails_install_with_case_lock_when_the_pin_differs_from_framework_lock(planted_b, releases, sandbox):
    assert _lock_release(planted_b) == s.VERSION_A
    assert s.read_pin(planted_b)["wheel"]["sha256"] != releases.a.wheel_sha256
    result = s.doctor_from_pin(planted_b, sandbox)
    s.assert_fails_with_case(result, "lock", f"the pin is release {s.VERSION_B} and framework.lock names "
                                             f"{s.VERSION_A} with another wheel sha256")


def test_doctor_fails_install_with_case_source_tree_when_its_gov_resolves_to_a_source_tree(planted_a, sandbox):
    result = s.doctor_from_source_tree(planted_a, sandbox, s.SRC)
    s.assert_fails_with_case(result, "source_tree", f"doctor's gov is imported from {s.SRC}/gov (PYTHONPATH)")


def test_doctor_passes_install_when_run_from_a_pin_that_matches_framework_lock(installed_a, sandbox):
    done = installed_a.run
    assert done.returncode == 0, f"`gov install {s.VERSION_A}` did not install the pin\n{done.describe()}"
    result = s.doctor_from_pin(installed_a.project, sandbox)
    section = result.section
    assert section.get("status") == "pass" and section.get("version") == s.VERSION_A, (
        f"the install section does not pass for a pin of release {s.VERSION_A}, the release framework.lock "
        f"names, with doctor run by the pin\n{result.describe()}")


def test_doctor_reports_install_unmeasured_naming_gov_install_without_a_pin(adopted, tmp_path, sandbox):
    project = s.copy_project(adopted, tmp_path / "product")
    result = s.doctor_of(s.worktree_gov(project, sandbox, "doctor", "--json"))
    section = result.section
    assert section.get("status") == "unmeasured" and "gov install" in str(section.get("reason", "")), (
        f"with no pin the install section is not unmeasured naming `gov install`\n{result.describe()}")


@pytest.mark.parametrize("tree", ["this-worktree", "another-source-tree"])
def test_a_session_importing_a_source_tree_s_gov_is_refused_by_doctor_naming_the_path(
        planted_a, releases, tree, sandbox):
    src = s.SRC if tree == "this-worktree" else releases.repo / "src"
    assert (src / "gov" / "__init__.py").is_file() and (src.parent / "pyproject.toml").is_file()
    result = s.doctor_from_source_tree(planted_a, sandbox, src)
    section = result.section
    assert section.get("status") != "pass", f"doctor passes a session that imports {src}/gov\n{result.describe()}"
    assert result.run.returncode != 0, f"doctor exits 0 for a session that imports {src}/gov\n{result.describe()}"
    assert section.get("status") == "fail" and section.get("case") == "source_tree", (
        f"the install section does not fail with case 'source_tree' for a session that imports {src}/gov\n"
        f"{result.describe()}")
    reason = str(section.get("reason", ""))
    assert str(src) in reason or str(src.resolve()) in reason, (
        f"the install section's reason does not name the path imported, {src}/gov\n{result.describe()}")
