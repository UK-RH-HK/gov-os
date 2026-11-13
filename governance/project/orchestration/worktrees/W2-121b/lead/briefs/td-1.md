# Brief: independent test designer, DAEO-ifgf (W2-121b), FULL, class C2 — gov dispatch part b: landing, closes, the nightly hold, heavy steps (tests run, td-1)

Budget: projection 4 USD. Keep your context short: read only what the tests need; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-ifgf --role independent-test-designer` refuses this ticket with
CONTEXT_OVER_CEILING, 19988 of 6000 tokens; this brief and the ticket are your inputs.)

You are a fresh independent test designer (MR-3) for ticket DAEO-ifgf (W2-121b). You work only in
`/home/usain/gov-os-worktrees/W2-121b-tests` on branch `w2/W2-121b-tests` (DEC-963). The engineer will build in
`/home/usain/gov-os-worktrees/W2-121b`, which you never read or write. You write to the KPI lines and the Interface,
never to an implementation: there is none yet for part b. You may read part a's public surface and its acceptance
suite to learn how a planted project is driven: `tests/acceptance/W2-121/` (its `w2_121_support.py`: the `Project`
class, a planted git root with `governance/project/dispatch.yaml`, stubs, a planted `/proc` folder through
`GOV_RESOURCES_PROC`, `plant_process(argv)`, and how `gov dispatch tick` / `status` are run and the state folder
`.gov-runtime/dispatch/` read). The CTO's dispatcher `governance/project/orchestration/tools/dispatch/` is a reference
for meaning only, never a target: no test names it.

## Step 0, before any work: the sandbox check (report it first in your return)

(a) `python3 -c "open('/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-ifgf','w').write('x')"` must fail;
(b) `echo sandbox-trial | git hash-object -w --stdin` and `git update-index --refresh` must work. If (a) wrote the
file or (b) failed, stop and return (delete nothing).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-ifgf`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-121b-tests`,
  `w2/W2-121b-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-ifgf.md` (the four KPI lines and its
  `## Interface` section: binding). Part a's Interface: `.tickets/DAEO-cb2b.md`, its `## Interface` section (the
  state folder, `land.txt`, `land-done.txt`, `inbox/`, `status.json`/`status.txt`, the exit codes). The register
  (`docs/DECISION_REGISTER.md`, 1.6 MB): grep only by id (`### DEC-1007`, `### DEC-1014`, `### DEC-1018`,
  `### DEC-1008`, `### DEC-979`); the sources are the ticket's `sources:`.
- **Writes:** only `tests/acceptance/W2-121b/**`. No earlier suite is revised. Scripts, if any, as files under your
  TMPDIR.
- **Every pytest** goes through the heavy slot, with the sandbox's TMPDIR (outside the repository and outside
  `~/gov-os-runs`; check `echo $TMPDIR`), in this form:
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-121b-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-121b-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-121b -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create the empty-home folder first if absent). If the sandbox refuses the heavy slot, say so and run the same
  line without `bash .../heavy_slot.sh`. Tests that need a HOME of their own (the slots live in
  `$HOME/.gov-os/machine/slots/`) set it in the subprocess's environment to a folder under `tmp_path`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`.
  Foreground only. No reset, checkout, clean, amend, rebase, push, merge or install.
- No real model, embedder, `claude` or `gov close` is started: stand-ins only (stub scripts under `tmp_path`, planted
  `/proc` entries). Planted projects live under `tmp_path`; no test writes into this repository's tree. Keep the suite
  fast: each case a few seconds, no wall-clock wait longer than ~10 s.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file.
  A resource gate's refusal (memory, CPU, disk, heavy slot) is a wait: retry when it opens. On an authentication
  error return `AUTH_REQUIRED`.

## What to write: `tests/acceptance/W2-121b/`

Tests for the KPI lines **S1 to S4** of the ticket, each from its `Verify:` text, through the public surface:
`gov dispatch tick` and `gov dispatch status` (run as `python3 -m gov.cli.main dispatch ...` in a planted project
with your tree's `PYTHONPATH`, as W2-121's suite does), the state folder `.gov-runtime/dispatch/` and its
`status.json` / `status.txt`, and the one module function the Interface names
(`gov.dispatch.landing.commit_records`) for S2's "two record commits". Prefer your own `w2_121b_support.py`; you may
import W2-121's support module (it is merged and stable) rather than copy it, but never edit it.

## The interface both sides build to (the ticket's `## Interface`, binding; summarised)

- **S1, claim and batch.** A pass claims only when no landing of its own is unfinished, the root has no tracked change
  and is on `integration_branch`, no conflicting close, no nightly hold. Claim = atomic rename `land.txt` ->
  `land-claimed-<land id>.txt` (`<land id>` = `land-<UTC stamp>`) before the launch; lines whose `<W2>=<head>` is
  already in `land-done.txt` are dropped. Batch = `landing_command` (a `dispatch:` key, an argv list) with the token
  `{approvals}` replaced by one argument per line `<W2>=<head>` (appended at the end when the token is absent), run
  detached in the root, output `logs/<land id>`, exit code `logs/<land id>.exit` (in the state folder). A later pass
  finalises: one line per approval `<W2>=<head> <time> <exit code> <land id>` into `land-done.txt`, one inbox item
  `<land id>.land.txt` (lines `log: <land id>`, `W2: <ids space-separated>`, `status: landed` | `failed (exit N)`,
  `kind: land`), the claimed file removed. A line not of the form `<W2>=<12-hex>` is never sent and is named in the
  status.
- **S2, closes.** A running close = a process whose command line matches `job_markers["close"]` (a substring). Its
  tickets = its arguments equal to a W2 id or ticket id in the landing's set. It blocks only when one is in the set, or
  while it commits its records: the root's `.git/index.lock` exists, or the root's tracked changes all lie under
  `close_record_paths` (list of path prefixes, default `[]`). Any other close does not block.
  `gov.dispatch.landing.commit_records(root, paths, message, trailers, attempts=3, wait_s=2)` commits, retrying while
  another holds `index.lock`; two at once both land (one retried).
- **S3, nightly hold.** `nightly_hold: {from: "HH:MM", until: "HH:MM", marker: <path, relative to the root or
  absolute>}` (marker optional). From `from` (local time) no landing is claimed until `marker`'s mtime is later than
  today's `from`, or until `until` (a window with `from` > `until` crosses midnight). Without `marker`, until `until`.
  A landing already claimed is finalised as usual, never stopped. Status: `status.json` key `land_hold` and a
  `status.txt` line `land: held for the nightly until it starts (from HH:MM, at the latest HH:MM)`. Exit 0.
- **S4, heavy steps.** Heavy steps = `job_markers` kinds `test`, `rebuild`, `check`, `measure`. A heavy step is in a
  slot when it or an ancestor (by the parent pid in its `/proc/<pid>/stat`) is a slot's runner, read from
  `gov.resources.slots.holders()` (records `slot-<n>.json` with `{"slot": n, "pid": <runner pid>, ...}` in
  `$HOME/.gov-os/machine/slots/`, counted only while `slot-<n>.lock` is flock-held). Status: `heavy_steps:
  [{kind, pid, slot}]`; one with no slot adds a `findings:` entry `heavy step outside a slot: <kind> pid <pid>` (a
  finding shown, never a failed pass: the pass's exit code is unchanged by it).
- **Exit codes:** a landing held (busy, unclean tree, wrong branch, conflicting close, nightly) is exit 0, its reason in
  the status as `land: <reason>`.

## The lead's naming for what the Interface leaves open (both sides use exactly these)

- The landing command is a stub script under `tmp_path` that records its argv (one file per run) and exits with a code
  the test chooses (0 for `landed`, e.g. 3 for `failed (exit 3)`). "Goes as one batch" = one run of the stub whose
  arguments carry every approved `<W2>=<head>`. Finalisation happens on a later `tick` after the stub exits (poll with
  a bounded wait, as W2-121's `wait_for`).
- "Unapproved never goes": a W2 present in the planted project (worktree, ready line, ticket) but absent from
  `land.txt` is never in any stub argv; a malformed line (e.g. `W2-9=xyz`) is never sent and appears in `status.json`
  or `status.txt` (assert the W2 id or the line text is named; do not pin the wording).
- "Never twice": (1) after finalisation, re-planting the same `<W2>=<head>` in a new `land.txt` and ticking does not
  send it again; (2) the claim precedes the launch: when the stub runs, `land.txt` no longer exists and a
  `land-claimed-*.txt` does (let the stub record `os.listdir` of the state folder), and a second `tick` while the
  first batch still runs starts no second batch.
- Held reasons: assert exit 0, no stub run, `land.txt` still present (not claimed), and a `land: ` line in
  `status.txt` (and/or the reason in `status.json`); pin the reason's wording only for the nightly hold (its text is
  in the Interface). Unclean tree = a modified tracked file in the root; wrong branch = the root on another branch.
- A running close is a planted `/proc` entry (`plant_process`) whose argv contains the configured
  `job_markers["close"]` substring (e.g. `gov-close-stub`) plus a ticket argument: the W2 id (e.g. `W2-7`) or its
  ticket id (`DAEO-xxxx` from the planted `.tickets/`); cover both forms across the cases. "Committing its records":
  (a) a planted `.git/index.lock` in the root with a non-sharing close running; (b) with `close_record_paths:
  ["docs/records/"]`, tracked changes only under that prefix and a non-sharing close running. Each blocks. A close
  with no shared ticket and neither condition: the batch goes.
- Two record commits: in a planted git repository, two `commit_records` calls started at the same moment (threads or
  processes, each its own path) both land: two new commits, each path committed. "One retried": hold
  `.git/index.lock` yourself for about 1 s, start one `commit_records` call, remove the lock, and assert the commit
  lands (and the call took at least about the hold time). Pass `wait_s` small (e.g. 0.5) and `attempts` explicitly.
  Do not pin its return value (the Interface does not state one).
- Nightly hold: set `from` and `until` relative to the test's own local time with at least 5 minutes' margin (e.g.
  from = now - 30 min, until = now + 60 min, written as `HH:MM`). Cases: (1) inside the window, marker absent or older
  than today's `from` -> no claim, status names the hold (`land_hold` in `status.json`, the `status.txt` line with the
  two times); (2) marker's mtime set after today's `from` (`os.utime`) -> the landing is claimed; (3) no marker key,
  past `until` (e.g. from = now - 60, until = now - 10) -> claimed; (4) a landing already claimed (a first tick before
  the hold, a stub that waits on a release file), then the hold configured: the next tick finalises it once the stub
  exits. Where the local time is within 90 minutes after midnight or before it (the "today's `from`" and wrapping
  arithmetic would be ambiguous), skip the time-relative cases with that reason, or choose a window that crosses
  midnight explicitly and test it as such.
- Heavy steps: plant `job_markers` for `test`, `rebuild`, `check`, `measure` (distinct substrings), and planted `/proc`
  entries for each. For "in a slot": plant a runner process, write `slot-1.json` `{"slot": 1, "pid": <runner pid>}` in
  the HOME you give the subprocess (`<HOME>/.gov-os/machine/slots/`), hold `slot-1.lock` with `fcntl.flock` from the
  test for the case's length, and plant the heavy step with the runner as parent (the 4th field of its `stat`; you
  may write your own planting helper with a ppid argument). Assert `status.json`'s `heavy_steps` holds `{kind, pid,
  slot: 1}` for it. For "no slot": a heavy step with no runner ancestor -> `findings` holds `heavy step outside a slot:
  <kind> pid <pid>`, and the pass's exit code is what it is without that process. Cover all four kinds.

Write `tests/acceptance/W2-121b/README.md` mapping every KPI line (S1 to S4) to its tests **with full node ids**
(`test_<file>.py::test_<name>`, every item; the runner fails a line whose map names a test it cannot collect).

## Check and commit

1. Run your suite on this branch (today's integrated code, part a only) with the pytest line above. S1 to S4 should be
   red there (no landing, no `gov.dispatch.landing`, no `land_hold`, no `heavy_steps`). Quote the last line and each
   failure's one-line reason, grouped by KPI line; a case green on today's code checks nothing new: fix it or say why
   (a guard case such as "unapproved never goes" may pass vacuously today; pair it with a positive case in the same
   test so it is red until the landing exists).
2. Commit only your paths:

       git commit -m "W2-121b acceptance: landing hand-off, non-conflicting closes, the nightly hold, heavy steps in slots (S1-S4)" --trailer "Task: DAEO-ifgf" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1007, DEC-1014, DEC-1018, DEC-1008, DEC-979, DEC-989, DEC-1084" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-121b

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers, `du -sh` of your TMPDIR, and
`ps -eo pid,args | grep -iE "[o]llama|[l]lama-server"` (must show nothing of yours). In `tests`: the case count per
KPI line. Also the refusals met. Where the Interface is silent on something a test needs, choose the narrowest
reading, name it in `discoveries`, and never invent a refusal code or a wording the Interface does not give.
