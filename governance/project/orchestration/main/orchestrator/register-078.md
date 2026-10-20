
## 78. Delegated decisions on W1-13's packages (register v0.78, appended by the W1 orchestrator on branch `w1/integrate`)

Decided by the orchestrator on 2026-10-05 under DEC-220, on the four packages the W1-13 (`DAEO-w616`) ticket lead
returned. For each the test designer's, the lead's and the orchestrator's recommendations agree on option (a), the
confidence is medium or higher, and the choice is reversible. The tests already encode these options.

### DEC-348 — W1-13 DP-1: `gov readiness` blocks through its exit code, judged from the rows
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-1 option (a); confidence medium-high · **Under:** CAP-30.a, DEC-308
- **Decision:**
  - W1-13 delivers the verdict and its exit code, judged from the readiness rows and never from the record's
    `status`. W1-26 runs it as a check and also fails a specification that is `CLOSED` with a required row open.
    W1-35's change skill runs it before OpenSpec apply and archive.
  - Until W1-26 and W1-35 exist nothing stops a direct `openspec archive`, and the READY rule (W1-09) still trusts
    a status set by hand. Both are residuals of W1-13, for W1-26 and W1-35.

### DEC-349 — W1-13 DP-2: a specification is closed by `gov.readiness.close`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-2 option (a); confidence medium · **Under:** CAP-47.d, DEC-088, CAP-27
- **Decision:**
  - `gov readiness` stays a read command. Closing is the public function `gov.readiness.close(root, id)`: it
    refuses and writes nothing when a required row is open or the record is invalid; otherwise it creates the audit
    ticket through `gov.tasks.create` (none for a LITE feature) and then sets the status. Closing twice gives one
    ticket, and the record is not left `CLOSED` when the ticket cannot be created.
  - The audit ticket has `role: independent-auditor`, `class: audit`, `status: open`, and a title that names the
    specification. A later ticket gives closing a command or a skill step (W1-35 or W1-30).
  - "Fresh" and "authored none of the audited files" (MR-4) are not testable here and stay with the orchestrator's
    session rules.

### DEC-350 — W1-13 DP-3: the specification record is the frontmatter of the change's `proposal.md`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-3 option (a); confidence medium · **Under:** DEC-307, DEC-302, DEC-305, DEC-085
- **Decision:**
  - A specification is the record in the frontmatter of `openspec/changes/<change>/proposal.md`: `id`,
    `type: specification`, `status`, `state_class`, `profile`, `spine` and `capability_types`; `readiness.yaml`
    sits beside it. A missing profile or an unknown capability type does not pass.
  - Nothing writes that frontmatter yet. W1-14's bridge reads this form, and the proposal template of W1-12 or the
    planning skill of W1-35 writes it: a residual of W1-13.

### DEC-351 — W1-13 DP-4: arguments, report and exit codes of `gov readiness`
- **Status:** ACCEPTED (orchestrator, delegated under DEC-220, 2026-10-05) · **Basis:** W1-13 package DP-4 option (a); confidence medium-high on the codes, medium on the names · **Under:** DEC-317, CAP-30.b, DEC-089
- **Decision:**
  - `--specification <record id>` or `--ticket <ticket id>` (through the ticket's `specification` key); with
    neither, every specification.
  - Passing: `ok: true`, exit 0, the report in `result`. A required row open: `ok: false`, `SPEC_NOT_CLOSED`, exit
    code 3, the report in `error.details`, and the message names the open rows. An invalid record:
    `READINESS_INVALID`, exit 1.
  - The report has `specification`, `profile`, `closed` and `open`; each open row has `n`, `key`, `state` and
    `gap_ticket` (the id or `UNLINKED`), in row order.

| Version | Date | Change |
|---|---|---|
| 0.78 | 2026-10-05 | Delegated under DEC-220: DEC-348 (W1-13 DP-1: the exit code blocks, judged from the rows; wiring is W1-26's and W1-35's), DEC-349 (DP-2: `gov.readiness.close` closes and creates the audit ticket), DEC-350 (DP-3: the specification record is the frontmatter of `proposal.md`), DEC-351 (DP-4: arguments, report, exit code 3). |
