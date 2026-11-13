# Brief: engineer, DAEO-ifgf (W2-121b), FULL, class C2 — S5: the template's default working size (eng-3)

Budget: projection 1 USD. A one-line change and one unit case. Keep your context short.

You are a fresh engineer for ticket DAEO-ifgf (W2-121b). You work only in `/home/usain/gov-os-worktrees/W2-121b` on
branch `w2/W2-121b`. Part b's dispatcher work is built and reviewed; the owner widened the ticket by one KPI line
(S5, DEC-1149 (2)). You never read or edit `tests/acceptance/`.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the
file or (b) failed, stop and return (delete nothing).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-ifgf`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b`, `w2/W2-121b`).
- Read the ticket's last two sections ("Widened (DEC-1149 (2) ...)" and "P-W2-121b-2 (a)") and its last success line:
  `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`.
- **Writes (these two files only):** `src/gov/resources/config.py` (the one entry below, nothing else) and the new
  file `tests/unit/dispatch/test_w2_121b_config_default.py`. Scratch files go under
  `/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/eng/`.
- **Every pytest** goes through the heavy slot, with a TMPDIR outside the repository and outside `~/gov-os-runs`
  (e.g. `/tmp/eng3-DAEO-ifgf`, created first), in this form (create the empty-home folder first if absent):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FOLDER or file> -q --tb=line -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  A busy heavy slot is a wait, not a refusal: retry.
- No `gov retrieve` or `gov context`; Read and Grep only (search again once, in other words). No `$(…)` or variable
  as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean, amend, rebase, push,
  merge, stash or install.
- Refused twice for the same call (guard, sandbox or hook): stop and say so; never reach the same effect by another
  command, form or file. On an authentication error return `AUTH_REQUIRED`.

## The change (S5)

KPI line S5: "The template's default `working_size_bytes` (a new machine's `gate.json`, `src/gov/resources/config.py`)
is 805,306,368 B (0.75 GiB per live session), dated 2026-11-12 with its source DEC-1149, as this machine's gate now
holds (ACT-P95-1)." Check: "a unit case reads `config.template()` and finds working_size_bytes 805306368 with the
date and the source naming DEC-1149".

1. Test first: write `tests/unit/dispatch/test_w2_121b_config_default.py` with one case that imports
   `gov.resources.config`, calls `config.template()` and asserts the `working_size_bytes` entry is
   `{"value": 805306368, "date": "2026-11-12", ...}` with `"DEC-1149"` in its `source`. Run it; it must be red
   (value 2191601664, date 2026-10-29). Quote the failure line.
2. In `src/gov/resources/config.py`, `template()` (about line 220), change only the `working_size_bytes` entry to
   `_entry(805_306_368, "2026-11-12", "DEC-1149 (1), (2): 0.75 GiB per live session, from the lead-memory ledger (ACT-P95-1)")`
   (or equivalent wording that names DEC-1149 and ACT-P95-1). No other line changes.
3. Run your case (green), then `tests/unit/dispatch`, `tests/unit/resources` and `tests/acceptance/W2-20` with the
   pytest line above. Quote each run's last line. Any red there that is not caused by your change: name it, do not
   fix it.

## Commit

    git commit -m "W2-121b: the template's default working_size_bytes 805,306,368 B (0.75 GiB per session, S5)" --trailer "Task: DAEO-ifgf" --trailer "Role: engineer" --trailer "Implements: DEC-1088" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/resources/config.py tests/unit/dispatch/test_w2_121b_config_default.py

(DEC-1149 is not in the ticket's `sources:`; do not put it in `Implements:`. Name it in `discoveries`.)
Then quote `git log --oneline -2` and `git status --short` (expect empty).

## Return (your last message; nothing else is read)

The twelve fields, each a labelled line ("none" where nothing):
- task
- status (DONE, PACKAGES, ESCALATION or AUTH_REQUIRED)
- work_completed
- files_changed
- evidence (the sandbox check result, the red line, and each pytest run's last line)
- tests (counts per suite)
- discoveries
- risks
- lessons
- proposed_decisions
- unresolved
- recommended_next_action

Then `commits:` (hash12, subject, and the trailers as committed) and `guard_refusals:` (none, or time | form | reason).
