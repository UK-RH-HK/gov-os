"""Fixtures for the W2-05 acceptance tests (DAEO-0z8c)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import w2_05_support as support  # noqa: E402


skip_without = support.skip_without


@pytest.fixture(scope="session")
def code_under_test():
    """The ``gov`` the cases start is this worktree's ``src/`` (DEC-732)."""
    assert (support.SRC / "gov" / "__init__.py").is_file(), f"no gov package under {support.SRC}"
    return support.SRC


@pytest.fixture(autouse=True)
def no_process_left(tmp_path):
    """At the end of every case, no process it started is left running under its temporary folder."""
    yield
    support.reap(tmp_path)


@pytest.fixture()
def box(tmp_path, code_under_test):
    skip_without("git")
    return support.Box(tmp_path / "box")


@pytest.fixture()
def ollama():
    """W1-21's stand-in embeddings endpoint on a loopback port."""
    import w1_21_support as w121
    server = w121.OllamaStandIn()
    yield server
    server.close()


@pytest.fixture()
def tiers(tmp_path):
    """A stand-in dev-tier folder built from scratch (DEC-723: ``GOV_DEV_TIERS`` names it; no workbench)."""
    skip_without("sqlite_vec")
    return support.build_tiers(tmp_path / "dev")


@pytest.fixture()
def retrieval_env(box, ollama, tiers):
    """The environment the retrieval-regression check measures in: the stand-in endpoint and dev tiers."""
    return box.env(OLLAMA_HOST=ollama.host, GOV_DEV_TIERS=tiers)


@pytest.fixture()
def decoy(tmp_path):
    """A repository nothing may touch, and its fingerprint taken now."""
    repo = support.make_decoy(tmp_path / "elsewhere")
    return repo, support.folder_fingerprint(repo)


@pytest.fixture()
def fifo_cleanup():
    """Fifos a case put in place of a git file: at the end every git still waiting on one is let go."""
    fifos = []
    yield fifos
    for fifo in fifos:
        for _ in range(50):
            try:
                handle = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
            except OSError:
                break
            os.close(handle)
        try:
            os.unlink(fifo)
        except OSError:
            pass
