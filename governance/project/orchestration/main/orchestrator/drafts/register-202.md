
## 202. Owner answers of 2026-10-13: the template's test-folder rule, the six red cases, ARGUS, the doctor; owner steps B1 and B2 part 1 (register v0.202, appended by the W1 orchestrator on branch `w1/integrate`)

### DEC-664 — The template's deny rule on `tests/acceptance/**` is taken out by one W1-38 round; the same edit goes into the two exit clones now
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-315, DEC-584 · **Basis:** the W1-42 lead's run 2 package 1 (`log/W1-42-lead-run2.json`); the orchestrator's finding that `template/.rulesync/permissions.jsonc` denies every edit of `tests/acceptance/**`, the independent test designer's included, while this repository's own source holds no such line
- **Decision:** option (a).
  - One round on W1-38 (DAEO-3ef2), the test designer first, with a probe, takes the test-folder line out of the template's permission source.
  - The same edit is made in the two exit clones now, so that the W1-42 lead is not waiting for the round.
  - Reason: in this repository the guard has decided who may write acceptance tests since the switch-over, and the template follows it. MR-3 is held by the launcher and the guard, not by a deny rule that also stops the test designer.

### DEC-665 — The six red cases on the integration branch: the orchestrator corrects its two records, and one test-designer pass rewrites the three cases
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-083, DEC-312, DEC-635, DEC-649 · **Basis:** the orchestrator's finding of 2026-10-12: six acceptance cases fail on `w1/integrate` itself (W1-48 three, W1-49 two, W1-33 one), all from the apply block `8bb34efe` and the DEC-649 records of 2026-10-11
- **Decision:** option (a).
  - The orchestrator corrects its two records: DEC-649 is recorded under DEC-083, and the tool registry's Claude Code entry names the VS Code extension version. That clears the three W1-48 cases.
  - One test-designer pass rewrites the three other cases to the decided state: the two W1-49 cases (the auto-compact window is set in the user-level settings since the apply block, DEC-635) and the one W1-33 case (`.claude/agents/research.md` is the generated file). Each is recorded as a rewrite after implementation, with its reason.
  - For the record: the close notes of W1-30 and W1-38 said "no code change since the clean regression of DEC-647". That was wrong: the apply commit lay between, and no suite was run after it.

### DEC-666 — ARGUS: a "now" earlier than `created_at` is refused with `ValueError`
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-657 · **Basis:** the W1-42 lead's run 2 package 3, the part left open by DEC-662 (the lead: keep, low confidence; the orchestrator: refuse)
- **Decision:** `retention_decision` refuses a "now" earlier than `created_at` with `ValueError`, as it refuses a missing timestamp.

### DEC-667 — `gov doctor` exiting 3 on version drift goes to the Wave 2 list, named for the exit auditor
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-210, DEC-659, DEC-584 · **Basis:** the orchestrator's package under DEC-659: `src/gov/doctor/command.py` makes the doctor unhealthy when a section's status is "drift", so drift alone gives exit 3, against DEC-210 as the owner reads it
- **Decision:** option (b).
  - No round in Wave 1. Wave 2 list: the doctor reports drift without failing on it (DEC-210).
  - The exit report names this for the exit auditor, so that a red doctor caused by drift alone is not misread.

### DEC-668 — Owner steps: B1 done, B2 part 1 done on a throwaway copy, B3 deferred
- **Status:** ACCEPTED (owner, 2026-10-13) · **Under:** DEC-409, DEC-428, DEC-442, DEC-444, DEC-660 · **Basis:** the owner's report of 2026-10-13
- **Decision and record:**
  - **B1 (Stop and SubagentStop, DEC-442) is done**, through the operator. Dry run and real run: "held-out step: rules written 1", "deny rules: in force 8, generated 8, lost 0, added 0", "generated files: 44 (new 0, changed 1, already the same 43)"; the one changed file is `.claude/settings.json`. Portability: `"findings": []`, exit 0. Commit `71ae763fa244976ed0eebfda8ac787c782943c52` on `w1/integrate` (Task: DAEO-gjjf, Role: owner, Implements: CAP-37.b, CAP-37.d); tree clean, nothing pushed.
  - **SubagentStop is active** from now on in sessions started in the main tree. Every brief the orchestrator writes asks subagents for the twelve-field return (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action).
  - **B2 part 1 (the manual freeze, pause and lift check; W1-42's KPI line "The owner freezes, pauses and lifts from a plain terminal, on a throwaway repository and on this one, and the results are recorded", DEC-428) is done on the throwaway repository.** The owner ran it himself in a plain Ubuntu terminal on a copy of the `a-dev-exit` clone (`~/gov-b2-throwaway`, since deleted). Output, in order:
    - status before: `"pause": {"paused": false, "flag": "absent", "mirror": false}`
    - pause: `{"ok": true, "command": "pause", "result": {"paused": true}, "session": ""}`
    - status while frozen: `"pause": {"paused": true, "flag": "frozen", "mirror": true, "by": "owner", "since": "2026-10-13T13:56:14Z"}`
    - lift: `type LIFT-5786 to lift the freeze: LIFT-5786`, then `{"paused": false}`
    - status after: `"pause": {"paused": false, "flag": "absent", "mirror": false}`
  - **B2 part 2 (the freeze on this repository) is still open**, so the KPI line is half met.
  - **B3 (the lefthook install) is deferred** until both W1-42's lead and the W1-31 round have finished, because git hooks are shared with their worktrees. The orchestrator tells the owner when that moment comes, together with B2 part 2.
  - **Stale state entries (exit checklist A5):** six removed by the owner (five old freeze markers of 2026-10-06, one empty); the last one, keyed to the throwaway copy, is removed after B2 part 1. `~/.local/state/gov-os/` is empty. The main-tree quiet window is released.

| Version | Date | Change |
|---|---|---|
| 0.202 | 2026-10-13 | Owner: DEC-664 (template deny rule on the test folder: (a), one W1-38 round with a probe, same edit in the two clones now), DEC-665 (six red cases: (a), two records corrected, one test-designer pass rewrites three cases), DEC-666 (ARGUS: "now" before `created_at` refused with ValueError), DEC-667 (doctor exit 3 on drift: (b), Wave 2 list, named for the exit auditor), DEC-668 (B1 done at `71ae763f`, SubagentStop active, B2 part 1 recorded, B3 deferred). Next free id: DEC-669. |
