
### DEC-955 — ACT 1 first: a close refused before ACT 1 waits for it; a fresh session right after ACT 1
- **Status:** ACCEPTED (owner, 2026-10-30, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-30)`) · **Under:** DEC-954 (Q8 a), DEC-952 item 6 · **Basis:** the owner's chat message of 2026-10-30, after ACT 1 was asked for ahead of milestone 2
- **Decision:**
  1. **ACT 1 comes first:** if any close is refused before ACT 1 is committed, its ticket is not repaired until ACT 1 is committed.
  2. **A fresh session right after ACT 1:** once ACT 1 is committed, the orchestrator writes the handover (the checkpoint and RESUME HERE), tells the owner it is ready, and stops. The fresh session starts under the five-rule guard.
- **Where it goes (DEC-851):** this register; RESUME HERE; the decisions-in-force list.

| Version | Date | Change |
|---|---|---|
| 0.338 | 2026-10-30 | Owner (recorded by the orchestrator, DEC-861): DEC-955 (a close refused before ACT 1 waits for it; a fresh session, under the five-rule guard, right after ACT 1 is committed). Next free id: DEC-956. |
