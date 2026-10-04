"""DEC-303: `template/openspec/config.yaml` makes `feature-readiness` the project's default schema.

A change made with `openspec new change <name>`, with no `--schema`, then gets the readiness record. Added after
implementation began, for a delegated decision (README, "Tests added after implementation").
"""

from __future__ import annotations

import pytest

import w1_12_support as support

local_only = pytest.mark.local_only


def test_the_project_config_names_the_forked_schema(get):
    """The committed `template/openspec/config.yaml` has `schema: feature-readiness`."""
    config = get(support.config_doc)
    assert config.get("schema") == support.SCHEMA_NAME, f"template/{support.CONFIG_REL} has schema: " \
                                                        f"{config.get('schema')!r}"


@local_only
def test_a_change_made_without_the_schema_option_gets_the_readiness_record(get, project):
    """In a project made from the template, `openspec status` reports the forked schema and its readiness record."""
    get(support.config_doc)
    project.new_change("no-option")
    status, done = project.json("status", "--change", "no-option")
    assert done.returncode == 0, f"`openspec status --change no-option` failed:\n{done.stdout}\n{done.stderr}"
    assert status["schemaName"] == support.SCHEMA_NAME, f"the change uses schema {status['schemaName']!r}"
    outputs = {artifact["id"]: artifact["outputPath"] for artifact in status["artifacts"]}
    assert outputs.get("readiness") == "readiness.yaml", f"the artifacts of the change: {outputs}"
