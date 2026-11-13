# Review, round 1: ACT-OPERATOR-ROUNDS-1 and ACT-MEMORY-AUDIT-INSTALL-1

The reviewer's return, unchanged (independent-auditor, claude -p, launch_worker.sh, DAEO-r30l, 2026-11-11 15:55 UTC; the return carries no REVIEW_MD block).

Both packages pass. Package 1 is **READY WITH FIXES**: no finding blocks, but there is one small fail-open gap to close and its rehearsal log is missing two results. Package 2 is **READY**, with two notes that need no change.

**Sandbox check (step 0):** (a) the write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-r30l` was refused (read-only file system, exit 1) and no file exists. (b) `git hash-object -w --stdin` and `git update-index --refresh` both worked (exit 0).
**ps check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` shows nothing.

task: Independent read-only audit, round 1, of ACT-OPERATOR-ROUNDS-1 (DEC-1131 (3)) and ACT-MEMORY-AUDIT-INSTALL-1 (DEC-1129 (2)), for orchestrator DAEO-sdxk (GOV_TICKET DAEO-r30l).
status: Done. Package 1: READY WITH FIXES. Package 2: READY.
work_completed: I read both packages, every script and diff, the live install copies and the launcher, and the launch script's parser and approval check (stage 10). I reran both rehearsals under my own TMPDIR. For package 1 I also ran the 13 new cases on the old and new code, ran the CTO's verdict tests, and rescanned the historical records.
files_changed: None in the repository, the live drafts or the install. Everything I wrote is under `/tmp/gov-launch-independent-auditor-5ll2qmj8/claude-1000/aud-r30l/`. Both drafts' `rehearsal.log` files still hash as built (`2a1509344782`, `c8841eb1cce8`), and the live install's `APPROVED` is still `b4a15c8f3b7c`.
evidence: Package 1, rerun in my clone of `w2/integrate` at `b2a33d7b` with HOME planted: `failures: 0`, 414 passed, 2 deselected, `APPROVED` after apply `ece74a76…`. Package 2, rerun on the same head with a planted sets root: 57 checks passed, 0 failures. My log matches the package's line for line except the clone head and commit ids.
tests: Only what the rehearsals run, plus two checks for package 1's claims. The 13 new cases: 10 fail and 3 pass on the old code, 13 pass on the new. The CTO's `test_verdict.py`: 3 failed and 5 passed on the old `verdict.py`, 8 passed on the new. The rehearsal's own pytest run used no `local_only`/real-model exclusion flags; the operator tests start no model.
discoveries: My reruns needed three environment changes, none to the packages' own files:
- Package 1's first rerun failed one step only because the planted HOME hid the user-installed pytest. I reran with `PYTHONUSERBASE=/home/usain/.local`.
- In package 1's clone, `heavy_slot.sh` was replaced by a stub that just runs the command.
- Package 2's `rehearse.sh` hard-codes its work folder and log inside the live drafts folder. I ran a copy whose only changes point that folder at my TMPDIR and pass TMPDIR through `env -i`.
risks: Package 1's count can drop earlier builds of an ACT if their `manifest.json` lacks a matching `act` field (P1-F1). Today all 13 bundles carry it.
lessons: Package 2's `rehearse.sh` cannot be rerun anywhere but the live drafts folder without editing it. A `HERE`/`BASE` override would let an auditor rerun it unchanged.
proposed_decisions: None.
unresolved: The live list under the sets root was not opened, as instructed. Only the owner's `apply.sh check` reads it.
recommended_next_action: Package 1: fix P1-F1 and add the two missing results to `rehearsal.log` (P1-F5), then send it to the owner. Package 2: send it to the owner as built.

## Package 1: ACT-OPERATOR-ROUNDS-1

How it stands against the checks:
- **(a) The diffs:** they do exactly what the package says and nothing more. The two test-pin edits change only the pinned hash. The starting files match the live repository and the install.
- **(b) Apply order:** `launch.lock` is taken before the backup and held to the end, and `APPROVED` is written last. Every operator run happens inside a launch that holds that lock, so nothing runs half-changed.
- **(c) Rehearsal:** reproduced. Of the 13 new cases, 10 fail on the old code; the other 3 are no-regression guards, as the package itself says.
- **(d) Rollback:** byte for byte, with the install files back at mode 0444.
- **(e) Historical records:** the three new "not READY" readings are right:
  - PR-DAEO-jpr0, success-7: KPI 7 is not in that tree (its F6).
  - w2-128-r1, F7: it cites an expired decision. W2-128's later records r2a and r2b still read READY.
  - w2-153-r1, S5: "not yet met", and the reviewer wrote "not ready to merge yet". The later records still read READY.

Findings:
- **P1-F1 (check f, fails open, not ordinary work; the one code fix):** `act_rounds` counts an earlier build only if its `manifest.json` names the same `act`. No gate requires or checks that field: `validate_manifest` asks only for touched, files and checks, and G1 never compares it. A build whose manifest leaves `act` out, or names another id, is silently dropped, which brings back the reset DEC-1131 (3) closes. Today all 13 bundles under scratch carry `act` equal to their folder id. Fix: refuse at G1 a manifest whose `act` is not the request's id, or drop the manifest condition (the folder name is the operator's own, built from the request).
- **P1-F2 (check d, does not block):** undo checks the install backup against the expected hashes before writing, but the repository backup only against its own `SHA256SUMS`. A backup altered together with its `SHA256SUMS` gets written into the main tree, and only the final state check catches it. Fix: check each repository backup file against its expected hash before any write.
- **P1-F3 (check b/d, does not block):** after a partial apply, the error messages say "run `bash apply.sh undo`", but undo refuses every state except fully applied. Section 5 already says to send the output to the CTO if undo refuses; the message should name the hand restore from `backup/`.
- **P1-F4 (check b, wording only):** section 4 says "the cron's launcher waits". It doesn't: it checks `APPROVED` first, then tries the lock without waiting. A launch during the swap either refuses "APPROVED mismatch" or exits "busy", so it is still safe.
- **P1-F5 (check c, log gap):** `rehearsal.log` has no lines for two results section 6 reports: the 13 cases on the old code, and the CTO's `test_verdict.py` passing 8. I reproduced both; the rehearsal should run them.
- **P1-F6 (row, a residual to state):** the count is per exact id. The CTO's ids carry a number (ACT-CLAUDE-COPIES-1/-2/-3, ACT-EFFORT-HIGH-1/-2), so a rebuild filed under the next number starts at zero. The code also counts verdict blocks, not rounds as DEC-1131 (2) defines them, so a re-review of a blocking-only fix counts as a round; that is stricter and fails closed. Residual 2 should say both; the hand ledger (DEC-1131 (1)) covers them.
- **P1-F7 (row):** the scan's 54 records are 57 on today's head; the same three change reading.

**Verdict: READY WITH FIXES:** P1-F1 and P1-F5. P1-F2, -F3 and -F4 are optional wording or hardening; P1-F6 and -F7 are text rows.

## Package 2: ACT-MEMORY-AUDIT-INSTALL-1

How it stands against the checks:
- **(a) The lists:** `APPROVED.before` is byte-identical to ACT-W2-149-INSTALL-1's reviewed `APPROVED.after` (`6b923cb4d552…`), the list that DECIDED-NOT-DONE row 75 records as applied. `APPROVED.after` is that list plus four comment lines and exactly three lines of the form `<sha256> brief <kind> <path>`. The hashes are DEC-1129 (2)'s, the kinds exist in `kinds.yaml`, and the briefs' budgets and timeouts are within its caps.
- **(b) Brief bytes:** the drafts equal the briefs at `8c18fa300`, which equal DEC-1129 (2)'s hashes. `apply.sh` checks them before writing and again after.
- **(c) Rehearsal:** each brief passes under its own kind (dry, exit 0). A changed byte is refused with exit 10, whether the launch gives the old hash or the new one. A wrong kind and a changed list line are also refused with exit 10.
- **(d) Refusal and mode:** apply refuses unless the live list is exactly `6b923cb4d552…`, and writes the list 0400 through a temp file and rename. The rehearsal refuses a list with one byte added.
- **(e) Rollback:** undo checks the backup against the expected before hash and restores the list byte for byte.
- **Order:** the briefs are written first, but uncommitted files are invisible to a launch, and the list goes last, so the order is safe.

Findings:
- **P2-F1 (check f, row, already there before this ACT and disclosed as residual 4):** in my rerun, all 4 memory walls still hold `packages/MEMORY-AUDIT-1/`, including the three brief copies. Keeping a session from reading them rests on its brief's instruction alone, which is consistent with the briefs' "this brief only" line. Also, the writer's 300-path sample is drawn from the tree less `tree-exclude.txt`, so those 6 tracked paths can turn up in its `selection.json`; by my estimate about a 38% chance per audit, out of 3,955 tracked paths. The brief says to skip a path that fits no category, but it also lists "would need to read something §4 forbids" as a reason to stop. Suggestion: take the `tree-exclude.txt` change before the first live cycle. This ACT neither adds nor removes any exposure; its new copies are excluded from every wall.
- **P2-F2 (check d/e, row):** if apply fails between writing the briefs and renaming the list, it exits with only `mv`'s own error. The state is then "other", which undo refuses, and a stray `.APPROVED.act-memaudit-install.<pid>` file may stay in `indep-walls/`. It fails closed (the list is unchanged), but the steps should name the hand cleanup.

**Verdict: READY.**
