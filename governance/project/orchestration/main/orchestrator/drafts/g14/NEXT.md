# G-14 (DAEO-sdxk): state, 2026-11-03 16:15 (CTO session 33b3628c's engineer)

## Where it stands
- Round 2 was READY. The owner's operator then ran §3, which stopped at the `test_guard_fix_4.py` line with
  `1 failed, 466 passed`. The live files were restored by hand.
- The failure is `test_logged_refusals`. It is ACT-D8's, not ACT-G14's:
  - ACT-D8 took the hidden half out of every tree, so 11 of the 13 logged refusals the test expects are no longer
    refused;
  - the test fails the same way on the live hook with no ACT;
  - its re-baseline is `STILL_REFUSED = [64, 80]`, named in ACT-G14 §2 for the test's owner, not written.
- The rehearsal (`rehearse_act_g14.sh`, `rehearsal.log`) found and fixed two real defects in `role_reads.py`:
  - (ii)'s fork point came from the reflog, which ACT-D8 emptied; it now comes from the commit graph (`_fork`);
  - the link cache's key now holds the method (the module's own sha256) and the repository (R2-F12).
- The rehearsal also found that an exported `D` turns two planted cases red; ACT-G14 now makes a fresh shell a
  precondition.
- §3 now has a pre-check line showing the stale test's failure before anything changes. Every line's expected output
  is the rehearsal's.

## The files here
- The candidate: `pretooluse.py` (`e406653ef6c9`, unchanged), `role_reads.py` (`8c1ea44b2313`), and `bash_writes.py`
  (unchanged).
- The path-map patch: `path-map-role_paths.patch` (`f8372ccdc4dd`).
- `guard4_check.py` (`2a2050872724`).
- The planted cases: `test_g14.py` (146 passed).
- The rehearsal: `rehearse_act_g14.sh` and `rehearsal.log`.
- The owner's ACT: `ACT-G14.md`.
- The replay: `replay.py` and `replay-counts.json`.
- `scoped_tests.sh`.

## Next
- The CTO decides whether the reviewer re-checks the delta in `role_reads.py` (about 30 lines: `_fork`, `_method`,
  the cache key).
- The test's owner re-baselines `STILL_REFUSED`, or §3 runs as written with its named failure.
- Rehearsed green from a fresh shell at 16:23–16:25 (467 / 146 / 747 passed); the delta review is READY; F4 is
  decided (`docs/` stays). Next: the owner runs §3 from a fresh shell.
