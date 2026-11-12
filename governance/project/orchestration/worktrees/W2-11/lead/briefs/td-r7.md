# Brief: independent test designer, W2-11 (DAEO-k7hz) round 2, run r7, STANDARD, a kernel change (CAP-33)

Hand-written by the ticket lead (`gov context DAEO-k7hz --role independent-test-designer` refused: `BLOCKED: mandatory input 'DEC-1083' not found in the store`), from `template/governance/kernel/templates/role-test-designer.md` and the ticket. You revise acceptance cases the CTO's decisions name. Read the ticket file's last paragraph first (`/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-k7hz.md`, read-only): "Delegated (the CTO, DEC-1112 (3), 2026-11-11), round 2's run r6 packages".

## Step 0: the sandbox check, before any work (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed: stop and return.

## Who and where
- Role `independent-test-designer`, ticket `DAEO-k7hz`. Check `printenv GOV_ROLE GOV_TICKET` and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11-tests`, `w2/W2-11-tests`). Different: stop and say so. Work and commit only there.
- **The work order in parallel (DEC-959 item 7, DEC-963):** a product-spec worker edits W2-11's skills in the other worktree at the same time; you never read its work. **Policy 2 (c) (DEC-820 (c)):** never read this ticket's implementation: the files `git diff --name-only w2/integrate...HEAD` names outside `tests/acceptance/` (the skills, `templates/skill.md`, the CIT-P), in any worktree; drop unread any `gov retrieve` or search result under them and name it in your return (P-R1). Read the integrated code on `w2/integrate` (`git show w2/integrate:<path>`). **(d):** never read the hidden half of any evaluation set by which you are measured.
- Retrieval (DEC-963, DEC-836): the integration store only: `gov retrieve --root /home/usain/gov-os-worktrees/W2-00-store "<question>"`; **search again once** (DEC-1092 (1)) in your own, different words if a bundle does not answer, then answer from both or say "not found"; two searches in all; never one giant query (DEC-860); small code-graph queries (DEC-859).

## Facts of the interface you may rely on (the lead states them; you do not read the files)
- On `w2/W2-11` the orchestration and test-design skills both carry `version: "1.4.0"` and `metadata:\n  version: "1.4.0"` (every kernel skill carries `metadata.version` equal to `version`: the one carried repeat, decided P-b); discovery and retrieval carry 1.1.0 likewise. Integrate's orchestration and test-design are 1.2.0.
- test-design's read rule (DEC-820 (c), the designer works from the spec and KPIs, CAP-38.c) is in the section headed `## The work order in parallel`; another section is headed `## The README map` (its heading also holds "read"). The rule names "the integration branch", not a project branch name such as `w2/integrate` (a kernel skill names no project branch). test-design's description is integrate's, word for word.
- The orchestration skill's reads line bars the four DEC-820 refusals with a refusal word ("except"), and test-design's read rule cites CAP-38.c (product-spec is writing both now).
- No kernel skill declares `output` today (adopt aside: it has its own form).

## Do (revisions; `Rewrite-Reason:` on the commit; lower no other expectation)
1. **F1, `tests/acceptance/W2-11/test_w2_11_round2.py::test_every_write_step_lies_in_the_skills_output_class`** (P-W2-11-R6-1 (b)): check only the kernel skills that declare `output`; a skill without `output` is not a failure (five of the nine are version-line only in W2-11's paths, DEC-981). Keep the stray-write check for every skill that does declare it, and keep the planted cases showing the check (permission field, a step writing outside its class, a skill writing inside its class). Update the README's failure-1 row (cases, red reason) and the section that says "Each kernel skill but adopt declares `output`". Rewrite-Reason: DEC-1112 (3) P-W2-11-R6-1 (b).
2. **W2-128's pins** (P-W2-11-R6-2 (c)), `tests/acceptance/W2-128/test_w2_128_round2a.py` and `test_w2_128_round2b.py`:
   - the read-rule cases (`test_s11_test_design_read_rule_permits_integrate_and_forbids_only_this_tickets_implementation`, `test_s11_f4_test_design_read_rule_cites_cap_38c_not_cap_38b_or_dec_136`, and any other that selects test-design's section by the word "read"): find the read rule where it now stands (above), and accept the integration branch named generically (the placeholder) in place of the literal `w2/integrate`, keeping that it permits the integrated code and forbids only this ticket's implementation, and the CAP-38.c citation with no CAP-38.b or DEC-136 in it;
   - `test_s11_skill_version_is_one_minor_above_integrates[orchestration]` and `[test-design]`: a later ticket (W2-11) raises them again; hold what W2-128 meant (raised above integrate's base, a valid semver, equal in every place) without pinning 1.2.0;
   - the front-matter guards (`test_s11_guard_test_design_skill_changes_only_its_read_rule`, `test_s11_guard_orchestration_skill_changes_only_the_named_parts`): also allow `metadata.version` when it equals `version`; nothing else.
   - `test_s11_k4_guard_still_bars_the_held_out_contents` is met by the text; do not change it.
3. **W2-142's pins**, `tests/acceptance/W2-142/test_w2_142_unchanged.py` (`test_f1_the_retrieval_skill_is_the_reference_but_for_step_7_and_its_version`, `test_f1_the_discovery_skill_is_the_reference_but_for_line_55_s_added_sentence_and_its_version`): also allow a `metadata:` block holding only `version` equal to `version`; nothing else.
- Each revised file's README row (if its README maps it) says why, citing the decision. Rewrite-Reason for 2 and 3: DEC-866, DEC-981, DEC-1137.
- Run what you changed, single files only: `env PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m pytest <file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed` (DEC-732: this worktree's own `src/`, per command). On your branch (the head before product-spec's change) the read-rule, CAP-38.c and k4 cases may still be red: say which, and why; the rest of what you changed should pass. Never read the skills on any W2-11 branch to check.
- Write only `tests/acceptance/W2-11/`, `tests/acceptance/W2-128/`, `tests/acceptance/W2-142/`.

## Commit
`git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-866, DEC-1112, DEC-1137" --trailer "Rewrite-Reason: DEC-866, DEC-981, DEC-1137; DEC-1112 (3) P-W2-11-R6-1 (b), P-W2-11-R6-2 (c)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- <the paths>`. Check `test ! -e /home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks/pre-commit` first; never `--no-verify`; no amend, rebase, reset, push or merge.

## Rules
- Machine (DEC-898): your share 1 GB and 10,000 files and folders outside the tracked tree; no tree copies (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`); give `du -sh` / `du -s --inodes` of anything you made. Your sandbox may not write `/tmp/gov-os-lead-W2-11` or `.gov-runtime/scratch/`: use the sandbox's own temp and say so.
- Row W2-L423's rule (DEC-911): under `.gov-runtime/` commit hashes as 12 digits, never 40, and never the keywords of the secrets rule that takes a bare 40-hex string.
- Protected material (DEC-820): never read the held-out material's contents; never print a secret; never read or name the qualification oracle; never write in `~/gov-os-workbench`.
- Guard read refusals (DEC-849): take a refusal, never another spelling; count them in your return.
- Command forms: one simple command per Bash call; literal paths; no here-documents, backticks, `bash -c`, long inline `python3 -c` with braces. Never `pgrep`, `pkill`, `killall` or the Monitor tool.
- Never ask or notify the owner; install nothing; one role per ticket (DEC-995, DEC-996). A dispute with a decision: a package in your return, not a workaround.
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
