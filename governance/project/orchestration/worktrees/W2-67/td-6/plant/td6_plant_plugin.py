"""W2-67 batch 6's plant carrier (a pytest plugin, loaded with ``-p td6_plant_plugin``; never under ``tests/``).

It changes no test and no source file. Before each case's fixtures are set up it wraps ``w1_30_support.sandbox_env``,
the environment of every ``gov`` process a W1-30 case starts, so that the plant's ``site`` folder comes first on
that process's ``PYTHONPATH``: Python then imports the plant's ``sitecustomize``, which applies the one fault
``GOV_TD6_PLANT`` names to ``gov.close`` as it loads, and writes a line to ``GOV_TD6_MARKER`` each time the planted
behaviour runs. ``gov close`` gives its own nested test runs a ``PYTHONPATH`` of the project's ``src/`` only, so
the plant lives in the ``gov close`` process alone, where every fault of lens I2's table lives.
"""

import os
import sys
from pathlib import Path

import pytest

SITE = str(Path(__file__).resolve().parent / "site")
PASSED_ON = ("GOV_TD6_PLANT", "GOV_TD6_MARKER")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    support = sys.modules.get("w1_30_support")
    if support is None or getattr(support, "_td6_planted", False):
        return
    original = support.sandbox_env

    def planted_env(sandbox):
        env = original(sandbox)
        env["PYTHONPATH"] = SITE + os.pathsep + env["PYTHONPATH"]
        env.update({key: os.environ[key] for key in PASSED_ON if key in os.environ})
        return env

    support.sandbox_env = planted_env
    support._td6_planted = True
