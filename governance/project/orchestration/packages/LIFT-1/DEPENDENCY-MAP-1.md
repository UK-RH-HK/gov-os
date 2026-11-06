# DEPENDENCY-MAP-1: dependency mapping as a tool, from each ticket's paths (for the owner; DEC-1087 (5))

**Status:** for the owner's decision. Nothing is filed or built before it. Written 2026-11-06 by the CTO, from the
refreshed memory (the integration store at integrate's head, 11-06 19:45) and a read-only survey of the code.

**In one paragraph:**
- **The tool:** a new command, `gov plan`, in a new engineer ticket, **W2-136**. It reads every open ticket's writes
  (its `allowed_paths`, as today) and two new fields set by the ticket template, `reads:` and `waits_on:`. From them it
  derives a dependency map, and from the map the launch: which tickets run together in one batch, and which wait for a
  named ticket or batch, each with its reason. It is deterministic, read-only and a proposal. The orchestrator approves
  it into the ready list, so the dispatcher still never chooses the order (DEC-1007 (2)).
- **The template's two fields** are one KPI line added to W2-128.
- **Recommendation:** build it right after re-pin window 4, beside the experiments, so it is live at the lift's re-pin,
  when leads start again and parallel batches matter. Building it first would delay the re-pin and the experiments by
  about 1.5 days.

## 1. What exists today (the survey; file and line)
- **Writes are declared and enforced:** each ticket's `allowed_paths` (front matter). The guard enforces them
  (`src/gov/guard/decide.py:63-158`; `*` stays inside one folder, `**` crosses folders, `decide.py:96-102`). The path
  map points at them per ticket through `{ticket_impl}` and `{ticket_tests}` (`governance/project/path-map.yaml`,
  `role_paths`).
- **Reads and waits are not declared:** no ticket has a `reads:` or `waits_on:` field. The ticket schema does not
  forbid adding them (`schemas/…/ticket.schema.json`).
- **Order today:**
  - `depends_on` becomes `DEPENDS_ON` edges in the store (`src/gov/store/loader.py:500-501`);
  - the READY rule reads `deps` (`src/gov/tasks/queue.py:55-92`);
  - the bridge checks for cycles (`src/gov/tasks/bridge.py:85-90`).
  - Some tickets' `deps` and `depends_on` disagree, so the READY rule can see a different order from the store.
- **Overlap:**
  - **no code compares one ticket's writes with another's.** The only overlap code maps changed files to tickets to
    choose tests (`src/gov/close/select.py:393`);
  - the rule "overlapping tickets wait" exists only as text (DEC-235: "a ticket starts only when its dependencies are
    closed and its `allowed_paths` overlap no ticket in flight"; the prompt §3).
- **The dispatcher:** "its order comes from the plan, never its own choice" (DEC-1007 (2)). W2-121 (the product's
  dispatcher, `DAEO-cb2b`) is not built.
- **Earlier decisions:**
  - **DEC-936 item 3.4** proposed "a planner: from the dependency graph (depends_on, overlapping paths), which tickets
    can run in parallel and how many fit on this machine", the full planner for Wave 3. **This decision brings its
    dependency half into Wave 2.** The machine-capacity half stays where it is (the gate, W2-20).
  - **DEC-899** allows owner exceptions to the overlap rule, so an override is needed.
- **The link graph:**
  - the store's edges (`DEPENDS_ON`, `SUPERSEDES`, …);
  - W2-92's stated links;
  - W2-129 (`gov links`, being built now), which will check that every id a ticket names exists. `waits_on:` ids are
    checked the same way.

## 2. The proposed decision (wording for the register)
**Dependency mapping as a tool, in Wave 2 (DEC-1087 (5)):**
- (1) **The ticket template** (W2-128) gains two fields, set when a ticket is filed:
  - `reads:` — the paths the ticket reads: wide, path patterns as the guard reads them;
  - `waits_on:` — the research, specs or other tickets it waits on: ids (a ticket, a decision, a research record) or
    record paths.

  `allowed_paths:` stays the writes: strict and limited, as today. W2-128's ready check refuses a new ticket without
  `reads:`, with a named reason.
- (2) **The ticket store is the per-ticket path data.** The path map keeps pointing at it (`{ticket_impl}`), with no
  per-ticket block of its own, so there is one source.
- (3) **A new engineer ticket, W2-136,** builds `gov plan`. It derives the dependency map and sets the launch:
  - **after (hard):** a ticket's `depends_on`, and its `waits_on` while the thing waited on is not closed or not
    ACCEPTED;
  - **after (read-after-write):** a ticket that reads a path another unfinished ticket writes runs after it;
  - **in series (write-write):** tickets whose writes overlap;
  - **in parallel:** the rest, in one batch;
  - **ties and cycles:** by a fixed key (priority, then the WBS order, then the id), never by chance;
  - **every wait is named:** the ticket or batch it waits for, and the reason code.
- (4) **It is a proposal, deterministic and read-only.**
  - The same tickets give the same plan, byte for byte.
  - The orchestrator approves it into the ready list (DEC-1007 (2) holds), and the dispatcher reads that list
    unchanged.
  - An owner exception to the overlap rule (DEC-899) is a recorded override on the ticket (`plan_override:` with the
    decision id), shown in the plan.
- (5) **What paths cannot show** is added by the orchestrator and leads, from memory and the link graph, as `waits_on:`
  entries with a reason. Those entries are the recorded links, and `gov links` checks their ids.

## 3. The spec of `gov plan` (W2-136)
- **Command:** `gov plan [--open | --tickets <id>…] [--json] [--ready <file>]`.
  - `--open`: every open and in-progress ticket.
  - `--ready <file>` writes the batches in the dispatcher's ready-list form, for the orchestrator to review and
    commit. It writes nothing else.
- **Input:**
  - from each ticket: `allowed_paths` (writes), `reads`, `waits_on`, `depends_on` (and `deps`; a disagreement between
    the two is a finding, `DEPS_DISAGREE`), status, priority and WBS id;
  - the store's edges, for the status of what is waited on;
  - the repository's tracked files, to settle pattern overlap.
- **Pattern overlap, decided one way only:**
  - Two patterns overlap when some path matches both under the guard's own matcher (`*` within a folder, `**`
    across). This is the same function the guard uses, so the plan and the guard never disagree.
  - It is computed on the tracked files, plus a pattern-to-pattern test for paths not yet created: literal prefixes
    compared, then the rest's wildcards. The test errs toward "overlap", so it can make tickets wait but never lets two
    writers collide.
- **Undeclared reads:**
  - A ticket with no `reads:` (every ticket filed before W2-128's line) is planned as reading only its own writes.
  - It is flagged `READS_UNDECLARED` in the plan, so the orchestrator sees that its order rests on less.
  - The ready check (W2-128) refuses it for new tickets.
- **Wide reads:** see §5, the one point for the owner.
- **Output:**
  - first line: `gov plan: N tickets, B batches, W waits (codes...)`;
  - then per batch: `batch k: T1, T3, T5`, and for each waiting ticket `T2 waits for T1 (READS_WHAT_WRITES
    src/gov/x.py)`;
  - `--json`: the same, in the shared envelope;
  - exit codes: 0, a plan; 1, a plan with findings (`READS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`); 2, cannot
    run.
- **Codes:** `DEPENDS_ON`, `WAITS_ON`, `READS_WHAT_WRITES`, `WRITES_OVERLAP`, `CYCLE_TIEBREAK`, `OVERRIDE`,
  `READS_UNDECLARED`, `DEPS_DISAGREE`, `UNKNOWN_WAIT`.
- **Bounds:** no model, no network, no GPU, no store write. Under 5 s on this repository's open tickets (measured by the
  CTO). Never a gate: no close, landing, launch, claim or hook calls it.

## 4. The KPI lines
**W2-136 `gov plan` (new; engineer; tests first by an independent test designer; est. about 450 lines of code plus
tests):**
- **S1** `gov plan --open` reads every open and in-progress ticket's writes, `reads`, `waits_on`, `depends_on` and
  `deps`, and prints the batches and the waits as §3 states; `--json` gives the same in the shared envelope. Verify: a
  planted ticket store [DEC-1087 (5)]
- **S2** A ticket that reads a path an unfinished ticket writes waits for it (`READS_WHAT_WRITES`, naming the path);
  tickets whose writes overlap run in series (`WRITES_OVERLAP`); a `depends_on` or an unfinished `waits_on` makes it
  wait (`DEPENDS_ON`, `WAITS_ON`); the rest share one batch. Verify: planted tickets for each case [DEC-1087 (5),
  DEC-235]
- **S3** Overlap is decided by the guard's own pattern matcher, on the tracked files and pattern to pattern for paths
  not yet created, erring toward overlap. Two patterns the guard would let two writers both touch are never planned in
  parallel. Verify: planted patterns with `*`, `**`, literal paths and a not-yet-created folder [DEC-1087 (5)]
- **S4** Deterministic: the same tickets give byte-identical output in any file order. Ties and cycles are broken by
  priority, then WBS order, then id, and named `CYCLE_TIEBREAK`. Verify: planted ties, a read-after-write cycle, and a
  shuffled file order [DEC-1087 (5)]
- **S5** A ticket without `reads:` is planned as reading only its writes and flagged `READS_UNDECLARED`. A `deps` that
  disagrees with `depends_on` is flagged `DEPS_DISAGREE`. A `waits_on` id that names nothing is `UNKNOWN_WAIT`. Verify:
  planted tickets [DEC-1087 (5)]
- **S6** `plan_override: <DEC-id>` on a ticket lets it share a batch despite an overlap, shown as `OVERRIDE` with the
  decision id. Verify: a planted override [DEC-899]
- **S7** `--ready <file>` writes the batches in the dispatcher's ready-list form and nothing else. Without it, the
  command writes nothing. Verify: the tree hashed before and after [DEC-1007 (2)]
- **S8** Never a gate: no close, landing, launch, claim, readiness or hook module imports or calls it. Verify: a source
  scan [DEC-1052]
- **S9** Under 5 s on this repository's open tickets: the median of five runs, measured by the CTO and recorded in its
  evidence [DEC-1052 basis (3)]
- **Failure lines:**
  - two tickets whose writes overlap planned in the same batch without an override;
  - a plan that differs between two runs on the same tickets;
  - a file written without `--ready`.

**W2-128, one line added (the template; the product-spec's lane, through W2-128's CIT-P):**
- **The ticket template** sets `reads:` (wide path patterns) and `waits_on:` (ids or record paths, each with a
  one-line reason) beside `allowed_paths:`.
- **The ready check** refuses a new ticket without `reads:`, naming `READS_MISSING`, and checks each `waits_on` id
  exists.
- **The guard** reads `reads:` only as information. Reads stay open (DEC-820).
- `[DEC-1087 (5), DEC-1052]`

**W2-121, one line added (the dispatcher):** the ready list it reads may come from `gov plan --ready`, reviewed and
committed by the orchestrator. Its own order is still never its choice. `[DEC-1007 (2), DEC-1087 (5)]`

## 5. The one point for the owner: how wide reads order tickets
Reads are wide by design (DEC-1087 (5)). Taken literally, a ticket that reads `src/**` would wait for every unfinished
ticket writing anything in `src/`. The survey counts 27 tickets that write `src/gov/retrieval/**` alone, so most of
Wave 2 would run one after another.
- **(a) Every read orders** (the decision's words, literally). It is safe, but heavily serial while reads are wide. The
  plan shows how many waits each wide read causes, so the reads can be narrowed ticket by ticket.
- **(b) Recommended.** `reads:` stays wide, for information and for the plan's warnings (`READS_WIDE`, with the waits it
  would cause). The hard read-after-write order comes from a narrower list in the same template, `needs:`: the paths
  whose finished state the ticket depends on. `waits_on:` covers research and specs.
  - The template asks for both. The plan orders on `needs:` and `waits_on:`, and warns on `reads:`.
  - This keeps the owner's wide reads, and gives parallel batches that are real.
- **(c)** Order on reads, but only against writers whose writes are concrete files rather than folders. This depends
  on how a writer happened to write its patterns, so it is not recommended.

## 6. Home, estimate and timing
**Home:**
- **One new ticket, W2-136** (`src/gov/plan/**`, `tests/unit/plan/**`). No existing ticket owns it:
  - W2-116 is the integration store only;
  - W2-121 is not built and may not choose the order;
  - W2-128 holds no `src/` path.
- **W2-128** gets the template line; **W2-121** the reading line.

**Estimate (est.):**

| part | effort |
|---|---|
| the tests, by an independent test designer | about 3 h |
| the engineer | about 1 lead-day (about 450 lines: the fields and validation 80, the derivation 150, the overlap matcher 80, the batches 70, the command and output 70) |
| one review | about 1.5 h |
| **W2-136 in all** | **about 1.5 days** |
| W2-128's template line | about 0.5 day, inside D-5 (the templates), through CIT-P |

**Before or after the re-pin? After, right away (recommended):**
- **Building it first** moves the re-pin from about 11-07 evening to about 11-09, and the experiments and the lift with
  it, by about 1.5 days.
- **It is not used before the lift:** no leads run until then (the emergency's rule). Its first real use is the three
  layers' streams after the lift (DEC-1087 (13)), where batches decide what runs in parallel.
- **Built right after the re-pin,** beside the experiments (CPU work while the GPU measures), it is live at the lift's
  re-pin (window 5).
- **The parallel-agents test after window 4** (DEC-1087 (10)) then checks the gating that exists, `depends_on` and the
  READY rule, and states that the planner comes at window 5.
- **If the owner prefers it before the re-pin:** the re-pin is ready about 11-09, and everything after moves 1.5 days
  (the lift about 11-16, EXAMIN's copy about 11-22).

**The owner's decisions here:**
- (1) the decision in §2;
- (2) W2-136's KPI lines and W2-128's and W2-121's added lines;
- (3) §5's option ((b) recommended);
- (4) the timing (after the re-pin recommended).
