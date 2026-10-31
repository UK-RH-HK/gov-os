"""W2-64 KPI success 4: the close schema states the evidence block W2-66's close writes; a close record with an
incomplete evidence block is refused, naming the record and the rule; the close records written before W2-66
still validate [DEC-890 item 1].

The close records are this repository's own, each a single named file read from ``docs/close/``: DAEO-c1uz's (W2-66's
block, a base commit), DAEO-uzme's (``base: null``, ``scope: full`` for ``BASE_UNKNOWN``) and DAEO-0rfi's (written
before W2-66, no ``evidence:`` key). A case writes the record's frontmatter, changed as it says, into a temporary
repository with the worktree's kernel schema files, and runs core-schema with the installed check-jsonschema.
"""

from __future__ import annotations

import copy

import pytest

import w2_64_support as S

CLOSE_SCHEMA = "close.schema.json"


def _run(tmp_path, source, change=None):
    """The record, changed by ``change``, at its own place (``docs/close/<ticket>/CL-<ticket>.md``): its path and
    core-schema's run."""
    front, body = S.close_record(source)
    front = copy.deepcopy(front)
    if change:
        change(front)
    project = S.Project(S.Place(tmp_path).real_tool()).kernel_schemas().registry()
    rel = project.write(source, S.markdown(front, body))
    return rel, project.core_schema()


@pytest.mark.parametrize("source", (S.CLOSE_WITH_EVIDENCE, S.CLOSE_BASE_UNKNOWN, S.CLOSE_BEFORE_W2_66))
def test_this_repository_s_close_records_validate(tmp_path, source):
    """W2-66's block (with a base, and with ``base: null``) and a close record written before W2-66 (no ``evidence``)
    validate: exit 0, no finding. Passes today."""
    rel, run = _run(tmp_path, source)
    assert run.code == 0 and S.about(run.findings, rel) == [], f"{source} does not validate\n{run.describe()}"


def test_evidence_null_validates(tmp_path):
    """``evidence: null`` (``gov close`` for a ticket judged on its evidence with no test run) validates. Passes
    today."""
    rel, run = _run(tmp_path, S.CLOSE_WITH_EVIDENCE, lambda front: front.__setitem__("evidence", None))
    assert run.code == 0 and S.about(run.findings, rel) == [], run.describe()


def test_the_close_s_other_fields_and_a_later_key_validate(tmp_path):
    """The fields the close writes beside the required ones (``per_test_timeout``, ``distribution``,
    ``tmp_path_retention_policy``, W2-68's ``code_fingerprint`` and ``records_fingerprint`` as a string or null and
    ``reused`` as an object) and a key no schema names yet validate. Passes today."""
    def change(front):
        front["evidence"].update({"code_fingerprint": "f" * 64, "records_fingerprint": None,
                                  "reused": {"from": "a later close"}, "a_later_field": [1, 2]})
    rel, run = _run(tmp_path, S.CLOSE_WITH_EVIDENCE, change)
    assert run.code == 0 and S.about(run.findings, rel) == [], run.describe()


@pytest.mark.parametrize("field", S.EVIDENCE_REQUIRED)
def test_an_evidence_block_without_a_required_field_is_refused(tmp_path, field):
    """*Red.* W2-66's block without ``field`` is refused: exit non-zero, a finding on the record's path, under the
    field ``evidence``, that names the schema file and the missing field. Today: no finding (the close schema
    states no evidence block)."""
    rel, run = _run(tmp_path, S.CLOSE_WITH_EVIDENCE, lambda front: front["evidence"].pop(field))
    assert run.code != 0, f"an evidence block without '{field}' passes\n{run.describe()}"
    mine = [f for f in S.about(run.findings, rel) if f.get("field") == "evidence"]
    assert mine and all(f.get("code") in S.REFUSALS for f in mine), \
        f"no refusal on {rel} under 'evidence'\n{run.describe()}"
    assert any(S.names_rule(f, CLOSE_SCHEMA, "evidence", (f"'{field}'",)) for f in mine), \
        f"no finding names {CLOSE_SCHEMA}, 'evidence' and the missing '{field}': {mine}"


def _set(path, value):
    def change(front):
        target = front["evidence"]
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
    return change


WRONG_SHAPES = {
    "scope is neither scoped nor full": (("scope",), "partial"),
    "a full scope with no reason": (("why_full",), []),
    "a reason with no text": (("why_full", 0), {"reason": ""}),
    "base is no commit id": (("base",), "not-a-commit"),
    "head is abbreviated": (("head",), "7ada0f58"),
    "tree is no text": (("tree",), 40),
    "changed is no list": (("changed",), "src/gov/close/command.py"),
    "a selected target with no why": (("selected", 0), {"target": "tests/acceptance/W1-05/"}),
    "a left-out entry with no why": (("left_out",), [{"target": "tests/unit/"}]),
    "a skip with no reason": (("skips",), [{"test": "tests/x.py::test_y"}]),
    "skip_count is negative": (("skip_count",), -1),
    "skip_count is text": (("skip_count",), "3"),
    "a failure with no text": (("failures",), [{"test": "tests/x.py::test_y"}]),
    "junit_xml is no list": (("junit_xml",), "junit.xml"),
    "per_test_timeout is text": (("per_test_timeout",), "300"),
}


@pytest.mark.parametrize("case", sorted(WRONG_SHAPES))
def test_an_evidence_block_of_the_wrong_shape_is_refused(tmp_path, case):
    """*Red.* W2-66's block (DAEO-uzme's, ``scope: full``) with one field of the wrong shape is refused:
    ``SCHEMA_INVALID_FIELD`` on the record's path under ``evidence``, naming the schema file. Today: no finding."""
    path, value = WRONG_SHAPES[case]
    rel, run = _run(tmp_path, S.CLOSE_BASE_UNKNOWN, _set(path, value))
    assert run.code != 0, f"an evidence block where {case} passes\n{run.describe()}"
    mine = [f for f in S.about(run.findings, rel) if f.get("field") == "evidence"]
    assert mine and all(f.get("code") in S.REFUSALS for f in mine), \
        f"no refusal on {rel} under 'evidence' where {case}\n{run.describe()}"
    assert any(S.names_rule(f, CLOSE_SCHEMA, "evidence") for f in mine), \
        f"no finding names {CLOSE_SCHEMA} and 'evidence': {mine}"


def test_an_evidence_block_that_is_no_object_is_refused(tmp_path):
    """*Red.* ``evidence`` as a list is refused under ``evidence``. Today: no finding."""
    rel, run = _run(tmp_path, S.CLOSE_WITH_EVIDENCE, lambda front: front.__setitem__("evidence", ["scoped"]))
    assert run.code != 0, run.describe()
    assert [f for f in S.about(run.findings, rel) if f.get("field") == "evidence"], run.describe()


def test_task_stays_required(tmp_path):
    """``task`` stays as today: a close record without it is ``SCHEMA_MISSING_FIELD`` naming it. Passes today."""
    rel, run = _run(tmp_path, S.CLOSE_WITH_EVIDENCE, lambda front: front.pop("task"))
    assert [f for f in S.about(run.findings, rel) if f.get("field") == "task" and f.get("code") == S.MISSING_FIELD], \
        run.describe()
