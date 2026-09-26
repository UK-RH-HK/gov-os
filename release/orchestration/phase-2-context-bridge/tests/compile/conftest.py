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
def _no_env_leak(tmp_path, monkeypatch):
    """Every ``tests/compile/**`` test gets its own private, per-test ``GOVBRIDGE_STORE``.

    BR-DAG-AMEND-R1-17 reopening (pass 3, coordinator finding): this fixture used to only
    ``delenv("GOVBRIDGE_STORE")``, which stops a value already exported in the surrounding shell from leaking
    IN, but does nothing to stop a test that never sets ``GOVBRIDGE_STORE`` itself from falling through to
    ``govbridge.core.store``'s own default, ``$HOME/.cache/gov-bridge/store/default`` -- a location shared
    with, and mutated concurrently by, every OTHER agent's own test-suite run in this multi-agent
    orchestration session (confirmed root cause of
    ``test_compile_real_view_mandatory_in_a.py::test_real_demonstration_task_compiles_byte_identical_twice``'s
    non-determinism: two ``compile_packet`` calls in the same test could see different code seeds because an
    unrelated process rebuilt or mutated that shared store between them). Pointing ``GOVBRIDGE_STORE`` at a
    fresh ``tmp_path``-derived directory instead keeps every test in this package hermetic (R1-T1) even when
    the test body itself never mentions ``GOVBRIDGE_STORE`` -- matching the isolation ``tests/code/conftest.py``
    and ``tests/lexical/conftest.py`` already give their own packages.

    Function-scoped (pytest's default) so it reruns, with a brand-new ``tmp_path``, for every single test --
    this also means it always wins the last word over any fixture of a WIDER scope (module/session) that a
    test file in this package might set up first, since pytest runs function-scoped fixtures' own setup after
    any higher-scoped ones for the same test. A prior attempt at isolating
    ``test_compile_real_view_mandatory_in_a.py`` alone, via a module-scoped fixture local to that file, relied
    on exactly this ordering without accounting for it and was silently overridden by this fixture's own
    (then plain ``delenv``) call every single test -- see that file's own history for the corrected fix,
    which now relies on this fixture instead of re-implementing its own."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "isolated-govbridge-store"))
