# W2-131 — the engineer's brief (DAEO-r8vq)

You are the engineer for **W2-131** (`.tickets/DAEO-r8vq.md`): a register chunk in a bundle carries its own entry's
id, not DEC-999. It is a priority fix in re-pin window 4 (DEC-1082 (2)). Read the ticket in full first. Its notes
give the cause, with file and line, and the pattern to copy.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-131`, branch `w2/W2-131`. It is `w2/integrate` with the
  designer's acceptance cases merged in (`a75a2704`), and integrate merged again for the evidence path.
- **Your paths** (the ticket's `allowed_paths`):
  - `src/gov/retrieval/retrieve.py`;
  - `tests/unit/retrieval/test_w2_131*`;
  - `docs/changes/W2-131-evidence.md`.
- **You never read `tests/acceptance/W2-131/`** (DEC-957, DEC-1056). Build to the KPI lines and the ticket's notes.
  You run the acceptance cases only through `gov accept W2-131`.

## The change (from the ticket)
1. **In `retrieve()`'s inner `item()`:** a register item's `id` is the entry that holds its first line (on integrate
   the item already has W2-92 S9's `entry` key, so `id` follows it). With no entry, in the preface or between entries,
   it is the chunk id. A parent expansion carries its first entry's id. Copy `supplementary.py:95`'s pattern
   (`id = entry['id'] if entry else chunk_id`).
2. **In `_graph()`:** `record_of` leaves out records that carry a span (the register's entries, as `supplementary.py`
   does), so no single entry stands for the register's path. Check DEC-424's ahead move still works.
3. **Nothing else changes in a bundle:** the evidence set, its order, the batches, the budget, the gaps and the
   continuation (S3).

## Your tests and evidence
- **Unit tests** in `tests/unit/retrieval/test_w2_131*.py`, on a planted repository and store built as
  `tests/unit/retrieval/test_w2_87_register.py` builds them. No GPU and no model: the lexical route or the fixtures'
  stand-in embedder.
- **The evidence record** `docs/changes/W2-131-evidence.md`: one row per KPI line, S1 to S3, with the test that shows
  it. S4 is the CTO's, after the re-pin.
- **Every test run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **When your unit tests pass,** run `gov accept W2-131` through the heavy slot, and report its counts.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job:** no reranker, no measure, no real-model run, no `gov retrieve` on the real repository.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.** Ask the CTO in your return.
- **Commit** on `w2/W2-131` with
  `--trailer "Task: DAEO-r8vq" --trailer "Implements: DEC-1082" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first, as
`EMG-d4b-launched.md` says. Include:
- the diff's size;
- the unit tests' names and outcome;
- `gov accept W2-131`'s counts.
