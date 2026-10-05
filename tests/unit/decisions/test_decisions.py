"""Builder tests for the decision checker (W1-11).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: the checker reads ``HEAD`` and needs no store, a folder inside
another repository is an error, the id grammar is the kernel's, and the points
where the checker cannot tell are findings (two roles on one commit, two records
with a cited id, a ticket whose frontmatter cannot be read).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov import decisions  # noqa: E402
from gov.cli.errors import GovError  # noqa: E402
from gov.decisions import checker  # noqa: E402

ADR = "docs/adr/ADR-0001.md"
_ENV = {"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t.invalid",
        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t.invalid",
        "GIT_AUTHOR_DATE": "2026-10-04T12:00:00+00:00", "GIT_COMMITTER_DATE": "2026-10-04T12:00:00+00:00"}


def _git(root, *args):
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True,
                          env={**_ENV, "HOME": str(root)})
    return done.stdout.strip()


def _record(record_id, record_type, status, **keys):
    lines = [f"id: {record_id}", f"type: {record_type}", f"status: {status}"]
    return "---\n" + "\n".join(lines + [f"{key}: {json.dumps(value)}" for key, value in keys.items()]) + "\n---\n"


def _commit(root, files, *roles):
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "records", *[arg for role in roles for arg in ("--trailer", f"Role: {role}")])


def _codes(root):
    return [(finding["code"], finding["ids"]) for finding in decisions.check(root)]


@pytest.fixture()
def project(tmp_path):
    _git(tmp_path, "init", "-q", "-b", "main")
    _commit(tmp_path, {ADR: _record("ADR-0001", "decision", "ACTIVE")}, "owner")
    return tmp_path


def test_the_check_reads_head_and_needs_no_store(project):
    assert decisions.check(project) == []
    (project / ADR).write_text(_record("ADR-0001", "decision", "ACTIVE", superseded_by="ADR-0002"), encoding="utf-8")
    assert decisions.check(project) == []
    assert not (project / ".gov-runtime").exists()
    assert _git(project, "status", "--porcelain") == f"M {ADR}"


def test_a_folder_inside_a_repository_is_not_checked_as_a_project(project):
    with pytest.raises(GovError) as raised:
        decisions.check(project / "docs")
    assert raised.value.code == "DECISIONS_NOT_A_REPOSITORY"
    assert raised.value.details == {"root": str(project / "docs")}


def test_the_decision_id_grammar_is_the_kernel_s():
    schema = json.loads((REPO / "template/governance/kernel/schemas/common.schema.json").read_text(encoding="utf-8"))
    assert schema["$defs"]["decision_id"]["pattern"] == f"^{checker.DECISION_ID.pattern}$"


def test_a_commit_with_the_owner_s_role_and_another_is_no_approval(project):
    _commit(project, {"docs/adr/ADR-0002.md": _record("ADR-0002", "decision", "ACTIVE")}, "engineer", "owner")
    assert _codes(project) == [("ACTIVE_UNAPPROVED", ["ADR-0002"])]


def test_a_decision_file_removed_and_added_again_needs_its_own_approval(project):
    _git(project, "rm", "-q", ADR)
    _commit(project, {}, "owner")
    _commit(project, {ADR: _record("ADR-0001", "decision", "ACTIVE")}, "engineer")
    assert _codes(project) == [("ACTIVE_UNAPPROVED", ["ADR-0001"])]


def test_one_of_two_records_with_the_cited_id_that_is_no_accepted_gate_does_not_authorise(project):
    _commit(project, {
        "docs/changes/CIT-1.md": _record("CIT-1", "change", "PROPOSED", approval=["DP-1"], cit="CIT-1"),
        "docs/packages/a.md": _record("DP-1", "decision-package", "ACCEPTED", cit="CIT-1"),
        "docs/packages/b.md": _record("DP-1", "decision-package", "REVOKED", cit="CIT-1"),
    })
    assert _codes(project) == [("GATE_NOT_AUTHORISING", ["CIT-1", "DP-1"])]


def test_a_ticket_whose_frontmatter_cannot_be_read_still_waits_on_a_dead_package(project):
    _commit(project, {
        ".tickets/PROJ-aaaa.md": "---\nid: PROJ-aaaa\nstatus: [closed\n---\n",
        "docs/packages/a.md": _record("DP-1", "decision-package", "STALE", cit="CIT-1", constrains=["PROJ-aaaa"]),
    })
    assert _codes(project) == [("TICKET_WAITS_ON_DEAD_GATE", ["PROJ-aaaa", "DP-1"])]
