"""Builder tests for W2-201 fix X7 (DEC-1219 (5)): the registry entry carries the launch's kind and line.

Regression evidence only: the helper that gives the entry its kind keys, for a worker (from its plan) and a lead
(from ``build_lead_settings``'s env values).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.launch import launcher  # noqa: E402


def test_a_worker_fix_or_chore_gives_its_kind_and_line():
    assert launcher._kind_key({"kind": ("fix", "the line")}, {}) == {"kind": "fix", "kind_line": "the line"}
    assert launcher._kind_key({"kind": ("chore", "tidy")}, {}) == {"kind": "chore", "kind_line": "tidy"}


def test_a_worker_feature_or_a_plan_without_a_kind_gives_neither_key():
    assert launcher._kind_key({"kind": ("feature", None)}, {}) == {}
    assert launcher._kind_key({}, {}) == {}


def test_a_lead_reads_its_env_values():
    env = {launcher.KIND_ENV: "fix", launcher.KIND_LINE_ENV: "the line", "GOV_ROLE": "orchestrator"}
    assert launcher._kind_key(None, env) == {"kind": "fix", "kind_line": "the line"}
    env = {launcher.KIND_ENV: "chore", launcher.KIND_LINE_ENV: "tidy"}
    assert launcher._kind_key(None, env) == {"kind": "chore", "kind_line": "tidy"}


def test_a_lead_feature_gives_neither_key():
    assert launcher._kind_key(None, {"GOV_ROLE": "orchestrator", "GOV_TICKET": "T"}) == {}
