You are the ticket lead for ticket `DAEO-ym8a` (`W2-03`, "Decisions as records, each with its own hash"), profile STANDARD, working only in the worktree `/home/usain/gov-os-worktrees/W2-03` on branch `w2/W2-03`.

**Restarted (2026-10-29):** the previous lead of this run was stopped at 16:57, about 20 minutes in, by the orchestrator's own mistake (stopping its launch queue also stopped the leads it had started). It returned nothing. It had committed step 1, the merge of `w2/integrate` (`b23bf1ac`, no conflict, as the dry merge said): check that commit's trailers and that `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` shows 1, then go on from step 2. Note: `w2/integrate` gained DEC-942 since (records only); do not merge again unless `git diff --stat b23bf1ac w2/integrate -- src tests` is non-empty.

**This is run 3: the merge-back (DEC-941 item 2), not a new round.** `git rev-parse --short=12 HEAD` must show `b23bf1ac0b4c`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- your run-2 checkpoint, `.gov-runtime/scratch/lead/CHECKPOINT.md` ("What the resume lead must do", item 3's "Watch", and the residuals);
- the ticket file (`.tickets/DAEO-ym8a.md`), DEC-752, DEC-755 and DEC-941 (items 1.3 and 2).

## Why you start now

- **W2-03 is built and verified work,** held since 2026-10-17 for the close order (DEC-737, DEC-752). Both holds are gone: W2-02 closed on 2026-10-21 (`e52ad8a2`), and W2-01 is closed.
- **The owner's re-plan (DEC-941, 2026-10-29):** the nine held tickets are merged back, re-verified and closed, those in EXAMIN's minimum first, and W2-03 and W2-05 now (item 1.3). Memory is the critical path (block B), and W2-37 waits on W2-03's close.
- **Where the branch stands:** 10 commits ahead of `w2/integrate` and 720 behind; merge bases `645ecbdf4891` and `2a35fd7bef3e` (W2-02's head, now in `w2/integrate`). A dry merge (`git merge-tree --write-tree`) reports **no conflict**.
- **What changed in your paths meanwhile:**
  - W2-68 (merged 2026-10-29, not closed): `src/gov/store/loader.py` (the fingerprints row, `_load`, `load_records`; `a47bc5ab`, `d095486b`) and `tests/unit/store/test_fingerprint_store.py`. Your `_read_register` and `register_entries` change merges into the same file without a conflict.
  - W2-67: 19 files of `tests/acceptance/W1-26/` revised (a green base, planted defects), two of them the files your run 2 changed.
- **Checked read-only today:** your branch's `register_entries`, run on the register as it stands (937 live entries), refuses none, and no two entries share a hash.

## The decisions for this run

1. **Merge `w2/integrate` into `w2/W2-03`** (`git merge --no-ff w2/integrate`, with `Task: DAEO-ym8a`, `Implements: DEC-941` and `Role: orchestrator` in the final trailer block). Never `-s ours`, never drop this ticket's side (DEC-750 item 3).
   - If git reports a conflict that a mechanical fix resolves (both sides kept as written, neither side's behaviour changed), resolve it and say how in the return. Any other conflict: `git merge --abort`, and return PACKAGES naming each file.
   - After the merge, `grep -c '^### DEC-941' docs/DECISION_REGISTER.md` must show 1. If not, stop and return PACKAGES: the trailer gate would refuse every `Implements: DEC-941`.
2. **Rebuild** from this worktree's code (check `gov.__file__` first), under the machine's rebuild lock. Name every entry or record the load lists as `invalid`; `invalid: []` is expected.
3. **Verification: in full,** in the close's form (LEAD-w2-common), plus `pytest --collect-only -q` over `tests` (DEC-868). The merged code has never run as one: W2-68's store change and yours meet in `loader.py`, and the store is shared core. Look hardest at:
   - `tests/acceptance/W2-03/` (its real-register case reads HEAD's register: 937 entries now, 745 at run 2);
   - `tests/acceptance/W1-26/`: W2-67's revised cases against your entry rule (a heading with no status line is no record; an id-only file satisfies no citation);
   - `tests/unit/store/` (W2-68's fingerprint store), `tests/unit/close/` (`state.py` imports `ENTRY` and `FENCE` from `citations.py`, both kept; `history.py` reads the register by its own rule) and `tests/acceptance/W2-68/`.
   - **The nightly:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists, run no suite. From about 01:00, start no full verification run that cannot finish before 02:00. A close queue may be running in the main tree: run your suites only when the 1-minute load is under 20.
   - **Known:** W1-42's accepted reds; the load-sensitive cases, re-run alone. Any other red is named with its cause.
4. **Repair: at most one batch.**
   - A red in this ticket's code: a fresh engineer (`gov launch`, sandboxed, `--effort high`), in the ticket's allowed paths only.
   - A red in `tests/acceptance/**`: a fresh independent test designer (DEC-906), each change with a `Rewrite-Reason:` and no expectation lowered.
   - Then the red cases and their suites again; a second full run only if code changed.
5. **Reviews: none.** W2-03 is STANDARD: no reviewer before the merge (DEC-498), and no probe record exists to go stale (DEC-895 does not apply).
6. **Checkpoint:** `gov checkpoint` at the end (DEC-511), committed with this ticket's trailers.
7. **Your trailers** (LEAD-w2-common, DEC-927 item 2): run `trailer_gate.py` on your worktree before you return.
8. **Return** DONE (green; ready to merge into `w2/integrate`, then the close queue), or PACKAGES. Carry run 2's residuals in the return as they stand. Add any new one.

**The park rule (DEC-941 item 2):** if the repair grows beyond this one run, stop and return PACKAGES naming the cost. That covers a second repair batch, a fix outside the ticket's paths, or a red whose cause is another ticket's code. Name what is left, its size in lines and hours, and what waits on it (W2-37, and W2-05's sweep rows 39 to 41).

**Running beside you:**
- W2-05's lead (today) leaves your paths alone. Its sweep marks the git calls in `src/gov/store/loader.py` and `src/gov/decisions/checker.py` "after W2-03 merges".
- W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
- W2-61 holds `src/gov/retrieval/measure.py`.
- W2-60a and W2-56 hold `src/gov/launch/**`.
- W2-77 holds `src/gov/close/nightly.py`.

Do not touch them. If a fix needs a change there, return PACKAGES.

**Estimate:** about 3 hours:
- the merge and the rebuild, about 30 minutes;
- one full run, about 95 minutes (the last two nightly runs took 5,623 s and 5,707 s);
- the return.

With one repair batch, up to 5 hours.

---
