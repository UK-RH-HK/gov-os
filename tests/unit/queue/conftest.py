"""Fixtures of gov queue's unit tests: a planted project (``queue_support``)."""
from __future__ import annotations

import os

import pytest

from queue_support import Repo, plant


@pytest.fixture
def project(tmp_path, monkeypatch) -> Repo:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", os.devnull)
    monkeypatch.delenv("GOV_ROLE", raising=False)
    return plant(tmp_path)
