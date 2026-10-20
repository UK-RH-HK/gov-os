
## 207. Owner answers of 2026-10-13, fourth set: the change of ORION-im02, the close of DAEO-3ef2 under its escalation, a pre-authorisation for DAEO-6mk8, the guard and tools it does not know (register v0.207, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-682 — ORION-im02 is the named dimension ACCELERATION; the owner accepts MATH-SPEC-003's "Compound dimensions" section for that one constant
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-511, DEC-656, DEC-678 · **Basis:** the W1-42 lead's package PKG-C of run 4 (`log/W1-42-lead-run4.json`): ORION-im01 leaves nothing of the closed specification unimplemented, so no ORION change was available on decided ground
- **Decision:** option (b).
  - The owner accepts MATH-SPEC-003's "Compound dimensions" section for the one constant `ACCELERATION = LENGTH / (TIME * TIME)`, and its name `ACCELERATION`. The rest of that document stays provisional.
  - It is a new small feature, ticket ORION-im02. The closed specification ORION-SPEC-DIMADD is not edited.
  - It is done entirely by the book: claimed, test designer first, engineer, every commit with `Task:`, `Role:` and `Implements:`, and closed with one `gov close`, with no exception and no disposition.
  - It is the DEC-511 proof.

### DEC-683 — DAEO-3ef2 is closed with the ticket tool under its ESCALATION_BLOCKED, by the owner's authorisation
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-492, DEC-584, DEC-651, DEC-664 · **Basis:** `gov close DAEO-3ef2` at `44f5bded` returned exit 4, ESCALATION_BLOCKED, "three consecutive non-converging iterations reached" (`log/close-W1-38M.json`); the orchestrator stopped for the owner as DEC-651 says
- **Decision:** option (a).
  - The owner authorises closing DAEO-3ef2 with `tk close`.
  - Its escalation comes only from history: the nine commits of 2026-10-07 without `Implements:`, and the undone `a95e54a3`.
  - The round's probe passed (`docs/probes/DAEO-3ef2/PR-DAEO-3ef2-round-DEC-664.md`), the regression at `44f5bded` is green (12,203 passed in parallel, 263 serial, validator ALL PASS), and every commit of the round carries all three trailers.
  - It is named for the exit auditor.

### DEC-684 — Pre-authorisation for DAEO-6mk8 only: a close with the ticket tool if its `gov close` returns exit 4 from history alone
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-651, DEC-672
- **Decision:**
  - If `gov close DAEO-6mk8` returns exit 4 and its escalation comes only from history commits from before the trailer rule, or from findings already named as exceptions, with its round's probe passed and its regression green, the orchestrator closes it with `tk close` and names it for the exit auditor.
  - Anything else stops for the owner, as DEC-651 says.

### DEC-685 — The guard refuses a tool it does not know; `MultiEdit` is judged like `Edit`; one short W1-02 round
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-584 (section 11), MR-3, CAP-58 · **Basis:** the W1-38 round's probe (`log/W1-38-probeM.json`, residual 2): the guard answers allow for `MultiEdit`, for every role
- **Decision:**
  - `MultiEdit` is not a deliberate shape. It is an ordinary Claude Code tool that writes files, and the guard answering allow for a tool it does not know breaks its default-deny design (W1-02). Under section 11 it is a fail-open hole in ordinary work.
  - One short W1-02 round, test designer first, with a probe.
  - `MultiEdit` is judged exactly like `Edit`, by its file path, for every role.
  - Any tool the guard does not know is refused (default-deny), unless it is a known read-only tool.
  - The orchestrator checks whether launched workers and leads can use `MultiEdit` today, and reports it.

| Version | Date | Change |
|---|---|---|
| 0.207 | 2026-10-13 | Owner: DEC-682 (ORION-im02 = `ACCELERATION`, MATH-SPEC-003 "Compound dimensions" accepted for that constant, by the book, one `gov close`), DEC-683 (DAEO-3ef2 closed with the ticket tool under ESCALATION_BLOCKED, history only, named for the exit auditor), DEC-684 (pre-authorisation for DAEO-6mk8 on an exit 4 from history alone), DEC-685 (guard: `MultiEdit` judged like `Edit`, unknown tools refused; one W1-02 round with a probe). Next free id: DEC-686. |
