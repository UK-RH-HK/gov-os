"""KPI success 3, first half, as DEC-185 states it: configuration loading and ``CONFIG_INVALID``.

Every ``gov`` command loads the ``governance/project/`` files it knows:
``path-map.yaml`` now. A missing file is not an error. An invalid one gives exit
code 1 with ``CONFIG_INVALID``, naming the file.

The cases here are invalid under any path-map schema: a file that is not YAML,
and a file whose top level is not a map. A case that names one invalid *key*
needs the minimal schema's shape, which no source states; see the decision
package in the README.
"""

from __future__ import annotations

import json
import shutil

import pytest

import w1_07_support as support

INVALID_FILES = {
    "not-yaml": "namespaces: [unclosed\nother: }\n",
    "a-list": "- src/**\n- docs/**\n",
    "a-scalar": "just one line of text\n",
}


def _write_path_map(project, text):
    path = project / support.PATH_MAP_REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    support.commit_all(project, "a path-map")
    return path


def _remove_path_map(project):
    path = project / support.PATH_MAP_REL
    if path.exists():
        path.unlink()
        support.commit_all(project, "no path-map")


def _assert_names_the_file(error, run):
    text = json.dumps(error)
    assert "path-map.yaml" in text, f"the CONFIG_INVALID error does not name the file\n{run.describe()}"


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
def test_a_missing_path_map_is_not_an_error(gov, project, interface, args):
    _remove_path_map(project)
    run = gov(*args, "--json")
    envelope = support.assert_envelope(run, interface, command=args[0])
    code = (envelope.get("error") or {}).get("code")
    assert code != support.CONFIG_INVALID, f"a missing path-map.yaml is reported as invalid\n{run.describe()}"


def test_status_succeeds_without_a_path_map(gov, project, interface):
    _remove_path_map(project)
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, run.describe()


def test_status_succeeds_without_a_governance_project_folder(gov, project, interface):
    shutil.rmtree(project / "governance" / "project", ignore_errors=True)
    support.commit_all(project, "no governance/project")
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True and run.returncode == 0, run.describe()


@pytest.mark.parametrize("args", support.EVERY_INVOCATION, ids=support.label)
@pytest.mark.parametrize("case", sorted(INVALID_FILES))
def test_an_invalid_path_map_gives_config_invalid_on_every_command(gov, project, interface, case, args):
    _write_path_map(project, INVALID_FILES[case])
    run = gov(*args, "--json")
    error = support.assert_error(run, interface, support.CONFIG_INVALID, exit_code=1, command=args[0])
    _assert_names_the_file(error, run)


def test_an_invalid_path_map_gives_exit_code_1_without_json(gov, project):
    _write_path_map(project, INVALID_FILES["a-list"])
    run = gov("status")
    assert run.returncode == 1, f"an invalid path-map.yaml must end with exit code 1\n{run.describe()}"
    assert "path-map.yaml" in run.stdout + run.stderr, f"the message does not name the file\n{run.describe()}"


def test_root_decides_which_path_map_is_loaded(gov, project, interface, sandbox):
    """``--root`` decides which project's configuration is loaded, not the working directory."""
    _write_path_map(project, INVALID_FILES["a-list"])
    run = gov("status", "--json", "--root", str(project), cwd=sandbox.elsewhere)
    error = support.assert_error(run, interface, support.CONFIG_INVALID, exit_code=1, command="status")
    _assert_names_the_file(error, run)


def test_repairing_the_path_map_clears_the_error(gov, project, interface):
    """The error comes from the file as it is now: once the file is gone, the command works again."""
    path = _write_path_map(project, INVALID_FILES["not-yaml"])
    support.assert_error(gov("status", "--json"), interface, support.CONFIG_INVALID, exit_code=1)
    path.unlink()
    run = gov("status", "--json")
    envelope = support.assert_envelope(run, interface, command="status")
    assert envelope["ok"] is True, run.describe()
