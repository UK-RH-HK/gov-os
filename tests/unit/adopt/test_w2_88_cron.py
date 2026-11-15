"""W2-88 run 8b, items 21-22 and 24 (DEC-893: no unfilled ``<...>`` slot in an operator command): step 6's cron script
ships inside the wheel and step 6 names its path found by ``fabric.shipped`` only; with no gitleaks on the PATH, step 6
names ``GITLEAKS_MISSING`` and holds no line, and A9's record names it.

Regression evidence only (DEC-136).
"""
from __future__ import annotations

import stat
from pathlib import Path

import pytest

from gov.adopt import fabric, memory_sets
from gov.cli.errors import GovError

REPO = Path(__file__).resolve().parents[3]
COPY = REPO / "src/gov/_shipped" / memory_sets.CRON
AUDIT = "memory-audit-20261115"


def step_6(out, monkeypatch, scanner, root=None):
    monkeypatch.setattr(memory_sets.shutil, "which", lambda name, *a, **k: scanner if name == "gitleaks" else None)
    made = memory_sets.variants(REPO / memory_sets.BRIEFS, {}, [])
    act = memory_sets.walls_act(out, sets_root="/srv/sets", audit=AUDIT, made=made, blind=["x/**"], root=root,
                                repo="/srv/adopted")
    return next(line for line in (act / "ACT.md").read_text().splitlines() if line.startswith("6. "))


def test_the_shipped_cron_script_equals_its_source_and_runs_from_cron():
    assert COPY.read_bytes() == (REPO / memory_sets.CRON).read_bytes()
    assert COPY.stat().st_mode & stat.S_IXUSR  # cron runs the path itself: the copy keeps its executable mode


def test_the_cron_script_is_package_data():
    text = (REPO / "pyproject.toml").read_text()
    assert f'"_shipped/{memory_sets.CRON}"' in text and memory_sets.CRON in fabric.PACKAGED


def no_tree(monkeypatch, package):
    monkeypatch.setattr(fabric, "_source_tree", lambda start=None: None)
    monkeypatch.setattr(fabric, "_package_copy", lambda: package)


def test_from_a_package_with_no_source_tree_step_6_names_the_packages_copy(tmp_path, monkeypatch):
    package = tmp_path / "site-packages/gov/_shipped"
    (package / memory_sets.CRON).parent.mkdir(parents=True)
    (package / memory_sets.CRON).write_bytes(COPY.read_bytes())
    for rel in (memory_sets.WALLS,):
        (package / rel).mkdir(parents=True)
    no_tree(monkeypatch, package)
    step = step_6(tmp_path / "out", monkeypatch, "/opt/bin/gitleaks", root=tmp_path / "project")
    assert f" {package / memory_sets.CRON} --repo /srv/adopted`" in step
    assert "<" not in step.split("`")[1]  # the line itself holds no slot


def test_with_the_copy_missing_too_step_6_is_refused_shipped_file_missing(tmp_path, monkeypatch):
    package = tmp_path / "site-packages/gov/_shipped"
    (package / memory_sets.WALLS).mkdir(parents=True)
    no_tree(monkeypatch, package)
    with pytest.raises(GovError) as raised:
        step_6(tmp_path / "out", monkeypatch, "/opt/bin/gitleaks", root=tmp_path / "project")
    err = raised.value
    assert err.code == "SHIPPED_FILE_MISSING" and err.details["file"] == memory_sets.CRON
    assert str(package / memory_sets.CRON) in err.message
    assert "path to Gov OS" not in Path(memory_sets.__file__).read_text()  # the placeholder fallback is gone


def test_with_gitleaks_found_step_6_names_its_absolute_path(tmp_path, monkeypatch):
    step = step_6(tmp_path / "out", monkeypatch, "/home/someone/.local/bin/gitleaks")
    assert "GOV_MEMAUDIT_GITLEAKS=/home/someone/.local/bin/gitleaks " in step.split("`")[1]
    assert memory_sets.GITLEAKS_MISSING not in step


def test_with_no_gitleaks_step_6_names_gitleaks_missing_and_holds_no_slot(tmp_path, monkeypatch):
    step = step_6(tmp_path / "out", monkeypatch, None)
    assert step.startswith(f"6. `{memory_sets.GITLEAKS_MISSING}`") and "<" not in step
    assert "0 21 * * 1" not in step  # no cron line is given
    assert "push stays blocked" in step and "run A9 again" in step and "Install gitleaks" in step
    assert memory_sets.gitleaks_missing() is True


def test_a9s_record_names_gitleaks_missing_and_is_not_refused_for_it(tmp_path, monkeypatch, stand_ins, tool):
    tool(graph_of({"main.py": {"CALLS": 1}}))
    monkeypatch.setattr(memory_sets.shutil, "which", lambda name, *a, **k: None)
    root, run = a9(tmp_path, monkeypatch)
    result = run()
    assert result["ok"] is True
    audit = head(root, result)["audit"]
    assert audit["gitleaks"] == memory_sets.GITLEAKS_MISSING and audit["act"] == "memory-audit/ACT-WALLS/ACT.md"
    step = next(line for line in (Path(result["out"]) / "memory-audit/ACT-WALLS/ACT.md").read_text().splitlines()
                if line.startswith("6. "))
    assert memory_sets.GITLEAKS_MISSING in step and "<" not in step


from .test_w2_88_fabric import stand_ins  # noqa: E402,F401  (a fixture)
from .test_w2_88_f1 import a9, graph_of, head, tool  # noqa: E402,F401  (tool is a fixture)
