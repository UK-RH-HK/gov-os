"""W2-64 KPI success 3 (and the live half of 2 and 4): every record of this worktree's head, the close records of
``docs/close/`` included, still validates; core-schema here is green and names ``docs/imported/`` as left out
[DEC-872 item 2, DEC-844, DEC-890 item 1].

The cases run in this worktree's root and only read. core-schema runs as declared, with the installed
check-jsonschema alone on the validator folder of ``PATH``.
"""

from __future__ import annotations

import json
import subprocess

import w2_64_support as S


def _close_records():
    return sorted((S.REPO_ROOT / "docs/close").rglob("CL-*.md"))


def test_core_schema_is_green_here_and_names_docs_imported(tmp_path):
    """*Red.* core-schema in this worktree: exit 0, no finding, and the success form whose result names
    ``docs/imported/`` as left out, as history. Today: exit 0, nothing printed."""
    place = S.Place(tmp_path).real_tool()
    run = S.run_core_schema(S.REPO_ROOT, place)
    assert run.code == 0 and run.findings == [], f"core-schema is not green here\n{run.describe()}"
    assert isinstance(run.output, dict) and run.output.get("ok") is True, \
        f"core-schema does not print the success form here\n{run.describe()}"
    assert S.says_imported_left_out(run.output.get("result")), \
        f"core-schema here does not name {S.IMPORTED} as left out, as history\n{run.describe()}"


def test_this_worktree_holds_close_records_of_both_forms():
    """The live close records hold both forms: W2-66's block, ``base: null`` among them, and none before W2-66.
    Passes today."""
    with_block, base_null, without = [], [], []
    for path in _close_records():
        front, _ = S.frontmatter_of(path.read_text(encoding="utf-8"))
        evidence = front.get("evidence")
        (with_block if isinstance(evidence, dict) else without).append(path.name)
        if isinstance(evidence, dict) and evidence.get("base") is None:
            base_null.append(path.name)
    assert with_block and base_null and without, (with_block, base_null, without)


def test_every_close_record_here_validates_under_the_pinned_validator(tmp_path):
    """Every close record of ``docs/close/`` validates against this worktree's ``close.schema.json`` under the
    installed check-jsonschema, called directly, its ``$ref``s resolved from the schema folder: the records with
    W2-66's block and those written before it. Passes today (the close schema states no block yet); must keep
    passing once it does."""
    instances = []
    for path in _close_records():
        front, _ = S.frontmatter_of(path.read_text(encoding="utf-8"))
        instance = tmp_path / f"{path.parent.name}.json"
        instance.write_text(json.dumps(front, default=lambda value: value.isoformat()), encoding="utf-8")
        instances.append(str(instance))
    assert instances
    schema = S.REPO_ROOT / S.KERNEL_SCHEMAS_REL / "close.schema.json"
    done = subprocess.run([str(S.installed_tool()), "--schemafile", str(schema), *instances], capture_output=True,
                          text=True, timeout=S.TIMEOUT_S, env=S.Place(tmp_path / "place").env())
    assert done.returncode == 0, f"a close record of docs/close/ fails close.schema.json\n{done.stdout}\n{done.stderr}"


def test_the_installed_validator_is_the_pinned_one():
    """The installed check-jsonschema answers the registry's pin (DEC-074), so that the live cases judge with it.
    Passes today."""
    done = subprocess.run([str(S.installed_tool()), "--version"], capture_output=True, text=True, timeout=60)
    assert S.pinned_version() in done.stdout, f"installed: {done.stdout!r}; pinned: {S.pinned_version()}"
