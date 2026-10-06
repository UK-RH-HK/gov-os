"""KPI success 8: ``gov`` validates ``governance/project/path-map.yaml`` against
the kernel's path-map schema of W1-08.

The W1-08 schema replaces the minimal schema of W1-07 in ``src/gov/config/``.
The five required top-level keys are: ``state_class``, ``namespaces``,
``capabilities``, ``policies``, ``systems`` (from
``template/governance/kernel/schemas/path-map.schema.json``).

DEC-185: every ``gov`` command loads the ``governance/project/`` files it knows.
DEC-189: an invalid file gives exit 1 with ``CONFIG_INVALID``; ``error.details``
carries ``file`` and ``key``.
DEC-228: W1-27 replaces the minimal schema.
DEC-265: ``languages`` required only when ``code_intelligence`` has ``enabled: true``.
"""

from __future__ import annotations

import json
import re

import pytest

import w1_27_support as support

SOME_INVOCATIONS = (("status",), ("doctor",), ("check", "--list"))


def _write_path_map(project, text):
    path = project / support.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    support.commit_all(project, "a path-map")
    return path


def _details(error, run):
    """``error.details`` as an object with ``file`` and ``key`` (DEC-189)."""
    details = error["details"]
    assert isinstance(details, dict), f"error.details is not an object\n{run.describe()}"
    for name in ("file", "key"):
        assert name in details, f"error.details does not carry {name!r}\n{run.describe()}"
    assert isinstance(details["file"], str) and details["file"].endswith("path-map.yaml"), \
        f"error.details.file does not name path-map.yaml\n{run.describe()}"
    return details


def _config_invalid(gov, interface, args):
    run = gov(*args, "--json")
    error = support.assert_error(run, interface, support.CONFIG_INVALID, exit_code=1, command=args[0])
    return _details(error, run), run


# --------------------------------------------------------------------------
# Valid path maps under the W1-08 schema
# --------------------------------------------------------------------------

def test_valid_w1_08_path_map_loads(gov, project, interface):
    """A path map with all five required top-level keys and valid content loads without error."""
    _write_path_map(project, support.minimal_valid_path_map())
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, \
        f"a valid W1-08 path-map.yaml is refused\n{run.describe()}"


@pytest.mark.parametrize("args", SOME_INVOCATIONS, ids=support.label)
def test_valid_w1_08_path_map_is_not_reported_as_invalid(gov, project, interface, args):
    """A valid W1-08 path map is not reported as CONFIG_INVALID by any command."""
    _write_path_map(project, support.minimal_valid_path_map())
    run = gov(*args, "--json")
    envelope = support.assert_envelope(run, interface, command=args[0])
    code = (envelope.get("error") or {}).get("code")
    assert code != support.CONFIG_INVALID, f"a valid path-map.yaml is reported as invalid\n{run.describe()}"


def test_valid_w1_08_path_map_with_code_intelligence_loads(gov, project, interface):
    """A path map with ``code_intelligence.enabled: true`` and ``languages`` loads (DEC-265)."""
    _write_path_map(project, support.minimal_valid_path_map_with_code_intelligence())
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, \
        f"a valid path map with code_intelligence enabled is refused\n{run.describe()}"


# --------------------------------------------------------------------------
# Missing required top-level keys
# --------------------------------------------------------------------------

@pytest.mark.parametrize("missing_key", ["state_class", "capabilities", "policies", "systems"])
def test_missing_required_top_level_key_names_the_key(gov, project, interface, missing_key):
    """Removing a required top-level key from a valid path map gives CONFIG_INVALID naming that key."""
    lines = support.minimal_valid_path_map().splitlines(keepends=True)
    filtered = []
    skip_block = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(f"{missing_key}:"):
            skip_block = True
            continue
        if skip_block:
            if stripped and not stripped[0].isspace() and not line[0].isspace():
                skip_block = False
            elif line[0] != " " and line[0] != "\n":
                skip_block = False
            else:
                continue
        if not skip_block:
            filtered.append(line)
    text = "".join(filtered)
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"])
    assert missing_key in key_value.lower(), \
        f"error.details.key does not mention {missing_key!r}\n{run.describe()}"


def test_missing_namespaces_names_the_key(gov, project, interface):
    """Removing ``namespaces`` from a valid path map gives CONFIG_INVALID naming ``namespaces``."""
    lines = support.minimal_valid_path_map().splitlines(keepends=True)
    filtered = []
    skip_block = False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith("namespaces:"):
            skip_block = True
            continue
        if skip_block:
            if line[0] != " " and line.strip():
                skip_block = False
            else:
                continue
        if not skip_block:
            filtered.append(line)
    text = "".join(filtered)
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    assert details["key"] == "namespaces" or "namespaces" in json.dumps(details["key"]), \
        f"error.details.key does not name 'namespaces'\n{run.describe()}"


# --------------------------------------------------------------------------
# DEC-265: code_intelligence.enabled: true requires languages
# --------------------------------------------------------------------------

def test_code_intelligence_enabled_without_languages_is_invalid(gov, project, interface):
    """``code_intelligence.enabled: true`` without ``languages`` is CONFIG_INVALID (DEC-265)."""
    text = support.minimal_valid_path_map().replace(
        "  code_intelligence:\n    enabled: false",
        "  code_intelligence:\n    enabled: true",
    )
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"]).lower()
    assert "language" in key_value or "code_intelligence" in key_value, \
        f"error.details.key does not mention languages or code_intelligence\n{run.describe()}"


def test_code_intelligence_disabled_languages_optional(gov, project, interface):
    """``code_intelligence.enabled: false`` with no ``languages`` is valid (DEC-265)."""
    _write_path_map(project, support.minimal_valid_path_map())
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    code = (envelope.get("error") or {}).get("code")
    assert code != support.CONFIG_INVALID, \
        f"disabled code_intelligence without languages is invalid\n{run.describe()}"


# --------------------------------------------------------------------------
# Namespace shape
# --------------------------------------------------------------------------

def test_namespace_missing_required_field_is_invalid(gov, project, interface):
    """A namespace that lacks one of the nine required fields is CONFIG_INVALID."""
    text = support.minimal_valid_path_map().replace(
        "    deletion_rebuild: authoritative",
        "",
    )
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"]).lower()
    assert "namespace" in key_value or "deletion_rebuild" in key_value, \
        f"error.details.key does not mention the missing namespace field\n{run.describe()}"


def test_namespaces_of_the_wrong_type_names_the_key(gov, project, interface):
    """``namespaces: 42`` (not a map) gives CONFIG_INVALID naming ``namespaces``."""
    text = support.minimal_valid_path_map()
    text = re.sub(r"namespaces:\n(?:  .*\n)*", "namespaces: 42\n", text)
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    assert "namespaces" in json.dumps(details["key"]), \
        f"error.details.key does not mention 'namespaces'\n{run.describe()}"


# --------------------------------------------------------------------------
# Policy and system shape
# --------------------------------------------------------------------------

def test_missing_policy_key_is_invalid(gov, project, interface):
    """Removing a required policy key (e.g. ``security``) gives CONFIG_INVALID."""
    text = support.minimal_valid_path_map().replace("  security: hard-block\n", "")
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"]).lower()
    assert "security" in key_value or "policies" in key_value, \
        f"error.details.key does not mention the missing policy\n{run.describe()}"


def test_missing_system_is_invalid(gov, project, interface):
    """Removing a required system (e.g. ``skills``) gives CONFIG_INVALID."""
    text = support.minimal_valid_path_map()
    text = re.sub(r"  skills:\n    status: absent\n    reason: minimal fixture\n", "", text)
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"]).lower()
    assert "skills" in key_value or "systems" in key_value, \
        f"error.details.key does not mention the missing system\n{run.describe()}"


def test_absent_system_without_reason_is_invalid(gov, project, interface):
    """A system with ``status: absent`` but no ``reason`` is CONFIG_INVALID."""
    text = support.minimal_valid_path_map().replace(
        "  constitution-and-policies:\n    status: absent\n    reason: minimal fixture",
        "  constitution-and-policies:\n    status: absent",
    )
    _write_path_map(project, text)
    details, run = _config_invalid(gov, interface, ("status",))
    key_value = json.dumps(details["key"]).lower()
    assert "reason" in key_value or "constitution" in key_value or "system" in key_value, \
        f"error.details.key does not mention the missing reason\n{run.describe()}"


def test_repairing_the_key_clears_the_error(gov, project, interface):
    """The error follows the file as it is now: replacing an invalid path map with a valid one loads."""
    bad_text = support.minimal_valid_path_map().replace("  security: hard-block\n", "")
    _write_path_map(project, bad_text)
    _config_invalid(gov, interface, ("status",))
    _write_path_map(project, support.minimal_valid_path_map())
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, run.describe()
