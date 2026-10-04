"""The project floor in the path map.

Success 5: the overlay schema carries the project floor (enabled capabilities and policy strengths); it identifies
each constitutional system at least minimally, and no overlay value may go below the kernel floor
[CAP-06.e, CAP-54.b].

The floor lives in `governance/project/path-map.yaml`, under three top-level keys of the path-map schema:
`capabilities`, `policies` and `systems` (DEC-224, DEC-230). A policy's value is one strength of `informational`,
`warning`, `hard-block`; the schema gives each policy only the strengths at or above its kernel minimum, so the
validator alone refuses a value below the floor (DEC-230, DEC-238). Each of the twenty-two constitutional systems
has a `status`, a `where` unless it is absent, and a `reason` when it is absent (DEC-230). `capabilities` is closed
to `code_intelligence` and `research_corpus` (DEC-238).

The good document is the committed path map; each bad one is that document with one change.
"""

from __future__ import annotations

import pytest

import w1_08_support as support

FLOOR_KEYS = ("capabilities", "policies", "systems")
STRENGTHS = ("informational", "warning", "hard-block")  # weakest to strongest
KERNEL_MINIMUM = {
    "security": "hard-block",
    "authority": "hard-block",
    "test": "hard-block",
    "change": "hard-block",
    "human_gate": "hard-block",
    "tool": "hard-block",
    "memory": "warning",
    "context": "warning",
    "checkpoint": "warning",
    "model_routing": "informational",
    "budget": "informational",
    "learning": "informational",
    "archive": "informational",
}
ABOVE_THE_WEAKEST = sorted(name for name, minimum in KERNEL_MINIMUM.items() if minimum != STRENGTHS[0])
CAPABILITIES = ("code_intelligence", "research_corpus")
SYSTEMS = (
    "constitution-and-policies", "knowledge-fabric", "repository-contract", "agent-organisation", "skills",
    "tools-and-capabilities", "command-surface", "model-adapters", "orchestration-and-handoffs",
    "specification-and-planning", "research-and-experiments", "task-system", "product-delivery",
    "verification-and-governance-tests", "change-impact-control", "checkpoint-and-recovery",
    "observability-and-cost", "organisational-learning", "independent-audit", "security-and-permissions",
    "budget-governance", "emergency-stop-and-rollback",
)
STATUSES = ("implemented", "minimal", "absent")


@pytest.fixture
def path_map():
    schema = support.schema_path("path-map")
    document = support.load_path_map()
    return schema, document


def _block(document, key):
    value = document.get(key)
    assert isinstance(value, dict), f"{support.PATH_MAP_REL}: `{key}` is {type(value).__name__}, not a map"
    return value


def _with_policies(document, changes):
    return support.replaced(document, "policies", {**_block(document, "policies"), **changes})


def _empty(value):
    return not value and value != 0 and value is not False


# --- the floor is in the path map [CAP-06.e] --------------------------------------------------------------------

@pytest.mark.local_only
@pytest.mark.parametrize("key", FLOOR_KEYS)
def test_a_path_map_without_the_floor_key_is_refused(key, path_map, check):
    schema, document = path_map
    assert key in document, f"{support.PATH_MAP_REL} has no `{key}`"
    check.good(schema, document, support.PATH_MAP_REL)
    check.refuses(schema, support.without(document, key), f"a path map without `{key}`")


# --- policy strengths and the kernel floor [CAP-06.e] -----------------------------------------------------------

def test_the_path_map_gives_each_of_the_thirteen_policies_a_strength_at_or_above_the_kernel_minimum():
    policies = _block(support.load_path_map(), "policies")
    missing = [name for name in KERNEL_MINIMUM if name not in policies]
    assert not missing, f"{support.PATH_MAP_REL}: `policies` has no {missing}"
    wrong = {name: policies[name] for name in KERNEL_MINIMUM if policies[name] not in STRENGTHS}
    assert not wrong, f"{support.PATH_MAP_REL}: not one of {STRENGTHS}: {wrong}"
    below = {name: policies[name] for name, minimum in KERNEL_MINIMUM.items()
             if STRENGTHS.index(policies[name]) < STRENGTHS.index(minimum)}
    assert not below, f"{support.PATH_MAP_REL}: below the kernel minimum: {below}"


@pytest.mark.local_only
def test_a_path_map_without_one_of_the_thirteen_policies_is_refused(path_map, check):
    schema, document = path_map
    policies = _block(document, "policies")
    check.good(schema, document, support.PATH_MAP_REL)
    for name in KERNEL_MINIMUM:
        assert name in policies, f"{support.PATH_MAP_REL}: `policies` has no `{name}`"
        check.refuses(schema, support.replaced(document, "policies", support.without(policies, name)),
                      f"a path map without the policy `{name}`")


@pytest.mark.local_only
def test_every_strength_at_or_above_the_kernel_minimum_is_accepted(path_map, check):
    schema, document = path_map
    check.accepts(schema, _with_policies(document, dict(KERNEL_MINIMUM)),
                  "a path map with every policy at its kernel minimum")
    check.accepts(schema, _with_policies(document, {name: STRENGTHS[-1] for name in KERNEL_MINIMUM}),
                  "a path map with every policy at hard-block")
    raised = {name: STRENGTHS[STRENGTHS.index(minimum) + 1]
              for name, minimum in KERNEL_MINIMUM.items() if minimum != STRENGTHS[-1]}
    check.accepts(schema, _with_policies(document, raised),
                  "a path map with every policy one step above its kernel minimum")


@pytest.mark.local_only
@pytest.mark.parametrize("name", ABOVE_THE_WEAKEST)
def test_a_strength_below_the_kernel_minimum_is_refused(name, path_map, check):
    schema, document = path_map
    check.good(schema, document, support.PATH_MAP_REL)
    for strength in STRENGTHS[:STRENGTHS.index(KERNEL_MINIMUM[name])]:
        check.refuses(schema, _with_policies(document, {name: strength}),
                      f"a path map whose policy `{name}` is {strength}, below its kernel minimum "
                      f"{KERNEL_MINIMUM[name]}")


@pytest.mark.local_only
@pytest.mark.parametrize("name", ("security", "archive"))
def test_a_policy_value_that_is_not_a_strength_is_refused(name, path_map, check):
    """Also for a policy whose kernel minimum is the weakest strength: `off` is below every floor."""
    schema, document = path_map
    check.good(schema, document, support.PATH_MAP_REL)
    for value in ("off", None):
        check.refuses(schema, _with_policies(document, {name: value}),
                      f"a path map whose policy `{name}` is {value!r}")


# --- capabilities [CAP-06.e] ------------------------------------------------------------------------------------

def test_the_path_map_names_no_capability_outside_the_two():
    capabilities = _block(support.load_path_map(), "capabilities")
    unknown = [name for name in capabilities if name not in CAPABILITIES]
    assert not unknown, f"{support.PATH_MAP_REL}: `capabilities` names {unknown}, outside {CAPABILITIES}"


@pytest.mark.local_only
def test_a_capability_outside_the_two_is_refused(path_map, check):
    """The list is closed. The unknown capability carries the value of a known one, so only its name is wrong."""
    schema, document = path_map
    capabilities = _block(document, "capabilities")
    value = next(iter(capabilities.values()), True)
    check.good(schema, document, support.PATH_MAP_REL)
    check.refuses(schema, support.replaced(document, "capabilities", {**capabilities, "w1_08_unknown": value}),
                  "a path map with the capability `w1_08_unknown`")


# --- the constitutional systems [CAP-54.b] ----------------------------------------------------------------------

def _identified_system(document):
    """``(name, entry)`` of the first system of the committed path map that is not absent."""
    systems = _block(document, "systems")
    for name in SYSTEMS:
        entry = systems.get(name)
        if isinstance(entry, dict) and entry.get("status") in STATUSES[:2] and not _empty(entry.get("where")):
            return name, entry
    raise AssertionError(f"{support.PATH_MAP_REL}: no system is `implemented` or `minimal` with a `where`")


def _with_system(document, name, entry):
    return support.set_at(document, ("systems", name), entry)


def test_the_path_map_identifies_each_of_the_twenty_two_constitutional_systems():
    systems = _block(support.load_path_map(), "systems")
    problems = []
    for name in SYSTEMS:
        entry = systems.get(name)
        if not isinstance(entry, dict):
            problems.append(f"{name}: not identified")
        elif entry.get("status") not in STATUSES:
            problems.append(f"{name}: `status` is {entry.get('status')!r}, not one of {STATUSES}")
        elif entry["status"] == "absent" and _empty(entry.get("reason")):
            problems.append(f"{name}: absent, with no `reason`")
        elif entry["status"] != "absent" and _empty(entry.get("where")):
            problems.append(f"{name}: {entry['status']}, with no `where`")
    assert not problems, f"{support.PATH_MAP_REL}: `systems`: " + "; ".join(problems)


@pytest.mark.local_only
def test_a_path_map_without_one_of_the_twenty_two_systems_is_refused(path_map, check):
    schema, document = path_map
    systems = _block(document, "systems")
    check.good(schema, document, support.PATH_MAP_REL)
    for name in SYSTEMS:
        assert name in systems, f"{support.PATH_MAP_REL}: `systems` has no `{name}`"
        check.refuses(schema, support.replaced(document, "systems", support.without(systems, name)),
                      f"a path map without the system `{name}`")


@pytest.mark.local_only
def test_a_system_is_implemented_or_minimal_with_a_where(path_map, check):
    schema, document = path_map
    name, entry = _identified_system(document)
    for status in STATUSES[:2]:
        check.accepts(schema, _with_system(document, name, {**entry, "status": status}),
                      f"a path map whose system `{name}` is {status}, with its `where`")
        check.refuses(schema, _with_system(document, name, support.without({**entry, "status": status}, "where")),
                      f"a path map whose system `{name}` is {status}, with no `where`")
    check.refuses(schema, _with_system(document, name, {**entry, "where": type(entry["where"])()}),
                  f"a path map whose system `{name}` has an empty `where`")


@pytest.mark.local_only
def test_an_absent_system_gives_its_reason(path_map, check):
    schema, document = path_map
    name, entry = _identified_system(document)
    absent = {**support.without(entry, "where"), "status": "absent"}
    check.accepts(schema, _with_system(document, name, {**absent, "reason": "Not built in this wave."}),
                  f"a path map whose system `{name}` is absent, with a `reason`")
    check.refuses(schema, _with_system(document, name, support.without(absent, "reason")),
                  f"a path map whose system `{name}` is absent, with no `reason`")


@pytest.mark.local_only
@pytest.mark.parametrize("status", ("planned", None))
def test_a_system_without_one_of_the_three_statuses_is_refused(status, path_map, check):
    schema, document = path_map
    name, entry = _identified_system(document)
    check.good(schema, document, support.PATH_MAP_REL)
    bad = support.without(entry, "status") if status is None else {**entry, "status": status}
    check.refuses(schema, _with_system(document, name, bad), f"a path map whose system `{name}` has status {status!r}")
