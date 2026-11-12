---
type: probe
task: DAEO-7oxm
reviewer_session: 92138876-57f7-4f00-a84c-ab2de351ef89
implementer_session: 351fe4bb-c01b-40ee-b90b-d3dcc9f6784d
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 2de763208278a906f9e5b0fe084088d4fc7044be
decisions_applied: [DEC-1101, DEC-820, DEC-1052, DEC-1120]
---

# Probe record: W2-178, the auditor's copy of a set leaves out its dropped questions

A fresh independent-auditor session (`92138876-57f7-4f00-a84c-ab2de351ef89`) ran on Opus at high effort, class C2, with
read-only tools. It probed head `2de763208278` of `w2/W2-178` and wrote nothing in the tree, which was clean when it
started and when it finished. The implementers were engineer eng-1 (`351fe4bb-c01b-40ee-b90b-d3dcc9f6784d`: the script,
its unit tests and the evidence) and test designer td-1 (`2a778a04-6040-4b0a-9b29-15a50ed903f5`: tests/acceptance/W2-178/,
`8b67f1344`, merged at `2de763208`). This is round 1, and its verdict is PASS with no findings.

## What was probed

- **S1 / F1 (the auditor's copy).** `plan_inputs` filters the auditor's set copies to the relative paths that do not
  start with `dropped/` under `hidden/` (two lines of code, four of docstring; nothing else in the script changed).
  `plain_files` checks the whole `hidden/` tree for links before the filter, so a link inside `dropped/` still refuses 10;
  a set empty after the exclusion refuses 10. The file budget counts the planned files, so the auditor's count drops by
  exactly the excluded files. `selection.json` comes from the repository tree and the auditor's result check reads
  `misses.jsonl`, so no other route carries a dropped question into the wall.
- **The reading of "its `hidden/dropped/` folder".** Both workers, independently, read it as the folder directly under
  `hidden/` (so `hidden/sub/dropped/`, a plain file `hidden/dropped`, `dropped.yaml`, `dropped-items/` stay staged). The
  reviewer judged it sound against W2-170's Interface (DAEO-61vm): drops are moved by `os.rename` into
  `<A>/hidden/dropped/`, and PF-COUNT refuses a set whose `hidden/` holds any other folder or a file not `q<nn>.yaml`.
- **F1 (other kinds unchanged).** The acceptance cases build the writer's (round 2) and checker's walls with the base
  script (`03393ee51`) and the head on the same planted set (dropped files included) and compare every file, mode and
  folder entry; only the run id inside file contents is replaced, and WALL.json's settings hash is checked against the
  wall's own settings file before it is re-derived. A sanity case builds twice with the base script for all three kinds
  and the walls match, so the replacement can hide no change but the run id itself.
- **F2.** Every case plants its sets root under `tmp_path` in W2-149's planted world; a grep of the new tests for the
  real root's name finds 0 lines.
- **F3.** `git diff --name-only 03393ee51 2de763208278` lists the three allowed paths and five files under
  `tests/acceptance/W2-178/`, nothing else.
- **Mutations** (copies under the reviewer's temporary folder, run through the acceptance tests via `W2_149_SCRIPT`):
  the filter for every kind (2 cases red), `startswith("dropped")` without the separator (1 red), any folder named
  `dropped` at any level (1 red), a destination filter on "contains `dropped/`" (1 red); a correct destination filter
  as control (19 green). Every wrong version was caught.

## What it found

No findings.

## Verification at the probed head

- `gov accept W2-178`: 21 passed, 0 failed, 0 skipped (before the change, at `03393ee51`: 4 failed, 17 passed, the four
  S1 cases).
- The reviewer's own run of the ticket's tests: 33 passed (20 acceptance and 13 unit, as the reviewer counted them).
- The engineer's runs: W2-149 acceptance 173 passed, 35 skipped; W2-173 acceptance 78 passed, 1 failed:
  `test_w2_173_unchanged.py::test_f4_the_branch_changes_only_the_ticket_s_paths`, branch-scoped (it judges any branch
  against W2-173's own paths; W2-180 makes it judge only W2-173's branch, the CTO's note).
- `lead_verify` (the whole suite, in parallel): 3817 tests, 6 failed, 6 skipped. All 6 are the W2-96 signal cases
  (P-W2-121-5; W2-177). Run alone with the empty HOME, the three W2-96 files give the same 19 failed and 15 passed on
  w2/integrate's head `d02e957ba` and on `2de763208` (identical lists); src/ and tests/unit/accept are untouched against
  `03393ee51`.
