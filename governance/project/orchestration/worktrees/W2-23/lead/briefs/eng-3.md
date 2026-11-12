# Brief: engineer, DAEO-kmcr (W2-23), FULL — the CTO's run-2 decisions (resume run, eng-3)

Budget: projection 6 USD. Class C2. Keep your context short: read only what this change needs; cut long outputs to
head and tail.

You are a fresh engineer for ticket DAEO-kmcr (W2-23). You work only in `/home/usain/gov-os-worktrees/W2-23` on branch
`w2/W2-23` (DEC-963). The ticket's code is built and its independent acceptance tests pass. The CTO decided two
packages (recorded at the end of the ticket, "Delegated ... run 2's packages", and in Interface item 5); you carry out
those two and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23`, `w2/W2-23`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` (Interface item 5 and the last
  "Delegated" paragraph are what changed). The context packet (`gov context`, built by the lead):
  `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/context-eng.json`.
- **Writes:** only `src/gov/adapters/**`, `tests/unit/adapters/**`, `tests/unit/adopt/test_safety.py`,
  `fixtures/adopt/**` (to move its files out), and scratch under your `TMPDIR`. Never `git add -A`.
  **Never read `tests/acceptance/W2-23/**`** (DEC-820, DEC-1063); the test designer revises the acceptance side.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src`. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -c "import gov; print(gov.__file__)"`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). Command forms: no `$(…)` or variable as a write target, no here-document, no
  `bash -c`; scripts as files under your sandbox `TMPDIR`. Foreground only. No reset, checkout, clean, amend, rebase,
  push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The change

1. **P-W2-23-4 (b): no compaction threshold (DEC-838: every session uses its model's full window; no launch sets a
   compaction threshold).** `src/gov/adapters/merge.py:30` reads
   `AUTO_COMPACT = {"CLAUDE_CODE_AUTO_COMPACT_WINDOW": "300000"}`, and `merge_settings` (~line 87) forces it into
   `env`. Make it `AUTO_COMPACT = {}` with a one-line comment naming DEC-838. The merged `.claude/settings.json` keeps
   Interface item 5's other rules unchanged: keys merged key by key, the programme's keys and list entries first in
   their order, generated keys and hook entries after; an `env` block merged with the programme's own entries first and
   any generated entries after. No `env` key is added when neither the programme nor the generated settings hold one
   (an empty block carries nothing). No compaction key or value appears anywhere in `src/gov/adapters/` afterwards
   (grep `COMPACT`). Update the unit assertions that expect the entry (`tests/unit/adapters/test_generate.py` ~lines 75
   and 110) to the new behaviour, and add one assertion that the merged settings hold no key matching `AUTO_?COMPACT`.
2. **P-W2-23-6 (b): the fixture programme moves under `tests/unit/adapters/fixtures/programme/`.**
   `fixtures/adopt/programme/` (5 tracked files: `.rulesync/rules/overview.md`, `AGENTS.md`, `CLAUDE.md`, `README.md`,
   `claude-settings.json`) is in no namespace of this repository's path map, which turns two repository-wide checks
   red (W1-08 `test_every_tracked_path_matches_exactly_one_namespace`, W2-91 `test_every_tracked_path_is_in_one_namespace`).
   Move it with `git mv fixtures/adopt/programme tests/unit/adapters/fixtures/programme` (content byte for byte; no
   other path-map change), so `fixtures/adopt/` holds no tracked file. Update every reference: `FIXTURE` and the
   docstring in `tests/unit/adapters/test_generate.py` (~lines 3, 19), `tests/unit/adopt/test_safety.py` (~line 291),
   and any other Grep finds for `fixtures/adopt` under `src/` and `tests/unit/`. Make sure pytest collects nothing new
   from the moved folder (it holds no `test_*.py`; add no `__init__.py`).

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/unit/adopt tests/unit/adapters -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
   (no test name of yours may contain `real`, `green_here` or `time_limit`): all pass; quote the last line.
2. `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/acceptance/W1-08/test_w1_08_path_map.py -q -p no:cacheprovider -o tmp_path_retention_policy=failed -k "every_tracked_path"`
   — run it after your commit (it reads tracked paths); quote the last line.
3. Commit only your paths:

       git commit -m "W2-23 (DAEO-kmcr): no compaction threshold in the merged settings (P-W2-23-4 (b), DEC-838); the fixture programme moves under tests/unit/adapters (P-W2-23-6 (b))" --trailer "Task: DAEO-kmcr" --trailer "Role: engineer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- src/gov/adapters tests/unit/adapters tests/unit/adopt/test_safety.py fixtures/adopt

   Then quote `git log --oneline -2` and `git status --short`. (The acceptance case on the compaction entry is red
   until the test designer's revision is merged; that is expected and not yours.)

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `gov.__file__` line, the two last lines, the commit hash with its trailers. Also the
refusals met (time, form, reason).
