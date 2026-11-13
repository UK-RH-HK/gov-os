# PKG-W2-172-TESTS-1: three Interface points from the test design (DAEO-p8tv, tests run 1b, 2026-11-12)

## GATE-1 (lead's, from td-1's discovery): `--gate-cmd <exe>` vs the default `gov resources --check`
Interface §1/§8: `run` calls `--gate-cmd` "with no arguments"; the wrapper's default (O2) is `gov resources --check`, a command with arguments, not one executable.
- (a) The driver splits `--gate-cmd` with `shlex.split` and runs the words as given, adding nothing (one-line Interface edit to §1 and §8; no test change, since the tests' gate stub is one word). Cost: ~5 lines.
- (b) The value stays one executable; the wrapper passes the path of `gov`, and the driver appends `resources --check`. Cost: the stub cases change; the seam stops being generic.
- (c) No default gate in the wrapper; the cron line sets `GOV_MEMAUDIT_GATE`. Cost: the crontab ACT has to carry it, and a missing variable means no gate.
Recommendation: (a), confidence 0.8. Blocks: the engineer's wrapper default (S9) and the gate call (§8).

## TD-1 (td-1's): `--force` in the digest
Item 1 says `--force` is recorded "in the counts and the digest", but item 7's 12 lines have no place for it.
- (a) Add a word to the MODE line (`MODE <m> reason <code> force`). Cost: a one-line Interface edit and one digest regex.
- (b) The digest does not record it; drop "and the digest" from item 1. COUNTS.json and STARTS.log already record it. Cost: none.
- (c) Add a 13th line. Cost: breaks "exactly 12".
Recommendation: (b), confidence 0.7. Blocks: nothing now.

## TD-2 (td-1's): a refusal's COUNTS.json and RN-NAME
§3: a refusal writes `<R>/<A>/COUNTS.json` when `<R>/<A>/` does not yet exist, so the folder then exists and a same-day retry refuses with `RN-NAME`, even though "a refusal is not a started audit".
- (a) Accept it: a refusal's retry waits for the next date. Cost: none; it can lose a day.
- (b) Judge `RN-NAME` by `STARTS.log`, i.e. refuse when a line there already names `<A>`. Cost: a one-line Interface edit.
- (c) Write a refusal's counts elsewhere (e.g. `<R>/refusals/<A>-<n>.json`). Cost: Interface edits in §3, §4 and §7.
Recommendation: (b), confidence 0.6. Blocks: nothing now (no case depends on either answer).
