You are the engineer for ticket `DAEO-fygv` (`W1-26`), in the worktree `/home/usain/gov-os-worktrees/W1-26b` on branch `w1/W1-26b`. A short repair turn. You change only `src/gov/check/audit_validator.py` and, if you need them, files under `tests/unit/check/`. You never write or edit anything under `tests/acceptance/`. You read nothing under `~/gov-os-workbench/`, nothing under `qualification-oracle/`, and you never copy or clone this tree. Nothing is installed.

The test designer added ten cases in `tests/acceptance/W1-26/test_w1_26_audit_validator.py` (commit `a86594e2`); they are red. They come from DEC-441 (`docs/DECISION_REGISTER.md`): read it, and read the ten cases and the README lines beside them. Make them pass without making any earlier case fail:

1. An evidence cell that is empty, or holds an empty entry among real ones, or ends in a comma, is a finding (not well-formed); "none" is written as `-`.
2. In a folder given as an argument, every Markdown file that has frontmatter is validated as a report; one whose frontmatter is broken or lacks a required field is a finding, never skipped. A file with no frontmatter at all is ignored.
3. `commit` is a hexadecimal commit id, abbreviated or full, that resolves to a commit; a name such as `HEAD` or a branch is a finding.
4. `pack_sha256` has the form the cases demand.

Nothing validated is unmeasured and never exits 0 (DEC-425): keep that.

Run `python3 -m pytest tests/acceptance/W1-26 tests/unit/check -q -p no:cacheprovider` to its end: everything passes. Commit once with the message `W1-26 audit-report validator: empty evidence, skipped reports, commit and pack hash form (DEC-441)` and the trailers `Task: DAEO-fygv`, `Role: engineer`, `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Return: the commit id, the counts, the lines changed, and anything in the module you saw that can still end green on a report that breaks DEC-441.
