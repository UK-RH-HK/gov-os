Step 0, before any work: the sandbox check in /home/usain/gov-os-worktrees/W2-149-sgx/.gov-runtime/scratch/brief/EMG-d4b-launched.md, reported first in your return (launch_worker.sh).

# W2-149 — the engineer's brief, set-up A's wiring, the finish (DAEO-52ku)

You are a fresh engineer for **W2-149** (`.tickets/DAEO-52ku.md`; the lines S16, S20, S22 to S28 and the new failure
line, each `[changed, DEC-1112 (3)]`). The interface is `.gov-runtime/scratch/lead/INTERFACE.md`; the five briefs are
in `.gov-runtime/scratch/ref/sgx1-briefs/`. **A short pass: finish what the last engineer's session left.** Its session
ended on a network error (EAI_AGAIN) at 02:26 UTC, after it had committed the build.

## Where it stands (the lead's measure, 09:3x UTC, at `1f6051e12` with its uncommitted edit)
- Commit `1f6051e12`: the set-up A flows in `indep_launch.py`, the confined rule script (code 18), the five result
  schemas and the counts schema's numbers, `kinds.yaml` and `tree-exclude.txt`, unit tests. Since then the lead merged
  `w2/integrate` in (`74dcbd3d2`).
- `gov accept W2-149`: 135 passed, 2 failed, 12 skipped. Outside the sandbox with the 9 `bwrap` cases: 144 passed,
  2 failed. The 2 reds are S16's writer case (both params). They are **a test defect, not yours**: the case's helper
  never skips the wall's own tar. A fresh test designer is fixing it in parallel; it reaches you when the lead merges
  it. Change nothing for it.
- Unit tests: 81 passed, counting the uncommitted edit.

## What to do
1. **The uncommitted edit** in `tests/unit/orchestration/test_w2_149_setup_a.py` (11 lines in, 6 out): read it, keep it
   if it is right, finish it if it is not, and commit it.
2. **The documented lines:** the module docstring's set-up A lines name `governance/project/indep-briefs/sgx1-<name>.md`.
   The real paths are `governance/project/indep-briefs/sgx1/<name>.md` (`labeller`, `labeller-2`, `writer-tuning`,
   `writer-heldout`, `overlap-auditor`). Correct them; S19's guard-line cases must still pass.
3. **The evidence:** a section "Set-up A's wiring (DEC-1112 (3))" in `docs/changes/W2-149-evidence.md`. It covers what
   changed and where (functions and lines), the confinement (how `bwrap` and the limits stop a file read, a socket, a
   process, a runaway), the template's two files with their sha256s, the script's sha256, and the tests.
4. **Read your build once against the five briefs** for anything the tests do not reach: each brief's inputs exactly,
   its deliveries, its result forms. Fix only what is wrong, and say what you checked.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149-sgx`, branch `w2/W2-149-sgx`, head `74dcbd3d2`. Your paths are the ticket's
  `allowed_paths`.
- **You never read `tests/acceptance/W2-149/`.** You see only `gov accept`'s results and failure messages.
- **The exclusion line:** recursive grep carries `--exclude-dir=W2-149`; Grep and Glob carry
  `!tests/acceptance/W2-149/**` (a separate pattern).
- Edit the template files with Edit or Write. Never name the template's folder in a Bash line. Stage with `git add -u`.

## Verify
Run everything through the heavy slot `EMG-common.md` names, with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149-sgx/src`,
your sandbox's TMPDIR, a scratch HOME with `.local` linked in, and `PYTHONUSERBASE=/home/usain/.local`:
1. `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149-sgx`. Expect every line green
   except S16's 2 writer cases (above), with the live and `bwrap` cases skipped.
2. `tests/unit/orchestration/test_w2_149*`.

## Rules
- The hidden-half rule of `EMG-common.md`. Never run the script against the real `~/gov-os-eval`, `~/gov-os-runs`,
  `~/gov-os-wall-trees` or `~/.claude`. No real `claude` session. No GPU, network or installs.
- Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`. **DEC-1080:** one simple command per Bash call. Waits and
  stops by pid only. Do not merge `w2/integrate`.
- **Commit** on `w2/W2-149-sgx` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1112, DEC-1113" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Report your scratch size.

## Return
In your final message:
- the twelve labelled fields of `EMG-common.md`, first, as labelled lines;
- the commits;
- `gov accept` per line;
- the unit counts;
- the script's and the two template files' sha256s.

Refused twice for the same call: stop and say so; no third try.
