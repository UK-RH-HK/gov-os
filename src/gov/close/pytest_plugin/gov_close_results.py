"""The pytest plugin that tells ``gov close`` the result of each test of a run, for the path map's lists of
DEC-757 (``accepted_reds``, ``load_sensitive``): ``gov close`` gives it to every run of a project that has one.

At the end of the session it writes, to the file ``GOV_CLOSE_RESULTS_TO`` names, one JSON object: the run's root
folder as pytest took it, and each test's node id relative to the project's root (``GOV_CLOSE_RESULTS_OF``) with
``passed``, ``failed``, ``error`` (its setup or teardown failed) or ``skipped``. Under a parallel run only the
controller writes, from the reports its workers send. The module imports nothing but the standard library.
"""

from __future__ import annotations

import json
import os

PLUGIN = "gov_close_results"
TO_VARIABLE = "GOV_CLOSE_RESULTS_TO"
ROOT_VARIABLE = "GOV_CLOSE_RESULTS_OF"

_config = None
_results: dict[str, str] = {}


def pytest_configure(config) -> None:
    global _config
    _config = config


def _node(nodeid: str) -> str:
    path, sep, rest = nodeid.partition("::")
    full = os.path.join(str(_config.rootpath), path)
    return os.path.relpath(full, os.environ[ROOT_VARIABLE]).replace(os.sep, "/") + sep + rest


def pytest_runtest_logreport(report) -> None:
    if _config is None or hasattr(_config, "workerinput") or not os.environ.get(TO_VARIABLE):
        return
    node = _node(report.nodeid)
    if report.failed:
        _results[node] = "failed" if report.when == "call" else "error"
    elif report.skipped and node not in _results:
        _results[node] = "skipped"
    elif report.passed and report.when == "call" and node not in _results:
        _results[node] = "passed"


def pytest_sessionfinish(session) -> None:
    to = os.environ.get(TO_VARIABLE)
    if not to or hasattr(session.config, "workerinput"):
        return
    with open(to, "w", encoding="utf-8") as handle:
        json.dump({"rootdir": str(session.config.rootpath), "results": _results}, handle)
