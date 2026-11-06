Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-133/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-133 — the engineer's brief (DAEO-k4wm)

You are the engineer for **W2-133** (`.tickets/DAEO-k4wm.md`): a narrowed or gap-starting register item carries its
own entry's id. It is W2-131's follow-up, in re-pin window 4 (DEC-1083). Read the ticket in full first. Its notes
give both causes with file and line.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-133`, branch `w2/W2-133`. It is `w2/integrate` (W2-131's fix
  included) with the designer's acceptance cases merged in.
- **Your paths** (the ticket's `allowed_paths`):
  - `src/gov/decisions/register.py`;
  - `src/gov/retrieval/retrieve.py`;
  - `tests/unit/decisions/test_w2_133*`;
  - `tests/unit/retrieval/test_w2_133*`;
  - `docs/changes/W2-133-evidence.md`.
- **You never read `tests/acceptance/W2-133/`** (DEC-957, DEC-1056). Build to the KPI lines and the ticket's notes.
  You run the acceptance cases only through `gov accept W2-133`.

## The change (from the ticket)
1. **`register.leave_out`:** when it narrows an expanded register item to its own chunk, recompute the kept item's
   `id`, `entry`, `status`, `in_force` and `also` from the narrowed chunk's own lines. Use the entry holding its first
   line, by `authority.register_entries_of`, as W2-131 does. Never keep the parent's.
2. **`retrieve.py`'s register label:** an item whose first line lies in the preface or a gap carries its chunk id,
   not the first entry it touches further down. One inside an entry carries that entry.
3. **Nothing else in a bundle changes** (S3).

## Your tests and evidence
- **Unit tests** go in the two `test_w2_133*` paths, on a planted register, as W2-131's
  `tests/unit/retrieval/test_w2_131_register_ids.py` does. No GPU and no model.
- **The evidence record** `docs/changes/W2-133-evidence.md`: one row per KPI line, S1 to S3. S4 is the CTO's.
- **Every test run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **A launched session's empty HOME** needs the user site-packages linked in for `gov accept` (W2-131's engineer's
  discovery). Link only `~/.local/lib/python3.12/site-packages` into your TMPDIR's HOME.
- **When your unit tests pass,** run `gov accept W2-133` through the heavy slot and report its counts.

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
- **Commit** on `w2/W2-133` with
  `--trailer "Task: DAEO-k4wm" --trailer "Implements: DEC-1083" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include:
- the diff's size;
- the unit tests' names and outcome;
- `gov accept W2-133`'s counts.
