# W2-130 acceptance tests: the link clean-up (DEC-1073 (5)(a)), re-baselined Verify lines

Ticket DAEO-q8cl (W2-130), profile STANDARD, class C2. Written by the independent test designer (MR-3) from the
ticket's eleven KPI lines (S1 to S8 are its eight success lines, F1 to F4 its four failure lines, in the ticket's
order), each ending `[Verify re-baselined to history, the CTO, P-W2-130-1 (a)]` (S4 also `[S4 re-baselined to
DEC-1123 (2), the CTO, P-W2-130-4 (a)]`), and the lead's interface text
(the layout of `docs/research/W2-130-link-cleanup.md`, its fenced blocks, the five follow-up commits). Branch base
`09542040f`. Nothing of the implementer's tree or branch after `09542040f` was read.

## What they are

Repository-state cases (`record_reading`: they read the repository's own records, not a planted one) on the tree the
tests sit in. They read git history (`git show`, `git diff`, `git log`) and a **shared clone** in a temporary folder
(`git clone --shared`, checked out at HEAD or at one commit), on which `gov links --all --json` runs as a child
process of the tree under test's `src` (`PYTHONPATH`, an empty `HOME`, no store, no network, nothing built or
read from another tree). The tree under test is never written (not even the mark `gov links` leaves). `record_reading`
is a list of the test map, not a pytest marker; the cases carry no marker, and adding them to
`governance/project/test-map.yaml` is outside this folder's paths (see the return's discoveries).

## How they run

    env HOME=<an empty folder> PYTHONUSERBASE=$HOME_REAL/.local PYTHONPATH=<worktree>/src \
      python3 -m pytest tests/acceptance/W2-130 -q -p no:cacheprovider -o tmp_path_retention_policy=failed \
      -m "not local_only" -k "not real and not green_here and not time_limit"

About 15 to 50 s: `gov links --all` is run on HEAD once, on the starting head once, and on one clone per marks commit
(three), each 5 to 12 s, once per session (session-scoped fixtures). No GPU, no model, no network. No case is
`local_only`, `real`, `green_here` or `time_limit`; no skip, xfail, flaky or rerun mark: a case whose block is
missing fails in its own body.

## Layout

- `w2_130_support.py`: git helpers, the record's block reader (`Record`), the register reader (status lines,
  `classify`, `register_delta`, `added_marks`), the ticket reader (`split_ticket`, `ticket_delta`), the sitting and
  reconciliation row readers, the independent trailer recount (`own_recount`), the `gov links` runner and the clones.
- `conftest.py`: the session fixtures (`record`, `head_tree`, `head_findings`, `start_findings`, `variant_findings`,
  `propose_sources_at`).
- `test_w2_130_marks.py` (S1, S2), `test_w2_130_audit.py` (S3, F3), `test_w2_130_sources.py` (S4),
  `test_w2_130_trailers.py` (S5), `test_w2_130_status.py` (S6, F2), `test_w2_130_lessons.py` (S7),
  `test_w2_130_record.py` (S8, F4), `test_w2_130_integrity.py` (F1).

## The record's blocks the cases read

Each block opens with a line of exactly ```` ```<lang> w2-130:<name> ```` (lang `yaml`, `diff` or `python`), once per
name: `commits`, `ids-87`, `census`, `archive-13`, `judged-wrong`, `audits`, `comparison`, `patch-a0`, `patch-a1`,
`patch-a2`, `patch-b1`, `patch-sources-2`, `patch-marks-3`, `trailer-residuals`, `recount`, `drift`, `drift-run`,
`counts-before`, `counts-after`, `closed-missing`, `no-record`, `dec-1123-linked`, `lessons`, `left`, as the interface states them. A pair
is `{changed: DEC-a, changer: DEC-b}` (or `DEC-a<-DEC-b`); every commit a full 40-hex hash (an abbreviation in
`audit_head` is resolved with `git rev-parse`).

## How the cases read what the interface leaves open

- **A status line "names" a changer** (S1's 87, the 13 archive-only pairs, the two follow-up marks) when the changer's `DEC-n` is in a `**Changed by:**` field of that line (up to
  the next ` · **`) or in a `SUPERSEDED by DEC-a, DEC-b` list. Spelling (zero padding) is the register's.
- **A mark a commit adds** is the tail appended after the old status line (` · **Changed by:** ...` or
  ` · SUPERSEDED by ...`); its pairs are the entry with each `DEC-n` of the tail. c4420040f's decided statuses are
  `- **Status:** <WORD> (...); it was <the old status text>` plus optional marks; the WORD is the first word of the
  sitting row's proposal (ACCEPTED, DONE, SUPERSEDED, WITHDRAWN, DEFERRED) and the id is in groups A to E of
  `W2-130-SITTING.md` (DEC-1098 (3) accepted groups A to G as proposed; group F stays in force, so no word changes).
- **"Derived from free text"** (S3, F3): `gov links` (the commit's own) flags the pair `text: true` on the commit's
  own tree with the marks it appends taken off (`variant_findings`: the commit's own tool (its tree's `src`), the
  commit's tree, its marks stripped; for e12f8a30c that is the parent's register). The brief's other source, the audit's own `free_text` list, is read for
  the verdicts and the comparison.
- **`labelled`** (S3): with an integer `seed` it holds 20 distinct marks; with `seed: null` it holds at most 20 and
  every mark the commit adds that is not free text.
- **A mark judged wrong** is an audited item with verdict `wrong` (fate `dropped`: the commit must not append that
  pair; fate `corrected`: it must append the `committed_mark`'s changers).
- **S5's own count** (`own_recount`): `Task:` a value with no `.tickets/<value>.md` at 232efc47d and not
  `decision-record`; `Implements:` a trailer value of which some element (split on commas and white space, as the
  census splits) is no register entry, no ticket id, no W2 id (`wbs_id`/`external-ref`) and no capability or MR id of
  `docs/contract/contract.yaml`. A residual covers my value when it lists it as written or lists every one of its
  unresolved elements. It finds 8 `Task:` and 12 `Implements:` values at 232efc47d (e.g. `Implements: engineer`, 34
  commits).
- **LINK-RECONCILIATION rows** (S6): the sitting file has no "reason" column; the reason is the row's Evidence column
  (verbatim), the proposal the Proposal column without `**`; groups A to F (150 ids: 110 spent, 40 PROPOSED) have an id
  in their first cell, groups G and H have none and are not row-checked.
- **F2's drift check**: the drift script's pairs whose changed id is in a sitting group C, D or E (not ruled current
  by DEC-1098 (3): superseded, withdrawn, deferred, DONE) fail the case; groups A, B and F are current.
- **S4, DEC-1123 (2)'s forms** (`w2-130:dec-1123-linked`, ticket id -> `[{id, form, via}]`; revised for P-W2-130-4 (a)):
  an *UNLINKED_ID on an open or in-progress ticket* is a `gov links --all --json` finding of that code on a ticket file
  whose `status:` is `open` or `in_progress` at the record's `counts-after.measured_at` (S4's "at HEAD" is re-baselined
  there, with that tree's own `gov links`; pin runs 2 and 3), the pair being (its second id = the ticket, its first id).
  The record lists exactly those pairs that a form links, and the cases read each form from the files at that tree:
  `list_rows` = the id matches `W<n>-<letter><digits>` and is held by the ticket's `list_rows:` field (flow or block
  list), `via` equal to the id; `wbs` = the id is the `wbs_id` (or `external-ref`, the other key `gov` resolves a W2 id
  by) of some ticket file, `via` is the id of one such ticket and that id is in the listed ticket's `sources:`;
  `dec-798` = the id is `DEC-798`, `via` is `DEC-1033`, `DEC-1033` is in the ticket's `sources:` and `gov links`
  reports it as no `NOT_IN_FORCE_AS_RULE` (its "live" test, so the register is read only through the tool). A
  duplicate pair, an unknown form, a ticket that is not open or in progress, and an entry gov links does not report
  are failures. The follow-up sources commit (`commits.sources[1]`): the ids it adds per ticket (tickets it does not
  change have no entry; empty entries are dropped from every side) equal `patch-sources-2`'s ids and `gov links
  --propose-sources --all` at its parent (open and in-progress tickets), each less the (ticket, id) pairs of
  `dec-1123-linked`. e12f8a30c's two cases are as before (its ids equal the whole proposal at its parent and the b1
  patch): the forms were added to `sources:` there, and nothing in the line changes that. The byte-for-byte equality of
  the `patch-sources-2` block with the proposal's sections is not asserted (the line states ids, not bytes).
- **`left`** (S8): D-5 is findings under `template/` and `docs/contract/`, D-6 under `src/` and `tests/`, D-9 under
  `.tickets/`; each as `{path: {role: n}}`, all codes, equal to `gov links --all` at `counts-after.measured_at` (that
  tree's own tool; pin runs 1 and 2).
- **Tool-version sensitive**: `counts-before` for UNMARKED_CHANGE, UNLINKED_ID and STATUS_CONFLICT is compared with the
  starting head's own `gov links` on the starting head; the tool at HEAD has codes the one of that day lacked, so only
  those three are read.
- **Pin run 3** (S4's `closed-missing` and `no-record`): both cases read the tickets' statuses and files, the register's
  headings and the ticket stems in the tree at `counts-after.measured_at`, with that tree's own `gov links`, as S4's
  other three cases do. The cases left on the branch's tool at HEAD are the HEAD-wide ones: S2's "no UNMARKED_CHANGE but
  the eight pairs", S6's no STATUS_CONFLICT and S7's no UNKNOWN_ID on a lesson.

## Proofs outside the commits (scratch copy under `$TMPDIR`)

A scratch clone with the five follow-up commits made by a script and a plausible record built from the real data:
**79 of 79 cases pass**. Two planted breaks, each in its own scratch copy, then discarded:
a register status line edited in its middle in a commit listed in `commits.cleanup` fails
`test_w2_130_integrity.py::test_f1_every_cleanup_commit_the_record_names_changes_only_status_lines_marks_sources_and_allowed_paths`
(`DEC-030 'other': not marks appended, nor a status DEC-1098 (3) names`); an `audits` item that judges one committed
mark wrong fails `test_w2_130_audit.py::test_s3_verdicts_and_fates_agree_with_what_each_commit_committed`,
`test_w2_130_audit.py::test_f3_no_committed_mark_is_one_any_audit_judged_wrong` and
`test_w2_130_audit.py::test_f3_the_comparison_shows_no_unchecked_and_no_wrong_mark_and_my_comparison_agrees`.

## KPI lines, tests, and the outcome on the branch base `09542040f`

**Revision, run 3 batch 3 (the lead's run-3 findings 1 to 5), branch head `ba9f5ed4d`:** five cases that read more than
their Verify line states were cut back to the line; each is still red on the base (no record) and green on a scratch
record built from the real history, and red for a planted break. 81 tests, **55 red, 26 green** at `ba9f5ed4d` (the same
counts as before; no other case changed).

- Finding 1 (S1, the a0-a2 patches): patch a0 is ARCHIVE-SUPERSEDED's change and holds no register hunk; the register
  marks are in a1 and a2. A patch with no register hunk now appends no register pair (a patch with no `diff --git`
  section still fails); the union of the three patches' register pairs, after the drops and rewrites, must equal the
  marks e12f8a30c adds; each patch's files must be files e12f8a30c changes; some patch must hold a register mark.
- Finding 2 (S1, marks added after e12f8a30c): the line is about the clean-up's marks (the census's pairs). A later
  commit's own change of a status line of the 87 (DEC-866's marking of a new decision's change, e.g. 518772b5c's
  DEC-989<-DEC-1141) may stay out of a marks commit when it keeps the old line whole (an append) and adds no census
  pair of that entry. An edit in the middle of the line, or a census pair appended outside a marks commit, fails; in a
  named marks commit the check is as before (append or decided status).
- Findings 3 and 4 (S2, the two follow-up marks): the Verify names the pairs (DEC-1115<-DEC-1122, DEC-026<-DEC-086),
  not the mark's wording, which the independent auditor may correct (S3). The case no longer fixes the appended text:
  exactly one follow-up marks commit, after both clean-up commits, appends to the old line a mark that makes the line
  name the changer; the audit's right verdict, ancestor head and earlier date are checked as before.
- Finding 5 (S2, the 215): "named on its own status line" is read as `gov links` reads it (UNMARKED_CHANGE: the
  changer's id is on the entry's status line). The form (**Changed by:** or SUPERSEDED by) is S1's, for the 87, and S1's
  case still checks it. The other census ids name some changers in older forms (**Amended by:**, **Lifted by:**, prose).
  The 13 archive-only pairs case keeps the form check (it passes on the history).

Proofs (scratch clone under `$TMPDIR`, a record built from the real data, never committed): the original cases fail on it
(finding 1: no register hunk in a0; 2: `518772b5c272 DEC-989 other`; 3 and 4: the exact text; 5: 7 old-form pairs not on
their line) and the revised pass; planted breaks fail the revised cases: an a1 patch lacking one hunk (139 marks
committed, 138 patched); a scratch commit editing DEC-030's status line in its middle; a scratch commit appending a census
changer to DEC-039 outside a marks commit; a follow-up commit naming DEC-1121 with the right mark in an unlisted commit;
DEC-150's line with DEC-156 removed.

**Revision, run 3 batch 2 (P-W2-130-4 (a)), branch head `11c4d7a5a`:** S4's head case and its follow-up case were
rewritten to DEC-1123 (2) and two cases added (`w2-130:dec-1123-linked`, also added to the block list S8 checks): **81
tests, 55 red, 26 green** on `11c4d7a5a` (whole folder, 17 s; run 2's count was 26 passed, 53 failed: the same 26 pass;
the S4 rows below are the only rows whose cases changed, and the S8 block-list case is red for the same reason as
before). The three S4 head cases and the follow-up case were also shown green on a scratch clone with a record built
from the real data (25 open or in-progress tickets with 97 UNLINKED_ID pairs at this base: 65 of the three forms, the
other 32 added to `sources:` by a scratch follow-up commit), and red for two planted breaks in scratch copies (an entry
whose form is false, a backlog row the ticket's `list_rows` does not hold: the form and the "reported by gov links"
cases fail; a form id left out of the list: the completeness case and the follow-up case fail), all discarded.

The table below was written at `09542040f` with 79 tests (**56 red, 23 green**, 17 s in the heavy slot); its green and
red words for rows outside S4 are as of that base. The 23 green are the history-only cases (the clean-up's two
commits as they are in git, ancestry, the sitting file, DEC-1098 (3)'s commit, the 150 sitting rows, the statuses
c4420040f wrote). Every red fails at its first assertion for the reason in its row; where the reason is the missing
record, the case reads the record first and fails (never skips).

| KPI line | Test (node id) | On the base | Why |
|---|---|---|---|
| S1 | `test_w2_130_marks.py::test_s1_the_first_cleanup_commit_is_e12f8a30c_and_its_parent_is_the_starting_head` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S1 | `test_w2_130_marks.py::test_s1_register_hunks_of_e12f8a30c_are_status_line_appends_only` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S1 | `test_w2_130_marks.py::test_s1_every_mark_e12f8a30c_appends_is_still_on_its_status_line_at_head` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S1 | `test_w2_130_marks.py::test_s1_the_record_names_e12f8a30c_as_the_first_commit_and_the_starting_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S1 | `test_w2_130_marks.py::test_s1_ids_87_are_87_distinct_ids_each_a_key_of_the_census` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S1 | `test_w2_130_marks.py::test_s1_each_of_the_87_names_every_changer_the_census_states_on_its_own_status_line` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S1 | `test_w2_130_marks.py::test_s1_the_marks_e12f8a30c_adds_equal_patches_a0_a1_a2_after_the_audits_drops_and_rewrites` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S1 | `test_w2_130_marks.py::test_s1_a_mark_on_one_of_the_87_added_after_e12f8a30c_is_in_a_marks_commit_and_append_only` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_gov_links_reports_no_unmarked_change_but_the_eight_pairs_the_auditor_judged_wrong` | red | HEAD reports UNMARKED_CHANGE for DEC-026<-DEC-086 and DEC-1115<-DEC-1122 besides the 8 (not yet marked); a pair whose later decision is recorded as the owner's counts as marked (rule, not a pinned list) |
| S2 | `test_w2_130_marks.py::test_s2_a_pair_is_a_marked_change_only_when_its_later_decision_is_recorded_as_the_owners` | green | green by design: the owner-decision rule on a planted register (a changer recorded as the owner's by `ACCEPTED (owner` or `Decided-by: owner` is a marked change; any other changer, or one the register lacks, is not) |
| S2 | `test_w2_130_marks.py::test_s2_judged_wrong_holds_the_eight_gov_links_pairs_each_with_the_auditors_verdict` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_the_two_follow_up_marks_are_in_a_marks_commit_after_a_right_verdict[dec-1115-dec-1122]` | red | HEAD's status line of DEC-1115 (DEC-026) does not name DEC-1122 (DEC-086) yet |
| S2 | `test_w2_130_marks.py::test_s2_the_two_follow_up_marks_are_in_a_marks_commit_after_a_right_verdict[dec-026-dec-086]` | red | HEAD's status line of DEC-1115 (DEC-026) does not name DEC-1122 (DEC-086) yet |
| S2 | `test_w2_130_marks.py::test_s2_census_has_215_keys_and_archive_13_has_13_distinct_pairs` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_each_census_id_names_every_stated_changer_unless_the_auditor_judged_the_pair_wrong` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_each_archive_only_pair_names_its_changer_unless_the_auditor_judged_it_wrong` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_the_drift_script_on_head_leaves_no_pair_once_the_listed_pairs_are_set_aside` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S2 | `test_w2_130_marks.py::test_s2_drift_run_keeps_the_command_the_output_and_the_pairs_set_aside_with_count_zero` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_every_marks_commit_has_one_audit_item_and_each_item_is_for_a_marks_commit` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_each_audit_is_dated_before_its_commit_and_made_at_an_ancestor_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_the_first_two_audits_were_made_at_the_heads_the_interface_names[e12f8a30c]` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_the_first_two_audits_were_made_at_the_heads_the_interface_names[c4420040f]` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_labelled_marks_are_twenty_drawn_by_a_seed_or_every_labelled_mark_when_twenty_or_fewer` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_s3_verdicts_and_fates_agree_with_what_each_commit_committed` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S3 | `test_w2_130_audit.py::test_f3_the_comparison_shows_no_unchecked_and_no_wrong_mark_and_my_comparison_agrees` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips); with a record, red until each of the 97 UNLINKED_ID pairs gov links reports on open or in-progress tickets at this base is listed or added to `sources:` |
| S4 | `test_w2_130_sources.py::test_s4_each_dec_1123_linked_entry_is_of_its_form_at_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_dec_1123_linked_lists_only_unlinked_ids_gov_links_reports_at_head_on_open_or_in_progress_tickets` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_the_record_names_e12f8a30c_and_at_most_one_follow_up_as_the_sources_commits` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_e12f8a30c_changes_only_the_sources_field_of_tickets_open_or_in_progress_at_its_parent[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S4 | `test_w2_130_sources.py::test_s4_the_follow_up_sources_commit_changes_only_sources_of_live_tickets_and_no_other_file` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_the_ids_e12f8a30c_adds_equal_gov_links_propose_sources_at_its_parent[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S4 | `test_w2_130_sources.py::test_s4_the_b1_patch_in_the_record_equals_the_ids_e12f8a30c_added` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_the_follow_up_ids_equal_patch_sources_2_and_gov_links_propose_sources_at_its_parent_less_the_forms` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_outside_the_sources_commits_a_cleanup_commit_adds_to_sources_only_dec_1098_and_dec_1088_on_this_ticket` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_c4420040f_adds_to_sources_only_dec_1098_and_dec_1088_on_this_ticket` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S4 | `test_w2_130_sources.py::test_s4_no_closed_ticket_is_changed_by_e12f8a30c_or_c4420040f[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S4 | `test_w2_130_sources.py::test_s4_no_closed_ticket_is_changed_by_e12f8a30c_or_c4420040f[c4420040f]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S4 | `test_w2_130_sources.py::test_s4_no_clean_up_commit_the_record_names_changes_a_ticket_closed_at_its_parent` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S4 | `test_w2_130_sources.py::test_s4_no_record_lists_per_ticket_ids_that_name_no_record` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_the_starting_head_is_an_ancestor_of_head_so_no_history_was_rewritten` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S5 | `test_w2_130_trailers.py::test_s5_the_residuals_are_taken_at_the_starting_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_each_trailer_and_value_is_listed_once_and_task_decision_record_is_not_listed` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_each_value_has_its_commits_its_tickets_and_the_ids_it_should_have_named` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_every_listed_commit_carries_the_value_it_is_listed_under_at_the_starting_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_the_recount_command_at_the_starting_head_gives_exactly_the_listed_set` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S5 | `test_w2_130_trailers.py::test_s5_my_own_count_of_values_naming_no_record_finds_none_missing_from_the_set` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S6 | `test_w2_130_status.py::test_s6_the_sitting_list_exists_in_2f9c80b1f_an_ancestor_of_the_starting_head` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S6 | `test_w2_130_status.py::test_s6_the_sitting_lists_the_150_ids_of_the_110_spent_and_the_40_proposed` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S6 | `test_w2_130_status.py::test_s6_c4420040f_changes_a_status_only_to_the_word_the_sitting_proposed_and_keeps_the_old_text` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S6 | `test_w2_130_status.py::test_s6_gov_links_reports_no_status_conflict_at_head` | red | STATUS_CONFLICT DEC-896 at DECISIONS-IN-FORCE.md (the R-12 line) |
| S6 | `test_w2_130_status.py::test_s6_the_r_12_commit_changes_only_decisions_in_force_and_only_its_r_12_line` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S6 | `test_w2_130_status.py::test_s6_linkreconciliation_names_the_sitting_file_and_dec_1098_3_and_carries_each_sitting_row` | red | LINK-RECONCILIATION.md does not exist at HEAD |
| S7 | `test_w2_130_lessons.py::test_s7_every_lesson_at_head_has_a_front_matter_sources_key_naming_at_least_one_id` | red | none of the 5 lessons has a `sources:` key |
| S7 | `test_w2_130_lessons.py::test_s7_gov_links_reports_no_unknown_id_with_a_lesson_s_path` | green | green by design: history only (the commits and the sitting file as they are in git) |
| S7 | `test_w2_130_lessons.py::test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S7 | `test_w2_130_lessons.py::test_s7_the_lessons_commit_changes_only_lessons_each_by_the_one_added_sources_line` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_the_record_exists_and_holds_each_block_the_interface_names_once` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_the_commits_block_names_the_fixed_facts_and_each_list` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_counts_before_are_at_the_starting_head_and_counts_after_at_the_last_cleanup_commit` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_gov_links_at_head_gives_the_after_counts` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_the_before_counts_of_the_codes_the_clean_up_works_on_equal_gov_links_at_the_starting_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| S8 | `test_w2_130_record.py::test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F1 | `test_w2_130_integrity.py::test_f1_register_changes_of_e12f8a30c_and_c4420040f_are_status_lines_marks_appended_or_decided[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_register_changes_of_e12f8a30c_and_c4420040f_are_status_lines_marks_appended_or_decided[c4420040f]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_ticket_fields_other_than_sources_and_bodies_are_byte_identical_across_e12f8a30c_and_c4420040f[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_ticket_fields_other_than_sources_and_bodies_are_byte_identical_across_e12f8a30c_and_c4420040f[c4420040f]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_the_two_commits_change_only_the_paths_the_ticket_allows[e12f8a30c]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_the_two_commits_change_only_the_paths_the_ticket_allows[c4420040f]` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_integrity.py::test_f1_every_cleanup_commit_the_record_names_changes_only_status_lines_marks_sources_and_allowed_paths` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F1 | `test_w2_130_integrity.py::test_f1_each_follow_up_marks_commit_changes_the_register_and_no_other_file` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F1 | `test_w2_130_integrity.py::test_f1_the_starting_head_is_an_ancestor_of_head` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F1 | `test_w2_130_status.py::test_s6_c4420040f_changes_a_status_only_to_the_word_the_sitting_proposed_and_keeps_the_old_text` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F2 | `test_w2_130_status.py::test_f2_the_owners_decision_9546edd61_is_an_ancestor_of_c4420040f` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F2 | `test_w2_130_status.py::test_f2_e12f8a30c_changes_no_status_word_and_no_done_tag` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F2 | `test_w2_130_status.py::test_f2_the_owners_decision_is_an_ancestor_of_every_status_commit_the_record_names` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F2 | `test_w2_130_status.py::test_f2_no_cleanup_commit_without_9546edd61_as_ancestor_changes_a_status_word_or_done_tag` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F2 | `test_w2_130_status.py::test_f2_the_drift_list_at_head_holds_no_sitting_id_that_dec_1098_3_did_not_rule_current` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F3 | `test_w2_130_audit.py::test_f3_every_free_text_mark_a_commit_adds_is_in_the_audit_with_a_verdict_of_right` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F3 | `test_w2_130_audit.py::test_f3_no_committed_mark_is_one_any_audit_judged_wrong` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F3 | `test_w2_130_audit.py::test_f3_the_comparison_shows_no_unchecked_and_no_wrong_mark_and_my_comparison_agrees` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
| F4 | `test_w2_130_record.py::test_f4_e12f8a30c_has_w2_129_s_landing_and_w2_92_s_stated_links_as_ancestors` | green | green by design: history only (the commits and the sitting file as they are in git) |
| F4 | `test_w2_130_record.py::test_f4_the_record_cites_dec_1097_9_the_owner_s_decision_that_allowed_the_start` | red | `docs/research/W2-130-link-cleanup.md` does not exist (the block this case reads is missing: the case fails, never skips) |
