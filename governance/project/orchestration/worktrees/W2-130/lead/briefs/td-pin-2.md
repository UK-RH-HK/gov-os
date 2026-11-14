# Brief: independent test designer, W2-130 (DAEO-q8cl): pin run, keep the mapped case names

You are a fresh independent test designer (role independent-test-designer), ticket DAEO-q8cl (W2-130), profile
STANDARD, class C2. Headless: only your last message is read. You work in the tests worktree and make ONE commit there.
Every pytest goes through heavy_slot.sh (below). Your scratch is your sandbox's own `$TMPDIR`.

## Where things are
| what | path |
|---|---|
| your worktree / branch | /home/usain/gov-os-worktrees/W2-130-tests / w2/W2-130-tests (head 35b6ac6ba) |
| the previous test designer's commit (read its body first) | `git show 35b6ac6bacae9aad1c5277e0cb5ac2b9f8973cd0` |
| the README maps `gov accept` reads | `tests/acceptance/W2-130/README.md` (S8 rows near lines 217-223), `tests/acceptance/W2-175/README.md` (lines 150-165) |
| how the runner reads a map | `src/gov/accept/runner.py` lines 66-230 |

## What is wrong with 35b6ac6ba
The previous test designer revised four cases to the CTO's decided behaviour (W2-130 S8's two cases run `gov links`
at the record's `counts-after.measured_at` instead of HEAD; W2-175 S7 hashes each template at W2-175's landing
61cae50dc instead of the working tree). The behaviour is right; keep it. But, as the lead's brief asked, it renamed
the cases, and added one new case (the landing-ancestor case). The README maps name the cases by their old node ids,
and `gov accept` cannot collect a mapped item it does not find (and the W2-175 README is outside this ticket's paths).

## What you do
1. Restore the original function names, so every README map item collects again:
   - `test_s8_gov_links_at_head_gives_the_after_counts`
   - `test_s8_left_holds_d_5_d_6_and_d_9_by_path_and_role_as_gov_links_finds_them_at_head`
   - `test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head` (parametrised over `t.SEVEN`, ids unchanged)
   Keep the new behaviour. Put a docstring on each saying what it now reads, and that the name is kept because the
   README map names it (DEC-1156 (7) pin run).
2. Add no case that the README maps do not name: fold the landing-ancestor assertion of the new case into
   `test_s7_record_sha256_of_each_template_is_its_sha256_at_the_head` (or into the support helper it calls), and
   remove the separate case. Check against `runner.py` whether an unmapped case would be refused or ignored, and say
   which in your return.
3. Leave every other line of 35b6ac6ba as it is, unless you find it wrong; then say so.
4. Show that no case lost its point again, briefly: in a scratch copy under `$TMPDIR`, plant one wrong count in the
   W2-130 record's `counts-after` and one wrong sha256 in the W2-175 record's role-lead row; each restored-name case
   fails, naming the disagreement.
5. Run both folders through heavy_slot.sh:
   `env PYTHONUSERBASE=/home/usain/.local HOME=<an empty folder under $TMPDIR> PYTHONPATH=/home/usain/gov-os-worktrees/W2-130-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <folder> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   on `tests/acceptance/W2-130` and `tests/acceptance/W2-175`. Known and outside this brief: one red,
   `test_w2_130_sources.py::test_s4_every_unlinked_id_on_an_open_or_in_progress_ticket_at_head_is_listed_with_its_dec_1123_2_form`
   (three UNLINKED_ID left by the CTO's ce8ae4353); do not touch it; report every other red.
   Then run `--collect-only -q` on both folders and confirm every item the two README maps name for the changed files
   collects.

Your paths: `tests/acceptance/W2-130/test_w2_130_record.py`, `tests/acceptance/W2-175/test_w2_175_record.py`,
`tests/acceptance/W2-175/w2_175_support.py`. No record, README, ticket or other file changes. No merge, no
`gov retrieve`, no `gov context` in the sandbox. A resource gate's refusal is a wait.

## Commit (one commit, your paths only, trailers in ONE final paragraph, no blank line inside it)
Message in a file under `$TMPDIR`; `git -C /home/usain/gov-os-worktrees/W2-130-tests commit -F <file> -- <changed paths>`.
Subject: `W2-130 (DAEO-q8cl) tests: pin run: the mapped case names kept (README maps), the landing-ancestor check folded into S7's case`.
Body: what changed, the planted-value failures, the runner's handling of an unmapped case. Final paragraph exactly:
```
Task: DAEO-q8cl
Role: independent-test-designer
Implements: DEC-1073, DEC-1010
Rewrite-Reason: DEC-1156 (7), DEC-1164 (18) (W2-130 pin run)
Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
```

## Return (your last message): the twelve fields, each a labelled line ("none" where nothing)
task: / status: / work_completed: / files_changed: / evidence: (the commit hash in full; both folders' pytest counts;
the collect-only check; the planted-value failures) / tests: / discoveries: / risks: / lessons: / proposed_decisions: /
unresolved: / recommended_next_action:
Report step 0's sandbox check first.

## Searching and refusals
Read and Grep, git show/log; search once, then once more in other words; answer from what you read with path and line,
or say "not found". Never open the evaluation sets' root, held-out material or any hidden or memory-verdict folder.
Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around a refusal.
