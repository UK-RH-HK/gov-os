# Brief: independent test designer, W2-116 (DAEO-f58b) pass 2b: S2's acceptance cases and R2-F3

You are the independent test designer (MR-3) for ticket DAEO-f58b (W2-116), profile STANDARD. You write acceptance
tests from the KPI line and the stated interface below, before and without reading the implementation of this pass
(the engineer builds it in parallel in /home/usain/gov-os-worktrees/W2-116; never read its uncommitted work or its
new commits on w2/W2-116 after e51b1fdf6, the counterpart's work, DEC-820). You may read the existing code on your
own branch to learn the public interface (CLI options, envelopes) as it stands.

## Where you work
- Your worktree: /home/usain/gov-os-worktrees/W2-116-tests, branch w2/W2-116-tests (at e51b1fdf6). Write only under
  `tests/acceptance/W2-116/` there. Commit there; never merge, never push.
- The existing suite of this ticket is in `tests/acceptance/W2-116/` (pass 1's cases, `w2_116_support.py`,
  `conftest.py`, `README.md`). Reuse the support code (a planted project with a branch `integrate`, a stand-in
  embedder, `gov(...)` runs as `sys.executable -m gov.cli.main` with the pytest process's PYTHONPATH). Extend it in
  place only by adding; never change what pass 1's cases rely on. Add a section to the README for pass 2b.
- Scratch: /home/usain/gov-os-worktrees/W2-116-tests/.gov-runtime/scratch/td/ (checkpoint and notes).
- Search with the Read and Grep tools; no `gov retrieve`, no `gov context` in the sandbox (DEC-1065). If a search does
  not answer, search once more in other words; then answer from both or say "not found".

## What to write: S2 and R2-F3 cases (new files `tests/acceptance/W2-116/test_w2_116_<name>.py`)
KPI S2: "It is refreshed after the nightly's verdict and at a set second time each day (both in the project's
configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982]. Verify: pass 2's
cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the
second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid
time refuses by name."

At least these, each a named case (name them `test_s2_success_...`, `test_s2_failure_...`, `test_r2f3_...`):
1. A planted config's two times are read: with `GOV_NOW` before `latest` and no verdict file, `--when-due` says
   `not_due` and builds nothing (no half, no record); moving `GOV_NOW` past `second` makes it due with reason `second`
   (so the times were read from the planted config, not defaults).
2. A refresh runs after a newer verdict file (a `verdict:` line file, and a JSON `"verdict"` file), with reason
   `after_nightly`, and writes `<link>.refresh.json` with the stated fields; a matching file without a verdict does not
   count; a verdict file older than the record's `at` does not make it due.
3. `latest` passes without a verdict: due with `after_nightly`; run again the same day: `not_due`.
4. `second`: due once after `second`; the next tick the same day says `not_due`.
5. `gov status --json`'s `integration_store` part: head, branch head, built time and age (age follows `GOV_NOW`), and
   `stale: false` for a fresh store; a store behind the branch (land a commit after the build) is `stale: true` with a
   `behind_branch` reason; a store built before the last due time (plant `GOV_NOW` and the times relative to the
   record's real `written_at`) is `stale: true` with `built_before_due`; no store configured gives the part
   `{"read": false, ...}` and `gov status` still exits 0.
6. A missing or invalid time refuses `REBUILD_CONFIG_INVALID` naming the key (`details.key` and the message): at least
   a missing `second`, an invalid `after_nightly.latest` (e.g. `"25:00"`), and no `integration_refresh` with
   `--when-due`; nothing is built.
7. R2-F3: two store folders at the same commit; a continuation made on one, used against the other, refuses
   `CONTINUATION_INVALID`; used against the same folder it pages. Through the link: a token made through the link, the
   link then pointed at the other half (at the same commit), refuses.

Keep each case's runtime low: one built store reused where the support code allows; plant the clock with `GOV_NOW`
and verdict file times with `os.utime`; never sleep for the clock.

## Check red
Run your new cases on your branch (the code before pass 2b) and record that each fails for the stated reason (an
unknown `--when-due` option, no `integration_store` part, a token accepted on the other folder ...), not for a
fault of the test. A case that passes on the old code: say why in the README (e.g. a guard that already holds), or
make it test the new behaviour. Write the red record (each case, its failure line) to your scratch and into the README.

## How to run pytest (every run)
```
env TMPDIR=/tmp/w2-116-td PYTHONUSERBASE=/home/usain/.local PYTHONPATH=/home/usain/gov-os-worktrees/W2-116-tests/src \
  bash /home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/tools/heavy_slot.sh \
  python3 -m pytest tests/acceptance/W2-116/<file> -q -p no:cacheprovider -o tmp_path_retention_policy=failed
```
(`mkdir -p /tmp/w2-116-td` first; put a multi-line command in a script under your scratch and run it with `bash`.) A
resource gate's refusal is a wait, not a refusal (DEC-1146). Never open the evaluation sets' root or any hidden or
memory-verdict folder.

## Commit
```
git -C /home/usain/gov-os-worktrees/W2-116-tests commit -m "<subject>" --trailer "Task: DAEO-f58b" --trailer "Role: independent-test-designer" --trailer "Implements: DEC-983, DEC-982, DEC-966, DEC-963, DEC-1087" -- tests/acceptance/W2-116/
```

## Rules
- Refused twice for the same call by the guard, the sandbox or a hook: stop and say so; never work around it (DEC-1142 (9)).
- A gap in the interface below: do not guess it into a case; name it in `unresolved` and test what is stated.
- Keep a checkpoint in your scratch (STATE / HEAD / NEXT).

## Return (your last message)
The twelve fields, each a labelled line ("none" where nothing): task / status (DONE, PACKAGES, ESCALATION) /
work_completed / files_changed / evidence (the red run: each case and its failure line, the JUnit or `-q` tail) /
tests / discoveries / risks / lessons / proposed_decisions / unresolved / recommended_next_action. Then `commits:` with
hash12 and subject.


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

## The ticket's context packet (gov context DAEO-f58b --role independent-test-designer --budget 16000; the default 6000-token ceiling refuses this ticket)
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
      "sha256": "3c3c17060dabdc79b34101b1dc844a6f1f4f5b60e612fcae8841ba786fb8bf89",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3c3c17060dabdc79b34101b1dc844a6f1f4f5b60e612fcae8841ba786fb8bf89",
      "reason": "declared in sources",
      "tokens": 1452
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
      "sha256": "3c3c17060dabdc79b34101b1dc844a6f1f4f5b60e612fcae8841ba786fb8bf89",
      "authority": "decision",
      "lifecycle": "ACCEPTED",
      "constraint": "3c3c17060dabdc79b34101b1dc844a6f1f4f5b60e612fcae8841ba786fb8bf89",
      "reason": "declared in sources",
      "tokens": 1452
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
  "supplementary": [],
  "supplementary_query": "The designers' store in the product: a double-buffered store of the integration branch, refreshed after the nightly and once more a day, that a test designer's retrieval reads (SMART-WORK-1)\n`gov rebuild --integration <branch>` keeps a store of that branch's head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-983, DEC-982] Verify: the success-1 cases in tests/acceptance/W2-116/test_w2_116_double_buffer.py (the build in a detached worktree behind the link, the two halves alternating, a search during a build and a killed build answered from the ready half) pass [Verify clause added, DEC-1157 (12)]\nIt is refreshed after the nightly's verdict and at a set second time each day (both in the project's configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-983, DEC-982] Verify: pass 2's cases: a planted configuration's two refresh times are read and the refresh runs after the nightly's verdict and at the second time; `gov status` names the integration store's head and age, and a stale store is named; a missing or invalid time refuses by name [Verify clause added, DEC-1157 (12)]\n`gov launch independent-test-designer` points the session's retrieval at it; a designer's retrieval never reads a ticket worktree's store [DEC-963, DEC-983, DEC-982] Verify: the success-3 cases in tests/acceptance/W2-116/test_w2_116_launch.py pass: each launched worker role's plain search reads the integration store from a worktree with none, and the session keeps its role and ticket [Verify clause added, DEC-1157 (12)]\nThe store is also refreshed after every landing on the integration branch, and it is the warm base `gov rebuild --seed` (W2-122) reads; a seed taken from a store behind the integration head is named, and only what changed since is re-embedded [DEC-1014 items 4 and 6, SMART-WORK-5 D, DEC-1015 item 3] (folds W2-06 S1, S2) Verify: the success-4 cases in tests/acceptance/W2-116/test_w2_116_refresh.py pass: after a merge the refresh brings the store to the new head re-embedding only what changed, an unchanged head does nothing, `gov rebuild --seed` reads it and a seed behind the head is named [Verify clause added, DEC-1157 (12)]\nA re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719]. [moved from W2-06 S5, DEC-1083] Verify: the success-5 cases in tests/acceptance/W2-116/test_w2_116_reindex.py pass: a model-less re-index of the integration store keeps its index and says the semantic facet is unavailable [Verify clause added, DEC-1157 (12)]\n`gov launch` points every worker session's retrieval at the integration store (the `GOV_STORE` of a launched session), not only a designer's; a designer's retrieval never reads a ticket worktree's store. Verify: a launcher unit test per worker role: the session environment names the integration store; a designer's never names a worktree's store [DEC-1087 (3), DEC-963] [added, the CTO's note of 2026-11-06 in the body (S3 widened), DEC-1087 (3)]\nA designer's retrieval answered from a ticket worktree's store. Verify: tests/acceptance/W2-116/test_w2_116_launch.py::test_s3_failure1_a_designer_never_reads_the_ticket_worktree_s_own_store passes [Verify clause added, DEC-1157 (12)]\nThe link switched to a store whose build failed, or a search answered from a half-built store. Verify: the failure-2 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a search during a build and through the link while the other half rebuilds is answered from the ready half, never stale; a build killed half way leaves the link [Verify clause added, DEC-1157 (12)]\nA re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088]. [moved from W2-06 F1, DEC-1083] Verify: the failure-3 cases in test_w2_116_double_buffer.py and test_w2_116_reindex.py pass: a killed build or a failed re-index leaves the previous index and reports the failure [Verify clause added, DEC-1157 (12)]",
  "further_batch": [],
  "supplementary_batches": [],
  "dropped": [
    {
      "id": "supplementary",
      "reason": "the lexical index is stale"
    }
  ],
  "tokens": 13583,
  "budget": {
    "limit": 16000,
    "used": 13583
  },
  "hash": "00cd15c3fa5ff20c6bbd87f96f084308f0951cfe032cf6ef0df9778fc1e5cf43"
}
```
