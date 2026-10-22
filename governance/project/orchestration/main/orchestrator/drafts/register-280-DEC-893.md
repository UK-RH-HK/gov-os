
## 280. The owner's rule of 2026-10-22 on placeholders (register v0.280, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-893 — No placeholder reaches the owner or a commit: a scan in the record checks
- **Status:** ACCEPTED (owner, standing, 2026-10-22, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-22)`) · **Under:** DEC-868, DEC-862 (a), DEC-861, DEC-851 · **Basis:** the owner's `Role: owner` commit of DEC-892's W1-38 entry (`49c24ac9`, 2026-10-22). The entry's reason carries an unfilled placeholder, "2026-10-22 00:2x", which the orchestrator had prepared.
- **Decision:**
  1. **The committed entry is not corrected now.** The real time goes into the owner's next ratchet commit, or into W2-57's removal of the entry. The alone run fell between 00:12 and 00:16 on 2026-10-22: after W2-63's refused close ended at 00:11, and before the DEC-891 commit at 00:16.
  2. **The rule (standing):** the orchestrator's record checks include a scan that refuses placeholders in any prepared entry, patch or record before it reaches the owner or a commit:
     - an unfilled time or date (`00:2x`, `16:xx`, `2026-10-xx`);
     - `TBD`, `TODO`, `XXX`, a whole-word `xx`, `???`;
     - in path-map lines and patches, an angle-bracket slot (`<n>`, `<time>`).
     The scan is `tools/placeholder_scan.py`, run by `tools/record_checks.sh`, and also on a package or entry before it is sent (`placeholder_scan.py <file>`). It caught the committed entry (`--commit 49c24ac9`) and passes `cf8219a8`.
  3. **The orchestrator's earlier records** that carry approximate times as placeholders are corrected in its next record commit (the "From" lines of eight packages, P-W2-63-C1's and row W2-L414's "00:2x"). DEC-892's register entry carries none.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §15 (the record checks), v3.14;
  - RESUME HERE;
  - the orchestrator's `tools/record_checks.sh`.
  It does not reach the leads' or auditors' briefs: they prepare no owner entries.
- Next free id: DEC-894.

| Version | Date | Change |
|---|---|---|
| 0.280 | 2026-10-22 | Owner (recorded by the orchestrator, DEC-861): DEC-893 (no placeholder reaches the owner or a commit: a scan in the record checks; the committed W1-38 entry's time folded into the next ratchet commit or W2-57's removal). Next free id: DEC-894. |
