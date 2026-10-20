You are a fresh independent test designer (MR-3). Ticket: DAEO-juee (W2-62, "Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force"), profile STANDARD, run 2 (a short repair). You work only in the worktree `/home/usain/gov-os-worktrees/W2-62` on branch `w2/W2-62`, which has just merged `w2/integrate` (head `6d7cc0d1`). You make one small revision to one existing acceptance test and commit it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-juee','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-juee`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-62` and `w2/W2-62`). If anything differs, stop and say so.

## Why (DEC-867, delegated, 2026-10-20)

`tests/unit/secrets/` is a test package named `secrets`, and it shadows the standard library's `secrets` module in any pytest process where the standard module was imported first. The live case `tests/acceptance/W2-62/test_w2_62_live_resume.py` imports the standard `secrets` (line 31) and calls `secrets.token_hex(8)` (line 82), so in one pytest run over `tests/` every `tests/unit/secrets/*` module fails to import ("'secrets' is not a package"). Reproduced here: `pytest tests --collect-only -q -p no:cacheprovider` from this worktree's root ends with 3 collection errors (`tests/unit/secrets/test_scan_scale.py`, `test_secrets.py`, `test_token_rule.py`). The renaming of `tests/unit/secrets/` belongs to another ticket (row W2-L373, W2-43); this run removes the trigger.

## The revision (the only change you make)

In `tests/acceptance/W2-62/test_w2_62_live_resume.py`, change only how the random token is drawn: without the `secrets` module, for example `os.urandom(8).hex()` (the file already imports `os`; check), with the same length and format as before (`W262-` followed by 16 lowercase hexadecimal characters). Remove the `import secrets` line. No other line of the file changes; no other expectation changes; nothing is deleted, skipped or weakened. No other file changes (the README needs no change unless it names the `secrets` module; if it does, change only that mention, and say so).

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** In this worktree, every test run and every `gov` command used for verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src` set per command (never in a session's `--settings` env). Quote `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -c "import gov; print(gov.__file__)"` in your return; it must point into this worktree.
- **Memory (DEC-836, DEC-860, DEC-859):** use `gov retrieve` for what you need to know before reading files at random: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m gov.cli.main retrieve "<question>" --json`. Never one giant query or context: a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph. (This task is small; you may need neither. Say in your return whether you used them.)
- **Reads (DEC-820, Policy 2):** you read freely: the whole repository, the committed context, git history, other worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on this ticket: **you never read this ticket's implementation**: `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**`, `tests/unit/hooks/**` as changed by this ticket, and `docs/changes/W2-62-CIT-P.md` (you need none of them for this revision); (d) the hidden half of any evaluation set, by whoever is measured by it. Never read or name the qualification oracle.
- **Read refusals (DEC-849):** until W2-58 lands, the guard still refuses some reads Policy 2 opened (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, and search named folders instead. Count the refusals you met and give the count in your return.
- **Refused twice for the same call: stop and say so; no third try (AR-6).**
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Nothing is ever put under a `.gov-runtime/` folder by a test.
- Never write in `~/gov-os-workbench`; never list, glob or search it. Never print a secret.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Write files with the Write and Edit tools and literal absolute paths (the guard refuses here-documents and unresolvable variables in Bash write targets). No subagents that write. Install nothing. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Nobody runs `gov close`, `gov adopt`, `gov pause`, `gov rebuild --no-embeddings` or `docs/plan/tools/validate_s1.py`. On ESCALATION_BLOCKED from any command, stop and return it.
- Never ask the owner a question and never use a question box (DEC-850): a question comes back in your return as a package.
- Use your model's full window; you are never asked to stop or compact early (DEC-838).
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package.

## Check, then commit

1. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m pytest tests --collect-only -q -p no:cacheprovider` from this worktree's root: report its last line; it must end with no collection error.
2. `PYTHONPATH=/home/usain/gov-os-worktrees/W2-62/src python3 -m pytest tests/acceptance/W2-62 -q -p no:cacheprovider -rs -m "not local_only"` to the end (never `-x`): report the counts. The live case is `local_only` and needs the network: show it collected (`--collect-only -q tests/acceptance/W2-62/test_w2_62_live_resume.py`); the lead runs it.
3. Show `git diff --stat` and `git diff`: only the token lines of that one file.
4. Commit that file only, in one commit, with the trailers in the final block. There is no pre-commit hook; never `--no-verify`, never `core.hooksPath`:

    git commit -m "W2-62 (DAEO-juee): the live case draws its token without the secrets module (DEC-867)" --trailer "Task: DAEO-juee" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-837" --trailer "Rewrite-Reason: DEC-867 (the standard secrets module collides with tests/unit/secrets in one pytest run)" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then show `git log --oneline -2`, `git log -1 --format=%B` and `git status --short`.

## Return

Your last message, complete in itself. The twelve fields come first, each as a labelled line (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Put in them: the sandbox check's result; your commit's hash and trailers; the diff; the collection line; the W2-62 counts; the guard read refusals you met (a count, with what was refused); whether you used `gov retrieve`; the `gov.__file__` line; any package.

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

Refused twice for the same call: stop and say so.
