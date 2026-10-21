# DEC-883: what to apply when the close queue ends (drafted 2026-10-21 14:3x; the queue was running)

Apply in this order, run `tools/record_checks.sh`, then commit with `Task: decision-record`, `Role: orchestrator`, `Decided-by: owner (chat, 2026-10-21)`.

1. **Register:** append `drafts/register-271-DEC-883.md`; version 0.271.
   - On DEC-879's status line: `· **Changed by:** DEC-883 item 1 (c) makes "no code merges while a batch runs" the batch rule of W2-66`.
2. **W2-66's card (WBS §2) and `.tickets/DAEO-c1uz.md`:**
   - Title: "Path-scoped regression and batched closes at close (the lite W2-38; DEC-880, DEC-883)".
   - Add KPI lines to the success list:
     - a batch: queued closes on one integrated head share one rebuild, one `gov check` and one full regression on that head, then each ticket's own checks one after another (its acceptance suite, the tests that read records, trailers, paths, probe record, checkpoint); no code merges while a batch runs; each close record cites the batch's run (fingerprint, commit) and states its validation scope (DEC-883 item 1);
     - a red batch closes no ticket on that run; the failure is attributed by `git bisect` over the batch's merges or by the failing tests' own ticket, with the evidence; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run; a close never cites a red regression (item 2);
     - a close whose code tree fingerprint (record-only paths left out, declared in the path map: `docs/checkpoints/`, `governance/project/orchestration/`, and the like) equals the last fully passing run's reuses that run and runs only its own ticket's checks; a failing run is never reused; any code difference runs fresh (item 3);
     - the store-freshness check accepts a store built on the same code fingerprint; the record-only commits' records are loaded incrementally; a code difference needs the full rebuild (item 4);
     - target: a batch in about one regression's time plus a few minutes per ticket, measured against today's queue (six closes, about 8.5 hours) (DEC-883).
   - Failure KPIs: a close that cites a red run, or a run on a different code fingerprint; a reused run whose code differs; a store accepted on a different code fingerprint; a record-only path list that hides a code path.
   - Paths widen: `src/gov/close/repo.py` (the store-freshness check only), `src/gov/close/batch.py` (new), `src/gov/close/fingerprint.py` (new), `src/gov/store/**` (the fingerprint the rebuild records and the incremental record load only), `tests/unit/store/test_fingerprint*`, and the path map's record-only list.
   - Sources: + DEC-883. Estimate: 200 → about 450 lines.
   - Entry note: DEC-881 stands (its test designer starts after lens H); lens H's findings refine DEC-883's details.
3. **W2-57's card:** add "DEC-883 item 5 (owner, 2026-10-21): find out why each of the 263 serial-only tests (29 min of every close) must run alone, and run in parallel every one that safely can, with lens H's findings; each kept serial case names its reason."
4. **Prompt (v3.9):**
   - §3 "Closes and the regression": add "From W2-66's merge and the re-pin that holds it, queued closes on one integrated head run as one batch (DEC-883): one rebuild, one check and one full regression, then each ticket's own checks; no code merges while a batch runs; a red batch closes nothing and its cause is found by bisect; a close on code identical to the last passing run reuses it."
   - §15 "Closes": add "Until W2-66 lands, the queue runs as today (DEC-883)."
5. **RESUME HERE:** already noted (scratch).

## DEC-884 (owner, 2026-10-21, the order after the queue), same commit

6. **Register:** append `drafts/register-272-DEC-884.md`; version 0.272.
   - DEC-879's status line: `· **Changed by:** DEC-884: W2-59 merges together with W2-65 just before the combined re-pin, not after the queue`.
   - DEC-880's status line: add `; DEC-884: the settings regeneration follows the combined re-pin`.
7. **W2-66's card and ticket:**
   - "Place": the first slot after lens H's findings are in its card, ahead of every other ticket (DEC-884 item 1).
   - Add "The ladder before the re-pin (DEC-884 item 4)": its FULL review, then a trial of the batched close on a dev-tier programme or a fixture repository, measured (time per batch; reuse correct; a planted code change forcing a fresh run; a red batch attributed and nothing closing on it), reported in `docs/research/W2-66-scoped-close.md`.
8. **W2-59's card:** "Held unmerged (DEC-884): merges together with W2-65 just before the combined re-pin, after W2-66 is merged and trialled; first it merges `w2/integrate` back, with trailers, and is re-verified. An earlier merge needs a package to the owner first." Its "After it merges" line: the owner re-pins once, at the combined merge commit (W2-58, W2-59, W2-65, W2-66).
9. **W2-65's card and `.tickets/DAEO-e82f.md`:** "Starts" now reads: "built stacked on `w2/W2-59` (both change `.rulesync/hooks.jsonc`; DEC-786), in a slot W2-66 does not need; merges together with W2-59 just before the combined re-pin (DEC-884); the settings regeneration follows the re-pin." Sources: + DEC-884.
10. **Prompt v3.9 §3 order line:** replace "W2-66 ... takes the next free slot after W2-58's merge, ahead of every other keystone-2 start ... W2-65 starts after W2-59 merges and lands before the owner's settings regeneration" with: "**W2-66 takes the first slot, ahead of every other ticket, once lens H's findings are in its card** (DEC-881, DEC-884). **No re-pin and no judge update until W2-66 is built, reviewed, merged and trialled** on a dev tier or fixture (time per batch, reuse correct, a planted change forcing a fresh run, a red batch attributed); then one combined re-pin (W2-58, W2-59, W2-65, W2-66) as an ACT ping, with the settings regeneration. **W2-59 and W2-65 (stacked on W2-59) stay unmerged and merge together just before it;** an earlier merge needs a package to the owner first. Other slots run the held tickets' resumes by keystone (DEC-884)."
   - §15: "Until W2-66 lands, the queue runs as today (DEC-883); the re-pin waits for DEC-884's ladder."
