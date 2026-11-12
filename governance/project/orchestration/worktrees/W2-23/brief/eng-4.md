# Brief: engineer, DAEO-kmcr (W2-23), FULL — S3 round 2 fix, R1 and R2 (resume run 4, eng-4)

Budget: projection 2 USD. Class C2. Keep your context short: read only what this change needs; cut long outputs to
head and tail.

You are a fresh engineer for ticket DAEO-kmcr (W2-23). You work only in `/home/usain/gov-os-worktrees/W2-23` on branch
`w2/W2-23` (DEC-963). The ticket's code is built; the independent review (round 1) failed S3 on two findings, R1 and
R2, and the CTO decided the fix round (ticket, last paragraph "Delegated ... run 3's P-W2-23-7 (a)"). You fix R1 and
R2 in one function and nothing else.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-kmcr`: (a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-kmcr','w').write('x')"` must FAIL;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the file
or (b) failed, stop there and return (delete nothing). Then read that file (its Engineer paragraph applies) and
`EMG-common.md` beside it.

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-kmcr`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-23`, `w2/W2-23`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-kmcr.md` (Interface item 6; the last
  "Delegated" paragraph). The context packet (`gov context`, built by the lead):
  `/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/brief/context-eng.json`.
- **Writes:** only `src/gov/adopt/safety.py` and `tests/unit/adopt/test_safety.py`, and scratch under your `TMPDIR`.
  Never `git add -A`. **Never read `tests/acceptance/W2-23/**`** (DEC-820, DEC-1063); the test designer's new S3
  cases are merged into this branch and you run them, but you do not open them.
- Every run: `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src`. Quote
  `PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -c "import gov; print(gov.__file__)"`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). Command forms: no `$(…)` or variable as a write target, no here-document, no
  `bash -c`; scripts as files under your sandbox `TMPDIR`. Foreground only. No reset, checkout, clean, amend, rebase,
  push, merge or install.
- Refused twice for the same call: stop and say so; never work around a refusal. On an authentication error return
  `AUTH_REQUIRED`.

## The change: `safety.citations` (`src/gov/adopt/safety.py`, about lines 278-317)

- **R1 — a folder or `../` tail citation that ends a sentence is missed.** The folder pattern's lookahead
  `(?![\w./*?\[-])` (~line 291) and the relative-tail pattern's `(?![\w.-])` (~line 287) both reject a following `.`,
  so `citations('The old store is legacy/memory.', ['legacy/memory/decisions/leg-001.md'], [])`,
  `'See legacy/memory/.'` and `'See ../memory/index.md.'` (store `legacy/memory/index.md`) return `[]`, while the same
  with a comma or a space after are found. Make a `.` that ends the citation (followed by whitespace, end of text, a
  closing quote or bracket, or other sentence punctuation) no part of the path and no bar to the match, as the glob
  form already does (`_AFTER_GLOB`, commit 7a74947a6). A `.` followed by more path characters still blocks
  (`legacy/memory.db`, `legacy/memory/.hidden`, `../memory/index.md.bak` stay not found as folder / tail). `found`
  holds the citation without the stop.
- **R2 — the store's folder is taken per file.** `folder = parts[:-1]` is each file's own parent, so a store whose
  files all sit in subfolders (`.claude/memory/2025/a.md`, `.claude/memory/2026/b.md`) is not found when cited by
  `.claude/memory/`. The CTO's reading (P-W2-23-7 (a)): "the store's folder" is **the deepest folder holding all the
  store's files, and each folder between it and a file** (so for `notes/memory/2025/q1/a.md` and
  `notes/memory/2026/b.md`: `notes/memory`, `notes/memory/2025`, `notes/memory/2025/q1`, `notes/memory/2026`). A folder
  above the store's folder (`notes/`) is not the store's folder. When the store's files share no folder at all, keep
  today's rule (each file's own parent folder). Each folder form keeps today's shape (with or without a trailing `/`;
  a one-segment folder needs its `/`) and R1's stop rule. What `cites` names for a folder hit is your choice within
  the existing output shape (`{"cites", "form", "found"}`); the caller is `src/gov/adopt/legacy.py:146,155` — keep
  its contract.
- Do not touch the other forms (R3 — leading-wildcard and brace globs — stays out on purpose), nor any other function.
- Update the docstring's list if its words change.

## Unit tests (`tests/unit/adopt/test_safety.py`, beside the existing `test_s3_*` cases)

Add cases for: each R1 text above found (form and `found` without the stop) and the `.db` / `.hidden` / `.bak`
controls not found as folder or tail; R2's nested store found by `notes/memory/`, `notes/memory` mid-sentence,
`notes/memory/2025/`, and `notes/memory.` at a sentence end, and **not** by `notes/`; a store with no shared folder
keeps today's behaviour. Every existing case stays as it is and passes. No test name containing `real`, `green_here`
or `time_limit`.

## Check and commit

1. `env HOME=/home/usain/gov-os-worktrees/W2-23/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-23/src python3 -m pytest tests/unit/adopt tests/unit/adapters tests/acceptance/W2-23 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`:
   all pass; quote the last line. (If the merged acceptance S3 cases are not yet on the branch, say so; the lead
   checks them after.)
2. Commit only your paths:

       git commit -m "W2-23 (DAEO-kmcr): A8 citations: a folder or ../ tail ending a sentence is found; the store's folder is the deepest folder holding all its files and each between (R1, R2; P-W2-23-7 (a))" --trailer "Task: DAEO-kmcr" --trailer "Role: engineer" --trailer "Implements: DEC-729, DEC-1052, DEC-954, DEC-315, DEC-1112" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- src/gov/adopt/safety.py tests/unit/adopt/test_safety.py

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the `gov.__file__` line, the run's last line, the commit hash with its trailers. Also
the refusals met.
