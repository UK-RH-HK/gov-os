"""Builder tests for the gov CLI skeleton (W1-07).

Regression evidence only (DEC-136). They cover what the acceptance tests leave
to the builder: ``CONFIG_INVALID`` naming the key against the minimal path-map
schema (DEC-185), an invalid check declaration, and the registry's classes.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "src"))

from gov.cli.checks import CHECKS_DIR, INSTALLED_CHECKS_DIR  # noqa: E402
from gov.cli.main import COMMANDS, main  # noqa: E402

PATH_MAP_REL = "governance/project/path-map.yaml"


def _run(capsys, root, *args):
    code = main([*args, "--json", "--root", str(root)])
    return code, json.loads(capsys.readouterr().out)


def _write(root, rel, text):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_a_valid_path_map_loads(tmp_path, capsys):
    _write(tmp_path, PATH_MAP_REL, "namespaces:\n  product:\n    paths: [src/**]\nother: kept\n")
    code, envelope = _run(capsys, tmp_path, "status")
    assert code == 0 and envelope["ok"] is True
    assert envelope["result"]["config_files"] == ["path-map.yaml"]


@pytest.mark.parametrize("text, key", [
    ("other: 1\n", "namespaces"),
    ("namespaces: 42\n", "namespaces"),
    ("namespaces:\n  product: [src/**]\n", "namespaces.product"),
], ids=["missing", "not-a-map", "value-not-a-map"])
def test_config_invalid_names_the_file_and_the_key(tmp_path, capsys, text, key):
    _write(tmp_path, PATH_MAP_REL, text)
    code, envelope = _run(capsys, tmp_path, "status")
    assert code == 1 and envelope["ok"] is False and envelope["result"] == {}
    error = envelope["error"]
    assert error["code"] == "CONFIG_INVALID"
    assert error["details"] == {"file": PATH_MAP_REL, "key": key}
    assert PATH_MAP_REL in error["message"] and key in error["message"]


@pytest.mark.parametrize("text, key", [
    ("- a list\n", None),
    ('id: "a"\nfamily: "f"\ntier: "G1"\ncommand: "true"\n', "severity"),
    ('id: "a"\nfamily: "f"\ntier: "G1"\nseverity: "fatal"\ncommand: "true"\n', "severity"),
    ('id: "a"\nfamily: "f"\ntier: 1\nseverity: "warning"\ncommand: "true"\n', "tier"),
], ids=["not-a-map", "missing-field", "severity-outside-the-two-words", "field-not-a-string"])
def test_an_invalid_check_declaration_is_refused_not_listed(tmp_path, capsys, text, key):
    _write(tmp_path, f"{CHECKS_DIR}/a.yaml", text)
    code, envelope = _run(capsys, tmp_path, "check", "--list")
    assert code == 1 and envelope["error"]["code"] == "CHECK_DECLARATION_INVALID"
    assert envelope["error"]["details"] == {"file": f"{CHECKS_DIR}/a.yaml", "key": key}


DECLARATION = 'id: "a"\nfamily: "f"\ntier: "G1"\nseverity: "warning"\ncommand: "true"\n'


def test_the_declarations_of_both_layouts_are_listed_each_check_once(tmp_path, capsys):
    """DEC-579: alike in the two layouts is one check; a file that one layout alone holds is listed."""
    _write(tmp_path, f"{CHECKS_DIR}/a.yaml", DECLARATION)
    _write(tmp_path, f"{INSTALLED_CHECKS_DIR}/a.yaml", DECLARATION)
    _write(tmp_path, f"{INSTALLED_CHECKS_DIR}/b.yaml", DECLARATION.replace('"a"', '"b"'))
    code, envelope = _run(capsys, tmp_path, "check", "--list")
    assert code == 0 and [each["id"] for each in envelope["result"]["checks"]] == ["a", "b"]


def test_one_check_id_declared_differently_in_the_two_layouts_is_refused(tmp_path, capsys):
    _write(tmp_path, f"{CHECKS_DIR}/a.yaml", DECLARATION)
    _write(tmp_path, f"{INSTALLED_CHECKS_DIR}/a.yaml", DECLARATION + 'allows-not-applicable: "true"\n')
    code, envelope = _run(capsys, tmp_path, "check", "--list")
    error = envelope["error"]
    assert code == 1 and error["code"] == "CHECK_DECLARATION_INVALID"
    assert error["details"] == {"file": f"{INSTALLED_CHECKS_DIR}/a.yaml", "key": "allows-not-applicable"}
    assert error["message"].startswith(f"{CHECKS_DIR}/a.yaml and {INSTALLED_CHECKS_DIR}/a.yaml: ")


def test_the_read_commands_are_those_of_cap_27():
    read = {command.name for command in COMMANDS if command.cls == "read"}
    assert read == {"status", "check", "readiness", "doctor", "context", "closure", "retrieve"}
    assert all(command.cls in ("read", "act") for command in COMMANDS)
    assert all(command.act_paths == () for command in COMMANDS)


def test_a_usage_error_ends_with_exit_code_2(capsys):
    with pytest.raises(SystemExit) as stop:
        main(["status", "--no-such-option", "--json"])
    assert stop.value.code == 2
    assert capsys.readouterr().out == ""
