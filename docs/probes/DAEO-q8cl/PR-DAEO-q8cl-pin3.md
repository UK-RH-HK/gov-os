---
type: probe
task: DAEO-q8cl
reviewer_session: bcc77457-64e4-48f8-9e4f-d3f464372e50
implementer_session: "independent-test-designer session 996a5e96-496b-487c-ae07-48ef600dfe94 (commit 83285c3c52c32b7f96936b815e2656604a6d97cb)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 17487b4700861003d208de7f256a7d1e479c9562
decisions_applied: [DEC-1156, DEC-1164, DEC-1073, DEC-1010]
---

# Probe record: W2-130 (DAEO-q8cl), pin run 3's narrow independent check (a decided-behaviour test revision)

A fresh independent-auditor session (`bcc77457-64e4-48f8-9e4f-d3f464372e50`) ran on `claude-opus-5-5` at high effort, class C2, read-only, with
JUDGEMENT.md word for word in its brief. It probed head `17487b470086` of `w2/W2-130` (the lead's merge of
`w2/W2-130-tests`), narrow: this revision only, since `aafaf6259d10`. It wrote nothing (`git status` empty; sandbox
trial file absent; tripwire clean).

What it probed: the CTO's answers under DEC-1164 (18) and DEC-1156 (7) (listed for the owner's reading):
P-W2-130-PIN2-HEAD (a) (the two S4 cases that still read HEAD,
`test_s4_closed_missing_lists_per_closed_ticket_the_ids_its_sources_lack` and
`test_s4_no_record_lists_per_ticket_ids_that_name_no_record`, pinned at `counts-after.measured_at` with the pinned
tree's own `gov links`), and row F1 riding along (`variant_findings`, used by the S3/F3 cases, runs the marks commit's
own tool). One independent test designer commit, `83285c3c5`, in `tests/acceptance/W2-130/` only (README prose,
`conftest.py`, `test_w2_130_audit.py` docstring, `test_w2_130_sources.py`); no record, ticket, source or map row edited;
every case name kept. The CTO also asked whether any W2-130 or W2-175 case still reads a value that a later ticket event
or approved change moves (item 6).

Its verdict is **PASS**: six items pass, two findings, none blocking (neither in scope with ordinary work yes and fails
open or loses work).

## The lead's judgement of the findings

- **F1** (out of scope: two W2-130 S7 cases,
  `test_w2_130_lessons.py::test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from` and
  `test_w2_130_lessons.py::test_s7_the_lessons_commit_changes_only_lessons_each_by_the_one_added_sources_line`, compare
  the record's lesson list with the lessons in the working tree; a lesson added after the land turns both red, shown by
  a scratch commit). Ordinary work: yes, because lessons are added routinely by approved changes. Consequence: other (a
  false red on a re-run of `gov accept W2-130`; fails closed, nothing lost). A row, brought to the CTO in the lead's
  return.
- **F2** (out of scope: W2-175's S1 to S5 read the role templates in the working tree and S5 asserts `version: 1.0.1`;
  the next approved template delta turns S5 red, shown by a scratch commit setting role-cto.md to 1.0.2). Ordinary work:
  yes, because template deltas go through CIT-P routinely. Consequence: other (a false red; fails closed, nothing lost).
  A row for the CTO; `test_w2_175_templates.py` is outside W2-130's paths.
- The cases the auditor lists as moved by HEAD-wide reads (S1, S2, S6, F2's drift list, S2/S6/S7's `head_findings`)
  judge HEAD itself; that is their point, as the test designer's commit body also states.

The lead's own runs at `17487b470086`: the two changed test files (sources and audit) 25 passed; `gov accept W2-130` 81
passed, 0 failed (all twelve lines pass); `gov accept W2-175` 51 passed, 0 failed; the scoped run (DEC-968) of
`tests/acceptance/W2-130` and `tests/acceptance/W2-175` 132 passed.

## The auditor's return, word for word

**Step 0, sandbox check (launch_worker.sh):** passed. (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-q8cl` failed with `OSError: [Errno 30] Read-only file system`, and no file exists there. (b) `echo sandbox-trial | git hash-object -w --stdin` worked (exit 0, `1ae28402a109c3397a44b19239a00adfa9472eb0`, an unreachable blob), and so did `git update-index --refresh` (exit 0). `GOV_TICKET=DAEO-q8cl`, `GOV_ROLE=independent-auditor`. **ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing (exit 1), both at the start and at the end.

task: DAEO-q8cl (W2-130), the narrow independent check of pin run 3 (test designer commit 83285c3c5, merged as 17487b470)
status: PASS. All six items pass. There are two non-blocking rows (F1, F2) under item 6, and none in scope reachable in ordinary work that fails open or loses work.
work_completed: Read the diff from aafaf6259d10 to 17487b470, the trailers, conftest, support, the sources, audit, record, lessons, status and marks modules, and W2-175's support, record and templates modules. Ran the W2-130 and W2-175 folders at the audited head. Ran `--collect-only` and compared it with the README map. In scratch clones under `$TMPDIR`: committed ticket events after measured_at; ran a modified copy of `src` first on PYTHONPATH against the audited head and against aafaf6259d10; planted 9 record changes; committed a lesson and an approved-style template change.
files_changed: none. The tree is clean at 17487b4700861003d208de7f256a7d1e479c9562 (`git status --porcelain` is empty). All scratch work is under `$TMPDIR/aud/`.
evidence: tests/acceptance/W2-130/conftest.py:78-94, tests/acceptance/W2-130/w2_130_support.py:585-636, tests/acceptance/W2-130/test_w2_130_sources.py:14-17,66-69,187-230, tests/acceptance/W2-130/test_w2_130_lessons.py:11,38-73, tests/acceptance/W2-175/test_w2_175_templates.py:106-115, tests/acceptance/W2-175/w2_175_support.py:47,117-119, tests/acceptance/W2-130/README.md:60-62,79-106, docs/research/W2-130-link-cleanup.md:5473-5476
tests: At the audited head, `tests/acceptance/W2-130` gave 81 passed (47.5 s) and `tests/acceptance/W2-175` gave 51 passed. Both ran through heavy_slot.sh with HOME empty and `-m "not local_only" -k "not real and not green_here and not time_limit"`. The exclusion left out the `local_only` cases and those named real, green_here or time_limit; none of the 81 or 51 was deselected by it in these folders. `--collect-only` collected 81, and all 81 map node ids collect.
discoveries: (1) DAEO-qyt2 was `in_progress` at measured_at and is `closed` at HEAD. This is a real event after the land of the kind F2 of pin run 2 was about, and the pinned case judges it at measured_at (item 4, cm_closed_after). (2) Two W2-130 S7 cases and W2-175's S5 (and S1 to S4) still read the working tree and turn red on ordinary approved events: rows F1 and F2. (3) README line 26 (unchanged by this revision) still says `gov links` runs "on HEAD once, on the starting head once, and on one clone per marks commit". It does not mention the measured_at clone or the propose-sources parents. This is stale timing prose only.
risks: F2 is certain to fire on the next approved delta to any of the seven role templates (DEC-1121's step bumps `version`). F1 fires on the next lesson added. Both give a false red and neither fails open.
lessons: A pin that covers the findings and the tool can still leave a "set equality with the working tree" read behind: a module-level `ROOT` glob (lessons.py:11), or a template read from the working tree. A search for `ROOT /` and working-tree reads finds these where a search for `head_findings` does not.
proposed_decisions: none. F1 and F2 are rows for the CTO. Possible answers: pin S7's two record cases to the lessons commit's tree, or to measured_at, for the set of lessons; pin W2-175 S1 to S5 to `t.LANDING`, as S7 already is.
unresolved: none for this revision.
recommended_next_action: The lead commits this record as `docs/probes/DAEO-q8cl/PR-DAEO-q8cl-pin3.md`. The CTO triages F1 and F2 as rows, or as a ride-along if W2-130 or W2-175 reopen for something else (DEC-802). Then W2-130 can land.

---

Independent auditor, 2026-11-14T09:49:46+00:00, at 17487b4700861003d208de7f256a7d1e479c9562, W2-130 pin run 3 narrow check.

## Item 1: Confined (pass)

- **What changed:** `git diff --name-status aafaf6259d10 17487b470` changes only `tests/acceptance/W2-130/README.md`, `conftest.py`, `test_w2_130_audit.py` and `test_w2_130_sources.py` (47+/26−). No record, ticket, source or other test changed.
- **Merge:** `git diff 83285c3c5 17487b470` is empty, so the merge (parents aafaf6259d10 and 83285c3c5) adds nothing.
- **Trailers:** `git log -1 --format='%(trailers:only,unfold)' 83285c3c5` gives one final paragraph: `Task: DAEO-q8cl`, `Role: independent-test-designer`, `Implements: DEC-1073, DEC-1010`, `Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run 3)`, `Co-Authored-By: …`.
- **README map:** no `|` row changed. Every change is prose, and it states what the code does:
  - Line 60-62: `variant_findings` is "the commit's own tool (its tree's `src`)". This matches conftest.py:91.
  - Lines 79-83: S4's "at HEAD" is re-baselined to `counts-after.measured_at` with that tree's own `gov links`. This matches sources.py:66-69, 194 and 217.
  - Lines 96-101: S8's `left` uses measured_at's own tool, and `counts-before` uses the starting head's own tool. This matches record.py:106-112 and conftest.py:72-75.
  - Lines 102-105: the "Pin run 3" bullet says only S2, S6 and S7's HEAD-wide cases stay on the branch's tool. This matches grep: `head_findings` is used only at marks.py:130, status.py:86 and lessons.py:33.
- **One stale line:** README line 26 (timing prose, untouched here) is discovery (3) above.

## Item 2: S4 pinned (pass)

- **Code:** both cases now take `pinned_findings`, not `head_findings` or `head_tree`.
  - They get `(tree, findings)` from `_pinned` → `pinned_findings(s.measured_at(record))`.
  - `measured_at` checks the full hash, that it is `counts-after.head` or a descendant, and that it is an ancestor of HEAD (support.py:622-636).
  - The findings come from `links_json(tree, home, src=pinned_src(tree))`.
  - Statuses and `sources:` (`_ticket_in(tree, …)`), register headings and ticket stems are all read from that same clone (sources.py:194-204, 217-219).
  - This is the same route as S4's other three cases (sources.py:78, 91, 103).
- **At the audited head:** green (part of the 81 passed).
- **Scratch commit 0ed09f880, on top of 17487b4 in a `git clone --shared`:**
  - It reopens DAEO-0i6h (closed → in_progress; the ticket is listed in closed-missing).
  - It puts DEC-77777 on open DAEO-2keg's `sources:`.
  - It adds CAP-59.a, which closed-missing lists as missing, to closed DAEO-03pw's `sources:`.
- **Result on that commit:**
  - The five S4 cases and S8's three pass at 17487b4's tests.
  - The aafaf6259d10 versions of the two cases, run on the same commit, fail. closed-missing fails with "DAEO-03pw: lists an id its sources: already holds". no-record fails with "gov links reports unknown ids the record does not list per ticket: [('DAEO-2keg', 'DEC-77777')]".

## Item 3: Tool pinned (pass)

- **Code:** conftest.py:88-92 builds a `make_clone` at the commit, writes only the register (`variant_register`), commits, and runs `links_json(tree, home, src=support.pinned_src(tree))`. So `PYTHONPATH=<variant clone>/src`, and that `src` is the marks commit's own.
- **Remaining `gov links` calls:** grep for `links_json` and `run_links` finds four fixtures only:
  - `head_findings`: the branch's tool.
  - `pinned_findings`: pinned.
  - `variant_findings`: pinned.
  - `propose_sources_at`: pinned.
- **Other subprocesses:** the drift and recount scripts run with the HEAD clone's own `src`, or run git only. They do not call `gov links`.
- **My run:** I made a copy of `src` under `$TMPDIR/aud/src_mod` whose `gov links --json` output differs from the real one:
  - It drops the first UNLINKED_ID on DAEO-03dg and the first UNKNOWN_ID on a ticket.
  - It sets `text: true` on every UNMARKED_CHANGE.
  - It adds UNMARKED_CHANGE (DEC-1, DEC-2), UNKNOWN_ID DEC-66666 on DAEO-2keg, UNKNOWN_ID on `docs/lessons/x.md`, a STATUS_CONFLICT, and UNLINKED_ID DEC-5 on DAEO-057v.
  - On the scratch tree it gives 1744 findings with 13 `text: true`, against the branch's 1741 with 6.
- **Results with that copy first on PYTHONPATH:**
  - At 17487b4: 78 passed, 3 failed. Only the HEAD-wide cases failed: `test_w2_130_marks.py::test_s2_gov_links_reports_no_unmarked_change_but_the_eight_pairs_the_auditor_judged_wrong`, `test_w2_130_status.py::test_s6_gov_links_reports_no_status_conflict_at_head` and `test_w2_130_lessons.py::test_s7_gov_links_reports_no_unknown_id_with_a_lesson_s_path`. The S3/F3 cases, the five S4 cases and S8's cases kept the pinned results.
  - At aafaf6259d10, the same copy turned 7 red. Besides those three, it turned red both F3 cases on `variant_findings` and the two S4 cases. So the revision is what holds them.

## Item 4: No case lost its point (pass)

I planted each change in a scratch clone at 17487b4, edited the record in the clone only, and restored it after each run. Each revised case fails and names the disagreement:

| plant | case | failure message |
|---|---|---|
| closed-missing: DEC-862 dropped from DAEO-03dg | closed_missing | "closed-missing differs from gov links' UNLINKED_ID on closed tickets at measured_at" |
| closed-missing: DAEO-2keg (open) listed | closed_missing | "DAEO-2keg is not a closed ticket at measured_at" |
| closed-missing: DAEO-qyt2 listed (closed at HEAD, in_progress at measured_at) | closed_missing | "DAEO-qyt2 is not a closed ticket at measured_at" (this shows the case reads measured_at, not HEAD) |
| no-record: DEC-1156 (a register heading) on DAEO-4k3l | no_record | "DAEO-4k3l: DEC-1156 names a record" |
| no-record: DAEO-03dg (a ticket stem) | no_record | "DAEO-4k3l: DAEO-03dg names a record" |
| no-record: DEC-99998 (not in the ticket's text) | no_record | "is in neither its brackets nor its sources" |
| no-record's unlisted side: commit C = 0bd63accb on measured_at adds DEC-88888 to open DAEO-4k3l, merged into the clone with `-s ours`, `measured_at` set to C | no_record | fails "…at measured_at the record does not list per ticket: [('DAEO-4k3l', 'DEC-88888')]"; with the pair listed it passes |
| F3: free-text mark DEC-261<-DEC-1033 dropped from e12f8a30c's `free_text` | both F3 cases on `variant_findings` | "free-text mark committed unchecked" |
| F3: DEC-421<-DEC-572's verdict set to wrong | F3 every-free-text case | "committed with a verdict of wrong" |

## Item 5: The map still holds (pass)

- `--collect-only` collects 81, and the README map names 81 node ids. Comparing the two lists gives nothing mapped but not collected, and nothing collected but not mapped.
- The `def test_*` names in conftest.py, test_w2_130_audit.py and test_w2_130_sources.py are unchanged from aafaf6259d10. The only rename is the helper `_ticket_at_head` → `_ticket_in`.

## Item 6: Cases a later event still moves (pass, with rows F1 and F2)

**Moved, and that is the case's point (HEAD-wide by the ticket's Verify):**
- S2 `test_s2_gov_links_reports_no_unmarked_change_but_the_eight_pairs_the_auditor_judged_wrong` and `test_s2_the_drift_script_on_head_leaves_no_pair_once_the_listed_pairs_are_set_aside`: moved by a later register entry that changes a decision without a mark, or by a `gov links` change (on purpose).
- S6 `test_s6_gov_links_reports_no_status_conflict_at_head`: moved by a later status that conflicts, or by a `gov links` change.
- S7 `test_s7_gov_links_reports_no_unknown_id_with_a_lesson_s_path` and `test_s7_every_lesson_at_head_has_a_front_matter_sources_key_naming_at_least_one_id`: moved by a lesson without `sources:`, or with an unknown id.
- S1 `test_s1_every_mark_e12f8a30c_appends_is_still_on_its_status_line_at_head` and `test_s1_each_of_the_87_names_every_changer_the_census_states_on_its_own_status_line`, and S2 `test_s2_each_census_id_…`, `test_s2_each_archive_only_pair_…` and `test_s2_the_two_follow_up_marks_…[*]`: moved by a later decision that rewrites a status line and drops its marks.
- S6 `test_s6_linkreconciliation_…` and `test_s6_the_r_12_commit_…` (the R-12 line at HEAD), and F2 `test_f2_the_drift_list_at_head_…`: moved by later edits to LINK-RECONCILIATION.md or DECISIONS-IN-FORCE, or by a later decision that rules a group C, D or E id current.

**Exposures, like F2 of pin run 2:**
- **W2-130:** `test_w2_130_lessons.py::test_s7_the_record_lists_each_lesson_with_its_sources_and_the_place_it_says_it_came_from` (`set(record lessons) == set(lessons at HEAD)`) and `test_w2_130_lessons.py::test_s7_the_lessons_commit_changes_only_lessons_each_by_the_one_added_sources_line` (compares with the module-level `LESSONS`, a working-tree glob, lessons.py:11 and 73). A lesson added after the land moves both.
- **W2-175:** `test_w2_175_templates.py::test_s5_front_matter_is_version_1_0_1_and_otherwise_the_base_s[*]` reads the working-tree templates. The next approved template delta (DEC-1121's version step) moves it. The same working-tree read sits under `test_s1_…[*]`, `test_s2_…`, `test_s3_one_statement_…[*]`, `test_s3_role_cto_keeps_…`, `test_s4_template_holds_…[*]` and `test_f1_…`: an approved rewording moves them.
- **Shown by scratch commits on 17487b4:** aee419908 adds `docs/lessons/L-9999.md` with `sources: [DEC-1073]`, and 4ac99b074 sets role-cto.md to `version: 1.0.2` with one added sentence. The result is 3 failed: the two S7 cases above and `test_s5_…[role-cto]`.

**Stable:** S3/F3, S4, S5, S8, F1 and W2-175's S7 are all pinned to fixed commits, read git at fixed revisions, or read W2-130's own unedited record.

## Findings

**F1: two W2-130 S7 cases compare the record's frozen lesson list with the lessons at HEAD (working tree).**
A lesson added after the land, even a correct one with a `sources:` key, turns `test_s7_the_record_lists_each_lesson_…` and `test_s7_the_lessons_commit_changes_only_lessons_…` red. I showed this with scratch commit aee419908. What would reverse it: a decision that S7's record listing is meant to track every lesson at HEAD for as long as the ticket exists.
Ordinary work: yes, because lessons are added routinely by approved changes (L-0074…L-0076 exist).
Consequence: other (a false red on a closed ticket's suite; it neither fails open nor loses work).
Scope: out (outside this revision; S7 was not touched by pin runs 1 to 3).

**F2: W2-175's S1 to S5 read the role templates in the working tree. S5 asserts `version: 1.0.1`.**
The next approved template delta (DEC-1121 bumps the version) turns `test_s5_…[<stem>]` red, as shown with role-cto at 1.0.2 in scratch commit 4ac99b074. An approved rewording turns S1 to S4 red. What would reverse it: a decision that W2-175's S1 to S5 judge the templates as they are now, rather than at W2-175's landing commit 61cae50dc.
Ordinary work: yes, because template deltas go through CIT-P routinely (b88a76172 already moved role-cto.md and role-lead.md after the close).
Consequence: other (a false red; it neither fails open nor loses work).
Scope: out (W2-175's cases are outside this revision; the CTO's item 6 asked for them).

```verdict
{"head": "17487b4700861003d208de7f256a7d1e479c9562", "date": "2026-11-14T09:49:46+00:00", "kpis": [{"kpi": "1-confined", "verdict": "pass", "findings": []}, {"kpi": "2-s4-pinned", "verdict": "pass", "findings": []}, {"kpi": "3-tool-pinned", "verdict": "pass", "findings": []}, {"kpi": "4-no-case-lost-its-point", "verdict": "pass", "findings": []}, {"kpi": "5-map-holds", "verdict": "pass", "findings": []}, {"kpi": "6-later-events-in-scope", "verdict": "pass", "findings": [{"id": "F1", "scope": "out", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
