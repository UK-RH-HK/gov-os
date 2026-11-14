# Brief: independent auditor, W2-116 (DAEO-f58b) pass 2b: a narrow independent check

You are a fresh independent auditor, read-only. You write nothing in any repository folder; work only under your
session's own `TMPDIR`. Your last message is the probe record, whole; the lead commits it under
`docs/probes/DAEO-f58b/`.

## What to check, and only this
Pass 2b's change on `w2/W2-116`, head **d4f05d6577a15e97e15eeed10404332c81f0cc1b**, in
/home/usain/gov-os-worktrees/W2-116: the diff `git diff e51b1fdf6 d4f05d657` (e51b1fdf6 is the merge of w2/integrate
that pass 2b started from; pass 1 was reviewed READY and is out of scope). The commits:
- 09247e423 R2-F3: the continuation token carries the resolved store folder (`src/gov/retrieval/retrieve.py`);
- ee3a8284e S2: `gov rebuild --integration <branch> --when-due`, the record, `REBUILD_CONFIG_INVALID`, `GOV_NOW`, and
  this repository's `integration_refresh` line (`src/gov/rebuild/integration.py`, `command.py`,
  `governance/project/rebuild.yaml`);
- ab7a7c50e S2: `gov status`'s `integration_store` part (`src/gov/status/command.py`, `integration_store.py`);
- c9c9d13fb, d4f05d657: the evidence record's "Pass 2b" section (`docs/changes/W2-116-evidence.md`) and unit tests;
- 20d6a21f5 (merge) / a97503b39: the independent test designer's acceptance cases `tests/acceptance/W2-116/test_w2_116_s2_*`,
  `test_w2_116_r2f3_continuation.py`, `w2_116_s2_support.py`.

Judge against:
1. **S2's KPI line:** "It is refreshed after the nightly's verdict and at a set second time each day (both in the
   project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982]. Verify:
   pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict
   and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a
   missing or invalid time refuses by name."
2. **The stated interface** (below: the ticket's note "S2's interface (pass 2b)", decided by the CTO under
   DEC-1157 (12), with the lead's settled detail). One addition the lead settled during the build (DEC-1052): the
   record `<link>.refresh.json` also carries `after_nightly_at`, the `at` of the last `after_nightly` refresh, carried
   over by a `second` refresh, and the rule "no `after_nightly` refresh dated today" reads it.
3. **R2-F3:** the continuation token carries a mark of the half (store folder) it was made on, checked when used.

Probe, do not only read: run the acceptance cases and the unit tests of the change, and try what an honest operator or
agent would plausibly do (a tick every 5 minutes across a day; a nightly that writes its run.txt before its verdict
line; a build that fails; a clock at an edge minute; a `gov status` on a project without the store; a page 2 after the
link switched). Do the due rules ever refresh too often, never refresh, or let `gov status` call a stale store fresh
(fails open)? Can a failure lose the previous store or record (loses work)? Do the acceptance cases test what the KPI
says, and would they fail on a plausible wrong implementation?

Out of scope (say so if you see them, as rows, not findings that fail): the cron line and hook (window 4's ACT); pass
1's S1/S3/S4/S5; other tickets' cases that the change turns red (the lead names them to the CTO:
`tests/unit/status/test_status.py:172` by the new part, and six token cases in `tests/unit/retrieval/test_w2_131_*`,
`test_w2_133_*`, `test_w2_135_*` by R2-F3's new `f` key).

## How to run pytest
```
env PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest <paths> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
Keep the sandbox's own `TMPDIR` (outside the repository; `/tmp` itself is read-only in the sandbox). Never write in
/home/usain/gov-os-worktrees/W2-116 (`-p no:cacheprovider` keeps pytest from writing there; a probe script goes under
your `TMPDIR`). A resource gate's refusal is a wait (DEC-1146). Never open the evaluation sets' root or any hidden or
memory-verdict folder. No `gov retrieve` or `gov context` in the sandbox: search with Read and Grep, and once more in
other words if the first does not answer (DEC-1065). Refused twice for the same call by the guard, the sandbox or a
hook: stop and say so; never work around it (DEC-1142 (9)).

## Judgement (word for word, the orchestrator's JUDGEMENT.md)

## Judgement rules: the w2 prompt's section 14, word for word (owner, DEC-801 to DEC-803, DEC-807 to DEC-809)

Every reviewer, probe and auditor brief you write carries this section and the two bullets after it, word for word. You judge your own reviewers' findings by the same rules, and every finding in a probe record you commit keeps its two lines.

- **The threat model is ADR-0001's** (`docs/adr/ADR-0001-threat-model.md`): the Gov OS guards against honest agent mistakes, plausible accidents and drift in ordinary work, not against a deliberate adversary with the owner's privileges. Machinery against an adversary the design cannot stop produces endless review loops.
- **Every finding is judged by two questions, word for word:**
  1. "Can an honest agent hit this in ordinary work?"
  2. "Does it fail open or lose work?"
- **Only a finding with "yes" to both justifies a round.** A finding that needs a deliberate construction (a link planted at a protected name, git environment variables set by hand such as `GIT_OBJECT_DIRECTORY` or alternates, replace refs, an opaque interpreter used to evade the guard) is a row for the Wave 3 hardening pass, never a new round (DEC-801). A finding marked "no" on the first question is a row automatically.
- **Every finding in a probe or audit record carries two lines:** `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other` (DEC-808).
- **No extra round on its own:** when a ticket will resume anyway, its accepted fixes ride along in that resume (DEC-802).
- **Feature-gated risks:** a risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on (DEC-803).
- **Packages:** every package that proposes a round states the classification of its findings on one line, before the recommendation (DEC-809).
- These rules go, word for word, into every reviewer, probe and auditor brief (A3, and every audit brief of W2-25, W2-28, W2-30 and W2-47).

From brief A3 (reviewer), word for word:
- Judge against ADR-0001's threat model (section 14): honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries. Ask of every finding, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?"
- Every finding carries two lines: `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`. A finding marked "no" is a row for the Wave 3 hardening pass, never a round; only "yes" with "fails open" or "loses work" fails the probe.


# W2-116 pass 2b: S2's interface and R2-F3 (the same text in the test designer's and the engineer's briefs)

Source: the ticket's note "S2's interface (pass 2b)" (P-W2-116-S2-INTERFACE Q1 (a), decided by the CTO under DEC-1157 (12),
8801ffd17), with the package's detail. The lead settled the points below that the note leaves open, so that both
sessions build against one text (DEC-1052). Anything not stated here is the engineer's choice and no case pins it.

## Configuration: `governance/project/rebuild.yaml`
```yaml
integration_store: <absolute path of the link>        # exists already (W2-122 / pass 1)
integration_refresh:
  branch: <ref>                                       # required
  after_nightly:
    verdict: <glob, relative to the project root>     # optional; default docs/close/nightly/NR-*.json
    latest: "HH:MM"                                   # required
  second: "HH:MM"                                     # required
```
- A time is `"HH:MM"`, 24-hour, `00:00` to `23:59`, two digits each. Anything else (missing, empty, not a string,
  `"25:00"`, `"9:5"`, `"10am"`) is invalid.
- A missing or invalid time, a missing `branch`, or no `integration_refresh` at all when `--when-due` is given, refuses
  with the error code **`REBUILD_CONFIG_INVALID`**. Its `details` carry `key`, the dotted key
  (`integration_refresh.second`, `integration_refresh.after_nightly.latest`, `integration_refresh.branch`,
  `integration_refresh`), and `value`, the value read (null when missing). The message names the key. Nothing is
  built and no record is written.
- A verdict file **counts** once it holds a line matching `^verdict:` or parses as JSON with a `"verdict"` key. A file
  that matches the glob and holds neither (a nightly still running) does not count.

## The clock
- `now` is the env variable `GOV_NOW` when set (ISO 8601; with an offset it is that instant and the wall clock of that
  offset; without one it is local time), else the real clock. The `HH:MM` times are wall-clock times on `now`'s date.
- A verdict file's time is its modification time (an instant), compared with `now` and with the record's `at`.
- An invalid `GOV_NOW` refuses `REBUILD_CONFIG_INVALID` with `key: "GOV_NOW"`.

## The command: `gov rebuild --integration <branch> --when-due`
`--when-due` is only valid with `--integration` (otherwise the existing `REBUILD_FAILED` usage refusal). It reads the
config (above) and the record `<link>.refresh.json` (beside the link, e.g. `/x/W2-00-store.refresh.json`), and is due:
- **after_nightly:** a counting verdict file whose time is later than the record's `at` (any counting verdict file when
  there is no record); or `now` is at or after today's `latest` and no scheduled refresh with reason `after_nightly`
  has an `at` on today's date.
- **second:** `now` is at or after today's `second` and the record's `at` is before today's `second` (or there is no
  record).
- When both are due, one refresh runs with reason `after_nightly`.
- **Due:** it runs the refresh that `gov rebuild --integration <branch>` runs (S1/S4, unchanged), and its result is that
  refresh's result with `integration.reason` set to `after_nightly` or `second`. On success (`integration.status`
  `switched` or `unchanged`) it writes `<link>.refresh.json` whole (atomic replace):
  `{"at": <now, ISO with offset>, "reason": "after_nightly"|"second", "head": <the head built, full sha>,
  "status": "switched"|"unchanged", "branch": <branch>}`.
  A failed refresh refuses `REBUILD_FAILED` as today and leaves the record as it was, so the next tick is due again.
- **Not due:** nothing is built or written; the command succeeds and its result is
  `{"integration": {"status": "not_due", "branch": <branch>, "link": <link>, "last_refresh": <the record or null>}}`.
- A plain `gov rebuild --integration <branch>` (no `--when-due`, e.g. after a merge) never reads the times and never
  writes the record.
- Running it in production (the cron line every 5 minutes, `flock <link>.refresh.lock`) is window 4's ACT, not this
  ticket.

## `gov status`: a new part, `integration_store`
`gov status --json` gains `result.integration_store`:
```
{link, half, head, branch, branch_head, built_at, age_seconds, stale, stale_reason, last_refresh}
```
- `link`: the configured `integration_store`; `half`: the realpath the link points at; `head`: that half's HEAD (full
  sha); `branch`: `integration_refresh.branch`; `branch_head`: the branch's commit in the project (full sha);
  `built_at`: `written_at` of the half's W2-122 record `<half>/.gov-runtime/rebuild/stores.json` (as written there:
  ISO, UTC, real clock at build time); `age_seconds`: `now - built_at` in whole seconds (`now` honours `GOV_NOW`);
  `last_refresh`: the content of `<link>.refresh.json`, or null.
- `stale` (bool) and `stale_reason` (null when not stale; else a string of the reasons that hold, joined by `"; "`, each
  starting with its code):
  - `behind_branch: ...` when `head` is not `branch_head` (the text names both, 12 hex digits or more each);
  - `built_before_due: ...` when `built_at` is before the last time a refresh fell due. That time is the latest one at
    or before `now` among: the newest counting verdict file's time; `second` on today's and yesterday's dates; and
    `latest` on today's and yesterday's dates, each counted only when no counting verdict file's time falls on that
    date before that `latest`. The text names that time.
- No `integration_store` configured, no link, or a link that does not resolve to a folder: the part is
  `{"read": false, "reason": ...}` (the command's existing convention; it then appears in `not_read`).
- `integration_store` there but `integration_refresh` missing or invalid: `link`, `half`, `head`, `built_at`,
  `age_seconds` and `last_refresh` are still given; `branch`, `branch_head`, `stale` and `stale_reason` are each
  `{"read": false, "reason": ...}`, the reason naming the key.
- `gov status` never refuses for this part and still exits 0.

## R2-F3: the continuation token carries the half
- The token made by `gov retrieve` carries a mark of the store folder it was made on: the store root as resolved once
  (the realpath, so a token made through the link names the half the link pointed at).
- A token used against a store whose resolved root is another folder refuses **`CONTINUATION_INVALID`**, even when
  both folders are at the same commit (the existing commit check alone cannot tell two halves at one head apart).
  The message says the continuation was made on another store and names both folders.
- A token made on the same folder still pages as before. A token without the mark (made before this pass) refuses
  `CONTINUATION_INVALID`, as a token from before W2-138 does today.
- Continuations are given as `gov retrieve --continue <token>`.

## Your last message: the probe record, whole
```
---
type: probe
task: DAEO-f58b
reviewer_session: <your session id, or how you know it>
implementer_session: 48f136f9-ab88-4fe1-a3a9-16e5b906ffb3 (engineer, eng-2: S2 committed); c88a0d4c-7359-436c-ba83-1a5591864573 (engineer, eng-1: R2-F3, 09247e423)
reviewer_wrote_nothing: true
commissioned_by: orchestrator
probed_commit: d4f05d6577a15e97e15eeed10404332c81f0cc1b
scope: narrow independent check of pass 2b (S2, the stated interface, R2-F3)
---
# Probe record: W2-116 pass 2b (DAEO-f58b), narrow check
- What was probed (setup, commands, counts)
- Each finding: id, what, where (file:line), how found, then the two lines
  `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`
- Rows (out of scope, or "no" on the first question)
- Verdict: pass or fail, with the one line why
```
and, at its end, the verdict block, one entry per line judged (S2 and R2-F3):
````
```verdict
{"kpis": [{"kpi": "S2", "verdict": "pass|fail", "findings": [{"id": "F-1", "scope": "in|out", "ordinary_work": "yes|no", "consequence": "fails open|loses work|other"}]}, {"kpi": "R2-F3", "verdict": "pass|fail", "findings": []}]}
```
````

## The ticket's context packet (gov context DAEO-f58b --role independent-auditor --budget 20000)
```json
{
  "ticket": "DAEO-f58b",
  "ticket_text": "---\nid: DAEO-f58b\nstatus: in_progress\ndeps: [DAEO-lrre]\nlinks: []\ncreated: 2026-10-31T23:52:57Z\ntype: task\npriority: 1\nassignee: engineer\nexternal-ref: W2-116\ntags: [wave-2, implementation, memory, standard, smart-work]\nwbs_id: W2-116\ntitle: 'The designers'' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer''s retrieval reads (SMART-WORK-1)'\nclass: implementation\nstate_class: AUTHORITATIVE\nrole: engineer\ndepends_on:\n- DAEO-lrre\nallowed_paths:\n- src/gov/status/**  # S2: the store's head and age in gov status (CTO, DEC-1157 (12))\n- docs/probes/DAEO-f58b/**  # the probe record\n- src/gov/rebuild/integration.py\n- src/gov/rebuild/command.py\n- src/gov/launch/store.py\n- src/gov/launch/launcher.py\n- src/gov/retrieve/command.py\n- docs/changes/W2-116-evidence.md\n- tests/unit/rebuild/test_w2_116*\n- tests/unit/launch/test_w2_116*\n- governance/project/rebuild.yaml  # S2, P-W2-116-S2-INTERFACE Q2 (b) (CTO, DEC-1157 (12)): this repository's integration_refresh line lands with the code that reads it\n- src/gov/retrieval/retrieve.py  # R2-F3, Q3 (a) (CTO): the continuation token carries the half it was made on (about 20 lines)\n- tests/unit/status/test_w2_116*\n- tests/unit/retrieval/test_w2_116*\nkpis:\n  success:\n  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]'\n  - 'It is refreshed after the nightly''s verdict and at a set second time each day (both in the project''s configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2''s cases: a planted configuration''s two refresh times are read and the refresh runs after the nightly''s verdict and at the second time; `gov status` names the integration store''s head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role''s plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]'\n  - 'The store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]'\n  - '`gov launch` points every worker session''s retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer''s; a designer''s retrieval never reads a ticket worktree''s store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer''s never names a worktree''s store [DEC-1087 (3), DEC-963] [added, the CTO''s note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]'\n  failure:\n  - 'A designer''s retrieval answered from a ticket worktree''s store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]'\n  - 'The link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]'\n  - 'A re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]'\nprofile: STANDARD\nsources:\n- DEC-1109\n- DEC-1112\n- DEC-983\n- DEC-982\n- DEC-963\n- DEC-966\n- DEC-1014\n- DEC-1015\n- DEC-1083\n- DEC-1087\n- DEC-719\n- DAEO-kia7\nest_loc: 150\nacceptance_tests:\n  path: tests/acceptance/W2-116/\n  author: independent-test-designer (MR-3); from the spec and KPIs, in parallel with the implementer (DEC-963); a planted branch, a build killed half-way, a search during a build\ntrack: B\nlist_rows:\n- W2-M088\n---\n# W2-116 The designers' store in the product\n\nThe owner's SMART-WORK-1 decision 2 (DEC-983): the designers' store (DEC-963, DEC-966 item 3) becomes the product's, not only the CTO's `refresh_integration_store.sh` and `store_refresh_daily.sh`.\n\n- **Why:** a test designer retrieves only from the integration branch's store, so its retrieval never serves a ticket's implementation. W2-33's role files and W2-83b's playbooks will tell an adopted product's designers so; nothing in the product builds that store.\n- **This repository's own configuration:** the place (`~/gov-os-worktrees/W2-00-store`) and the two times a day; the CTO's scripts are retired once this lands.\n- **Order:** after W2-60b (the launcher's files) and W2-33 (the rule it serves); before EXAMIN's copy (W2-27).\n\n**DEC-1087 (3) placed here (CTO, 2026-11-06, delegated P3 on the scope):** the owner orders the refresh after every\nmerge into integrate built, tested and reviewed before re-pin window 4, so the window puts it live. The worktrees get\nthe integration store's path, so workers can search.\n- **S2's interface (pass 2b; P-W2-116-S2-INTERFACE Q1 (a), the CTO, DEC-1157 (12), 2026-11-13).** A product tick that\n  watches a configured verdict file; the nightly does not change.\n  - **Config** in `rebuild.yaml`: `integration_refresh: {branch, after_nightly: {verdict: <glob>, latest: \"HH:MM\"},\n    second: \"HH:MM\"}`.\n  - **Command:** `gov rebuild --integration <branch> --when-due`. It refreshes when a verdict file is newer than the\n    last scheduled refresh, when `latest` passes without one, or once `second` passes; otherwise it builds nothing and\n    says `not_due`.\n  - **Record:** each scheduled refresh writes `<link>.refresh.json`. Tests plant the clock with `GOV_NOW`.\n  - **Error:** a missing or invalid time refuses `REBUILD_CONFIG_INVALID`, naming the key.\n  - **`gov status`** gains an `integration_store` part: head, branch head, built time, age, `stale` and the stale\n    reason. **Stale:** the store's head is behind the branch, or it was built before the last time a refresh fell due.\n  - **This repository's values** (Q2 (b), in this ticket's paths): `branch: w2/integrate`, verdict glob\n    `.gov-runtime/scratch/orchestrator/log/nightly/*/run.txt`, `latest: \"10:00\"`, `second: \"18:00\"`.\n  - **Cron:** a line every 5 minutes, in window 4's ACT next to the hook (not this ticket).\n  - **R2-F3 (Q3 (a)):** the continuation token carries a mark of the half it was made on, checked when it is used\n    (`src/gov/retrieval/retrieve.py`).\n- **This pass builds S1, S3 (widened, below), S4 and S5, and the three failure lines.** S2's two daily times and\n  `gov status` stay for the next pass. Until then the CTO's `store_refresh_daily.sh` runs as the backstop (DEC-1087\n  (3)).\n- **S3 widened:** `gov launch` points every worker session's retrieval at the integration store, not only a\n  designer's. A designer's retrieval still never reads a ticket worktree's store. A worktree has no store of its own\n  today, so a worker's search answers `STORE_MISSING` (checked 2026-11-06).\n- **S4's trigger:** \"after every landing\" covers every merge into the integration branch, by the merge queue or by\n  hand. The product offers the refresh as a command run after the merge (`gov rebuild --integration <branch>`, idempotent\n  at an unchanged head). The hook that calls it after a hand merge is installed by the owner's operator in re-pin window\n  4's ACT (hooks are the operator's). The design is the engineer's, stated in its evidence record.\n- **The deps W2-60b (the session record) and W2-33 (the roles) are not needed** for this pass: it touches neither the\n  session record nor the role files. They stay in `deps:` for S2 and the role rule's text.\n- **The rebuild uses the code it runs under.** The store at window 4's head is built by window 4's code, so the pinned\n  code and the store always match. The engineer states how the double buffer keeps the ready half answering while the\n  other builds (F2).\n\n**TESTS-READY and the designer's points settled (CTO, 2026-11-06, delegated P3):**\n- **The tests:** `tests/acceptance/W2-116/` on `w2/W2-116-tests`.\n- **The interface they assume:**\n  - `gov rebuild --integration <branch>`, its link at the path `rebuild.yaml`'s `integration_store` names (W2-122's\n    key);\n  - a seed from a store behind the head names the base's head commit (12 hex digits or more) and says `behind`.\n- **`allowed_paths` widened:** S3 needs a plain `gov retrieve` in a launched session to answer from the integration\n  store. So the launcher's session env (`src/gov/launch/launcher.py`) and the place `gov retrieve` picks its root\n  (`src/gov/retrieve/command.py`) are added, with the evidence record. Use an environment variable the launch sets and\n  `gov retrieve` reads when no `--root` is given.\n- **The refresh after a merge seeds from the ready half,** so it re-embeds only what changed (the designer's N-1).\n- **A build whose semantic store is not recreated counts as failed** (N-2), as the CTO's script counts it.\n- **Untested (N-4):** a search through the link writes its question-vector cache into the ready half. The engineer\n  states whether a sandboxed session may write there, or where the cache goes instead.\n\n**Pass 1 merged (CTO, 2026-11-06, `75acb0ff`; review READY in round 2, `reviews/w2-116.md`).** For the next pass (S2),\nriding along (DEC-802):\n- **R2-F1:** `gov retrieve --root <link>` still resolves the link once per facet. Resolve the root once in\n  `_store_root` in both branches. The plain form with `GOV_STORE` is fixed.\n- **R2-F3:** a continuation token carries no mark of the half it was made on. Page 2, asked after a switch, pages the\n  other half. The parallel-agents test after window 4 measures it (DEC-1087 (10)).\n- **F7:** the merge queue's promotion builds with the clone's code. Retire it, or make it build with the pinned gov,\n  once the hook is live.\n- **Window 4's ACT** installs the hook with `flock -o` (R2-F2), `env -u PYTHONPATH -u PYTHONHOME -u PYTHONSTARTUP -u\n  GOV_REBUILD_LOCK` (F5), and the separate `W2-00-store.refresh.lock` taken before the heavy slot (F6).\n- **F3,** a stale `index.lock` after a refresh killed during its checkout, is a row (not ordinary work).\n\n[DEC-1087]\n- **W2-60b dropped from deps (CTO, 2026-11-13 16:00, a plan-order P2, DEC-957):** S2 needs no W2-60b code (the session record, the role set, KNOWN_ROLES); with DEC-1167 (3) moving W2-60b after the copy starts, the dependency made a cycle W2-27 -> W2-116 -> W2-60b -> after W2-27's start. W2-33's rule text is delivered (closed). `src/gov/status/**` added for S2's `gov status` line.\n",
  "authority": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "mandatory": [
    {
      "id": "DEC-1109",
      "sha256": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4b36c28f1d8ad543975372c226a3c47b9c1b89204c8aa5f054d770ed8ebfbde5",
      "reason": "declared in sources",
      "tokens": 468
    },
    {
      "id": "DEC-1112",
      "sha256": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "73856ce6d8f2441a1cd8c74538a84c9584c8a978a5045ad9618f6ac98b56dbc2",
      "reason": "declared in sources",
      "tokens": 498
    },
    {
      "id": "DEC-983",
      "sha256": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "233beeb29481fec13ee793eb99cd2539861b3463f9e5950631e7ff9b134505de",
      "reason": "declared in sources",
      "tokens": 674
    },
    {
      "id": "DEC-982",
      "sha256": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "53e4421664306dc765bf7db22f615b9b7a8deaf49c4550deff1b70a737b334ff",
      "reason": "declared in sources",
      "tokens": 766
    },
    {
      "id": "DEC-963",
      "sha256": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "4a1905d866aafee5adc282ec609265f7df15540c75f06c3e5bbd528b3810cb7e",
      "reason": "declared in sources",
      "tokens": 821
    },
    {
      "id": "DEC-966",
      "sha256": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "1a88776392ae3ef7540de64dabef936038b679629045776e45b588bf20ceeec3",
      "reason": "declared in sources",
      "tokens": 607
    },
    {
      "id": "DEC-1014",
      "sha256": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "c77bbc022cae4d3901fe4d3659051b4a42d541f4dcf3b330e3e2b0d7bedda549",
      "reason": "declared in sources",
      "tokens": 624
    },
    {
      "id": "DEC-1015",
      "sha256": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "f3de26fd33f5e175c6dddb75706ec8acc189c7d89162bb67a4f59aa973473763",
      "reason": "declared in sources",
      "tokens": 689
    },
    {
      "id": "DEC-1083",
      "sha256": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "907612978858f8b9d55318cc0e8f313d7f06c317d235cf28af27142240e181be",
      "reason": "declared in sources",
      "tokens": 711
    },
    {
      "id": "DEC-1087",
      "sha256": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "2f6dbbf2fe7939aeef5a29de2e41d93144997ccd061d4af5bf04f5609d1d3298",
      "reason": "declared in sources",
      "tokens": 1467
    },
    {
      "id": "DEC-719",
      "sha256": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "76e88cd4b06f7b5b75d21579f94f0243235def45e6714247a7b7f1a784751add",
      "reason": "declared in sources",
      "tokens": 655
    },
    {
      "id": "DAEO-kia7",
      "sha256": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "ef3935e07048d805e4639d9c068b19d614c7387feaf8f2e4450c23883fba8725",
      "reason": "declared in sources",
      "tokens": 896
    },
    {
      "id": "DAEO-lrre",
      "sha256": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "authority": "task",
      "lifecycle": "closed",
      "constraint": "8e205955baf4b3da66dda2983331718d5bd8db493aaaacf4043285375419db03",
      "reason": "declared in sources",
      "tokens": 1622
    }
  ],
  "supplementary": [
    {
      "id": "1a507a0e364a6e7208ae51aa",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "## Files\n\n- `w2_116_support.py`: the planted project and its landings, the two stand-in endpoints, the commands, the link,\n  the hand-built store, the searches and the stand-in CLI for `gov launch`.\n- `conftest.py`: the case's box, the two endpoints, the environment, the project.\n- `test_w2_116_double_buffer.py` (S1, F2, F3, freshness), `test_w2_116_launch.py` (S3, F1),\n  `test_w2_116_refresh.py` (S4), `test_w2_116_reindex.py` (S5, F2, F3).\n\n**D-10's red fix (2026-11-10, W2-20 `DAEO-r30l`, DEC-1088 (5)(b), DEC-1109):** `w2_116_support.launch_and_search` plants an open gate (`plant_open_gate`, W2-136's form) in the box's HOME and adds its readings to the launch's environment. Its six launch cases stay red after it, for another reason reported to the CTO: the session's cleaned environment (W2-56 S5) no longer carries `W2_116_SESSION_LOG` to the stand-in CLI. The gate is W2-20's, not under test here; no expectation changes. W2-20 S19 runs the resource gate on every `gov launch`; with no `gate.json` in the case's HOME it shuts, and with the machine's own it shuts under load.\n\n",
      "tokens": 273
    },
    {
      "id": "8fe4fd172bd4ad411d46733b",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-5 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n| success-5 | `test_w2_116_reindex.py::test_s5_guard_a_model_less_re_index_of_a_tree_keeps_its_vectors_and_reports_the_facet_unavailable` | green (guard) | a plain model-less rebuild keeps every vector and reports `semantic: not_recreated` with `EMBEDDER_UNAVAILABLE` |\n| failure-1 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | as in success-3 |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | no `--integration` |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale` | red | no `--integration` |\n| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |\n",
      "tokens": 267
    },
    {
      "id": "342a04ae563d98b84548ecf2",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-test-designer]` | red | as above |\n| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[product-spec]` | red | as above |\n| success-3 | `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store` | red | the designer's search in a ticket worktree with its own store gives the engineer's new note (`docs/engineer-new.md`) |\n| success-3 | `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket` | green (guard) | the session's `env` keeps `GOV_ROLE` and `GOV_TICKET` and starts in the worktree |\n| success-4 | `test_w2_116_refresh.py::test_s4_after_a_merge_the_refresh_brings_the_store_to_the_new_head` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_at_an_unchanged_head_the_refresh_does_nothing` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` | red | no `--integration` |\n",
      "tokens": 292
    },
    {
      "id": "f070cd6977599617110c4fa5",
      "path": "governance/project/orchestration/reviews/w2-27-citp.md",
      "text": "### F9: the effect on the memory store and the measure is not stated\n\nUnder V (i), the apply rewrites 278 files under `docs/contract/`. It inserts about 10 lines into `contract.yaml` (the\n4.3 entry, and CAP-45's wave note and sources) and one row into `CONTRACT_v4.md`, so every later line number moves. The\nnote does not mention the store's refresh and re-embedding of these files, or the measure's re-anchoring of labels on\nthe Contract's files (DEC-1084). It also does not place the apply relative to the experiment windows (E1 to E5, the\nfresh 80 on a fixed pin). The measure runs on pinned clones, so this is probably harmless. One line in \u00a74 settles it.\nI opened no evaluation set.\n\n- Ordinary work: yes, because the apply lands on integrate while the experiments run.\n- Consequence: other.\n\n",
      "tokens": 200
    },
    {
      "id": "84c5da38559f1e5aeeed0f1e",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-4 | `test_w2_116_refresh.py::test_s4_the_refresh_after_a_merge_re_embeds_only_what_the_merge_changed` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_the_integration_store_is_the_warm_base_gov_rebuild_seed_reads` | red | no `--integration` |\n| success-4 | `test_w2_116_refresh.py::test_s4_a_seed_from_a_store_behind_the_integration_head_is_named` | red | the seed from the hand-built store at H1, into a tree at H2, is `seeded` with `base`, `reason`, `copied`: no head, no `behind` |\n| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_behind_the_head_re_embeds_only_what_changed` | green (guard) | W2-122's seed: only `changed.md` and `merged.md` are embedded |\n| success-4 | `test_w2_116_refresh.py::test_s4_guard_a_seed_from_a_store_at_the_head_does_not_say_behind` | green (guard) | the seed says no `behind` today; it must not start to at the head |\n| success-5 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n",
      "tokens": 271
    },
    {
      "id": "967690db82b58c1822e82f92",
      "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md",
      "text": "## 5. Search during a refresh, and the continuation (W2-116's R2-F1 and R2-F3)\n- **The probe:** a search every 1.5 s for 4 minutes, alternating the two forms a worker uses (`--root <link>`, and `GOV_STORE=<link>` from inside a worktree with no store). A record commit landed during it.\n  - 147 searches: 0 errors, 0 fallbacks, 0 with a facet missing.\n  - The answers changed from the old half to the new half **exactly once**, in both forms: 92 old, then 55 new, with no flip-back.\n  - One search spanned the switch and answered from one half. No answer had the new record through only one facet, so R2-F1 (the link resolved once per facet) never showed.\n- **R2-F3, page 2 after a switch:** it is **refused**, with `CONTINUATION_INVALID` (\"the continuation's candidate pool is not this question's: the store or the pool settings changed since the earlier call\"). It never pages the other half silently. The worker asks page 1 again. Agent B saw the same.\n  - The refusal does not name the store the token came from (B's note).\n\n",
      "tokens": 257
    },
    {
      "id": "353a3809b2193d483afb2243",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "- *the warm base:* a ticket worktree at the store's head, `gov rebuild --seed` with no folder: `seeded`, `base` the\n  link's half, nothing embedded.\n- *model-less re-index:* the H2 refresh with no model does not report success with a recreated semantic store,\n  names `semantic`, leaves the link, the ready half's head and its vectors, and the ready store answers; with the\n  model back the next refresh switches.\n\n**A check of the tests themselves** (a scratch copy of `src`, never committed): a sketch of about 60 lines\n(`--integration` alternating two halves `<link>-a` / `<link>-b`, each built by a child `gov rebuild --seed <ready\nhalf>`, the link replaced only when that child is ok with its semantic store recreated; the launcher putting\n`integration_store` in the session's env and `gov retrieve` reading it when no `--root` is given; the seed adding\nthe base's `head` and a `behind` sentence) passes all 20. A mutant of it that builds into the half in use and\nswitches on a failed build fails five: the alternation, the search during a build (`semantic: stale`), the\nfreshness case, the killed build (the ready half moved) and the model-less re-index.\n\n",
      "tokens": 291
    },
    {
      "id": "3d86d9347c37c13d7866a98c",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "**D-10's red fix, the cleaned session environment (2026-11-10, W2-116 `DAEO-f58b`, DEC-1112 (3); Rewrite-Reason DEC-826 Q5, DEC-877 item 4):** W2-56 S5 gives a launched session a cleaned environment, so no parent variable reaches the stand-in CLI: not `W2_116_SESSION_LOG` (its `KeyError`), nor the question, the stand-in endpoints or `PYTHONPATH`. The stand-in now has its log, its question and the case's environment written into it when the case plants it (`install_cli`); its search runs with the case's environment beneath the session's own environment and the settings' `env` block, so whatever the launch gives the session wins, as before W2-56 (the case's environment names no store). The fixture project also plants the eight `.claude/templates/<stem>.md` copies (W2-153, DEC-1050; W1-46's and W2-56's form): without them `gov launch` refused every case with `LAUNCH_NO_TEMPLATE` before the session ran. No assertion changes. On integrate `9ca161a6f` the six launch cases (`test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer]`, `[independent-auditor]`, `[independent-test-designer]`, `[product-spec]`, `test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store`, `test_w2_116_launch.py::test_s3_guard_the_launched_session_keeps_its_role_and_ticket`) pass.\n",
      "tokens": 343
    },
    {
      "id": "7f29cec2abf86733bd5a2b0e",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| failure-2 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |\n| failure-2 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n| failure-3 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | no `--integration` |\n| failure-3 | `test_w2_116_reindex.py::test_s5_failure2_failure3_a_model_less_re_index_of_the_integration_store_keeps_its_index_and_says_so` | red | no `--integration` |\n\n**What each case asks once `--integration` exists:**\n- *the build keeps \u2026:* the link's target is outside the project, a detached worktree at the branch's head, and a\n  search through the link answers with both facets available.\n- *the next build \u2026:* H2's build switches to the other half and leaves the first at H1; H3's goes back into the\n  first; exactly two worktrees, both detached.\n- *a search during a build \u2026:* with H2's build held half-way, the link has not moved, a search through it answers\n",
      "tokens": 295
    },
    {
      "id": "2eca1ecd5a18190b04c7b1f5",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | as above |\n| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_freshness_a_search_through_the_link_while_the_other_half_rebuilds_is_never_stale` | red | as above |\n| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_failure3_a_build_killed_half_way_leaves_the_link_and_the_ready_store_answers` | red | as above |\n| success-2 | next pass (DEC-1087 (3)): the two daily times and gov status; no case in this pass | \u2014 | \u2014 |\n| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[engineer]` | red | the session's plain search answers `STORE_MISSING`: the launch sets only `GOV_ROLE`, `GOV_TICKET` and the temp folder |\n| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-auditor]` | red | as above |\n| success-3 | `test_w2_116_launch.py::test_s3_every_worker_session_searches_the_integration_store_from_a_worktree_with_none[independent-test-designer]` | red | as above |\n",
      "tokens": 292
    },
    {
      "id": "5743853c55dfe3c1674c63b0",
      "path": "tests/acceptance/W2-116/test_w2_116_launch.py",
      "text": "def test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store(box, env, project):\n    half = support.hand_built_store(box, project, env)\n    worktree = support.worktree(project, box.base / \"worktrees\" / \"W2-901\", branch=\"w2/W2-901\")\n    support.write(worktree / ENGINEERS, support.note(ENGINEERS_WORD))   # the engineer's work, on the ticket branch\n    support.git(worktree, \"add\", \"-A\")\n    support.git(worktree, \"commit\", \"-q\", \"-m\", \"the engineer's new note\")\n    built = support.rebuild(worktree, env)\n    assert built.ok, f\"the ticket worktree's own store was not built\\n{built.describe()}\"\n    premise = support.search(worktree, env, ENGINEERS_WORD)\n    assert ENGINEERS in support.evidence_paths(premise), (\n        f\"premise: the ticket worktree's own store does not hold the engineer's note\\n{premise.describe()}\")\n    assert not (half / ENGINEERS).exists(), \"premise: the integration store's half holds the engineer's note\"\n\n    session = support.launch_and_search(box, env, worktree, \"independent-test-designer\", ENGINEER_TICKET,\n                                        ENGINEERS_WORD)\n",
      "tokens": 278
    },
    {
      "id": "DAEO-mb2t",
      "path": ".tickets/DAEO-mb2t.md",
      "text": "- tests/acceptance/W2-13/test_w2_13_unavailable.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-13/test_w2_13_latency.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-76/test_w2_76_timings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-76/test_w2_76_unchanged.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W2-116/test_w2_116_reindex.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/acceptance/W1-41/test_w1_41_embedding_policy.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_w2_116_integration.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_no_embeddings.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/rebuild/test_w2_122_seed.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n- tests/unit/retrieval/test_w2_32_rebuild_cut.py  # one test-designer revision under S1's rule (P1-L (a), DEC-1150 (3))\n",
      "tokens": 298
    },
    {
      "id": "b08edcec71ea046892af000f",
      "path": "tests/acceptance/W2-116/README.md",
      "text": "## KPI lines, tests, and the outcome on `w2/integrate`\n\nRun in the launch sandbox through the heavy slot, with `-m \"not local_only\" -k \"not real and not green_here and not\ntime_limit\"` (it leaves none of these out), on the branch point `fc61f303d467` and again on integrate's head\n`e3355def9f99` (its `src` exported to scratch; W2-32's retrieval changes since): **20 tests, 16 failed, 4 passed**,\nthe same on both. Every red fails on its line's behaviour or on the missing `--integration` option, none on a\nplanted premise.\n\n| KPI line | Test (node id) | On integrate | Why |\n|---|---|---|---|\n| success-1 | `test_w2_116_double_buffer.py::test_s1_the_build_keeps_the_branch_head_in_a_detached_worktree_outside_the_project_behind_the_link` | red | `gov rebuild` takes no `--integration`: a usage error, exit 2 |\n| success-1 | `test_w2_116_double_buffer.py::test_s1_the_next_build_goes_into_the_other_half_and_the_two_alternate` | red | as above |\n| success-1 | `test_w2_116_double_buffer.py::test_s1_failure2_a_search_during_a_build_is_answered_from_the_ready_half` | red | as above |\n",
      "tokens": 271
    },
    {
      "id": "1e6be0b90c6d67f37e8bf4bf",
      "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md",
      "text": "  - the S3 cases would answer STORE_MISSING and go red;\n  - the F1 case would answer from the worktree's own store and go red.\n- **No hidden leak:** the planted values live in the stand-in's file and reach only its child `gov retrieve`. They neither widen the cleaned environment nor read from it. No W2-116 case ever checked that parent variables are absent; that is W2-56 S5's job, and its cases are untouched.\n- **What the session received is still checked:**\n  - The guard case checks `GOV_ROLE` and `GOV_TICKET` in the settings block, and that the session's working folder is the worktree.\n  - S3 and F1 check which store the search answered from, which depends on the launch's `GOV_STORE`.\n  - The assertions in `test_w2_116_launch.py` are unchanged; the diff touches only its module docstring.\n- **Templates:** the eight template copies are committed in H1, so W2-153's template refusal never stops these launches. W2-116 asserts nothing about templates.\n\n*W1-32*\n\n- **The failure is still in the launcher's removal:**\n  - The launcher creates the session's temp folder directly in its own TMPDIR (`launcher.py:521`).\n",
      "tokens": 282
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-114 | A | **New (DEC-982, P1-NEW-TICKETS-2026-10-31 T2).** W1-28's whole-tree copy check reads code, not message text; every true copy still found (`DAEO-4eux`) | test-revision | independent-test-designer | LITE | none | 40 | DEC-982, DEC-385, DEC-906 |\n| W2-115 | A | **New (DEC-983, SMART-WORK-1 decision 1).** `gov close`, the smart close: scoped runs only, a close refused only by a red its own change caused, the culprit of a batch sent back, no lists, a close record, the nightly's full secrets scan; the strict close kept built; before EXAMIN's copy (`DAEO-emq1`) | implementation | engineer | FULL | W2-55 | 400 | DEC-983, DEC-982, DEC-968, DEC-953 |\n| W2-116 | A | **New (DEC-983, SMART-WORK-1 decision 2).** The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, read by a test designer's retrieval; before EXAMIN's copy (`DAEO-f58b`) | implementation | engineer | STANDARD | W2-60b, W2-33 | 150 | DEC-983, DEC-982, DEC-963 |\n",
      "tokens": 256
    },
    {
      "id": "DAEO-6f0s",
      "path": ".tickets/DAEO-6f0s.md",
      "text": "  - 'The launch record also holds `tier`, `criticality`, `model_source` (role default, by criticality, after --, trial, promotion), the trial id and the promotion reason, each null when not given. Verify: a planted launch by criticality, one with a trial and one promoted each record their fields; a plain launch records them null [DEC-1120 (3)] [from W2-60a S8, DEC-1167]'\n  - 'On a FULL ticket the second review is the probe, Opus max, and the first is Opus high; the record shows both; the same setting twice is refused unless the owner named it; max on any other review needs `--reason`. Verify: a planted FULL ticket: the two launch records differ as stated; the same setting twice is refused [DEC-1014 item 1, SMART-WORK-5 A, DEC-1015 item 3, DEC-1120 (2)] [from W2-60a S10, DEC-1167]'\n  - 'A ticket whose review records show two failed reviews or a fail-open finding launches its next round on Opus at the table''s effort, recorded as `promotion` with the reason and the record''s path; a lower model is refused. Verify: planted review records: one with two failed reviews, one with a fail-open finding, one with neither [DEC-1120 (3)] [from W2-60a S11, DEC-1167]'\n  failure:\n",
      "tokens": 296
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "---\nid: DAEO-9bc0\nstatus: closed\ndeps: [DAEO-k7hz]\nlinks: [DAEO-k7hz]\ncreated: 2026-11-02T00:18:23Z\ntype: task\npriority: 1\nassignee: product-spec\nexternal-ref: W2-11b\ntags: [wave-2, skill, standard]\nwbs_id: W2-11b\ntitle: 'The orchestration skill''s and the reviewer template''s seven lines that W2-11 landed without (SMART-WORK-3, SMART-WORK-4 lines 4, 6, 9, 10, SMART-WORK-5 B and C)'\nclass: skill\nstate_class: AUTHORITATIVE\nrole: product-spec\ndepends_on:\n- DAEO-k7hz\nallowed_paths:\n- template/governance/kernel/templates/brief-*.md\n- template/governance/kernel/skills/orchestration/**\n- template/governance/kernel/skills/qa-review/**\n- .claude/skills/orchestration/**\n- .claude/skills/qa-review/**\n- .rulesync/skills/orchestration/**\n- .rulesync/skills/qa-review/**\n- template/.rulesync/skills/orchestration/**\n- template/.rulesync/skills/qa-review/**\n- docs/changes/W2-11b-CIT-P.md\nkpis:\n  success:\n",
      "tokens": 226
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "  - 'The orchestration skill: the resume block comes first and the checkpoint stays under a set token budget; over it, the stop hook names it [DEC-1014, SMART-WORK-4 line 10]'\n  - 'Delegation does not count the recommendation and the proposer''s agreement as corroboration on a decision that touches verification; that needs an independent reviewer''s record [DEC-1014 item 1, row 4, SMART-WORK-5 B]'\n  - 'The daily document gives the week''s net ticket growth (filed minus closed, counted from the tickets) and the share of new tickets that fix the machinery; when net growth passes a configured share of the remaining plan in a week (default 5 %), it goes to the owner as one re-plan package with DEC-105''s three options, not as single P1s [DEC-1014 item 1, row 2, SMART-WORK-5 C]'\n  failure:\n  - 'A skill or template that still teaches the old rule (agreement counted as corroboration; a typed count; a rule with neither a mechanism nor \"prose only\").'\n  - 'A copy (.claude/, .rulesync/, template/.rulesync/) that differs from its kernel source.'\nprofile: STANDARD\nsources:\n- DEC-1022\n- DEC-1010\n- DEC-1014\n- DEC-1015\n- DEC-105\nest_loc: 120\nacceptance_tests:\n  path: tests/acceptance/W2-11b/\n",
      "tokens": 299
    },
    {
      "id": "DAEO-9bc0",
      "path": ".tickets/DAEO-9bc0.md",
      "text": "# W2-11b The orchestration skill's and the reviewer template's seven lines\n\nThe owner's DEC-1022 item 3 (P-W2-11-LINES (a)): seven approved KPI lines meant for W2-11 (SMART-WORK-3's reviewer\ntemplate and qa-review line; SMART-WORK-4 lines 4, 6, 9 and 10; SMART-WORK-5 B and C) could not ride in W2-11's round,\nwhich landed without them. This ticket carries them, word for word. It starts once W2-11 (`DAEO-k7hz`) closes. If\nW2-11 goes back for another round instead, the seven lines ride along in that round and this ticket is withdrawn.\nSMART-WORK-5 B fixes a product defect: the kernel orchestration skill counts the recommendation's and the proposer's\nagreement as corroboration (`template/governance/kernel/skills/orchestration/SKILL.md`).\n\n**D9-FATES (DEC-1083):** Merged into W2-128 by DEC-1083. S1, F1 and F2 fold into W2-128's TPL-1 S3 and TPL-4 (no new line); S2 moved to W2-128 as the reviewer template's line; S3 to S7 lifted. S1's other half (the qa-review skill's triage, its blocking rule, the two-round cap and the two questions) lives in W2-11 S12 and W2-33's moderator line (S10 in D9-FATES' numbering, its S6 since its lifts and moves).\n",
      "tokens": 289
    },
    {
      "id": "DAEO-j9z6",
      "path": ".tickets/DAEO-j9z6.md",
      "text": "  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired Verify: grep of the close and queue code for this repository''s branch names, paths and ticket ids finds 0 lines; a planted second repository''s queue runs with the same code; this repository''s queue runs on it and W2-97''s tool is no longer called. [DEC-983, DEC-982] [moved from W2-117 S3, DEC-1083]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it Verify: a planted landing: the integration store''s refresh (W2-116) is started once afterwards and the queue''s own warm clones are seeded from that store, both visible in the queue''s record. [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3] [moved from W2-117 S4, DEC-1083]'\n",
      "tokens": 220
    },
    {
      "id": "DAEO-zkr9",
      "path": ".tickets/DAEO-zkr9.md",
      "text": "  - '`gov queue` gives W2-97''s queue in the product: the commit tested is the commit landed; one run per batch on the merged result, in a heavy-job slot (W2-20); a run skipped when the merged code is identical to what the lead tested, with its reason; a red batch''s culprit ejected and the rest advanced (W2-115''s attribution) [DEC-959 item 1, DEC-983, DEC-982]'\n  - 'Each green run lands and closes in one step: the ticket merges, its close record (the run, its counts, every red with its verdict, the baseline traced against) is written and the ticket closed on that run, the close citing the queue''s record instead of running its own tests on the same code; no ticket sits merged but not closed [DEC-989, DEC-959 item 1, DEC-983, DEC-982, DEC-1003, SMART-WORK-2]'\n  - 'Nothing project-specific: no branch, path or ticket of this repository is named in the code; this repository''s queue moves onto it and W2-97''s tool is retired [DEC-983, DEC-982]'\n  - 'After each landing, the queue starts the integration store''s refresh (W2-116) and seeds its own warm clones from it [DEC-1014 items 4 and 6, SMART-WORK-5 E, DEC-1015 item 3]'\n",
      "tokens": 285
    },
    {
      "id": "DEC-1022",
      "path": "docs/DECISION_REGISTER.md",
      "text": "- **Decision:** (1) ACT-PUSH-INPUT-1's live test is re-run by day, after 07:30 on 2026-11-02: the CTO pings first, the owner steps away from the laptop and lets the prompt wait a few minutes (at 00:12 the owner approved from the laptop within 25 s, so the phone push was probably skipped as the owner was active). (2) P-W2-90b-1 (b): W2-90b's KPI S4 for W1-46's live sessions and W1-50's freeze launcher is re-baselined under DEC-822 item 3 (a live session judges the pinned guard by design; the non-live cases judge the worktree's code); the line sits in W2-90c (`DAEO-fu3n`, DEC-1016) and is re-worded there; nothing is lowered. (3) W2-11's seven unplaced lines (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C): option (a), W2-11b (`DAEO-9bc0`, product-spec, STANDARD) filed with them word for word, to start once W2-11 closes; if W2-11 goes back for another round instead, the lines ride along in it and W2-11b is withdrawn. (4) SMART-WORK-4 line 3 (reviewer recall per model): option (c), Wave 3 row W3-P21.\n\n| Version | Date | Change |\n|---|---|---|\n",
      "tokens": 279
    },
    {
      "id": "WAVE-2-WBS",
      "path": "docs/plan/WAVE_2_WBS.md",
      "text": "| W2-66b | A | **New (DEC-1027 B).** W2-66's record-only case reads `win_toast.ps1` as code; a test revision under the owner's named decision (`DAEO-zuiy`). | test-revision | independent-test-designer | LITE | none | 2 | DEC-1027, DEC-906 |\n| W2-11b | A | **New (DEC-1022 item 3, P-W2-11-LINES (a)).** The seven KPI lines W2-11 landed without (SMART-WORK-3's reviewer template and qa-review line; SMART-WORK-4 lines 4, 6, 9, 10; SMART-WORK-5 B and C), word for word; starts once W2-11 closes; withdrawn if W2-11 takes them in another round (`DAEO-9bc0`). | skill | product-spec | STANDARD | W2-11 | 120 | DEC-1022, DEC-1014, DEC-1010 |\n| ACT 2 | \u2014 | **Milestone (DEC-954 item 6; PLAN-GROWTH-1 gap 4).** The one re-pin, an owner ACT, once memory, the roles and the three layers' foundations have landed; W2-100 and W2-101 start after it | milestone | owner | \u2014 | memory landed (K4), the roles landed (W2-33, W2-60b, W2-11), W2-104 | 0 | DEC-954 item 6 |\n| W2-55 | C | Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see (DEC-791) | implementation | engineer | STANDARD | W2-03 | 150 | DEC-791 (i) |\n",
      "tokens": 287
    }
  ],
  "supplementary_query": "The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer's retrieval reads (SMART-WORK-1)\n`gov rebuild --integration <branch>` keeps a store of that branch's head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]\nIt is refreshed after the nightly's verdict and at a set second time each day (both in the project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]\n`gov launch independent-test-designer` points the session's retrieval at it; a designer's retrieval never reads a ticket worktree's store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role's plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]\nThe store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]\nA re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]\n`gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer's; a designer's retrieval never reads a ticket worktree's store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer's never names a worktree's store [DEC-1087 (3), DEC-963] [added, the CTO's note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]\nA designer's retrieval answered from a ticket worktree's store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]\nThe link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]\nA re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]",
  "further_batch": [
    {
      "id": "85b4eff26dd0e6bc7205707e",
      "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md"
    },
    {
      "id": "DAEO-2bdu",
      "path": ".tickets/DAEO-2bdu.md"
    },
    {
      "id": "ADR-0002",
      "path": "docs/adr/ADR-0002-architecture-and-stack.md"
    },
    {
      "id": "8f356b7e327136440b9c3c32",
      "path": "docs/research/W2-88-memory-practice.md"
    },
    {
      "id": "868e890ee2e86be828d4d6b0",
      "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
    },
    {
      "id": "d94dd360e8fb33577ee0ecea",
      "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md"
    }
  ],
  "supplementary_batches": [
    {
      "items": [
        {
          "id": "1a507a0e364a6e7208ae51aa",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "8fe4fd172bd4ad411d46733b",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "342a04ae563d98b84548ecf2",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "f070cd6977599617110c4fa5",
          "path": "governance/project/orchestration/reviews/w2-27-citp.md"
        },
        {
          "id": "84c5da38559f1e5aeeed0f1e",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "967690db82b58c1822e82f92",
          "path": "governance/project/orchestration/packages/LIFT-1/PAT-1-RESULT.md"
        },
        {
          "id": "353a3809b2193d483afb2243",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "3d86d9347c37c13d7866a98c",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "7f29cec2abf86733bd5a2b0e",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "2eca1ecd5a18190b04c7b1f5",
          "path": "tests/acceptance/W2-116/README.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "5743853c55dfe3c1674c63b0",
          "path": "tests/acceptance/W2-116/test_w2_116_launch.py"
        },
        {
          "id": "DAEO-mb2t",
          "path": ".tickets/DAEO-mb2t.md"
        },
        {
          "id": "b08edcec71ea046892af000f",
          "path": "tests/acceptance/W2-116/README.md"
        },
        {
          "id": "1e6be0b90c6d67f37e8bf4bf",
          "path": "governance/project/orchestration/reviews/D10-W2-56-effects-review.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "DAEO-6f0s",
          "path": ".tickets/DAEO-6f0s.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-9bc0",
          "path": ".tickets/DAEO-9bc0.md"
        },
        {
          "id": "DAEO-j9z6",
          "path": ".tickets/DAEO-j9z6.md"
        }
      ],
      "limit": 10
    },
    {
      "items": [
        {
          "id": "DAEO-zkr9",
          "path": ".tickets/DAEO-zkr9.md"
        },
        {
          "id": "DEC-1022",
          "path": "docs/DECISION_REGISTER.md"
        },
        {
          "id": "WAVE-2-WBS",
          "path": "docs/plan/WAVE_2_WBS.md"
        },
        {
          "id": "85b4eff26dd0e6bc7205707e",
          "path": "governance/project/orchestration/packages/SMART-WORK-5.md"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        },
        {
          "id": "DAEO-2bdu",
          "path": ".tickets/DAEO-2bdu.md"
        },
        {
          "id": "ADR-0002",
          "path": "docs/adr/ADR-0002-architecture-and-stack.md"
        },
        {
          "id": "8f356b7e327136440b9c3c32",
          "path": "docs/research/W2-88-memory-practice.md"
        },
        {
          "id": "868e890ee2e86be828d4d6b0",
          "path": "governance/project/orchestration/packages/ADR-0002-REFRESH/ADR-0002-architecture-and-stack.draft"
        },
        {
          "id": "d94dd360e8fb33577ee0ecea",
          "path": "governance/project/orchestration/packages/EMERGENCY-TOOLS-1.md"
        }
      ],
      "limit": 10
    }
  ],
  "dropped": [
    {
      "id": "85b4eff26dd0e6bc7205707e",
      "reason": "budget exceeded"
    },
    {
      "id": "868e890ee2e86be828d4d6b0",
      "reason": "budget exceeded"
    },
    {
      "id": "8f356b7e327136440b9c3c32",
      "reason": "budget exceeded"
    },
    {
      "id": "ADR-0002",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "budget exceeded"
    },
    {
      "id": "DAEO-2bdu",
      "reason": "budget exceeded"
    },
    {
      "id": "d94dd360e8fb33577ee0ecea",
      "reason": "budget exceeded"
    }
  ],
  "tokens": 19945,
  "budget": {
    "limit": 20000,
    "used": 19945
  },
  "hash": "6d3b0f41f004abac58c6a7f0d91bd859b7f79d57cb6e15bbf3a1e41e1a6159ca"
}
```
