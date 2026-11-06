# W2-134 — the engineer's brief (DAEO-m4rq)

You are the engineer for **W2-134** (`.tickets/DAEO-m4rq.md`). The memory measure:
- re-anchors line-cited gold in memory for the commit it measures, and never writes the sets root (S1 to S4,
  W2-61h S8);
- fixes W2-61h S7's source families (S5: a floor and word boundaries for family hits; S6: the families in force named
  on the first line).

Read the ticket in full first. Its notes hold the interface the acceptance cases assume, the settled points and the
TESTS-READY note.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-134`, branch `w2/W2-134`. It holds W2-61h S7's code
  (`ab18f6f5`, not yet merged into integrate), the designer's cases and `w2/integrate`.
- **Your paths** (the ticket's `allowed_paths`): `src/gov/retrieval/measure.py`, `tests/unit/retrieval/test_w2_134*`,
  `docs/changes/W2-134-evidence.md`.
- **You never read `tests/acceptance/W2-134/`** (DEC-957, DEC-1056). Build to the KPI lines and the ticket's notes,
  and run those cases only through `gov accept W2-134`.
- **What you may read:**
  - S7's own unit tests, `tests/unit/retrieval/test_w2_61h_families*`;
  - the S7 review, `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/reviews/w2-61h-s7.md`,
    for F1's and F3's probes;
  - the re-anchoring pattern, `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/drafts/d4b/repin_gold.py`.

## The change (from the ticket)
1. **S1 to S3:** before scoring, find each line-cited gold block again in the measured commit.
   - Read the block with git at the source's own commit, else the question's.
   - Find it once at the measured root, as `repin_gold.py` does.
   - Score against the lines found, in the overlap rule and in S7's family text, live and under `--kept`.
   - A block found nowhere, or more than once, is unresolved: named by question id and `entry <n>` only, and counted
     as not found.
   - A source with no commit keeps its stated lines.
   - Nothing is ever written to the sets root or a label file.
2. **S5:** a family hit needs the normalised gold to be at least 4 words and 24 characters, held on word boundaries.
   A leading `DEC-nnnn:` must never be dropped so that `DEC-1078: X` matches `DEC-1079: X`.
3. **S6:** the first line of the text output is `families: <name> (<n> members), …`, or `families: none`. With
   `--json`, standard output stays one JSON document.
4. **S4:** everything else is as today.

## Your tests and evidence
- **Unit tests** go in `tests/unit/retrieval/test_w2_134*`, on a planted git repository and a planted sets root. No GPU
  and no model.
- **The evidence record** `docs/changes/W2-134-evidence.md`: one row per KPI line, S1 to S6.
- **Every test run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`,
  with `PYTHONUSERBASE=/home/usain/.local` so pytest loads under the launched session's empty HOME.
- **When your unit tests pass:**
  - run `gov accept W2-134` and report its counts;
  - run S7's acceptance file, `tests/acceptance/W2-61h/test_w2_61h_families.py`, which must still pass;
  - run S7's unit tests and `tests/unit/retrieval/test_measure.py`.
  - Do not run `test_w2_61h_hidden_form.py`: it reads `~/gov-os-runs`.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder. No measure on real sets.
- **No GPU job.**
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-134` with
  `--trailer "Task: DAEO-m4rq" --trailer "Implements: DEC-1085" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include:
- the diff's size;
- the unit tests' names and outcome;
- `gov accept W2-134`'s counts, and the S7 file's counts.
