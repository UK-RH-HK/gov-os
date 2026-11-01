---
type: probe
task: DAEO-9nys
reviewer_session: 5ac658ff-a07d-4fcd-8247-c5d9710f9ba8
implementer_session: 6edef3cd-38c2-4751-88db-fceef0c5c9bf
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: aa4a4a9ef53e972fa58849110389db90714697b0
---

# Probe record: W2-67 (DAEO-9nys), run 7: the disposition case's ids (DEC-970, P-W2-67-R6-DISP (a))

- **What was probed.** Run 6's scoped run found one red this ticket caused: a clean auto-merge (`0568d91baf56`, DEC-954) had given `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure` W2-64's fixture ids (`DEC-9003`, `DEC-9004`) while this ticket's revised assertion still looked for `DEC-cyc1` and `DEC-cyc2`. The CTO decided a second test-design batch and a short review (DEC-970, P-W2-67-R6-DISP (a)). Before run 7 the orchestrator merged `w2/integrate` (`1a8357702abd`) as `0978a976e85f`, a clean auto-merge (its tree equals git's own merge of its parents).
  - **td-11** (independent test designer, session `6edef3cd-38c2-4751-88db-fceef0c5c9bf`, sandboxed through `gov launch`, effort xhigh), in the tests worktree `W2-67-tests` (DEC-963): commit `0d2fc195f449`, the assertion's two ids made the fixture's (+1 −1), `Rewrite-Reason: DEC-954 merge of W2-64`. Case alone: 1 failed before (on that assertion only), 1 passed after; the whole file 1 failed, 15 passed before, 16 passed after.
  - The lead merged the tests branch as `f7ca56a0fbb5` (`--no-ff`, message file) and committed checkpoint CP-DAEO-9nys-0028 as `aa4a4a9ef53e`, the head probed.
  - **rev-7** (session `5ac658ff-a07d-4fcd-8247-c5d9710f9ba8`; role `independent-auditor`, `gov launch` under its OS sandbox, reading tools only, effort max), commissioned and judged by the ticket lead, reviewed `0978a976e85f..f7ca56a0fbb5` on `aa4a4a9ef53e`, plus the two W1-27 files both sides of the clean merge `0978a976e85f` changed (run 6's lesson). **Pass**: no finding that justifies a round; one observation, O1 ("Ordinary work: yes", "Consequence: other").
- **Which review this is.** The review of DEC-970's new round (DEC-916), the last of this change (DEC-413). The earlier records keep their verdicts (`PR-DAEO-9nys.md`, `PR-DAEO-9nys-run3.md`, `PR-DAEO-9nys-run6.md`).
- **The tripwire.** td-11: only the tests worktree changed (its head and `tests/acceptance/W1-30`); rev-7: nothing changed in this worktree; the main tree changed by the orchestrator's own work only.
- **The lead's verification on `aa4a4a9ef53e`** (this worktree's `src/`; `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`):
  - rebuild (under the rebuild lock, never `--no-embeddings`; held 62 minutes by the load wait, a batch close loading the machine): exit 0, `store.invalid: []`;
  - the selection (`select_tests.py`): scope `scoped`, `core_changed` [], `unplaced` [], 36 targets (reasons OWN, OVERLAP, TEST_CHANGED, UNIT, COUPLING, EVERY_CLOSE, RECORD_READING); no "serial"-route entry reached, so no serial phase;
  - the scoped run in the close's form (`-n auto`, `-p gov_close_serial_only`, `--timeout=900 --timeout_method=signal`, `-o tmp_path_retention_policy=failed`, the selection's `--ignore`/`--deselect`), in two parts because a load of 45 to 75 on 20 processors stretched the one-part run past the background run's two-hour limit (the one-part run was stopped at 30%): part A, `tests/acceptance/W1-30`: **537 passed in 881.72 s** (the disposition case among them); part B, the rest of the selection: **4605 passed, 1 skipped, 2 errors in 1567.41 s**. The skip: `tests/unit/retrieval/test_lexical.py:54` (no `govbridge`). The two errors: `tests/acceptance/W2-54/test_w2_54_green_here.py::test_gov_check_gives_core_schema_green_here` and `::test_the_w1_43_audit_report_is_untouched`, both at setup of one session fixture whose `gov check` over this worktree passed the 900 s limit; the same two errors alone (5 passed, 2 errors, 901.31 s, load about 42). The file passed in run 6's scoped run (before the merge `0978a976e85f`); run 7's own change since is one line of a W1-30 case, and no `src/` file of this ticket's; a red this change did not cause, named for the CTO;
  - KPI 4's count: after part A (no red) no base folder of its own was left; after part B (two errors) four base folders (its own, kept for the errors, and three empty nested-session folders);
  - collect-only over `tests`: "18388/18390 tests collected (2 deselected)", exit 0; `gov check`, run twice under the load (13:45 to 14:15 and 16:15 to 16:40, 1-minute load 35 to 80), the same both times: context-reproducibility and retrieval-regression RED at their 600 s time limits, core-decision-citations YELLOW at its 60 s limit, openspec-validate YELLOW (not on PATH), the rest GREEN (core-mutation GREEN now).
- **Threat model (DEC-801, DEC-808).** Every finding is judged by ADR-0001's two questions; only "yes" with "fails open" or "loses work" fails a probe. **The lead's judgement: pass.** O1 (the ids assertion is also met by core-schema's finding on the fixture's single-value `supersedes`, since W2-64's merge, not this change) is "Ordinary work: yes", "Consequence: other" (W1-11's hazard cases pin the cycle's detection): a residual row, no round.

## rev-7's record

task: Independent review at effort max of `git diff 0978a976e85f f7ca56a0fbb5` (one file, +1 −1: the disposition case's ids realigned to W2-64's fixture, DEC-970, P-W2-67-R6-DISP (a)) on head `aa4a4a9ef53e`, ticket DAEO-9nys (W2-67), the last review of this change (DEC-413).
status: DONE. Verdict pass: the fix is right, nothing is lowered by this change, the clean merge `0978a976e85f` keeps both sides with no clash in meaning, and the scope and trailers are as decided; no finding justifies a round.
work_completed: Step 0 sandbox check; identity checks; read the diff, the case, its fixture helpers (W1-30, W1-11), the schema check before and after the W2-64 merge, the decision checker, the close's pre-close gate, the shared frontmatter schema and core-schema's declaration; ran the single case once on the head; read both sides of `0978a976e85f` against their merge base for the two W1-27 files, plus the rebuild lock's code and the harness's lock setup; checked the three commits' scope, parents, tree and trailers.
files_changed: none. Step 0 (b) wrote one blob to the object store as the brief prescribes (`1ae28402a109`); no file of the repository was written and no commit was made.
evidence: `0d2fc195f449` (parent `0978a976e85f`) changes only `tests/acceptance/W1-30/test_w1_30_disposition.py` (+1 −1), trailers parsed by `git interpret-trailers`: Task: DAEO-9nys, Role: independent-test-designer, Implements: DEC-970, DEC-954, Rewrite-Reason: DEC-954 merge of W2-64. `f7ca56a0fbb5` has parents `0978a976e85f` and `0d2fc195f449`; the second parent's parent is the first, so this is a `--no-ff` merge; its tree `887c5622091b` equals `0d2fc195f449`'s tree; trailers Task: DAEO-9nys, Implements: DEC-970, DEC-963, DEC-954, Role: orchestrator. `aa4a4a9ef53e` (parent `f7ca56a0fbb5`) only adds `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0028.md` (23 lines); trailers Task, Implements, Role: orchestrator. The merge base of `0978a976e85f`'s parents is `c07a1115577f` (only one). The reviewed range touches no `src/` file. `gov.__file__` = `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`. TMPDIR before: 9 inodes, 20K; after: 9 inodes, 24K.
tests: `tests/acceptance/W1-30/test_w1_30_disposition.py::test_disposition_with_context_failure`, run once on the head, without `-n`, with this worktree's `src/` on PYTHONPATH, `-o tmp_path_retention_policy=failed -q -p no:cacheprovider`: 1 passed in 22.08 s. Nothing else was run; the file-level and before figures are td-11's (DEC-959 item 1).
discoveries: (1) `gov retrieve` answered `FACET_UNAVAILABLE` during the review: both its lexical and semantic facets are stale, probably while the lead's rebuild runs. (2) The ids assertion is also satisfied by core-schema's hard-block finding that each decision's `supersedes` is a single value where the shared frontmatter schema wants a list. Since the W2-64 merge `0568d91baf56`, the case therefore stays green even if all supersession detection were lost. This came with the merge, not with this change (observation O1). (3) This ticket's W1-30 README (para "The disposition case and PF2") says `core-authority` and `core-graph` are RED for the two decisions; since the W2-64 merge core-schema is RED for them as well. The README names no ids, so what it claims is not stale. (4) No test under `tests/` names `DAG_CYCLE` by its code; W1-26's planted-defect cases mention cycles (I did not read them case by case).
risks: The schema finding naming the ids depends on `check-jsonschema` being on PATH in the case's sandbox (td-11's run shows it is). Without it, core-schema would refuse naming no ids, and the ids assertion would rest on the supersession findings alone, which is stricter, not weaker. My run covered one case; the scoped figures are the lead's.
lessons: When a clean auto-merge renames a fixture's ids, an assertion on the old ids is red for every implementation, and only the scoped run after the merge finds it (run 6). To judge "nothing lowered" for such a realignment, compare which findings name the ids before and after the merge; the one-line diff alone does not show it.
proposed_decisions: none
unresolved: The lead's rebuild and scoped run on `aa4a4a9ef53e` were running while I reviewed; I did not wait for them, and their results go into the probe record beside this verdict.
recommended_next_action: Lead: commit this probe record with the rebuild and scoped-run results on `aa4a4a9ef53e`; if both are green, return run 7 to the orchestrator with no further round.

---

Verdict: pass

**Head probed:** `aa4a4a9ef53e` on `w2/W2-67` (`/home/usain/gov-os-worktrees/W2-67`). Reviewed: `git diff 0978a976e85f f7ca56a0fbb5`, one file, +1 −1.

**Step 0:** (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys` failed with `OSError: [Errno 30] Read-only file system`, as required. (b) `git hash-object -w --stdin` worked (blob `1ae28402a109`) and `git update-index --refresh` exited 0. The sandbox holds. The identity checks matched: `GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-9nys`, the worktree root and branch, and HEAD `aa4a4a9ef53e`. The only untracked files are the placeholder dot-names and `tests/acceptance/W1-27/w2_67_td4_plant.py`.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"` → `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`

**Classification (DEC-809):** 0 findings that justify a round; 1 observation (O1): ordinary work yes, consequence other, so no round and no row proposed.

### 1. The fix is right: sound

- **The assertion matches what the fixture plants.** The case plants two ACTIVE decisions, `DEC-9003` superseding `DEC-9004` and `DEC-9004` superseding `DEC-9003`. The revised assertion requires both ids, exactly as planted, in the whole error object (code, message and details as one string). No `DEC-cyc` string is left anywhere in `src/` or `tests/`.
- **Green on the head.** The single case, run once without `-n`: 1 passed in 22.08 s.
- **Red before only on that assertion.** The reviewed range touches only the test file, so the code under test is identical before and after. Every assertion before the changed line is unchanged and passes on the head, so it passed before too. The changed line then looked for ids that nothing plants, so it was the first and only failing assertion. This matches td-11's figures: 1 failed on the ids assertion before, 1 passed after; the whole file 15 passed and 1 failed before, 16 passed after.

### 2. Nothing lowered: sound

- **Every other line is unchanged.** Against `0978a976e85f`, the diff is the one assertion line; the rest of the case and the file are as they were.
- **The other assertions stand as strong.** They still require:
  - no whole-system context literal;
  - exit 3;
  - no hash in the answer;
  - exactly one repair ticket, recording the class `defer` and no context hash.
- **The schema finding (td-11's note) is a property of the merge, not of this change.** Before the W2-64 merge (`bdc1bb3e1d43`), the schema check held decision records only to the four shared fields and never to their shapes, so no schema finding named `DEC-cyc1` or `DEC-cyc2`. W2-64's full validator (DEC-872 item 2), merged at `0568d91baf56`, now refuses the fixture's single-value `supersedes`. The fixture wrote `supersedes` as a single value before W2-64 too; W2-64 changed only the ids and the WBS. Because core-schema is hard-block and the close lists each hard-block red check's findings verbatim, both ids now reach the refusal through that finding alone. The decision checker, the graph check, the runner and the check declarations are unchanged across the merge.
- **Even before the merge, the ids assertion never pinned the cycle itself.** The checker's "ACTIVE while superseded" finding needs only a supersession edge and ACTIVE status, with no cycle search, and it names each of the two decisions. So "green if the cycle were no longer detected" was already true before the merge.
- **What the merge did take away.** The case's sensitivity to losing all supersession detection. That arrived with `0568d91baf56` and was in the case on `0978a976e85f` before this change.
- **This change could not lower anything.** On `0978a976e85f` the old assertion was red for every implementation, so it caught nothing. The new one is the assertion that tells a refusal naming the planted decisions apart from one that does not.
- **It does not fail open.** W1-11's hazard cases pin the cycle and the "ACTIVE while superseded" finding by code and ids, on fixtures whose `supersedes` are lists. The case's own KPI (A3: the disposition when the context fails) is not the detection of the cycle.

### 3. The clean merge `0978a976e85f` does not clash in meaning: sound

- **Merge base:** `c07a1115577f` (only one).
- **This ticket's side** (W2-67 batch 8):
  - the r8 test imports the code-graph helper and passes the twin project's path through its `note` function;
  - the support file imports it and passes both rebuild-project builders' destinations through it (with a docstring line).
- **W2-76's side:** one line in each file, passing the rebuild-lock override from the test process's environment into the environment of the rebuild run (the r8 file's `gov` fixture, and the support's run helper).
- **Both sides are kept, unaltered.** The merge's diff against its first parent is exactly W2-76's two lines, and its diff against its second parent is exactly this ticket's hunks.
- **No assertion of either side looks for what the other changed:**
  - `note()` returns its root unchanged and only records the code index's daemon folder (`/tmp/gov-cbm-<uid>/<16 hex>`) for removal after the case.
  - The override is a flock file path (`src/gov/rebuild/watch.py`), unrelated to those daemon folders.
  - The harness makes its lock file with `mkstemp` in the session temp folder before any test runs (`tests/conftest.py`), so a rebuild's flock creates no file. That file lies outside the folders this ticket's revised case `test_the_mode_writes_only_under_gov_runtime` snapshots: the project, `sandbox/home` and `sandbox/elsewhere`, all under the case's `tmp_path`.
  - W2-76's lines assert nothing.
- I only read these files; the lead's scoped run executes them.

### 4. Scope: sound

- **`0d2fc195f449`** touches only the disposition file and carries Task: DAEO-9nys, Role: independent-test-designer, Implements: DEC-970, DEC-954 (decision ids) and Rewrite-Reason: DEC-954 merge of W2-64.
- **`f7ca56a0fbb5`** is a `--no-ff` merge: a fast-forward was possible, and its tree equals `0d2fc195f449`'s, so it adds nothing. It carries Task: DAEO-9nys and Role: orchestrator.
- **`aa4a4a9ef53e`** only adds `docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0028.md`.

### Observation O1 (informational, no round)

- **What was done:** an honest engineer's possible regression of the supersession-cycle detection, judged against the revised disposition case.
- **What happens:** the close's refusal still names both planted decisions, through the schema check's finding that each decision's supersession is a single value where a list is required. The ids assertion holds, so this case stays green; since the W2-64 merge it would stay green even if all supersession hazards were lost.
- **What should have happened, for this change:** nothing different. The change realigns the ids as DEC-970 decided; the detection of the cycle is the W1-11 cases' KPI, not this case's.
- **Severity:** informational (P3).
- Ordinary work: yes, because an honest engineer refactoring the decision checker or the graph check could drop the cycle's detection in ordinary work, and this case alone would not turn red.
- Consequence: other (W1-11's hazard cases still turn the suite red on such a regression, so nothing fails open and no work is lost; the case's own KPI stands).

### Scratch, refusals, retrieval

- **Scratch:** TMPDIR `/tmp/gov-launch-independent-auditor-e4pyafrj/claude-1000` was 9 inodes and 20K before the probe run, 9 inodes and 24K after. The retention policy removed the case's numbered folder after the pass, leaving an empty `pytest-of-usain`. `-p no:cacheprovider` kept `.pytest_cache` out of the worktree, and `git status --short` was unchanged after the run.
- **Read refusals met:** 0. Every search started at a named folder.
- **`gov retrieve`:** used once, for which check finding names a decision whose `supersedes` is a single value. It answered `FACET_UNAVAILABLE` (lexical and semantic facets stale), so I read named files directly.
- **Code-graph tool:** not offered in this session (no `trace_path`, `search_graph` or `query_graph`). Code questions were answered with targeted searches in `src/gov/check`, `src/gov/decisions`, `src/gov/close` and `src/gov/rebuild`, and in the W1-07, W1-11, W1-26, W1-27 and W1-30 test folders.
