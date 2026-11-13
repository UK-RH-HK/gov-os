---
type: probe
task: DAEO-6lid
reviewer_session: 80cdbed1-ea87-4363-ac20-a1ca2a066aad
implementer_session: "eng-1 11f69ffa-2adb-4261-8caa-1b6b21376c9f (ab2f0d223f22); eng-2 872133fc-eade-48ea-a3f0-ac0e869841d0 (680bdce1f526); eng-3 f77d63a4-59db-454b-bf2d-a974a57710d7 (d25c7f171467)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: da85fe5bcd88cc15be39dda82b7d27eae830973b
decisions_applied: [DEC-1110, DEC-1109, DEC-1027, DEC-1010, DEC-136, DEC-802, DEC-801, DEC-808]
---

# Probe record: W2-159 (DAEO-6lid) the orchestrator's two Stop checks in the product, STANDARD review, rounds 1 and 2 of 2 (DEC-1010)

- **Round 1** (reviewer session b586cef3-a81c-4993-bdae-c2b3534abb21, independent-auditor, Opus high, read-only)
  probed head `2a67c4a63da0`: **fail**. S2 was marked fail with FR-1 blocking (in scope, ordinary work, fails open).
  FR-1: a leftover pid file whose number now belongs to an unrelated, newer process counted as running work, so an
  idle turn ended. S3 was marked fail with FR-2 (in scope, ordinary work, other): the two checks run side by side
  overwrote each other's once-a-turn record. FR-3, FR-4 and FR-5 were out of scope.
- **The repair:** the lead gave FR-1 and FR-2 as behaviours B1 and B2 (DEC-136). B1: a pid file's process counts only
  when it started no later than 900 s after the file was written [lead]. B2: after both checks end, the state file
  holds both records for the turn. FR-2 rode along (DEC-802). The independent test designer added 9 acceptance cases
  (`29b7a2c335fb`). Run without the fix they gave 5 red (exactly B1 and B2) and 89 green. They were merged at
  `da85fe5bcd88`, for 94 cases. A fresh engineer fixed the code with its own unit cases (`d25c7f171467`):
  `running.py` adds the start slack, and `state.py`'s `record()` re-reads and merges under a lock.
- **Round 2** (reviewer session 80cdbed1-ea87-4363-ac20-a1ca2a066aad, independent-auditor, Opus high, read-only, a
  fresh session) probed head `da85fe5bcd88`: **pass**. Every KPI line S1-S5 and F1-F4 passes, FR-1 and FR-2 are
  fixed, and no finding is in scope, ordinary work and fails open or loses work. Rows: FR-3, FR-4, FR-5 (holding, out
  of scope), FR-6 (in scope, other), FR-7 and FR-8 (out of scope, other). There is no third round (DEC-1010).
- **The lead's checks of the probed head `da85fe5bcd88`:**
  - `gov accept W2-159`: pass, 94 passed, 0 failed, every line. S1 15, S2 35, S3 22, S4 11, S5 9, F1 16, F2 6, F3 1,
    F4 1.
  - The scoped verification (`lead_verify.sh`): 4868 tests in the parallel phase, 10 failed, 7 skipped; the serial
    phase had 1 test, green. All 10 reds are outside this ticket: the W2-96 signal family. They also fail on
    w2/integrate f7962d3661d1 (`.gov-runtime/scratch/lead/base_reds.sh`), and integrate has not changed the W2-96 code
    or tests since. They are shared base reds, and W2-177 fixes them.
  - An earlier step, at `680bdce1f526`: `gov accept` read failure-4 as fail because F4 had no case (the README called it
    the lead's check). The test designer added F4's case (`9254a220dfbc`, merged at `2a67c4a63da0`).
- **Residual rows the lead names:**
  - FR-3: standing watchers other than the configured waiter count as running, bounded at 3 h and named. For W2-160's
    helper watch.
  - FR-4: the default dispatcher source takes in-progress tickets in batch 1 as unblocked. An extra block, with
    IDLE-REASON as a way out.
  - FR-5: the waiter is matched machine-wide by command-line text, as S1's wording and the reference do.
  - FR-6: after a host sleep of more than 15 min, a live worker may read as a reused pid. An extra block; unmeasured on
    WSL2; the reference behaves the same.
  - FR-7: `docs/changes/W2-159-evidence.md` was not written. No KPI line covers it.
  - FR-8: the messages cite this register's DEC ids. F3 covers file names, folders and tickets only.

The two reviewers' returns follow verbatim, round 1 first. The last verdict block (round 2's) decides.

## Round 1 (2a67c4a63da0): the reviewer's return

