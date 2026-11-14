**Sandbox check (Step 0):** (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with a read-only file system, as required. (b) `git hash-object -w` and `git update-index --refresh` both worked. The `ps` check for ollama/llama-server shows nothing of mine.

task: DAEO-q8cl (W2-130), independent test designer, run 2 batch 1, STANDARD, C2.
status: done. The tests are committed and `TESTS-READY`. On the base `09542040f`, 23 of 79 cases are green and 56 are red.
work_completed:
- I wrote 79 repository-state cases covering all eleven KPI lines (S1–S8, F1–F4), plus a README map, `conftest.py` and a support module.
- A scratch clone with the five follow-up commits made by a script and a plausible record built from real data passes 79 of 79.
- `gov accept DAEO-q8cl` reads the README map: 12 lines, 0 unmapped cases, 23 passed and 56 failed on the base.
files_changed: all new, under `tests/acceptance/W2-130/`:
- `README.md`, `conftest.py`, `w2_130_support.py`
- `test_w2_130_marks.py` (S1, S2), `test_w2_130_audit.py` (S3, F3), `test_w2_130_sources.py` (S4), `test_w2_130_trailers.py` (S5)
- `test_w2_130_status.py` (S6, F2), `test_w2_130_lessons.py` (S7), `test_w2_130_record.py` (S8, F4), `test_w2_130_integrity.py` (F1)

evidence:
- Base run at `09542040f` through the heavy slot, with `-m "not local_only" -k "not real and not green_here and not time_limit"`: `56 failed, 23 passed in 16.94s`. The exclusion left out nothing; no case is `real`, `green_here`, `time_limit` or `local_only`.
- `gov accept` totals: `passed 23, failed 56, skipped 0`.
- **Planted break 1:** a register status line edited in its middle, in a scratch commit after c4420040f and listed in `commits.cleanup`, fails `test_f1_every_cleanup_commit_the_record_names_changes_only_status_lines_marks_sources_and_allowed_paths`. The message is `DEC-030 'other': not marks appended, nor a status DEC-1098 (3) names`.
- **Planted break 2:** an `audits` item that judges one committed mark wrong fails `test_s3_verdicts_and_fates_agree_with_what_each_commit_committed`, `test_f3_no_committed_mark_is_one_any_audit_judged_wrong` and `test_f3_the_comparison_shows_no_unchecked_and_no_wrong_mark_and_my_comparison_agrees`. Both scratch copies were discarded.

tests: results on the base, case by case.
- **Green (23), history-only, as the brief expected.**
  - F1 history cases:
    - register hunks of e12f8a30c and c4420040f (two cases)
    - tickets' fields (two cases)
    - allowed paths (two cases)
    - starting head is an ancestor of HEAD
  - S1:
    - e12f8a30c's parent is 232efc47d
    - e12f8a30c's register hunks are status-line appends only
    - every mark e12f8a30c appends is still named at HEAD
  - S4 on e12f8a30c and c4420040f:
    - e12f8a30c changes only the `sources:` field of tickets open or in progress at its parent
    - the ids e12f8a30c adds equal `gov links --propose-sources` at 232efc47d, which I checked on all 50 tickets
    - c4420040f adds only DEC-1098 and DEC-1088 to this ticket
    - no closed ticket is touched by either commit (two cases)
  - S5: 232efc47d is an ancestor of HEAD.
  - S6 and F2:
    - sitting file in 2f9c80b1f, an ancestor of the starting head
    - the sitting's 150 rows
    - 9546edd61 is an ancestor of c4420040f
    - e12f8a30c changes no status word
    - c4420040f writes each decided status as proposed, old text kept, 143 ids
  - S7: 0 UNKNOWN_ID on a lesson's path.
  - F4: the 34eed411a and 3679ca0ba ancestry.
  - No history-only case was red, so there is no finding to report there.
- **Red for a reason other than the missing record (6):**
  - S2, 1 case: HEAD reports UNMARKED_CHANGE for DEC-026<-DEC-086 and DEC-1115<-DEC-1122 beyond the 8.
  - S2, 2 cases: HEAD's status lines of DEC-1115 and DEC-026 do not name the changer yet.
  - S4: 102 UNLINKED_ID on open tickets at HEAD.
  - S6: STATUS_CONFLICT on DEC-896 (the R-12 line).
  - S6: LINK-RECONCILIATION.md does not exist.
  - S7: none of the 5 lessons has a `sources:` key.
  - Of these six, the S7 and S6 cases fail on their own assertion.
- **Red (the other 50): `docs/research/W2-130-link-cleanup.md` does not exist.** Each case fails in its own body; none skips.

discoveries:
- **Sources removed after e12f8a30c.** The 102 UNLINKED_ID on open tickets include ids that e12f8a30c added to `sources:` and commit `66303c373` (D-10 run 2, DEC-1123 (2)) later removed, for example W2-H021 on DAEO-057v. Follow-up (1) must re-add them, or the ticket must state otherwise.
- **`gov links --propose-sources` uses a flow-style line.** For tickets with `sources: [...]` it rewrites the whole line, so `patch-sources-2` has no `+- ID` lines for those. My patch reader handles both forms.
- **The tool reads the in-force claim before the first colon.** `gov links` reads ids in a DECISIONS-IN-FORCE line only before its first `:`. A reword of R-12 that keeps DEC-896 in the parenthesis before the colon, even as "the done DEC-896", still gives STATUS_CONFLICT. DEC-896 has to move after the colon or out of the line.
- **Census pairs the auditor dropped.** Several pairs from the earlier audit (DEC-454, DEC-455 and DEC-480 with DEC-904 or DEC-899; DEC-038<-DEC-051; DEC-045<-DEC-053) are not on their status lines. They belong in `judged-wrong` with `in_gov_links: false`, or S1 and S2 fail.
- **`record_reading` is not a pytest marker.** It is a list in the test map. Adding these cases there is outside my allowed paths; the CTO needs to do it.

risks:
- **Tool-version sensitivity.** `variant_findings` and the S8 before-counts use HEAD's `gov links` on older trees. A later tool change could flag a different `text` set or different before-counts. I limited the before-count check to UNMARKED_CHANGE, UNLINKED_ID and STATUS_CONFLICT.
- **S3's "free text" oracle is my reading.** I used the pairs `gov links` flags `text: true` on the commit's own tree with its marks stripped. The audit's `free_text` list is only read for verdicts and the comparison.
- **`left` (S8) is read strictly.** I compare D-5, D-6 and D-9 to all findings under their prefixes at HEAD, all codes. If the implementer means a narrower set, this case needs revising.
- **Other readings that could go red.**
  - Sitting row "reason" is the Evidence column.
  - Lesson `came_from` must be a quote from the lesson.
  - Each `**Source:**` DEC id in a lesson must be in its `sources:`.
  - The S5 recount treats `AR-9` and `(no` style tokens as unresolved.
  - All of these are written up in the README.
- **Session cost.** The folder takes about 50 s of its own, once per session.

lessons: none.
proposed_decisions: none (no ambiguous KPI line left unresolved; the readings above are in the README).
unresolved: none.
recommended_next_action: the CTO merges the tests into the implementer's branch and adds the cases to `record_reading` in the test map. The implementer then runs `gov accept DAEO-q8cl` after follow-ups (1)–(5).

commits: `02cbbb169` W2-130 (DAEO-q8cl): acceptance cases for the re-baselined Verify lines: 79 repository-state cases (S1-S8, F1-F4), 23 history-only green and 56 red on the base… | trailers as committed: `Task: DAEO-q8cl`, `Role: independent-test-designer`, `Implements: DEC-1073, DEC-1072, DEC-866, DEC-825, DEC-927, DEC-861, DEC-953, DEC-1010, DEC-1098, DEC-1088`, `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`. Tracked `git status --short` is empty.

guard_refusals: one. A Bash call that read DAEO-057v's ticket file and the `links_head.json` scratch file together was denied once, with no reason given. I did not repeat it and read the ticket with Grep instead; no other call was refused.