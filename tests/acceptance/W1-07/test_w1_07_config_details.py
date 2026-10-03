"""KPI success 3, first half, as DEC-189 states it: what ``CONFIG_INVALID`` carries, and the minimal path-map shape.

- **Stable contract.** An invalid ``governance/project/`` file gives exit code 1
  with ``CONFIG_INVALID``, and ``error.details`` carries ``file`` and ``key``.
- **Provisional shape.** The top level of ``path-map.yaml`` is a map;
  ``namespaces`` is required and maps a name to a map. This holds until W1-08
  replaces the minimal schema; if W1-08 changes the keys, the cases marked
  *provisional* below are revised with it.

The documents are written from DEC-189's sentence alone, not from the schema
under ``src/gov/config/``.
"""

from __future__ import annotations

import json

import pytest

import w1_07_support as support

# Provisional (DEC-189): valid under "the top level is a map; namespaces maps a name to a map".
VALID_PATH_MAP = "namespaces:\n  core: {}\n"

# Provisional (DEC-189): ``namespaces`` is there, and is not a map.
NAMESPACES_OF_THE_WRONG_TYPE = {
    "a-number": "namespaces: 42\n",
    "a-list": "namespaces:\n  - core\n  - docs\n",
    "a-string": "namespaces: core\n",
}

# Provisional (DEC-189): the top level is a map, and ``namespaces`` is not in it.
NAMESPACES_MISSING = "{}\n"

# Provisional (DEC-189): ``namespaces`` is a map, and one name does not map to a map.
A_NAMESPACE_THAT_IS_NOT_A_MAP = "namespaces:\n  core: 42\n"

# Invalid under any schema (the cases of test_w1_07_config.py): no key is at fault, the file is.
INVALID_FILES = {
    "not-yaml": "namespaces: [unclosed\nother: }\n",
    "a-list": "- src/**\n- docs/**\n",
    "a-scalar": "just one line of text\n",
}

# A built command, a command not yet built, and the second built invocation.
SOME_INVOCATIONS = (("status",), ("doctor",), ("check", "--list"))


def _write_path_map(project, text):
    path = project / support.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    support.commit_all(project, "a path-map")
    return path


def _details(error, run):
    """``error.details`` as an object that carries ``file`` and ``key`` (DEC-189); ``file`` names the path-map."""
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
# Stable contract: error.details carries file and key
# --------------------------------------------------------------------------

@pytest.mark.parametrize("case", sorted(INVALID_FILES))
def test_a_file_level_error_carries_file_and_key_in_details(gov, project, interface, case):
    """The value of ``key`` for a file that is invalid as a whole is not stated, so it is not asserted."""
    _write_path_map(project, INVALID_FILES[case])
    _config_invalid(gov, interface, ("status",))


def test_details_file_names_the_path_map_of_the_root_given(gov, project, interface, sandbox):
    _write_path_map(project, NAMESPACES_OF_THE_WRONG_TYPE["a-number"])
    run = gov("status", "--json", "--root", str(project), cwd=sandbox.elsewhere)
    error = support.assert_error(run, interface, support.CONFIG_INVALID, exit_code=1, command="status")
    assert _details(error, run)["key"] == "namespaces", run.describe()


# --------------------------------------------------------------------------
# Provisional shape (until W1-08): namespaces is required and maps a name to a map
# --------------------------------------------------------------------------

def test_a_valid_path_map_loads(gov, project, interface):
    _write_path_map(project, VALID_PATH_MAP)
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, f"a valid path-map.yaml is refused\n{run.describe()}"


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
def test_a_valid_path_map_is_not_reported_as_invalid_by_any_command(gov, project, interface, args):
    _write_path_map(project, VALID_PATH_MAP)
    run = gov(*args, "--json")
    envelope = support.assert_envelope(run, interface, command=args[0])
    code = (envelope.get("error") or {}).get("code")
    assert code != support.CONFIG_INVALID, f"a valid path-map.yaml is reported as invalid\n{run.describe()}"


@pytest.mark.parametrize("args", SOME_INVOCATIONS, ids=support.label)
@pytest.mark.parametrize("case", sorted(NAMESPACES_OF_THE_WRONG_TYPE))
def test_namespaces_of_the_wrong_type_names_the_key(gov, project, interface, case, args):
    _write_path_map(project, NAMESPACES_OF_THE_WRONG_TYPE[case])
    details, run = _config_invalid(gov, interface, args)
    assert details["key"] == "namespaces", f"error.details.key does not name 'namespaces'\n{run.describe()}"


@pytest.mark.parametrize("args", SOME_INVOCATIONS, ids=support.label)
def test_a_missing_namespaces_names_the_key(gov, project, interface, args):
    _write_path_map(project, NAMESPACES_MISSING)
    details, run = _config_invalid(gov, interface, args)
    assert details["key"] == "namespaces", f"error.details.key does not name 'namespaces'\n{run.describe()}"


def test_a_namespace_that_is_not_a_map_is_invalid(gov, project, interface):
    """How a key below ``namespaces`` is written (``namespaces.core``, a list, a pointer) is not stated: only that
    ``key`` is there and mentions ``namespaces`` is asserted."""
    _write_path_map(project, A_NAMESPACE_THAT_IS_NOT_A_MAP)
    details, run = _config_invalid(gov, interface, ("status",))
    assert "namespaces" in json.dumps(details["key"]), \
        f"error.details.key does not mention 'namespaces'\n{run.describe()}"


def test_repairing_the_key_clears_the_error(gov, project, interface):
    """The error follows the file as it is now: the same file with a valid ``namespaces`` loads."""
    _write_path_map(project, NAMESPACES_OF_THE_WRONG_TYPE["a-number"])
    _config_invalid(gov, interface, ("status",))
    _write_path_map(project, VALID_PATH_MAP)
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, run.describe()
