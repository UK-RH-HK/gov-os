# ACT-OPERATOR-ROUNDS-1, review round 2 (the last; manifest.sha256 79c95ff36618)

## Round 2

Independent-auditor, claude -p session (round 2), started by the CTO (launch_worker.sh, DAEO-r30l); not the author. Judged only on round 1's findings (P1-F1 to P1-F7) and the fix pass, under ADR-0001's threat model (JUDGEMENT.md). The package's rehearsal was rerun in my own clone of `w2/integrate` at `09e856c70992`, with HOME planted.

**Round 1's findings against the fix pass**

| Round 1 finding | Round 2 reading |
|---|---|
| **P1-F1** (the count can drop a build) | **Closed, fails closed.** `check_act` refuses a manifest whose `act` is missing, null, empty, not a string, or not the requested id. It is called in the fresh G1 path (after `validate_manifest`, before any freeze; the temp copy is removed in `finally`) and in `g1_reuse` (before the sha comparison). The 4 new cases cover the fresh path. My own test covers the reuse path: refused under the new code where the old code passed. No regression: all 13 distinct ACT manifests under scratch and the 6 live frozen copies name their own id. The bundle folder is `<scratch>/acts/<act>/`, so the request id and the folder id are the same string. `undo_step` reads the frozen manifest directly, so `check_act` can never block an undo. |
| **P1-F2** (undo trusted the repository backup) | **Closed; adds a refusal only.** Before taking the lock or writing, each repository backup file must hash to its expected before value. Rehearsed: a backup altered together with its `SHA256SUMS` is refused "is not the before file … nothing changed", and the tree and install are unchanged. |
| **P1-F3** (the stop message pointed at undo) | **Closed; correct restore lines.** After the backup is taken, an EXIT trap prints `cp -pf` lines for the 3 install files and the 4 repository files, and `rm -f` for the new test file. That puts back the exact before state, which `drafts_ok`/`state` require before any write. The old "run undo" texts are gone. Rehearsed: the 7 lines run as printed, the tree is clean, `check` reads "state: before" and every install file is as at the start. Nothing it prints loosens a check (wording row R2-F3). |
| **P1-F4** (the launcher does not wait) | Wording fixed in section 4. |
| **P1-F5** (results missing from the log) | **Real.** `rehearse.sh` now runs and logs the 17 cases on the old code (14 failed, 3 passed) and the CTO's `test_verdict.py` (old: 3 failed, 5 passed; new: 8 passed). My rerun gives the same counts. |
| **P1-F6** (per exact id, counted in blocks) | Stated in section 2 and residual 7.2. |
| **P1-F7** (the scan count) | Stated as 57 "on today's head". That was true at `b9e878009b8c`, the package log's head; it is 58 on `09e856c70992` (R2-F1). |

**Does the fix pass widen anything?** No.
- `operator_run.py` against round 1: only `check_act`, its two calls and one docstring line.
- `verdict.py` and both pin files: byte for byte round 1's.
- `apply.sh` against round 1: one added refusal (P1-F2), the trap and restore text (P1-F3), "run undo" removed from three error texts, and fixed temp names replaced by `mktemp` names. No check is removed or loosened.
- Test file: 4 cases added, none changed.

**Findings**

- **R2-F1 (KPI 3, the rehearsal; scope: in; row).** `rehearse.sh` asserts `records with a verdict block: 57`. On today's head `09e856c70992` the scan reads 58, so a rerun ends `failures: 1`. The 58th record is `governance/project/orchestration/reviews/ACT-NIGHTLY-RESTART-1-review-r1.md`, committed after the package's log. At `b9e878009b8c` the package's own `scan_history.py` reads 57. The same 3 records change reading on both heads, and every apply, undo, tamper, stop and test line matches.
  Ordinary work: yes, because the head moves with every committed review. Consequence: other. Nothing live changes; the owner runs only section 5.
  Fix (optional): assert the 3 changing records rather than the total, or state the count with its head.
- **R2-F2 (KPI 4, the checks, for P1-F1; scope: in; row).** The reuse-path call to `check_act` has no case in `test_dec1131_rounds.py`. I verified it by hand (see the P1-F1 row).
  Ordinary work: no, because the only manifests it could catch are frozen copies made before this ACT that lack `act`, and none exist. Consequence: other. It fails closed either way.
  Fix (optional): add the case.
- **R2-F3 (KPI 2, the undo; scope: in; row, wording).** When `undo` stops after its writes begin, `hand_restore` still opens with "apply stopped part way". The printed lines are right in both cases: both lead back to the before state, from the hash-checked backup.
  Ordinary work: yes, rarely (an undo failing mid-write). Consequence: other.
  Fix (optional): name the command that stopped.

**Class:** (O), the `operator-own` row: the operator's own install and `governance/project/operator/**`, applied by the owner by hand. No path-map or deny-list change, so `replay_refused` is empty.

**Verdict: READY.**

```verdict
{"kpis": [{"kpi": "1", "verdict": "pass", "findings": []}, {"kpi": "2", "verdict": "pass", "findings": [{"id": "R2-F3", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "3", "verdict": "pass", "findings": [{"id": "R2-F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "4", "verdict": "pass", "findings": [{"id": "R2-F2", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}, {"kpi": "5", "verdict": "pass", "findings": []}, {"kpi": "6", "verdict": "pass", "findings": []}], "manifest_sha256": "79c95ff36618eee76d9535402e4c7f9e78c25d88b8f2217e7eca725f21597ff8", "package_sha256": "6fddda37b92312d1aa27620a4ca8c0262d44804fedd8e4f8824230a5f4cf9249", "class": "O", "reviewer": "independent-auditor, claude -p session (round 2) started by the CTO (launch_worker.sh, DAEO-r30l); not the author", "reviewer_brief_sha256": "e86703304144f7d0c3f48332478f696d8f704c540f5ecf6c0551f6bd761ff81a", "time": "2026-11-11T16:33:10+00:00", "replay_refused": []}
```
