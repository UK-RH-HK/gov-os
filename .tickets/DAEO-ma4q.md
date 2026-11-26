---
id: DAEO-ma4q
status: closed
deps: [DAEO-0cd2, DAEO-zlog]
links: [DAEO-0cd2, DAEO-zlog]
created: 2026-11-19T01:30:00Z
type: task
priority: 1
assignee: engineer
external-ref: W2-204
tags: [memaudit, adoption, fresh-80, emergency-2]
wbs_id: W2-204
title: 'The memory measure runs on any adopted repository by product commands: per-repository configuration, `gov memaudit` steps and the fresh-80 driver, generated briefs, F-1 and F-2 fixed (EXAMIN F-032; EMERGENCY-2 §8.2 item 3, §7.4; DEC-1210, DEC-1214 E3)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
profile: FULL
depends_on: [DAEO-0cd2, DAEO-zlog]
waits_on: []
allowed_paths:
- src/gov/memaudit/**
- governance/project/memory-audit.yaml
- template/governance/kernel/schemas/memory-audit.schema.json
- tests/unit/memaudit/**
- tests/acceptance/W2-204/**
- tests/conftest.py
- tests/acceptance/conftest.py
- tests/unit/memaudit/conftest.py
- docs/changes/W2-204-evidence.md
- .tickets/DAEO-ma4q.md
- .tickets/DAEO-0cd2.md
est_loc: 1500
kpis:
  success:
  - 'S1 Gov OS''s constants come from its configuration file: `governance/project/memory-audit.yaml` holds today''s domain table, subsystem table, 12 categories with their quotas (6, 4, 4, 4, 4, 4, 3, 3, 3, 3, 1, 1), the control set (`memory-retrieval`, part `visible`, size 40, baseline 34, spread 2) and the spread rule (4 per 40 for a domain, 10 per 40 for a subsystem), and `gov.memaudit.config.load` of Gov OS''s repository returns exactly those values; the file validates against `template/governance/kernel/schemas/memory-audit.schema.json` Verify: a test with the old tables written out as literals compares them with the loaded values (names, order, patterns, counts, control figures) and validates the file against the schema; every test of `tests/unit/memaudit` and of `tests/acceptance/W2-170`, `W2-171`, `W2-172`, `W2-187`, `W2-88`, `W2-198` and every other folder that names `memaudit` passes with its test files unchanged [EMERGENCY-2 §8.2 item 3; the CTO''s decision 1]'
  - 'S2 No silent default: in a repository whose audit commit holds no `governance/project/memory-audit.yaml`, each of `preflight`, `void`, `declare`, `measure`, `judge`, `brief`, `check` and `fresh` refuses with exit 1 and the line `MA-CONFIG-MISSING write governance/project/memory-audit.yaml`, writes nothing under the audit''s run folder and the set, reads no store and starts no search or model call Verify: a planted repository without the file and a planted sets root: each command exits 1 with that line; the sets root tree is byte-identical before and after; the fake gov and fake claude record no call [the CTO''s decision 1]'
  - 'S3 The file''s failure lines: a category quota list that does not sum to `half_size` gives `MA-CONFIG-QUOTA sum <s> of <half_size>`; a domain no tracked file at the commit matches gives `MA-CONFIG-DOMAIN-EMPTY <name>`; an unknown key (top level or inside a domain, subsystem, category or control row) gives `MA-CONFIG-KEY <dotted key path>`; any other fault (unreadable YAML, a wrong type, a missing required key, `nonexistent-id` absent from the categories, a duplicate name, a `baseline` that is neither an integer nor `first`) gives `MA-CONFIG-FORM <key path>: <reason>`; each exits 1 at every step and `check`, naming the first fault only, and nothing is written Verify: planted files with one fault each, each command''s line and exit code; no line holds a question, a path under the sets root or the file''s text beyond the key path [the CTO''s decision 1]'
  - 'S4 A second repository goes from two delivered halves to a judged figure: a planted repository with its own domains, its own categories and quotas (for example decision 6, task 4, spec 4, scenario 3, report 3, exact-string 4, callers 4, code-paraphrase 4, multi-file 3, failure-memory 3, history 1, nonexistent-id 1), its own subsystems and its own control set, whose two halves are delivered into a planted sets root, runs `gov memaudit fresh` to the end with a fake gov and a fake reader and graders: both halves have `FIGURES.json` with `by_category` keyed by the repository''s categories, and the last lines are one `FRESH VERDICT hidden right <r> of <n> (<p> %): passes|misses` line and one `FRESH BESIDE visible right <r> of <n>` line (counts only), exit 0 Verify: the planted second repository with a fake reader that answers every question right: exit 0, both `FIGURES.json` hold the repository''s category names and none of Gov OS''s that are not in the file, the verdict line''s n equals the kept hidden questions, `passes`; with a fake that answers 3 of 40 wrong it says `misses` [the CTO''s decisions 1 and 2]'
  - 'S5 A subsystem may be declared by a record key: a subsystem row `{name, record_key, values}` counts a question for the subsystem whose `values` hold the value of the key in the front matter of the question''s first source file at the audit commit; a path row counts by path as before; the first matching row decides, a question matching none counts as `none` Verify: a planted repository with records carrying `feature: F01` and `F02`: questions whose first source is such a record are counted per feature in `PREFLIGHT.json` and `DROPS.json`; a half with 11 of 40 in one feature is refused `PF-SPREAD subsystem <name> 11`; a source file with no front matter counts `none` [EXAMIN''s proposal, the CTO''s decision 1]'
  - 'S6 The control is the configuration''s: `measure` runs the control set, part and size the file names and compares its hit@5 with the last audit''s control figure (else the file''s `baseline`) within the file''s `spread`; `baseline: first` records the first measure''s figure and cannot be out of range; `control: none` runs the probe search only and `FIGURES.json` holds a null control; Gov OS''s own figures (34, 2) are unchanged Verify: planted runs with a baseline of 20 and a fake control of 20 (in range), 24 (`STOPPED control`, exit 2), with `first` (passes, the figure recorded for the next audit), with `none` (no control search made, the figures null) and Gov OS''s file with 34 [the CTO''s decision 1]'
  - 'S7 The driver follows the design''s cycle (F-1): per half, from what is delivered in the sets root: the first pre-flight runs once the writer''s round 1 is delivered and a refusal is recorded, never a stop; the checker''s round 1 is then needed; when its notes hold any `revise` or `reject` line, or the first pre-flight refused, the writer''s round 2 and the checker''s round 2 are needed; then `void`; then the final pre-flight on the kept set (a refusal stops: `STOPPED <audit> preflight-final`, exit 2, nothing spent); then `measure` and `judge`. A step whose delivery is not there yet ends the run with `WAITING <audit> <step>` and exit 5, nothing spent; running the command again resumes at that step and never repeats a recorded one Verify: planted halves: (a) a thin domain in round 1: the first pre-flight is refused and recorded, `WAITING <audit> checker-1`, then after the notes `WAITING <audit> writer-2`, then after a repaired round 2 and notes `XCHECK-r2`, the run goes on to the judged figure with the final pre-flight ok; (b) all accepted and the first pre-flight ok: no round 2 is asked; (c) a round 2 still thin in a domain: `void` ends the half (`STOPPED <audit> void 2`, exit 2, no `USED`, no measure); a refusal only the final pre-flight sees (a subsystem over its maximum after `void`): `STOPPED <audit> preflight-final`, exit 2, no `USED`, no measure; (d) a second call after a stop repeats no recorded step (the ledger holds one first pre-flight line) [P-FRESH-80-1 §6 F-1; JOB-20261116-17''s cycle; the CTO''s decision 4]'
  - 'S8 One command for a whole fresh 80 on a pinned snapshot it builds: `gov memaudit fresh --sets-root <R> --repo <D> --commit <rev> --tag <YYYYMMDD[b-z]>` names the two halves from the tag (`memory-audit-<YYMMDD>` and `<2k+1:02d>` for the visible half, `<2k+2:02d>` for the hidden half, k from the letter), clones the repository at the commit (no hard links, a detached clean tree) into `<runs-dir>/fresh/<tag>/repo`, builds that clone''s own store with the rebuild command (`--rebuild-cmd`, default `gov rebuild` in the clone), measures and judges each half on that store, and releases the visible half after its measure into `<runs-dir>/fresh/<tag>/visible/`; the repository''s own store, tree and index are not touched; a tag whose audit names exist without its run folder, or whose run folder holds another commit, is refused (`FR-NAME`); the run folder is outside the sets root Verify: a planted repository with a store file and a dirty-looking index: the store''s bytes and the repository''s `git status` are identical after; the clone is at the commit with a clean tree; the rebuild stub ran in the clone only; the visible half''s files are copied after its measure and the hidden half is not; a reused tag is refused [DEC-1210 (1), A17; the CTO''s decision 2]'
  - 'S9 The briefs are filled from the configuration: `gov memaudit brief --kind writer|checker --sets-root <R> --audit <A> --commit <rev> --repo <D> [--round 1|2] [--since <rev>] --out <dir>` writes `<dir>/brief.md` (never printed), and for the writer `<dir>/input/selection.json` (`commit`, `last_audit`, `seed_sha256`, `changed`, `sample`; paths tracked at the commit, less the file''s `exclude`; `sample` of 300 or fewer drawn with a seed that is also written to `<dir>/seed.txt`, `seed_sha256` its sha256) with a copy as `<set>/selection.json` in the sets root (the record the pre-flight''s draw check reads), and for round 2 and for the checker `<dir>/input/set/` (the delivered questions) and for the writer''s round 2 `<dir>/input/notes.md` (the round-1 notes); the brief names the repository, the pinned commit, the half size, the categories with their quotas and their `about` text, the domains (with the writer''s result''s `by_area` counted in the domain names and `none`, F-2), the subsystems, the spread numbers and the paths to leave unread and uncited; it holds no category, domain or subsystem name of another repository; it prints one line `BRIEF <kind> round <n> <12 hex of its sha256>` and appends a `brief` event to the audit''s ledger Verify: the briefs of Gov OS''s file and of the planted second repository: each category name and quota of the file is in its brief and none of the other''s; `by_area` lists the file''s domains and `none`; the selection''s lists exclude the `exclude` paths and its `seed_sha256` is the sha256 of `seed.txt`; `<set>/selection.json` equals the folder''s; a round 2 writer folder holds the set and the notes; the line has no path; the Gov OS brief''s differences from `governance/project/indep-briefs/memory-audit/writer.md` and `checker.md` are listed in `docs/changes/W2-204-evidence.md` [the CTO''s decision 3, F-2]'
  - 'S10 Delivery by command: `gov memaudit deliver --kind writer|checker --sets-root <R> --audit <A> --repo <D> --from <dir> [--round 1|2]` takes a session''s `out/` folder: a writer''s `out/result.json` (`questions`, `by_kind`, `by_area` each summing to `questions`, `by_area` keyed by the configuration''s domains and `none`) and `out/set/q*.yaml` (plain files only) into `<set>/hidden/`; round 1 refuses when `hidden/` already holds files (`DL-EXISTS`); round 2 moves the round-1 files to `<set>/r1/` first, so no stray reaches the pre-flight; a checker''s `out/notes.md` (the form of the checker brief: `# Cross-check notes`, `## Questions` with one line per id, `## The set`) into `<set>/XCHECK-r<n>.md`; a result or notes that fail their form give `DL-RESULT`, `DL-NOTES` or `DL-SET` (exit 1, nothing copied); it prints counts only Verify: planted out folders: a good writer delivery lands 40 files and prints `DELIVER writer round 1 files 40`; a `by_area` keyed in another repository''s areas, a by_area that does not sum, a file named `notes.txt` in `out/set`, a symbolic link and a second round-1 delivery are each refused with their code and the set unchanged; round 2 leaves `hidden/` holding only the new files; notes missing `## Questions` are refused [the CTO''s decision 3, F-2]'
  - 'S11 The steps are on the CLI: `gov memaudit` has `preflight`, `void`, `declare`, `measure`, `judge`, `figures`, `brief`, `deliver`, `check` and `fresh` beside `scan`, each taking the flags of `python3 -m gov.memaudit <step>` (`void` gains `--repo`) and ending with the same exit code (0 ok, 1 refused, 2 void or stopped, 3 used, 4 usage, 5 waiting); `scan` is unchanged; `python3 -m gov.memaudit` still runs every step it ran, and now `brief`, `deliver`, `check` and `fresh` too Verify: one planted world driven twice, by `python3 -m gov.memaudit` and by `gov memaudit`: the same lines and exit codes for `preflight`, `void`, `declare`, `measure`, `judge` and `figures`; `gov memaudit --help` lists the eleven names; the existing `gov memaudit scan` cases pass unchanged [the CTO''s decision 2]'
  - 'S12 The transcript scan closes the measure: after both halves are judged, `fresh` runs the scan for each half over the window from the earliest `brief` event of that half''s ledger (or `fresh --since <ISO time>`) to now, with `--projects` and each `--allow-session` passed on, and prints `SCAN <audit> clean` or, on a finding, `MEASURE VOID <audit>`, exit 2 and no `FRESH VERDICT` line Verify: a planted transcript folder with no finding: two `SCAN <audit> clean` lines and the verdict; a planted transcript that names the hidden half''s question id as a whole token: `MEASURE VOID <audit>`, exit 2, no verdict line; the same transcript allowed with `--allow-session` is clean [EMERGENCY-2 §2.7, §5.3; DEC-1214 E3]'
  failure:
  - 'F1 A real session or the true sets: no test starts a writer, checker, reader or grader, runs a measure or a rebuild of a shared store, or opens anything under `~/gov-os-eval`; every set is planted under the test''s own temporary folder Verify: the tests'' own guard (the planted home, the fake gov and claude) and a check that no path of the true home is opened [the CTO''s decision 6]'
  - 'F2 The comparability breaks: the reader''s or the graders'' prompt, schema, model or cap changes, or a model is substituted Verify: `tests/unit/memaudit/test_prompts.py` passes unchanged; `git diff` of `src/gov/memaudit/prompts.py` and `src/gov/memaudit/claude.py` against the base is empty [DEC-1098; the CTO''s decision 5]'
  - 'F3 A line of any command or a file outside the run folder holds a question, a gold answer, a source or an answer of a delivered half Verify: planted unique strings in the questions, notes and result files do not appear in stdout, stderr, `FIGURES.json`, the digest, the ledger or any file outside the run folder and the briefs'' own folders; `say` stays the only printer [DEC-1101 (2); F1 of W2-170]'
  - 'F4 Gov OS''s repository measures as it did: a category, domain, subsystem or control that is not in a repository''s own file is never taken from Gov OS''s Verify: a question of the second repository labelled `kernel-template` is `PF-FORM`; a half with no `docs/DECISION_REGISTER.md` question is not `PF-SPREAD` for a missing Gov OS domain [the CTO''s decision 1]'
non_goals:
- 'the reader''s and graders'' prompts, schemas, models and caps (DEC-1098); no model substitution reaches them'
- 'the walls launcher `indep_launch.py` and Gov OS''s approved briefs under `governance/project/indep-briefs/` (pinned by sha); the product does not launch the writer or the checker, the adopter''s CTO does (DEC-1214 E3)'
- 'the standing set, `maintain`, `push`, `pool`, `classes` and the cron wrapper except that they read the configuration where they read the old tables'
- 'the adopt skill''s step 6 and the practice record (W2-188): the CTO decides their new text (EMERGENCY-2 §3.5); the evidence record names what they should now say'
- 'a real fresh 80, a real rebuild of a shared store, a real model call'
done_when: [DOD-1, DOD-2, DOD-3]
sources: [EMERGENCY-2, DEC-1210, DEC-1214, DEC-1098, DEC-1101, DEC-1097, DEC-1204, DAEO-0cd2, DAEO-zlog]
acceptance_tests:
  path: tests/acceptance/W2-204/
  author: independent-test-designer (MR-3); written before implementation
track: A
---
# W2-204 The memory measure runs on any adopted repository, by product commands

EXAMIN's CTO found (its F-032, 2026-11-19 01:45) that `python3 -m gov.memaudit` holds Gov OS's own repository as
constants (`tables.py` DOMAINS, SUBSYSTEMS, QUOTAS; `measure.py` the control set and its fixed figure 34), so no adopted
repository can go from a question set to a judged figure; EMERGENCY-2 §8.2 item 3 needs EXAMIN's copy at 95 % or better
end to end on a fresh 80, measured as Gov OS's is. Gov OS's own first fresh 80 stopped on the same module
(JOB-20261116-15; P-FRESH-80-1 §6 F-1 and F-2). W2-187 (the weekly audit) and W2-188 (the adopt skill's step 6) are
reopened by EMERGENCY-2 §6.1; the fixes to W2-187's driver are recorded in `.tickets/DAEO-0cd2.md`, the new feature is
this ticket (EMERGENCY-2 4.6).

## The CTO's decisions (not to be reopened)

1. The domain table, subsystem table, categories with quotas and the control set with its baseline move into
   `governance/project/memory-audit.yaml` (schema `template/governance/kernel/schemas/memory-audit.schema.json`). Gov OS's
   file holds today's constants. No silent default. A subsystem by path or by record key.
2. The steps an adopter runs are on the CLI under `gov memaudit` and one command runs a whole fresh 80 on a pinned snapshot
   it builds. `python3 -m gov.memaudit` keeps working.
3. The writer and checker are independent fresh sessions the adopter's CTO launches; the walls launcher stays Gov OS's.
   The product gives the filled briefs and takes the delivered halves from the sets root.
4. F-1 and F-2 are fixed here (the driver follows the cycle; the writer's result counts areas in the configuration's domain list).
5. The reader's and graders' prompts, schemas, models are not touched.
6. No real session, no measure, no rebuild of a shared store, nothing under `~/gov-os-eval`; the CTO runs the first real
   fresh 80 after the land.

## Interface (the names the tests use; the engineer may add, never rename)

**I1 The file** `governance/project/memory-audit.yaml` (YAML, a closed set of keys):

```yaml
version: 1
repository: Gov OS                 # the display name the briefs use
half_size: 40                      # the questions of one half; the quotas sum to it
categories:                        # ordered; the table order breaks the writer's ties
  - {name: decision, count: 6, about: "a decision or what replaced it (at least 2 are supersession questions)"}
  - ...                            # `nonexistent-id` must be one of them (it is scored apart)
domains:                           # the first row matching the first source path decides
  - {name: decisions, paths: [docs/DECISION_REGISTER.md]}
subsystems:                        # may be []; path rows and record-key rows
  - {name: retrieval, paths: [src/gov/retrieval/**, ...]}
  - {name: capture, record_key: feature, values: [F00]}
spread: {domain_min: 4, subsystem_max: 10}     # optional, per `half_size` as today (ceil / floor, integer arithmetic)
exclude: [archive/**]              # optional: paths a question's source may never be in (PF-EVALNS) and the briefs name
control: {set: memory-retrieval, part: visible, size: 40, baseline: 34, spread: 2}   # baseline an integer or `first`; or `control: none`
```

A pattern ending `/**` matches anything below the folder, a `*` stays inside one name, a bare name is that file (as
`tables._matches` today).

**I2 Loading.** `gov.memaudit.config.load(repo, commit=None)` returns an object with the fields above (the tests read
`.domains`, `.subsystems`, `.categories`, `.control`, `.half_size`, `.spread`, `.exclude`, `.repository`) and raises
`config.ConfigError(code, detail)`; the code is the line's first word. Resolution: the file named by the environment
variable `MEMAUDIT_CONFIG` when it is set (a trial before commit; also how the existing test folders keep Gov OS's
file), else the blob at `commit` in `repo`, else the file in `repo`'s working tree. The refusal lines (`say` prints them;
exit 1): `MA-CONFIG-MISSING write governance/project/memory-audit.yaml`, `MA-CONFIG-KEY <path>`, `MA-CONFIG-QUOTA sum <s>
of <n>`, `MA-CONFIG-DOMAIN-EMPTY <name>`, `MA-CONFIG-FORM <path>: <reason>`. `tables.py` keeps its functions but takes the
configuration (`spread(first_paths, config, at=None)`, `thin_domains`, `heavy_subsystems`, `domain_min`, `subsystem_max`).
The apart category stays the one name `nonexistent-id` (the matcher scores it apart).

**I3 CLI.** `gov memaudit <step>` delegates to `gov.memaudit.__main__.main([<step>, ...])` and ends with its exit code
(`CHILD_EXIT_CODE`); `EXIT` gains `waiting: 5`. New steps (also under `python3 -m gov.memaudit`): `check --repo <D>
[--commit <rev>]` (prints `CONFIG ok half <n> categories <k> domains <k> subsystems <k> control <set|none>`), `brief`,
`deliver`, `fresh`. `void` gains `--repo` (default the top level), and for a record-key subsystem reads the audit commit
from `PREFLIGHT.json`.

**I4 `fresh`.** `gov memaudit fresh --sets-root R --repo D --commit REV --tag YYYYMMDD[b-z] [--runs-dir DIR]
[--rebuild-cmd CMD] [--gov EXE] [--claude EXE] [--gate-cmd CMD] [--since <ISO time>] [--projects DIR] [--allow-session ID]...`.
State per half is derived from the sets root (the delivered files, the recorded `PREFLIGHT.json` and its `set_digest`,
`XCHECK-r<n>.md`, `DROPS.json`, `USED`, `FIGURES.json`); the driver opens no question file's text and prints counts only.
Lines: `FRESH plan: visible <audit> hidden <audit> at <12 hex>`, `SNAPSHOT <12 hex> store built`, `STEP <audit> <step> ok|refused|skipped`,
`WAITING <audit> <step>`, `STOPPED <audit> <step> [<code>]`, `SCAN <audit> clean`, `MEASURE VOID <audit>`, `FRESH VERDICT hidden ...`,
`FRESH BESIDE visible ...`. Exit 0 done, 1 refused, 2 stopped, 5 waiting. Steps in order: `writer-1`, `preflight-1`,
`checker-1`, `writer-2`, `checker-2`, `void`, `preflight-final`, `measure`, `judge`. Round 2's delivery is told from the
set's digest differing from the first pre-flight's `set_digest`; the checker's from `XCHECK-r2.md`. The state of the
run is `<runs-dir>/fresh/<tag>/COUNTS.json`.

**I5 `brief` and `deliver`** as S9 and S10 state. The brief text is a template shipped in `src/gov/memaudit/briefs/`
filled from the configuration; it follows the approved Gov OS briefs' sections (jobs, folder, what to read, what never to
read, rules, round 2, output, result, stops) and counts `by_area` in the domain names and `none`.

**I6 Existing test folders.** The configuration is what every existing test needs and their planted repositories hold
none: `tests/conftest.py` (or the two folder conftests) sets `MEMAUDIT_CONFIG` to Gov OS's own file for every test by
an autouse fixture; the new `tests/acceptance/W2-204/` tests delete it where they test a repository's own file. This is
the only change to existing test files, made by the independent test designer with a `Rewrite-Reason`.

## What the evidence record holds (`docs/changes/W2-204-evidence.md`)

- the diff of the generated Gov OS briefs against the approved `writer.md` and `checker.md` (the `by_area` change is expected);
- EXAMIN's `memory-audit.yaml` as written from its proposal (domains decisions, tasks, specs, reports, code; features F00 to F06
  by record key; the categories for 40; `control: none` or `baseline: first`; `exclude` its archive, wave 0 audits,
  `.gov-runtime` and `product/data`);
- the exact commands EXAMIN's CTO runs after `gov update`, from the briefs to the judged figure;
- what W2-188's adopt skill step 6 and the practice record should now say (for the CTO).

## Added by the lead at the land (2026-11-19)
Refusal codes the build added beyond the lines above, so that each refusal names itself: `BR-NOSET` and `BR-NONOTES` (`brief`: the
delivered set or notes it must copy are not there), `FR-SNAPSHOT` (the snapshot's clone or store could not be built or does not
match the commit), `FR-LOCK` (another `fresh` holds the tag's run folder), and `STOPPED <audit> scan 3` (a transcript in the scan's
window could not be read). `say` lets exactly two whole lines of `fresh` hold the word `hidden` (`FRESH plan: ...`, `FRESH VERDICT
hidden ...`); every other use of `hidden` is still refused. The configuration's environment variable is `MEMAUDIT_CONFIG`
(no `GOV_` prefix: the planted worlds of W2-171, W2-172 and W2-187 strip `GOV_` variables from their children).

**Closed at the land, 2026-11-19 06:04 (the CTO; EMERGENCY-2 4.3 step 5):** merged as 7c4d9f3ab (branch `e2/memaudit-adopted` at a65783b0d). On the merged tree, through the slot with workers: `tests/unit/memaudit`, `tests/unit/optin` and the acceptance folders W2-204, W1-32, W2-61h, W2-81, W2-88, W2-94, W2-170, W2-171, W2-172, W2-187, W2-188, W2-198: 2,690 passed, 13 skipped; `gov accept W2-204`: 169 passed, 0 failed (again 169 of 169 on W2-200's landing branch). `gov memaudit check` on this repository: `CONFIG ok half 40 categories 12 domains 5 subsystems 7 control memory-retrieval`. `prompts.py` and `claude.py` unchanged by the merge (DEC-1098). The CTO's rulings on the lead's lines: `say.py`'s two `FRESH` lines and the variable name `MEMAUDIT_CONFIG` stand; `fresh` keeps its plain rebuild of the snapshot. Owed (the CTO's): the adopt skill's step 6 and the practice record's text (the evidence record §4); the choice of briefs for Gov OS's own first fresh 80. For the owner: release 0.1.4, so EXAMIN gets these commands by `gov update` (R-1).

## Fix: the transcript scan's id match (EXAMIN's F-033)

Found 2026-11-20 by EXAMIN's CTO on release 0.1.4 (`REQUESTS.md`, "2026-11-20 15:1x"): `gov.memaudit.scan` matched a set's
question ids (`q01`..`q40`, the stems of its files) as bare whole tokens in every transcript of the window. Such tokens are
in any session that numbers things, so a dummy set of 40 empty files nobody read gave `MEASURE VOID: 20 finding(s), 27
transcripts read`, and every fresh 80 ended void after the writers, checkers and the measure had run. Ordinary work lost.
The rule the scan serves is unchanged (EMERGENCY-2 2.7, A-12): the scan reads **every** transcript written in the window
(none is left out by session or folder), looking for the set's path and its question ids; a set that was read voids the
measure. The fix changes what counts as having read the set, not which transcripts are read. Kind: a fix, no new ticket;
the ticket stays closed. The failing tests come first (`tests/acceptance/W2-204/`, S13 to S16). Code is C3
(`src/gov/memaudit/**`): test designer Opus, engineer Sonnet (the C3 trial).

Terms. *The set's names*: the components of the set's real path that read `memory-audit-<8 digits>` or
`memory-standing-<8 digits>` (the audit name), and the eight digits of each (the tag). A set whose path holds none uses
its own folder's name (the parent's when the folder is `hidden`) when that name is at least 8 characters, and has no tag.
A name or tag counts as a whole token (not inside a longer letter, digit or underscore run), as ids do today. *A
question's key*: the question's own text (its `question` field, read from the set's `*.yaml` files by the scan's code,
never printed or kept in a result), normalised (all whitespace runs one space, trimmed, lower case) and cut to its first
48 characters; a question whose normalised text is under 24 characters has no key (too short to be specific: 24
characters is about four words; 48 is long enough that two different questions do not share a prefix, short enough to
survive a line that cuts the text). A file that cannot be read is a problem (the scan's exit 3 rule); one that holds no
question text has no key and is not a problem.

- **S13 (M1) A bare id is not evidence.** A question id (`q07`) counts as a finding only when the same transcript line
  also names the set by its audit name or its tag. A line with the id and no such name is no finding. Verify: a planted
  projects folder whose transcript holds a line for each of `q01`..`q40` (as a chat) and a dummy set of 40 files
  nobody read: `gov memaudit scan` exits 0, `no transcript in the window names the set`; the same folder plus one line
  `<tag> q07` (and one with the audit name and `q07` in another transcript): exit 1, `MEASURE VOID`, each finding
  naming that line's transcript, `kind=id`, `match=q07`.
- **S14 (M2) A question's text read is evidence.** A transcript line whose decoded text values hold a question's key
  (compared normalised the same way) is a finding of kind `text`, whose `match` is the question's **id**, so a session
  that read the file's contents is caught without the path. Verify: a planted transcript holding one question's text
  (spread across a different whitespace, or in another case, or after other text): exit 1, `MEASURE VOID` naming the id
  and the transcript, the text printed nowhere (stdout, stderr, `--json`); a transcript holding text that is no
  question's: clean; a question under 24 normalised characters gives no text finding.
- **S15 (M3) The path counts as today; nothing printed holds a question's or answer's text.** Every path form the scan
  knows (absolute, `~/`, `$HOME/`, the `fixtures/evaluation/` part) is a finding of kind `path` as before, and so is a
  question id file path; the scan's output and result hold ids, kinds and transcript paths only. Verify: the existing path
  cases of `tests/acceptance/W2-198` and `tests/unit/memaudit/test_w2_198_scan.py` stay green (those that planted a bare
  id as the evidence are rewritten to M1's rule, a `Rewrite-Reason` each); a case with a question's text and gold
  answer in files and in a transcript: no output holds either.
- **S16 (M4) EXAMIN's case, end to end.** A dummy set of 40 empty `q<nn>.yaml` files; a window of busy transcripts (bare
  ids, numbered lists, other sessions' work) and one line, in a session outside the measure, where the dummy's path is
  typed: `gov memaudit scan` finds that one line (kind `path`) and no other, exit 1 (the path is still evidence); the same
  window without the path line: exit 0. Verify: both runs through `gov memaudit scan --set <dummy> --since <ISO>
  --projects <planted>`; the `fresh` close (`SCAN <audit> clean`) agrees on the second.

**Landed:** merged into `w2/integrate` at `cc857b977` on 2026-11-20 by hand (the CTO); on the merged tree W2-204, W2-198, W2-208 and the memaudit and opt-in units: 653 passed. EXAMIN's reproduction on the real transcripts: VOID with 1,025 findings on the base, clean on the fix. For release 0.1.5.

## Fix: the strict forbidden-citation rule in the product's own grading (DEC-1227 D5 (a))

Found in the 0.1.4 proving run (`docs/emergency-2/W2-81-PROVING-RUN-0.1.4-ANALYSIS.md`, rows T7 and line 169): W2-81's
scorer counts an answer wrong when it cites a forbidden (stale, superseded, legacy) source; the product's
`judge.one` sets `citation_right` from gold alone and `prompts.outcome` has no forbidden concept, so 24 of the proving
run's 30 misses would have been graded right by the product. The owner (DEC-1227 D5 (a)) keeps W2-81's strict rule and
applies it to the product's own measure, so EXAMIN's 95 % is graded the way the proving run is. Kind: a fix, no new
ticket; the ticket stays closed; `Fix:` trailer. The test designer's cases are red on the base first. Code is C3
(`src/gov/memaudit/**`); every helper Sonnet (DEC-1225).

W2-81's rule, which the product now follows: `citation_right = (a cited place holds a gold line) and (no cited path is a
forbidden path)`; the answer is right only when the grade is `correct` and `citation_right` (a path matches a forbidden
path by equality, as W2-81's `cited` does). Correct + gold + forbidden cited = wrong. `prompts.py` stays untouched (its
hash is pinned by `test_prompts.py`): the rule lives in `judge.py`'s `citation_right`, which `prompts.outcome` reads.

- **S1 A question may name forbidden sources.** A question file may hold `forbidden: [<repository path>, ...]` (a list of
  non-empty path strings, W2-81's shape; absent = none). Verify: a set with and without the field both load and pass the
  pre-flight; a malformed one (not a list, an empty list item, a non-string item) is `PF-FORM`, naming the question's id.
- **S2 Citing a forbidden source makes the answer wrong,** whatever the grader says. Verify: planted grades through
  `judge`: correct + gold cited = right; correct + forbidden cited = wrong; correct + gold and forbidden cited = wrong;
  grade wrong = wrong; no forbidden list = as before. One function (`gov.memaudit.matcher`) holds the rule, and a
  parity test pins it against W2-81's `judge_question` on the same planted cases.
- **S3 The question writer is told to name the forbidden sources** where a stale or superseded source exists for a
  question (the generated writer brief's form and rubric text; the checker's input form names the field). Verify: the
  generated briefs hold the `forbidden` field and the instruction; kernel text is untouched.
- **S4 The record says it.** `FIGURES.json` holds `forbidden_rule: "strict"` and `misses.forbidden_cited` (the
  forbidden-cited misses counted apart, a subset of `misses.total`) (the five printed verdict lines are unchanged). Verify: a
  planted run with a forbidden citation gives the count 1 and the key; with none, 0.

## Fix: the figure carries a stamp, and a figure without it is not compared (F15)

Found 2026-11-22 (fixes-015a): `FIGURES.json` named no release, commit or model, so a run of one release could be set beside a
figure of another, and a strict-rule run (D5) could be declared with no question that carries a `forbidden` list, a rule that
then cannot fail. Owner-fixed: no opt-out flag. Kind: a fix, no new ticket; the ticket stays closed. Failing tests first:
`tests/acceptance/W2-204/test_w2_204_fix_figure_stamp.py` (README ids success-17 to success-19; 8 red, 2 guards on the base).
Code: `FIGURES.json` and the printed run carry `release` (`pyproject.toml` version), `commit` (the declared audit commit),
`reader_model`, `grader_models`, `forbidden_rule`, `questions_with_forbidden` (`figures.py`, `judge.py`; the fresh run's
stamp line goes to standard error through `say.say_stderr`, so its two verdict lines keep their form, `fresh.py`); a standing
line copies the stamp (`driver.py`); `declare` refuses with `DC-FORBIDDEN` when no question carries a list (`declare.py`);
`standing.drift` returns `comparable: false`, `missing: [...]` and `word: null`, and writes nothing, when either the fresh
figure or one of the four lines lacks a stamp key (`standing.py`). Fixtures: the planted question sets carry a `forbidden` list
(`tests/unit/memaudit/conftest.py`, `w2_171_world.py`, `w2_204_support.py`: the first question, when no spec lists one, and
not when a case passes its own specs to `prepare`, so S18's case stays red-to-green), the stamp keys in the key-set pins of
`test_judge.py` and `test_w2_171_s6_figures.py` and in W2-171's expected figures, the stamp on the planted lines of
`test_standing.py` (each marked `# Rewrite-Reason:`). Verified: `tests/unit/memaudit`, W2-171, W2-204: 738 passed, 1 skipped,
1 failed (`test_fix_s3_guard_kernel_template_prompts_and_claude_are_the_merge_base_s_files`, red on the base: it diffs against
`2f0c07bcb`, and `w2/integrate` holds the models-rubric merge after it).

## Fix: declare notices, never refuses, a set with no forbidden list (fix-dc-forbidden, 2026-11-24)

F15 made `gov memaudit declare` refuse (`DC-FORBIDDEN`) a set where no hidden question carries a `forbidden` list; W2-187's
standing sets have none, so 42 cases failed in the 0.1.5 full suite. The CTO's ruling: a set with no forbidden list is
legitimate. `declare` now never refuses for it: it prints `NOTICE DC-FORBIDDEN-NONE: no question carries a forbidden list;
the strict rule grades as the lenient rule would`, and `DECLARATION.json` carries `forbidden_lists: <count>`; verdict and
exit code unchanged. Two further causes of the remaining W2-187 reds, found on the way: the fresh figures line printed by
`digest.figures` omitted the six stamp keys, so `standing.drift` never compared a real fresh run ("DRIFT not yet"), now
copied from FIGURES.json; and W2-187's planted standing lines carried no stamp (fixture stamped). Tests: W2-204 S18 revised
(Rewrite-Reason in its commit), W2-187 `std_line` stamped.

## Fix: the pre-flight refuses a store behind HEAD (plan item 0-2; phase0-memory, 2026-11-24)

Found 2026-11-22 (I-9): a memory measure ran against a store 664 paths stale. DEC-1245 (2), DEC-1241 G-1. The rebuild of
Gov OS's live store is the CTO's chore, not this fix.

- **P0-2 (success).** `gov memaudit` pre-flight refuses `STORE_BEHIND` when the integration store's commit is not the
  repository's HEAD. Verify: a planted behind-store makes the pre-flight exit with `STORE_BEHIND` naming the store's commit
  and HEAD and writes no declaration (`DECLARATION.json` absent); a store at HEAD passes the check as before.
  Failure: the pre-flight passes (or a declaration is written) while the store is behind HEAD.
  Tests: `tests/acceptance/W2-204/test_w2_204_p0_2_store_behind.py`.

## Fix: the fresh 80's writer loop (I-23 with EF-9, I-18, I-19; fix-memaudit, 2026-11-24)

Found by EXAMIN's memory measure on 0.1.5 (FINDINGS I-18, I-19, I-23; EF-9): 5 of 11 halves were refused at pre-flight 1, a pair
was lost at the final pre-flight, three clean re-rolls were each refused on a different code. Causes confirmed in the code:
`deliver.py` `_writer` checks only `result.json`'s sums and the `q<nn>.yaml` names and count (`DL-RESULT`, `DL-SET`), never the
per-question checks of `preflight.run`, and the writer has no shell; `brief.py` `run` copies only `XCHECK-r1.md` into the round-2
writer's `input/notes.md` and renders the same template for round 2, so `PREFLIGHT.json`'s refusals never reach either round-2
brief; `fresh.py` `half` runs the void step only when its half is reached in turn, and `stop`/`__main__.main` print a bare code or
`ERROR: UsageError`. Kind: a fix, no new ticket; the ticket stays closed.

- **FM-1 Every writer's questions are form-checked by code before its session ends, and a refused question goes back to the same
  writer to fix** (the owner, 2026-11-24, Q-7). `gov memaudit brief --kind writer` writes into the session folder a Claude Code
  `Stop` hook (`.claude/settings.json`) that runs `gov memaudit writer-check`; the hook runs, by `preflight.py`'s own functions, every
  per-question check (`form_ok`, `PF-COMMIT`, `PF-DRAWN`, `PF-SOURCE`, `PF-EVALNS`, `PF-DUPPOOL`, `PF-IDEXISTS`) on `out/set/`, and the
  set-level ones (`PF-COUNT`, `PF-QUOTA`, `PF-SPREAD`) once the half is complete, and blocks the stop with a reason that names each
  refused id and its code only (never a question's text, gold or sources). The session ends when the files pass, or after 3 returns,
  when it ends and the refused ids are recorded (`out/` is not written; the sets root's run folder holds `WRITER-CHECK.json`).
  `gov memaudit deliver --kind writer` runs the same checks and refuses with `DL-PREFLIGHT` and codes only. A half that passes the
  writer's check passes pre-flight 1 on the same files. Verify: planted sets, one refused case per plantable code through the hook and
  through deliver; a clean set ends at once; the fourth stop is allowed; delivered then `preflight` ok on the same files.
- **FM-2 Round 2 sees pre-flight 1's refusals (I-23).** When `PREFLIGHT.json` records a refusal, `gov memaudit brief --round 2`
  (writer and checker) appends a section `## Pre-flight 1 refusals` listing each refused id with its code (a set-level code on its own
  line), and the writer's section tells it to repair or replace exactly those. Codes and ids only. A round 2 after a clean pre-flight 1
  carries no such section. Verify: planted half refused at pre-flight 1, both round-2 briefs.
- **FM-3 A void is said at once (I-18).** `gov memaudit fresh` runs both halves' void count as soon as the last checker notes are there,
  before any measure or judge of either half; a half that cannot keep the minimum prints
  `VOID <audit> <VOID-COUNT|VOID-DOMAIN> kept <k> dropped <d> need <min>` and `STOPPED <audit> void 2`, exit 2, no measure. Verify:
  planted pair, visible clean and hidden void: no measure of the visible half is started.
- **FM-4 A stop names its cause (I-19).** Every `STOPPED` line of `fresh` is preceded by `CAUSE <audit> <step> <CODE>: <reason>`; an
  `FR-*` refusal is followed by a `CAUSE` line; a usage fault prints `CAUSE fresh FR-USAGE-<NAME>: <reason>` before `ERROR: UsageError`.
  Codes, ids and counts only. Verify: one planted stop per kind (final pre-flight refusal, void, measure used-marker, bad tag).
- **FM-5 The check runs in every real writer launch (fix-memaudit-3, 2026-11-24; gates 0.1.6).** Launch paths: (a) the adopter CTO's
  `claude -p` in the folder `gov memaudit brief --kind writer` writes: the brief prints the exact launch line (`LAUNCH writer <command>`,
  also `LAUNCH.txt` in the folder; `--restricted --setting-sources project --settings <out>/.claude/settings.json`, never `--safe-mode`),
  so the Stop hook of FM-1 loads; (b) Gov OS's walled writer (`indep_launch.py`): the wall's `settings.json.tmpl` carries the same Stop
  hook (`writer` kind only), filled from the launch's own sets root, set, commit, repository and wall; the template's sha256 is the
  owner's to enter in `APPROVED`; (c) a launch that loads no hooks (`--safe-mode`): `gov memaudit writer-run` holds the loop by code
  (the session started with a kept session id, `writer-check` run after it, a refusal resumed into the same session with its ids and
  codes only, at most 3 returns, never a fresh writer). In each, a refused question goes back to that writer with its ids and codes
  only, at most 3 returns, and the refused ids are recorded in `WRITER-CHECK.json`. Verify: unit cases for the launch line, the wall's
  rendered settings and `writer-run` with a planted session seam; one real `claude -p` Sonnet writer, launched as the product prints,
  on a planted 2-question set with one form fault in a temporary folder: the transcript shows the refusal returned and the fixed file
  accepted, and `WRITER-CHECK.json` shows `returns` 1 and `ended` pass.

Hidden-set protections unchanged (EMERGENCY-2 §2.7): nothing printed or logged names a hidden question's text, gold or sources.

## Fix: the fresh 80's launch lines and the writer check's visible record (I-33, I-37, I-38; memaudit-launch, 2026-11-26)

Found by EXAMIN's fresh 80 on 0.1.7 (EF-13; FINDINGS I-33, I-37, I-38). Causes confirmed in the code: `say.py` `refused` refuses any
line holding a folder word (`fixtures/`, `runs/`, `indep-walls/`, `hidden`) as a substring, and `brief.py`'s `LAUNCH writer` line holds
the CTO's own `--out` and `--repo` paths (both already checked to lie outside the sets root), so an `--out` under e.g. `gov-os-runs/`
or in a folder named `hidden-writer` is refused (exit 4, the refusal on both streams) after `LAUNCH.txt` is written; `brief.py` `run`
writes and prints the launch only `if kind == "writer"`; `writercheck.check` writes `WRITER-CHECK.json` only in the audit's run folder
on the sets-root side and a clean pass prints nothing. Kind: a fix under W2-204, no new ticket; the ticket stays closed. Approved by
the CTO in the lead's brief (`docs/emergency-2/briefs/LEAD-memaudit-launch.md`).

- **ML-1 (I-33) The writer brief prints its launch line and exits 0.** `gov memaudit brief --kind writer` prints one `LAUNCH writer
  <command>` line after its `BRIEF` line and exits 0 wherever `--out` and `--repo` lie outside the sets root, a path holding a folder
  word included; the line never holds the sets root's path. The refusal to print a line naming the sets root's path, or any other line
  holding a folder word, stays. Verify: planted `--out` under `gov-os-runs/` and in a `hidden-writer` folder, and a `--repo` under such
  a path: exit 0, no `REFUSED`; `say` still refuses a line naming the sets root, a `LAUNCH` line holding it included.
  Failure: exit 4 or `REFUSED` where nothing of the sets root is named; a line holding the sets root's path is printed.
- **ML-2 (I-38) Every kind has its launch line.** `brief --kind writer` and `--kind checker`, round 1 and 2, print exactly one
  `LAUNCH <kind> <command>` line and write `<out>/LAUNCH.txt`, whose content is the printed command byte for byte (plus one newline).
  The checker's command loads no `Stop` hook, carries the checker's tools (read, search, write: `Read,Grep,Glob,Write,Edit,TodoWrite`;
  no shell, web or subagent), asks no permission prompts and grants Write and Edit into `<out>/out/` only. Verify: the four planted
  briefs. Failure: a kind or round without the line or the file, the two differing, or a checker session that loads the writer's hook.
- **ML-3 (I-37) The writer's session folder shows the check ran.** `gov memaudit writer-check` also writes `<folder>/WRITER-CHECK.json`
  with exactly `returns`, `ended` and `refused` (each refused code with question ids only, never a question's text, gold answer or
  source), at every call (a clean pass, each return, the limit); the run folder's record stays as it is. A folder record that cannot be
  written changes neither the hook's block nor the run folder's record. Verify: planted pass, refusal and limit through the hook
  command; one real `claude -p` Sonnet writer launched from a planted `LAUNCH.txt`: `<out>/WRITER-CHECK.json` exists with `ended` set.
  Failure: no record in the session folder after the hook ran, or a record holding more than counts, codes and ids.

## Fix: forbidden-reach, whether the forbidden sources an audit's misses cited are now outside default memory (DEC-1254 E-02's note; forbidden-reach, 2026-11-26)

The owner (DEC-1254 E-02): "confirm EXAMIN's three stale citations leave default memory under the amended rule". Which sources
were cited sits only under the sets root, which no session but the measure's own reads (DEC-1249 (2)), and no `gov memaudit`
command reports it: `judge.py` records `forbidden_cited` (a bool) and the attempts' citations in `reader/<id>.json`, and
`figures.py` keeps the count alone. Kind: a fix under W2-204, no new ticket; the ticket stays closed. Approved by the CTO in the
lead's brief (`docs/emergency-2/briefs/LEAD-forbidden-reach.md`).

- **FR-1 `gov memaudit forbidden-reach --sets-root R --audit <name> [--repo D]`** reads the audit's judged rows
  (`<R>/runs/<name>/reader/<id>.json`); for each row with `forbidden_cited` true, the cited forbidden sources are the paths of the
  final answer's citations (the last attempt whose verdict is `answer`, `search_again` or `not_found`) that are in that question's
  `forbidden` list (`<R>/fixtures/evaluation/<name>/hidden/<id>.yaml`), each counted once per row. Each is resolved against the
  repository's current path map (`--repo`, default the top level; the working tree's file): **outside** default memory when a
  namespace holding it states a `stale_class` or `lexical_policy: not indexed`, or the repository no longer tracks the file;
  otherwise **inside** (`embedding_policy` alone does not take a file out: the keyword route still finds it). It prints one line of
  counts only, `FORBIDDEN-REACH <c> cited, <o> outside, <i> inside; <holder>: <n>, ...`, the holder being the namespace that takes
  the source out, else the first namespace holding it, `unmapped` for none and `untracked` for a file no longer tracked; holders in
  name order, the `; ...` part absent when nothing is cited. Never a path, a question or an id, and every line goes through `say`.
  Exit 0 on a readable audit (0 cited included). `REACH-NOAUDIT` (no run folder for the audit), `REACH-NOROWS` (no judged row) and
  `REACH-NOSET` (a row with `forbidden_cited` true whose question file is missing or unreadable, or whose citations and list share
  no path) are each printed as the only line, exit 1. It writes nothing. `gov.retrieval` (and D3's classifier,
  `gov.retrieval.stale.classifier`, where the tree has it) is reused, never copied. Verify: a planted sets root and repository whose
  audit has three misses citing forbidden sources in two namespaces, one stale-classed `not indexed`/`not embedded` and one live:
  `3 cited, 2 outside, 1 inside` with the namespaces; after the live namespace gains the class, `3 outside`; the output holds no
  planted path, question or id.
