"""KPI: the schema carries the capability-type table for STANDARD rows; a change to the taxonomy or to
readiness-dimensions.yaml is accepted only with a linked CIT-E record [CAP-30.e].

The table is `capability_types.extra_rows_for_standard` of readiness-dimensions.yaml (DEC-085). Every expected value
is read from the YAML when the test runs, so a change to the YAML that the schema does not carry turns these red.
"""

from __future__ import annotations

import w1_12_support as support


def _source_table():
    return support.source()["capability_types"]["extra_rows_for_standard"]


def test_the_table_has_the_capability_types_of_the_yaml(get):
    """The same taxonomy: no capability type missing, none added."""
    expected = set(_source_table())
    actual = set(get(support.carried_table))
    assert actual == expected, (f"capability types missing from the schema: {sorted(expected - actual)}; "
                                f"types not in the YAML: {sorted(actual - expected)}")


def test_each_capability_type_marks_the_rows_of_the_yaml(get):
    """Per capability type, the same extra rows for STANDARD."""
    expected = {name: sorted(rows) for name, rows in _source_table().items()}
    actual = {name: sorted(rows) for name, rows in get(support.carried_table).items()}
    differing = {name: (actual.get(name), rows) for name, rows in expected.items() if actual.get(name) != rows}
    assert not differing, f"rows that differ, as type: (schema, YAML): {differing}"


def test_the_table_marks_only_rows_the_schema_carries(get):
    """Every row number in the carried table is one of the carried rows."""
    numbers = {n for n, _, _ in get(support.carried_rows)}
    unknown = {name: [row for row in rows if row not in numbers]
               for name, rows in get(support.carried_table).items()}
    unknown = {name: rows for name, rows in unknown.items() if rows}
    assert not unknown, f"the table marks rows the schema does not carry: {unknown}"


def test_the_schema_states_the_governed_change_rule(get):
    """The taxonomy's source and its extension rule (only through CIT-P and CIT-E) are carried as the YAML has them."""
    expected = support.source()["capability_types"]
    actual = get(support.carried_capability_types)
    assert "CIT-E" in expected["extension"], f"{support.SOURCE_REL} no longer names CIT-E in its extension rule"
    for field in ("source", "extension"):
        assert actual.get(field) == expected[field], (
            f"`capability_types.{field}` in the schema is {actual.get(field)!r}; the YAML has {expected[field]!r}")
