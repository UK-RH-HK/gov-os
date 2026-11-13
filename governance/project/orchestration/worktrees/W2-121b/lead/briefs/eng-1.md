# Brief: engineer, DAEO-ifgf (W2-121b), FULL, class C2 — gov dispatch part b: landing, closes, the nightly hold, heavy steps (build, eng-1)

Budget: projection 8 USD. Keep your context short: read only what you need; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-ifgf --role engineer` is over its ceiling for this ticket; this brief and
the ticket are your inputs.)

You are the engineer for ticket DAEO-ifgf (W2-121b). You work only in `/home/usain/gov-os-worktrees/W2-121b` on branch
`w2/W2-121b`. You implement until the acceptance suite `tests/acceptance/W2-121b/` (48 cases, all red now, written by
an independent test designer) passes. You never edit the acceptance tests; if one is wrong against the ticket, say so
in your return (with the case, the ticket's line and why) and leave it red.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the
file or (b) failed, stop and return (delete nothing).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-ifgf`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b`, `w2/W2-121b`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md`: the four KPI lines S1 to S4 and its
  `## Interface` section are binding. Part a's Interface (the state folder `.gov-runtime/dispatch/`, `land.txt`,
  `land-done.txt`, `inbox/`, `status.json`/`status.txt`, `job_markers`, exit codes): `.tickets/DAEO-cb2b.md`, its
  `## Interface` section. Part a's code is `src/gov/dispatch/` (config, state, procs, status, run, command, ...):
  extend it, do not rewrite it; part a's suites (`tests/acceptance/W2-121/`, `tests/unit/dispatch/`) must stay green.
- The CTO's dispatcher `governance/project/orchestration/tools/dispatch/` is a reference for meaning only, never a
  target: never import it, never edit it, nothing in `src/` names it or this repository (all generic; every new key in
  `governance/project/dispatch.yaml`'s `dispatch:`).
- The register (`docs/DECISION_REGISTER.md`, 1.6 MB): grep only by id (`### DEC-1007`, `### DEC-1014`,
  `### DEC-1018`, `### DEC-1008`, `### DEC-979`).
- **Writes (allowed paths only):** `src/gov/dispatch/**`, `tests/unit/dispatch/test_w2_121b*`,
  `src/gov/resources/slots.py` (at most a read helper: the runner pids of the slots held, from `holders()`; no new slot
  kind; `src/gov/resources/command.py` stays untouched). Nothing else: not `tests/acceptance/`, not `docs/`, not
  `.tickets/`. Scratch files under `/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/eng/`.
- **Every pytest** goes through the heavy slot, with a TMPDIR outside the repository and outside `~/gov-os-runs` (the
  sandbox's TMPDIR; check `echo $TMPDIR`), in this form (create the empty-home folder first if absent):
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-121b/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <FOLDER or file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  If the heavy slot is busy (a resource gate), wait and retry: that is not a refusal. If the sandbox refuses the heavy
  slot itself, say so and run the same line without `bash .../heavy_slot.sh`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`.
  Foreground only. No reset, checkout, clean, amend, rebase, push, merge, stash or install.
- No real model, `claude` or `gov close` is started by your tests: stand-ins only.
- Refused twice for the same call (guard, sandbox or hook): stop and say so; never reach the same effect by another
  command, form or file (DEC-1142 (9)). On an authentication error return `AUTH_REQUIRED`.

## What to build (the ticket's `## Interface`, summarised; the ticket wins on any difference)

- **S1, claim and batch** (a new `src/gov/dispatch/landing.py` is the natural home, wired into the pass in `run.py`).
  A pass claims only when: no landing of its own is unfinished, the root has no tracked change and is on
  `integration_branch`, no conflicting close, no nightly hold. Claim = atomic rename `land.txt` ->
  `land-claimed-<land id>.txt` (`<land id>` = `land-<UTC stamp>`) *before* the launch; lines whose `<W2>=<head>` is
  already in `land-done.txt` are dropped. Batch = `landing_command` (argv list) with the token `{approvals}` replaced
  by one argument per line `<W2>=<head>` (appended at the end when the token is absent), run detached in the root,
  output `logs/<land id>`, exit code `logs/<land id>.exit`. A later pass finalises: one line per approval
  `<W2>=<head> <time> <exit code> <land id>` into `land-done.txt`, one inbox item `<land id>.land.txt` (`log: <land
  id>`, `W2: <ids space-separated>`, `status: landed` | `failed (exit N)`, `kind: land`), the claimed file removed. A
  line not of the form `<W2>=<12-hex>` is never sent and is named in the status.
- **S2, closes.** Running close = a process matching `job_markers["close"]`; its tickets = its arguments equal to a W2
  id or ticket id in the landing's set (map a ticket id to its W2 through `.tickets/` `external-ref:`/`wbs_id:` as the
  suite plants them). Blocks only when one is in the set, or while it commits its records: the root's `.git/index.lock`
  exists, or the root's tracked changes all lie under `close_record_paths` (list of path prefixes, default `[]`). Any
  other close does not block. `gov.dispatch.landing.commit_records(root, paths, message, trailers, attempts=3,
  wait_s=2)`: a commit that retries while another holds `index.lock`; two at once both land (one retried). The
  `trailers` argument: a list of `"Key: value"` strings (the suite passes `["Task: DAEO-test"]`); accept a dict
  `{Key: value}` too. Commit only the given paths (`git commit ... -- <paths>` after `git add`), and treat git's
  "index.lock exists" failure (on add or commit) as the retryable case.
- **S3, nightly hold.** `nightly_hold` gains an optional `marker` (a path, relative to the root or absolute): from
  `from` (local time) no landing is claimed until `marker`'s mtime is later than today's `from`, or until `until` (a
  window with `from` > `until` crosses midnight). Without `marker`, until `until`. A landing already claimed is
  finalised as usual, never stopped; starts and the inbox are not held. Status: `status.json` key `land_hold` and a
  `status.txt` line `land: held for the nightly until it starts (from HH:MM, at the latest HH:MM)`. Exit 0.
- **S4, heavy steps.** Heavy steps = `job_markers` kinds `test`, `rebuild`, `check`, `measure`. In a slot when it or an
  ancestor (parent pid from `/proc/<pid>/stat`, honouring `GOV_RESOURCES_PROC`) is a slot's runner, read from
  `gov.resources.slots.holders()`. Status: `heavy_steps: [{kind, pid, slot}]`; one with no slot adds a `findings:`
  entry `heavy step outside a slot: <kind> pid <pid>` (shown, never a failed pass: the exit code is unchanged).
- **Exit codes:** a landing held (busy, unclean tree, wrong branch, conflicting close, nightly) is exit 0, its reason
  in the status as `land: <reason>`.

Read `tests/acceptance/W2-121b/` (README.md maps each KPI line to its cases; `w2_121b_support.py` shows how a project,
the stub landing command, planted `/proc` entries and slots are planted) before writing code. Add your own unit tests
in `tests/unit/dispatch/test_w2_121b_*.py` for logic the suite does not reach (claim parsing, the hold window across
midnight, the ancestor walk). Keep `est_loc` near 500 lines of source.

## Check and commit (in batches; commit after each green batch)

1. Run `tests/acceptance/W2-121b`, then `tests/acceptance/W2-121` and `tests/unit/dispatch` (part a must stay green),
   with the pytest line above. Quote each run's last line.
2. Commit only your paths, with these trailers exactly:

       git commit -m "W2-121b: <what this batch does>" --trailer "Task: DAEO-ifgf" --trailer "Role: engineer" --trailer "Implements: DEC-1007, DEC-1008, DEC-1014, DEC-1018, DEC-979, DEC-989, DEC-1084" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- src/gov/dispatch tests/unit/dispatch src/gov/resources/slots.py

   (`Task:` is the ticket id DAEO-ifgf, never W2-121b; `Implements:` only ids from the ticket's `sources:`.)
   Then quote `git log --oneline -3` and `git status --short` (expect empty for tracked files).

## Return (your last message; nothing else is read)

The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES, ESCALATION,
AUTH_REQUIRED) / work_completed / files_changed / evidence (the sandbox check result; each pytest last line) / tests
(counts per suite) / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then
`commits:` (hash12 subject, trailers as committed) and `guard_refusals:` (none, or time | form | reason).
