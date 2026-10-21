
## 272. The owner's order of 2026-10-21 after the close queue: W2-66 first, one combined re-pin (register v0.272, recorded by the W2 orchestrator on branch `w2/integrate`)

### DEC-884 — W2-66 takes the first slot; no re-pin until it is built, reviewed, merged and trialled; W2-59 and W2-65 merge together just before one combined re-pin
- **Status:** ACCEPTED (owner, 2026-10-21, in the chat; recorded and committed by the orchestrator with `Role: orchestrator`, `Task: decision-record`, `Decided-by: owner (chat, 2026-10-21)`) · **Under:** DEC-880, DEC-881, DEC-883, DEC-879, DEC-822, DEC-853 item 4, DEC-786, DEC-861 · **Basis:** the owner's order of 2026-10-21. Today's pin (`fecb870c`) predates W2-58. W2-59 makes the hooks and the declared checks call the pinned judge, so merged before a re-pin it would bring the old read refusals back.
- **Decision:**
  1. **W2-66 comes first.** After lens H reports and its findings go into W2-66's card (DEC-881), W2-66 takes the first slot, ahead of every other ticket.
  2. **No re-pin and no install of judge updates until W2-66 is built, reviewed and merged.** Then one combined re-pin carries:
     - W2-58: reads open;
     - W2-59: checks and hooks on the pin;
     - W2-65: the guard fails safe;
     - W2-66: batched closes, same-code reuse, the index fingerprint.
     The owner re-pins once, not twice.
  3. **W2-59 and W2-65 stay unmerged until that point, and merge together just before the re-pin.**
     - If a reason forces W2-59 or W2-65 to merge earlier, the orchestrator brings the owner a package first.
     - W2-65 shares `.rulesync/hooks.jsonc` with W2-59, so it is built stacked on `w2/W2-59` (DEC-786).
     - Each of the two branches merges `w2/integrate` back in, with its trailers, before the joint merge, and is re-verified there.
  4. **The ladder before the re-pin.** W2-66 has its FULL review, then a trial of the batched close on a dev-tier programme or a fixture repository, measured:
     - the time per batch;
     - reuse correct;
     - a planted code change forcing a fresh run;
     - a red batch attributed, with nothing closing on it.
     Then the orchestrator gives the owner the re-pin commands as an ACT ping. The settings regeneration from `.rulesync/hooks.jsonc` follows the re-pin, in the same ping.
  5. **Meanwhile,** the slots W2-66 doesn't need run the held tickets' resumes by keystone, as the machine and the close queue allow.
- **Changes:** DEC-879 item 1 (W2-59 merges after the queued closes, then the re-pin): W2-59 now merges together with W2-65 just before the combined re-pin. DEC-880 item 3 (W2-65 lands before the settings regeneration after W2-59's re-pin): the regeneration follows the combined re-pin. DEC-853 item 4 (the re-pin at a commit holding W2-50's fix): still holds, since the combined re-pin's commit holds it.
- **Where it goes (DEC-851):**
  - this register;
  - the prompt §3 (order) and §15, v3.9, with DEC-883;
  - RESUME HERE;
  - the cards and ticket files of W2-66 (first slot, the ladder), W2-59 (held, merges with W2-65 before the re-pin) and W2-65 (stacked on `w2/W2-59`, merges with it).
  It does not reach the lead or auditor briefs.
- Next free id: DEC-885.

| Version | Date | Change |
|---|---|---|
| 0.272 | 2026-10-21 | Owner (recorded by the orchestrator, DEC-861): DEC-884 (W2-66 first after lens H; no re-pin until W2-66 is built, reviewed, merged and trialled on a dev tier or fixture; W2-59 and W2-65, stacked, merge together just before one combined re-pin of W2-58, W2-59, W2-65 and W2-66; the held tickets' resumes meanwhile; DEC-879 item 1 and DEC-880 item 3 changed). Next free id: DEC-885. |
