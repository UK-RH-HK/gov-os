"""``gov queue --full --dry-run`` (L2-4, DAEO-j9z6): no selection is computed for a full run, so its ``select.json``
holds no ``unplaced_base`` key, and the dry run still answers as the landing does."""
from __future__ import annotations

import json

from gov.queue import command

from queue_support import TICKET

GREEN = {"src/pkg/feature.py": "def twice(x):\n    return 2 * x\n"}


def test_a_full_dry_run_exits_0_and_its_select_json_has_no_unplaced_base(project, tmp_path, monkeypatch):
    monkeypatch.setenv("PYTEST_XDIST_AUTO_NUM_WORKERS", "2")
    monkeypatch.setenv("GOV_HEAVY_CPUS", "0-1")
    project.branch("topic/a", GREEN, f"Task: {TICKET}", "Role: engineer")
    out = tmp_path / "out"
    result, code = command.dry_run(project.root, [f"{TICKET}=topic/a"], out=str(out), full=True)
    assert code == 0 and result["landed"] == [TICKET] and result["dry_run"] is True
    chosen = json.loads((out / "select.json").read_text(encoding="utf-8"))
    assert chosen["suites"] and "unplaced_base" not in chosen, chosen
