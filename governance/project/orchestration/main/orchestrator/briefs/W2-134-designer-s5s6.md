# W2-134 — the independent test designer's second brief: S5 and S6 (DAEO-m4rq)

You are the independent test designer for **W2-134** (`.tickets/DAEO-m4rq.md`). Your first pass wrote S1 to S4
(`tests/acceptance/W2-134/`, `7227c5e8`). The ticket has since gained **S5 and S6**: W2-61h S7's review findings F1 and
F3, which ride on this ticket. Read the ticket in full again, and the review record
`/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-61h-s7.md` for F1's and
F3's probe cases (its findings only; it names no hidden content).

## Where you work
- The same worktree, `/home/usain/gov-os-worktrees/W2-134-tests`, branch `w2/W2-134-tests`, with integrate merged in.
- You write only `tests/acceptance/W2-134/`: new cases for S5 and S6, and the README's map.
- The guard denies your role the ticket's own code (`measure.py`); take the interface from your first pass and from
  the W2-61h S7 cases (`tests/acceptance/W2-61h/`), as before.

## What the cases must show
- **S5:** a family hit needs the gold span's normalised text to be at least 4 words and 24 characters, matched on word
  boundaries.
  - The review's probes, each with a family declared and the gold in a member of it:
    - `- id: CAP-1` must not hit text holding only `CAP-10`;
    - `DEC-1078: X` must not hit `DEC-1079: X`;
    - `floor: 85` must not hit text holding `1985`.
  - A gold below the floor counts only in its own path, as with no family.
  - A gold just above the floor, in a member, still hits.
- **S6:** the output begins with one line naming the families in force, each with its member count, or none.
  - Cases with families declared and with none.
  - Under `--kept` too.
- The failure line "A family hit on text that holds the gold only inside a longer token, or on a gold below the
  floor" is covered by S5's cases.
- Each case is **red on your branch for the right reason**, or a green guard; say which. S1 to S4's cases stay as they
  are, except where S6's first line changes S4's word-for-word output. If it does, update S4's expected text to
  start with that line and say so.

## Rules
- No GPU, no model, no measure on real sets. Never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any
  `hidden`, `memory-verdict` or `memory-verdict-2` folder. Your cases plant their own sets.
- Run the folder through the heavy slot (`EMG-common.md`), with `PYTHONUSERBASE=/home/usain/.local` as in your first
  pass.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Commit** on `w2/W2-134-tests` with
  `git commit -m "..." --trailer "Task: DAEO-m4rq" --trailer "Implements: DEC-1085" --trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`, with the new case list (node id, KPI line, red or green, why), the
commit, the whole folder's counts, and any interface the engineer must add (S6's line format).
