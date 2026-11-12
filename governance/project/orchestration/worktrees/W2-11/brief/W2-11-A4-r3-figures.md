Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-11/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-11 (DAEO-k7hz): one product-spec pass on the CIT-P's figures (review row R3), before the owner reads it

You are a product-spec worker (Sonnet, high; class C3 ticket, product-spec on Sonnet by RUBRIC-2), launched in W2-11's worktree `/home/usain/gov-os-worktrees/W2-11`, branch `w2/W2-11`, head `58ac442d6820`. First calls: `printenv GOV_ROLE GOV_TICKET` (expect `product-spec`, `DAEO-k7hz`); `git -C /home/usain/gov-os-worktrees/W2-11 status --short` must be empty.

## The one change
Edit only `docs/changes/W2-11-CIT-P.md` so its figures describe the reviewed head `646850506819`, per row R3 of `docs/probes/DAEO-k7hz/CITP-REVIEW-r2.md` (read R3 whole):
- §7.2: 9,981 chars = 2,496 tokens (orchestration) and 5,671 = 1,418 (test-design), as measured (§7.1 already says 2,496);
- the front matter's `round2_head`: `646850506819` (not the pre-round-2 test commit `c96136eb62c8`);
- §7.1: the versions as 1.2.0 (integrate's, the real before) → 1.4.0 (1.3.0 never merged);
- §7.3 b: the head's accept (186 passed, 7 failed, 1 skipped; the 7 are the `.claude/` copy cases until the copies ACT), beside the pre-round-2 one;
- add one line: the lead's suite at the head, 4,646 tests, 13 failed (the 7 copy cases and 6 W2-96 unit cases on signals and timeouts, in files W2-11 does not touch).
Re-measure the two body sizes yourself (the skill files under `template/governance/kernel/skills/`) and use your measures if they differ, saying so. Change no other line, no other file. Commit alone: `git commit -m "W2-11 (DAEO-k7hz): the CIT-P's figures describe the reviewed head (review row R3)" --trailer "Task: DAEO-k7hz" --trailer "Role: product-spec" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- docs/changes/W2-11-CIT-P.md`.

## Rules
Write nothing else in any tree. Refused twice for the same call: stop and say so; never work around a refusal. The owner's decisions are recorded by the orchestrator's decision-record commits; never put `Role: owner` or `Decided-by:` on a commit of yours. Under `.gov-runtime/`, commit hashes as 12 digits. Use `gov retrieve` only if needed.

## Return
First twelve labelled lines in order: task, status, work_completed, files_changed, evidence (the commit, your two measures), tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action.
