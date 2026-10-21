
## 203. Owner answers of 2026-10-13, second set: where the DEC-665 pass runs, B3's timing, the W1-49 live-session case, W1-31's close, durable backups of the exit clones (register v0.203, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-669 — The DEC-665 test-designer pass runs as a separate designer session inside the W1-38 round
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-664, DEC-665, DEC-491 · **Basis:** the orchestrator's question: the three cases belong to W1-49 (DAEO-32n6, two cases) and W1-33 (DAEO-xog0, one case), both closed, and `gov launch` starts a designer only on an `in_progress` ticket
- **Decision:** option (a).
  - The pass runs as a separate designer session inside the W1-38 round (DAEO-3ef2), with its own commit.
  - Each of the three cases (two of W1-49, one of W1-33) carries a `Rewrite-Reason:` trailer.
  - DAEO-32n6 and DAEO-xog0 are not reopened.

### DEC-670 — B3 waits for W1-42's lead, the W1-31 round and the W1-38 round
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-660, DEC-668
- **Decision:** B3 (the lefthook install) waits until W1-42's lead, the W1-31 round and the W1-38 round have all finished, because git hooks are shared with their worktrees. The orchestrator tells the owner then, together with B2 part 2 (the freeze on this repository). This widens DEC-668's line on B3 by the W1-38 round.

### DEC-671 — The W1-49 live-session case is run three more times alone
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-232, DEC-372, DEC-442 · **Basis:** the regression at `9495bf3a`: in the serial run `tests/acceptance/W1-49/test_w1_49_live_session.py::test_after_the_compaction_the_session_names_the_loop_counts[23]` failed (the reply after the compaction named loop count 17 and not 23); the file passed when run alone once (9 passed)
- **Decision:**
  - The orchestrator runs the case three more times on its own, serially.
  - If it fails again, it comes to the owner as a package, with the Stop hook (active since `71ae763f`) as a possible cause.
  - If it passes all three, it is named for the exit auditor as a flaky live-model case.

### DEC-672 — W1-31 is closed by `gov close` only; if the close refuses on the three DEC-665 cases, one more close follows the designer pass
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-651, DEC-655, DEC-665, DEC-669
- **Decision:**
  - If `gov close DAEO-6mk8` refuses on the three DEC-665 cases, the ticket is not closed with `tk close`.
  - It is closed after the designer pass has merged, with one more `gov close`.
  - If an escalation blocks, the orchestrator stops for the owner (DEC-651).

### DEC-673 — Durable backups of the W1-42 exit clones are made by the operator, outside the repository
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-604, DEC-611 · **Basis:** the orchestrator's report: the two safety copies of the exit clones stood under `.gov-runtime/scratch/orchestrator/`, where the secrets-indexing check found the synthetic programmes' planted secrets in them (ten files) and went red; the orchestrator moved them to its session scratchpad under `/tmp`, so the live clones and their copies are all under `/tmp` now
- **Decision:**
  - In its next report the orchestrator gives the owner the exact paths of the two live clones and of the two safety copies.
  - The operator copies them to `~/gov-os-workbench/archive/w1-42-exit-clones/`, outside the repository and outside any scanned folder.
  - No clone and no programme file is put under `.gov-runtime/` again.

| Version | Date | Change |
|---|---|---|
| 0.203 | 2026-10-13 | Owner: DEC-669 (the DEC-665 designer pass runs as a separate session inside the W1-38 round, Rewrite-Reason on each of the three cases), DEC-670 (B3 waits for W1-42's lead, the W1-31 round and the W1-38 round; told with B2 part 2), DEC-671 (W1-49 live-session case: three more runs alone; package if it fails, named as flaky if not), DEC-672 (W1-31 closed by gov close only, one more close after the designer pass if the first refuses on the three cases), DEC-673 (the operator makes durable backups of the exit clones outside the repository; no clone under the runtime folder). Next free id: DEC-674. |
