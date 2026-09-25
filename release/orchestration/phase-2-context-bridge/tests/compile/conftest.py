import sys
from pathlib import Path

import pytest

FIXTURES_COMPILE = Path(__file__).resolve().parents[1] / "fixtures" / "compile"
sys.path.insert(0, str(FIXTURES_COMPILE))
import compile_repobuilder as repobuilder  # noqa: E402


@pytest.fixture
def fixture_repo(tmp_path):
    return repobuilder.build(tmp_path / "repo")


@pytest.fixture
def view_path(tmp_path, fixture_repo):
    p = tmp_path / "canonical-view.yaml"
    repobuilder.write_canonical_view(p, fixture_repo)
    return str(p)


@pytest.fixture
def registry_path(tmp_path):
    p = tmp_path / "authority-registry.yaml"
    repobuilder.write_registry(p)
    return str(p)


@pytest.fixture
def budgets_path():
    return str(Path(__file__).resolve().parents[2] / "config" / "budgets.yaml")


def make_task_spec(view_path, required_inputs=None, seeds=None, queries=None, budget_profile="bounded-builder"):
    return {
        "schema": "govbridge-task-spec/1", "task_id": "T-COMPILE-1", "role": "test",
        "objective": "compile a packet over the fixture corpus",
        "view": view_path,
        "required_inputs": required_inputs if required_inputs is not None else [
            {"state_ref": "state:bridge#mandatory_bridge_inputs.items[*]", "reason": "test"},
        ],
        "seeds": seeds or [],
        "queries": queries or [],
        "mutation_scope": ["tests/compile/**"],
        "prohibitions": ["do not touch anything outside mutation_scope"],
        "required_checks": ["pytest tests/compile -q"],
        "completion_vocabulary": ["ANSWERED", "PARTIAL", "BLOCKED"],
        "budget_profile": budget_profile,
    }


@pytest.fixture
def task_spec_factory():
    """Returns ``make_task_spec`` itself, so tests build a task spec without a fragile ``from conftest import
    ...`` (which does not resolve reliably under ``--import-mode=importlib``, used by the cross-package coexistence
    check)."""
    return make_task_spec


@pytest.fixture(autouse=True)
def _no_env_leak(monkeypatch):
    monkeypatch.delenv("GOVBRIDGE_STORE", raising=False)
