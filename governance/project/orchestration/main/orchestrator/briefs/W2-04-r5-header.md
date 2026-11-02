# W2-04 (DAEO-u4oz) — the repair round after review 1 (DEC-1025, delegated), then review 2, the last

**Read this first; it overrides the steps below where they differ.** Your review run returned PACKAGES at
`b37b5c8f1741` (head must show it, tree clean; else return PACKAGES naming it). The CTO decided, as you recommended:
- **Merge `w2/integrate` into your branch first** (`--no-ff`, `Task: DAEO-u4oz`, `Role: orchestrator`), so
  `JUDGEMENT.md` (with DEC-1010's rules), the register (DEC-1019 to DEC-1025) and DEC-960's superseded mark are current.
- **P-W2-04-6 (a), F1 (blocks):** a test-design batch (in the tests worktree, from the integration store) gets F1 as a
  described behaviour (DEC-136): a mandatory file or a dependency ticket emptied, or reduced to whitespace, in the
  working tree gives BLOCKED naming the id and the file, or `read: false`; never shown as read with the empty-content
  sha256 or 0 tokens (KPI 5, S5, row W2-H034). Then a fresh engineer fixes it inside `src/gov/context/**`.
- **Riding along (DEC-802):** F2, P-W2-04-8 (a): `further_batch` names the first ranked item not stacked on an exact fit
  or zero room (S7a as written); the designer revises round 2's case with `Rewrite-Reason: DEC-1025`. F3: the check says
  unmeasured, not green, when every ticket refuses. F5 and F6 are Wave 3 rows; P-W2-04-7 is with the owner.
- **Then:** `gov accept`; the scoped run once (heavy-job slot; output outside the worktree; no new rebuild unless the
  selection needs one); then **review 2, the last** (DEC-1010): a fresh independent-auditor with a different model or
  effort from review 1 (`--model claude-sonnet-5-5 --effort max` is fine), the record valid against
  `probe.schema.json`, READY computed by `tools/verdict.py`. READY: commit the record, return DONE with the head. Not
  READY: return PACKAGES; it goes to the owner once, with options.
- You are memory's critical path: W2-15a waits for your landing. The shared embedder is overloaded today: start the
  heavy steps in the background and wait for them; never take an embedder timeout for a code red.

---

