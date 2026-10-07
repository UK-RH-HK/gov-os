"""Builder tests for ``gov ci checks`` (W1-40): regression evidence only. The hook cases are the acceptance suite's."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.ci import command  # noqa: E402
from gov.cli.checks import CHECKS_DIR  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402


def _declare(root, tier, command_line, severity="hard-block"):
    path = root / CHECKS_DIR / f"check-{tier.lower()}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"id": f"check-{tier.lower()}", "family": "schema/invariants", "tier": tier,
                                    "severity": severity, "command": command_line}), encoding="utf-8")


def test_only_the_tiers_named_run(tmp_path):
    _declare(tmp_path, "G1", "true")
    _declare(tmp_path, "G3", "touch ran-g3; false")
    assert command._checks(tmp_path, ["G1", "G2"])["checks"] == {"check-g1": "GREEN"}
    assert not (tmp_path / "ran-g3").exists()


def test_a_red_hard_block_check_refuses_with_exit_code_3(tmp_path):
    _declare(tmp_path, "G2", "false")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, ["G1", "G2"])
    assert (refused.value.code, refused.value.exit_code) == ("CHECK_FAILED", 3)


def test_no_check_of_the_tiers_is_not_a_pass(tmp_path):
    _declare(tmp_path, "G3", "true")
    with pytest.raises(GovError) as refused:
        command._checks(tmp_path, ["G1", "G2"])
    assert refused.value.code == command.NOT_MEASURED
