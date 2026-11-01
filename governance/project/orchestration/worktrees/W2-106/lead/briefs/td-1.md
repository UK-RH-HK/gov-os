# Brief: independent test designer, DAEO-0mtg (W2-106), run 1

You are a fresh independent test designer (MR-3). Ticket: DAEO-0mtg (W2-106), profile FULL. You work only in the
tests worktree `/home/usain/gov-os-worktrees/W2-106-tests` on branch `w2/W2-106-tests`; you never read or write the
ticket's own worktree (`/home/usain/gov-os-worktrees/W2-106`). You write the ticket's acceptance tests from its KPI
lines and its sources, in parallel with the engineer (DEC-959 item 7, DEC-963), and you show them red.

## Step 0: the sandbox check (before any work, reported first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-0mtg','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return, naming what happened.

## Standing rules (read first)

- Run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0mtg`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-106-tests` and
  `w2/W2-106-tests`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another. Return only after your commit exists.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge, no tag.
- **The code under test (DEC-732), word for word:** in this worktree, every test run and every `gov` command used for
  verification runs this worktree's own `src/`: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src` set per
  command (never in a session's `--settings` env). Your verification shows it with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106/src python3 -c "import gov; print(gov.__file__)"`, quoted in your
  return; it must point into this worktree. — For you, in the tests worktree, "this worktree" is
  `/home/usain/gov-os-worktrees/W2-106-tests`: use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106-tests/src`.
  Your tests must read the template files and the `gov` code **relative to the repository they sit in**
  (e.g. `Path(__file__).resolve().parents[3]`), so that when the lead merges them into the ticket's worktree and
  runs them there, they judge that worktree's template and code. Your README says how, with the `gov.__file__` line.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and
  only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve
  "<question>" --json`. Never this ticket's worktree's store. For what changed on `w2/integrate` since that store's
  refresh, read `git show w2/integrate:<path>`. Never one giant query (DEC-860): a large question in batches
  (`--batch-size`, then `--continue <token>`). A code question (DEC-859) uses the code-graph tool's own traversal
  (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths
  (`template/governance/kernel/settings.json`, `template/.rulesync/hooks.jsonc`, `tests/unit/hooks/test_w2_106*`)
  **as they stand in the ticket's worktree or branch `w2/W2-106`**, and name in your return any such result you were
  served. (Reading those two template files **as they stand on `w2/integrate`, before this ticket**, is reading the
  existing code, which you may do.)
- **Policy 2 (DEC-820), reads open, writes closed:**
  (c) you never read this ticket's implementation: no file that branch `w2/W2-106` changes against `w2/integrate`
  (`git diff --name-only w2/integrate...w2/W2-106` names them), other than your own tests. Never read anything in
  `/home/usain/gov-os-worktrees/W2-106`.
  (d) never read the hidden half of any evaluation set.
  Never read secrets or keys, never print one; never read the held-out qualification material's contents; never read
  or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name
  only and clone into a temporary folder.
- **DEC-849:** the guard may still refuse searches that start at the repository root, `governance/project/` or
  `.claude/`. Take the refusal, never look for another form; search named folders instead. Count every refusal you
  meet and list it in your return.
- **The guard's command forms:** no shell variable as a write target, no here-document, no backticks, no
  `bash -c '…'`, no long inline `python3 -c` with braces; put anything longer in a script file under
  `/home/usain/gov-os-worktrees/W2-106-tests/.gov-runtime/scratch/td/` with the Write tool and run it.
- **Refused twice for the same call: stop and say so; no third try** (AR-6).
- Never copy the repository or a folder of it (`cp -r`, `rsync`, `git archive`, `git worktree`, `git clone`). Tests
  that need a project build a temporary one (from scratch, or generated from the template the way W1-39 and W1-38's
  suites already do it, file by file). Inside a launched session `.gov-runtime/freeze` shows as a placeholder device
  file: conclude nothing from it. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Install nothing (raise it as a P1 in your return). Building a throwaway wheel and a throwaway venv in a temporary
  folder from this worktree's own code, with no network (`pip wheel --no-deps --no-build-isolation --no-index`,
  `python3 -m venv --system-site-packages`, `pip install --no-deps --no-index` into that venv), is how W2-59's suite
  makes a stand-in pinned `gov`; you may do the same inside the tests (see `tests/acceptance/W2-59/README.md`).
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/` write commit hashes as 12 digits, never the full 40, and
  never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.
- **Disk budget (DEC-898):** the lead's 20 GB and 1,000,000 files and folders are shared; your share is 6 GB and
  300,000 files and folders outside the tracked tree. `TMPDIR` is set by the launcher's sandbox: keep it. Keep
  pytest's own retention (never `--basetemp`); use `-o tmp_path_retention_policy=failed`. Clean up every temp tree
  you made when done. Give `du -sh` and `du -s --inodes` of your scratch at the end.
- **Machine load (DEC-847):** before a suite run, wait while both the 1- and 15-minute loads are at or above the
  CPU count.

## What you read

- The ticket file `.tickets/DAEO-0mtg.md` (read-only): its KPI lines, `allowed_paths` and sources.
- The decisions in `docs/DECISION_REGISTER.md`: DEC-966 (item 2), DEC-822 (items 1 to 3), DEC-957, DEC-965,
  DEC-801, DEC-616, DEC-917 (the four lifecycle lines keep DEC-608's plain form), DEC-880 item 3 and DEC-913 item 1
  (the exit-mapping form), DEC-732, DEC-820.
- `governance/project/orchestration/packages/P-W2-90-1.md` (P1-B: the measurement this ticket must turn into a
  refusal).
- **The pinned form, specified by reference (the KPI names it):** this repository's own guard line in
  `.rulesync/hooks.jsonc` (the `preToolUse` entry) — it is not this ticket's implementation, it is the form the
  ticket asks for. W2-59's README (`tests/acceptance/W2-59/README.md`) for how a stand-in pin is built and how a
  hook line is run as Claude Code runs it.
- How a project is generated from the template and its hook lines run: `tests/acceptance/W2-90/README.md` and
  `tests/acceptance/W2-90/w2_90_kernel_wiring.py`; W1-39's and W1-38's support modules (`assemble_source`,
  `create_project_and_run`, `run_rulesync_generate`). Claude Code's hook contract: PreToolUse blocks only on exit 2
  or a deny decision with exit 0; any other non-zero exit lets the call through.
- The existing template files as they stand on `w2/integrate` (`git show w2/integrate:template/governance/kernel/settings.json`,
  `git show w2/integrate:template/.rulesync/hooks.jsonc`), and the hook programs under
  `template/governance/kernel/hooks/`.
- W1-38's and W1-39's suites (KPI 4 names them): read them to see whether, once the template's three guard lines take
  the pinned form, their harness still gives the line a pinned `gov` it can find. Do the same reading for the other
  suites that run the template's guard lines (W1-05, W1-28, W1-46, W1-47 through W2-90's helper; W2-65). You may
  revise W1-38 or W1-39 only if the KPI requires it (they are named by KPI 4), each revision with
  `Rewrite-Reason: DEC-966 item 2` and no lowered expectation; any other suite you find affected is **named in your
  return, not edited** (it is W2-90's next round, a P2 package).

## The behaviour to test (the KPI lines, in their words)

Success:
1. Each of the template's three guard hook lines (pre-tool, and the two post-tool lines: PostToolUse and
   PostToolUseFailure on Bash), in `template/governance/kernel/settings.json` and in their rulesync source
   `template/.rulesync/hooks.jsonc`, takes this repository's pinned form (DEC-822, W2-59): it finds the installed gov
   (`$HOME/.local/bin/gov`, else `gov` on PATH), reads the interpreter its first line names, and runs the hook
   program (at `$CLAUDE_PROJECT_DIR/governance/kernel/hooks/<program>.py`, where Copier puts it) with that
   interpreter and `-E`; the line's exit codes are kept (0 and 2 pass through; any other ends in a refusal, exit 2).
2. Fail closed: with no gov found, or a first line that names no interpreter that runs, the line refuses (exit 2)
   with a message naming what is missing; it never falls back to a bare `python3`.
3. A session's PYTHONPATH cannot change which guard code runs: in a generated project, a planted PYTHONPATH pointing
   at an edited copy of gov that would allow a refused write, the hook still refuses it (P-W2-90-1 P1-B's
   measurement, now refused).
4. A generated project's hook lines equal the template's source after `rulesync generate` (the two sources stay in
   step), and the template's own suites (W1-38, W1-39) pass.

Failure:
- A template guard hook line that runs a bare `python3`, or one without `-E`.
- A missing or broken gov lets the hook pass, or falls back to another interpreter.
- An edited gov on PYTHONPATH lets a refused write through.
- The settings and the rulesync source out of step, or W1-38 or W1-39 red.

Scope note (lead's reading, P3): the KPIs cover the three guard lines only. The four lifecycle lines of
`template/.rulesync/hooks.jsonc` (sessionStart, stop, preCompact, subagentStop) keep DEC-608's plain form by DEC-917,
which W1-38 holds them to; do not test them for the pinned form.

## What you write

- Only under `tests/acceptance/W2-106/` in the tests worktree, plus W1-38 or W1-39 only if KPI 4 requires it.
- FULL: thorough, every KPI line's success and failure, the key edges (the `$HOME/.local/bin/gov` link versus `gov`
  on PATH; a first line with no interpreter or a missing one; a program exit of 1 or a crash mapped to 2; exit 0 and 2
  passed through; each of the three lines in both files; a decoy `python3` first on PATH never started). No
  combinatorial expansion beyond the KPIs. Behaviour through public interfaces; deterministic; no network.
- A `README.md` mapping each KPI line to its tests and its expected red reason, and saying how the tests run the
  code of the worktree they sit in (DEC-732), with the `gov.__file__` line.
- Red first: run your folder to its end (never `-x`) with
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-106-tests/src python3 -m pytest tests/acceptance/W2-106 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -rs`
  (add `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH` if rulesync needs node). They must fail on this base
  for the reason the README states (the template's lines run a bare `python3`). Tests that guard what already holds
  may pass on the base; name each with the reason.
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact,
  reversibility, cost, recommendation, confidence).

## Commit

Before committing, check `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only
`*.sample`); if one is there, stop and return. Never `--no-verify`. Commit only your test paths, in one commit (a
second only for a W1-38 or W1-39 revision), with the trailers in the final block:

    git commit -m "W2-106: acceptance tests for the template's pinned hook lines" --trailer "Task: DAEO-0mtg" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-966" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the test count; each KPI line with its tests; the red result as you saw it (counts,
time) and the red reason; the `gov.__file__` line; every earlier test you rewrote with its reason; every other suite
you found affected by the pinned form (named, not edited); the `gov retrieve` queries you ran; the guard refusals you
met; any package.

One message, your last, complete in itself, with no worker transcript. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them:

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
