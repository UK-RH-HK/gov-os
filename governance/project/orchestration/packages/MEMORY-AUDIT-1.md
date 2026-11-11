# MEMORY-AUDIT-1: the memory audit as a scheduled tool (for the owner's approval)

Written for the owner by a product-spec helper for the CTO (orchestrator `DAEO-sdxk`), 2026-11-11, from DEC-1125 (3)
(iii) e. **Nothing is installed, scheduled or run by this package.** E = estimated (basis named); M = measured (source
named); $ = Anthropic's list price; 1 point of the weekly meter is about $27.5 (USAGE-1, M).

- **Under:** DEC-1101 (1)-(3), DEC-1125 (2)-(3), DEC-1097 (4) (folded in), DEC-1112 (3), DEC-1113, DEC-1120 (RUBRIC-2),
  DEC-1069, DEC-1050.
- **Files:** the three briefs, `MEMORY-AUDIT-1/briefs/writer.md`, `checker.md`, `auditor.md`; the two ACTs,
  `MEMORY-AUDIT-1/ACT-DRAFTS.md`; the lines for W2-88, `MEMORY-AUDIT-1/W2-88-LINES.md`; four tickets W2-170 to W2-173.

## 1 What to decide, in short
1. **Approve the three briefs** (writer, checker, auditor) as drafted, or tell me the changes. No labeller is needed (§3).
2. **Approve the schedule:** every Monday at 21:00 (the machine's clock), with the rule that moves it to monthly (§4).
3. **Approve 40 questions per audit** and the regression pool's cap (§3.4, §9).
4. **Say yes to the plan for the first audit: Monday 2026-11-23 at 21:00**, its digest on Tuesday 11-24 at 09:00 (§6).
Recommendation on each: yes, as written. Confidence: high on 1 to 3 (each follows DEC-1101 and DEC-1125), medium on 4
(the date depends on four tickets and two ACTs landing in six working days after the weekly reset).

## 2 Where it stands today (M: the files named)
- **The walls are in.** ACT-INDEP-WALLS-1 was applied by your operator (`147706ae`): the walls' template, the path
  map's hidden globs, the walls' approved list (row 28 and row 42 of DECIDED-NOT-DONE).
- **The launch script is merged and installed.** W2-149 (`DAEO-52ku`) merged `b4de529b` (11-09); set-up A's wiring
  `7f0e71519`, its fixes `90c1fea6c` and `2f98aecbc` (row 86). ACT-W2-149-INSTALL-1 was applied by your operator
  (`baac0b2c2`, 11-10 15:41; list `6b923cb4d552`, 0 mismatches; row 75). ACT-SETS-GLOBS-1 applied `9cce7430d`; ACT-PATHMAP-NS-2
  placed the briefs' folder in the path map. **So the walls and the launch script wait for nothing but briefs.**
- **The fixed briefs that exist are set-up A's five** (`governance/project/indep-briefs/sgx1/`: two writers, two
  labellers, the overlap auditor), for the guard experiment. **There is no brief for the memory audit's writer,
  checker or auditor.** The walls' template and the script already support those three kinds (`kinds.yaml`, W2-149's
  schemas), so this package supplies them. The old operator folders `~/gov-os-writer` and `~/gov-os-checker` stay as they
  are until the default (ACT-INDEP-WALLS-1 §7 item 3).
- **The measure is a set of one-off tools.** `gov.retrieval.measure` (W2-61) gives hit@5 and full evidence and is a
  product module. The end-to-end run that judged the fresh 80 (reader, graders, the fault rule, the figures) lives
  in the CTO's scratch (`drafts/fresh80/`) and is pinned to one set name; it cost $12.46 and 8.2 minutes for 80
  questions (FRESH-80-RESULT, M). **Nothing yet turns a delivered set into a measured audit.** That is W2-170 and W2-171.
- **The schedule is not in the crontab.** The crontab holds the dispatcher (every minute) and the operator agent's launch
  (every 10 minutes, 00:00 to 00:59 and 08:00 to 23:59). The nightly's four lines are commented out by DEC-1049 and
  DEC-1050; when they come back, the nightly runs 04:00 to 08:00 and its check to 09:00 (DEC-973).
- **Adopted repositories:** W2-88 (`DAEO-2bdu`) has the first practice (S12 to S17: a tuning set of about 80, a verdict
  set of 80 used once) and a `memory_sets.py` that nobody has written. It has no line for the periodic audit (§5).

## 3 The fixed briefs (drafts, for your approval)
Hashes are taken only after you approve. The bytes you approve are the bytes the launch script checks. A change after
approval means a new approval (DEC-1101 (2)).

| | writer | checker | auditor |
|---|---|---|---|
| **Purpose** | writes the audit's 40 questions, then revises them after the checker's notes | checks each question against the repository with the rubric, lists the other places that state each answer | classifies every miss as one of five kinds |
| **Reads** | the repository tree at the audit commit, less the walls' exclusions; `input/selection.json` | the same tree; the writer's questions in `input/set/` | the same tree; the questions; `input/misses.jsonl` |
| **Content by rule** | 24 from the paths changed since the last audit, 16 from a seeded sample of 300 older paths (§3.1) | none: it checks what it is given | none |
| **Must not read** | memory's search and run outputs; earlier sets; the evaluation's documents; records of the standing measure that name misses; anything about this audit | the same, and the writer's folder | the same, and any other audit's files |
| **Output** | `out/set/q01.yaml`...`q40.yaml`; `out/result.json` | `out/notes.md` in a fixed form; `out/result.json` | `out/classes.json`; `out/result.json` |
| **Set size** | 40 | checks 40 | classes each miss |
| **Stop rule** | stops with no set if fewer than 36 questions can be written, two decisions conflict, or a forbidden read is needed | stops on an empty or unreadable set | stops on an unreadable misses file |
| **Model, effort (RUBRIC-2, DEC-1120 (2))** | Sonnet 5.5, high | Opus 5.5, high | Opus 5.5, high |
| **Budget, time** | $12, 90 min | $10, 60 min | $6, 40 min |
| **Rounds** | 2 (round 2 only when the checker finds a revise or reject) | once after each writer round | once |

**Why no labeller.** A labeller (set-up A) labels guard cases against a rulebook. The audit has no labels: the checker
cross-checks the questions and the auditor classifies the misses. If a later step needs one, it comes with its own brief.

### 3.1 How the content is chosen, and the walls that enforce it
- **By rule, from a seed recorded first.** The launch script records the seed before it writes anything (its stage 13),
  lists the tracked paths changed since the last audit from git (`changed`) and draws 300 older paths (`sample`) from the
  seed. The writer then draws from the two lists by a fixed rule (its section 5 item 2): list C turned to start at
  `SEED mod length(changed)`; list S in the order drawn; each path to the open category with most places left. The
  pre-flight (W2-170) checks that every question's governing source is in the list its `drawn` field names.
- **At a first audit the changed list starts at the fresh 80's commit** (`c00d525fd420`, 11-07), written once as a
  baseline line (W2-172's `baseline`). That makes the first audit's 24 changed-path questions come from everything
  changed since the last measured retrieval, which includes the re-pin's retrieval change.
- **Walls (M: the template and the script):** no shell, so memory's search cannot be run; the wall's settings deny it;
  the wall hook refuses every path outside the folder and the tree; the tree leaves out the evaluation's documents
  (`tree-exclude.txt`); the six roles cannot read the walls or the sets root (the path map's hidden globs, which already
  hold `fixtures/evaluation/*/hidden/**`, `*/XCHECK-r*.md`, `runs/*/miss-classes.json` and `runs/*/misses.jsonl`).
- **Two rows rest on the brief alone** (the tree holds them): the three measure records `W2-86`, `W2-87` and
  `W2-92-memory-measure.md` with the two D4B survey files (they name tuning questions and misses), and this package and
  its briefs. Option 3 in §9 closes both with a template change.
- **The rubric is inside the briefs.** `docs/research/memory-measure-audit/RUBRIC.md` is excluded from every wall's tree
  (the folder holds the tuning questions), so a session could not read it. Its eleven tests (version 2, DEC-1069) are
  written into the writer's and checker's briefs. A new rubric version means new briefs and a new approval (DEC-1097
  (13) already plans version 3 after the fresh 80).

### 3.2 What each brief hands back (counts only reach the CTO)
- The launch script returns `counts.json` per run: the checker's three verdict counts, the writer's counts by kind and
  area, the auditor's five class counts. Question text, answers and paths never leave the sets root.
- The auditor's input `misses.jsonl` carries one fact about the search: `evidence_in_bundle`, yes or no, from the
  measure. It decides only "memory did not find it" against "memory found it and the agent answered wrongly". It shows
  no rank, bundle or search result.

### 3.3 How the rest of the cycle goes (the tickets build it)
Writer round 1, then the pre-flight (a script: counts, form, spread, sources exist, no duplicate of an earlier
question), checker round 1, writer round 2 and checker round 2 only if the first notes found something, then every
question not accepted is dropped (never deleted). Fewer than 36 kept, or a domain under 4: the audit is **void**
and nothing is measured. Then the declaration and the use-once marker, the standing control, the measure, the judged
end-to-end run (search again once, as the fresh 80), the misses file, the auditor, the pool's re-run and the digest block.
A miss is a result: never run again, never re-scored (W2-88 S16's rule).

### 3.4 The size, and the bar on it
40 questions suit the rubric (its category table is for 40) and the cost. On 40 the bar of DEC-1097 (1)(d) is **at least
34 right end to end and at most 2 wrong claims** (85 % and 5 %); the target is 38. One question is 2.5 points, so one
audit is a signal and the trend over weeks is the evidence; the pool (§7) adds the regression check. 80 would give a
tighter interval at twice the reading cost.

## 4 The schedule
- **Weekly: Monday at 21:00**, the machine's clock (Europe/London). It runs for about 3.5 hours and ends near 00:30 (E).
- **Why Monday 21:00.**
  - It is clear of the nightly's window (04:00 to 08:00, its check to 09:00) and of the digests (09:00 and 18:00) and the
    20:00 capacity brief. It ends before the quiet hours (02:00 to 07:30).
  - A week of merges is in before it, so the "changed" half has weight. Its digest block is ready for Tuesday 09:00, with
    the week's days left to fix, and the next audit, a week later, is the verdict on the fixes (DEC-1101 (1)).
  - The usage week resets on Sunday at 09:00, so the audit's spend falls early in the week's allowance.
- **How it runs.** One crontab line starts `memaudit_cron.sh`, which asks `due` and starts the cycle only when an audit is
  due (W2-172). The cron line never changes when the rhythm does. It is **class (b)** in `class-rules.yaml` (the
  `crontab` row), not (O): your yes, then the operator agent applies it (ACT-MEMORY-AUDIT-CRON-1, `ACT-DRAFTS.md`).
  The briefs' install is **class (O)**: your yes, then your operator by hand (ACT-MEMORY-AUDIT-INSTALL-1).
- **Active or stable: a rule, computed from git and the audits' own results.**
  - The measure of churn: the share of tracked paths changed in the 28 days before the audit commit, less the walls'
    exclusions. Today it is about 36 % in a week and 73 % in 28 days (M: git, 3,896 tracked paths).
  - **To monthly** only when the last three audits each had churn under 5 %, no change to a retrieval path in the 28 days
    before each, a verdict that met the bar, and no pool regression.
  - **Back to weekly at once** when any one holds before a monthly run: churn of 10 % or more; a change to a retrieval
    path since the last audit; a verdict below the bar; a pool regression.
  - Retrieval paths: `src/gov/retrieval/**`, `src/gov/retrieve/**`, `src/gov/store/**`, `src/gov/codeintel/**`,
    `governance/project/retrieval.yaml`, `governance/project/path-map.yaml`.
  - The numbers (5 %, 10 %, three audits) are mine; you may change them. Gov OS is active by any of them today.
- **How a retrieval change waits.** It merges as ordinary work, and the next audit measures it: no separate run. The
  digest block names the retrieval paths changed since the last audit. A release cut asks
  `gov.memaudit status --since <commit>`: `audited` once a measured audit's commit is at or after the last retrieval
  change, else `not audited, next due <date>` (DEC-1097 (4) folded in). At most seven days in weekly mode; a retrieval
  change brings a monthly repository back to weekly, so it never waits a month. If you want a release sooner, the same
  tool runs the same briefs on your word (`--force`): the audit brought forward, not a separate measure.

## 5 Home tickets
**Gov OS, filed here** (`tk create`; WBS ids W2-170 to W2-173; each validated against the ticket schema; all after the
lift and, under usage (A), waiting for the weekly reset on 11-15):

| WBS | id | what | est. lines | profile |
|---|---|---|---|---|
| W2-170 | `DAEO-61vm` | the set's record: pre-flight checks, drop and void rule, declaration and use-once marker, the set declared in the sets root's own map, counts only | 450 | FULL |
| W2-171 | `DAEO-k1e2` | the measure: control, retrieval figures, judged end-to-end run, fault rule, misses file, regression pool (waits on W2-170) | 600 | FULL |
| W2-172 | `DAEO-p8tv` | the driver and the schedule: the cycle through the launch script, the active and stable rule, the digest block, the release check, the cron wrapper (waits on W2-170, 171, 173) | 450 | FULL |
| W2-173 | `DAEO-qz4p` | the launch script's follow-ups: the brief's effort passed to the session, a stop word for writers and checkers, the notes' and classes' form checked at delivery | 200 | FULL |

Each is a package `src/gov/memaudit/` (W2-170 to W2-172) or the launch script (W2-173), with a designer's tests first
(Sonnet, high; class C2) and one review (Opus, high on FULL). The code ships with Gov OS so that adopted repositories
get it. **W2-88's lines** (`MEMORY-AUDIT-1/W2-88-LINES.md`, S18 to S23): the audit's record at adoption, the briefs'
variants approved once per repository, one core and not two (`memory_sets.py` calls `gov.memaudit`), the first audit
after the verdict set, the walls by one ACT, the cost stated. W2-88 gains three dependencies, on W2-170 to W2-172. Not
filed: the weekly "not found" and "may be incomplete" counts (DEC-1101 (1), row 46) have no home yet; they are not part
of the audit's cycle, and I recommend one small ticket after the lift.

## 6 The first audit: Monday 2026-11-23 at 21:00
**It measures the re-pin's retrieval change** (the first audit's changed list starts at the fresh 80's commit; 11
files under the retrieval paths changed since, in 11 commits to the retrieval code and its settings, M: git). **What must land first, with earliest dates:**

| Step | Who | Earliest | Waits on |
|---|---|---|---|
| Approve the three briefs, the schedule, the size | you | 11-11 (the digest) | this package |
| Weekly reset; usage (A) ends | | 11-15 09:00 | DEC-1122 (2) |
| W2-173 and W2-170: designers, engineers, reviews | CTO's workers | 11-15 to 11-17 (E) | the reset |
| W2-171, then W2-172 | CTO's workers | 11-17 to 11-19 (E) | W2-170 (and W2-173 for W2-172) |
| ACT-MEMORY-AUDIT-INSTALL-1 built from the approved bytes, rehearsed, reviewed; your yes and operator, one minute | CTO, you | 11-18 to 11-19 | the briefs' approval |
| The baseline line, the pool's import (the 79 and the 138), one dry cycle on planted roots, one live canary under each brief | CTO | 11-19 to 11-20 | the tickets, the install |
| ACT-MEMORY-AUDIT-CRON-1: your yes, then the operator agent | you | 11-20 to 11-21 | all of the above |
| **First audit** | the cron | **Mon 11-23 21:00** | |
| Its digest block | CTO | Tue 11-24 09:00 | |

The estimate for the tickets is E: W2-149 (700 lines, FULL) went from filed to merged in about a day on 11-09 and 11-10.
**If a step slips, the first audit is Monday 11-30.** Monday 11-16 is not reachable: the tickets cannot start before the
11-15 reset, and the cron line needs them merged. The CTO may run a missed audit by hand with the same tool and the same
briefs; that is not a second kind of audit.

## 7 What it costs per audit (E, basis named)
| | $ (list price) | meter points | other |
|---|---|---|---|
| Writer, round 1 (Sonnet, high) | about 3.5 | | 40 min |
| Checker, round 1 (Opus, high) | about 7 | | 40 min |
| Writer round 2, checker round 2 (only when the first notes found something) | about 3 and 7 | | 25 and 40 min |
| Judged end-to-end run on 40 questions | about 6.3 (0.157 a question, M: FRESH-80) | | 5 min |
| Auditor (Opus, high) | about 3 | | 15 min |
| **Model total** | **about 30 with round 2; about 20 without; capped at 50 by the briefs' budgets plus 12.6 for the run's brake** | **about 1.1 (typical); at most 2.3** | |
| Retrieval measure of the set and of the control (no model tokens) | 0 | | about 10 min of query and embedding GPU (M: 407 searches at a median 1.3 s per 80 questions) |
| The regression pool (retrieval only) | 0 | | about 25 min at first (217 questions), at most about 45 min (the cap of 400) |

- **The basis (E):** USAGE-1's average launched worker is $3.6 at Opus; a Sonnet token costs half an Opus token;
  the checker reads and verifies 40 questions, so I took twice the average. The first audit measures the real figures
  and replaces these (the spend log records tier, class and cost, DEC-1118 (3)).
- **A week's allowance is about 100 points, so an audit is about 1 % of a week** (typical). A month of weekly audits is
  about $125 (E).
- **Your minutes:** once, about 45 for this package, the three briefs and two yeses. Then about 5 a week for the digest
  block, and about 20 in a week that proposes a structural fix (DEC-1101 (1): brought to you, judged on the earlier sets).
- **The wall-clock** is about 3.5 hours (E), from 21:00 to about 00:30.

## 8 The tool in one place
- **Goals:** a fresh, independent set of 40 questions each week; measured once; misses classified; drift found while
  it is small; the same tool for every adopted repository; no session opened by hand.
- **Non-goals:** no change to retrieval by the audit itself (fixes are brought to you); no second measure beside it; no
  judgement of a question by its score; no automatic fix; no new guard rule.
- **Alternatives (one line each):** a monthly audit from the start (rejected by DEC-1125 (2) while development is
  active); 80 questions a week (twice the reading, a tighter bar; option 1 of §9); the old operator folders (rejected:
  they load your user settings and read the live repository, ACT-INDEP-WALLS-1 §7).

## 9 Options, with my recommendation
1. **Set size.** (a) 40 (recommended); (b) 80, about $45 and 6 hours a week; (c) 20, too thin for the rubric's spread.
2. **The pool's re-run.** (a) retrieval only, the whole pool up to 400 questions and then a seeded draw of 400
   (recommended; it keeps the GPU time flat); (b) the whole pool every time (the time grows by about 3 minutes a week);
   (c) end to end (about $0.16 a question: $60 at 400). DEC-1101 (1) says "re-run at every audit"; (a) is that, bounded.
3. **The blindness the brief alone holds.** (a) leave the five measure records and this package to the briefs'
   instruction (recommended now); (b) one small template change by an ACT (class (O), a new hash for `tree-exclude.txt`
   and a rebuilt install list) that leaves them out of every wall's tree. I would take (b) with the next template change,
   or at once if a writer's `conflicts.md` ever names one.
4. **The auditor's kinds.** (a) the five that the schema has (`gold_wrong`, `question_ambiguous`, `out_of_scope`,
   `retrieval_miss`, `answer_wrong`), with rank bucket and namespace counted by the runner (recommended); (b) the kinds
   DEC-1101 (1) lists (never retrieved, ranked low, vocabulary, correct answer citing an unlisted place), which needs a
   new result schema and a richer brief. The rank and namespace splits give "never retrieved" and "ranked low" without a
   model; "vocabulary" is the one kind (a) cannot see. I would look at the first two audits before adding it.
5. **The first date.** (a) Monday 11-23 (recommended); (b) 11-16, not reachable.
6. **The rule's numbers.** 5 %, 10 %, three audits, and the pool regression at 3 points (about one question in thirty):
   mine, to change if you wish.

## 10 Found while drafting (for the CTO)
- **DECIDED-NOT-DONE is out of date on this item:** row 43 says "WAITS: the ACT's design" (the script merged, row 67, and
  was installed, row 75); row 45 still says every two weeks (DEC-1125 (2): weekly); row 44's briefs are this package.
  Row 117's state should now point here.
- **No `--effort` reaches an independent session.** The script passes `--model` only; the walls' settings and `kinds.yaml`
  carry no effort. RUBRIC-2's effort high is therefore not enforced there. The briefs name `effort: high` in their front
  matter, which the script ignores today; W2-173 S1 makes it real. Until then the first audit's sessions run at the CLI's
  default effort and the digest says so.
- **The set must be declared in the sets root's own path map for the measure** (`gov.retrieval.measure` reads
  `<sets-root>/governance/project/path-map.yaml`'s `evaluation_sets`, by exact name). A new name every week would need an
  ACT every week, so W2-170 S4 has the runner add the one entry itself. I did not open the sets root, so I could not
  check that the map is there as the measure's code expects; the CTO checks it in code before the first launch.
- **The auditor's result schema has five classes and the writer's has fixed `by_kind` and `by_area` keys.** I used both as
  they are (the simplest reading). The category counts, R5's spread and the draw are checked by the pre-flight from
  the files themselves, not from `result.json`.
- **The audits' log (`AUDITS.log`) gets a line only when an auditor delivers.** The driver therefore always runs the
  auditor, with an empty misses file when there is no miss (W2-172 S1).
- **The old measure scripts are pinned** to `memory-verdict-2` and to their own run folder; W2-171 generalises them. The
  CTO copies them into the ticket's worktree.
- **ACT class:** the brief that asked for this package called the crontab class (O); `class-rules.yaml` makes it (b).
- **W2-149 is still `in_progress`** (rows F37 and F40, neither in this package's path). W2-173 does not wait for its
  close; it changes the script as reviewed code under the list in force (ACT-W2-149-INSTALL-1 §3, F34).
- **Checked against the launch script's own stage-10 reading** (its `front_matter`, `resolve_brief` and `read_schema`, run
  on the three drafts, nothing launched): each resolves its model, result schema and sample, and its budget and timeout are
  within `kinds.yaml`'s caps. The briefs carry no `brief:` id on purpose: an id must name a set-up A entry in `kinds.yaml`
  (else code 10), and a memory brief takes the kind's defaults. `effort` and `rounds` are ignored by the script today.
- **An abandoned ticket: none.** All four I filed are complete.
