---
type: probe
task: DAEO-c1uz
reviewer_session: e72d5ea1-4a16-4a13-807d-6e7b1aeadd8f
implementer_session: 095ec0a8-8144-4df2-a2aa-090c7fb19b86
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 6eb5a93f4332b0cf97b3a51f95292bfb1083b139
---

# Probe record: DAEO-c1uz (W2-66), path-scoped regression at close: the third and last FULL review (DEC-912 items 3 and 4)

## The lead's note

- **Commissioned and judged** by the ticket lead (an orchestrator-role session in this ticket's worktree, DEC-137). The reviewer was a fresh `independent-auditor` session (`e72d5ea1-4a16-4a13-807d-6e7b1aeadd8f`, 2026-10-24), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max. It wrote nothing: the lead's tripwire before and after its session shows no change in this worktree.
- **The earlier reviews.** Review 1 (session `f631a982-c0fb-4c27-b234-2bb0e7aed92b`, head `9174e358`) failed on F1 to F3; review 2 (session `9f0502c7-515a-473e-9831-10c2a8c62ae3`, head `5634d430`) failed on P1 and P2. Their records stay drafts. The owner allowed this third review by DEC-912 item 3 and made it the last (item 4).
- **The lead's verification at the probed head** (`6eb5a93f4332`, after a full rebuild): collection 16,426 of 16,428 tests (2 deselected), no error; `gov check` exit 0; the full parallel run in the close's form 16,131 passed, 30 skipped, 0 failed (49:46); the serial-only cases 265 passed (16:08).
- **Verdict: pass.** Classification (DEC-809): 0 findings "yes" with "fails open" or "loses work"; rows R1, R2, R5, R6, R7 no / fails open; R8 no / loses work; R3, R4, R9 yes / other; one feature-gated row (DEC-803). The lead's judgement agrees. It also checked R7's premise: the new ticket W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**` only, not the scanner's configuration files.

## What was probed
- **Head:** `6eb5a93f4332` on `w2/W2-66`, worktree `/home/usain/gov-os-worktrees/W2-66`.
- **The change since the second review** (head `5634d4305a7c`, which failed on P1 and P2):
  - The test designer's `e9c639f19bd4` (P1's cases, `test_w2_66_unresolved_targets.py`) and `952193aecd00` (P2's live-map cases), with the README's "Interface" items 1, 3 and 6 revised.
  - The engineer's `73a402771ec2`: the selection resolves each selected map target in the committed head and widens with `UNRESOLVED_TARGET`.
  - The engineer's `0f0f6cb2acd5`: the live map couples every Python source under `tests/acceptance/` to `tests/acceptance/W1-28/test_w1_28_fixture_copies.py`.
  - The orchestrator's checkpoint `6eb5a93f4332`.
- **The merges:**
  - `02b62e033a10`: `w2/integrate` (DEC-910 to DEC-912, W2-69's secrets work, run 3's KPI lines).
  - `052a3b9b05c9`: W2-70's round 2, `3ff8ba51b3ed` (W1-01's merge rule, DEC-912 item 1).
  - No close module but the selection changed: `nightly.py`, `evidence.py`, `command.py`, `gates.py`, the schema and the template map are as at `5634d4305a7c`.
- **Method:** the code was run, not only read:
  - the real resolution on every live target and on node-id shapes in a throwaway repository;
  - the real selection on the live tree for 19 changed paths, with the base and the change put in memory and nothing written;
  - three real `gov close` runs in W2-66's fixture project;
  - W1-28's check file collected;
  - W2-66's whole acceptance suite and the close unit tests;
  - the nightly's worktree cleanup on a throwaway repository.

## Who probed
A fresh independent-auditor session (`GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-c1uz`), read-only on the repository and sandboxed: the write outside the worktree was refused, and git object writes worked. Effort max. No guard refusals and no read refusals. `gov retrieve` was used once, on planned changes to the gitleaks and path-map templates.

## Threat model
ADR-0001: the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Every finding is judged by the two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?". Only "yes" with "fails open" or "loses work" fails the probe.

## The earlier findings at this head
- **F1, answered.** The change is read with rename detection off; the three moved-file cases pass.
- **F2, answered.**
  - On the live map, `tests/conftest.py` and `tests/acceptance/conftest.py` run the full regression (`SHARED_CORE`).
  - `governance/project/orchestration/sync_context.py`, `docs/plan/tools/validate_s1.py` and `docs/contract/contract.yaml` run full (`UNPLACED`).
  - The overlap rule reads each ticket's declared folder.
- **F3, answered.** A change to W1-07's or W1-25's conftest selects `tests/acceptance/W1-27/test_w2_67_copies.py`.
- **F4, answered.** Each deselected case is named in `left_out` (31 for a typical change).
- **F5, answered.** W2-67's close names `tests/acceptance/W1-27/` as its own suite, and none of its files is left out.
- **F6, answered.** The map's note matches the selection: `apply_adapter_output.py` is placed by W1-42; the two scripts only tickets without a suite hold run full.
- **P1, answered.** A selected record-reading, every-close or coupling target that the committed head does not hold widens the run to the full regression and is named with its reason. This holds for a file renamed or gone, a function, class or method renamed, and a folder gone:
  - the acceptance cases cover a renamed function, every-close file and coupled file, the refusals that follow, and the targets that resolve;
  - the unit cases cover a method gone and a folder gone;
  - this probe covered a renamed class.

  A target that resolves does not widen, and a coupling the change does not reach widens nothing. Resolution reads the committed head; since the close refuses a working tree that differs from it, the run tests what was resolved. All 54 live targets resolve at this head.
- **P2, answered.** The coupling's pattern matches all 732 tracked Python files under `tests/acceptance/`, at any depth, in a new or a hidden folder. On the live tree, a change to a suite's conftest, a helper module, a test file or a new folder's conftest each selects the check file by coupling, neither ignored nor deselected. The file holds the four scanning cases the README names (18 cases collected), and W1-28's other files are named as left out.

## The two risks the workers named
- **A parameter set whose id is renamed still resolves: sound, not fail-open.**
  - What was done: the every-close target named one parameter set; the ids were renamed before the base, and the renamed set checks the widget. Then the change broke the widget.
  - What happened: the close stayed scoped, ran the whole function (both renamed sets) and was refused (exit 3) on the renamed set's red.
  - The record keeps the map's spelling of the target under `selected`, as the README's interface reads a parameter set as its function. The JUnit XML names what ran.
- **A case inherited from a base class, or defined in an `if` or `try` block, is judged gone: it widens; row R9.**
  - The same holds for a case named through a class alias, and for a parameter id holding `::`.
  - The fixture close with an inherited target ran full (`UNRESOLVED_TARGET`, `CASE_GONE`) and passed.
  - No live target has these shapes today.

## Findings
None that is "yes" with "fails open" or "loses work".

## Rows

### R5: A folder target still resolves after its record-reading file moved to another suite folder (low)
- **What was done:**
  - The fixture map's record-reading set named W1-rr's folder.
  - W1-rr's record-reading file was moved into a new suite folder before the base; W1-rr kept its README and another test.
  - An orchestrator's record-only commit then broke the register, followed by the ticket's one-module change and the close.
- **What happened:**
  - The folder target resolves, because the folder still holds files.
  - The close passed (exit 0, scoped).
  - The new folder was left out (`NOT_REACHED`), and the moved record-reading case did not run.
- **What should have happened:** a folder target resolves only while it holds a test file, as a ticket's suite does for the overlap rule; or the moved case joins the set.
- `Ordinary work: no, because no test file has moved between suite folders in this repository's history, and a record-reading test in a new place is the set's own upkeep (KPI 5's first list), corrected by the nightly's selection-miss package.`
- `Consequence: fails open`

### R6: The map's literal paths are not checked at the head (low)
- **What was done:** read how shared-core members and coupling paths are matched; ran the live selection.
- **What happened:**
  - P1 checks targets only. A shared-core member named by its file (the eight retrieval modules, `src/gov/config/loader.py`, `src/gov/tasks/tickets.py`, `src/gov/store/loader.py`, `src/gov/cli/main.py`, `src/gov/cli/errors.py`) or a coupling path named by its file (`src/gov/retrieval/rerank_worker.py`, `src/gov/retrieval/retrieve_check.py`, the gitleaks configurations) would match nothing after a rename.
  - The rename's own close sees the old path and runs full or the coupled suites. Later changes to the renamed module run scoped.
- **What should have happened:** a literal map path that names no file at the head widens the run, or is named, as a target does.
- `Ordinary work: no, because no source file the map names has been renamed or moved in this repository's history: the only rename under src/, template/ and tests/ is W2-69's tests/unit/secrets/ folder, and the only deletion under src/ is a hook pair the hook patterns cover.`
- `Consequence: fails open`

### R7: Fixture inputs that no coupling takes to the suites that read them (low)
- **What was done:** the live selection for a change to each of four template inputs, and a search of the suites that read them.
- **What happened:**
  - A change to `template/.gitleaks.toml` or `.gitleaks.toml` runs scoped. It selects W1-15 and the eight coupled suites. It leaves out W1-40 and W2-50, which read the template's rules and which lens I's list missed, and W2-69, merged since the map was written, which copies them into its fixtures.
  - A change to `template/governance/project/path-map.yaml` selects W1-39 only. W2-50, W2-58 and W2-69 build their fixture path maps from it.
  - A change to `template/governance/kernel/checks/secrets-indexing.yaml` leaves out W2-69, which reads the check's command and time limit.
- **What should have happened:** the map couples each input to the suites that read it (KPI 3's fixture inputs).
- `Ordinary work: no, because none of these inputs has changed in Wave 2 (the gitleaks configurations last on 2026-10-04, the check declaration on 2026-10-10, the template path map on 2026-10-08), no open ticket holds either gitleaks configuration, and the open tickets that hold the other two change what these suites override or do not read (W2-06's KPIs move checks between tiers, while W2-69 reads only the declaration's command and time limit; W2-23 adds namespaces for adoption moves, while W2-50 and W2-69 set their own docs and src namespaces, W2-58 adds evaluation sets, and the loaders refuse no overlap).`
- `Consequence: fails open`

### R8: The nightly's cleanup prunes every worktree whose folder it cannot see (low)
- **What was done:** read the nightly's cleanup. In a throwaway repository: a second worktree with a staged change was hidden, the same prune command was run, and the worktree was put back.
- **What happened:**
  - The nightly ends by removing its own temporary worktree and then pruning all worktree records of the project's repository.
  - The hidden worktree lost its admin folder and its staged change; git answered "not a git repository" there.
- **What should have happened:** the nightly removes only the worktree it added.
- `Ordinary work: no, because it needs a worktree folder that is missing or hidden when the nightly ends (moved, unmounted, or outside the running sandbox's view); the sessions here read the worktrees' parent folder, and the fixture runs prune only their own repositories.`
- `Consequence: loses work` (the hidden worktree's index and its link to the repository)

### R9: A named case that is inherited, defined in an `if` or `try` block, or reached through a class alias is judged gone (low)
- **What was done:** resolution of those shapes, and a fixture close with an inherited every-close target.
- **What happened:** each is judged gone (`CASE_GONE`), and the close runs the full regression until the map names the case where it is defined.
- **What should have happened:** as the README states, the safe direction; worth knowing for the map's upkeep.
- `Ordinary work: yes, because moving shared cases into a base class or under a guard is ordinary test refactoring.`
- `Consequence: other` (a needless full run; nothing passes that should fail)

### R1, carried: a renamed helper imported inside a function is not followed
- The code that follows helpers is unchanged since the second review.
- `Ordinary work: no, because no acceptance helper module has been renamed or deleted in this repository's history, and module-level imports are refused at collection.`
- `Consequence: fails open`

### R2, carried with its reason updated: `pyproject.toml` is placed by W1-07 alone
- At this head, 26 suites read the file, most for the `gov` console-script entry point.
- One open ticket now holds it: W2-59 (DAEO-kh9l, in progress), for package data only.
- `Ordinary work: no, because W2-59 changes package data only and its close runs the full regression through its shared-core paths (src/gov/check/runner.py, src/gov/cli/main.py); the file has not changed since W1-07 (2026-10-03), and the project keeps its pytest settings in tests/conftest.py, which is shared core.`
- `Consequence: fails open` (once a ticket outside the shared core changes its entry point or adds a pytest section)

### R3, carried: F7, the nightly's bisect names the range's first commit when the red test is new
- The nightly is unchanged since `5634d4305a7c`; not re-run.
- `Ordinary work: yes, because a newly added red test is an ordinary red.`
- `Consequence: other`

### R4, carried: an unreadable check result holds back a counted refusal by one run
- `command.py` is unchanged since `5634d4305a7c`; not re-run.
- `Ordinary work: yes, because a mistyped path is ordinary.`
- `Consequence: other`

### Row (feature-gated, DEC-803): the check result is taken as given
- Unchanged: only W2-66's fixture reads the variable.
- `Ordinary work: no, because no live test reads the variable at this head.`
- `Consequence: fails open` (once a reader exists)

## Found sound
- **The new code only widens.**
  - Only selected targets are resolved, and only against the committed head.
  - The evidence block carries the target and its reason in the result, the record and a refusal.
  - The close schema leaves the block open, so the new entries cannot fail a later `gov check`.
- **The template map names no target**, so P1 changes nothing for adopted projects.
- **W2-66's live-map cases** read the list of tracked paths, not record contents. A record file the record-only patterns miss is unplaced and runs full.
- **The tests the merges brought read no record-only path.**
  - W2-69's design-note case reads git history and its own note.
  - W1-01's new whole-repository merge case reads the path map, which is shared core, and git history.
  - Like the MR-3 case, it stays out of scoped closes by KPI 13's design, and the lead's full verification runs it.
- **Helper names are unique across suites**, and no new path-based load of another suite's file has appeared.
- **Acceptance tests:** since `5634d4305a7c`, only test-designer commits change them. The engineer's commits stay inside the ticket's allowed paths.
- **The merge with W2-07, the per-test limit and the retention option:** the code is as found sound at `5634d4305a7c`. W2-66's limit and retention cases pass within the 170.

## Verdict
**pass.**
- F1 to F6, P1 and P2 are answered.
- Both risks the workers named fail safe: a renamed parameter id runs the whole function; inherited and guarded cases widen.
- Every other finding is a row: R5 to R9 new, R1 to R4 carried, and the feature-gated row.
