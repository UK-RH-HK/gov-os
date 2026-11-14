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
