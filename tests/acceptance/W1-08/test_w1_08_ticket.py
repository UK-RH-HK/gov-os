"""The ticket schema.

Success 1: the ticket carries class, role, depends_on, allowed_paths, kpis, profile, sources, est_loc and
acceptance_tests [CAP-31.a]; the profile is LITE, STANDARD or FULL [CAP-53.a].
Failure 1: a schema accepts a ticket without kpis, role or allowed_paths.

The good ticket is the committed ticket template; each bad ticket is that template with one change. The 48
committed tickets of this repository are valid tickets too (DEC-229).
"""

from __future__ import annotations

import pytest

import w1_08_support as support

TICKET_FIELDS = ("class", "role", "depends_on", "allowed_paths", "kpis", "profile", "sources", "est_loc",
                 "acceptance_tests")
# One value per field that no reading of the field allows.
WRONG_VALUES = {
    "class": 42,
    "role": 42,
    "depends_on": 42,
    "allowed_paths": 42,
    "kpis": 42,
    "profile": "HUGE",
    "sources": 42,
    "est_loc": "many",
    "acceptance_tests": 42,
}
REQUIRED_BY_THE_KPI = ("kpis", "role", "allowed_paths")
PROFILES = ("LITE", "STANDARD", "FULL")


@pytest.fixture
def ticket():
    schema = support.schema_path("ticket")
    _, good = support.template("ticket")
    return schema, good


def test_the_ticket_template_carries_the_nine_fields():
    path, good = support.template("ticket")
    missing = [field for field in TICKET_FIELDS if field not in good]
    assert not missing, f"the ticket template {path.name} has no {missing}"
    assert good.get("profile") in PROFILES, f"{path.name}: profile is {good.get('profile')!r}, not one of {PROFILES}"


@pytest.mark.local_only
@pytest.mark.parametrize("field", TICKET_FIELDS)
def test_the_ticket_schema_defines_the_field(field, ticket, check):
    """The schema knows the field: a value of the wrong kind is refused."""
    schema, good = ticket
    check.good(schema, good, "the ticket template")
    check.refuses(schema, support.replaced(good, field, WRONG_VALUES[field]),
                  f"a ticket whose `{field}` is {WRONG_VALUES[field]!r}")


@pytest.mark.local_only
@pytest.mark.parametrize("field", REQUIRED_BY_THE_KPI)
def test_a_ticket_without_the_field_is_refused(field, ticket, check):
    """Left out, or null in its place: both are a ticket without the field."""
    schema, good = ticket
    assert field in good, f"the ticket template has no `{field}`"
    check.good(schema, good, "the ticket template")
    check.refuses(schema, support.without(good, field), f"a ticket without `{field}`")
    check.refuses(schema, support.replaced(good, field, None), f"a ticket whose `{field}` is null")


@pytest.mark.local_only
def test_a_ticket_without_kpis_role_and_allowed_paths_is_refused(ticket, check):
    schema, good = ticket
    bad = support.without(support.without(support.without(good, "kpis"), "role"), "allowed_paths")
    check.good(schema, good, "the ticket template")
    check.refuses(schema, bad, "a ticket without `kpis`, `role` and `allowed_paths`")


@pytest.mark.local_only
def test_the_three_profiles_are_accepted_and_no_other(ticket, check):
    schema, good = ticket
    for profile in PROFILES:
        check.accepts(schema, support.replaced(good, "profile", profile), f"a ticket with profile {profile}")
    for profile in ("MEDIUM", "standard", ""):
        check.refuses(schema, support.replaced(good, "profile", profile), f"a ticket with profile {profile!r}")


@pytest.mark.local_only
def test_the_committed_tickets_validate_against_the_ticket_schema(check):
    """DEC-229: tickets carry `state_class` too, and the committed ones already do. A ticket schema that refuses
    this repository's own tickets (their ids, their `tk` fields) is not the schema of these records."""
    schema = support.schema_path("ticket")
    check.accepts_all(schema, support.committed_tickets(), "a committed ticket of this repository")
