"""core-schema: validate record frontmatter against JSON schemas (schema/invariants).

Every record is validated through check-jsonschema, the validator the tool registry pins (DEC-074), not a subset of
it (DEC-872 item 2, lens G R2 (a)). Each record's frontmatter is written out as one JSON instance; one validator
process per schema file per kernel layout takes all of that schema's records. A validator that is absent, fails,
answers what cannot be read or is not the pinned version is a finding, never a pass. ``docs/imported/`` is left out
by name, as history (DEC-844).
"""
from __future__ import annotations

import datetime
import json
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yaml

VERSION = "2.0.0"

RECORD_PATHS = (".tickets", "docs")
SCHEMA_DIR = "template/governance/kernel/schemas"
# The kernel's two layouts (DEC-579): a record is held to the schemas of each layout the project holds.
SCHEMA_DIRS = (SCHEMA_DIR, "governance/kernel/schemas")
COMMON_SCHEMA = "common.schema.json"

SCHEMA_MAP = {
    "task": "ticket.schema.json",
    "decision": "madr.schema.json",
    "decision-package": "decision-package.schema.json",
    "research": "research.schema.json",
    "failure": "failure.schema.json",
    "lesson": "lesson.schema.json",
    "checkpoint": "checkpoint.schema.json",
    "probe": "probe.schema.json",
    # the record types in use beside them (DEC-612, DEC-620): each owes the shared frontmatter and nothing more
    "change-execution-record": "change-execution-record.schema.json",
    "change-impact-proposal": "change-impact-proposal.schema.json",
    "capability": "capability.schema.json",
    "specification": "specification.schema.json",
    "plan": "plan.schema.json",
    # the record types of W2-02: the close record gov close writes, an audit report in DEC-441's form, and the
    # adoption verdict of CAP-44.h (DEC-722); a decision entry (register-entry) has a schema and no record file
    # (DEC-274)
    "close": "close.schema.json",
    "audit-report": "audit-report.schema.json",
    "adoption-verdict": "adoption-verdict.schema.json",
}

# A type whose schema stands alone (DEC-565): its records owe what the schema requires, the shared frontmatter
# only where the schema takes it in. Every other record owes the shared four fields even where its schema does not
# ask for them.
STANDALONE_TYPES = ("probe", "audit-report", "adoption-verdict")
SHARED_FIELDS = ("id", "type", "status", "state_class")

# The audit-report folder (DEC-626, the audit-reproducibility declaration): a record there that states no `type`
# is an audit report.
AUDIT_REPORT_DIR, AUDIT_REPORT_TYPE = "docs/audit", "audit-report"

# The one folder left out (DEC-844): imported records are history, kept as they came.
IMPORTED_DIR = "docs/imported"
LEFT_OUT_WHY = "history (DEC-844): imported records are kept as they came and are not held to the schemas"

# The validator and its pin (DEC-074): the registry is read, never written.
VALIDATOR = "check-jsonschema"
REGISTRY = "governance/project/tool-registry.yaml"
NO_PIN = f"no pin was stated: {REGISTRY} has no {VALIDATOR} entry or does not exist"

_REQUIRED = re.compile(r"'(.+)' is a required property")


def _frontmatter(text: str) -> tuple[dict | None, str | None]:
    """``(frontmatter, None)`` of a record; ``(None, None)`` when the file is no record (its first line is not
    ``---``); ``(None, why)`` when it opens with ``---`` and its frontmatter cannot be read."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, None
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "its frontmatter has no closing '---' line"
    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError as error:
        return None, f"its frontmatter is not YAML ({str(error).splitlines()[0]})"
    if not isinstance(front, dict):
        return None, "its frontmatter is not a mapping"
    return front, None


def _instance(front: dict) -> str:
    """The frontmatter as one JSON instance; dates and timestamps as their ISO text."""
    def iso(value):
        if isinstance(value, (datetime.date, datetime.time)):
            return value.isoformat()
        raise TypeError(f"{type(value).__name__} has no JSON form")
    return json.dumps(front, default=iso, allow_nan=False)


def _schema_fault(root: Path, rel: str) -> str | None:
    """Why the schema file at ``rel`` cannot be used (it cannot be read or is no JSON), or None."""
    try:
        json.loads((root / rel).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, ValueError) as error:
        return f"{rel} cannot be read or is not valid JSON ({error})"
    return None


def _pin(root: Path) -> tuple[str | None, dict | None]:
    """The version the tool registry pins for the validator (None when no pin is stated), or a finding."""
    path = root / REGISTRY
    if not path.exists():
        return None, None
    try:
        registry = yaml.safe_load(path.read_text(encoding="utf-8"))
        tools = registry["tools"]
        entries = [tool for tool in tools if tool.get("name") == VALIDATOR]
        if entries and not isinstance(entries[0].get("version"), str):
            raise ValueError(f"its {VALIDATOR} entry states no version")
    except (OSError, UnicodeDecodeError, yaml.YAMLError, TypeError, KeyError, AttributeError, ValueError) as error:
        return None, {"code": "SCHEMA_REGISTRY_UNREADABLE", "path": REGISTRY,
                      "message": f"{REGISTRY} cannot be read, so the pin of {VALIDATOR} is unknown: {error!r}; "
                                 "the records were not measured"}
    return (entries[0]["version"] if entries else None), None


def _validator(root: Path) -> tuple[str | None, dict, list[dict]]:
    """The validator's program, what the output says of its version and pin, and the findings that stop it."""
    pin, fault = _pin(root)
    stated = {"tool": VALIDATOR, "pin": pin}
    if pin is None and fault is None:
        stated["note"] = NO_PIN
    if fault:
        return None, stated, [fault]
    program = shutil.which(VALIDATOR)
    if program is None:
        return None, stated, [{"code": "SCHEMA_VALIDATOR_ABSENT", "tool": VALIDATOR,
                               "message": f"{VALIDATOR} is not found on PATH: the records were not measured"}]
    try:
        done = subprocess.run([program, "--version"], capture_output=True, text=True, stdin=subprocess.DEVNULL)
    except OSError as error:
        return None, stated, [_failed(f"{VALIDATOR} --version could not start ({error})")]
    found = re.search(r"version\s+(\S+)", done.stdout)
    if done.returncode != 0 or not found:
        return None, stated, [_failed(f"{VALIDATOR} --version exited {done.returncode} and named no version: "
                                      f"{(done.stdout + done.stderr).strip()[:200]!r}")]
    stated["version"] = found.group(1)
    if pin is not None and stated["version"] != pin:
        return None, stated, [{"code": "SCHEMA_VALIDATOR_VERSION", "tool": VALIDATOR,
                               "installed": stated["version"], "pinned": pin,
                               "message": f"{VALIDATOR} {stated['version']} is installed, {REGISTRY} pins {pin}: "
                                          "the pinned validator is the judge (DEC-074); the records were not "
                                          "measured"}]
    return program, stated, []


def _failed(why: str) -> dict:
    return {"code": "SCHEMA_VALIDATOR_FAILED", "tool": VALIDATOR,
            "message": f"{why}: the records were not measured"}


def _validate(program: str, schema: Path, instances: list[str]) -> tuple[list[dict], str | None]:
    """The errors check-jsonschema answers for ``instances`` against ``schema`` (``-o json -v``), or why its answer
    cannot be taken. Every instance must be accounted for, passed or refused."""
    try:
        done = subprocess.run([program, "-o", "json", "-v", "--schemafile", str(schema), *instances],
                              capture_output=True, text=True, stdin=subprocess.DEVNULL)
    except OSError as error:
        return [], f"could not start ({error})"
    said = (done.stdout.strip() or done.stderr.strip())[:300]
    if done.returncode < 0:
        return [], f"was killed (signal {-done.returncode})"
    try:
        answer = json.loads(done.stdout)
    except ValueError:
        return [], f"exited {done.returncode} with no JSON answer: {said!r}"
    if not isinstance(answer, dict):
        return [], f"exited {done.returncode} with an answer that is no JSON object: {said!r}"
    errors, parse_errors = answer.get("errors"), answer.get("parse_errors") or []
    if not isinstance(errors, list) or not all(
            isinstance(error, dict) and all(isinstance(error.get(key), str) for key in ("filename", "path", "message"))
            for error in errors):
        return [], f"exited {done.returncode} with no readable error list: {said!r}"
    if set(error["filename"] for error in errors) - set(instances):
        return [], "named an instance it was not given"
    # from here the errors it gives are each a record's refusal, whatever else is wrong with the answer
    if parse_errors:
        return errors, f"could not parse instances: {parse_errors!r}"[:400]
    if done.returncode == 0 and answer.get("status") == "ok" and not errors:
        accounted = answer.get("checked_paths")
    elif done.returncode == 1 and answer.get("status") == "fail" and errors:
        accounted = answer.get("successes")
        accounted = accounted + [error["filename"] for error in errors] if isinstance(accounted, list) else None
    else:
        return errors, (f"exited {done.returncode} with status {answer.get('status')!r} and "
                        f"{len(errors)} error(s): an answer that cannot be taken")
    if not isinstance(accounted, list):
        return errors, f"exited {done.returncode} and did not list the instances it checked"
    unaccounted = set(instances) - set(accounted)
    if unaccounted:
        return errors, f"did not account for {len(unaccounted)} of the {len(instances)} instances it was given"
    return errors, None


def _top_key(where: str, front: dict) -> str | None:
    """The top-level key of the record a validator path (``$.deps[0]``) is under; None for the record itself."""
    keys = [key for key in front if isinstance(key, str)
            and (where == f"$.{key}" or where.startswith((f"$.{key}.", f"$.{key}[")))]
    return max(keys, key=len) if keys else None


def _finding(rel: str, schema_file: str, error: dict, front: dict) -> dict:
    """One validator error as a finding on the record, naming the rule: the schema file, the place and the message."""
    where, why = error["path"], error["message"]
    missing = _REQUIRED.fullmatch(why)
    if where == "$" and missing:
        field = missing.group(1)
        return {"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field, "schema": schema_file, "at": where,
                "message": f"{rel}: missing required field '{field}' ({schema_file} at {where}: {why})"}
    field = _top_key(where, front)
    named = f"field '{field}'" if field is not None else "the record"
    return {"code": "SCHEMA_INVALID_FIELD", "path": rel, "field": field, "schema": schema_file, "at": where,
            "message": f"{rel}: {named} is refused by {schema_file} at {where}: {why}"}


def _same(finding: dict) -> tuple:
    """What makes two findings one: a missing field is one finding whichever rule owes it, and a refusal both
    layouts give is not doubled."""
    if finding["code"] == "SCHEMA_MISSING_FIELD":
        return finding["code"], finding["path"], finding.get("field")
    return finding["code"], finding["path"], finding.get("field"), finding.get("at"), finding["message"]


def run(root: Path) -> tuple[list[dict], dict]:
    """``(findings, result)``: the findings of every record, and what the output states beside them (the count of
    records validated, what was left out and why, the validator and its pin)."""
    root = Path(root)
    findings: list[dict] = []
    per_record: dict[str, list[dict]] = {}
    records: list[tuple[str, str, str]] = []  # (rel, type, schema file)
    fronts: dict[str, dict] = {}
    left_out = 0
    for record_dir in RECORD_PATHS:
        base = root / record_dir
        if not base.is_dir():
            continue
        for md_file in sorted(base.rglob("*.md")):
            rel = md_file.relative_to(root).as_posix()
            if md_file.is_relative_to(root / IMPORTED_DIR):
                left_out += 1
                continue
            try:
                front, unreadable = _frontmatter(md_file.read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError) as error:
                front, unreadable = None, f"the file cannot be read ({error})"
            if unreadable:
                findings.append({"code": "SCHEMA_UNREADABLE_RECORD", "path": rel,
                                 "message": f"{rel}: opens with '---' but {unreadable}: unmeasured"})
                continue
            if front is None:
                continue
            in_audit_dir = md_file.is_relative_to(root / AUDIT_REPORT_DIR)
            record_type = front.get("type", AUDIT_REPORT_TYPE if in_audit_dir else None)
            if not isinstance(record_type, str):
                findings.append({"code": "SCHEMA_INVALID_TYPE", "path": rel,
                                 "message": f"{rel}: 'type' field is missing or not a string"})
                continue
            owed = [] if record_type in STANDALONE_TYPES else [
                {"code": "SCHEMA_MISSING_FIELD", "path": rel, "field": field,
                 "message": f"{rel}: missing required field '{field}' (the shared frontmatter, {COMMON_SCHEMA})"}
                for field in SHARED_FIELDS if field not in front]
            per_record[rel] = owed
            findings.append({"record": rel})  # its place in the order of findings
            schema_file = SCHEMA_MAP.get(record_type)
            if schema_file is None:
                owed.append({"code": "SCHEMA_UNKNOWN_TYPE", "path": rel, "type": record_type,
                             "message": f"{rel}: unknown record type '{record_type}'"})
                continue
            records.append((rel, record_type, schema_file))
            fronts[rel] = front

    program, stated, stops = _validator(root)
    result = {"check": "core-schema", "records_validated": 0,
              "left_out": [{"path": f"{IMPORTED_DIR}/", "files": left_out, "why": LEFT_OUT_WHY}],
              "validator": stated}
    if stops:
        stopped = [{**stop, "records": len(records)} for stop in stops]
        return stopped + _ordered(findings, per_record), result

    # the schema files each layout holds, read by the check itself before any call
    layouts = [schema_dir for schema_dir in SCHEMA_DIRS if (root / schema_dir).is_dir()]
    usable: dict[tuple[str, str], Path] = {}
    for schema_dir in layouts:
        needed = sorted({schema_file for _, _, schema_file in records})
        if needed and (root / schema_dir / COMMON_SCHEMA).exists():
            needed.insert(0, COMMON_SCHEMA)
        broken = False
        for schema_file in needed:
            rel = f"{schema_dir}/{schema_file}"
            if not (root / rel).exists():
                continue
            fault = _schema_fault(root, rel)
            if fault:
                findings.insert(0, {"code": "SCHEMA_UNREADABLE", "path": rel, "message": f"{fault}: unmeasured"})
                broken = broken or schema_file == COMMON_SCHEMA
            elif schema_file != COMMON_SCHEMA:
                usable[(schema_dir, schema_file)] = root / rel
        if broken:  # the shared definitions cannot be read: nothing in this layout is measured
            usable = {key: path for key, path in usable.items() if key[0] != schema_dir}

    measured: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="core-schema-") as scratch:
        by_file: dict[str, tuple[str, dict]] = {}
        batches: dict[tuple[str, str], list[str]] = {}
        for number, (rel, _, schema_file) in enumerate(records):
            instance, front = str(Path(scratch) / f"{number}.json"), fronts[rel]
            try:
                Path(instance).write_text(_instance(front), encoding="utf-8")
            except (TypeError, ValueError) as error:
                per_record[rel].append({"code": "SCHEMA_UNREADABLE_RECORD", "path": rel,
                                        "message": f"{rel}: its frontmatter has no JSON form ({error}): unmeasured"})
                continue
            by_file[instance] = (rel, front)
            for schema_dir in layouts:
                if (schema_dir, schema_file) in usable:
                    batches.setdefault((schema_dir, schema_file), []).append(instance)
        keys = sorted(batches, key=lambda key: (SCHEMA_DIRS.index(key[0]), key[1]))  # the layouts in their order
        with ThreadPoolExecutor(max_workers=max(1, min(8, len(keys)))) as pool:
            answers = list(pool.map(lambda key: _validate(program, usable[key], batches[key]), keys))
        for (schema_dir, schema_file), (errors, fault) in zip(keys, answers):
            if fault:
                findings.insert(0, {"code": "SCHEMA_VALIDATOR_FAILED", "path": f"{schema_dir}/{schema_file}",
                                    "tool": VALIDATOR, "records": len(batches[(schema_dir, schema_file)]),
                                    "message": f"{VALIDATOR} on {schema_dir}/{schema_file} {fault}: its "
                                               "records were not measured"})
            else:
                measured.update(by_file[instance][0] for instance in batches[(schema_dir, schema_file)])
            for error in errors:
                rel, front = by_file[error["filename"]]
                found = _finding(rel, schema_file, error, front)
                if _same(found) not in {_same(held) for held in per_record[rel]}:
                    per_record[rel].append(found)

    written = {rel for rel, _ in by_file.values()}
    for rel, record_type, schema_file in records:
        if rel in written and not any((schema_dir, schema_file) in usable for schema_dir in layouts):
            per_record[rel].append({"code": "SCHEMA_UNREADABLE", "path": rel, "type": record_type,
                                    "message": f"{rel}: unmeasured, the schema {schema_file} cannot be read"})
    result["records_validated"] = len(measured)
    return _ordered(findings, per_record), result


def _ordered(findings: list[dict], per_record: dict[str, list[dict]]) -> list[dict]:
    """The findings in the order of the records, each record's own at its place."""
    ordered = []
    for finding in findings:
        ordered.extend(per_record[finding["record"]] if set(finding) == {"record"} else [finding])
    return ordered


def check(root: Path) -> list[dict]:
    return run(root)[0]


def main() -> int:
    findings, result = run(Path.cwd())
    if findings:
        print(json.dumps({"findings": findings, **result}, indent=2))
        return 1
    print(json.dumps({"ok": True, "result": result}, indent=2))
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
