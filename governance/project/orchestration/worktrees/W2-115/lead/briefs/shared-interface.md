## The interface both sides build to (the ticket's Interface, DEC-1112 (3), plus the lead's naming for what it leaves open)

From the ticket (`.tickets/DAEO-emq1.md`, section "Interface"), binding:
- The switch: `governance/project/close.yaml` holding `close: scoped` or `close: strict`. The template's copy
  `template/governance/project/close.yaml` holds `close: scoped`, and so does this repository's. **A project with no
  file runs strict** (today's close, unchanged; F4). An unreadable file or another value is refused (fail closed).
- Refusal codes: `SELECTION_REFUSED` (a selection that cannot be made, S2; and `--verify`'s exit 2, S13),
  `BATCH_UNEXPLAINED` and `CANDIDATE_NOT_ISOLATED` (S6), `VERDICT_MALFORMED`, `VERDICT_NOT_REVIEWER` and
  `FINDING_BLOCKS` (S11). Each refusal prints its code and its reason.
- The close record at the existing place `docs/close/<ticket>/CL-<ticket>.md` (YAML front matter, then text).
- The warm clone at `.gov-runtime/close/clone/` in the project (S10).

The lead's naming for what the Interface leaves open (both the tests and the code use exactly these; the CTO is told):
- `gov close --select <ticket>` prints one JSON object on stdout:
  `{"ticket": "<id>", "suites": [<test paths or node ids, sorted>], "pytest_options": [<strings>]}`, exit 0;
  a refused selection prints `SELECTION_REFUSED: <reason>` on stderr, prints no set, and exits 2.
- `gov close --verify <ticket> [--out <dir>]` (default `<dir>` = `.gov-runtime/close/verify/<ticket>/`), modelled on
  the CTO's `lead_verify.sh`: it writes in `<dir>` `select.json` (the `--select` object), `parallel.xml` and
  `serial.xml` (JUnit; an empty suite when no serial entry is selected), `summary.txt` (one summary line) and
  `verify.exit` (the code, written last). Exit 0 green; 1 a red (a failure or error in either JUnit file); 2 the
  selection refused; 3 a run that did not complete (pytest's exit not 0 or 1, a JUnit file missing, a killed run).
  The serial phase is today's (`gov.close.serial.phase`, W2-57), restricted to entries inside the selection; each
  phase runs in a heavy-job slot (`gov.resources`' slots).
- The close record's front matter, scoped close, carries these keys (strict close: unchanged, it may add `close: strict`):
  - `close: scoped`
  - `commit: <full sha of the commit closed>`
  - `selection: {suites: [...], pytest_options: [...]}`: equal to what `--select` prints for the same ticket
  - `runs: [{name: <str>, passed: <int>, failed: <int>, errors: <int>, skipped: <int>}]` (never a full-suite run)
  - `review: {verdict: READY|<refusal code>, record: <probe record path or null>}`
  - `reds: [{test: <node id>, failure_type: <e.g. AssertionError, timeout, unknown>, caused: true|false, reason: <text>, repair_ticket: <id or null>}]`
  - `culprits: [<ticket or candidate id>, ...]` (an empty list when none)
  - `clone: {path: .gov-runtime/close/clone, reused: true|false, replaced: <reason text or null>}`
  - `nightly: {read: true|false, record: <path or null>}` (S4: the nightly's recorded result read first)
  A missing key is a failed check (S7).
- A red not caused by the change opens a repair ticket in `.tickets/` (the project's ticket form, `assignee:
  orchestrator`, the red's node id and failure type in its text) and the record's `repair_ticket` names its id (S5).
- The structured reviewer verdict (S11) is the probe record's fenced `verdict` block as `governance/project/briefs/JUDGEMENT.md`
  defines it (read it whole); per KPI line: pass or fail; per finding: scope in|out, ordinary work yes|no, consequence
  fails open|loses work|other. Who wrote it is judged from the commit that wrote the probe record (its `Role:` trailer
  `independent-auditor`; a record whose verdict block a commit with `Role: orchestrator` wrote or changed after the
  reviewer's is `VERDICT_NOT_REVIEWER`).
- The test map: only its existing keys (`shared_core`, `record_only`, `record_reading`, `every_close`, `couplings`,
  `test_inputs`); a shared-core path selects the suites its `couplings` entries and the import graph name, never the
  full suite; a changed path that nothing maps is `SELECTION_REFUSED`.
- The nightly (S8): `gov.close.nightly` rebuilds the worktree's stores with `GOV_SECRETS_FULL_SCAN=1` in the rebuild's
  environment, whatever the caller's, before its run; its record (under `docs/close/nightly/`) says
  `secrets_full_scan: true`.
- Batches (S6): `gov.close.batch` builds the merged result without each candidate in turn (a fresh merge of the
  others onto the base, never a revert of merged code); only the culprits go back, the rest land on the same run.
