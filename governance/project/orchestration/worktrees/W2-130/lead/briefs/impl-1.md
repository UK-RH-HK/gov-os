# Brief: implementer (orchestrator), W2-130 (DAEO-q8cl), run 2: the follow-up commits and the record

You are a fresh orchestrator session working as this ticket's implementer (role orchestrator), ticket DAEO-q8cl
(W2-130), profile STANDARD, class C2. Headless: only your last message is read. You launch no worker, merge nothing
and push nothing.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-130 |
| branch | w2/W2-130 (head 94baaafa8, the acceptance tests merged) |
| your context packet (gov context output, JSON) | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/briefs/ctx-orchestrator.md |
| the ticket | /home/usain/gov-os-worktrees/W2-130/.tickets/DAEO-q8cl.md (read it in full: S1-S8, F1-F4 and their Verify clauses) |
| the acceptance tests (the independent test designer's; never edit them) | /home/usain/gov-os-worktrees/W2-130/tests/acceptance/W2-130/ (README first) |
| the earlier run's drafts and scripts (copies) | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/ref/drafts/ (README.md, residuals.py, findings.py, build_patches.py, final_build.py, patches a0-a3, b1, b2, marks-audit.md with the 20 drawn labelled marks and their seed, c-trailer-residuals.md, e-spurious-changers.md) |
| the earlier independent audits | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/ref/w2-130-marks.md (part 1 at 2f9c80b1f for e12f8a30c; part 2 "Final patches", at ce7f10eb8a2a, for c4420040f), ref/readiness-2-links.md, ref/e-spurious-changers.md |
| this run's marks audit (fresh independent auditor, before your marks commit) | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/aud-marks-1-return.md |
| the census (lead's run of docs/research/D4B-link-census.py at 3d1c459e on 24f06026) | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/census-m6.json, census-87.txt, census-3d1c.py, check87.py |
| gov links at the start of this run | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/lead/links-all-0954.json |
| scratch | /home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/impl/ (scripts, outputs), TMPDIR your sandbox's own `$TMPDIR` |

Allowed paths: docs/DECISION_REGISTER.md, governance/project/orchestration/ARCHIVE-SUPERSEDED.md,
governance/project/orchestration/DECISIONS-IN-FORCE.md,
governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md, .tickets/*.md, docs/lessons/*.md,
docs/research/W2-130-link-cleanup.md. Nothing else (never tests/, src/, the sitting file, the census script).

## What this is
A records clean-up, no code. Most was applied on 2026-11-08/09: e12f8a30c (marks a0-a2, sources b1) and c4420040f
(the owner's sitting rulings DEC-1098 (3), marks a3, this ticket's KPI 4). The CTO re-baselined the Verify clauses to
that history (P-W2-130-1 (a), -2 (a), -3 (a)). You make the follow-ups and write the record. The register holds the
owner's decisions: a mark changes no decision's meaning; any finding that would need an entry's text changed (other than
its status marks) is not yours to make: stop and report it in `unresolved`.

## The interface (the lead's decisions where the ticket is silent; the same text goes to the test designer and the implementer)

The ticket fixes the paths and what each holds. The lead fixes the layout here so cases can read it.

### Fixed facts (full hashes are resolved with `git rev-parse`; abbreviations below are unique in this repository)
- Clean-up starting head: `232efc47d` (e12f8a30c's parent). The merge that brought the re-baselined ticket: `09542040f`.
- Clean-up commits already in history: `e12f8a30c` (batches a0, a1, a2 and b1: the 87's marks, the rest's marks, the
  archive one-per-line change, the open tickets' sources) and `c4420040f` (after the owner's sitting, DEC-1098 (3):
  status words, the a3 marks, this ticket's KPI 4 line and its sources DEC-1098 and DEC-1088).
- Owner decisions: DEC-1097 (9) allowed the start; DEC-1098 (3) (committed in `9546edd61`) ruled the sitting list
  `governance/project/orchestration/packages/W2-130-SITTING.md` (committed in `2f9c80b1f`).
- W2-129's landing: merge `34eed411a`; W2-92's stated links adopted: merge `3679ca0ba`.
- The earlier independent audit: `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-130-marks.md`
  (at `2f9c80b1f`, for e12f8a30c) and its second part for c4420040f (at `ce7f10eb8a2a`). The record copies what it
  needs from it; cases read only the record and git, never that scratch file.
- This run's follow-up commits (made after the tests are merged): (1) a sources commit (only `sources:` lines of open
  or in-progress tickets, only `.tickets/*.md`, the ids `gov links --propose-sources` gives at its parent); (2) the
  R-12 rewording in `DECISIONS-IN-FORCE.md`; (3) the lessons' `sources:` keys; (4) a marks commit adding exactly
  `**Changed by:** DEC-1122 (4)` to DEC-1115's status line and `**Changed by:** DEC-086` to DEC-026's (status-line
  appends only), after a fresh independent auditor's check; (5) the record and LINK-RECONCILIATION.md, last.
  Each of (1)-(4) is its own commit and changes no other file.

### The record: `docs/research/W2-130-link-cleanup.md`
Prose for a reader, plus machine-readable fenced blocks. Each block opens with a line of exactly
```` ```<lang> w2-130:<name> ```` and closes with ```` ``` ````; `<lang>` is `yaml`, `diff` or `python`. Each name
appears once. Every commit is a full 40-hex hash in the blocks. Ids are `DEC-n` with the register's zero padding.
A pair is written `DEC-a<-DEC-b` (changed <- changer) in prose; in YAML it is `{changed: DEC-a, changer: DEC-b}`.

- `yaml w2-130:commits` — a mapping:
  `starting_head`, `first_commit` (e12f8a30c), `w2_129_landing`, `w2_92_adoption`, `start_decision: "DEC-1097 (9)"`,
  `status_decision: "DEC-1098 (3)"`, `status_decision_commit` (9546edd61), `sitting_commit` (2f9c80b1f);
  `cleanup:` the list of every clean-up commit in order (e12f8a30c, c4420040f, then follow-ups (1)-(4)); and the
  lists `marks:` (e12f8a30c, c4420040f, follow-up (4)), `sources:` (e12f8a30c, follow-up (1)), `status:`
  (c4420040f, follow-up (2)), and the single hashes `r12:` (2) and `lessons:` (3). The record's own commit(s) are not
  in these lists; they change only the record and LINK-RECONCILIATION.md.
- `yaml w2-130:ids-87` — a list of the 87 ids (the census's script at 3d1c459e on 24f06026).
- `yaml w2-130:census` — a mapping, one key per each of the census's 215 drifting ids, value the list of changers the
  census states for it (`DEC-1115: [DEC-1122]`).
- `yaml w2-130:archive-13` — a list of the 13 pairs stated only in ARCHIVE-SUPERSEDED §A.
- `yaml w2-130:judged-wrong` — a list of every pair left unmarked because the earlier independent auditor judged it
  wrong: `{changed, changer, verdict: "<the auditor's words, quoted>", finding: "<its finding id, e.g. F1>",
  in_gov_links: true|false}`. It holds exactly the 8 pairs gov links reports (DEC-853<-DEC-884, DEC-1050<-DEC-1057,
  DEC-120<-DEC-173, DEC-724<-DEC-860, DEC-056<-DEC-017, DEC-072<-DEC-064, DEC-162<-DEC-156, DEC-1053<-DEC-880, each
  `in_gov_links: true`) plus each census pair not on its status line that the auditor judged wrong
  (`in_gov_links: false`).
- `yaml w2-130:audits` — a list, one item per marks commit (each hash in `commits.marks`):
  `{commit, audit_head, audit_date: "<ISO 8601 with time and zone>", audit_source: "<where the check is recorded>",
  seed: <int or null>, free_text: [<mark>...], labelled: [<mark>...]}` where `<mark>` is
  `{changed, changer, mark: "<the mark text gov links proposed>", verdict: right|wrong, fate: committed|dropped|corrected,
  committed_mark: "<text committed, when fate is committed or corrected>"}`. `labelled` holds the 20 drawn by `seed`,
  or every labelled mark when the commit adds 20 or fewer (then `seed: null`).
- `yaml w2-130:comparison` — a mapping commit -> `{unchecked: <int>, wrong: <int>}`, from comparing each marks commit's
  diff with `audits`.
- `diff w2-130:patch-a0`, `diff w2-130:patch-a1`, `diff w2-130:patch-a2`, `diff w2-130:patch-b1` — the patches
  e12f8a30c applied, byte for byte as gov links (or the drafts' builder) printed them, before the auditor's drops and
  rewrites; `diff w2-130:patch-sources-2` — the open and in-progress tickets' file sections of `gov links --propose-sources` at follow-up (1)'s parent, byte for byte (as b1 was e12f8a30c's; the closed tickets' sections are not applied, their ids go to `closed-missing`);
  `diff w2-130:patch-marks-3` — `gov links --propose-marks` at follow-up (4)'s parent (all of it; the two applied
  marks are among its hunks; the 8 judged-wrong ones are not applied).
- `yaml w2-130:trailer-residuals` — `{head: <232efc47d full>, values: [{trailer: Task|Implements, value: "<the value as
  written>", commits: [<full>...], tickets: [<ticket id or W2 id or null>...], should_have_named: [<ids>] or "<text>"}]}`;
  each (trailer, value) once. `Task: decision-record` is not listed (valid under DEC-861).
- `python w2-130:recount` — a self-contained Python 3 script (standard library and git only) that, run as
  `python3 - <rev>` with stdin the script and cwd the repository, prints one JSON list of `{trailer, value}` for every
  trailer value in `git log <rev>`'s history that names no record. Run at 232efc47d it gives exactly the set in
  `trailer-residuals`.
- `python w2-130:drift` — a self-contained Python 3 script that applies docs/research/W2-92-proto-drift.py's
  definitions to `docs/DECISION_REGISTER.md` and `governance/project/orchestration/ARCHIVE-SUPERSEDED.md` as read
  from the working tree (the entries' own text, no store), run as `python3 -` with cwd the repository, and prints one
  JSON object `{"drift": [{changed, changer}...], "count": <int>}`. `yaml w2-130:drift-run` holds
  `{head, command, output: <that JSON object>, set_aside: [<pairs>], count_after_set_aside: 0}`.
- `yaml w2-130:counts-before` and `yaml w2-130:counts-after` — `{head, command: "gov links --all --json ...",
  by_code: {CODE: n}, by_code_role: {CODE: {role: n}}, unlinked_by_status: {open: n, in_progress: n, closed: n, ...}}`;
  before at 232efc47d, after at the last clean-up commit (follow-up (4)); a re-run at the record's commit gives the
  same `by_code`.
- `yaml w2-130:closed-missing` — mapping closed ticket id -> list of ids its KPI brackets or worker commits name that
  its `sources:` lacks (from gov links --all's UNLINKED_ID on closed tickets at the last clean-up commit).
- `yaml w2-130:no-record` — mapping ticket id -> list of ids in its brackets or sources that name no record (for D-9).
- `yaml w2-130:lessons` — mapping lesson id (L-0074 ...) -> `{sources: [ids], came_from: "<the lesson's own words
  naming its decision or failure>", agree: true}`.
- `yaml w2-130:left` — `{D-5: {<path>: {<role>: n}}, D-6: {...}, D-9: {...}}`, the findings left at the last
  clean-up commit by path and role.

### LINK-RECONCILIATION.md (`governance/project/orchestration/packages/LIFT-1/LINK-RECONCILIATION.md`)
Names `governance/project/orchestration/packages/W2-130-SITTING.md` as the list the owner ruled on and DEC-1098 (3).
Carries one markdown table row per sitting row: `| <DEC-id> | <group letter> | <proposal> | <reason> | <ruling> |`,
where `<proposal>` and `<reason>` are the sitting row's proposal column (without `**`) and reason column, verbatim.

### Lessons
Each `docs/lessons/*.md` gets one front-matter line `sources: [<ids>]` (ids that gov links resolves: `DEC-n`,
`L-nnnn`, a ticket id or a W2 id), added before the closing `---`; no other byte of the file changes.

### R-12
DECISIONS-IN-FORCE.md's R-12 line is reworded so it does not list DEC-896 as in force (for example "lifting item 2
of the done DEC-896" written so gov links reads no in-force claim); gov links --all then reports no STATUS_CONFLICT.

## Notes from the test designer's return (read its README for the rest)
- `gov links` reads the ids of a DECISIONS-IN-FORCE line only before its first `:`; a reword that keeps DEC-896 before
  the colon (even as "the done DEC-896") still gives STATUS_CONFLICT.
- `--propose-sources` rewrites a flow-style `sources: [...]` line whole.
- Pairs the earlier audit dropped through the archive rewrite (for example DEC-038<-DEC-051 and DEC-045<-DEC-053, from
  part 2's f2 chain lines) are not on their status lines: if the census or `archive-13` holds them they go in
  `judged-wrong` (`in_gov_links: false`) with part 2's words. A pair with no independent auditor's verdict anywhere is
  a finding for `unresolved` (the lead then has it checked); never fill a verdict yourself.
- The cases read `left` strictly (all findings under each prefix at the head, all codes); the README states the
  prefixes and the sitting row "reason" column it reads.

## The work, in this order (each numbered commit its own, changing only what it names; this run commits (2), (3) and (4) only)
0. Read the ticket, the interface above and `tests/acceptance/W2-130/README.md`. Run the acceptance folder once at
   the start and keep its result (it is red where the follow-ups and the record are missing).
1. **Sources commit (follow-up (1)): HELD, make no sources commit in this run.** 62 of the 102 UNLINKED_ID on open or
   in-progress tickets are ids that commit 66303c373 removed from `sources:` under the owner's DEC-1123 (2) (backlog
   rows moved to `list_rows`, WBS ids replaced by their ticket's id, DEC-798 re-pointed to DEC-1033); re-adding them
   would reverse an owner decision, so the lead takes it to the CTO as a package. Prepare only, in your scratch:
   `propose-sources-full.patch` (gov links --all --propose-sources at HEAD), and `sources-split.md`: each UNLINKED_ID on
   an open or in-progress ticket classed as (i) an id DEC-1123 (2)'s forms cover (a backlog row in the ticket's
   `list_rows`; a WBS id whose ticket id is in `sources:`; DEC-798), (ii) the same forms on a ticket 66303c373 did not
   touch, (iii) the rest (DEC ids, CAP ids, others), with counts. The lead's first cut is in
   `.gov-runtime/scratch/lead/split102.py`.
2. **R-12 (follow-up (2)).** In DECISIONS-IN-FORCE.md, reword only the R-12 line (P-W2-130-3 (a)) so it does not read
   as listing DEC-896 in force, keeping its meaning (R-12 comes from DEC-1057, which lifted DEC-896 item 2 and DEC-927
   item 2). Read `src/gov/links/` to see how a STATUS_CONFLICT on that file is found, so the new line is read right.
   gov links --all then reports 0 STATUS_CONFLICT. Commit only that file.
3. **Lessons (follow-up (3)).** For each `docs/lessons/*.md`, read its text and find the decision or failure it says it
   came from; add one front-matter line `sources: [<ids>]` before the closing `---` (ids gov links resolves); no
   other byte changes. gov links --all then reports no UNKNOWN_ID on a lesson. Commit only those files.
4. **Marks (follow-up (4)).** Read this run's marks audit (path above). Only for a mark it judges `right`, append
   its `commit_as` text exactly as the verdict block gives it (it starts with ` · **Changed by:**`) to the end of that entry's `- **Status:**` line (DEC-1115 <- DEC-1122 (4),
   DEC-026 <- DEC-086): an append only, the old line kept whole. Save `gov links --all --propose-marks` at this
   commit's parent as `.gov-runtime/scratch/impl/patch-marks-3.patch` first. Commit only the register. If the audit
   judges either mark wrong, or judges any pair it was asked about "should be marked", do not commit (4): stop after
   (3), write what you have of the record uncommitted under your scratch, and report it in `unresolved`.
5. **The record and LINK-RECONCILIATION.md: DRAFT ONLY in this run, uncommitted, under `.gov-runtime/scratch/impl/record/` (the two files at their final relative paths there), complete except what needs the sources commit (its hash, `patch-sources-2`, `counts-after`, `left`, `closed-missing` at the last clean-up commit: fill them from the current head and mark each such value in a list at the top of `.gov-runtime/scratch/impl/record/TODO.md`), with a script `.gov-runtime/scratch/impl/build_record.py` that regenerates every block from the repository so the resume only re-runs it.** Build it this way: Build every block of
   the interface from the sources above, by script (keep the scripts in your scratch; the `recount` and `drift` blocks
   are self-contained scripts that the cases run). In particular:
   - `audits`: e12f8a30c from part 1 of the earlier audit (19 free-text marks judged by hand, the worksheet's 20
     labelled marks with its seed, the 12 wrong marks' fates and the rewrites); c4420040f from part 2 (its free-text
     marks, the labelled marks: every one if 20 or fewer, else 20 drawn by a seed you state and compute; F14's drop);
     follow-up (4) from this run's audit (both labelled marks, `seed: null`). Copy each auditor's words; never judge a
     mark yourself in the auditor's place. If a mark a commit added has no verdict in its audit, that is a finding:
     report it, do not invent a verdict.
   - `judged-wrong`: the 8 gov links pairs and every census pair not on its status line, each with the verdict and
     finding id of the auditor who judged it (this run's audit covers all of them; cite it, and the earlier one where it
     agrees).
   - `trailer-residuals` and `recount`: at 232efc47d (not HEAD); `residuals.py` is the earlier reading; the census's
     totals are in the ticket's S5 line. Explain in prose any difference from the census's counts.
   - `counts-before` at 232efc47d: run gov links from a detached copy of that commit (`git worktree add --detach` under
     your scratch, with that commit's own `src/`), then remove the worktree; `counts-after` at follow-up (4).
   - `drift-run`: run the `drift` block's script at follow-up (4); its output; the pairs set aside are exactly
     `judged-wrong`'s.
   - LINK-RECONCILIATION.md from W2-130-SITTING.md's rows (with each row's ruling from DEC-1098 (3)).
   - The prose: what was done and when, F4's order (e12f8a30c after 34eed411a and 3679ca0ba; DEC-1097 (9)), and the
     findings left by path and role for D-5, D-6 and D-9.
   Do not commit the draft. To try it against the cases, copy the two files into the tree, run the acceptance folder,
   and remove them again (`git status --short` empty afterwards); report the result.
6. Run the acceptance folder (below) at your last commit (and once with the draft copied in, as above). Every case
   green except those that need the sources commit is the goal. A red you cannot fix in your paths, or one that
   looks like a case reading the Verify differently from you, goes in `unresolved` with the case, its message and
   your reading; never edit the tests.

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-130/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-130/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-130 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"
```
A resource gate's refusal is a wait (re-run when it opens). Quote the count lines in your return.

## Searching
Read and Grep only (grep the register by id only); no `gov retrieve` or `gov context` in the sandbox. Search once, then
once more in other words; answer from what you read with path and line, or say "not found". Never open the evaluation
sets' root, held-out material or any hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a
script under `.gov-runtime/scratch/impl/`, run with `bash <file>` or `python3 <file>`. Literal paths as write targets.
Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.

## Commit (your paths only)
```
git commit -m "<subject>" --trailer "Task: DAEO-q8cl" --trailer "Role: orchestrator" --trailer "Implements: DEC-1073, DEC-1072, DEC-866, DEC-825, DEC-927, DEC-861, DEC-953, DEC-1010, DEC-1098, DEC-1088" -- <paths>
```
Trailers in one final paragraph (no blank line inside it). `Implements:` only ids from the ticket's `sources:`. Never
`Role: owner` or `Decided-by:`. Subject: `W2-130 follow-up (<n>): <what>`. Before you return: tracked
`git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed (one line each); gov links --all by_code before (09542040f's
is in links-all-0954.json) and after; the acceptance count line; guard_refusals: none or a line each.
