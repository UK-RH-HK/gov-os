
## 294. The owner's answer of 2026-10-24 on P-W2-69-R2-1 (register v0.294, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-909 — W2-69's last round: each key block to gitleaks whole, one more review as the owner's exception to DEC-413; the filter's cases; two daemon cases serial; blocks over 24 KB a residual
- **Status:** ACCEPTED (owner, 2026-10-24, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-24)`) · **Under:** DEC-897, DEC-413, DEC-906, DEC-899 item 4, MR-3 · **Basis:** package P-W2-69-R2-1 (`governance/project/orchestration/packages/P-W2-69-R2-1.md`). W2-69's second and last review failed on F1′: in a document over about 55 KB, a PEM or armoured PGP key block of 10.6 to 13.9 KB is missed at 6 to 15 of 53 piece-edge placements; the code before the ticket missed 0 to 1. Ordinary work: yes; fails open.
- **Decision:**
  1. **(a), the owner's exception to DEC-413:** one more round and one more review, the third.
  2. **The fix:** each BEGIN…END key block goes to gitleaks whole, as its own piece, up to 24 KB.
  3. **Its tests:**
     - blocks of 9 to 24 KB at every boundary position;
     - **P-3:** the index filter's cases, a KPI addition, for the pre-index filter shares the check's gitleaks call and its miss.
  4. **P-4:** the two W2-69 cases that start the code-graph daemon join `tests/acceptance/serial-only.txt`, by its test designer (DEC-906):
     - `test_w2_69_deleted_text_after_rebuild.py::test_the_code_graph_store_holds_no_deleted_word_and_no_free_page_after_a_rebuild`;
     - `test_w2_69_review_rebuild_root_and_held_store.py::test_a_rebuild_given_the_project_relatively_returns_its_result_and_compacts_every_store`.
  5. **Blocks over 24 KB are a recorded residual row** (W2-L419), since gitleaks reads at most 25,000 bytes ahead.
  6. **The fix must not bring back the chance red:** an embedded fragment of a longer identifier stays unflagged, at every read edge.
  7. **This is the last round.** If the third review finds another fail-open case an honest agent can hit, no fourth round starts: the orchestrator brings the owner a package with the options.
  8. **W2-69 keeps its place in the first re-pin.**
- **Changes:** DEC-413 (for W2-69 only: a third review); DEC-897 item 1 (KPI 1 bounded at 24 KB per key block, with the residual above).
- **Where it goes (DEC-851):** this register, with DEC-413's status line marked; W2-69's ticket file and card (its own commit, `Task: DAEO-rmbe`); the Wave 2 list (row W2-L419); RESUME HERE; W2-69's run 2 brief. No standing brief changes.
- Next free id: DEC-910.

| Version | Date | Change |
|---|---|---|
| 0.294 | 2026-10-24 | Owner (recorded by the orchestrator, DEC-861): DEC-909 (P-W2-69-R2-1 (a) with P-3 and P-4, the owner's exception to DEC-413: each key block to gitleaks whole up to 24 KB, tests for 9 to 24 KB blocks at every boundary and the index filter's cases, two daemon cases serial by the test designer, blocks over 24 KB a residual row, the chance red not brought back; the last round, any further fail-open finding a package; W2-69 keeps its place in the first re-pin). Next free id: DEC-910. |
