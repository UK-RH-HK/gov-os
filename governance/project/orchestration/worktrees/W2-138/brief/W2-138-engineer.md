Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-138/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-138 — the engineer's brief (DAEO-rmhj)

You are the engineer for **W2-138** (`.tickets/DAEO-rmhj.md`): every search result names the store's commit and folder,
the store is resolved once per search, `CONTINUATION_INVALID` names both commits, and the retrieval skill gains the
line-hash line (DEC-1090 (3)). Read the ticket in full first, with its "designer's points settled" section.

## Where you work
- **Your worktree:** `/home/usain/gov-os-worktrees/W2-138`, branch `w2/W2-138`: `w2/integrate` (`b741707e`) with the
  designer's cases merged in (`999b1211`).
- **Your paths:** `src/gov/retrieve/command.py`, `src/gov/retrieval/retrieve.py`, `src/gov/retrieval/validate.py`,
  `src/gov/cli/main.py` (the text form's `store:` line only), `template/governance/kernel/skills/retrieval/SKILL.md`
  (step 5's one line), `tests/unit/retrieve/test_w2_138*`, `tests/unit/retrieval/test_w2_138*`,
  `docs/changes/W2-138-evidence.md`.
- **You never read `tests/acceptance/W2-138/`** (DEC-957, DEC-1056). Run those cases only through `gov accept W2-138`.
  Its README's interface notes are given to you here instead:
  - `result.store = {"commit": <full commit>, "root": <folder>}`; the commit is the store's own fingerprint `head`
    (the commit it was built at), not the folder's HEAD now;
  - the text form's first line `store: <commit, 12 digits> (<folder>)`;
  - one folder for every facet of a search, the link resolved once (W2-116's R2-F1);
  - the continuation token carries its store's commit; `CONTINUATION_INVALID` names the token's commit and the store's
    commit now (full or 12 digits, in `message` or `details`); a token from before this change is refused as today,
    with "made before W2-138" in its message;
  - each item's `sha256` stays the hash of exactly its lines at that commit (lines end after their LF, a CRLF keeps
    both bytes, the last line as it is, both ends inclusive, a cut item hashed on its full lines);
  - step 5 of the retrieval skill: compare each item's sha256 with the same lines in your own tree; if they differ,
    read `git show <commit>:<path>`; never cite the store's line numbers as your tree's.

## Tests and evidence
- **Unit tests** in `tests/unit/retrieve/test_w2_138*` or `tests/unit/retrieval/test_w2_138*`, on planted stores. No
  GPU, no model.
- **The evidence record** `docs/changes/W2-138-evidence.md`: one row per KPI line S1-S5.
- **Every run** goes through
  `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh <command>`.
- **`gov accept` drops `PYTHON*` variables.** Use a scratch HOME whose `.local` links to `/home/usain/.local`.
- **When your unit tests pass:** run `python3 -m gov.cli.main accept W2-138 --root <worktree>` and report its counts;
  then `tests/unit/retrieval tests/unit/retrieve` and `tests/acceptance/W2-116 tests/acceptance/W2-32 tests/acceptance/W2-133`
  with `-m "not local_only" -k "not real and not green_here and not time_limit"`, and list every red with its cause;
  and the skills check (`python3 -m gov.cli.main check --family skills --root <worktree>` or the structural pass's
  skills family).

## Rules
- **The hidden-half rule:** never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder.
- **No GPU job; no `gov retrieve` on the real repository.**
- **DEC-1080:** read with the Read and Grep tools; one simple command per Bash call; no `cd … &&` chains and no
  `git -C`; one line before any command that will ask for permission.
- **Do not merge `w2/integrate` yourself.**
- **Commit** on `w2/W2-138` with
  `--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1090" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.

## Return
The twelve labelled fields of `EMG-common.md`. Put the sandbox check and the `ps` check first. Include the diff's size,
the unit tests' names and outcome, `gov accept`'s counts, and the regression run's counts with every red named.
