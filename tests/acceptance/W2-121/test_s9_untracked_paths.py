"""S9, review round 1 finding F-4: a path that only exists untracked is unresolved.

Reading fixed by the fix round: a relative path a return names on ``files_changed:`` resolves only when git knows it in
the ticket's worktree: it is in HEAD's tree or in the history (``git log -- <path>`` names a commit), or it exists and
git ignores it (``git check-ignore``). A path that exists only as an untracked, not-ignored file (or only staged, in no
commit) is named on the item's ``unresolved:`` line. The planted returns leave out the return's own ``unresolved:``
field, so the only such line an item holds is the dispatcher's.
"""

from __future__ import annotations

import w2_121_support as support
from test_s9_resolved_returns import return_text, unresolved_lines

UNTRACKED = "src/only_untracked.py"
IGNORED = "build_out/generated.txt"


def run_to_item(p, entry, text, before_item=None):
    p.set_output(text)
    p.ready(entry)
    assert p.tick().code == 0
    p.wait_launches(1)
    p.wait_exit_file(entry.log)
    if before_item:
        before_item()
    assert p.tick().code == 0
    (item,) = p.items()
    return item


def test_s9_a_file_that_exists_only_untracked_is_named_unresolved(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    (p.wt(entry) / "src").mkdir(exist_ok=True)
    (p.wt(entry) / UNTRACKED).write_text("never committed\n", encoding="utf-8")
    assert support.git(p.wt(entry), "status", "--porcelain", "--untracked-files=no") == ""  # still a clean worktree
    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", f"src/real_file.py, {UNTRACKED}"))
    lines = unresolved_lines(item)
    assert len(lines) == 1, f"the untracked file is not named unresolved:\n{item.text}"
    assert UNTRACKED in lines[0], item.text
    assert "src/real_file.py" not in lines[0] and full[:12] not in lines[0], f"a committed path or commit is named:\n{item.text}"


def test_s9_a_committed_path_beside_an_untracked_one_is_not_named(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    (p.wt(entry) / UNTRACKED).parent.mkdir(parents=True, exist_ok=True)
    (p.wt(entry) / UNTRACKED).write_text("never committed\n", encoding="utf-8")
    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", "src/real_file.py"))
    assert unresolved_lines(item) == [], f"a committed path was named unresolved:\n{item.text}"


def test_s9_a_path_that_exists_and_is_ignored_by_the_worktrees_gitignore_is_not_named(project):
    p = project
    entry = p.add_ticket(901)
    p.commit(entry, ".gitignore", "build_out/\n")
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    (p.wt(entry) / IGNORED).parent.mkdir(parents=True, exist_ok=True)
    (p.wt(entry) / IGNORED).write_text("generated\n", encoding="utf-8")
    assert support.git(p.wt(entry), "check-ignore", IGNORED) == IGNORED  # the premise: git ignores it
    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", f"src/real_file.py, {IGNORED}"))
    assert unresolved_lines(item) == [], f"an ignored path that exists was named unresolved:\n{item.text}"


def test_s9_an_ignored_path_beside_an_untracked_one_names_only_the_untracked(project):
    p = project
    entry = p.add_ticket(901)
    p.commit(entry, ".gitignore", "build_out/\n")
    full = p.commit(entry, "src/real_file.py", "x = 1\n")
    for rel in (IGNORED, UNTRACKED):
        (p.wt(entry) / rel).parent.mkdir(parents=True, exist_ok=True)
        (p.wt(entry) / rel).write_text("planted\n", encoding="utf-8")
    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", f"{IGNORED}, src/real_file.py, {UNTRACKED}"))
    (line,) = unresolved_lines(item)
    assert UNTRACKED in line and IGNORED not in line and "src/real_file.py" not in line, item.text


def test_s9_a_path_that_was_committed_and_later_removed_still_resolves_by_the_history(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/gone_later.py", "x = 1\n")
    support.git(p.wt(entry), "rm", "-q", "--", "src/gone_later.py")
    support.git(p.wt(entry), "commit", "-q", "-m", "planted removal")
    assert not (p.wt(entry) / "src" / "gone_later.py").exists()
    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", "src/gone_later.py"))
    assert unresolved_lines(item) == [], f"a path in the history was named unresolved:\n{item.text}"


def test_s9_a_path_that_is_only_staged_in_no_commit_is_named_unresolved(project):
    p = project
    entry = p.add_ticket(901)
    full = p.commit(entry, "src/real_file.py", "x = 1\n")

    def stage():  # staged after the session started: staging a file before would make the worktree unclean
        (p.wt(entry) / UNTRACKED).parent.mkdir(parents=True, exist_ok=True)
        (p.wt(entry) / UNTRACKED).write_text("staged only\n", encoding="utf-8")
        support.git(p.wt(entry), "add", "--", UNTRACKED)

    item = run_to_item(p, entry, return_text(f"{full[:12]} planted", f"src/real_file.py, {UNTRACKED}"), stage)
    (line,) = unresolved_lines(item)
    assert UNTRACKED in line and "src/real_file.py" not in line, item.text
