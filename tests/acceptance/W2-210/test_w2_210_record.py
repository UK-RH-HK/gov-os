"""V3: the record is of type ``adoption-verdict``, valid under the schema of W2-02, with ``lite: true``, the ten
ADOPTED_HEALTHY conditions with their markings, ``conditions_not_checked``, standing on the A10 record and naming the
commit it was computed at [CAP-44.h; DEC-722; W2-02].

The record the command line committed on the harbour (``cli_plain``) is read back, and the record ``compute`` gives
with the tools stood in (every condition met).
"""

from __future__ import annotations

import re

import pytest

import w2_210_support as d1

support = d1.support


def _healthy(adopted):
    """The project and the record ``compute`` gives it with the tools stood in (every condition met)."""
    return adopted.project, d1.compute(adopted.project, tools=d1.healthy_tools())


def test_the_record_is_of_type_adoption_verdict_and_valid_under_the_schema(cli_plain):
    """V3: the committed record has the shared frontmatter, ``type: adoption-verdict``, a verdict and conditions
    (name, source, state; ``owner_entry`` where accepted) valid under the kernel's W2-02 schema."""
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert front["type"] == "adoption-verdict"
    assert isinstance(front["id"], str) and support.RECORD_ID_RE.match(front["id"]), front["id"]
    assert d1.schema_errors(front) == []


def test_gov_rebuild_lists_the_record_among_none_invalid(cli_plain):
    """V3: ``gov rebuild`` reads the record: no record is invalid."""
    d1.taken(cli_plain)
    run = cli_plain.ad.gov("rebuild", "--json")
    envelope = run.envelope()
    assert envelope["ok"] is True, run.describe()
    assert envelope["result"]["store"]["invalid"] == [], envelope["result"]["store"]["invalid"]


def test_the_record_names_itself_lite(cli_plain):
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert front["lite"] is True


def test_the_record_gives_the_ten_adopted_healthy_conditions_with_their_markings(adopted):
    """V3: ten entries, numbered 1 to 10, each with its ``name``, its ``wave`` (``W2`` or ``W3``: only (3) is W2)
    and its ``lite_part``: the names of the lite conditions that check it (none for (2), (7), (8) and (10))."""
    _, result = _healthy(adopted)
    listed = result["adopted_healthy_conditions"]
    assert [item["number"] for item in listed] == list(range(1, 11)), listed
    for item in listed:
        assert isinstance(item["name"], str) and item["name"].strip(), item
        assert item["wave"] == d1.HEALTHY_TEN[item["number"]], f"({item['number']}) {item['name']}: {item['wave']}"
        assert isinstance(item["lite_part"], list) and set(item["lite_part"]) <= set(d1.CONDITIONS), item
    by_number = {item["number"]: item for item in listed}
    for number in d1.NO_LITE_PART:
        assert by_number[number]["lite_part"] == [], (number, by_number[number])
    for number, names in d1.LITE_PART_HAS.items():
        assert names <= set(by_number[number]["lite_part"]), (number, by_number[number]["lite_part"])


def test_the_command_lines_record_gives_the_same_ten(cli_plain, adopted):
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert front["adopted_healthy_conditions"] == _healthy(adopted)[1]["adopted_healthy_conditions"]


def test_conditions_not_checked_names_what_the_verdict_does_not_check(adopted):
    """V3: (2), (7), (8) and (10) (W3, no lite part), A9 and A11, the certification by qualification and a separate
    verifier role are named."""
    _, result = _healthy(adopted)
    listed = result["conditions_not_checked"]
    assert isinstance(listed, list) and listed
    said = " ".join(str(item) for item in listed)
    for number in d1.NO_LITE_PART:
        assert f"({number})" in said, f"conditions_not_checked does not name ({number}): {listed}"
    for word in ("A9", "A11", "qualification", "verifier"):
        assert word in said, f"conditions_not_checked does not name {word!r}: {listed}"


def test_the_record_stands_on_the_a10_record_and_names_the_commit_it_was_computed_at(adopted):
    """V3: ``stands_on`` is the sha256 of the A10 record as it now is; ``commit`` the commit computed at."""
    project, result = _healthy(adopted)
    assert result["stands_on"] == d1.sha256_at_head(project, d1.RECORD["A10"])
    assert result["commit"] == support.git(project, "rev-parse", "HEAD").strip()
    assert re.fullmatch(r"[0-9a-f]{40}", result["commit"])


def test_the_committed_record_stands_on_a10_and_the_commit_before_its_own(cli_plain):
    d1.taken(cli_plain)
    front, _ = d1.record_at_head(cli_plain.project)
    assert front["stands_on"] == d1.sha256_at_head(cli_plain.project, d1.RECORD["A10"])
    assert front["commit"] == d1.git_parent(cli_plain.project)


def test_the_committed_record_carries_produced_by_the_digest_of_its_body(cli_plain):
    """F1/V3: ``produced_by`` is the sha256 of the record's text without its ``produced_by`` line (README)."""
    d1.taken(cli_plain)
    front, text = d1.record_at_head(cli_plain.project)
    assert front["produced_by"] == d1.digest_of(text), front.get("produced_by")


def test_the_conditions_say_where_they_come_from(adopted):
    """V3 [W2-02]: each condition has a ``source``, the item of the Contract or the register it comes from."""
    _, result = _healthy(adopted)
    assert all(isinstance(item["source"], str) and "CAP-44" in item["source"] for item in result["conditions"]), \
        [item["source"] for item in result["conditions"]]
