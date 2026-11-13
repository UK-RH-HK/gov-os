# Brief: independent test designer, DAEO-mb2t (W2-124), STANDARD, class C2 — the semantic store's fail-named rule (build run 2, td-1)

Budget: projection 3 USD. Keep your context short: read only what the tests need; cut long outputs to head and tail.
(Hand-built by the lead: `gov context DAEO-mb2t --role independent-test-designer` refuses this ticket with
CONTEXT_OVER_CEILING, 17598 of 6000 tokens; this brief and the ticket are your inputs.)

You are a fresh independent test designer (MR-3) for ticket DAEO-mb2t (W2-124). You work only in
`/home/usain/gov-os-worktrees/W2-124-tests` on branch `w2/W2-124-tests` (DEC-963). The engineer builds in parallel in
`/home/usain/gov-os-worktrees/W2-124`, which you never read or write. You write to the KPI lines and the Interface
below, never to the implementation: do not read `src/gov/rebuild/command.py`, `src/gov/adopt/stages.py` or
`src/gov/close/rebuild_gate.py` beyond their public names; you may run `gov rebuild --help` and `gov adopt --help`
(`PYTHONPATH=<your tree>/src python3 -m gov.cli.main ...`) and read the existing acceptance suites
`tests/acceptance/W2-122/` (its `w2_122_support.py`: a loopback embedder stand-in at `OLLAMA_HOST`, `GOV_OLLAMA_BIN`
pointing at a path that does not exist, a planted project and a `rebuild()` helper), `tests/acceptance/W1-27/`
(rebuild, `--no-embeddings`), `tests/acceptance/W1-41/` and `tests/acceptance/W2-23/` (planted adoption runs through
A0 to A6, with the auditor's verdict commit) to see how planted projects are built.

## Step 0, before any work: the sandbox check (report it first in your return)

Do step 0 of `/home/usain/gov-os-worktrees/W2-124-tests/.gov-runtime/scratch/brief/EMG-d4b-launched.md` with ticket id
`DAEO-mb2t`. If it fails, stop and return (delete nothing). Then read `EMG-common.md` beside it (its test-designer
paragraph applies).

## Standing rules

- First `printenv GOV_ROLE GOV_TICKET` (expect `independent-test-designer`, `DAEO-mb2t`) and
  `git rev-parse --show-toplevel --abbrev-ref HEAD` (expect `/home/usain/gov-os-worktrees/W2-124-tests`, `w2/W2-124-tests`).
- The ticket: `/home/usain/Dynamic-Agentic-Engineering-OS/.tickets/DAEO-mb2t.md` (KPI lines, the `## Interface`
  section and run 1's P2 and P3 at its end: all binding). The register (`docs/DECISION_REGISTER.md`): grep only by id
  (e.g. `### DEC-1027`); the sources are the ticket's `sources:`.
- **Writes:** only `tests/acceptance/W2-124/**`. No earlier suite is revised (P3). Scripts, if any, as files under
  your TMPDIR.
- **Every pytest** goes through the heavy slot, with the sandbox's TMPDIR (outside the repository and outside
  `~/gov-os-runs`; check `echo $TMPDIR`), in this form:
  `env TMPDIR=<your TMPDIR> PYTHONUSERBASE=/home/usain/.local HOME=/home/usain/gov-os-worktrees/W2-124-tests/.gov-runtime/scratch/empty-home PYTHONPATH=/home/usain/gov-os-worktrees/W2-124-tests/src bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh python3 -m pytest tests/acceptance/W2-124 -q -p no:cacheprovider -o tmp_path_retention_policy=failed -m "not local_only" -k "not real and not green_here and not time_limit"`
  (create the empty-home folder first if absent). If the sandbox refuses the heavy slot, say so and run the same
  line without `bash .../heavy_slot.sh`.
- No `gov retrieve` or `gov context`; search with Read and Grep, and search again once in other words if the first
  search does not answer (DEC-1065). No `$(…)` or variable as a write target, no here-document, no `bash -c`.
  Foreground only. No reset, checkout, clean, amend, rebase, push, merge or install.
- No test starts a real embedder or model; stand-ins only (a loopback HTTP stand-in as W2-122's). Planted projects
  live under pytest's `tmp_path`; no test writes into this repository's tree. Keep the suite fast: each case a few
  seconds; the hung-embedder case must not wait out the real 120 s endpoint timeout (see below).
- Refused twice for the same call: stop and say so; never reach the same effect by another command, form or file.
  On an authentication error return `AUTH_REQUIRED`.

## What to write: `tests/acceptance/W2-124/`

Tests for the KPI lines **S1 to S5, F1 and F2** of the ticket, each from its `Verify:` text, through the public
surface: `gov rebuild` and `gov rebuild --json` / `--no-embeddings` (run as `python3 -m gov.cli.main rebuild ...` in a
planted project with your tree's `PYTHONPATH`), `gov adopt --lite --stage A6 --json`, the committed A6 record, and the
module the Interface names (`gov.close.rebuild_gate`) where a line has no CLI form (S4).

## The interface both sides build to

From the ticket's `## Interface` (binding, quoted in substance):
- **Asked for** = no `--no-embeddings` AND the path map has a namespace with `embedding_policy: embedded`. Otherwise
  `result.stores.semantic` = `{status: not_recreated, requested: false, reason}` and no embedder is called (S2).
- **Asked for and not recreated** (the embedder unavailable, hung past the endpoint timeout, failing part way):
  `GovError` `REBUILD_FAILED`, details `{store: "semantic", reason, stores}`, exit 1; no warm-base record.
- `src/gov/close/rebuild_gate.py`: `semantic_failure(result: dict) -> str | None` (takes a `gov rebuild --json`
  envelope or its `result`; returns the reason a semantic store that was asked for is not recreated, else None) and
  `check(result: dict) -> None` (raises that `REBUILD_FAILED`). `gov rebuild` calls `check()` on its result, so the
  close and the merge queue's prepare (`rebuild_slot.sh` -> `gov rebuild --json`) fail through it.
- **Adoption:** stage A6 catches `REBUILD_FAILED` with store `semantic` and finishes; the committed A6 record and the
  stage's `gov adopt --lite --json` result ("the adoption report") each hold
  `findings: [{code: SEMANTIC_NOT_RECREATED, store: semantic, reason, command: "gov rebuild"}]`. Any other
  `REBUILD_FAILED` stays `INDEX_REFRESH_FAILED`.
- **P2 (b), S5:** `gov rebuild` keeps exit 0 and `"ok": true`, and its result carries `complete: false` and
  `not_built: [{store, reason}]` for every store not built (no path map, no `.gitleaks.toml`, a store the path map
  calls for not built). W2-26's finding 2 (an unadopted clone answering `"ok": true`) stays `ok`, named in the result.

The lead's naming for what the Interface leaves open (both sides use exactly these):
- Human output of the failure is the CLI's form `gov rebuild: REBUILD_FAILED: <message>` on stderr; the message holds
  the literal text `store: semantic` and the reason. With `--json`, the envelope has `"ok": false` and
  `error.code == "REBUILD_FAILED"`, `error.details.store == "semantic"`, `error.details.stores` the stores built.
- "Prints ok" = exit 0 and, with `--json`, `"ok": true`.
- `not_built` lists only stores that were to be built and were not. A store with `requested: false` (S2's projects,
  or `--no-embeddings`) is never in `not_built`. `complete` is true exactly when `not_built` is empty. With
  `--no-embeddings`, `stores.semantic.requested` is false and its `reason` names `--no-embeddings` ("says it skipped
  the vectors"). S2 "names no semantic store" = no `REBUILD_FAILED`, no `store: semantic` in the output, and
  `semantic` not in `not_built`.
- S5 without `.gitleaks.toml`: `complete: false` and an entry of `not_built` whose `reason` names `.gitleaks.toml`
  (which store is the engineer's finding; do not pin the store name there). Without the path map: `complete: false`
  and an entry naming the path map.
- S4: "the close's rebuild check" is `gov.close.rebuild_gate.semantic_failure` / `check` on the planted result;
  "the merge queue's prepare" is `gov rebuild --json` failing through `check()` (S1's cases) and, for the planted
  result itself, the CTO's `rebuild_slot.sh`: run
  `/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/rebuild_slot.sh <planted tree>`
  with `GOV_REBUILD_PYTHON` pointing at a stand-in executable that prints the planted envelope and exits 0, and
  expect exit 75; skip that one case with its reason where the tool is absent or the sandbox refuses the heavy slot.
- The hung embedder: a stand-in that accepts and never answers. The real endpoint timeout is 120 s
  (`gov.retrieval.semantic.TIMEOUT_S`); for that case only you may call `gov.rebuild.command.run` in-process with
  `TIMEOUT_S` monkeypatched to about 1 s (the timeout is the seam, nothing else is patched), asserting the
  `GovError` code and details; the unavailable and failing-part-way cases go through the CLI.
- Failing part way: a stand-in that answers the first embed request and fails (HTTP 500 or a dropped connection) on
  the later ones; plant enough files for more than one batch, or check the stand-in was asked more than once.

Write `tests/acceptance/W2-124/README.md` mapping every KPI line to its tests **with full node ids**
(`test_<file>.py::test_<name>`, every item; the runner fails a line whose map names a test it cannot collect).

## Check and commit

1. Run your suite on this branch (today's integrated code, before the engineer's change) with the pytest line above.
   S1, S3 (the finding), S4 (the gate module is absent), S5 (`complete`/`not_built`) and F1/F2 should be red there; the
   `--no-embeddings` cases and parts of S2 may be green. Quote the last line and each failure's one-line reason,
   grouped by KPI line; a line wholly green on today's code is a test that checks nothing new: fix it or say why.
2. Commit only your paths:

       git commit -m "W2-124 acceptance: the semantic store fails named, adoption records it (S1-S5, F1-F2)" --trailer "Task: DAEO-mb2t" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-1027, DEC-1015, DEC-1014, DEC-1083, DEC-530, DEC-954, DAEO-2ds6, DAEO-2bdu" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>" -- tests/acceptance/W2-124

   Then quote `git log --oneline -2` and `git status --short`.

## Return

One message, your last. **The twelve fields first, each a labelled line** ("none" where nothing):

```
task: / status: / work_completed: / files_changed: / evidence: / tests: / discoveries: / risks: / lessons: / proposed_decisions: / unresolved: / recommended_next_action:
```

`status` is DONE, PACKAGES, ESCALATION, ESCALATION_BLOCKED, LAUNCH_BLOCKED or AUTH_REQUIRED, with one line of why. In
`evidence`: the sandbox check, the run's last line, the commit hash with its trailers, `du -sh` of your TMPDIR. In
`tests`: the case count per KPI line. Also the refusals met. Where the Interface is silent on something a test needs,
choose the narrowest reading, name it in `discoveries`, and never invent a refusal code.
