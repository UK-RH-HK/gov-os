"""Builder tests for core-schema through check-jsonschema (W2-64): how an answer is read, the pin, the findings'
shapes, ``docs/imported/`` left out and the output's two forms (regression evidence only; the acceptance tests are
tests/acceptance/W2-64/)."""
from __future__ import annotations

import datetime
import json
import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.check import schema  # noqa: E402

TICKET = ("---\nid: PROJ-aaaa\ntype: task\nstatus: open\nstate_class: AUTHORITATIVE\nrole: engineer\n"
          "allowed_paths: [src/x.py]\nkpis: {success: [a], failure: [b]}\n---\n# A ticket\n")


def _project(tmp_path, records):
    schemas = tmp_path / schema.SCHEMA_DIR
    schemas.mkdir(parents=True)
    for name in ("common.schema.json", "ticket.schema.json"):
        shutil.copyfile(REPO / schema.SCHEMA_DIR / name, schemas / name)
    for rel, text in records.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text, encoding="utf-8")
    return tmp_path


def _stand_in(tmp_path, body):
    """A program at ``bin/check-jsonschema`` that answers ``--version`` as 0.38.2 and runs ``body`` otherwise."""
    program = tmp_path / "bin" / schema.VALIDATOR
    program.parent.mkdir()
    program.write_text(f"#!{sys.executable}\nimport json, sys\nif sys.argv[1:] == ['--version']:\n"
                       f"    print('check-jsonschema, version 0.38.2'); sys.exit(0)\n{body}\n", encoding="utf-8")
    program.chmod(0o755)
    return str(program)


def test_a_valid_ticket_passes_and_the_result_counts_it(tmp_path):
    findings, result = schema.run(_project(tmp_path, {".tickets/PROJ-aaaa.md": TICKET}))
    assert findings == []
    assert result["records_validated"] == 1
    assert result["validator"]["note"] == schema.NO_PIN


def test_every_error_is_a_finding_naming_the_record_and_the_rule(tmp_path):
    text = TICKET.replace("AUTHORITATIVE", "NOPE").replace("role: engineer\n", "deps: [x]\n")
    found = schema.check(_project(tmp_path, {".tickets/PROJ-aaaa.md": text}))
    assert sorted((f["code"], f["field"], f["at"]) for f in found) == [
        ("SCHEMA_INVALID_FIELD", "deps", "$.deps[0]"), ("SCHEMA_INVALID_FIELD", "state_class", "$.state_class"),
        ("SCHEMA_MISSING_FIELD", "role", "$")]
    assert all(f["path"] == ".tickets/PROJ-aaaa.md" and f["schema"] == "ticket.schema.json" for f in found)


def test_a_shared_field_the_schema_owes_too_is_one_finding(tmp_path):
    found = schema.check(_project(tmp_path, {".tickets/PROJ-aaaa.md": TICKET.replace("status: open\n", "")}))
    assert [(f["code"], f["field"]) for f in found] == [("SCHEMA_MISSING_FIELD", "status")]


def test_docs_imported_is_left_out_by_name_and_no_other_folder(tmp_path):
    bad = TICKET.replace("AUTHORITATIVE", "NOPE")
    findings, result = schema.run(_project(tmp_path, {"docs/imported/T.md": bad, "docs/imported-x/T.md": bad}))
    assert [f["path"] for f in findings] == ["docs/imported-x/T.md"]
    assert result["left_out"] == [{"path": "docs/imported/", "files": 1, "why": schema.LEFT_OUT_WHY}]


def test_a_timestamp_is_written_as_its_iso_text():
    instance = json.loads(schema._instance({"created": datetime.datetime(2026, 10, 29, 15, 55, 50,
                                                                         tzinfo=datetime.timezone.utc),
                                            "date": datetime.date(2026, 10, 29)}))
    assert instance == {"created": "2026-10-29T15:55:50+00:00", "date": "2026-10-29"}


def test_the_top_key_of_a_path_takes_the_longest_key_that_holds_it():
    assert schema._top_key("$.a.b[0]", {"a": 1, "a.b": 2}) == "a.b"
    assert schema._top_key("$.a[0]", {"a": 1, "ab": 2}) == "a"
    assert schema._top_key("$", {"a": 1}) is None


def test_a_nested_required_property_is_an_invalid_field():
    found = schema._finding("R.md", "close.schema.json",
                            {"path": "$.evidence", "message": "'scope' is a required property"}, {"evidence": {}})
    assert (found["code"], found["field"]) == ("SCHEMA_INVALID_FIELD", "evidence")


@pytest.mark.parametrize("body, why", (
    ("print(json.dumps({'status': 'ok', 'errors': [], 'checked_paths': []}))", "did not account for 1"),
    ("print(json.dumps({'status': 'ok', 'errors': [], 'checked_paths': sys.argv[4:], 'parse_errors': [{}]}))",
     "could not parse"),
    ("print('Error: schemafile could not be parsed'); sys.exit(1)", "no JSON answer"),
    ("sys.exit(2)", "no JSON answer"),
    ("print(json.dumps({'status': 'fail', 'errors': [], 'successes': sys.argv[4:]})); sys.exit(1)",
     "cannot be taken"),
    ("print(json.dumps({'status': 'fail', 'errors': [{'filename': '/elsewhere.json', 'path': '$', "
     "'message': 'm'}], 'successes': []})); sys.exit(1)", "not given"),
))
def test_an_answer_that_cannot_be_taken_is_a_fault(tmp_path, body, why):
    instance = tmp_path / "0.json"
    instance.write_text("{}", encoding="utf-8")
    errors, fault = schema._validate(_stand_in(tmp_path, body), REPO / schema.SCHEMA_DIR / "ticket.schema.json",
                                     [str(instance)])
    assert fault and why in fault, fault


@pytest.mark.parametrize("text, pin", (
    (None, None),
    ("tools:\n- {name: other, version: '1'}\n", None),
    ("tools:\n- {name: check-jsonschema, version: '0.38.2'}\n", "0.38.2"),
))
def test_the_pin_is_read_from_the_registry(tmp_path, text, pin):
    if text is not None:
        (tmp_path / schema.REGISTRY).parent.mkdir(parents=True)
        (tmp_path / schema.REGISTRY).write_text(text, encoding="utf-8")
    assert schema._pin(tmp_path) == (pin, None)


@pytest.mark.parametrize("text", ("tools: [", "- a list\n", "tools:\n- {name: check-jsonschema, version: 0.38}\n"))
def test_a_registry_that_cannot_be_read_is_a_finding(tmp_path, text):
    (tmp_path / schema.REGISTRY).parent.mkdir(parents=True)
    (tmp_path / schema.REGISTRY).write_text(text, encoding="utf-8")
    pin, fault = schema._pin(tmp_path)
    assert pin is None and fault["code"] == "SCHEMA_REGISTRY_UNREADABLE"


def test_the_output_has_the_success_form_on_a_pass_and_the_findings_beside_the_statement_on_a_refusal(
        tmp_path, monkeypatch, capsys):
    root = _project(tmp_path, {".tickets/PROJ-aaaa.md": TICKET})
    monkeypatch.chdir(root)
    assert schema.main() == 0
    answer = json.loads(capsys.readouterr().out)
    assert answer["ok"] is True and answer["result"]["left_out"][0]["path"] == "docs/imported/"
    (root / ".tickets/PROJ-aaaa.md").write_text(TICKET.replace("AUTHORITATIVE", "NOPE"), encoding="utf-8")
    assert schema.main() == 1
    answer = json.loads(capsys.readouterr().out)
    assert [f["field"] for f in answer["findings"]] == ["state_class"] and answer["left_out"]
