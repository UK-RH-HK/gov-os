"""F3 (a check run that is not the tree's own declaration) and the declaration rules of L3.

The reference tool ran a built-in ``python3 -m gov.check.<module>`` for a family the tree does not declare. This pass
never does: only the tree's own declared ``command`` strings run. The cases plant stand-ins for every module such a
built-in list names (``src/gov/check/schema.py``, ``graph.py``, ``claims.py``, ``mutation.py``, ``authority.py``,
``pathmap.py``, ``audit_validator.py``, ``skill_validator.py`` and ``src/gov/adapters/portability.py``), each recording
if it is ever run, and assert none was.
"""

from __future__ import annotations

import pytest

import w2_158_support as support
from w2_158_support import DECL_DIR, ALT_DECL_DIR, FAMILIES, OUTPUT_ORDER

UNDECLARED = ("graph", "claims", "mutation", "authority", "pathmap", "audit", "skills")


def test_f3_the_declared_marker_runs_and_no_built_in_command_does(tree):
    """Only ``core-schema`` is declared, with a marker command, in a tree that holds every built-in module's stand-in: the
    marker runs (``schema: ok``); every other family reads ``skipped (no declaration)`` and no stand-in ran. The same with a
    base whose range touches the kernel (portability would run if it were declared): ``portability: skipped (no declaration)``,
    still no stand-in run."""
    tree.plant_builtins()
    tree.declare_family("schema", "ok")
    base = tree.commit("the base")
    outcome = tree.structural()
    lines = outcome.lines()
    assert lines[0] == "schema: ok", outcome.text()
    for name in UNDECLARED:
        assert lines[OUTPUT_ORDER.index(name)] == f"{name}: skipped (no declaration)", f"{name}: {lines}"
    assert tree.started() == ["core-schema"], tree.started()
    assert tree.builtins_run() == [], f"a built-in command ran: {tree.builtins_run()}"
    tree.commit("kernel", files={"template/governance/kernel/skills/x/SKILL.md": "a\n"})
    again = tree.structural(base)
    assert again.family("portability") == "portability: skipped (no declaration)", again.text()
    assert tree.builtins_run() == [], f"a built-in command ran: {tree.builtins_run()}"
    assert tree.started() == ["core-schema"], tree.started()


def test_f3_a_tree_with_no_declaration_at_all_reads_every_family_as_skipped(tree):
    """No declaration anywhere (and the built-in stand-ins present): all eight families read ``skipped (no declaration)``,
    exit 0, the last line is there, nothing ran."""
    tree.plant_builtins()
    tree.commit("nothing declared")
    outcome = tree.structural()
    lines = outcome.lines()
    assert len(lines) == len(OUTPUT_ORDER) + 1, outcome.text()
    for name in FAMILIES:
        assert lines[OUTPUT_ORDER.index(name)] == f"{name}: skipped (no declaration)", lines
    assert lines[-1].startswith(f"structural pass at {tree.head12()}"), lines[-1]
    assert tree.started() == [] and tree.builtins_run() == []


def test_f3_a_declaration_under_governance_kernel_checks_is_used_when_the_template_layout_has_none_and_the_templates_wins(tree):
    """``governance/kernel/checks/<id>.yaml`` is used for an id the template layout does not declare (graph: only there);
    where both hold one, the ``template/governance/kernel/checks/`` one runs and the other does not (schema)."""
    tree.declare("core-schema", tree.marker_command("schema-template"), family="schema/invariants", folder=DECL_DIR)
    tree.declare("core-schema", tree.marker_command("schema-governance"), family="schema/invariants", folder=ALT_DECL_DIR)
    tree.declare("core-graph", tree.marker_command("graph-governance"), family="graph", folder=ALT_DECL_DIR)
    tree.commit()
    outcome = tree.structural()
    lines = outcome.lines()
    assert lines[0] == "schema: ok" and lines[1] == "graph: ok", outcome.text()
    assert tree.started() == ["graph-governance", "schema-template"], tree.started()
    assert lines[OUTPUT_ORDER.index("claims")] == "claims: skipped (no declaration)", lines


@pytest.mark.parametrize("text, what", [
    ("id: core-mutation\ncommand: [unclosed\n", "YAML that does not parse"),
    ("id: core-mutation\nfamily: mutation\ntier: G1\nseverity: hard-block\n", "no command"),
    ("id: core-mutation\ncommand: 5\n", "a command that is not a string"),
    ("- a\n- b\n", "a YAML list, not a mapping"),
])
def test_f3_a_declaration_that_cannot_be_read_makes_only_its_own_family_a_notice_naming_the_file(tree, text, what):
    """One declaration file that cannot be read or has no string ``command`` (``core-mutation.yaml``): the mutation family
    reads NOTICE naming that file, every other family is judged as usual, exit 0."""
    tree.declare_family("schema", "ok")
    tree.declare_family("graph", "ok")
    path = tree.tree / DECL_DIR / "core-mutation.yaml"
    path.write_text(text)
    tree.commit()
    outcome = tree.structural()
    lines = outcome.lines()
    line = lines[OUTPUT_ORDER.index("mutation")]
    assert line.startswith("mutation: NOTICE ") and "core-mutation.yaml" in line, f"{what}: {line!r}\n{outcome.text()}"
    assert lines[0] == "schema: ok" and lines[1] == "graph: ok", lines
    assert lines[OUTPUT_ORDER.index("claims")] == "claims: skipped (no declaration)", lines
    assert tree.started() == ["core-graph", "core-schema"], tree.started()
