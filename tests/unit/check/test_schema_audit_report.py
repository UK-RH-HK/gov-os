"""Unit tests for core-schema's audit-report type (W2-54, DEC-768 item 1; DEC-441, DEC-565, DEC-626)."""
from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from gov.check import schema

REPO = Path(__file__).resolve().parents[3]
REPORT = "---\nmilestone: wave-1-exit\ncommit: 60ea6924\npack_sha256: 2355ce5f\n---\n\n# An audit\n"


@pytest.fixture
def project(tmp_path):
    schemas = tmp_path / schema.SCHEMA_DIR
    schemas.mkdir(parents=True)
    for name in ("common.schema.json", "audit-report.schema.json"):
        shutil.copyfile(REPO / schema.SCHEMA_DIR / name, schemas / name)
    return tmp_path


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_typeless_record_in_the_audit_folder_is_an_audit_report(project):
    _write(project, "docs/audit/wave-1/report.md", REPORT)
    assert schema.check(project) == []


def test_a_record_stating_type_audit_report_is_held_to_the_schema(project):
    _write(project, "docs/notes/report.md", REPORT.replace("---\n", "---\ntype: audit-report\n", 1))
    assert schema.check(project) == []


@pytest.mark.parametrize("field", ("milestone", "commit", "pack_sha256"))
def test_an_audit_report_lacking_a_field_fails_naming_it(project, field):
    text = "\n".join(line for line in REPORT.split("\n") if not line.startswith(f"{field}:"))
    _write(project, "docs/audit/report.md", text)
    findings = schema.check(project)
    assert [(f["code"], f.get("field")) for f in findings] == [("SCHEMA_MISSING_FIELD", field)]


def test_a_commit_of_the_wrong_shape_fails(project):
    _write(project, "docs/audit/report.md", REPORT.replace("60ea6924", "not-a-commit"))
    assert [(f["code"], f.get("field")) for f in schema.check(project)] == [("SCHEMA_INVALID_FIELD", "commit")]


@pytest.mark.parametrize("folder", ("docs/notes", "docs/audit-archive", "docs/reports/audit"))
def test_a_typeless_record_outside_the_audit_folder_still_fails(project, folder):
    _write(project, f"{folder}/report.md", REPORT)
    assert [f["code"] for f in schema.check(project)] == ["SCHEMA_INVALID_TYPE"]


# KPI S4 is about W2-54's own change, not the tree (DEC-874 item 1): W2-54's own commits, the non-merge commits whose
# `Task:` trailer is DAEO-0rfi, bring in no schema file and no type of W2-02's beyond `audit-report`. Read through git
# only, each commit against its parent; it holds before and after W2-02 merges (4ce16df2 holds W2-02's types).
OWN_TASK = "DAEO-0rfi"
W2_02_OTHER_TYPES = ("close", "adoption-verdict")
SCHEMA_PY = "src/gov/check/schema.py"
_NAMED = "|".join(re.escape(name) for name in W2_02_OTHER_TYPES)
_MAP_ENTRY = re.compile(rf"""["']({_NAMED})["']\s*:""")
_STANDALONE_ENTRY = re.compile(rf"""STANDALONE_TYPES.*["']({_NAMED})["']""")


def _git(repo, *args, env=None):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=True, env=env).stdout


def _w2_02_types_in_own_commits(repo, rev, env=None):
    found = []
    log = _git(repo, "log", "--no-merges", "--format=%H%x09%(trailers:key=Task,valueonly,separator=%x2C)", rev, env=env)
    for line in log.splitlines():
        sha, _, tasks = line.partition("\t")
        if OWN_TASK not in (task.strip() for task in tasks.split(",")):
            continue
        for row in _git(repo, "show", "--no-renames", "--name-status", "--format=", sha, env=env).splitlines():
            status, _, path = row.partition("\t")
            if status == "A" and Path(path).name in {f"{name}.schema.json" for name in W2_02_OTHER_TYPES}:
                found.append(f"{sha[:8]} adds {path}")
        for added in _git(repo, "show", "-U0", "--format=", sha, "--", SCHEMA_PY, env=env).splitlines():
            if added.startswith("+") and not added.startswith("+++"):
                hit = _MAP_ENTRY.search(added) or _STANDALONE_ENTRY.search(added)
                if hit:
                    found.append(f"{sha[:8]} adds {hit.group(1)!r} to {SCHEMA_PY}: {added[1:].strip()}")
    return found


def _assert_no_w2_02_types_in_own_commits(repo, rev, env=None):
    found = _w2_02_types_in_own_commits(repo, rev, env=env)
    assert not found, f"W2-54's own commits in {rev} bring in W2-02's other types: {found}"


@pytest.mark.parametrize("rev", ("HEAD", "4ce16df2"))
def test_the_other_types_of_w2_02_stay_unknown(rev):
    _assert_no_w2_02_types_in_own_commits(REPO, rev)


@pytest.fixture
def built_history(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "HOME": str(tmp_path),
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }
    _git(repo, "init", "-q", "-b", "main", env=env)
    _git(repo, "config", "user.email", "t@t", env=env)
    _git(repo, "config", "user.name", "T", env=env)

    def commit(task, rel, text):
        _write(repo, rel, text)
        _git(repo, "add", "-A", env=env)
        _git(repo, "commit", "-q", "-m", f"a change\n\nTask: {task}", env=env)
        return _git(repo, "rev-parse", "HEAD", env=env).strip()

    commit(OWN_TASK, SCHEMA_PY, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n}\n'
           'STANDALONE_TYPES = ("probe", "audit-report")\n')
    return repo, env, commit


@pytest.mark.parametrize(
    "rel, text",
    (
        (SCHEMA_PY, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n    "close": "close.schema.json",\n}\n'
                    'STANDALONE_TYPES = ("probe", "audit-report")\n'),
        (SCHEMA_PY, 'SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n}\n'
                    'STANDALONE_TYPES = ("probe", "audit-report", "adoption-verdict")\n'),
        (f"{schema.SCHEMA_DIR}/close.schema.json", "{}\n"),
        (f"{schema.SCHEMA_DIR}/adoption-verdict.schema.json", "{}\n"),
    ),
    ids=("close-in-schema-map", "adoption-verdict-in-standalone-types", "close-schema-file", "adoption-verdict-schema-file"),
)
@pytest.mark.parametrize("task, fails", ((OWN_TASK, True), ("DAEO-zflj", False)))
def test_the_reading_of_w2_54_own_commits_fails_only_on_its_own(built_history, rel, text, task, fails):
    repo, env, commit = built_history
    sha = commit(task, rel, text)
    if fails:
        with pytest.raises(AssertionError, match=sha[:8]):
            _assert_no_w2_02_types_in_own_commits(repo, "HEAD", env=env)
    else:
        _assert_no_w2_02_types_in_own_commits(repo, "HEAD", env=env)
