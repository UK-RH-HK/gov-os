# Brief: engineer, W2-110 (DAEO-3r1j), run 3: the five unit cases' revision (DEC-980)

You are a fresh engineer. Ticket: `DAEO-3r1j` (`W2-110`), profile FULL. You work only in the worktree
`/home/usain/gov-os-worktrees/W2-110` on branch `w2/W2-110` (head `0aa2854bb6ba`). The ticket's code is committed,
reviewed and passed; **it does not change in this run.** Under the CTO's decision DEC-980 (P-W2-110-1 (a)) you revise
five builder-level cases in `tests/unit/install/test_install.py` that still assert a superseded rule. You are a
headless session: nobody answers questions while you work, and only your final message is read.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-3r1j','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must WORK.
If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `engineer` and `DAEO-3r1j`) and
`git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-110` and `w2/W2-110`). If
anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src` set per command
  (never in a session's `--settings` env). Show it once with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -c "import gov; print(gov.__file__)"` and quote it.
- **Retrieval (DEC-836):** use `gov retrieve` for what you need to know before reading files at random, from the
  integration branch's store (this worktree's store indexes this ticket's acceptance tests, which you must not read):
  `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). For this ticket's own
  files, read them in this worktree. Never one giant query or context (DEC-860): a large question is taken in batches
  (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. A code question uses the
  code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of
  the whole graph (DEC-859).
- **Policy 2 (DEC-820), reads open, writes closed.** You read freely: the whole repository, git history, other
  worktrees. Only four things are refused: (a) secrets and keys, never printed; (b) the contents of the held-out
  qualification material (its file names may be seen); never read or name the qualification oracle; (c) **the
  counterpart's work on this ticket: you never read `tests/acceptance/W2-110/`, nor any test designer's work in
  `/home/usain/gov-os-worktrees/W2-110-tests` or on branch `w2/W2-110-tests`,** by any tool; you may run acceptance
  tests and see their names, results and failure messages, never their source; (d) the hidden half of any evaluation
  set, by whoever is measured by it.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads Policy 2 opened (searches that
  start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form,
  search named folders instead, and count the refusals in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document, no
  backticks, no `bash -c '…'`; no long inline `python3 -c` with braces. Put anything longer in a script file in your
  session's scratchpad (the Write tool refuses `.gov-runtime/scratch/eng/`) and run that file. A refused form is not
  retried in another disguise.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Run everything in the foreground, one command after another; return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge.
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). A test
  that needs a repository builds a temporary one. Never write in `~/gov-os-workbench`.
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists:
  conclude nothing from it.
- Install nothing (a tool you need is returned as a P1 package). No sudo. Never write `.gov-runtime/**` outside
  `.gov-runtime/scratch/`. Never touch `tests/acceptance/**`. No subagents that write. Never ask or notify the owner.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` and in your return, write commit hashes as 12 digits, never
  the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Your scratch budget (DEC-898):** 4 GB and 200,000 files and folders, outside the tracked tree, as your share of the
  ticket's 20 GB / 1,000,000. Your temp folder is the one the sandbox sets (keep it). Keep pytest's own retention;
  never a per-run `--basetemp`; run pytest with `-o tmp_path_retention_policy=failed`. Remove every temp tree you made
  as soon as it is no longer needed; if a removal is refused, name the path and leave it. Measure your scratch
  (`du -s --inodes`, `du -sh`) at the end and give the figures in `evidence`.
- Every suite is run to its end, never with `-x`. Never run the full test suite.

## What you read

- The ticket file `.tickets/DAEO-3r1j.md` (read-only): its KPI lines, its `allowed_paths` and the DEC-980 paragraph.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-980 (item 1), DEC-971 (item 4), DEC-957, DEC-083, DEC-866, DEC-491.
- The ticket's design note `/home/usain/gov-os-worktrees/W2-110/.gov-runtime/scratch/lead/design.md`, and the code it
  describes (`template/governance/kernel/hooks/pretooluse.py`, `src/gov/guard/install.py`), read only.
- `tests/unit/install/test_install.py`, the file you revise.

## The revision (DEC-980 item 1, exactly; nothing else lowered)

The five cases `test_orchestrator_install_gets_ask`, `test_ask_leaves_snapshot`, `test_ask_output_has_three_keys`,
`test_unfrozen_repo_asks_install_for_orchestrator` and `test_curl_combined_option_ask_for_orchestrator` assert
DEC-083's "any orchestrator is asked" with no coordination-ticket key in their fixture repository, and now get
`deny` ("the project's coordination ticket is not set"). Revise them so that:

- **each fixture repository gets a roster** (`governance/project/roster.yaml` with a top-level `coordination_ticket`)
  naming the orchestrator's ticket the case's session carries (`GOV_TICKET`), and the ticket file under `.tickets/`
  where the fixture lacks it; their asks, prompts, snapshots and output keys are then kept exactly as asserted;
- a case of an orchestrator subagent in a worker's session, if any, flips to refused; nothing else flips;
- **nothing else is lowered:** no assertion removed or weakened, no case dropped or skipped, no new tolerance; other
  cases in the file are untouched. Prefer one shared fixture helper over per-case edits.

You change no code under `src/` or `template/`. If a case cannot be brought back without a change beyond this, name it
in your return as a package; never bend the code to it.

## Run (each to its end)

- `TMPDIR` is the sandbox's own. Before and after the revision:
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -m pytest tests/unit/install -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
- After: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-110/src python3 -m pytest tests/unit/guard -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`.
- Report both runs' counts.

## Commit

Before you commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file; if
one is there, stop and return. Never `--no-verify`. Commit only `tests/unit/install/test_install.py`, with the
trailers in the final block:

    git commit -m "W2-110: the five install unit cases' revision: a coordination-ticket roster in their fixture (DEC-980)" --trailer "Task: DAEO-3r1j" --trailer "Role: engineer" --trailer "Implements: DEC-980, DEC-971, DEC-957" --trailer "Rewrite-Reason: DEC-957, DEC-971 item 4" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the
start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after
them. Put in them: the sandbox check's result; the `gov.__file__` line; your commit's hash (12 digits); the lines
added and removed; each case changed and how; the runs with their counts before and after; whether you used
`gov retrieve` and how often; read refusals met; your scratch figures; any package (question, why now, options,
impact, reversibility, cost, recommendation, confidence).

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
