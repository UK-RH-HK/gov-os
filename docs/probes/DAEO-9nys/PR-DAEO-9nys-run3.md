---
type: probe
task: DAEO-9nys
reviewer_session: a4262e07-c027-4be9-8255-afc60a8edc20
implementer_session: 00111c40-3d95-4023-bf63-e256d80feebb
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: a74e9c67e913dd41c661e03408aa5fc20197a029
---

# Probe record: W2-67 (DAEO-9nys), rounds 2 and 3 (run 3), the first review (DEC-916, DEC-920)

- **What was probed.** Head `a74e9c67e913` of `w2/W2-67` (the lead's checkpoint record CP-DAEO-9nys-0018; code head `db8d50bb4893`): run 3's whole change, `6d44fc801255..a74e9c67e913` (18 commits, 24 files), rounds 2 and 3 run together (DEC-914). By part: (1) W1-30's 13 first-round cases, each red under its plant (PF2's case shown under PF2b, as recorded), test designer td-6; (2) row W2-L420's docstrings; (3) W2-50's large-store and hang cases against a declared short limit, test designer td-7; (4) TD1C-A's code-graph clean-up in W1-27's fixtures, test designer td-8; (5) KPI 4's static guard and its f-string case (P-W2-67-TD4-A), td-6; (6) the 13 bounded nested-run functions of `tests/unit/close` and P1's `TMPDIR`, engineer eng-4 (`db8d50bb4893`, session `00111c40-3d95-4023-bf63-e256d80feebb`). The reviewer's question: does any revision only look red-then-green, or weaken what a case caught before?
- **Which review this is.** Round 1 was reviewed twice and passed (`PR-DAEO-9nys.md`, head `915a764dd660`, an earlier round's record). Rounds 2 and 3 are declared in the ticket's plan; run together, this one review counts as one review of each (DEC-916). It passes, so no second review is needed.
- **Who probed.** A fresh read-only reviewer (role `independent-auditor`, session `a4262e07-c027-4be9-8255-afc60a8edc20`, 2026-10-25), started through `gov launch` under its OS sandbox with the reading tools alone, at effort max; commissioned and judged by the ticket lead (an orchestrator-role session, DEC-137). It wrote nothing in the repository: the lead's tripwire before and after its session shows no change in this worktree or the main tree (the one change it shows is another ticket's worktree head, W2-72, moved by that ticket's own lead).
- **The lead's run of what the sandbox could not run.** TD1C-A's case needs the code-graph folder, which is read-only inside the sandbox; the reviewer judged it by reading, the lead's plant records and a probe of its own against a stand-in folder, and named the run. The lead ran it at this head outside the sandbox (2026-10-25, `PYTHONPATH` this worktree's `src/`, `-n 3`, `-o tmp_path_retention_policy=failed`): 5 passed in 28.35 s, and the daemon folders under `/tmp/gov-cbm-<uid>` numbered 13,070 before and after (none of the nested cases' projects left). Under the lead's plant (release switched off) the same case was 4 failed and 1 passed, the guard case green by design (run 3's red check).
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Every finding carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; only "yes" with "fails open" or "loses work" fails the probe. **The lead's judgement:** pass. F-A and F-B are "Ordinary work: yes" with "Consequence: other"; neither fails open or loses work, so neither justifies a round. F-A widens round 1's row F3; F-B is a residual on the ticket file's list of named acceptance files. Both are returned to the orchestrator as rows. DEC-920's items are decided and not re-raised.

## The reviewer's record

task: Fresh first review of DAEO-9nys (W2-67) rounds 2 and 3, run together as run 3 (DEC-916), at head a74e9c67e913 (code head db8d50bb4893). Probe for behaviour the tests miss: failing open, losing work, writes outside a role's scope, acceptance tests changed by an implementer.
status: DONE. Verdict pass: two low findings, both rows (Ordinary work: yes; Consequence: other); none fails open or loses work, so no round.
work_completed: Step 0 and the identity checks. Read the ticket, card, DEC-914, 907, 908 and 905, and round 1's review. Diffed run 3 (`git diff 6d44fc801255 db8d50bb4893`, 24 files) part by part against each file at 6d44fc801255. Ran a spy plugin of my own over all of tests/unit/close. Ran the revised cases on the head. Ran PF2 under copies of td-6's carrier and in-process. Probed KPI 4's static guard and TD1C-A's `release()` against stand-in roots in my temporary folder. Read td-6's, td-7's and td-8's plant records, td-6's JUnit records, the lead's plant8 shim and the logs red6, red7 and red8.
files_changed: none. No repository file written and no commit; every probe file is in my temporary folder. My first unit run had no PYTHONDONTWRITEBYTECODE, so it may have refreshed git-ignored bytecode under tests/unit/close/__pycache__/; `git status` is unchanged apart from the known plant file and the sandbox's placeholder device files.
evidence: (1) Step 0: (a) OSError Errno 30, no file made; (b) hash-object wrote 1ae28402a109 and update-index exited 0. (2) gov.__file__ is /home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py. (3) Trailers of run 3's 18 commits: every one has Task: DAEO-9nys and Implements: DEC-914. Roles: independent-test-designer on 16, engineer on db8d50bb4893 (tests/unit/close/** only), orchestrator on a74e9c67e913 (docs/checkpoints/DAEO-9nys/CP-DAEO-9nys-0018.md only). Every commit that revises a case has a Rewrite-Reason. (4) Spy: 26 node ids in 20 functions start a real pytest. 13 functions (19 node ids) run tests, all with -n 1 and a 180 s limit; the time-limit case has 1 s and TMPDIR under its own tmp_path. 7 functions start only serial collect-only runs at 120 s. (5) td-6's after-plant JUnit: each red for its own fault; PF2 passed, PF2b red. (6) Lead's logs: red6 (11 W1-30 plants red, PF2 green, PF2b red, guard plant red, head 31 passed); red7 (5 plants red, head 23 passed); red8 (plant 4 failed and 1 passed, head 5 passed). (7) Scratch: 8 inodes / 24K at start, 55 / 292K before the heavy runs, 137 / 688K after; pytest kept three base folders; peak not sampled, far below my share.
tests: tests/unit/close whole, under my spy, -n 4: 417 passed in 8.47 s. W1-30's 13 revised cases by node id, -n 4: 13 passed in 22.25 s. W2-50's large-store and hang cases (6 node ids), -n 3: 6 passed in 42.42 s. test_w2_67_temp_folders.py's two static guards: 2 passed in 0.20 s. PF2 under td-6's carrier on test_w1_30_context_failures.py, test_w1_30_disposition.py and test_w1_30_r8_test_runs.py, -n 4: 34 passed in 36.18 s. PF2 in-process on test_every_finding.py::test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket: 1 failed (KeyError 'context'); on the head 1 passed. Not run here: test_w2_67_codegraph_folders.py (/tmp/gov-cbm-<uid> is read-only in the sandbox). Every run used -o tmp_path_retention_policy=failed, no --basetemp and no -x.
discoveries: Seven more unit close functions start a nested pytest (serial collect-only, 120 s); they are bounded but not among the 13. Since DEC-868 item 3, PF2 is caught by the unit suite rather than W1-30. The test designer role may write all of tests/acceptance/** (role file line 8), so only review holds a ticket's list of named files. The guard's Bash parser reads a Python `> 1` inside a heredoc body as a redirect to a worktree file. gov retrieve's facets are stale. In the lead's red8 head run the entry count rose by 5 (12,812 to 12,817); the case's per-project check shows these were not the nested cases' folders.
risks: I could not run TD1C-A's own case; I judged it by reading, the lead's records and my stand-in-base probe of `release()`. W2-50's scaled stores cannot show a fault that appears only at real sizes; that cost comes with the KPI's declared short limit.
lessons: In this sandbox, write probe files with the Write tool and give Bash write commands literal absolute paths: the guard parses heredoc bodies and refuses variable paths as unresolvable. A `cd` into a scratch folder moves the session's working directory.
proposed_decisions: No packages. Two rows: F-A widens round 1's row F3 (high confidence); F-B, the ticket file names W2-50's helper and README files, or the card's `W2-50/**` wording is recorded as the scope (medium confidence).
unresolved: TD1C-A's committed case was not run by me; the command is in part 4 below. The inert untracked tests/acceptance/W1-27/w2_67_td4_plant.py is still present (DEC-914 item 2).
recommended_next_action: The lead commits this record as the first review of rounds 2 and 3 (pass), routes F-A and F-B as rows, and returns to the orchestrator.

Verdict: pass

**Head probed:** a74e9c67e913 on `w2/W2-67` (code head db8d50bb4893). Run 3 is `6d44fc801255..HEAD`: 18 commits, 24 files changed.

**Step 0:**
- (a) Writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-9nys` failed: OSError Errno 30, read-only file system. No file was made.
- (b) `git hash-object -w --stdin` worked (1ae28402a109) and `git update-index --refresh` exited 0.

**gov.__file__:** `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -c "import gov; print(gov.__file__)"` gives `/home/usain/gov-os-worktrees/W2-67/src/gov/__init__.py`.

**Classification (DEC-809):** 2 findings, F-A and F-B, both "Ordinary work: yes" and "Consequence: other". Neither fails open or loses work, so neither justifies a round. DEC-920's items (1) to (3) are not re-raised; each revision does what is recorded.

## What was probed and found sound

### 1. W1-30's 13 first-round cases (KPI 5)

- **No expectation lowered.** Against each case's version at 6d44fc801255, every revision adds to what the case asserts:
  - the ticket is checkpointed, so it can't be refused for the missing checkpoint;
  - each refusal must name its own gate's finding (the commit and the `Implements` trailer; `Task: <ticket>` exactly; the failing test by node id; containment's commit and path);
  - the success cases must show the test ran once and that the answer states the run that passed it;
  - the regression case must name and count all 8 owner's failing tests;
  - the receipt case requires an exact hash;
  - the dispositions case gives each of the six names to `gov close` itself.
  - The support helpers the cases use all existed at 6d44fc801255 and are unchanged.
- **Every plant fails for its own fault**, judged from td-6's after-plant JUnit messages:
  - PF1: `owner` is refused with INVALID_DISPOSITION.
  - PF4: the close closed despite W1-50's finding.
  - PF5: the acceptance test did not run, or the close was not refused.
  - PF9: the zero hash does not match the context's hash.
  - PF10: exit 3 instead of 4. The lift was wrongly granted, so the close went on to its failing tests.
  - PF11: 6 of the 8 regression tests are not named.
  - PF12, PF13 and PF15: the close was not refused.
  - PF16: the regression test did not run.
  - PF2b: the repair ticket carries a context hash.
  - The lead's red6 log agrees. On the head, 13 of 13 passed in my run.
- **PF2 against PF2b: the record's choice is right.**
  - The close sets `details["context"]` only when a class is given and its own context step, after the tests, raised CONTEXT_FAILED (`src/gov/close/command.py:355-358`).
  - Since DEC-868 item 3, this case's broken context is refused first by the pre-close gate (context-reproducibility RED, code CHECK_FAILED, `:216`). PF2's line is not on this case's path.
  - PF2 also removes a context, while the case forbids a context that was not built. The fault the case is meant to catch is a fabricated context, which is PF2b, and the case is red under it.
  - I ran PF2 against the three W1-30 files that pass a class: 34 passed. Every refusal the plant met had no `details["context"]`, including the one CONTEXT_FAILED refusal (the checker case, which gives no class).
  - PF2 is still caught where its line runs: the unit case `test_every_finding.py::test_with_a_class_a_context_that_failed_is_a_finding_and_is_named_on_the_repair_ticket` fails under PF2 (KeyError 'context') and passes on the head.
- **PF10's change of input loses no coverage.**
  - The old input, a decision file whose frontmatter is broken YAML, now appears in no acceptance case.
  - `frontmatter()` returns None for broken YAML as well as for no frontmatter (`src/gov/tasks/tickets.py:13-22`).
  - That branch is still held by `tests/unit/close/test_state.py:257-260`.
  - `lift_escalation` refuses in layers: no frontmatter, then type and id, then status, then the checker's findings.

### 2. Row W2-L420's docstrings (a0325f527f06)

Every hunk is inside the two module docstrings. They now state DEC-868 and DEC-908, and the checker case keeps its counted refusal with its reason, as DEC-920 (2) records.

### 3. W2-50's large-store and hang cases (KPI 3)

- **The declared figures are in force.** The check reads `_TIMEOUT_S`, `_FLOOR` and `_LARGE` as module globals at call time (`src/gov/secrets/__init__.py:174`, `:469`), in the process and threads that start gitleaks. Setting them after import therefore takes effect, and `assert_declared` ties every gitleaks run's parent process to a proof line.
- **The cases still measure the same property.** The declared base (4 s) is shorter than the real one (60 s) and the per-byte term is the check's own. A run that passes under the declaration therefore passes under the real check, and a hang fails under both. `_LARGE` is scaled with the store (6.4 MiB against 16 MiB, as 64 MiB is to 160 MiB).
- **The change stays inside these cases.** `sandbox` is per case, and only the named file imports the helper, so the conditional path entry reaches no other case.
- **td-7's five faults all fail.** A fixed limit fails after 4 s on the large store. The other four (later pieces never scanned, halves cut at the middle, a hang taken as clean, a hang recorded clean first) also fail, and each `ran.jsonl` shows the fault acting. The lead's red7 log agrees.
- **On the head:** 6 passed in 42 s at load about 7.

### 4. TD1C-A, the code-graph clean-up

- **Construction:**
  - The folder rule equals `gov.codeintel.daemon_dir`.
  - `CBM_RUNTIME_DIR` reaches the daemon through its environment, so `holders()` can see it.
  - Every builder is function-scoped and under `tmp_path`. W2-69 uses its own support module, so no other suite's roots are noted.
  - Notes made before a case's mark (a wider fixture's) are never that case's to release.
- **My probe of `note()` and `release()` against a stand-in base in my temporary folder** (the real folder was never touched). Each scenario behaves as stated:
  - a folder made during the case is removed;
  - a folder there before is kept;
  - a holder that stops by itself is waited for (3.1 s), then the folder goes;
  - a lingering holder is stopped by SIGTERM, or by SIGKILL if it ignores SIGTERM, then the folder goes;
  - another root's folder, a foreign name and a foreign 16-hex name are kept;
  - a root noted twice is removed once;
  - a wider fixture's note is kept by the case and released by its owner;
  - a link at the folder's name is kept and its target is intact;
  - with two roots, the second is still removed after the first's holder is stopped.
- **The lead's plant is sound.** The shim runs the real module with only `release` switched off. Its red8 log shows 4 failed and 1 passed (the guard case is green by design), then 5 passed on the head.
- **Not reproduced (sandbox).** The run, outside the sandbox: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-67/src python3 -m pytest -q -p no:cacheprovider -o tmp_path_retention_policy=failed -n 3 tests/acceptance/W1-27/test_w2_67_codegraph_folders.py`. It should show 5 passed, and no folder of the nested cases' projects left under `/tmp/gov-cbm-<uid>`.
- **Note, not a finding.** No committed case exercises the "there before" or "link at the name" branches; my probe did, and they hold.

### 5. The static guard's f-string widening (ff4afbeca92e)

- **Found now:** every f-string form inside a list or tuple. That covers plain, raw, implicitly concatenated, split-literal, with a conversion, and inside an `extend([...])`.
- **The exemption is exactly the form's own parameter.**
  - Still exempt: `f"--basetemp={given}"`, `f"--basetemp={str(given)}"` and the separate option.
  - Found: `{given.parent}`, `{given}/sub`, `!r`, a format spec, a fixed folder beside the given one, a nested fixed list, and a second parameter.
- **On the head:** both guards pass. The residual is F-A.

### 6. Bounded nested runs (KPI 2) and P1's TMPDIR

- **The count matches.** My spy over all of tests/unit/close (417 passed) confirms the engineer's 13 functions and 19 node ids:
  - each runs its tests with `-n 1` (or as the serial run after it) and a 180 s limit;
  - the time-limit case keeps 1 s, and its nested run alone gets `TMPDIR` under its own `tmp_path`, which is not shared;
  - the killed run's process group is killed whole (`_started`).
- **Seven more functions** (two in test_measured.py, five in test_governance_checks.py) start only the pre-close collect-only runs. Those are serial with 120 s (`max(timeout, DEFAULT_TIMEOUT)`), so they are bounded too.
- **None is unbounded.** test_follow_up.py and test_every_finding.py start no real run.
- **One worker hides nothing.** None of the 13 passes `told` or `scope`, so the close has no merge across workers for one worker to hide.
- **DEC-914 item 3:** W1-05 starts no nested run now; it only passes a pytest command string to the hook's decision.

### Scope

- The engineer wrote only `tests/unit/close/**`.
- The test designers wrote only under `tests/acceptance/W1-27/`, `W1-30/` and `W2-50/`; F-B covers the W2-50 files outside the ticket's list.
- The lead wrote only its checkpoint record.
- No implementer changed an acceptance test.

## Findings

### F-A (low): KPI 4's static guard still misses per-run base folder forms outside list and tuple literals

- **What was done:** my probe ran the guard's `_settings_in` from `test_w2_67_temp_folders.py` over sources in a stand-in root.
- **What happened:**
  - Found: every f-string `--basetemp=` that is an element of a list or tuple, and the separate option.
  - Missed: an f-string passed to `cmd.append(...)`; the option appended alone and then the folder; `env["PYTEST_ADDOPTS"] = f"--basetemp={folder}"`; an f-string shell command; and the option built with `+`, `.format` or `%`.
- **What should have happened:** KPI 4's guard finds a per-run base folder however the argument is built, or its row states that it reads literal lists only. This widens round 1's row F3, which is still open.
- **Severity:** low.
- Ordinary work: yes, because appending an option to a command list, setting `PYTEST_ADDOPTS` and joining strings with `+` are ordinary ways to pass an option.
- Consequence: other (as F3: the root conftest's runtime refusal still stops any run that loads it, whatever the form; only a nested run of a project outside `tests/` would get a per-run base folder, inside the outer run's own base folder).

### F-B (low): W2-50's test designer changed acceptance files the ticket file does not name

- **What was done:** commits 8b4fcf067410 and 1d17c7d1f802.
- **What happened:**
  - They changed `tests/acceptance/W2-50/w2_50_scan_support.py` and `README.md`, and added `README-W2-67.md`.
  - The ticket file's list of acceptance files names only `tests/acceptance/W2-50/test_w2_50_secrets_scan_scale.py` there, as DEC-914 item 1 does. The card names `W2-50/**` (the large-store and hang cases only).
  - The helper's changes reach only the named file, its only importer, and only once a case declares the limit: a `ppid` field in the stand-in's log, the declaration functions, and a conditional path entry.
  - The guard allowed the write because the role holds all of `tests/acceptance/**`, so only review holds the ticket's list.
- **What should have happened:** the ticket file names the helper and the READMEs the revision needed, or the card's wording is recorded as the scope.
- **Severity:** low.
- Ordinary work: yes, because a test designer revising a case naturally edits the helper only that case imports.
- Consequence: other (no other case's behaviour changes; nothing fails open or is lost).

## Scratch, refusals and memory

- **Scratch figures:** 8 inodes and 24K at start; 55 and 292K before the heavy runs; 137 and 688K after. pytest kept its three base folders. The largest content, W2-50's 16 MiB stores, was removed with each passing case's `tmp_path`.
- **Read refusals met:** 0.
- **Write-side refusals met:** 3, none twice for the same call.
  - The guard read a heredoc's Python `> 1` as a redirect to a worktree file `1`.
  - It refused twice as `/<guard-unresolvable>`, for writes to variable paths (`rm -f "$VAR"`, and a `cp` to variable targets).
  - I redid each with the Write tool or literal absolute paths inside my temporary folder.
- **gov retrieve:** used once, for run 3's scope. It returned FACET_UNAVAILABLE (lexical and semantic facets stale); I did not rebuild the index, since that writes.
- **Code-graph tool:** not used. I read named files with targeted greps instead.
