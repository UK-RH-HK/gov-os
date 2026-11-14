"""S5: the commit trailers' residuals at the starting head, listed once; history not rewritten."""

from __future__ import annotations

import json
import subprocess
import sys

import pytest

import w2_130_support as s


def _residuals(record) -> dict:
    data = record.data("trailer-residuals")
    assert isinstance(data, dict) and isinstance(data.get("values"), list), "trailer-residuals: {head, values: [...]}"
    return data


def _key(item) -> tuple[str, str]:
    assert isinstance(item, dict) and item.get("trailer") in ("Task", "Implements"), f"bad residual {item!r}"
    return item["trailer"], str(item.get("value"))


def test_s5_the_starting_head_is_an_ancestor_of_head_so_no_history_was_rewritten():
    assert s.is_ancestor(s.START, "HEAD")


def test_s5_the_residuals_are_taken_at_the_starting_head(record):
    assert s.need_hash(_residuals(record).get("head"), "trailer-residuals.head") == s.full(s.START)


def test_s5_each_trailer_and_value_is_listed_once_and_task_decision_record_is_not_listed(record):
    keys = [_key(item) for item in _residuals(record)["values"]]
    assert keys, "trailer-residuals lists no value"
    assert len(set(keys)) == len(keys), "a (trailer, value) is listed twice"
    assert ("Task", "decision-record") not in keys, "Task: decision-record is valid under DEC-861"


def test_s5_each_value_has_its_commits_its_tickets_and_the_ids_it_should_have_named(record):
    bad = []
    for item in _residuals(record)["values"]:
        key = _key(item)
        commits, tickets = item.get("commits"), item.get("tickets")
        if not isinstance(commits, list) or not commits:
            bad.append((key, "no commits"))
        else:
            for commit in commits:
                s.need_hash(commit, f"{key} commit")
        if not isinstance(tickets, list) or not tickets:
            bad.append((key, "no tickets list"))
        named = item.get("should_have_named")
        if not (isinstance(named, list) and named) and not (isinstance(named, str) and named.strip()):
            bad.append((key, "should_have_named is empty"))
    assert not bad, f"{bad[:6]}"


def test_s5_every_listed_commit_carries_the_value_it_is_listed_under_at_the_starting_head(record):
    bad = []
    for item in _residuals(record)["values"]:
        trailer, value = _key(item)
        for commit in item.get("commits") or []:
            full = s.need_hash(commit, "commit")
            if not s.is_ancestor(full, s.START):
                bad.append((trailer, value, full[:12], "not in the history at the starting head"))
                continue
            block = s.git("log", "-1", f"--format=%(trailers:key={trailer},unfold)", full).strip()
            if value not in [line.partition(":")[2].strip() for line in block.splitlines()]:
                bad.append((trailer, value, full[:12], "the commit carries no such trailer value"))
    assert not bad, f"{bad[:6]}"


def test_s5_the_recount_command_at_the_starting_head_gives_exactly_the_listed_set(record):
    script = record.block("recount", "python")
    done = subprocess.run([sys.executable, "-", s.full(s.START)], input=script, cwd=s.ROOT, capture_output=True,
                          text=True, check=False, timeout=600)
    assert done.returncode == 0, f"the recount script failed: {done.stderr.strip()[-300:]}"
    try:
        counted = json.loads(done.stdout)
    except ValueError:
        pytest.fail(f"the recount script printed no JSON list: {done.stdout[:200]!r}")
    assert isinstance(counted, list)
    assert {_key(item) for item in counted} == {_key(item) for item in _residuals(record)["values"]}


def test_s5_my_own_count_of_values_naming_no_record_finds_none_missing_from_the_set(record):
    """Reading: ``Task:`` a value with no ``.tickets/<value>.md`` at the starting head (not ``decision-record``);
    ``Implements:`` a value some element of which (split on commas and white space) is no register entry, ticket,
    W2 id (``wbs_id`` or ``external-ref``) or capability/MR id of ``contract.yaml`` there. A residual covers my value
    when it is listed as written, or every unresolved element of mine is an element of a listed value."""
    listed = [_key(item) for item in _residuals(record)["values"]]
    exact = set(listed)
    elements = {(trailer, token) for trailer, value in listed for token in value.replace(",", " ").split()}
    missing = [(item["trailer"], item["value"]) for item in s.own_recount(s.START)
               if (item["trailer"], item["value"]) not in exact
               and not all((item["trailer"], token) in elements for token in item["tokens"])]
    assert not missing, f"{len(missing)} values naming no record are not in the set: {missing[:6]}"
