"""Builder tests for W2-59: the canaries and the retrieval-regression check read the project under check, never the
install path, and the baseline ships as package data (DEC-835).

Regression evidence only (DEC-136); the acceptance tests prove it from an installed wheel.
"""
from __future__ import annotations

import sys
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.retrieval import canary, retrieve_check  # noqa: E402


def _searcher(root, query, refresh=False):
    return {"available": True, "hits": [{"path": "x.md"}]}


@pytest.mark.parametrize("layout", ["template/governance/kernel/canaries", "governance/kernel/canaries"])
def test_the_canaries_are_read_from_the_project_in_either_layout(tmp_path, layout):
    (tmp_path / layout).mkdir(parents=True)
    for index in ("lexical", "semantic"):
        (tmp_path / layout / f"{index}.yaml").write_text(yaml.safe_dump({"canaries": [{"query": "q"}]}), encoding="utf-8")
    with patch.object(canary, "_SEARCHERS", {"lexical": _searcher, "semantic": _searcher}):
        result = canary.run_canaries(tmp_path)
    assert all(entry["status"] == canary.AVAILABLE for entry in result.values())


def test_a_project_with_no_canary_declaration_is_not_given_the_install_path_s(tmp_path):
    with patch.object(canary, "_SEARCHERS", {"lexical": _searcher, "semantic": _searcher}):
        result = canary.run_canaries(tmp_path)
    assert all(entry["status"] == canary.FACET_UNAVAILABLE for entry in result.values())


def test_the_retrieval_check_adopts_a_tier_with_the_project_s_path_map_and_gitleaks_configuration(tmp_path):
    project, tier = tmp_path / "project", tmp_path / "tier"
    (project / "governance/project").mkdir(parents=True)
    (project / "governance/project/path-map.yaml").write_text(yaml.safe_dump({"policies": {"w259": "warning"}}),
                                                               encoding="utf-8")
    (project / ".gitleaks.toml").write_text("# w259 project rules\n", encoding="utf-8")
    (tier / ".git").mkdir(parents=True)
    retrieve_check._adopt(tier, project)
    adopted = yaml.safe_load((tier / "governance/project/path-map.yaml").read_text(encoding="utf-8"))
    assert adopted["policies"] == {"w259": "warning"} and "everything" in adopted["namespaces"]
    assert (tier / ".gitleaks.toml").read_text(encoding="utf-8") == "# w259 project rules\n"


def test_every_data_file_of_the_package_is_declared_as_package_data():
    declared = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["setuptools"]["package-data"]
    package = REPO / "src" / "gov"
    data = {path for path in package.rglob("*") if path.is_file() and path.suffix not in (".py", ".pyc")}
    shipped = {package.joinpath(*name.split(".")[1:], pattern) for name, patterns in declared.items()
               for pattern in patterns}
    assert data <= shipped, sorted(str(path.relative_to(package)) for path in data - shipped)
