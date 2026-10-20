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


# Rewrite-Reason: DEC-874 (orchestrator, delegated, 2026-10-20). The two cases below judged the tree (W2-02's files
# absent, W2-02's types unknown), so they were red on any tree holding W2-02's merge. KPI S4 is about W2-54's own
# change: they now read W2-54's own commits (no merge, `Task: DAEO-0rfi`) through git, in two histories, this
# branch and W2-02's branch merged with w2/integrate (README, "Run 5 (DEC-874)").
HISTORIES = ("HEAD", S.W2_02_MERGED_COMMIT)


@pytest.fixture
def histories_that_bring_in_w2_02_s_types(tmp_path):
    """Two temporary repositories built from scratch whose change adds both schema files of W2-02's other types, a
    ``"close"`` type map entry and ``"adoption-verdict"`` among the standalone types: under ``Task: DAEO-0rfi``
    (``own``) and under another Task (``other-task``). In both, a merge carrying ``Task: DAEO-0rfi`` also brings in the
    two schema files. The reading must name the first's commit and nothing of the second."""
    module = ('SCHEMA_MAP = {\n    "audit-report": "audit-report.schema.json",\n    "close": "close.schema.json",\n}\n'
              'STANDALONE_TYPES = ("probe", "audit-report", "adoption-verdict")\n')
    adds = {**{f"{S.SCHEMAS_REL}/{name}": "{}\n" for name in S.W2_02_OTHER_SCHEMAS}, S.SCHEMA_MODULE_REL: module}
    return {case: S.own_task_repo(tmp_path / case, task, adds)
            for case, task in (("own", S.OWN_TASK), ("other-task", "DAEO-zflj"))}


def _the_reading_tells_them_apart(repos, reading):
    """The reading names the own commit of ``own`` that brings W2-02's types in (the newest own commit; the one before
    it adds only ``audit-report``) and nothing of ``other-task`` (a merge never counts)."""
    found = reading(repos["own"])
    assert found, f"the reading misses a commit carrying Task: {S.OWN_TASK} that brings W2-02's types in"
    assert {entry[0] for entry in found} == {S.own_commits("HEAD", repos["own"])[0]}, found
    other = reading(repos["other-task"])
    assert other == [], f"the reading counts another Task's commit or a merge as W2-54's own: {other}"


# Rewrite-Reason: DEC-874, second batch. The module readings read the checked-out branch whatever history they named,
# and a walk limited to the module followed only the side W2-02's merge-back kept, so W2-54's own 4f753c72 was missed
# on 4ce16df2 (README, "Run 5 (DEC-874)", "Second batch").
NO_SUCH_HISTORY = "w254-no-such-revision"


@pytest.fixture
def a_merge_that_keeps_its_own_side_of_the_module(tmp_path):
    """A temporary repository built from scratch in the shape of W2-02's merge-back (``w2_54_support.merge_back_repo``):
    ``(repo, the merge, the own commit)``."""
    return S.merge_back_repo(tmp_path / "merge-back")


def _the_module_readings_read_the_named_history(merge_back, kind):
    """Through a merge of another Task that keeps its own side of the module, the readings of the named history still
    find the own commit that changed it, and count none of the other side's lines; the checked-out branch, which holds
    no own commit, is not what is read; a history that does not exist is an error, not a pass."""
    repo, merge, own = merge_back
    assert S.last_own_commit_of(merge, S.SCHEMA_MODULE_REL, repo) == own, \
        "through a merge that keeps its own side of the module, the reading misses the own commit that changed it"
    assert own in {commit for commit, _ in S.own_added_lines(merge, S.SCHEMA_MODULE_REL, repo)}, \
        "the own commit's added lines are not read through the merge"
    assert S.other_type_lines_brought_in(merge, kind, repo) == [], "another Task's lines are counted as W2-54's own"
    assert S.last_own_commit_of("HEAD", S.SCHEMA_MODULE_REL, repo) is None, \
        "the checked-out branch holds no own commit, yet one is found: the named history is not what is read"
    for reading in (lambda: S.other_type_lines_brought_in(NO_SUCH_HISTORY, kind, repo),
                    lambda: S.last_own_commit_of(NO_SUCH_HISTORY, S.SCHEMA_MODULE_REL, repo),
                    lambda: S.other_type_lines_brought_in(NO_SUCH_HISTORY, kind),
                    lambda: S.last_own_commit_of(NO_SUCH_HISTORY, S.SCHEMA_MODULE_REL)):
        with pytest.raises(AssertionError, match="bad revision"):
            reading()


@pytest.mark.parametrize("history", HISTORIES)
def test_no_schema_file_of_w2_02_s_other_types_comes_with_it(history, histories_that_bring_in_w2_02_s_types):
    """Nothing of W2-02's other types: no commit of W2-54's own in ``history`` adds or changes a ``close`` or
    ``adoption-verdict`` schema file under either schema folder (``git log --no-merges --name-status``, each against
    its parent). Holds on this branch and on W2-02's branch merged with w2/integrate. Passes today."""
    _the_reading_tells_them_apart(histories_that_bring_in_w2_02_s_types,
                                  lambda repo: S.other_schema_files_brought_in("HEAD", repo))
    own = S.own_commits(history)
    assert own, f"{history} holds no commit carrying Task: {S.OWN_TASK}: nothing of W2-54's own change is read"
    brought = S.other_schema_files_brought_in(history)
    assert brought == [], "W2-54's own commits bring in W2-02's other schema files:\n" + "\n".join(
        f"{commit[:12]} {status} {path}" for commit, status, path in brought)


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


@pytest.mark.parametrize("history", HISTORIES)
@pytest.mark.parametrize("kind", S.W2_02_OTHER_TYPES)
def test_w2_02_s_other_types_are_judged_as_an_unknown_type(box, tmp_path, kind, history,
                                                           histories_that_bring_in_w2_02_s_types,
                                                           a_merge_that_keeps_its_own_side_of_the_module):
    """W2-54's own change adds no ``close`` or ``adoption-verdict`` type: no line its own commits in ``history`` add
    to ``src/gov/check/schema.py`` names it (a type map key, a standalone type, its schema file); and core-schema as
    W2-54's own last commit to that module leaves it (``git show`` of that one file, run as declared) gives a record
    of that type the findings a record of a type it does not know gets, no more and no fewer. Passes today."""
    _the_reading_tells_them_apart(histories_that_bring_in_w2_02_s_types,
                                  lambda repo: S.other_type_lines_brought_in("HEAD", kind, repo))
    _the_module_readings_read_the_named_history(a_merge_that_keeps_its_own_side_of_the_module, kind)
    lines = S.other_type_lines_brought_in(history, kind)
    assert lines == [], f"W2-54's own commits add the type {kind} to {S.SCHEMA_MODULE_REL}:\n" + "\n".join(
        f"{commit[:12]} +{line}" for commit, line in lines)

    last = S.last_own_commit_of(history, S.SCHEMA_MODULE_REL)
    assert last, f"no commit of W2-54's own in {history} touches {S.SCHEMA_MODULE_REL}"
    front = {"id": "REC-W254-1", "verdict": "accepted", "ticket": "DAEO-0000"}
    files = {"docs/records/known.md": S.frontmatter({**front, "type": kind}),
             "docs/records/unknown.md": S.frontmatter({**front, "type": "w254-no-such-type"})}
    project = S.schema_project_at(tmp_path / "p", files, last)
    done, findings = S.core_schema_at(box, project, last)
    assert "Traceback" not in done.stderr, done.describe()

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
