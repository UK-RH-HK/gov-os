# Brief: engineer (a repair batch), DAEO-arrl (W2-55), profile STANDARD, run 1

You are a fresh engineer. Ticket: `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-55` on branch `w2/W2-55`. You make one repair, below, to the ticket's code; you build to the specification, never to the tests, and you never read `tests/acceptance/W2-55/`.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-arrl','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-arrl`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-55` and `w2/W2-55`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return.
- **Memory used (DEC-836):** use `gov retrieve` (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -m gov.cli.main retrieve "<question>" --json`) for what you need to know before reading files at random. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read `tests/acceptance/W2-55/`**, by any tool, here or in `/home/usain/gov-os-worktrees/W2-55-tests` or on any branch; you may run those tests and see their names, results and failure messages; (d) the hidden half of any evaluation set (W2-61's measure's hidden half among them).
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/eng/` with the Write tool and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one. No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in imports the installed package or copies single named files, never `governance/project/`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 10 GB and 500,000 files and folders, outside the tracked tree. Keep the sandbox's own `TMPDIR`; do not set `TMPDIR` yourself. Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- **Never `gov rebuild --no-embeddings`.** Do not rebuild the store yourself unless you must; if you do, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json`.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, `docs/DECISION_REGISTER.md`, the plan files or `governance/project/path-map.yaml`. Never run `gov close`, `gov adopt` or `gov pause`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-arrl.md` (read-only) and its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-55`).
- The code: `src/gov/decisions/` (`register.py` and its callers), `src/gov/context/`, `src/gov/retrieve/command.py`.

## The repair (this batch's whole task)

The ticket is built and its 76 acceptance tests pass. One measured defect is left, and this batch fixes only it.

**The failing output (the lead's measurements on this worktree, head `0263e8c4e828`, under the same machine load):**

- `gov check --json`: `context reproducibility: RED` — "context-reproducibility did not end within its time limit of 600 seconds". That check computes the context of each of the project's 180 tickets twice (`src/gov/context/context_check.py`).
- One `gov.context.context(root, "DAEO-arrl")` call, profiled: 1.996 s in all; the supplementary part 1.730 s; the retrieval 1.187 s; **the new register filter `leave_out` 0.504 s, of which the register's read and parse at `HEAD` 0.410 s** (`src/gov/decisions/register.py`, `read`). The register is read and parsed again on every call, though it changes only with `HEAD`.
- Ten tickets, two contexts each: 3.44 s per ticket with the base's code, 4.64 s with this branch's code. Over 360 contexts the filter adds about 180 s.

**What to change:** the register's reading must cost its parse once per process for one `HEAD` (and one register file), not once per call: the same `root`, `HEAD` commit and register give the same answer without parsing again; any change of `HEAD` (a new commit) or of the root reads afresh, so no stale register is ever served. Every caller of the read (the filter in `gov context` and `gov retrieve`, `--in-force`, the two register checks) keeps its behaviour exactly. Nothing fails open: a register that cannot be read still refuses as before. Stay in `src/gov/decisions/**` (and `tests/unit/decisions/**` for a builder test of the cache: a second call does not parse again, and a new commit is read afresh). Do not touch `src/gov/retrieval/**`.

**Then:** commit; run `tests/unit/decisions` and the ticket's acceptance tests once (`PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider --tb=no -rfE -o tmp_path_retention_policy=failed`, results only, never the source); and give, in your return, the same ten-ticket timing as above with your code (`for` the first ten tickets of `gov.context.context_check.project_tickets(root)`, two `context()` calls each, wall time per ticket), and one profiled call's `leave_out` and `read` times.

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-927 item 2: `Implements:` holds only decision ids the register holds):

    git commit -m "<subject>" --trailer "Task: DAEO-arrl" --trailer "Role: engineer" --trailer "Implements: DEC-791, DEC-825, DEC-866, DEC-983, DEC-786, DEC-851" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the files changed; the lines added and removed; the builder tests and the acceptance tests you ran with their results; the timings asked for; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; anything you were refused or could not settle, as a package.

Your last message is your return, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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

Right after the twelve fields: a section `guard_refusals:` (one line per refusal: time | command form | the hook's reason | true or false-positive | minutes it cost), or `guard_refusals: none`; and a section `brief_gaps:` (one line per thing you had to discover that this brief did not tell you: what | where it belonged | minutes), or `brief_gaps: none`. Refused twice for the same call: stop and say so.
