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
