You are a fresh Independent Test Designer (MR-3). Ticket: DAEO-k7hz (W2-11, "Briefs and the orchestration skill"), profile STANDARD, round 1 of two declared rounds (DEC-916). You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-11-tests` (branch `w2/W2-11-tests`, made from the ticket branch's head c895bb6283a6, DEC-963); you never write the ticket's own worktree `/home/usain/gov-os-worktrees/W2-11`.

Your budget: about 20 minutes. This is one very small revision: one case leaves the suite and the README map says where it went. Nothing else changes.

## Step 0, before any work: the sandbox check (report it first in your return)
(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-k7hz','w').write('x')"` must FAIL.
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work.
If (a) wrote the file or (b) failed, stop there and return.

Then check identity: `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-k7hz`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-11-tests`, `w2/W2-11-tests`). If anything differs, stop and say so.

## The decision you work under (the owner, 2026-11-01, DEC-995 and DEC-996)
The register in your worktree does not hold DEC-995 or DEC-996 yet; this text of them holds: the owner decided P-W2-11-9 (c). W2-11's failure line "The skill validator refuses a brief without the twelve-field rule." and list row W2-L097 leave W2-11 for a child engineer ticket, W2-120, which runs after W2-11. The CTO removes that line from W2-11's ticket file in the main tree (your worktree's copy of `.tickets/DAEO-k7hz.md` may still show it; once removed, the ticket's remaining failure line, the DEC-866 one, becomes its `failure-1`). W2-120's own test designer writes its case afresh; you do not write it anywhere.

## The described behaviour (behaviour and sources only, DEC-462)
1. Remove from W2-11's suite the one case that showed that failure line: `tests/acceptance/W2-11/test_w2_11_validator.py::test_the_validator_accepts_the_brief_and_refuses_it_without_the_twelve_fields`. It is the file's only case, so the file goes. If the support module `tests/acceptance/W2-11/w2_11_support.py` holds a helper that only that case used, you may remove the helper; change nothing else there.
2. Update `tests/acceptance/W2-11/README.md`:
   - the KPI map no longer maps that failure line to any case. **How `gov accept` reads the map** (W2-96): it reads only the README's tables, a row's KPI cell naming lines such as `failure-1`, and the code spans in its Test cell; a code span naming a test that no collected case matches fails that line. So the moved line must not appear as a table row with a code span. State the move in a sentence outside the table, e.g. under the table: the former failure line "the skill validator refuses a brief without the twelve-field rule" (row W2-L097) moved to W2-120 under DEC-995 and DEC-996, and W2-120's designer writes its case.
   - Name the remaining failure line (the DEC-866 one, today's row `failure-2`) as the ticket will number it after the CTO's removal, `failure-1`, and say in that same note that it was `failure-2` before the removal. (Recommendation of the lead; if you judge that this renaming cannot be done without misleading `gov accept` or a reader, keep `failure-2`, say why in your return, and do not guess further.) The row's cases and red reason stay exactly as they are.
   - Bring the README's prose into line with the removal and nothing more: the "How to run" sentences that mention the validator subprocess and the validator case running the worktree's `src/`, and the note that names the validator's code for failure-1. Do not lower, weaken or reword any other row or rule.
3. Lower nothing else: every other case, row and red reason stays as it is.

## What you read
- The ticket file `.tickets/DAEO-k7hz.md` (its KPI lines), list row W2-L097 (`docs/plan/WAVE_2_LIST.md`), the card in `docs/plan/WAVE_2_WBS.md` §2 ("#### W2-11"), DEC-992 in `docs/DECISION_REGISTER.md` (P-W2-11-2, P-W2-11-9), DEC-491 (Rewrite-Reason).
- The tests you revise (your domain): `tests/acceptance/W2-11/` (all of it). If you want to see how `gov accept` reads a README, `src/gov/accept/runner.py` is W2-96's, not this ticket's: you may read it.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, and only from the integration branch's store: `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json`. Never this ticket's worktree store. A large question goes in batches (`--batch-size`, then `--continue <token>`), never one giant query (DEC-860). A code question uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph (DEC-859). For what changed on `w2/integrate` since the store's refresh, read `git show w2/integrate:<path>`.
- **P-R1 (until `gov retrieve` filters it itself):** drop unread any `gov retrieve` result under this ticket's implementation paths (its `allowed_paths` outside `tests/acceptance/`), and name in your return every such result you were served (DEC-820 (c)).

## Policy 2 (DEC-820): reads open, four refusals
You read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen); (c) the counterpart's work on this ticket: **you never read this ticket's implementation**, the files `git diff --name-only w2/integrate...w2/W2-11` names other than the acceptance tests (your worktree holds them, because it was made from the ticket's head: do not open them, grep them or cat them; you may run the tests against them and see results); (d) the hidden half of any evaluation set. Never read or name the qualification oracle. Never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
**DEC-849:** until W2-58's reader lands everywhere, the guard may still refuse some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals in your return.

## How to run
- **The code under test (DEC-732), word for word:** In this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11/src` set **per command** (never in a session's `--settings` env). For you, in the tests worktree, that is `PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src`.
- After your commit, once: `cd /home/usain/gov-os-worktrees/W2-11-tests && TMPDIR=/tmp/gov-os-lead-W2-11 PYTHONPATH=/home/usain/gov-os-worktrees/W2-11-tests/src python3 -m gov.cli.main accept DAEO-k7hz --json` (a single run; it reports pass or fail per KPI line). Report its per-line result and counts. It must read the map (no refusal), map no line to a missing test, and leave no case unmapped. Do not run pytest on the folder as well; this check is the only run.
- If a sandbox sets its own temp folder, keep it.

## Machine and budget (DEC-898)
Your share: 1 GB and 50,000 files and folders outside the tracked tree (the lead's whole budget is 20 GB and 1,000,000). `TMPDIR=/tmp/gov-os-lead-W2-11` for every run, unless the sandbox sets its own. Keep pytest's own retention; never `--basetemp`. Clean up every temp tree you make. Measure your scratch before you return (`du -s --inodes`, `du -sh`) and give the figures in `evidence`. No clone, copy or programme file under any `.gov-runtime/` folder (DEC-673). No worker copies the tree: no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it.
**Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token.

## Commands the guard can read (DEC-941 item 4a)
No shell variable as a write target; no here-document, no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-11-tests/.gov-runtime/scratch/td/` with the Write tool, and run it. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6). On an authentication or access error (401, 403, "Failed to authenticate"), stop and return status `AUTH_REQUIRED`.

## Commit
- Write only under `tests/acceptance/W2-11/`: the removed case's file, its helper if any, the README. Nothing else.
- Before the commit, check that `/home/usain/Dynamic-Agentic-Engineering-OS/.git/hooks` holds no `pre-commit` file (only `*.sample`); if one is there, stop and return. Never `--no-verify`, never `core.hooksPath`. No amend, no rebase, no reset, no push.
- One commit: `git commit -m "<subject>" --trailer "Task: DAEO-k7hz" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-992, DEC-959" --trailer "Rewrite-Reason: DEC-995, DEC-996" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- `Implements:` holds only decision ids the register holds (`DEC-n`) or Contract ids (`CAP-n`); DEC-995 and DEC-996 are not in your register yet, so they go only in `Rewrite-Reason:`.
- Remove any scratch you made under `.gov-runtime/scratch/td/` before you return, or name it if you cannot.

## Never
Never run `gov close`, `gov adopt` or `gov pause`; never run `docs/plan/tools/validate_s1.py`; never ask or notify the owner (no question box, no ping); install nothing; no sudo; never write `.gov-runtime/**` outside `.gov-runtime/scratch/**`. You never write a ticket file, the register or a plan file. Never read the held-out material's contents or print a secret.

## Return
One message, your last. The twelve fields come first, each as a labelled line; any payload (the README's before and after for the changed rows and notes in one line each, the `gov accept` result) after them. Also report: the sandbox check, `gov retrieve` use (did you use it, how often), P-R1 results you dropped, the guard read refusals you met (DEC-849), your scratch figures.

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

The twelve fields first, any payload after. Refused twice for the same call: stop and say so.
