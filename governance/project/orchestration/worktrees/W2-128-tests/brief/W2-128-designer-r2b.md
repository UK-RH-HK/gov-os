Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-128-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-128 round 2b — the independent test designer's brief (DAEO-t8mp)

You are a fresh independent test designer for **W2-128** (`.tickets/DAEO-t8mp.md`). Read the body's **"Round 2b"**
in full, then the review it answers: `governance/project/orchestration/reviews/w2-128-r2a.md` (F1 to F4) and its
F5 (the link notice). Round 2a's cases are `tests/acceptance/W2-128/test_w2_128_round2a.py` (yours to revise,
TESTS-READY `f3e2a55accd4`). Sources by id in `docs/DECISION_REGISTER.md`: DEC-511 and DEC-1057 (R-6), DEC-254,
DEC-963, DEC-820, DEC-1052. Also `docs/contract/contract.yaml`'s CAP-38.b and CAP-38.c.

## What the cases must show (map new cases to `S11`, the checkpoint case to `S14`)
- **F1:** `template/.rulesync/subagents/orchestrator.md`'s body names no retired `brief-*.md` text as content, the
  same as the kernel role's line. Extend round 2a's F6 case to that copy.
- **F2, the orchestration skill** (`template/governance/kernel/skills/orchestration/SKILL.md`):
  - no line requires a `gov checkpoint` record per round on DEC-511's authority (lifted by DEC-1057, R-6);
  - the one-writer-per-tree line cites DEC-963, not DEC-254;
  - no line forbids reading another session's folders beyond DEC-820's four refusals.
- **F3, strengthen round 2a's two cases:**
  - the test-design "permits" half: a sentence that permits reading names `w2/integrate` or the integrated code, and
    no sentence keeps a general "does not read … source code / implementation files" bar;
  - K-4's line: the four DEC-820 refusals are named (secrets, the held-out contents, the counterpart's work on the
    same ticket, the hidden half), not only the citation.
- **F4:** the test-design skill's read rule cites CAP-38.c, and neither CAP-38.b nor DEC-136, for the designer
  working from the spec and its KPIs.
- **The link notice:** `template/governance/kernel/templates/checkpoint.md`'s front-matter `task:` is empty (its
  comment says to fill it), and `gov links` run on a tree holding the template gives no `UNKNOWN_ID` for it.
- **Round 2a's guards and versions, revised (DEC-866: a revision of your own cases, with `Rewrite-Reason:`):**
  - the "nothing else changes" guards allow F2's and F4's lines too;
  - the version case expects one more minor above round 2a's: 1.2.0 for orchestration and test-design. Pin its
    baseline to the integrate commit you merged from (state it), as round 2a pinned `61231e61`.
- Say for each case whether it is red on integrate for the right reason, or a green guard.

## Where you work, rules, return
- Your worktree `/home/usain/gov-os-worktrees/W2-128-tests`, branch `w2/W2-128-tests`, with integrate merged by the
  CTO (`a2576c6f`). Write only `tests/acceptance/W2-128/`. Update the README's map.
- **Never read this ticket's implementation:** never open `/home/usain/gov-os-worktrees/W2-128` or `w2/W2-128`. Keep
  every search inside your worktree. You may read integrate's text and code (DEC-963).
- Run only W2-128's cases, with an empty `HOME` (`PYTHONUSERBASE=/home/usain/.local` if pytest is not found):
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-128-tests/src python3 -m pytest tests/acceptance/W2-128 -q -p no:cacheprovider -m "not local_only" -k "not real and not green_here and not time_limit"`.
- No GPU, model, network or installs. Never open `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`, `memory-verdict`
  or `memory-verdict-2` folder. DEC-1080: one simple command per Bash call. No merge inside the sandbox. Search again
  once (DEC-1092 (1)) if a search does not answer.
- **Commit** on `w2/W2-128-tests`, only `tests/acceptance/W2-128/`, with
  `--trailer "Task: DAEO-t8mp" --trailer "Implements: DEC-963, DEC-820, DEC-1052" --trailer "Role: independent-test-designer" --trailer "Rewrite-Reason: round 2a's guards and version case follow round 2b's stated changes (DEC-866, DEC-1112 (3))" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- A small round: about 8 to 12 cases.
- **Return** (your final message, in full): the twelve labelled fields of `EMG-common.md` (sandbox and `ps` checks
  first), the cases added and revised (red or green on integrate, why), the run's counts and `TESTS-READY <hash12>`.
