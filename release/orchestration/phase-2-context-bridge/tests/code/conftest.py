import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repobuilder  # noqa: E402

# BR-AR-0019 reopening (fourth pass): govbridge.authority's own package __init__ reads config/state-aliases.yaml
# EAGERLY, at import time (govbridge/authority/classes.py, outside this node's mutation scope) -- a one-time,
# process-wide side effect the first time ANYTHING imports govbridge.authority (Python caches a successful module
# import; the module body never re-runs). govbridge/code/lineage_layer.py and govbridge/graph/derive.py both need
# govbridge.authority (id-grammar resolution), so a test file here that happens to run FIRST in a given pytest
# invocation -- with GOV_BRIDGE_DOMAIN already monkeypatched to a synthetic tmp_path repo that has no
# config/state-aliases.yaml of its own -- would otherwise crash on that import, non-hermetically (BR-DAG-AMEND-
# R1-4: no test-order/selection dependency). Importing it here, at COLLECTION time, before any fixture or
# monkeypatch has run, guarantees the successful, cached import happens against the REAL domain's own real
# config/state-aliases.yaml, once, regardless of which test file or test method pytest happens to run first.
import govbridge.authority  # noqa: E402,F401


@pytest.fixture(autouse=True)
def _isolated_store(tmp_path, monkeypatch):
    """Every test gets its own store -- never the real BR-AR-0005 store, and never another test's (tmp_path is
    unique per test). Mirrors tests/core/conftest.py's _no_env_leak intent for this node's own tests."""
    monkeypatch.setenv("GOVBRIDGE_STORE", str(tmp_path / "store"))


@pytest.fixture
def repo(tmp_path):
    root = tmp_path / "repo"
    _repobuilder.init(root)
    return root
