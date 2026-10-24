"""The one case ``test_w2_67_sweep_namespaces.py`` starts in a nested pytest of this repository (W2-67, batch 5).

Its name does not start with ``test_``, so a run of ``tests`` never collects it; the nested run names it, from the
repository's root, so the root ``tests/conftest.py`` is loaded. What it does is read from ``W2_67_NS_MODE``:

- ``pass``: writes one file in its temp folder and passes (the sweeping run).
- ``hold-setup``: a session fixture makes the run's base folder, writes its path to the ready file and waits for the
  release file, all before the case's own temp folder: a run still in its first test's setup.
- ``hold-call``: the case writes in its temp folder, writes the base folder's path to the ready file and waits for
  the release file: a run in the middle of a test.
- ``hold-teardown``: the case has run; the session fixture's teardown writes the ready file and waits for the release
  file: a run in its last teardown, before pytest's own end.
- ``kill-setup``, ``kill-call``: as ``hold-setup`` and ``hold-call``, but the run ends its own process with SIGKILL
  where it would wait: a killed run, whose ``.lock`` stays.

A run that waits fails when its base folder or its temp folder vanished while it waited, or when no release came
within ``HOLD_S`` seconds (so a lost case never hangs).
"""

import os
import signal
import time
from pathlib import Path

import pytest

MODE = os.environ.get("W2_67_NS_MODE", "pass")
READY = os.environ.get("W2_67_NS_READY", "")
RELEASE = os.environ.get("W2_67_NS_RELEASE", "")
HOLD_S = 150


def _ready(base):
    part = Path(READY + ".part")
    part.write_text(f"{base}\n", encoding="utf-8")
    os.replace(part, READY)


def _hold(base, where):
    """Say the run got here, then wait for the release (or die by SIGKILL, in a ``kill-`` mode)."""
    _ready(base)
    if MODE.startswith("kill-"):
        os.kill(os.getpid(), signal.SIGKILL)
    deadline = time.monotonic() + HOLD_S
    while not Path(RELEASE).exists():
        if time.monotonic() > deadline:
            pytest.fail(f"no release within {HOLD_S} s")
        time.sleep(0.05)
    assert base.is_dir(), f"the run's base folder {base} vanished while the run was {where}"


@pytest.fixture(scope="session")
def held(tmp_path_factory):
    if MODE in ("hold-setup", "kill-setup"):
        _hold(tmp_path_factory.getbasetemp(), "in its first test's setup")
    yield
    if MODE == "hold-teardown":
        _hold(tmp_path_factory.getbasetemp(), "in its last teardown")


def test_probe(held, tmp_path, tmp_path_factory):
    (tmp_path / "probe.txt").write_text("W2-67 batch 5\n", encoding="utf-8")
    if MODE in ("hold-call", "kill-call"):
        _hold(tmp_path_factory.getbasetemp(), "in the middle of a test")
        assert (tmp_path / "probe.txt").is_file(), f"the run's temp folder {tmp_path} vanished in the middle of a test"
    assert (tmp_path / "probe.txt").is_file()
