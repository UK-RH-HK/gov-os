"""Unit tests for iteration tracking and escalation in gov close."""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def root(tmp_path):
    r = tmp_path / "project"
    r.mkdir()
    tickets = r / ".tickets"
    tickets.mkdir()
    front = {
        "id": "T-0001", "status": "open", "wbs_id": "W1-test",
        "profile": "STANDARD", "allowed_paths": ["src/**"],
    }
    import yaml
    (tickets / "T-0001.md").write_text(
        "---\n" + yaml.safe_dump(front) + "---\n", encoding="utf-8")
    return r


class TestIterationTracking:
    def test_first_failure_creates_iteration_file(self, root):
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        iter_file = root / ".gov-runtime" / "iterations" / "T-0001.json"
        assert iter_file.is_file()
        data = json.loads(iter_file.read_text())
        assert data["count"] == 1

    def test_same_failure_increments_count(self, root):
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        _handle_failure(root, "T-0001", ["test failed"], {})
        iter_file = root / ".gov-runtime" / "iterations" / "T-0001.json"
        data = json.loads(iter_file.read_text())
        assert data["count"] == 2

    def test_different_failure_resets_count(self, root):
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["failure A"], {})
        _handle_failure(root, "T-0001", ["failure B"], {})
        iter_file = root / ".gov-runtime" / "iterations" / "T-0001.json"
        data = json.loads(iter_file.read_text())
        assert data["count"] == 1

    def test_escalation_after_three_non_converging(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        _handle_failure(root, "T-0001", ["test failed"], {})
        with pytest.raises(GovError) as exc:
            _handle_failure(root, "T-0001", ["test failed"], {})
        assert exc.value.code == "ESCALATION_BLOCKED"
        assert exc.value.exit_code == 4

    def test_escalation_has_six_options(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        _handle_failure(root, "T-0001", ["test failed"], {})
        with pytest.raises(GovError) as exc:
            _handle_failure(root, "T-0001", ["test failed"], {})
        options = set(exc.value.details.get("options", []))
        expected = {"fix_differently", "narrow", "split", "defer", "delete", "continue"}
        assert expected <= options

    def test_escalation_writes_file(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        _handle_failure(root, "T-0001", ["test failed"], {})
        with pytest.raises(GovError):
            _handle_failure(root, "T-0001", ["test failed"], {})
        esc_file = root / ".gov-runtime" / "escalations" / "T-0001.json"
        assert esc_file.is_file()
        data = json.loads(esc_file.read_text())
        assert "outcomes" in data
        assert len(data["outcomes"]) >= 3

    def test_outcomes_are_distinct(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _handle_failure

        _handle_failure(root, "T-0001", ["test failed"], {})
        _handle_failure(root, "T-0001", ["test failed"], {})
        with pytest.raises(GovError) as exc:
            _handle_failure(root, "T-0001", ["test failed"], {})
        outcomes = exc.value.details.get("outcomes", [])
        iterations = [o.get("iteration") for o in outcomes]
        assert len(set(iterations)) == len(iterations)
