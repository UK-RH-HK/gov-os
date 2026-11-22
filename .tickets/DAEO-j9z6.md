---
id: DAEO-j9z6
status: closed
deps: [DAEO-emq1]
links: [DAEO-emq1]
created: 2026-11-11T23:59:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-115b
tags: [close, queue, full, emergency-2]
wbs_id: W2-115b
title: 'gov queue, the product''s deterministic landing: a thin queue on the close''s pieces (EMERGENCY-2 4.3 step 3)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-emq1]
waits_on: []
closes:
- CAP-23.c
- CAP-39.c
- CAP-63.a
- CAP-63.b
- CAP-63.d
allowed_paths:
- src/gov/queue/**
- src/gov/close/select.py
- src/gov/close/batch.py
- tests/unit/queue/**
- tests/acceptance/W2-115b/**
- .tickets/DAEO-j9z6.md
- governance/project/facts.yaml
- src/gov/adopt/facts.py
- template/governance/kernel/templates/**
- .claude/templates/**
- src/gov/_shipped/template/governance/kernel/templates/**
- template/.rulesync/subagents/**
- .rulesync/subagents/**
- .claude/agents/**
est_loc: 480
kpis:
  success:
  - '`gov queue <ticket>[=<branch>] ... [--onto <branch>]` merges each ticket''s branch (`--no-ff`) onto the integration branch''s head in the warm clone, runs one impact-selected run on the merged result (the union of the candidates'' `select.scoped` selections, the change counted as the branch''s own commits since the integration head as well as the ticket''s), and on green moves the integration branch from that head to the tested merge with one close commit per landed ticket on top of it Verify: a planted repository, one ticket whose change is green: afterwards the integration branch''s head reaches the recorded tested merge through close commits only (each changing only that ticket''s ticket file, `docs/close/<id>/` and `docs/checkpoints/<id>/`); the tested merge''s parents are the old head and the branch''s tip; the run''s JUnit holds the ticket''s own suite and a suite that imports the changed module, and no suite the change reaches by nothing; the root''s working tree follows the branch where it is checked out there. [EMERGENCY-2 4.3 step 3; audit 1 §4; DEC-959 item 1, DEC-983]'
  - 'The ticket closes at the land: each landed ticket''s close record `docs/close/<id>/CL-<id>.md` (`close: queue`, the tested merge as `commit`, the selection, the runs'' counts, every red with its verdict, the culprits, the base, the queue''s record) is written and its status is `closed` in the same landing, with no test run of its own Verify: a planted green landing: the ticket''s close record holds those keys, `commit` equals the tested merge and `runs` the queue run''s counts, its `queue` key names the queue''s record, the ticket''s status at the new head is `closed`, and the planted tests'' run log shows only the queue''s run. [EMERGENCY-2 4.3 step 5; DEC-989]'
  - 'On red the failing tests are named and nothing moves: a ticket whose change turns a test red is not landed; the answer names each failing test''s node id and the ticket as the culprit, and the integration branch, the ticket''s branch and the ticket''s status are as they were Verify: a planted ticket that breaks a reached test: exit 3; the answer names the failing node id and the ticket among the culprits; the integration branch, the work branch and the ticket file are unchanged. [EMERGENCY-2 4.3 steps 3 and 4; W2-115 attribution]'
  - 'A red batch''s culprit is sent back and the rest land: of two tickets, the one whose change is red is not landed and stays open, named with its failing test; the other is landed and closed on the merged result without the culprit, run again there Verify: a planted batch of two tickets, one red: the culprit''s branch is not an ancestor of the new head and its status is open; the other''s branch is, its status is `closed`, its close record names the culprit and its `commit` is the merge without the culprit; exit 3. [DEC-959 item 1, DEC-982, W2-115 S6]'
  - 'Who wrote the acceptance tests is checked by code (G-1): a ticket whose branch holds a commit that changes `tests/acceptance/` or the ticket''s `acceptance_tests.path` without every `Role:` trailer of it being `independent-test-designer` or `owner` is refused before the run (`TEST_AUTHOR_REFUSED`, the commit''s id named) and not landed; a merge commit counts only where its result there differs from git''s own merge of its parents Verify: planted branches: an engineer-role commit to `tests/acceptance/` refused with its id named and nothing of it landed, the rest of the batch landing; a test designer''s or owner''s commit landing; a clean merge of the test designer''s branch landing; a merge that edits an acceptance test in its resolution refused. [MR-3 as audit 7 rewrites it; DEC-1050 (12); land.py G-1]'
  - 'Paths outside the ticket''s allowed paths are a notice, never a refusal: each commit''s path outside the ticket''s `allowed_paths` (read at the branch''s tip) and outside its own record places is listed under `path_notices` with the commit''s id, and the ticket lands Verify: a planted ticket with a commit outside its allowed paths: it lands and closes; the answer and its close record list that path and commit under `path_notices`; a path inside them is not listed. [audit 7 C-6, CAP-58.h as rewritten]'
  - 'Nothing project-specific: the integration branch and the work branch''s form come from `--onto` and `<ticket>=<branch>`, else from `governance/project/queue.yaml` (`integration`, `work_branch` with `{wbs}` and `{ticket}`), else the integration branch is the one checked out at the root; with neither the queue refuses before anything (`INTEGRATION_UNKNOWN`, `BRANCH_UNKNOWN`, exit 1) Verify: grep of `src/gov/queue/` for `w2/`, `integrate`, `DAEO-`, `/home/` finds 0 lines; a planted repository on `main` with branches `feature/<wbs>` named in `queue.yaml` lands with the same code; a planted repository with neither setting nor branch is refused with each code and changes nothing. [DEC-983, DEC-982; audit 1 §4 row 2]'
  - 'Minutes, measured: the answer and the queue''s record (`.gov-runtime/queue/<stamp>/queue.json`) state the seconds of each step (merge, selection, run, close) and the total Verify: a planted landing: the record exists at that place, holds the same result as the answer, and each of the five figures is a number of seconds, none negative, the total not less than any step. [EMERGENCY-2 4.3 step 3 "in minutes"; audit 1 §4 Time]'
  - 'DONE is the green landing itself (audit 1 question 2 (b)): the Definition of Done is three lines, acceptance green (`gov accept`), the landing''s checks green (`gov queue`: the run on the merged result green, the acceptance tests'' authors checked) and the close written at the land; DOD-4 (the FULL review) and DOD-6 (the return''s fields and guard_refusals) are gone from the facts files (the project''s and the default `gov adopt` writes), the ticket template''s `done_when`, the lead template and every generated copy Verify: `governance/project/facts.yaml`''s `dod` and the facts `gov adopt` writes in a planted repository each hold exactly DOD-1, DOD-2 and DOD-3, whose lines name `gov accept` (or its command key), `gov queue` and the close; no kernel template, `.claude/templates/` copy, `src/gov/_shipped/` copy, `.rulesync/` source or `.claude/agents/` file quotes DOD-4, DOD-5, DOD-6 or "DOD-1 to DOD-6"; the ticket template''s `done_when` is `[DOD-1, DOD-2, DOD-3]`; each `.claude/templates/` copy equals its kernel template byte for byte. [EMERGENCY-2 4.3 step 5; audit 1 §2 and question 2 (b); the owner''s working assumption of 2026-11-17, approved kernel text by the CTO''s message (3.5)]'
  - 'Fix, the base'' unplaced paths (L2-4): with `change` given, a path counted from the green record that neither the ticket''s own commits nor `change` wrote, and that nothing places, is not refused: `select.scoped` lists it under `unplaced_base` (always present when `change` is given; the object `gov queue <T>=<branch> --select` prints holds it) and the landing goes on Verify: a planted project with a green record and, after it, two commits on the base that no ticket made (a document outside `record_only`, a shell script) beside a branch that changes mapped code: `--select` exits 0 with both under `unplaced_base` and the ticket''s own suite selected, and a landing of it lands and closes. [L2-4; DEC-1217 (1); EMERGENCY-2 3.2]'
  - 'Fix, the landing''s own unplaced path is still refused: a path the branch itself wrote (the ticket''s own commits or `change`) that nothing places is refused `SELECTION_REFUSED` (exit 2 for `--select`), the reason naming it and none of the base''s paths Verify: the same project with the branch also writing `tools/stray.sh`: the refusal names `tools/stray.sh` and neither base-side path. [L2-4]'
  - 'Fix, a base-side path that is placed still selects: a path counted from the green record that nothing of the landing wrote but a test imports (or a coupling or a ticket''s allowed paths holds) selects that suite and is not under `unplaced_base` Verify: a base commit changing a module a test imports: that test is in the selection. [L2-4]'
  - 'Fix, `gov close` is unchanged: without `change`, a path counted from the green record that nothing places is refused as before Verify: `gov close --select <T>` in the same project: `SELECTION_REFUSED`, exit 2, naming the base''s paths. [L2-4; W2-115 S2]'
  - 'Fix, adopted repositories land (D7, DEC-1227): a repository adopted with `gov adopt --lite` lands a ticket through `gov queue` with the stage commits in the branch''s range. The stage commits carry no `Role` or `Task` trailer by design (W1-41; `governance/project/bootstrap.md`, "The adoption''s commits"), and the landing asks none of them: no trailer check, no marker Verify: a planted project (the adoption ticket''s `allowed_paths` hold `governance/adoption/**`, `.gitleaks.toml` and `.gitignore`) whose branch holds `gov adopt --lite` stages A0, A1 and A2 as committed by the tool, then one feature commit with `Task:` and `Role: engineer`: every stage commit has no `Role` and no `Task` trailer, and `gov queue <T>=<branch>` exits 0, lands and closes the ticket, `refused` and `culprits` empty. [DEC-1227 D7; CAP-58.h, CAP-63.a, CAP-63.d]'
  - 'Fix, what the stage commits write outside the ticket''s places is named, not refused: the coordination ticket A0 files and the roster it writes are notices (`path_notices`, `ticket_notices`) in the answer of the same landing, exit 0 Verify: the run of the line above: `path_notices` names a path of A0''s commit, and the exit is 0. [DEC-1227 D7; audit 7 C-6]'
  - 'Fix, a hand edit of a stage record is still caught, by `gov adopt` and not by trailers: a stage record changed by a commit that is not the tool''s (even with `Role: orchestrator` and a `Task:`) is refused by the next stage as `ADOPT_CHAIN_BROKEN`, naming the record that no longer stands, and nothing is committed Verify: the same planted project: a committed hand edit of `governance/adoption/A1-inventory.md`, then `gov adopt --lite --stage AS`: non-zero exit, `ADOPT_CHAIN_BROKEN` naming `A2-classification.md`, HEAD unchanged. [DEC-1227 D7; W1-41]'
  - 'Fix, a test file the change deleted is no selected target (I-1): a path the change deleted since the last green record (absent from the tree at HEAD) is never selected as `TEST_CHANGED`; `select.scoped` lists it under `deleted` (always present when `change` is given; in the object `gov queue <T>=<branch> --select` prints) and its suite folder still runs where the folder remains Verify: a planted project with a green record, A\'s branch deleting one test file of a suite folder that keeps other test files, and changing mapped code: `--select` exits 0, `deleted` names the file, the file is in no `suites` entry and the remaining suite folder is selected; the landing lands and closes. [FINDINGS I-1; DEC-1239 (1)]'
  - 'Fix, a map-named target that is gone still refuses (I-1, DEC-912 item 3): a target the test map names (coupling suites, `every_close`, `record_reading`) that the head does not hold is refused `SELECTION_REFUSED` naming it with `FILE_GONE`, as before Verify: a planted project whose coupling names a test file the branch deletes and whose changed path triggers that coupling: `--select` exit 2 naming the file and `FILE_GONE`. [DEC-912 item 3]'
  - 'Fix, a record-only document the branch writes is placed with a notice (I-2): a Markdown document the branch writes outside `src/`, `tests/`, `template/`, `governance/kernel/`, `.claude/` and `.rulesync/`, that no suite, coupling or ticket places, is placed as a record: it is listed under `records` and a notice `RECORD_PLACED <path>` under `notices` in the `--select` object, in the landing\'s answer and in the queue\'s record, and the landing goes on; the paths the test map\'s `record_only` patterns cover are records as before Verify: a planted project whose branch writes `docs/x.md` beside mapped code: `--select` exit 0, `records` holds `docs/x.md`, `notices` holds `RECORD_PLACED docs/x.md`; the landing lands and closes with the notice in its answer and the queue record. [FINDINGS I-2; DEC-1239 (2)]'
  - 'Fix, code the branch writes that nothing places still refuses (I-2): an unplaced path that is not a record-only document (a shell script, a Python file outside any suite, a Markdown file under `src/` or `template/`) is refused `SELECTION_REFUSED` naming it, as before Verify: the branch writing `tools/stray.sh` beside `docs/x.md`: exit 2 naming `tools/stray.sh` and not `docs/x.md`. [L2-4; DEC-1239 (2)]'
  failure:
  - 'The integration branch advanced after a red, after a refusal, or to anything but the tested merge with its close commits; or advanced from a head other than the one the run merged onto. Verify: planted runs that are red, red on the base too (`BATCH_UNEXPLAINED`), refused by G-1, and one where the integration branch moves during the run (`HEAD_MOVED`, exit 3): the branch is not moved by the queue in any of them (the moved head stays as it was moved).'
  - 'A ticket merged and not closed, or closed and not merged. Verify: after every planted run, each planted ticket''s status at the integration head is `closed` exactly when its branch''s tip is an ancestor of that head.'
  - 'A path the landing wrote that nothing places is no longer refused, or, without `change`, the base''s unmapped path stops being refused Verify: the two cases of success lines 11 and 13 above.'
  - 'A commit whose subject is a stage commit''s and that changes the acceptance tests is let through for it Verify: a branch commit with the subject `gov adopt --lite A0: safety baseline`, no `Role` trailer, that adds a file under `tests/acceptance/`: `gov queue` refuses it `TEST_AUTHOR_REFUSED` naming the commit, nothing lands. [DEC-1227 D7; MR-3, CAP-58.h]'
non_goals:
- the close itself (W2-115), its strict mode, W2-193 and W2-194
- Gov OS's own landing tools (land.py, merge_queue.py, landing_select.sh) and the switch-over to gov queue (the CTO's, later)
- merge_queue.py's speed-ups (records-only head moves, store seeding and promotion, the identical-code skip), until friction asks for them
- the run of a direct commit (a chore) through the queue
- languages other than Python (W2-19)
done_when: [DOD-1, DOD-2, DOD-3]
sources: [EMERGENCY-2, DEC-983, DEC-982, DEC-959, DEC-989, DEC-1050, DEC-1083, DEC-1201, CAP-33, DAEO-zkr9]
acceptance_tests:
  path: tests/acceptance/W2-115b/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-115b gov queue, the product's merge queue

Split from W2-115 (DAEO-emq1) by the CTO's delegated decision on its run 1's P1 (b), 2026-11-11: the six queue success
lines and two failure lines moved here word for word, with W2-97's queue (`governance/project/orchestration/tools/merge_queue.py`)
as the reference. Runs after W2-115 (the close it lands through). Class C3 (the landing path).

## Parked (the owner, DEC-1142 (8), 2026-11-12 ~09:50)

Parked in docs/plan/WAVE_3_PARKING.md as W3-P32: filed or split by the CTO without the owner's P1 (DEC-974; the prompt's §3). Not started again in Wave 2 without the owner's decision.

**Moved to Wave 3's list 2026-11-16 by the owner (DEC-1201 (3)):** W2-115b leaves Wave 2's list (status `deferred`, tag `wave-2` removed); it is not closed and not done. It is listed in `docs/plan/WAVE_3_PARKING.md` under "Moved from Wave 2 (DEC-1201)". `gov plan` no longer offers it.


## Rewritten for Emergency 2 (the CTO's brief, 2026-11-17)

EMERGENCY-2 §6.2 A-4 moves W2-115b back to the release ("the landing must exist in adopted repositories"); §4.3 step 3
is the deterministic landing it builds. The CTO's decision on audit 1's question 1 is option (b), a thin queue on the
product's existing pieces (`batch.isolate`, `select.scoped`, the close's record and `tk close`), about 300 to 500
lines, not a port of Gov OS's scratch `merge_queue.py`. The six success and two failure lines of 2026-11-11 predate
Emergency 2 and are replaced by the lines above; the warm-clone measure, the records-only head moves, the store
refresh and the identical-code skip are left out (non-goals) until friction asks for them. The FULL review
(DOD-4) and `guard_refusals` (DOD-6) go by §3.6 and §2.2. `select.py` and `batch.py` are in the allowed paths only
for keyword arguments the queue passes (`scoped`'s change, `isolate`'s workers); their behaviour without them is
unchanged.

**DONE by code (the owner's working assumption, 2026-11-17, through the CTO):** audit 1's question 2, option (b), is
added to this ticket: DONE is the green landing itself (accept green, the land's checks green, the close written);
the Definition of Done shrinks to those three lines and DOD-4 and DOD-6 go (success line 9). The kernel text for it
is approved by the CTO's message (§3.5).

**Closed at the land 2026-11-18 by the CTO (EMERGENCY-2 4.3 step 5):** merged into w2/integrate with gov accept green on the merged tree; no review (3.6).

## Fix: the queue's selection refuses only the landing's own unplaced paths (L2-4, DEC-1217 (1), DEC-1223 (9))
- **The bug (found by the CTO, 2026-11-20):** `gov queue DAEO-sdhj=e2/w2-17-fixes --onto w2/integrate --select` was refused,
  `SELECTION_REFUSED: 6 changed path(s) nothing maps to a suite`: `docs/emergency-2/briefs/*.md`, `proposals/*.md`,
  `release-0.1.4/STEPS.md` and `repin.sh`, none written by the branch. They were committed on `w2/integrate` after the last
  green record (`e74765954`). Every document the CTO commits after a green run therefore blocks every landing.
- **The cause, from the code and the tickets:** `select.scoped` counts the change as "everything since the newest green
  record, with the ticket's own commits" (W2-115 S2, `0fb32b21f`; `test_s2_an_unmapped_path_merged_since_the_green_base_refuses`
  pins it for `gov close`). `gov queue` calls it in the warm clone at the tested merge, so the green range holds the
  base's own commits too, and a path of it that no suite places is refused as if the branch had written it. W2-115b's
  success line 1 says the queue's change is "the branch's own commits since the integration head as well as the
  ticket's"; its non-goals say `select.py` is open to it only for the keyword the queue passes and that the behaviour
  without it is unchanged. The since-green range is `gov close`'s model (W2-115) and leaked into the queue; the base's
  paths are neither this landing's change nor its to refuse (EMERGENCY-2 §3.2: a block must be within the change's
  scope). The range stays (it selects what the untested base paths reach); the refusal does not apply to it.
  The test map's `record_only` cannot take the documents (W2-66: DEC-891's places and nothing else, no code path).
- **The fix line:** with `change` given, a path counted from the green record that neither the ticket's own commits nor
  `change` wrote, and that nothing places, is not refused: it is listed under `unplaced_base` in the selection (the
  object `--select` prints too), and every suite it does reach (imports, couplings, overlaps) is still selected.
  A path the landing's own change wrote and nothing places is refused as before. Without `change` (`gov close`)
  nothing changes. Verify: a planted project with a green record and, after it, two commits on the base that no ticket
  made (a document outside `record_only`, a shell script) beside a branch that changes mapped code: `gov queue <T>=<branch>
  --select` prints the object and exits 0, the two paths under `unplaced_base`; a branch that itself writes an unplaced
  path is refused `SELECTION_REFUSED` (exit 2) naming it and not the base's; a base-side path a test imports still
  selects that test; `select.scoped(root, T)` without `change` still refuses the base-side path.
- **Order:** this section (`Role: orchestrator`); the test designer (Opus, the C3 trial of DEC-1222 (2); `src/gov/close/**`
  and `src/gov/queue/**` are C3), tests under `tests/acceptance/W2-115b/` and `tests/unit/queue/`, red on the base;
  the engineer (Sonnet) until `gov accept W2-115b` is green. Every commit carries `Task: DAEO-j9z6` and a `Fix:`
  trailer with the line above. The ticket stays closed.

## Fix: adopted repositories land; the stage commits need no trailer and no marker (D7, DEC-1227)
- **The finding (measured 2026-11-22, `~/gov-os-runs/d7/`, this branch's code):** on a synthetic repository with a path map, a
  branch holding `gov adopt --lite` A0, A1 and A2 (subject-only commits, `Role` and `Task` absent) and one feature commit, `gov
  queue` lands green with the adoption ticket's `allowed_paths` holding `governance/adoption/**`, `.gitleaks.toml` and
  `.gitignore` (the shape of W2-81's adoption ticket). Nothing refuses: the trailer check (`queue/checks.py` reads `Role` only for
  paths under the acceptance places), the path check (a notice, never a refusal) and test authorship (adopt writes nothing under
  `tests/acceptance/`) pass. The only extras are notices (A0's coordination ticket and roster: `path_notices`,
  `NEW_TICKET_NOT_FEATURE`). The red of W2-81's six dry runs was the set-up's own F1 (`setup_0.1.4.py:125`), not the product.
  A hand edit of a stage record is refused by `gov adopt`'s own chain (`ADOPT_CHAIN_BROKEN`), whatever trailers it carries.
- **The choice (DEC-1227 D7):** neither (T) trailers on the stage commits nor (M) a marker the landing accepts: nothing refuses, so
  nothing is built. Both would add code and a Contract-visible rule for a refusal that does not exist. The fix is the pin: tests
  on a real adopted repository, so a later change to the landing that starts to ask adopt's commits for trailers goes red.
- **What stays as it is, and is told:** a ticket whose `allowed_paths` do not hold `governance/adoption/**` and A0's set-up files
  (not the proving run's case, whose adoption ticket does) is refused `SELECTION_REFUSED` naming exactly those paths, as any
  unplaced code path; `record_only` is not widened (W2-66, DEC-891). A6's moves into `tests/acceptance/` would be refused by G-1
  for want of `Role` (failure line above): rare, named, the owner's `Role: owner` answers it.
- **Order:** this section (`Role: orchestrator`); the independent test designer (Sonnet, DEC-1225), tests under
  `tests/acceptance/W2-115b/`, green on the base by design (a pin, the measurement above); no engineer: nothing to build.
  Every commit carries `Task: DAEO-j9z6` and the `Fix:` line below. The ticket stays closed.

## Fix: `gov queue` never leaves uncommitted work behind (F8; audit N-01; DEC-1232, DEC-1233)

Found 2026-11-22 by the E2 audits (merged table, N-01), the one new gap that meets EMERGENCY-2 §3.2: it loses work. The queue
merges the branch tip; a worktree holding that branch with uncommitted or untracked work was left behind unmerged and
unnoticed. Required: such a worktree (linked or the main tree) is refused before the merge, `QUEUE_WORKTREE_DIRTY`, naming
the worktree and the files; ignored files are not dirty; another branch's dirty worktree does not refuse; after commit or
discard the same entry lands. Kind: a fix; the ticket stays closed. Failing tests first:
`tests/acceptance/W2-115b/test_w2_115b_dirty_worktree.py` (README ids success-17 and failure-5, numbered at the merge with D7, whose `kpis:` lines hold success 14 to 16 and failure 4; the fix itself read them as success-14 and failure-4; 8 red, 5 guards on the
base), `708efc2c0`; code `src/gov/queue/checks.py` (`dirty_files`: `git status --porcelain -z --untracked-files=all
--no-optional-locks`, never writes the worktree's index) and `command.py` (`_refuse_dirty`, called from `_candidate`; exit 1,
the form of `BRANCH_UNKNOWN`: the lead's ruling), `72034b182`; units `tests/unit/queue/test_queue_dirty_worktree.py`. Lead
`fixes-015b` (Sonnet), branch `e2/fixes-015b`. `gov accept W2-115b` green on the first run (every README line then, success-1 to success-14,
failure-1 to failure-4; 74 passed); `tests/unit/queue`: 119 passed. A worktree holding the branch with untracked files that
are not gitignored (stray tool folders) now refuses: intended.
