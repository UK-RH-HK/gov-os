Step 0, the sandbox check (launch_worker.sh): (a) writing `/home/usain/gov-os-worktrees/.sandbox-trial-DAEO-f58b` **failed**, read-only file system, as it should; (b) `git hash-object -w --stdin` worked (gave `1ae28402a109…`) and `git update-index --refresh` worked, both exit 0. The `ps` check for ollama or llama-server shows nothing of mine, before and at the end. `GOV_TICKET=DAEO-f58b`, `GOV_ROLE=independent-auditor`.

---
type: probe
task: DAEO-f58b
decisions: [DEC-1157, DEC-1052, DEC-966, DEC-983, DEC-982, DEC-801, DEC-808, DEC-1010]
reviewer_session: cf8cd743-3f8d-4164-ab28-ec09fbbe1000 (the session folder in this session's tool-output path)
implementer_session: 48f136f9-ab88-4fe1-a3a9-16e5b906ffb3 (engineer, eng-2: S2 committed); c88a0d4c-7359-436c-ba83-1a5591864573 (engineer, eng-1: R2-F3, 09247e423)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
probed_commit: d4f05d6577a15e97e15eeed10404332c81f0cc1b
scope: narrow independent check of pass 2b (S2, the stated interface, R2-F3)
---
# Probe record: W2-116 pass 2b (DAEO-f58b), narrow check

## Identity
- `git rev-parse HEAD` = `d4f05d6577a15e97e15eeed10404332c81f0cc1b`.
- `git status --porcelain` was empty at the start and is empty at the end. Everything I wrote is under the sandbox's `TMPDIR`.

## What was probed

**Read.** I read the whole diff `e51b1fdf6..d4f05d657`:
- `src/gov/rebuild/integration.py`, `command.py`, `governance/project/rebuild.yaml`;
- `src/gov/status/integration_store.py`, `command.py`;
- `src/gov/retrieval/retrieve.py`;
- the evidence record's "Pass 2b" section;
- the four new acceptance files and `w2_116_s2_support.py`.

I also read the code these depend on:
- `_refresh` (the unchanged path returns before any build);
- `seed.remember` (`written_at` is set when a build completes);
- `retrieve.resolved` and `store_of`, `gov.retrieve.command._store_root`, `gov.launch.store.session_root` (the root is resolved once by realpath, and `f` carries it).

**Tests.** Every run went through `heavy_slot.sh` with `HOME` set to an empty scratch folder and `-m "not local_only" -k "not real and not green_here and not time_limit"`. The files run: the four pass-2b acceptance files and the three new unit files.
- Default opt-in: **99 passed, 80 deselected** (the repository's opt-in keeps only the first row of each parametrised test).
- `GOV_TESTS_OPTIN=lifted,breadth`: **178 passed, 1 deselected**.
- The one case the name filter left out is `test_w2_116_when_due.py::test_without_gov_now_it_is_the_real_clock`. It contains "real" but is about the clock, not a model. Run alone: **1 passed**.
- No real model was started.

**Ticks across days.** A script under `TMPDIR` ran the real `refresh_when_due` with only `refresh()` stubbed: a tick every 5 minutes, `GOV_NOW` planted, a real `rebuild.yaml`, the real record file, and nightly `run.txt` files whose times were set with `os.utime`. Results:

| Scenario | Refreshes |
|---|---|
| This repository's values (10:00 / 18:00); nightly creates `run.txt` at 04:04 with no verdict, adds its `verdict:` line at 05:02; 3 days | 2 a day: 05:05 `after_nightly`, 18:00 `second`. The run.txt without a verdict line never counted. |
| Nightly adds one more line 5 minutes after its verdict | 3 a day (row R-1) |
| Late nightly, verdict at 11:32 | 10:00, 11:35, 18:00 |
| Nightly ending 23:52 | Next day: 10:00, 18:00 (row R-3) |
| No nightly at all | 10:00, 18:00 each day |
| Build fails 10:00–10:30 | 6 refused ticks, then the record is written at 10:30; the record is untouched while it fails |
| `second` before `latest` (06:00 / 10:00) | 06:00, 10:00 |
| Edge minutes (`latest` 23:59, `second` 00:00, ticks every minute) | Exactly one refresh at each |

No scenario refreshed more than three times a day, and no scenario failed to refresh.

**Stale judgement.**
- I called `last_due` directly for a store switched at 05:06 whose 18:00 refresh found the head unchanged (finding F-1).
- I ran `gov.status.integration_store.read()` read-only on this worktree's real configuration. It names the link `W2-00-store`, the half `W2-00-store-a`, head = branch head `8801ffd17df9`, `built_at` 2026-11-13T18:05:25Z and an age, and says `stale: false`.

**This repository's verdict files.** All 12 `run.txt` under the main tree's `.gov-runtime/scratch/orchestrator/log/nightly/` were checked:
- 11 hold one `^verdict:` line. `20261101-0400` holds none, so it never counts and the `latest` rule covers that day.
- The most recent one names `verdict[...]` test ids but they are not at the start of a line, so the regular expression is right not to count them.

## Found sound
- **Configuration refusals:** all 14 rows plus `GOV_NOW` refuse with `REBUILD_CONFIG_INVALID` before anything is built, with `details.key` and `value`.
- **Record writes:** the record is written by an atomic replace, only after `switched` or `unchanged`. A failed refresh leaves both the record and the link, so no work is lost.
- **`after_nightly_at`:** a `second` refresh carries it over, so no extra `after_nightly` refresh falls due after 18:00.
- **`at`** is the moment of the decision, so a verdict that lands during a build makes the next tick due.
- **Plain refresh:** `--integration` without `--when-due` never reads the times and never writes the record.
- **`gov status` never calls a store fresh when a figure is unread:** `stale` becomes unread, not `false`. `behind_branch` reads the branch in the shared refs, so its answer is the same from any worktree.
- **R2-F3:** `f` is the realpath, resolved once, for all three forms (`--root`, `GOV_STORE`, a plain search). Both checks refuse with `CONTINUATION_INVALID` naming both folders: a token from another folder at the same commit, and a token with no `f`. A token used on its own folder pages as before. The acceptance cases cover a page 2 after the link switched, at the same commit.
- **The acceptance cases would fail on plausible wrong implementations:**
  - a literal rule without `after_nightly_at` fails "second is due once";
  - counting a file by its time alone fails the no-verdict case;
  - a default `latest` instead of the planted 05:15 fails the first case;
  - writing the record on a failure or on `not_due` fails the byte-equality checks;
  - a `second` rule judged by date instead of by `at` fails the 18:05 case;
  - stale judged by head alone fails the three `built_before_due` cases.

## Findings

**F-1. `gov status` calls a store stale after a scheduled refresh that found nothing to do** (`src/gov/status/integration_store.py:590`, `_reasons`; with `src/gov/rebuild/integration.py:289-292`).
- **What was done:** the store was switched at 05:06 after the nightly, no merge landed, and the 18:00 `second` refresh ran on time and returned `unchanged`.
- **What happened:** `gov status` reports `stale: true` with `built_before_due … 18:00` from 18:00 until the next refresh that switches. On a day with no merge into the integration branch, that lasts all day.
- **Why:** an `unchanged` refresh builds nothing, so `built_at` (the half's `written_at`) keeps the time of the last build that switched.
- **What should happen:** a store at the branch's head whose scheduled refresh ran at or after the due time is not stale. For example, a record `at` at or after the due time with `head` equal to `branch_head` would answer it.
- **This matches the stated interface word for word.** The interface defines `built_before_due` by `built_at` alone, so the change belongs to the interface text, not only to the code.
- **How found:** read in `_refresh`, then confirmed with `last_due`: fresh at 09:00 and 17:59; stale at 18:30, 23:00 and 04:00 the next day.
- **What would reverse it:** an `unchanged` refresh that rewrites `written_at`, or a stale rule that also reads `last_refresh`. Neither is in the diff.
- Ordinary work: yes, because a day with no merge between two scheduled refreshes is common, and every `unchanged` refresh leaves the old `built_at`.
- Consequence: other (it fails closed: a store that is current is named stale, never the reverse; `behind_branch`, the check of content, stays correct).

## Rows (no round)
- **R-1.** A nightly that writes to its `run.txt` after the verdict line moves the file's time past the record's `at`, so one more `after_nightly` refresh falls due. It is `unchanged` and cheap. This repository's nightly writes `verdict:`, `duration`, `clone kept` and `done` within about a second, so the window is a tick that lands inside that second. Ordinary work: yes, because the nightly's last lines follow its verdict line. Consequence: other (one more refresh at most).
- **R-2.** A build that keeps failing (for example, the model is down) is retried on every tick, every 5 minutes, all day. This is what the interface asks ("the next tick is due again"). Ordinary work: yes, because a model or disk can stay down for hours. Consequence: other (load, no lost work).
- **R-3.** A nightly whose verdict lands before midnight does not count for the next day's `latest`, so one more refresh runs at 10:00. This is what the interface asks. Ordinary work: yes, because evening nightlies happen (`20261110-2222`). Consequence: other.
- **R-4.** The default glob `docs/close/nightly/NR-*.json` names files that may be committed. A checkout or merge that rewrites them sets their time to "now": one more refresh, and `gov status` names the store stale until it runs. This repository uses an untracked glob. Ordinary work: yes, for an adopting project with committed verdict files. Consequence: other.
- **R-5.** `gov status` reads the verdict glob relative to the root it runs in. In a ticket worktree the untracked nightly log is absent: I checked that `.gov-runtime/` is ignored and has no nightly folder here. So `built_before_due` there is judged by `latest` and `second` alone, and after a late nightly it can differ from the main tree's answer. `behind_branch` does not depend on the root. Ordinary work: yes, because agents run `gov status` in worktrees. Consequence: other (it is a scheduling flag; the content check is the same everywhere).
- **R-6.** Overlapping ticks without the cron's `flock` each wait on the refresh lock and write the record in the order they wake, which can leave an earlier `at` last. That gives at most one more refresh. Out of scope: the `flock` belongs to window 4's ACT. Ordinary work: no, because the cron line takes the lock. Consequence: other.
- **R-7, test coverage.**
  - The when-due acceptance cases plant their times in UTC, and this machine's local zone is UTC. A wrong implementation that read `HH:MM` in local time instead of `GOV_NOW`'s offset would pass those cases; the unit table and the status cases, which use other offsets, pin it.
  - No acceptance case names `built_before_due` caused by `second`.
  - Ordinary work: no, because it needs a wrong implementation, which this one is not. Consequence: other.
- **Out of scope, named by the lead and not checked by me:**
  - `tests/unit/status/test_status.py:172` (the new part);
  - six token cases in `tests/unit/retrieval/test_w2_131_*`, `test_w2_133_*` and `test_w2_135_*` (the new `f` key).
  - The cron line and the hook are window 4's ACT.
- **Environment note:** `heavy_slot.sh` could not append to `log/heavy-slot-waits.jsonl` (read-only file system in the sandbox). It waited for a slot and ran anyway, so this was a gate wait, not a refusal.

Classification: 1 finding in scope, ordinary work yes, consequence other (F-1); 7 rows. No finding fails open or loses work.

## Verdict
**Pass** for S2 and for R2-F3. The due rules refresh twice a day as configured, never too often and never not at all. A failure leaves the store and the record. `gov status` names head, age and a stale store and never calls a stale store fresh. The token carries its half and is refused on another. F-1, a store wrongly called stale after an `unchanged` refresh, fails closed, so it is recorded as a row to ride along (DEC-802, DEC-1010).

```verdict
{"kpis": [{"kpi": "S2", "verdict": "pass", "findings": [{"id": "F-1", "scope": "in", "ordinary_work": "yes", "consequence": "other"}]}, {"kpi": "R2-F3", "verdict": "pass", "findings": []}]}
```