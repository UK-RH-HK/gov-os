# Brief: independent test designer (repair), W2-11 (DAEO-k7hz) round 2, run r7, STANDARD, a kernel change (CAP-33)

Hand-written by the ticket lead (`gov context` refused: `BLOCKED: mandatory input 'DEC-1083' not found in the store`), from `role-test-designer.md`. A fresh session: you get the failing output and the lead's ruling only. The CTO's decision P-W2-11-R6-2 (c) (the ticket file's last paragraph, `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`, read-only): W2-11's designer revises W2-128's pins that W2-11's legitimate change cannot meet by text, lowering nothing else.

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- Role `independent-test-designer`, ticket `DAEO-k7hz`. Check `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11-tests`, `w2/W2-11-tests`). Different: stop and say so. Work and commit only there.
- **Policy 2 (c) (DEC-820 (c)):** never read this ticket's implementation: the files `git diff --name-only w2/integrate...HEAD` names outside `tests/acceptance/` (the skills, `templates/skill.md`, the CIT-P), in any worktree; drop unread any retrieval or search result under them and name it in your return (P-R1). Run cases against the implementation only with `--tb=no` (assertion diffs print its text). Read the integrated code on `w2/integrate` (`git show w2/integrate:<path>`). **(d):** never read the hidden half of any evaluation set by which you are measured.
- Retrieval (DEC-963, DEC-836): the integration store only: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"`; **search again once** (DEC-1092 (1)) in your own, different words if a bundle does not answer, then answer from both or say "not found"; two searches in all; never one giant query (DEC-860); small code-graph queries (DEC-859).

## The red and the ruling
```
tests/acceptance/W2-128/test_w2_128_round2a.py::test_s11_guard_test_design_skill_changes_only_its_read_rule
AssertionError: the test-design skill's sections changed
  At index 1 diff: 'The work order in parallel' != 'Read restriction'
  Left contains 5 more items, first extra item: "Red against the ticket's base"
```
W2-11's ticket lines S1, S7, S10 and S15 (DEC-951, DEC-889 item 11 c, DEC-959, DEC-963, DEC-983) restructure the test-design skill's sections; the text cannot meet this section-list pin. **The lead's ruling (your option (a) of run r7's P-W2-11-R7-1, read as part of the CTO's (c) "pins"):** this guard's section-list half checks W2-128's own change: read "now" for that half at W2-128's merge commit on integrate (found by git from history, not a hash written by hand if avoidable), so it keeps holding W2-128's change to its read rule and stops pinning later tickets' sections. Only test-design's guard: the orchestration guard is met by text (product-spec puts its heading back now); do not change it. Keep every other half of the test-design guard as it is (front matter: version and `metadata.version` only). Update W2-128's README row for it. `Rewrite-Reason: DEC-866, DEC-981, DEC-1137; DEC-1112 (3) P-W2-11-R6-2 (c)`. If the merge commit cannot be found reliably from git in a test (shallow clone, a later re-merge), say so and propose the alternative, keeping the guard live.
- Run it with `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m pytest /home/usain/gov-os-worktrees/W2-11-tests/tests/acceptance/W2-128/test_w2_128_round2a.py -q -p no:cacheprovider --tb=no -o tmp_path_retention_policy=failed` (DEC-732: this worktree's own `src/`, per command), and show the guard still fails for a planted change of W2-128's own sections, in a temporary repository or a planted text.
- Write only `tests/acceptance/W2-128/`.

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-866, DEC-1112, DEC-1137" --trailer "Rewrite-Reason: DEC-866, DEC-981, DEC-1137; DEC-1112 (3) P-W2-11-R6-2 (c)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the paths>`. Check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` first; never `--no-verify`; no amend, rebase, reset, push or merge.

## Rules
- Machine (DEC-898): your share 1 GB and 10,000 files and folders outside the tracked tree; no tree copies (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository); give `du -sh` / `du -s --inodes` of anything you made; use the sandbox's own temp.
- Row W2-L423's rule (DEC-911): under `.gov-runtime/` commit hashes as 12 digits, never 40, and never the keywords of the secrets rule that takes a bare 40-hex string.
- Protected material (DEC-820): never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- Guard read refusals (DEC-849): take a refusal, never another spelling; count them in your return.
- Command forms: one simple command per Bash call; literal paths; no here-documents, backticks, `bash -c`, long inline `python3 -c` with braces. Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- Never ask or notify the owner; install nothing; one role per ticket (DEC-995, DEC-996).
- **Refused twice for the same call: stop and say so; no third try** (AR-6). Never work around a refusal: report it.
- On an authentication or access error (401, 403, "Failed to authenticate", "access grant"): stop, return status `AUTH_REQUIRED`.
- Keep your output short.

## Return (your last message; nothing else is read)
The twelve fields first, each a labelled line, any payload after them; refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | AUTH_REQUIRED, and one line of why>
work_completed: <what was done>
files_changed: <each path, or "none">
evidence: <commits with their trailers, logs, command outputs that show it>
tests: <each suite run, with its counts, or "none run">
discoveries: <what you found that was not known, or "none">
risks: <what could go wrong with what was done, or "none">
lessons: <what the next worker should know, or "none">
proposed_decisions: <each package, with your recommendation and confidence, or "none">
unresolved: <what is still open, or "none">
recommended_next_action: <one line>
```
After the twelve fields: the sandbox check's result; whether you used `gov retrieve` and any result under the ticket's paths you dropped; `guard_refusals:` lines or `none`; `brief_gaps:` lines or `none`.
