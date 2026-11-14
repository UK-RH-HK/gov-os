You are a fresh independent test designer. Ticket: DAEO-cv58 (W2-60a, "The role, its skills and its model and effort loaded at launch; the launch record"), profile FULL. Worktree `/home/usain/gov-os-worktrees/W2-60a-tests`, branch `w2/W2-60a-tests`. One job: the older launch suites' fixture projects predate this ticket and are refused before they reach what they test; fix their fixtures, never an assertion (P-8 (a), the CTO's decision, recorded in the ticket; P-3's form, DEC-1156 (7)).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-cv58','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` must WORK.
If (a) wrote the file or (b) failed, stop and return. Then `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-cv58`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-60a-tests`, `w2/W2-60a-tests`). If anything differs, stop and say so.

## Standing rules

- Foreground only; your session ends with your last message.
- Your files (nothing else; never code under `src/`): `tests/acceptance/W1-28/w1_28_launch_support.py`, `tests/acceptance/W1-32/w1_32_launch_support.py`, `tests/acceptance/W1-46/w1_46_support.py`, `tests/acceptance/W1-50/w1_50_freeze_support.py`, `tests/acceptance/W2-116/w2_116_support.py`, `tests/acceptance/W2-136/w2_136_support.py`, `tests/acceptance/W2-20/w2_20_support.py`, `tests/acceptance/W2-56/w2_56_support.py`, `tests/acceptance/W2-56/w2_56_sandbox_support.py`, `tests/unit/resources/test_w2_20_unit_launch.py`, `tests/unit/resources/test_w2_20_round3.py`, `tests/unit/resources/conftest.py`. If the ticket's paths as the guard reads them do not hold one of these yet, the guard's refusal is the answer: stop and report it (refused twice for the same call: stop; never another form).
- Every pytest through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`, with your session's own `$TMPDIR` as TMPDIR, `HOME=/home/usain/gov-os-worktrees/W2-60a/.gov-runtime/scratch/empty-home`, `PYTHONUSERBASE=/home/usain/.local`, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-60a-tests/src`, `-p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`. Write the output to a file under `$TMPDIR` and read its tail (a slot wait is otherwise silent). A resource gate's refusal is a wait.
- Write with the Write and Edit tools and absolute paths. No `git merge`, `checkout`, `reset`, `stash`, `clean`, rebase or push. Commit your files only (one commit, or one per folder): `git commit -m "<subject>" --trailer "Task: DAEO-cv58" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-826, DEC-832, DEC-839" --trailer "Rewrite-Reason: <why, one line>" -- <your paths>`. Commit hashes in 12 digits. Time budget about 90 minutes.

## What the launcher now refuses (the decided behaviour)

`gov launch <role> <ticket>` (worker roles: engineer, independent-test-designer, independent-auditor, research, product-spec) refuses:
1. a project without `template/governance/kernel/roles/<role>.md` (or `governance/kernel/roles/<role>.md` in an adopted layout) carrying exactly one `- **Version:** <x.y.z>` line and exactly one `- **Launch default:** model <id>, effort <e>` line (`<id>` a full `claude-…` id; effort low, medium, high, xhigh or max): "the role file … cannot be read";
2. a role file whose `- **Skills:** a, b` line names a skill that is not at `.claude/skills/<name>/SKILL.md` with a version (top-level `version`, or `metadata: version:`, or for the vendored Superpowers skills the manifest `template/governance/kernel/skills/superpowers/vendored.yaml`): "names the skill '…', which is not at …";
3. a model given after `--` that is not the role file's (naming both).
It hands one `--append-system-prompt-file <TMPDIR>/role-<role>.md` (the role text, a blank line, the template's bytes) last, after the caller's arguments. Leads and the orchestrator need no role file.

## The failing cases (the lead's scoped run at 97f208456bdb; this tree is now at 71cdfd994, with W2-42a merged from integrate)

- No role file (113): W2-56 (`test_w2_56_sandbox_block.py` 50, `session_daemon` 10, `todays_refusals` 5, `placeholders` 3, `r5_lead_store` 2, `session_reranker` 2, `start_together` 2), W2-20 (`test_w2_20_launch.py` 13, `stale_samples` 1), W2-116 `test_w2_116_launch.py` 6, W2-136 `test_w2_136_launch_check.py` 1, `tests/unit/resources/test_w2_20_unit_launch.py` 16 and `test_w2_20_round3.py` 4.
- Kernel role files copied but not the skills they name (113): W1-46 (all its launch files, 77), W1-28 (`launch_product_spec` 21, `launch_temp_folder` 8), W1-32 (`test_w1_32_launch.py` 11, `added_cases` 1), W1-50 `test_w1_50_freeze_launcher.py` 6.

Fix each in its support module (or the unit file's own fixture): plant a role file per role launched, or, where the fixture copies the kernel's role files, copy the `.claude/skills/<name>/` folders they name as well (with the vendored manifest for the three Superpowers skills), or plant a fixture role file without a `- **Skills:**` line, whichever keeps the case's point. Where a case passes `--model <m>` after `--`, the planted role's default line names that model. Keep each case's point; delete or skip none.

## Verify, then return

Run each of the nine folders/files above (each its own run, the form above). For every red left: file:line, assertion, message, and whether it is your fixture (fix it) or the launcher's behaviour (report it; do not touch code). Return the twelve fields (task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), each a labelled line: the sandbox check, the counts per folder, every red named, the guard refusals met (count), and your commits' hashes and trailers.
