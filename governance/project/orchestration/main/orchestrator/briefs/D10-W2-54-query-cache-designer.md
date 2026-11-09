# D-10's red-fix list: W2-54's one-answer case compares two folders' answers whole (W2-138, DAEO-rmhj)

You are a fresh **independent test designer**, launched under W2-138's ticket (`.tickets/DAEO-rmhj.md`). Its S1 made
this case red. The CTO found it while it re-ran W2-54 for D-10's list tonight. DEC-1109 (2) asks that the list be
ready before D-10's full run.

## The red (the CTO's run at integrate `b0bbd373f`: 1 failed, 8 passed in the file)
- **The case:** `tests/acceptance/W2-54/test_w2_54_query_cache.py::test_one_ticket_gets_one_packet_hash_whatever_the_cache_s_state`.
- **The failure:** "cold, after another question: one question, two answers (the first in a new store)". The two
  canonical answers are equal up to their last characters: `…one_packe0/reference"}}` against `…one_packe0/p"}}`.
- **The cause:**
  - The case builds a reference project (`tmp_path / "reference"`) and the case's project (`tmp_path / "p"`) alike,
    then compares `gov retrieve --json`'s whole `result` from each with `S.canonical`.
  - Since W2-138's S1 (`dcda27011`, 2026-11-07, DEC-1090 (3)), every result carries
    `result.store = {"commit": …, "root": <the store folder>}`.
  - The two roots differ by design, so the answers can never be equal. The commits are equal here, since both
    projects are built alike.

## The task
1. Revise the case so that its comparison of the two answers leaves out exactly what S1 makes folder-specific,
   `result.store.root`, and nothing else:
   - keep `store.commit` in the comparison, if it is equal by construction (say whether it is);
   - keep the packet-hash assertions and every other assertion as they are.
   - Lower no other expectation.
2. Sweep `tests/acceptance/` for other cases that compare whole `gov retrieve --json` results (or `gov context`
   packets) built in two different folders:
   - **W2-54's other files:** fix them the same way, in this commit, if they are red for the same cause;
   - **other suites:** name each with its file and line; change none.
   - Read only; run what you name.
3. Do not edit W2-54's README (another branch edits it tonight). Put the reason in the case's docstring, as its
   earlier revisions do ("Rewrite-Reason: …").
4. Every commit carries `--trailer "Rewrite-Reason: DEC-1090 (3): W2-138 S1 puts the store's folder in every gov retrieve result, so two folders' answers differ by result.store.root by design"`.

## Where you work
- Your worktree: `/home/usain/gov-os-worktrees/W2-138-d10-tests`, branch `w2/W2-138-d10-tests`. It is integrate at
  `f9facd7f6`, plus the CTO's ticket commit `389867fe6`.
- Write only `tests/acceptance/W2-54/test_w2_54_query_cache.py`, and any other `tests/acceptance/W2-54/` test file
  red for this cause.
- Do not read W2-138's implementation (`src/gov/retrieve/command.py` and the files its ticket names): DEC-820 (c).
  S1's text in the ticket file tells you the field.
- Run through the heavy slot (`EMG-common.md`), with:
  - `PYTHONPATH=/home/usain/gov-os-worktrees/W2-138-d10-tests/src` and `TMPDIR` a folder of your own under the
    sandbox's TMPDIR;
  - `python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -o tmp_path_retention_policy=failed`.
  - Report the counts before and after. The `green_here` and `time_limit` cases need a store in the tree they run
    in: name them if red, do not fix them.

## Rules
- `EMG-common.md` holds. The hidden-half rule: never open anything under `~/gov-os-eval/` or `~/gov-os-runs/`, or
  any `hidden`, `memory-verdict` or `memory-verdict-2` folder. No GPU, no model, no installs, never the full suite.
- Commit on `w2/W2-138-d10-tests` only, with `--trailer "Task: DAEO-rmhj" --trailer "Implements: DEC-1109, DEC-1090"`
  `--trailer "Role: independent-test-designer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`
  plus the Rewrite-Reason trailer. Never merge, push, amend or rebase.
- Estimate: 25 minutes. Return the twelve fields, short:
  - the case before and after;
  - the sweep's list;
  - the counts;
  - the head commit.
