"""KPI success 4 and failure 3: the ``audit-report`` type exactly as W2-02 defines it at ``2a35fd7b``, and
nothing of W2-02's other types; core-schema green here with the W1-43 report untouched; a record outside
``docs/audit/`` that states no ``type`` still fails, and an audit report lacking a required field fails, naming
it [DEC-768 item 1, DEC-441, DEC-565, DEC-626].

Core-schema runs as its declaration says (``python3 -m gov.check.schema`` in the project root) in temporary
projects that hold this worktree's ``common`` and ``audit-report`` schema files. Its codes are those it gives
other types today (``SCHEMA_MISSING_FIELD``, ``SCHEMA_INVALID_FIELD``, ``SCHEMA_INVALID_TYPE``).

Red reasons, today: there is no ``template/governance/kernel/schemas/audit-report.schema.json``, so every case
that needs it fails on that first; and core-schema reports this repository's W1-43 report as
``SCHEMA_INVALID_TYPE``. The cases marked "passes today" hold what the fix must keep.
"""

from __future__ import annotations

import pytest
import yaml

import w2_54_support as S

REPORT_IN_FOLDER = ("docs/audit/report.md", "docs/audit/wave-9/wave-9-exit-audit.md")
OUTSIDE_FOLDER = ("docs/notes/report.md", "docs/audit-archive/report.md", "docs/reports/audit/report.md")


def _codes(findings):
    return [(finding.get("code"), finding.get("field")) for finding in findings]


# ---- the type, exactly W2-02's

def test_the_schema_file_is_w2_02_s_byte_for_byte():
    """*Red.* ``template/governance/kernel/schemas/audit-report.schema.json`` is byte for byte
    ``git show 2a35fd7b:template/governance/kernel/schemas/audit-report.schema.json``."""
    path = S.REPO_ROOT / S.AUDIT_SCHEMA_REL
    assert path.is_file(), f"there is no {S.AUDIT_SCHEMA_REL}"
    assert path.read_bytes() == S.show(S.W2_02_COMMIT, S.AUDIT_SCHEMA_REL), \
        f"{S.AUDIT_SCHEMA_REL} differs from W2-02's at {S.W2_02_COMMIT}"


def test_no_schema_file_of_w2_02_s_other_types_comes_with_it():
    """Nothing of W2-02's other types: no ``close`` or ``adoption-verdict`` schema file. Passes today."""
    for folder in (S.SCHEMAS_REL, "governance/kernel/schemas"):
        for name in S.W2_02_OTHER_SCHEMAS:
            assert not (S.REPO_ROOT / folder / name).exists(), f"{folder}/{name} is added"


@pytest.mark.parametrize("rel", REPORT_IN_FOLDER)
def test_a_record_in_the_audit_folder_that_states_no_type_is_held_as_an_audit_report(box, tmp_path, rel):
    """*Red.* A record under ``docs/audit/`` (at any depth) that states no ``type`` and holds ``milestone``,
    ``commit`` and ``pack_sha256`` is an audit report (DEC-626): core-schema finds nothing and is green.
    Today: ``SCHEMA_INVALID_TYPE``."""
    project = S.schema_project(tmp_path / "p", {rel: S.audit_record()})
    done, findings = S.core_schema(box, project)
    assert S.of_path(findings, rel) == [], f"core-schema refuses an audit report: {S.of_path(findings, rel)}"
    assert done.returncode == 0, done.describe()


@pytest.mark.parametrize("rel", ("docs/reports/report.md", "docs/audit/stated.md"))
def test_a_record_of_type_audit_report_owes_no_shared_frontmatter(box, tmp_path, rel):
    """*Red.* A record that states ``type: audit-report`` and holds the three fields, with no ``id``, ``status``
    or ``state_class``, is green wherever it is: the type stands alone (DEC-441, DEC-565). Today:
    ``SCHEMA_UNKNOWN_TYPE`` and missing shared fields."""
    text = S.frontmatter({"type": "audit-report", **S.audit_front()}, S.AUDIT_BODY)
    project = S.schema_project(tmp_path / "p", {rel: text})
    done, findings = S.core_schema(box, project)
    assert S.of_path(findings, rel) == [], f"core-schema refuses an audit report: {S.of_path(findings, rel)}"
    assert done.returncode == 0, done.describe()


@pytest.mark.parametrize("field, value", (("commit", "not-a-commit"), ("milestone", ""), ("pack_sha256", "")))
def test_an_audit_report_s_fields_are_held_to_the_schema_s_shapes(box, tmp_path, field, value):
    """*Red.* The schema's shapes hold: a ``commit`` that is no commit id, an empty ``milestone`` or an empty
    ``pack_sha256`` is ``SCHEMA_INVALID_FIELD`` naming the field."""
    rel = "docs/audit/report.md"
    project = S.schema_project(tmp_path / "p", {rel: S.audit_record(**{field: value})})
    done, findings = S.core_schema(box, project)
    assert (S.INVALID_FIELD, field) in _codes(S.of_path(findings, rel)), \
        f"no {S.INVALID_FIELD} naming '{field}': {S.of_path(findings, rel)}"
    assert done.returncode != 0, done.describe()


@pytest.mark.parametrize("kind", ("close", "adoption-verdict"))
def test_w2_02_s_other_types_are_judged_as_an_unknown_type(box, tmp_path, kind):
    """A record of type ``close`` or ``adoption-verdict`` gets the findings a record of a type core-schema
    does not know gets today, no more and no fewer. Passes today."""
    front = {"id": "REC-W254-1", "verdict": "accepted", "ticket": "DAEO-0000"}
    files = {"docs/records/known.md": S.frontmatter({**front, "type": kind}),
             "docs/records/unknown.md": S.frontmatter({**front, "type": "w254-no-such-type"})}
    project = S.schema_project(tmp_path / "p", files, require_audit=False)
    done, findings = S.core_schema(box, project)

    def shape(rel, name):
        return sorted((finding.get("code"), finding.get("field"), finding.get("type") == name,
                       finding.get("message", "").replace(rel, "<path>").replace(name, "<type>"))
                      for finding in S.of_path(findings, rel))

    assert shape("docs/records/known.md", kind) == shape("docs/records/unknown.md", "w254-no-such-type"), \
        f"a {kind} record is not judged as an unknown type:\n{findings}"
    assert shape("docs/records/known.md", kind), "an unknown type gives no finding: the comparison is empty"


# ---- failure line 3

@pytest.mark.parametrize("rel", OUTSIDE_FOLDER)
def test_a_record_outside_the_audit_folder_that_states_no_type_still_fails(box, tmp_path, rel):
    """Failure line 3, first half. A record outside ``docs/audit/`` that states no ``type`` is
    ``SCHEMA_INVALID_TYPE``, even with the audit report's three fields, in a folder whose name only begins
    with ``audit`` or in an ``audit`` folder elsewhere. Passes today."""
    project = S.schema_project(tmp_path / "p", {rel: S.audit_record()}, require_audit=False)
    done, findings = S.core_schema(box, project)
    assert (S.INVALID_TYPE, None) in _codes(S.of_path(findings, rel)), \
        f"a record outside docs/audit/ with no type is not refused: {findings}"
    assert done.returncode != 0, done.describe()


@pytest.mark.parametrize("missing", S.AUDIT_FIELDS)
@pytest.mark.parametrize("placement", ("folder", "stated"))
def test_an_audit_report_lacking_a_required_field_fails_naming_it(box, tmp_path, missing, placement):
    """*Red.* Failure line 3, second half. An audit report, read from its folder (no ``type``) or stating
    ``type: audit-report``, that lacks ``missing`` is ``SCHEMA_MISSING_FIELD`` naming that field, and only
    that field. Today: ``SCHEMA_INVALID_TYPE`` or ``SCHEMA_UNKNOWN_TYPE``, naming no field."""
    if placement == "folder":
        rel, front = "docs/audit/wave-9/report.md", S.audit_front(**{missing: None})
    else:
        rel, front = "docs/reports/report.md", {"type": "audit-report", **S.audit_front(**{missing: None})}
    project = S.schema_project(tmp_path / "p", {rel: S.frontmatter(front, S.AUDIT_BODY)})
    done, findings = S.core_schema(box, project)
    mine = S.of_path(findings, rel)
    assert (S.MISSING_FIELD, missing) in _codes(mine), f"no {S.MISSING_FIELD} naming '{missing}': {mine}"
    others = [field for field in S.AUDIT_FIELDS if field != missing]
    assert not [finding for finding in mine if finding.get("field") in others], \
        f"a field the report holds is named: {mine}"
    assert done.returncode != 0, done.describe()


# ---- this repository

def test_core_schema_is_green_on_this_repository_with_w1_43_untouched(code_under_test):
    """*Red.* Core-schema, run as declared in this worktree, finds nothing; the W1-43 report's sha256 is
    ``b14e17d6...cdac1d`` before and after the run. Today: ``SCHEMA_INVALID_TYPE`` on the W1-43 report."""
    assert S.sha256(S.REPO_ROOT / S.W1_43_REL) == S.W1_43_SHA256, "the W1-43 audit report is changed"
    declaration = (S.REPO_ROOT / S.CHECKS_REL / "core-schema.yaml").read_text(encoding="utf-8")
    command = yaml.safe_load(declaration)["command"]
    done = S.run(["sh", "-c", command], cwd=S.REPO_ROOT, env=S.worktree_env(), timeout=S.CALL_TIMEOUT_S)
    assert done.returncode == 0, f"core-schema is not green on this repository\n{done.describe()}"
    assert S.sha256(S.REPO_ROOT / S.W1_43_REL) == S.W1_43_SHA256, "the W1-43 audit report is changed by the run"
