You are a fresh independent test designer (MR-3). Ticket: DAEO-0rfi (W2-54), profile FULL. You work only in the worktree `/home/usain/gov-os-worktrees/W2-54` on branch `w2/W2-54`. You write the ticket's acceptance tests from its KPI lines and its sources, before the implementation, and you show them red.

## Standing rules (read first)

- First run `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer` and `DAEO-0rfi`) and `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-54` and `w2/W2-54`). If anything differs, stop and say so.
- Run everything in the foreground, one command after another: your session ends with your last message, and nothing started in the background is ever read. Return only after your commit exists.
- **The code under test (DEC-732):** in this worktree, **every test run and every `gov` command used for verification runs this worktree's own `src/`**: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src` set **per command** (never in a session's `--settings` env). Your verification shows it with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -c "import gov; print(gov.__file__)"`, quoted in your return; it must point into this worktree.
- The project's test command, for your suite: `PATH=/home/usain/.nvm/versions/node/v22.23.3/bin:$PATH PYTHONPATH=/home/usain/gov-os-worktrees/W2-54/src python3 -m pytest tests/acceptance/W2-54 -q -p no:cacheprovider -rs`, run to its end, never with `-x`.
- No `git checkout` of another commit, no `git reset`, no `git clean`, no amend, no rebase in this worktree. Reading another branch's file with `git show <commit>:<path>` is allowed; checking it out is not.
- Run no glob, no search and no listing over `governance/project/`: name the files you need there one by one (DEC-508). Never read `.claude/settings.json` or `.claude/settings.local.json`, in this worktree or anywhere. Nobody reads anything under `~/.claude/`.
- Never read, print, search, diff or copy the held-out file under `governance/project/`, and never type its path (DEC-525). Never read or name the qualification oracle.
- **The workbench (DEC-723):** never write in `~/gov-os-workbench`, and never list, glob or search it. Dev-tier tests use `GOV_DEV_TIERS` by name only and clone into a temporary folder.
- Never copy the repository or a folder of it (no `cp -r`, `rsync`, `git archive`, `git worktree` or `git clone` of this repository or a folder of it) anywhere. A throwaway stand-in imports the installed package or copies single named files, never `governance/project/`; a test that needs a repository builds a temporary one from scratch. No clone, copy or file of a programme is ever put under a `.gov-runtime/` folder (DEC-673).
- Inside a launched session `.gov-runtime/freeze` shows as a placeholder device file whether or not a flag exists: conclude nothing from it.
- Never run `gov rebuild --no-embeddings`. Do not run `gov rebuild` at all: the lead has built this worktree's store with a full rebuild before starting you. Never run `gov close`, `gov adopt` or `gov pause`.
- The guard refuses here-documents and unresolvable variables in Bash write targets: write files with the Write and Edit tools and literal absolute paths. No subagents. Install nothing: a tool you need is returned as a package. No push, merge, rebase or tag. Never write `.gov-runtime/**` outside `.gov-runtime/scratch/`.
- Never edit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` (nobody in this ticket edits it).
- The git hooks are uninstalled. Never `--no-verify`, never `core.hooksPath`.
- Your temporary folder is removed when your session ends (DEC-386): everything the lead needs is in your final message.
- If the guard or the sandbox refuses something you needed for the ticket, do not work around it: return it as a package. **Refused twice for the same call: stop and say so; no third try** (AR-6).

## What you read

- The ticket file `.tickets/DAEO-0rfi.md` (read-only): its KPI lines, its `allowed_paths` and its sources. Its card in `docs/plan/WAVE_2_WBS.md` §2 (W2-54) and §0 (rules for every ticket).
- The sources: DEC-768, DEC-626, DEC-441, DEC-565 in `docs/DECISION_REGISTER.md`, and CAP-33 in `docs/contract/contract.yaml`.
- The decisions that apply, in the register: DEC-595 (a check's declared time limit; a check that states none gets the runner's 60 seconds), DEC-600, DEC-285, DEC-628, DEC-221, DEC-462, DEC-136, DEC-491, DEC-732.
- The list rows the ticket takes in: none.
- The public interfaces the ticket must work with:
  - `gov context <ticket> --json` (and its `--budget`), whose packet carries `items`/`authority`, `supplementary`, `dropped` and `hash`; its supplementary part comes from the retrieval (`gov retrieve`, the public retrieval entry in `src/gov/retrieval/`).
  - The context-reproducibility check, run as its declaration says (`template/governance/kernel/checks/context-reproducibility.yaml`: `python3 -m gov.context.context_check`, in the project root).
  - `gov check --json` and its handling of a declaration's `timeout-seconds` (`src/gov/cli/checks.py` documents the declaration's fields).
  - The core-schema check (`python3 -m gov.check.schema`, in the project root): its findings and their codes as they are produced today for other types.
  - W2-02's held branch, read only with `git show 2a35fd7b:<path>`: `template/governance/kernel/schemas/audit-report.schema.json`, and the `audit-report` lines of `src/gov/check/schema.py` there (`git diff b644d28a 2a35fd7b -- src/gov/check/schema.py`). Read that diff for what the type must be, never to learn how to implement it.
  - Earlier suites' support files, for how a suite here builds a temporary repository and runs this worktree's code: `tests/acceptance/conftest.py`, and as examples `tests/acceptance/W1-24/` (the context packet's first suite) and `tests/acceptance/W2-53/`.
  You read no private part of the code to be written to learn what a test should expect.

## The behaviour to test

In the words of the KPI lines (the ticket file holds them in full):

1. **One hash per ticket.** Two computations of any ticket's context in one store give one hash and the same packet: the `dropped` list comes out in one stable order with a full tie-break, **whatever order the retrieval returns tied items in** (items tied in score, items with the same id, an empty supplementary result, a store whose index is missing). Measured on `w2/integrate` at `c9537e39`, the check failed on 15 tickets of this repository: the two computations gave the same dropped items in two orders. A test may control the order in which the retrieval returns items through the retrieval's public entry; it states the expected behaviour (the same packet and hash under any order of tied items), not a sort key or a name of the code to be written. A ticket whose context is otherwise unchanged keeps its contents: nothing is dropped or added by the fix.
2. **A declared time limit that fits the measured run.** The context-reproducibility declaration states `timeout-seconds` (as `retrieval-regression` and `secrets-indexing` declare theirs; without it the check gets 60 seconds, DEC-595). Measured alone at `c9537e39`: 122 seconds. The limit fits the run measured after the fix on this repository, and is not set so high that it hides a hang (decide a bound you can defend from the sources and state it in the README; if you cannot, return a package). The measurement (the run's seconds, the tickets measured, the machine's load) is recorded in `docs/changes/W2-54-CIT-E.md`, with the change. The declaration's other keys (`id`, `family`, `tier`, `severity: hard-block`, `command`, `enforces`) are unchanged: only the `timeout-seconds` line is added.
3. **Green here.** `gov check` gives context-reproducibility green on this repository (run in this worktree against the store the lead built).
4. **The `audit-report` type, exactly W2-02's.** Its schema file `template/governance/kernel/schemas/audit-report.schema.json` is byte for byte `git show 2a35fd7b:template/governance/kernel/schemas/audit-report.schema.json`. Core-schema holds a record of type `audit-report` to that schema as a standalone type (no shared frontmatter owed, DEC-441, DEC-565), and reads a record in `docs/audit/` that states no `type` as an audit report (DEC-626). Nothing of W2-02's other types comes with it: a record of type `close` or `adoption-verdict` is judged as core-schema judges an unknown type today, and no schema file for them is added. Core-schema is green on this repository with `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` untouched (its sha256 is `b14e17d6e71b2727c3cea123dec112fdccbeb27afc1f50b67f5e27294ecdac1d`, before and after).

Failure lines:

5. A context whose items or hash differ between two computations still fails the context-reproducibility check, naming the ticket.
6. A check that runs past its declared limit still fails; no hard-block check is weakened (DEC-768 item 4): nothing skipped, downgraded or excluded.
7. A record outside `docs/audit/` that states no `type` still fails core-schema; an audit report that lacks `milestone`, `commit` or `pack_sha256` fails it, naming the field (each of the three on its own).

## What you write

- Only inside `tests/acceptance/W2-54/`. No throwaway implementation is left in the tree.
- FULL: thorough; every KPI line's success and failure; no combinatorial expansion beyond what a KPI demands (DEC-221).
- Behaviour through public interfaces, never internals. Deterministic, no network. Tests that need a repository build a temporary one from scratch. Tests that read this repository (lines 3 and 4's "green here", the W1-43 hash, the declaration) read this worktree, and every subprocess they start runs this worktree's `src/` (DEC-732).
- A `README.md` in `tests/acceptance/W2-54/` that maps each KPI line to its tests, gives the expected red reason of each, and says how the suite makes sure it exercises this worktree's code (the `gov.__file__` line). Say which tests need this worktree's store and how long the slowest test runs.
- Red first: run the suite with the test command above, to its end; the tests fail for the reason the README states (tests of behaviour that already holds, such as line 6's or line 7's first half, may pass now: say which, and why they are there).
- An ambiguous KPI line or a dispute is never a guess: return it as a package (question, why now, options, impact, reversibility, cost, recommendation, confidence). If the KPIs require revising an earlier ticket's acceptance test, name it and return it as a package; do not edit it.

## Commit

Commit only your test paths, in one commit, with the trailers in the final block (DEC-182, DEC-476):

    git commit -m "W2-54 (DAEO-0rfi): acceptance tests" --trailer "Task: DAEO-0rfi" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-768" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"

Then check `git log --oneline -2` and `git status --short`.

## Return

One message, your last, complete in itself. **The twelve fields come first, each as a labelled line** (label at the start of a line, a colon, at least one word; "none" where there is nothing), and any machine-readable payload after them. Refused twice for the same call, stop and say so.

```
task: <what you were asked to do, in one line>
status: <DONE | PACKAGES | ESCALATION | ESCALATION_BLOCKED | LAUNCH_BLOCKED | LEAD_CHECKPOINT | AUTH_REQUIRED, and one line of why>
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

In the fields: your commit's hash; the test count; the KPI lines with their tests; the red reason as you saw it, per test; the `gov.__file__` line; any package.
