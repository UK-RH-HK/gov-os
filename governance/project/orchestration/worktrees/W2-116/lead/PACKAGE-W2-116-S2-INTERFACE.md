# P-W2-116-S2-INTERFACE (lead, pass 2, 2026-11-13): S2's interface and one path outside the ticket

task: DAEO-f58b · decisions_applied: DEC-1052 (interface before the pair), DEC-963, DEC-966 item 3, DEC-983, DEC-1087 (3)

## Ground (read)
- The repository's nightly (`governance/project/orchestration/nightly/nightly.sh`) writes its verdict as a `verdict:` line in
  `.gov-runtime/scratch/orchestrator/log/nightly/<YYYYMMDD-HHMM>/run.txt`. It never runs the product's nightly
  (`gov.close.nightly`), which writes `docs/close/nightly/NR-<stamp>-<head12>.json` with a `"verdict"` key.
- The CTO's `store_refresh_daily.sh` already triggers on the run.txt verdict (latest 10:00) and again at 18:00. It does
  this by **watching the verdict file**, not by a call from the nightly. The crontab has no line for it today.
- `governance/project/rebuild.yaml` holds `integration_store` and nothing for S2. It is **outside the ticket's paths**.
- `gov status` (`src/gov/status/command.py`) has seven parts and a `{"read": false, "reason"}` form. It has no part for
  the integration store.
- The store's age can be read from the W2-122 record `<half>/.gov-runtime/rebuild/stores.json` (`written_at`) of the
  half the link points at.

## Question 1: the ticket doesn't state S2's interface (config keys, trigger, branch, status part, stale rule, error name)
The test designer and the engineer work in parallel, so both need the interface first (DEC-1052).
- **(a) Recommended. A product "when due" tick that watches a configured verdict, with no change to the nightly.**
  About 150 to 250 lines inside the paths. Add this text to the ticket:
  - Config, in `governance/project/rebuild.yaml`:
    `integration_refresh: {branch: <ref>, after_nightly: {verdict: <glob, relative to the project root>, latest: "HH:MM"}, second: "HH:MM"}`.
    - A verdict file counts once it holds a `^verdict:` line or a JSON `"verdict"` key.
    - The product's default glob is `docs/close/nightly/NR-*.json`.
  - Command: `gov rebuild --integration <branch> --when-due` (the branch may come from config).
    - **Due after the nightly:** a verdict file written after the last scheduled refresh, or `latest` passed today without one.
    - **Due at the second time:** `second` passed today and no scheduled refresh since then.
    - Otherwise it ends `status: not_due` and builds nothing.
    - Each scheduled refresh writes `<link>.refresh.json` with `{at, reason: after_nightly|second, head, status}`.
    - The clock can be planted for tests through the env variable `GOV_NOW` (ISO).
  - Error: a missing or invalid time (or a missing `integration_refresh` with `--when-due`) refuses
    `REBUILD_CONFIG_INVALID`. The details name `key` (e.g. `integration_refresh.second`) and the value.
  - `gov status` gets a new part, `integration_store`:
    `{link, half, head, branch, branch_head, built_at, age_seconds, stale, stale_reason, last_refresh}`.
    - **Stale** means the ready half's head is not the branch's head, or it was built before the last time a scheduled
      refresh fell due.
    - With no store configured, the part is `{"read": false, "reason"}`.
  - Running it: a cron line every 5 minutes, `flock <link>.refresh.lock heavy_slot.sh gov rebuild --integration w2/integrate --when-due`.
    This is the operator's line in window 4's ACT, next to the hook.
- **(b) The nightly calls the refresh after its verdict, and cron runs the second time.**
  - Needs `nightly.sh` (a reviewed folder, with `test_nightly.sh`) and `src/gov/close/nightly.py`: two paths outside the ticket.
  - The "after the nightly" trigger would then not be in the project's configuration as S2 asks. The cron line is
    needed anyway.
- **Recommendation:** (a). **Confidence:** medium-high.

## Question 2: this repository's own values need a path outside the ticket
For (a) or (b) the repository needs its own values in `governance/project/rebuild.yaml`:
`integration_refresh: {branch: w2/integrate, after_nightly: {verdict: .gov-runtime/scratch/orchestrator/log/nightly/*/run.txt, latest: "10:00"}, second: "18:00"}`.
- (a) The CTO adds the line (as with `integration_store`, `a1d3e81a984c`).
- (b) Widen the ticket by that one file.

Without the line, the live tick refuses `REBUILD_CONFIG_INVALID` by design. The acceptance cases plant their own config.
**Recommendation:** (a). **Confidence:** high.

## Question 3: the ride-alongs
- **R2-F1 is already fixed on this head:** `_store_root` resolves a given `--root` once (`src/gov/retrieve/command.py:112-113`,
  "W2-138 S2"). Nothing is left to build.
- **R2-F3:** the token is encoded and decoded in `src/gov/retrieval/retrieve.py:199,259`, which is outside the paths.
  - (a) Widen the ticket by that file: the token carries the half's realpath and refuses (or restarts) after a switch.
    About 20 lines.
  - (b) Build it inside the paths: `retrieve/command.py` wraps and checks the token. This is hackier.
  - (c) Leave it for the parallel-agents measure (DEC-1087 (10)).
  - Recommendation: (a), confidence medium.
- **F7 can't be built in this ticket:** the merge queue's promotion is the CTO's tool (`merge_queue.py`), not product
  code. It is a step of window 4's ACT, retired or pinned there.

## What this blocks
The pair's start for pass 2: the test designer's S2 cases and the engineer's S2 build. That in turn blocks W2-138 (it
waits only on W2-116) and W2-27's list.
