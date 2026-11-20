# W2-198 acceptance tests: `gov backup`, `gov memaudit scan`, `gov decisions basis`

Ticket DAEO-o5wi (W2-198), profile STANDARD. Written by the independent test designer (MR-3) from the ticket's five
success lines, two failure lines and its `## Interface` section, before any implementation, on the base `76309f7c6`.
Every case is of the acceptance kind. Public interfaces only: the `gov` command line (exit code, stdout, stderr, the
`--json` envelope `{ok, command, result, error?, session}`), `git` (`for-each-ref`, `bundle list-heads`, `clone`,
`cat-file`) and the files. No module of the three tools is imported.

## How they run

    TMPDIR=$(mktemp -d) python3 -m pytest tests/acceptance/W2-198 -q -n 4

or `gov accept W2-198`. 33 cases, about 20 s at `-n 4`; no network, no model. Every `gov` runs as
`python3 -m gov.cli.main` (the runner's `PYTHONPATH`, else this worktree's `src/`) with a fixture `HOME` under the
test's `tmp_path` (its own `.gitconfig`; every `GIT_*` and `GOV_*` variable of the caller removed; `TZ=UTC`). Never the
real `~/.gov-os`, `~/.claude/projects` or eval root: `--projects`, `--set` and `--dest` always name fixtures.

## What is planted

- **The backup repository** (`w2_198_support.backup_world`): main worktree folder `proj` (branches `main`, `dev`; an
  annotated tag `v1` and a light tag; a stash), a linked worktree `proj-feature` on branch `feature` with a commit of
  its own, a detached worktree `proj-detached` with a commit reachable from no ref. A plain one-commit `proj` for S2/F1.
- **S2's dest**: name-form files (`proj-<YYYYMMDDTHHMMSSZ>.bundle`, small dummy bytes) hourly for the 72 hours before
  `GOV_BACKUP_NOW` = 2026-11-18T12:30:00Z and three a day (03:00, 11:00, 19:00) for the 40 days before those; their
  mtimes reversed against their names (the oldest name the newest mtime); plus `README.txt`, `otherproj-...bundle` and
  `proj-20261001T000000Z.bundle.tmp`. The expected kept set is computed from the rule in the test.
- **F1's git**: a `git` first on `PATH` that execs the real git (found with `shutil.which` first) except for any call
  holding `bundle verify`, which exits 1.
- **The scan's set**: `<HOME>/eval/fixtures/evaluation/memory-audit-20261101/hidden/q01.yaml` to `q03.yaml`, passed by
  its real path; transcripts in Claude Code's JSONL form under `<HOME>/.claude/projects/<project>/`, with planted
  `timestamp`s and mtimes; a sub-agent transcript at `<project>/sess-main/subagents/agent-a1b2.jsonl` beside
  `agent-a1b2.meta.json` (`{"agentType": "independent-auditor"}`) whose lines carry the parent's `sessionId`.
- **The register**: fixture repositories whose `docs/DECISION_REGISTER.md` gains entries commit by commit; S5's commits
  dated (author and committer, noon UTC) 20, 10 and 2 days before the real now.

## The map

| KPI line | tests | expected red reason |
|---|---|---|
| S1 | `test_w2_198_s1_backup.py::test_s1_default_dest_holds_one_verified_bundle_of_every_ref`, `test_w2_198_s1_backup.py::test_s1_text_form_is_one_line_naming_file_refs_verified_and_counts`, `test_w2_198_s1_backup.py::test_s1_backup_root_dest_and_name_place_the_file`, `test_w2_198_s1_backup.py::test_s1_run_from_the_linked_worktree_bundles_the_same_refs` | `gov backup` does not exist: exit 2, "invalid choice: 'backup'", no bundle |
| S2 | `test_w2_198_s2_retention.py::test_s2_defaults_keep_the_newest_48_and_one_a_day_for_30_days`, `test_w2_198_s2_retention.py::test_s2_keep_5_days_3_applies_the_same_rule_at_those_numbers` | `gov backup` does not exist: exit 2, not 0 |
| S3 | `test_w2_198_s3_scan.py::test_s3_each_naming_line_in_the_window_is_one_finding_with_its_fields`, `test_w2_198_s3_scan.py::test_s3_text_form_says_the_measure_is_void_then_one_line_a_finding`, `test_w2_198_s3_scan.py::test_s3_names_outside_the_window_in_longer_tokens_or_allowed_give_none`, `test_w2_198_s3_scan.py::test_s3_id_option_replaces_the_sets_ids_and_until_defaults_to_now`, `test_w2_198_s3_scan.py::test_s3_question_ids_come_from_file_names_even_when_the_files_cannot_be_read` | `gov memaudit` does not exist: exit 2 ("invalid choice: 'memaudit'"), not 1 or 0 |
| S4 | `test_w2_198_s4_basis.py::test_s4_the_range_names_exactly_the_new_rule_entries_without_an_incident`, `test_w2_198_s4_basis.py::test_s4_text_form_is_one_line_an_entry_naming_each_failure_and_its_reason`, `test_w2_198_s4_basis.py::test_s4_a_range_of_passing_entries_exits_0_and_the_default_is_head`, `test_w2_198_s4_basis.py::test_s4_an_uncommitted_edit_to_the_register_changes_no_answer`, `test_w2_198_s4_basis.py::test_s4_register_option_reads_another_file` | `gov decisions` does not exist: exit 2 ("invalid choice: 'decisions'"), not 1 or 0 |
| S5 | `test_w2_198_s5_week.py::test_s5_week_lists_only_the_entries_of_the_last_7_days_with_their_fields`, `test_w2_198_s5_week.py::test_s5_week_text_form_lists_the_same_and_exits_0_with_a_failing_entry`, `test_w2_198_s5_week.py::test_s5_since_a_date_before_both_lists_all_the_entries_since` | `gov decisions` does not exist: exit 2, not 0 |
| F1 | `test_w2_198_f1_backup_failures.py::test_f1_a_bundle_failing_verify_exits_1_and_the_dest_is_unchanged`, `test_w2_198_f1_backup_failures.py::test_f1_a_repository_with_no_commit_exits_1_and_deletes_nothing`, `test_w2_198_f1_backup_failures.py::test_f1_a_dest_inside_the_repository_or_a_worktree_exits_1_and_writes_nothing` | `gov backup` does not exist: exit 2, not 1 with `BACKUP_VERIFY_FAILED`, `BACKUP_FAILED` or `BACKUP_DEST_INSIDE` |
| F2 | `test_w2_198_f2_scan_safety.py::test_f2_no_output_holds_a_line_of_a_set_file_but_its_id`, `test_w2_198_f2_scan_safety.py::test_f2_an_unreadable_transcript_and_no_finding_exits_3_naming_it`, `test_w2_198_f2_scan_safety.py::test_f2_an_unreadable_transcript_beside_a_finding_is_named_in_problems` | `gov memaudit` does not exist: exit 2, not 0, 1 or 3 (the no-leak cases first require the scan's own exit, so argparse's error, which holds no question text, is not a pass) |

Count per line: S1 4 functions (6 cases), S2 2, S3 5, S4 5, S5 3, F1 3 (5 cases), F2 3 (7 cases). Three cases (S3's
names-only case and F2's two unreadable-file cases) are skipped when run as root (root reads a mode 000 file).

Red run on the base (`-n 4`): `33 failed in 20.14s`, every case at its first `gov` call with exit 2 and argparse's
"invalid choice" for `backup`, `memaudit` or `decisions`; no fixture or collection error. `gov accept DAEO-o5wi --root .`:
outcome fail, 33 failed, 0 unmapped, every line 0 passed.

## Rewritten for the fix under W2-204 (EXAMIN's F-033, 2026-11-20)

W2-204's S13 (M1) makes a bare question id no evidence: an id is a finding only on a line that also names the set by its
audit name or its tag; S14 (M2) makes a question's text read a finding of kind `text` and has the scan read the set's
`question` fields. The S3 and F2 cases that planted a bare id as the evidence now plant the tag (`20261101`) or the
audit name beside it (each finding's line, kind and match unchanged); F2's no-finding case drops `--id zz9` and plants a
bare id and the gold answer without the question's text; S3's names-only case, renamed `..._even_when_the_files_cannot_be_read`,
keeps its claim that the ids come from the file names (the files are now read for their question text, M2). Every other
assertion stands. The new rule's own cases are in `tests/acceptance/W2-204/` (S13 to S16).

## The test designer's readings where the ticket is open

- **`--json` and the options** are given after the command's own arguments (`gov memaudit scan ... --json`,
  `gov decisions basis --range A..B --json`), as `gov msg` accepts them. `gov decisions basis` runs with the fixture
  repository as its working directory (the default `--root`); `gov backup` is given `--root`.
- **S1, "the number of refs"**: the text line holds a whole number between the count of `git for-each-ref` and the
  count of `git bundle list-heads` lines (either reading of "refs"); the JSON `refs` is at least the former. "Naming
  the file": the line holds the file's name. With an empty dest the counts kept and removed are 1 and 0. The JSON
  `kept` may be a count or a list. The bundle's heads must hold every `(sha, ref)` pair of `for-each-ref`, and the
  detached worktree's commit by its sha under whatever name; run from the linked worktree, the heads other than `HEAD`
  are the same as from the main worktree. Without `GOV_BACKUP_NOW`, the name's time is the run's UTC time (within 2 s).
- **S2, "the last `--days` days"**: today's UTC date and the `days - 1` dates before it. The day `days` back (where
  this reading and "30 days back from now, inclusive" differ) is left empty in the planted dest, so either reading
  passes. `removed` is compared by file names (a path's base name). F1's planted older bundles would be deleted by a
  retention pass at `--keep 1 --days 1`, so a retention run before the verify shows.
- **S3, one finding a line**: a line naming the absolute path also holds the `fixtures/evaluation/` segment; the ticket
  says each such line gives one finding, so exactly one finding is expected for it, with the most specific form it
  names (the absolute path, `~/`, `$HOME/`, else the segment) as its `match`. The forms are the strings themselves
  (`~/eval/...`, `$HOME/eval/...`, `fixtures/evaluation/memory-audit-20261101`). `file` is compared as a real path
  (a relative one is read against `--projects`). A line naming `q02` after an escaped newline (`"...:\nq02 ..."`) must
  be found (decoded values), and a line that is not JSON (a cut-off last line) is read as text with the file's stem as
  its session. A transcript older than `--since` holds a summary line with no timestamp. "Listed as allowed": the
  result's `allowed` mentions the session id. The text form: its first line (stdout's; or stderr's void line when
  stdout holds only the findings) holds `void`, then one line a finding.
- **F2**: the no-leak check covers the question's and the gold answer's text and every line of the set file but its
  `id:` line, in stdout and stderr, in text and JSON, with and without findings (`--id zz9`). `SCAN_INCOMPLETE` is
  looked for anywhere in the envelope or the text output; `problems` must name the file's name.
- **S4/S5 verdicts**: a verdict is read as failing when it begins with `fail` (any case) and passing when it begins
  with `pass`; a reason must contain the ticket's words (`no basis line`, `basis names no incident`). The text form is
  stdout (stderr when stdout is empty): each new entry's id on exactly one line, the failing lines with their reason;
  `BASIS_MISSING` anywhere in stdout or stderr. S5's "date of the commit that added it" is any string value of the
  entry holding that commit's `YYYY-MM-DD` (UTC); the basis is compared whitespace-folded, continuation line included.
