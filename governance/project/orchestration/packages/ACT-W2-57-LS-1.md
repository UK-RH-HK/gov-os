# ACT-W2-57-LS-1 — Six of W2-57's `load_sensitive` removals, and W2-57's two `Implements:` corrections (DEC-931, DEC-927)

From: the W2 orchestrator, 2026-10-28. Your operator runs it (DEC-928 item 3: an owner commit of a patch). The patch is `.gov-runtime/scratch/orchestrator/drafts/ACT-W2-57-LS-1.patch` (it stays in scratch, not in the tree).

## What it changes (one file, `governance/project/path-map.yaml`: 6 insertions, 24 deletions)

**Removes six `load_sensitive` entries, each whose fix is in force in a close under the current pin (DEC-931 item 1, its reading accepted by DEC-932 item 1):**

| Entry | Where its fix lives |
|---|---|
| `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestRegisteredFamilyCheck::test_gov_check_is_green_on_a_clean_generated_project` | `src/gov/adapters/portability.py` (rulesync limit 10 to 25 s); the test runs `gov` from `src/` |
| `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestSettingsHandEdit::test_key_added_by_hand_is_found_and_named[top-level-env]` | the same |
| `tests/acceptance/W1-38/test_w1_38_rulesync.py::TestUnsourcedFile::test_file_of_another_owner_is_not_a_finding[.claude/worktrees/by-hand/.claude/agents/by-hand.md]` | the same |
| `tests/acceptance/W1-07/test_w1_07_envelope.py::test_every_command_returns_the_envelope[doctor]` | `src/gov/doctor/command.py` (probe budgets); the test runs `gov` from `src/` |
| `tests/acceptance/W1-30/test_w1_30_r13_probe_findings.py::test_after_a_run_cut_at_the_time_limit_no_process_of_it_lives_or_writes_into_the_project` | the test itself (its limit 5 to 30 s) |
| `tests/unit/close/test_follow_up.py::test_at_the_time_limit_the_processes_a_run_started_are_ended_with_it` | no fix: not reproduced in 6 runs, and green in the clone run below |

The other 24 (W1-46's 23 live-session cases, W1-19's warm p95) stay until the second re-pin pins W2-57's nightly route: ACT-W2-57-LS-2.

**Adds two `accepted_history` entries in DEC-927's form:** `6be837bbbe41` and `d0bfeb6afd95`, W2-57's run 1 lead commits with `Implements: engineer`, each with the ids it should have named (W2-57's sources). DEC-927 names both (register commit `f06ccf4b`).

## Validated (DEC-895, DEC-925 item 2, DEC-931 item 2)

- **The full run in the close's form, with the current pin, on a clone with the patch applied** (`tools/act_clone_run.sh`; head `55d9bee6fdf8`; the pin's interpreter, `PYTHONPATH` the clone's `src/`, the pin's serial-only plugin with its 63 entries, `-n auto --dist load --timeout=900 --timeout_method=signal`, retention `failed`; 2026-10-28 00:52 to 03:41, waiting for the verification lock between phases):
  - parallel: 16,431 passed, 32 skipped, 0 failed;
  - serial: 180 passed, 0 failed;
  - verdict: green. All six removed entries' tests passed in the run itself, with no re-run.
- **The pinned judge's readers** (`tools/validate_entry.py`): both corrections pass; the placeholder scan of the lines added finds nothing.
- **The pinned ratchet** reads the list after the patch: 24 entries counted, 0 refused.
- **Gate (e)** on W2-57 with the corrections applied: 0 lacking, 0 unresolved. **Product traceability** (pinned): exit 0, no findings.
- **The record checks** and the 69 tests that read these lists pass.
- **Since the clone run,** `w2/integrate` merged W2-07 round 2 and W2-57's re-probe; neither changes the path map, and the patch still applies (`git apply --check`).

## The commands

```
cd /home/usain/Dynamic-Agentic-Engineering-OS
git status --short
git apply .gov-runtime/scratch/orchestrator/drafts/ACT-W2-57-LS-1.patch
git diff --stat -- governance/project/path-map.yaml
git commit -m "Owner decision DEC-931: six load_sensitive entries whose fix is in force removed; W2-57's two Implements corrections (DEC-927)" --trailer "Task: decision-record" --trailer "Implements: DEC-931, DEC-927" --trailer "Role: owner" -- governance/project/path-map.yaml
git log -1 --format='%h %s'
```

## What to see

- `git status --short` prints nothing.
- `git diff --stat` shows `governance/project/path-map.yaml | 30 ++++++------------------------`.
- `git log -1` shows the new commit.

## Rollback

`git revert <the new commit>` (an owner commit, `Role: owner`).

## Then

Tell me the commit's sha. I re-run gate (b) and the record checks.
