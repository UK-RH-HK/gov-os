# Brief: independent test designer, W2-130 (DAEO-q8cl): pin run 2 (S4's three HEAD cases pinned; every pinned case runs the pinned tree's own gov links)

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read. You work in the tests worktree and make ONE commit there;
the lead merges it. Every pytest goes through heavy_slot.sh (below). Your scratch is your sandbox's own `$TMPDIR`.

## Where things are
| what | path |
|---|---|
| your worktree (write here only) / branch | /home/usain/gov-os-worktrees/W2-130-tests / w2/W2-130-tests (at 67364dbea2fb) |
| the ticket (KPI lines S4 and S8 and their Verify clauses; its last paragraph, "Reopened 2026-11-14") | `.tickets/DAEO-q8cl.md` |
| your context packet (the ticket and its authority, built by `gov context` outside the sandbox) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/context-td.md |
| pin run 1 (read both bodies first: what was pinned and why) | `git show 35b6ac6ba` and `git show 6a0b84a81` |
| pin run 1's narrow check (its F1 and F4 are what this run answers) | `docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin.md` |
| W2-130's record (read only; never edited) | `docs/research/W2-130-link-cleanup.md`: blocks `w2-130:counts-after` (its `measured_at`), `w2-130:left`, `w2-130:dec-1123-linked` |
| the README map `gov accept` reads (not edited) | `tests/acceptance/W2-130/README.md` (S4 rows near lines 185-200, S8 rows near 218-223) |

## Your paths (only these files change)
`tests/acceptance/W2-130/test_w2_130_sources.py`, `tests/acceptance/W2-130/test_w2_130_record.py`,
`tests/acceptance/W2-130/w2_130_support.py`, and only if a fixture is needed `tests/acceptance/W2-130/conftest.py`.
No record, README, ticket, register, source or other test file changes.

## The decided behaviour (the CTO, under DEC-1156 (7) and DEC-1164 (18); listed for the owner's reading)
- **F1 confirmed:** the pin is the record's `counts-after.measured_at` (6b62de94e), as pin run 1 did for S8.
- **P-W2-130-PIN-S4 (a):** the three S4 cases that read HEAD are pinned at `counts-after.measured_at`, as S8 now is:
  - `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`
  - `test_w2_130_sources.py::test_s4_each_dec_1123_linked_entry_is_of_its_form_at_head`
  - `test_w2_130_sources.py::test_s4_dec_1123_linked_lists_only_unlinked_ids_gov_links_reports_at_head_on_open_or_in_progress_tickets`
  They now use `head_findings`/`head_tree`; instead they run `gov links` on `clone_at(<measured_at>)` and read ticket
  statuses and files in that same tree. S4's Verify "on HEAD" is re-baselined to the record's measured tree under
  DEC-1156 (7); live tickets' links stay `gov links`'s own job and D-9's. Reuse pin run 1's `_measured_at(record)`
  checks (full hash, `counts-after.head` or a descendant, ancestor of HEAD); move it to `w2_130_support.py` if both
  files need it, rather than copying it.
- **F4: pin the tool too.** Every pinned case runs `gov links` from the pinned tree's own `src` (the clone at the
  pinned commit, `PYTHONPATH=<clone>/src`), so a later change to `gov links` cannot move a pinned count. Today
  `w2_130_support.run_links`/`child_env` take `PYTHONPATH` from `src_dir()` (the test run's own PYTHONPATH, i.e. the
  branch's `src`). Give the pinned cases a way to run the clone's own `src` (for example a `src` argument to
  `links_json`/`run_links`, or a session fixture `pinned_findings`), and leave the unpinned HEAD-wide cases (the
  "no UNMARKED_CHANGE but the 8 pairs" case and the others on `head_findings`) running the branch's tool as now.
  The pinned cases are: the three S4 cases above; S8's `test_s8_gov_links_at_head_gives_the_after_counts` and
  `test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head` (at `measured_at`); and S8's
  `test_s8_the_before_counts_of_the_codes_the_clean_up_works_on_equal_gov_links_at_the_starting_head` (pinned at the
  starting head 232efc47d through `start_findings`; its docstring says it runs HEAD's tool: make it run the starting
  head's own `src`, and fix the docstring). If you find any other case that runs `gov links` at a fixed commit, say so
  and pin its tool the same way; if you judge one should not be, say why in your return.
- **Keep every case name the README map uses** (`gov accept` collects mapped node ids; an unmapped new case is not
  wanted). Put a docstring on each revised case saying what tree and which tool it now reads, and that the name is kept
  for the README map (DEC-1156 (7) pin run 2).

## The lead's measurement (for your check, not instead of it)
With the cases' own counting (lead's probe `.gov-runtime/scratch/lead/run6/probe_pinned_tool.py` in
/home/usain/gov-os-worktrees/W2-130; judge the tests, not the script): at `measured_at` 6b62de94e3fd, both the branch's
tool and the clone's own `src` give the record's `by_code`, `by_code_role`, `unlinked_by_status` and `left` D-5, D-6,
D-9; S4's three conditions hold there (no unlisted pair, no extra listed pair, no form problem). At the starting head
232efc47d, both tools give the record's before counts for UNMARKED_CHANGE 185, UNLINKED_ID 1877, STATUS_CONFLICT 116.
So every pinned case should be green with the pinned tool.

## No case loses its point (show it)
In a scratch copy under `$TMPDIR` (a `git clone --shared` of your worktree with your change committed, records edited
in the copy only; never in your worktree):
1. Plant one wrong count in `counts-after` and one wrong path count in `left`: the two S8 cases fail, naming it.
2. In `dec-1123-linked`, drop one listed entry (S4 case 1 fails: an unlisted pair), add one pair that is no UNLINKED_ID
   at `measured_at` (case 3 fails), and change one entry's `form`/`via` so it is not of its form (case 2 fails).
3. Show the tool is pinned: in the copy, make the branch's `src` differ from the pinned tree's (for instance a copy of
   `src` whose `gov links` adds or drops one finding, put first on PYTHONPATH) and show the pinned cases still give
   the pinned tree's counts (they do not read the branch's tool), while a HEAD-wide case does read it.
Say what you planted and what failed in the commit body and in your return.

## Run
Run the changed files, then both folders, each through heavy_slot.sh:
`env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
on `tests/acceptance/W2-130` and `tests/acceptance/W2-175`. Both folders must be green at your commit; report every red
with its message. Then `--collect-only -q` on `tests/acceptance/W2-130` and confirm every node id the README map names
in `test_w2_130_sources.py` and `test_w2_130_record.py` collects. A resource gate's refusal is a wait (relaunch when
open). No merge, no `gov retrieve`, no `gov context` in the sandbox.

Also report, without changing them: whether `test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack`
and `test_s4_no_record_lists_per_ticket_ids_that_name_no_record` (they read HEAD through `head_findings`) can be turned
red by a ticket closed or reopened after the land, and how; the lead brings that to the CTO.

## Commit (one commit, your paths only, trailers in ONE final paragraph, no blank line inside it)
Write the message to a file under `$TMPDIR` and commit with `git -C /home/usain/gov-os-worktrees/W2-130-tests commit -F <file> -- <your changed paths>`.
Subject: `W2-130 (DAEO-q8cl) tests: pin run 2: S4's three HEAD cases at the record's measured tree; every pinned case runs the pinned tree's own gov links`.
Body: what changed and why; **which cases now run the pinned tool** (by node id, and at which commit); the
planted-value demonstrations. Final paragraph, exactly these lines:
```
Task: DAEO-q8cl
Role: independent-test-designer
Implements: DEC-1073, DEC-1010
Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 2)
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```
(DEC-1156 and DEC-1164 are not in the ticket's sources:, so they go in Rewrite-Reason and your discoveries, not
Implements.)

## Return (your last message): the twelve fields, each a labelled line ("none" where nothing)
task: / status: (DONE, PACKAGES or ESCALATION) / work_completed: / files_changed: / evidence: (the commit hash in full,
both folders' pytest counts, the collect-only check, the planted-value failures) / tests: / discoveries: / risks: /
lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Report step 0's sandbox check first.

## Searching and refusals
Read and Grep, and git show/log; search once, then once more in other words; answer from what you read with path and
line, or say "not found". Never open the evaluation sets' root, held-out material or any hidden or memory-verdict
folder. Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a
refusal.
