# Discovery G-7: the chain from feature to code, and three ways to make it deterministic

`docs/emergency-2/integration/CHAIN-DISCOVERY.md` · research (Sonnet), read-only · 2026-11-24 · Gov OS `w2/integrate` at `98893679c`; EXAMIN `/home/usain/gov-os-runs/W2-27/examin` at `e2c25b8` (read only) · for the owner's card G-7 (DEC-1241)

**How it was made.**
- **Memory first.** `gov retrieve` ran once. The store was behind HEAD (584 stale paths, finding I-9), so the bundle gave only a few useful chunks (`discover/tickets.py:107`, the spec-writing skill, the ticket template). I read the files in my own words after that. No claim below rests on the bundle alone.
- **What I read.** The spec form and `check_spec.py`; `gov discover`; the ticket schema and template; `gov plan`; `gov brief`; `gov accept` and its README-map parser; the landing's checks and selection; `gov impact`; `gov links`; the record graph loader; the tasks bridge. I read DEC-1238 to DEC-1242, TOOL-MAP §4, DECISIONS-HELD §4 and audit 4's A-3, A-12 and A-23b. I read EXAMIN's X12 feature (backlog row, OpenSpec change, ticket).
- **What I measured.** I ran Gov OS's own parser over the 189 acceptance folders and 271 tickets, read-only, with `python3 -I`.
- **Helper.** One Sonnet helper did the outside state of practice (§2) and returned rows with URLs. What it could not confirm is marked in §2.
- **One slip.** I ran `gov links --all --root <EXAMIN>`. It rewrote its bookmark `.gov-runtime/links/mark` (git-ignored, one sha). I restored the old value (`f97faba0…`) and checked `git status` is clean. Nothing else in EXAMIN was touched.
- **Not done.** No test of Gov OS was run. Sizes in §3 are my estimates, not measurements.

---

## The short answer

1. **The unit of the whole chain is the KPI line, and it has no home and no stable name.**
   - In the spec it is a bullet `K<n>` in prose (`check_spec.py:32`).
   - In the ticket it is a list position, read as `S<n>`/`F<n>` by `gov brief` (`brief/build.py:112`) and as `success-N`/`failure-N` by `gov accept`. A prefix typed into the line text is only a convention (20 % of the lines have one, and 37 of those disagree with the position).
   - In the README it is a cell of prose that a 130-line regex reader tries to understand (`accept/runner.py:73-200`).
   - No code compares any two of these.
2. **`gov accept` never reads the ticket's own KPI lines.** It judges only the lines the README names (`accept/runner.py:662-705`; `ticket` and `front` are used only to find the folder, `:707-760`). A line the README omits is never judged, never failed, never mentioned. Measured: **45 closed tickets have 138 of their 1,272 KPI lines (11 %) in no map; 15 tickets' maps name a line the ticket does not have.**
3. **The Gov OS machinery to join the chain mostly exists** (`gov discover --ticket` copies a spec's K-lines into a ticket with the id `[K1]` and a verify; `gov brief` prints the KPI table; `gov accept` judges per line; the landing's selection traces code to tests; `gov impact` walks the graph). **They are used on separate paths:** `gov discover` has no caller; EXAMIN's X12 ticket and spec were written by hand in a different spec form.
4. **Recommendation:** Approach A, *derive and check the trace over what exists*. Its first slice needs no new command and about 150 lines. See §4.

---

## 1. Each link today

"Held by": **code** = a program refuses or produces it; **after** = a program checks it, but only when typed or after the fact; **agent** = a session writes it by hand, no check.

### 1.0 The forms, and what a "KPI line" is in each

| Where | Form | Id of a line | Read by |
|---|---|---|---|
| Spec, Gov OS form | nine `##` parts; `- K<n>: <behaviour>` then `Fails if:` (`spec-form.md:6-44`) | `K<n>`, typed | `check_spec.py` (text, not a schema; `specification.schema.json` is front matter only) |
| Spec, OpenSpec form (EXAMIN) | `### Requirement:` with `SHALL`, `#### Scenario:` WHEN/THEN (`template/openspec/.../spec.md`) | none (names only) | `openspec validate` (node; pinned 1.13.2, `tool-registry.yaml:52-59`) |
| Contract item (Gov OS's own features) | one `acceptance:` sentence and a list of `covers` items (`contract.yaml`, CAP-33) | none | nothing |
| Ticket | `kpis: {success: [..], failure: [..]}`, each a string or `{line, verify}` (`ticket.schema.json:5-25`) | **list position** | `gov brief`, `gov accept` (by name only), `links` (brackets only) |
| README map | prose table, cell like `S1 / success 4, failure 2 [CAP-61.c]` | `success-N`, `failure-N` | `parse_map` (`runner.py:139`) |
| Test | a pytest function | its name, matched to a README item (`runner.py:205`) | `gov accept` |

### 1.1 Feature → spec

- **How made.**
  - EXAMIN: a backlog row (`docs/plans/tasks/X12.md`, 308 such rows) → an OpenSpec change (`openspec/changes/x12-term-registers/`: proposal, tasks, two spec deltas), by hand.
  - Gov OS: a Contract item or a decision, then a WBS row, by hand. Gov OS has no `openspec/` folder and no spec file with K-lines for its own work.
  - `gov discover "<idea>"` would write a draft nine-part spec, a proposal, a readiness record and a discovery ticket (`discover/command.py:87-110`). **Nothing calls it** (TOOL-MAP row 32).
- **Held by.** Agent. `gov readiness` and the spec check are typed.
- **Breaks.**
  - There is no field naming a feature. The ticket's `wbs_id` is a free id; `sources` lists decisions, Contract items and paths.
  - **Two spec forms exist and conflict.** `gov discover` writes `openspec/changes/<change>/spec.md` in the nine-part form with K-lines; the `feature-readiness` schema it sits in (`schema.yaml`, `templates/spec.md`) asks for `specs/**/*.md` deltas with Requirements and Scenarios. EXAMIN follows the schema: `gov discover --check x12-term-registers` answers `DISCOVER_CHANGE_NOT_FOUND ... holds no spec.md`. See SQ-G7-1.

### 1.2 Spec → KPI lines (K-lines in the spec, the lines in the ticket)

- **How made.**
  - By code, in one place only: `gov discover --ticket` copies each K-line, verbatim, into the ticket as `"<behaviour> [K<n>]"` plus the spec's `## Verify` line, and sets `specification: <id>` (`discover/tickets.py:107-117`, `discover/command.py:186-205`). It refuses a spec that fails the check.
  - Everywhere else a person re-tells the spec. EXAMIN's X12: the spec has two Requirements with six Scenarios; the ticket has S1 to S3 and F1 to F2, cut differently, with code names (`keyword_strategy.generate`, `sync_terminology`) that the spec form refuses in a KPI line (`spec-form.md:46-61`).
- **Held by.**
  - Agent. `check_spec.py` checks a spec in itself (nine parts, `Fails if:`, no code names).
  - **Nothing compares a ticket's lines with its spec's K-lines.** `links/check.py:158` reads the ticket's lines only for bracketed ids such as `[DEC-n]` (`UNLINKED_ID`, `:556-575`). The ready check reads `kpis` alone (`brief/build.py:157-186`). Audit 4 names the gap (A-23b, "tests written to a ticket that drifted from its spec") and the owner's page names it ("nothing checks that a ticket's KPIs match its spec", G-6).
- **Breaks.**
  - 0 of 271 Gov OS tickets have a `[K<n>]` suffix; 0 have a `specification` field (measured). The field is declared in no schema (`ticket.schema.json` lists no `specification`).
  - The queue's idea of "has a spec" is a non-empty ticket body (`queue/checks.py:121`, `NO_SPEC = "no spec (the ticket's body is empty)"`).
  - The third way a ticket was meant to be made, the tasks bridge (`tasks/bridge.py:1-14`, `tasks.md` → tickets with `specification`), has no caller either (TOOL-MAP row 95).

### 1.3 KPI lines → tickets

- **How made.**
  - By hand in Gov OS and EXAMIN (`tk create`, then edit). Gov OS: 271 tickets, 2,336 lines, 87 with the `{line, verify}` form (the rest are strings, some holding `Verify:`).
  - By code: `gov discover --ticket`, with `acceptance_tests: {path, author}` set (`discover/command.py:196-202`).
  - `gov plan` orders tickets by `depends_on`, `waits_on`, `needs` and path overlap (`plan/derive.py:1-30`). It reads no KPI line and no spec.
- **Held by.**
  - Code for the form: the ready check refuses an empty `allowed_paths`, a success line with no `verify` (`KPI_NO_VERIFY`), an unclosed dependency (`brief/build.py:157-186`); the schema requires `role`, `allowed_paths`, `kpis` (`ticket.schema.json:6`).
  - After, for "is it a feature": the queue's notice `NEW_TICKET_NOT_FEATURE` (`queue/checks.py:106-139`), by guessing from "has a verified line and a body". Decided but not built: R-3 (`kind: feature`, required by the schema, 219 tickets migrated by a chore).
- **Breaks.**
  - **Ticket lines carry their own ad hoc id.** 479 of 2,336 lines (20 %) start with `S<n>`/`F<n>`, some after an item label like `A1 S1:`; **37 of those 479 disagree with the line's real position.** `gov brief` and `gov accept` use the position and ignore the prefix.
  - Gov OS's leads start from hand briefs; about 40 briefs only mention commands (TOOL-MAP §2, rule 2). `gov brief` is used in EXAMIN (3 times) and builds the KPI table (`brief/build.py:413`) from the position. G-3 decided that every brief is generated.

### 1.4 KPI lines → tests (the test designer's map)

- **How made.** The independent test designer writes tests and a README. Its map is a table with a KPI column (`success-N`, `failure-N`, N its number in the ticket) and a test column of code spans (`test-design/SKILL.md:47`; `test-kinds.md`). In practice the cells are prose (`S4: the ratchet's reading of both lists [I4 F14]`).
- **Held by.**
  - Code at the landing: `gov queue` refuses a ticket whose README `gov accept` cannot read (`acceptance_refusal`, `queue/checks.py:171-199`: `NO_ACCEPTANCE_TESTS`, `ACCEPT_NO_MAP`, `ACCEPT_MAP_UNREADABLE`) and checks who wrote the tests (`checks.py:52-73`).
  - Not before: `gov accept --map-only` (A-12) is not built, so the designer learns the map is unreadable at the landing.
  - Not at all: red on the base (A-3; "no base run exists in `src/gov/queue/`", TOOL-MAP row 52). The only trace of the incident is `8a95d3873` ("5 pass on the base", audit 4 §A-3), self-reported.
- **Breaks (measured on this tree).**
  - Of 189 acceptance folders: **122 parse; 24 have no README, 31 have a map row naming no line the reader can read, 8 map no line, 4 have a cell it refuses** (`Unlisted`). That is 67 failing, close to TOOL-MAP's 72 at `5617f2e5e` (a different commit).
  - **A ticket line absent from the map is never judged.** `_report` iterates `mapping`, not the ticket's lines (`runner.py:662-705`). Of 129 tickets with a readable map: 45 (all closed) have some ticket line unmapped, 138 of 1,272 lines. Fifteen maps name a line the ticket lacks (drift).
  - The reader is 130 lines of regex to understand free prose (`runner.py:73-200`): the symptom of a map that is not a typed record.
  - T-3 (DEC-1242: "at least one red case per KPI line; guard cases allowed when the README row marks them guard") needs a *typed* row (a line, its tests, a guard mark). `parse_map` has no such notion.

### 1.5 Tests → code (and the way back: code → tests)

- **How made.**
  - Forward: the ticket's `allowed_paths` say what code the ticket may write; the tests exercise it. Nothing links a test to the code it covers except what the selection derives.
  - Back, at the landing: `close/select.py` (`scoped`, `:756`) selects, for a change, the suite of every ticket whose `allowed_paths` match a changed path (`_tickets`, `:231`), tests that import a changed module (`import_reach`, `:680`), the test map's couplings, and the full run on anything unplaced.
- **Held by.** Code, at `gov queue` and, for hand commits on `w2/integrate`, the scratch `landing_select.sh` (TOOL-MAP rows 25, 28).
- **Breaks.**
  - Code → *tests* is traced; code → *KPI line* is not. A failing selected test names a test, not the line or the spec.
  - `allowed_paths` is typed by hand; the path map (G-8) is the open source for it.
  - Two incidents hit exactly this selection: I-1 (a deleted test read as changed, `FILE_GONE`) and I-2 (a record-only document nothing maps). Both fixed in 0.1.5 (FINDINGS).

### 1.6 The way back: test → KPI → spec, and decision → spec → ticket (`gov impact`)

- **How made.** `gov impact` walks the record graph (`store/loader.py:49` `EDGE_TYPES`; stated links from `sources`, `closes`, `links`, `parent`) and the code graph, and groups the result into specifications, decisions, tickets, tests, code (`impact/__init__.py:283`, `readings.py:18`).
- **Held by.** Nothing calls it (TOOL-MAP row 22). It ran past 150 s on a record-only id (I-5, `impact/__init__.py:135-150`). It refuses a store that is not loaded from HEAD (`:89-95`, finding I-9). T-11 (DEC-1242) decided it runs at the landing (`--changed`, into the close record), plus a use at planning "when the plan step is built".
- **Breaks.**
  - The graph's nodes are *records*. A KPI line is not a record, so the graph can say "ticket T affects spec S" but never "this test proves that line".
  - A test is a `tests` node only if a record carries a `tests:` key (48 files under `docs/` and `.tickets/` do). No acceptance README has front matter (0 of the 165 that exist, measured), so the graph does not reach the acceptance tests.
  - The trace from a changed spec K-line to the tickets and tests it touches does not exist. It could only be built on a line id (§1.0).

### 1.7 What the incidents say, in one table

| Incident | Link that failed | Evidence |
|---|---|---|
| KPI drift: tests written to a ticket that drifted from its spec | spec → ticket line | audit 4 A-23b; G-6 "nothing checks" |
| Maps unreadable by `gov accept` | ticket line → test | 67 of 189 folders; `ACCEPT_MAP_UNREADABLE`; A-12; G-2 |
| A line nothing proves | ticket line → test | 138 lines in 45 closed tickets (measured above) |
| Tests green on the base | test → base | A-3; `8a95d3873` |
| Hand-written briefs | ticket → brief | G-3; about 40 briefs; `gov brief` used 3 times |
| `gov impact` never called | everything backward | TOOL-MAP row 22; I-5; T-11 |
| Two spec forms | feature → spec | §1.1; `DISCOVER_CHANGE_NOT_FOUND` on EXAMIN |

---

## 2. How it is usually made deterministic

Sources are the helper's rows, each checked by it against the page named. **Not confirmed** is marked.

1. **One requirement id carried end to end, with traceability generated and checked.**
   - *Doorstop* stores each link as parent id plus a fingerprint of the parent, so when a parent changes, the link is "suspect" (warning `LLT005`) (https://doorstop.readthedocs.io/en/v3.1/cli/validation.html).
   - *OpenFastTrace* reads tags in code and tests (`[impl->swdd~id~1]`, `[utest->...]`) and reports statuses `orphaned`, `unwanted`, `outdated`, and deep coverage (Eclipse Ankaios' use: https://eclipse-ankaios.github.io/ankaios/0.7/development/requirement-tracing; OFT design: https://github-redirect.dependabot.com/itsallcode/openfasttrace/blob/main/doc/spec/design.md).
   - *Sphinx-needs* warns on a missing or malformed id (`needs_id_required`) and an unknown link target (https://sphinx-needs.readthedocs.io/en/stable/tutorial.html).
   - **Lesson:** the id is typed once, at the source; the trace is *generated* from tags, never kept by hand; a changed requirement turns its links "suspect". Most tools *warn*: refusal needs a flag or a custom exit code. **Not confirmed:** whether `oft trace` exits non-zero on uncovered items, and whether StrictDoc refuses on a broken link.
2. **Executable specifications.**
   - *pytest-bdd* binds Gherkin scenarios to Python with `@scenario` or `scenarios()`; a step with no definition fails at run time and `--generate-missing` prints skeleton code (https://pytest-bdd.readthedocs.io/en/latest/).
   - *Hypothesis* states a property over generated inputs.
   - Known cost: the upkeep sits in the step glue (duplication, over-detailed or UI-coupled scenarios) (third-party reports; the helper marks these as weaker sources).
   - **Lesson:** a scenario *is* the test skeleton, so "a line with no test" cannot happen; but the glue is paid for in every feature. **Not confirmed:** `behave`'s exit code for an undefined step.
3. **Typed spec records in a graph (requirements as code).**
   - *OpenSpec* (which Gov OS pins at 1.13.2): `openspec validate` needs `SHALL` or `MUST` in a requirement body (a missing one is a warning that fails under `--strict`), at least one `#### Scenario:` per requirement, delta sections ADDED / MODIFIED / REMOVED / RENAMED; a MODIFIED requirement that drops a main-spec scenario is an error, exit 1 (https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/openspec/specs/cli-validate/spec.md).
   - **OpenSpec does not link a requirement to a test or to code.**
   - *Spec Kit* (`/speckit.analyze` checks consistency of spec, plan, tasks, constitution; https://github.github.com/spec-kit/) and *Kiro* (an analyze step for gaps and ambiguity; https://kiro.dev/docs/specs/) were not confirmed to link tasks or tests to requirement ids.
   - **Lesson:** the spec side is well covered by typed forms; the *spec-to-test* link is the part these tools leave out, which is the part Gov OS needs.
4. **"Fail when a requirement has no test, or a test has no requirement."**
   - *jamb*: `@pytest.mark.requirement("UID")` with `--jamb-fail-uncovered` fails the run when a requirement has no test (https://jamb.readthedocs.io/en/latest/user-guide/pytest-integration.html). *pytest-intent* fails on untested requirements by default (a third-party page).
   - The helper found no tool that generates tests from OpenSpec or Spec Kit requirements; only pytest-bdd prints skeletons, from feature files.
   - **Lesson:** check both directions; carry the id as a test marker (a code-readable tag, not a prose map); generate the stub from the id.

**What this teaches a small tool that already has typed tickets, a map and a record graph:** (a) put the id on the line once and let code carry it; (b) check both directions, fail closed; (c) fingerprint what a link was made against, so a later edit shows as "suspect"; (d) generate stubs from ids rather than adopting Gherkin glue; (e) do not expect a spec tool to link to tests: that link is yours.

---

## 3. Three approaches for Gov OS

All three keep the golden rule: *what code can decide, code decides; what stays with an agent is a job with fixed inputs, a fixed output form and a code check.* They differ in where the trace lives.

### Approach A. Derive and check: one line id, one trace computed from the files that exist

**Idea.** Change no record type. Give a KPI line one stable name, then let one module *derive* the chain feature → spec → line → ticket → map → test → code from the files already there, and *refuse* a broken link. The trace is computed, never stored; the only thing written is a fingerprint lock (Doorstop's idea).

**What it builds.**
- `src/gov/trace/` (a library; a command `gov trace <ticket> [--check] [--base] [--changed <range>]` only if the owner approves a command):
  - `lines.py`: the ticket's lines with their id (the stable `K<n>` token, else the position as today), their verify and a fingerprint. It reuses `kpi_rows` (`brief/build.py:112`) and `discover.check.kpis` for spec K-lines.
  - `chain.py`: joins line ↔ spec K-line (by `specification:` and the `[K<n>]` id), line ↔ README map (reuses `parse_map`), map item ↔ collected test, ticket `allowed_paths` ↔ code (reuses `select._tickets`).
  - `check.py`: the refusals:
    - `TRACE_LINE_UNMAPPED`: a ticket line no test is mapped to.
    - `TRACE_MAP_PHANTOM`: a map line the ticket lacks.
    - `TRACE_TEST_UNKNOWN`: a map item no test matches.
    - `TRACE_SPEC_ORPHAN`: a spec K-line with no ticket line, or a ticket `[K<n>]` with no spec K-line.
    - `TRACE_SUSPECT`: the spec line or ticket line changed since the lock was stamped.
    - `TRACE_GREEN_ON_BASE` (with `--base`): a mapped test passes on the merge base (A-3).
    - `TRACE_NO_RED_CASE`: a line has no red case and no `guard` mark (T-3).
- A strict map form for new tickets: a table `| line | tests | red reason | guard |`, one id per cell, no prose. Old prose maps keep working through `parse_map`. The designer's brief supplies the empty table.
- Record changes: `kind: feature` and `specification:` on a ticket (R-3 and SQ-G7-5); `acceptance_tests/trace.lock` (code-written: line id, fingerprint of the line and of its spec K-line); an optional leading `K<n>` token in ticket lines (SQ-G7-2). Nothing in the store or the graph changes.
- Wiring (all of it exists as a hook point): `gov brief`'s ready check (A-23b); the queue's pre-check next to `acceptance_refusal` (A-12 and A-3); `gov accept` reports unmapped ticket lines; the queue's after-step runs `trace --changed` beside `gov impact --changed` (T-11) and writes both into the close record.

**Size: M.** About 500 lines of code and 600 of tests. The parts it reuses: the map reader (`parse_map` and its helpers, about 130 lines), `kpi_rows`, `discover.check.kpis`, `select._tickets`, `acceptance_refusal`.

**What it makes code.**
- Every join and every refusal above, at the brief, at the landing and by schedule.
- The ticket's lines when the spec has K-lines (`gov discover --ticket`, already built).
- The stub of the map (the empty strict table with one row per ticket line, and its fingerprints).
- The red-on-base check.

**What stays with agents, in a fixed form.**
- Spec K-lines (product-spec; nine-part form; `check_spec.py`).
- Ticket lines for work not started from `gov discover` (the CTO or a lead; the `{line, verify}` form, with the `K<n>` token; the new check).
- Tests (designer; strict table; `gov trace --check`).
- Code (engineer; `gov accept`).

**Friction it removes.**
- *KPI drift:* `TRACE_SPEC_ORPHAN` and `TRACE_SUSPECT`.
- *Maps unreadable by `gov accept`:* the strict table, and `--map-only` before the landing (A-12).
- *A line nothing proves* (138 lines): `TRACE_LINE_UNMAPPED`, for new tickets.
- *Tests green on the base:* `--base`.
- *Hand-written briefs:* the brief gets its lines, map table and verify from the same module, so it cannot drift from the landing's reading (G-3's "all read the same ticket fields").
- *`gov impact` never called:* the after-step calls it (T-11); `trace` is the file-based half that works when the store is stale (I-9), so the landing never depends on the store being at HEAD.

**What it costs EXAMIN at adoption.**
- Almost nothing. Six tickets, one in flight (X12), none yet with an acceptance folder (`tests/acceptance/` is empty).
- X12's lines already sit at S1 to S3, F1 to F2, equal to position, so they are already well-formed. Only the `K<n>` token and `specification:` are new; its code names stay, but move to `verify` if SQ-G7-3 is answered (a).
- EXAMIN has to pick one spec form (SQ-G7-1) before the *spec* end of the trace works. The ticket ↔ map ↔ test end works with no spec at all.

**Risks.**
- The `K<n>` token is one more convention. If agents do not use it, the check degrades to position, which is today's behaviour.
- The strict table must be easy enough for a designer to fill. A hand-made table the designer gets wrong is a refusal at the brief stage, not at the landing: cheaper, but still a refusal.
- Closed tickets need a `legacy` rule or the 45 will turn red (SQ-G7-4).

### Approach B. Scenario first: the spec is the test skeleton

**Idea.** Make the *spec* the one source and generate the rest from it: each OpenSpec Scenario (WHEN/THEN) is a KPI line; code generates the ticket's lines and a pytest stub for each scenario, tagged with the scenario's id. A test is mapped to a line by the tag, so no README map is read.

**What it builds.**
- `gov scenarios` (or inside `gov discover`):
  - A parser for the fixed OpenSpec delta form (four hashtags, `SHALL`). A small Python reader; calling `openspec show --json` would put node on every landing's path (I-6 showed the cost).
  - A stable scenario id: `<capability>/<requirement-slug>#<scenario-slug>` (SQ-G7-2).
  - A generator: ticket `kpis` from scenarios (verbatim, verify filled by the generator from the id); one pytest stub per scenario with `@pytest.mark.scenario("<id>")` and a body that fails (`pytest.fail("scenario not written")`).
  - A pytest plugin (`tests/acceptance/conftest.py`) registering the marker and writing the collected ids to the JUnit file.
  - `gov accept` rewritten to read the ticket's lines and the markers (no README map). Fail closed: a scenario with no marked test, or a marked test with no scenario.
- Record changes: a spec form decision (SQ-G7-1: OpenSpec Requirements/Scenarios *replace* the nine-part K-lines, so `check_spec.py`, `discover/check.py`, the spec-writing skill and `spec-form.md` are rewritten); `kind: feature`; ticket line ids = scenario ids; migration helper for old tickets (legacy, never rewritten).

**Size: L.** About 1,500 lines of code (parser 250, generator 300, plugin 150, accept rewrite 200, spec check and discover changes 300, migration and templates 300) and 1,000 of tests. It also changes kernel text (spec skill, templates, test-design skill), which is the CTO's with the owner's yes (CLAUDE.md, EMERGENCY-2 §3.5), and rewrites a closed feature (`gov accept`, W2-96) deeply.

**What it makes code.** The ticket's lines; the test skeleton and its id; the mapping; the "line with no test" and "test with no line" checks (both directions); the red state of an unwritten test (red by construction).

**What stays with agents.** Writing the requirements and scenarios (product-spec; the OpenSpec form with `openspec validate` plus the id grammar); filling each stub's body (designer; the stub; run red on the base); code.

**Friction it removes.**
- *KPI drift:* ticket lines are generated, so they cannot differ.
- *Unreadable maps:* there is no map.
- *Hand-written briefs:* the brief's table comes from the generator.
- *Tests green on the base:* only partly. A stub is red until filled, but a filled test can still pass vacuously on the base, so A-3 is still needed.
- *`gov impact`:* no change; still T-11.

**What it costs EXAMIN at adoption.**
- EXAMIN already writes OpenSpec deltas, so this fits its habit and matches the schema Gov OS ships. But X12's ticket (S1 to S3, F1 to F2, five lines) is cut differently from the spec's six scenarios, so its ticket would be regenerated (the lines change, the id changes).
- Every future spec is held to Requirement/Scenario with no `Fails if:`, no Test data table, no Open questions as packages, no Accepted by; those would have to move into `proposal.md` or `design.md`. That loses what DEC-959 and the spec-writing skill asked for.

**Risks.**
- It forces the spec-form decision first, and it is the biggest change to a spec form already in force.
- Scenarios make good test names but poor KPIs for performance or measured outcomes (EXAMIN's X12 `verify` is "report before/after term counts on cached inputs"); the generator would need an escape (a scenario kind `measure`).
- A plugin and markers add coupling to pytest and to a conftest in every acceptance folder; the independent runner (`gov accept` is built to leak nothing of a test's content) would need to read markers without leaking names.

### Approach C. Typed records in the graph: a KPI line becomes a node

**Idea.** Make every link an edge in the record graph that the landing and the impact trace already read. A KPI line becomes a record; its edges (`IMPLEMENTS` a spec K, `TESTS`/`VALIDATES` a test) are typed; `gov impact` becomes the one trace.

**What it builds.**
- A `kpi` record type: either one small file per line, or the loader turning a `kpis:` list in a spec's or ticket's front matter into nodes (`<ticket>:S2`). The spec gains front matter with `kpis:` (`specification.schema.json` today: "the shared frontmatter and nothing more").
- Edges from the acceptance folder to lines: a typed `trace.yaml` beside the README (line → tests), loaded as `VALIDATES` edges. This replaces the prose map for new tickets.
- Loader and store changes: `store/loader.py` (the edge types exist, `:49`), `retrieval/graph_route.py`, the digest and schema version (`:~95-110`), `rebuild`, `impact/__init__.py` (a `kpi` kind beside the five, `readings.py:18`), `gov links` (`KPI_DRIFT` from the graph), `gov plan` and `gov brief` reading the graph.
- Record changes: `kind: feature`, `specification:` required; the record schema for `kpi`; a loader refusing a dangling `IMPLEMENTS`.

**Size: L to XL.** About 1,800 lines of code and 1,200 of tests. It touches the shared core of the test map (`store/loader.py`, `check/**`, `records/**`; `test-map.yaml` `shared_core`), so every change to it runs the full regression, and it changes the store's digest and schema, so every store (Gov OS, EXAMIN, every adopted repo) is rebuilt.

**What it makes code.** All of A's checks, plus any query the graph can answer: "which tickets and lines does this decision or this spec line touch", from the landing, from planning, from memory (`gov retrieve` answers over the same nodes).

**What stays with agents.** The same jobs as A, in the same forms, plus the typed `trace.yaml` (designer).

**Friction it removes.** KPI drift, unreadable maps (typed form), the line nothing proves, hand-written briefs and `gov impact` never called: all, through one engine. Red on the base: not by itself.

**What it costs EXAMIN at adoption.**
- A `gov update`, a store rebuild and a re-measure of memory (W4: the 80-question measure at 95 %). EXAMIN's priority now is its memory measure on 0.1.5 (DEC-1238 (4), DEC-1241). A schema change to the store lands in the middle of it.
- Frontmatter on specs it does not have today.

**Risks.**
- **Staleness.** The graph answers only for a store loaded from HEAD (`impact/__init__.py:89-95`); the memory refresh failed in the field and was 23 commits behind (TOOL-MAP row 10, I-9). A landing check that must rebuild first adds the embedder and about a minute to every landing; one that reads the stale store is wrong. A files-based check (A) has neither problem.
- It models in the graph what the files already say, so every ticket edit is a graph change.
- Most of the value (§1.4's incidents) sits in the ticket ↔ map ↔ test hop, which does not need a graph.

### Side by side

| | A. Derive and check | B. Scenario first | C. Typed graph |
|---|---|---|---|
| Where the trace lives | computed from files, one lock | the spec (generated down) | the store |
| Change to forms | small: `K<n>` token, `specification:`, strict map | the spec form replaced | spec front matter, `trace.yaml`, `kpi` records |
| Size | M (~500 + 600 test lines) | L (~1,500 + 1,000) | L to XL (~1,800 + 1,200) |
| Needs the spec-form decision first | only for the spec end | yes, before anything | for the spec end |
| Depends on the store being at HEAD | no | no | yes |
| Closes "line nothing proves" | yes, for new tickets | yes (by construction) | yes |
| Closes "tests green on the base" | yes (`--base`) | partly | no |
| First value after | one slice (§4) | the whole build | the whole build |
| Kernel text changed | little (map form, brief) | much (spec skill and form) | some (schemas) |

---

## 4. Recommendation

**Approach A, built in four slices; do not start B or C now.**

**Why.**
1. The measured friction is at one hop (ticket line ↔ README map ↔ test: 67 unreadable folders, 138 unproven lines, 15 phantom lines, 37 mis-numbered prefixes) and one missing comparison (spec K-line ↔ ticket line). Both are *checks over files that exist*. This matches the owner's own guess for G-7 ("often the answer is not new machinery but a smarter way of linking what already exists").
2. A needs no decision on the spec form to start. B needs it first and rewrites a form in force. C needs a store schema change in the middle of EXAMIN's memory measure.
3. A does not depend on the store being current; the landing must work when the refresh has failed (I-9).
4. A is the half that B and C would also need (the id, the strict map, the checks). Done first, it leaves both open; B's generation can be added later as "the stub of the strict table from a scenario", and C's graph can read A's lock. Nothing in A is thrown away.

**The smallest first slice (slice 1): ticket ↔ map, new tickets only, no new command, no spec question.**
- *What.* One function, `unmapped_lines(front, mapping)`, in `gov.accept`:
  - `gov accept` adds the ticket's lines with no map entry to its answer as `outcome: fail, note: unmapped`, and lists map names the ticket lacks as `phantom`.
  - The queue's pre-check (`acceptance_refusal`, `queue/checks.py:171`) refuses `ACCEPT_LINE_UNMAPPED` and `ACCEPT_MAP_PHANTOM` before any run.
  - `gov brief`'s ready check for the test designer carries the same function and prints the table of lines to map.
- *Scope.* Only tickets created at or after the facts file's `ready.new_since`, the cut the ready check already uses (`brief/build.py:157-186`); closed tickets are exempt. No `legacy` field is needed because the cut does the job.
- *Size.* About 150 lines of code and 250 of tests.
- *Under what.* A fix, not a feature: A-12 (unreadable maps found at commit) is already a plan item and `gov accept` is W2-96's (TOOL-MAP row 54); the brief's ready check is W2-152's (row 36). No new command and no new ticket (DEC-1238 (7)); the owning-ticket choice is the CTO's. Failing test first: a planted ticket with three lines and a map with two must fail `gov accept`.
- *Proof.* On the scratch repository and in EXAMIN (DEC-1239), not on Gov OS's own landings. X12 is the first real trial: its acceptance folder does not exist yet.

**Then.**
- Slice 2: the strict map form and `--map-only`. The designer's brief supplies the table; T-3 gets its `guard` mark. Fixes the 31 + 8 + 4 unreadable maps for new tickets (G-2 handles the old folders).
- Slice 3: the spec end. `[K<n>]` token, `specification:` (with R-3's migration chore), `TRACE_SPEC_ORPHAN` and `TRACE_SUSPECT` with the lock. Needs SQ-G7-1 to SQ-G7-3 answered. This is the A-23b comparison.
- Slice 4: `--base` (A-3, red on the base) and `trace --changed` in the after-step beside `gov impact --changed` (T-11).
- Later, only if the owner wants it: B's generation of the strict table and the stubs from scenarios, for new EXAMIN features.

---

## 5. Spec questions (decision records, DEC-1238 (10))

None stops the first slice. SQ-G7-1 to SQ-G7-3 stop slice 3.

### SQ-G7-1: Which form is "the spec": the nine-part K-line form or OpenSpec Requirements and Scenarios?
- **Found.**
  - The product ships both. `check_spec.py` and `gov discover` read a nine-part `spec.md` with `K<n>` and `Fails if:` lines (`spec-form.md:6-44`). The `feature-readiness` schema and its template ask for `specs/**/*.md` deltas of Requirements and Scenarios (`schema.yaml`; `templates/spec.md`).
  - EXAMIN's real spec for X12 is the second form only. `gov discover --check x12-term-registers` answers `DISCOVER_CHANGE_NOT_FOUND`.
  - Gov OS's own work has neither: its "spec" is a Contract item with one `acceptance:` sentence plus decisions (`contract.yaml`, CAP-33).
  - The golden workflow (W7) says "the Contract (features, behaviour, KPIs) first" and does not say in which form.
- **Options.**
  - (a) Nine-part is the spec; OpenSpec deltas hold the living behaviour beside it, and a K-line names the Requirement it summarises (cost: two documents per feature; they can drift unless a check links them).
  - (b) OpenSpec only; the other eight parts move to `proposal.md` and `design.md`; a scenario is a KPI line (cost: `check_spec.py`, the skill and `discover` rewritten; the `Fails if:` and Test data rules are lost or re-homed; it is Approach B).
  - (c) Nine-part only; drop the OpenSpec delta from the schema (cost: EXAMIN's X12 spec is rewritten; `openspec validate` and archive are lost).
- **Recommendation.** (a) for now, with the K-line the only unit the trace reads; the Requirement link is a free-text `Covers:` in a K-line, not checked. Confidence: low. It is a spec-form change in force and the owner's.
- **Sources.** `spec-form.md`; `check_spec.py`; `template/openspec/schemas/feature-readiness/schema.yaml`; `discover/command.py:87-110`; `GOLDEN-WORKFLOW.md` W7; EXAMIN `openspec/changes/x12-term-registers/`.
- **Stops work.** No for slices 1 and 2; yes for slice 3 and for Approach B.

### SQ-G7-2: What is a KPI line's identity: its position, or a stable id carried in the line?
- **Found.** The ticket's lines are identified by position (`S<n>`/`F<n>` in `gov brief`; `success-N`/`failure-N` in `gov accept` and READMEs). A typed prefix exists in 479 of 2,336 lines and disagrees with the position in 37. `gov discover` writes a stable `[K<n>]` suffix. A line inserted or removed after the tests are written changes every later number silently.
- **Options.**
  - (a) A stable id as the first token of a new feature ticket's line (`K3:`), required by the schema for `kind: feature`; old tickets keep position, read as legacy (cost: one convention; the accept parser names lines by id for new tickets).
  - (b) Position forever, plus a fingerprint of the line list stamped when the tests are written (cost: no new convention; an edit shows as "suspect" but cannot say which line moved).
  - (c) Both: position as today, id optional (cost: two names for the same line, the problem we have).
- **Recommendation.** (a), with the fingerprint (b) as the drift catch. Confidence: medium.
- **Sources.** `brief/build.py:112-128`; `accept/runner.py:139`; `discover/tickets.py:107-117`; my measurement (479 / 37).
- **Stops work.** Slice 3.

### SQ-G7-3: Is a ticket's KPI line a copy of the spec's K-line, or a refinement with the same id?
- **Found.**
  - `gov discover --ticket` copies it verbatim; the code names go in `verify`.
  - EXAMIN's X12 ticket lines name code in the line itself (`keyword_strategy.generate`, `registers {patent: [...]}`, `sync_terminology`), which the spec form refuses for a KPI (`spec-form.md:46-61`).
  - So "the ticket matches its spec" is a string comparison in one world and an interpretation in the other.
- **Options.**
  - (a) Verbatim, plus `verify`, which may name code (cost: X12's three success lines are reworded; the drift check is exact).
  - (b) A refinement is allowed if it carries the id and the fingerprint of the spec line it refines; a later change of the spec line makes it suspect (cost: an agent decides what counts as a refinement; the check only says "re-read").
  - (c) No relation beyond the id (cost: A-23b stays unmet).
- **Recommendation.** (a) for new feature tickets. Confidence: medium.
- **Sources.** `discover/tickets.py:107-117`; EXAMIN `.tickets/exa-6lq4.md` (S1 to S3); `spec-form.md:46-61`; audit 4 A-23b.
- **Stops work.** Slice 3.

### SQ-G7-4: Does `gov accept` fail a ticket line that no map row names, and for which tickets?
- **Found.**
  - `gov accept` judges only the lines the README names (`runner.py:662-705`). 45 closed tickets have 138 lines (11 %) in no map (measured).
  - DEC-1242 T-3 (b) decided "at least one red case per KPI line" without saying whether an unnamed line is a fail, or for which tickets.
  - EMERGENCY-2 §4: "a new KPI line on a closed feature is a new ticket", so a closed ticket is not reopened to fill a map.
- **Options.**
  - (a) A fail for tickets created at or after `ready.new_since`; older ones exempt (cost: two regimes, one cut date).
  - (b) A fail for every ticket; the 45 closed tickets are re-mapped or marked legacy (cost: work with no value; touches closed records).
  - (c) A notice only (cost: the incident stays open for new work; unproven lines keep landing).
- **Recommendation.** (a). Confidence: high.
- **Sources.** `accept/runner.py:662-705`; `brief/build.py:157-186` (`new_since`); DEC-1242 T-3; `CLAUDE.md` (the three kinds of work).
- **Stops work.** Slice 1's brief. Answer before it is written; the default in the brief is (a).

### SQ-G7-5: Should R-3 (`kind: feature`) also require `specification:` and `acceptance_tests.path`?
- **Found.**
  - R-3 is decided: `kind: feature` required in the schema, 219 tickets migrated by a chore. It does not say whether a feature must name its spec.
  - Today the queue treats "a spec" as a non-empty ticket body (`queue/checks.py:121`). `specification:` is written only by `gov discover --ticket` and the tasks bridge, and is declared in no schema. 0 of 271 Gov OS tickets carry it; 109 have a `CAP-` id in `sources`, 252 a `DEC-` id.
  - Gov OS's features have no `spec.md` (SQ-G7-1), so the value would be a Contract item or a decision.
- **Options.**
  - (a) Require `specification: <id or path>` with the migration chore, filled from the single `CAP-` source where there is one, else `DEC-` (cost: a rule for ambiguous cases; the 162 without a CAP source need a human or `legacy`).
  - (b) Require it for new feature tickets only (cost: the old tickets stay unlinked, the chore stays small).
  - (c) Leave it out; `sources` is the link (cost: a feature can name no spec and still land).
- **Recommendation.** (b), added in R-3's migration chore as an optional field for old tickets. Confidence: medium.
- **Sources.** `queue/checks.py:106-139`; `ticket.schema.json`; DEC-1242 R-3; `DECISIONS-HELD.md` §4 SQ-3.
- **Stops work.** No. It should be answered with R-3.
