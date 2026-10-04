"""The ticket schema.

Success 1: the ticket carries class, role, depends_on, allowed_paths, kpis, profile, sources, est_loc and
acceptance_tests [CAP-31.a]; the profile is LITE, STANDARD or FULL [CAP-53.a].
Failure 1: a schema accepts a ticket without kpis, role or allowed_paths.

The good ticket is the committed ticket template; each bad ticket is that template with one change.
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
PROFILES = ("LITE", "STANDARD", "FULL")


@pytest.fixture
def ticket():
    schema = support.schema_path("ticket")
    _, good = support.template("ticket")
    return schema, good


@pytest.mark.parametrize("field", TICKET_FIELDS)
def test_the_ticket_template_carries_the_field(field):
    path, good = support.template("ticket")
    assert field in good, f"the ticket template {path.name} has no `{field}`"


@pytest.mark.local_only
@pytest.mark.parametrize("field", TICKET_FIELDS)
def test_the_ticket_schema_defines_the_field(field, ticket, check):
    """The schema knows the field: a value of the wrong kind is refused."""
    schema, good = ticket
    check.accepts(schema, good, "the ticket template")
    check.refuses(schema, support.replaced(good, field, WRONG_VALUES[field]),
                  f"a ticket whose `{field}` is {WRONG_VALUES[field]!r}")


@pytest.mark.local_only
@pytest.mark.parametrize("field", ("kpis", "role", "allowed_paths"))
def test_a_ticket_without_the_field_is_refused(field, ticket, check):
    schema, good = ticket
    assert field in good, f"the ticket template has no `{field}`"
    check.accepts(schema, good, "the ticket template")
    check.refuses(schema, support.without(good, field), f"a ticket without `{field}`")


@pytest.mark.local_only
def test_a_ticket_without_kpis_role_and_allowed_paths_is_refused(ticket, check):
    schema, good = ticket
    bad = support.without(support.without(support.without(good, "kpis"), "role"), "allowed_paths")
    check.accepts(schema, good, "the ticket template")
    check.refuses(schema, bad, "a ticket without `kpis`, `role` and `allowed_paths`")


@pytest.mark.local_only
@pytest.mark.parametrize("field", ("kpis", "role", "allowed_paths"))
def test_a_ticket_whose_field_is_null_is_refused(field, ticket, check):
    """A null in place of the field is no better than leaving it out."""
    schema, good = ticket
    check.accepts(schema, good, "the ticket template")
    check.refuses(schema, support.replaced(good, field, None), f"a ticket whose `{field}` is null")


@pytest.mark.local_only
@pytest.mark.parametrize("profile", PROFILES)
def test_each_profile_is_accepted(profile, ticket, check):
    schema, good = ticket
    check.accepts(schema, support.replaced(good, "profile", profile), f"a ticket with profile {profile}")


@pytest.mark.local_only
@pytest.mark.parametrize("profile", ("MEDIUM", "", "lite-ish"))
def test_a_profile_outside_the_three_is_refused(profile, ticket, check):
    schema, good = ticket
    check.accepts(schema, good, "the ticket template")
    check.refuses(schema, support.replaced(good, "profile", profile), f"a ticket with profile {profile!r}")


def test_the_ticket_template_declares_one_of_the_three_profiles():
    path, good = support.template("ticket")
    assert good.get("profile") in PROFILES, f"{path.name}: profile is {good.get('profile')!r}, not one of {PROFILES}"
