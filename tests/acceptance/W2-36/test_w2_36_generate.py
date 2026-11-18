"""S4 (readiness gaps become linked gap tickets, with their dependencies, once) and S5 (research is scheduled with an
evidence record, and the judgement goes to a brief; no API key, no network)."""

from __future__ import annotations

import re

import yaml

import w2_36_support as support


def by_row(project, ticket_ids):
    """{row key: (ticket id, front matter)} of gap tickets, by their ``readiness_row``."""
    found = {}
    for ticket_id in ticket_ids:
        front = support.ticket(project, ticket_id)
        row = front.get("readiness_row") if isinstance(front.get("readiness_row"), dict) else {}
        assert row.get("key") not in found, f"two tickets for row {row.get('key')}"
        found[row.get("key")] = (ticket_id, front)
    return found


def generated_ok(outcome):
    assert outcome.run.returncode == 0, f"gov discover --generate did not exit 0:\n{outcome.run.describe()}"
    return by_row(outcome.project, outcome.new_tickets)


def rows(text):
    record = yaml.safe_load(text)
    return {row["key"]: row for row in record["rows"]}, {k: v for k, v in record.items() if k != "rows"}


# --- S4 -------------------------------------------------------------------------------------------------------------

def test_generate_creates_one_ticket_per_open_row_naming_its_row_with_its_class_and_role(generated):
    found = generated_ok(generated)
    assert len(generated.new_tickets) == 3, generated.new_tickets
    assert set(found) == set(support.GAPS_OPEN), sorted(map(str, found))
    for key, (ticket_id, front) in found.items():
        assert front["readiness_row"] == {"specification": support.GAPS_SPEC_ID, "n": support.NUMBER[key],
                                          "key": key}, (ticket_id, front["readiness_row"])
        assert (front.get("class"), front.get("role")) == support.gap_class(key), (ticket_id, key)


def test_generate_writes_each_rows_gap_ticket_in_place_and_changes_nothing_else(generated):
    found = generated_ok(generated)
    before, before_rest = rows(generated.extra["record_before"])
    after, after_rest = rows(generated.extra["record_after"])
    assert after_rest == before_rest
    assert list(after) == list(before)
    for key, row in before.items():
        expected = dict(row, gap_ticket=found[key][0]) if key in support.GAPS_OPEN else row
        assert after[key] == expected, (key, after[key])


def test_gap_tickets_depend_on_each_other_in_the_order_of_spec_work(generated):
    found = generated_ok(generated)
    scenarios, inputs = found["scenarios"][0], found["inputs"][0]
    inputs_deps = found["inputs"][1].get("depends_on") or []
    tests_deps = found["acceptance_tests"][1].get("depends_on") or []
    assert scenarios in inputs_deps, inputs_deps
    assert {scenarios, inputs} <= set(tests_deps), tests_deps


def test_readiness_lists_no_open_row_as_unlinked_after_generate(generated):
    found = generated_ok(generated)
    readiness = generated.extra["readiness"]
    envelope = readiness.envelope()
    assert envelope is not None, readiness.describe()
    report = envelope.get("result") if envelope.get("ok") else (envelope.get("error") or {}).get("details")
    open_rows = (report or {}).get("open")
    assert isinstance(open_rows, list), readiness.describe()
    assert {row["key"]: row["gap_ticket"] for row in open_rows} == {key: found[key][0] for key in support.GAPS_OPEN}


def test_a_second_generate_exits_0_creates_no_ticket_and_changes_no_byte(generated):
    generated_ok(generated)
    second = generated.extra["second"]
    assert second.returncode == 0, second.describe()
    first, again = generated.extra["snapshot_first"], generated.extra["snapshot_second"]
    assert sorted(again) == sorted(first), sorted(set(again) ^ set(first))
    assert [path for path in first if first[path] != again[path]] == []


def test_a_row_already_linked_to_an_existing_ticket_gets_no_ticket(own_p, home):
    support.plant_gaps(own_p, linked=support.REPORT_TICKET)
    before = support.tickets(own_p)
    run = support.discover(own_p, "--generate", support.GAPS_CHANGE, "--json", home=home)
    assert run.returncode == 0, run.describe()
    new = sorted(set(support.tickets(own_p)) - set(before))
    assert set(by_row(own_p, new)) == {"inputs", "acceptance_tests"}, new
    after, _ = rows((own_p / support.GAPS_CHANGE_REL / "readiness.yaml").read_text(encoding="utf-8"))
    assert after["scenarios"]["gap_ticket"] == support.REPORT_TICKET


# --- S5 -------------------------------------------------------------------------------------------------------------

def researched_ok(outcome):
    assert outcome.run.returncode == 0, f"gov discover (no key, no network) did not exit 0:\n{outcome.run.describe()}"
    generate = outcome.extra["generate"]
    assert generate.returncode == 0, f"gov discover --generate (no key, no network) did not exit 0:\n{generate.describe()}"
    return by_row(outcome.project, outcome.extra["generate_new"])


def test_research_rows_get_research_tickets_whose_kpi_names_the_evidence_record(researched):
    found = researched_ok(researched)
    folder = f"docs/research/{support.CHANGE}"
    for key in support.STANDARD_EXTRA:
        assert key in found, f"no gap ticket for {key}: {sorted(map(str, found))}"
        ticket_id, front = found[key]
        assert (front.get("class"), front.get("role")) == ("research", "research"), ticket_id
        assert f"{folder}/**" in (front.get("allowed_paths") or []), front.get("allowed_paths")
        record = f"{folder}/{key}.md"
        named = [support.plain(f"{line} {verify}") for line, verify in support.kpi_items(front, "success")
                 if record in support.plain(verify)]
        assert named, f"no success KPI line whose verify names {record}: {front.get('kpis')}"
        assert any(all(re.search(word, text, re.I) for word in (r"tested", r"\bhow\b", r"measured", r"verdict"))
                   for text in named), f"the evidence record's four parts are not named: {named}"


def test_gov_brief_research_accepts_each_research_ticket(researched, home):
    found = researched_ok(researched)
    for key in support.STANDARD_EXTRA:
        brief = support.gov(researched.project, "brief", "research", found[key][0], home=home, no_network=True)
        assert brief.returncode == 0, brief.describe()


def test_gov_brief_product_spec_on_the_discovery_ticket_holds_the_idea_and_the_spec_path(researched, home):
    researched_ok(researched)
    assert len(researched.new_tickets) == 1, researched.new_tickets
    brief = support.gov(researched.project, "brief", "product-spec", researched.new_tickets[0], home=home,
                        no_network=True)
    assert brief.returncode == 0, brief.describe()
    assert support.WORDS in brief.stdout, brief.describe()
    assert support.SPEC_REL in brief.stdout, brief.describe()


def test_discover_and_generate_name_the_brief_command_of_each_ticket_they_created(researched):
    found = researched_ok(researched)
    assert len(researched.new_tickets) == 1, researched.new_tickets
    command = f"gov brief product-spec {researched.new_tickets[0]}"
    assert command in researched.run.output, researched.run.describe()
    generate = researched.extra["generate"]
    assert len(found) == len(set(support.MANDATORY) | set(support.STANDARD_EXTRA)), sorted(map(str, found))
    for key, (ticket_id, front) in found.items():
        command = f"gov brief {front.get('role')} {ticket_id}"
        assert command in generate.output, f"{command!r} is not named:\n{generate.describe()}"
