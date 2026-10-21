
## 278. The owner's answer of 2026-10-21 on P-W2-62-H, and a standing rule on accepted history (register v0.278, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-891 — W2-62's claim commit 162f17ea9caf accepted as history; accepted-history entries for record-only commits recorded by the orchestrator, entries for code, test or kernel commits stay the owner's own commits
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-734, DEC-487, DEC-436, DEC-871, DEC-861, DEC-862 (a), DEC-851 · **Basis:** package P-W2-62-H (`governance/project/orchestration/packages/P-W2-62-H.md`). On 2026-10-21 at 22:39 the queue's gate (e) stopped W2-62 before its close: its claim commit `162f17ea9caf` ("W2-62 (DAEO-juee): claimed", 2026-10-19), the orchestrator's, carries `Task:` and `Role:` but no `Implements:`. It changes only `.tickets/DAEO-juee.md` (one line).
- **Decision:**
  1. **P-W2-62-H (a).** The commit `162f17ea9caf` (full id `162f17ea9cafeec96687d2a83c43c060c08d3e1b`) is accepted as history. The path map's `accepted_history` gains `{commit: 162f17ea9cafeec96687d2a83c43c060c08d3e1b, decision: DEC-891}`, committed by the orchestrator: the close reads the entry under this ACCEPTED owner decision, which names the commit (`gov/close/history.py`, DEC-734). W2-62 closes after queue run 6.
  2. **The standing rule (owner, standing):**
     - **Record-only commits:** an accepted-history entry for a commit that changes only records or ticket files may be recorded by the orchestrator from the owner's chat decision, as here, under DEC-861.
       - Records and ticket files means `.tickets/`, `docs/checkpoints/`, `docs/close/`, `docs/probes/`, the register, the plan files and `governance/project/orchestration/`.
     - **Code, test and kernel commits:** an entry for any commit that changes code, tests or the kernel stays the owner's own `Role: owner` commit, as the ratchet entries are (DEC-862 (a)), because it exempts that commit from traceability.
       - Code, tests and the kernel means `src/`, `tests/`, `template/`, `.rulesync/`, `.claude/`, `schemas/` and `fixtures/`, and any other path that is not a record.
     - **How the orchestrator applies it:** before recording such an entry, it lists the commit's changed paths (`git show --stat <commit>`) in the decision record. A commit with any path outside the records goes to the owner as an ACT for a `Role: owner` commit, with the entry prepared.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §5 (the decision-record rule, beside DEC-862 (a)'s exception), v3.12;
  - RESUME HERE;
  - W2-12's card and ticket file (`DAEO-j8gn`): the class of owner-only entries W2-12 moves to the owner's push in git now names accepted-history entries for code, test or kernel commits beside the ratchet entries and the escalation lifts.
  It does not reach the lead or auditor briefs: leads and auditors make no such entries.
- Next free id: DEC-892.

| Version | Date | Change |
|---|---|---|
| 0.278 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-891 (P-W2-62-H (a): W2-62's claim commit 162f17ea9caf accepted as history; standing: accepted-history entries for record-only commits are recorded by the orchestrator from the owner's chat decision; entries for code, test or kernel commits stay the owner's own Role: owner commits). Next free id: DEC-892. |
