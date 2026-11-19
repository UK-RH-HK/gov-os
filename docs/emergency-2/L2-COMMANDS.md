# L2: the command table, and the landing-and-close as one action

`docs/emergency-2/L2-COMMANDS.md` · 2026-11-18 night · research lead (Sonnet), branch `e2/l2-table` from `w2/integrate` at `0123c8b5f` · docs only, nothing run but `--help`, `grep`, `git log` and `wc`

**The owner's decision (DEC-1214 L2):** "the landing and the close are one deterministic action. The landing writes the close record itself; no separate close step carries weight of its own. The CTO proposes which `gov` commands stay and which retire on that basis: practical, fast, cheap, high quality, records kept, nothing duplicated." With **Q-CLOSE** folded in (the landing records such a red as a known base red) and **M1** (`gov context` retires, another lead tonight).

---

## 0. The owner's page: answer with codes

The result in one line: **37 `gov` commands become 34.** `gov close` merges into `gov queue` (your yes: L2-1). `gov context` (M1) and `gov session-watch` (A-2, audit 3) leave on decisions you already made. The other 31 stay, and none of them duplicates another. The bigger cut is inside the close: about 2,800 of the 6,400 lines of `src/gov/close/`, about 3,650 lines of git-ignored scratch landing tools, and about 8,200 lines of tests that assert the retired strict close.

| Code | Question | Options | Recommendation |
|---|---|---|---|
| **L2-1** | `gov close` merges into `gov queue`: the command, the strict close (repair tickets, iteration counter and escalation after three, trailer-history and probe gates), and `python3 -m gov.close.batch run / run_scoped`. For one release `gov close` answers `retired: use gov queue`. The engine (`gov.close.select`, `attribution`, `isolate`, the record writer) stays under its name. | yes / no | **yes.** In Gov OS itself `gov close` wrote 18 records in `docs/close/` (the last on 2026-10-29); the landing tools wrote 122 in `governance/project/orchestration/closes/`. An adopter with no `close.yaml` still gets the strict close today. Two closes is the duplication you named. |
| **L2-2** | The path map's `accepted_reds` and `load_sensitive` lists (your ratchet, DEC-757; entries count only with `Role: owner`) retire. The landing records every red that is red at the base itself (Q-CLOSE), so a list that excuses base reds is a second way to say the same. | yes / no | **yes.** Nothing is lost: the base red is in each close record with its test id, failure type and base commit. |
| **L2-3** | Before a lead returns a ticket, must it run the landing's selected tests itself (`gov queue --dry-run`, which replaces `gov close --verify` and `lead_verify.sh`)? | (a) no: the lead runs `gov accept` only, the landing finds the red (estimated 3 to 5 min, audit 1 §4); (b) yes, as today, a second run of the same selection | **(a).** (b) pays the same run twice: audit 1 measured `lead_verify` at 22.5 min median and judged that the landing catches the same red one step later. `--dry-run` stays as a flag whichever you choose. |
| **L2-4** | Gov OS's own landing moves onto `gov queue`, after one green proving landing through it. The scratch tools `land.py`, `merge_queue.py`, `select_tests.py`, `landing_select.sh`, `lead_verify.sh`, `close_build.py`, `landing_check.py`, `structural_pass.py`, `verdict.py` then retire (about 3,650 lines, all outside git). `kernel_gate.py` stays as the CTO's own list, run by a wrapper of about 20 lines before `gov queue`. | yes / no / keep `merge_queue.py` as well for now | **yes**, with `merge_queue.py` retired only after that proving landing. It needs the green base of Q-CAP44 first (branch `e2/cap44m`). |
| **L2-5** | The name of the one action. | keep `gov queue` / rename `gov land` | **keep `gov queue`.** The name is in the ticket, 9 test files, the facts file and `dispatch`'s `landing_command`; a rename buys only a nicer word. |
| **L2-6** | Direct commits (chores, EMERGENCY-2 4.6) have no ticket and so no landing. `landing_select.sh` is the only check on them today and had the best catch rate of any gate (13 of 17 runs RED, audit 1). | (a) `gov queue --direct`: the same selected run, after the fact, a notice in the digest; (b) a chore also goes through the queue before it lands; (c) no check | **(a).** It keeps "catch and correct, do not prevent" (EMERGENCY-2 §2) and costs seconds for a docs-only chore. |

Already decided, no answer needed: `gov context` retires (M1 (c), lead on `e2/m1-context`); `gov session-watch` folds into the run-time tool (A-2; audit 3 rows 13, 15, 16, D7).
Answer form: "L2-1 yes, L2-2 yes, L2-3 a, L2-4 yes, L2-5 keep, L2-6 a". Everything under §3 that is not on this page I decide as L2 (the merge itself, no owner yes needed).

---

## 1. The table

**How to read it.** "Mentions" are `grep` counts at `0123c8b5f`: kernel text = files under `template/governance/kernel/{roles,skills,templates,hooks}`; scratch = the CTO's git-ignored tools (executables and notes, no logs); tests = files under `tests/` that name the command. A mention is not a call. The one measured use is `gov close`'s: `git log -- docs/close` (18 closes, last 2026-10-29) against `governance/project/orchestration/closes/` (122, written by `land.py`). Verdicts: **stays**; **stays, changed** (what changes is named, and belongs to a §3 item); **merges into X**; **retires** (and where the job goes).

### Table 1: the 37 `gov` commands

| # | Command | What it does today | Who uses it | Verdict | Reason (owner's terms) | Replaced by | Takes with it |
|---|---|---|---|---|---|---|---|
| 1 | `status` | One read of tickets, gates, readiness, share, pause state | CTO, NL routing (CAP-28); kernel text 2, scratch 17, tests 165 | **stays** | practical: the one view; no copy | — | — |
| 2 | `check` | Declared check families; `--list`; `--structural` (one bounded notice pass) | `gov ci` hooks, leads' steps; kernel text 2, scratch 35, tests 171 | **stays, changed** | quality; `--structural` becomes the landing's after-step | `structural_pass.py` (scratch, 275 lines) folds into it | — |
| 3 | `readiness` | READY of a spec or a ticket's spec | MR-1, `gov discover`; kernel text 1, tests 24 | **stays** | records; READY exists three times (audit 1 §2), a G5 matter, not the landing's | — | — |
| 4 | `doctor` | Health of the install and the project | owner, CAP-25/43/45; tests 64 | **stays** | quality | — | — |
| 5 | `rebuild` | Rebuild derived state; `--seed`, `--integration`, `--when-due` | the landing's clone prepare; kernel text 1, scratch 66, tests 139 | **stays, changed** | fast; `--integration` is the landing's after-step (A8) | `merge_queue.py`'s store promotion | — |
| 6 | `context` | Context packet for a ticket (`--dry-run`, `--in-force`) | kernel text 5 (7 lines), scratch 55; 143 of 373 lead calls were refused (P5) | **retires** (M1, decided) | cheap, quality: no ceiling anywhere | `gov brief` carries memory; the close record carries `decisions`; `--in-force` moves to `gov decisions` | `src/gov/context/` (457 lines), 7 test files, the check family (lead `e2/m1-context`) |
| 7 | `closure` | Closure of ids over the record and code graphs | library of `retrieve` and `impact`; tests 25 | **stays** | cheap to keep: 24 lines over a library two other commands use; CAP-29 is G5's | — | candidate only if G5 drops CAP-29 |
| 8 | `retrieve` | Memory search | everyone; kernel text 18, scratch 39, tests 124 | **stays** | quality: memory first (§5) | — | — |
| 9 | `checkpoint` | Write, watch, resume a checkpoint | hooks (RT-5), sessions; kernel text 3 | **stays, changed** | records, no duplicate: the landing stops writing its own "ticket closed" checkpoint (`close/command.py:1492`); the close record says it | — | — |
| 10 | **`close`** | Strict close, scoped close, `--select`, `--verify`, `--full`; opens repair tickets in strict mode | nobody on the landing path: `land.py` writes its own close; `gov queue` calls only its internals (`_record_and_close`) | **merges into `queue`** (L2-1) | records kept, nothing duplicated: two close records, two closes. Fast, cheap: the strict path is about 1,300 of 2,129 lines | `gov queue` (§2) | strict gates and tests (Table 3) |
| 11 | `adopt` | Adoption stages A0 to A10, MA, AS | owner, adopters; tests 68 | **stays, changed** | practical: writes `queue.yaml`, writes no `close.yaml` and no context entry | — | — |
| 12 | `pause` | Freeze, cancel agents, rollback | owner; tests 34 | **stays, changed** | quality: the launcher honours the freeze (`launcher.py:282`), the queue does not (audit 7 C-1; CAP-05) | the queue reads the freeze (A5) | — |
| 13 | `accept` | Runs a ticket's acceptance folder, pass or fail per KPI line | engineers (29 kernel lines), landing; tests 80 | **stays, changed** | quality: the landing calls its runner and records the per-line result (A3) | — | — |
| 14 | `adapters` | Generate adapters from `.rulesync/` | adopters; tests 12 | **stays** | practical | — | — |
| 15 | `backup` | Verified git bundle outside the tree | cron; tests 5 | **stays** | records (§2.8) | — | — |
| 16 | `brief` | Filled brief from ticket and facts, refused if not READY | CTO, leads; tests 39 | **stays, changed** | CTO's text: `--run land` says `gov queue`; `--run review` is the K1/§3.6 matter | — | — |
| 17 | `ci` | Hook and CI gates by tier; `staged-secrets`; evidence record | lefthook; tests 13 | **stays** | cheap: nothing here duplicates the landing (G1/G2 per commit). `staged-secrets` is a no-op under `scan: off` and its code is the one the pre-public scan needs | — | — |
| 18 | `decisions` | Basis check on new rules, weekly | A-8; tests 7 | **stays, changed** | gains `--in-force` (M1) | — | — |
| 19 | `discover` | Idea to spec check, gap tickets, feature ticket | W2-36; tests 11 | **stays** | practical | — | — |
| 20 | `dispatch` | Tick, status, watch, limits | the run-time tool (slice 2 tonight) | **stays, changed** | cheap: its landing step guards against a separate `gov close` | §3 item B4 | ~70 lines of `dispatch/landing.py` |
| 21 | `impact` | Impact over the graphs | CAP-33, test selection; tests 18 | **stays** | quality | — | — |
| 22 | `install` | Pinned, hash-checked install | `update`; tests 11 | **stays** | records | — | — |
| 23 | `launch` | Start a worker with model and effort from the rubric | leads, dispatch; kernel text 9, tests 130 | **stays** | practical (K1 lead's) | — | — |
| 24 | `links` | Link integrity, a notice | leads, `check --structural`; tests 44 | **stays** | records | — | — |
| 25 | `memaudit` | Transcript scan for a hidden set | §2.7; tests 5 | **stays** | quality | — | — |
| 26 | `memory-use` | Memory-use log per day and role | §5.6; tests 3 | **stays** | records | — | — |
| 27 | `msg` | Send, read, wait, watch messages | run-time tool (D6, D7); tests 7 | **stays** | practical: replaces the watcher layers | — | — |
| 28 | `plan` | Dependency map, ready batches | `dispatch`; tests 35 | **stays** | fast | — | — |
| 29 | **`queue`** | Checks, merge, scoped run, close commit, move (W2-115b, built) | landing; `tests/unit/queue` 3 files, W2-115b acceptance 10 files | **stays, changed: it becomes the landing-and-close** | all six terms; §2 | — | — |
| 30 | `release` | Build a release (owner, plain terminal) | owner; tests 17 | **stays** | the owner's | — | — |
| 31 | `resources` | Resource gate, slots, trip-wire | every heavy run; tests 20 | **stays** | cheap: the machine rule | — | — |
| 32 | `session-watch` | Stop-hook checks; helper watch | unregistered since the switch-off | **retires** (A-2, decided) | cheap: four watcher layers | `gov msg` wait plus the Stop check; the tick (audit 3 D4, D7) | `src/gov/session_watch/` (about 1,040 lines), 5 test files (run-time lead) |
| 33 | `skilleval` | Run a skill's three scenarios | skills; kernel text 7, tests 14 | **stays** | quality | — | — |
| 34 | `spend` | Runaway brake | A-1, until the run-time tool replaces it; tests 11 | **stays** | cheap | — | — |
| 35 | `telemetry` | Governance share of a ticket (reads logs) | the weekly measure (A-7); tests 13 | **stays** | records; not on the landing's path (fast): the close record carries no share | — | — |
| 36 | `update` | Update an adopted project, three-way merge | adopters; tests 15 | **stays** | records | — | — |
| 37 | `wait` | Bounded wait on a job's exit file | leads, dispatch; tests 11 | **stays** | practical: `--dry-run` writes its `.exit` file for it | — | — |

**Count: 37 before, 34 after** (−`close`, −`context`, −`session-watch`). Only `close` is this page's ask.

### Table 2: subcommands and modes that are separate actions

| Command and mode | Today | Verdict | Becomes |
|---|---|---|---|
| `close` strict (no `close.yaml`; the adopter default) | every gate; repair ticket; iteration count; escalation | **retires** (L2-1) | the landing's checks (§2). Contract CAP-31.b and CAP-59.a are already "changed" by audit 7 |
| `close` scoped (`close: scoped`) | scoped run in the warm clone, base run, `accepted_reds`, close record | **merges into `queue`** | the queue's run; the base run's job is Q-CLOSE (A1) |
| `close --select` | prints the selection | **merges** | `queue --select` |
| `close --verify` | the selection, parallel and serial phases, `verify.exit` | **merges** (L2-3) | `queue --dry-run` (same `--out`, same exit-file form) |
| `close --full` | refused in scoped mode (DEC-968) | **retires** | `queue --full`: the nightly's own run on the tested merge (no second full-run code) |
| `python3 -m gov.close.batch run`, `run_scoped`, `refresh`, `reuse` | W2-68 batched strict close; batched scoped close | **retire** (L2-1) | `queue` with several tickets |
| `python3 -m gov.close.batch` `isolate` | the culprit search the queue calls | **stays** as a function | — |
| `python3 -m gov.close.nightly` | the full regression and its attribution | **stays** (A-1; NIGHT (c): off tonight, back when green) | — |
| `python3 -m gov.close.traceability` | closed tickets' trailers resolve (CAP-38.b) | **stays** | — |
| `queue --onto`, `--timeout` | as built | **stays** | — |
| `queue --dry-run`, `--select`, `--full`, `--direct` | not built | **new flags** | A6, A7 |
| `ci checks / job / push / record` | tiers G1 to G3, the evidence note | **stays** | — |
| `ci staged-secrets` | gitleaks on what is staged | **stays**, idle under `scan: off` | — |
| `dispatch tick / status / watch / limits` | run-time tool | **stays** | — |
| `msg send / read / wait / watch` | inboxes | **stays** | — |
| `session-watch stop-check / helper-watch` | watcher layers | **retires** (A-2) | `msg wait`, the tick |
| `spend check / clear / sum` | the brake | **stays** (A-1) | — |
| `resources --check / --slot / --register / --sample / --remeasure / --init-config / --trip-wire / --backstop` | the machine gate | **stays** | — |
| `checkpoint` write / `--watch` / `--resume` | checkpoints | **stays** | — |
| `pause` / `--off` / `--cancel-agents` / `--rollback` | freeze | **stays, changed** (A5) | — |
| `adopt --stage A0 … A10, MA, AS`; `--verify-list`, `--verify-apply`, `--facts` | adoption | **stay** | `--facts` also writes `queue.yaml` (A5) |
| `check --list`, `--structural` | declared checks; notice pass | **stay** | — |
| `rebuild` full / `--seed` / `--integration` / `--when-due` | stores | **stay** | — |
| `brief --run tests / build / review / resume / land` | lead runs | **stay** (text is the CTO's, 3.5) | `review` is K1's; `land` names `gov queue` |
| `discover` idea / `--check` / `--generate` / `--ticket` | W2-36 | **stay** | — |
| `adapters generate`, `decisions basis`, `memaudit scan`, `update --check`, `plan --open / --tickets / --ready` | one action each | **stay** | — |

**Count, the close family:** 5 `close` modes become 0 (three live on as `queue` flags: `--select`, `--dry-run`, `--full`); 4 `batch` modes (`run`, `run_scoped`, `refresh`, `reuse`) become 0, with `isolate` kept as a function; `nightly` and `traceability` stay. Module commands of the family: 3 (`batch`, `nightly`, `traceability`) become 2. `queue` gains 4 flags (`--dry-run`, `--select`, `--full`, `--direct`).

### Table 3: what the retirements take (line counts are estimates from `wc -l` and the line ranges named)

| Part | Today | Retires | Stays | Source |
|---|---|---|---|---|
| `src/gov/close/command.py` | 2,129 lines | about 1,300: the strict `run` and its gates (lines 132 to 1,497, less `_record_and_close`, `_work_of`) | `_record_and_close`, `_write_close_record`, `_phases`, `_base_run`, `review_verdict` (kept as a library for reviews that happen; the landing never calls it) | `command.py:132-310, 455-498, 1498-1560, 1702-1779, 1860-1942` |
| `close/history.py`, `ratchet.py`, `state.py` | 203, 136, 272 | all three (trailer history, the owner's ratchet lists, iteration counter and escalation) | — | L2-1, L2-2 |
| `close/gates.py` | 328 | about 220 | `ticket_class`, `acceptance_folder`, `has_tests`, `check_evidence`, `check_specification` | `gates.py:1-25` |
| `close/batch.py` | 815 | about 620 (`run`, `run_scoped`, `reuse`, `refresh`, `check_red_run`, the CLI) | `isolate`, `_build`, `_candidate`, `_entangled`, `_targets` | `batch.py:408-723` |
| `close/tool.py`, `select.py` | 192, 854 | about 60 (repair ticket), about 60 (`ticket_change`, `head_without_change`: trailer-based, the queue passes `change=` itself) | `tk close`, `scoped` | `select.py:588-611` |
| **`src/gov/close/` total** | about 6,400 | **about 2,800** | about 3,600 | |
| Scratch landing tools (git-ignored) | `land.py` 387, `merge_queue.py` 1,374, `select_tests.py` 384, `landing_select.sh` 269, `lead_verify.sh` 107, `close_build.py` 601, `landing_check.py` 213, `structural_pass.py` 275, `verdict.py` 45 | **about 3,650** | `kernel_gate.py` 161 | audit 1 §1 |
| Unit tests | `tests/unit/close` 46 files, 7,343 lines | 16 files, 2,678 lines: `test_collection_gate`, `test_decision_records`, `test_every_finding`, `test_follow_up`, `test_governance_checks`, `test_history`, `test_measured`, `test_parallel_runs`, `test_ratchet`, `test_refuse`, `test_repair_ticket`, `test_run_and_record`, `test_state`, `test_w2_07_decision_records`, `test_batch_refresh`, `test_batch_reuse` | the rest, plus 3 queue files | file names; the test designer confirms each |
| Acceptance folders | W2-07 1,515, W2-66 3,053, W2-68 942 lines | **about 5,500** (retire where every test asserts a retired behaviour) | W2-115, W2-193, W2-194 rewritten where they assert the review gate, repair tickets or the lists | the independent test designer writes the retirements, with `Role:` |
| Docs and kernel text | Contract lines 114, 116, 388, 489, 597, 614, 707, 911 name `gov close`; `orchestration` skill line 26; `close.schema.json`, `probe.schema.json`, `path-map.schema.json` (`close_timeout`, `close_workers`); `facts.yaml` `dod` and `steps` | the CTO changes the kernel text (3.5); the G5 lead takes the Contract lines | — | 131 files under `docs/` and 82 under `governance/` mention `gov close`: history, they stay |

---

## 2. The landing-and-close: one action

`gov queue <ticket>[=<branch>] ...` is built today and does most of it. What follows is the action after the change; §3 lists what changes.

### Steps, from the request to the closed ticket

| # | Step | What it does | Fails as |
|---|---|---|---|
| 0 | **Hold** | Refuses while `gov pause` froze the project. Reads settings: integration branch (`--onto`, else `queue.yaml`, else the branch checked out at the root), work branch (`=<branch>`, else the form in `queue.yaml`) | `PROJECT_PAUSED`, `INTEGRATION_UNKNOWN`, `BRANCH_UNKNOWN`: exit 1, nothing written |
| 1 | **Read** | Each ticket is read at the integration head, the base. Its branch tip is read. A tip already on the base goes to step 3 without a merge | `TICKET_UNKNOWN`, `TICKET_CLOSED`: exit 1 |
| 2 | **Checks, before any run** (seconds) | G-1: every commit that changes the acceptance folder carries the test designer's or the owner's role. The ticket's acceptance folder holds a test (a class judged on a record, research, audit, specification, is judged on that record instead). Paths outside `allowed_paths` are a notice. The change is `base...tip`: no trailer is read to find it | `TEST_AUTHOR_REFUSED`, `NO_ACCEPTANCE_TESTS`: that ticket is out of the batch, the others go on |
| 3 | **Merge** | The candidates are merged onto the base in the warm clone: one tested merge | `CANDIDATE_NOT_ISOLATED`: exit 3, nothing lands |
| 4 | **Acceptance** | Each ticket's folder runs through the runner `gov accept` uses, on the tested merge; each KPI line's pass or fail goes into the record. The selection's pytest call leaves those folders out, so no test runs twice | a red here is that ticket's: it is the culprit |
| 5 | **The run** | The union of each ticket's `select.scoped` selection runs once. A red runs again alone; green alone is flaky (named, not blocking). A red alone is tried with each candidate left out, then at the base (Q-CLOSE below). The culprit is out, the rest run again | `RED_CAUSED` for the culprit; `SELECTION_REFUSED` for an unmapped path (the landing never widens by itself: `--full` is the asked-for widening) |
| 6 | **Close** | For each landed ticket, one close commit on the tested merge holds the close record and `tk close`'s change to the ticket file. A ticket not landed is not closed, and nothing of it is left | `CLOSE_RECORD_FAILED`: the record and the ticket are taken back |
| 7 | **Move** | The integration branch moves from the base to the last close commit, only if it is still at the base; where it is checked out, its tree follows | `HEAD_MOVED`, `LAND_BLOCKED`: exit 3, nothing lands |
| 8 | **After** (never refuses) | `gov rebuild --integration <branch>` where `rebuild.yaml` names one (CAP-17.b: the store is fresh at the new head); `gov check --structural <base>`. Both results go into `queue.json`; the digest reads them | a notice only |

Exit codes stay as built: 0 all landed and closed; 3 some did not land; 1 refused as a whole.
Time (audit 1's estimate, to be measured on the proving run): about 3 to 5 min a land, against 21 min median today.

### The close record

One writer: the landing. One place: `docs/close/<ticket>/CL-<ticket>.md`, committed in the close commit (the schema requires only `task`; the rest is free). The old strict record's `packet_hash`, `inputs`, `tests_produced`, `deviations: not measured` and `governance_share: not measured` go; they recorded what the strict close could not measure.

| Field | Content | Why kept |
|---|---|---|
| `close: landing` | replaces `strict`, `scoped`, `queue` | one form |
| `landed` | `onto`, `base` (the integration head before), `tested` (the merge that ran), `branch` name and tip, the batch's other tickets | the commit that was tested is the commit that landed |
| `acceptance` | the folder; each KPI line, pass or fail | DOD-1, read from code (EMERGENCY-2 §4.3 step 2) |
| `authors` | the commits that changed the folder, each with its role | G-1 evidence |
| `selection`, `runs` | suites, pytest options, changed paths; each run's passed, failed, errors, skipped, seconds | what was run |
| `reds` | each: test id, failure type, `verdict` (`caused`, `base`, `flaky`), for `base` the base commit it was red at | Q-CLOSE |
| `base_reds` | the `base` entries of `reds`, listed once more by id | the known base reds, found by one grep |
| `culprits` | candidates that did not land, with the reds they explain | red attribution |
| `path_notices` | each commit and path outside `allowed_paths` | audit 7 C-6 |
| `decisions` | the decisions that govern the change, from the ticket's `sources`, `decisions` and KPI citations (M1: no ceiling) | replaces `gov context` |
| `skill_versions` | the skill ids and versions in the tree (Contract CAP-24's acceptance line) | the one strict-record field a Contract line names |
| `seconds` | merge, selection, acceptance, run, close, total | the landing-time measure (§10.2) |
| `queue` | path of `queue.json` | the runtime log (git-ignored) holds detail; the close record is the committed record |

No repair ticket file, no register entry, no inbox item is written for a red; the audit-9 rule "no register entry for what the landing records" holds.

### Base reds (Q-CLOSE)

Today `isolate` refuses the whole batch with `BATCH_UNEXPLAINED` when a red stays red with every candidate left out (`batch.py:610-613`). That is the refusal EXAMIN met on a base red (F-028, F-030, F-031). The change: such a red runs once at the base. Red there with the same failure type (the existing `NEVER_MATCH` rule: a timeout, an unknown type or an absent test never matches) → a **known base red**: recorded in every landed ticket's close record, not blocking, no ticket. Green at the base and still unexplained by any one candidate (an interaction of two) → refused as today. Because the change is `base...tip` and no trailer is read, a first commit without a `Task:` trailer is inside the change (a red it causes is the culprit's) or inside the base (a red it left behind is a base red). The case the owner's Q-CLOSE named, "a red from an untrailered first commit excused by the close's base", cannot arise: nothing excuses by trailer.

### What `gov queue` and `gov close` become, and what an adopter runs

- **`gov queue`** is the landing and the close. New flags: `--dry-run` (steps 0 to 5, nothing moved or committed; `--out` and the `.exit` file as `close --verify` wrote them, so `gov wait` still works), `--select` (prints the selection, exit 0, or the refusal), `--full` (step 5 widened to the nightly's own run on the tested merge), `--direct [<since>]` (§3 A7).
- **`gov close`** answers `COMMAND_RETIRED: use gov queue` for one release, then is unknown. The package `gov.close` keeps `select`, `attribution`, `isolate`, the record writer and the nightly.
- **An adopter** runs: `gov adopt` (writes `queue.yaml`: `integration: main`, `work_branch: "{ticket}"`); the engineer, `gov accept <T>`; whoever lands, `gov queue <T> [<T> ...]`; a daily cron, `gov queue --direct`. Nothing else for the close. Kernel text, facts and role files say so (the CTO's change, 3.5).

---

## 3. The code changes, ticket-sized

Each is a feature or a fix in W2-115b's record (4.2: a fix is recorded in its owning ticket, a new KPI line on a closed feature is a new ticket, 4.6). **A items need no owner yes** (the merge itself, decided by L2). **B items need the owner's yes** (the table's retirements). Sizes are estimates by analogy with the code named. Every KPI line has its verify. Tests: the independent test designer first, red on the base; **C3 (the close and the landing): the designer and the engineer run Opus** (NIGHT-COMMON, audit 4 Table 3).

### A: the landing becomes the close

**A1 · Base reds are recorded, not refused (Q-CLOSE).** `src/gov/close/batch.py` `isolate`, `src/gov/queue/command.py`. About 70 lines.

| Line | Verify |
|---|---|
| S1: a batch whose merged run has a red that is red at the base, same failure type, lands; each landed ticket's close record lists it in `reds` (`verdict: base`) and `base_reds` with the base commit | acceptance: a fixture repository with one base-red test and one clean candidate: `gov queue` exits 0; the record holds the entry |
| S2: the same when the commit that made the test red has no `Task:` trailer | the same fixture, the cause committed without a trailer |
| S3: a red green at the base that no single candidate explains is refused (`BATCH_UNEXPLAINED`), nothing lands | a fixture of two candidates that fail only together |
| F1: a red the candidate causes is never recorded as a base red; the candidate does not land | a fixture whose candidate breaks a green test: exit 3, the candidate in `culprits` |
| F2: no file is created under `.tickets/`, no line under `docs/` outside `docs/close/` and `docs/checkpoints/` for a base red | `git status --porcelain` of the clone after S1 |

**A2 · One close record, one writer.** `queue/command.py` `_close_all`, `close/command.py` `_record_and_close`. About 120 lines.

| Line | Verify |
|---|---|
| S1: the close commit of a landed ticket holds `docs/close/<T>/CL-<T>.md` with every field of the table in §2 and `.tickets/<T>.md` at `status: closed`; the integration branch's head is the last close commit | acceptance: read the record's front matter and `git show --stat` of the close commit |
| S2: no "ticket closed" checkpoint is written (`docs/checkpoints/<T>/` gains nothing at a land) | `git show --stat`; and `grep` shows no check or hook reads a close-time checkpoint (the verify names what it grepped) |
| S3: a ticket that did not land has no close record and is not closed | fixture with one culprit: no `CL-` file, `status` unchanged |
| F1: a failed write of the record leaves neither record nor `tk close`'s change | existing take-back case, kept |

**A3 · Acceptance at the landing.** `queue/command.py`, `accept/runner.py` (called, not changed). About 100 lines.

| Line | Verify |
|---|---|
| S1: a feature ticket whose acceptance folder holds no test is refused with `NO_ACCEPTANCE_TESTS`; the scoped close has this refusal and the queue lacks it today | fixture: empty folder, exit 3 |
| S2: a research, audit, specification or coordination ticket is judged on its record (`check_evidence`, `check_specification`) and lands without a test folder | fixture per class |
| S3: each KPI line's pass or fail from the runner is in the record's `acceptance` | record read against `gov accept`'s own answer on the same tree |
| F1: no test of the acceptance folder runs twice in one landing | the junit names of the two runs are disjoint |

**A4 · A branch already merged.** `queue/command.py` `_candidate`. About 80 lines. Replaces `gov close <T>` for hand-merged work (today `CANDIDATE_NOT_ISOLATED: already merged`).

| Line | Verify |
|---|---|
| S1: `gov queue <T>` for an open ticket whose tip is on the integration branch merges nothing, runs steps 2 to 5 on the head, writes the close commit and moves the branch | fixture: merge by hand, then `gov queue <T>`: exit 0, record and ticket closed |
| F1: a closed ticket is still `TICKET_CLOSED` | existing case |

**A5 · Settings and the pause.** `queue/command.py`, `adopt` (facts entry). About 60 lines.

| Line | Verify |
|---|---|
| S1: while `gov pause` froze the project, `gov queue` lands nothing and says why (`PROJECT_PAUSED`); `gov pause --off` restores it (CAP-05, audit 7 C-1) | acceptance: pause, queue, exit 1, branch unmoved; off, queue, lands |
| S2: `gov adopt --facts` writes `governance/project/queue.yaml` (`integration`, `work_branch`) and no `close.yaml` | an adopted fixture |
| F1: a project with neither file and the root on `main` lands onto `main` | existing `INTEGRATION_UNKNOWN` cases, adjusted |

**A6 · `--dry-run`, `--select`, `--full`.** `queue/command.py`; the logic of `close._verify_command`, `_select_command` moves. About 120 lines.

| Line | Verify |
|---|---|
| S1: `--dry-run` runs steps 0 to 5, moves no branch, commits nothing, writes `select.json`, the run files, `summary.txt` and last `verify.exit` under `--out` (default `.gov-runtime/queue/dry/<T>/`) | `git rev-parse` before and after; `gov wait` on the exit file returns |
| S2: `--select` prints the selection as one JSON object, exit 0; a refusal goes to stderr, exit 2 | as `close --select` today |
| S3: `--full` runs the nightly's function on the tested merge and lands only on green | the nightly's own test fixture |
| F1: `--dry-run` and `--select` leave `git status --porcelain` empty at the root | fixture |

**A7 · Direct commits are checked after the fact (L2-6 (a)).** `queue/command.py`. About 100 lines. Replaces `landing_select.sh`.

| Line | Verify |
|---|---|
| S1: `gov queue --direct [<since>]` runs the scoped selection over the commits on the integration branch since `<since>` (default: the last mark under `.gov-runtime/queue/`) that no landing made, and writes one line per red to `queue.json` for the digest | fixture: a chore that breaks a test lands directly; `--direct` names it |
| S2: a docs-only chore selects only record reading and ends in seconds | timing in `queue.json` |
| F1: `--direct` never moves a branch, opens a ticket or refuses | `git rev-parse`, `.tickets/` unchanged |

**A8 · The after-step.** `queue/command.py`. About 50 lines.

| Line | Verify |
|---|---|
| S1: after a move, `gov rebuild --integration <branch>` runs where `rebuild.yaml` names a store, and `gov retrieve` then reports no stale count at the new head | fixture with a store: `retrieve`'s store line after the land |
| S2: `gov check --structural <base>` runs, bounded; its lines are in `queue.json` | read the file |
| F1: a failure of either is a notice; the exit code and the landed branch are unchanged | fixture with a failing rebuild |

A items: about 620 lines, 8 tickets' worth of KPI lines. Order: A1 first (it unblocks Gov OS's own base reds), then A2, A3, A4; A5 to A8 in any order.

### B: the retirements (the owner's yes)

**B1 · `gov close` merges into `gov queue` (L2-1, L2-2).** About −2,800 lines in `src/gov/close/`; +30 for `COMMAND_RETIRED` (`cli/main.py`). After A1 to A4 are green.

| Line | Verify |
|---|---|
| S1: `gov --help` lists no `close`; `gov close <T>` exits 1 with `COMMAND_RETIRED` naming `gov queue` | `gov --help`; one run |
| S2: no source file under `src/gov` imports a retired function (`history`, `ratchet`, `state`, the strict `run`, `batch.run`, `batch.run_scoped`) | `python3 -m compileall` plus a grep the verify prints |
| S3: the 16 unit files and the acceptance folders of Table 3 are retired, each with a line naming DEC-1214 L2, by the independent test designer (`Role: independent-test-designer`) | `gov queue` G-1 passes on the branch; `tests/unit/close`, `tests/unit/queue`, `tests/acceptance/W2-115`, `W2-115b`, `W2-193`, `W2-194` green through the slot |
| F1: `gov queue`, `gov accept`, `gov rebuild`, `gov check` behave as before on a repository that had `close.yaml` | `tests/unit/optin`, the queue's acceptance folder |

**B2 · Gov OS's own landing moves onto `gov queue` (L2-4).** No product lines; a wrapper of about 20 lines; the dispatcher's `landing_command` set to it.

| Line | Verify |
|---|---|
| S1: one ticket lands through the wrapper (`kernel_gate.py`, then `gov queue`), its close record in `docs/close/` | the proving landing's `queue.json` and record |
| S2: after S1, `merge_queue.py` and the other tools of L2-4 are removed from the CTO's tools folder and from `dispatch`'s settings | `ls` of the folder; a dispatcher tick starts and lands nothing wrongly |
| F1: a kernel file not on the approved list stops the wrapper before `gov queue` runs | `kernel_gate.py`'s own fixture |

**B3 · The dispatcher's landing step loses its close guard.** `src/gov/dispatch/landing.py` (the run-time lead's file: after slice 2 lands). About −70 lines: `conflicting_close`, `close_arguments`, `commit_records` (no caller in `src`), `job_markers["close"]`, `close_record_paths`.

| Line | Verify |
|---|---|
| S1: a landing is held only for the reasons that remain: the nightly, an unfinished landing, a locked index, tracked changes at the root, the wrong branch | `tests/unit/dispatch` landing cases, rewritten |
| F1: no config key names a close | `grep` of `dispatch/config.py` |

**B4 · Kernel text and records follow (the CTO's change, 3.5; the G5 lead for the Contract).** Facts `dod` lines, the `orchestration` skill (line 26), `brief --run land`, `close.schema.json`'s description, `path-map.schema.json`'s `close_timeout` and `close_workers` (renamed or dropped), `probe.schema.json`'s description; Contract lines 114, 116, 388, 489, 597, 614, 707, 911.

| Line | Verify |
|---|---|
| S1: no kernel or instruction file tells an agent to run `gov close` or `gov context` | `grep -rn "gov close\|gov context" template governance/project/facts.yaml .claude CLAUDE.md AGENTS.md` returns none |
| S2: DONE (L2, confirmed) is the three lines of `facts.yaml`'s `dod`: acceptance green, the landing's checks green, the close written at the land | read the file |

### What this page does not decide

- `review_verdict` (83 lines) stays as a library; K1 and the audit's "a review only for a red" decide who calls it.
- READY exists three times (audit 1 §2); merging the copies is not a landing question.
- `gov closure` and `gov ci staged-secrets` stay; each is a candidate only if G5 drops its Contract line.
- `scratch/tools/close_queue.sh` (calls `gov close`; its last close commit is 2026-10-29) is not in audit 1's list; B2 removes it with the rest if the CTO finds no caller.

### Limits of this page

The "who uses it" counts are `grep` mentions, not runtime calls; the only measured use is the `gov close` figure above. Line counts are `wc -l` and my reading of the line ranges, not a measure of what deletes cleanly: each retirement's real size is the engineer's to confirm against the test designer's list. I ran no test and no `gov rebuild`. `gov queue` is built and has its own acceptance folder (W2-115b), but I did not run it; the 3 to 5 minute figure is audit 1's estimate.
