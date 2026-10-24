# Lens H: Test strategy (audit, research, design)

Independent assessment of the Gov OS, October 2026.

| | |
|---|---|
| **Lens** | H, test strategy: Part A audit, Part B research, Part C design (the owner's order of 2026-10-21; DEC-881) |
| **Author** | an independent auditor (`GOV_ROLE=independent-auditor`, Opus 5.5, effort max), started by the Wave 2 orchestrator; no part of the work assessed is mine |
| **Date** | 2026-10-21, 11:36 to 16:30 BST (the report written at 16:20) |
| **Head assessed** | `w2/integrate` at `21302ae9208a0696bb69dc7eb831529df4f864bb`, as the brief names it; every run used that commit. The head moved during my session, and I read these later commits read-only: `97405c6f` (DEC-881, this lens, 11:39); `4845b9b8` (W2-58 merged, 13:56); `9d8c1887` (DEC-882, delegated, 14:00, which repairs two reds of finding 1); `2b254458` (W2-02's checkpoint before its close, 14:06); `f3a1079a` (DEC-883 and DEC-884, owner, and DEC-885, delegated, 15:49); `3cb740dd` (working memory, 15:50); `f46b1ff9` (W2-02's checkpoint for the queue's fourth run, 15:58). The close queue held its lock from 14:01 to 15:36 and again from 15:50; W2-02's second close started at 16:11:55 and was running when I finished |
| **Branches read** | `w2/integrate`; `w2/W2-48` (the withdrawn cache: `docs/research/W2-48-cache-choice.md`); `w2/W2-02` (`close.schema.json`); `w2/W2-26` (EXAMIN profile); the ticket worktrees' heads from `git worktree list` (read only) |
| **The `gov` I used** | the pinned `gov` (`~/.local/bin/gov`, wheel of `fecb870c`) for no measure. It answered only read-only calls on the main tree: one listing (`…/pin-fecb870c/bin/python -m gov.guard.hooks`) and the `gov retrieve` questions below. Every test run and every analysis of code ran **my clone's own code**: `PYTHONPATH=/tmp/gov-os-assessment-H/repo/src` |

**What I read.**
- **Code:** `src/gov/close/` (all of it), `src/gov/codeintel/__init__.py`, the kernel hooks, the test tree (all 55 acceptance folders' support and conftest files where relevant, the serial-only list, the root acceptance conftest).
- **Settings:** the path map's close settings and ratchet lists, `pyproject.toml`, `lefthook.yml`, `.github/workflows/ci.yml`.
- **Records and plans:**
  - the one close record;
  - every close log of Wave 1 and Wave 2;
  - the close queue's logs and script, and the repair tickets;
  - the 2026-10-08 profile (`log/PERF-REPORT.md`);
  - the leads' A5 returns and the copied lead records under `governance/project/orchestration/worktrees/*/lead/`;
  - the register entries on testing (DEC-042, DEC-372, DEC-514, DEC-527, DEC-549, DEC-554, DEC-567, DEC-726, DEC-736, DEC-757, DEC-760, DEC-762, DEC-766, DEC-780, DEC-813, DEC-823, DEC-852, DEC-859, DEC-860, DEC-868, DEC-869, DEC-871, DEC-876, DEC-880, DEC-881, and those decided during my session: DEC-882, DEC-883, DEC-884, DEC-885);
  - the WBS cards W2-07, W2-08, W2-19, W2-24, W2-37, W2-38, W2-43, W2-45, W2-46, W2-57, W2-66, and the W2-66 ticket file;
  - the Wave 2 list and triage rows on testing;
  - the Contract's CAP-38, CAP-39 and CAP-53;
  - the lead brief, the orchestrator prompt (§3–§15, Appendix A), the test-design skill and brief template, JUDGEMENT.md;
  - the other lens reports (A to G, synthesis) where they touch testing.
- **EXAMIN** (read only): "/home/usain/gov-os-workbench/examin/product/pyproject.toml", its `product/tests/` and `governance/scripts/tests/` file lists and markers. Nothing ran there.

**What I ran, and where.** Every run that wrote anything ran in my folder `/tmp/gov-os-assessment-H/`:
- **Clones:** `git clone --no-hardlinks` of the repository into `repo/`; two throwaway clones, `repo-w2start/` (checked out at `7d60dec6`, Wave 2's start) and `repo-tm/` (testmon trial); and at 15:37 a worktree of my clone, `repo-head/`, at `2b254458` (fetched read-only from the main repository), for the localisation probes.
- **Isolation of every test run:**
  - started from an empty environment (`env -i`);
  - `HOME` and `TMPDIR` in my folder; the git identity given by environment variables;
  - a private `/tmp` (`bwrap --dev-bind / / --bind <mine>/faketmp /tmp --bind <mine> <mine>`), so the product's fixed `/tmp/gov-cbm-<uid>` folder and every temporary file stayed in my folder.
- **The resource gate and the close lock** were checked in the same command before every heavy run.

| Run | Command (abridged) | Started (load) | Result |
|---|---|---|---|
| Collection | `pytest tests --collect-only -q -p no:cacheprovider` (+ `-m local_only`, `needs`, `needs_rulesync`) | 11:4x | 14,770 cases (+2 deselected) in 12.7 s |
| Part 1: timed run | `pytest tests -n 8 -m "not local_only" @p1.args(--deselect each serial-only entry) -p govh_probe --junitxml … -o junit_duration_report=total` | 11:54:29 (9.6) | 14,220 passed, 7 failed, 33 skipped in 2,083 s |
| Part 2: serial cases | `pytest @p2.args` (the 22 serial-only cases that are not `local_only`), serially | 12:34:53 (1.7) | 22 passed in 571 s |
| Re-runs alone | the three unexpected reds; W1-27's case with one file moved aside | 12:3x | 3 failed alone; W1-27 passes without the log |
| Part 3: who-tests-what map | part 1's selection under the venv interpreter with my coverage shim (`-p govh_covmap`) | 12:45:36 (1.0) | 14,219 passed, 7 failed (part 1's seven), 1 error (W1-07's copy racing git's gc, finding 2), 33 skipped in 2,296 s |
| testmon control | W1-32 with `--testmon`: record, plant a fault, select | 12:4x | 0 of 80 tests selected; the fault missed |
| Planted faults (B2) and mutation sample (A6) | `scripts/mutation_runner.py` (one edit in place, the executing tests run, the file restored), every item gated on the close lock, the load and memory | 13:30 to 14:09, 15:36 to 15:50 (2 to 7) | B2: 23 of 32 faults ran (22 valid), 2 controls. A6: 3 controls, 47 of 116 items (`ratchet.py` 26, `claims.py` 21). The rest stopped when the lock returned at 15:50; I stopped the runner at 16:10 |
| Localisation probes | in a worktree of my clone at `2b254458`: W1-07's `doctor` case alone; W1-35 collected with W1-38 or W1-15 in both orders; one W1-25 and one W1-07 case with and without an untracked file | 15:38 to 15:48 (5 to 7) | the `doctor` case passed alone in 9.5 s; the W1-35 clash shown (finding 17); W1-25's gc race in both clean runs, the file irrelevant |
| `gov retrieve` | the pinned `gov`, read-only, lexical facet only (see Limits) | 13:01, 14:33 | stale at 13:01; 9 to 16 evidence items per exact string at 14:33 |
| Copy cost | W1-07's `copy_working_tree` and the per-test `copytree`, twice each, on throwaway clones at `21302ae9` and `7d60dec6` | 13:59 (0.95) | head (10,087 files with `.git`): session 3.13 and 1.86 s, per test 0.93 and 0.83 s; Wave 2 start (3,724 files): 0.71 and 0.46 s, 0.19 and 0.18 s |
| Static analyses | estate, import graph, allowed-paths map, duplicates, ever-failed, scoped cost (`scripts/*.py`) | — | in the logs folder |

**Tools installed: none.**
- The guard refused my one install: `install by role 'independent-auditor' denied: only the orchestrator may propose installs, and research may install inside its experiment folder`. I took the refusal and tried no other form (refusal 8).
- I downloaded one wheel before that, from PyPI: `coverage-7.16.2-cp312-cp312-manylinux1_x86_64.manylinux_2_28_x86_64.manylinux_2_5_x86_64.whl`, sha256 `5375ebd99038021b35e99dc88255022912c06565d316212f4a576e4b08d30f5d`, licence Apache-2.0. It was never installed. It is still in `wheels/` (see the last limit).
- The trials used only packages already on the machine, installed under DEC-843 and DEC-514: coverage 7.16.2, pytest-testmon 2.2.0, pytest-xdist 3.8.0, pytest 9.0.3.
- They also used my own standard-library scripts and a venv with system site packages that held only my coverage shim (`govh_covstart.py` and a one-line `.pth`).
- **The venv and the pip cache were not removed.** The harness refused the removal twice (see the last limit).

**Limits of this assessment.**
- **Not run:** the 488 `local_only` cases (dev tiers, real models, the code-graph daemon, live Claude sessions). A live session writes under `~/.claude/` and spends the owner's usage. Their times come from the close records.
- **Trials cut short by the close lock.** The queue held its lock from 14:01 to 15:36 and again from 15:50, and I start no heavy run under it.
  - The planted-fault trial ran 23 of its 32 faults. The nine left out include all six in the three widest-reaching modules.
  - The mutation sample ran 47 of its 116 items: two modules, `record.py` not at all.
  - The B2 controls ran for three of the sixteen modules.
  - I finished rather than wait up to eight hours, because W2-66's test designer waits for this report (DEC-881, DEC-884). The plans and `scripts/run_rest.sh` resume where the runs stopped.
- **Tool trials the install refusal prevented:** grimp or tach (static import-graph selection), pytest-split, pytest-randomly, pytest-timeout, pytest-rerunfailures, mutmut and cosmic-ray. I replaced the import-graph and mutation parts with standard-library scripts of my own; the rest are judged from their documentation (B2).
- **No GitHub access:** I did not query CI's runs; its state comes from the workflow and the orchestrator's CI exit package.
- **Refusals met: 15.**
  - **One was a Policy 2 search refusal** (DEC-849): refusal 11, a `grep -r` whose folder list included `governance/project/`. I repeated the search over the named folders `src/` and `template/governance/kernel/` only.
  - **The others were not read refusals:**
    - a here-document in Bash (refusal 1);
    - two size measurements over folders that hold protected files (2, 3): stopped after two, so the size of the copied tree comes from `git ls-tree` instead;
    - a variable in a write target (4);
    - a symbolic link to `~/.nvm` (5);
    - the harness's sensitive-file prompt for a `.gitconfig` in my folder (6, 7);
    - the install (8);
    - my read-only research helpers' file writes (9, by design: non-role subagents write nothing);
    - a `>` inside an inline script read as a write into the repository (10);
    - a second here-document the guard could not read (12);
    - the Monitor tool, "not known to the guard" (13; DEC-685): I waited with background shell loops instead;
    - the removal of my venv, pip cache and wheel (14, 15). The harness asked for an approval this non-interactive session cannot give, first for the compound command and then for `rm -rf` alone. After the second refusal I stopped, as the brief requires.
- **One `git status` without `--no-optional-locks`:** at the start I ran `git status --short` once in the main repository without that option. It may have refreshed git's index stat cache; it changed no content. Every later git command there used `--no-optional-locks`.
- **`gov retrieve`** (the pinned `gov`, read-only, `--batch-size 8` under DEC-860; `scripts/retrieve_batch.py`).
  - **13:01:** I asked "What has the owner decided about a nightly full uncached regression run, and from when does it run?". It answered nothing: `stopping_reason: FACET_UNAVAILABLE`, both facets `stale`, because the main tree's store was older than its head.
  - **14:33:** the close queue's rebuild had made the store fresh at 14:13, for `2b254458`, so I asked again.
    - **How I kept it read-only.** I kept the semantic facet off on purpose: no reachable embedder, no Ollama binary, and a throwaway `HOME`. To answer that facet, `gov` would start a CPU-only `ollama serve`. It would also write the question's vector into the repository's `.gov-runtime/query-vector-cache.db` (`semantic.py:146-189`), which is outside the two places I may write.
    - **Six questions, two forms.** The lexical facet matches an exact string only (`lexical.search`), so the six questions in plain words found nothing. Their exact-string forms found 9 to 16 items each, in batches of 8:
      - "nightly full": W2-66's and W2-48's tickets;
      - "pre-close gate": W2-07's ticket and DEC-867, DEC-869 and DEC-870;
      - "test_inputs": W2-66's ticket, P-W2-48-5, the path map's lines 284-301, DEC-875, DEC-876 and DEC-880;
      - "load_sensitive": W2-53's, W2-12's and W2-19's tickets and register entries such as DEC-757;
      - "quiet window" and "path-scoped regression": register entries (DEC-631 to DEC-881, DEC-726 and DEC-841 among them) and the Wave 2 plan.
    - **What it gave.** It located sources I had already read by name. It answered no question by itself.
  - **It confirms lens B's F4 at today's head.** Every register chunk carries the id of the register's last entry, now DEC-882. DEC-875 and DEC-876, both SUPERSEDED, came back as evidence under that id, and the dropped list was empty (`retrieve.py:52`, `:183-189`). That is a fail-open lens B has already sent to a package, so I do not repeat it as a finding.
  - So every question of this lens was answered from sources taken by name (register entries, cards, logs, code) and by `grep`.
- **The code-graph tool** (codebase-memory) is not reachable as a tool from this session, so code questions were answered by reading the code and by my own `ast` import graph.
- **The throwaway venv, pip cache and wheel are still in my folder.** They are `/tmp/gov-os-assessment-H/venv` (16 MB, my coverage shim only), `pip-cache` (1.3 MB) and `wheels` (the uninstalled coverage wheel). The removal was refused twice (refusals 14 and 15). They hold no secret and nothing installed. Whoever can grant it removes them with `rm -rf /tmp/gov-os-assessment-H/venv /tmp/gov-os-assessment-H/pip-cache /tmp/gov-os-assessment-H/wheels`.

## In brief

- **What a close costs, and why.**
  - Every `gov close` runs all 14,770 test cases: about 31 minutes in parallel plus 29 minutes for 263 cases run alone afterwards (W2-53's close).
  - Three quarters of the cases (74.5 %) start `gov` as a separate Python process, often with an environment built from scratch. That process holds 96 % of the test time.
  - 13 suites copy the whole working tree, which grew in Wave 2 from 1,784 files to 10,058, 73 % of them the committed orchestration record. Those suites take 48 % of the test time.
- **Every test runs at least twice per ticket.**
  - A lead runs every suite serially before each return: 3.85 hours in W2-48's run.
  - The close runs everything again, and so does each refused close.
  - In both waves, 18 refused closes ran the full regression: about 17 hours of quiet-window machine time.
  - The tests found the ticket's own code at fault once. Load caused 9 test failures and the repository's state 5; process slips caused the other refusals.
  - W2-53 needed eight attempts over 62 hours.
- **Nothing tests the integrated head between closes.**
  - The nightly run is decided but not running, CI cannot run tests, and the hooks are off.
  - My run found the head red: 3 acceptance tests made red by the orchestrator's own record commits this morning. One of them was red because a committed test log appeared inside a test's copy of the tree.
  - Two were repaired at 14:00 (DEC-882) after W2-58's lead hit them in its full verification. The third (W1-08: two record files in no namespace) was not: the gate's path-map check measures nothing (known row W2-M214).
  - W2-02's close met it. It ran 75.6 minutes and was refused at 15:36 for W1-08 and for a W1-07 case that passed alone. That close kept no failure message, so its cause cannot be told now.
  - The orchestrator repaired W1-08's cause at 15:49 (DEC-885), and the queue of six restarted at 15:50 (P-H-1).
- **Why W2-48's cache saved 3 %, and what the research says.** This repository's tests depend on repository-wide state and on child processes, so per-test tracking makes almost every test "always run". The literature predicts it: a file-level selector for Python saved 3.10 % (NameRTS, ISSTA 2026). In-process tracking sees 17 % of the dependencies of tests that spawn processes (RTSLinux, FSE 2017).
- **My trials.**
  - Plain testmon selected 0 of 80 tests for a fault two of them catch.
  - Static import graphs cannot see 483 of the 531 acceptance files.
  - A coverage map across processes, built with the installed coverage 7.16.2 and an 83-line shim, works. It attributed the child's lines to 97.9 % of the tests that start `gov` in a child, at +10 % wall time.
  - **Planted faults** (22 valid, in 13 non-core modules):
    - W2-66's declared map caught all 22 while selecting a median 9 % of the test time. Without `tests/unit` it would have missed 3.
    - The measured map caught the same 22 at four times the time. The static graph caught 18.
    - Nine faults did not run before the close lock returned at 15:50, among them all six in the three widest-reaching modules. For those modules the question is still open.
  - **Mutation sample:** about nine of ten sampled mutants killed in `ratchet.py` (23 of 26) and `claims.py` (19 of 21). One real gap: the rule that every ratchet entry names its fix has no test (finding 19).
  - **Two hazards for W2-66 found by running it:**
    - a selection passed as a list of suite folders breaks W1-35's collection (finding 17);
    - W1-25's per-test copy races git's gc, like W1-07's (finding 2).
- **The design.** L1 to L5 with one selector for leads and the close, inside DEC-883's batched closes:
  - path-to-suite by tickets' paths, plus test-side imports, plus a weekly measured map, against the last full green commit;
  - the run keeps the full run's form, `pytest tests --ignore=…`, because a list of suite folders breaks W1-35's collection (finding 17);
  - the tests that read the records run on every head, reused or not (finding 18);
  - the shared core and anything unplaced widen to everything;
  - live and model cases move to the nightly;
  - every record states its scope, commit, what ran and what did not;
  - the nightly run is the backstop, with history, a flaky-candidate report and bisection.
  It becomes a kernel capability built inside W2-66, W2-19, W2-07, W2-64 and W2-11, and adopted repositories receive it with their declared commands (EXAMIN first; Rust and TypeScript use their own graphs).
- **Decisions made during my session.** The owner decided DEC-883 (batched closes, same-code reuse, the index by code fingerprint, the serial-only tests examined) and DEC-884 (W2-66 first, after this report). The orchestrator repaired the head (DEC-882, DEC-885) and added a gate step that runs the four record-reading test files before each close.
  - My evidence refines DEC-883 in one place where it would fail open. Its "same code" leaves out `governance/project/orchestration/`, and two of today's three reds came from commits that touched only that folder (finding 18).
- **Nine owner packages,** in order:
  1. W2-66's card before its test designer starts: its corrections (P-H-2) and DEC-883 refined (P-H-9), both P1;
  2. a nightly run now as glue (P-H-3);
  3. the record-reading tests after record commits, widened (P-H-1);
  4. the lead's verification in the close's form (P-H-4);
  5. test hygiene (P-H-5);
  6. the subagent-stop hook's hidden reason and small record corrections (P-H-7, P-H-8);
  7. the capability's placement (P-H-6).

## Terms used

- **`gov close`, a close:** the Gov OS command that closes a ticket. It checks the ticket's commits and review record, runs the ticket's acceptance tests and then every other test (the **regression**), and writes a **close record** under `docs/close/`. A **refused close** exits non-zero, counts an iteration and opens a repair ticket. At three refusals the ticket is **escalated** and only an owner decision lifts it.
- **Acceptance suite:** the tests an independent test designer writes for one ticket before it is built, in `tests/acceptance/<ticket>/`.
- **Builder or unit tests:** the engineer's own tests, in `tests/unit/`.
- **Lead:** the session that runs one ticket's loop in its own worktree: test designer, engineer, verification, review.
- **Worker:** a session a lead starts.
- **Orchestrator:** the main session; it merges branches and runs the closes.
- **Serial-only list** (`tests/acceptance/serial-only.txt`): cases that run alone after the parallel run (latency, live sessions, real models or daemons, races).
- **`load_sensitive`:** an owner-only list in the path map. A listed test that fails in a close is re-run alone, and counts only if it then passes.
- **`accepted_reds`** (the **ratchet**): an owner-only list of known failing tests that do not refuse a close. Both lists may only shrink (DEC-766).
- **Pre-close gate:** the orchestrator's checks before each close (DEC-868). It runs collection of all tests in one process, `gov check` after a fresh rebuild, a fresh checkpoint and a clean tree. Its script, `tools/close_queue.sh`, runs from the orchestrator's untracked scratch (`.gov-runtime/scratch/orchestrator/`); a copy is tracked in the orchestration record (`governance/project/orchestration/main/orchestrator/tools/`).
- **Quiet window:** closes run one at a time while no lead runs heavy work (DEC-780). The lock file `CLOSE-RUNNING` marks one.
- **Path map** (`governance/project/path-map.yaml`): the repository's map of every tracked path to a namespace, plus the close's settings and the two lists.
- **Shared core:** DEC-880's list of code a change to which makes even a scoped close run everything.
- **Orchestration record:** the orchestrator's and leads' working files copied into the repository at each checkpoint (Policy 1, DEC-819), under `governance/project/orchestration/`.
- **Batched close** (DEC-883, decided during my session): queued closes on the same integrated head share one rebuild, one `gov check` and one full regression; then each ticket runs only its own checks. It is a merge queue at the close.
- **Fingerprint:** a hash of a tree's files. DEC-883's code fingerprint leaves out record-only paths, so two trees that differ only in records count as "the same code", and the last passing run is reused.
- **W2-66:** the ticket that brings **path-scoped regression** into the close. A **scoped close** runs only the suites its change can affect; the full suite stays for the shared core and as the **nightly** run.
- **Layers L1 to L5:** the owner's model. L1 immediate (seconds), L2 affected components (minutes), L3 merge (5 to 30 minutes), L4 nightly full run, L5 release qualification.
- **Planted fault / mutant:** a deliberate one-line change to the code, used to see which tests catch it.
- **Killed:** a mutant at least one test catches. **Survived:** a mutant no test catches.

## Part A. Audit: the state of testing in the Gov OS today

### A1. The test estate, measured

**How it was measured.**
- **Commit:** the clone at `21302ae9`, its own code (`PYTHONPATH=<clone>/src`), Python 3.12.3, pytest 9.0.3, pytest-xdist 3.8.0.
- **Counts:** `pytest tests --collect-only` (13.6 s) and `-m <marker>` collections.
- **Times and subprocess use** come from two runs with JUnit XML (`junit_duration_report=total`, so setup and teardown are included) and my probe plugin. The plugin records, per test, the processes the test starts itself.
  - **Part 1:** every case except the `local_only` ones and the serial-only list, 8 workers. Started 11:54:29 at load 9.6 and ended 12:32:10; other sessions raised the load to 31 at times.
  - **Part 2:** the 22 serial-only cases that are not `local_only`, run serially at load 1.7.
- **The `local_only` cases (488)** were not run. They include the 241 serial-only cases with live sessions, real models and the code-graph daemon. Their time comes from the close records.

**Counts by kind (14,770 collected cases; 2 more deselected by W2-54's conftest).** The estate keeps growing: at `2b254458`, after W2-58's merge, the close queue's collection counted 15,762 cases (`close-queue-20261021-1401/queue.txt`, 14:13), 992 more (6.7 %) from one merge.

| Kind | Cases | Note |
|---|---|---|
| Unit (`tests/unit/`, builder tests) | 2,396 (16 %) | 34 folders; in-process; 3.6 % start `gov` in a child |
| Per-ticket acceptance (`tests/acceptance/<ticket>/`) | 12,374 (84 %) | 55 folders: Wave 1 11,385, Wave 2 989 |
| of which serial-only (run alone after the parallel run) | 263 | real model or daemon 188, live session 50, latency 23, race 2 |
| of which live sessions (a real Claude session) | 50 | W1-25, W1-46, W1-49, W1-50 (in the serial list); also W2-54's sandboxed worker and W2-62's live resume, which are `local_only` but not in the serial list |
| `local_only` (dev tiers, real models, daemons, live) | 488 | 241 of them also serial-only; by suite, about 171 code-graph daemon cases (W1-16, W1-20), about 53 live sessions (W1-46 36, W1-49, W1-25, W1-50, W2-54, W2-62), about 18 real-model cases (W1-19, W1-21) and about 244 dev-tier or machine-local cases (W1-08 173, W1-15 21, W1-06 11, W1-07 8, W1-48 8, others) |
| `needs` / `needs_rulesync` markers | 161 / 181 | tools that must be on the machine |
| Load-sensitive (`load_sensitive`) | 42 cases in 30 entries | re-run alone in the close |
| Known reds (`accepted_reds`) | 2 | W1-42 |
| Deselected in every run | 2 | W2-54's `shared_gpu` cases |
| Distinct test functions | 5,665 | 62 % of cases (9,105) come from parametrisation; W1-02 alone has 3,653 cases (25 % of the estate), and one function has 187 parameter sets |

**The share that runs `gov` as a separate process (part 1, 14,260 cases):**
- **10,624 cases (74.5 %)** start `gov` code in a new Python process: a launcher script, `python -m gov…`, or a driver script that imports `gov`. **11,999 (84.1 %)** start some process.
  - Acceptance: 10,537 of 11,864 (88.8 %).
  - Unit: 87 of 2,396 (3.6 %).
- These cases hold **96.2 % of the measured test time**.
- **Statically:** of the 531 acceptance test files, only 48 import `gov` in the test's own process. Through their own helper modules, 483 reach `gov` only through a child (my `ast` import graph, `scripts/import_graph.py`).
- **Children with a scrubbed environment are the rule.** Tests pass the child an environment built from scratch: `PATH`, a sandbox `HOME`, `TMPDIR`, `PYTHONPATH` (`tests/acceptance/W1-07/w1_07_support.py:404-425`). This is why in-process tools (testmon, coverage's own subprocess hook) cannot see the child.

**Each suite's runtime (part 1, sum of case durations, serial-equivalent seconds; 8 workers):**

| Suite | Cases | Seconds | `gov` in a child |
|---|---|---|---|
| W1-30 (`gov close`) | 512 | 2,041 | 90 % |
| W1-41 (adoption) | 240 | 1,597 | 91 % |
| W2-50 (runs root, secrets scan) | 636 | 1,140 | 100 % |
| W1-27 (rebuild, doctor) | 132 | 831 | 96 % |
| W1-07 (CLI) | 214 | 650 | 100 % |
| W1-26 (checks) | 413 | 511 | 99 % |
| W1-02 (guard) | 3,648 | 499 | 99 % |
| W2-01 | 88 | 370 | 100 % |
| W1-50 (containment) | 682 | 369 | 95 % |
| W1-47 (guard, oracle) | 983 | 367 | 93 % |
| … 75 more folders | … | … | … |
| **All of part 1** | **14,260** | **11,292 s = 3.1 h serial; 2,083 s = 34.7 min wall at 8 workers** | 74.5 % |
| `tests/unit` | 2,396 | 168 | 3.6 % |

- **The serial part** (263 cases) took 1,746 s in W2-53's clean close. Its 241 `local_only` cases (daemons, models, live sessions) were not run here.
- **Part 2:** the 22 other serial cases took 571 s serially at load 1.7, all passed (latency and race cases included). Of that, **W1-05's switch-over case alone took 516 s**: it reruns W1-02, W1-03 and W1-04 inside a child pytest, which makes it the slowest single case in the estate. So the 241 `local_only` serial cases account for about 1,175 of W2-53's 1,746 serial seconds.
- **A close** therefore costs about 31 min parallel + 29 min serial on 20 workers (W2-53's record).
- **A lead's verification** runs the same suites serially, one process per suite: 13,857 s (3.85 h) in W2-48's run 2.

**Where the time goes.**
- The slowest 500 cases (3.5 %) take 48.5 % of the time; the slowest 2,000 take 78 %.
- Durations: under 0.1 s 6,245 cases; 0.1–1 s 5,951; 1–5 s 1,593; 5–30 s 460; 30 s or more 11.
- **The 13 suites that copy the whole working tree** in a fixture take **48.4 % of all case time** (5,460 s): W1-05, W1-07, W1-18, W1-25, W1-26, W1-27, W1-28, W1-30, W1-39, W1-46, W1-47, W1-49, W1-50. In W1-07 and W1-27 the copy happens per test (`shutil.copytree(cli, target)` in a function-scoped fixture).
  - At Wave 2's start (`7d60dec6`) the tree held **1,784 tracked files (14.9 MB)**. Now it holds **10,058 (66.5 MB)**, of which **8,046 files (48.7 MB, 73 %) are the orchestration record** committed since DEC-819 (`git ls-tree -r -l`).
  - These suites' cost therefore grows with the orchestrator's working memory, not with the code under test. Measured at 13:59 at load 0.95 with W1-07's own helper (`scripts/copy_cost.py`, two runs each, on throwaway clones at `21302ae9` and `7d60dec6`):
    - **Session copy** (`copy_working_tree`: copy every tracked and untracked file, then `git init`, `add` and `commit`): 0.46–0.71 s on the Wave 2 start tree, against 1.86–3.13 s on the head.
    - **Per-test copy** (the function-scoped `copytree` of that commit, `.git` included, in W1-07 and W1-27): 0.18–0.19 s against 0.83–0.93 s, **4.6 times slower**.
    - W1-07 and W1-27 have 346 such tests, so the per-test copy alone grew by about 4 minutes of serial time per full run, before load.

**Top 20 slowest cases (part 1, seconds, setup and teardown included):**

| # | Seconds | Case |
|---|---|---|
| 1 | 169.7 | W2-50 `test_w2_50_secrets_scan_scale.py::test_a_large_store_among_many_small_files_is_decided_by_gov_check` |
| 2 | 168.9 | W2-50 `…::test_a_large_clean_store_is_decided_green` |
| 3 | 84.7 | W2-50 `…::test_a_large_store_with_a_canary_across_its_middle_is_red_naming_it` |
| 4 | 62.2 | W2-50 `…::test_a_scan_that_cannot_finish_fails_closed_and_records_nothing[hang]` |
| 5 | 50.4 | W1-41 `test_w1_41_embedding_policy.py::test_the_rebuild_says_no_namespace_is_embedded[every-namespace-not-embedded-full]` |
| 6 | 41.5 | W1-47 `test_w1_47_session_role.py::test_the_builder_tests_of_the_guard_pass` (runs the guard's unit tests again, in a child pytest) |
| 7 | 41.2 | W2-54 `test_w2_54_cpu_embedder.py::test_an_address_held_by_something_that_is_not_an_embedder_gives_no_semantic_answer_and_no_fallback` |
| 8 | 34.7 | W1-41 `test_w1_41_legacy.py::test_each_kind_of_legacy_rule_file_is_imported_into_rulesync[agents-md-roles]` |
| 9 | 34.6 | W1-41 `test_w1_41_legacy.py::test_a_record_that_no_longer_stands_does_not_keep_the_store[RETIRED]` |
| 10 | 31.6 | W1-41 `test_w1_41_verdict.py::test_a_path_map_that_changes_after_a5_passed_is_not_executed` |
| 11 | 31.4 | W1-41 `test_w1_41_verdict.py::test_a_verdict_about_a_path_map_that_changed_afterwards_moves_nothing` |
| 12 | 29.9 | W1-41 `test_w1_41_legacy.py::test_a_longer_path_or_id_that_only_contains_the_stores_is_no_citation[another folder's file of the same name]` |
| 13 | 29.8 | W1-35 `test_w1_35.py::TestSkillRegressionGreen::test_skill_regression_green_with_well_formed_skills` |
| 14 | 29.1 | W1-27 `test_w1_27_rebuild_r8_no_embeddings.py::test_the_mode_builds_everything_else_a_rebuild_builds` |
| 15 | 28.9 | W1-41 `test_w1_41_migration.py::test_the_index_refresh_follows_the_moves` |
| 16 | 28.6 | W1-41 `test_w1_41_migration.py::test_every_moved_file_is_byte_for_byte_what_it_was` |
| 17 | 28.2 | W1-27 `test_w1_27_recovery_check.py::test_derived_state_deleted_and_rebuilt_gives_same_digest` |
| 18 | 27.4 | W1-41 `test_w1_41_migration.py::test_the_rollback_points_are_the_ones_the_plan_recorded` |
| 19 | 27.3 | W1-41 `test_w1_41_migration.py::test_no_other_tracked_file_changes_content_during_a_move_batch` |
| 20 | 26.9 | W1-41 `test_w1_41_legacy.py::test_a_longer_path_or_id_that_only_contains_the_stores_is_no_citation[a folder whose name only ends …]` |

The serial cases are not in this list. W1-05's switch-over case (516 s in part 2) would top it.

**Tests that never failed (Wave 1 and Wave 2).**
- No per-test history exists: a close records counts, not tests, and only failures are named.
- From every recorded failure, I collected the failing test ids: the close logs of both waves (`close-*.json`, the queue logs), and every Wave 2 lead's copied records under `governance/project/orchestration/worktrees/*/lead/` (`scripts/ever_failed.py`).
  - **146 of the 14,770 cases (1.0 %)** appear as `FAILED`/`ERROR` in a regression-type run, that is, outside their own ticket's red phase.
  - **14,624 (99.0 %) were never seen failing** in any recorded run.
- The ones that did fail cluster in four places:
  - latency and live cases (W1-05, W1-02, W1-19, W1-46);
  - guard tests that a guard change (W2-58's Policy 2) legitimately broke: 33 W1-02 ids in W2-58's lead logs;
  - tests asserting the live repository's state (W2-54's green-here tests, W1-49's window, W1-33's definitions);
  - the known reds.
- This is a lower bound on failures (Wave 1 leads' logs were not copied), and it is not evidence that the 99 % are useless: they are what a full close re-runs every time, and the place a selection could save time.

**Duplicate tests.**
- **Literal duplicates are rare:** 3 groups of identical test bodies (6 functions) among 5,667 test functions; 37 test names repeat across files (`scripts/dupes.py`).
- **Duplication is structural instead:**
  - (a) parametrisation re-runs one guard decision path for every role and tool (W1-02: 3,653 cases in 0.14 s each);
  - (b) nested re-runs: W1-05's switch-over case reruns three whole suites (516 s), and W1-47 reruns the guard's builder tests in a child pytest (41.5 s);
  - (c) run-level duplication: every suite runs in the lead's verification, again in the close, again after each refused close, and again at W2-24 and W2-46 (A2).

**Test-suite size against code.**
- `src/`: 18,095 lines of Python; `tests/`: 161,898 lines (acceptance 141,381; unit 20,517): **8.9 test lines per code line**.
- **Wave 2 on `w2/integrate`** (`7d60dec6..21302ae9`): source +1,487 / −226 lines, tests +16,483 / −90: **11.1 test lines added per code line added** (13.0 net).
- The owner's "about 8 per code line" holds for the estate; Wave 2's own rate is higher.

### A2. Testing in practice, by role and step

Who runs what today, from the committed rules and the run records:

| Step (who) | What runs | How | Evidence |
|---|---|---|---|
| Test design (independent test designer, a fresh session per batch) | the ticket's new acceptance tests, red first | writes `tests/acceptance/<W2 id>/` with a README mapping each KPI line to its tests and the expected red reason; runs them "to the end" and they must fail for that reason; "proportional": FULL thorough, STANDARD every KPI line's success and failure plus key edges, LITE one test per KPI line; "behaviour through public interfaces, never internals; deterministic, no network" | prompt Appendix A1; `template/governance/kernel/templates/brief-test-designer.md` lines 52-62 |
| Red check (the lead) | the designer's suite | the lead runs it to the end and checks each failure reason | `LEAD-w2-common.md` loop step 2 |
| Building (engineer) | the ticket's acceptance suite (results only, never its source), its builder tests, and whatever other suites the engineer judges related | by judgement: W2-20's engineer ran W2-20 plus the command lists of W1-26, W1-07 and W1-32; W2-52's ran W2-52, W1-36, W1-27, W1-38 and W1-26; W2-50's ran W1-02 in full with `-n 8` because serial suites passed the 10-minute foreground limit | engineers' returns under `governance/project/orchestration/worktrees/*/lead/log/eng-*.json` |
| Verification before every return (the lead) | a full `gov rebuild`; **every** acceptance suite, each in its own pytest process, serially; `tests/unit`; `gov check`; a re-run alone of a failing `load_sensitive` case; `pytest --collect-only` over `tests` (DEC-868) | in batches of under two hours, waiting for load below 20 and for no close | `LEAD-w2-common.md` lines 17, 21, 86-89; W2-48's run 2: 13,857 s of serial suite time for one verification (`.../W2-48/lead/log/verify3/*.codes`) |
| Review (FULL tickets, independent auditor) | its own probes, often subsets of suites | read-only session | W2-59's reviewer: W2-59 55, W1-38 201, unit subsets |
| Pre-close gate (orchestrator, `tools/close_queue.sh`) | hold the leads; wait for 5 minutes of load below 3; a fresh checkpoint commit; a full `gov rebuild` (4-6 min); `pytest --collect-only` over `tests` in one process (about 6 s); `gov check` (about 7 min); every commit of the ticket carries `Implements:`; the tree is clean. Since 15:50 today also gate (f): the four record-reading test files (W1-06, W1-08, W1-27's path compliance, W1-07's envelope; 80 tests in 108 s) | one ticket at a time, each stops the queue on its first failure | `close_queue.sh`; queue logs `close-queue-*/queue.txt` |
| Close (`gov close`, orchestrator) | the ticket's acceptance suite (parallel, `-n auto`); then the regression, all of `tests/` but that suite (parallel); then the 263 serial-only cases alone and serially; then a re-run alone of any failing `load_sensitive` case; the ratchet judges the reds | `-q -p no:cacheprovider --tb=line`; environment scrubbed of `PYTEST_ADDOPTS`, `PYTEST_PLUGINS` and the interpreter switches; time limit 7,200 s per run | `src/gov/close/command.py:192-203, 767-895, 989-1028` |
| Gates W2-24 and W2-46 (orchestrator, later) | "the full, uncached regression runs once and is green" (W2-24); "the full, uncached regression and the dev-tier regression, both green" (W2-46) | not yet run | WBS cards W2-24, W2-46 |
| Nightly full run (DEC-852 item 3) | the full uncached regression on `w2/integrate`'s head | decided, standing from W2-66's merge; not running | no scheduler, no script (A3) |

**Where the same tests run twice or more, and what it costs.** For one ticket that closes at the first attempt:

| Run | Tests | Cost (measured) |
|---|---|---|
| Lead's verification before each return (a ticket returns 1 to 8 times: W2-50 had runs 1 to 8) | every suite, serially, one process each | 13,857 s ≈ 3.85 h of serial suite time per verification (W2-48 run 2); 3,451 s for its batch A alone |
| Close, on the merged commit | every suite again (acceptance + regression + serial-only) | 60.3 min of test runs in W2-53's clean close; 73 min wall from its start; 85 min with the queue's rebuild and gate |
| Each refused close | everything again | W2-53: 5 refused full runs, 297 min; W2-01: 80.6 min |
| W2-24, W2-46, and every night from W2-66 | everything again | about 60 to 80 min each |

So every test runs at least twice per ticket (lead and close), and a ticket that needs one resume runs everything four times before the close. Inside one run there is a further duplicate by design: W1-05's switch-over case runs W1-02, W1-03 and W1-04 again in a child pytest (516 s in my part 2).

### A3. Decided against built

| Decision | What it says (short) | State | Evidence |
|---|---|---|---|
| DEC-042 | builder tests are regression evidence only | **built** | the close runs the acceptance suite and the regression as separate runs (`command.py:192-202`) |
| DEC-372 | a latency case that fails under parallel load is re-run alone | **built**, as the serial-only list plus the `load_sensitive` re-run | `tests/acceptance/serial-only.txt`; `command.py:989-1028` |
| DEC-514 | profile `gov close`; try parallel runs; xdist installed | **done** | `log/PERF-REPORT.md` (2026-10-08) |
| DEC-527, DEC-549, DEC-554 | the regression in parallel; workers and time limit as project settings | **built** | `command.py:767-895`; path map `close_timeout: 7200`, workers `auto` |
| DEC-567 | "fast feedback at scale": result caching, merge queue, staged gates, full suite on CI machines, flaky quarantine | **mostly not built**: caching withdrawn (DEC-880); merge queue → Wave 3 (W2-L207), now decided for W2-66 as batched closes (DEC-883, today); staged gates → W2-66 (planned); CI full suite (W2-M241) → triaged to W2-38 → Wave 3; automatic flaky quarantine (W2-M242) → Wave 3 | `WAVE_2_TRIAGE.md` rows W2-M240 to W2-M242, W2-L207 |
| DEC-726 (changed by DEC-880) | no result cache; a scoped close from W2-66's merge; the full uncached run stays at W2-24 and W2-46 | **decided**; neither gate reached | register line 7717ff |
| DEC-736 | EXAMIN at adoption: W2-19 on the path; a ratchet baseline of known reds | **not built** (W2-19 open) | `.tickets/DAEO-jzvg.md` |
| DEC-757 | the `accepted_reds` ratchet; integration-side ticket edits; the `load_sensitive` quarantine | **built** (W2-53, closed 2026-10-20) | `src/gov/close/ratchet.py`; `CL-DAEO-7rr2` |
| DEC-760, DEC-762 | first entries; every entry names `fixed_by`; a check that the fix's close refuses while its entries remain | entries carry `fixed_by`: **yes**; the check: **not built** (W2-19) | path map lines 309-429 |
| DEC-766 | the lists only shrink; any addition comes first as an owner package | **followed**: additions by DEC-823 (1 entry) and DEC-871 (2), each through a package; the ratchet counts only entries added by a `Role: owner` commit (`ratchet.py:_refused_because`) | path map; `ratchet.py` |
| DEC-780 | a quiet window for closes; queued back-to-back; never a ratchet retry | **built by hand**: the orchestrator's untracked `tools/close_queue.sh` sets the lock, holds it for the whole queue, and waits for 5 minutes of load below 3 only before the first ticket; the resource gate (W2-20) is open | `close_queue.sh:12-18, 72` |
| DEC-813, DEC-823 (b) | load out of the close (W2-57): the close's own resource gate, or an isolated timing suite | **not built**; W2-57 has a card but **no ticket file** | WBS line 885; no `.tickets/` file but W2-66's names W2-57 |
| DEC-852 item 3 | every night, the full uncached regression on `w2/integrate`'s head, result in the digest | **decided** (standing from W2-66's merge); **not running**: no crontab, no script | `crontab -l`: none; `tools/`: no nightly script |
| DEC-868 | the pre-close gate: collection in one process, `gov check` after the rebuild, a fresh checkpoint; leads run the collection | **built** as the orchestrator's script and a lead-brief rule; inside `gov close` (W2-07): **not built** | `close_queue.sh`; `LEAD-w2-common.md:17`; W2-07's card |
| DEC-869 | W2-48 next | **SUPERSEDED** by DEC-880 | register 9483 |
| DEC-871 | three queue commits as accepted history; W1-38's two cases load-sensitive until W2-57 | **applied** | path map 275-283, 422-429 |
| DEC-876 | W2-48's conditions | **SUPERSEDED** by DEC-880; `test_inputs` kept "with this reason: W2-66 may use the declared inputs … or it removes them" | path map 284-290 (inert today) |
| DEC-880 / P-W2-48-8 (b)+(d) | W2-48 withdrawn; W2-66 path-scoped regression with four conditions; a 15-minute target | **decided**; W2-66 open, waiting for this report (DEC-881) | `.tickets/DAEO-c1uz.md` |
| DEC-882 (delegated, today 14:00) | DEC-843's install item stands; suite logs out of the orchestration record | **applied** (`9d8c1887`): two of finding 1's reds repaired | register 9720 |
| DEC-883 (owner, today) | batched closes on one integrated head; same-code reuse by a fingerprint without record paths; the index fresh by code fingerprint; the serial-only tests examined | **decided** for W2-66; "until W2-66 lands, today's queue runs as it is". This lens refines items 3 to 5 (P-H-9) | register 9744 |
| DEC-884 (owner, today) | W2-66 takes the first slot after this report; one combined re-pin after it | **decided** | register 9778 |
| DEC-885 (delegated, today 15:49) | W2-02's refusal; the sync keeps to the namespaces; W1-07's `doctor` case as row W2-L409 | **applied** (`f3a1079a`, `3cb740dd`). The queue also gained gate (f), which runs four record-reading files before each close | register 9814; `close_queue.sh:41-48` |
| CAP-39.a (tiers G0 to G5 by lefthook and CI; W1-40) | pre-commit G1/G2 checks and staged secrets; pre-push G3 and the evidence note; CI on push | **hooks not installed** (only `*.sample` in `.git/hooks`; W2-08 open). **CI runs on every push, but its test step is red by design**: "pytest is not on the runner" (W2-43 open; needs owner approval Q-8) | `lefthook.yml`; `.github/workflows/ci.yml`; `EXIT-PACKAGE-CI.md` |
| CAP-39.c (scheduler: dependency-aware impacted-test selection, cache) | Wave 3 | not built; W2-66 pulls a lite part forward | `contract.yaml:2338` |
| CAP-53.b (profile computed from impact) | a Wave 2 item; its ticket W2-38 moved to Wave 3 (DEC-841) | not built | `contract.yaml:3049` |

**Is the nightly full run running?** No. Nothing tests `w2/integrate`'s head between closes. Before my session, the last test run on it was W2-53's close on 2026-10-20, and my run found it red (finding 1). Since 15:50 today the queue's gate (f) runs four record-reading test files before each close, but still nothing runs between closes.

**Are the hooks and CI on?**
- **Claude Code hooks:** on (guard, containment, compaction, session start, stop, subagent stop; listed by `gov.guard.hooks`). None runs a test.
- **Git hooks:** off.
- **CI:** runs on each push of the owner's daily backup, and fails its test, `gov ci job` and evidence steps every time, as the CI exit package of 2026-10-10 says.

**The ratchet lists and their justification.**
- **`accepted_reds` (2 entries):** both are W1-42's exit-report cases (RETR-X-02 → W2-13; governance share per programme → W2-14). Both fixes are open tickets. Both entries are justified. In my run both failed as listed.
- **`load_sensitive` (30 entries, 42 cases).** Every entry names a fix:
  - 23 entries (W1-46 live sessions) → W2-M364 / W2-57;
  - W1-30 r13 → W2-M384 / W2-57;
  - W1-38 ×2 → W2-57 (+ W2-M392);
  - the three p95 cases (15 parameter sets) → W2-M332, a Wave 3 row;
  - the unit `test_follow_up` case → W2-L352, a Wave 3 row.
- **Justification.** All are justified by recorded failures under load that passed alone.
  - The three p95 cases and the unit case have a fix that is only a Wave 3 row with no date, so in practice they are permanent through Wave 2.
  - The fix of 26 entries, W2-57, has no ticket file yet.
  - In my part 2 run, on a quiet machine, every latency case passed. That supports "load, not code" as their cause.
- **The serial-only list (55 entries, 263 cases)** is wider than the quarantine. 22 of its entries (the W1-25 and W1-49 live sessions, W1-07's 300-ms help, W1-10 and W1-17 bounds, W1-18 deadlines, W1-09 races, W1-15's scan bound, W1-16's daemon cases) run alone but are not re-run when they fail. A failure under outside load still refuses a close: W1-15 H2 and W1-31 b2 were refused by a W1-46 live case before it was listed.

**Superseded decisions still in force somewhere (DEC-866).** No enforcement of a superseded decision without a recorded reason was found in code. Five stale texts were found at `21302ae9`, and one of them broke a test:
- **The tool registry's `approved_by: "DEC-843"`** for pytest-testmon and coverage. DEC-880's sweep had marked all of DEC-843 superseded, while the registry's approval field still named it, so W1-06's approvals test was red (finding 1). DEC-882 (delegated, 14:00) narrowed the mark: DEC-843's item 3, the install package, stands while the tools are installed, and the registry's `approved_by` stays.
- W2-19's KPI: "the input globs W2-48's cache keys on" (`.tickets/DAEO-jzvg.md:29, :83`).
- W2-38's KPI: "on top of W2-48's cache" (`.tickets/DAEO-g23i.md:30, :57`).
- W2-07's allowed paths: "except `src/gov/close/cache*`, W2-48's" (`.tickets/DAEO-r9ss.md:86`).
- W2-L207's triage reason: "the close bottleneck is met in Wave 2 by W2-38", although W2-38 is now Wave 3 (DEC-841).

### A4. Reliability: every refused close, flaky tests, localisation

**Every `gov close` attempt of Wave 1 and Wave 2,** read from the orchestrator's logs (`.gov-runtime/scratch/orchestrator/log/close-*.json`, `close-queue-*/`, `W2-01-close.json`, `sweep-close-DAEO-7rr2.json`). Causes are classed: **T** the ticket's own code or tests; **E** environment or repository state (governance checks already red on the baseline, a store missing an input, a test asserting a setting a later decision changed, a name clash brought in by another merge, the network); **L** machine load; **P** process (trailers on pre-base history, work without a task, a stale or missing checkpoint, a stale store, a probe made stale by a later commit, the escalation counter); **O** the orchestrator's own slip (a file of its own left uncommitted, an edit after a probe, its own queue commits without `Implements:`, a sync that copied files ignored only by their own `.gitignore`).

Wave 1: 30 attempts on 11 tickets (W1-02, W1-15, W1-30, W1-31, W1-32, W1-35, W1-38, W1-39, W1-40, W1-41, W1-42) between 2026-10-07 and 2026-10-16. **None closed.** Every Wave 1 ticket was closed with `tk close` under the bootstrap rule or by an owner decision (for example DEC-713 for W1-42). The refusals were almost all P and E: `gov close` (W1-30) was built while the tickets it judged were already done, so it judged their pre-base history (missing trailers, work without a task, containment of old merges), store gaps (`CONTEXT_FAILED: mandatory input 'G-12' not found in the store`), and governance checks already red on the baseline; five attempts were `ESCALATION_BLOCKED`. Test failures inside those runs:

| Attempt | Test failures | Class |
|---|---|---|
| W1-32 (10-09) | W1-05 p95 hook latency, two parameters | L |
| W1-30 G2 (10-10) | unit `test_follow_up` time-limit case | L (later `load_sensitive`, DEC-762) |
| W1-15 H2 (10-10) | a W1-46 live session (`developer.mozilla.org`), serial run | L/E |
| W1-30 K (10-11) | 10 unit tests of `close` (`test_measured`, `test_run_and_record`); W1-38 rulesync | **T** (W1-30's own code); L |
| W1-31 b (10-13) | W1-33 agent definition, W1-49 auto-compact window ×2 | E (tests asserting a setting a later decision changed: DEC-838) |
| W1-31 b2 (10-13) | a W1-46 live session (`static.crates.io`), serial run | L/E |
| W1-42 (10-16) | the two reds later put on `accepted_reds` | T-known |

Wave 2, as of 2026-10-21 11:36:

| When | Ticket | Outcome | Causes | Test time spent |
|---|---|---|---|---|
| 10-17 13:46 | W2-01 | refused, 6 findings | O (the ticket file edited after its probe, DEC-757 item 6), P (checkpoint stale), E (store lacked DEC-750), L (W1-05 p95 `[Read-no-role]`), plus the 2 accepted reds | 80.6 min; then **closed by owner decision** (DEC-757, a named exception) |
| 10-18 01:53 | W2-53 | refused, 7 findings | E (three hard-block checks already red: core-schema on W1-43's audit record, product-traceability on W1-42's claim commit, context-reproducibility over its 60-s limit), P (checkpoint stale) | 51.8 min |
| 10-18 15:39 | W2-53 (blocker sweep, scratch merge, leads running) | refused, 17 findings | E (W2-54's "green here" tests red on context-reproducibility), L (3 W1-46 cases failed "alone" while leads ran: DEC-780's basis), P | 55.6 min |
| 10-19 10:44 | W2-53 | `STORE_STALE`, exit 1, not counted | P | — |
| 10-19 12:01 | W2-53 | refused, 1 finding | L (W1-30 r13 time-limit case at load about 25) → DEC-823 lists it | 59.0 min |
| 10-20 08:38 | W2-53 (load 28.87 at start) | refused, 20 findings | E (W2-54's green-here tests red on the register's state; `tests/unit/secrets` shadowing the standard library's `secrets`, so three files fail to import; W1-07 and W1-25 errors), P (checkpoint stale) | 64.5 min (76 min wall) |
| 10-20 11:07 | W2-53 | `ESCALATION_BLOCKED`, exit 4 | P → DEC-870 lifts it | — |
| 10-20 11:52 | W2-54 | `TREE_NOT_COMMITTED`, exit 1, not counted | O (the orchestrator's own package file `P-W2-53.md` uncommitted) | — |
| 10-20 12:30 | W2-53 | refused, 10 findings | O (the queue's own checkpoint commits lacked `Implements:`) → DEC-871 accepted history; L (W1-38's 10-s rulesync probe) → DEC-871 lists them | 66.4 min (79 min wall) |
| 10-20 14:40 | W2-53 | **closed**, exit 0 | — | 60.3 min (73 min wall) |
| 10-20 16:04 | W2-54 | stopped by the pre-close gate: `gov check` red (core-schema does not know W2-53's new `close` record type; W2-02 defines it) | E/P → DEC-872 | gate only |
| 10-21 02:37 | W2-02 | `TREE_NOT_COMMITTED`, exit 1, not counted | O (the sync copied W2-48's cache stores, ignored only by their own `.gitignore`) | — |
| 10-21 14:20 (during my session) | W2-02 | refused (`CHECK_FAILED`, exit 3), 2 findings | E: W1-08's red from the record commit of finding 1, which the gate's `gov check` passed. Unknown: W1-07's `test_every_command_returns_the_envelope[doctor]` failed. The record names it with no reason. Alone at the same commit, in my private copy, it passed in 9.5 s (15:38), so load or the shared machine state is the likely cause; it is on no list | 63.9 min of test runs (parallel 1,987 s for 15,446 cases, serial 1,843 s for 263); 75.6 min wall |

**Totals.**
- 43 attempts across both waves: 30 in Wave 1 and 13 in Wave 2, counting W2-54's stop at the gate and W2-02's refusal at 15:36 today.
- One ticket closed cleanly: W2-53, on its eighth attempt, about 62 hours after its first.
- The full regression ran in **18 refused attempts** (Wave 1: 11, 581 test minutes; Wave 2: 7, 442 test minutes), about **17 hours** of machine time in quiet windows.
- In those runs the tests found the ticket's own code at fault **once** (W1-30 K's unit tests), plus W1-42's known reds. Every other test failure was load (9 occasions), the repository's state (5, W2-02's W1-08 red included) or, once, unknown (W2-02's W1-07 case, which passed alone).
- The other refusals were process and the orchestrator's slips, which a one-minute check finds.
- The pre-close gate (DEC-868) answers exactly this. It has already stopped one close in minutes instead of an hour (W2-54, 10-20 16:04).
- But until 15:50 today the gate ran none of the tests that read the repository's state, and its path-map check measures nothing (W2-M214). That is why W1-08's red reached W2-02's full close. Its new step (f) now runs four of those test files first.

**Flaky tests today.** Handled by lists the owner keeps (DEC-757, DEC-760, DEC-762, DEC-766):
- `load_sensitive` (30 entries, 42 cases): a listed test that fails is re-run alone inside the same close and counts only if it passes; it is reported by name. Never a retry of the whole close (DEC-780 item 3). Additions only by an owner package; every entry names its fix. Four entries name only a Wave 3 row as their fix.
- `serial-only.txt` (55 entries, 263 cases): run alone after the parallel run. 22 of its entries are not on `load_sensitive`, so their failure under outside load still refuses a close.
- No automatic detection: nothing records each test's outcome over time, so a flaky test is found when it refuses a close (W2-53's three load refusals each became an owner package: P-W2-47, P-W2-55).
- At least two flaky cases are on no list. W1-07's copy races git's background gc: my part 3 hit `shutil.Error … .git/objects/03 … No such file` in W1-07's setup (one error in 14,260 cases), the race W2-48's lead had recorded as a residual. W1-25's per-test copy races the same way: one case errored at setup in two of my three runs of it at `2b254458`. In a close either would refuse.

**How a failure is localised today, and how long it takes.**
1. The close prints each failure as one line (`--tb=line`), names it in the refusal and writes a repair ticket.
2. The reason is often not in that line: W2-48's lead noted that its failure output "names the failing tests (`FAILED <id>`) but not their reason; a lead must re-run to read why".
3. Someone re-runs the test alone, in a lead or in the orchestrator's session, then decides: a load package to the owner, a repair round, or an orchestrator fix.
4. Then the close queue waits for its next quiet window and the full run starts again.
5. W2-53's refused attempts were 7 to 21 hours apart (10-18 01:53, 10-18 15:39, 10-19 12:01, 10-20 08:38, 10-20 12:30). The re-run alone takes seconds to minutes; the cycle around it takes most of a day.
   - **Today's example.** W2-02's close ran 75.6 minutes and named W1-07's `doctor` envelope case as red, with no reason. My re-run of that one case alone, at the same commit, took 10 seconds and passed. Nothing kept from the close can now say whether load, git's gc race or the shared `/tmp` folder (finding 14) made it fail. The JUnit XML of C2's localisation item would have kept the assertion text.
6. Nothing bisects: no `git bisect` and no culprit finding is used or built, because a refusal is always about one known ticket's merge.

### A5. Evidence today: what a close record says about the tests

There is one close record in the whole history, W2-53's (`docs/close/DAEO-7rr2/CL-DAEO-7rr2.md`, written 2026-10-20 14:53 UTC). It says about the tests:

| Field | What it holds | What it does not say |
|---|---|---|
| `tests_run` | totals: 14,652 passed, 2 failed, 0 errors, 31 skipped | which tests; which were skipped and why |
| `test_runs` | three runs, each with form (`parallel`, `serial-afterwards`), seconds, counts and `workers: auto`; the serial run lists its 55 entries | the command line, the interpreter, pytest and xdist versions, the worker count actually used, the machine load |
| `accepted_reds` | the two listed reds, each with `result: failed` | — |
| `load_sensitive` | `[]` (no re-run was needed) | — |
| `check_commit` | `872874e6…`, the commit `gov check` ran on | it appears only when the ticket's commits touched a governance prefix (`command.py:1049`); there is no field naming the commit or tree **the tests ran on** |
| `tests_produced` | the ticket's test files | — |
| (none) | — | the scope of the validation (scoped, integration or full); tests that were collected but deselected |

Three gaps, each checked against the code and the run:

1. **The tested commit is implied, not stated.** `gov close` refuses unless the working tree is `HEAD` (`_check_tree`) and the store is of `HEAD` (`_check_store`), so the tests did run on `HEAD`. But the record names `HEAD` only through `check_commit`, which is absent for a ticket that touches no governance file, and through the checkpoint it points to. A reader must reconstruct it.
2. **Two collected tests never run anywhere, and no record says so.** W2-54's conftest deselects its two `shared_gpu` cases unless `-m shared_gpu` is given (`tests/acceptance/W2-54/conftest.py:23-29`). Every close and every lead run prints "2 deselected" (the queue logs: "14685/14687 tests collected (2 deselected)"), but the close's count parser reads only passed, failed, error and skipped (`command.py:936-941`). The record's "regression" therefore means "every collected test but two", and nothing records the two.
3. **Skips are counted, not named.** 31 skipped (W2-53's record); `skip` is "counted, not refused" (DEC-500, `command.py:792`). W2-M162 ("skips above a threshold refuse, or are justified per case") is triaged to W2-19 and open.

**Could a record be read as full validation when it was not?** Today's record states counts that look like "everything" while two tests never ran and 31 skipped for reasons nobody reads; it is not false, but "full" is nowhere defined. The leads' returns are free text in the twelve fields: most leads ran every suite, but some briefs narrowed verification (W2-63: "`gov check` and the full acceptance regression were not run; the brief limited verification to these suites"; W2-01 run 5: "I ran no suites myself"). They said so honestly; nothing machine-readable separates a full verification from a partial one. Once W2-66 lands, a scoped close will produce the same kind of record unless the record gains an explicit scope (C3).

**Wave 1 tickets have no close record at all:** none closed through `gov close`; each closed by `tk close` under the bootstrap or by an owner decision (A4). Their evidence is narrative, in `governance/project/bootstrap.md` and the register.

### A6. Test quality: a mutation sample on three modules (two ran)

**Method.**
- The guard refused installs, so mutmut and cosmic-ray could not be installed. mutmut would not fit anyway: its active mutant travels in an environment variable that a scrubbed child drops (B2).
- I used my own single-line mutator (`scripts/mutate.py`). Its operators: comparison flip, `and`/`or` swap, condition negation, `return X` → `return None`, `True`/`False` swap, small integer + 1, call statement → `pass`.
- Each mutant edits one node by column range and leaves the rest of the file byte for byte. It is applied in my clone, the tests that executed the mutated line run (from the who-tests-what map, child processes included; at most one failure needed: `--maxfail=1`), and the file is restored.
- A mutant is **killed** if any of those tests fails, **survived** if all pass, and **not covered** if no measured test executes its line.
- **Controls first.** For each module, the union of those tests ran once with only a comment line appended to the file (A6 controls, 15:40 to 15:42). `ratchet.py`'s 31 tests and `claims.py`'s 126 all passed. For `record.py`, 11 of 629 tests failed or errored: 9 in this control (1 failed, 8 setup errors) and 2 in B2's earlier control. They were taken out of every `record.py` item before its run, so they cannot count as kills.
  - **What those 11 are.** I first suspected the untracked backup file my edit leaves beside the source. A probe in a separate worktree refuted that: one W1-25 case errored in both runs on the clean tree, and both probed cases passed in the run with the file present. The error is `shutil.Error … .git/objects/00 … No such file or directory`. It is W1-25's per-test copy of its session repository racing git's background gc, the same race as W1-07's (finding 2).
  - So a race error could also fake a kill in a mutant's run. From the B2 phase on, the runner keeps each failure's message and flags that race. The A6 results below were checked for it in their JUnit files.
- The items of each module ran in a shuffled order (seed 882), so the part that ran is still a random sample if a run is cut short.
- **Modules:**
  - `src/gov/close/ratchet.py` (shared core; unit-tested in-process and through W2-53's acceptance suite): all 43 mutants;
  - `src/gov/tasks/claims.py` (non-core; W1-09's drivers and many children): all 33;
  - `src/gov/checkpoint/record.py` (non-core; W1-25 and children): a seeded sample of 40 of 86.

**Results** (15:42 to 15:50, clone code at `21302ae9`, load 5 to 7; the close lock returned at 15:50 and stopped the rest; `logs/results_a6.jsonl`, `logs/analysis_a6.txt`):

| Module | Mutants sampled | Covered by a test | Run | Killed | Survived | Score (killed of run) |
|---|---|---|---|---|---|---|
| `close/ratchet.py` (shared core) | 43, all | 41 | 26 | 23 | 3 | **88.5 %** |
| `tasks/claims.py` | 33, all | 33 | 21 | 19 | 2 | **90.5 %** |
| `checkpoint/record.py` | 40 of 86, seeded | 38 | 0 | — | — | not run (close lock) |

- Each item ran in 1 to 61 seconds; killed items stop at their first failure. No kill rested on the gc race alone (each JUnit file checked).
- The runs are a random part of each module's sample, because the order was shuffled: 26 of 41 covered mutants for `ratchet.py`, 21 of 33 for `claims.py`. Two modules ran, the brief's lower bound; `record.py` did not.

**The survivors, read one by one.**
- `claims.py:39`, `time.sleep(0.01)` dropped, and `claims.py:60`, `os.close(descriptor)` dropped: nothing a test can observe (a 10 ms pause in a wait loop; a file descriptor of a short process). Equivalent in practice.
- `ratchet.py:108`, `[:12]` to `[:13]`: the length of a commit id inside a message. Cosmetic.
- `ratchet.py:44`, `ok=(0, 128)` to `(0, 129)`: no test has a commit that holds no path map. The mutant would make the close stop on a git error, so the gap fails closed.
- **`ratchet.py:93`, `and` to `or`:** with it, an `accepted_reds` or `load_sensitive` entry whose required field is blank counts. It survived the 30 tests that run the line. The refusal on line 95 (an entry that does not give each of its fields) is executed by no test in the who-tests-what map, and every ratchet test fills every field of its entries. **That is finding 19:** the rule that every entry names its fix (DEC-760, DEC-762) has no test.
- Not covered: `ratchet.py:95` (above) and `:107` (an entry no commit added, a defensive branch); `record.py:32` and `:73`.

**What it says about test quality.** On these two modules the tests kill about nine of ten sampled mutants, and the survivors are mostly harmless. That is a good level for unit and acceptance tests together, measured on the code that decides a close (`ratchet.py`) and on claims. The one real gap is a protective rule nobody exercises, the kind of gap mutation testing exists to find.

## Part B. Research: industry practice and free tools

### B1. Industry practice, from primary sources

All sources were read on 2026-10-21, through two research helpers working only with WebSearch and WebFetch: R1 (industry practice) and R2 (peer-reviewed work). Their full digests are in my folder, `/tmp/gov-os-assessment-H/research/`. Quotations are exact unless marked as a paraphrase.

**How teams with thousands of tests choose what runs at each layer.**

| Layer | What large teams do | Source |
|---|---|---|
| L1 (seconds) | Run small, hermetic tests and cached results. At Google, small tests "must run in a single process" and "aren't allowed to sleep, perform I/O operations, or make any other blocking calls". Bazel reruns a test only if "Bazel detects changes in the test or its dependencies" or "the test failed". | *Software Engineering at Google* ch. 11 (Bender, 2020), https://abseil.io/resources/swe-book/html/ch11.html; Bazel user manual, https://bazel.build/docs/user-manual |
| L2 (minutes) | Run the affected tests, found through a dependency graph: "The primary mechanism for determining which tests need to be run is an analysis of the downstream dependency graph for every change." Pants: `pants --changed-since="$MERGE_BASE" --changed-dependents=transitive test`. Nx: "The recommended approach is to set the base SHA to the latest successful commit on the main branch." | SWE at Google ch. 23 (Tannenbaum, 2020), https://abseil.io/resources/swe-book/html/ch23.html; Pants docs, https://www.pantsbuild.org/stable/docs/using-pants/advanced-target-selection; Nx docs, https://nx.dev/ci/features/affected |
| L3 (merge gate) | Run "only fast, reliable" tests before submit, usually "just those for the project where the change is happening". Then test the merged result before or as it lands: GitHub's merge queue tests each pull request against "the latest version of the `base_branch` as well as changes from pull requests ahead of it"; GitLab's merge trains test "against the combined changes of every merge request ahead of it"; Uber's SubmitQueue keeps "an always green master branch at scale". | SWE at Google ch. 23; GitHub Docs, "Managing a merge queue"; GitLab Docs, "Merge trains"; Ananthanarayanan et al., EuroSys 2019, DOI 10.1145/3302424.3303970 (abstract only) |
| L4 (post-submit / nightly) | Run every affected test after submit, including the large and slow ones: "we use TAP to asynchronously run all potentially affected tests, including larger and slower tests". Batch the runs, and split a failing batch "into individual changes". Microsoft's Test Impact Analysis (TIA): "TIA can be conditioned to run all tests at a configured periodicity. Setting this option is recommended". Develocity runs its "relevant tests" before merge and its "remaining tests" "nightly or pre-release". | SWE at Google ch. 23; Microsoft Learn, "Use Test Impact Analysis"; Develocity docs, "Predictive Test Selection" |
| L5 (release) | Run the full suite again on the release candidate (RC), "even if it is the same suite that CB just ran against the code on post-submit", "For auditability: If an engineer wants to check an RC's test results, they are readily available and associated with the RC." | SWE at Google ch. 23 |

**Test impact analysis (TIA) and dependency-aware selection.**
- **Microsoft's TIA is dynamic and fails safe.** Its selection "includes existing impacted tests, previously failing tests, and newly added tests". "For commits and scenarios that TIA can't understand, it falls back to running all tests"; "When TIA opens a commit and sees an unknown file type, it falls back to running all tests". To check it: "Run TIA selected tests and then all tests in sequence". (Microsoft Learn, read 2026-10-21)
- **Meta: ML selection with a stated recall.** It runs "just a third of all tests that transitively depend on modified code" and reports "over 95% of individual test failures and over 99.9% of faulty changes". Selecting by build dependencies alone "would cause as many as a quarter of all available tests to be exercised for each change". Recall is reported at two levels, per failing test and per faulty change; a selection KPI should say which level it uses. (Machalica et al., ICSE-SEIP 2019, https://arxiv.org/abs/1810.05286; Engineering at Meta blog, 2018-11-21)
- **Safety (R2).** A selection technique is "safe" when it keeps every test that could reveal a fault caused by the change (Rothermel & Harrold, TOSEM 1997). File-level dynamic dependencies (Ekstazi: Gligoric, Eloussi, Marinov, ISSTA 2015) are the practical safe point. Process boundaries need explicit treatment: RTSLinux traces the files a test's spawned processes touch (Celik, Vasic, Milicevic, Gligoric, FSE 2017). That is the problem this repository has.
- **Static selection** (import or build graphs) is cheap but blind to links that exist only as command-line strings. Pants warns that "dependency inference cannot infer everything, such as dependencies on `resource` and `file` targets". Jest's `--onlyChanged` "requires a static dependency graph (ie. no dynamic requires)".

**Risk-based widening.**
- Microsoft TIA runs everything for unknown file types.
- Nx and Pants treat a lockfile change as touching everything.
- pytest-impacted marks all tests impacted when `pyproject.toml`, `pytest.ini` or a requirements file changes, and offers "invalidate all" globs for non-Python files.
- Develocity "will *always select* recently flaky tests".

**Caching, parallelism, sharding.**
- Bazel caches test results keyed on declared inputs. Its tests must be hermetic: they "ought to access only those resources on which they have a declared dependency". A cache works only where inputs are declared or traced.
- Sharding by recorded durations: Develocity Test Distribution ("Historical test execution data… is used to create balanced partitions"), pytest-split, and cargo-nextest partitions.
- Google cut presubmit runtime "by a factor of 14, with virtually no flakiness" by making it hermetic (ch. 23).

**Flaky-test management.**
- **Scale.** Google sees "about 1.5% of all test runs reporting a 'flaky' result" and "Almost 16% of our tests have some level of flakiness" (Micco, Google Testing Blog, 2016-05-27). Flakiness grows with size: "0.5% of our small tests were flaky, 1.6% of our medium tests were flaky, and 14% of our large tests were flaky" (Listfield, 2017-04-17).
- **Quarantine with an owner and a deadline.** Atlassian opens a ticket "for the owning team with pre-decided due dates", and lets a test out after it "remains healthy for a configured period" (Atlassian Engineering, 2025-12-08). GitLab: "Quarantining a test should be temporary: tests must be fixed, removed, or moved to a lower test level", with "3 days maximum" for fast quarantine and "3 months maximum" for long-term (GitLab Handbook).
- **Why some teams refuse a retry that lets a gate pass.** Google's three-in-a-row flaky marking "encourages developers to ignore flakiness" and delays a real breakage by up to three runs. Ignored flaky failures "may represent real faults in the production code" (Lam et al., ISSTA 2019, Microsoft). Azure DevOps does not suppress flaky failures by default. Bazel's `flaky` attribute "is generally discouraged". DEC-780 item 3 ("the ratchet does not retry a load-sensitive case to let a close through") matches this camp.

**Failure localisation.**
- `git bisect run` uses exit codes: 0 for good, 1 to 127 except 125 for bad, 125 to skip (https://git-scm.com/docs/git-bisect).
- Google splits failing batches automatically. Its Flake Aware Culprit Finding uses "Bayesian inference and noisy binary search" and was "more accurate overall than all versions of Bisect" on 13,000+ breakages (Henderson et al., ICST 2023).
- Delta debugging shrinks a failing case to a minimal one; it reduced "896 lines of HTML to a single line" (Zeller & Hildebrandt, IEEE TSE 2002, abstract).

**Recording what a run did and did not validate.**
- **Bazel's Build Event Protocol** records each test's `status`, `cached_locally`, `attempt_count` and `shard_count` (https://bazel.build/remote/bep).
- **Develocity** labels unselected tests: "A test outcome of 'NOT SELECTED' indicates that the test class was skipped because Predictive Test Selection's machine learning system determined that it's unlikely to provide a useful test signal".
- **The in-toto test-result predicate** (v0.1) records `result`, `configuration` and `passedTests`/`warnedTests`/`failedTests`, "to verify: (1) that all tests were in fact run, and (2) that all required tests passed". It has no field for skipped or unselected tests, so a selected-versus-full scope has to go in `configuration` (https://github.com/in-toto/attestation/blob/main/spec/predicates/test-result.md).
- **Google** ties a release candidate's results to it "for auditability".

**What the peer-reviewed work says** (helper R2; each paper read 2026-10-21; figures quoted as found, section given where recorded):

| Question | Result | Source |
|---|---|---|
| What "safe" selection means | "An algorithm that selects every fault-revealing test in T is safe" (§3.1.2). It holds only "when all factors that might influence the output of P′, except for the code in P′, are kept constant" (Yoo & Harman §4). | Rothermel & Harrold, TOSEM 1997, doi:10.1145/248233.248262; Yoo & Harman, STVR 2012, doi:10.1002/stv.430 |
| File-level dynamic selection | Ekstazi "reduced the end-to-end testing time 32% on average, and 54% for longer-running test suites". It offers "no special support for dependencies other than files". | Gligoric, Eloussi, Marinov, ISSTA 2015, doi:10.1145/2771783.2771784 |
| **Tests that spawn processes** | RTSLinux "tracks the entire process tree of the test" with a kernel module. It skips 74.17 % of tests and saves 52.83 % of time on 21 Java projects that "escape the JVM by spawning new processes". In-process tracking "collects only 16.99% of dependencies collected by RTSLinux". Overhead is 14.90 % (kernel module) against 61.16 % with strace. | Celik, Vasic, Milicevic, Gligoric, ESEC/FSE 2017, doi:10.1145/3106237.3106297 |
| **Python specifically** | "Because eager importing executes substantial global code during test initialization, many tests exhibit broad coverage even without semantic dependence." A file-level, Ekstazi-style selector for Python achieved "7.42% test reduction and 3.10% time reduction". A name-based selector skips 69.90 % of test files and cuts 45.59 % of time, safe on 99.6 % of commits. | Wang, Pradel, Liu, NameRTS, arXiv:2605.25356 (ISSTA 2026 per the arXiv comment; proceedings DOI not verified) |
| Coverage-based selection in Python | A missed-fault rate of 0–2 % at file level and 16–24 % at line level, measured by mutation testing (abstract only). | Kauhanen et al., SANER 2021, doi:10.1109/SANER50967.2021.00077 |
| Coarse against fine selection in CI | Module-level selection ran 58.8 % of tests in 79.7 % of the time; class-level ran 30.6 % in 76.0 %. Coarse selection costs little extra wall time. Almost all missed failures (38 of 39) were flaky. The one real miss came from a non-source file the configuration excluded. | Shi, Zhao, Marinov, ISSRE 2019, doi:10.1109/ISSRE.2019.00031 |
| What industry selects | Facebook, Google and Microsoft "perform project-level RTS, rerunning tests in a changed library and in all its transitive clients". | Gyori et al., ISSRE 2018, doi:10.1109/ISSRE.2018.00022 |
| How few affected tests fail | "of the 5.5 Million affected tests … only 63K ever failed". Running only targets within MinDist=10 or 6 would save 42 % and 55 %. | Memon et al., ICSE-SEIP 2017, doi:10.1109/ICSE-SEIP.2017.16 |
| Static against dynamic | Class-level static selection is "comparable to Ekstazi … but at the risk of being unsafe sometimes": safety violations in 0.2 % of revisions, against 10.6 % for method level. | Legunsen et al., FSE 2016, doi:10.1145/2950290.2950361 |
| Flaky causes | Async wait 45 %, concurrency 20 %, test order 12 % (Luo et al., FSE 2014). In Python, order dependency causes 59 % and infrastructure 28 % (Gruber et al., ICST 2021). 46.5 % of flaky tests are resource-affected (Silva et al., TSE 2024). Selection unaware of test dependencies gives flaky failures in "90% of the human-written test suites with dependent tests" (Lam et al., ISSTA 2020). | doi:10.1145/2635868.2635920; 10.1109/ICST49551.2021.00026; 10.1109/TSE.2024.3462251; 10.1145/3395363.3397364 |
| Quarantine's cost | Practitioners: "it's a dangerous way to go because then suddenly the number of tests goes down". | Habchi et al., ICST 2022, doi:10.1109/ICST53961.2022.00034 |
| Mutation testing | "73% of real faults are coupled to the mutants generated by commonly used mutation operators". Google mutates "Only lines affected by the diff under review that are covered and are not arid", "at most one mutant" per line; reported usefulness "improved from 20% to 80%". | Just et al., FSE 2014, doi:10.1145/2635868.2635929; Petrović & Ivanković, ICSE-SEIP 2018, doi:10.1145/3183519.3183521 |
| Bisection | Batch testing with bisection saved 72 % of test executions, 42 % with flakiness (Najafi et al., ESEC/FSE 2019). Selecting tests inside bisection saves "74% of testing effort on average" (Saha & Gligoric, FASE 2017). | doi:10.1145/3338906.3338944; 10.1007/978-3-662-54494-5_4 |

**For this repository, the literature predicts what was seen:**
- W2-48's 3 % is NameRTS's 3.10 % for file-level selection in Python, made worse by children testmon cannot see (RTSLinux's 16.99 %).
- Selection by suite costs little more wall time than fine selection (Shi et al.).
- The safety hole is the non-code inputs and the shared helpers a map omits (Shi et al.'s one real miss).

### B2. Free tools to glue, and what the trials showed

**The inventory** (helper R3; every fact from the project's own page or registry, read 2026-10-21; full digest with URLs in my folder). Licence, latest version (date), maintenance, whether it works when a test runs the code in a child with a scrubbed environment, and fit here:

| Need | Tool | Licence | Latest (date) | Maintenance | Child-safe? | Fit here |
|---|---|---|---|---|---|---|
| Change impact (dynamic) | pytest-testmon | MIT | 2.2.0 (2025-12-01) | slow | **no** (in-process coverage; no documented subprocess path) | poor: measured below |
| Change impact (dynamic) | coverage.py, per-test contexts, `[run] patch = subprocess` (7.10+) | Apache-2.0 | 7.16.2 (2026-09-27) | active | **only if** `COVERAGE_PROCESS_START`/`_CONFIG` reaches the child, which a scrubbed environment drops | **good with a shim**: measured below |
| Change impact (static) | pytest-impacted (git diff + AST import graph) | MIT | 0.35.0 (2026-10-01) | active, beta, young | static: blind to CLI strings | partial |
| Change impact (static) | tach `tach test` | MIT | 0.35.3 (2026-10-06) | changed hands in Nov 2025 after being marked unmaintained | static | partial to poor |
| Import graph library | grimp | BSD-2-Clause | 3.17 (2026-09-04) | active | static | good as a building block (my stand-in: a standard-library `ast` graph) |
| Changed-file picker | pytest-picked | MIT | 0.5.1 (2024-11-06) | slow | static | poor (test files only) |
| Import-graph selector | pytest-incremental | MIT | 0.6.0 (2021-04-24) | **unmaintained** (deprecation notice 2026-02-05) | static | poor |
| Gate on changed lines | diff-cover | Apache-2.0 | 10.6.0 (2026-09-22) | active | yes, given child coverage | good as a gate, not a selector |
| Build system selection | Pants (`--changed-since --changed-dependents=transitive`) | Apache-2.0 | 2.33.1 (2026-08-27) | active | static; hermetic runs | strong but heavy to adopt |
| Parallel run | pytest-xdist (`load`, `loadfile`, `loadgroup`, `worksteal` since 3.2) | MIT | 3.8.0 (2025-07-01) | code active, release slow | yes | good (installed): use `worksteal` |
| Duration shards | pytest-split | MIT | 0.11.0 (2026-02-03) | slow | yes | good for CI shards |
| Flaky signal | pytest-rerunfailures (reruns shown as R) | MPL-2.0 | 16.7 (2026-09-17) | active | yes | good as a signal; never to pass a gate (DEC-780) |
| Timeouts | pytest-timeout | MIT | 2.4.0 (2025-05-05) | commits active | partial (children not documented) | good, beside the close's own limit |
| Order dependence | pytest-randomly | MIT | 5.0.0 (2026-09-01) | active | yes | good (nightly only) |
| Mutation | mutmut 3 (trampolines; active mutant from `MUTANT_UNDER_TEST`) | BSD-3-Clause | 3.8.0 (2026-09-12) | active | **no as is** (the scrubbed child loses the variable) | poor here |
| Mutation | cosmic-ray (edits files on disk; `cr-filter-git`) | MIT | 8.7.0 (2026-08-09) | active | **yes** | good but costly; put a selector in its test command |
| Evidence | JUnit XML (`pytest --junitxml`) | MIT (pytest) | built in | active | n/a | good: the per-test record |
| Evidence | in-toto test-result predicate v0.1 | Apache-2.0 | spec v1.2.0 (2026-03-18) | active | n/a | good for releases; no field for unselected tests |
| Rust | cargo-nextest (partitions, flaky marking, JUnit, `rdeps()`), cargo-mutants, cargo-llvm-cov | MIT/Apache | 0.9.149 (2026-10-20); 27.1.0; 0.9.1 | active | yes / yes / conditional | good |
| TypeScript | Vitest (`related`, `--changed`, `--shard`), Jest (`--findRelatedTests`), Nx / Turborepo affected, StrykerJS | MIT / Apache-2.0 | 5.0.5; 30.5.2; 23.3.0; 2.11.10; 10.0.0 | active | static imports only; Stryker's variable conditional | good |

**Trials on my clone, on a repository whose tests mostly run `gov` in a child.**
- The guard refused installs, so no new tool could be trialled.
- I trialled the three approaches that matter, with the installed packages and standard-library scripts: the dynamic in-process tool (testmon), the static import graph (grimp's method), and coverage across processes (coverage.py with a shim).
- I measured each against planted faults whose catching tests I established by running them.

**Trial 1: plain pytest-testmon 2.2.0, a fault in subprocess-only code.**
- **Setup:** suite W1-32 (`gov status`) in a throwaway clone. Planted fault: `src/gov/status/command.py:69`, `if "CLAIMED" in reasons:` became `not in`.
- **Without selection** the fault is caught: 2 failed, 78 passed (`test_a_claimed_ticket_is_listed_with_its_holder`, `test_a_ticket_in_progress_is_listed_as_claimed`).
- **testmon's recording run:** 80 passed (`testmon: new DB`).
- **With the fault and testmon's selection:** `testmon: changed files: tests/acceptance/W1-32/test_w1_32_status_read_only.py, unchanged files: 18` … `collected 11 items / 11 deselected / 0 selected`. **0 of 80 tests ran: the fault was missed.** testmon never saw `status/command.py` as a dependency, because no test runs it in its own process.
- **Two side facts:**
  - testmon crashes when pytest's cache plugin is off (`INTERNALERROR … KeyError: 'lf'`), and `gov close` always passes `-p no:cacheprovider`.
  - testmon switches its selection off whenever `-m` is used ("selection automatically deactivated because -m was used"). EXAMIN's `addopts = "-m 'not live'"` would therefore switch it off on every run unless `--testmon-forceselect` is set.
- **W2-66's declared map** selects W1-32 for this file and catches the fault.

**Trial 2: static import-graph selection** (the method of grimp, pytest-impacted and tach; my standard-library `ast` version, `scripts/import_graph.py`).
- 114 `gov` modules and 402 import edges.
- Of 620 test files, 132 import a `gov` module in their own process. Of the 531 acceptance test files, **only 48**.
- So for 483 acceptance files (91 %) a static selector has no edge at all. Every fault that only acceptance tests catch is invisible to it unless the CLI is modelled as depending on everything, which selects everything.
- It does work for the unit tests (in-process) and for test helpers imported across suites (finding 3), which is where the design uses it.
- On the planted faults below it detected 18 of 22. It missed the four that only acceptance tests caught.

**Trial 3: a who-tests-what map across processes, with the installed coverage 7.16.2.**
- **Method.** An 83-line `sitecustomize`-style shim (`govh_covstart.py`, loaded by a `.pth` line in my venv) starts coverage in every Python process of the venv's interpreter.
  - It finds the test a process belongs to by walking up its parent chain to the pytest worker, which writes the running test's id to a file. So it works when the test gave the child an environment built from scratch: the case that defeats `COVERAGE_PROCESS_START`.
  - A small pytest plugin switches the worker's own context per test.
  - Run: part 1's 14,260 cases, 8 workers. The unit tests were re-mapped with the C tracer, because the `sysmon` core does not keep per-test contexts in-process (coverage's own warning `no-sysmon-context`).
- **Results.**
  - **Attribution:** 10,404 of the 10,624 tests that start `gov` in a child (**97.9 %**) produced child coverage attributed to them; 23,610 child data files were attributed. 12,749 of 14,260 tests executed some `gov` line.
  - **Overhead:** wall time 2,296 s against 2,083 s plain (**+10 %**); summed case time 14,464 s against 11,292 s (**+28 %**). The data took 1.9 GB in 30,544 files. Building the map took 28 s with 8 processes.
  - **What it shows about W2-66's declared map.**
    - For **54 of the 64 non-core files**, tests in suites the declared map does not select execute the file. For example, `src/gov/tasks/claims.py` is declared for W1-09 and W1-30, and 1,324 tests in 26 other suites execute it.
    - Selecting by measured suites would cost a median **38.1 %** of the full parallel run's time, against **14.6 %** for the declared map.
    - Executing a file is not testing it, so the planted faults below decide whether the declared map's narrowness matters.
  - **Gaps:** 220 child-starting tests (2.1 %) left no data: interpreters outside the venv, and processes killed or ended by `os._exit`. The hook scripts W1-29 runs left none. A production version records such tests as "not measured" and selects them always.

**Planted faults (32 planned in 16 non-core modules, with controls; 23 ran before the close lock returned, 22 of them valid).**
- **Method:**
  - (1) Each fault is one line from `scripts/mutate.py`: a comparison flipped, a condition negated, or a return value replaced, on a line the map shows executed. Two faults per module, chosen with seed 881.
  - (2) Ground truth: every test that executed the line was run with the fault (`scripts/mutation_runner.py`, private `/tmp`, file restored after each).
  - (3) A control per module (a comment line appended) removes tests that react to the file's text rather than its behaviour. Controls ran for `status/command.py` (none), `checkpoint/record.py` (11 tests, W1-25's copy racing git's gc among them; A6) and `tasks/claims.py` (none). The B2 controls for the other modules were next in line when the lock returned. No fault's detection rests only on tests of the 13 whole-tree-copy suites, where that race lives.
  - (3a) The runner lists W1-35's tests last on the command line (finding 17).
  - (4) Each strategy "detects" a fault when it selects at least one test that failed with it.
  - (5) Time is the summed part-1 durations of what a strategy selects, as a share of part 1's 11,292 s. Time saved is the rest.
  - **Runs:** 13:30 to 14:09 and 15:36 to 15:41, clone code at `21302ae9`, load 2 to 7 at each start, every item gated on the close lock. Logs: `logs/results_b2.jsonl`; analysis: `logs/analysis_b2.txt`.

**Results: 22 valid planted faults in 13 modules, every one caught by the tests that execute its line.**

| Strategy | What it selects | Faults detected | Mean recall (lowest) | Test time selected: mean (median) |
|---|---|---|---|---|
| W2-66's declared map | `tests/unit` plus the suites whose ticket's `allowed_paths` match the file | **22 of 22** | 0.84 (0.10) | 12.6 % (**9.0 %**) |
| the same without `tests/unit` (a check only) | the matching suites alone | 19 of 22 | 0.55 (0.00) | 11.1 % (7.5 %) |
| static import graph | test files that import the module, directly or through other modules | 18 of 22 | 0.30 (0.00) | 0.2 % (0.1 %) |
| measured map, by suite | `tests/unit` plus every suite with a test that executed the file | 22 of 22 | 1.00 (1.00) | 43.7 % (39.5 %) |
| measured map, by test | every test that executed the file | 22 of 22 | 1.00 (1.00) | 21.7 % (18.6 %) |

Recall is the share of the catching tests a strategy selects.

**What the results show.**
1. **W2-66's declared map was safe on every fault that ran.** It caught all 22 while selecting a median 9 % of the test time, so it would save about 91 % of the parallel run on such changes.
   - Its margin can be thin. For `record.py:139` and `claims.py:37` it selected only one catching test in ten: one or two declared suites carried the detection, while the fault broke tests in up to five other suites.
2. **`tests/unit` is part of its safety.** Without it the declared suites would have missed 3 of the 22 (`portability.py:114`, `cli/main.py:121`, `doctor/command.py:217`). W2-66's rule includes `tests/unit` and must keep it.
3. **The static import graph missed 4 of 22:** each was caught only by acceptance tests that run `gov` in a child. That is what Trial 2 predicts.
4. **The measured map caught the same 22 with every catching test,** at four times the declared map's time (by suite). On these faults it added catching tests, not caught faults. Its use is a cross-check in the nightly, and a widening once it shows a miss.
5. **Not run.** One more fault (`portability.py:50`) ran but gave an invalid result: its only "catch" was W1-35's collection error (finding 17). I set it aside; its re-run, with W1-35 listed last, was queued. Nine more faults did not run at all before the close lock returned at 15:50. Among them are all six of the three modules with the widest reach (`config/loader.py`, `store/loader.py`, `tasks/tickets.py`; 1,400 to 2,900 executing tests each), where a declared map is most likely to miss. The plans are in my folder, and `scripts/run_rest.sh` resumes them.
   - **So the verdict holds for narrow and medium modules. For the widest it is unmeasured,** which is one more reason for the nightly cross-check.

**What each candidate is fit for.**

| Candidate | Works with child processes here? | Selection accuracy on planted faults | Time saved | Licence, maintenance | Verdict |
|---|---|---|---|---|---|
| pytest-testmon | no (0 of 80 selected for a caught fault) | — | — | MIT, slow | do not use here; possible for EXAMIN (in-process), with `--testmon-forceselect` |
| static import graph (grimp, pytest-impacted, tach) | no edge for 91 % of acceptance files | 18 of 22 detected (mean recall 0.30) | 99.8 %, because it selects almost nothing | BSD-2 / MIT | use for unit tests and test helpers only |
| W2-66's declared map (tickets' `allowed_paths` + `tests/unit`) | yes (no tracing needed) | **22 of 22** (mean recall 0.84, lowest 0.10) | median 91 % on the faults; median 85 % over all 64 non-core files (14.6 % selected) | built | use, with the corrections of C2, P-H-2 and P-H-9 |
| coverage map across processes (coverage.py + shim) | yes (97.9 % attributed) | 22 of 22 (recall 1.00) | median 60 % on the faults by suite; 62 % over all non-core files (38.1 % selected) | Apache-2.0, active | use as the nightly cross-check and widening, not alone |

## Part C. Gap analysis and design

### C1. Gap table

Each row: an industry practice (B1), what the Gov OS does today (A1 to A6), what is missing, what that costs today, and the proposed fix (glue a named tool or build) with the ticket that should carry it.

| # | Practice (B1) | Gov OS today | Missing | Cost today | Fix (glue / build) | Ticket |
|---|---|---|---|---|---|---|
| 1 | Affected-test selection at the merge gate (Google TAP presubmit, Pants/Nx affected, Microsoft TIA) | Every close runs everything: 14,770 cases, about 60 min of tests (W2-53) | Any selection; W2-66 will add a declared path-to-suite map | about 60 to 85 min per close × about 50 closes left in Wave 2 | **Build** the selection in `gov close` (W2-66, about 450 to 550 lines with the corrections of P-H-2 and P-H-9); **glue** coverage.py 7.16 per test across processes (my trial's shim) as the measured map in the nightly run | W2-66 (declared map); W2-66's `nightly.py` or a follow-up (measured map) |
| 2 | Fail safe for what the map cannot read: unknown file type → run everything (Microsoft TIA); "invalidate all" globs (pytest-impacted); a lockfile change marks all (Nx, Pants) | DEC-880's shared core, unplaced file and missing map all run everything (W2-66, decided) | Test helper modules shared across suites (W1-07's helper is imported by 14 suites); non-code repository files that tests read (the register, the orchestration record); the serial-only cases' scope | a W2-66 that follows only `allowed_paths` fails open on helper changes (finding 3) | **Build:** in the same selector, follow test-side imports (static import graph, standard library); `test_inputs` for non-code inputs; serial cases selected with their suites | W2-66 |
| 3 | Test the integrated result (merge queue, GitLab merge trains, Uber SubmitQueue; "not rocket science") | The close tests the merged commit (good), but only at close. Orchestrator commits between closes were tested by nobody, and the head went red (finding 1). DEC-883 (today) decides batched closes for W2-66, and the queue's gate (f) (today) runs four record-reading files before each close | A run of the record-reading tests after each batch of record commits, and on every head under DEC-883's reuse | 3 reds on `21302ae9` from record commits (01:08, 08:39). W2-02's close was refused at 15:36 for one of them | **Build** the nightly run (DEC-852 item 3, from W2-66); **glue** gate (f) as the after-commit run, widened (P-H-1); the record-reading set as a W2-66 KPI (P-H-9) | W2-66; orchestrator |
| 4 | Periodic full run as the backstop of selection (TIA: "recommended"; Develocity: remaining tests nightly) | Decided (DEC-852 item 3) from W2-66's merge; not running | The scheduler, the record, the comparison with scoped closes | Today nothing runs on the head between closes (finding 1) | **Build** `nightly.py` (in W2-66's paths) and a cron or orchestrator-queue trigger in a quiet window | W2-66; orchestrator |
| 5 | Test sizes with resource limits and default timeouts (Google small/medium/large; Bazel sizes and timeouts) | Kinds exist only implicitly: the serial-only list's four kinds, `local_only`, `needs`; no size, no per-test timeout | A declared kind per test (in-process / subprocess / repository-state / real model / live / latency), per-kind layer and timeout | The 241 `local_only` serial cases (live sessions, models, daemons) took about 1,175 of the 1,746 serial seconds in W2-53's close, and run in every close; timing cases failed under load 9 times; no per-test time limit (finding 16) | **Glue** pytest markers (`pytest.mark`) and pytest-timeout (MIT, 2.4.0; install by owner package) or the close's own per-run limit; **build** the kind-to-layer table in the path map | W2-66 (layer table for serial kinds); W2-57 (timing kinds); test-design skill |
| 6 | Hermetic tests (Google: "cut the runtime by a factor of 14") | 13 suites copy the whole working tree (66.5 MB, 10,058 files), some per test; tests read the live register and orchestration record | Tests that build only what they need; no reading of the live repository except declared repository-state tests | 48.4 % of case time; W1-27's red from a committed log (finding 1); W1-07's git-gc copy race (W2-48 residual) | **Build** (test refactor): a shared minimal-project fixture; keep the orchestration record out of test copies (copy `git ls-files` minus `orchestration-record` namespaces) | W2-67 (proposed, P-H-5); test-design skill |
| 7 | Result caching keyed on inputs (Bazel) | Per-test caching withdrawn (W2-48, DEC-880): per-test dependency tracking reused 11.5 %. Whole-run reuse for the same code decided (DEC-883 item 3) | Inputs declared for the whole-run reuse: its fingerprint leaves out the record paths that tests read (finding 18) | A reused run would hide a record-made red (two of today's three) | **Remove** the inert `test_inputs` key or give it to W2-66; **glue** nothing per test until tests are hermetic; **build** DEC-883's reuse with the record-reading set on every head (P-H-9) | W2-66 |
| 8 | Duration-aware parallelism and sharding (Develocity distribution, pytest-split, nextest partitions) | `-n auto` with xdist's default `load` scheduler; the slowest cases arrive late (part 1's last 2 % took about 13.5 of 38 min) | Longest-first ordering or `--dist worksteal` | about 5 to 10 min of tail per full run (measured: workers idle from 98 %) | **Glue:** xdist `--dist worksteal` (already installed, 3.2+), or order by recorded durations (pytest-split for CI shards) | W2-66 or W2-57 (the close's run) |
| 9 | Flaky quarantine with owner and deadline (Atlassian, GitLab: 3 days / 3 months; Google) | Owner-only `load_sensitive` list with `fixed_by` (good); four entries' fix is a Wave 3 row with no date; no history, no detection | Deadline per entry; per-test outcome history; automatic flaky-candidate report (never automatic quarantine, DEC-766) | Each new flaky case became an owner package after a refused close (P-W2-47, P-W2-55) | **Build** a results history (JSONL from the JUnit XML) in the nightly and close; a `deadline` field; the candidate report | W2-19 (ratchet core: fixed_by check, deadline); W2-66 (history); Wave 3 W2-M242 (automatic quarantine) |
| 10 | No retry to pass a gate (Google, Microsoft, Azure DevOps default) | DEC-780 item 3: no retry; only listed load-sensitive cases are re-run alone, reported by name | — | — | keep | — |
| 11 | Failure localisation: short traceback, reproduce command, automated bisect (git bisect run; Google's culprit finding) | `--tb=line`; a lead re-runs to see why; no bisect | Failure messages in the record; `git bisect run` over the failing ids for nightly failures | each refused-close cycle took 7 to 21 h (A4) | **Glue:** JUnit XML (pytest built in) for messages; `git bisect run` (git) with the selector inside | W2-66 (record); nightly (bisect) |
| 12 | Record what ran and what did not (Bazel BEP; Develocity "NOT SELECTED"; in-toto test-result) | Counts only; no scope; deselected and skipped tests unnamed; tested commit implied (A5) | A validation block: scope, commit and tree, selected and not-selected suites with reasons, per-test results file with hash | A scoped close could be read as full (W2-66 failure KPI) | **Build** the record fields in `gov close` (W2-66), **schema** in the close type (W2-02 / W2-64); **glue** JUnit XML as the per-test artifact; optional in-toto statement at releases | W2-66, W2-64, W2-16 (release attestation) |
| 13 | Mutation testing on the diff (Google: changed, covered, non-arid lines) | none | A diff-scoped mutation check on FULL tickets' core paths | Test strength was unmeasured. My sample (A6): about 9 in 10 mutants killed in `ratchet.py` and `claims.py`, plus one protective rule no test exercises (finding 19) | **Glue** cosmic-ray (MIT, works with subprocess tests because it edits files on disk) with `cr-filter-git`; mutmut 3 does not fit (its active mutant travels in an environment variable that scrubbed children drop) | Wave 3 (a FULL-profile probe aid) |
| 14 | Full suite on CI machines (Google, everyone) | GitHub workflow runs on push, its test step is red: pytest is not on the runner | Owner approval of runner tools (Q-8); a `not local_only` CI job | the only hosted signal is red by design | **Glue** GitHub Actions with pinned pytest/xdist (W2-43) running L4's non-local part | W2-43 |
| 15 | Language-agnostic runners with selection (cargo-nextest `rdeps()`, Vitest `--changed`, Jest `--findRelatedTests`, Nx/Turborepo affected) | pytest only | Declared test commands with their selectors and result readers | blocks UPIM and ASMO | **Glue** each ecosystem's selector behind W2-19's declared commands | W2-19 |

### C2. The target strategy for the Gov OS itself, layer by layer

The owner's layers, as they apply here.

| Layer | Trigger | What runs | How it is selected | Budget (target) |
|---|---|---|---|---|
| **L1** immediate | each save or commit by a worker; the pre-commit hook once W2-08 puts the hooks back | collection of the changed test files; the unit tests of the changed modules; the changed test files themselves | static import graph over `src/` and `tests/` (unit tests import code in-process, so this works for them) | under 60 s |
| **L2** affected components | a worker before it hands back; the lead inside its loop | the scoped selection, the same selector as the close, in parallel; the live and real-model kinds only if their area changed | the path-to-suite selection below (`gov tests select --base w2/integrate`) | 2 to 10 min |
| **L3** merge (the close) | `gov close`, on the merged commit | the pre-close gate (inside `gov close`, W2-07), then the scoped regression (W2-66); the shared core widens to the full run | the selection below, against the last full green commit | ≤ 15 min of test time for a non-core change (measured); a full close stays about 60 min until P-H-5 |
| **L4** nightly full | every night in a quiet window, on `w2/integrate`'s head (DEC-852 item 3) | everything, uncached, serial kinds and live sessions included; failures re-run alone; the selection audit; bisection of new reds; weekly, the measured map's refresh | none: the whole suite | 70 to 90 min a night |
| **L5** release qualification | W2-24, W2-46, a release cut (W2-16, W2-18) | the full uncached run, the dev-tier regression, live sessions, later the qualification tiers (G6, Wave 3); an evidence statement bound to the release commit | none | as long as it takes |

#### How tests are selected at L2 and L3

1. **The change set** is every file that differs between a base and the commit being closed, the orchestrator's own commits included.
   - The base should be **the last commit whose full run passed**: the nightly, or a `--full` close. This is Nx's advice ("set the base SHA to the latest successful commit on the main branch").
   - With the ticket's merge-base as base, the orchestrator's commits between closes are never in any scoped close. Those commits are what made the head red today (finding 1).
2. **The path-to-suite map.**
   - **Declared:** the tickets' `allowed_paths` (W2-66's rule, which places all 64 non-core source files in my map: `logs/allowed_map.json`), plus `test_inputs` for non-code files that suites read.
   - **Test-side imports:** a suite whose helper or conftest imports a changed test module is selected too. This needs a static import graph over `tests/` only, because test helpers are imported in-process. Without it, a change to `w1_07_support.py` selects 1 suite instead of 15 (finding 3).
   - **Measured, as a cross-check** (CAP-39.c's "dependency-aware" in its honest form here): the nightly's weekly coverage run, across processes, records which tests executed each source file. A suite the measured map adds is selected, and a disagreement is reported. B2 shows this works on this repository with the installed coverage 7.16.2 and an 83-line shim. testmon and import graphs cannot see the 89 % of acceptance cases that run `gov` in a child.
   - **Through the code graph** (DEC-859): once W2-37's `gov impact` answers "who calls X", the selector can ask it for callers of a changed function by its own traversal, never the whole graph. Its answers are static, so the measured map stays the check. This belongs to W2-38 in Wave 3.
3. **Risk rules that widen to the full suite.**
   - The shared core, named by path in one path-map list. DEC-880 names close, guard, check, records, "the retrieval core", the kernel hooks and the path map. "The retrieval core" must become paths: I propose `src/gov/retrieval/**` and `src/gov/retrieve/**`. That is 50 of 114 source files, 58 % of the source lines.
   - Also widen for: `tests/acceptance/conftest.py`, `pyproject.toml`, the serial-only list, a dependency change, any unplaced file, and a missing, unreadable or stale map (the measured map is stale when it is older than 7 days, for example).
4. **The serial kinds are selected with their suites,** and two kinds move out of the close by default:
   - live sessions: 50 cases, which spend the owner's usage and fail under load;
   - real models and daemons: 188 cases.
   Together with the other `local_only` serial cases they took about 1,175 of the 1,746 serial seconds in W2-53's close: the serial run's total, less the 571 s my part 2 measured for the 22 other cases. W1-05's switch-over case alone is 516 of those 571 s.
   They run at L4 and L5, and at L3 only when their own area changed: the launcher and sandbox for live sessions; retrieval, `codeintel` and secrets for models and daemons. This is an owner decision; today every close runs them.
5. **The run keeps the full run's form:** `pytest tests --ignore=<each unselected suite>`, never a list of suite folders. Given several folders, pytest loads all their conftests first, and W1-35's modules then import another suite's (finding 17).
6. **Parallelism.**
   - Keep xdist, but schedule the slowest first: `--dist worksteal` (installed since xdist 3.2) or an ordering by recorded duration.
   - In part 1 the last 2 % of the cases took about 13.5 of 38 minutes while most workers sat idle.
   - Sharding across machines comes with CI (W2-43): pytest-split, by recorded durations.

#### What W2-48's failure teaches about caching here

- **Per-test dependency tracking cannot work while tests read repository-wide state.**
  - W2-48's measured causes: 7,076 tests listed a folder of the project, 3,750 read a file outside the declared inputs, and the 263 serial cases always ran. Its subprocess children *were* measured after its round-2 widening.
  - The recorded one-line lesson, "testmon cannot see a repository whose tests run `gov` as a separate process", is true but is not the whole cause (finding 12).
  - My testmon trial shows the base fact: a fault in subprocess-only code, 0 of 80 tests selected.
- **The literature predicts the 3 %.** A file-level, Ekstazi-style selector for Python saved 3.10 % of time, because import-time code makes every test look dependent (NameRTS, ISSTA 2026, §4.2).
- **What would work.** Selection by suite (coarse but safe), checked by a measured map, and the nightly backstop. RTSLinux shows that tracking the whole process tree is what makes selection safe for tests that spawn processes (Celik et al., FSE 2017: in-process tracking saw 16.99 % of the dependencies).
- **Caching results** per test becomes possible only after the tests are hermetic (P-H-5). The one safe reuse now is a whole run for the same code, which DEC-883 item 3 decides. It is safe only if "the same code" covers what the tests read, or the tests that read the rest run every time (P-H-9).

#### Flaky tests: a quarantine with a deadline, never permanent

- **Keep:** the owner-only lists, the shrink rule, `fixed_by`, the re-run alone only for listed cases, and no retry of the close (DEC-757, DEC-762, DEC-766, DEC-780).
- **Add:**
  - (a) a `deadline` field on every entry: a named gate (for example "before W2-24") or a date, refused when passed (W2-19's check);
  - (b) a per-test outcome history (JSONL from each run's JUnit XML: nightly, closes, leads);
  - (c) a nightly "flaky candidate" report: each case that failed and then passed alone, with its history. It goes to the owner as a package and is never added automatically (DEC-766);
  - (d) quarantined tests keep running and are reported by name in every record.
- **Industry practice:** GitLab caps quarantine at 3 days (fast) and 3 months (long-term); Atlassian opens a ticket "with pre-decided due dates" (B1).

#### Failure localisation

1. Every failing test's message and short traceback go into the record from JUnit XML (pytest built in). Today the record keeps `--tb=line` and leads re-run to read why.
2. Each failure carries its one-line reproduce command (`PYTHONPATH=<root>/src python3 -m pytest '<node id>' -p no:cacheprovider`).
3. For a nightly red: `git bisect run` over the integration branch's first-parent commits between the last green nightly and the head, running only the failing node ids, so each step is seconds. Exit 125 skips a commit that cannot be tested. The culprit (a ticket's merge or an orchestrator commit) goes into the P1 package.
4. Flaky-aware: a red that does not reproduce alone at the head is reported as a flaky candidate, not bisected (Henderson et al., ICST 2023: about 40 % of Google's breakages had no culprit).

#### The integrated commit tested again after merges

- **Kept:** the close already tests the merged commit.
- **Added:**
  - (a) the scoped close's base is the last full green commit, so everything merged since is in its change set;
  - (b) a **repository-state run** after each batch of orchestrator commits: the tests that read the live repository (W1-06 approvals, W1-08 path map, W1-27 path compliance, W2-54 green-here, the check-declaration and drift cases), marked by kind (C4). This takes minutes, and would have caught the three reds of finding 1 within minutes of their commits (01:08 and 08:39). The queue's gate (f), added today, is its gate form: the same idea, run before each close;
  - (c) the nightly run.
- **A merge queue that tests batches** (GitHub merge queue, GitLab merge trains) is now decided for W2-66 (DEC-883, owner, today):
  - one rebuild, one check and one full regression per integrated head, then each ticket's own checks;
  - a red batch closes nothing and is attributed by bisect;
  - same code reuses the last passing run.
  W2-L207's Wave 3 row is overtaken in part, and its triage reason was already stale (finding 5). P-H-9 gives the four conditions this lens's evidence sets on DEC-883: the record-reading set on every head, the split index fingerprint, the serial-only kinds, and an alone-first check before a bisect.

#### Removing duplicated runs

1. The lead's verification in the close's form (P-H-4 (a)): the same scope in one parallel call, about 35 to 60 minutes instead of about 3.9 hours.
2. Reuse of the last passing run for the same code (DEC-883 item 3), with the tests that read the records run on every head (P-H-9).
3. The nested re-runs move to L4: W1-05's switch-over case (516 s), and W1-47's rerun of the guard's builder tests (41.5 s) (P-H-5).
4. With the pre-close gate inside `gov close` (W2-07), a refused close no longer costs a full run for faults found in minutes.
5. Research, audit and coordination tickets run no regression beyond their class (W2-07's "by ticket class").

### C3. Evidence: what every close record must state

**The rule.** Every close record states its validation scope, which tests ran, which did not run and why, and on which commit. No agent and no record claims full validation when only a selection ran. Industry precedents: Develocity labels unselected tests "NOT SELECTED"; Bazel's Build Event Protocol records each test's status, attempts and cache use; Google ties release-candidate results to the RC "for auditability" (B1).

**The fields: a `validation` block in the close record's frontmatter.**

```yaml
validation:
  scope: scoped            # scoped | full | integration (a nightly or gate run on the integration head)
  commit: <full sha of HEAD the tests ran on>
  tree: <git tree sha of HEAD>
  base: <full sha the change set was measured from, and why: "last full green: nightly 2026-10-22" or "ticket merge-base">
  change_set: [<paths>]    # or a count plus a hash when long
  selection:
    rule_version: <path map's hash or the selector's version>
    suites:                # every suite under tests/, each with its decision
      - {suite: tests/acceptance/W1-32, selected: true, reason: "allowed_paths of W1-32 match src/gov/status/command.py"}
      - {suite: tests/acceptance/W1-41, selected: false, reason: "not reached by the change set"}
    widened_to_full: null  # or the reason: "src/gov/guard/decide.py is shared core", "unplaced file docs/x", "map missing"
  counts: {collected: 14770, selected: 2476, not_selected: 12294, deselected: 2, passed: …, failed: …, skipped: …}
  deselected: [<node ids and the marker or conftest that deselected them>]
  skipped: [{test: <id>, reason: <pytest's reason>}]
  results_file: {path: docs/close/<ticket>/results-<ticket>.xml, sha256: …}   # JUnit XML, one line per test
  source: {run: batch | own | reused, fingerprint: <code fingerprint>, reused_from: <commit of the passing run> | null,
           record_reading_run: <this head's run of the record-reading set>}   # DEC-883 items 1 d and 3; P-H-9
  environment: {python: 3.12.3, pytest: 9.0.3, xdist: 3.8.0, workers: 20, load_at_start: 3.2}
```

The record keeps the counts and reasons. The full per-test list goes in a results file next to the record, with its hash in the record. W2-48 found that a full per-test list in frontmatter is 8.8 MB.

**What makes it trustworthy.**
1. `scope: full` only when `counts.not_selected == 0`, `deselected` is empty or each entry is a declared policy (for example `shared_gpu` run elsewhere), and the selected set equals the collected set. Otherwise the record says `scoped`.
2. The selection's reason for each suite comes from the selector, not from prose.
3. The results file is written by pytest itself (`--junitxml`), not parsed from the summary line. Today's count parser drops "deselected" (`command.py:936-941`).
4. Leads' and nightly runs write the same block (`scope: full` or `scoped`, `commit`, `results_file`), so that "the lead verified everything" is a record, not a sentence.
5. A batched or reused run (DEC-883) names its source: the batch's run or the reused run's commit and fingerprint. It also names this head's own run of the tests that read the records, which reuse never replaces (P-H-9).

**Where it lives.**
- **The close record type** (W2-02's `close.schema.json`): today it constrains only `task` and says "the close packet's other fields … are not constrained here". The `validation` block becomes required there: in W2-64 (W2-02's widening, already planned), or in W2-66 if its paths gain the schema file.
- **The writer** is `gov close` (`src/gov/close/command.py`, W2-66's "record's lines"), and later the extracted runner (C4).
- **The check:** `core-schema` refuses a close record without the block. A test in W2-66's acceptance suite refuses a record whose `scope` is `full` while `not_selected` is above 0 (W2-66's failure KPI: "a scoped record that says 'full'").
- **The nightly record** (W2-66's `nightly.py`) uses the same block with `scope: integration`, plus `selection_misses`: each test that fails at night and that a scoped close since the last nightly did not run.

### C4. As part of the Gov OS product: a "test orchestration and evidence" capability

Today the test machinery is spread out:
- inside `gov close` (`_run_tests`, two pytest plugins, the ratchet);
- in the orchestrator's scratch scripts (`close_queue.sh`, the gate);
- in prose rules in the lead brief (serial per-suite runs, re-running load-sensitive cases by hand).

An adopted repository gets only the part inside `gov close`, and only for pytest.

**The capability, in five parts.** The kernel ships one module (proposed: `src/gov/tests/`, with `gov tests` subcommands). `gov close`, the leads and the workers all call it, and every adopted repository receives it with the kernel.

| Part | What it does | Built on (glue first) | Used by |
|---|---|---|---|
| 1. Inventory | collects the tests (the project's declared command's collect step), their kind (in-process, subprocess, repository-state, real model, live, latency, race) from markers and the serial-only list, and their recorded durations | pytest `--collect-only`; pytest markers; W2-19's declared commands for other languages | everyone; the nightly run |
| 2. Change impact and selection | from a base and head: the change set; the selected suites with reasons; widening to the full run for shared core, unplaced files, missing or stale maps; the serial kinds with their suites | the path map's `test_suites` and `shared_core` keys; tickets' `allowed_paths`; a standard-library import graph over `tests/` (or grimp); the measured map from the nightly (coverage.py) | `gov close` (L3); leads and workers (L2, `gov tests select --base w2/integrate`) |
| 3. Execution | the parallel run (`-n auto`, worksteal, longest first), the serial kinds alone, per-run and per-kind time limits, the resource gate (W2-20), the ratchet (W2-53's core, reused) | pytest-xdist; pytest-timeout (owner package) or the run's own limit | close, nightly, leads, gates |
| 4. Failure diagnosis | each failure's message and traceback from JUnit XML; a re-run alone for load-sensitive kinds (DEC-757); a flaky-candidate report from history; for nightly reds, `git bisect run` over the failing ids between the last green and the head | JUnit XML; `git bisect run` | nightly; close refusals; leads |
| 5. Evidence | the `validation` block (C3) and the per-test results file; for a release, an in-toto test-result statement pointing at it; a results history (JSONL) per test | JUnit XML; in-toto attestation predicate (Apache-2.0) at release only | close records, nightly records, release records, `gov status` |

**Configuration an adopted repository receives with the kernel (path-map keys, schema-checked):**

```yaml
tests:
  commands:            # W2-19: one per runner
    - {name: product, run: "python -m pytest product/tests -q -p no:randomly", collect: "... --collect-only -q",
       parallel: "-n {workers}", reader: junit, kinds_from: markers}
  suites:              # path-to-suite map (declared); globs on both sides
    - {suite: "product/tests/test_auth*", covers: ["product/app/auth/**"]}
  shared_core: ["product/app/db/**", "product/app/config.py"]   # any change -> full
  inputs: ["product/tests/fixtures/**"]                           # non-code inputs -> the suites that read them
  layers:              # which kinds run where
    close:   {kinds: [unit, subprocess, repository-state], serial_kinds: [latency]}
    nightly: {kinds: all, except: [live]}
    release: {kinds: all}
  budgets: {close_minutes: 15, nightly_minutes: 120}
  never_in_gates: [live]   # e.g. EXAMIN's `live` marker spends money
```

**The kernel rules that come with it** (they extend the test-design skill and the brief templates; today's skill, `test-design` v1.0.0, says nothing about these):
- **Declare each test's kind with a marker.** A repository-state test (one that reads the live repository) is marked as such and runs in the gate and after record commits.
- **No whole-tree copies in fixtures.** Build the minimal project a test needs. A test that must copy the tree copies `git ls-files` minus the record namespaces (`orchestration-record`).
- **Every timing assertion is a `latency` kind** with a quiet-machine layer.
- **Live sessions are a `live` kind:** never in a close, always in the nightly or release.
- **Proportionality** (prompt §9) gains a cost line: a test design batch states its added suite time, and a case over 30 s needs a reason.

### C5. Adopted repositories, starting with EXAMIN

**What EXAMIN's tests are.** Read only, nothing run. Sources: W2-26's profile on its branch (`w2/W2-26:docs/research/EXP-003/examin/README.md`, a clone at `a7cf346`), and the owner's copy at "/home/usain/gov-os-workbench/examin/".
- **Product suite, `product/tests/`:** pytest.
  - Command: `.venv/Scripts/python.exe -m pytest product/tests -q -p no:randomly -m "not live"` (a Windows venv).
  - `product/pyproject.toml` sets `asyncio_mode = "auto"`, `testpaths = ["tests"]` and `addopts = "-m 'not live'"`.
  - Markers: `live` ("hits real external APIs"; the comment in the file explains that a bare `pytest` once attempted five real Anthropic calls) and `slow` ("boots a throwaway postgres (~20s)").
  - At the top level of `product/tests/`, 167 of 184 Python files import the app in-process and 28 use `subprocess`; 44 use pgserver/psycopg; 40 cases are marked `slow` and 6 `live`.
  - W2-26 could not run it: it needs ten packages (among them pgserver, psycopg, anthropic, fastembed) and a database.
- **Governance suite, `governance/scripts/tests/`:** 101 files, pytest-xdist `-n 8 --dist=loadgroup` through `run_gov_suite.py`; 31 files use `subprocess`. On Linux it ran in 1 min 13 s: 828 passed, 15 failed, 165 errors (W2-26).
- **No hosted CI:** the copy has no `.github/`.

**What follows for the Gov OS.**

1. **Learning the test commands (W2-19).**
   - The adoption run writes EXAMIN's two commands into the path map's `tests.commands` (C4) from the documented lines: the product suite with its `-m "not live"`, the governance suite with its xdist options.
   - It reads `pyproject.toml`'s `addopts` and markers and records them as kinds (`live`, `slow`).
   - An undeclared language or an unreadable command is a named refusal (W2-19's failure KPI).
   - The ratchet baseline of known reds (DEC-736) is built from the first full run of each command. W2-26's 180 governance failures show the baseline will not be empty.
2. **Layers and selection.**
   - EXAMIN's product tests import the app in their own process, so the in-process tools that failed here fit there. pytest-testmon's per-test coverage, or coverage contexts, can select well.
   - That is a trial for W2-27 on the clone, measured with planted changes as in B2, not an assumption.
   - Until it is measured, the declared map (`tests.suites`) and the shared core (the database layer, configuration) apply.
3. **Live and database tests.**
   - `live` never runs in any gate: it spends money, and only the owner opts in.
   - `slow` (a throwaway Postgres) runs at L3 when the database layer or its migrations change, and always at L4.
   - Each kind gets its own time limit (a Postgres boot is about 20 s).
4. **Nightly and CI.**
   - The nightly runs both suites in full, `live` excluded, on a clone under `~/gov-os-runs/` (DEC-723, DEC-728), in the quiet window.
   - A hosted CI job is a later owner decision; it needs the packages and a Postgres service.
5. **What `gov close` requires there.**
   - The pre-close gate: collection of both commands and `gov check`.
   - The scoped selection over both suites.
   - The ratchet over EXAMIN's baseline.
   - The `validation` block (C3) naming both commands, the markers excluded (`live`) and the database kind's decision.
6. **Time budget per close.**
   - The governance suite takes 73 s in full, so it can always run whole.
   - The product suite's time is unknown until W2-27 runs it on a clone with its packages. Set the budget after that measurement: a target such as "under 10 minutes" stated as measured, never assumed.

**What changes for Rust (UPIM) and TypeScript (ASMO).**

| Need | Rust | TypeScript |
|---|---|---|
| Runner with JUnit and partitions | cargo-nextest (Apache-2.0 OR MIT, 0.9.149 of 2026-10-20): `--partition`, retries that mark a test "flaky", JUnit with `flakyFailure` | Vitest 5.0.5 / Jest 30.5.2 (MIT): `--shard`, JUnit reporters |
| Affected selection | nextest filter `rdeps(crate)` ("all the crates that (possibly transitively) depend on"), fed with the changed crates from `git diff` (or the `determinator` library); cargo's crate graph is static and complete, so selection is reliable | `vitest related` / `--changed <ref>`, Jest `--findRelatedTests` / `--changedSince` (static imports only: "not the dynamic ones"); Nx `affected` / Turborepo `--affected` at package level |
| Coverage | cargo-llvm-cov (needs `LLVM_PROFILE_FILE` to reach child processes) | V8/Istanbul coverage built into Vitest/Jest |
| Mutation | cargo-mutants (MIT, 27.1.0): `--in-diff`, `--shard` | StrykerJS (Apache-2.0, 10.0.0), per-test coverage, `--incremental` |
| Same caution as here | state passed in environment variables is lost when a test scrubs the child's environment | the same: Stryker's active mutant and coverage travel in environment variables |

In both, the language's own graph is what makes selection safe, as long as tests import code instead of spawning a CLI. The kernel's "declare the kind" rule (C4) tells them apart.

### C6. Mapping to the plan and the Contract

| Item of this design | Ticket | Contract | State today |
|---|---|---|---|
| Scoped selection at close: declared map + test-side imports + `test_inputs` + serial kinds scoped + fail-safe widening; `--full`; the `validation` record lines | **W2-66** (`DAEO-c1uz`) | CAP-39.c ("dependency-aware impacted-test selection", Wave 3) in a lite form, pulled forward by DEC-880; DEC-880 names CAP-53.b ("Profile computed from impact"), which W2-66 does not compute | open; its test designer waits for this report (DEC-881), then W2-66 takes the first slot (DEC-884) |
| Batched closes, same-code reuse with the record-reading set on every head, the index by two fingerprints, alone-first before a bisect (DEC-883 as P-H-9 refines it) | **W2-66** (first slot, DEC-884); W2-57 for the serial-only kinds (DEC-883 item 5) | CAP-39.c (lite), CAP-39.a (G2/G3) | decided today; W2-66 open |
| The nightly full run, its record, the selection audit, the flaky-candidate report, the bisect of nightly reds | **W2-66** (`nightly.py`) for the run and record; the trigger is an orchestrator act (cron or the queue) | CAP-39.a (G5 "full suite"), CAP-39 (scheduler, Wave 3) | decided (DEC-852 item 3), not running |
| The measured who-tests-what map (coverage across processes) refreshed weekly by the nightly | B2 found no miss of the declared map on the 22 faults that ran, so the map is the nightly's cross-check (W2-66's `nightly.py`), not a selector. It becomes a widening in W2-38 (Wave 3), or earlier if the nightly reports a miss | CAP-39.c | trialled in this report; the widest modules unmeasured |
| The pre-close gate inside `gov close` (collection, `gov check`, fresh checkpoint, clean tree, trailers); close by ticket class (research and audit tickets run no regression beyond their class) | **W2-07** | CAP-39.a (G2 task close) | gate exists as a script; not in `gov close` |
| Declared test commands for any language; result readers; the ratchet core reused; `fixed_by` and the shrink check, with an acceptance case for an entry with a missing or blank field (finding 19); skips counted against a threshold (W2-M162); tests in a clean checkout (W2-M253) | **W2-19** | CAP-39.a; DEC-736 | open |
| `gov impact` (code graph traversal) as a later input to selection and to the profile | **W2-37** (in progress) → **W2-38** (Wave 3) | CAP-33.b, CAP-53.b | W2-37 in progress |
| Profile from impact; impact-selected tests at close (the full W2-38) | **W2-38**, Wave 3 (DEC-841) | CAP-53.b, CAP-39.c | Wave 3; its KPI line still builds "on top of W2-48's cache" (stale, finding 5) |
| CI on the hosted runner: pinned pytest/xdist, the `not local_only` regression as an L4 complement, a green job | **W2-43** | CAP-39.a (CI) | open, needs Q-8 (owner approval of runner tools) |
| `gov check` semantics: an unmeasured or absent-tool check is not green; time limits stated | **W2-45** | CAP-38.b, CAP-39.d | open |
| Load out of the close: timing kinds as an isolated suite or the close's own resource gate; W1-46's live cases robust | **W2-57** (card only, no ticket file) | CAP-39.a | not created |
| The close record type with a required `validation` block | **W2-64** (W2-02's widening) or W2-02's resume | CAP-38.d (suite currency), CAP-22-type records | W2-02 merged; its close was refused on 2026-10-21 at 15:36 for two reds outside the ticket; W2-64 planned |
| Hooks back on: pre-commit G1/G2 + staged secrets; add collection of changed tests (L1) | **W2-08** | CAP-39.a (G0/G1) | open |
| Full uncached runs at gates | **W2-24**, **W2-46** (`gov close --full` or `gov tests run --full`) | CAP-39.a (G4/G5) | not reached |
| Test hygiene: no whole-tree copies, the orchestration record out of test copies, repository-state tests marked; W1-05's and W1-47's nested reruns moved to L4 | a new ticket (proposed W2-67, Track A) or folded into W2-57 | CAP-38.d (suite currency) | not planned |
| Test-design skill and brief templates: kinds, cost line, no live-state assertions unmarked | **W2-11** (kernel rules) / a skill revision under CIT-P | CAP-24, CAP-38.c | not planned |
| Flaky quarantine with deadline, automatic detection, `gov status` listing | W2-19 (deadline field, the check); **W2-M242** (Wave 3) for automatic quarantine | CAP-39 | partly decided |

**Contract notes.**
- CAP-39.c is the Contract item for dependency-aware selection and is Wave 3. W2-66 pulls a lite part of it into Wave 2, so the re-baseline in DEC-880 should name CAP-39.c (partial, W2-66), next to CAP-53.b.
- CAP-39.a lists tiers G0 to G5 (guard, mutation, task close, checkpoint/handoff, milestone, full suite). The owner's layers L1 to L5 map onto them: L1 = G0/G1; L2 = G2 (pre-close, scoped); L3 = G2/G3 at close; L4 = G5 nightly; L5 = G4 milestones plus G6 qualification (CAP-39.b, Wave 3).
- W1-40 built G0 to G5 as `gov ci` commands, but none runs today: the hooks are off and CI cannot run the tests.

## Findings

Each finding carries the two lines of the judgement rules (JUDGEMENT.md, DEC-808). Only a "yes" with "fails open" or "loses work" fails the audit's item and justifies a round. A feature-gated risk is an entry criterion of the ticket that switches the feature on (DEC-803).

### Finding 1. The integrated head went red through the orchestrator's record commits, and one of the reds refused W2-02's close

- **Evidence.** Part 1 on `21302ae9`, the clone's own code, then the cases alone (`3 failed in 7.48s`). One cause each, all three from orchestrator commits on 2026-10-21:
  - **W1-06:** `test_every_approving_decision_is_accepted_by_the_owner` fails: "entries of governance/project/tool-registry.yaml whose approving decision is not ACCEPTED (owner): ['pytest-testmon: DEC-843 has status 'SUPERSEDED by DEC-880 …', 'coverage: …']". DEC-843 was marked superseded in `6cce71bb` (08:39); the registry's `approved_by: "DEC-843"` (line 211) was not changed.
  - **W1-08:** `test_every_tracked_path_matches_exactly_one_namespace` fails: "2 of 10058 tracked paths are in no namespace …: `governance/project/orchestration/main/orchestrator/packages-pending/P-W2-48-8.md`, `…/P-W2-58-4.md`". Both were added by the working-memory sync `21302ae9` (08:39).
  - **W1-27:** `test_old_path_inside_its_new_path_is_not_stale` fails because the committed log `governance/project/orchestration/worktrees/W2-48/lead/log/verify2/W1-27.txt` (`90ef0af6`, 01:08) contains the fixture's file name. With the file moved aside the case passes (`1 passed in 6.12s`).
- **Aggravating.** The pre-close gate relies on `gov check`, but the hard-block core-pathmap check reads `namespaces` as a list while this path map holds a mapping, so it reports no finding at all (`python3 -m gov.check.pathmap` exits 0 on this tree). This is known row W2-M214, triaged to W2-23 and open. The gate therefore passes, and only the full regression, about an hour later, meets the red.
- **What happened next (read only, during my session).**
  - W2-58's lead, verifying in full before its return, reported the W1-06 and W1-27 reds and a third: W2-54's two cases on `context-reproducibility` (W2-48's ticket file cites DEC-843). My clone, which has no record store, could not show that third red.
  - The orchestrator repaired these at 14:00 by DEC-882 (delegated, `9d8c1887`): DEC-843's install approval stands, the two logs were removed, and `sync_context.py` stops copying suite logs.
  - **W1-08's red was not reported and was not repaired.** At `2b254458` (14:06) the two `packages-pending/` files were still tracked and the path map unchanged. The pre-close gate passed, `gov check` included (14:20:41).
  - **W2-02's close then ran 75.6 minutes and was refused** (15:36:17, `CHECK_FAILED`, exit 3). It had two findings: W1-08's case, as predicted here, and W1-07's `test_every_command_returns_the_envelope[doctor]`. The record names the W1-07 case with no reason; alone, at the same commit, in my private copy, it passed in 9.5 s (A4). The queue stopped, and the five closes behind W2-02 waited.
  - **The repair, 15:49-15:50** (DEC-885, delegated, `f3a1079a`, `3cb740dd`): the two copies were removed, and `sync_context.py` now copies nothing into a path no namespace holds. W1-07's case became row W2-L409. The queue restarted at 15:50 with the same six tickets, and W2-02's second close started at 16:11:55 after the new gate (f) passed (80 passed in 108 s).
- **What this shows.** Before a close, the only thing that caught the head's reds in Wave 2 was a lead's full verification on another ticket. It missed W1-08's, which the close then met. That duplicate is useful today, and it disappears if leads verify by selection.
- **Ordinary work: yes,** because these are the orchestrator's routine decision-record and working-memory commits.
- **Consequence: other** (fails closed): a refused close of about an hour, and a counted iteration against a ticket that did nothing wrong. Both happened to W2-02 at 15:36.
- **Severity:** high. The three causes are repaired, and gate (f) now checks four record-reading files before each close. The standing rule's other half, a run after record commits, is open (P-H-1).

### Finding 2. The committed orchestration record now decides test outcomes and cost

- **Evidence.**
  - 13 acceptance suites copy the whole working tree in a fixture: W1-05, W1-07, W1-18, W1-25, W1-26, W1-27, W1-28, W1-30, W1-39, W1-46, W1-47, W1-49, W1-50. W1-07 and W1-27 copy it per test (`conftest.py:56-61`).
  - The tree went from 1,784 tracked files (14.9 MB) at `7d60dec6` to 10,058 (66.5 MB) at `21302ae9`. Of those, 8,046 files (48.7 MB) are the orchestration record added under DEC-819.
  - These suites take 48.4 % of all measured test time (part 1).
  - W1-27's red (finding 1) comes from a log inside that record.
  - W1-07's per-test copy became 4.6 times slower (0.18 s → 0.88 s) and its session copy about 4 times slower (0.6 s → 2.5 s), measured at load 0.95 (A1).
  - The copy races git's background gc: my part 3 hit `shutil.Error … .git/objects/03 … No such file` in W1-07's setup, the race W2-48's lead recorded. W1-25's per-test copy does the same: `test_a_checkpoint_is_a_file_git_can_track` errored at setup in two of my three runs of it at `2b254458` (load about 7). These are flaky cases on no list.
- **Ordinary work: yes,** because every checkpoint syncs more of the record into the tree (prompt §15).
- **Consequence: other:** refused closes and a slower regression that grows every day.
- **Severity:** high.

### Finding 3. W2-66 as specified does not follow test helpers shared across suites

- **Evidence.**
  - `w1_07_support` is imported by 14 other suites: W1-13, W1-15, W1-25, W1-26, W1-27, W1-28, W1-30, W1-31, W1-35, W1-38, W1-39, W1-41, W1-46, W1-50.
  - `w1_46_support` is imported by W1-28, W1-33, W1-38, W1-50 and W2-54; `w1_02_support` by W1-28, W1-45 and W1-50; `w1_30_support` by W2-01 (`grep` of the imports).
  - W2-66's rule selects "the ticket's own suite … and the suites of every ticket whose allowed_paths overlap a file the ticket changed" (`.tickets/DAEO-c1uz.md`). Test helpers are in no ticket's `allowed_paths`, so a change to `w1_07_support.py` selects only W1-07.
  - W2-57 will rewrite W1-46's fixtures. Test designers revise earlier tickets' tests by rule (A1 brief).
- **Ordinary work: yes,** because test designers edit shared helpers in ordinary rounds.
- **Consequence: fails open:** a scoped close passes while the suites that import the broken helper are not run. Only a nightly that does not exist yet would catch it.
- **Severity:** high for W2-66. It is feature-gated, so it is **an entry criterion of W2-66** (DEC-803), not a round elsewhere.

### Finding 4. The 15-minute target cannot be met by selection alone as the close stands

- **Evidence.**
  - Before every close in the queue: the rebuild takes about 6 minutes (`14:27:53 → 14:34:04`) and `gov check` about 7 minutes (`14:34:04 → 14:40:54`) (`close-queue-20261020-1422/queue.txt`).
  - The serial-only block took 1,746 s in W2-53's close and runs whole whatever the change. It holds 50 live sessions and 188 model or daemon cases.
  - W2-66's card mentions neither, and the target's scope ("a typical close") is not defined.
  - My scoped estimates: the parallel part of a non-core selection takes a median 14.6 % of the full run's test time and at most 41.1 %, before the serial block and the gate.
- **Ordinary work: yes. Consequence: other** (a target missed, or a round spent).
- **Severity:** medium.

### Finding 5. Superseded-decision text survives in four places (DEC-866)

- **Evidence.**
  - W2-19's ticket KPI requires "the input globs W2-48's cache keys on" (`.tickets/DAEO-jzvg.md:29, :83`).
  - W2-38's KPI: "on top of W2-48's cache" (`DAEO-g23i.md:30, :57`).
  - W2-07's paths: "except `src/gov/close/cache*`, W2-48's" (`DAEO-r9ss.md:86`).
  - W2-L207's triage reason: "the close bottleneck is met in Wave 2 by W2-38" (W2-38 is Wave 3, DEC-841).
  - The registry approval of finding 1 is the fifth, and the only one that breaks something.
- **Ordinary work: yes,** because a test designer reads its KPI literally. **Consequence: other.**
- **Severity:** low.

### Finding 6. The close record cannot say what was not validated

- **Evidence.**
  - W2-53's record holds counts per run and no scope.
  - The tested commit is implied: `check_commit` appears only when governance files changed (`command.py:1049`).
  - The 2 `shared_gpu` cases are deselected in every run, and the count parser drops "deselected" (`command.py:936-941`).
  - 31 skips are unnamed.
  - W2-02's `close.schema.json` constrains only `task`.
- **Ordinary work: yes. Consequence: other today.** Once scoped closes exist, a record that does not state its scope can be read as full validation.
- **Severity:** medium. It is an entry criterion of W2-66 (DEC-803) and of W2-64's schema.

### Finding 7. No signal between closes: nightly not running, CI tests red by design, hooks off

- **Evidence.**
  - DEC-852 item 3 waits for W2-66's merge; there is no crontab and no script.
  - `.github/workflows/ci.yml`'s test step prints "unmeasured: pytest is not on the runner" and fails (W2-43 needs Q-8).
  - `.git/hooks` holds only samples.
  - Since 15:50 today the queue's gate (f) runs four record-reading test files before each close. Between closes, still nothing runs.
- **Ordinary work: yes. Consequence: other** (late detection: finding 1 went unseen).
- **Severity:** medium-high.

### Finding 8. The same tests run two to four times per ticket

- **Evidence.**
  - Lead verification: 13,857 s serial per verification (W2-48 run 2).
  - The close: about 60 min.
  - W2-53's refused attempts: about 297 minutes.
  - W2-24 and W2-46 will repeat everything.
- **Ordinary work: yes. Consequence: other** (machine time, close-queue throughput).
- **Severity:** medium.

### Finding 9. Load decides most test refusals, and the quarantine has fixes without dates

- **Evidence.**
  - 9 of the test-related refusal causes were load (A4).
  - 22 serial-only entries are not on `load_sensitive`, so they refuse a close under outside load.
  - 4 `load_sensitive` entries name only Wave 3 rows (W2-M332 ×3, W2-L352).
  - W2-57, the fix of 26 entries, has no ticket file.
  - On a quiet machine all 22 latency and race cases passed (part 2).
- **Ordinary work: yes. Consequence: other.**
- **Severity:** medium.

### Finding 10. Test-design guidance says nothing about kind, cost, copies or live-state assertions

- **Evidence.**
  - `template/governance/kernel/skills/test-design/SKILL.md` (v1.0.0, 40 lines) and the brief template cover KPI traceability, red first, the README and proportion. They say nothing of test kinds, run-time cost, whole-tree copies, timing assertions or tests that read the live repository.
  - The estate shows the result: 62 % of the cases come from parametrisation, 13 whole-tree-copy suites, repository-state tests (W2-54's "green here") that turn red on unrelated record states, and nested reruns (W1-05: 516 s; W1-47: 41.5 s).
- **Ordinary work: yes. Consequence: other.**
- **Severity:** medium.

### Finding 11. The SubagentStop hook hides its reason, so helpers loop and their results are lost

- **Evidence.**
  - `template/governance/kernel/hooks/subagentstop.py:51-56` writes `{"hookSpecificOutput": {"blockReason": …}}` to standard output and exits 2.
  - The documented contract: "The message that comes with the block is your hook's stderr. If your hook also printed JSON that makes a blocking decision, Claude Code uses that decision's reason instead". For SubagentStop that is `decision: "block"` with `reason` (https://code.claude.com/docs/en/hooks, read 2026-10-21).
  - My three read-only research helpers were blocked repeatedly ("blocks every stop without giving a reason"; one 13 times). Their digests reached me only after I resumed each with the field list.
- **Ordinary work: yes,** because any in-session helper whose brief omits the twelve fields meets it.
- **Consequence: loses work** (the helper's result is not delivered unless someone resumes it).
- **Severity:** medium. Outside this lens's core; it rides along with the next hooks ticket (DEC-802).

### Finding 12. W2-48's recorded lesson is narrower than its measured causes

- **Evidence.**
  - W2-48's research record §6: 11,786 tests (79.9 %) always ran. First causes: a listing of a project folder 7,076; a read outside the declared inputs 3,750; dot-files 125; unfollowable processes about 500; 259 of the 263 serial cases.
  - Its §3: children with their own environment were measured after round 2.
  - DEC-880 and W2-66's card record the lesson as "testmon cannot see a repository whose tests run gov as a separate process".
  - Lens G (F6) had recommended testmon from its documentation, without a run.
- **Ordinary work: yes,** because designers act on the recorded lesson. **Consequence: other.**
- **Severity:** low-medium.

### Finding 13. The parallel run's tail wastes workers

- **Evidence.** Part 1 reached 98 % of its cases about 24 minutes after it started (11:54:29 → about 12:18:30) and ended 13.5 minutes later (12:32:10), most workers idle: xdist's default `load` scheduler sends the slowest cases late. `--dist worksteal` (installed, xdist 3.2+) or longest-first ordering addresses it.
- **Ordinary work: yes. Consequence: other.**
- **Severity:** low-medium.

### Finding 14. Test runs leave state in a fixed folder shared with the real index daemon

- **Evidence.**
  - `/tmp/gov-cbm-1000` held 8,510 daemon folders in the morning and 8,704 at 15:38, after W2-02's close (`DAEMON_BASE = Path(f"/tmp/gov-cbm-{os.getuid()}")`, `src/gov/codeintel/__init__.py:35`). The orchestrator's real index daemon uses the same folder.
  - 44 `/tmp/gov-testcache-*` leftovers (the orchestrator's checkpoint) and several `/tmp/gov-check-*` folders.
- **Ordinary work: yes. Consequence: other.**
- **Severity:** low.

### Finding 15. The re-baseline names the wrong Contract item

- **Evidence.** DEC-880: "this pulls back the lite form of W2-38 (CAP-53.b's impact-selected tests)". CAP-53.b is "Profile computed from impact". The impacted-test selection is CAP-39.c ("dependency-aware impacted-test selection", Wave 3) (`contract.yaml:3049`, `:2338`).
- **Ordinary work: yes. Consequence: other** (traceability).
- **Severity:** low.

### Finding 16. No per-test time limit: one hang stalls a whole run for up to two hours

- **Evidence.**
  - No test in the estate has a time limit of its own. pytest-timeout is not installed, and the close sets only a per-run limit (`close_timeout: 7200`, `command.py:930-933`).
  - My planted fault at `src/gov/tasks/claims.py:37` (the wait loop's condition negated, an ordinary slip) made `holder()` spin forever. 77 of the 78 tests that run that line hung.
  - My runner's first attempt waited about 12 minutes before I stopped it. With my own 20-line SIGALRM limit (`scripts/plugins/govh_timeout.py`, 65 s for that item) the hangs became failures in 604 s.
  - In a close, the same slip would hold the parallel run until its 7,200-second limit cut it, and then refuse.
- **Ordinary work: yes,** because an off-by-one in a wait loop is a plain mistake.
- **Consequence: other** (fails closed: up to two hours of a quiet window lost).
- **Severity:** medium. Glue: pytest-timeout (MIT) by an owner install package, or the close's own per-test limit through its results plugin.

### Finding 17. A selection that names several suites on one command line breaks W1-35's collection

- **Evidence.**
  - Two W1-35 modules import their constants from a bare `conftest` (`tests/acceptance/W1-35/test_w1_35.py:19`, `test_w1_35_orchestration.py:27`). That name resolves to the conftest pytest loaded last.
  - In the full run (`pytest tests`) pytest loads each folder's conftest as it reaches the folder, so W1-35 gets its own.
  - Given several suite folders as arguments, pytest loads every one of their conftests first, in argument order. Collection only, at `2b254458`, in my clean worktree (`scripts/collect_order.sh`):
    - `pytest tests/acceptance/W1-35 tests/acceptance/W1-38 --collect-only`: `ImportError: cannot import name 'CHECKS_DIR' from 'conftest' (…/W1-38/conftest.py)`, and the same for `CITATION_PATTERN`. With W1-15 in place of W1-38, the same, from W1-15's conftest.
    - The same two folders in the other order: 367 tests collected.
    - `pytest tests --ignore=<every other suite>`, the form today's close uses, collects 367 too.
  - My trial met it first: one planted fault was "caught" only by this collection error, so I set that result aside and list W1-35 last in later runs (B2).
  - 55 of the acceptance folders have a conftest. `tests/unit` has none, so W1-35 with `tests/unit` alone is safe.
- **Why it matters for W2-66.** A scoped close that passes its selected suites as folders, in sorted order, refuses every close whose selection holds W1-35 and any later suite, for a reason the full run does not have. No other conftest defines W1-35's names, so today the failure is loud, not silent.
- **Ordinary work: yes,** once W2-66 lands: any change whose selection includes W1-35 and another suite.
- **Consequence: other** (fails closed: a refused close).
- **Severity:** medium. It is feature-gated, so it is **an entry criterion of W2-66** (DEC-803). There are two fixes, either sufficient:
  - the selector keeps the full run's form, `pytest tests --ignore=<unselected suites>`;
  - W1-35's two modules import from a support module of their own (two lines, under its test designer's rules).

### Finding 18. DEC-883's same-code reuse leaves out the record paths, but tests read them: two of today's three reds came from record-only commits

- **The decision.** DEC-883 item 3 (owner, 2026-10-21, for W2-66): "A close whose code is byte-identical to the last fully passing run reuses that run as its evidence". The tree fingerprint "leaves out record-only paths such as `docs/checkpoints/` and `governance/project/orchestration/`". Item 1 b runs each ticket's own checks, among them "the tests that read records", but names no such set.
- **Evidence.**
  - W1-27's red (finding 1) was caused by `90ef0af6` (01:08). That commit touched 167 files, all under `governance/project/orchestration/`. With the one log moved aside, the case passes.
  - W1-08's red was caused by `21302ae9` (08:39), which touched 18 files, all under `governance/project/orchestration/`. It refused W2-02's close at 15:36 (DEC-885).
  - Under item 3, both commits keep the code fingerprint. A close after either would have reused the last passing run and closed while those cases were red at its head, unless item 1 b's set held W1-08 and W1-27.
  - What reads the record today:
    - the 13 suites that copy the whole working tree, 48.4 % of the test time (finding 2);
    - W1-08's namespace check over every tracked path;
    - W1-06's approvals check (register and tool registry);
    - W2-54's "green here" cases (register state; A4, 10-20 08:38);
    - W1-49's window and W1-33's definitions (A1, ever-failed).
- **Ordinary work: yes,** because the orchestrator commits records between every two closes (checkpoints, working memory, decision records).
- **Consequence: fails open.** A close cites a passing run for a head on which tests fail, and nothing runs them until the nightly, which is not running yet (finding 7).
- **Severity:** high. It is feature-gated (W2-66 builds item 3), so it is **an entry criterion of W2-66** (DEC-803), and a DEC-105 choice for the owner (P-H-9).

### Finding 19. The rule that every ratchet entry names its fix has no test

- **Evidence.**
  - `_refused_because` refuses an `accepted_reds` entry that does not give each of `test`, `decision`, `reason` and `fixed_by`, and a `load_sensitive` entry without its first three (`src/gov/close/ratchet.py:24, 93-95`). That is the rule of DEC-760 and DEC-762: every entry names its fix.
  - In my mutation sample (A6), the refusal line 95 is executed by no test in the who-tests-what map.
  - The mutant that lets a blank field count (line 93, `and` to `or`) survived all 30 tests that run that line.
  - Every ratchet test builds its entries through `w2_53_support.red_entry(…, fixed_by="W2-13", reason=…)`, with every field filled.
- **Ordinary work: yes,** because W2-19's card changes this check ("`fixed_by` and the shrink check"), and W2-66 and W2-07 edit the close around it.
- **Consequence: fails open, latent.** The check works today. A regression in it would let an entry that names no fix count, and every test would still pass.
- **Severity:** medium. The fix rides along (DEC-802) with the next ticket that touches `ratchet.py`, W2-19 or W2-66's test designer: for each list, one acceptance case where an entry with a missing or blank field does not count and the close names it.

## Owner packages

Each package is in the six parts of DEC-818. Together they say what to glue, what to build and what to remove, in which ticket, in what order, with estimates; the last table orders them. None of them blocks my audit: every item of the lens was measured or stated as a limit. P-H-2 and P-H-9 block W2-66's test designer (DEC-881), and W2-66 has the first slot (DEC-884). P-H-1's three repairs were done during my session.

### P-H-1 (P2 now; P1 until 15:50). The integrated head went red through record commits: repaired, a standing rule still missing

**Update during my session:**
- The orchestrator repaired two of the three reds at 14:00 by DEC-882, after W2-58's lead reported them (finding 1).
- W1-08's red (two unplaced `packages-pending/` files) remained at `2b254458`.
- The queue's first close, W2-02, ran from 14:20:41 to 15:36:17 and was refused (exit 3). Its findings were W1-08's case and W1-07's `doctor` envelope case, which passed alone in my copy (A4). The queue stopped there.
- DEC-885 (delegated, 15:49) then removed the two files and made the sync keep to the path map's namespaces, and the queue restarted at 15:50.
- The restarted queue has a new **gate (f)**. Before each close it runs the four record-reading test files and stops the queue, uncounted, if any is red: W1-06's approvals, W1-08's path map, W1-27's path compliance and W1-07's envelope (`close_queue.sh:41-48`). At 16:04 it reported "80 passed in 108.43s". That is this package's standing rule in gate form.
- What remains is the reach of that rule: it runs only before a close, and its set is narrower than what reads the record. P-H-9 shows why that matters more under DEC-883's reuse.

1. **Context** (as of `21302ae9`, this morning).
   - No `gov close` had run since W2-53's close (2026-10-20 15:53).
   - Six closes were queued behind W2-58's merge: W2-02, W2-54, W2-62, W2-63, W2-50 and W2-58.
   - Between closes nothing runs the tests on `w2/integrate`: the nightly run is decided but not running, CI cannot run tests, and the hooks are off.
2. **What happened.** My part-1 run on `21302ae9`, the clone's own code, found three acceptance tests red. No ticket caused them; each fails alone too (`3 failed in 7.48s`):
   - **W1-06** `test_every_approving_decision_is_accepted_by_the_owner`: the tool registry still gives `approved_by: "DEC-843"` for pytest-testmon and coverage (`governance/project/tool-registry.yaml:211` and the coverage entry). Commit `6cce71bb` (2026-10-21 08:39) marked DEC-843 SUPERSEDED by DEC-880.
   - **W1-08** `test_every_tracked_path_matches_exactly_one_namespace`: two files of the working-memory sync (`21302ae9`, 08:39), `governance/project/orchestration/main/orchestrator/packages-pending/P-W2-48-8.md` and `…/P-W2-58-4.md`, fall in no namespace of the path map.
   - **W1-27** `test_old_path_inside_its_new_path_is_not_stale`: a W2-48 lead's test log, `governance/project/orchestration/worktrees/W2-48/lead/log/verify2/W1-27.txt`, was committed in `90ef0af6` (01:08). It holds the fixture's file name. The case copies the whole working tree and asserts that `gov doctor` does not name it. With that one file moved aside in my clone the case passes (`1 passed in 6.12s`).
3. **Why it matters.**
   - The first queued close, W2-02, touches the shared core, so it runs the full regression even after W2-66.
   - As of `21302ae9`, it would take about 60 to 80 minutes and be refused for these reds, counting an iteration against a ticket that did nothing wrong. That happened: 75.6 minutes, refused for W1-08.
   - The pre-close gate runs collection and `gov check`. It catches W1-08 only if core-pathmap reports the two files, which it did not, and it does not run W1-06 or W1-27.
4. **Options.**
   - **(a) Repair the three now, then run them with `gov check` before the queue restarts.**
     - Registry: the two entries' approval becomes DEC-880, which keeps the installs "installed and unused until the owner removes them". Alternatively the owner removes the installs and their entries.
     - Path map: add `governance/project/orchestration/main/orchestrator/packages-pending/**` to the `orchestration-record` namespace.
     - Orchestration record: stop committing test-run outputs (`*/lead/log/verify*/`, `*/lead/log/timed*/`) through `sync_context.py`, and remove this log from the record.
     - Cost: about an hour of orchestrator work and 10 minutes of runs. Risk: low.
   - **(b) Let the queue run and repair after the refusals.** Cost: at least one refused close (one hour or more) and a counted iteration per cause.
   - **(c) Put W1-06 and W1-27 on `accepted_reds`.** Wrong: they are defects of the record, not known product gaps (DEC-766's spirit).
5. **Recommendation: (a)**, confidence high.
   - Its three repairs are done: two by DEC-882 at 14:00 (the registry, where DEC-843's item 3 stands; the logs and the sync) and the third by DEC-885 at 15:49 (the two files removed; the sync keeps to the namespaces).
   - The standing rule is half built: gate (f) runs four record-reading files before each close, 80 tests in under 2 minutes.
   - Two steps remain. Run the same set after each batch of record commits, not only before a close, so a red is found within minutes of the commit. And widen it to W2-54's green-here cases, W1-33's definitions and W1-49's window (P-H-9's set).
   - Classification of the findings: three findings, each "Ordinary work: yes; Consequence: other (fails closed)"; no ticket round.
   - The structural cause, tests that copy the whole tree including the record, is P-H-5.
6. **What it blocks:** nothing now that the three are repaired. Without the standing rule, the next record-made red costs another refused close of an hour or more.

### P-H-2 (P1 for W2-66's start). What W2-66's card and tests must take in before its test designer starts

1. **Context.**
   - W2-66 (`DAEO-c1uz`) brings path-scoped regression into the close: the ticket's own suite, `tests/unit`, and the suites of tickets whose `allowed_paths` overlap the change.
   - The shared core, an unplaced file or a missing map run everything.
   - It also carries `--full`, the nightly run and a 15-minute target.
   - DEC-881 item 4 holds its test designer until this report, and DEC-884 gives W2-66 the first slot after it.
2. **What happened** (A1, B2, C2):
   - (a) **Shared test helpers are not followed.** `w1_07_support` is imported by 14 suites, `w1_46_support` by 6 (W2-54 among them), `w1_02_support` by 4 and `w1_30_support` by W2-01. A changed helper selects only its own suite.
   - (b) **The serial-only block is not mentioned.** It holds 263 cases and took 29 minutes in W2-53's close. Run whole, it alone exceeds the target. Its 50 live sessions and 188 model or daemon cases need a layer rule.
   - (c) **"The change" has no base.** If the base is the ticket's merge-base, the orchestrator's own commits between closes (which made the head red today, P-H-1) are never in any scoped close.
   - (d) **"The retrieval core" names no path.**
   - (e) **The target's scope is not stated.** A rebuild (about 6 minutes) and `gov check` (about 7 minutes) come before every close in the queue (queue logs 2026-10-20).
   - (f) **The record does not say what was left out.** It "names each suite and why". It also needs the suites not selected, the tested commit and tree, the deselected and skipped tests, and a schema that requires them (C3).
   - (g) **My planted-fault trial** (B2): 22 valid faults in 13 non-core modules.
     - The declared map caught all 22 at a median 9 % of the test time. Its recall was as low as 0.10, and without `tests/unit` it would have missed 3.
     - The measured map caught the same 22 at four times the time.
     - The three widest-reaching modules did not run before the lock returned, so the card should not claim the declared map safe for them. The nightly's measured cross-check covers that.
   - (h) **Measured map:** a coverage map across processes is feasible with the installed coverage 7.16.2 and an 83-line shim. 97.9 % of the tests that start `gov` in a child had their child's lines attributed to them. It cost +10 % wall time and +28 % summed case time on one full run (1.9 GB of data, 28 s to build the map). It shows that tests of suites the declared map does not select execute 54 of the 64 non-core files.
   - (i) **The form of the run.** A selection passed as several suite folders breaks W1-35's collection: two of its modules import from a bare `conftest` (finding 17). The selector must keep the full run's form, `pytest tests --ignore=<unselected suites>`, and a KPI line must say that a scoped run collects each selected suite's cases exactly as the full run does.
3. **Why it matters.**
   - By their `allowed_paths`, 23 of the 59 open or in-progress Wave 2 tickets (39 %) may change a shared-core file, so their closes will still run everything. This takes "the retrieval core" as `src/gov/retrieval/**` and `src/gov/retrieve/**` (`scripts/core_share.py`, clone at `21302ae9`). The other 36 will be closed on a selection.
   - A selection miss is a fail-open, caught only by a nightly run that does not exist yet.
4. **Options.**
   - **(a)** Take (a) to (f), (i) and the nightly into W2-66 now. The measured map (h) becomes a follow-up after the nightly runs a week. Estimate: W2-66 grows from 200 to about 350 to 400 lines (selector, test-side import graph, serial scoping, record block). The schema line goes to W2-64.
   - **(b)** All of it, including the measured map, in W2-66: about 550 lines, before P-H-9's additions.
   - **(c)** Keep the card as is and rely on the nightly. This leaves the helper fail-open and makes the target unreachable.
5. **Recommendation: (a)**, confidence medium-high.
   - Classification of the findings: helper changes not followed (finding 3): "Ordinary work: yes; Consequence: fails open". It is feature-gated, so it is an entry criterion of W2-66 (DEC-803), not a round elsewhere. W1-35's collection under a folder list (finding 17): "Ordinary work: yes; Consequence: other (fails closed)", also an entry criterion of W2-66. The rest: "Ordinary work: yes; Consequence: other".
6. **What it blocks:** W2-66's test designer. Waiting costs a full close (60 to 85 minutes) for every ticket closed meanwhile.

### P-H-9 (P1 for W2-66's start). DEC-883 refined by this lens's evidence: what "same code" must include, the index, the serial-only tests, attribution

1. **Context.**
   - DEC-883 (owner, 2026-10-21, during my session) gives W2-66 four things: batched closes (one rebuild, one check, one full regression per integrated head); same-code reuse; the index fresh by code fingerprint; and an examination of the serial-only tests.
   - It says "Lens H's findings refine the details when they come", and it asks this lens about items 4 and 5 by name.
   - DEC-884 gives W2-66 the first slot once this report is in its card.
2. **What happened** (evidence):
   - **Item 3, the fingerprint.** It leaves out record-only paths such as `docs/checkpoints/` and `governance/project/orchestration/`. Two of the three reds of finding 1 came from commits that touched only `governance/project/orchestration/`: `90ef0af6`, 167 files, W1-27's red; and `21302ae9`, 18 files, W1-08's red, which refused W2-02's close today. A close after either commit would have reused the last passing run. Item 1 b's "tests that read records" would catch this only if that set holds those cases, and it is not defined (finding 18).
   - **Item 4, the index.** The lexical and semantic indexes hold record text, not only code. My 14:33 retrieval returned chunks of the register, the tickets, `governance/project/orchestration/packages/P-W2-48-5.md` and the orchestrator's `CHECKPOINT.md`. At 13:01, record-only commits had made both facets `stale`. Reused on the code fingerprint alone, these indexes would serve stale record text: the newest decisions, DEC-883 itself among them, would be missing from retrieval, the route DEC-860 makes standard.
   - **Item 5, the serial-only list** (`tests/acceptance/serial-only.txt`: 55 entries, 263 cases; each entry states its kind):
     - **real-model-or-daemon, 38 entries:** 35 are W1-16's code-graph daemon cases (about 171 cases); W1-19, W1-20 and W1-21 use real models.
       - The daemon cases' stated cost is the tool's start (DEC-561). Each project root already gets its own index folder (`codeintel/__init__.py:56`).
       - What they share is machine-wide: the tool's lock and socket folder `cbm-daemon-<uid>` (DEC-338; W1-16's support can point it elsewhere, `w1_16_support.py:285`) and the UI port that `test_w1_16_ui_off.py` checks.
     - **latency, 10 entries:** time bounds. W1-05's switch-over case is one of them; it reruns three suites (516 s).
     - **live-session, 5 entries (50 cases):** real Claude sessions that spend the owner's usage.
     - **race, 2 entries:** W1-09's claims raced from separate processes. These are correctness checks, not timing.
   - **Item 2 b, attribution by bisect.** W2-02's second red (W1-07's `doctor` case) passed alone on the same tree, both in my copy (9.5 s) and in the orchestrator's re-run (DEC-885). A bisect needs a red that reproduces, and the close kept no failure text.
3. **Why it matters.**
   - As worded, item 3 fails open for the tests that read the repository's records, and those are the tests that went red today.
   - Item 4 would either keep the index `stale` after every record commit (no saving) or serve stale records silently.
   - Item 5 decides whether a batch meets "about one regression": the serial block is 29 of the 72 minutes.
4. **Options** (DEC-105).
   - **(a) Apply now, refined, in W2-66's KPIs:**
     - **item 3:** "the tests that read records" becomes a declared set, a marker such as `repository_state`. It starts from the four files of the queue's gate (f), built today: W1-06's approvals, W1-08's path map, W1-27's path compliance and W1-07's envelope. It adds W2-54's green-here cases, W1-33's definitions and W1-49's window. It also holds every suite that copies the whole tree, until P-H-5 takes the record out of those copies. The set runs on every head, reused or not. The nightly reports any red outside it as a selection miss.
     - **item 4:** two fingerprints. The code fingerprint governs the code index. Changed record files get their lexical and semantic chunks refreshed incrementally; both refreshes already work by file (`lexical._update`; `semantic.refresh` embeds only chunks without a vector). A lexical index whose record files differ is never accepted as fresh.
     - **item 5:**
       - W1-16's daemon cases, except the UI-port case, are tried in parallel with a lock-and-socket folder per test (W2-57's trial; a few lines in W1-16's fixture).
       - W1-09's two race cases are tried in parallel.
       - The latency entries stay alone, with W2-57 revising their bounds; W1-05's switch-over case moves to the nightly (P-H-5).
       - Live sessions and real models move to L4 and L5, and run at L3 only when their own area changed (C2 item 4).
     - **item 2 b:** before a bisect, the failing ids re-run alone at the batch's head. A red that passes alone is a flaky candidate (as W2-L409 is) and is not bisected. The batch's run keeps JUnit XML, so the failure text exists for attribution.
     - **Cost:** about 100 to 150 lines more in W2-66 than P-H-2's estimate (the marker set, the split fingerprint, the alone-first rule), plus W2-57's daemon trial. Risk: low. Until P-H-5 lands, the copy suites (48 % of the test time) run on every head, so reuse saves about half a regression. After P-H-5 the record-reading set takes minutes.
   - **(b) Defer:** build item 3 as worded and rely on the nightly (P-H-3) to find record-made reds within a day. Cost and risk: on 2026-10-21 alone, record commits made three reds. Under (b), each would let closes pass for up to a day (fails open).
   - **(c) Re-baseline:** keep batches (item 1) and drop same-code reuse (item 3) from Wave 2. Cost: no saving across batches when only records changed; every batch runs one full regression, about 60 minutes. Risk: none added.
5. **Recommendation: (a)**, confidence high for items 3 and 2 b. For items 4 and 5 it is medium: item 5's parallel safety is reasoned from the code and the list's own reasons, not measured, because the daemon, model and live cases are `local_only` and did not run here.
   - Classification of the finding: finding 18, "Ordinary work: yes; Consequence: fails open". It is an entry criterion of W2-66 (DEC-803) and refines the owner's own decision; it does not reverse it.
6. **What it blocks:** W2-66's test designer (DEC-881, DEC-884). Waiting costs nothing if decided before W2-66's tests are written, and a test rewrite after.

### P-H-3 (P2). Start the nightly full run now, as glue, before W2-66 lands

1. **Context.** DEC-852 item 3 (standing) puts a nightly full uncached run on `w2/integrate`'s head "from W2-66's merge". Until then nothing tests the head between closes.
2. **What happened.**
   - The head went red at 01:08 and 08:39 today and nobody saw it (P-H-1).
   - In Wave 1 and Wave 2, 5 of the test-related refusal causes came from the repository's state, not from a ticket, W2-02's today among them (A4).
3. **Why it matters.**
   - A red head turns the next close into an hour lost and a counted iteration.
   - A nightly run moves the discovery to the next morning, at no cost to the quiet window when it runs on nights without closes, or after the queue.
4. **Options.**
   - **(a) An orchestrator script now**, like `close_queue.sh`:
     - In the quiet window, clone `w2/integrate`'s head into a scratch folder, then run `pytest tests -n auto` with the serial-only cases afterwards, with `--junitxml`.
     - Write a one-line result to the digest and save the JUnit file.
     - Glue only: pytest, xdist, cron or the orchestrator's queue. About 60 lines, 70 minutes of machine time a night.
     - W2-66's `nightly.py` replaces it later.
   - **(b)** Wait for W2-66.
5. **Recommendation: (a)**, confidence high. Classification: no finding of a ticket; it closes a detection gap ("Ordinary work: yes; Consequence: other").
6. **What it blocks:** nothing. Waiting costs one refused close per undetected red.

### P-H-4 (P2). Remove duplicated runs: the lead's verification in the close's form, and reuse of a run on an identical tree

1. **Context.**
   - Every lead runs every acceptance suite serially, one process each, before each return: 13,857 s (3.85 h) in W2-48's run 2.
   - The close then runs everything again in parallel (about 60 min).
   - DEC-880 (b) keeps "the lead's full verification … as it is".
2. **What happened.**
   - The same 14,770 cases run at least twice per ticket, four times with one resume, more with refused closes (A2).
   - Engineers already shift to `-n 8` because serial runs pass the foreground limit (W2-50's engineer).
3. **Why it matters.**
   - Hours of machine time per ticket, on the machine that also needs quiet windows for closes.
   - The parallel form is the one the close uses, so a lead that verifies in it sees the close's failures, load-sensitive ones included.
   - The lead's full scope is today's only integration test between closes: W2-58's lead found the head's reds of 2026-10-21 (finding 1). Narrowing it before the nightly run exists would remove that.
4. **Options.**
   - **(a)** The lead's full verification keeps its scope (everything) but changes its form to the close's: one `pytest tests -n auto` call with the serial-only cases afterwards. About 35 to 60 minutes instead of about 3 to 4 hours. Only the lead brief changes.
   - **(b)** (a), plus reuse: when the lead's full run is recorded by gov on a tree identical to the merged commit (the lead merged `w2/integrate` last and the integration branch has not moved), the close may accept it as its own run of that tree. The record says `scope: full, reused-from: <run>`. This needs the run record of C3 and a small change in `gov close`.
   - **(c)** Keep as is.
5. **Recommendation: (a) now**, confidence high: the same scope, so the backstop stays. Do not narrow the lead's scope before the nightly exists.
   - **(b) is now decided in another form.** DEC-883 item 3 (owner, today) reuses the last fully passing run for byte-identical code. That is the same idea with the close's own runs as the source, and P-H-9 states the condition it needs: what "the same code" must include. A lead's run as a source can wait until that rule has run for some weeks; confidence medium.
   - Classification: no finding of a ticket; cost only.
   - (a) changes the form of DEC-880 (b)'s "as it is", not its scope. DEC-883 repeats that the leads' "full verification stays", which (a) keeps. It still needs the owner's word.
6. **What it blocks:** nothing. Waiting costs about 3 hours of machine time per lead verification.

### P-H-5 (P2). Test hygiene: no whole-tree copies of the record, mark repository-state tests, move nested reruns to the nightly

1. **Context.**
   - 13 acceptance suites copy the whole working tree in a fixture; W1-07 and W1-27 do it per test.
   - Since DEC-819 the tree holds the orchestration record: 8,046 of 10,058 tracked files, 73 % of the bytes. At Wave 2's start the tree had 1,784 files.
2. **What happened.**
   - These suites take 48.4 % of all measured test time (A1).
   - One of them was red this morning because of a log's contents (P-H-1; repaired at 14:00).
   - W1-07's copy races git's auto-gc (W2-48's residual), and so does W1-25's (A4).
   - W1-05's switch-over case reruns three suites (516 s in my run) and W1-47 reruns the guard's builder tests (41.5 s).
3. **Why it matters.** The regression's cost and its stability now depend on the size and contents of the orchestrator's working memory, not on the code under test, and both grow every day.
4. **Options.**
   - **(a)** A Track A test ticket (proposed W2-67, independent test designer only, every change a recorded `Rewrite-Reason:`):
     - the copy helpers copy `git ls-files` minus the `orchestration-record` namespaces;
     - the function-scoped copies become one session copy plus a cheap reset;
     - the nested reruns move to the nightly.
     - Estimate: about 150 to 250 lines of test code, one round.
   - **(b)** Fold it into W2-57, which already rewrites W1-46's fixtures.
   - **(c)** Wave 3.
5. **Recommendation: (a)**, scheduled right after W2-66 (both touch what a close runs), confidence medium-high. Classification: "Ordinary work: yes; Consequence: other".
6. **What it blocks:** nothing. Waiting costs the copy tax on every run, plus refusals like W1-27's.

### P-H-6 (P2). The kernel capability "test orchestration and evidence": placement and order

1. **Context.** C4 describes the capability: inventory, selection, execution, diagnosis and evidence. Adopted repositories need it with the kernel. EXAMIN is pytest; UPIM and ASMO are Rust and TypeScript.
2. **What happened.**
   - Today the parts are scattered: `gov close`, the orchestrator's scripts and the lead brief.
   - The test-design skill (v1.0.0) says nothing about kinds, cost, copies or repository-state tests.
3. **Why it matters.** Without it, every adopted repository repeats the Gov OS's path: full runs, no evidence of scope, no nightly.
4. **Options.**
   - **(a)** Build it inside the tickets that already exist:
     - W2-66: selection, nightly, record;
     - W2-19: declared commands, readers, ratchet reuse, skips;
     - W2-64: schema;
     - W2-07: gate in `gov close`;
     - W2-11 or a skill CIT-P: kinds and cost rules;
     - Wave 3 W2-38: measured map and profile.
     The extraction into `src/gov/tests/` waits for Wave 3.
   - **(b)** A new kernel ticket now.
   - **(c)** Wave 3 only.
5. **Recommendation: (a)**, confidence medium. Classification: no finding; plan placement.
6. **What it blocks:** nothing in Wave 2. Waiting costs EXAMIN's adoption without scoped closes (W2-27 to W2-29).

### P-H-7 (P3). The SubagentStop hook hides its block reason

1. **Context.** The kernel's SubagentStop hook refuses a helper's final message that lacks the twelve labelled fields (W1-29, CAP-37.d).
2. **What happened.**
   - It writes its reason as JSON on standard output with exit code 2, and nothing on standard error (`template/governance/kernel/hooks/subagentstop.py:51-56`).
   - Claude Code's documentation: "The message that comes with the block is your hook's stderr. If your hook also printed JSON that makes a blocking decision, Claude Code uses that decision's reason instead". For SubagentStop that is `decision: "block"` with `reason` (https://code.claude.com/docs/en/hooks, read 2026-10-21). The hook's `hookSpecificOutput.blockReason` is not that form.
   - My three read-only research helpers were blocked repeatedly "without giving a reason" (one 13 times). Their results reached me only after I resumed each with the twelve-field instruction.
3. **Why it matters.** A helper whose brief forgets the twelve fields cannot learn what is missing, so its work is lost unless someone resumes it.
4. **Options.**
   - **(a)** Print the reason on standard error, or emit `{"decision": "block", "reason": …}` with exit 0. One line, plus one acceptance case.
   - **(b)** Leave it.
5. **Recommendation: (a)**, riding along in the next ticket that touches the kernel hooks (W2-65 or W2-08; DEC-802), confidence high. Classification: "Ordinary work: yes; Consequence: loses work" (recoverable by resume).
6. **What it blocks:** nothing. Waiting costs lost helper results.

### P-H-8 (P3). Record and plan corrections (delegable)

1. **Context.** Small stale items found on the way.
2. **What happened.**
   - DEC-866 sweep misses: W2-19's KPI ("the input globs W2-48's cache keys on"); W2-38's KPI ("on top of W2-48's cache"); W2-07's paths ("except `src/gov/close/cache*`"); W2-L207's triage reason ("met in Wave 2 by W2-38").
   - DEC-880's re-baseline names CAP-53.b, where the selection is CAP-39.c.
   - W2-57, the fix of 26 `load_sensitive` entries, has no ticket file.
   - Four `load_sensitive` entries' fixes are Wave 3 rows with no date.
   - The serial-only list holds 22 entries that are not on `load_sensitive`.
   - The ratchet's field rule (every entry names its fix) has no test (finding 19). One acceptance case per list belongs in W2-19's KPIs, which already change that check.
3. **Why it matters.** Agents read KPIs literally (DEC-866), and a quarantine without a deadline stays (B1: GitLab's 3 days and 3 months; Atlassian's due dates).
4. **Options.** (a) The orchestrator corrects them, delegated (P3, reversible). (b) Leave them to W2-55's check.
5. **Recommendation: (a)**, confidence high.
   - Classification: "Ordinary work: yes; Consequence: other" for the stale texts and lists.
   - Finding 19 is "Ordinary work: yes; Consequence: fails open, latent". Its fix is a test that rides along in W2-19 (DEC-802), not a round of its own.
6. **What it blocks:** nothing.

### Order and estimates

| Order | Package | What | Glue / build / remove | Ticket | Estimate |
|---|---|---|---|---|---|
| 1 | P-H-2 + P-H-9 | W2-66's card before its test designer starts: the corrections, and DEC-883 refined | build selector, serial scoping, record, the record-reading set, the split fingerprint, alone-first attribution; glue JUnit XML | W2-66 (+ W2-64 schema line; W2-57's daemon trial) | 450–550 lines (from 200), before DEC-883's own items |
| 2 | P-H-3 | nightly full run now | glue (script, cron) | orchestrator | 60 lines; 70 min a night |
| 3 | P-H-1 | the record-reading set after record commits, widened (gate (f) built today) | glue (the queue's gate (f) reused) | orchestrator | about 20 lines; 2 to 3 min per batch of record commits |
| 4 | P-H-4 (a) | lead verification in the close's form | remove duplicated serial runs | lead brief | 1 edit; saves about 3 h per verification |
| 5 | P-H-5 | test hygiene | remove whole-tree copies and nested reruns | W2-67 (new) or W2-57 | 150–250 test lines |
| 6 | P-H-7, P-H-8 | hook reason; record corrections; the ratchet's field-rule test | fix | W2-65 / W2-08; orchestrator; W2-19 | small |
| 7 | P-H-6 | the capability across tickets | build in W2-19, W2-07, W2-64, W2-11; Wave 3 W2-38 | those tickets | within their estimates |
| 8 | P-H-4 (b) | a lead's full run as a reuse source | build, once DEC-883's reuse has run for some weeks | after W2-66 | about 80 lines |

## Appendix: where the evidence is

Everything below is in my folder, `/tmp/gov-os-assessment-H/`, and stays after this session. The venv, the pip cache and the wheel were meant to be removed, but the removal was refused twice (header, last limit).

| What | Path |
|---|---|
| Session log and the refusals met | `notes/00-log.md` |
| Collection lists (all, per marker) | `logs/collect*.txt` |
| Part 1, 2 and 3 outputs and JUnit files | `logs/p1.out`, `logs/p1.xml`, `logs/p2.*`, `logs/p3.*`, `logs/p3u.out` |
| Per-test subprocess probe | `logs/probe-p1/`, `logs/probe-p2/`; plugin `scripts/plugins/govh_probe.py` |
| Estate, durations and subprocess summary | `logs/estate.txt`, `logs/p1_summary.txt`, `logs/p1_summary.json` |
| The allowed-paths map (W2-66's declared rule) | `logs/allowed_map.json`, `scripts/allowed_map.py` |
| Static import graph | `logs/import_graph.json`, `scripts/import_graph.py` |
| Who-tests-what map across processes | `logs/cov_map.json` (built by `scripts/cov_map.py`); shim `scripts/govh_covstart.py` and its `.pth` line (the copies the venv used); plugin `scripts/plugins/govh_covmap.py` |
| Map against declared map | `logs/map_compare.txt`, `scripts/map_compare.py` |
| Scoped-close cost estimate | `logs/scoped_cost.txt`, `scripts/scoped_cost.py` |
| Planted faults and mutation sample | plans `logs/plan_b2*.json`, `logs/plan_a6*.json`; results `logs/results_b2.jsonl`, `logs/results_a6.jsonl`; analyses `logs/analysis_b2.json` and `.txt`, `logs/analysis_a6.json` and `.txt`; chain log `logs/rest.log`; `scripts/mutate.py`, `scripts/make_plans.py`, `scripts/prep_rest.py`, `scripts/make_controls.py`, `scripts/filter_a6.py`, `scripts/mutation_runner.py`, `scripts/run_rest.sh`, `scripts/analyse_b2.py`, `scripts/analyse_a6.py`; per-test limit plugin `scripts/plugins/govh_timeout.py` |
| Localisation probes at `2b254458` | `scripts/bisect_doctor.sh`, `logs/bisect.log`, `logs/bisect-last.txt`; `scripts/collect_order.sh` (finding 17); `scripts/untracked_probe.sh` (A6); the set-aside result `logs/b2_invalid.jsonl` |
| `gov retrieve` questions | `logs/retrieve-q*.json`, `logs/retrieve-s*.json` (evidence locations only, texts dropped), `scripts/retrieve_batch.py` |
| Shared-core share of open tickets | `scripts/core_share.py` (output quoted in P-H-2) |
| testmon control trial | `logs/tm*.out`, `notes/B2-testmon.md` |
| Ever-failed tests, duplicates | `logs/ever_failed.json`, `scripts/ever_failed.py`, `logs/dupes.txt`, `scripts/dupes.py` |
| Copy cost | `scripts/copy_cost.py` (output quoted in A1) |
| Research digests (helpers R1, R2, R3) | `research/R1-industry-extract.md`, `research/R2-literature-extract.md`, `research/R3-tools-extract.md` |
