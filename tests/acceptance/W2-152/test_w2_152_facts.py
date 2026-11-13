"""W2-152 S10: facts.yaml's ready.new_since, its schema, and W2-128's acceptance cases (README)."""

from __future__ import annotations

import copy
import datetime
import json
import subprocess
import sys

import yaml

import w2_152_support as s

TICKET_CREATED = datetime.date(2026, 11, 9)  # DAEO-o5x1's created date: the earliest day it can land


def _facts() -> dict:
    data = yaml.safe_load(s.FACTS.read_text(encoding="utf-8"))
    assert isinstance(data, dict), "governance/project/facts.yaml is not a mapping"
    return data


def _schema_errors(instance: dict) -> list[str]:
    import jsonschema

    schema = json.loads(s.FACTS_SCHEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())
    return [f"{'/'.join(map(str, error.absolute_path)) or '$'}: {error.message}"
            for error in validator.iter_errors(instance)]


def test_s10_facts_yaml_holds_ready_new_since_an_iso_date():
    ready = _facts().get("ready")
    assert isinstance(ready, dict) and "new_since" in ready, f"facts.yaml has no ready.new_since: ready = {ready!r}"
    value = ready["new_since"]
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        day = value
    else:
        assert isinstance(value, str), f"ready.new_since is not an ISO date: {value!r}"
        try:
            day = datetime.date.fromisoformat(value)
        except ValueError:
            raise AssertionError(f"ready.new_since is not an ISO date (YYYY-MM-DD): {value!r}") from None
    assert day >= TICKET_CREATED, f"ready.new_since {day} is before this ticket was filed ({TICKET_CREATED})"


def test_s10_schema_declares_ready_new_since_and_the_file_validates():
    schema = json.loads(s.FACTS_SCHEMA.read_text(encoding="utf-8"))
    ready = schema.get("properties", {}).get("ready")
    assert isinstance(ready, dict) and "new_since" in ready.get("properties", {}), \
        "facts.schema.json does not declare ready.new_since"
    data = _facts()
    errors = _schema_errors(data)
    assert not errors, f"facts.yaml does not validate against facts.schema.json: {errors[:5]}"
    wrong = copy.deepcopy(data)
    wrong["ready"] = {"new_since": "soon"}
    assert _schema_errors(wrong), "facts.schema.json accepts ready.new_since 'soon', which is no ISO date"


def test_s10_gov_accept_w2_128_still_passes(tmp_path):
    """W2-128's acceptance cases pass on this tree, through gov accept (a green guard on integrate)."""
    done = subprocess.run([sys.executable, "-B", "-m", "gov.cli.main", "accept", "W2-128", "--root", str(s.REPO),
                           "--json"], capture_output=True, text=True, timeout=900, cwd=str(tmp_path),
                          env=s.accept_env(tmp_path), stdin=subprocess.DEVNULL)
    try:
        data = json.loads(done.stdout)
    except ValueError:
        raise AssertionError(f"gov accept W2-128 printed no envelope: exit {done.returncode}\n{done.stderr[-2000:]}") \
            from None
    result = data.get("result") or {}
    failing = [line.get("kpi") for line in result.get("lines", []) if line.get("outcome") != "pass"]
    assert done.returncode == 0 and result.get("outcome") == "pass", \
        f"gov accept W2-128: exit {done.returncode}, outcome {result.get('outcome')}, error kind " \
        f"{result.get('error_kind')}, failing lines {failing}, totals {result.get('totals')}, error {data.get('error')}"
