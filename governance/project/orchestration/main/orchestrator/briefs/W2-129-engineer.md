# W2-129 — the engineer's brief (DAEO-q7lk)

You are the engineer for **W2-129** (`.tickets/DAEO-q7lk.md`): `gov links`, one cheap, incremental, read-only
link-integrity check. It finds every unlinked or contradicted record and names the role that fixes it; it is a notice,
never a gate. The owner wants it built, tested and reviewed before re-pin window 4 (DEC-1087 (4)).
- Read the ticket in full first, with its notes ("TESTS-READY" and "the designer's points settled").
- Read the design: `governance/project/orchestration/packages/LIFT-1/LINK-INTEGRITY.md` §4.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-129`, branch `w2/W2-129`: `w2/integrate` with the designer's
  cases merged in (`5d5fe8abb1cb`).
- **Your paths:** `src/gov/links/**`, `tests/unit/links/**`, `docs/research/W2-129-links.md`.
- **You never read `tests/acceptance/W2-129/`** (DEC-957, DEC-1056). Build to the KPI lines, the ticket's notes and the
  design, and run those cases only through `gov accept W2-129`.
- **The interface the tests assume** (from the designer's return, so you build to it):
  - the command `gov links [--since <rev> | --all] [--json] [--propose-marks | --propose-sources]`;
  - the first line `gov links: N new since <rev>, M standing (...)`;
  - one line per new finding with `code`, `ids`, `path:line`, `role` and `fix`, in LINK-INTEGRITY §4.4's form, with
    ` | ` between fields and `(text)` marking a free-text finding;
  - exit 0, 1 or 2 through the child exit code;
  - the mark at `.gov-runtime/links/mark` holding HEAD's sha, and nothing else written.
  - If a detail is not stated in the KPI or §4.4, choose the simplest form, and state it in your research record.
- **What you reuse:**
  - the loader's `register_statements` (`src/gov/store/loader.py`), imported, never copied;
  - W2-55's `gov.decisions.propagation`;
  - the store's id grammar.
- **Command registration:** see how the other commands are registered with `gov.cli.main`. If registering needs a line
  outside your paths, stop and say so in your return. Do not route round it.

## Tests and evidence
- **Unit tests** go in `tests/unit/links/`, on planted repositories. No model, no network, no GPU.
- **The research record** `docs/research/W2-129-links.md`:
  - each finding code's form;
  - any reading you chose;
  - the first `--all` run's counts by code and role on this repository's main tree (run it read-only; it writes only
    its mark, under your worktree's `.gov-runtime/links/`).
- **Every run** goes through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept`:** run it with `HOME=/home/usain` (these cases start no model). `gov accept` strips `PYTHON*`, so an
  empty HOME cannot find pytest. Report its counts.

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **DEC-1080:**
  - read with the Read and Grep tools;
  - one simple command per Bash call;
  - no `cd … &&` chains and no `git -C`;
  - one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-129` with
  `--trailer "Task: DAEO-q7lk" --trailer "Implements: DEC-1073" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include:
- the diff's size;
- the unit tests;
- `gov accept`'s counts;
- the `--all` run's counts and time on the main tree.
