"""KPI: the forked OpenSpec schema carries all 26 rows x 5 states exactly as readiness-dimensions.yaml [CAP-30.a].

Failure KPI: a row name or a state differs from readiness-dimensions.yaml. Every expected value is read from the
YAML when the test runs.
"""

from __future__ import annotations

import w1_12_support as support


def test_schema_is_where_openspec_looks_for_it(schema):
    """`template/openspec/schemas/feature-readiness/schema.yaml` is an OpenSpec schema of that name."""
    assert schema.get("name") == support.SCHEMA_NAME, (
        f"schema.yaml names the schema {schema.get('name')!r}; OpenSpec resolves it by its folder, "
        f"{support.SCHEMA_NAME!r} (ADR-0002, product layout)")


def test_fork_keeps_the_base_workflow_and_adds_the_readiness_record(get):
    """A fork of `spec-driven`: its four artifacts stay, and one artifact is the feature-readiness record."""
    artifacts = get(support.artifacts)
    missing = [name for name in support.BASE_ARTIFACTS if name not in artifacts]
    assert not missing, f"the fork dropped artifacts of {support.BASE_SCHEMA}: {missing} (has {list(artifacts)})"
    get(support.readiness_artifact)


def test_every_row_is_carried_by_its_id_in_order(get):
    """The same rows as the YAML, by number and key, none missing, none added, in the YAML's order."""
    expected = [(n, key) for n, key, _ in support.source_rows()]
    assert len(expected) == 26, f"{support.SOURCE_REL} no longer has 26 rows"
    actual = [(n, key) for n, key, _ in get(support.carried_rows)]
    missing = [row for row in expected if row not in actual]
    extra = [row for row in actual if row not in expected]
    assert not missing and not extra, f"rows missing from the schema: {missing}; rows not in the YAML: {extra}"
    assert actual == expected, "the schema carries the rows in another order than the YAML, or carries one twice"


def test_every_row_name_is_the_name_in_the_yaml(get):
    """Failure KPI: a row name differs. Names are compared character by character, per row id."""
    expected = {(n, key): name for n, key, name in support.source_rows()}
    actual = {(n, key): name for n, key, name in get(support.carried_rows)}
    differing = {row: (actual.get(row), name) for row, name in expected.items() if actual.get(row) != name}
    assert not differing, f"row names that differ, as row: (schema, YAML): {differing}"


def test_the_five_states_are_carried_exactly(get):
    """Failure KPI: a state differs. The same state names as the YAML, none missing, none added, in its order."""
    expected = support.source_states()
    assert len(expected) == 5, f"{support.SOURCE_REL} no longer has 5 states"
    assert get(support.carried_states) == expected


def test_the_only_not_applicable_state_needs_a_reason(get):
    """A silent N/A is invalid (MR-1): no state is a bare N/A, and the N/A state carries `requires: reason`."""
    wanted = {entry["state"]: entry["requires"] for entry in support.source()["cell_states"] if "requires" in entry}
    entries = get(support.carried_state_entries)
    carried = {entry["state"]: entry.get("requires") for entry in entries if isinstance(entry, dict)}
    for state, requires in wanted.items():
        assert carried.get(state) == requires, (
            f"state {state} must carry `requires: {requires}` as in the YAML; the schema has {carried.get(state)!r}")
    bare = [name for name in get(support.carried_states)
            if name.upper().replace(" ", "").startswith("N/A") and name not in wanted]
    assert not bare, f"the schema has a not-applicable state without a reason: {bare}"


def test_the_readiness_record_template_lists_every_row(get):
    """The fresh record has each of the 26 rows once, under the row's key or name."""
    path = get(lambda: support.template_path(support.readiness_artifact()))
    cells = get(lambda: support.record_cells(path))
    missing = [(n, name) for n, _, name in support.source_rows() if n not in cells]
    twice = [(n, name) for n, _, name in support.source_rows() if len(cells.get(n, [])) > 1]
    assert not missing, f"rows the readiness record template does not list: {missing}"
    assert not twice, f"rows the readiness record template lists more than once: {twice}"


def test_the_readiness_record_template_fills_no_cell(get):
    """No defaulted N/A (DEC-085) and no empty cell (MR-1): on first use every row is MISSING, "no answer yet"."""
    unanswered = [entry["state"] for entry in support.source()["cell_states"]
                  if not entry["satisfies"] and entry["meaning"] == "no answer yet"]
    assert len(unanswered) == 1, f"{support.SOURCE_REL} no longer has one `no answer yet` state"
    path = get(lambda: support.template_path(support.readiness_artifact()))
    cells = get(lambda: support.record_cells(path))
    assert cells, "the readiness record template lists no row"
    wrong = {n: states for n, states in cells.items() if states != unanswered}
    assert not wrong, f"cells of the fresh record that are not {unanswered[0]} (row: state): {wrong}"
