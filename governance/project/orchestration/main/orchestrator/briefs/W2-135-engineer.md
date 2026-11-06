# W2-135 — the engineer's brief (DAEO-c4pb)

You are the engineer for **W2-135** (`.tickets/DAEO-c4pb.md`): a bundle item over 4,000 characters is sent as its first
4,000, marked `cut: {"chars": <full length>, "sent": 4000}`, its lines cited unchanged. It is a guard against one-line
files (DEC-1086 B). Read the ticket in full first.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-135`, branch `w2/W2-135`: `w2/integrate` (`e3355def`, W2-32's
  S11 included) with the designer's cases merged in (`ee54d3ca`).
- **Your paths:** `src/gov/retrieval/retrieve.py`, `tests/unit/retrieval/test_w2_135*`,
  `docs/changes/W2-135-evidence.md`.
- **You never read `tests/acceptance/W2-135/`** (DEC-957, DEC-1056). Run those cases only through `gov accept W2-135`.

## The change (from the ticket and the designer's interface notes)
- In `retrieve()`'s inner `item()`, where an evidence item's `text` is set: text over 4,000 characters is sent as its
  first 4,000 **characters** (not bytes), with `cut: {"chars": len(full text), "sent": 4000}`. `chars` is the length of
  the text the item carries today, its final newline included.
- The pieces of an expanded parent are items too, so they are cut the same way.
- `path`, `start_line`, `end_line`, `id`, `chunk_id` and `sha256` stay those of the full span. The budget's `used`
  stays counted on the full text, as today. Text at or under 4,000 is untouched, with no `cut` key.
- Nothing else changes: the order, the batches, the expansions, the left-out spans, the repeats, the gaps, the
  continuation, and the reranker's input.

## Tests and evidence
- **Unit tests** go in `tests/unit/retrieval/test_w2_135*`, on a planted repository. No GPU, no model.
- **The evidence record:** one row per KPI line, S1 to S3.
- **Every run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept` drops `PYTHON*` variables.** Use a scratch HOME whose `.local/lib` links to `/home/usain/.local/lib`,
  as the designer did.
- **When your unit tests pass:**
  - run `python3 -m gov.cli.main accept W2-135 --root <worktree>` and report its counts;
  - run `tests/unit/retrieval` and `tests/acceptance/W2-32` with `-m "not local_only" -k "not real and not green_here and not time_limit"`.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job.**
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-135` with
  `--trailer "Task: DAEO-c4pb" --trailer "Implements: DEC-1086" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include:
- the diff's size;
- the unit tests' names and outcome;
- `gov accept`'s counts;
- the regression run's counts.
