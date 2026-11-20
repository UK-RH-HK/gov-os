"""W2-17 fix S5 (DEC-1223 (6)): doctor's part ``updates``. Builder evidence; the other parts are stubbed."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

from gov.doctor import command as doctor

STUBBED = ("tools", "hooks", "path_map", "path_compliance", "index_freshness", "canaries", "framework_lock",
           "install", "isolation", "claude_code", "held_out", "templates")


def _run(root: Path, part: dict):
    stubs = [mock.patch.object(doctor, f"_check_{name}", return_value={"status": "pass"}) for name in STUBBED]
    stubs.append(mock.patch.object(doctor, "_check_updates", return_value=part))
    stubs.append(mock.patch.object(doctor, "_check_adoption_level", return_value={"status": "pass"}))
    for stub in stubs:
        stub.start()
    try:
        return doctor.run(root, None, {})
    finally:
        mock.patch.stopall()


def test_check_updates_is_the_pending_reading_of_the_project(tmp_path):
    with mock.patch("gov.update.pending.pending", return_value={"status": "report", "pending": False}) as read:
        assert doctor._check_updates(tmp_path) == {"status": "report", "pending": False}
    read.assert_called_once_with(tmp_path)


def test_the_updates_part_is_in_the_report_and_a_pending_update_never_makes_doctor_unhealthy(tmp_path):
    part = {"status": "report", "held": "1.0.0", "newest": "1.0.1", "pending": True, "kind": "patch", "fixes": 1,
            "next": "at the next quiet point", "summary": "update pending"}
    result = _run(tmp_path, part)
    assert result["healthy"] is True and result["updates"] == part


def test_a_failing_read_is_a_part_that_reports_nothing_pending_not_a_failed_doctor(tmp_path):
    with mock.patch("gov.update.pending.pending", side_effect=RuntimeError("boom")):
        part = doctor._check_updates(tmp_path)
    assert part["status"] == "report" and part["pending"] is False and "boom" in part["reason"]
