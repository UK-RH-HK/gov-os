"""Builder tests for the research role's install exception (W1-46, DEC-163, DEC-240).

Regression evidence only (DEC-136): the cases of ``cd`` the acceptance tests
leave to the builder, and the shapes of a ticket that give no experiment folder.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.guard.install import experiment_folder, install_in_experiment_folder  # noqa: E402

FOLDER = "experiments/exp-1"


def _project(root, allowed=(f"{FOLDER}/**",), role="research", status="in_progress"):
    (root / FOLDER / "sub").mkdir(parents=True)
    (root / "experiments/exp-2").mkdir()
    (root / ".tickets").mkdir()
    paths = "".join(f"- {entry}\n" for entry in allowed)
    (root / ".tickets/T-1.md").write_text(
        f"---\nid: T-1\nstatus: {status}\nrole: {role}\nallowed_paths:\n{paths}---\n", encoding="utf-8")
    return str(root)


def test_the_experiment_folder_is_the_tickets_single_entry(tmp_path):
    root = _project(tmp_path)
    assert experiment_folder(root, "T-1") == os.path.realpath(tmp_path / FOLDER)


@pytest.mark.parametrize("kwargs", (
    {"allowed": (FOLDER,)}, {"allowed": ("/**",)}, {"allowed": ("experiments/missing/**",)},
    {"allowed": ("../outside/**",)}, {"role": "engineer"}, {"status": "open"},
))
def test_another_shape_gives_no_experiment_folder(tmp_path, kwargs):
    root = _project(tmp_path, **kwargs)
    assert experiment_folder(root, "T-1") is None
    assert not install_in_experiment_folder("uv sync", str(tmp_path / FOLDER), root, "T-1")


@pytest.mark.parametrize("command, cwd, inside", (
    ("uv sync", FOLDER, True),
    ("uv sync", f"{FOLDER}/sub", True),
    ("uv sync", "experiments/exp-10", False),
    (f"cd {FOLDER} && uv sync", ".", True),
    (f"cd {FOLDER}; uv sync", ".", True),
    ("cd .. && uv sync", f"{FOLDER}/sub", True),
    ("cd ../exp-2 && uv sync", FOLDER, False),
    (f"cd {FOLDER} && cd .. && uv sync", ".", False),
    (f"cd {FOLDER} && pushd .. && uv sync", ".", False),
    ("uv sync && cd ..", FOLDER, False),
    ("cd $W1_46_UNSET && uv sync", FOLDER, False),
    ("cd && uv sync", FOLDER, False),
    (f"cd -P {FOLDER} && uv sync", ".", False),
))
def test_inside_the_folder_is_the_working_directory_or_a_first_cd(tmp_path, command, cwd, inside):
    root = _project(tmp_path)
    (tmp_path / "experiments/exp-10").mkdir()
    assert install_in_experiment_folder(command, str(tmp_path / cwd), root, "T-1") is inside


def test_no_ticket_is_never_inside(tmp_path):
    root = _project(tmp_path)
    assert not install_in_experiment_folder("uv sync", str(tmp_path / FOLDER), root, None)
