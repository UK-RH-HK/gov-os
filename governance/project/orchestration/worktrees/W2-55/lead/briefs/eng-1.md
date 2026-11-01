# Brief: engineer, DAEO-arrl (W2-55), profile STANDARD, run 1

You are a fresh engineer. Ticket: `DAEO-arrl` (`W2-55`, "Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see"), profile STANDARD. You work only in the worktree `/home/usain/gov-os-worktrees/W2-55` on branch `w2/W2-55`. You build the ticket to its specification and its KPIs, never to the tests.

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
- **Disk and scratch (DEC-898):** your share of the ticket's budget is 10 GB and 500,000 files and folders, outside the tracked tree. Use `TMPDIR=/tmp/gov-os-lead-W2-55` for your runs unless the sandbox sets its own temp folder (keep that one). Keep pytest's own retention; never a per-run `--basetemp`. Remove what you make as soon as it is not needed.
- **Never `gov rebuild --no-embeddings`.** Do not rebuild the store yourself unless you must; if you do, `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src flock /tmp/gov-os-rebuild.lock python3 -m gov.cli.main rebuild --json`.
- Run everything in the foreground, one command after another; return only after your commit exists. No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase, no push, no merge. Install nothing (a needed install is a P1 in your return). No subagents that write. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`. Never edit `.tickets/`, `docs/DECISION_REGISTER.md`, the plan files or `governance/project/path-map.yaml`. Never run `gov close`, `gov adopt` or `gov pause`.
- Never ask or notify the owner (no question box, no `owner-ping`); a question is a package in your return.
- Your temporary folder may be removed when your session ends: everything the lead needs is in your final message.

## What you read

- The ticket file `.tickets/DAEO-arrl.md` (read-only): its seven success KPI lines and four failure lines and its `allowed_paths`; its card in `docs/plan/WAVE_2_WBS.md` §2 (`#### W2-55`).
- The decisions, in `docs/DECISION_REGISTER.md`: DEC-791 item 1, DEC-825 items 2 and 4, DEC-866, DEC-851, DEC-786, DEC-833 item 3, DEC-941, DEC-952 item 5, DEC-953 item 7, DEC-982, DEC-983, DEC-135 (proportion).
- `governance/project/orchestration/packages/SWEEP-2026-10-20.md` (KPI 5's first fixture), `governance/project/orchestration/packages/SMART-WORK-1.md` (practice 15), `governance/project/orchestration/DECISIONS-IN-FORCE.md` (the hand-made digest that `--in-force` generates from the register), `docs/assessment/2026-10/B-memory-retrieval.md` (Q05, F4).
- The code: `src/gov/decisions/` (W2-03's checker), `src/gov/context/` (`__init__.py`, `command.py`, `context_check.py`), `src/gov/retrieve/command.py`, and what they use (`src/gov/store/loader.py`'s register entries, `src/gov/retrieval/retrieve.py`, `src/gov/retrieval/authority.py`'s entry mapping, `src/gov/cli/main.py`'s output envelope).

The specification below fixes the public forms. It is the same text the test designer has.

{{SPEC}}

## What you write

- Only inside the ticket's `allowed_paths`: `src/gov/decisions/**`, `src/gov/context/**`, `src/gov/retrieve/**`, `template/governance/kernel/schemas/decision*`, `tests/unit/decisions/**`, `docs/research/W2-55-backfill.md`.
- **Shared files:** `src/gov/retrieve/**` is shared with W2-13 (on the critical chain): touch only the decisions filter in `src/gov/retrieve/command.py`, and keep it small. **Never touch `src/gov/retrieval/**`** or the path map. `src/gov/context/**`: the decisions filter and `--in-force` only.
- W2-03's `gov.decisions.check(root)` keeps its codes and its results (S2): five earlier suites and the strict close read it.
- A `gov` command that is new would need recording outside your paths: `--in-force` is an option of the existing `gov context`, and the two register checks are module commands of `gov.decisions`; if you find you need anything outside your paths, return it as a package.
- **The backfill (KPI 4, S6):** a proposal only, `docs/research/W2-55-backfill.md`, for every entry of the register; nothing written to the register. Make it with a script you keep (in `src/gov/decisions/` if it is a reusable product proposer for an adopted register, or under `.gov-runtime/scratch/eng/` if it is a one-off) and state in the file how it was made. Its reasons must be honest: a heuristic proposal says it is one.
- **KPI 5 on this repository:** when the propagation check is built, run it on this worktree (`cd /home/usain/gov-os-worktrees/W2-55 && PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -m gov.decisions.propagation`) and give its findings in your return (counts by old decision and the first lines). A finding is a report, not a change outside your paths. Also run the register check (`python3 -m gov.decisions.tags`) here and give its count (the register has no tags yet: it is expected to fail on every entry until the accepted backfill is applied).
- Builder tests in `tests/unit/decisions/` (your own test-driven development), as regression evidence only.
- Proportion (DEC-135): no code for edge cases beyond the KPI lines. Never make a check fail open: a register that cannot be read refuses, never passes; each failure KPI must still refuse. Estimate: about 150 lines of code, plus the backfill record.
- **The acceptance tests (DEC-963):** the independent test designer wrote them from the same specification; your lead has already merged them into this worktree (`/home/usain/gov-os-worktrees/W2-55/.gov-runtime/scratch/lead/TESTS-READY` names the commit; 76 tests, red on the base). Build to the specification first. **Commit your work before you run any long suite.** Then run them once your build is ready, reading results only (`gov accept` has not landed; use `PYTHONPATH=/home/usain/gov-os-worktrees/W2-55/src python3 -m pytest tests/acceptance/W2-55 -q -p no:cacheprovider --tb=no -rfE -o tmp_path_retention_policy=failed`, to its end, never `-x`; read only the names, pass or fail and the one-line failure messages, never the source). You may run them again after a fix, reading results the same way. A test you think is wrong is returned as a package, never worked around; you never bend the code to a test against the specification.
- **Temporary folders in the sandbox:** keep the sandbox's own `TMPDIR`; do not set `TMPDIR` yourself (`/tmp/gov-os-lead-W2-55` is not writable inside the sandbox, and pytest then writes its temp folders into the worktree). If you see a `pytest-of-*` folder appear in the worktree, say so. If the Write tool refuses `.gov-runtime/scratch/eng/`, put your scripts in your session's own scratchpad instead.
- **DEC-866:** when something you touch still enforces a superseded decision, do not fix it silently and do not bend the code to it: name it in your return (old decision, new decision, file and line).

## Commit

Commit only your paths, with the trailers in the final block (DEC-182, DEC-927 item 2: `Implements:` holds only decision ids the register holds):

    git commit -m "<subject>" --trailer "Task: DAEO-arrl" --trailer "Role: engineer" --trailer "Implements: DEC-791, DEC-825, DEC-866, DEC-983, DEC-786, DEC-851" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

The git hooks are uninstalled until W2-08; never `--no-verify`, never `core.hooksPath`. After each commit, show `git log --oneline -2` and `git status --short`.

## Return

Your commits' hashes (12 digits); the files changed; the lines added and removed; the builder tests and the acceptance tests you ran with their results; KPI 5's findings on this repository and the register check's count; the sandbox check; the `gov.__file__` line; whether you used `gov retrieve` (and how many queries); the read refusals you met; anything you were refused or could not settle, as a package.

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
