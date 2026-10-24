task: Fresh FULL probe of DAEO-c1uz (W2-66, path-scoped regression at close) at head 9174e358 on w2/W2-66, read-only, looking for behaviour the acceptance tests miss.
status: DONE — probe complete, verdict fail: three findings are "yes" and "fails open".
work_completed: Sandbox check passed and identity confirmed. I read the ticket, the selection, evidence, nightly and merged close code, the test map and its schema, the W2-66 README, the W1-30 revision and the measured report. I ran the real selection on this worktree's live map and tickets for chosen changed paths (base and change list patched in memory, nothing written), and swept every tracked file. I built two fixture projects with W2-66's own support module and ran `gov close` in each, plus one scratch pytest project. I recomputed the report's selection figures.
files_changed: none
evidence: Sandbox (a) refused with "OSError: [Errno 30] Read-only file system" (exit 1). Sandbox (b) worked: object 1ae28402a109c3397a44b19239a00adfa9472eb0 written, index refresh exit 0. printenv gave independent-auditor and DAEO-c1uz. The worktree is /home/usain/gov-os-worktrees/W2-66 on w2/W2-66 at 9174e358d77bbb0829a3c6ea9694026018686e9b. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-66/src python3 -c "import gov; print(gov.__file__)"` printed /home/usain/gov-os-worktrees/W2-66/src/gov/__init__.py; my scripts put that same src first on sys.path, and the fixture closes ran through W1-30's launcher with it. Fixture closes: the move out of the shared core gave `scope: scoped`, no reason for full, exit 0; the move out of another ticket's paths gave exit 0, with W2-cc left out although its suite at the closed head is "1 failed, 1 passed". On the live map, a change to `tests/conftest.py` gets `scoped` and selects no suite beyond the always-run set. Scratch at start was 8 inodes and 24K; at end 2,183 inodes and 27M. Guard refusals: 1 (a Bash call whose Python `>` inside a heredoc was read as a write to an unresolvable path; nothing was written, and later scripts ran from the scratchpad). Read refusals: 0. gov retrieve: not used; I read the named files directly and ran the code.
tests: None of the repository's suites ran. I ran: 2 fixture `gov close` runs (both exit 0, both wrong per F1); 1 pytest run of the fixture's W2-cc suite (1 failed, 1 passed: the red that was missed); 2 scratch pytest runs (1 failed, 1 passed, 1 error, then exit 2). Deviation: the second scratch run, which only hit a collection error and ran no test, was not given `-o tmp_path_retention_policy=failed`.
discoveries: F1: the selection's change list hides the old path of a moved file, so a move out of the shared core or out of another ticket's paths gets a scoped close; the close's own commit reader turns rename detection off, the selection does not. F2: `tests/conftest.py`, which arrived with the merge, is placed only by W2-67, whose acceptance folder is declared as W1-27, which the overlap rule never reads; a change to it selects nothing beyond the always-run set. F3: W1-27's `test_w2_67_copies.py` loads the W1-07, W1-25 and W1-27 conftests by file path, which the selection does not follow. Also: `w2/integrate` has moved to a00ae32d since the merge's second parent 4da40b60.
risks: The live-map results come from the real selection code with the base and change list substituted, not from a close of this worktree. The record-reading search (two heuristics) is not exhaustive. The report's times and case counts were not re-run (one run is 11.5 min, above the command limit). F7 is reasoned, not reproduced.
lessons: W2-66's `Fixture` builds a project `gov close` accepts in under a minute. Patching the base and change list on the live tree gives exact selections without writing anything. The Bash guard reads `>` inside a heredoc as a write, so probe scripts belong in the scratchpad.
proposed_decisions: Classification: 3 findings yes and fails open (F1 high, F2 medium, F3 low), 4 yes and other (F4 to F7), 1 feature-gated row (DEC-803), 1 known item judged as yes and other. Recommendation (confidence high for F1, medium for F2 and F3): the lead passes F1 to F3 to a test designer for acceptance cases first (MR-4), and the fixes ride along in the resume this ticket needs anyway for the merge package (DEC-802), not in a round of their own.
unresolved: Whether `docs/contract/contract.yaml` (placed only by W2-49, which has no suite) has a live-reading acceptance suite outside the always-run set. The merge package for W1-01's two reds stays the lead's to the orchestrator.
recommended_next_action: The lead commits this probe record and hands F1 to F3 to a test designer as acceptance cases, to ride along with the merge package's resume.

PROBE_RECORD:

# Probe record: DAEO-c1uz (W2-66), path-scoped regression at close, fresh FULL probe after the merge with W2-07

## What was probed
- **Head:** `9174e358d77bbb0829a3c6ea9694026018686e9b` on `w2/W2-66`, worktree `/home/usain/gov-os-worktrees/W2-66`.
- **The ticket's change:** `git diff --stat w2/integrate...HEAD`, 30 files, +4,145 −26: `select.py`, `nightly.py` and `evidence.py` (new); `command.py`; the test map, its schema and the template's copy; W2-66's acceptance suite; W1-30's and W1-39's revised cases; the unit tests; `docs/research/W2-66-scoped-close.md`.
- **The merge:** `03f470a5`, `w2/integrate` (W2-07's gates, W2-70, W2-67 round 1) merged into this branch. Its message says `command.py` was resolved keeping both sides, with the record key `evidence` left to this ticket's engineer, who renamed W2-07's judged paths to `class_evidence` in `7c18f587`.
- **Method:** the code was run, not only read:
  - the real `gov.close.select.plan` on this worktree's live test map and tickets, for chosen changed paths (base and change list substituted in memory, nothing written);
  - a sweep of every tracked file through the selection;
  - two fixture projects built with W2-66's own support module, with a real `gov close` in each;
  - a scratch pytest project for the per-test limit and the naming of collection errors;
  - the report's selection figures recomputed at this head.

## Who probed
A fresh independent-auditor session (`GOV_ROLE=independent-auditor`, `GOV_TICKET=DAEO-c1uz`): read-only on the repository, sandboxed (the write outside the worktree was refused, git object writes worked), effort max. One guard refusal: a Bash heredoc whose Python `>` was read as a write. No read refusals. `gov retrieve` was not used.

## Threat model
ADR-0001: the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Every finding is judged by the two questions: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?". Only "yes" with "fails open" or "loses work" fails the probe.

## Findings

### F1 — A file moved out of the shared core, or out of another ticket's paths, is seen only at its new path (high)
- **What was done:** two fixture projects (`w2_66_support.Fixture`, a green night as the base), each followed by checkpoint and `gov close PROJ-aaaa`.
  - **Fixture 1:** the ticket's paths hold the widget and the shared core (the orchestrator widened them before the base). The engineer moved the shared-core module `src/gov/close/core.py` into `src/gov/widget/core.py`, unchanged.
  - **Fixture 2:** W2-cc's suite (its ticket owns `src/gov/gadget/**`) imports `gov.gadget.other`. The ticket, whose paths hold that file, moved it into `src/gov/widget/other.py`.
- **What happened:** the selection's change list named only the new path.
  - Fixture 1: `scope: scoped`, `why_full` empty, the shared-core owner's suite (W2-zz) left out as `NOT_REACHED`, the close passed (exit 0).
  - Fixture 2: W2-cc's suite left out as `NOT_REACHED`, the close passed (exit 0). W2-cc's suite run at the closed head is red: 1 failed, 1 passed.
- **Cause:** the selection asks git for the changed names with git's default rename detection, which lists a renamed file only under its new name. The close's own commit reader, which the containment gate uses, turns rename detection off, so containment sees both paths and the selection does not. Moves inside the core, and moves into it, are still seen.
- **What should have happened:**
  - a file moved out of the shared core is a change under the shared core, so the full regression runs with `why_full: SHARED_CORE` (KPI failure line 1);
  - a file moved out of another ticket's paths selects that ticket's suite through its old path.
- `Ordinary work: yes, because moving or renaming a module is ordinary refactoring, git's rename detection is on by default for every diff, and nothing needs to be built for it to happen.`
- `Consequence: fails open`

### F2 — The root `tests/conftest.py` gets a scoped close that runs no suite beyond the always-run set (medium)
- **What was done:** the live selection for a change to `tests/conftest.py` alone, and a sweep of every tracked file.
- **What happened:**
  - `scope: scoped`; nothing selected beyond the own suite, `tests/unit`, the every-close files and the record-reading set.
  - The file arrived with the merge (W2-67 round 1). Every pytest run under `tests/` loads it: it refuses a per-run base folder at the start and sweeps old base folders at the end.
  - Only W2-67's `allowed_paths` place it. The overlap rule looks for `tests/acceptance/W2-67/`, which does not exist, because W2-67 declares its acceptance folder as `tests/acceptance/W1-27/` (DEC-892). W2-07's gate reads that declaration; the selection does not.
  - So the cases that test this conftest are left out as `NOT_REACHED` for any close but W2-67's own: `W1-27/test_w2_67_basetemp_refusal.py`, `test_w2_67_sweep_namespaces.py`, `test_w2_67_temp_folders.py`. So is every other acceptance suite that loads it.
  - The test map was written before the file existed and does not list it.
  - The sweep found three more paths placed only by tickets with no suite:
    - `governance/project/orchestration/sync_context.py` (W2-00);
    - `docs/contract/contract.yaml` (W2-49);
    - `docs/audit/wave-1/context-pack-DAEO-03pw.json` (W1-43; its readers are in `tests/unit` and the record-reading set).
    For the contract, the pre-close gate's `gov check` and `tests/unit/readiness` read it; I did not establish an acceptance suite that reads the live file.
- **What should have happened:** a file every suite loads is a test-side shared helper of every suite. It is in the shared core, or followed to every suite. A ticket's suite for the overlap rule is its declared acceptance folder. A path placed only by tickets with no suite places nothing, and widens as an unplaced path does.
- `Ordinary work: yes, because W2-67 is in progress and its round 2 edits tests/conftest.py, and any later ticket given the path gets the same scoped close.`
- `Consequence: fails open`

### F3 — Another suite's conftest loaded by file path is not followed (low)
- **What was done:** the live selection for a change to `tests/acceptance/W1-07/conftest.py`, and separately to `tests/acceptance/W1-25/conftest.py`.
- **What happened:** each change selects only its own suite. `tests/acceptance/W1-27/test_w2_67_copies.py` (merged with W2-67 round 1) loads the W1-07, W1-25 and W1-27 conftests by file path and calls their fixture bodies as plain functions. The selection follows import statements only, and the map has no coupling for this file.
- **What should have happened:** that W1-27 file is selected when one of those conftests changes.
- W2-67's own close runs W1-27 whole as its acceptance folder; another ticket's close does not.
- `Ordinary work: yes, because revising a copying fixture in W1-07's or W1-25's conftest is ordinary test-designer work (W2-67's own round 2 names it).`
- `Consequence: fails open`

### F4 — Cases left out by deselection are not named in the evidence (low)
- **What was done:** the live selection for one module change (`src/gov/cli/commands.py`; the same for `src/gov/status/command.py`).
- **What happened:** every scoped close here deselects 31 cases: W1-01's history file except its one named case (W1-01's MR-3 whole-history case among them), and W1-10's register and completeness files except their named cases. None is named in `left_out`, and the evidence block carries no deselection list.
- **What should have happened:** every case the run left out is named with its reason (KPI 6; failure line 2).
- `Ordinary work: yes, because every scoped close in this repository deselects these cases.`
- `Consequence: other` (the record understates what was left out; nothing passes that would fail)

### F5 — A ticket whose declared acceptance folder is another ticket's has its own suite misnamed in the evidence (low)
- **What was done:** the live selection for W2-67 (declared folder `tests/acceptance/W1-27/`).
- **What happened:** `selected` names `tests/acceptance/W2-67/`, which does not exist, as the own suite. `left_out` names all 18 test files of W1-27 as `NOT_REACHED`, W2-67's own acceptance files among them, although the acceptance run runs W1-27 whole. The same holds for W2-63 (W1-49) and W2-70 (W1-05).
- **What should have happened:** the own suite is the declared folder, and it is not listed as left out.
- `Ordinary work: yes, because three in-progress tickets (W2-67, W2-63, W2-70) declare such folders.`
- `Consequence: other` (a misstated record; the declared folder does run)

### F6 — The test map's note on scripts is wrong for three of four (low)
- **What was done:** the live selection for each of the four scripts named by the note "the scripts under docs/plan/ and governance/project/orchestration/ stay unplaced".
- **What happened:**
  - `docs/plan/tools/validate_s1.py` is unplaced and runs the full regression, as the note says.
  - `docs/plan/wave-1-exit/apply_adapter_output.py` and `write_permissions_source.py` are placed by W1-42, whose suite runs on every close anyway.
  - `governance/project/orchestration/sync_context.py` is placed by W2-00, which has no suite: a scoped close with nothing extra. No test exercises it (only the live-map case names it), so a full run would not catch a fault there either.
- **What should have happened:** the note matches the selection.
- `Ordinary work: yes, because the note is what a reader of the map relies on.`
- `Consequence: other`

### F7 — The nightly's bisect counts "file or node not found" as a bad commit (low; not reproduced)
- **What was done:** read the bisect step; read real JUnit XML of a collection error through the evidence reader.
- **What happened (reasoned):**
  - The step counts pytest's "no tests collected" as a skip and every other failing exit as bad.
  - A collection-error red has a node id of the form `<file>::<dotted module name>`, seen in real JUnit XML. A red test added after the last green night does not exist at older commits.
  - In both cases pytest finds no such node or file at the older commits, so every step is bad and `first_bad` names the range's first commit.
- **What should have happened:** a commit where the test cannot be found is skipped, not counted bad.
- Not reproduced with the nightly itself.
- `Ordinary work: yes, because a new test that is red, or a test module that no longer imports, is an ordinary red.`
- `Consequence: other` (a wrong first bad commit in the P1 package; the red itself is reported)

### Row (feature-gated, DEC-803) — the check result is taken as given
- **What was done:** read how `--check-result` is handled, and searched for readers of `GOV_CLOSE_CHECK_RESULT`.
- **What happened:** the close copies the caller's file byte for byte and hands it to every run. Nothing checks that it is the pre-close gate's own result at this head. No live test reads the variable yet; only W2-66's fixture does.
- **Entry criterion:** of the ticket that makes W2-54's context-reproducibility and core-schema cases read the variable.
- `Ordinary work: no, because no live test reads the variable at this head.`
- `Consequence: fails open` (once a reader exists, a stale file could pass those cases)

### Known item, judged and not found again — W1-01's two reds on the merge `03f470a5`
- **What happened:** git's merge combined two test designers' edits of `tests/acceptance/W1-30/test_w1_30_close.py`. DEC-253's rule refuses a merge whose acceptance file equals neither parent's version, so W1-01's two history tests are red.
- `Ordinary work: yes, because merging w2/integrate into a ticket branch where two designers edited one file is ordinary.`
- `Consequence: other` (the rule refuses; it fails closed, nothing passes)
- It is the orchestrator's package, as the lead plans.

## Found sound
- **Sandbox and identity:** as the brief states.
- **The shared core:**
  - Every member the KPI names is in the live map, written in the guard's pattern grammar, so nested files are covered.
  - Root-level unplaced paths run the full regression: `pytest.ini`, `conftest.py`, `requirements.txt`, `.gitignore`, `tests/acceptance/conftest.py`, `tests/acceptance/__init__.py`.
  - No ticket has a pattern broad enough to switch off the unplaced rule.
- **Suites and helpers:** every acceptance suite has a ticket of its wbs. No two suites have a helper module of the same name. Path-based loads in support modules load `gov` modules by name, W1-27's copies case excepted (F3).
- **Schema:** `shared_core` is required and non-empty. `per_test_timeout` must be above 0, so a map cannot switch the limit off with 0. `distribution` is an enum: the live map says `load`, and a change to the map is itself a shared-core change.
- **The per-test limit:** a hung test failed at the limit with pytest-timeout's text naming it. A collection error is named in the evidence with its file and text. Every run of the close carries the limit, the signal method and `-o tmp_path_retention_policy=failed`: the acceptance run, the parallel run, the serial cases afterwards, and the load-sensitive run alone. So does every run of the nightly: its full run, its runs alone and its bisect steps. This was read in the code; the acceptance cases cover it.
- **The merge with W2-07:**
  - No gate call was removed or reordered; the only W2-07 change is the judged paths under `class_evidence`.
  - W2-07's evidence-class refusal carries no `evidence` key, so the refusal's evidence block overwrites nothing of W2-07's. W2-07's tests use `evidence` only as the ticket's input key.
  - The commit gates and the pre-close gate refuse, uncounted, before the selection runs.
  - An absent pytest-timeout, or a check-result file that cannot be read, ends the close uncounted with nothing recorded, as an absent test runner does on `w2/integrate`.
- **Acceptance tests:** on this branch only test designers' commits change them, besides the known merge. W1-30's revised case adds two assertions and lowers none.
- **The report's selection figures reproduce exactly at this head:**
  - §1: 185 targets left out (43 whole suites, and 142 files in 12 suites), 31 deselections, 26 record-reading targets in 14 suites;
  - the selection column of 12 of the 32 fault rows (1, 3, 5, 6, 7, 9, 10, 11, 14, 15, 16, 18).
  Its times and case counts were not re-run.
- **The record-reading set:** two searches found no record-reading test outside it: record places named next to the repository root, and scans of the whole tree. This is not exhaustive.

## Verdict
**fail.** F1, F2 and F3 are each "yes" and "fails open". F1 breaks the ticket's first failure line: a change under the shared core runs less than the full regression.