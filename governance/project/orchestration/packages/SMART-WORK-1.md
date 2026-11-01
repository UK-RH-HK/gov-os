# SMART-WORK-1: the smart way of working, made part of the Gov OS (P1, the owner's request of 2026-10-31 ~22:30)

For the owner. The practices this repository has established replace bulk work with smart work. Most of them live today in the CTO's own tools (`.gov-runtime/scratch/orchestrator/tools/`) and in the orchestrator's prompt and briefs, not in the product. This package maps each of the 22 to the product as it stands, to the tickets that will give it, or to no ticket, and proposes the changes. It answers DEC-982 item 2 (the KPI lines below cite it); the owner's decisions on it will be DEC-983. Nothing here is filed or edited yet.

## Headline

Of the 22 practices:
- **2 the product already has:** the secrets cache (1; its nightly full scan is missing from the product's nightly) and checks done once per process (10, W2-108).
- **4 a ticket gives, and its KPIs say so:** the merge queue (7, W2-97, but only as this repository's tool), the shared reranker (11, W2-112), the parallel work order and QA per stream (12: W2-33, W2-96, W2-60b, W2-83b), and the test-data rule (22, W2-98).
- **8 a ticket should give, but its KPIs do not say so, or say the opposite:** the full suite only in the nightly (3), heavy-job slots (8), timing tests timing their own work (9), fresh sessions and the anti-drift kit (15), brief gaps (18), scope control (19), resource safety's trip-wire (20), one writer per worktree (21).
- **8 have no ticket:** scoped tests at every level (2), a close refused only by its own change (4), no accepted-reds lists (5), culprit batches (6), the designers' store (13), the audit's 10 practices in `gov close` (14), interim results (16), the guard's false-refusal tracking (17).

**The surprise:** the product's `gov close` contradicts five of the practices today. It widens to the full suite on a shared-core change. It refuses on any red that an owner-accepted list (`accepted_reds`) does not cover. It quarantines timing tests on a list (`load_sensitive`). Its batch closes nothing on a red run. EXAMIN's copy (W2-27) and the proving ground (W2-81) prove a clean `gov close` at exit 0, so as things stand they would prove the old close, not the smart one. And four tickets' KPIs say the opposite of a decision in force: W2-20 (a reserved verification peak and "no fixed number", against DEC-961 and DEC-979 D1), W2-97 and W2-38 (the full suite on core changes or at milestones, against DEC-968), and W2-12 (the owner's acceptance of `accepted_reds` entries, against DEC-968's no-list rule).

**Proposed:** five new tickets (W2-115 to W2-119), three before EXAMIN's copy and two after it; KPI changes to ten existing tickets; and a short list of what stays this repository's own.

## The map

| # | Practice | The product today | Ticket | Its KPIs say so? | Proposal |
|---|---|---|---|---|---|
| 1 | Secrets scan of new or changed content, full scan nightly, cache cleared on change | **Has it:** `src/gov/secrets/cache.py` (W2-107, closed): content hash, engine fingerprint, `GOV_SECRETS_FULL_SCAN` | W2-107 | yes, for the cache; the product's nightly (`gov.close.nightly`) rebuilds nothing, so nothing sets the full scan | W2-115: the product's nightly rebuilds with the full scan |
| 2 | Scoped tests at every level; records and governance files never widen a run | Partly: `src/gov/close/select.py` (W2-66) selects for the close; the record places (`record_only`) select nothing; but the template's test map widens to full on `governance/kernel/**` and the maps, and on any unplaced path; leads and workers have no product command (they use the CTO's `select_tests.py`) | none (W2-78, parked, moved the lists only) | no | W2-115 |
| 3 | The full suite only once a day, in the nightly | **Contradicted:** `select.py` runs the full regression on `SHARED_CORE`, `UNPLACED`, an unknown base | W2-97, W2-38, and the old KPI "the full regression in the close's form is green" in W2-82 and W2-83a | **the opposite:** W2-97 "the full suite runs only for a change to the core"; W2-38 "The full suite runs at milestones and in CI" | KPI changes; W2-115 |
| 4 | A close refused only by failures its change caused, proven with and without | **Contradicted:** `gov close` judges reds by the ratchet (`src/gov/close/ratchet.py`); `batch.py` attributes by bisect but refuses on any red | none | no | W2-115 |
| 5 | Every failure the change did not cause is fixed at once or escalated, never left on a list | **Contradicted:** `accepted_reds` is exactly such a list | W2-12 strengthens the list | **the opposite** (W2-12 KPI 4: "the close counts a ratchet entry (accepted_reds, load_sensitive) … from a commit carrying … Decided-by: owner") | W2-115; W2-12 KPI change |
| 6 | Batch closes: the culprit taken out, the rest close on the same run | **Contradicted:** `batch.py` "Nothing closes on a red run (exit 3)" | W2-97 has it for the queue only ("a red batch is bisected by ticket, the good ones advance and the causing one is ejected") | for the queue, yes; for `gov close`, no ticket | W2-115 |
| 7 | Test before merge; skip a run when the merged code is identical | No | W2-97 (running): `governance/project/orchestration/tools/merge_queue.py`, **this repository's tool, not the product's** | yes ("skips the run when the merged code is identical to what the lead tested"), but not in the product | W2-97 KPI change (no full, a slot); W2-117 after EXAMIN |
| 8 | Heavy jobs take a slot; everything else runs freely | No (`src/gov/resources/` not built) | W2-20 (claimed) | **the opposite:** "the floor + one verification run's peak (reserved once)" and "No fixed number: no ceiling on leads or sessions, weighted or not" | W2-20 KPI change |
| 9 | Failures re-run alone to filter out load; timing tests time only their own work | Partly: the nightly and the batch re-run every red alone; `gov close` re-runs alone only what the `load_sensitive` list names, a quarantine | W2-111 (this repository's 11 cases only) | for this repository's cases, yes; the kernel's test-design skill says nothing | W2-115 (all reds alone); W2-11 KPI (the skill) |
| 10 | Checks once per run, not before every search | **Has it:** `src/gov/retrieval/semantic.py`, `lexical.py` (W2-108: freshness and status once per process) | W2-108 (closing) | yes | none |
| 11 | Shared services instead of a copy per session | Partly: one Ollama (`src/gov/retrieval/ollama.py`, started on demand, never stopped) and one CPU query embedder on its own port (DEC-798); the reranker is one per process (`rerank.py`); a sandboxed session runs a private embedder (DEC-261) | W2-112 (filed) | yes, for the reranker | none now; the sandbox's private embedder stays (DEC-261) until W2-56's sandbox can reach the shared one |
| 12 | Test designer and engineer in parallel, the engineer seeing pass or fail only; QA per stream, core tickets one by one | Partly: `gov accept` (W2-96, running) is the opaque runner; `qa-engineer` a known role (W2-60b) | W2-33, W2-96, W2-60b, W2-83b | yes (W2-33: "the test designer and the engineer work in parallel from it, never reading each other's work; the engineer runs the acceptance tests once ready (through gov accept)"; "tickets that touch the core … one by one before they merge, the others in batches of up to about five") | none |
| 13 | The designers' store: separate, double-buffered, refreshed twice a day | No (the CTO's `refresh_integration_store.sh`, `store_refresh_daily.sh`) | W2-33 and W2-83b name the rule ("retrieves only from the integration branch's store") but nothing builds the store | the rule, yes; the store, no ticket | W2-116 |
| 14 | The audit's 10 practices for a close, in `gov close` itself | **Contradicted in part:** `gov close` carries the lifted gates (ratchet lists, the pre-close gate, full widening); practice 9's close record and practice 2's scoped run on the merged commit are the CTO's `close_build.py`, not the product | W2-81 and W2-27 prove "a clean gov close at exit 0" | they prove a clean close, not which close | W2-115 |
| 15 | Fresh sessions and the anti-drift kit (morning handover, decisions in force at start, RESUME HERE) | Partly: the kernel's checkpoint skill and `sessionstart.py` deliver RESUME HERE in full; no digest of the decisions in force; the morning handover is this repository's practice | W2-55 (gov context leaves out superseded entries); W3-P04 (the morning package skill, parked) | partly: W2-55 leaves superseded entries out, but no digest is loaded at start; nothing on the fresh session | W2-55 and W2-11 KPI changes |
| 16 | Key results reported at once (interim results), not only at the final return | No: `subagentstop.py` checks the twelve fields at the end only (the CTO's `interim_watch.sh`, `lead_return_watch.sh`) | none | no | W2-118 after EXAMIN |
| 17 | The guard's false refusals tracked, with a threshold that triggers a fix | No: the guard writes containment findings (`.gov-runtime/findings.jsonl`) and observations (`records.jsonl`), not its PreToolUse refusals (the CTO's `guard_refusals.py` reads session transcripts) | none | no | W2-119 before EXAMIN |
| 18 | Brief gaps: every return lists what its brief lacked; the template fixed the same week | No: the kernel's `brief-lead.md` has no `brief_gaps:`; `subagentstop.py` does not check it | W2-11 (ROLES-SPEC-1 G14 gives it to "W2-11 r1"); W3-P02 (parked) | **no:** W2-11's KPIs do not mention brief gaps | W2-11 KPI change; the hook check in W2-118 |
| 19 | Scope control: every new ticket to the owner first; the WBS's growth reported | No: the planning and orchestration skills do not state DEC-974; `gov status` gives no growth (W3-P05, parked) | W2-11 (the orchestration skill); W3-P05 | no | W2-11 KPI change; the numbers stay W3-P05 |
| 20 | Resource safety: disk floor, memory floor, out-of-memory trip-wire | No (`src/gov/resources/` not built; the CTO's `disk_gate.sh`, `gate_check.py`, `oom_watch`) | W2-20 | partly: disk and inode floors and the memory floor, yes; the trip-wire, no | W2-20 KPI change |
| 21 | One writer per worktree; separate worktrees for parallel work | Partly: containment (DEC-254, `src/gov/guard/containment.py`) attributes a worktree's changes to its session; nothing refuses a second writer; nothing makes the tests worktree | W2-33 (the role files), W2-83b (the playbooks), W2-60b (the launcher) | the body says so (W2-33, DEC-963), the KPIs do not | W2-33 and W2-60b KPI changes |
| 22 | The test-data rule: the spec states the data, who secures it, escalation | No (a writing rule) | W2-98 (the spec-writing skill) | yes ("the spec states what data its tests need … data that cannot be secured is escalated as a P1, never skipped") | none; the ticket template's line rides with W2-98 if it is in its paths |

## The changes proposed to existing tickets

Each line is a KPI to add, or a KPI to replace, in the tickets' own style. All cite DEC-982 (this decision).

**W2-20 (the machine-wide gate; practices 8 and 20).** Replace KPI 6's "the floor + one verification run's peak (reserved once) + a working size for each running session and for the new one" with:
- 'The gate opens on memory while MemAvailable plus the running sessions'' live memory is at least the floor plus a working size for each running session and for the new one; nothing is reserved for a run that has not started [DEC-961, DEC-982]'

Replace KPI 7 ("No fixed number …") with:
- 'Heavy jobs take a slot: a test run and a rebuild each wait for one of a configured number of machine-wide slots (the number in the gate''s configuration file, sized from a measure so that the load stays near the number of processors); sessions, reviews and single-process runs take no slot and are gated only by load, memory and disk; no other fixed ceiling on leads or sessions [DEC-979 item 1 D1, DEC-982]'

Add:
- 'The out-of-memory trip-wire: below a second, lower memory floor (in the configuration file), the gate names the largest heavy job and stops it before the kernel''s out-of-memory killer would end a session, and the stop is a finding; nothing else is stopped [DEC-947, DEC-982]'

**W2-97 (the merge queue; practices 3 and 8).** In KPI 3, replace "the full suite runs only for a change to the core (the selection's own …)" with "the full suite never runs here; it runs only in the nightly [DEC-968, DEC-982]". In KPI 1, replace "under the test lock" with "in a heavy-job slot (DEC-979), or freely until the slots run [DEC-962, DEC-982]". (Its lead started at 22:14: the change rides in its run if the owner approves tonight, else in its next round.)

**W2-38 (impact-selected tests; practice 3).** Replace "The full suite runs at milestones and in CI" with "The full suite runs only in the nightly [DEC-968, DEC-982]".

**W2-82 and W2-83a (practice 3).** Replace "the full regression in the close's form is green apart from reds the ticket does not own" with "the scoped set in the close's form is green; every red the ticket did not cause is named for the CTO [DEC-968, DEC-982]". (W2-78 has the same line; it is parked.)

**W2-12 (owner approval facts; practice 5).** Qualify KPI 4: "where a project keeps the ratchet's lists on (the strict close, W2-115), the close counts a ratchet entry … ; in the default close no list is read [DEC-968, DEC-982]". The rest of W2-12 (`gov approve`, the owner's push as acceptance) is unchanged.

**W2-11 (the briefs and the orchestration skill; practices 9, 15, 18, 19).** In round 2 (round 1 is running and narrow, DEC-981), add:
- 'The kernel''s lead brief template carries a `brief_gaps:` section (gap, where it belongs, its cost) after the twelve fields, and the orchestration skill states that the gaps are fixed in the template within the week (DEC-943, ROLES-SPEC-1 G14) [DEC-982]'
- 'The orchestration skill states the anti-drift kit: a fresh orchestrator session every morning from a handover (checkpoint, RESUME HERE, the decisions in force), the digest loaded at start, every rule written into its five places (DEC-851) [DEC-952 item 6, DEC-953 item 7, DEC-982]'
- 'The orchestration skill states scope control: a new ticket in the WBS goes to the owner as a P1 with a recommendation before it is filed; leads name a needed ticket in their return and never file one [DEC-974, DEC-982]'
- 'The test-design skill states that a timing test measures the work under test (its process''s CPU time, or against a quiet reference beside it), never the wall time of a loaded machine, at the same bound [DEC-979 item 1 D2, DEC-982]'
(Its paths gain the test-design skill's `SKILL.md` body for that section.)

**W2-55 (decisions by domain, status and scope; practice 15).** Add:
- '`gov context --in-force` prints the digest of the decisions in force (one line each, superseded and done ones left out), generated from the register, and the kernel''s session-start hook loads it with RESUME HERE where the project turns that on (the hook''s injection is the owner''s CIT-P question, DEC-952 item 5) [DEC-953 item 7, DEC-982]'

**W2-33 and W2-60b (practice 21).** W2-33, add:
- 'Every role file states one writer per worktree: two sessions that write never share a worktree; a ticket''s test designer works in its own tests worktree, merged by the lead [DEC-847, DEC-963, DEC-982]'

W2-60b, add:
- '`gov launch` refuses a second writing session in a worktree that has one live (read from the session records), naming it; a reviewer or the QA engineer, which write only their reports, are not counted; `gov launch --tests-worktree` makes a ticket''s tests worktree on its own branch from the ticket''s head [DEC-847, DEC-963, DEC-982]'

## The new tickets (P1s, DEC-974)

### W2-115: `gov close`, the smart close (before EXAMIN's copy)

- **Why:** the product's close contradicts practices 2 to 6 and 14 (the map). EXAMIN's copy and the proving ground prove "a clean `gov close` at exit 0"; it must be this close they prove. DEC-953 keeps every feature built, so the strict close stays, switched off by default.
- **Class:** implementation; engineer; **FULL** (it is the judge). About 400 lines. **Paths:** `src/gov/close/command.py`, `select.py`, `batch.py`, `nightly.py`, `tool.py`, `ratchet.py` (reads only), a new `src/gov/close/attribution.py`, `template/governance/project/test-map.yaml`, `tests/unit/close/test_w2_115*`.
- **Dependencies:** W2-108 (closed tonight); W2-12 and W2-38 touch the same files: one chain (W2-115 first). It holds the close's shared core while it runs: keep the critical chain's files apart.
- **KPIs:**
  - 'A project setting chooses the close: `close: scoped` (the default of a new project) or `close: strict` (today''s close, unchanged, every lifted gate kept built); this repository runs scoped [DEC-953 item 1, DEC-982]'
  - 'The scoped close runs only the selection: the ticket''s own suite and every suite its change can reach, a shared-core change included (its mapped suites, never the full); records and governance files (the record places, the governance overlay) select nothing by themselves; a selection that cannot be made is refused with its reason, never widened; the full suite runs only in the nightly [DEC-953 item 4, DEC-968, DEC-982]'
  - 'One selection command for every level: `gov close --select <ticket>` prints the scoped set and its `pytest` options for a lead or a worker, the same set the close runs [DEC-953 item 4, DEC-982]'
  - 'Every failing test is run again alone; a red alone is traced with and without the change, interleaved, three rounds and three more unless decisive; the close is refused only by a red the change caused (green without it every round, or red with it at least half the rounds more than without; a case that cannot be collected without the change is the change''s only if it is red with the change alone) [DEC-968, DEC-982]'
  - 'A red the change did not cause is named in the close record and opened as a repair ticket for the orchestrator to fix at once or escalate; no list is read or written in the scoped close [DEC-968, DEC-982]'
  - 'A batch close finds the culprit of each caused red (its merges taken out, the red re-run alone, the merge refused as a candidate when it brings another ticket''s commits); the rest close on the same run and the culprits go back; a red no single ticket explains, or a candidate that cannot be isolated, refuses the batch [DEC-979 item 3, DEC-982]'
  - 'Each close writes its close record (the commit closed, the runs and their counts, the review''s verdict, every red with its reason, the culprits sent back) — the audit''s practice 9 [DEC-953 item 5, DEC-982]'
  - 'The nightly rebuilds its worktree''s stores with the full secrets scan (`GOV_SECRETS_FULL_SCAN=1`) before its run, and its record says so [DEC-966 item 4, DEC-982]'
  - 'Measured: the CTO''s `close_build.py` and this close give the same verdict on three of this repository''s recorded batches (one clean, one with a caused red, one with an unowned red) [DEC-982]'

### W2-116: the designers' store (before EXAMIN's copy)

- **Why:** the test designer retrieves only from the integration branch's store (DEC-963), so its retrieval never serves a ticket's implementation; W2-33's role files and W2-83b's playbooks will tell an adopted product's designers so, but nothing in the product builds that store.
- **Class:** implementation; engineer; STANDARD. About 150 lines. **Paths:** `src/gov/rebuild/` (an `--integration` mode), `src/gov/launch/` (the designer's store), `tests/unit/rebuild/test_w2_116*`.
- **Dependencies:** W2-60b (the launcher's files), W2-33 (the rule it serves).
- **KPIs:**
  - '`gov rebuild --integration <branch>` keeps a store of that branch''s head in two detached worktrees outside the project, building into the one not in use and switching a link to it only when the build succeeded; a search during a build is answered from the ready one [DEC-963, DEC-982]'
  - 'It is refreshed after the nightly''s verdict and at a set second time each day (both in the project''s configuration), and its status (head, age) is in `gov status` [DEC-966 item 3, DEC-982]'
  - '`gov launch independent-test-designer` points the session''s retrieval at it; a designer''s retrieval never reads a ticket worktree''s store [DEC-963, DEC-982]'

### W2-117: the merge queue in the product (after EXAMIN's copy, Wave 3)

- **Why:** W2-97 builds this repository's queue as its own tool (`governance/project/orchestration/tools/`), which is right for now; an adopted product with streams needs it as a `gov` command. EXAMIN's copy runs one LITE ticket, which needs no queue.
- **Class:** implementation; engineer; FULL. About 250 lines: `gov queue` (enqueue, test, advance or eject, record) from W2-97's tool, in `src/gov/queue/`. **Dependencies:** W2-97 (measured in use here first), W2-115 (its runs), W2-20 (its slots).
- **KPIs:** W2-97's, in the product: the commit tested is the commit landed; one run per batch on the merged result; a run skipped when the merged code is identical, with its reason; a red batch's culprit ejected and the rest advanced [DEC-959 item 1, DEC-982].

### W2-118: interim results and the return's brief gaps (after EXAMIN's copy, Wave 3)

- **Why:** the three layers in this repository use the CTO's watchers; an adopted product's Senior Engineers need the same, in the product.
- **Class:** implementation; engineer; STANDARD. About 120 lines. **Paths:** `template/governance/kernel/hooks/subagentstop.py`, a `gov watch` command. **Dependencies:** W2-33, W2-60b.
- **KPIs:**
  - '`gov watch` wakes its caller when a lead''s worktree gains a commit whose subject marks a key result (a probe record, a measure, a package, a baseline) and when a lead returns, each once, named [DEC-952 item 3, DEC-982]'
  - 'The subagent-stop hook checks a lead''s return for the `brief_gaps:` section beside the twelve fields (W3-P02) [DEC-943, DEC-982]'

### W2-119: the guard's refusals counted (before EXAMIN's copy)

- **Why:** EXAMIN's agents will meet the guard in ordinary work; a refusal that should not happen costs minutes each time, and today only this repository's CTO counts them, from transcripts (41 of 43 since ACT 1 were false).
- **Class:** implementation; engineer; FULL (it is the guard, but it only records). About 80 lines. **Paths:** `template/governance/kernel/hooks/pretooluse.py` (one record per refusal), `src/gov/status/` (the count). **Dependencies:** W2-110 (the hook's file).
- **KPIs:**
  - 'Each refusal of the PreToolUse hook writes one line to `.gov-runtime/records.jsonl` (time, the session''s role and ticket, the tool, the rule, a hash of the command''s form, never its text or a secret) [DEC-958, DEC-982]'
  - '`gov status` counts the refusals by rule over a day and a week; a rule whose count passes the project''s threshold (default 3 a day) is a finding that asks for a fix package [DEC-958, DEC-982]'
  - 'Nothing the guard decides changes; a record that cannot be written never changes a decision [DEC-982]'

## What stays this repository's own, and why

- **The nightly's schedule:** the crontab lines, the Windows wake task, the quiet hours and the ping gate (`governance/project/orchestration/nightly/`). They fit one owner's PC and one time zone. The product gives the nightly run (`gov.close.nightly`, W2-115's full scan) and W3-P03 parks its window and estimate for the judge; when to run it is each operator's choice.
- **The CTO's capacity tools:** the samplers, the benchmark loop, the store survey and the latency trace. They are measurements for this machine's decisions, not practices a product needs.
- **The brief builder and this repository's briefs:** the kernel's templates are the product's (W2-11); the builder that fills this repository's common brief is this repository's.
- **The CTO's watchers and close tool, until W2-115 to W2-119 land:** they keep running here; each is retired when its product feature replaces it, so the Gov OS dog-foods its own.
- **The designers' store's place** (`~/gov-os-worktrees/W2-00-store`) and its two times a day: this repository's configuration of W2-116.

## The owner's decisions

1. **W2-115, the smart close.**
   1. Context: the product's `gov close` contradicts five practices, and EXAMIN's copy would prove it.
   2. What happened: the smart close lives only in the CTO's `close_build.py` and `select_tests.py`.
   3. Why it matters: EXAMIN and every adopted product would run the bulk close.
   4. Options: (a) file W2-115 before EXAMIN's copy, FULL; (b) after EXAMIN, with EXAMIN on `close: strict` meanwhile.
   5. Recommendation: (a), high confidence.
   6. Blocks: EXAMIN's exit criterion 1 proves the wrong close without it.
2. **W2-116 and W2-119, before EXAMIN's copy:** (a) file both; (b) file after EXAMIN. Recommendation: (a). W2-116 makes the designers' rule work in a product; W2-119 is small and protects ordinary work.
3. **W2-117 and W2-118, after EXAMIN's copy:** (a) file both now, ordered after W2-27 (Wave 3 work, in the WBS for its order); (b) park them as Wave 3 rows. Recommendation: (a), so the order is in the plan.
4. **The KPI changes to W2-20, W2-97, W2-38, W2-82, W2-83a, W2-12, W2-11, W2-55, W2-33 and W2-60b:** (a) apply them as written (W2-97's in its running lead's next step, W2-11's in its round 2); (b) apply only those that remove a contradiction (W2-20, W2-97, W2-38, W2-82, W2-83a, W2-12). Recommendation: (a). W2-55's KPI 5 ("supersession propagates") would have caught the four contradictions; it should run before W2-115.
5. **What stays this repository's:** as listed. Recommendation: agree.
