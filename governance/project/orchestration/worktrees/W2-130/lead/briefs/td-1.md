# Brief: independent test designer, W2-130 (DAEO-q8cl), run 2 batch 1: the acceptance cases from the re-baselined Verify lines

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read.

## Where you work
| what | path |
|---|---|
| your tree (write here only) | /home/usain/gov-os-worktrees/W2-130-tests |
| branch | w2/W2-130-tests (from 09542040f) |
| your context packet (gov context output, JSON: the ticket, KPIs, sources) | /home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/brief/td-context.md |
| the ticket (read it in your tree) | /home/usain/gov-os-worktrees/W2-130-tests/.tickets/DAEO-q8cl.md |
| the plan | /home/usain/gov-os-worktrees/W2-130-tests/governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md §3 |
| the owner's sitting list | /home/usain/gov-os-worktrees/W2-130-tests/governance/project/orchestration/packages/W2-130-SITTING.md |
| the decision register (grep by id only) | /home/usain/gov-os-worktrees/W2-130-tests/docs/DECISION_REGISTER.md |
| scratch | your sandbox's own `$TMPDIR` only |

Your allowed paths: `tests/acceptance/W2-130/**` only (new). Nothing else.

The implementer (an orchestrator session) works on the same ticket in `/home/usain/gov-os-worktrees/W2-130` at the
same time: never read that tree or its branch's commits after 09542040f (the counterpart's work, DEC-820). History up
to 09542040f is open to you (e12f8a30c, c4420040f and everything before). Write from the KPI lines and the interface.

## What this ticket is
A records clean-up, no code. Most of it was applied on 2026-11-08/09 (e12f8a30c, c4420040f). The CTO re-baselined the
Verify clauses to that history (P-W2-130-1 (a), 617f884f5): each KPI line now ends `[Verify re-baselined to history,
the CTO, P-W2-130-1 (a)]` and its Verify names the existing commits. This run adds follow-ups (listed in the interface)
and the record. Your cases are repository-state cases on this repository (not fixtures): they read HEAD's files, git
history and `gov links --all --json` (about 12 s; run it once per session with a module- or session-scoped fixture,
`python3 -m gov.cli.main links --all --json --root <tree>` with `PYTHONPATH=<tree>/src`, empty `HOME`). The tree under
test is the repository the tests sit in (resolve from `__file__`); never read a store of another tree, never build a
store. Mark the cases as gov accept's `record_reading` kind if W2-129's or another acceptance README shows that form.

## Read first
- The ticket in full: its eleven KPI lines (S1-S8, F1-F4) and their Verify clauses. Those clauses are the spec.
- `tests/acceptance/W2-129/` (README, `conftest.py`, `w2_129_support.py`): the form of a README `gov accept` reads,
  and how gov links is run and its JSON envelope read (`result` -> findings with `code`, `ids`, `path`, `line`, `role`,
  `text`, `mark`).
- `src/gov/links/` (read only) for the finding codes and how a status line, a mark and a ticket's `sources:` are read.
- `docs/research/W2-92-proto-drift.py` (the drift definitions S2 names) and `docs/research/D4B-link-census.py`.
- `git show --stat e12f8a30c c4420040f` and their diffs of `docs/DECISION_REGISTER.md` and `.tickets/`.

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

## The work
1. Write `tests/acceptance/W2-130/` with a README mapping every KPI line (S1-S8, F1-F4) to its cases in `gov accept`'s
   form (as W2-129's README does), a `conftest.py` and a support module (record block parser, gov links fixture, git
   helpers). Cover each Verify clause, at least:
   - S1: every id in `ids-87` (87 of them) has every changer `census` states for it named on its own status line at
     HEAD (`**Changed by:** DEC-n` or `SUPERSEDED by DEC-n`), except pairs in `judged-wrong`; `ids-87` has 87 distinct
     ids, each a key of `census`; e12f8a30c's register hunks are status-line appends only (each removed line an
     existing entry's `- **Status:**` line, the added line that line kept whole as a prefix with only marks appended);
     the marks e12f8a30c appends equal patches a0-a2's marks after `audits[e12f8a30c]`'s drops and rewrites;
     `commits.first_commit` and the parent relation (e12f8a30c^ == 232efc47d); any mark on one of the 87 added after
     e12f8a30c is in a commit of `commits.marks`, append-only.
   - S2: gov links' UNMARKED_CHANGE pairs at HEAD equal exactly the 8 named pairs, each in `judged-wrong` with a verdict;
     DEC-1115's status line names DEC-1122 and DEC-026's names DEC-086, each added by a commit in `commits.marks` after
     e12f8a30c and c4420040f, whose `audits` item has `verdict: right` for that pair, an `audit_head` that is an
     ancestor of the commit and an `audit_date` before the commit's committer date; each of the 215 `census` ids and
     each `archive-13` pair has every stated changer on its own status line unless in `judged-wrong`; `census` has 215
     keys and `archive-13` 13 pairs; the `drift` script, run on HEAD, gives a drift list whose pairs not in
     `judged-wrong`/`drift-run.set_aside` number 0, and `drift-run` records count_after_set_aside 0.
   - S3 and F3: for each commit in `commits.marks` an `audits` item exists, with `audit_head` an ancestor of it and
     `audit_date` before its committer date; e12f8a30c's has `audit_head` 2f9c80b1f…, c4420040f's `ce7f10eb8a2a`…;
     `labelled` has 20 items with a seed, or (seed null) every labelled mark the commit adds; every mark the commit adds
     that gov links flags as derived from free text (`text: true` at the commit's parent, or the audit's `free_text`
     list) appears in `free_text` with `verdict: right`; no committed mark (read from the commit's diff) is one any
     `audits` item judged wrong; `comparison` shows 0/0 for each, and your own comparison agrees.
   - S4: 0 UNLINKED_ID on an open or in-progress ticket at HEAD (status read from each ticket's front matter);
     `commits.sources` is e12f8a30c plus at most one more; in each, every changed ticket line is inside the `sources:`
     field of a ticket open or in progress at the commit's parent, every other field and the body byte-identical; the
     follow-up changes only `.tickets/*.md`; the ids it adds equal `patch-sources-2`'s, and e12f8a30c's equal
     `patch-b1`'s; outside those, a clean-up commit adds to `sources:` only DEC-1098 and DEC-1088 on DAEO-q8cl
     (c4420040f); no clean-up commit changes a ticket closed at its parent; `closed-missing` and `no-record` exist as
     mappings (each value a non-empty list of ids).
   - S5: `trailer-residuals.head` is 232efc47d; each (trailer, value) once; `Task: decision-record` absent; the
     `recount` script run at 232efc47d gives exactly that set of (trailer, value); your own independent count of
     history's trailer values at 232efc47d that name no record (a `Task:` value with no `.tickets/<value>.md` at
     232efc47d, not `decision-record`; an `Implements:` value that is not a list of ids each resolving to a register
     entry, ticket, W2 id or capability) finds no value missing from the set (state your reading in the README); each
     item has `commits`, `tickets` and `should_have_named`; 232efc47d is an ancestor of HEAD.
   - S6 and F2: W2-130-SITTING.md exists in 2f9c80b1f, an ancestor of 232efc47d; LINK-RECONCILIATION.md exists at
     HEAD, names W2-130-SITTING.md and DEC-1098 (3), and carries each sitting row's id with the same proposal and reason;
     9546edd61 is an ancestor of every `commits.status` commit; no clean-up commit without 9546edd61 as ancestor
     changes a register status word or `· done` tag; 0 STATUS_CONFLICT at HEAD; `commits.r12` changes only
     DECISIONS-IN-FORCE.md and its R-12 line no longer reads DEC-896 as in force; the S2 drift list at HEAD holds no
     sitting id that DEC-1098 (3) did not rule current (the 110 spent and 40 PROPOSED ids, read from the sitting file;
     read DEC-1098 (3) in the register for which rulings were "in force").
   - S7: every `docs/lessons/*.md` at HEAD has a front-matter `sources:` naming at least one id; 0 UNKNOWN_ID with a
     lesson's path; `lessons` in the record has one entry per lesson file with the same ids and `agree: true`;
     `commits.lessons` changes only `docs/lessons/*.md`, and each changed file differs from its parent only by the added
     `sources:` line.
   - S8: the record exists with every block named in the interface; `counts-before.head` is 232efc47d,
     `counts-after.head` is the last of `commits.cleanup`; gov links at HEAD gives `counts-after.by_code`; the commits
     lists include e12f8a30c and c4420040f; `left` has keys D-5, D-6 and D-9.
   - F1: in every `commits.cleanup` commit, every changed line of `docs/DECISION_REGISTER.md` is an existing entry's
     status line, either marks appended (old line a prefix) or, in c4420040f only, a status DEC-1098 (3) names for that
     id (the new status word first and the old status text kept in the new line); every ticket file's front matter
     other than `sources:` and its body byte-identical across each commit, except c4420040f's change of DAEO-q8cl's
     KPI 4 line (which then carries `[changed, DEC-1098 (3); DEC-1088 (6)]`); 232efc47d is an ancestor of HEAD.
   - F4: e12f8a30c has 34eed411a and 3679ca0ba as ancestors; the record cites DEC-1097 (9).
2. Run the cases at your branch head (09542040f): history-only cases (e12f8a30c's and c4420040f's diffs, ancestry,
   F4's ancestry) should pass; the cases that need the record, LINK-RECONCILIATION.md, the lessons' `sources:`, the
   two marks, the R-12 rewording or the follow-up sources commit should be red. Record each case's result on the base
   in your return (a short line each, with the red reason). If a history-only case is red at the base, that is a
   finding: report it (the case, the commit, the lines), and do not weaken it.
3. Lower nothing; add no skip, xfail, flaky or rerun mark (a case that cannot run because a block is missing fails, it
   does not skip). Prove two planted breaks are caught, in a scratch copy of the repository under `$TMPDIR` (never in
   your tree's commits): a register status line edited in its middle (not an append) in a scratch commit after
   c4420040f listed as a clean-up commit must fail F1; a record whose `audits` judges one committed mark wrong must fail
   S3/F3. Show both, then discard.
4. Commit, then return.

## How you run tests
Every pytest through the heavy slot, TMPDIR your sandbox's own `$TMPDIR`:
```
env PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-130-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <file or folder>[::<test>] -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
A whole-folder run adds `-m "not local_only" -k "not real and not green_here and not time_limit"`; name no case
`real`, `green_here` or `time_limit` and mark none `local_only`. A resource gate's refusal is a wait (relaunch when it
opens). Quote the count lines in your return.

## Searching
Read and Grep only; no `gov retrieve` or `gov context` in the sandbox. Search once, then once more in other words; answer
from what you read with path and line, or say "not found". Never open the evaluation sets' root, held-out material or any
hidden or memory-verdict folder.

## Forms that work
Write and edit with the Write and Edit tools and absolute paths. Anything longer than one line of shell goes in a script
under your `$TMPDIR`, run with `bash <file>`. Refused twice for the same call by the guard, the sandbox or a hook: stop and
say so; never work around a refusal. No merge, no push.

## Commit (your paths only; one or more commits)
```
git -C /home/usain/gov-os-worktrees/W2-130-tests commit -m "<subject>" --trailer "Task: DAEO-q8cl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1073, DEC-1072, DEC-866, DEC-825, DEC-927, DEC-861, DEC-953, DEC-1010, DEC-1098, DEC-1088" -- tests/acceptance/W2-130
```
Trailers in one final paragraph. Never `Role: owner` or `Decided-by:`. Before you return: tracked `git status --short` empty.

## Return (your last message; the twelve fields, each a labelled line, "none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
Then: commits: <hash12> <subject> | trailers as committed; each case with its result on the base; any place where the
ticket or the interface was unclear and how you read it; guard_refusals: none or a line each.
