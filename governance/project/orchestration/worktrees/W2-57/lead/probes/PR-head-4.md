---
type: probe
task: DAEO-cy5o
reviewer_session: 2d310c50-9b13-496f-b973-32c91ba8b57a
implementer_session: 310f4f41-0e50-4ddd-9c2d-bb6c998cc96f
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: @@PROBED@@
---

# Probe record: DAEO-cy5o (W2-57), judgement-only re-probe after W2-68's merge (DEC-895)

## The lead's note

- **What was probed.** Head `bd418982e6c0` of `w2/W2-57` is made of two commits:
  - the lead's merge of `w2/integrate` at `848f5ab366b9` (merge `27f290a2beef`, made for this re-probe), which brought W2-68 (DAEO-2gc7: batched closes, reuse of a fully passing run on the same code, two fingerprints, the red-run hold);
  - the lead's checkpoint record `CP-DAEO-cy5o-0015`.
- **What kind of probe.** It was a judgement-only re-probe (DEC-895 item 2), not a new review round.
- **Its scope** was every file the earlier probe judged that changed between that probe's head `8d9d78d93529` and this head. That is two files:
  - `src/gov/close/command.py`, read with the change behind it in W2-68's `src/gov/close/batch.py` and `src/gov/close/fingerprint.py`;
  - `docs/plan/WAVE_2_WBS.md`, a new W2-75 card only.
- **Its questions:** does W2-68's change alter what the earlier probe found? Does it let a close pass something W2-57's change refused? The four areas were:
  - the serial phase's entries, in a full and in a reusing close;
  - the nightly route, and a reused run's skips;
  - the order of the commit gates before any test;
  - the reused check.
- **Why.** The earlier record, `PR-DAEO-cy5o-reprobe-1.md` (pass at `8d9d78d93529`), went stale when the merge of W2-68 changed a judged file (`command.py`, 31 lines in, 11 out). The earlier records stay as they are.
- **Who probed.** A fresh read-only reviewer: role `independent-auditor`, session `2d310c50-9b13-496f-b973-32c91ba8b57a`, effort max, from 2026-10-29 23:56 to 2026-10-30 00:18.
  - It was started through `gov launch` under its OS sandbox, with the reading tools alone (`Bash`, `Read`, `Grep`, `Glob`).
  - The ticket lead, an orchestrator-role session (DEC-137), commissioned and judged it.
  - It wrote nothing in the repository. The lead's tripwire before and after its session shows no change in this worktree. The changes it shows are elsewhere, by other sessions:
    - the main tree's head and its W2-71 acceptance folder;
    - W2-03's head and its W2-71 folder;
    - W2-60a's sandbox placeholder entries.
- **The lead's verification at this head** (the code is identical to the merge):
  - **`w2/integrate`:** it moved to `26309d7b430c` (records, and W2-68's and DAEO-5j8b's closes). `git diff --stat 848f5ab366b9 w2/integrate -- src tests` is empty, so there was no second merge.
  - **Rebuild:** a full rebuild at the head under the rebuild lock, exit 0. A first `gov check` after the merge-time rebuild was red on index freshness and recovery/rebuild, only because `CP-DAEO-cy5o-0015` had been committed after that rebuild. The rebuild at the head cleared both.
  - **Keyword warning:** 0 files.
  - **`gov check`:** ok; 15 GREEN, 2 YELLOW (`core-decision-citations` and `openspec-validate`, both known at the earlier reviews), no RED.
  - **Parallel run:** `tests/acceptance/W2-57/` and `tests/unit/close/` in the close's parallel form, under the verify lock, with `-o tmp_path_retention_policy=failed`: 493 passed, 0 failed, 0 skipped.
  - **Serial entry:** the one serial entry in that scope, `tests/acceptance/W2-57/test_w2_57_designer_read_p95.py`, alone, under the verify lock: 1 passed in 2.86 s (2026-10-30 02:13, load 0.61).
  - **Collection:** over `tests` in one process, `16751/16753 tests collected (2 deselected)`, no error.
- **Threat model (DEC-801, DEC-808).** Reviewers and probes judge against ADR-0001's threat model: honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries.
  - Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`.
  - Only "yes" with "fails open" or "loses work" fails the probe.
- **Verdict: pass.**
  - **Classification (DEC-809):** no finding. Observation A is yes / other: a plain `gov close` reuses a full close's run on the same code, by W2-68's design. Observation B is no / other, feature-gated (DEC-803): a red batch record on the head's code refuses the close before the commit gates report.
  - **Earlier records:** review 2's F1 to F4 and run 3's O1 stand with their classification, since nothing they judged changed.
  - **The lead's judgement agrees with the reviewer's.** In a full and in a reusing close, W2-57's serial phase runs exactly the entries not routed to the nightly, and `cases` states what ran. The nightly route is not widened, and a reused run's skips are stated. The commit gates still refuse before any test, uncounted. The reused check never stands in at this head, and every path W2-57 governs is code, so any change to it ends reuse.
  - **Observation B** goes to the orchestrator as an optional entry criterion for switching on the batch (W2-68's owners). It is not a round.

## The reviewer's record

