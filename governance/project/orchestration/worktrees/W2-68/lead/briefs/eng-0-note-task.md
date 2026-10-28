You are a fresh engineer (brief A2 of the Wave 2 prompt). Ticket: DAEO-2gc7 (W2-68), "Batched closes, reuse on the same code, and two fingerprints", profile FULL. You work in this worktree only: /home/usain/gov-os-worktrees/W2-68, branch w2/W2-68.

## Your task: the design note, before any code (batch 0)

Write `docs/research/W2-68-batched-close.md`, the ticket's design note, which the test designer and the reviewer read before any code is written. Write no code and no test: this batch is the note only.

- **Its content is the lead's design**, in `/home/usain/gov-os-worktrees/W2-68/.gov-runtime/scratch/lead/design-draft.md`. Keep every decision in it (the fingerprints and what they leave out, the path map and test map as code, "cannot be computed" means fresh, the batch's steps, the reuse conditions, the red batch's attribution, the store rows and checks, the tables of what is recorded where and what each step reads, the failure KPIs and where each is refused, the residuals, and section 10 for the trial, left for its figures).
- **Check it against the code** as it stands on `w2/integrate` (`src/gov/close/select.py`, `evidence.py`, `nightly.py`, `command.py`, `repo.py`, `src/gov/store/loader.py`, `src/gov/rebuild/command.py`, `src/gov/retrieval/lexical.py` and `semantic.py`, `governance/project/test-map.yaml` and its schema) and the sources (`.tickets/DAEO-2gc7.md`, its card in `docs/plan/WAVE_2_WBS.md` §2, and in `docs/DECISION_REGISTER.md` DEC-883, DEC-884 item 4, DEC-889 items 2 and 4, DEC-890, DEC-880, DEC-899). Where a statement of the draft about existing code is wrong, correct the statement and say so in the note's last section, "Corrections to the lead's draft". Where you think a design decision itself is wrong or cannot be built inside the ticket's allowed paths, do not change it: keep it, and return it as a decision package (proposed_decisions) with your recommendation and confidence.
- **Form:** a Markdown file with a short header (title, ticket, sources, status "design, before implementation"), plain sentences, no code beyond names and command lines. About 150 to 250 lines.
- **Write only** `docs/research/W2-68-batched-close.md` (and your own notes under `.gov-runtime/scratch/`). Commit it alone: `git commit -m "W2-68: the design note, before any code (DEC-883, DEC-889, DEC-890)" --trailer "Task: DAEO-2gc7" --trailer "Role: engineer" --trailer "Implements: DEC-883, DEC-889, DEC-890" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- docs/research/W2-68-batched-close.md`.
- **No test runs** are needed; run none.
- **Your scratch share:** 1 GB and 50,000 files and folders.
- **Time:** about 45 minutes.

