# Brief: independent test designer, DAEO-arrl (W2-55), profile STANDARD, run 1

You are a fresh independent test designer (MR-3). Ticket: `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD. You work only in the tests worktree `/home/usain/gov-os-worktrees/W2-55-tests` on branch `w2/W2-55-tests` (DEC-963); you never read or write the ticket's own worktree (`/home/usain/gov-os-worktrees/W2-55`). You write the ticket's acceptance tests from its KPI lines and its sources, in parallel with the engineer, and you show them red.

## Step 0: the sandbox check, before any work (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-arrl','w').write('x')"` must FAIL. (b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file or (b) failed, stop there and return.

Then run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-arrl`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-55-tests` and `w2/W2-55-tests`). If anything differs, stop and say so.

## Standing rules (read first)

- **The code under test (DEC-732), word for word:** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src` set **per command** (never in a session's `--settings` env). Show it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src python3 -c "import gov; print(gov.__file__)"` and quote it in your return. Your tests must call the code of the tree they run in (a child process with that tree's `src/` on `PYTHONPATH`, as `tests/acceptance/W2-87/w2_87_support.py` and `tests/acceptance/W2-03/w2_03_support.py` do), so that once merged into the ticket's worktree they exercise its code; your README says how.
- **Retrieval (DEC-963, DEC-836):** use `gov retrieve` for what you need to know before reading files at random, **only from the integration branch's store:** `cd /home/usain/gov-os-worktrees/W2-00-store && gov retrieve "<question>" --json` (a read). Never this ticket's worktree's store or files. For what changed on `w2/integrate` since that store's refresh, read `git show w2/integrate:<path>`. **Never one giant query (DEC-860):** a large question is taken in batches (`--batch-size`, then `--continue <token>`), ranked and stacked within your budget. **A code question (DEC-859)** uses the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), small and targeted, never a load of the whole graph.
- **P-R1:** drop unread any `gov retrieve` result under this ticket's implementation paths (`src/gov/decisions/**`, `src/gov/context/**`, `src/gov/retrieve/**`, `template/governance/kernel/schemas/decision*`, `tests/unit/decisions/**`, `docs/research/W2-55-backfill.md`), and name in your return any such result you were served (DEC-820 (c)). You may read those files **as they stand on `w2/integrate`** (`git show w2/integrate:<path>`): that is the existing code, not this ticket's work.
- **Reads open, writes closed (DEC-820):** you read freely, except: (a) secrets and keys, never printed; (b) the contents of the held-out qualification material (its file names may be seen), and never read or name the qualification oracle; (c) **the counterpart's work on this ticket: you never read this ticket's implementation**, the files `git -C /home/usain/gov-os-worktrees/W2-55 diff --name-only w2/integrate...HEAD` names other than tests, nor anything in `/home/usain/gov-os-worktrees/W2-55` that differs from `w2/integrate`; (d) the hidden half of any evaluation set. Writes stay inside `tests/acceptance/W2-55/` in this worktree.
- **Read refusals (DEC-849):** until W2-58 lands the guard still refuses some reads (searches that start at the repository root, `governance/project/` or `.claude/`). Take the refusal, never look for another form, search named folders instead, and count the refusals you met in your return.
- **The guard's command forms (DEC-941 item 4a):** no shell variable as a write target; no here-document (`<<EOF`), no backticks, no `bash -c '…'`; no long inline `python3 -c` with braces; put anything longer in a script file under `/home/usain/gov-os-worktrees/W2-55-tests/.gov-runtime/scratch/td/` with the Write tool and run that file. A refused form is not retried in another disguise. **Refused twice for the same call: stop and say so; no third try** (AR-6).
- **Protected material:** never write in `~/gov-os-workbench`; dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder. Tests that need a repository build a temporary one from scratch (`tmp_path`). No `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it; a throwaway stand-in copies single named files, never `governance/project/`. Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file: conclude nothing from it.
- **Row W2-L423's rule (DEC-911):** under `.gov-runtime/`, write commit hashes as 12 digits, never the full 40, and never write the keywords of the gitleaks rule that takes a bare 40-hex string for a token (call it "row W2-L423's rule"). Your return follows the same rule.
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 5 GB and 250,000 files and folders, outside the tracked tree. Use `TMPDIR=/tmp/gov-os-lead-W2-55` for your runs unless the sandbox sets its own temp folder (keep that one). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, the register or plan files.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-arrl.md` (read-only): its seven success KPI lines and four failure lines, its `allowed_paths` and its sources; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-55`) and §0 (rules for every ticket).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-791 item 1, DEC-825 items 2 and 4, DEC-866, DEC-851, DEC-786, DEC-833 item 3, DEC-941, DEC-952 item 5, DEC-953 item 7, DEC-982, DEC-983, DEC-221 (tests in proportion), DEC-462, DEC-491.
- The fixture of KPI 5: `governance/project/orchestration/packages/SWEEP-2026-10-20.md` (§3 and §5); `governance/project/orchestration/packages/SMART-WORK-1.md` (practice 15).
- Lens B's Q05 and F4: `docs/assessment/2026-10/B-memory-retrieval.md`.
- The existing public interfaces as they stand on `w2/integrate`: `gov.decisions.check(root)` (W2-03's checker), `gov.store.load(root)`, `gov.records.records(root)`, `gov context <ticket> --json`, `gov retrieve <query> --json` (`python3 -m gov.cli.main …`), the store's register entries (W2-03), and how earlier suites drive them: `tests/acceptance/W2-03/`, `tests/acceptance/W2-87/` (temporary repositories with a planted register and path map, child processes on this tree's `src/`).

The specification below fixes the public forms. It is the same text the engineer has.

{{SPEC}}

## The behaviour to test, by KPI line (STANDARD: every line's success and failure, plus the key edge cases)

1. KPI 1 and failure 1: an entry with no domain, no status naming its successor, or no scope fails the register check, naming the entry; a fully tagged register passes; a domain outside the list and a scope outside the two are refused (S1, S2).
2. KPI 2: a missing lands-in tag, a place `HEAD` does not hold, and a place outside where its scope says each fail, naming the entry (S1, S2).
3. KPI 3 and failure 2: `gov retrieve --json` and `gov context <ticket> --json` leave out register evidence of superseded and done entries and state how many (`left_out`); a changed entry is still served; nothing is left out and no key appears when no entry is superseded or done; a superseded entry that reaches the bundle or the packet fails a test (S4). Lens B's Q05 as a case.
4. KPI 4 and failure 4: the backfill proposal exists at `docs/research/W2-55-backfill.md` with the three sections, one row per register entry at the ticket's base (the ids of `docs/DECISION_REGISTER.md` as `w2/integrate` holds it), each with a domain from the list, a scope, a lands-in, a status and a reason; the amends-and-refines section; a repeatable sample; and the ticket's branch changes nothing in `docs/DECISION_REGISTER.md` against its merge base with `w2/integrate` (S6). These cases read the tree they run in; before the engineer has written the file they are red.
5. KPI 5 and failure 3: the propagation check finds a test, code, a skill, a brief, a non-closed ticket's KPI, the prompt and the path map that enforce a superseded decision, by id and by recorded value, naming both decisions and the place with its line; a kept place with its reason gives no finding; a place that cites the successor is updated; a changed entry's id alone is no finding; a closed ticket is not searched. **Its first fixture is the sweep of 2026-10-20:** W1-49's two window cases and W2-59's three earlier cases, reproduced in a planted repository from the sweep's description (S3).
6. KPI 7: `gov context --in-force --json`: one line per entry in force, in register order, beginning with its id; superseded and done entries left out with their count; a changed entry names what changed it; generated from the register (a change to the register changes the digest after the store is loaded again); no register named gives an empty digest; an unreadable named register refuses; `gov context` with no ticket and no `--in-force` is refused (S5).
7. KPI 6 (W2-61's measure after the merge) is the lead's own measurement: write no test for it; the README says so.

Edge cases worth a test: an entry tagged with two places; `none` as lands-in on an entry in force (a finding) and on a done one (none); `SUPERSEDED by` an id the register does not hold.

## What you write

- Only inside `tests/acceptance/W2-55/` in this worktree. No throwaway implementation is left in the tree. If the KPIs require revising an earlier ticket's acceptance test, do not revise it: name it (file, case, why) in your return.
- In proportion (STANDARD, DEC-221): every KPI line's success and failure plus the key edge cases; no combinatorial expansion. Behaviour through the public interfaces above, never internals. Deterministic, no network: no vector is built (the semantic route is unavailable and gives no hit, as W2-87's tests do), no reranker loaded. Each child-process call has a time limit.
- A `README.md` that maps each KPI line to its tests and gives the expected red reason of each, and says how the tests reach the code of the tree they run in.
- The test module names begin `test_w2_55_`; no test package or module may shadow a standard-library module; a `conftest.py`, if any, only for this folder.
- **Red first:** run `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55-tests/src TMPDIR=/tmp/gov-os-lead-W2-55 python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider -o tmp_path_retention_policy=failed` to its end (never `-x`); they fail for the reason the README states (the base has none of the new behaviour), and none fails for a defect of the test itself (a collection error, a typo, a missing fixture).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence).

## Commit

Commit only `tests/acceptance/W2-55/`, in one commit, with the trailers in the final block:

    git commit -m "W2-55: acceptance tests (independent test designer)" --trailer "Task: DAEO-arrl" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-791, DEC-825, DEC-866, DEC-983" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After the commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commit's hash (12 digits); the test count; the KPI lines with their tests; the red result as you saw it (counts, and the reason for each failing group); every earlier test the KPIs would revise, with its reason; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; any P-R1 result you were served; any package.

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
