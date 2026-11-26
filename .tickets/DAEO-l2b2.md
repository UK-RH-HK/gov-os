---
id: DAEO-l2b2
status: closed
deps: [DAEO-l2bd]
links: [DAEO-l2bd, DAEO-j9z6]
created: 2026-11-19T03:00:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-206
tags: [close, queue, landing, emergency-2]
wbs_id: W2-206
title: 'gov queue becomes the landing-and-close, part 2: --dry-run, --select, --full, the after-step (L2 §3 A6, A8; DEC-1214 L2) and two fixes of W2-202'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-l2bd]
waits_on: []
allowed_paths:
- src/gov/queue/**
- src/gov/close/batch.py
- src/gov/close/nightly.py
- src/gov/accept/runner.py
- tests/unit/queue/**
- tests/unit/close/**
- tests/unit/accept/**
- tests/acceptance/W2-206/**
- tests/acceptance/W2-202/**
- .tickets/DAEO-l2b2.md
- .tickets/DAEO-l2bd.md
est_loc: 330
kpis:
  success:
  - 'A6 S1: `gov queue <T>... --dry-run` runs steps 0 to 5 (the hold, the read, the checks, the merge in the warm clone, the acceptance runs, the selection''s run, the culprits) and moves no branch, writes no close commit and no close record; it writes `select.json`, the run files and `summary.txt` and, last, `verify.exit` (its exit code and a newline, written whole) under `--out <dir>` (default `.gov-runtime/queue/dry/<T>/`, the tickets joined by `+` where there are several); its exit code and answer are those the landing would have given (0 it would land every ticket, 3 some would not, 1 refused as a whole) Verify: a planted landing: the integration branch and every ref under `refs/heads/` as `git rev-parse` gives them before and after are equal, no `docs/close/<T>/` exists at the root or in the warm clone''s tested commit, the five files are under `--out` with `verify.exit` last in time, and `gov wait <out>/verify.exit` returns the dry run''s exit code; a planted culprit gives exit 3 in the answer and in `verify.exit`. [L2 §3 A6 S1]'
  - 'A6 S2: `gov queue <T>... --select` prints the selection as one JSON object on stdout (`ticket` for one ticket, `tickets`, `suites`, `pytest_options`: the union of the tickets'' `select.scoped` selections, each branch''s changed paths counted in its change, as the run would have chosen) and exits 0, running no test; a refusal of the selection (`SELECTION_REFUSED`) goes to stderr with exit 2 Verify: a planted ticket: the object equals `gov close --select <T>`''s on the same tree, no test file is run, the integration branch is unmoved; a ticket changing a path the test map does not map: stderr names `SELECTION_REFUSED`, exit 2. [L2 §3 A6 S2]'
  - 'A6 S3: `gov queue <T>... --full` is step 5 widened to the nightly''s own run: the whole `tests/` of the tested merge runs in the nightly''s way (the path map''s serial and parallel split, its limits), a red is run again alone (green alone is flaky: named, not blocking), a red no candidate explains that is red at the base with the same failure type is a known base red, and the tickets land only if the run is green (a red a candidate caused leaves it out, as a selection''s red does); `queue.json` holds the full run under `full` (its runs, `workers`, `cpus`) and the close record''s `selection` says `full` Verify: the nightly''s own test fixture (a planted tree whose one unrelated test, outside every ticket''s selection, is red because of the candidate): without `--full` the candidate lands, with `--full` it is a culprit, exit 3, nothing lands; with the unrelated test green `--full` lands and the record says `full`; `--full` writes no nightly record (`docs/close/nightly/`) into the project tree. [L2 §3 A6 S3]'
  - 'A6 S4: a `--full` run starts no pool wider than its slot''s CPUs (the owner, DEC-1216 (5): every run inside the gate, the full suite included, fewer workers rather than a peak): its workers are the smallest of the project path map''s number (where it names one), `PYTEST_XDIST_AUTO_NUM_WORKERS` (where set), the number of CPUs in `GOV_HEAVY_CPUS` (where set) and, with none of these, one slot''s workers by the product''s rules (`gov.resources.slots`, `gov.dispatch.limits`), never `auto` Verify: planted settings: with `GOV_HEAVY_CPUS=0-1` and `PYTEST_XDIST_AUTO_NUM_WORKERS=2` and a path map naming 12 workers the full run''s xdist pool (`-n`) is 2 and `queue.json` names `workers: 2`; with neither variable and no number in the path map the pool is the product''s one-slot size, not the machine''s CPU count; no `-n auto` and no `-n` above the cap appears in any command the run started. [L2 §3 A6; W2-199; DEC-1216 (5)]'
  - 'A8 S1: after a move, the queue runs `gov rebuild --integration <branch>` where `governance/project/rebuild.yaml` names an `integration_store`, and `gov retrieve` then reports no stale store at the new head Verify: a planted project with a rebuild.yaml naming a store link: after the landing `queue.json` holds `after.rebuild` (its outcome and the head it was built at, the landed head) and the store line `gov retrieve` prints for the link names the new head and no stale count; a project whose rebuild.yaml names no store has `after.rebuild` as `not_configured` and no rebuild is run. [L2 §3 A8 S1]'
  - 'A8 S2: after a move, `gov check --structural <base>` runs, bounded (its own bound, the default), with the landing''s base as `<base>`; its lines and exit code are in `queue.json` under `after.structural` Verify: a planted landing that adds a file the structural pass notices: `after.structural` holds its exit code and its lines, and the pass ran once, after the move. [L2 §3 A8 S2]'
  - 'W2-202 fix 1: the queue''s acceptance run keeps its JUnit report through a parameter, `gov.accept.runner.accept(root, ticket, timeout, keep_report=<path>)`, which copies the run''s report to the path before it is read and changes nothing else (the default gives today''s answer); `gov.queue.acceptance` replaces nothing in `gov.accept.runner` at run time Verify: a planted ticket: `accept(..., keep_report=p)` leaves a JUnit file at `p` and answers as without it; after `gov.queue.acceptance.run` returns, `gov.accept.runner.read_cases` is the very function it was before; the existing W2-202 and `tests/unit/accept` cases stay green. [W2-202 record, the lead''s risks]'
  failure:
  - 'A6 F1: `--dry-run` and `--select` leave `git status --porcelain` at the root empty (the runtime folder is ignored), create no branch, no ref (`refs/gov-queue/land` included), no commit and no file under `.tickets/` or `docs/`; the warm clone is left at the base Verify: `git status --porcelain`, `git for-each-ref` and `git log --all` at the root before and after a dry run, a `--select`, and a dry run that finds a culprit. [L2 §3 A6 F1]'
  - 'A6 F2: a `--full` run that cannot complete (a time limit, a crash, a missing runner) lands nothing and says why (`RUN_INCOMPLETE`, exit 3), never as green Verify: a planted tree whose run times out under `--timeout`: exit 3, `RUN_INCOMPLETE`, the branch unmoved. [L2 §3 A6; W2-115b fail-closed]'
  - 'A8 F1: a failure of either after-step is a notice in `queue.json` (`after.rebuild` or `after.structural` with `ok: false` and the reason); the exit code, the answer''s landed list and the integration branch are as they would have been without it; a landing that landed nothing runs neither Verify: a planted project whose rebuild.yaml names a store that cannot be built, and one whose structural pass exits 2: exit 0, the tickets closed, the branch at the last close commit, the notice in `queue.json`; a landing with a culprit only (nothing landed) has no `after`. [L2 §3 A8 F1]'
  - 'W2-202 fix 2: an acceptance run that fails without naming a failing test (a crash, a time limit, a line no test ran for) names its ticket as the culprit: exit 3, that ticket in `culprits`, the batch''s other tickets landed; the batch is not refused as a whole with `BATCH_UNEXPLAINED` Verify: a planted batch of two tickets, one whose acceptance folder crashes at collection (or whose README maps a line to a test that does not exist) and one clean: exit 3, `culprits` names the first, the second lands and closes, no `BATCH_UNEXPLAINED`; the same ticket alone: exit 3 as a culprit, nothing landed. A test failing by name is still attributed by the batch''s own search. [W2-202 record, the lead''s risks]'
non_goals:
- "A2 (one close record, one writer: it waits for the M1 lead's `e2/m1-context`, which changes the close record), A7 (`--direct`: the owner answers L2-6), every B item (the owner's yes)"
- "`src/gov/close/command.py`'s record writing (M1's) and `src/gov/dispatch/**` (the run-time lead's)"
done_when: [DOD-1, DOD-2, DOD-3]
sources: [EMERGENCY-2, DEC-1214, DEC-1216, DEC-983, DEC-982, DEC-959, DEC-953, CAP-33, DAEO-l2bd]
acceptance_tests:
  path: tests/acceptance/W2-206/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-206 the landing becomes the close, part 2 (L2 §3 A6, A8; two fixes of W2-202)

A new KPI line on W2-115b/W2-202 (closed) is a new ticket (EMERGENCY-2 4.6). The lines are those of
`docs/emergency-2/L2-COMMANDS.md` §3 items A6 (`--dry-run`, `--select`, `--full`) and A8 (the after-step), decided by
the owner in DEC-1214 L2, with the owner's rule for the full run (DEC-1216 (5): every run inside the gate, fewer
workers rather than a peak) and the two fixes W2-202's record named (recorded in `.tickets/DAEO-l2bd.md`, the failing
test first). A2 waits for the M1 lead's close record; A7 waits for the owner's answer to L2-6; B waits for the owner's yes.

**The logic of `close._verify_command` and `_select_command` moves** into `gov.queue` (the close's own commands stay
until B1 retires them; `gov close --select`'s output is the reference for A6 S2).

**The lead's rulings on the test designer's four open points (2026-11-19):** (1) a dry run refused as a whole writes
`verify.exit` (exit 1) so `gov wait` returns; the tests assert only exit 1, `TICKET_UNKNOWN`, nothing moved. (2)
`--select` equals `gov close --select` (each ticket's own acceptance folder is in the selection). (3) A `--full` run
leaves the candidates' own acceptance folders out of its run (W2-202 A3 F1: no test runs twice in a landing). (4) A6 S4's
second case plants no number in the path map.

**Closed at the land, 2026-11-19 04:34 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 8e27b6248 (branch `e2/l2-build-2` at 6192547a7). On the merged tree, through the slot with workers: `tests/unit/queue`, `close`, `accept`, `optin` and `tests/acceptance/W2-115`, `W2-115b`, `W2-193`, `W2-194`, `W2-202`, `W2-206`: 724 passed; `gov accept W2-206`: 45 passed, 0 failed. The CTO's rulings on the lead's lines: `--full`'s path-map worker number is also capped by one slot's size (with the A2 ticket); the lead brief's line telling the engineer to read the acceptance folder is corrected (the engineer role's text holds). Not built here: A2 (after W2-200), A7 (the owner's L2-6), the B items (the owner's yes).

## Fix: one selection for many branches, SEL-4 (2026-11-25; plan item 1-0; the owner's order of 25 Nov)

- **SEL-4 One run for many branches.** `gov queue <T1>=<b1> <T2>=<b2> ... --select`, and a batch branch's several branches
  (`--select` accepts the same ticket twice with different branches, and a branch that is the merge of several), print one
  object for the merged tree of all of them: one `suites` list (the union, each branch's own change counted alone, never the
  sum of two ranges), `tickets` naming each, and the merge's refusal (`CANDIDATE_NOT_ISOLATED`) where the branches do not merge
  together. Held branches land in one run. Verify: two planted branches under two tickets: one object, `suites` equal to the union
  of each branch's selection alone; a planted pair that conflicts is refused as a whole, nothing run.

## Fix: the landing proves the path map holds every path a change adds exactly once, PM-1 to PM-3 (2026-11-26; plan item 1-11 (c); G-8 (a), Q-1 (a), DEC-1244; approved by the CTO in the lead's brief)

- **PM-1 Refused at the landing.** Before the integration branch moves, the landing (and `--dry-run`, `--full`, `--select`)
  runs the path map's coverage check (`gov.check.pathmap.check`, reused, never copied) on the merged tree and refuses a
  candidate that adds or renames a path held by no namespace (`PATH_NO_NAMESPACE`) or by two or more
  (`PATH_MULTIPLE_NAMESPACES`); no switch. The reason names each such path and, for one in none, the exact line to add
  under a namespace's `paths` (`- "<folder>/**"`; the path itself, `- "<path>"`, for a root file or where the folder
  holds files the map already places); for one in two, the namespaces and their patterns. The landing lists it under
  `refused` (`ticket`, `code`, `paths`, `reason`), the other candidates land (exit 3); `--select` says
  `<code>: <ticket>: <reason>` on stderr, exit 2. A path already in none or two that the change does not add refuses
  nothing. Where the merged tree's map cannot be used (missing, unreadable, invalid), a candidate that adds a path or
  changes the map is refused with the check's code. Verify: a planted branch adding `docs/newfolder/x.md` under no
  namespace is refused naming `- "docs/newfolder/**"` (the landing and `--select`); the same file under a mapped folder
  lands; a path two namespaces hold is refused naming both; a rename into an unmapped folder is refused; a second clean
  candidate of the batch lands.
- **PM-2 A record inside a mapped folder.** A record-only document the branch writes inside a folder the map holds is
  never refused: it passes, with the notice `RECORD_PLACED <path>` where nothing else places it (DEC-1239 (2)).
  Verify: planted: `--select` exit 0 with the notice; the landing lands with it.
- **PM-3 The counts are printed.** The landing's answer, `queue.json`, a dry run's answer and `select.json`, the
  `--select` object and a ticket's first close record hold `path_map` (a fix landing's close record stays as W2-201 X6 pins it,
  one fix entry and line; the CTO's call, 2026-11-26): `path map: <n> tracked, <a> in none, <b> in two` for the
  merged tree (`in two`: in two or more). A project with no `governance/project/` has no `path_map`. Verify: planted: a
  clean landing says `0 in none, 0 in two` with `<n>` equal to `git ls-files` of the tested merge; a project with one
  path already in none lands and says `1 in none`.

## Fix: the impact trace at the landing, IT-1 and IT-2 (2026-11-26; plan item 1-9; T-11 (a), DEC-1242; X-1, DEC-1244; approved by the CTO in the lead's brief)

- **IT-1 The trace, into the close record.** For each candidate that lands, the landing traces every **record** file its
  own change holds (a Markdown file with a frontmatter `id`: a specification, a ticket, a decision record; and each
  entry the change adds, edits or removes in the file the path map names under `decision_register`) with `gov impact`
  on the tested merge. A source file is not traced and the code graph is never loaded (I-42). The answer and
  `queue.json` hold `impact`, a mapping of ticket to its entry; the ticket's first close record holds that entry under
  its front-matter key `impact`: `{records: [{id, path, tickets: [<id>...], tests: [<id>...], complete: <bool>}...],
  complete: <bool>}`, `tickets` and `tests` and `complete` as `gov impact <id>` says them on that tree; the entry's
  `complete` is true only where every record's is. A record `gov impact` cannot trace (a removed one) is `{id, path,
  unavailable: "unavailable (<reason>)", complete: false}`. A change with no record file has `{records: [], complete:
  true}`. A trace that fails as a whole or takes longer than its limit (120 s; `GOV_QUEUE_IMPACT_TIMEOUT`, seconds)
  never refuses the landing nor changes its exit code: the entry is the string `unavailable (<reason>)`. A fix landing's
  close record stays as W2-201 X6 pins it; its trace is in the answer and `queue.json` only. Where it runs: after the
  merge and before the close commit, so the one close commit holds it (the integration branch gets no commit after the
  last close commit, A8 F1). Verify: planted: a branch changing a decision entry of the register and a specification
  lands; the close record names, for each, the tickets and tests `gov impact` names on the landed tree; a changed source
  file is not listed; a path map naming a register `HEAD` does not hold, and a limit of `0.001`, each land with exit 0
  and `impact: unavailable (...)`.
- **IT-2 `--select` carries the same trace.** The `--select` object (and a dry run's `select.json` and answer) holds
  `impact`, the mapping of ticket to entry, for the candidate range on the merged tree; it runs no test and moves
  nothing; a trace that fails is the string, exit 0. Verify: planted: `--select` of the IT-1 branch prints the same
  `impact` the landing then records.
