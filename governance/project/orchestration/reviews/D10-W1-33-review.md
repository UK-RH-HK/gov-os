# D-10's red-fix list: the review of W1-33's launcher cases under the gate and the lead check (W2-20, DAEO-r30l)

- Brief: `.gov-runtime/scratch/orchestrator/briefs/D10-W1-33-review.md`; branch `w2/W2-20-d10-tests` at `e66c69c45`; reviewer log `/home/usain/gov-os-worktrees/W2-20-d10-tests/.gov-runtime/scratch/lead/log/D10-W1-33-review.json`.
- verdict.py: READY (no blocking finding).

## Review record: W2-20 (`DAEO-r30l`), D-10 red fix of W1-33's launcher cases, revision `e66c69c45`

**Sandbox check (Step 0):**
- (a) The write to `/home/usain/gov-os-worktrees/.sandbox-trial-W2-20` was refused with `OSError: [Errno 30] Read-only file system`.
- (b) `git hash-object -w --stdin` returned `1ae28402a109` and `git update-index --refresh` exited 0. Passed.

**`ps` check:** `ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` showed nothing.

- **task:** an independent read-only review of `16f4958c5..e66c69c45` (tests only), KPI id `w1-33-launcher-gate`.
- **status:** DONE. The verdict is **pass**. There are three findings and none blocks: all are `Consequence: other`, and F3 is `scope: out`.
- **work_completed:**
  - Read the diff, W1-46's launch support, the launcher's lead and gate paths, `plan_check`, `main_root`, the gate's readings, DEC-1088 (5), W2-136's S9 (`DAEO-p3ln` line 37), W2-20's gate line (`DAEO-r30l` line 59), DEC-1111 and D10-REDS.
  - Ran the changed file, the whole W1-33 folder, and the folder with `--optin=lifted,breadth`.
- **files_changed:** none. The only write in a repository was Step 0's prescribed blob in the shared object store.
- **evidence:**
  - The revision is one commit on `16f4958c5`. `diff --stat` shows 4 files, all under `tests/acceptance/W1-33/`.
  - Scratch use was 20M and 3192 inodes under the sandbox's TMPDIR, removed afterwards. `git status --porcelain` is clean.
- **tests:** all runs used an empty HOME, `PYTHONPATH=<worktree>/src`, the heavy slot, `-m "not local_only" -k "not real and not green_here and not time_limit"` and `-p no:cacheprovider -o tmp_path_retention_policy=failed`.
  - **Changed file:** 17 collected, 15 passed, 2 deselected. Both rewritten ids passed: `[orchestrator-no ready list]` and `[orchestrator-a ready list without the ticket]`.
  - **Folder, default:** 111 passed, 1 skipped, 2 deselected. This matches the designer's figure.
  - **Folder, `--optin=lifted,breadth`:** 2 failed, 111 passed, 1 skipped. The two reds are the untouched lifted guard cases:
    - `test_the_auditor_writes_only_the_report_path_of_its_own_ticket`: the auditor's write on an engineer's ticket is let through (G-4 is off).
    - `test_an_install_asks_for_the_orchestrator_and_is_denied_to_every_other_role[orchestrator]`: the install is denied under DEC-953 item 2.
  - **What the exclusion left out in W1-33:** nothing. The 2 deselected cases are the opt-in lifted ones. The 1 skip is the rulesync comparison (`test_w1_33_agent_definitions.py:102`), because rulesync is not in my empty HOME.
- **discoveries:**
  - (1) W1-46's `test_only_the_four_worker_roles_are_launched[orchestrator]` (`tests/acceptance/W1-46/test_w1_46_sandbox_settings.py:162-166`) is not in this revision and I did not run it.
    - It accepts a refusal naming "role" or "orchestrator". Today's lead refusal names neither.
    - Its temp folder is named after the test (`test_only_the_four_worker_role0`), and that path appears in the "no approved ready list can be read at …" text. So it likely passes on its folder name, not its reason. This is from reading the code only.
  - (2) Of the "two DEC-1111 cases", DEC-1111 (1) names only W1-33's auditor case. The install `[orchestrator]` case is its lifted sibling, listed in D10-REDS §1 (opt-in list line 83). Only the label is loose.
  - (3) The planted gate, like W2-136's form, leaves `GOV_RESOURCES_EMBEDDING_CPU_NOW` unset. Each launch therefore samples the real embedding servers through `/proc`, read-only, with its history kept in the planted HOME (`src/gov/resources/machine.py:268-276`).
    - Because p95 is planted at 0, `max(0, p95 − now)` is 0 whatever that reading is, so the gate stays open. The fixture's "whatever the machine is doing" claim holds in practice.
- **risks:** none from this revision. F2 could hide only a regression where every lead is refused (fails closed), never one that lets a lead through (fails open).
- **lessons:** a refusal case that pins its reason by a word several faults share cannot show which fault fired. Pin each case to the word only its own fault says.
- **proposed_decisions:** none.
- **unresolved:** the Write tool was refused for a probe script in my TMPDIR (permission not granted). I took the refusal and did not route round it. The probe would have printed the launcher's refusal text and run controls. Code reading covers the same ground (check 1), so nothing depends on it.
- **recommended_next_action:**
  - Merge as READY.
  - F1 and F2 can ride along with the next W1-33 touch: fix the README counts, and assert "batch" in the second case.
  - File F3 and discovery (1) as rows.

### Answers to the checks

**1. No expectation lowered.**
- **Network profile:** the open gate hides nothing.
  - The launcher builds the worker's settings (`launcher.py:432`) before the gate runs (`launcher.py:445`).
  - `_run` changes only the filesystem and env blocks, never `sandbox.network`.
  - `result.settings()` still requires exactly one session and one `--settings` value, then `allowedDomains == []`.
  - The fixture's new body is `launch_support.launch` plus the gate variables. The env is the same `gov_environment(...)`, still built from scratch, so the operator's `GOV_PLAN_READY`, `GOV_ROLE` and `GOV_TICKET` never reach the launcher.
  - `plant_open_gate` is W2-136's `_plant_open_gate`, value for value (`test_w2_136_launch_check.py:103-143`). It returns the variables instead of using `monkeypatch`, because W1-46's runner passes only the variables it names.
  - Registry, start lock, config and samples all live under the planted HOME (`config.py:39-41`, `registry.py:31-32`).
- **Where the gate is planted:** in the `launch` fixture, which only these two functions use.
- **Row 2 cannot pass for the gate's reason:**
  - For a lead, `_admit_lead` runs first (`launcher.py:411-412`), before the gate (`:419`).
  - The gate's refusals ("the resource gate is shut…" / "…cannot be read…") contain neither "ready list" nor "batch". In `src/gov/launch`, only `plan_check.py:104` and `:106` say them.
  - So the case can pass only on the lead check's refusal: `no lead for ticket 'DAEO-zz91': … (DEC-1088 (5))` (`launcher.py:348`).
  - If the list held the ticket, the lead would be admitted and the open gate would let the stand-in start, so the case would go red. It is not vacuous.

**2. Row 2 against DEC-1088 (5) and S9.**
- The reading is right:
  - DEC-1088 (5)(a) (`DECISION_REGISTER.md:13686-13693`): `gov launch` refuses "a lead for a ticket that is not in the approved batch", and every refusal names the ticket.
  - S9: the refusal "names what it waits for (the ticket, the path) and starts no session".
- Both cases do what they claim:
  - The fixture ticket `DAEO-zz91` (W1-91) has no waits.
  - With no list, the refusal is "no approved ready list can be read" (fails closed).
  - The planted list (`W1-98 DAEO-zz90 …`) matches neither the id nor the WBS, so the refusal is "not in the approved ready list's batches".
  - `main_root` reads the planted copy, because the project's `.git` is a folder (`store.py:55-77`).
- **W1-33's KPI is properly superseded.** S3 (`DAEO-xog0.md:27-28`) speaks of launched *worker* sessions, and the network-profile row still tests that. "Not a worker" was a derived negative.
  - Among W1-33's five roles, none is still refused as "not a worker". Product-spec has been launched since DEC-386, and the orchestrator is now a lead.
  - The "not a worker role" refusal is still tested by W1-46's `[no-such-role]` case.
  - The supersession is recorded in the docstring, the README note and the `Rewrite-Reason` trailer.

**3. The DEC-1111 cases are untouched.** The diff changes neither the auditor case, nor the install case, nor the `guard` fixture. Both fail under the opt-in for their own guard reasons.

**4. Trailers and paths are present and correct:**
- `Task: DAEO-r30l`
- `Role: independent-test-designer`
- `Implements: DEC-1109, DEC-1088`
- `Rewrite-Reason: DEC-1088 (5): …`
- `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`

Only `tests/acceptance/W1-33/**` changed.

### Findings

**F1: the README's counts are one off.** The line reads "Cases: 111 in the full run, 0 in `breadth`, 3 in `lifted`" and the new note says "from 110 to 111" (`README.md:35`, `:113`). The real figures are 112 in the full run (111 passed and 1 skipped, in both the designer's run and mine) and 2 in `lifted`.
- The cause is older: DEC-1103 (2) moved `test_the_orchestrator_may_write_anywhere_else_in_the_repository` back into the gates (`tests/optin-lifted-guard.txt:81`), and the README was never updated. This revision re-states the stale baseline.
- No code reads the line.
- Ordinary work: yes, because anyone comparing the README with a run gets 112 against 111.
- Consequence: other. scope: in.

**F2: the second case cannot tell its own fault from the first.** Both cases pass on "ready list" (`LEAD_REFUSAL_WORDS = ("ready list", "batch")`).
- If a later change moved where the launcher reads the list (as W2-20 S21's main-tree rule just did), the "a ready list without the ticket" case would pass on "no approved ready list can be read" without testing its own condition.
- Asserting "batch" for that case pins it, since only the "not in the batches" refusal says it.
- Ordinary work: yes, because a change to the list's location is ordinary engineering.
- Consequence: other, because what it could hide refuses every lead (fails closed). scope: in.

**F3: `NOT_LAUNCHED` still holds the orchestrator.** The roster case `test_a_role_the_launcher_does_not_start_has_no_launched_session[orchestrator]` still says "The launcher starts engineer, test designer, auditor and research only (DEC-161)" (`test_w1_33_roster.py:53-56`).
- Since W2-136's S9, `gov launch orchestrator <ticket>` starts a lead on an approved ticket. The revision updated only the constant's comment.
- A roster entry that documents the lead launch would turn this case red.
- Ordinary work: yes, because the name and the docstring mislead a reader.
- Consequence: other. scope: out (a row; the roster case is not in this revision).

```verdict
{"kpis": [{"kpi": "w1-33-launcher-gate", "verdict": "pass", "findings": [{"id": "F1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F2", "scope": "in", "ordinary_work": "yes", "consequence": "other"}, {"id": "F3", "scope": "out", "ordinary_work": "yes", "consequence": "other"}]}]}
```
