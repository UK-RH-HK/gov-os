---
id: WAVE-2-WBS
type: plan
status: ACCEPTED
state_class: AUTHORITATIVE
depends_on: [CHARTER-v5, CONTRACT-v4, WAVE-1-WBS, WAVE-2-LIST]
decisions: [DEC-078, DEC-083, DEC-086, DEC-096, DEC-104, DEC-105, DEC-136, DEC-137, DEC-159, DEC-160, DEC-166, DEC-167, DEC-182, DEC-235, DEC-236, DEC-409, DEC-412, DEC-414, DEC-434, DEC-522, DEC-534, DEC-567, DEC-704, DEC-709, DEC-712, DEC-714, DEC-715, DEC-716, DEC-718, DEC-719, DEC-720, DEC-721, DEC-722, DEC-723, DEC-724, DEC-725, DEC-726, DEC-727, DEC-728, DEC-729]
---

# Wave 2 (Strengthen) — work breakdown (revision 3)

**Status: ACCEPTED by the owner, 2026-10-16 (DEC-729): revision 2 approved, with W2-50 added (DEC-728).** The owner commits this plan with DEC-719 to DEC-729 (`Role: owner`). No ticket is created and nothing starts before that commit. After it the orchestrator:
1. creates W2-00 first with `tk` in the main tree, and gives the owner its id for `GOV_TICKET` (O-3);
2. creates every other ticket the same way (the `wbs_id` and `external-ref` carry the W2 number);
3. starts W2-01.

**Sources.** Charter v5, Contract v4 (version 4.1) and its 17 Wave 2 `covers` items; DEC-718 and its consolidated list `docs/plan/WAVE_2_LIST.md` (the block AR-1 to AR-10, EXP-003's plan, and 791 open rows); the W1-43 exit audit `docs/audit/wave-1/W1-43-wave-1-exit-audit.md`; the Wave 1 WBS's Wave 2 outline (§6); the owner's planning brief of 2026-10-16; and the owner's review of the first draft, recorded as DEC-720 to DEC-727.

**Changes since the first draft (owner's review).**
- **DEC-720 to DEC-724** answer P-W2-1 to P-W2-5. Contract v4.2 is lite: CAP-44.h with A7 and A10, and CAP-43.b. Signed tags stay in Wave 3, so releases are hash-pinned (W2-16, W2-49).
- **DEC-725:** W2-13 becomes a ranked lexical route (BM25, SQLite FTS5). EXP-003 is split into W2-15a (baseline) and W2-15b (final), with bounded improvements in W2-32 between them.
- **DEC-726:** test-result caching at close is its own ticket, W2-48, in layer 2.
- **DEC-727:** EXAMIN adoption on the copy (W2-27) depends only on the safety-critical subset. The real repository (W2-29) stays gated by W2-25 and W2-15b.
- **DEC-723:** agents never write, list, glob or search `~/gov-os-workbench`.
- **Proposed:** a coordination ticket, W2-00, for the main session's identity (P-W2-6).

**Changes in revision 3 (the owner's approval).**
- **DEC-729:** P-W2-6 is answered (a). W2-00 is created first after the plan's commit.
- **DEC-728, the durable scratch root.** A new Track A ticket, W2-50, in layer 2, lets a session write under `~/gov-os-runs/<its own ticket>/` and nowhere else outside the repository. It loosens the guard, so it goes through CIT-P like W2-09.
  - Every ticket that clones into `~/gov-os-runs` depends on it: W2-14, W2-15a (and through it W2-15b), W2-24 and W2-27.
  - Until W2-50 closes, W2-26 clones into a folder under `/tmp`, and its results are committed.
  - W2-M355 moves from W2-14 to W2-50.

**Companion files.**
- `docs/plan/WAVE_2_TRIAGE.md`: every one of the 791 open rows, into a Wave 2 ticket, Wave 3 or the backlog, each with a one-line reason.
- `governance/project/prompts/w2-orchestrator.md`: the Wave 2 orchestrator prompt.
- Register §221 to §223 (DEC-719 to DEC-729), for the owner's commit.

**Ids.** Wave 2 tickets are `W2-00` to `W2-50`, with W2-15 split into `W2-15a` and `W2-15b`. Rows of the Wave 2 list keep their own ids (`W2-H001`, `W2-M001`, `W2-L001`, `W2-I001`): a letter and three digits, so the two never collide.

## 0. Rules for every ticket

Wave 1's rules carry over unchanged unless this section says otherwise: the READY rule (`tests/acceptance/<W2 id>/` exists before implementation, MR-3), no implementer path under `tests/acceptance/**`, proportional tests (DEC-221), probes (DEC-136, DEC-137), the loop policy (DEC-096), learning metrics (DEC-106), trailers in the final block (DEC-182), parallel tickets under ticket leads (DEC-235, DEC-236), and the delegation rule (MR-6).

New or changed for Wave 2:

1. **Every Wave 2 ticket in this repository closes through a clean `gov close`:** exit 0, no `--disposition`, no exception, with its close record kept (the F-M3 proof; AR-8). A `tk close` is never used, unless the owner orders it by decision; that close is then a named failure of exit criterion 1.
   - **W2-01 goes first, alone (DEC-721).** It fixes the close path (trailers base, merge form, accepted history, the probe gate after a merge-back). It is itself closed with `gov close` once merged, because `gov` runs from this repository's `src/` (an editable install).
   - The one exception to "alone" is W2-26. It is read-only on the owner's copy, writes only its own evidence and a throwaway clone under `/tmp` (rule 8), and closes after W2-07.
   - **W2-07 lands before the first close of a ticket that has no acceptance tests of its own** (research, integration, audit and coordination tickets), so that `gov close` can judge a ticket by its class (W2-H045).
   - A refused close is repaired in a new round, never worked round. Two refusals for the same reason go to the owner as a package.
2. **Branches (DEC-720).** `w2/integrate` is cut from `main` after the owner fast-forwards `main` to `wave-1-exit`. Each ticket has its worktree `~/gov-os-worktrees/<W2 id>` on branch `w2/<W2 id>`, cut from `w2/integrate`. **No commit on `w2/integrate` is ever amended or rewritten, merges included** (DEC-412, DEC-718 item 8); a correction is a new commit.
3. **Rebuilds (DEC-719).** DEC-709 is suspended while the hooks are off. A rebuild is a full `gov rebuild`, never `--no-embeddings`. Until W2-06 lands, the orchestrator runs one before each `gov close`, in the main tree, with no worker command running there.
4. **Hooks.** The lefthook hooks stay uninstalled until Track A's fixes land (W2-01, W2-02, W2-05, W2-06). W2-08 then asks the owner to reinstall them.
5. **Subagent returns (AR-6, until W2-10 and W2-11 pass).**
   - Every brief lists the twelve return fields by name: task, status, work_completed, files_changed, evidence, tests, discoveries, risks, lessons, proposed_decisions, unresolved, recommended_next_action.
   - The brief requires them first, as labelled lines, with any machine-readable payload after them.
   - It tells the helper to stop, and say so, after two identical refusals.
6. **Launches.** Until W2-21 closes, leads start in the owner's launch form (DEC-715); a blocked launch is a `LAUNCH_BLOCKED` stop to the owner. After W2-21, `gov launch lead <ticket>` and `gov launch <role> <ticket>` are the only ways in.
7. **Product repositories.** No product repository is written in Wave 2 except as DEC-727 allows: a throwaway clone of EXAMIN may be adopted (W2-27) once the safety-critical subset has closed. The real repository waits for W2-25, W2-15b and the owner's go. A product repository runs a fixed, pinned, hash-verified Gov OS release (W2-16, W2-18), never this repository's editable development copy.
8. **The workbench (DEC-723).**
   - Agents never write in `~/gov-os-workbench`, and never list, glob or search it. They name a file there explicitly, or ask the owner.
   - The owner makes the EXAMIN copy at `~/gov-os-workbench/examin/` in a plain terminal and gives its exact path.
   - Work that writes (indexing, test runs, adoption on a copy, dev-tier clones) runs on a clone the agent makes under `~/gov-os-runs/<W2 id>/`, from an exact path. Acceptance tests keep reading the dev tiers through `GOV_DEV_TIERS` by name and cloning into a temporary folder.
   - **The durable scratch root (DEC-728).** Until W2-50 closes, neither the guard nor the launcher's sandbox lets a session write in `~/gov-os-runs`. Every ticket that clones there therefore depends on W2-50.
   - The one exception is W2-26, which runs before W2-50. It clones into a folder of its own under `/tmp`, named by literal path (for example `/tmp/gov-os-W2-26/examin/`), and commits its results to `docs/research/EXP-003/examin/`. Only the throwaway clone is volatile.
9. **Machine-wide resource gate.** Several repositories' sessions will share this machine.
   - Until W2-20 closes, the orchestrator reads the gate by hand before each start: `free -g` shows at least 4 GiB available, the 1-minute load is below `nproc`, and heavy tickets count double. It counts every Gov OS session on the machine, not only its own.
   - After W2-20, `gov launch` refuses when the gate is shut.
10. **List rows.** A list row's state is re-checked against the code when its ticket picks it up (DEC-718). A row a ticket closes is marked closed in `docs/plan/WAVE_2_LIST.md` with its commit.
11. **Owner decisions (DEC-724).**
    - The orchestrator drafts and stages owner register entries; the owner commits them with `Role: owner`.
    - Owner decisions are staged in batches, with at most one owner commit per session break.
    - Once W2-12 lands, the owner commits them with `gov approve` in a plain terminal.
    - Delegated decisions are the orchestrator's, with `Role: orchestrator`.
12. **The coordination ticket W2-00 (DEC-729)** carries the main session's own records (section 2, W2-00).
13. **The finish line (§6) applies from day one,** EXP-003's two passes included (DEC-725).

## 1. Tickets

Three tracks.
- **Track A** (adoption readiness) is done first and gates the real-repository pilot.
- **Track B** (the EXAMIN pilot) starts with the profile early. It adopts a copy once the safety-critical subset has closed (DEC-727), and adopts the real repository after W2-25 and W2-15b.
- **Track C** (the rest of Wave 2) uses the slots Track A leaves free. W2-32 is in Track C but on the critical path, so it takes slot priority like a Track A ticket.

| W2 | Track | Title | Class | Role | Profile | Depends on | est. LOC | Closes |
|---|---|---|---|---|---|---|---|---|
| W2-00 | — | Wave 2 coordination: the main session's records | coordination | orchestrator | LITE | — (closes last) | 0 | F-m7, DEC-729 |
| **W2-01** | A | `gov close` and traceability: trailers base, merge form, owner-accepted history, the probe gate after a merge-back | implementation | engineer | FULL | — | 180 | AR-8 fix, AR-3 (history), DEC-704 |
| **W2-02** | A | Record types: decision entry, audit report, adoption verdict, close record; core-schema green here | schema | product-spec | STANDARD | — | 160 | AR-1 (schema), AR-3, AR-9 (schema) |
| **W2-03** | A | Decisions as records, each with its own hash | implementation | engineer | STANDARD | W2-02 | 160 | AR-1 |
| W2-04 | A | `gov context` bounded and reproducible | implementation | engineer | FULL | W2-03 | 220 | AR-1, AR-9 (ORION-gp01) |
| W2-05 | A | The git environment of every check, hook and helper; the settings re-sort | implementation | engineer | FULL | — | 140 | AR-2 |
| W2-06 | A | Fast pre-commit tier and commit-time re-index | implementation | engineer | FULL | W2-05 | 220 | AR-2 (DEC-719), CAP-17.b |
| W2-07 | A | `gov close` by ticket class; complete, tracked repair tickets; a share for every close | implementation | engineer | STANDARD | W2-01, W2-02 | 160 | AR-9 (claims), F-m8, W2-H045 |
| W2-08 | A | Hooks back on: F-M4 restated, `gov check` green here, a report commits through the hook | integration | orchestrator | STANDARD | W2-01, W2-02, W2-06 | 0 | AR-3, F-M4, F-M13 |
| W2-09 | A | `SubagentHandback` on the guard's list; the list checked against the CLI | implementation | engineer | FULL | — | 90 | AR-4, F-M7 |
| W2-10 | A | Guardrails explain themselves, refuse once, then record | implementation | engineer | FULL | W2-09 | 160 | AR-5, AR-6, F-M12 |
| W2-11 | A | Briefs and the orchestration skill: twelve fields, payload after, two-refusal stop, DEC-430 | skill | product-spec | STANDARD | W2-10 | 120 | AR-5, AR-6, F-m1 |
| W2-12 | A | Owner approval facts and `gov approve` | implementation | engineer | FULL | W2-03 | 280 | AR-7, F-M6, DEC-724 |
| **W2-13** | A | RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5) | implementation | engineer | FULL | W2-03 | 300 | AR-9 (RETR-X-02), DEC-725 |
| W2-14 | A | ARGUS's full cycle, a-dev green, the governance share per programme | integration | orchestrator | FULL | W2-04, W2-07, W2-13, W2-50 | 0 | AR-9, F-M1 |
| **W2-15a** | A | EXP-003, pass 1: the baseline | research | research | FULL | W2-03, W2-04, W2-07, W2-13, W2-50 | 100 | AR-10 (EXP-003) |
| W2-16 | A | Immutable, hash-pinned releases (CAP-43.b lite) | implementation | engineer | FULL | W2-49 | 150 | CAP-43.b (lite, DEC-722) |
| W2-17 | A | `gov update` | implementation | engineer | FULL | W2-16 | 260 | CAP-45.a, AR-10 |
| W2-18 | A | Pinned install: a product repository runs a fixed release, never the development copy | implementation | engineer | STANDARD | W2-16 | 140 | CAP-43, W2-H032, W2-H021 |
| W2-19 | A | Language-agnostic test commands | implementation | engineer | FULL | W2-07, W2-53 (DEC-757) | 300 | AR-10, DEC-534, DEC-567 |
| W2-20 | A | Machine-wide resource gate | implementation | engineer | STANDARD | — | 120 | W2-M244, W2-M188 |
| W2-21 | A | Stable launch: `gov launch lead`, the ticket-lead role, launch records | implementation | engineer | FULL | W2-20 | 220 | AR-10, DEC-715, DEC-434, W2-H001, W2-H046 |
| W2-22 | A | `gov doctor` green | implementation | engineer | STANDARD | W2-09 | 120 | F-M2 |
| W2-23 | A | Adoption safety on a real repository | implementation | engineer | FULL | W2-18 | 220 | W2-H036, W2-H035, W2-H050 |
| W2-24 | A | Track A gate run | integration | orchestrator | FULL | every other Track A ticket | 0 | AR-1 … AR-10 |
| W2-25 | A | Track A independent audit | audit | independent-auditor | FULL | W2-24 | 0 | AR block verdict |
| W2-48 | A | Test-result cache at close, keyed on exact input hashes | implementation | engineer | FULL | W2-01 | 220 | W2-H044, W2-M153, DEC-726 |
| W2-49 | A | Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) | specification | product-spec | STANDARD | W2-51 (closes after it, DEC-744) | 0 | DEC-722 |
| W2-50 | A | The durable scratch root: `~/gov-os-runs/<own ticket>/` in the guard and the launcher's sandbox (CIT-P) | implementation | engineer | FULL | W2-01 | 120 | DEC-728, W2-M355 |
| W2-51 | A | The Wave 2 plan validator (DEC-744) | implementation | engineer | STANDARD | W2-01 | 120 | exit criterion 7's two-way check |
| W2-52 | A | The lite A7 and A10 stage records (DEC-741) | implementation | engineer | FULL | W2-01, W2-49 | 100 | CAP-44.f (lite) |
| W2-53 | A | The probe gate measures every later merge against git's own merge of its parents; owner-accepted known reds, integration-side ticket edits, a load-sensitive quarantine (DEC-750, DEC-754, DEC-757) | implementation | engineer | FULL | W2-01 | 160 | DEC-750 item 2, DEC-757 |
| W2-26 | B | EXAMIN profile on the owner's copy (EXP-003's EXAMIN leg) | research | research | STANDARD | the owner's copy (DEC-723); a `/tmp` clone until W2-50 (DEC-728) | 60 | EXP-003 (EXAMIN), W2-I041 |
| W2-27 | B | EXAMIN adoption on a copy | integration | orchestrator | FULL | the DEC-727 subset, W2-26, W2-49, W2-50, W2-19 (DEC-736), W2-52 (DEC-741) | 0 | Track B |
| W2-28 | B | Independent verdict on the copy | audit | independent-auditor | FULL | W2-27 | 0 | Track B |
| **W2-15b** | B | EXP-003, pass 2: the final measurement against 99 % | research | research | FULL | W2-15a, W2-32, W2-26 | 60 | AR-10, exit criterion 4 |
| **W2-29** | B | EXAMIN adoption on the real repository | integration | orchestrator | FULL | W2-28, W2-25, W2-15b | 0 | Track B |
| **W2-30** | B | Healthy-adoption verdict on the real repository | audit | independent-auditor | FULL | W2-29 | 0 | CAP-44.h (lite) |
| W2-31 | C | Budget gates | implementation | engineer | FULL | W2-07 | 200 | CAP-04.a, CAP-04.d |
| **W2-32** | C | Retrieval components and bounded improvements: model pin, swap by configuration, learning loop; ranked-lexical tuning, chunking, the hit@5 85 row | implementation | engineer | STANDARD | W2-15a | 320 | CAP-10.b, CAP-19.a, CAP-19.c, DEC-725 |
| W2-33 | C | Wave 2 roles and typed handoff records | role-definition | product-spec | STANDARD | W2-21 | 260 | CAP-22.b, CAP-22.c |
| W2-34 | C | `gov readiness --generate` | implementation | engineer | STANDARD | W2-03 | 180 | CAP-30.c, MR-2 |
| W2-35 | C | The UX readiness row: approved wireframes, visual checks | implementation | engineer | STANDARD | W2-33, W2-34 | 150 | CAP-30.g, DEC-104 |
| W2-36 | C | `gov discover` | implementation | engineer | STANDARD | W2-34 | 160 | CAP-32.d, DEC-166 |
| W2-37 | C | `gov impact` | implementation | engineer | FULL | W2-03 | 280 | CAP-33.b, CAP-33.g, DEC-167 |
| W2-38 | C | Profile from impact; impact-selected tests at close | implementation | engineer | FULL | W2-37, W2-41, W2-48 | 150 | CAP-53.b, W2-H043 |
| W2-39 | C | Model and provider switch reconstructs the same inputs | implementation | engineer | STANDARD | W2-04 | 80 | CAP-37.e |
| W2-40 | C | EXP-002: the untested sandbox cases and the harness's hook limits | research | research | FULL | W2-21 | 60 | CAP-61.f, W2-H052 |
| W2-41 | C | Close and escalation integrity | implementation | engineer | FULL | W2-19 | 160 | W2-H022 … W2-H025, W2-H033 |
| W2-42 | C | Guard: missing role, links, late paths, atomic saves | implementation | engineer | FULL | W2-10 | 180 | W2-H006, H007, H009, H010, H011, H013, H031 |
| W2-43 | C | CI integrity and the secret-rule floor | implementation | engineer | STANDARD | W2-08 | 140 | W2-H002, H008, H014, H027, H028 |
| W2-44 | C | Trailers bound to the launch identity | implementation | engineer | FULL | W2-21 | 160 | W2-H019 |
| W2-45 | C | `gov check` runner semantics and scale | implementation | engineer | STANDARD | W2-08 | 160 | W2-H018 |
| **W2-46** | C | Wave 2 exit run | integration | orchestrator | FULL | every ticket above | 0 | Exit criteria |
| **W2-47** | C | Wave 2 exit audit, with the audit→repair loop's tests | audit | independent-auditor | FULL | W2-46 | 0 | Exit audit, F-M10 |

Bold rows are on the critical path (§3).

**Totals:** **51 tickets** plus the coordination ticket W2-00:
- Track A: 28 tickets, ≈ 4,100 est. LOC.
- Track B: 6 tickets, ≈ 120.
- Track C: 17 tickets, ≈ 2,640.
- Altogether ≈ 6,860 est. LOC.

**The Contract's 17 Wave 2 items, by ticket.**
- CAP-04.a and CAP-04.d → W2-31.
- CAP-10.b, CAP-19.a and CAP-19.c → W2-32.
- CAP-17.b → W2-06.
- CAP-22.b and CAP-22.c → W2-33.
- CAP-30.c → W2-34.
- CAP-30.g → W2-35.
- CAP-32.d → W2-36.
- CAP-33.b and CAP-33.g → W2-37.
- CAP-37.e → W2-39.
- CAP-45.a → W2-17.
- CAP-53.b → W2-38.
- CAP-61.f → W2-40.

Two of the 17 (CAP-17.b, CAP-45.a) sit in Track A because the adoption-readiness block needs them.

**Contract v4.2 adds, lite (DEC-722):** CAP-44.h with the A7 and A10 gates of CAP-44.f (W2-49, W2-02, W2-27 to W2-30), and CAP-43.b (W2-49, W2-16). CAP-02.c stays in Wave 3.

**The 53 high rows.** 47 are in Wave 2 tickets. 6 go to Wave 3 with reasons:
- H004, H016, H017 and H030: held-out and oracle hardening before qualification.
- H003 and H005: opaque Bash in the unsandboxed orchestrator session.

See `docs/plan/WAVE_2_TRIAGE.md`.

## 2. Ticket cards

Each card gives:
- the profile and the allowed paths;
- the KPI lines, success and failure, each ending with the ids it closes in brackets;
- the main list rows it takes in. The full set of rows per ticket, including the lesser rows inside its paths, is in `docs/plan/WAVE_2_TRIAGE.md`.

Every ticket's acceptance tests are at `tests/acceptance/<W2 id>/`, written by a fresh independent test designer before implementation. Every implementation ticket's builder tests go under `tests/unit/<module>/`.

#### W2-00 Wave 2 coordination (LITE, orchestrator; DEC-729)
- **Why:** the main session records under DAEO-6cc2, the closed W1-45 ticket (F-m7). Its own records need a live ticket of their own: bootstrap notes, list and triage updates, ticket creation, checkpoints, and delegated decisions.
- **How:**
  - Straight after the owner's commit of the plan, the orchestrator creates W2-00 with `tk`, before any other ticket, in the main tree, and gives the owner its `tk` id.
  - The owner sets `GOV_TICKET` to that id in the env block of `.claude/settings.local.json` (owner act O-3), and the session restarts.
  - Merges into `w2/integrate` keep the merged ticket's `Task:`. Delegated decisions keep `Task: decision-record`.
- **Allowed paths:** `.tickets/**` (through `tk`), `governance/project/bootstrap.md`, `docs/plan/WAVE_2_LIST.md`, `docs/plan/WAVE_2_TRIAGE.md`, `docs/plan/WAVE_2_WBS.md` (status lines), `docs/DECISION_REGISTER.md` (delegated entries only), `.gov-runtime/scratch/orchestrator/**`.
- **KPIs:** every main-session commit in Wave 2 that belongs to no ticket carries W2-00's id; `echo "$GOV_TICKET"` in the main session names W2-00; W2-00 closes last, with `gov close` as a coordination ticket after the owner's exit decision (its evidence is the exit report), and its close record is appended to the exit report.

### Track A — adoption readiness

#### W2-01 `gov close` and traceability: trailers base, merge form, owner-accepted history, the probe gate after a merge-back (FULL, engineer)
- **Why first:** every later ticket must close cleanly (exit criterion 1); W1-42 met 22 close findings, 15 of them trailer findings on history and merge commits.
- **Allowed paths:** `src/gov/close/**`, `template/governance/kernel/checks/product-traceability-trailers.yaml`, `tests/unit/close/**`.
- **KPIs, success:**
  - `gov close`'s own trailer gate reads the project's `trailers_base` and does not judge commits before it [DEC-704, W2-M238, W2-M250].
  - A merge of the integration branch into a ticket branch in DEC-436's merge form (`Task:` and `Role:`) passes the trailer gate [W2-M165].
  - History commits that an ACCEPTED owner decision names are accepted history. They are listed in the close and check output as accepted, with the decision id. They fail neither `gov close` nor the product-traceability check of a later commit [AR-3, W2-M147, W2-L235].
  - A ticket branch probed, then merged with the integration branch and merged back, passes the probe gate when the probed code is unchanged [W2-H047, W2-M202].
  - A reopened FULL ticket with an earlier-round probe record and a passing later one passes the probe gate [W2-M209, W2-L111].
  - The ticket-creating commit and clone path maps without a trailers base are judged as the base rule says, and the output names the base used [W2-M251, W2-M266].
- **KPIs, failure:**
  - A commit after the base without `Task:`, `Role:` or `Implements:` still refuses.
  - A merge that adds its own change outside the merged side still refuses.
  - A hand-resolved merge that changes probed code still refuses the probe gate, for the cases its acceptance suite holds: a hand-resolved inward merge; a merge-back that changes, drops or replaces probed code, whatever task it names; and a later merge holding the probed commit that rewrites or removes probed code present in both parents. A later merge measured against git's own merge of its parents is W2-53's (DEC-754).
  - An accepted-history entry without an ACCEPTED owner decision is refused.

#### W2-02 Record types: decision entry, audit report, adoption verdict, close record (STANDARD, product-spec)
- **Allowed paths:** `template/governance/kernel/schemas/**`, `schemas/**`, `template/governance/kernel/templates/decision-record.md`, `src/gov/check/schema.py` (the type map only), `tests/unit/check/test_schema*`.
- **KPIs, success:**
  - The kernel schemas define these types [AR-1, AR-3, W2-M316, W2-M317, AR-9]:
    - a decision entry: one register entry, with id, status, owner, date and its own span;
    - an audit report in DEC-441's form;
    - an adoption verdict: the three CAP-44.h verdicts and the conditions behind them, in the lite form Contract v4.2 states. Read as (DEC-741, I (ii)): the three values, and a list of named conditions, each with its source item and its state (met, not met, accepted by an owner entry); W2-02 closes on its own;
    - the `close` record type that `gov close` writes.
  - core-schema reads `docs/audit/wave-1/W1-43-wave-1-exit-audit.md` and the exit report as valid, and is green on this repository [F-M13, W2-M301, W2-M309, W2-M310, W2-L243].
  - A type with no schema file is reported unmeasured, not green [W2-M260, W2-L177].
- **KPIs, failure:** an audit report missing its milestone or pack hash is invalid [W2-M138]; a record with an unknown type is still `SCHEMA_INVALID_TYPE`.

#### W2-03 Decisions as records, each with its own hash (STANDARD, engineer)
- **Allowed paths:** `src/gov/store/**`, `src/gov/records/**`, `src/gov/decisions/**`, `src/gov/check/citations.py`, `tests/unit/store/**`, `tests/unit/records/**`, `tests/unit/decisions/**`.
- **KPIs, success:**
  - The store loads each `### DEC-nnn` entry of the register as a record of its own, with its own sha256 over its own span; two decisions never share a hash [AR-1, F-M5].
  - A decision id resolves to its entry, not to the register [AR-1].
  - A register heading alone, or any Markdown file with a decision id in its frontmatter, is not a decision record [W2-L221, W2-M267, W2-M145].
  - Decision status and id comparisons follow the schema's grammar, case included [W2-M106, W2-L069].
- **KPIs, failure:** an edited entry changes only its own hash; a duplicate DEC id is refused with both locations.

#### W2-04 `gov context` bounded and reproducible (FULL, engineer)
- **Allowed paths:** `src/gov/context/**`, `src/gov/retrieval/supplementary*`, `tests/unit/context/**`.
- **KPIs, success:**
  - `gov context <ticket>` holds the packet ceiling (≈ 6k tokens, Contract envelope) and never drops the ticket's own text [AR-1, CAP-15.d].
  - When the mandatory inputs alone exceed the ceiling, it refuses with a named error and a non-zero exit; it never reports `ok: true` over its budget [AR-1, F-M5].
  - Each decision in the packet is named by its own hash (from W2-03) [AR-1].
  - Two builds of one ticket's context, on stores rebuilt from one commit, give the same packet hash with or without a live semantic index. Ties in the supplementary block are ordered deterministically [AR-9, W2-M294, W2-M239, W2-M330].
  - An unreadable mandatory record blocks the context or is marked not read; it is never shown as read with an empty hash [W2-H034, W2-M215].
  - The supplementary query is built from the ticket's KPIs and title, not the first long word [W2-M126].
- **KPIs, failure:** DAEO-03pw's context (814,821 tokens at the audit) refuses or fits; a RETIRED or REJECTED record does not satisfy a mandatory source.

#### W2-05 The git environment of every check, hook and helper; the settings re-sort (FULL, engineer)
- **Allowed paths:**
  - `src/gov/**/*.py`, limited to calls that start git. The sweep is the ticket's first deliverable and names each file before it is changed.
  - `src/gov/util/gitenv.py` (new), `lefthook.yml`, `template/lefthook.yml`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`.
- **KPIs, success:**
  - Every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables. One helper does it, and the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160].
  - A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case) [AR-2].
  - `lefthook install` and `uninstall` leave `.claude/settings.json` byte-identical to the committed file, and adapter-portability stays green [AR-2].
- **KPIs, failure:** a planted `GIT_DIR` or `GIT_INDEX_FILE` in a hook's environment reaches no child git call.

#### W2-06 Fast pre-commit tier and commit-time re-index (FULL, engineer)
- **Allowed paths:** `src/gov/ci/**`, `src/gov/rebuild/**`, `src/gov/retrieval/index*`, `template/governance/kernel/checks/index-freshness.yaml`, `template/governance/kernel/checks/recovery-rebuild.yaml`, `template/governance/kernel/checks/secrets-indexing.yaml`, `lefthook.yml`, `template/lefthook.yml`, `tests/unit/ci/**`, `tests/unit/rebuild/**`.
- **KPIs, success:**
  - After any commit, the lexical (ranked and exact) and semantic indexes match the committed tree without a rebuild by hand, and index-freshness is green [CAP-17.b, W2-H041, W2-M011, W2-M293].
  - A merge commit triggers the same re-index (`post-merge`) [W2-M295].
  - The pre-commit tier holds only fast checks and finishes in under 60 s on this repository. Index-freshness and recovery-rebuild run at pre-push (G3) or in CI [W2-H039, W2-H040, W2-M210, W2-M282].
  - The staged-secrets scan reads only the staged files [W2-M243, W2-M143].
  - A re-index never empties the semantic index; a model-less re-index reports the semantic facet unavailable instead [DEC-719].
- **KPIs, failure:** a re-index that fails leaves the previous index and reports the failure; it never leaves no index [W2-M088].

#### W2-07 `gov close` by ticket class; complete, tracked repair tickets; a share for every close (STANDARD, engineer)
- **Allowed paths:** `src/gov/close/**` (except `src/gov/close/cache*`, W2-48's), `src/gov/telemetry/**`, `tests/unit/close/**`, `tests/unit/telemetry/**`.
- **KPIs, success:**
  - `gov close` judges a ticket by its class [W2-H045]:
    - an implementation ticket on its acceptance tests;
    - a specification ticket on its closed readiness record and its acceptance tests;
    - an audit ticket on its report and the audit validator;
    - a research ticket on its evidence record;
    - an integration or coordination ticket on its named evidence files.
  - A refused close writes a complete repair ticket (role, allowed paths, KPIs) that stays tracked in `.tickets/` [F-m8, W2-L209, W2-L236, AR-9].
  - The close record carries the measured governance share [W2-M166, W2-M286].
  - Adoption-gap and baseline refusals do not count toward the escalation counter; a repeated identical refusal reuses its repair ticket [W2-H038, W2-M249, W2-M252].
  - An interrupted close leaves nothing that blocks the next close [W2-M158].
- **KPIs, failure:** a research ticket without an evidence record refuses; an audit ticket whose report fails the validator refuses.

#### W2-08 Hooks back on (STANDARD, orchestrator, with the independent test designer)
- **Allowed paths:** `docs/plan/wave-2/hooks-back-on/**` (evidence), `tests/acceptance/W1-40/**` (test designer only).
- **Steps and KPIs:**
  - The independent test designer restates `test_no_lefthook_hook_is_installed_in_this_repository` so that installed hooks are the expected state. This is a rewrite after implementation, with its reason [F-M4, MR-3, DEC-136].
  - The owner reinstalls the hooks (an owner act). The orchestrator asks; the operator restores `.claude/settings.json` only if W2-05 did not fix the re-sort [AR-3, W2-M013].
  - A commit of a report in DEC-441's form passes the pre-commit hook, straight after staging, with no hand rebuild [AR-3, F-M13].
  - `gov check` on this repository: 17 of 17 families, no RED, no unexplained YELLOW [W2-H020, W2-L106, W2-L335, W2-M142, W2-L017].
  - DEC-709 is retired by a register entry (DEC-719 item 4).
- **Failure:** any hook refusal is reported to the owner and never worked round.

#### W2-09 `SubagentHandback` on the guard's list; the list checked against the CLI (FULL, engineer)
- **Allowed paths:** `src/gov/guard/**`, `src/gov/doctor/tools_list*`, `tests/unit/guard/**`, `tests/unit/doctor/**`, `docs/changes/W2-09-CIT-P.md`.
- **Route:** the guard change goes through CIT-P with owner approval (CAP-33). The lead returns the proposal as a package before the engineer starts.
- **KPIs, success:**
  - `SubagentHandback` is on the guard's known list with its reason; a helper's return is handed back under the guard [AR-4, F-M7].
  - `gov doctor` compares the guard's known list with the installed CLI's tool list at every CLI version change, and names each difference [AR-4, W2-M236].
  - The read-only tools the owner lists (for example Monitor and read-only MCP tools) are judged, not refused as unknown [W2-M016, W2-I015].
- **KPIs, failure:** an unknown tool is still refused by default (DEC-685); a tool on the list with a write effect is judged like Bash.

#### W2-10 Guardrails explain themselves, refuse once, then record (FULL, engineer)
- **Allowed paths:** `src/gov/guard/**`, `src/gov/hooks/**`, `template/governance/kernel/hooks/**`, `tests/unit/guard/**`, `tests/unit/hooks/**`.
- **KPIs, success:**
  - The SubagentStop and Stop hooks name the missing fields and the expected form in their refusal text, on standard error, where Claude Code shows it to the agent [AR-6.1].
  - They block at most once: with `stop_hook_active` set, they let the agent stop and record a "return without the contract fields" finding [AR-6.2].
  - The rule text says where a machine-readable payload goes: after the twelve fields [AR-6.3].
  - Every guard refusal says it is final for that call [AR-5, F-M12].
  - A loop counter records identical refused calls; the third identical refusal in a session writes a finding [AR-5].
  - An exception inside a stop hook lets the agent stop and records the exception; it does not exit 2 silently [AR-6, W2-M049, W2-M280].
- **KPIs, failure:** a helper briefed for JSON lines only is refused once, with the missing fields named, then stops with a recorded finding (the AR-6 case).

#### W2-11 Briefs and the orchestration skill (STANDARD, product-spec)
- **Allowed paths:** `template/governance/kernel/templates/brief-*.md`, `template/governance/kernel/skills/orchestration/**`, `template/governance/kernel/skills/audit/**`, `.claude/skills/orchestration/**` and `.claude/skills/audit/**` (generated, through the adapter), `docs/changes/W2-11-CIT-P.md`.
- **Route:** a kernel skill change: CIT-P, independent review, owner approval (CAP-33).
- **KPIs, success:**
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry the workbench rule (DEC-723) and the owner-approval rule (DEC-724).
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
- **KPIs, failure:** the skill validator refuses a brief without the twelve-field rule.

#### W2-12 Owner approval facts and `gov approve` (FULL, engineer)
- **Allowed paths:** `src/gov/decisions/**`, `src/gov/approve/**` (new), `src/gov/check/authority.py`, `template/governance/kernel/checks/core-authority.yaml`, `tests/unit/decisions/**`, `tests/unit/approve/**`, `tests/unit/check/test_authority*`.
- **KPIs, success:**
  - **`gov approve`** [DEC-724]:
    - It is run by the owner in a plain terminal. It shows the staged register entries (ids and titles), asks for a typed one-time code, and commits exactly those entries, with the files staged beside them, with `Role: owner`.
    - It refuses, with a named reason and nothing committed, when it is run with a Claude Code ancestor process, with a launched session's identity (`GOV_ROLE` or `GOV_TICKET` set), or without an interactive terminal. This is the freeze lift's test (DEC-409).
    - It refuses when nothing is staged, or when a staged entry is not an owner entry.
  - A register entry reads as the owner's only when the commit that sets it ACCEPTED carries `Role: owner` and was made by `gov approve`, or by the owner's own commit before W2-12 (or, once the owner chooses signatures, has a valid owner signature). Otherwise core-authority names it "transcribed" [AR-7, F-M6, W2-M258, W2-M108].
  - A decision set ACTIVE without an owner approval fact turns core-authority red [W2-H049, W2-M227, W2-M257].
  - "The decision checker could not run" is a finding, never green [W2-H037, W2-H048].
  - Body edits that keep an approved decision ACTIVE are flagged [W2-L010]. An author date earlier than the committer date by more than a day is flagged [W2-M107].
- **KPIs, failure:**
  - `gov approve` run from an agent's Bash call, piped input included, commits nothing.
  - A `Role: owner` trailer on a commit made inside an agent's call is a containment finding, not an approval.

#### W2-13 RETR-X-02 and a ranked lexical route (BM25, SQLite FTS5) (FULL, engineer)
- **Needs first:** the owner's ruling on RETR-X-02 (queued Q-1).
- **Allowed paths:** `src/gov/retrieve/**`, `src/gov/retrieval/lexical*`, `src/gov/retrieval/fusion*`, `src/gov/rebuild/lexical*`, `tests/unit/retrieve/**`, `tests/unit/retrieval/**`.
- **KPIs, success:**
  - **The ranked lexical route.** The lexical index is an SQLite FTS5 table over the same parents and spans as today, built by `gov rebuild` (and, after W2-06, by the commit-time re-index). A plain-word question returns hits ranked by BM25, with field weights for id, title and body. An exact identifier still ranks first: the exact-match route is kept as a boost, not replaced [DEC-725, W2-M102, W2-L233, W2-M292, W2-M072, W2-M100].
  - The fusion receives a ranked lexical list beside the semantic one, so that lexical, semantic and the reranker each contribute. The dev queryset's lexical-only hit@5 is recorded in the ticket's evidence [DEC-725].
  - Lexical search returns "unavailable" instead of raising [W2-M071]. Retrieval latency stays within the retrieve budget on the dev tiers.
  - A question about an id that exists nowhere stops with a named reason and no unrelated items, or shows a named parent expansion, as the owner rules [AR-9, W2-M296].
- **KPIs, failure:**
  - RETR-A-04's bundle is unchanged (citations, three parent expansions, stopping reason).
  - The secrets filter applies to the FTS5 table as to the old index: a planted canary is never indexed.

#### W2-14 ARGUS's full cycle, a-dev green, the governance share per programme (FULL, orchestrator)
- **Allowed paths:** `docs/plan/wave-2/argus-cycle/**` (evidence); the dev-tier clones under `~/gov-os-runs/W2-14/`, made from the dev tiers by exact path (never `/tmp`, W2-M355; never the workbench, DEC-723).
- **KPIs:**
  - b-dev is adopted far enough that its store holds the ticket's sources. ARGUS's implementation ticket closes with `gov close` at exit 0, then `gov ci` and the owner's merge after green CI; each is kept as evidence [AR-9, W2-L018].
  - b-dev's canaries run and hit [AR-9].
  - On a store freshly rebuilt with embeddings, a-dev's `gov check` is green on context reproducibility, claims and schema [AR-9].
  - `governance-share.json` holds a measured share for ORION and for ARGUS, each ≤ 15 %, from the counter after clean closes, with every part measured. W1-42's share case is green [F-M1, W2-H053, W2-L324].
  - ORION's `test_exact_agreement` is green, or named with its owner [W2-L341].
- **Failure:** any clone held under `/tmp` or the workbench; a programme merge made by a lead.

#### W2-15a EXP-003, pass 1: the baseline (FULL, research)
- **Needs first:** the owner's approval of the metric (queued Q-2), recorded before the first run. The same metric serves both passes.
- **Allowed paths:** `docs/research/EXP-003/**`, `experiments/EXP-003/**`; working copies under `~/gov-os-runs/W2-15a/`, cloned by exact path.
- **KPIs:**
  - **The metric is defined and recorded before the first run** [AR-10]:
    - what counts as a hit;
    - how the needed evidence for each question is labelled (by whom, blind to the system's answers);
    - per-question recall of needed evidence in the stacked context;
    - the corpus mean, against the owner's goal of 99 %.
  - **Corpora:** the dev tiers; `~/workspace` read-only; EXAMIN through this ticket's own clone of the owner's copy. W2-26's clone sits under `/tmp` and may be gone.
  - **Five modes compared:** lexical only (now ranked), semantic only, fused, fused plus reranker, and the lighter-reranker spike (DEC-074 Q3) [W2-L329].
  - **Indexing** time, peak RSS and incremental update per corpus, against DEC-078's envelope [W2-L102, W2-L321].
  - **The stacking test** (a question needing about 24k tokens, retrieved in 8k batches, assembled complete, no duplicates by span hash), run once as a baseline [AR-10].
  - Decision-level retrieval after W2-03 [AR-10]. The thin-margin cases and the two dev queries without gold paths are fixed or named [W2-M342, W2-L322, W2-M340].
- **Closes when:** the evidence record holds every measure per corpus and mode, with commands, versions and raw answers kept, and names the gaps that W2-32 will work on (at most three, chosen with the owner's approval of the metric).

#### W2-15b EXP-003, pass 2: the final measurement against 99 % (FULL, research)
- **Allowed paths:** as W2-15a, with working copies under `~/gov-os-runs/W2-15b/`.
- **KPIs:**
  - The same metric, corpora and modes as W2-15a, re-run after W2-32's bounded improvements. Each figure is shown beside its baseline [AR-10].
  - The corpus mean per corpus and mode against the owner's 99 % goal, with every miss classified (labelling, chunking, ranking, coverage).
  - **The stacking test**, final: complete and no duplicates, or each gap named [AR-10].
  - **The scale probe:** EXAMIN's clone and `~/workspace` against DEC-078's envelope (≈ 80k nodes, 270k edges, ≈ 2.2 GB peak RSS), including the brute-force vector scan and the graph cache [W2-M351, W2-L317, W2-L320, W2-M089].
  - CAP-10's hit@5 against 85, per class beside the single-class figure, for the owner's CAP-10 package (Q-10) [W2-M017, F-m2].
- **Under the finish line (DEC-725):** one run plus its probe; what is short of 99 % becomes a named residual with its cause, and goes to the owner.
- **Gates:** W2-29 (DEC-727).

#### W2-16 Immutable, hash-pinned releases (CAP-43.b lite) (FULL, engineer)
- **Needs first:** W2-49 (Contract v4.2).
- **Allowed paths:** `src/gov/lock/**`, `src/gov/release/**` (new), `copier.yml`, `template/framework.lock*`, `tests/unit/lock/**`, `tests/unit/release/**`, `docs/releases/**`.
- **KPIs, success:**
  - `gov release <version>` builds a release from a clean `w2/integrate` commit [CAP-43.b lite]. Its manifest holds:
    - the semantic version and the commit;
    - every shipped file with its sha256;
    - the wheel hash, the CLI version and the schema versions;
    - release notes;
    - the manifest's own hash.
  - The owner tags the release commit (agents never tag); the tag is not signed (CAP-02.c stays in Wave 3, DEC-722).
  - A release is immutable: building the same version from another commit, or changing a file after release, is refused [CAP-43].
  - `framework.lock` records the release version and manifest hash, at copy as well as at update. A missing lock fails, and a project cannot silence the lock comparison [W2-L227, W2-H029 (the silencing part), W2-M174, W2-M175].
  - The vendored skills carry their licence and version in the release [W2-L002, W2-L014].
- **KPIs, failure:** a release whose files or manifest do not match their hashes is refused by `gov install`, `gov update` and `gov doctor`.

#### W2-17 `gov update` (FULL, engineer)
- **Allowed paths:** `src/gov/update/**` (new), `src/gov/adapters/**` (regeneration only), `tests/unit/update/**`.
- **KPIs, success:**
  - `gov update --check` reports the installed and target versions, the migrations and their impact.
  - The update [CAP-45.a, W2-M176]:
    - verifies the target release's manifest and file hashes;
    - applies the migrations with `copier update`, keeping the overlay files unchanged;
    - regenerates the adapters and rebuilds the affected indexes;
    - runs `gov doctor` and writes a ledger entry.
  - A failed update rolls back to the recorded point.
- **KPIs, failure:**
  - An update to a release that fails hash verification refuses.
  - An overlay file changed by the update is a failure and triggers the rollback.

#### W2-18 Pinned install: a product repository runs a fixed release, never the development copy (STANDARD, engineer)
- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.
- **KPIs, success:**
  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned `gov`, never a product's own package named `gov`. With no `gov` installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173, W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
- **KPIs, failure:** a product session that imports this repository's `src/gov` is refused by doctor and reported.

#### W2-19 Language-agnostic test commands (FULL, engineer)
- **Needs first:** a Rust toolchain for the fixture (an install package under DEC-083, queued Q-6); Node 22 is present.
- **Allowed paths:** `src/gov/close/**` (except `src/gov/close/cache*`), `src/gov/config/**`, `template/governance/kernel/schemas/path-map.schema.json` (the test-command keys), `tests/unit/close/**`, `fixtures/lang/**` (new: a small Rust and a small TypeScript project).
- **KPIs, success:**
  - A project declares its test commands (for example `cargo test`, `npm test` or `vitest run`, `pytest`), each with its own parallel option, its own result reader, and the input globs W2-48's cache keys on. `gov close` and the regression run the declared commands [AR-10, W2-H042, W2-L119].
  - A Rust fixture and a TypeScript fixture each close a ticket with their own command [AR-10].
  - A run that collects or passes nothing counts as unmeasured or failed, never passed [W2-H026, W2-M162].
  - Tests run in a clean checkout of the commit, so ignored and compiled files neither dirty the tree nor reach the run [W2-M253, W2-M159, W2-M160].
- **KPIs, failure:** an undeclared language in a project with no test command is a named refusal, not a silent pytest run.
- **On EXAMIN's path (DEC-736):** `gov close` runs its regression only over `tests/`, and EXAMIN's suites are elsewhere, so W2-27 needs the declared test commands. It also builds the ratchet baseline of known reds (estimate 300).

#### W2-20 Machine-wide resource gate (STANDARD, engineer)
- **The values (DEC-742):** at least 4 GiB available, 1-minute load below `nproc`, heavy sessions counting double, at most 8 Gov OS sessions on the machine; taken as configuration, in one place.
- **Allowed paths:** `src/gov/resources/**` (new), `src/gov/launch/gate*`, `tests/unit/resources/**`.
- **KPIs, success:**
  - `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
- **KPIs, failure:** a session in another repository counts against the gate; a start while the gate is shut is refused with the reading.

#### W2-21 Stable launch: `gov launch lead`, the ticket-lead role, launch records (FULL, engineer, with a product-spec worker for the role file)
- **Allowed paths:** `src/gov/launch/**`, `template/governance/kernel/roles/ticket-lead.md` (new), `template/governance/kernel/settings.json` (the one allow rule), `tests/unit/launch/**`.
- **KPIs, success:**
  - `gov launch lead <ticket>` builds the whole lead invocation (absolute paths, the identity in `--settings`, the model, background mode, the log and PID files) and passes the resource gate [DEC-715, W2-H046].
  - Leads run under a ticket-lead role with lead rights, not orchestrator rights. The main session records under its own coordination ticket (W2-00), not a closed one [DEC-434, W2-H001, W2-M291].
  - Every launch writes a launch record (session id, role, ticket, model, PID), and the session's commits carry a `Session:` trailer [W2-M247, W2-M152].
  - A launch is refused if it has no model, names an unknown ticket or role, or would run with unsafe user-level settings [W2-M245, W2-H012].
  - Signals reach the session's process group, and temporary folders are removed on every ending [W2-M187, W2-M095, W2-L105].
  - Launched sessions can run `gov check`, `gov rebuild` and their own suite inside the sandbox [W2-M275, W2-M094, W2-M097, W2-M181].
  - The kernel template's settings carry one narrow allow rule, `Bash(gov launch:*)` [DEC-715].
- **KPIs, failure:** a raw `claude` launch stays unallowed in the template.

#### W2-22 `gov doctor` green (STANDARD, engineer)
- **Allowed paths:** `src/gov/doctor/**`, `governance/project/tool-registry.yaml`, `tests/unit/doctor/**`.
- **KPIs, success:**
  - Doctor reads the installed pytest-xdist version [W2-M287, W2-L336].
  - It does not judge citations inside adoption records or evidence snapshots [W2-M288].
  - After a model-less rebuild it says "semantic index not built", not a canary miss [W2-M289, W2-L206].
  - CLI and extension drift is reported by the owner's policy: a warning below a set gap, a failure above it [W2-M139, W2-M264].
  - It checks that the hook time limit exceeds the guard's deadline [W2-M201, W2-L215].
  - Model hashes are cached by size and mtime [W2-L101].
  - `gov doctor` exits 0 on this repository [F-M2, W2-M290].
- **KPIs, failure:** a tool at the wrong version still fails; a real canary miss still fails.

#### W2-23 Adoption safety on a real repository (FULL, engineer)
- **Allowed paths:** `src/gov/adopt/**`, `src/gov/adapters/**`, `template/governance/project/path-map.yaml`, `tests/unit/adopt/**`, `tests/unit/adapters/**`, `fixtures/adopt/**` (new: a repository with its own `CLAUDE.md`, `AGENTS.md`, `.claude/settings.json`, untracked files, and a path with a space).
- **KPIs, success:**
  - Rollback never deletes an untracked file it did not create; it refuses or preserves [W2-H036].
  - Adapter generation merges a programme's own `CLAUDE.md`, `AGENTS.md` and `.claude/settings.json` instead of overwriting them, keeping their order [W2-H050, W2-M232, W2-M312, W2-M229].
  - The A8 dependency proof finds every listed citation form [W2-H035, W2-M225].
  - A failed or interrupted batch leaves a resumable record and no half-staged state [W2-M219, W2-M220, W2-M224].
  - A project without `.gitleaks.toml`, or with a `.gitignore` that omits `.gov-runtime/`, is set up, not refused late [W2-M217, W2-M218, W2-M307].
  - Every command and hook works in a repository whose path contains a space (`~/EXAMIN APP`).
  - A move to a target that no namespace holds is refused before it runs [W2-M216].
- **KPIs, failure:** the fixture's own instruction files and every untracked file survive an adoption and its rollback byte for byte.

#### W2-48 Test-result cache at close, keyed on exact input hashes (FULL, engineer; DEC-726)
- **Allowed paths:** `src/gov/testcache/**` (new), `src/gov/close/cache*` (the call from close only), `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md`.
- **KPIs, success:**
  - **The key.** Each test's cache key is a sha256 over all of these:
    - its test file;
    - the source it imports, followed transitively inside the repository;
    - the fixtures, `conftest.py` chain and data files it reads;
    - the configuration (`pyproject.toml`, pytest settings, the path map's test keys);
    - the interpreter version and the dependency lock;
    - the test command and its options.
  - A test whose key matches a recorded pass is **reused, not skipped.** It is labelled "reused" in the close record, with the key and the run it came from [W2-H044, W2-M153].
  - A test whose inputs cannot all be hashed (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.
  - A failed or errored result is never reused.
  - Cache entries are written only by `gov close` in the main tree, from a clean tree at a recorded commit. An entry from a worker session or a dirty tree is ignored.
  - `gov close --no-cache` runs everything. W2-24 and W2-46 run the full, uncached regression and say so in their records.
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - **The choice.** `docs/research/W2-48-cache-choice.md` compares pytest-testmon with a small built-in cache:
    - correctness on a planted change set: a change to an imported module, a fixture, a configuration file, a data file, and a file outside every key;
    - the time saved on this repository's suite.
    Any install comes as a package under DEC-083 (queued Q-13).
- **KPIs, failure:** each planted change in an input class makes every dependent test run; a change outside every key reuses. A cache that cannot be read means everything runs, never "passed".

#### W2-49 Contract v4.2, lite (STANDARD, product-spec; DEC-722)
- **Allowed paths:** `docs/contract/contract.yaml`, `docs/contract/CONTRACT_v4.md` (the v4.2 text), `docs/changes/W2-49-CIT-P.md`, `docs/changes/W2-49-CIT-E.md`, `docs/contract/capabilities/**` (DEC-741 K, confirmed by DEC-745: the version line in every record, and the eight records of the split and moved items rewritten from the approved `contract.yaml` in a commit of their own), `docs/contract/SOURCE_MAP.csv` (the eight rows of the CIT-P's §8 only, aligned with v4.2; DEC-745).
- **Route:** CIT-P, independent review, the owner's approval, versioned promotion (CAP-33). **Approved (DEC-741, `0faa0664`), with answers A to J.** The plan validator lines close with W2-51 (DEC-744).
- **KPIs, success:**
  - The CIT-P names each change, its source (DEC-722) and its impact (W2-02, W2-16, W2-18, W2-27 to W2-30, exit criteria 6 and 7):
    - CAP-44.h, lite: the three verdicts and the conditions a lite verdict checks;
    - the A7 and A10 gates of CAP-44.f, lite, with what each lite gate checks and what stays for Wave 3;
    - CAP-43.b, lite: the manifest and file hashes.
  - Contract v4.2 moves exactly those parts to Wave 2. CAP-02.c, A9, A11, the qualification certificate and the rest of CAP-43.b stay in Wave 3.
  - The plan validator's two-way check covers the moved parts.
  - The CIT-E record matches the CIT-P, or lists the differences.
- **KPIs, failure:** a Contract item moved without a CIT-P line, or a CIT-P line with no change, fails the validator.

#### W2-50 The durable scratch root (FULL, engineer; DEC-728)
- **Why:** the plan moves writing work to `~/gov-os-runs/<W2 id>/` (DEC-723), but nothing lets a session write there.
  - The guard allows writes outside the repository only in the temp folder (`src/gov/guard/decide.py`).
  - The launcher's sandbox write list holds only the session's own temp folder (DEC-159, `src/gov/launch/launcher.py`).
  - Clones under `/tmp` are lost on a reboot (W2-M355).
- **Route:** the change loosens the guard, so it goes through CIT-P with the owner's approval (CAP-33), like W2-09. DEC-728 is the owner decision behind it. The lead returns the CIT-P as a package before the engineer starts (queued Q-15). The test designer goes first, and a probe follows green. **Approved (DEC-743), with R1 to R8 (R7 scoped to the root), §6.1 (i), the own folder open only while the ticket is `in_progress`, and `ticket-lead` not among "any role"; the engineer commits the CIT-P before any code (DEC-738).**
- **Allowed paths:**
  - `src/gov/guard/runs.py` (new);
  - `src/gov/guard/decide.py` (the outside-repository rule, and `rmdir` of the root, R7);
  - `src/gov/launch/launcher.py` (the sandbox write list, and making the own folder before the session starts, R2);
  - `template/governance/kernel/checks/secrets-indexing.yaml` (the exclusion only);
  - `src/gov/secrets/__init__.py` (the link rule only: a link from `.gov-runtime/` into `~/gov-os-runs` is not followed; DEC-743 §6.1 (i));
  - `tests/unit/guard/test_runs*`, `tests/unit/launch/test_runs*`;
  - `docs/changes/W2-50-CIT-P.md`, `docs/changes/W2-50-CIT-E.md`.
- **KPIs, success:**
  - **One durable root.** `~/gov-os-runs/` is the one durable scratch root outside the repository, known to the guard and to the launcher's sandbox [DEC-728, W2-M355].
  - **Its own folder only.** A session of any role writes only under `~/gov-os-runs/<its own ticket>/`. That folder is named by the ticket's W2 id (its `external-ref`, as for worktrees), or by its `tk` id when it has none, and resolved from the session's `GOV_TICKET`.
    - The guard allows Write, Edit and judged Bash targets there.
    - The launcher adds exactly that folder (not the root) to the sandbox write list.
    - The folder is created on first use.
  - **Survival.** A clone made there survives the session's end and a restart.
  - **Never indexed.** Nothing under `~/gov-os-runs` is indexed by this repository's stores, and this repository's secrets-indexing check never scans it.
    - A product clone that is adopted there has its own store, inside the clone; that store is the clone's, not this repository's.
    - A planted secret in a clone there reaches no index of this repository.
- **KPIs, failure** (each refused, with the guard's reason):
  - another ticket's folder under `~/gov-os-runs`;
  - the root itself (a file directly in it, or removing it);
  - a path outside it reached by `..`, a symbolic link or a hard link;
  - a session with no ticket;
  - any path outside the repository other than the temp folder and the session's own folder.
  - `~/gov-os-workbench` and `~/gov-os-worktrees` (other than the session's own worktree) stay refused as before.

#### W2-51 The Wave 2 plan validator (STANDARD, engineer; DEC-744)
- **Why:** `docs/plan/tools/validate_s1.py` is Wave 1's. It fails on Wave 2's tree, and by default it reads `~/gov-os-workbench` and `docs/source/`. Exit criterion 7 and W2-49's KPI need a validator that reads Wave 2. `validate_s1.py` stays as Wave 1's record, unchanged.
- **Allowed paths:** `docs/plan/tools/validate_w2.py` (new), `tests/unit/plan/**` (new).
- **KPIs, success:**
  - It reads the Wave 2 plan: the WBS ticket table, the Wave 2 tickets in `.tickets/` (by `wbs_id`, or `external-ref` when it has none; a letter suffix such as `W2-15a` is a W2 id), the list and the triage. Each check prints pass or fail with a named reason.
  - **The two-way check of exit criterion 7:** every Contract item in Wave 2, and every lite item of Contract v4.2, is delivered by a Wave 2 ticket and cited by an acceptance test; every Contract id a Wave 2 ticket cites exists in the Contract.
  - A Contract item moved to Wave 2 with no CIT-P line, or a CIT-P line with no change, fails it (W2-49's failure KPI).
  - The list's and the triage's counts agree with their rows.
- **KPIs, failure:**
  - It never reads `~/gov-os-workbench` or `docs/source/` by default; a check that would need them is reported as not run, by name.
  - An input it cannot read is a named failure, never a pass.

#### W2-52 The lite A7 and A10 stage records (FULL, engineer; DEC-741)
- **Why:** Contract v4.2 (DEC-741, H (i)) brings the A7 and A10 gates of CAP-44.f into Wave 2, lite, but no ticket built their stage records. Exit criterion 7 needs each lite item delivered by a closed ticket and cited by an acceptance test.
- **Starts** after W2-49's apply round; **closes** before W2-27 starts. It shares `src/gov/adopt/` with W2-23, which runs after it.
- **Allowed paths:** `src/gov/adopt/lite_gates.py` (new), `src/gov/adopt/stages.py` (the A7 and A10 entries only), `template/governance/kernel/skills/adopt/**` (the A7 and A10 steps only), `tests/unit/adopt/test_lite_gates*`. The engineer writes the skill's steps too (DEC-738 item 1).
- **KPIs, success:**
  - `gov adopt` runs the lite A7 and A10 gates as Contract v4.2's CAP-44.f (lite) states; each writes a stage record with its evidence, and the adopt skill names both steps.
  - Each lite gate checks what v4.2 says it checks, and its record names what stays for Wave 3.
  - The adoption verdict (W2-02's type) reads both records as named conditions.
- **KPIs, failure:** a lite gate that fails writes a failing record, and the verdict cannot be ADOPTED_HEALTHY; a missing record is a named failure, never healthy.

#### W2-53 The probe gate measures every later merge against git's own merge of its parents (FULL, engineer; DEC-750, DEC-754, DEC-757)
- **Why:** split from W2-01 after its fourth and last probe (DEC-750 item 2). A later merge holding the probed commit, bringing another ticket's branch made before the merge-back and naming that ticket's `Task:`, can delete or revert a probed file or remove an acceptance test, and `gov close` passes; a reopened ticket whose first round was merged back before its final probe cannot close.
- **Starts** right after W2-01 closes (the same paths), alone, ahead of every held ticket (DEC-757), test designer first. W2-07, W2-41 and W2-48 share `src/gov/close/` and run after it.
- **Allowed paths:** `src/gov/close/**`, `tests/unit/close/**`.
- **KPIs, success:**
  - After a FULL ticket's probed commit, every later merge that holds it refuses, naming the merge, whatever task it names (or none), when a probed path (the ticket's allowed paths, its acceptance folder, its ticket file) at the merge is not what git's own merge of its parents gives, a removal or a return to a version from before the ticket included; on the integration branch, inward on the ticket's branch, and for an octopus merge [DEC-750, DEC-754].
  - A later merge that takes another ticket's whole version of a probed file is measured the same way, against git's own merge of its parents (P-5 (c)) [DEC-754].
  - A reopened FULL ticket whose earlier round was merged back before its final probe closes when the probed code at the closed head is the final probed code [DEC-754].
  - A merge whose probed paths are what git's own merge of its parents gives, and another ticket's merge holding the probed commit on neither side, pass as before; W2-01's acceptance cases stay green [W2-H047, W2-M202].
  - **The accepted-red ratchet (DEC-757 item 2.1).** A red whose exact test id the path map's `accepted_reds` lists, with an ACCEPTED owner decision naming it, a reason and the ticket that fixes it, does not refuse the close; the close names it with its decision and fixing ticket. An entry counts only when the commit that added it carries `Role: owner`. Its core is one function W2-19 reuses for declared test commands (DEC-736) [DEC-757].
  - **Integration-side ticket edits (DEC-757 item 2.2).** A change to the ticket's file after its probed commit, made by a commit carrying `Role: orchestrator` or `Role: owner`, naming the ticket in `Task:` and changing only that file, is not a change to the probed code [DEC-757].
  - **The load-sensitive quarantine (DEC-757 item 2.3).** A test the path map's `load_sensitive` lists that fails in the close is re-run alone, in its own process, inside the same close; it counts as passed only if that re-run passes, and the close reports it by name with both results [DEC-757, DEC-372].
  - W2-53 closes through `gov close` with its own merged mechanism, its only reds the listed ones [DEC-757].
- **KPIs, failure:**
  - An acceptance test added on the ticket's branch before the probe and removed or changed by a later merge refuses the close.
  - A merge whose own merge git cannot compute, or cannot read, is judged against the probed code and never passes by default.
  - A red not on `accepted_reds` refuses the close. A listed red that passes refuses the close, naming the entry to remove. An entry added by a commit without `Role: owner`, or whose decision is not an ACCEPTED owner entry naming that test id, is refused, naming the entry; the list never grows without an owner decision [DEC-757].
  - A ticket-file change on the ticket's own side after the probe, or an integration-side commit that changes more than the ticket's file, still refuses [DEC-757].
  - A load-sensitive test that fails its isolated re-run refuses; a test not on `load_sensitive` is never re-run; no re-run is silent [DEC-757].

#### W2-24 Track A gate run (FULL, orchestrator)
- **Allowed paths:** `docs/plan/wave-2/track-a-gate/**` (evidence); fixture clones under `~/gov-os-runs/W2-24/`.
- **KPIs:**
  - From a fresh orchestrator session in accept-edits mode, one lead starts with `gov launch lead`, with no classifier denial and no permission given by hand; the launch is recorded [AR-10, DEC-716].
  - A release is cut and hash-verified, then installed pinned into a fresh copy of a non-Python dev fixture (the W2-19 TypeScript fixture) [AR-10, CAP-43.b lite]:
    - the fixture is adopted (A0 to A6, A8);
    - `gov doctor` and `gov check` are green there;
    - one ticket closes with `gov close` at exit 0, using the fixture's own test command.
  - `gov update` moves the fixture to a second release and back [CAP-45.a].
  - The full, uncached regression runs once and is green (DEC-726).
  - AR-1 to AR-10 are each shown to pass, in order, with the evidence path of each (DEC-721). EXP-003's line is shown by W2-15a.
- **Failure:** any AR line not shown; the fixture importing this repository's `src/`.

#### W2-25 Track A independent audit (FULL, independent-auditor)
- A fresh, read-only auditor checks AR-1 to AR-10 and Track A's tickets against DEC-718, DEC-720 to DEC-727 and this plan. Its verdict is Track A's pass or fail. A BLOCKER is fixed; every other finding goes to the owner (§6).

### Track B — the EXAMIN pilot

EXAMIN's real repository is never written before W2-25 passes, W2-15b reports, W2-28's verdict is in, and the owner gives the go (DEC-727). Before that, every EXAMIN step works on clones under `~/gov-os-runs/`, made from the owner's copy by its exact path (DEC-723). The one exception is W2-26's throwaway `/tmp` clone, before W2-50 (DEC-728).

#### W2-26 EXAMIN profile on the owner's copy: EXP-003's EXAMIN leg (STANDARD, research)
- **Needs first:** the owner's copy at `~/gov-os-workbench/examin/`, made in a plain terminal, and its exact path (owner act O-1).
- **Allowed paths:** `docs/research/EXP-003/examin/**`, plus a working clone made with `git clone --no-hardlinks` from the exact path:
  - before W2-50 closes, the clone goes in a folder of its own under `/tmp`, by literal path (`/tmp/gov-os-W2-26/examin/`); it is throwaway, and every result is committed under `docs/research/EXP-003/examin/` (DEC-728);
  - after W2-50 closes, it goes under `~/gov-os-runs/W2-26/examin/`.
  The owner's copy is read only by that clone; nothing in the workbench is listed or written.
- **KPIs:**
  - On the working clone: size (files, lines, tracked bytes, commits), languages, test runner(s) and their commands, and the test suite's wall time.
  - Indexing time and peak RSS for each index, against DEC-078's envelope.
  - Whether the path with a space breaks any command [W2-I041].
- **Consequences:**
  - If its tests are not pytest, W2-19 joins W2-27's dependencies (DEC-727).
  - If the decision checker or `gov check` exceeds its budget at EXAMIN's size, W2-45 joins them too.
- **Runs** beside W2-01 (layer 1), and **closes** after W2-07.

#### W2-27 EXAMIN adoption on a copy (FULL, orchestrator)
- **Depends on (DEC-727):** W2-01, W2-03, W2-04, W2-05, W2-06, W2-08, W2-09, W2-10, W2-16, W2-18, W2-20, W2-21 and W2-23; W2-26; W2-49 (the lite gates); W2-50 (the clone's folder, DEC-728); W2-19 (DEC-736); W2-52 (the lite A7 and A10 stage records, DEC-741); and W2-45 if the index measures say so (DEC-735). W2-07 lands before it by rule 1.
- **Allowed paths:** `docs/plan/wave-2/examin-copy/**` (evidence); the clone at `~/gov-os-runs/W2-27/examin/` only.
- **KPIs:**
  - The pinned, hash-verified release is installed (W2-16, W2-18).
  - `gov adopt` runs A0 to A6 and A8 with the A5 independent review, and the lite A7 and A10 gates of Contract v4.2.
  - EXAMIN's own `CLAUDE.md`, settings and untracked files are preserved (W2-23).
  - `gov doctor` and `gov check` are green.
  - One LITE ticket goes through the full cycle: test designer, red, implement, green, then `gov close` at exit 0 with EXAMIN's own test command.
  - Its governance share is measured and ≤ 15 %.

#### W2-28 Independent verdict on the copy (FULL, independent-auditor)
- A fresh auditor gives the copy's verdict against the lite conditions of Contract v4.2's CAP-44.h: ADOPTED_HEALTHY, ADOPTED_WITH_ACCEPTED_EXCEPTIONS or NOT_ADOPTED_HEALTHY. Anything short of ADOPTED_HEALTHY goes to the owner before W2-29.

#### W2-29 EXAMIN adoption on the real repository (FULL, orchestrator)
- **Needs first (DEC-727):** W2-25 passed; W2-15b reported; W2-28's verdict; the owner's go (queued Q-9); a backup of `~/EXAMIN APP` (archive and backup ref, A0); and the owner's adoption branch.
- **KPIs:** the same steps as W2-27, on the real repository, on an adoption branch the owner merges after green CI. The first real ticket closes with `gov close` at exit 0. Only the pinned, hash-verified release is used.

#### W2-30 Healthy-adoption verdict on the real repository (FULL, independent-auditor)
- A fresh auditor gives the real repository's verdict. **Track B ends with ADOPTED_HEALTHY** (exit criterion 6).

### Track C — the rest of Wave 2

#### W2-31 Budget gates (FULL, engineer)
- **Allowed paths:** `src/gov/budget/**` (new), `src/gov/close/budget*`, `src/gov/hooks/budget*`, `tests/unit/budget/**`.
- **KPIs:**
  - A ticket declares a token budget with executable thresholds [CAP-04.a].
  - A run that exceeds it stops at the next `gov close` or hook boundary and raises a decision package, and the breach is recorded in the ticket [CAP-04.d].
- **Failure:** a breach that passes silently.

#### W2-32 Retrieval components and bounded improvements (STANDARD, engineer; on the critical path)
- **Allowed paths:** `src/gov/retrieval/**`, `src/gov/config/models*`, `tests/unit/retrieval/**`, `tests/unit/semantic/**`.
- **KPIs, components:**
  - Changing the embedder pin in configuration triggers a full re-embed, and the dev-tier retrieval regression passes [CAP-10.b].
  - An unpinned or mismatched model fails closed with a named error [CAP-19.a, W2-M073, W2-M191, W2-L065].
  - A retrieval miss is recorded as a memory-quality event with its root cause, its repair and a held-out regression case [CAP-19.c].
  - A reranker that dies after loading is reported, not raised [W2-M104].
  - The fusion limit is honoured [W2-M103].
- **KPIs, bounded improvements (DEC-725):** at most the three gaps that W2-15a named, from these:
  - ranked-lexical tuning: field weights, tokenizer, and the exact-identifier boost;
  - chunking: span size, overlap and parent expansion, with a re-embed;
  - the hit@5 85 row on the dev queryset [W2-M341].
  Each gets one round plus its probe; its effect is measured by W2-15b. What remains is a named residual.
- **Failure:** an improvement that lowers any baseline figure of W2-15a beyond its noise band is reverted.

#### W2-33 Wave 2 roles and typed handoff records (STANDARD, product-spec)
- **Allowed paths:** `template/governance/kernel/roles/**`, `template/governance/kernel/schemas/handoff*`, `template/governance/kernel/templates/handoff.md` (new), `.claude/agents/**` (generated through the adapter).
- **KPIs:**
  - Distinct test-execution and integration roles, each with its own rights [CAP-22.c, DEC-094, W2-M321].
  - A UX role [W2-M322].
  - A typed handoff record, from which a fresh agent states the task, inputs, open questions and next step identically [CAP-22.b].
  - The twelve-field return is a handoff record [AR-6].
  - The agent definitions are generated, not placed by hand [W2-M084].

#### W2-34 `gov readiness --generate` (STANDARD, engineer)
- **Allowed paths:** `src/gov/readiness/**`, `src/gov/tasks/**`, `template/governance/kernel/templates/openspec/**`, `tests/unit/readiness/**`, `tests/unit/bridge/**`.
- **KPIs:**
  - `gov readiness --generate` creates one linked gap ticket per required open row, with its dependencies [CAP-30.c, MR-2, W2-M283].
  - A MISSING required row keeps production tickets out of READY [W2-M274].
  - The delivered `tasks.md` template is accepted by the bridge [W2-H051].
  - A direct `openspec archive` or a hand-set status does not bypass readiness [W2-H015].
  - The bridge checks the role against the roster [W2-M082].

#### W2-35 The UX readiness row (STANDARD, engineer)
- **Allowed paths:** `src/gov/readiness/ux*`, `template/governance/kernel/schemas/readiness*`, `tests/unit/readiness/**`.
- **KPIs:** for a feature with a user interface, the UX row closes only on scenario-derived wireframes or mockups the owner has approved, and its acceptance tests include visual checks against them [CAP-30.g, DEC-104]. A visual-testing tool is installed under DEC-083 when first needed (queued).

#### W2-36 `gov discover` (STANDARD, engineer)
- **Allowed paths:** `src/gov/discover/**` (new), `tests/unit/discover/**`.
- **KPIs:** `gov discover <question or feature>` opens a discovery ticket, runs the discovery skill (readiness gaps, owner questions), and schedules research and experiment tasks whose evidence records back the answer. The same request in plain language works the same way [CAP-32.d, DEC-166, W2-M284].

#### W2-37 `gov impact` (FULL, engineer)
- **Allowed paths:** `src/gov/impact/**` (new), `src/gov/closure/**` (read API only), `tests/unit/impact/**`.
- **KPIs:**
  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].
  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].
  - "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167].
  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).

#### W2-38 Profile from impact; impact-selected tests at close (FULL, engineer)
- **Allowed paths:** `src/gov/impact/profile*`, `src/gov/close/select*`, `tests/unit/impact/**`, `tests/unit/close/test_select*`.
- **KPIs:**
  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by `gov impact` [CAP-53.b].
  - A close runs the tests `gov impact` names, on top of W2-48's cache. The full suite runs at milestones and in CI [W2-H043, W2-M240, W2-M241, W2-M163].
- **Failure:** a change whose impact misses a test that would fail is caught by the milestone run and recorded as a learning event.

#### W2-39 Model and provider switch reconstructs the same inputs (STANDARD, engineer)
- **Allowed paths:** `src/gov/context/**` (the model-independence part), `src/gov/checkpoint/**` (resume inputs only), `tests/unit/context/**`, `tests/unit/checkpoint/**`.
- **KPIs:** a ticket's context, checkpoint resume and handoff record, built for two different models, give the same input hash [CAP-37.e].

#### W2-40 EXP-002: the untested sandbox cases and the harness's hook limits (FULL, research)
- **Allowed paths:** `docs/research/EXP-002/**`, `experiments/EXP-002/**`.
- **KPIs:** each of these is measured:
  - the sandbox cases: `denyWrite` on a path that does not exist yet; symlink and hard-link tricks; the seccomp filter; `bypassPermissions`; subagents inside a sandboxed worker session; `excludedCommands` [CAP-61.f, DEC-160, W2-M336, W2-M337, W2-M350, W2-L316];
  - file tools, hooks and MCP servers outside the sandbox [W2-M334, W2-M335];
  - the harness's behaviour at a hook's time limit, so that the guard's deadline sits below it [W2-H052, W2-M347, W2-L328];
  - live auto-compaction and the PreCompact output [W2-M338, W2-M344].

#### W2-41 Close and escalation integrity (FULL, engineer)
- **Allowed paths:** `src/gov/close/**` (except `cache*` and `select*`), `src/gov/tasks/external*`, `tests/unit/close/**`.
- **KPIs:**
  - Close refuses task-less changes to test configuration [W2-H022].
  - The commit range is computed by ancestry [W2-H023].
  - Only a decision naming the escalated ticket lifts its escalation [W2-H024].
  - Escalation state is stored where the caller cannot reset it, or a reset is detected [W2-H025].
  - The external-references list is read from a commit and accepts decision ids only [W2-H033].
  - The probe gate judges every commit after the probe that touches the ticket's paths, whatever its task, and refuses a hand-resolved merge that drops probed code [W2-M015, W2-M204, W2-M255, W2-M256, W2-M203, W2-M254].
  - A late commit on a closed ticket is caught [W2-M115].
  - The tree and HEAD are re-checked before the record is written [W2-M164].

#### W2-42 Guard: missing role, links, late paths, atomic saves (FULL, engineer)
- **Allowed paths:** `src/gov/guard/**`, `src/gov/checkpoint/**` (atomic writes only), `tests/unit/guard/**`, `tests/unit/checkpoint/**`.
- **KPIs:**
  - A missing role argument yields no write scope [W2-H006].
  - A missing held-out file, where the project declares one, fails closed, and doctor reports it [W2-H007].
  - Checkpoint and guard-file saves are atomic, and a broken guard-file edit cannot lock every session [W2-H009, W2-H031, W2-M047, W2-M061].
  - Late-created `.gov-runtime/` names are refused in launched sessions [W2-H010].
  - The main `.git` refs are writable only through the session's own commit [W2-H011].
  - Links are resolved, and a write that reaches the acceptance tests through a link is refused [W2-H013, W2-M031, W2-M067].
  - The guard creates the folder of an allowed file instead of refusing it [W2-M173, W2-L216].
  - A quoted `$NAME` target is judged as the literal the shell writes [W2-M019].

#### W2-43 CI integrity and the secret-rule floor (STANDARD, engineer)
- **Allowed paths:** `src/gov/ci/**`, `src/gov/secrets/**`, `.github/workflows/**`, `template/.github/workflows/**`, `tests/unit/ci/**`, `tests/unit/secrets/**`.
- **Needs first:** the owner's approval of pytest, openspec, rulesync and gitleaks on the CI runner (queued Q-8).
- **KPIs:**
  - The CI job is green on a push, with the approved tools installed by checksum [W2-H002, W2-M003, W2-M018, W2-M271].
  - CI compares the evidence note with the checkout's G3 declarations and refuses a mismatch [W2-H027].
  - gitleaks scans every commit of the pushed range [W2-H028].
  - The template and canary secret rules hold whatever the project file says [W2-H008].
  - The store deletes securely, so removed text leaves no free-page copy [W2-H014].

#### W2-44 Trailers bound to the launch identity (FULL, engineer)
- **Allowed paths:** `src/gov/close/traceability*`, `src/gov/guard/containment*`, `tests/unit/close/test_traceability*`, `tests/unit/containment/**`.
- **KPIs:**
  - A commit's `Role:` and `Task:` are checked against the launch record of the session that made it (W2-21's `Session:` trailer), and a forged role is refused [W2-H019, W2-M156, W2-M222, W2-L078].
  - A worker's commit is attributed to the worker, not to its waiting lead [W2-M038, W2-L135, W2-M037].

#### W2-45 `gov check` runner semantics and scale (STANDARD, engineer)
- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/check/commands.py`, `src/gov/decisions/checker.py` (speed only), `tests/unit/check/**`.
- **KPIs:**
  - The decision checker runs within the `gov check` budget on a 200-decision, 20k-commit repository [W2-H018].
  - A check that exits 0 with findings, or with "unmeasured" in its result, is not green [W2-M129, W2-M212].
  - An absent tool of a hard-block check is red, not yellow [W2-M130, W2-M265].
  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].
  - The time limit is stated and tested [W2-M151].

#### W2-46 Wave 2 exit run (FULL, orchestrator)
- **Allowed paths:** `docs/plan/wave-2-exit/**`.
- **KPIs:** every exit criterion of §5 is run and evidenced, including:
  - the full, uncached regression and the dev-tier regression, both green;
  - a mid-programme specification change on a-dev that propagates through CIT-P → CIT-E with the correct impact set (WBS §6 exit);
  - every Wave 2 close record listed with its exit code;
  - the governance share per programme, the EXAMIN pilot included;
  - `gov doctor` green here and in EXAMIN.

#### W2-47 Wave 2 exit audit, with the audit→repair loop's tests (FULL, independent-auditor)
- **Test design first:** the independent test designer writes the tests for the audit→repair loop (the W1-43 part of CAP-59.a and CAP-59.b, F-M10, W2-M333) and for CAP-56's transcript case (F-m3, W2-L315), red before the audit.
- **KPIs:**
  - A fresh, read-only auditor gives a finding row to every Wave 2 covers item, every Contract v4.2 lite item, every AR line and every MR clause, against Contract v4.2 and the decisions.
  - The audit→repair loop runs on its findings under DEC-096.
  - The report commits through the hook.

## 3. Order, layers and critical path

A layer is the earliest a ticket can start once its dependencies have closed. Tickets in flight stay within the ceiling of 6, with no overlapping paths, and under the resource gate.

When a layer holds more ready tickets than free slots, they are taken in this order:
1. the critical path;
2. the EXAMIN-copy subset (DEC-727);
3. the rest of Track A;
4. Track C.

| Layer | Track A | Track B | Track C |
|---|---|---|---|
| 1 | **W2-01** (alone among code tickets) | W2-26 (read-only; closes after W2-07) | |
| 2 | **W2-02**, W2-05, W2-09, W2-20, W2-48, W2-49, W2-50, W2-51, W2-53 | | |
| 3 | **W2-03**, W2-06, W2-07, W2-10, W2-16, W2-21, W2-22, W2-52 | | |
| 4 | **W2-13**, W2-04, W2-18, W2-08, W2-12, W2-11, W2-17, W2-19 | | W2-31, W2-33, W2-34, W2-37, W2-40, W2-42, W2-44 |
| 5 | **W2-15a**, W2-23, W2-14 | | W2-35, W2-36, W2-39, W2-41, W2-43, W2-45 |
| 6 | W2-24 | W2-27 | **W2-32**, W2-38 |
| 7 | W2-25 | W2-28, **W2-15b** | |
| 8 | | **W2-29** | |
| 9 | | **W2-30** | |
| 10 | | | **W2-46** |
| 11 | | | **W2-47** |

**Shared paths in layer 2 and 3.** W2-50 shares one file each with W2-09 (`src/gov/guard/decide.py`), W2-21 (`src/gov/launch/launcher.py`) and W2-06 (`secrets-indexing.yaml`). Each of those three runs after W2-50, and W2-50 goes first in layer 2 after the critical path:
- W2-50 closes at ≈ day 5.
- W2-09 then closes at ≈ day 7, W2-10 at ≈ day 10, W2-21 at ≈ day 8 and W2-06 at ≈ day 8.
- All of these are ahead of their users: W2-14 and W2-15a at ≈ day 10, W2-27 at ≈ day 11. None becomes critical.

**Shared paths added later.** W2-52 shares `src/gov/adopt/` with W2-23, so W2-23 runs after W2-52 (DEC-741). W2-49 closes after W2-51, whose validator its KPI uses (DEC-744). W2-53 shares `src/gov/close/` with W2-07, W2-41 and W2-48, which run after it (DEC-754).

**Critical path** (by working days, from est. LOC and profile; owner waits not included): W2-01 → W2-02 → W2-03 → **W2-13 → W2-15a → W2-32 → W2-15b** → W2-29 → W2-30 → W2-46 → W2-47, ≈ 20.5 working days.

**Two shorter paths:**
- **The EXAMIN copy:** W2-01 → W2-49 → W2-16 → W2-18 → W2-23 → W2-27 → W2-28. The copy's verdict comes at ≈ day 13, about four days earlier than in the first draft.
- **Track A's verdict:** W2-01 → W2-02 → W2-03 → W2-13 → W2-15a → W2-24 → W2-25, at ≈ day 14.

**What the owner's changes did to the path.**
- The ranked lexical route and EXP-003's two passes (DEC-725) now set the critical path: the real repository waits for W2-15b.
- The copy's adoption moved earlier (DEC-727).
- W2-48 takes the close queue off the critical path from layer 3 on (DEC-726).
- W2-50 (DEC-728) adds a ticket in layer 2 but no time to the critical path or the copy path. It has about 5 days of slack before W2-14 and W2-15a need it.

## 4. Size and estimate per track

| Track | Tickets | est. LOC | Wall time | Owner touchpoints |
|---|---|---|---|---|
| A — adoption readiness | 30 | 4,340 | Track A's verdict (W2-25) by working day 14 to 17 | DEC-720 acts (fast-forward, push); Q-1 RETR-X-02, Q-2 the metric, Q-3 the guard change, Q-4 the hook reinstall, Q-6 the Rust install, Q-7 the gate values, Q-13 the cache tool, Q-14 Contract v4.2's approval, Q-15 W2-50's CIT-P |
| B — the EXAMIN pilot | 6 | 120 (+ fixes the profile and the verdicts raise, as new tickets) | the copy's verdict (W2-28) by day 13 to 16; the real repository's verdict (W2-30) by day 18 to 23 | O-1 the owner's copy; Q-9 the go for the real repository; the merge of EXAMIN's adoption branch; any verdict short of healthy |
| C — the rest of Wave 2 | 17 | 2,640 | beside A and B; done by day 19 to 23 | Q-8 CI tools; the visual-testing tool; the exit decision |
| **Wave 2** | **53 + W2-00** | **≈ 7,100** | **≈ 21 to 27 working days** | |

**How the figures were made.**
- **Durations.** Each ticket's duration is about 1 day plus 1 day per 150 est. LOC, plus half a day for FULL. Research is 1.5 days; integration and audit are 1 day each.
  - The critical path from these is ≈ 20.5 days.
  - The upper end adds 30 % for the systematic overruns of Wave 1 (W2-I040) and a day's owner turnaround on each package the path waits for.
- **Closes.** Before W2-48, every close runs the full regression (≈ 1 hour) after a full rebuild (≈ 4 min), one at a time. That costs ≈ 7 hours over layers 1 and 2. From layer 3 on, a close runs only the tests whose inputs changed, plus the uncached runs at W2-24 and W2-46.
- **Against the first draft** (18 to 24 days): ≈ 3 days longer. Most of that is the two EXP-003 passes and the bigger W2-13 now in front of the real repository. The cache took most of the ≈ 50 hours of serial close time off the path.
- **Unknowns.** EXAMIN's size is unknown until W2-26. A repository larger than DEC-078's envelope adds W2-45 to the copy's gate and two to four days.

## 5. Wave 2 exit criteria

Wave 2 exits when **all** of these hold. W2-46 runs the checks; W2-47 is the independent audit.

1. **Every Wave 2 ticket in this repository closes through a clean `gov close`:** exit 0, no disposition, no exception, close record kept (the F-M3 proof; AR-8; DEC-522). A ticket closed any other way is a named failure of this criterion. W2-00 closes last, the same way, after the owner's exit decision, and its close record is appended to the exit report.
2. **The hooks are back on, with fast pre-commit checks.**
   - The owner has reinstalled lefthook.
   - A commit made straight after staging, with no hand rebuild, passes the pre-commit hook in under 60 s.
   - Index-freshness and recovery-rebuild run at pre-push or in CI.
   - DEC-709 is retired.
3. **`gov doctor` is green** (exit 0) on this repository and on EXAMIN; **`gov check`** reports 17 of 17 families with no RED on this repository.
4. **EXP-003 reports (W2-15b), with the metric approved before W2-15a's first run:**
   - the metric, measured against the owner's goal of 99 % for each corpus and mode, beside W2-15a's baseline, with lexical (ranked), semantic and reranking each shown working in the fusion;
   - **the stacking test:** a question needing about 24k tokens, retrieved in 8k batches, assembled complete, with no duplicates;
   - **the scale probe** against DEC-078's envelope, on EXAMIN's clone and `~/workspace`;
   - CAP-10's figures for the owner (F-m2).
5. **The adoption-readiness block passes:** AR-1 to AR-10, shown in order (W2-24) and audited (W2-25).
6. **EXAMIN is adopted with a healthy verdict.** ADOPTED_HEALTHY comes from a fresh independent auditor on the real repository (W2-30), after the copy's verdict (W2-28), against Contract v4.2's lite CAP-44.h. **EXAMIN runs a pinned, hash-verified Gov OS release** (DEC-722).
7. **The Contract's 17 Wave 2 items, and Contract v4.2's lite items** (CAP-44.h with A7 and A10, CAP-43.b), are each delivered by a closed ticket and cited by an acceptance test. The plan validator checks this both ways.
8. **Governance share ≤ 15 %** on each programme's run (ORION, ARGUS and the EXAMIN pilot), measured as in DEC-086.
9. **The full, uncached regression and the dev-tier regression are green,** and a mid-programme specification change on a-dev propagates through CIT-P → CIT-E with the correct impact set.
10. **Every one of the 791 rows** is closed, carried to Wave 3 or the backlog with its reason, or named as an exception the owner accepts (`docs/plan/WAVE_2_TRIAGE.md` kept current).
11. **An independent exit audit** (W2-47): a fresh, read-only auditor; every Wave 2 covers item, Contract v4.2 lite item, AR line and MR clause; the audit→repair loop runs (F-M10).

## 6. The Wave 2 finish line (owner rule, from day one)

- **Before opening any new work in Wave 2, classify it.** Does it break a Wave 2 exit criterion (§5)? Is it a fail-open hole that ordinary work produces?
  - If neither, it goes on the Wave 2 list as a new row, triaged to Wave 3 or the backlog, with no new round.
  - If either, it comes to the owner as a package before any round starts.
- **A running follow-up gets at most one more run plus its probe.** Then whatever remains becomes a named residual, unless it is a fail-open in ordinary work.
  - This includes W2-32's bounded improvements and W2-15b: a figure short of 99 % after W2-15b is a named residual for the owner, not a new round (DEC-725).
- **Exit audit findings:** a BLOCKER is fixed; every other finding comes to the owner, recommended for the Wave 3 list unless it meets the test above.
- **The order to the end:**
  1. close the running pieces;
  2. W2-15b;
  3. EXAMIN's healthy verdict (W2-30);
  4. W2-46;
  5. W2-47;
  6. the owner's exit decision;
  7. W2-00's close.
  Nothing else starts once W2-46 has started.
- **Every report starts with a countdown:** the steps left to the end of Wave 2, with a time estimate for each.

## 7. Owner decisions

**Answered (DEC-720 to DEC-729, staged for the owner's commit).**

| Package | Answer | Entry |
|---|---|---|
| P-W2-1 branching | (a): `main` fast-forwarded to `wave-1-exit`, `w2/integrate` cut from it | DEC-720 |
| P-W2-2 the AR order | (a): W2-01 first; AR-1 to AR-10 shown in order at W2-24 | DEC-721 |
| P-W2-3 Contract re-baseline | In part: Contract v4.2 lite for CAP-44.h (A7, A10) and CAP-43.b; CAP-02.c stays in Wave 3; exit criterion 6 says "pinned, hash-verified"; Q-5 dropped | DEC-722 |
| P-W2-4 the EXAMIN profile | (a): early, read-only, on the owner's copy; no agent writes, lists, globs or searches the workbench | DEC-723 |
| P-W2-5 the AR-7 form | (a): `Role: owner`, staged in batches, and `gov approve` (W2-12) | DEC-724 |
| Plan changes | Ranked lexical route and EXP-003 in two passes; test-result cache as W2-48; EXAMIN copy on the safety-critical subset | DEC-725, DEC-726, DEC-727 |
| The durable scratch root | W2-50 in layer 2, through CIT-P; every ticket that clones into `~/gov-os-runs` depends on it; W2-26 uses `/tmp` until then | DEC-728 |
| P-W2-6 W2-00, and the plan | (a): W2-00, created first after the commit; the plan (revision 2, with W2-50) approved | DEC-729 |

**Open now:** none.

**Owner acts the plan needs:**
- **O-1:** the EXAMIN copy at `~/gov-os-workbench/examin/` and its exact path, before W2-26.
- **O-2:** the fast-forward of `main` and the pushes (DEC-720).
- **O-3:** setting `GOV_TICKET` to W2-00's `tk` id, which the orchestrator gives straight after creating it (DEC-729).

**Queued** (raised when their ticket reaches them; never more than five open at once):
- **Q-1** RETR-X-02 (W2-13): must a question about an id that exists nowhere show a parent expansion? Recommendation: no. A named "not found" stopping reason with no unrelated items is the right answer, and W1-42's case is restated by the test designer.
- **Q-2** EXP-003's metric, before W2-15a's first run; it also fixes at most three gaps for W2-32.
- **Q-3** The guard change of W2-09 (CIT-P, CAP-33).
- **Q-4** The hook reinstall (W2-08), an owner act.
- ~~Q-5 the signing key~~: dropped (DEC-722).
- **Q-6** A Rust toolchain for W2-19's fixture (an install under DEC-083).
- **Q-7** The machine-wide gate's values (W2-20).
- **Q-8** pytest, openspec, rulesync and gitleaks on the CI runner (W2-43; W2-H002).
- **Q-9** The go for EXAMIN's real repository (W2-29), after W2-25, W2-28 and W2-15b.
- **Q-10** CAP-10 under DEC-105 (F-m2), with W2-15b's figures.
- **Q-11** `COMPLIANCE.md` (F-m5): retire it in favour of the exit audits (recommended), or bring it up to date.
- **Q-12** The triage itself: any row the owner moves.
- **Q-13** pytest-testmon, if W2-48's comparison chooses it (an install under DEC-083).
- **Q-14** The approval of Contract v4.2 (W2-49's CIT-P).
- **Q-15** The approval of W2-50's CIT-P, the guard and sandbox change behind DEC-728 (CAP-33).
- **Q-16** (added 2026-10-16, with O-1) EXAMIN's real repository carries 9 uncommitted entries (6 modified, 3 untracked; the owner's copy shows the same at head `a7cf346`, and a clone sees only that commit). What happens to them before W2-29 adopts the real repository? Raised when W2-29 is next, with W2-26's list of the entries (ticket W2-29).

## 8. Branching (DEC-720; nothing done yet)

**The remote today:**
- `main` is at `8f458d82` (2026-10-01, "archive: docs/source removed after S1-A acceptance").
- `w1/integrate` is at `a26f555c`.
- The tag `wave-1-exit` (annotated, unsigned) is on `a26f555c`.
- `main` is an ancestor of `wave-1-exit`, 1,343 commits behind, so a fast-forward needs no merge.
- Local branches: `main`, `w1/integrate`, `w1/W1-42` (kept, DEC-711).

**The steps,** which keep `w1/integrate` exactly at `wave-1-exit` and put the plan's commit at the start of the Wave 2 line:
1. The owner fast-forwards `main` to `wave-1-exit` and pushes it (`git push origin wave-1-exit^{commit}:main` from a plain terminal). Agents never push.
2. The orchestrator cuts `w2/integrate` from `main` in the main tree with `git switch -c w2/integrate main`. `main` and `w1/integrate` then point at the same commit, so the staged plan files carry over unchanged.
3. The owner commits the staged plan with DEC-719 to DEC-729 (`Role: owner`) as the first commit on `w2/integrate`, and pushes the branch.
   - The orchestrator then creates W2-00 with `tk` and gives the owner its id.
   - The owner sets `GOV_TICKET` (O-3) and restarts the session.
   - The other tickets follow.
4. `w1/integrate` is frozen as history at `wave-1-exit`. `w1/W1-42` stays until the owner says otherwise.
5. Ticket branches are `w2/<W2 id>`, cut from `w2/integrate`, in worktrees under `~/gov-os-worktrees/`.
6. At Wave 2's exit the owner fast-forwards `main` to the exit tag again. Release commits (W2-16) are on `w2/integrate`, and the owner tags them.

## 9. Triage of the 791 open rows

`docs/plan/WAVE_2_TRIAGE.md` places every open row: **in Wave 2** (with its ticket), **Wave 3** or **backlog**, each with a one-line reason. Nothing is silently dropped.

**Counts:**
- **537 in Wave 2:** 47 high, 309 medium, 170 low, 11 info.
- **85 to Wave 3.**
- **169 to the backlog.**

Every medium row not in a ticket has its own reason.

**Changes since the first draft:**
- W2-M102 and W2-L233 come into W2-13.
- W2-I017 comes in, lite, through W2-49.
- EXP-003's rows split between W2-15a, W2-32 and W2-15b.
- The caching rows (W2-H044, W2-M153) move to W2-48.
- Revision 3: W2-M355 (live clones under `/tmp` lost on reboot) moves from W2-14 to W2-50 (DEC-728).

The S0b2 glue items on the Wave 1 WBS's Wave 2 outline but not on the list are placed there too: G-13 → W2-32, G-16 and G-24 → W2-37, G-23 → W2-06.
