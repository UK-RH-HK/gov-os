# W2-149 — the engineer's brief, set-up A's wiring (DAEO-52ku)

You are a fresh engineer for **W2-149** (`.tickets/DAEO-52ku.md`). Read the ticket: the changed lines **S16** and
**S20**, the new lines **S22 to S28**, the new failure line (each marked `[changed, DEC-1112 (3)]`) and its last note
("Set-up A's wiring placed here"). Then read the **interface section** of the test designer's README, copied for you
as `.gov-runtime/scratch/lead/INTERFACE.md`: you build to it exactly (places, file names, the template's `briefs:`
keys, the environment overrides, the new exit code 18).

## The point
The merged launch script (`governance/project/orchestration/tools/indep_launch.py`) refuses the five owner-approved
set-up A briefs at stage 10, and it has none of the flows set-up A needs. **The five briefs' bytes are fixed** (approved
once by the owner, hashed). The template supplies what they lack, and the script gains set-up A's flows. The CTO's
rulings (delegated, DEC-1112 (3)):
- the seeds stay the script's own draw (S6; the declaration's amendment A5);
- the labeller kind runs set-up A's flows only, so the old labeller flow (the sealed folder's `rulebook.md`,
  `corpus/actions-r1/-r2.jsonl`, `labels/<run>.jsonl`, the `random.Random` overlap) goes;
- the overlap auditor never appends to `AUDITS.log` (the memory writers' last audit stays theirs);
- a rule script that cannot run confined refuses with the new code 18;
- `tree-exclude.txt` gains `governance/project/indep-briefs/**`, and `kinds.yaml` gains a `model` per kind
  (`claude-opus-5-5`) and the `briefs:` entries for the five set-up A briefs (ids `sgx1-labeller`, `sgx1-labeller-2`,
  `sgx1-writer-tuning`, `sgx1-writer-heldout`, `sgx1-overlap-auditor`; `sample: 0` for the labellers and the auditor;
  each entry's `tree_exclude` the guard's and launcher's code), as the interface says.

References in your worktree (untracked): `.gov-runtime/scratch/ref/sgx1-briefs/*.md` (the five briefs in full: their
inputs, outputs and result forms are your spec for S24 to S28), `.gov-runtime/scratch/ref/INTERFACE-DRAFT.md` (the
lead's draft; the README's interface section wins where they differ), `.gov-runtime/scratch/ref/LAUNCH-SPEC.md`.

## What to build
- The script's set-up A flows (S16, S20, S22 to S28); the four result schemas and the counts schema's new numbers
  in `indep-schemas/`; the two template files. Keep every other kind's behaviour byte for byte (the memory writer,
  checker and auditor flows; S1 to S15, S17 to S19, S21).
- **The confined rule script (S25):** `bwrap` with every namespace unshared and no network, read-only binds of the
  interpreter's own files only (the pin's python is a link to `/usr/bin/python3.12`: bind what that needs, nothing of
  HOME, the sets root, the runs folder, the repository or the wall), `--die-with-parent`, `--new-session`, rlimits
  (CPU, address space, file size 0, open files), a wall-clock cap, a stdout cap, `-I`; its process group stopped by
  pgid on any exit. A failure, a timeout or invalid output is 18, never a pass. The interface asks that a fork or an
  exec inside fails: the designer notes this needs more than the namespaces (a process limit set inside the sandbox,
  or a seccomp filter). Since `bwrap` cannot run in your sandbox, make the confinement code small and plain, and give
  your own unit tests of it the same `bwrap` opt-in, so they run outside the sandbox too.
- Your unit tests (`tests/unit/orchestration/test_w2_149*`), and a "Set-up A's wiring (DEC-1112 (3))" section in
  `docs/changes/W2-149-evidence.md`: what changed, where, the tests.
- Update the module docstring's documented command lines to set-up A's real lines (one per brief; `--set tuning` or
  `held-out`), so S19's guard-line case still covers every documented line.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-sgx`, branch `w2/W2-149-sgx`, made from the designer's branch
  `w2/W2-149-sgx-tests` at `59030819b` (`w2/integrate` at `ce1e9d0df` with the designer's cases).
- Your paths are the ticket's `allowed_paths`.
- **You never read `tests/acceptance/W2-149/`.** You see only `gov accept`'s results and failure messages.
- **The exclusion line:**
  - recursive grep carries `--exclude-dir=W2-149`;
  - Grep and Glob carry `!tests/acceptance/W2-149/**`. A brace glob does not exclude: pass a separate pattern.
- Edit the two template files with the Edit or Write tool. Never name the template's folder in a Bash line (the
  guard's line rule for the sets root's walled folder matches its name): stage with `git add -u` or `git commit -a`.

## Verify
Run everything through the heavy slot that `EMG-common.md` names, with
`PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src`, `TMPDIR=/tmp/gov-os-emg-w2-149-sgx-engineer`, a scratch
HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`:
1. `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx`. Every line green but the
   live cases and the 9 cases marked `bwrap`, which skip: a nested `bwrap` cannot start in your sandbox ("No
   permissions to create new namespace"). The lead runs those 9 outside the sandbox (`GOV_W2_149_BWRAP=1`) after your
   return and sends a fresh engineer any red. Today: 76 passed, 61 failed, 12 skipped.
2. `tests/unit/orchestration/test_w2_149*`.

Commit as you go.

## Rules
- The hidden-half rule: never open the evaluation sets' hidden half or the run folders outside this repository, as
  `EMG-common.md` names them. Never run the script against the real `~/gov-os-eval`, `~/gov-os-runs`,
  `~/gov-os-wall-trees` or `~/.claude`; no real `claude` session.
- No GPU, network or installs. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- Scratch budget: 20 GB and 1,000,000 files and folders outside the tracked tree; remove temp trees as you go.
- **DEC-1080:** one simple command per Bash call. Waits and stops by pid only, never a name match. Do not merge
  `w2/integrate`. Use `gov retrieve` for what you need to know; code questions through the code graph's own traversal,
  small and targeted.
- **Commit** on `w2/W2-149-sgx` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size (`du -s --inodes`, `du -sh`).

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md` (task, status, work_completed, files_changed, evidence, tests,
  discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action), first, as labelled lines;
- the commits;
- `gov accept W2-149` per line;
- the unit counts, with every red named and whether it was red before;
- the new template files' sha256s and the script's sha256.
Refused twice for the same call: stop and say so; no third try.
