The record follows.

```
task: Review 1 of W2-170 (DAEO-61vm): a fresh, read-only FULL probe of head ad664fc87755 against S1-S6, F1-F5 and Interface sections 1-10
status: PACKAGES. One finding is in scope, reachable in ordinary work and fails open, and the code matches the Interface's own DC-PREFLIGHT rule, so the fix needs a CTO decision (DEC-1052) before the engineer's one fix pass
work_completed: Read the ticket, the package's sections 3.3-3.4, the writer and checker briefs (source-path and notes forms), all nine memaudit modules, the unit conftest, the acceptance world module, the S3 acceptance flow, the test-map change, and the launch script's round-2 delivery. Ran 6 probe processes on planted worlds under TMPDIR (10 worlds built and removed).
files_changed: none
evidence: Step 0: (a) the write to the worktrees folder FAILED with "Read-only file system"; (b) `echo sandbox-trial | git hash-object -w --stdin` returned 1ae28402a109, and `git update-index --refresh` worked; GOV_ROLE=independent-auditor, GOV_TICKET=DAEO-61vm. Head at start ad664fc87755 and at end ad664fc87755. gov.__file__ = /home/usain/gov-os-worktrees/W2-170/src/gov/__init__.py. Session id: probably 528369a4-afcf (from the sandbox's task path). TMPDIR at end: 20K, 8 inodes; every planted world removed. Read refusals met: 0. One Write-tool refusal (a probe script under TMPDIR): not retried, not worked around; the probes ran as inline `python3 -c` commands instead. Step 0 left two loose objects in the shared object store (the empty blob e69de29bb2d1 and 1ae28402a109), as the brief asks. `git status --porcelain` is empty at the end.
tests: none run (the lead's gov accept and unit runs not repeated); 6 probe processes on planted roots only
discoveries: In the package's own order (section 3.3: writer round 1, then pre-flight, checker round 1, writer round 2, checker round 2, drop), writer round 2 delivers a whole new set into hidden/; the launch script moves round 1's files aside. `declare` accepts any PREFLIGHT.json with ok true, so the set that gets measured may never have been pre-flighted (RV1, reproduced).
risks: If W2-170 merges as is, a round-2 question with a missing source, the wrong commit, a source under an evaluation namespace, a draw outside the lists, a pool duplicate or an existing id is declared and USED is written; the set is then measured once and cannot be re-run.
lessons: Probes of a gate must follow the cycle's real order (round 2 replaces the set), not only the single-pass order the acceptance tests use.
proposed_decisions: PKG-W2-170-R1-PREFLIGHT-FRESH (to the CTO, DEC-1052). Options: (a) PREFLIGHT.json records each file's sha256 by id, and DC-PREFLIGHT also refuses when a kept file is not byte-equal to a pre-flighted one. About 20 lines; the S3 acceptance flow (pre-flight, void with drops, declare) stays green. (b) Leave W2-170 as is and make "pre-flight re-run after writer round 2" an entry criterion of W2-172's cycle, with a row here. (c) DC-PREFLIGHT requires PREFLIGHT.json's digest to equal the current one; this breaks S3's acceptance flow, so the designer would have to change it. Recommend (a), confidence medium-high.
unresolved: RV1 awaits the CTO's choice, then the engineer's one fix pass in this round (DEC-1133 (4)). The lead's own gov accept on ad664fc87755 was not seen by me.
recommended_next_action: The CTO decides PKG-W2-170-R1-PREFLIGHT-FRESH (recommend (a)); then one engineer fix pass and re-check S1/S3 on the new head.
```

task: DAEO-61vm
decisions: DEC-1101 (1), DEC-1125 (2), DEC-1052, DEC-801, DEC-803, DEC-808, DEC-1010, DEC-1014, DEC-1133
probed_commit: ad664fc87755bd16f3a0509db2b3ca8b0de2dedf

## Scope
- **In scope:** the KPI lines S1-S6, F1-F5 and Interface sections 1-10, with the engineer's readings P1-P5.
- **Out of scope (named by the lead):** the measure (W2-171), the cycle and the schedule (W2-172), the launch script's follow-ups (W2-173), and the files the merge of `w2/integrate` brought in.

## Method
- Read every memaudit module in full, plus the unit conftest, the acceptance world module, the S3 acceptance flow, the briefs' forms, the package's section 3.3, and the launch script's round-2 delivery (by search).
- Built worlds with `w2_170_world.build` under TMPDIR: an empty HOME, every root flag explicit, this tree's own `src/`.
- Six probe runs:
  1. Revised files after a clean pre-flight, then void and declare (and a control that pre-flights the same revisions).
  2. Source-path spellings (`./`, `//`, `..`), an empty or missing heading with lines outside the file, and pool gold sources in another order.
  3. Verdict spellings, a second line for one id, a short line, a missing line, an id not in the set.
  4. A crash halfway through void, and a same-name file already in `dropped/`.
  5. Declare: digest against the shell's `LC_ALL=C sha256sum *.yaml | sha256sum`, file times, ledger, all three subcommands after `USED` (whole-tree snapshot), a re-run after a crash between the two files.
  6. The test-map change and F5's diff.

## Probed and found sound
1. **S1:**
   - A typo'd category is refused by PF-FORM, and at n = 40 also by PF-QUOTA.
   - A missing or renamed source is refused by PF-SOURCE (and by PF-DRAWN when drawn).
   - A missing heading with lines outside the file is refused.
   - `//` and `..` spellings fail closed: `..` is caught by PF-EVALNS as well.
   - A pool question with the same gold sources in another entry and alternative order is refused by PF-DUPPOOL.
   - PF-IDEXISTS matches whole tokens and is case-sensitive as `lexical.whole_id` states, so `W2-17` is not held by `W2-170`.
   - The clean set ends `PRE-FLIGHT: every check as expected`.
2. **S2 and F4:**
   - `Accept`, `accept ` with a trailing space, ` accept`, two lines for one id, a four-field line and a missing line are all dropped and moved, counted `UNFIT` or `NOLINE` or by their codes. A line for an id not in the set is ignored.
   - A re-run gives `DR-DONE`.
   - A void audit gets `DC-PREFLIGHT`/`DC-DROPS`, with no `USED` and no `DECLARATION.json`.
   - A same-name file in `dropped/` stops the run before anything moves (`ERROR: FileExistsError`, exit 4); the old file is kept and no `DROPS.json` is written.
   - After a crash halfway, the re-run's kept count and scales are correct.
   - The checker brief's notes form matches the parser.
3. **S3 and F2:**
   - The ledger reads `preflight, drop, declaration, used`, and `DECLARATION.json`'s mtime is earlier than `USED`'s.
   - The set digest equals the shell's.
   - After `USED`, preflight, void and declare each exit 3, and no byte or mtime changes in the sets root or the repository.
   - A crash between the two files: the re-run declares again, the map entry stays single, and declaration/used are appended again. It neither refuses forever nor measures without a declaration.
   - The bar for n = 36..40 is 31/1/35, 32/1/36, 33/1/37, 34/1/38, 34/2/38, by integer ceil and floor.
   - Pool off gives `DC-DECISION`, `ok: false`, no `USED` and no map entry.
   - The real `retrieval.yaml` holds no reranker, bundle or search-again key, so reading only `pool` loses nothing.
4. **S4 and F3:**
   - The entry is inserted once, every other byte is kept, a second audit's entry sits beside the first, and the repository's `git status` stays empty.
   - No default points at the real sets root (`--sets-root` is required). `--runs-dir`'s default `~/gov-os-runs` is the Interface's own; the unit tests set HOME to tmp_path and drop `GOV_INDEP_RUNS_DIR`.
5. **S5 and F1:**
   - Every failure prints only `ERROR: <class>`; git's stderr is captured; YAML errors are swallowed into the form check; warnings are off.
   - The JSON files hold ids, counts, codes and digests only.
   - `say` refuses the folder words before printing (P1).
6. **S6:** the coupling `src/gov/memaudit/**` → `tests/unit/memaudit/` is explicit, and `--help` goes through `say`.
7. **P1-P5:** each as built and consistent with the Interface.
8. **F5:** `git diff --name-only w2/integrate...ad664fc87755` lists only the allowed paths and the designer's acceptance tests. The two-dot diff also shows `DECIDED-NOT-DONE.md`, but only because integrate moved on afterwards (`08f51ea8c`).

## Findings

**RV1: the measured set need not be the pre-flighted set** (scope: in, S1)
- **What was done:** a clean set was pre-flighted (all ten ok). Then, as writer round 2 does, q05 got a source that does not exist at the commit, q06 got the earlier commit, and q08 got a second source under `fixtures/evaluation/`. The checker's round-2 notes accepted all; void was run, then declare.
- **What happened:** void exit 0 ("kept 40 dropped 0"); declare exit 0 with "USED written", `ok: true`. Pre-flighting the same three files directly refuses PF-COMMIT q06, PF-DRAWN q05, PF-SOURCE q05 and PF-EVALNS q08.
- **What should have happened:** no `USED` for a set whose current files were never pre-flighted.
- **Why it is reached:** the package orders pre-flight after writer round 1 only, and round 2 replaces the whole of `hidden/`. Declare's gate, as the Interface states it, checks only that PREFLIGHT.json says ok.
- Ordinary work: yes, because round 2 is the normal path whenever checker round 1 finds a revise or reject, and the writer brief has the writer re-anchor, re-word or pick a new path then.
- Consequence: fails open
- **What would reverse it:** a stated rule (in the package, W2-172's ticket or the launch script) that pre-flight is re-run on the delivered set after writer round 2, before void and declare, and that declare is reached only through that cycle. Or a decision that checker round 2's judgement replaces the mechanical checks for round-2 files.

**RV2: a `./`-prefixed source under an evaluation namespace passes** (scope: in, S1)
- **What was done:** a second source `./fixtures/evaluation/old-set/hidden/a.yaml` was added to q03.
- **What happened:** git resolves `./` against the repository root, so PF-SOURCE passes. The path map's glob does not match a `./` form, so PF-EVALNS passes too.
- **What should have happened:** a PF-EVALNS refusal; alternatively, PF-FORM refuses a path that is not in normal form.
- Ordinary work: no, because the writer copies paths from git's lists (never `./`), and its tree excludes `fixtures/evaluation/**`, so it cannot open such a file.
- Consequence: fails open. A Wave 3 row.
- **What would reverse it:** the writer being able to see evaluation-namespace files, or briefs that write paths with `./`.

**RV3: an empty heading passes with lines outside the file** (scope: in, S1)
- **What was done:** q09's source was given `heading: ""` and lines 900-990 in a short file.
- **What happened:** PF-SOURCE passes, because the empty heading equals any blank line of the file.
- **What should have happened:** a refusal: the heading is not really found, and the lines lie outside the file.
- Ordinary work: no, because the brief makes the heading "one whole line of the file", and a writer without a heading leaves the key out.
- Consequence: fails open. A Wave 3 row.
- **What would reverse it:** sets in practice holding empty headings.

**RV4: after a crash halfway through void, the re-run's record under-counts the drops** (scope: in, S2)
- **What was done:** q01 was moved by hand, as a crash would leave it; then void ran with notes that drop q01, q02 and q03.
- **What happened:** `DROPS.json` says dropped 2, `by_code {R2: 1, R4: 1}`, while `dropped/` holds 3 files. Kept 37 and the scales are correct; nothing is lost.
- **What should have happened:** the count covers every file in `dropped/` that the notes do not accept.
- Ordinary work: no, because a kill must land in the milliseconds between two renames.
- Consequence: other. A row.
- **What would reverse it:** a void that can stop for a long time mid-move.

**RV5: PF-IDEXISTS refuses a nonexistent-id question that also names a real id** (scope: in, S1; found by reading)
- **What was done (read):** for a question like "What does DEC-9999 add to DEC-1101?", every id-shaped token is checked.
- **What happens:** the existing DEC-1101 refuses the question.
- **What should happen:** the question passes, if only the asked id counts. This matches the Interface's words "an id-shaped token".
- Ordinary work: yes, because such context is a natural way to write the question.
- Consequence: other (fails closed; the writer rewords). A row.
- **What would reverse it:** a CTO reading that any existing id in the question is meant to refuse.

**Classification:** 1 yes/fails open (RV1); 1 yes/other (RV5); 3 rows (RV2, RV3, RV4).

**Recommendation:** RV1 blocks. Its fix needs the CTO's choice in PKG-W2-170-R1-PREFLIGHT-FRESH (recommend (a)); then one engineer fix pass in this round.

```verdict
{"kpis": [{"kpi": "S1", "verdict": "fail", "findings": [{"id": "RV1", "scope": "in", "ordinary_work": "yes", "consequence": "fails open"}, {"id": "RV2", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "RV3", "scope": "in", "ordinary_work": "no", "consequence": "fails open"}, {"id": "RV5", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "S2", "verdict": "pass", "findings": [{"id": "RV4", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "S3", "verdict": "pass", "findings": []}, {"kpi": "S4", "verdict": "pass", "findings": []}, {"kpi": "S5", "verdict": "pass", "findings": []}, {"kpi": "S6", "verdict": "pass", "findings": []}, {"kpi": "F1", "verdict": "pass", "findings": []}, {"kpi": "F2", "verdict": "pass", "findings": []}, {"kpi": "F3", "verdict": "pass", "findings": []}, {"kpi": "F4", "verdict": "pass", "findings": []}, {"kpi": "F5", "verdict": "pass", "findings": []}]}
```