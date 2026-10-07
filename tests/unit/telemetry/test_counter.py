"""Builder tests for ``gov telemetry`` (W1-31). Regression evidence only (DEC-136).

No test reads a real session log: ``ccusage`` is a stand-in script in a temporary folder, and ``HOME`` and
``CLAUDE_CONFIG_DIR`` are temporary.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.errors import GovError  # noqa: E402
from gov.telemetry import command, counter  # noqa: E402
from gov.telemetry.counter import NOT_MEASURED  # noqa: E402

TICKET, SESSION = "PROJ-aaaa", "11111111-1111-4111-8111-111111111111"


def row(**changes):
    return {"sessionId": SESSION, "inputTokens": 1500, "outputTokens": 500, "cacheCreationTokens": 0,
            "cacheReadTokens": 120000, "totalCost": 0.02, "modelsUsed": ["claude-opus-5-5"],
            "modelBreakdowns": [{"modelName": "claude-opus-5-5", "cost": 0.02}], **changes}


@pytest.fixture()
def project(tmp_path, monkeypatch):
    """A project with one ticket, and a stand-in ccusage that prints ``report.json``."""
    root = tmp_path / "project"
    (root / ".tickets").mkdir(parents=True)
    (root / ".tickets" / f"{TICKET}.md").write_text(f"---\nid: {TICKET}\nprofile: LITE\n---\n# t\n", encoding="utf-8")
    (tmp_path / "bin").mkdir()
    stand_in = tmp_path / "bin" / "ccusage"
    stand_in.write_text(f"#!/bin/sh\ncat '{tmp_path}/report.json'\n", encoding="utf-8")
    stand_in.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}/bin:/usr/bin:/bin")
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv("CLAUDE_CONFIG_DIR", str(tmp_path / "config"))
    return root


def report(project, *rows):
    (project.parent / "report.json").write_text(json.dumps({"sessions": list(rows)}), encoding="utf-8")


def test_the_share_is_a_number_only_when_every_part_was_measured():
    assert counter.share(250, 1900, 600) == 0.1
    assert counter.share(NOT_MEASURED, 1900, 600) == NOT_MEASURED
    assert counter.share(250, 0, 0) == NOT_MEASURED, "no tokens in the sessions is no denominator"


def test_undecided_sources_say_not_measured_and_the_command_ends_with_3(project):
    report(project, row())
    args = argparse.Namespace(ticket=TICKET, ticket_session=[SESSION, SESSION])
    record, code = command.run(project, args, {})
    assert code == command.EXIT_NOT_MEASURED == 3 and record["governance_share"] == NOT_MEASURED
    assert record["governance_tokens"] == {**dict.fromkeys(counter.SOURCES, NOT_MEASURED), "total": NOT_MEASURED}
    assert record["not_measured"] == list(counter.SOURCES), "a ticket without a record is not a count of 0"
    assert (record["tokens_in"], record["tokens_out"], record["profile"]) == (1500, 500, "LITE"), "named once"
    assert record["sandbox_system_prompt_tokens"] == NOT_MEASURED and 3250 not in record.values()


def test_a_cost_without_a_price_for_every_model_is_not_measured(project):
    report(project, row(modelBreakdowns=[{"modelName": "a", "cost": 0.02},
                                         {"modelName": "b", "cost": 0.0, "missingPricing": True}]))
    record = counter.measure(project, TICKET, [SESSION])
    assert record["cost"] == NOT_MEASURED == record["sessions"][0]["cost"]
    assert record["cache_read_tokens"] == 120000


@pytest.mark.parametrize("rows", [[], [row(), row()], [row(outputTokens=None)], [row(inputTokens=True)]],
                         ids=["no row", "two rows", "a figure absent", "a figure that is no count"])
def test_a_session_ccusage_did_not_measure_refuses(project, rows):
    report(project, *rows)
    with pytest.raises(GovError) as refusal:
        counter.measure(project, TICKET, [SESSION])
    assert refusal.value.code == "SESSIONS_NOT_MEASURED"
