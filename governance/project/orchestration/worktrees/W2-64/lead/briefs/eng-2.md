You are a fresh engineer. Ticket: DAEO-0uhh (W2-64, "the record validator through check-jsonschema; `docs/imported/` out of the schema check"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-64` on branch `w2/W2-64`. Your job is one small change the owner accepted as a ride-along (DEC-954, P-W2-64-1): a one-line relaxation of the close schema, with its builder test.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0uhh','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return (name any file you made outside this worktree; never delete it).

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-0uhh`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-64` and `w2/W2-64`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag, no stash.
- **Policy 2 (DEC-820):** reads are open: the whole repository, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); never read or name the qualification oracle; (c) the counterpart's work on this ticket: **you never read `tests/acceptance/W2-64/`**, by any tool (no Read, cat, grep, glob or retrieval result of it); you may run those tests and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation set, by whoever is measured by it. Writes stay inside your paths.
- **Read refusals (DEC-849):** the guard may still refuse some reads Policy 2 opened. Take the refusal, never look for another form, search named folders instead, and **count the refusals you met in your return**. Run no glob, search or listing over `governance/project/`. Never read `.claude/settings.json`.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. Drop unread any retrieval result under `tests/acceptance/W2-64/`. Say in your return whether you used `gov retrieve`.
- **Command forms the guard reads (DEC-941 item 4a):** no shell variable as a write target (use literal paths); no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Write files with the Write and Edit tools. A refused form is not retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- No subagents that write. **Install nothing.** Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`, and never `tests/acceptance/**`.
- **Never copy the repository** or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). No clone or programme file under any `.gov-runtime/` folder. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** in anything you write under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **The machine:** while `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/NIGHTLY-RUNNING` or `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/CLOSE-RUNNING` exists, run at most a single test file; wait with short checks and go on the moment it is gone. Never the full suite. Never `-x`.
- **Budget (DEC-898):** your share is 2 GB and 100,000 files and folders outside the tracked tree, the sandbox's temp folder included. Keep the sandbox's own temp folder; keep pytest's own retention (no `--basetemp`); add `-o tmp_path_retention_policy=failed` to every pytest run. Give `du -sh` and `du -s --inodes` of what you used in your return.
- **On an authentication or access error:** stop and return with status AUTH_REQUIRED.
- Your time budget is about 30 minutes.

## The change

In `template/governance/kernel/schemas/close.schema.json`, the evidence block's `skips` items require `test` and `reason`; today `reason` refers to `#/$defs/text` (a non-empty string). An empty skip reason in a future close record (pytest can report a skip with no reason) would then turn `core-schema` RED for every ticket. **Relax `skips[].reason` alone to a plain string** (`{ "type": "string" }`): it stays required, it must still be a string, and the empty string is accepted. Nothing else in the schema changes (`why_full`, `selected`, `left_out` reasons stay non-empty; `skips[].test` stays `text`). One line.

**Builder test** in `tests/unit/check/test_schema*` (an existing file there that tests the close schema, or a new `tests/unit/check/test_schema_close_skips.py`): a close record whose evidence block has a skip with `reason: ""` validates; one with no `reason` key, or a non-string `reason`, is still refused (naming the record and the rule). Run it through the real check (`python3 -m gov.check.schema` in a temporary repository built from scratch with the kernel schema files copied by name, or the check's `check(root)`), as the neighbouring builder tests do.

Your paths: `template/governance/kernel/schemas/close.schema.json` and `tests/unit/check/test_schema*`. Nothing else.

## Verification you run

- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m pytest tests/unit/check -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` to its end, and `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m pytest tests/acceptance/W2-64 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs` to its end; quote both summary lines. Both must be green.
- `PYTHONPATH=/home/usain/gov-os-worktrees/W2-64/src python3 -m gov.check.schema` in the worktree root: quote its exit code and the first 300 characters of its output.

## Commit

Before committing, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if one is there, stop and return. Commit only your two paths, in one commit:

    git commit -m "<subject> (DEC-954 ride-along)" --trailer "Task: DAEO-0uhh" --trailer "Role: engineer" --trailer "Implements: DEC-954, DEC-890" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`, quoted in your return.

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

In those fields give: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits) and trailers; the diff of the schema line; whether you used `gov retrieve`; the read refusals you met (count); your scratch measure.

Right after the twelve fields, two sections:
- `brief_gaps:` one line per thing you had to discover that this brief did not tell you: `- <what was missing> | <where it belonged> | <minutes it cost, estimated so marked>`, or `brief_gaps: none`.
- `guard_refusals:` one line per refusal by the five-rule hook you met: `- <time> | <the command's form, one line, no secret or file contents> | <the rule's reason as the hook gave it> | true or false-positive | <minutes it cost and what you did instead>`, or `guard_refusals: none`. A false positive is worked round only by an equivalent form that does what was meant (such as the Read, Grep or Glob tool, or a script file); a true refusal is taken.

Refused twice for the same call: stop and say so.
