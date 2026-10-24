"""W2-67 batch 6's plants for KPI 4's static guard (P-W2-67-TD4-A): a pytest plugin, loaded with ``-p td6_guard_plant``.

``GOV_TD6_GUARD_PLANT`` names the plant; nothing is written under ``tests/``:

- ``other``: the guard's source list gains one more source, ``fstring_basetemp_source.py`` in this folder (under the
  worktree's ``.gov-runtime/scratch/``), whose argument list passes ``f"--basetemp={folder}"``.
- ``refusal-<n>``: the guard reads a scratch root (``root-<n>/`` in this folder) that holds only a copy of the
  refusal cases' file with change ``<n>`` of ``CHANGES`` (``0`` is the unchanged copy, the control).
"""

import os
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLANT = os.environ.get("GOV_TD6_GUARD_PLANT", "")
REFUSAL = "tests/acceptance/W1-27/test_w2_67_basetemp_refusal.py"
EQUALS = '"equals": lambda given: ((f"--basetemp={given}",), None),'
CHANGES = {
    "0": (EQUALS, EQUALS),
    "1": (EQUALS, '"equals": lambda given: ((f"--basetemp={given.parent}",), None),'),
    "2": (EQUALS, '"equals": lambda given: ((f"--basetemp=/tmp/fixed-{given}",), None),'),
    "3": (EQUALS, '"equals": lambda given: ((f"--basetemp={given!s}",), None),'),
    "4": ("SERIAL_FORMS = (", 'EXTRA = (f"--basetemp={REPO_ROOT}",)\nSERIAL_FORMS = ('),
    "5": (EQUALS, '"equals": lambda given: ((f"--basetemp",), None),'),
}
_saved = {}


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    module = item.module
    if not PLANT or not hasattr(module, "_round_1_sources"):
        return
    if PLANT == "other":
        original = module._round_1_sources

        def planted():
            yield from original()
            yield HERE / "fstring_basetemp_source.py"
        _saved["_round_1_sources"] = original
        module._round_1_sources = planted
    elif PLANT.startswith("refusal-"):
        old, new = CHANGES[PLANT.split("-", 1)[1]]
        text = (Path(module.REPO_ROOT) / REFUSAL).read_text(encoding="utf-8")
        assert text.count(old) == 1, f"the change's anchor is not once in the refusal file: {old}"
        root = HERE / f"root-{PLANT.split('-', 1)[1]}"
        copy = root / REFUSAL
        copy.parent.mkdir(parents=True, exist_ok=True)
        copy.write_text(text.replace(old, new), encoding="utf-8")
        _saved["REPO_ROOT"] = module.REPO_ROOT
        module.REPO_ROOT = root


def pytest_runtest_teardown(item):
    for name, value in _saved.items():
        setattr(item.module, name, value)
    _saved.clear()
