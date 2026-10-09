"""The probe record's schema in the kernel (DEC-565; the follow-up after W1-41, DEC-569).

DEC-565: "In the follow-up after W1-41 the probe type is added to the kernel's record schema".

A probe record is the file ``gov close`` reads for a FULL-profile ticket: frontmatter with ``type: probe`` and
the fields the probe gate asks (DEC-137, DEC-487, DEC-490). The schema is found as the suite finds every
schema: by the record type's word in the file's name (here ``probe``), never by a full name.

The fields and their shapes (proposed; README, section "The probe record's schema"):

- required: ``type`` (``probe``), ``task`` (a ticket id), ``reviewer_session`` and ``implementer_session``
  (text, not empty), ``reviewer_wrote_nothing`` (a truth value), ``commissioned_by`` and ``judged_by`` (text,
  not empty), ``judgement`` (``pass``, ``passed``, ``fail`` or ``failed``), ``probed_commit`` (forty lower-case
  hexadecimal characters);
- not required: ``id``, ``status``, ``state_class``. This repository's probe records state none of them.

That the reviewer is not the implementer, that the two names are ``orchestrator`` and that the judgement
passed are questions of the probe gate, not of the schema: a record of a failed probe is a well-formed record.

Every case is red until the schema exists: "no JSON Schema for the probe record".
"""

from __future__ import annotations

import pytest

import w1_08_support as support

WORDS = (("probe",), ())
COMMIT = "0123456789abcdef0123456789abcdef01234567"
REQUIRED = ("type", "task", "reviewer_session", "implementer_session", "reviewer_wrote_nothing",
            "commissioned_by", "judged_by", "judgement", "probed_commit")


def _schema():
    found = [path for path in support.schema_files()
             if support._matches(path.name[: -len(support.SCHEMA_SUFFIX)], WORDS)]
    names = [path.name for path in support.schema_files()]
    assert found, (f"no JSON Schema for the probe record: no file named *{support.SCHEMA_SUFFIX} under "
                   f"{support.SCHEMAS_REL}/ has 'probe' in its name (found: {names})")
    assert len(found) == 1, f"more than one schema file for the probe record: {[path.name for path in found]}"
    return found[0]


def _good():
    return {
        "type": "probe",
        "task": "PROJ-full",
        "reviewer_session": "2e97ad0c-eee6-4500-baae-303e79f117f7",
        "implementer_session": "9e9a7dc8-1be2-4138-87a8-c80fe86a1f53",
        "reviewer_wrote_nothing": True,
        "commissioned_by": "orchestrator",
        "judged_by": "orchestrator",
        "judgement": "pass",
        "probed_commit": COMMIT,
    }


def _own_records():
    files = sorted((support.REPO_ROOT / "docs" / "probes").glob("*/*.md"))
    assert files, "this repository holds no probe record"
    return files


def test_the_kernel_has_one_schema_for_the_probe_record():
    schema = support.load_json(_schema())
    assert isinstance(schema, dict), f"{_schema().name} is not a JSON object"


def test_the_probe_schema_names_no_path_of_a_project():
    """No path of this repository goes into the kernel: the schema says what a record is, not where it lies."""
    text = _schema().read_text(encoding="utf-8")
    assert "docs/" not in text and ".tickets" not in text, f"{_schema().name} names a path of a project"


@pytest.mark.local_only
def test_the_probe_schema_is_a_valid_json_schema(check):
    check.metaschema(_schema())


@pytest.mark.local_only
def test_the_probe_schema_accepts_a_well_formed_record(check):
    schema = _schema()
    documents = {"plain": _good(),
                 "with-the-shared-fields": {**_good(), "id": "PR-PROJ-full", "status": "ACTIVE",
                                            "state_class": "NARRATIVE"}}
    for word in ("passed", "fail", "failed"):
        documents[f"judgement-{word}"] = {**_good(), "judgement": word}
    check.accepts_all(schema, documents, "a well-formed probe record")


@pytest.mark.local_only
def test_the_probe_schema_accepts_this_repository_s_probe_records(check):
    schema = _schema()
    documents = {f"{path.parent.name}-{path.stem}": support.load_record(path) for path in _own_records()}
    check.accepts_all(schema, documents, "a probe record of this repository")


@pytest.mark.local_only
def test_the_probe_schema_refuses_a_record_without_a_required_field(check):
    schema = _schema()
    check.good(schema, _good(), "a well-formed probe record")
    check.refuses_each(schema, {field: support.without(_good(), field) for field in REQUIRED},
                       "a probe record without the field")


@pytest.mark.local_only
def test_the_probe_schema_refuses_a_field_of_a_wrong_type_or_value(check):
    schema = _schema()
    check.good(schema, _good(), "a well-formed probe record")
    wrong = {
        "another type": ("type", "probing"),
        "a judgement outside the four words": ("judgement", "inconclusive"),
        "a judgement in upper case": ("judgement", "PASS"),
        "a judgement that is a truth value": ("judgement", True),
        "an abbreviated commit id": ("probed_commit", COMMIT[:12]),
        "a name that moves": ("probed_commit", "HEAD"),
        "a commit id in upper case": ("probed_commit", COMMIT.upper()),
        "a commit id one character too long": ("probed_commit", COMMIT + "0"),
        "a commit id that is a number": ("probed_commit", 1234567),
        "reviewer_wrote_nothing as a word": ("reviewer_wrote_nothing", "yes"),
        "an empty reviewer session": ("reviewer_session", ""),
        "an implementer session that is a number": ("implementer_session", 7),
        "commissioned_by that is empty": ("commissioned_by", ""),
        "judged_by that is a list": ("judged_by", ["orchestrator"]),
        "a task that is no ticket id": ("task", "the ticket"),
    }
    check.refuses_each(schema, {what: support.replaced(_good(), field, value)
                                for what, (field, value) in wrong.items()},
                       "a probe record with")
