# Brief: engineer, DAEO-mb2t (W2-124), STANDARD, class C2 — the semantic store's fail-named rule (build run 2, eng-1)

Budget: projection 5 USD. Keep your context short: read only what the change needs; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-mb2t --role engineer` refuses this ticket with CONTEXT_OVER_CEILING,
17598 of 6000 tokens; this brief and the ticket are your inputs.)

You are the engineer for ticket DAEO-mb2t (W2-124). You work only in `/home/usain/gov-os-worktrees/W2-124` on branch
`w2/W2-124`. An independent test designer writes `tests/acceptance/W2-124/` in parallel in another worktree, which you
never read; the lead merges it into your branch between your batches and tells you (resume) when it is there.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-mb2t`. If it fails, stop and return (delete nothing). Then read `EMG-common.md` beside it (its engineer
paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `engineer`, `DAEO-mb2t`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-124`, `w2/W2-124`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-mb2t.md`: its KPI lines (S1-S5, F1, F2), its
  `## Interface` and run 1's P2 and P3 at its end are binding. The register: grep only by id (`### DEC-1027`).
- **Writes (allowed_paths, nothing else):** `src/gov/rebuild/command.py`, `src/gov/adopt/stages.py`,
  `src/gov/close/rebuild_gate.py` (new), `tests/unit/rebuild/test_w2_124*`, `tests/unit/adopt/test_w2_124*`. No
  other file, no earlier test, no `tests/acceptance/`. If the change truly needs another file (for example
  `src/gov/adopt/safety.py`, `src/gov/close/*` beyond the gate file, or an earlier suite), stop and return PACKAGES
  naming it and why; W2-115 holds `src/gov/close`.
- **Every pytest** goes through the heavy slot, with the sandbox's TMPDIR (outside the repository and outside
  `~/gov-os-runs`; check `echo $TMPDIR`), in this form:
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-124/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-124/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create the empty-home folder first if absent). If the sandbox refuses the heavy slot, say so and run the same
  line without `bash .../heavy_slot.sh`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words (DEC-1065). No
  `$(…)` or variable as a write target, no here-document, no `bash -c`. Foreground only. No reset, checkout, clean,
  amend, rebase, push, merge or install. No real embedder in a test: stand-ins only.
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file.
  On an authentication error return `AUTH_REQUIRED`.

## What to build (the ticket's Interface, with the lead's naming for what it leaves open)

1. **Asked for** (in `gov.rebuild.command`): the semantic store is asked for exactly when `--no-embeddings` is not
   given AND the path map has a namespace with `embedding_policy: embedded` (`none_embedded(config)` is None and a
   path map exists). Otherwise `stores.semantic = {status: not_recreated, requested: false, reason}` and no embedder
   is called or started (S2). With `--no-embeddings` the reason names `--no-embeddings` (already so).
2. **Asked for and not recreated** (unavailable, hung past the endpoint timeout, failed part way; today these give
   `status: not_recreated` with a reason and an ok answer): `gov rebuild` raises `GovError("REBUILD_FAILED", message,
   {"store": "semantic", "reason": <reason>, "stores": <the stores dict>})`, exit 1, never an ok answer; no warm-base
   record (as today). The message holds the literal text `store: semantic` and the reason (the CLI prints
   `gov rebuild: REBUILD_FAILED: <message>`). Raise through `gov.close.rebuild_gate.check()` called on the result.
   `--integration` is out of scope (it already never switches to a build without its semantic store).
3. **`src/gov/close/rebuild_gate.py`** (new): `semantic_failure(result: dict) -> str | None` takes a `gov rebuild
   --json` envelope (`{"result": {...}}`) or its result (`{"stores": {...}}`) and returns why a semantic store that was
   asked for is not recreated, else None; its rule is the CTO's
   `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_semantic_check.py`
   (status not `recreated` and `requested` not `False`; an absent semantic entry is a failure). `check(result: dict)
   -> None` raises the `REBUILD_FAILED` of item 2. The close (`close/batch.py` `_rebuild` -> `command.run`) and the
   queue's prepare (`rebuild_slot.sh` -> `gov rebuild --json`) then fail through it: no edit to other close files.
4. **S5, read in the result (P2 (b))**: `gov rebuild` keeps exit 0 and `"ok": true` and its result carries
   `complete: <bool>` and `not_built: [{store, reason}]` for every store that was to be built and was not: no path
   map (the lexical index, and any other store that then builds nothing), no `.gitleaks.toml` (establish what each
   store does today without it, with the scan on: the stores that build nothing or are refused for it are named, the
   reason naming `.gitleaks.toml`), a store the path map calls for not built. A store with `requested: false` is never
   in `not_built`; `complete` is true exactly when `not_built` is empty. W2-26's finding 2 (an unadopted clone
   answering `"ok": true`) gives `complete: false` with its stores named.
5. **Adoption** (`gov.adopt.stages`): stage A6 catches `REBUILD_FAILED` whose details' store is `semantic` and
   finishes; both the committed A6 record and the stage's `gov adopt --lite --json` result each hold
   `findings: [{code: "SEMANTIC_NOT_RECREATED", store: "semantic", reason: <reason>, command: "gov rebuild"}]`; the
   result's `rebuild` holds the stores from the error's details. Today `safety.migrate` commits the A6 record before
   `stages.rebuild` runs: order the rebuild and the record's commit **within `stages.py`** so the committed record
   holds the finding (for example by having the record's commit run the rebuild first); A6's other behaviour
   (resume, rollback, failed batches: W2-23's suites) stays as it is. Any other `REBUILD_FAILED` stays
   `INDEX_REFRESH_FAILED`. A8 (`legacy.retire`) is not changed unless it calls `stages.rebuild`; if it does, the same
   catch applies there.

Write unit tests for each item in `tests/unit/rebuild/test_w2_124_*.py` and `tests/unit/adopt/test_w2_124_*.py`.

## Earlier suites (P3: none is revised)

After your change, run these with the pytest line above and report each red by file and node id, with its one-line
reason: `tests/unit/rebuild tests/unit/adopt tests/unit/close tests/acceptance/W1-27 tests/acceptance/W1-41
tests/acceptance/W2-23 tests/acceptance/W2-122`. Do not edit any of them. Where a red comes from a project that
rebuilds for real with an embedded namespace and no embedder (the new rule working), name it as such; where it is a
fault of yours, fix your code. The lead takes the list of reds to the owner (widening is the owner's).

## Commit (your paths only; one or more commits)

    git commit -m "W2-124: <what>" --trailer "Task: DAEO-mb2t" --trailer "Role: engineer" --trailer "Implements: DEC-1027, DEC-1015, DEC-1014, DEC-1083, DEC-530, DEC-954, DAEO-2ds6, DAEO-2bdu" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- <your paths>

Then quote `git log --oneline -3` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, each run's last line, the commit hashes with trailers, `du -sh` of your TMPDIR. In
`tests`: your unit counts, and the earlier suites' reds by file (or "none red"). In `discoveries`: what each store does
without `.gitleaks.toml` today. Also the refusals met.
