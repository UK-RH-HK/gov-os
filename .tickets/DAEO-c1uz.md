---
id: DAEO-c1uz
status: in_progress
deps: []
links: []
created: 2026-10-21T07:33:34Z
type: task
priority: 0
assignee: engineer
external-ref: W2-66
tags: [wave-2, close, regression, selection, keystone-2]
wbs_id: W2-66
title: 'Path-scoped regression at close: selection and evidence (the lite W2-38)'
class: implementation
state_class: AUTHORITATIVE
role: engineer
depends_on: []
allowed_paths:
- src/gov/close/select.py
- src/gov/close/nightly.py
- src/gov/close/evidence.py
- src/gov/close/command.py
- governance/project/test-map.yaml
- template/governance/kernel/schemas/test-map.schema.json
- template/governance/project/test-map.yaml
- tests/unit/close/test_select*
- tests/unit/close/test_nightly*
- tests/unit/close/test_evidence*
- docs/research/W2-66-scoped-close.md
kpis:
  success:
  - 'A close runs the ticket''s own acceptance suite, tests/unit, and the acceptance suites of every ticket (Wave 1 and Wave 2) whose allowed_paths overlap a file changed since the last fully green commit (the base, so record-only commits between closes are inside the scope), following test-side imports of shared helpers (such as w1_07_support, imported by 14 suites); it selects in the full run''s form (pytest tests --ignore=...), so W1-35''s collection holds; the close record names each suite and why it was chosen [DEC-880 item 2, DEC-889 item 1, DEC-890 item 1]'
  - 'Any change under the shared core runs the full regression. The shared core is one list in the test map: src/gov/close, src/gov/guard, src/gov/check, src/gov/records; the retrieval core as its eight modules (src/gov/retrieval/__init__.py, chunking.py, lexical.py, semantic.py, ollama.py, rerank.py, fusion.py, retrieve.py); both copies of the kernel hooks (template/governance/kernel/hooks/ and src/gov/hooks/); the path map and the test map; the three widest-reaching modules (src/gov/config/loader.py, src/gov/tasks/tickets.py, src/gov/store/loader.py); and src/gov/cli/main.py and src/gov/errors.py until a planted-fault measurement shows a narrower selection catches their faults. A changed file the mapping cannot place, and a test map that is missing or cannot be read, run the full regression too [DEC-880 item 2 (a), DEC-892 c, P-IS-1 (a)]'
  - 'The couplings imports and coverage cannot see are declared in the test map and followed: text reads (W1-42 reads src/gov/cli/main.py and kernel templates; W1-30''s r11 reads serial-only.txt), a separate process (src/gov/retrieval/rerank_worker.py to W1-19''s real-model file, W1-21''s dev-tier file and tests/unit/semantic/test_rerank_process.py), the two hook copies (to W1-29, W1-49, W2-62, tests/unit/hooks; the session-start and PreCompact hooks also to W1-31, W1-37, W1-38, tests/unit/telemetry), fixture inputs (the live path map and the gitleaks configurations, to W1-16, W1-17, W1-19, W1-20, W1-21, W1-22, W1-24 and W2-54; W1-18''s unit-file listing), declared checks to W1-26, and the named lines of the synthesis''s section 4; W1-07''s three contract files run on every close [P-IS-1 (a)]'
  - 'The serial-only tests are scoped by the same selection: a scoped close runs the serial cases of the suites it selected, one at a time, and the record says which [DEC-889 item 1]'
  - 'A declared record-reading set runs on every head, whatever was selected: every test that reads a declared record-only path, directly or by scanning the tree, is in it; the first list is in the test map, from lens I''s four reports filtered by that rule; the record-only paths are exactly DEC-891''s list (.tickets/, docs/checkpoints/, docs/close/, docs/probes/, the decision register, the plan files, governance/project/orchestration/); for context-reproducibility and core-schema the set reads the pre-close gate''s own gov check result instead of running gov check again [DEC-889 item 2, P-IS-2 (a)]'
  - 'The close record''s evidence block states the scope (scoped, full), the base commit, the head, the tree, every suite and case run, every suite left out and why, every skip with its reason and the skip count, the failing tests with their failure text kept, and the run''s JUnit XML file; the schema line is W2-64''s [DEC-889 item 12, DEC-890 item 1, I4 F5]'
  - 'gov close --full runs the full regression and the record says so; W2-24 and W2-46 use it [DEC-880 item 2 (d)]'
  - 'Every test has a per-test time limit (pytest-timeout with the signal method, an owner install package at this ticket''s start), set above the slowest test''s measured time (900 s held in the trial); a test that passes it fails, naming the limit [DEC-889 item 11 b, DEC-892 b]'
  - 'The parallel run''s distribution mode is one setting; it stays the default (no worksteal) until the nested reruns are gone and worksteal is re-measured in the nightly [DEC-892 a, P-IS-3]'
  - 'One command runs the nightly full uncached regression on w2/integrate''s head in the close''s form, with JUnit XML: every failing test is re-run alone; a red that fails alone is a P1 package with git bisect run over the commits since the last green night; a red that passes alone is a flaky candidate; a test that fails there and that a scoped close since the last green night passed or did not run is a P1 package with the test map corrected in it; coverage.py with lens H''s shim writes the measured map weekly [DEC-880 item 2 (c), DEC-852 item 3, DEC-889 items 4 and 12]'
  - 'Measured and reported in docs/research/W2-66-scoped-close.md, on a quiet machine: the time of a typical scoped close (one module outside the shared core and its tests) against the full close, and the selection''s catch rate on lens H''s planted faults, the three widest modules included; the 15-minute target is stated as reached by W2-66 with W2-68, W2-57''s serial rework and worksteal together [DEC-889 item 11 e]'
  - 'The lead''s full verification before every return is unchanged [DEC-880 item 2 (b)]'
  - 'The valid case this ticket turns red is revised by its test designer with a Rewrite-Reason: W1-30''s test_regression_includes_other_acceptance_folders [I2 F9]; W1-01''s MR-3 whole-history test stays in the nightly and every full run'
  failure:
  - A change under the shared core, a change no mapping places, or a missing or unreadable test map runs anything less than the full regression.
  - A scoped close whose record says full; a skip, a left-out suite or a failure the record does not name; a record without its JUnit XML or failure text.
  - A record-reading test outside the set on a head with record-only commits; a record-only path list that hides a code path.
  - A per-test limit that lets a hung test hold the close; worksteal switched on before the nested reruns are gone.
profile: FULL
sources:
- DEC-880
- DEC-726
- DEC-852
- DEC-841
- DEC-881
- DEC-883
- DEC-884
- DEC-889
- DEC-890
- DEC-892
- DEC-896
- DEC-891
est_loc: 400
acceptance_tests:
  path: tests/acceptance/W2-66/
  author: independent-test-designer (MR-3); written before implementation
track: A
closes:
- P-W2-48-8
list_rows: [W2-H044, W2-M153]
---
# W2-66 Path-scoped regression at close: selection and evidence (the lite W2-38)

Card: `docs/plan/WAVE_2_WBS.md` §2 (W2-66), from DEC-880 item 2, DEC-883, DEC-884, DEC-889, DEC-890 (the split), DEC-892, DEC-896 item 2 (the test map), lens I's synthesis (P-IS-1, P-IS-2) and the owner's review point (DEC-889 item 14).

- **Why:** W2-48's cache, glued to testmon, reused 11.5 % of the tests and saved 3 % of a close (79 min against 81). Per-test tracking made almost every test "always run" here. The measured causes (lens H finding 12, DEC-889 item 11 d):
  - folder listings: 7,076 tests;
  - reads of undeclared files: 3,750;
  - dot-files: 125;
  - child processes the cache could not follow: only about 500.
  The owner withdrew the cache and brought back the lite form of W2-38. A close runs what the change can affect, the full regression stays as the backstop, and the nightly full run catches a miss within a day (DEC-880). Batching, reuse and the fingerprints are W2-68's (DEC-890).
- **Place:**
  - The first slot, the review point passed (DEC-899), with P-IS-1 and P-IS-2 (a) settled.
  - It shares `src/gov/close/command.py` with W2-07 and W2-57: the record's lines here, the gates in W2-07.
  - **The merge order (owner, DEC-899 item 2):** W2-66 and W2-07 are built in parallel, and **W2-07 merges first.** Then this ticket merges `w2/integrate` back into its branch, with its trailers, re-verifies in full, and gets a fresh FULL probe on the merged head before the re-pin. So no merge invalidates the other's review (the W2-50/W2-58 pattern).
- **The ladder (DEC-884 item 4, DEC-889 item 15, DEC-896):**
  - its FULL review;
  - a trial of the scoped close on a fixture repository: a planted change in the shared core runs everything; a planted change in one module runs its suites; a record-only commit runs the record-reading set;
  - then the first re-pin (W2-58, W2-59, W2-65, W2-66, W2-07, W2-69).
- **Allowed paths:**
  - new modules:
    - `src/gov/close/select.py` (the selection);
    - `src/gov/close/nightly.py` (the nightly run and its record);
    - `src/gov/close/evidence.py` (the evidence block);
  - `src/gov/close/command.py`: the calls into these, `--full`, and the record's lines only;
  - **the test map (DEC-896 item 2):**
    - `governance/project/test-map.yaml`: the shared core, the couplings, the record-only list and the record-reading set;
    - its schema `template/governance/kernel/schemas/test-map.schema.json`;
    - the template's copy for adopted projects.
    The path map is named by no ticket. The path map's `test_inputs` key (DEC-876 item 2) moves into the test map; its removal from the path map is the orchestrator's record edit.
  - tests and records:
    - `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`;
    - W1-30's regression files, for the one revision named above;
    - `docs/research/W2-66-scoped-close.md`.
- **Install (DEC-892 b):** pytest-timeout (the signal method), an owner install package at the ticket's start, into the tool registry.
- **Not in this ticket:**
  - batching, the red batch, reuse and the two fingerprints (W2-68);
  - the serial-only list's rework and the load fixes (W2-57);
  - the commit gates before any test, and the disk gate in the close (W2-07);
  - the test hygiene (W2-67).
- **The test designer's files (MR-3: named here, never in the implementer's `allowed_paths`; DEC-899):** `tests/acceptance/W1-30/test_w1_30_regression*`. Each change carries a `Rewrite-Reason:`; no expectation is lowered.
