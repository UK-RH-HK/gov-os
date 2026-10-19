
## 48. Owner decisions: auto-resume hooks (W1-49), the mid-wave audit, and stops (register v0.48, appended by the W1 orchestrator on branch `w1/integrate`)

Owner decisions of 2026-10-04, given during the parallel run.

### DEC-248 — New ticket W1-49: light auto-resume hooks (a light form of CAP-37)
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** CAP-37, DEC-025, DEC-208, DEC-237 · **Amends:** the Wave 1 ticket set (48 → 49 tickets)
- **Decision:**
  - A new ticket, W1-49, delivers light auto-resume hooks, a light form of CAP-37 brought forward by the owner.
    W1-29 later upgrades the injection to the full context packet.
  - Role engineer, profile FULL, priority high, no dependency on an open ticket. It runs with priority, in parallel
    with the tickets in flight.
  - KPIs:
    - (a) a PreCompact hook ensures the orchestrator's checkpoint is current, and in a worktree the lead's;
    - (b) a SessionStart hook on compact, clear and resume injects, within the hook's size cap, the prompt path and
      the checkpoint's RESUME HERE section, with the instruction to read both now;
    - (c) the auto-compact threshold is set to about 300k tokens (30 % of the window) if Claude Code allows it to
      be configured. An acceptance test proves whether it can. If it can't, a residual is recorded: the
      `CONTEXT_CHECKPOINT` stop stays;
    - (d) after a forced compaction (`/compact`), the session's next action shows it knows the active tickets, the
      open owner decisions and the loop counts, without the owner restating them.
  - Allowed paths: `template/governance/kernel/hooks/precompact*`, `template/governance/kernel/hooks/sessionstart*`,
    `.claude/settings.json` (hook registration and any env key, under this decision), `tests/unit/hooks/**`.
  - The Contract gets a Wave 1 covers item under CAP-37 for the light form, in its own commit.
  - Written by the orchestrator to make the ticket valid, not by the owner, and open to the owner's change: the
    dependency on W1-05 (closed; it placed the hook wiring), the estimate of 120 LOC, and the failure KPI lines,
    which mirror the success lines.

### DEC-249 — Mid-wave audit when W1-21 is merged
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Under:** MR-4, DEC-088, DEC-220
- **Decision:**
  - When W1-21 (`gov retrieve`) is merged, a fresh read-only independent auditor, in its own worktree and writing
    to no ticket, checks every ticket closed so far against Contract v4.1 and its covers items, and reports
    findings.
  - Findings follow the delegation rule (DEC-220); owner-level ones come to the owner.

### DEC-250 — Stops after W1-49 closes
- **Status:** ACCEPTED (owner, 2026-10-04) · **Basis:** OWNER · **Amends:** DEC-237, DEC-208 (the main orchestrator's `CONTEXT_CHECKPOINT` stop)
- **Decision:**
  - Until W1-49 closes, the `CONTEXT_CHECKPOINT` stop stays.
  - After W1-49 closes, the orchestrator stops only for owner-level decision packages (P1, and everything the
    delegation rule reserves for the owner), for escalations, and for `WAVE_1_EXIT_READY`. Context is handled by
    auto-compaction with the W1-49 hooks.
  - When W1-49 closes, the orchestrator tells the owner, so that the operator can update section 7 of the
    orchestrator prompt. The orchestrator does not edit the prompt.
  - If KPI (c) of W1-49 ends in the residual (the threshold can't be configured), the orchestrator says so in the
    same message, because the `CONTEXT_CHECKPOINT` stop then stays by DEC-248.

| Version | Date | Change |
|---|---|---|
| 0.48 | 2026-10-04 | Owner decisions: DEC-248 (new ticket W1-49, light auto-resume hooks, a light form of CAP-37; engineer, FULL, priority high), DEC-249 (a mid-wave audit by a fresh read-only independent auditor when W1-21 is merged), DEC-250 (after W1-49 closes the orchestrator stops only for owner-level packages, escalations and `WAVE_1_EXIT_READY`). |
