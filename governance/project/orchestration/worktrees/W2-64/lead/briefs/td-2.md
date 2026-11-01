You are a fresh independent test designer (MR-3). Ticket: DAEO-0uhh (W2-64, "the record validator through check-jsonschema; `docs/imported/` out of the schema check"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-64` on branch `w2/W2-64`.

**Your job (the owner's decision DEC-954, answer (a) to package P-W2-64-1, under DEC-906):** the record check `core-schema` now validates every record through the pinned check-jsonschema 0.38.2 against the kernel's real schemas, where before a small subset validator let much through. About 203 earlier test cases now fail because **their fixtures are records the real schemas refuse**, or because their environment has no check-jsonschema on `PATH`. You correct those fixtures and helpers so that the tests again judge what they were written to judge, **lowering no expectation**. You do not change what any test asserts about the product, except where an assertion names a finding code or form that the owner's decision itself changes (listed below).

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0uhh','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (name any file you made outside this worktree; never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0uhh`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-64` and `w2/W2-64`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commits exist.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag, no stash.
- **Policy 2 (DEC-820):** reads are open: the whole repository, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: **you never read this ticket's implementation** — the files `git diff --name-only w2/integrate...HEAD` names, other than tests: today `src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json`, `tests/unit/check/test_schema_shapes.py`, `tests/unit/check/test_schema_validator.py` (and the checkpoint records under `docs/checkpoints/DAEO-0uhh/`). You learn what the check refuses from **running** it and reading its findings (each names the record, the schema file, the place and the validator's message), and from the kernel schemas other than `close.schema.json` under `template/governance/kernel/schemas/` (above all `common.schema.json` and `ticket.schema.json`), which are not this ticket's implementation. You may read `close.schema.json` as it stands on `w2/integrate` (`git show w2/integrate:template/governance/kernel/schemas/close.schema.json`), never this branch's; (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside your paths (below).
- **Read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened. Take the refusal, never look for another form, search named folders instead, and **count the refusals you met in your return**. Run no glob, search or listing over `governance/project/`: name the files you need there one by one. Never read `.claude/settings.json`.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/check/schema.py`, `template/governance/kernel/schemas/close.schema.json`, `tests/unit/check/test_schema*`), and name in your return every such result you were served. Say in your return whether you used `gov retrieve`.
- **Command forms the guard reads (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools and literal absolute paths; put anything longer in a script under the session's own scratch folder and run that file. **Note:** the current five-rule hook has been seen refusing plain reads such as `ls` or `grep -r` over `tests/acceptance/` as "a command that may write the acceptance tests" (a false positive for other roles; for you it should pass). If it refuses a read, use the Read, Grep and Glob tools instead, and log it under `guard_refusals:`. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No subagents that write. Install nothing: a tool you need is returned as a package. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone` of this repository). A test that needs a repository builds a temporary one from scratch. No clone, copy or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` (and in your return), write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run at most a single test file at a time; wait with short checks (`until [ ! -e <that file> ]; do sleep 60; done`, never longer than a few minutes in one call). You run only the test files you change (and their neighbours you need to check); never the full suite. Never `-x`.
- **Budget (DEC-898):** your share is 8 GB and 400,000 files and folders outside the tracked tree, the sandbox's temp folder included. Keep the sandbox's own temp folder (do not set `TMPDIR`); keep pytest's own retention, no `--basetemp`; add `-o tmp_path_retention_policy=failed` to every pytest run (it removes a passing test's temp folder). W1-30's cases build whole repositories: run W1-30 a few files at a time, not all at once while they are red. Clean up every temporary tree you make; give `du -sh` and `du -s --inodes` of what you used in your return. Past the budget: stop and return.
- **On an authentication or access error** (401, 403, "Failed to authenticate"): stop and return with status AUTH_REQUIRED.
- Your time budget is about 2 hours. Commit as you go (one commit per test folder is good), before any long run.

## What you read

- The owner's decision DEC-954 in `docs/DECISION_REGISTER.md` (its P-W2-64-1 item), DEC-906, DEC-872 (item 2), DEC-866, DEC-491, DEC-462; the package `governance/project/orchestration/packages/P-W2-64-1.md` (by name), which lists the failures.
- The ticket file `.tickets/DAEO-0uhh.md` (read-only).
- The kernel schemas (`template/governance/kernel/schemas/common.schema.json`, `ticket.schema.json`, and the others the failures name; `close.schema.json` only as on `w2/integrate`), and the grammar of ids there: a wbs id matches `^W[0-9]+-[0-9]{2,}[a-z]?$`; a ticket id matches the ticket schema's `id` pattern; a decision id is `DEC-<digits>`.
- The failing tests themselves and their support modules, and the README of each earlier ticket's folder, so that each corrected fixture keeps what the test means.

## The cases to correct (the owner's list; re-establish it by running)

Run each named file first against this worktree's code to see today's reds; the lead's run-1 list (JUnit, 203 cases) was:
1. **W1-30, ~180 cases across most `tests/acceptance/W1-30/test_w1_30_*.py` files:** the shared fixture tickets in its support modules (`w1_30_support.py`, `w1_30_r15_support.py`, `w1_30_r16_support.py`, and any fixture a test file builds itself) carry `wbs_id` values such as `W1-work`, `W1-iter`, `W1-prfd`, which the ticket schema refuses (`^W[0-9]+-[0-9]{2,}[a-z]?$`), and one fixture decision id `DEC-earlier`. The fixture repositories' `gov close` then refuses with CHECK_FAILED from core-schema before reaching what each test judges. Give each fixture a valid id **that stays distinct where the tests rely on distinct ids**, and where a test matches a path or a name derived from the old id (for example `tests/acceptance/W1-prfd`), keep the test's meaning (change both sides consistently). Check also cases that failed for a knock-on reason (`test_w1_30_r13_long_findings`'s length precondition, `test_w1_30_disposition`'s context hash, `test_w1_30_r13_refused_runs`): find the cause before you change anything, and if the cause is not a fixture the schemas refuse, do not change it; name it in your return.
2. **W2-57, 1 case:** `tests/acceptance/W2-57/test_w2_57_nightly_route.py`, its fixture wbs id (`W1-w257`).
3. **W1-26, 4 cases:** `tests/acceptance/W1-26/test_w1_26_dec436.py::test_record_in_new_directory_discovered_by_schema_check` (fixture record id `REC-NEW-001`, refused); `tests/acceptance/W1-26/test_w1_26_installed_kernel.py` (3 cases; its "well-formed" records give `kpis` in a form the ticket schema refuses — make them well-formed by the schema).
4. **W2-54, 16 cases:** `tests/acceptance/W2-54/w2_54_support.py` runs the check with `PATH=<workdir>/bin:/usr/bin:/bin` (no check-jsonschema, so the check now says `SCHEMA_VALIDATOR_ABSENT`, correctly RED), and its helper reads only a list as the check's output. Correct the support: **give the check the suite's own check-jsonschema on its PATH** (the folder of the `check-jsonschema` that the running suite's `PATH` finds, e.g. through `shutil.which`; never a hard-coded home path), and **read the output's dict forms** as well as a list: the success form `{"ok": true, "result": {...}}` (no findings) and the refusal form `{"findings": [...], ...}`. Do not touch W2-54's two time-limit cases that W2-85 routed to the nightly.
5. **Two unit tests, now in this ticket's paths:** `tests/unit/check/test_check.py::test_schema_clean_record` (its "clean" ticket fixture id `T-001` is refused by the ticket schema's id pattern: make the clean record clean) and `tests/unit/check/test_kernel_followup.py::test_a_probe_record_is_never_silent_where_its_schema_cannot_be_read` (it expects `SCHEMA_INVALID_FIELD` where the schema cannot be read; with the real validator a schema that cannot be built is reported as `SCHEMA_VALIDATOR_FAILED`). For this one the test's meaning is "never silent": the finding must still be a hard finding on that record, never green. Keep that meaning and accept the validator's code for "cannot be measured"; the expectation is not lowered so long as the test still requires a finding and the check still fails.

Any other failing case you meet in those files whose cause is not a fixture the real schemas refuse (or check-jsonschema missing from a test's PATH): **do not change it**; name it in your return with its failure line.

## Rules for every change (DEC-954, DEC-491, DEC-866)

- **Lower no expectation:** no assertion removed, weakened, skipped, marked xfail, or widened to accept more; no test deleted; no time limit raised. Only the fixture data and helpers change, plus the one finding code in item 5 that the decision names.
- You write only: the files under `tests/acceptance/W1-30/`, `tests/acceptance/W2-57/`, `tests/acceptance/W1-26/`, `tests/acceptance/W2-54/` that the corrections need, and `tests/unit/check/test_check.py` and `tests/unit/check/test_kernel_followup.py`. Nothing under `src/`, `template/`, `tests/acceptance/W2-64/`, nothing else.
- Each commit's message names DEC-954 and carries, in its final block, `Rewrite-Reason: DEC-872 item 2`. If an earlier folder's README describes the fixture ids you change, update that README in the same commit.

## Verification you run

For each corrected file: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m pytest <the files> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`, to its end; quote each summary line. Every case you corrected must pass; quote any still red with its first failure line and its cause. Then the list of every file you changed (`git diff --name-only <your first parent>..HEAD`), so the lead runs exactly those.

## Commit

Before each commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop and return. Commit only your paths, with the trailers in the final block:

    git commit -m "<subject> (DEC-954)" --trailer "Task: DAEO-0uhh" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-954, DEC-872" --trailer "Rewrite-Reason: DEC-872 item 2" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -3` and `git status --short`, quoted in your return.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

In those fields give: the sandbox check's result; the `gov.__file__` line; each commit's hash (12 digits) and trailers; per file, the cases corrected and what changed in the fixture (old id → new id, and so on); every expectation you judged and kept; each still-red case with its cause; whether you used `gov retrieve`, and any result under the implementation paths you were served and dropped; the read refusals you met (count); your scratch measure.

Right after the twelve fields, two sections:
- `brief_gaps:` one line per thing you had to discover that this brief did not tell you: `- <what was missing> | <where it belonged> | <minutes it cost, estimated so marked>`, or `brief_gaps: none`.
- `guard_refusals:` one line per refusal by the five-rule hook you met: `- <time> | <the command's form, one line, no secret or file contents> | <the rule's reason as the hook gave it> | true or false-positive | <minutes it cost and what you did instead>`, or `guard_refusals: none`. A false positive is worked round only by an equivalent form that does what was meant (such as the Read, Grep or Glob tool, or a script file); a true refusal is taken.

Refused twice for the same call: stop and say so.
