"""Builder tests for W2-153 S-ADOPTED (DEC-1192 (2)): doctor's ``templates`` part names a missing or a differing
copy under ``.claude/templates/`` of the kernel's templates. Regression evidence only; no installed tool is needed."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from gov.adapters import portability
from gov.doctor import command as doctor

KIT = Path(__file__).resolve().parents[3] / "template" / "governance" / "kernel" / "templates"


def rel(stem):
    return f".claude/templates/{stem}.md"


@pytest.fixture()
def repo(tmp_path):
    kernel = tmp_path / "governance" / "kernel" / "templates"
    kernel.mkdir(parents=True)
    copies = tmp_path / ".claude" / "templates"
    copies.mkdir(parents=True)
    for stem in portability.TEMPLATE_COPIES:
        shutil.copyfile(KIT / f"{stem}.md", kernel / f"{stem}.md")
        shutil.copyfile(KIT / f"{stem}.md", copies / f"{stem}.md")
    return tmp_path


def test_all_copies_present_and_equal_pass(repo):
    assert doctor._check_templates(repo) == {"status": "pass"}


def test_a_missing_and_a_differing_copy_drift_and_are_named(repo):
    (repo / rel("role-lead")).unlink()
    (repo / rel("role-engineer")).write_text("edited\n")
    part = doctor._check_templates(repo)
    assert part["status"] == "drift"
    assert part["missing"] == [rel("role-lead")] and part["differing"] == [rel("role-engineer")]
    assert rel("role-lead") in part["reason"] and rel("role-engineer") in part["reason"]
    assert "gov adapters generate" in part["reason"]


def test_no_kernel_templates_folder_is_unmeasured(repo):
    shutil.rmtree(repo / "governance" / "kernel" / "templates")
    part = doctor._check_templates(repo)
    assert part["status"] == "unmeasured" and isinstance(part["reason"], str) and part["reason"]


def test_run_carries_the_part_and_fails_on_drift(repo, monkeypatch):
    from gov.cli.errors import GovError
    for name in ("_check_tools", "_check_hooks", "_check_path_compliance", "_check_index_freshness",
                 "_check_canaries", "_check_framework_lock", "_check_isolation", "_check_claude_code",
                 "_check_held_out"):
        monkeypatch.setattr(doctor, name, lambda root: {"status": "pass"})
    monkeypatch.setattr(doctor, "_check_path_map", lambda root, config: {"status": "pass"})
    result = doctor.run(repo, None, {})
    assert result["templates"] == {"status": "pass"} and result["healthy"] is True
    (repo / rel("brief")).unlink()
    with pytest.raises(GovError) as caught:
        doctor.run(repo, None, {})
    assert caught.value.code == "DOCTOR_UNHEALTHY" and "templates (" in str(caught.value)
