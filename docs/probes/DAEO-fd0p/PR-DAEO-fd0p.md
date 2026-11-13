---
type: probe
task: DAEO-fd0p
reviewer_session: 33f2b54b-891e-4b48-88ea-ed1ecb9add24
implementer_session: "eng-3 64613a2c-585d-42c0-9660-1c944d5cc325 (2c2302c4b); td-2 12f37ea5-d41d-44cb-9f19-30f87c1a8705 (e1e170d35)"
reviewer_wrote_nothing: true
commissioned_by: orchestrator
judged_by: orchestrator
judgement: pass
probed_commit: 14c9e7a36eb200e3fd7c1203b54f628aa87bd6e0
decisions_applied: [DEC-1079, DEC-1052, DEC-1073, DEC-1112, DEC-495, DEC-1153, DEC-1154, DEC-1156]
---

# Probe record: W2-160 (DAEO-fd0p), narrow independent check (DEC-1154) of the run-3 changes (DEC-1156 (1), (6))

- **What was checked.** Review round 1 passed at `eb6d0cc07643` (0 blocking; its record is now
  `PR-DAEO-fd0p-round-1.md`). The owner then decided two changes for this ticket (DEC-1156 (1), (6)). Under
  DEC-1154 (1) they had a narrow independent check of those two changes only, at head `14c9e7a36`:
  - ROUTE-1 (a), commit `2c2302c4b` (engineer): `tests/unit/session_watch/test_route.py:19` asserts the two-path
    `ACT_PATHS` of `src/gov/session_watch/command.py:17` (DEC-1153 (2)).
  - W2-159's F4 revision, commit `e1e170d35` (test designer; `Rewrite-Reason:` DEC-1156 (6)), merged at
    `14c9e7a36`: `tests/acceptance/W2-159/test_f4_scope.py` judges only on `w2/W2-159` and skips elsewhere with its
    reason. On a planted `w2/W2-159` branch with a change outside W2-159's paths, it still fails.
- **The verdict.** Reviewer session 33f2b54b-891e-4b48-88ea-ed1ecb9add24 (independent-auditor, Opus high,
  read-only): **pass**, 0 blocking.
- **The lead's triage.** N-1 is non-blocking and is recorded as a residual, not fixed on this branch. The judgement
  in `test_f4_scope.py:52-53` reads the git config of whoever runs pytest. The planted repositories do not. The
  reviewer found no key that changes these four git calls' output, and any such change would show red, not pass.
  W2-170's F5 model has the same gap.
- **The round-1 rows that stay recorded and are not fixed.** R1-1, R1-3, R1-5, R1-6 and R1-10 are out of this run's
  scope (see `PR-DAEO-fd0p-round-1.md`).
- **The lead's checks at `14c9e7a36`:**
  - `lead_verify.sh`, after `rebuild_slot.sh`: GREEN. The parallel phase ran 5413 tests: 0 failed, 0 errors,
    8 skipped. The serial phase selected 0 entries. One of the skips is W2-159's F4 real case, whose reason reads
    "F4 judges only the branch w2/W2-159; this is the branch w2/W2-160: not judged here". The other seven skip
    for reasons unrelated to this ticket: local_only, bwrap, and the CTO's scratch tools.
  - F4: `git diff --name-only --no-renames <merge-base with w2/integrate>...HEAD` lists 21 paths. Each one is in the
    ticket's allowed_paths or in `tests/acceptance/W2-160/`.

The reviewer's return follows verbatim. Its verdict block decides.

## Narrow check (14c9e7a36): the reviewer's return

The narrow check passes with no blocking findings. Both changes do what DEC-1156 (1) and (6) asked; one minor point is recorded as N-1.

**Step 0, the sandbox check (launch_worker.sh):**
- (a) The test write to `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-fd0p` failed as it should (`OSError: [Errno 30] Read-only file system`), and no file was left.
- (b) `echo sandbox-trial | git hash-object -w --stdin` worked (`1ae28402a…`), and `git update-index --refresh` worked.
- The `ps` check found no ollama or llama-server process.
- Identity: `git rev-parse HEAD` = `14c9e7a36eb200e3fd7c1203b54f628aa87bd6e0`, and `git status --porcelain` is empty at start and end.

```verdict
ticket: DAEO-fd0p
head: 14c9e7a36
round: narrow check (DEC-1154) of DEC-1156 (1), (6)
verdict: PASS
blocking: 0
```

```verdict
{"kpis": [{"kpi": "F4 (ticket failure line 4, W2-159's F4 revision and the ROUTE-1 (a) assertion)", "verdict": "pass", "findings": [{"id": "N-1", "scope": "in", "ordinary_work": "no", "consequence": "other"}]}]}
```

Findings are classified as 0 blocking and 1 non-blocking (ordinary work: no). I recommend a PASS and the land.

## Findings

**N-1 — non-blocking** — `tests/acceptance/W2-159/test_f4_scope.py:52-53` (the `env` built inside `judge_f4_paths`)
- **What it does:** the planted cases build their repository with a temporary HOME. The judgement step then runs git with the HOME of whoever runs pytest. So the true home's global git config is read by the four judging calls (`rev-parse`, `symbolic-ref`, `merge-base`, `diff --name-only`). The old real case blocked this with `GIT_CONFIG_GLOBAL=/dev/null` and `HOME=tmp_path`. The model in W2-170's F5 has the same gap, and is weaker still, because it does not strip `GIT_*` variables.
- **What I did:**
  - Ran `git -c color.ui=always -c color.diff=always -c diff.relative=true -c core.quotePath=true -c core.quotePath=false diff --name-only --no-renames 2c2302c4b~1 2c2302c4b | cat -v`. The output was a plain path with no escape codes. Colour, relative paths and quoting do not change the name-only output.
  - `git config --global --list` holds only `github.user`, `init.defaultbranch`, `user.email` and `user.name`. None of these affects the four judging calls.
- **Ordinary work: no**, because changing the result would take a hand-set global config key built to alter the output of `diff --name-only`, and I found no such key.
- **Consequence: other.** If anything it would show red where it should be green (fails closed); it would not fail open.
- **What would be right:** the judgement also runs with an empty HOME, or with `GIT_CONFIG_GLOBAL` set to an empty file, as the planting does.
- **What would reverse it:** a git config key that changes the output of these four commands.

## What I probed and found sound

**1. ROUTE-1 (a), commit 2c2302c4b (engineer)**
- `git show eb6d0cc07643:tests/unit/session_watch/test_route.py | diff - …` shows exactly one changed line, line 19. The old and new `act_paths` assertions are shown in the brief's diff, and nothing else in the file changed.
- It uses exact tuple equality, so it is no weaker than before, and it matches `src/gov/session_watch/command.py:17` character for character.
- `git diff 70d0b5a8e 14c9e7a36 --name-only` lists only the two files in scope.

**2. W2-159's F4 revision, commit e1e170d35 (test designer), merged at 14c9e7a36**
- **Rewrite-Reason:** the trailer is present, citing DEC-1156 (6) and PKG-W2-160-KNOWN-1, with `Role: independent-test-designer` and `Task: DAEO-fd0p`.
- **Same judgement on `w2/W2-159`:**
  - The old matcher was `fnmatch` plus a prefix check on `tests/acceptance/W2-159/`. The new one is `gov.close.select.match` (which calls `gov.util.patterns._match_pattern`) plus `acceptance_tests.path + "/**"`.
  - For W2-159's patterns (two `/**` folders, four literal paths, no `?` or `[`) both matchers give the same regular expressions.
  - The list is now read with YAML instead of a regex; for this ticket both give the same six entries.
  - Two changes make it stricter:
    - `--no-renames` now also lists the old name of a renamed file.
    - `core.quotePath=false` stops non-ASCII names from being quoted, so they are no longer falsely red.
  - A missing `w2/integrate` or ticket file now skips instead of failing, as in the model. The brief allows this.
  - Read-only cross-check on the real branch: W2-159 is merged, so its tip is the merge-base. The diff is empty and both the old and new judgements find nothing outside.
- **The skip cannot hide a red on `w2/W2-159`:**
  - It skips only when `w2/integrate` is missing (branches are shared across worktrees), when the ticket file is missing (it is tracked on `w2/W2-159`: `git cat-file -e w2/W2-159:.tickets/DAEO-6lid.md` succeeds), or when HEAD is not `refs/heads/w2/W2-159`.
  - The branch is read from the tree under test (`gov.__file__`), not from the current directory or an environment variable.
  - `GIT_*` variables are stripped, so a `GIT_DIR` set by a hook cannot redirect the check.
- **The planted cases cannot pass vacuously:**
  - `test_f4_the_planted_paths_are_outside_and_inside_the_ticket_s_paths` checks against the real ticket that OUTSIDE (`docs/changes/W2-160-evidence.md`) is not allowed and INSIDE (`src/gov/session_watch/inside_w2_159.py`) is.
  - The outside case must raise an AssertionError that names the path.
  - If one of these cases ever skipped, it would show as SKIPPED, not PASSED. In this run all six planted cases passed.
- **Writes:** only `tmp_path/home` and `tmp_path/repo`. The judging calls only read; a diff between two commits does not touch the index. The home's config is covered by N-1.

## Probe run
The brief's exact command (heavy slot, empty HOME, the exclusions):
- `heavy_slot: all 3 slots taken; waiting`, then `10 passed, 1 skipped in 0.49s`.
- The skip was `test_f4_scope.py:66: F4 judges only the branch w2/W2-159; this is the branch w2/W2-160: not judged here`. That is the 4 test_route cases plus 6 of F4's 7, with the real F4 case skipped.
- The `-m`/`-k` exclusions deselected nothing in these two files.

---
- task: DAEO-fd0p
- status: done (PASS, 0 blocking)
- work_completed: Step 0 sandbox and ps checks; narrow independent check of ROUTE-1 (a) and W2-159's F4 revision at 14c9e7a36
- files_changed: none (one git object `1ae28402a…` written by Step 0's mandated `hash-object -w`; working tree clean)
- evidence: the diffs eb6d0cc07643..14c9e7a36 of the two files; commit trailers; the pytest run above; the matcher comparison; the read-only judgement on `w2/W2-159`'s tip
- tests: 10 passed, 1 skipped (the real F4 case on `w2/W2-160`, expected); the exclusions deselected nothing here
- discoveries: N-1 (the planted judgement reads the caller's global git config); the W2-170 F5 model has the same gap and also does not strip `GIT_*`
- risks: none blocking
- lessons: none
- proposed_decisions: none
- unresolved: none
- recommended_next_action: lead writes this as the probe record (the old one to `-round-1.md`) and lands; N-1 as a recorded row
- guard_refusals: none
