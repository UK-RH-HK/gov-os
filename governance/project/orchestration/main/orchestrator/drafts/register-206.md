
## 206. Owner answers of 2026-10-13, third set: the W1-49 live-session case, the governance share in the exit report, the a-dev clean close, the secret-file namespace, DEC-674, the backups of the exit clones (register v0.206, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-676 — The W1-49 live-session case is named for the exit auditor as a flaky live-model case
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-232, DEC-671, DEC-584 · **Basis:** the orchestrator's package under DEC-671: of the three runs alone, one failed and two passed (`test_after_the_compaction_the_session_names_the_loop_counts[23]`: the reply named loop count 17 and not 23); two failures in six runs since the B1 apply
- **Decision:** option (a).
  - The case is named for the exit auditor as a flaky live-model case.
  - Wave 2 list: "the case asks a small model to repeat four facts".
  - **The Stop hook is ruled out as a user-level cause:** the owner's user-level settings have no hooks block at all, checked by the operator, so no user-level Stop or SubagentStop hook exists. The case builds its own temporary project, whose settings register PreCompact, SessionStart and PostCompact only.

### DEC-677 — The exit report states the governance share per ticket as estimated share, measured parts, and the measured total where a close record exists
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-086, DEC-106, DEC-655, DEC-663 · **Basis:** the orchestrator's measurement with the merged reader (`log/share-*.json`): no refusal, version 2.1.292 on every ticket; estimated shares of 0.95 % to 4.2 %; the measured total "not measured" on every ticket, for want of a close record and, on three tickets, for an attachment type no specimen shows
- **Decision:** option (a).
  - The exit report gives, per ticket, the estimated share, the measured parts, and the measured total wherever a close record exists, with "not measured" and its reason elsewhere.
  - The exit auditor judges exit criterion 4 on that.
  - No further round on W1-31.

### DEC-678 — The a-dev clean close: a trailers base only at a genuine adoption boundary; otherwise one small new implementation ticket done by the book is the DEC-511 proof
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-482, DEC-511, DEC-651 · **Basis:** the W1-42 lead's PKG-A: `gov close ORION-im01` refused with `TRAILER_MISSING` on run 2's lead commit `540004a`, which lacks `Implements:`
- **Decision:**
  - Option (a), a trailers base in the a-dev clone's path map at `540004a`, is used only if `540004a` is a-dev's genuine adoption boundary (its adoption's last commit), the way DEC-482 set this repository's base. A base chosen just to pass over the offending commit is not accepted.
  - If it is not the boundary, option (d): in run 4, one small new implementation ticket in a-dev (a real, minimal ORION change), done entirely by the book (claimed, test designer first, engineer, every commit with `Task:`, `Role:` and `Implements:`), and closed with `gov close`, with no exception and no disposition. That ticket is the DEC-511 proof.
  - The orchestrator reports which applied.
- **Which applied (the orchestrator's reading of a-dev's history, 2026-10-13): option (d).** `540004a` (2026-10-12 11:12, the lead's commit that created the ticket file of ORION-im01) is not the adoption's last commit: the adoption stages A6 (`1aadf0e`) and A8 (`bb1852e`, 2026-10-13 17:41) were committed after it. No trailers base is set. ORION-im01 stays as it is, its refused close reported, with no disposition.

### DEC-679 — The a-dev namespace that holds the secret-named files is left for Wave 1
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-662
- **Decision:** the permitted roles of that namespace stay as written. A named residual.

### DEC-680 — DEC-674 accepted
- **Status:** ACCEPTED (owner, 2026-10-13)
- **Decision:** the owner accepts the orchestrator's delegated DEC-674.

### DEC-681 — The exit clones are backed up outside the repository; the copies go into the exit report's evidence list
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-673
- **Decision and record:** the backups were made through the operator, with `cp -a`, to `~/gov-os-workbench/archive/w1-42-exit-clones/`. The sources under `/tmp` are untouched. Every clone is clean, and the entry counts match the sources:
  - `live/a-dev-exit` at `82dca10` (repair ticket `ade-5rcs`, from `gov close ORION-im01`'s refusal);
  - `live/b-dev-exit` at `fc28272` (repair ticket `bde-0kr6`, from `gov close ARGUS-im01`'s refusal);
  - `safety-run2/a-dev-exit` at `8e517f9`;
  - `safety-run2/b-dev-exit` at `132ca2d`;
  - `safety-run1/a-dev-exit` at `29ff08f`;
  - `safety-run1/b-dev-exit` at `ac074b5`.
  They are recorded in the exit report's evidence list.

| Version | Date | Change |
|---|---|---|
| 0.206 | 2026-10-13 | Owner: DEC-676 (W1-49 live-session case named as flaky; no user-level hooks; Wave 2 item), DEC-677 (governance share in the exit report: estimated, measured parts, measured total where a close record exists), DEC-678 (a-dev clean close: a trailers base only at a genuine adoption boundary, otherwise one small new implementation ticket by the book; option (d) applied, `540004a` is not the boundary), DEC-679 (secret-file namespace left, named residual), DEC-680 (DEC-674 accepted), DEC-681 (backups of the exit clones recorded for the exit report). Next free id: DEC-682. |
