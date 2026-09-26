import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _repobuilder  # noqa: E402

# BR-DAG-AMEND-R1-12 (R1-XC): the collection-time `import govbridge.authority` this file used to carry (BR-AR-0019
# reopening, fourth pass) is REMOVED. It existed only to win a race: govbridge.authority.classes used to read
# config/state-aliases.yaml EAGERLY, at import time, against whatever GOV_BRIDGE_DOMAIN happened to be active then
# -- a one-time, process-wide side effect the first time ANYTHING imports govbridge.authority. govbridge/code/
# lineage_layer.py and govbridge/graph/derive.py both need govbridge.authority (id-grammar resolution), so a test
# file here that happened to run FIRST, with GOV_BRIDGE_DOMAIN already monkeypatched to a synthetic tmp_path repo
# with no config/state-aliases.yaml of its own, would otherwise have crashed on that import. Importing
# govbridge.authority here, at COLLECTION time, forced the real domain's value to win the race instead -- a
# workaround for the race, not a fix for the process-global import-time read that caused it (of the same class as
# the gitobj.repo_root cache, BR-DAG-AMEND-R1-6). govbridge.authority.classes.BRIDGE_STATE_PATH is now a lazy
# module attribute (PEP 562 `__getattr__`, computed and cached on first ACCESS, never at import time), so merely
# importing govbridge.authority no longer touches the filesystem at all -- there is no more race for this
# collection-time import to win, so it is deleted rather than kept as a no-op.


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
