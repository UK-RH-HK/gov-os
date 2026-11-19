"""Fixtures for the W2-208 acceptance tests (README).

The planted source (releases A0, A1 and B), the projects adopted from it and the four ``gov update`` runs are built
once per test run and shared by every worker (``w2_208_support.shared``); a case only reads them. A fixture that cannot
be built fails its cases with "W2-208 fixture could not be built (not the feature under test)".
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import w2_208_support as support  # noqa: E402


def _built(make):
    try:
        return make()
    except AssertionError as exc:
        message = f"W2-208 fixture could not be built (not the feature under test): {exc}"
    pytest.fail(message, pytrace=False)


@pytest.fixture(scope="session")
def copier_bin():
    return _built(support.w216.require_copier)


@pytest.fixture(scope="session")
def source(copier_bin, tmp_path_factory):
    """The planted Gov OS source: its path. Never changed."""
    def build(folder):
        return {"repo": str(support.build_source(folder / "gov-os", support.sandbox_at(folder / "sandbox")))}
    return Path(_built(lambda: support.shared(tmp_path_factory, "source", build))["repo"])


def _adopted(tmp_path_factory, copier_bin, source, name, version, plant=None):
    def build(folder):
        project = support.adopt(copier_bin, source, folder / "product", support.sandbox_at(folder / "sandbox"),
                                version)
        if plant is not None:
            plant(project)
        return {"project": str(project)}
    return Path(_built(lambda: support.shared(tmp_path_factory, name, build))["project"])


@pytest.fixture(scope="session")
def adopted_at_b(copier_bin, source, tmp_path_factory):
    """A project adopted at release B directly (``copier copy`` and ``gov adapters generate``). Never changed."""
    return _adopted(tmp_path_factory, copier_bin, source, "adopted-at-b", support.B)


@pytest.fixture(scope="session")
def examin_013(copier_bin, source, tmp_path_factory):
    """The EXAMIN-like project at A1 (0.1.3's kind), planted with the legacy and the owner's lines. Never changed."""
    return _adopted(tmp_path_factory, copier_bin, source, "examin-013", support.A1, support.plant_examin)


@pytest.fixture(scope="session")
def examin_010(copier_bin, source, tmp_path_factory):
    """A project at A0 (0.1.0's kind: no permission source) whose settings hold only the legacy lines."""
    return _adopted(tmp_path_factory, copier_bin, source, "examin-010", support.A0,
                    lambda project: support.plant_examin(project, owner_lines=False))


def _update_outcome(tmp_path_factory, name, origin, args=(), first=None, text_form=False):
    """A copy of ``origin``, its state, ``gov update B [args] --json`` (and the text form), its state after."""
    def build(folder):
        project = support.w216.clone_folder(origin, folder / "product")
        sandbox = support.sandbox_at(folder / "sandbox")
        before = support.tree_state(project)
        settings_before = support.read_settings(project)
        extra_first = (first(sandbox),) if first is not None else ()
        done = support.update(project, sandbox, *args, first=extra_first)
        text = support.update(project, sandbox, *args, json_form=False, first=extra_first) if text_form else None
        return {"project": str(project), "sandbox": str(folder / "sandbox"), "before": before,
                "settings_before": settings_before, "run": support.run_to_json(done),
                "text": support.run_to_json(text) if text else None, "after": support.tree_state(project),
                "porcelain": support.w216.porcelain_paths(project), "lock": support.lock_version(project)}
    data = _built(lambda: support.shared(tmp_path_factory, name, build))
    data = dict(data)
    data["project"] = Path(data["project"])
    data["run"] = support.run_from_json(data["run"])
    data["text"] = support.run_from_json(data["text"]) if data["text"] else None
    return data


@pytest.fixture(scope="session")
def updated_013(examin_013, tmp_path_factory):
    """``gov update B --json`` in a copy of the EXAMIN-like project at A1."""
    return _update_outcome(tmp_path_factory, "updated-013", examin_013)


@pytest.fixture(scope="session")
def updated_010(examin_010, tmp_path_factory):
    """``gov update B --json`` in a copy of the project at A0 holding only the legacy lines."""
    return _update_outcome(tmp_path_factory, "updated-010", examin_010)


@pytest.fixture(scope="session")
def checked_013(examin_013, tmp_path_factory):
    """``gov update B --check --json``, then ``gov update B --check``, in a copy of the EXAMIN-like project."""
    return _update_outcome(tmp_path_factory, "checked-013", examin_013, ("--check",), text_form=True)


@pytest.fixture(scope="session")
def losing_013(examin_013, tmp_path_factory):
    """``gov update B --json`` in a copy of the EXAMIN-like project, a fixture rulesync first on PATH that loses the
    owner's deny line at the regeneration (F2)."""
    real = support.rulesync_version()[0]
    return _update_outcome(tmp_path_factory, "losing-013", examin_013,
                           first=lambda sandbox: support.owner_line_losing_rulesync(Path(sandbox.bin), real))


@pytest.fixture()
def sandbox(tmp_path):
    return support.sandbox_at(tmp_path / "sandbox")

