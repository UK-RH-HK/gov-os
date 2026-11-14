# Brief: engineer, W2-116 (DAEO-f58b) pass 2b: S2 (the two daily refresh times and `gov status`) and R2-F3

You are the engineer for ticket DAEO-f58b (W2-116), profile STANDARD. Pass 1 (S1, S3, S4, S5, F1-F3) is merged on
this branch. This pass builds S2 and R2-F3 against the interface stated below, which the CTO decided (DEC-1157 (12),
8801ffd17). An independent test designer writes the acceptance cases in parallel from the same text; they are merged
into your branch when you are between batches (the lead tells you; then make them pass). Never read the designer's
worktree (/home/usain/gov-os-worktrees/W2-116-tests) or its branch before the lead merges it (DEC-820).

## Where you work
- Your worktree: /home/usain/gov-os-worktrees/W2-116, branch w2/W2-116 (at e51b1fdf6). One writer per worktree: you.
- Write only inside the ticket's paths, and for this pass only these:
  `src/gov/rebuild/integration.py`, `src/gov/rebuild/command.py`, `src/gov/status/**`,
  `src/gov/retrieval/retrieve.py`, `src/gov/retrieve/command.py`, `src/gov/launch/store.py` (only if the config
  reader belongs there), `governance/project/rebuild.yaml`, `docs/changes/W2-116-evidence.md`,
  `tests/unit/rebuild/test_w2_116*`, `tests/unit/status/test_w2_116*`, `tests/unit/retrieval/test_w2_116*`.
  Never `tests/acceptance/` (the designer's).
- Scratch: /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/eng/ (checkpoint, notes).
- Search with the Read and Grep tools; no `gov retrieve`, no `gov context` in the sandbox (DEC-1065). If a search does
  not answer, search once more in other words; then answer from both or say "not found".

## What to build
1. S2 in `gov.rebuild` (`integration.py`, `command.py`): the `integration_refresh` config reader with
   `REBUILD_CONFIG_INVALID`, the clock (`GOV_NOW`), `--when-due` with its due rules, `not_due`, the record
   `<link>.refresh.json`; exactly as the interface below states.
2. `gov status`'s `integration_store` part (`src/gov/status/command.py`, and a new module under `src/gov/status/` if
   cleaner), with the stale rule; update the module docstring's list of parts.
3. R2-F3 in `src/gov/retrieval/retrieve.py` (about 20 lines): the token carries the resolved store folder's mark and is
   refused on another folder. Keep every existing continuation case green (`tests/unit/retrieval/`, W2-138's).
4. This repository's line in `governance/project/rebuild.yaml`, with a comment like the file's others:
   ```yaml
   integration_refresh:
     branch: w2/integrate
     after_nightly:
       verdict: .gov-runtime/scratch/orchestrator/log/nightly/*/run.txt
       latest: "10:00"
     second: "18:00"
   ```
   It lands in the same commit as the code that reads it (Q2 (b)), so no reader meets the key before its code.
   Check first that nothing else that reads `rebuild.yaml` refuses an unknown key (grep the readers:
   `gov.launch.store.configured`, `gov.rebuild.seed._configured`, `gov.config.loader`, the W2-32 `embed_headers`
   reader); name any that does.
5. Unit tests under `tests/unit/rebuild/test_w2_116_*`, `tests/unit/status/test_w2_116_*`,
   `tests/unit/retrieval/test_w2_116_*`: the due rules on a planted clock (edge minutes, yesterday's times, a verdict
   file without a verdict), each invalid-key refusal, the stale rule, the token mark.
6. The evidence record `docs/changes/W2-116-evidence.md`: add a "Pass 2b" section: what was built, the design of the
   due rules, the record, and the stale rule, each against the interface; the commands run and their results.

## How to run pytest (every run)
```
env TMPDIR=/tmp/w2-116-eng PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(`mkdir -p /tmp/w2-116-eng` first.) A whole-folder run adds `-m "not local_only" -k "not real and not green_here and
not time_limit"` and `HOME=/home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/empty-home`. Put a multi-line
command in a script under your scratch and run it with `bash`. Run at least `tests/unit/rebuild`, `tests/unit/status`,
`tests/unit/retrieval`, `tests/unit/retrieve` and `tests/acceptance/W2-116/` before you return. A resource gate's
refusal is a wait (DEC-1146). The three `test_cto_safety_nets.py` live-inbox cases and `test_w2_23_space.py:94` are
known reds: name them, never fix them. Another ticket's case red on this branch: name it with file:line, do not fix it.
Never open the evaluation sets' root or any hidden or memory-verdict folder.

## Commit (in batches; one commit per coherent step)
```
git -C /home/usain/gov-os-worktrees/W2-116 commit -m "<subject>" --trailer "Task: DAEO-f58b" --trailer "Role: engineer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- <paths>
```
`Implements:` only ids from the ticket's `sources:` (DEC-1109, DEC-1112, DEC-983, DEC-982, DEC-963, DEC-966, DEC-1014,
DEC-1015, DEC-1083, DEC-1087, DEC-719, DAEO-kia7). An id you need that is not there goes in `discoveries`.

## Rules
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).
- A gap or contradiction in the interface: build what is stated, name the gap in `unresolved`; never widen the paths.
- Keep a checkpoint in your scratch (STATE / HEAD / NEXT), rewritten at each commit.
- After each commit, write one line `BATCH <n> committed <hash12>` to
  /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/eng/batches.txt; if the file
  /home/usain/gov-os-worktrees/W2-116/.gov-runtime/scratch/eng/HOLD exists, stop editing and wait (check it every
  minute with `test -f`, through a script with a bounded loop, at most 20 minutes) until it is gone: the lead is
  merging the tests into your tree. Then `git log -1` and continue with the acceptance cases included.

## Return (your last message)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES, ESCALATION) /
work_completed / files_changed / evidence (each suite's counts) / tests / discoveries / risks / lessons /
proposed_decisions / unresolved / recommended_next_action. Then `commits:` with hash12 and subject.

