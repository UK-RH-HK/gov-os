"""Fixtures of gov queue's unit tests: a planted project (``queue_support``)."""
from __future__ import annotations

import os
import site

import pytest

from queue_support import Repo, plant


@pytest.fixture
def project(tmp_path, monkeypatch) -> Repo:
    monkeypatch.setenv("PYTHONUSERBASE", site.getuserbase())  # the test runner where the home held it
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    return plant(tmp_path)
