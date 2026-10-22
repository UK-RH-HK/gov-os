
## 284. The owner's answer of 2026-10-22 on P-W2-62-G1 (register v0.284, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-897 — The secrets check's chance red: W2-69 (FULL) in the first re-pin, with a widened design question; one proven re-run of a close's queue, written and narrow
- **Status:** ACCEPTED (owner, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-868, DEC-780, DEC-896, DEC-889 item 15, DEC-801, DEC-861 · **Basis:** package P-W2-62-G1 (`governance/project/orchestration/packages/P-W2-62-G1.md`).
  - W2-62's queue stopped at gate (b) at 13:56: secrets-indexing RED on the code-graph store, rebuilt at 13:44.
  - The orchestrator's diagnosis printed positions, rule ids and exit codes only:
    - one `gov-token-lower` hit, 62 bytes inside an 84-character identifier, in no tracked file;
    - gitleaks is clean on the line that holds them and red on that line cut at the match's first byte.
    So a read of gitleaks that begins inside a word makes the rule's word boundary match. It is a new cause, not row W2-M395's byte join.
- **Decision:**
  1. **(a) W2-69, FULL, rides in the first re-pin** (with W2-58, W2-59, W2-65, W2-66 and W2-07, DEC-896).
     - **Its design question is wider than reads at word boundaries.** Should the secrets check:
       - scan the indexed text (a SQLite store's rows, as text) instead of the database's raw bytes;
       - with the store compacted after each rebuild (`VACUUM`), so no deleted text survives in free pages;
       - and keep a boundary-aware raw scan only as a backstop?
     - **Its tests decide:**
       - a real token is found at every offset and in every form the stores hold it;
       - an embedded fragment of a longer identifier is not flagged;
       - deleted text does not survive a rebuild.
     - Row W2-M404 records the cause (fixed by W2-69). Row W2-M395 (fixed by W2-45) is W2-69's to settle too, if the text scan covers it.
  2. **(b) A narrow, written exception, not a habit: one re-run of a close's queue.**
     - **When:** only when the orchestrator has proven, as for W2-62:
       - that the hit lies inside a longer identifier;
       - and that it is in no tracked file.
     - **How it is recorded:** with that evidence (rule id, length, the enclosing word's length, the tracked-file count, the cut test), in the queue's log and in the report. Positions and classes only, never the bytes.
     - **At most one per close.**
     - **Any other red, or a second red, stops the queue until W2-69 is pinned.**
     - The same rule covers W2-50's re-close.
     - This does not lift "never rebuild-until-green" for anything else, and it weakens no check: `gov check` runs unchanged and must pass.
  3. **W2-62's queue runs once now under (b)** (its one re-run, evidence in P-W2-62-G1 §2).
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §15 (the closes), v3.17;
  - RESUME HERE;
  - the Wave 2 list (row W2-M404);
  - W2-69's card in the WBS and its ticket (each ticket-file commit with `Task: <W2-69's id>`, DEC-896).
  It does not reach the lead or auditor briefs: only the orchestrator runs the close queue.
- Next free id: DEC-898.

| Version | Date | Change |
|---|---|---|
| 0.284 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-897 (P-W2-62-G1 (a) and (b) with conditions: W2-69 FULL in the first re-pin, its design question widened to scanning the rows as text with the store vacuumed after each rebuild and a boundary-aware raw scan as a backstop, its tests deciding; one re-run of a close's queue only on proof that the hit is inside a longer identifier and in no tracked file, recorded with the evidence, at most one per close, any other or second red stopping the queue until W2-69 is pinned; W2-62's queue once now). Next free id: DEC-898. |
