"""K2: ``gov update`` does not put back what Emergency 2 removed and takes the legacy lines out; the owner's lines stay;
the report and the record say what was removed; ``--check`` names the change and writes nothing (DEC-1217 (6))."""

from __future__ import annotations

import w2_208_support as support


def _succeeded(outcome, what):
    done = outcome["run"]
    assert done.returncode == 0, f"`gov update {support.B} --json` did not exit 0 ({what})\n{done.describe()}"
    return done.result()


def test_k2_update_from_0_1_3_leaves_the_two_deny_lines_and_the_owners_own_lines(updated_013):
    _succeeded(updated_013, "from A1, 0.1.3's kind")
    deny, allow = support.permission_lines(support.read_settings(updated_013["project"]))
    support.assert_exact_lines(deny, (*support.TWO, support.OWNER_DENY), "permissions.deny after the update")
    assert allow == [support.OWNER_ALLOW], f"permissions.allow after the update is {allow}, not [{support.OWNER_ALLOW!r}]"
    assert updated_013["porcelain"] == [], f"`git status --porcelain` is not empty: {updated_013['porcelain']}"


def test_k2_the_report_and_the_record_list_the_four_removed_lines(updated_013):
    result = _succeeded(updated_013, "from A1, 0.1.3's kind")
    for what, report in (("the update's report", result), ("the record", support.record_of(updated_013))):
        removed = support.removed_lines(report, what)
        assert sorted(removed) == sorted(support.REMOVED), (
            f"{what} lists {removed} as removed, not the four legacy lines {list(support.REMOVED)}")


def test_k2_update_from_0_1_0_without_a_permission_source_ends_the_same(updated_010):
    result = _succeeded(updated_010, "from A0, 0.1.0's kind, no permission source")
    deny, allow = support.permission_lines(support.read_settings(updated_010["project"]))
    support.assert_exact_lines(deny, support.TWO, "permissions.deny after the update from A0")
    assert allow == [], f"permissions.allow after the update from A0 holds lines the kit wrote: {allow}"
    for what, report in (("the update's report", result), ("the record", support.record_of(updated_010))):
        removed = support.removed_lines(report, what)
        assert sorted(removed) == sorted(support.REMOVED), (
            f"{what} lists {removed} as removed, not the four legacy lines {list(support.REMOVED)}")
    assert updated_010["porcelain"] == [], f"`git status --porcelain` is not empty: {updated_010['porcelain']}"


def test_k2_check_names_the_settings_change_and_writes_nothing(checked_013):
    done, text = checked_013["run"], checked_013["text"]
    assert done.returncode == 0, f"`gov update {support.B} --check --json` did not exit 0\n{done.describe()}"
    assert text is not None and text.returncode == 0, f"`gov update {support.B} --check` did not exit 0\n" + (
        text.describe() if text else "")
    changed = support.w217.tree_difference(checked_013["before"], checked_013["after"])
    assert not changed, f"`--check` changed files or HEAD: {changed[:20]}"
    removed = support.removed_lines(done.result(), "the dry run's report")
    assert sorted(removed) == sorted(support.REMOVED), (
        f"the dry run lists {removed} under settings, not the four legacy lines {list(support.REMOVED)}")
    missing = [line for line in support.REMOVED if line not in text.stdout]
    assert "settings" in text.stdout.lower() and not missing, (
        f"the dry run's printed plan does not name the settings change (missing: {missing})\n{text.describe()}")
