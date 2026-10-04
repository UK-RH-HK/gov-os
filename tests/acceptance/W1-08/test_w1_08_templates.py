"""Success 2, first half: every record type has a template that validates against its schema [CAP-06.a]."""

from __future__ import annotations

import pytest

import w1_08_support as support

RECORD_TYPES = sorted(support.RECORD_TYPES)


@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_a_committed_template_exists_for_the_record_type(record_type):
    tracked = set(support.tracked_files())
    for path in support.template_paths(record_type):
        relative = path.relative_to(support.REPO_ROOT).as_posix()
        assert relative in tracked, f"{relative} is not committed"
        assert support.load_record(path), f"{path.name}: the frontmatter is empty"


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_template_validates_against_its_schema(record_type, check):
    schema = support.schema_path(record_type)
    for path in support.template_paths(record_type):
        check.accepts(schema, support.load_record(path), f"the template {path.name}")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_template_validates_as_it_is_written(record_type, check):
    """The frontmatter text itself, read by the validator's YAML reader (dates and numbers as the file has them)."""
    schema = support.schema_path(record_type)
    for path in support.template_paths(record_type):
        check.accepts_file(schema, support.frontmatter_text(path), f"the frontmatter of the template {path.name}")


@pytest.mark.local_only
@pytest.mark.parametrize("record_type", RECORD_TYPES)
def test_the_schema_refuses_a_record_that_is_not_a_map(record_type, check):
    """A schema that accepts everything would pass the tests above."""
    schema = support.schema_path(record_type)
    _, good = support.template(record_type)
    check.good(schema, good, "its own template")
    check.refuses(schema, ["not", "a", "record"], "a list in place of a record")
