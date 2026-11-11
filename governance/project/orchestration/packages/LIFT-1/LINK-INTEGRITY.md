# LINK-INTEGRITY: link integrity as a Gov OS capability (DEC-1073 (5))

- **For:** the CTO's review, then the owner's decision. A draft: nothing is created with `tk`, no ticket is edited,
  nothing is built before the owner decides.
- **By:** product-spec, 2026-11-05.
- **Evidence:**
  - the census `docs/research/D4B-link-census.md` (`3d1c459e`, m6 at `24f06026`). Its counts are used as they stand,
    with no recount;
  - W2-92's prototype on `w2/W2-92-proto` (`06479938`): the stated links as typed edges, one bounded hop, and the
    drift script;
  - what already exists on `w2/integrate` (`3bd637f9`), read for this package;
  - a few timings, each named where it is used.
- **Draft tickets:** `LINK-INTEGRITY-tickets/W2-129-gov-links.md` and `LINK-INTEGRITY-tickets/W2-130-link-cleanup.md`.

## 0. The CTO's review (2026-11-05, night) — read with the package
The package stands, with three corrections and one note:
1. **The drift figure under DEC-1073 (2).**
   - The package uses the census's figures: 215 drifting, 87 with no hint in their own entry.
   - Under the owner's definitions (the 110 archive-"spent" listed apart; a PROPOSED decision never current), the
     prototype's drift script (`e884675b`) counts **184 drifting, 82 with no hint**.
   - With the stated links, all 184 are joined to their changer (178 to every changer).
   - W2-130's clean-up is sized on 184 and 82. The census's 215 is kept as the stated count.
2. **One gap against DEC-1073 (5)(b).** The owner asks for "a ticket, commit, KPI, test, role, skill, lesson or plan
   line that cites an id it does not link".
   - `UNLINKED_ID` covers tickets (KPI brackets) and worker commits only.
   - For tests, roles, skills, lessons and plans, only an id that does not exist is found (`UNKNOWN_ID`). These records
     have no link field today, so a mention there is not a missing link until (c) gives them one (`sources:` on lessons,
     failures and research; brackets on kernel lines).
   - Once (c) lands, `UNLINKED_ID` extends to them.
   - The owner may prefer them reported from the start, as notices on a mention with no field.
3. **"DAY.md's rule" (section 9) is superseded.** The methods are now judged by DEC-1071's rule, which is in the
   register. Nothing in force rests on the scratch file. Section 5's line still applies: a rule a decision adopts is
   written in the entry.
4. **Note:**
   - §4.6 (W2-55's `tags` at each decision record) and the D-4b row (W2-129's tests written now) begin only after the
     owner decides.
   - Nothing is built or run from this package before then.

## 1. The recommendation
1. **One read-only command, `gov links` (new ticket W2-129).** It finds six kinds of finding across the records, the
   register, the Contract, the kernel texts and the commits. Each finding names its place, the role that fixes it,
   and a one-line fix.
   - **It is never a gate.** It runs on demand. It also runs as one more family of the CTO's structural pass (R1-21),
     after each landing and each record commit, and a finding there becomes one inbox notice.
   - **It costs about 3 s** on this repository, with no model and no network.
   - **What it reuses:** the census's patterns, which W2-92's loader holds, and W2-55's two decision checks. Both are
     already built and run nowhere today.
2. **The clean-up (new ticket W2-130), right after re-pin window 4.** Two things come first: W2-92's graph links
   adopted, and W2-129 landed.
   - The graph fixes retrieval for the 215 drifting decisions without any edit.
   - The register's own text is fixed by a patch the tool prints:
     - the 87 entries with no hint first, then the rest of the 215;
     - an independent auditor checks every mark derived from free text.
   - Tickets get their missing `sources:` from the same kind of patch.
   - Commit history is listed, never rewritten.
   - The 110 "spent" decisions and the 40 PROPOSED entries go to the owner as one reconciliation list.
3. **Prevention at the source, in D-5.** The link lines in §5 go into the templates of W2-128 (TPL-1 to TPL-8,
   P1-7's proposed ticket): the front-matter keys, the trailers, and the decision lines `Under:`, `Changes:`,
   `Supersedes:` and `Changed by:`.
   - **The rule that removes most findings:** every id a ticket rests on goes in `sources:`, and a commit's
     `Implements:` comes from it.
   - **The CTO's change:** the CTO writes a decision's `Changed by:` marks in the same commit as the decision.
4. **Existing tickets that change, by text only:** W2-92 (three KPI lines: its stated links, status in the bundle,
   the drift count), W2-55 (KPI 5 becomes a notice), W2-88 (link integrity at adoption) and W2-98 (one Done-when
   line). W2-128, when it is filed, takes §5's lines. No other ticket changes (§6).
5. **The CTO uses part of it today**, before anything is built. W2-55's `gov.decisions.tags` already reports a
   decision changed without a mark (`STATUS_RELATION_UNMARKED`, 66 today on its narrower patterns). The CTO runs it
   after each decision record (§4.6).

## 2. The wider look

### 2.1 The records
- **The register:** 1,072 decisions, of which 1,065 are register entries and 7 are files. Statuses today (grep of
  the status lines): 1,014 ACCEPTED, 40 PROPOSED, 8 SUPERSEDED, 5 DONE, 1 REJECTED, 1 CONDITIONAL.
- **Tickets:** 194 in the census; `.tickets/` holds 193 today.
- **Commits:** 3,561 carry `Task:` and 2,647 carry `Implements:`.
- **The Contract:**
  - `contract.yaml` (capabilities, items, providers, sources, master rules) and `CONTRACT_v4.md`;
  - 276 generated capability pages.
- **KPIs and tests:**
  - KPI lines inside the tickets;
  - 95 acceptance folders;
  - `tests/**`;
  - `test-map.yaml`.
- **Roles and skills:** 6 kernel role files and the kernel skills, with generated copies in `.claude/` and
  `.rulesync/`.
- **Lessons and failures:** lessons in `docs/lessons/`. No failure record exists beyond the template.
- **Plans:** `docs/plan/*.md` and the W2 cards.
- **Changes and CIT-Ps:** `docs/changes/`, with the keys `decisions_carried`, `decisions_recorded` and
  `decisions_read`.
- **Checkpoints (364) and close records (226).**
- **Specs and ADRs:** `decisions:`.
- **Packages:** `orchestration/packages/**`. These are text, not records.
- **The path map:** one configuration file, with decisions cited in its comments.
- **Generated records:**
  - the capability pages;
  - MR-1 to MR-6, which take the Contract's status (D-5 row);
  - `gov context --in-force` (W2-55);
  - the backfill proposal `docs/research/W2-55-backfill.md`.
- **Hand-kept lists that restate status:** `DECISIONS-IN-FORCE.md` and `ARCHIVE-SUPERSEDED.md`.
- **Memory (the store):**
  - 2,034 records and 757 edges;
  - the `trailers` table, which retrieval does not read;
  - the lexical and semantic chunks;
  - on the prototype, the `stated_links` table.
- **Outside memory, and outside this tool:** the CTO's scratch (`.gov-runtime/scratch/orchestrator/**`: DAY.md,
  drafts, logs) and the session's own auto-memory. These are not records and are not indexed. One finding comes from
  them (§9): DEC-1070 (11) points to "DAY.md's rule on m6", a rule that lives only in an untracked scratch file.

### 2.2 The links: how each is stated, what requires it, what checks it, and whether the graph holds it
The census figures are pairs in the graph out of distinct stated pairs. "Proto" means W2-92's prototype. The
`gov links` column gives the finding codes of §4.1.

| Link | Stated as | Required by | Checked today | In the graph (census) | Proto | `gov links` |
|---|---|---|---|---|---|---|
| decision supersedes decision | register `Supersedes:`, `Replaces:`, `Withdraws:`, `Changed by: superseded by`, free text; ARCHIVE §A | DEC-866 (mark the old entry at once); DEC-825 item 4 (a part is a `Changed by` note) | W2-55 `tags` `STATUS_*` (built, runs nowhere) | 3 / 55 | SUPERSEDES for ids alone, else AMENDS | UNMARKED_CHANGE |
| decision amends decision | `Changes:`, `Changed by:`, `Amends:`, `Lifted by:`, `Corrects:`, free text | DEC-866 | W2-55 `tags` (66 findings on its patterns) | 0 / 340 | AMENDS | UNMARKED_CHANGE |
| refines, extends, settles, ratifies, confirms | register labels | nothing | nothing | 0 / 133 | not built | none (not a change) |
| decision under decision, capability or ticket | `**Under:**` | the decision-record form (recent entries) | nothing | 0 / 2,458 + 0 / 294 | UNDER | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE |
| a decision cites another (free text) | entry text | nothing | nothing | 6 / 4,987 | not built (census: wait) | none |
| a decision's own status | `**Status:**` | DEC-866 | W2-55 `tags` | 8 by status word | read | STATUS_CONFLICT |
| a decision is "spent" | ARCHIVE-SUPERSEDED §B (111 ids) | DEC-953 item 7 (a draft list) | nothing | 0 | not built | STATUS_CONFLICT |
| ticket → decision, capability (`sources:`) | front matter | ticket schema (optional key) | `validate_w2` (Wave 2 CAP ids only) | 0 / 807; 0 / 304 | CITES | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE |
| ticket `closes:` | front matter | Contract delivery | `validate_w2` contract-items-delivered | 0 / 129 | CITES | UNKNOWN_ID |
| ticket → decision named in a KPI `[DEC-n]` | the `kpis` text | R3 §B (a line carries its id) | nothing | 0 / 764 | not built | UNLINKED_ID (into `sources:`) |
| ticket → decision named in the body | text | nothing | nothing | 0 / 698 | not built | none (narrative) |
| ticket → ticket (`depends_on`, `deps`) | front matter | the ticket form | `core-graph` (dangling, cycles), `core-claims` | 440 / 440 | same | none (already checked) |
| ticket `links:`, `parent:` | front matter (tk) | nothing | nothing | 10 / 28; 0 / 6 | not built | UNKNOWN_ID |
| commit `Task:` → ticket | trailer | DEC-182 | `trailer_gate.py` (lead, queue); `traceability` (product close only, unused since 28 Oct) | no; store table only | not built | UNKNOWN_ID |
| commit `Implements:` → id | trailer | DEC-182, DEC-927 | `trailer_gate.py` (resolves in the register); `traceability` `IMPLEMENTS_UNRESOLVED` | no | not built | UNKNOWN_ID, UNLINKED_ID, NOT_IN_FORCE_AS_RULE |
| ticket ⇄ decision through one commit | derived | nothing | nothing | 0 / 1,176 (341 not in the ticket file) | not built | UNLINKED_ID |
| `Role:`, `Decided-by:` | trailer | DEC-182, DEC-861 | `trailer_gate.py` (Role) | n/a | n/a | none |
| commit message names a decision | text | nothing | `core-decision-citations` lifted (T-3) | no | no | none |
| capability (item) → provider ticket | `contract.yaml` | the Contract | `validate_w2`; W2-109 forms-agree (in progress) | 0 / 394 | not built | UNKNOWN_ID |
| capability → decision | `contract.yaml` sources | nothing | nothing | 0 / 331 | not built | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE |
| capability tree | generated pages' `depends_on` | the generator | `core-graph` | 276 / 276 | same | none |
| Contract text → decision | `CONTRACT_v4.md` | nothing | nothing | 0 / 108 | not built | NOT_IN_FORCE_AS_RULE |
| ticket → its acceptance tests | `acceptance_tests.path` | the ticket form | `gov accept` (the README map) | 0 / 173 (104 paths exist) | not built | UNKNOWN_ID (path, on in-progress and closed tickets) |
| test → decision or ticket | test text and comments | nothing | W2-55 `propagation` (superseded only) | 0 / 3,847; 0 / 2,087 | not built | UNKNOWN_ID, ENFORCES_SUPERSEDED, NOT_IN_FORCE_AS_RULE |
| test map → suite, decision | `test-map.yaml` | nothing | the selection's tests | 0 / 81; 0 / 11 | not built | UNKNOWN_ID |
| role → skill | never stated | TPL-4 S3 plans `skills:` | portability (the copies only) | n/a | n/a | UNKNOWN_ID once `skills:` exists |
| role or skill → decision, CAP, MR | kernel text | nothing | `skill_validator` (form only); `propagation` (superseded) | 0 / 87; 0 / 95 | not built | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE, ENFORCES_SUPERSEDED |
| lesson → ticket (`constrains:`) | front matter | the lesson form | nothing | 6 / 6 | same | UNKNOWN_ID |
| lesson → its source | body `**Source:**` | nothing | nothing | 0 / 4 | not built | §5: a `sources:` key |
| failure → source | no failure records | the failure template | n/a | n/a | n/a | §5: a `sources:` key |
| plan → decisions | `docs/plan/*.md` `decisions:` | nothing | nothing | 0 / 168 | CITES | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE |
| plan card → ticket, decision | `#### W2-n` cards | W2-51 | `validate_w2` wave2-tickets (ids agree) | 0 / 93; 0 / 380 | not built | none (kept by `validate_w2`) |
| path map → decision | comments | nothing | `propagation` (the path map) | 0 / 33 | not built | NOT_IN_FORCE_AS_RULE, ENFORCES_SUPERSEDED |
| checkpoint → ticket | `task:` | checkpoint schema (required) | `core-schema` (presence only) | 0 / 364 | OF_TASK | UNKNOWN_ID |
| close record → ticket, decisions | `task:`, `decisions_applied:`, `requirements_implemented:` | close schema (`task`) | `core-schema` (presence only) | 0 / 226 | OF_TASK, CITES | UNKNOWN_ID, STATUS_CONFLICT (against the ticket's status) |
| spec, ADR → decisions | `decisions:` | nothing | nothing | 0 / 129 | CITES | UNKNOWN_ID, NOT_IN_FORCE_AS_RULE |
| change record → decisions | `decisions_carried`, `decisions_recorded`, `decisions_read` | the change skill | nothing | 0 / 138 | CITES | UNKNOWN_ID |
| package → ticket, decision | text | nothing | nothing | 0 / 629; 0 / 1,400 | not built | none (narrative) |
| in-force list → decision | `DECISIONS-IN-FORCE.md` | DEC-953 item 7 | nothing | 0 / 56 | not built | STATUS_CONFLICT |
| any other indexed text → decision | 598 files | nothing | nothing | 0 / 7,426 | not built | none |

**What the table shows:**
- Of 65 link kinds, 5 are both required and checked: `depends_on`, the capability tree, `Task:`, `Implements:` and
  `Role:`. Of those 5:
  - only `depends_on` and the capability tree are in the graph;
  - the trailers are checked only by a lead's `trailer_gate.py` and by a product close nobody runs.
- The decision links carry the drift. DEC-866 requires them, and W2-55 built a check for them, yet nothing runs that
  check.

## 3. (a) The clean-up of what is here (new ticket W2-130)
Per DEC-1073 (2), the register is the authority. A PROPOSED decision is not current. The 110 "spent" decisions are a
separate reconciliation list.

| Item | Census count | Fixed automatically by W2-92's links (the prototype, once adopted) | Needs a hand or a script | Who | When |
|---|---|---|---|---|---|
| **1. Drifting decisions with no hint in their own entry** | 87 | **Retrieval:** a search reaching the decision also reaches its changer. Of the 215, 209 reach every changer (the prototype's drift script). With W2-92 S9 (§6.1), every register chunk shows its changers, which covers the 536 chunks with no hint | **The register's own text,** for grep readers (the register was reached by `grep` 188 times, R2-1) and as the authority. `gov links --propose-marks` prints a patch adding `**Changed by:** DEC-y (part)` to each entry's status line. The CTO applies it after the check, in a commit of its own, the 87 first | Script: W2-129. Applies: the CTO. Checks: an independent auditor, every free-text-derived mark (the census hand-checked 18 and found 1 wrong) and 20 labelled marks | First thing after re-pin window 4 and W2-129 |
| **2. The other drifting decisions** | 128 (215 − 87) | Same as item 1 | The same patch, for the changers their status line misses | Same as item 1 | Same commit series |
| **3. Changes stated only in ARCHIVE §A** | 13 pairs | No: the prototype reads the register only | The same patch. ARCHIVE §A is one of the tool's statement sources | Same as item 1 | Same commit series |
| **4. Whole supersessions** | 1 (DEC-140) plus the status-SUPERSEDED entries | SUPERSEDES drops it from current | `SUPERSEDED by DEC-842` on its status line (in the patch) | CTO | Same commit series |
| **5. Tickets → the decisions they cite** | 1,378 pairs in ticket files, 0 in the graph | `sources:` (807) and `closes:` (37 resolvable) become CITES | KPI-bracket ids (764 pairs) and worker commits' `Implements:` (341 pairs not in the ticket file) are missing from `sources:`. `gov links --propose-sources` prints a patch adding them, from worker commits only, never the landing commits' process ids (DEC-953, DEC-989, DEC-1050). Body mentions (698) stay narrative | CTO (tickets are the orchestrator's) | Right after item 1, one commit, before D-9 so D-9 starts from it |
| **6. Ids that name no record** | `sources:` 40 (304 − 264), `closes:` 92 (mostly list rows; a row the list file holds is not a finding), `acceptance_tests.path` 69, test-file ids 46 pairs | No | Listed per ticket and path by `gov links --all`. Fixed by judgement: tickets in D-9, tests in D-6 | CTO (tickets); test designers and engineers (tests, code) | D-6 and D-9 |
| **7. Commit trailers** | `Task:` 3,561 (3,053 resolve; 496 are `decision-record`, valid under DEC-861); `Implements:` 4,246 (4,187 resolve) | None as edges: no commit nodes (census) | **Linked through `sources:`** (item 5). The roughly 12 `Task:` and 59 `Implements:` values that resolve to nothing are listed once with the ids they should have named, as DEC-927 did for its 39. History is not rewritten | CTO | With item 5 |
| **8. Status conflicts** | 110 spent but current; 40 PROPOSED entries (13 of them stated changed); the rest uncounted (ticket against close record, the register against `DECISIONS-IN-FORCE`) | Retrieval shows each decision's status (W2-92 S9) | **One reconciliation list to the owner** (`LINK-RECONCILIATION.md`). Per id the CTO proposes one of: done, in force, superseded by, accepted or rejected, with the reason. Once the owner decides, the CTO applies W2-55's `· done` tag or the status word, and the two hand lists are made to agree with the register | CTO proposes, the owner decides once (est. 20–30 min), the CTO applies | Beside item 1. Not counted as drift until then |
| **9. Other front-matter keys** | checkpoint 364, close 226, plan 168, spec 129, change 138 | All of them (CITES, OF_TASK) | Unknown ids only (item 6) | n/a | n/a |
| **10. `Under:`** | 2,458 | All of them (UNDER) | none | n/a | n/a |
| **11. Capability ↔ provider and decision** | 394 + 349 | No. These sit in `contract.yaml`, which is not a record (census rank 5) | Unknown ids only. Not an edge kind now | product-spec, if any are found | D-5 |
| **12. Kernel texts citing a superseded or PROPOSED rule** | `propagation`: 44 places today (all paths) | No | Rewritten in W2-128 (TPL-1 S3 already removes superseded rules) for `template/**`. Code and tests in D-6 | product-spec (kernel); engineers and test designers (D-6) | D-5, D-6 |
| **13. Lessons → their source** | 4 pairs | No | A `sources:` key on each lesson | CTO | With item 5 |

**Estimate of the work:**
- the CTO's review and commits for items 1 to 5, 7 and 13: about half a day (215 marks at about 20 to 30 s each,
  plus the two patches);
- the auditor: about 1 h;
- the owner: one list.

The ticket-side judgement is folded into D-9, which edits every ticket anyway, so no ticket is edited twice by hand.

## 4. (b) The mechanism: `gov links` (new ticket W2-129)

### 4.1 What it finds
Every finding carries:
- its code;
- the ids;
- the path and line;
- the role responsible;
- a one-line fix;
- `(text)` when it comes from a free-text pattern rather than a label.

| Code | What | Where it reads | Role responsible |
|---|---|---|---|
| UNMARKED_CHANGE | A decision another entry supersedes or amends (by a register label, free text or ARCHIVE §A), whose own entry names no such changer | the register, ARCHIVE §A | orchestrator |
| UNKNOWN_ID | An id, or a path, in a typed place that names nothing that exists. The typed places: register labels (`Under:`, `Changes:` …); tickets' `sources`, `closes`, `depends_on`, `links`, `parent`, KPI brackets and `acceptance_tests.path` (in-progress and closed tickets); trailers (since the mark); `contract.yaml` providers and sources; lessons' `constrains` and `sources`; plans' `decisions`; checkpoint and close `task`; specs' and change records' keys; kernel role, skill and template brackets; test files' ids | as listed | the writer of the place (table below) |
| UNLINKED_ID | An id a ticket rests on but does not link: one named in its KPI brackets, or in a worker commit's `Implements:`, that is missing from its `sources:` | tickets, commits | orchestrator (the ticket), or the commit's lead when the id is wrong |
| STATUS_CONFLICT | Two records disagree on a status: the register against ARCHIVE §B "spent" or `DECISIONS-IN-FORCE.md`; a ticket's `status` against its close record; a generated MR record against `contract.yaml` | as listed | orchestrator (product-spec for the Contract) |
| NOT_IN_FORCE_AS_RULE | A decision whose status is PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED, named in a rule-bearing place: a ticket's `sources` or KPI bracket (open or in-progress tickets), a commit's `Implements:` (since the mark), a register `Under:`, a kernel role, skill or template line, a brief or prompt line, a path-map comment, `CONTRACT_v4.md` | as listed | the writer of the place |
| ENFORCES_SUPERSEDED | W2-55's `gov.decisions.propagation`, as built: a place that still enforces a superseded or changed decision, with no `Kept:` reason | `src/`, `tests/`, `template/`, prompts, briefs, path map, open tickets | the writer of the place |

**The role is assigned by path,** from one fixed table that every adopted repository shares:

| Path | Role |
|---|---|
| the register, `.tickets/`, plans, prompts, briefs, the path map, lessons, orchestration lists | orchestrator |
| `template/governance/kernel/**`, `docs/contract/**` | product-spec |
| `src/**` | engineer |
| `tests/**` | independent-test-designer |
| `docs/audit/**` | independent-auditor |
| `docs/research/**` | research |
| a commit | the role its `Role:` trailer names, and once landed, the ticket's lead (orchestrator) |
| anything else | orchestrator |

**Not findings:**
- body and package mentions of an id (narrative);
- free citations between decisions;
- plan cards (`validate_w2` keeps them);
- `depends_on` (`core-graph` keeps it).

**"Each finding is fixed straight away":**
- The role that finds its own finding fixes it before its next commit.
- Any other finding goes to its role in the next brief or return.
- Nothing waits for a gate.

### 4.2 Where it runs: no gate, no ceremony
- **On demand:** `gov links [--since <rev> | --all] [--json]`, by the CTO, a lead (in place of quoting
  `trailer_gate.py` alone) and the Wave 3 orchestrator.
- **In the structural pass (R1-21)** as its family `links`, after every landing (`land.py`) and after the CTO's record
  commits (`structural_pass.py <repo> HEAD~1`, which the CTO already runs then).
  - Like every family, it is a notice only, never a refusal.
  - It becomes one inbox item only when a new finding exists.
  - The CTO adds the family line to its own tool (about 5 lines) when W2-129 lands.
- **`gov check`:** no declaration in this repository for now, because the structural pass is the runner. The kernel
  declaration `link-integrity` (severity `warning`, never `hard-block`) ships to adopted repositories through W2-88,
  after a week of use here (DEC-1052 (5)). There it is the Wave 3 orchestrator's runner.
- **Not:**
  - in `gov close` or the merge queue's gates;
  - in `gov launch` or `gov claim`;
  - in a pre-commit hook (option O1);
  - in the readiness check (W2-82).

### 4.3 How it stays incremental
- **What it reads:** the whole record set each run, because that is cheap (§4.5), so a status conflict between an old
  record and a new one is still seen.
- **What it lists:** only findings touching what changed since the mark:
  - a record changed in `<rev>..HEAD`;
  - an entry a changed entry names;
  - a commit in the range.
- **The mark:** `--since <rev>` gives it. Without that, the mark is `.gov-runtime/links/mark` (the head of the last
  run, the only file the tool writes). With no mark, `--since` is required.
- **Standing findings** (those older than the mark) are counted by code and role on every run, so none is lost.
  `--all` lists them.
- **After the clean-up** the standing count should be close to 0, so `--all` and `--since` agree.

### 4.4 Its output
```
gov links: 2 new since 3bd637f9, 0 standing (records 2,041, register 1,074 entries, commits 3)
UNMARKED_CHANGE DEC-1003 <- DEC-1057 (**Changes:**) | docs/DECISION_REGISTER.md:12871 | orchestrator | add "**Changed by:** DEC-1057" to DEC-1003's status line
NOT_IN_FORCE_AS_RULE DEC-045 (PROPOSED) in sources | .tickets/DAEO-abcd.md:61 | orchestrator | decide DEC-045 or cite it in the body as proposed
```
(The lines are illustrative: the pair DEC-1003 and DEC-1057 is one of `tags`' real findings today, but the line
numbers, the ticket and the counts are made up.)

**The output form:**
- one finding a line;
- `--json` gives the same findings in gov's shared envelope;
- exit codes: 0 with no new finding, 1 with new findings, 2 when it cannot run (named).

**The two patches.** `--propose-marks` and `--propose-sources` print a `git apply` patch for UNMARKED_CHANGE and
UNLINKED_ID. The tool never writes a record.

### 4.5 Its cost on this repository (estimate, with its basis)
Measured today on the main tree at `3bd637f9`, CPython with the C YAML loader, each once:

| Part | Time |
|---|---|
| W2-55's `gov.decisions.tags` | 0.13 s |
| W2-55's `gov.decisions.propagation` (all of `src/`, `tests/`, `template/`, prompts, briefs, open tickets) | 0.94 s |
| The prototype's `register_statements` (1,069 entries, 3,040 statements) | 0.13 s |
| The front matter and id scan of all 1,004 markdown files under `.tickets/` and `docs/` | 0.61 s |
| `git log` with the trailers of 4,577 commits | 0.10 s |

- **The estimate:** about 2 s of work plus about 0.5 s of start-up, so about 3 s for `--all` and under 2 s with
  `--since`.
- **The KPI's bound:** under 10 s and under 5 s.
- **On an adopted repository of 10^4 files** (W2-88's proofs), the scan grows with its record and text files. Est.
  under 30 s for `--all`; `--since` stays small.
- **Other costs:**
  - tokens: 0;
  - GPU: none;
  - the owner's time: none in use, plus the one reconciliation list in (a).
- **Its build:** about 400 LOC with tests (W2-129). At the plan's rate (W2-66: 400 LOC in 13.1 h), about one
  lead-day.

### 4.6 Today, before anything is built
After each decision record the CTO runs:
```
PYTHONPATH=src python3 -m gov.decisions.tags | grep STATUS_RELATION
```
Its lines naming the new entry are the marks to add in the same commit.
- **Cost:** 0.13 s and no build.
- **Why it is filtered:** `TAG_MISSING` gives 1,069 lines until W2-55's backfill is accepted.
- **The rest:** `propagation`'s 44 findings wait for the clean-up.

### 4.7 Against DEC-1052's basis
1. **Does it serve memory, spec and KPI development, role separation or ticket traffic?** Memory and ticket traffic:
   an agent is led to the current rule, and a ticket links what it rests on.
2. **Without it, would ordinary work fail open or lose work?** Yes, it fails open, quietly. 215 changed decisions are
   served as current, 87 with no hint; 536 chunks carry no hint. Nothing reports a new one.
3. **Does it run only where the risk is?** Yes. It lists only what changed since the mark. It runs after landings and
   record commits, which are the only places records change, and on demand. It does not run on every commit, in the
   close or at launch.
4. **More delivery with less drift, or only records, approvals and pings?** It adds no approval and no new record (one
   runtime mark). The one inbox line appears only when a new finding exists. Its findings are fixed by the role that
   made them, and the patches do the bulk.
5. **Proven in use before it enters the product?** Yes. It runs here in the CTO's structural pass first. It reaches
   the kernel and adoption (W2-88) only after a week of use with its findings fixed within the day.

The line it states at adoption: "passes basis questions 1 to 3: memory, it fails open without it, and it runs only
on change."

## 5. (c) Prevention at the source: the lines per recording role
Each line is one imperative with its decision id (R3 §B). `{ID}`, `{IMPL}` and `{BASE}` are the generator's keys
(TPL-3). **Where they live:** the role templates of W2-128 (P1-7, TPL-1 T-2 to T-8), the ticket template (TPL-5 T-1),
the record templates (`template/governance/kernel/templates/`), and the skill each role loads (TPL-6 S3). Kernel parts
go through W2-128's CIT-P (CAP-33). They are entered in `D5-ROWS.md` as rows 10 to 17, by the CTO.

**Every role (T-0, the envelope's commit form; D5 row 10):**
- `git commit -m "{SUBJECT}" --trailer "Task: {ID}" --trailer "Role: {ROLE}" --trailer "Implements: {IMPL}"`
  - `Task:` is the ticket's id (`DAEO-…`), never a W2 id;
  - `{IMPL}` lists only ids from the ticket's `sources:`, each ACCEPTED (DEC-182, DEC-927, DEC-1073).
- An id you need that is not in `sources:` goes in your return's `discoveries`, never into `Implements:` alone
  (DEC-1073).
- Cite only ACCEPTED decisions as rules. Name a PROPOSED one as "proposed", never as the rule (DEC-1073 (2)).

**The orchestrator, the CTO (T-8 `role-cto.md`, the orchestration skill; D5 row 11):**
- A decision entry's first lines:
  - `- **Status:** ACCEPTED (owner, {DATE}, …) · **Under:** DEC-a, DEC-b`, with ids alone in `Under:`;
  - then `**Changes:** DEC-x (item n: what), DEC-y` for a change in part;
  - `**Supersedes:** DEC-x` only when the whole entry is replaced, with ids alone (DEC-866, DEC-825 item 4).
- **In the same commit**, on every entry the new one changes:
  - `**Changed by:** DEC-new (item n)` on its status line;
  - for a whole supersession, its status becomes `SUPERSEDED by DEC-new` (DEC-866).
- Then run `gov links --since HEAD~1`, or the structural pass, and fix its findings before the next commit (DEC-1073).
- The decision-record commit: `Task: decision-record`, `Implements: DEC-new`, `Role: orchestrator`,
  `Decided-by: owner (chat, {DATE})` (DEC-861).
- A rule the decision adopts is written in the entry, never only in a scratch file it points to (DEC-1073).
- Filing a ticket:
  - `sources:` holds every decision and capability its KPIs' brackets name;
  - `depends_on:` holds tickets;
  - `closes:` holds only ids the register, the Contract or the list holds (DEC-1073).
- A lesson or failure record carries `sources: [DEC-n | the failure's id]` and `constrains: [ticket ids]`.
- Status is stated once, in its own record: the register for decisions, the ticket's `status:` for tickets. A list
  that restates it is generated (`gov context --in-force`), never kept by hand (DEC-1073 (2)).

**Leads (T-7 `role-lead.md`, and the facts file's commands, TPL-2; D5 row 12):**
- Check each worker commit's `Task: {ID}` and `Implements:` against the ticket's `sources:` the moment it exists
  (DEC-927).
- Before you return, run `gov links --since {BASE}` in your worktree. Quote its first line in `evidence` (in place of
  `trailer_gate.py`'s), and name any id the ticket should cite in `discoveries` (DEC-1073).
- Your checkpoint and close records carry `task: {ID}` and `decisions_applied:` (the ids the work applied).

**Product-spec (T-3 `role-product-spec.md`, the spec-writing skill W2-98, the change skill; D5 row 13):**
- A spec or ADR carries `decisions:`. A change record carries `decisions_read:` and `decisions_carried:`.
- A kernel role, skill or template line that states a rule ends with its decision id in brackets, ACCEPTED only.
- A capability item names its provider ticket and its source decision in `contract.yaml`.

**Engineers (T-5 `role-engineer.md`; D5 row 14):**
- A code comment that cites a decision cites an ACCEPTED one.
- When that decision changes, the propagation finding names the line, and the line is fixed in the ticket that owns
  the file.

**Test designers (T-4 `role-test-designer.md`, the test-design skill; D5 row 15; D5 rows 1 and 7 stand):**
- A case revised for a ticket carries that ticket's `Task:`.
- The README map names each case by its node id and the KPI line it covers.
- `acceptance_tests.path` is the folder the cases are committed in.

**Auditors and reviewers (T-6 `role-reviewer.md`, the audit skill, `AUDITOR-common.md`; D5 row 16):**
- The audit or review record carries `task: {ID}` and `decisions:` (the ids its findings rest on).
- A finding that a superseded or PROPOSED rule is in use names both ids.

**Research (T-2 `role-research.md`, the research template, R3-12; D5 row 17):**
- The record carries `decisions:` (the decision it feeds).

**Schemas** (W2-128 TPL-5, product-spec): `sources` (an array of ids) is allowed on the lesson, failure and research
schemas, and `decisions` on research. Both are optional, so no existing record turns invalid.

**When (c) is built:** in D-5, with the templates per session kind, as the owner suggests. Until then the CTO's lines
above are used by hand. They need no build.

## 6. The tickets

### 6.1 Existing tickets that change (text for the CTO to apply after the owner decides)
**W2-92** (`DAEO-n0wb`, in progress)
- **Why:** the prototype is built under W2-92's id, but none of its KPIs states it. DEC-1073 (2) asks that retrieval
  show a decision's status.
- **Add to success:**
  - `'S7 The stated links (DEC-1072 (1), the census''s kinds 1 to 4): at rebuild the store keeps, in a table of its own outside the digest, the links the records state that no edge holds: the front-matter id keys (sources, closes, decisions, decisions_applied, decisions_carried, decisions_recorded, decisions_read, requirements_implemented) as CITES, task as OF_TASK, the register''s **Under:** as UNDER, a supersession naming ids alone as SUPERSEDES and every other supersession or amendment as AMENDS, by the census''s patterns in one function (register_statements) that gov links reads too; on this repository''s register they match the census''s statements one for one; the closure, gov dangling and every reader of edges are unchanged [DEC-1072, DEC-1073]'`
  - `'S8 One bounded hop: from what the record route or the closure reached, retrieval follows CITES, UNDER and OF_TASK out and AMENDS and SUPERSEDES in (from the changed decision to its changer), at most 12 records, after today''s closure chunks; adopted only under DEC-1071''s rule (all 80 not lower, the halves'' gap not wider) [DEC-1071, DEC-1072]'`
  - `'S9 Status in the bundle: every register chunk a bundle carries names its entry''s status word and the entries that change it; a PROPOSED, REJECTED, WITHDRAWN or SUPERSEDED decision is marked not in force, so no agent takes it as a rule [DEC-1073 (2)]'`
  - `'S10 The drift count before and after, by the census''s definitions (docs/research/W2-92-proto-drift.py on the rebuilt store): of the decisions current though stated changed, how many a search reaching the decision also reaches a changer of, in docs/research/W2-92-memory-measure.md [DEC-1072 (1)]'`
- **Add to failure:** `'A partial supersession that drops its target from what is current; a register chunk in a bundle without its status.'`
- **Add to `allowed_paths`:** `docs/research/W2-92-proto-drift.py`.
- **Add to `sources`:** DEC-1071, DEC-1072, DEC-1073.

**W2-55** (`DAEO-arrl`, merged, in progress, "land what is built", W-7)
- **Why:** DEC-1052's basis (3) and (4). The module already only prints and exits, and nothing calls it as a gate.
  This keeps it that way, so it costs no new round.
- **Amend KPI 5's opening** to: `'Supersession propagates: a check reports, as a notice naming the place and the role, run as a family of gov links and the structural pass and never a refusal of a commit, a close or a landing, anything (a test, code, …) that still enforces …'`. The rest of the KPI is unchanged.
- **Amend failure line 3** to: `'A test or check that enforces a superseded decision with no recorded reason is not reported, naming both decisions and the place.'`
- **A note on its relation check:** `tags.py`'s `STATUS_RELATION_UNMARKED` reads fewer forms than the census (66
  against 215). W2-129's UNMARKED_CHANGE replaces it in use. The duplicate check is listed for D-6's tidy-up, which
  points it at `register_statements` or removes it.

**W2-88** (`DAEO-2bdu`, open)
- **Why:** DEC-1073 (5) makes link integrity part of every adopted repository, and DEC-1072 (2) makes this ticket the
  owner of memory-building at Wave 0.
- **Add to success:** `'Link integrity at adoption (DEC-1073 (5)): after its store is built, A9 runs gov links --all on the adopted repository and writes in the memory-assessment record the census of its stated links (per kind: instances, distinct pairs, resolvable, in the graph) and the findings by code and role; the findings go to the repository''s owner as its clean-up list and are never fixed by the tool. The kernel ships the link-integrity check declaration (severity warning, never hard-block) and the adopt skill''s step only after gov links has run in this repository''s structural pass for at least a week with its new findings fixed within the day [DEC-1073, DEC-1072 (2), DEC-1052]'`
- **Add to failure:** `'A link finding that stops or refuses an adoption; a link fixed by the tool in an adopted repository.'`
- **Add to `allowed_paths`:** `template/governance/kernel/checks/link-integrity.yaml`.
- **Add to `depends_on`:** W2-129.
- **Add to `sources`:** DEC-1073, DEC-1072.

**W2-98** (`DAEO-wi46`, open)
- **Why:** product-spec records links in specs (§5).
- **Add to success:** `'Its Done when also checks the links: every decision and capability the spec rests on is in its decisions: or sources: front matter, each ACCEPTED; a PROPOSED one is an open question, never a rule [DEC-1073 (5)(c)]'`

**W2-128** (P1-7's proposed templates ticket, not yet filed)
- **Why:** (c) belongs in D-5's templates, as the owner suggests.
- **When it is filed, add:**
  - `'Links recorded at the source (DEC-1073 (5)(c)): each role template (T-2 to T-8), the ticket template (T-1) and the record templates (decision-record, lesson, research, checkpoint, failure) carry LINK-INTEGRITY.md §5''s lines for the records that role writes; verify: a string test per template, and gov links on a planted record filled from each template''s example gives no finding [DEC-1073, DEC-866, DEC-182, DEC-927]'`
  - `'The facts file''s commands hold links (gov links --since {BASE}) with its check form; the lead template''s return quotes its first line [DEC-1073, DEC-927]'`
  - `'The lesson, failure and research schemas allow sources (ids), and research decisions, both optional; every existing record stays valid [DEC-1073]'`
- **M3 (the follow rate)** covers the links lines.

**Unchanged, and why:**
- W2-115 (the smart close): no link check in the close. The structural pass runs after the landing.
- W2-45: a `warning` declaration is already YELLOW at most.
- W2-44: trailer identity is a separate concern.
- W2-109: `gov links` reads `contract.yaml`'s ids only; the forms-agree check stays W2-109's.
- W2-11 and W2-11b: they land as built. W2-128's lines replace theirs.
- W2-33: the role files get the lines through W2-128's templates (TPL-4 delivery).
- W2-06 and W2-08: no hook (O1).
- W2-82: no link check enters a readiness gate.
- `traceability.py` and `trailer_gate.py`: unchanged. They use the same resolution rule, and `trailer_gate.py`
  stays the close's gate (e).
- `validate_w2.py`: unchanged. It keeps the plan cards.

### 6.2 New tickets (full drafts in `LINK-INTEGRITY-tickets/`)
- **W2-129, `gov links`:**
  - engineer, STANDARD, est. 400 LOC;
  - independent tests first, on a planted repository;
  - depends on W2-92 (its `register_statements`) and W2-55 (its `propagation`).
- **W2-130, the clean-up:**
  - orchestrator, STANDARD (it edits the authority);
  - repository-state acceptance tests by a test designer first, an independent auditor's check, and the owner's one
    reconciliation list;
  - depends on W2-129 and W2-92.

## 7. The timing and the order
| When (the plan) | What | Who |
|---|---|---|
| **D-4b, now** | The owner decides this package. The CTO uses W2-55's `tags` at each decision record (§4.6). W2-129's acceptance tests are written: the interface is fixed here, the work is CPU only, and no GPU job is touched | CTO; test designer |
| D-4b step 7 | W2-92's prototype measured under DEC-1071's rule. The owner approves the graph change. W2-92's KPIs S7 to S10 apply | CTO, owner |
| **Re-pin window 4** | W2-92's links in the product. **W2-129 built and landed right after** (about 1 lead-day, CPU only). The CTO adds the `links` family to the structural pass | engineer; CTO |
| **Right after window 4** | **(a) W2-130:** the marks patch (the 87 first), the auditor's check, the `sources:` patch, the commit residuals listed, the reconciliation list to the owner | CTO, auditor, owner |
| **D-5** | **(c)** in W2-128's templates and D5-ROWS rows 10 to 17. The kernel texts' citations of superseded or PROPOSED rules are rewritten (TPL-1 S3) | product-spec, CTO |
| D-6 | The code and test findings (UNKNOWN_ID, ENFORCES_SUPERSEDED in `src/` and `tests/`). W2-55's duplicate relation check tidied | engineers, test designers |
| D-9 | The ticket findings that need judgement (unknown ids, `closes:`), fixed in the WBS refactor's one edit per ticket. After D-9, `gov links --all` reports 0 standing on tickets | CTO |
| **Wave 3** | The orchestrator runs it after every landing and record commit (the structural pass or `gov check`'s warning) and on demand. W2-88 ships the kernel declaration and the adoption step after a week of use | Wave 3 orchestrator; W2-88 |

**The order and its reasons:**
1. **The graph comes first** because it fixes retrieval for all 215 with no edits.
2. **Then the tool,** because it makes the clean-up's patches and proves the clean-up is done.
3. **Then the clean-up,** because the cheap mechanical part comes before the templates, so they start from a clean
   repository.
4. **Then the templates,** which stop new drift at the source.

**If W2-92's graph change is refused or delayed:**
- W2-129 takes `register_statements` into a module of its own (`src/gov/decisions/statements.py`, the census's
  patterns unchanged) and goes on.
- The clean-up's text marks still apply.
- Only the "fixed automatically" column in §3 is lost.

## 8. Options for the owner (only the real choices)
- **O1. A pre-commit warning when hooks return (W2-08):**
  - (A) **No, recommended.** Records change in a few places, all of which the structural pass already covers. A
    hook adds a step to every commit by every role (basis question 3).
  - (B) Yes, as a warning, changed files only, about 2 s a commit.
- **O2. The reconciliation list's grain:**
  - (A) **Recommended:** the owner decides the 150 ids as one list, with the CTO's proposal per id, in about 20 to
    30 min.
  - (B) The owner delegates it to the CTO, with an auditor's sample of 20, and sees only the disputed ids.

Everything else is a recommendation, not a choice.

## 9. What no source settled, and the risks
- **False findings from free text:**
  - the census's free-text patterns were 1 wrong in 18 hand checks;
  - such findings are marked `(text)`, and an auditor checks every free-text mark before it is committed;
  - the remedy for a recurring false finding is to write the link in its labelled form, never an allow-list.
- **The count after the clean-up is an expectation, not a measure.** W2-130's tests measure it.
- **The rules in scratch.** DEC-1070 (11) and DEC-1073 cite "DAY.md's rule", which lives only in
  `.gov-runtime/scratch`. Memory does not index it, and `gov links` cannot see it. §5 adds the CTO's line that such a
  rule is written into the entry.
- **The uncounted status conflicts:** ticket against close record, and the register against `DECISIONS-IN-FORCE`.
  They are counted by W2-129's first `--all` run.
- **W2-55's relation check against the census's.** Two pattern sets give 66 and 215. W2-129 uses one (S8), and D-6
  removes the other.
