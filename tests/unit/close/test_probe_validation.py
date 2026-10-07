"""Unit tests for probe-record validation in gov close."""
from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml


def _make_probe(root: Path, ticket: str, **overrides) -> Path:
    defaults = {
        "id": f"PR-{ticket}",
        "type": "probe",
        "status": "ACTIVE",
        "state_class": "NARRATIVE",
        "task": ticket,
        "reviewer_session": "reviewer-001",
        "implementer_session": "impl-001",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator",
        "judged_by": "orchestrator",
        "judgement": "pass",
    }
    defaults.update(overrides)
    probe_dir = root / "docs" / "probes" / ticket
    probe_dir.mkdir(parents=True, exist_ok=True)
    path = probe_dir / f"PR-{ticket}.md"
    text = "---\n" + yaml.safe_dump(defaults, sort_keys=False) + "---\n\n"
    path.write_text(text, encoding="utf-8")
    return path


@pytest.fixture
def root(tmp_path):
    return tmp_path / "project"


class TestCommissionedBy:
    def test_rejects_non_orchestrator(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _check_probe

        _make_probe(root, "T-0001", commissioned_by="engineer")
        with pytest.raises(GovError) as exc:
            _check_probe(root, "T-0001")
        assert exc.value.code == "PROBE_INVALID"
        assert "commissioned_by" in exc.value.message

    def test_accepts_orchestrator(self, root):
        from gov.close.command import _check_probe

        _make_probe(root, "T-0001", commissioned_by="orchestrator")
        _check_probe(root, "T-0001")


class TestJudgedBy:
    def test_rejects_non_orchestrator(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _check_probe

        _make_probe(root, "T-0001", judged_by="engineer")
        with pytest.raises(GovError) as exc:
            _check_probe(root, "T-0001")
        assert exc.value.code == "PROBE_INVALID"
        assert "judged_by" in exc.value.message

    def test_accepts_orchestrator(self, root):
        from gov.close.command import _check_probe

        _make_probe(root, "T-0001", judged_by="orchestrator")
        _check_probe(root, "T-0001")


class TestMalformedProbe:
    def test_malformed_yaml_raises(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _check_probe

        probe_dir = root / "docs" / "probes" / "T-0001"
        probe_dir.mkdir(parents=True, exist_ok=True)
        (probe_dir / "PR-T-0001.md").write_text(
            "---\ninvalid: yaml: [broken\n---\n", encoding="utf-8")
        with pytest.raises(GovError) as exc:
            _check_probe(root, "T-0001")
        assert exc.value.code == "PROBE_INVALID"
        assert "malformed" in exc.value.message.lower()

    def test_no_frontmatter_raises(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _check_probe

        probe_dir = root / "docs" / "probes" / "T-0001"
        probe_dir.mkdir(parents=True, exist_ok=True)
        (probe_dir / "PR-T-0001.md").write_text(
            "plain text, not yaml frontmatter\n", encoding="utf-8")
        with pytest.raises(GovError) as exc:
            _check_probe(root, "T-0001")
        assert exc.value.code == "PROBE_INVALID"

    def test_missing_probe_dir_raises(self, root):
        from gov.cli.errors import GovError
        from gov.close.command import _check_probe

        with pytest.raises(GovError) as exc:
            _check_probe(root, "T-0001")
        assert exc.value.code == "PROBE_MISSING"
