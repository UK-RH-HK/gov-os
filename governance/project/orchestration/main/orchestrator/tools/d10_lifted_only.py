"""A pytest plugin for D-10's report-only `lifted` step: after tests/conftest.py's own selection (run with
--optin=lifted), keep only the items the `lifted` lists name, matched by the conftest's own optin_left_out, so the
default cases sharing a file with a lifted entry are not run a second time. Load with `-p d10_lifted_only` and this
folder on PYTHONPATH. Changes nothing in the repository."""
from pathlib import Path

import pytest


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(config, items):
    cf = next((p for p in config.pluginmanager.get_plugins()
               if hasattr(p, "optin_entries") and hasattr(p, "optin_left_out") and hasattr(p, "optin_name")), None)
    if cf is None:
        raise pytest.UsageError("d10_lifted_only: tests/conftest.py's opt-in functions were not found")
    lifted = [e for e in cf.optin_entries() if cf.optin_name(Path(e[2])) == "lifted"]
    keep = {id(i) for i in cf.optin_left_out(items, lifted)}
    gone = [i for i in items if id(i) not in keep]
    if gone:
        items[:] = [i for i in items if id(i) in keep]
        config.hook.pytest_deselected(items=gone)
