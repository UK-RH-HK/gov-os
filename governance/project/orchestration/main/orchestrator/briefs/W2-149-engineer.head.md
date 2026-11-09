# W2-149 — the engineer's brief: build the launch script to the stated interface (DAEO-52ku)

You are the engineer for **W2-149** (`.tickets/DAEO-52ku.md`: read it in full, with its body's "Readings settled by
the CTO"; reading 1 corrects LAUNCH-SPEC's canary): the independent sessions' launch script, which builds one walled
folder per job (writer, checker, auditor, labeller) from an owner-approved brief and template, chooses the content by
rule from a seed recorded first, guards the wall's settings with a canary, starts one closed headless `claude -p`
session in it, delivers its product by its own code, and returns only counts (the owner's DEC-1101 (2)-(3) step 2,
DEC-1109 (2)). Read `.gov-runtime/scratch/ref/LAUNCH-SPEC.md` in your worktree in full: its §1 to §5 are the
specification, its §6 the KPI lines. The ticket's KPI lines S1 to S21 and its ten failure lines are what you build to.
Profile FULL: every check fails closed; a refusal never leaves a half-built wall.

The independent test designer has written `tests/acceptance/W2-149/` (@CASES@). Its README states the interface the
cases call; the CTO hands you that section below, **from the start** (the spec, not the tests), so you build to it
without reading the cases.

**Your job:**
1. **Build `governance/project/orchestration/tools/indep_launch.py`** to the interface below, with the counts schema
   and the four kinds' result schemas in `governance/project/orchestration/tools/indep-schemas/`. Standard library,
   PyYAML and `git` only; no `gov` import (the CTO runs it standalone). It reads the walls' template
   (`governance/project/indep-walls/`: `kinds.yaml`, `settings.json.tmpl`, `wall_hook.py`, `CLAUDE.md.tmpl`,
   `tree-exclude.txt`, `README.md`) from the repository at `--commit` and never changes it. The reference builder
   `.gov-runtime/scratch/ref/build_wall.py` in your worktree shows LAUNCH-SPEC's B1 to B6 as the rehearsal built them
   (a reference, not the script: its arguments are not the interface).
2. **The canary (ticket reading 1):** its target file lies in its own temporary folder, which the canary's command adds
   with `--add-dir` (otherwise the wall's flags), so Claude Code's `--restricted` alone would allow the Read and only the
   wall's settings and hook can refuse it. A Read not in `permission_denials`, a canary that errors, times out or whose
   output cannot be read: code 16, no real session.
3. **Your own unit tests** in `tests/unit/orchestration/test_w2_149*`, and the evidence record
   `docs/changes/W2-149-evidence.md`: what you built, the counts, every red named, and what only the CTO can run
   outside your sandbox (the live cases: a real canary and a real session).

**Nothing live:** you never open the real `~/gov-os-eval/`, `~/gov-os-runs/`, `~/gov-os-wall-trees/` or `~/.claude/`,
and never start a real `claude` session (a stub on PATH in your tests). The CTO runs the live cases outside the sandbox.

## Where you work
- `/home/usain/gov-os-worktrees/W2-149`, branch `w2/W2-149` (from `w2/integrate`, with `w2/W2-149-tests` merged in).
  Your paths are the ticket's `allowed_paths`: `governance/project/orchestration/tools/indep_launch.py`,
  `governance/project/orchestration/tools/indep-schemas/**`, `tests/unit/orchestration/test_w2_149*`,
  `docs/changes/W2-149-evidence.md`.
- **You never read `tests/acceptance/W2-149/`** (G-14; DEC-820 (c)): only `gov accept`'s results. **The exclusion line
  (DEC-1093 (2)), by base name:** every recursive grep carries `--exclude-dir=W2-149`; every Grep or Glob call that
  could reach the folder carries `!tests/acceptance/W2-149/**`; find carries `-path '*/W2-149' -prune`. Start your
  searches from relative paths inside your worktree (`.`, `governance/`, `src/`), never from its absolute path (grep's
  `--exclude-dir` would skip the worktree itself, which is also named `W2-149`). If a search shows you a line of the
  cases anyway, stop reading it and say so in your return.
- **The template folder's name and the guard:** `indep-walls` is under the sets root's hidden glob, and the guard's line
  rule refuses a Bash line that names it next to a path. Read its files with the Read tool; never name the folder in a
  Bash command line (your code builds the name itself).
- You may read any code and record in your worktree: the ticket, `ACT-INDEP-WALLS-1.md` under
  `governance/project/orchestration/packages/`, the template, `governance/project/path-map.yaml` (`sets_root`,
  `sets_root_hidden`: the hidden part's walk for S18), `.claude/hooks/pretooluse.py` (S19: your documented lines must
  pass it; read how its line rule and its walk work), and `.gov-runtime/scratch/ref/` (`LAUNCH-SPEC.md`,
  `REHEARSAL.md`, `build_wall.py`, `walls_check.py`).

## Verify
- Through `bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh`,
  with `PYTHONPATH=/home/usain/gov-os-worktrees/W2-149/src`: your unit tests; then
  `python3 -m gov.cli.main accept W2-149 --root /home/usain/gov-os-worktrees/W2-149` (counts per line, results only).
  Name every red with its cause; a case that cannot pass in your sandbox (say why) is run by the CTO outside it.
- **Commit as you go**, each part as it passes, so a session that ends early leaves its work committed.

## Rules
- The hidden-half rule: never open anything under `~/gov-os-eval/`, `~/gov-os-runs/`, or any `hidden`,
  `memory-verdict` or `memory-verdict-2` folder of a real tree. No GPU, no model, no network, no installs, no service.
- DEC-1080: Read and Grep tools; one simple command per Bash call; no `cd … &&` chains. Search again once
  (DEC-1092 (1)) if needed.
- Do not merge `w2/integrate`. Never touch `tests/acceptance/**`, `.tickets/` or `.claude/`.
- Waits and stops by pid or pgid only, never a name match (L-0075), in your code and your session.
- **Commit** on `w2/W2-149` with
  `--trailer "Task: DAEO-52ku" --trailer "Implements: DEC-1101" --trailer "Role: engineer" --trailer "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"`.
- Before you end, every run you started has finished.

## Return
Your whole return is your session's **final message**, in full (the launcher keeps it in this worktree's
`.gov-runtime/scratch/lead/log/W2-149-engineer.json`; it is the record): the twelve labelled fields of `EMG-common.md`
(sandbox and `ps` checks first), what you built, `gov accept W2-149`'s counts per line, the unit counts, every red
named, and any place where the interface and a KPI line disagree (the KPI line wins: say so, with the case's failure
message).

---

# The interface the acceptance cases assume (the designer's README, as written)

