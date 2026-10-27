You are the ticket lead for ticket `DAEO-2azm` (`W2-74`, "The settings regeneration's test revisions: the docs/source cases retired, W1-49's sandbox gov, W2-69's case name"), profile LITE, a test-revision ticket, working only in the worktree `/home/usain/gov-os-worktrees/W2-74` on branch `w2/W2-74`.

**This is run 1.** `git rev-parse --short=12 HEAD` must show `a42e899b56fb`, and `git status --short` must show nothing. Anything else: stop and return PACKAGES naming it. Read the ticket file (`.tickets/DAEO-2azm.md`), its card in `docs/plan/WAVE_2_WBS.md` §2, the package `governance/project/orchestration/packages/P-REPIN-R1.md` and DEC-925 first.

## Why you start now

- **Every close is refused.** The first re-pin's settings regeneration (DEC-922 Part B) left base reds:
  - six cases enforce the two `docs/source` deny rules it dropped (P-I1-2);
  - W1-49's `test_without_tk_the_block_says_so_and_holds_the_rest[not on PATH]` runs the new lifecycle hook line (DEC-917) in a sandbox with no gov, so the hook ends with 1.
  W2-70's close (2026-10-26) was refused on them, and the queue waits for you.
- **W2-69's case name.** One case in `tests/acceptance/W2-69/test_w2_69_word_internal_fragments.py` holds a keyword of row W2-L423's rule in its own test id. So every run's JUnit XML under `.gov-runtime/` holds it, and the orchestrator's early warning reads those files.

## The decisions for this run (owner, DEC-925 item 1)

- **A fresh independent test designer** (launched sandboxed, `--effort high`; its brief must not set `TMPDIR`) makes three revisions. Each carries a `Rewrite-Reason:` and is described in its README:
  1. **Retire** W1-01's `test_docs_source_deny_rules_survive_the_change` (its four cases) and W1-47's `test_the_other_deny_rules_are_in_place[Read(./docs/source/**)]` and `[Edit(./docs/source/**)]`. The reason: the `docs/source` folder left the tree on 2026-10-01, and P-I1-2 (DEC-899) dropped its deny rules in DEC-922's regeneration (`Rewrite-Reason: DEC-925 item 1, P-I1-2`). Every other deny rule these files check stays checked.
  2. **Revise** W1-49's `[not on PATH]` case so that its sandbox has a gov (for example a link at the sandbox HOME's `.local/bin/gov` to the pinned one), so only tk is missing. Its assertions stay as they are (`Rewrite-Reason: DEC-917`).
  3. **Rename** the W2-69 case whose test id holds the keyword (its function name or parametrize id), so that no test id holds one. Its input and assertions stay the same; a keyword in its input is written in parts (`Rewrite-Reason: DEC-911`).
- **Your checks** (a script file under `.gov-runtime/scratch/lead/`; never `python3 -c` with braces, DEC-409):
  - the four revised files pass, run alone;
  - `pytest --collect-only -q` over `tests` shows no test id with either keyword. Use `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/keyword_warn.py` on a file holding the collection, and print paths only, never the keyword.
- **Verification:** the full run in the close's form, under the lock, with the retention option and the disk gate first.
  - **Known:** W1-19's warm-query case is on `load_sensitive`; W2-54's green-here case may time out under load (row W2-L429; re-run it alone).
  - The six `docs/source` reds and W1-49's red are gone. W1-06's is fixed on `w2/integrate` (`1c3d4dff`), and your base holds it.
  - Any other red is named with its cause.
- **No review (LITE).**

## This run's order

1. The test designer.
2. Your checks.
3. Rebuild and verify in full.
4. **Return** DONE (it merges at once, and the queue restarts with W2-70), or PACKAGES.

**Estimate:** about 30 lines, about 2 hours with the full run.

**Time:** each worker gets a budget of about 90 minutes (the Bash tool's two-hour limit).

---
