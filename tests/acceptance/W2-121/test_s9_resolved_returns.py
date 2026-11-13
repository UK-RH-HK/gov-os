"""S9: every commit id and path a return names is resolved against git; one that does not resolve is named in the inbox
item.

Readings fixed by the brief (the lead's reading): the return is what the session printed to its log; the commit ids
(7 to 40 hex) and paths it names on its ``commits:`` and ``files_changed:`` lines (the values on the same line,
separated by commas or blanks) are each resolved in the ticket's worktree (the commit as a commit, the path as a path
of the worktree's tree); any that does not resolve is named on one ``unresolved:`` line of the item; none: no such line.
Only those two lines are read: an id or a path elsewhere in the return is not looked up. The planted returns leave out
the return's own ``unresolved:`` field (the twelve-field return has one), so that the only ``unresolved:`` line an item
can hold is the dispatcher's.
"""

from __future__ import annotations

import re

import w2_121_support as support

GHOST_COMMIT = "deadbee1234f"
GHOST_PATH = "src/not_there.py"


def return_text(commits: str, files: str, *more: str) -> str:
    lines = ["task: planted", "status: DONE", "work_completed: planted", f"files_changed: {files}", "evidence: ok",
             "tests: none", "discoveries: none", "risks: none", "lessons: none", "proposed_decisions: none",
             "recommended_next_action: none", f"commits: {commits}", *more]
    return "\n".join(lines) + "\n"


def item_for(p, entry, text):
    p.set_output(text)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.wait_exit_file(entry.log)
    assert p.tick().code == 0
    (item,) = p.items()
    return item


def unresolved_lines(item):
    return [l for l in item.lines if l.startswith("unresolved:")]


def test_s9_a_return_naming_a_commit_and_a_path_that_exist_names_nothing_unresolved(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    item = item_for(p, entry, return_text(f"{full[:12]} planted commit", "src/real_file.py"))
    assert item.fields["status"] == "DONE", item.text
    assert unresolved_lines(item) == [], f"a real commit and path were named unresolved:\n{item.text}"


def test_s9_a_commit_and_a_path_that_do_not_resolve_are_named_and_the_existing_ones_are_not(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    item = item_for(p, entry, return_text(f"{full[:12]} planted commit, {GHOST_COMMIT} ghost commit",
                                          f"src/real_file.py, {GHOST_PATH}"))
    lines = unresolved_lines(item)
    assert len(lines) == 1, f"expected one unresolved: line\n{item.text}"
    line = lines[0]
    assert GHOST_COMMIT in line and GHOST_PATH in line, f"the ones that do not resolve are not named:\n{item.text}"
    assert full[:12] not in line and "src/real_file.py" not in line, f"a real one is named unresolved:\n{item.text}"


def test_s9_short_and_full_commit_ids_both_resolve(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    item = item_for(p, entry, return_text(f"{full[:7]} short, {full} full", "src/real_file.py"))
    assert unresolved_lines(item) == [], item.text


def test_s9_only_the_commits_and_files_changed_lines_are_resolved(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    item = item_for(p, entry, return_text(
        f"{full[:12]} planted", "src/real_file.py",
        "evidence: ran against deadbee9999 and checked", "lessons: read src/also_missing.py before changing it"))
    assert unresolved_lines(item) == [], f"an id or path outside the two lines was looked up:\n{item.text}"


def test_s9_the_item_is_the_same_item_with_its_first_lines(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    item = item_for(p, entry, return_text(f"{GHOST_COMMIT} ghost", "src/real_file.py"))
    assert [l.split(":")[0] for l in item.lines[:3]] == ["log", "W2", "status"], item.text
    assert item.fields["W2"] == entry.w2 and re.search(GHOST_COMMIT, item.text)
