You are the ticket lead for ticket `DAEO-2gc7` (`W2-68`, "Batched closes, reuse on the same code, and two fingerprints"), profile FULL, keystone 2, working only in the worktree `/home/usain/gov-os-worktrees/W2-68` on branch `w2/W2-68`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `966b9f6b5596`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it.

**Read first:**
- the ticket file (`.tickets/DAEO-2gc7.md`) and its card in `docs/plan/WAVE_2_WBS.md` §2;
- DEC-883, DEC-884 (item 4), DEC-889 (items 2 and 4), DEC-890, DEC-880 and DEC-899;
- W2-66's selection code and test map: `src/gov/close/select.py`, `governance/project/test-map.yaml`, and the close records' `evidence` blocks under `docs/close/`.

## Why you start now

- **Closes are the machine's bottleneck.** The queue of 2026-10-21 ran six closes on the same code, about 85 minutes each (DEC-883). On 2026-10-27, W2-66's scoped selection brought six closes down to 10 to 28 minutes each. But each close still ran its own rebuild, collection, record suites and `gov check` first, about 12 minutes per ticket, longer than the scoped close itself.
- **Your ticket shares that work:** queued closes on one head share one regression, a close on code that already passed reuses it, and a store built on the same code fingerprint is fresh.
- **The owner's cadence (DEC-933, DEC-936):** each judge improvement is re-pinned as soon as it merges and passes its checks. You and W2-71 make the third re-pin.

## The decisions for this run

- **Design first:** write `docs/research/W2-68-batched-close.md` before any code:
  - the batch's flow, step by step;
  - where each fingerprint is computed and recorded;
  - how reuse finds "the last fully passing run" (W2-66 already takes a base from committed full close records, `docs/close/*/CL-*.md` with `scope: full`, or `docs/close/nightly/*.json`): reuse that, don't build a second store of runs;
  - how a red batch is attributed;
  - what each step reads.
  
  The test designer and the reviewer read it.
- **Fingerprints:**
  - the code fingerprint leaves out exactly the test map's `record_only` paths (read, never written);
  - the path map counts as code (it is shared core, DEC-880): a change to it runs fresh;
  - a lexical or semantic index is fresh only if its record files' fingerprint matches too.
- **Fail closed everywhere:**
  - a run that failed, was cut, or lacks its JUnit XML is never reused;
  - a fingerprint that cannot be computed means a fresh run;
  - reused evidence states the reused run's skip count and names its run (fingerprint, commit, JUnit paths).
- **Tests first,** by a fresh independent test designer (launched sandboxed, `--effort xhigh`, a measured trial for FULL test designers, DEC-839; its brief must not set `TMPDIR`), in `tests/acceptance/W2-68/`:
  - one case per KPI line, in temporary repositories built from scratch: a batch of two tickets on one head; a reuse on the same code; a planted code change forcing a fresh run; a planted record-only commit running only the record-reading set; a red batch, with a red that passes alone not bisected, a red that fails alone attributed, and nothing closing on it; a skip carried in reused evidence;
  - W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later`, re-read against two fingerprints with a `Rewrite-Reason:` and no expectation lowered.
- **The engineer** (fresh, launched sandboxed, `--effort high`) works only in the ticket's allowed paths:
  - `command.py`: the calls and the record's lines only;
  - `repo.py`: the store-freshness check only;
  - `src/gov/store/**`: the fingerprints a rebuild records and the incremental record load only.
- **The trial (DEC-884 item 4),** measured on a fixture or dev-tier programme and written into the research note: the time per batch, reuse correct, a planted code change forcing a fresh run, a planted record-only commit running the set and nothing else, a red batch attributed with nothing closing on it.
- **Running beside you:**
  - W2-75 holds `tests/acceptance/W2-54/`;
  - W2-71 holds `src/gov/secrets/**` and `tests/unit/secrets_check/**`.
  
  Do not touch them. If your design needs a change there, return PACKAGES.
- **Verification:** in the close's form, under the lock, with the retention option and the disk gate first.
  - **The nightly (owner, DEC-933, DEC-936):** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` exists (from 02:00 most nights), you and your workers run no suite and no full run. Wait, and go on the moment it is gone. Every full run also waits for the verification lock.
  - **Known:** W2-54's green-here cases may time out under load in a plain full run (row W2-L429; W2-75 fixes the close's route); re-run them alone. W1-46's and W1-19's cases run in your serial phase.
  - Any other red is named with its cause.
- **Reviews:** two (DEC-413). A fresh FULL reviewer (brief A3 with `JUDGEMENT.md` word for word, `--effort max`) on the final head. The probe asks above all whether any path lets a close pass on a red run, another fingerprint's run, or a run on different code. Commit the probe record only when it passes.

## This run's order

1. The research note.
2. Tests first (the test designer), then **check red yourself.**
3. The engineer.
4. The trial.
5. Rebuild and verify in full.
6. Review 1. If it fails on a fail-open or lose-work finding an honest agent can hit: one test-design batch, one engineer, a full run, review 2 (the last).
7. **Return** DONE (probe passed; ready to merge, then re-pinned), or PACKAGES.

**Estimate:** about 300 lines (DEC-890), one to two days with the trial, the full runs and the reviews.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit). Split the engineer's work into batches that fit.

---
