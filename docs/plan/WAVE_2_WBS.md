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
- **DEC-726:** test-result caching at close is its own ticket, W2-48, in layer 2. **Changed by DEC-880 (owner, 2026-10-21):** W2-48's cache is withdrawn; a close runs a path-scoped regression from W2-66's merge, the full regression before it.
- **DEC-727:** EXAMIN adoption on the copy (W2-27) depends only on the safety-critical subset. The real repository (W2-29) stays gated by W2-25 and W2-15b.
- **DEC-723:** agents never write in `~/gov-os-workbench`. (Its listing refusal was replaced by DEC-820: reads there are open except the held-out material's contents; DEC-866.)
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
   - **W2-01 goes first, alone (DEC-721).** It fixes the close path (trailers base, merge form, accepted history, the probe gate after a merge-back). It is itself closed with `gov close` once merged, because `gov` ran from this repository's `src/` (an editable install, DEC-605; since DEC-822 the pinned release judges, and `PYTHONPATH` chooses only the code under test).
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
6. **Launches.** **DEC-789 (owner, 2026-10-18): the next worker any lead starts is a trial through `gov launch <role> <ticket>`, sandboxed; if it starts, does its job and is refused a write outside its worktree, every new worker starts through `gov launch` and this rule is amended by DEC-789; if it fails, the failure goes to the owner as a package.** **DEC-799 (owner, 2026-10-19), from the trial: every worker whose suites do not need the code graph, test designers included, starts through `gov launch`, sandboxed; only a worker whose suites need it starts in the old launch form, with the tripwire (DEC-789 item 1); each lead's return names which workers ran sandboxed. W2-56 makes `gov launch` usable for every worker.** Until W2-21 closes, leads start in the owner's launch form (DEC-715); a blocked launch is a `LAUNCH_BLOCKED` stop to the owner. After W2-21, `gov launch lead <ticket>` and `gov launch <role> <ticket>` are the only ways in.
7. **Product repositories.** No product repository is written in Wave 2 except as DEC-727 allows: a throwaway clone of EXAMIN may be adopted (W2-27) once the safety-critical subset has closed. The real repository waits for W2-25, W2-15b and the owner's go. A product repository runs a fixed, pinned, hash-verified Gov OS release (W2-16, W2-18), never this repository's editable development copy.
8. **The workbench (DEC-723).**
   - Agents never write in `~/gov-os-workbench`. Reads there are open except the held-out material's contents (DEC-820, replacing DEC-723's listing refusal; DEC-866).
   - The owner makes the EXAMIN copy at `~/gov-os-workbench/examin/` in a plain terminal and gives its exact path.
   - Work that writes (indexing, test runs, adoption on a copy, dev-tier clones) runs on a clone the agent makes under `~/gov-os-runs/<W2 id>/`, from an exact path. Acceptance tests keep reading the dev tiers through `GOV_DEV_TIERS` by name and cloning into a temporary folder.
   - **The durable scratch root (DEC-728).** Until W2-50 closes, neither the guard nor the launcher's sandbox lets a session write in `~/gov-os-runs`. Every ticket that clones there therefore depends on W2-50.
   - The one exception is W2-26, which runs before W2-50. It clones into a folder of its own under `/tmp`, named by literal path (for example `/tmp/gov-os-W2-26/examin/`), and commits its results to `docs/research/EXP-003/examin/`. Only the throwaway clone is volatile.
9. **Machine-wide resource gate.** Several repositories' sessions will share this machine.
   - Until W2-20 closes, the orchestrator reads the gate by hand before each start: `free -g` shows at least 4 GiB available, the 1-minute load is below `nproc`, and heavy tickets count double. It counts every Gov OS session on the machine, not only its own.
   - After W2-20, `gov launch` refuses when the gate is shut.
10. **List rows.** A list row's state is re-checked against the code when its ticket picks it up (DEC-718). A row a ticket closes is marked closed in `docs/plan/WAVE_2_LIST.md` with its commit.
11. **Owner decisions (DEC-724, changed by DEC-861 and DEC-862).**
    - The orchestrator records the owner's decisions and commits them itself, as soon as they are written, with `Role: orchestrator`, `Task: decision-record` and `Decided-by: owner (chat, <date>)`; nothing stays staged. The owner's push is the acceptance.
    - Until W2-12 lands, ratchet entries (`accepted_reds`, `load_sensitive`) and escalation lifts stay the owner's own `Role: owner` commits (DEC-862 (a)).
    - Once W2-12 lands, the owner approves with `gov approve` in a plain terminal, and the close counts a decision-record commit once it is in the owner's pushed ref (DEC-862 (b)).
    - Delegated decisions are the orchestrator's, with `Role: orchestrator`.
12. **The coordination ticket W2-00 (DEC-729)** carries the main session's own records (section 2, W2-00).
13. **The finish line (§6) applies from day one,** EXP-003's two passes included (DEC-725).
14. **Stacked starts (DEC-786).** A ticket may start stacked on a held, verified base when its paths overlap no unmerged ticket's paths, parallelism allows one more lead (DEC-847, which replaced DEC-786's "at most 3"), and it merges every change to its base and re-verifies before its own merge, which comes only after its base has closed.
15. **Reports (DEC-787).** Every orchestrator report ends with exactly one line, `OWNER_ACTION: <P1|P2|COMMIT|none> <ids> - <one-line summary>`, naming every open owner item.
16. **Owner commits (DEC-788, changed by DEC-861).** There is no owner batch any more: the orchestrator commits the records of the owner's decisions as they are written (rule 11). The owner commits only a ratchet entry or an escalation lift (DEC-862 (a)), prepared by the orchestrator and asked for with an `ACT` ping (DEC-855); the report's final line then names it.
17. **Workers (DEC-789, DEC-793).** After each worker exits, its lead confirms that the main tree, every other worktree and every acceptance folder are unchanged (`git status` and a hash of `tests/acceptance/`), and reports it. Until W2-33 lands, the lead checks every worker's return for the twelve fields and sends a non-compliant return back with the missing fields named. Until every worker starts through `gov launch`, a guard hole a worker can reach through a script is fixed, not rowed (DEC-779 as DEC-789 reads it), when an honest agent reaches it in ordinary work (DEC-801).
18. **Reviews (DEC-801, DEC-802, DEC-803, DEC-824).** Every reviewer, probe and auditor brief carries the one canonical judgement text, `governance/project/briefs/JUDGEMENT.md` (the w2 prompt's §14), word for word. In short: reviewers and probes judge against ADR-0001's threat model, honest agent mistakes and plausible accidents in ordinary work, not deliberate adversaries; a finding that needs a deliberate construction is a row for the Wave 3 hardening pass, never a new round. Every finding is judged by two questions, word for word: "Can an honest agent hit this in ordinary work?" and "Does it fail open or lose work?" Every finding in a probe or audit record carries two lines, `Ordinary work: yes|no, because …` and `Consequence: fails open|loses work|other`; a finding marked "no" is a row automatically, never a round (DEC-808). A package that proposes a round states its findings' classification on one line before the recommendation (DEC-809). A ticket that will resume anyway takes its accepted fixes in that resume, never in a separate round. A risk that exists only when a feature is switched on is an entry criterion of the ticket that switches it on.
19. **Closes first (DEC-806).** W2-54, then W2-53's re-close, then the held tickets in the quiet-window order; no new ticket starts while a close waits on a quiet window it would disturb.

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
| W2-12 | A | Owner approval facts and `gov approve` | implementation | engineer | FULL | W2-03 | 340 | AR-7, F-M6, DEC-724, DEC-862 |
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
| W2-48 | A | **WITHDRAWN (DEC-880; its purpose passes to W2-66).** Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run (DEC-843, DEC-852) | implementation | engineer | FULL | W2-01 | 220 | W2-H044, W2-M153, DEC-726 |
| W2-49 | A | Contract v4.2, lite: CAP-44.h with A7 and A10, CAP-43.b (CIT-P) | specification | product-spec | STANDARD | W2-51 (closes after it, DEC-744) | 0 | DEC-722 |
| W2-50 | A | The durable scratch root: `~/gov-os-runs/<own ticket>/` in the guard and the launcher's sandbox (CIT-P) | implementation | engineer | FULL | W2-01 | 120 | DEC-728, W2-M355 |
| W2-51 | A | The Wave 2 plan validator (DEC-744) | implementation | engineer | STANDARD | W2-01 | 120 | exit criterion 7's two-way check |
| W2-52 | A | The lite A7 and A10 stage records (DEC-741) | implementation | engineer | FULL | W2-01, W2-49 | 100 | CAP-44.f (lite) |
| W2-53 | A | The probe gate measures every later merge against git's own merge of its parents; owner-accepted known reds, integration-side ticket edits, a load-sensitive quarantine (DEC-750, DEC-754, DEC-757) | implementation | engineer | FULL | W2-01 | 160 | DEC-750 item 2, DEC-757 |
| W2-54 | A | The context packet's dropped list in a stable order; the context-reproducibility check's declared time limit; the `audit-report` type as W2-02 defines it (DEC-768) | implementation | engineer | FULL | — | 120 | DEC-768 items 1 and 3, DEC-773 |
| W2-55 | C | Decisions tagged by domain, status and scope; superseded and done entries left out of what agents see (DEC-791) | implementation | engineer | STANDARD | W2-03 | 150 | DEC-791 (i) |
| W2-56 | A | `gov launch` usable for every worker: the code-graph folder in the session's own temporary folder, the sandbox's write list limited to the ticket's paths, no placeholder in a commit (DEC-799) | implementation | engineer | FULL | W2-50, W2-05 (closes after them) | 120 | DEC-789, DEC-799 |
| W2-57 | A | Load out of the close: W1-46's live cases and W1-30's time-limit case hold under load; the close reads the gate or isolates its timing-sensitive cases (DEC-813, DEC-823) | implementation | independent-test-designer, then engineer | FULL | the closes now queued; closes before W2-24 | 120 | DEC-813, DEC-823, W2-M364, W2-M384 |
| W2-58 | A | Policy 2 in the guard and the launcher: reads open, refused only secrets, held-out contents, the counterpart's work on the ticket, an evaluation set's hidden half (DEC-820, DEC-821; keystone 3) | implementation | engineer | STANDARD | keystone 3 of the revised plan (DEC-829) | 150 | DEC-820, DEC-821 |
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
| W2-42 | C | Guard: missing role, links, late paths, atomic saves | implementation | engineer | FULL | W2-10 | 180 | W2-H006, H007, H009, H010, H011, H013, H031, H060 |
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
- **DEC-860 (owner, 2026-10-20; standing):** never one giant query and never one giant context. Within the packet's ceiling, the supplementary evidence comes from retrieval in batches, ranked and stacked in order of relevance; the packet names what it left for a further batch.
- **KPIs, failure:** DAEO-03pw's context (814,821 tokens at the audit) refuses or fits; a RETIRED or REJECTED record does not satisfy a mandatory source.

#### W2-05 The git environment of every check, hook and helper; the settings re-sort (FULL, engineer)
- **Allowed paths:**
  - `src/gov/**/*.py`, limited to calls that start git. The sweep is the ticket's first deliverable and names each file before it is changed.
  - **DEC-776, DEC-777 (2026-10-18):** an early start. While another ticket is unmerged or unclosed, W2-05 changes no file in that ticket's allowed paths (W2-50, W2-54, W2-53's `src/gov/close/**`, and the held W2-02, W2-03, W2-16, W2-20, W2-49, W2-51). The sweep lists those calls as "after <ticket> merges", and the resume round changes them.
  - `src/gov/util/gitenv.py` (new), `lefthook.yml`, `template/lefthook.yml`, `tests/unit/gitenv/**`, `docs/research/AR-2-git-sweep.md`.
  - **DEC-783 (2026-10-18), P-W2-33 (b):** the settings re-sort is re-baselined (the KPI below); the test designer rewrites its 4 cases. The freeze lookup's own time limit is 15 seconds, in `src/gov/guard/decide.py`, set in the resume round after W2-50 merges. `template/lefthook.yml.jinja` stays untouched; W2-M281 is read as `template/.rulesync/hooks.jsonc`.
  - **DEC-804, DEC-805 (owner, 2026-10-19):** no third round now. The resume after W2-50 and W2-53 merge also takes, tests first: F-A (a declared check gets no inherited `GIT_INDEX_FILE`) and P-1 (an inherited index honoured only for git calls in the project root); F-B and D-1 are Wave 3 rows W2-M375 and W2-M376 (DEC-807); W2-M281 as hook events and matchers with paths normalised, and `template/.rulesync/hooks.jsonc` gains the template's missing `sessionStart` matcher (that line only), so adapter-portability lands green. The resume's fresh probe reviews them.
- **KPIs, success:**
  - Every check, test helper and command that runs git in another folder clears the inherited `GIT_*` variables. One helper does it, and the sweep record lists every call [AR-2, W2-M105, W2-M113, W2-M161, W2-L160].
  - A hooked commit in a linked worktree leaves its branch, index and reflog as the commit made them (the DEC-710 case) [AR-2].
  - `lefthook install` leaves `.claude/settings.json` byte-identical to the committed file; `uninstall` is an owner act, followed by restoring the committed file (DEC-712); adapter-portability stays green [AR-2, DEC-783].
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

#### W2-07 `gov close` by ticket class; the commit gates before any test; complete, tracked repair tickets; a share for every close (STANDARD, engineer; DEC-868, DEC-892, DEC-896 item 3, DEC-898; keystone 1)
- **Place (DEC-896 item 3):** comes forward to sit with W2-66, before the first re-pin, and rides in it.
  - It shares `src/gov/close/command.py` with W2-66: W2-66 writes the record's evidence lines, W2-07 the gates.
  - **The merge order (owner, DEC-899 item 2):** the two are built in parallel, and **W2-07 merges first.** Then W2-66 merges `w2/integrate` back, re-verifies and gets a fresh FULL probe before the re-pin.
  - Its close is judged by the pin, so its own gates help from the re-pin on.
- **Allowed paths:** `src/gov/close/**` (except W2-66's and W2-68's new modules `select.py`, `nightly.py`, `evidence.py`, `batch.py`, `fingerprint.py`), `src/gov/telemetry/**`, `tests/unit/close/**`, `tests/unit/telemetry/**`, `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` and W1-30's collection-error cases (one named revision batch for its test designer).
- **KPIs, success (the existing ones kept):**
  - judged by its class:
    - implementation on its acceptance tests;
    - specification on its readiness record and tests;
    - audit on its report and validator;
    - research on its evidence record;
    - integration or coordination on its named evidence files;
  - a complete, tracked repair ticket;
  - the measured governance share;
  - adoption-gap and baseline refusals not counted;
  - an interrupted close blocks nothing;
  - the probe gate's named-finding acceptance (W2-M371, DEC-790);
  - DEC-868's pre-close gate inside `gov close`.
- **Added by DEC-896 item 3 (owner):**
  - **Decision records measured by their decision:** a decision-record commit that changes only governance records, under an ACCEPTED decision, counts as measured for the work-without-a-task gate. A decision-close would hide the gap and is not this.
  - **Test-revision tickets** are judged on their declared `acceptance_tests.path` (DEC-892). W2-63, W2-67's revisions and W2-70 wait for this.
  - **A stale probe is named before the close spends its run** (W2-M403).
- **Added from lens I (P-IS-4 (a), for the owner's decision):**
  - **The commit gates run first,** and stop before any test when one refuses, spending no ratchet attempt (DEC-868 item 3). They are the trailers, task-less work, accepted history, the probe gate, and the ratchet's own reading of both lists' entries. On 2026-10-22 two closes spent about 70 minutes each before refusing on commit findings (I2 F13, I4 F14, F17).
  - **Named for its test designer** (cases this ticket turns red): `tests/acceptance/W1-30/test_w1_30_no_acceptance_tests.py` (3 functions, 6 cases) and `test_collection_error_refuses_close`. **For its engineer:** the unit `test_a_collection_error_is_a_finding` (I2 F9).
  - **Optional:** the missing case for the close record's packet hash, made a constant in a planted fault that nothing caught (I2 PF9).
- **Added by DEC-898 (owner):** before its regression, `gov close` reads the shared disk's free space and free inodes (W2-20's reading once it lands; until then the same floors, 100 GiB and 10,000,000 inodes, from the configuration). Below the floor it refuses at once, naming the reading, and spends no attempt.
- **KPIs, failure:**
  - a research ticket without an evidence record, or an audit ticket whose report fails the validator, closes;
  - a tree with a collection error, a red `gov check`, a stale checkpoint, a stale probe, an unmeasured commit, a ratchet entry the ratchet would not count, or a disk below the floor is refused only after the regression;
  - a decision-record commit outside an ACCEPTED decision counts as measured.

#### W2-08 Hooks back on (STANDARD, orchestrator, with the independent test designer)
- **Allowed paths:** `docs/plan/wave-2/hooks-back-on/**` (evidence), `tests/acceptance/W1-40/**` (test designer only).
- **Entry criteria (DEC-803, DEC-804, DEC-807):** W2-05's F-A (a project's own check running git during a hooked commit acts on the project's index) is fixed and tested on `w2/integrate`; the hooks do not return before.
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
- **DEC-808 (owner, 2026-10-19):** the paths gain `template/governance/kernel/schemas/probe.schema.json` and `template/governance/kernel/schemas/audit-report.schema.json` (the two finding fields only, required for records written after the change; earlier records stay valid).
- **KPIs, success:**
  - **The threat model in the kernel (DEC-808, W2-M377):** every finding in a probe record and an audit report carries `ordinary_work` (yes or no, with its reason) and `consequence` (fails open, loses work or other); the reviewer brief template and the audit skill ask the two questions word for word ("Can an honest agent hit this in ordinary work?", "Does it fail open or lose work?") and say that a finding marked "no" is a row, never a round.
  - **The standing decisions distilled (DEC-791 (ii)):** the orchestration skill and the brief templates state DEC-715 and DEC-731, DEC-719, DEC-732, DEC-733, DEC-847 (which replaced DEC-737's and DEC-786's caps), DEC-750 and DEC-754, DEC-757 item 6, DEC-766, DEC-768 item 4, DEC-779, DEC-780 and DEC-787, each with its source; entries scoped to this repository go to the project prompt, not the kernel skill.
  - Every brief template and the orchestration skill carry the twelve-field rule, the payload-after rule, and "stop after two identical refusals and return" [AR-5, AR-6].
  - They also carry Policy 2's read rule (DEC-820, which replaced DEC-723's listing refusal and DEC-508) and the decision-record rule (DEC-861, DEC-862, which changed DEC-724's owner commits) [DEC-866].
  - The audit brief states DEC-430 [F-m1, W2-L268].
  - The launcher command is stated as a command, not a code span [W2-L257].
  - The five brief templates carry record frontmatter [W2-L258], and loose citations are fixed [W2-L256].
  - **The test-design skill (DEC-889 item 11 c; lens H finding 10):** it states the test kinds (unit, acceptance, live or harness, dev-tier, load-sensitive, repository-state), the run-time cost a test may take and how it is measured, that a test never copies the whole working tree where a minimal fixture will do, and that a test asserting the live repository's own state is declared as such (the record-reading set).
  - Its paths gain the test-design skill and its copies (`template/governance/kernel/skills/test-design/**`, `.claude/skills/test-design/**`, `.rulesync/skills/test-design/**`, `template/.rulesync/skills/test-design/**`; DEC-889).
- **DEC-866 (owner, 2026-10-20), the sweep's findings for this ticket** (`governance/project/orchestration/packages/SWEEP-2026-10-20.md`):
  - The brief templates (`brief-lead.md`, `brief-engineer.md`, `brief-test-designer.md`, `brief-product-spec.md`, `brief-reviewer.md`), the orchestration skill and its three copies (`template/.rulesync/skills/`, `.rulesync/skills/`, `.claude/skills/`) and the orchestrator role file and its copies no longer teach a superseded rule: no `LEAD_CHECKPOINT` and no "at about <context limit> tokens" (DEC-838; a checkpoint at every handover, DEC-837); no listing or search refusal over the governance folder or `.claude/`, and the held-out list's names readable (DEC-820, replacing DEC-508, DEC-525, DEC-557 and DEC-162's "names a held-out path"); no fixed ceiling of tickets in flight (DEC-847); the owner's decisions recorded by the orchestrator's decision-record commits (DEC-861). DEC-460's citation for naming the model stays (its pin of main sessions stands).
  - Its independent test designer revises the W1-35 cases that require those sentences (`test_the_brief_carries_the_standing_sentences_word_for_word`, `test_every_clause_of_the_row_is_stated[temp hygiene and protected files]`, `[parallel tickets]`), each with `Rewrite-Reason: <the new decision>`; no other expectation changes.
  - The paths gain `template/governance/kernel/roles/orchestrator.md` and its copies (`.rulesync/subagents/`, `template/.rulesync/subagents/`, `.claude/agents/`: those lines only) and the skill copies under `.rulesync/skills/` and `template/.rulesync/skills/` (W2-L363). The W1-35 cases are not in `allowed_paths` (an implementer's paths never cover acceptance tests, MR-3, `core-mutation`): its test designer revises them because the KPI names them (brief A1, DEC-867).
  - If W2-58 has merged first, the listing-refusal sentences are already wrong in practice; if not, they stay until W2-58 merges, and W2-11 merges after it.
- **KPIs, failure:** the skill validator refuses a brief without the twelve-field rule; a template, skill or role file that still teaches `LEAD_CHECKPOINT`, a listing refusal or a fixed ceiling fails a test.

#### W2-12 Owner approval facts and `gov approve` (FULL, engineer)
- **Allowed paths:** `src/gov/decisions/**`, `src/gov/approve/**` (new), `src/gov/check/authority.py`, `template/governance/kernel/checks/core-authority.yaml`, `tests/unit/decisions/**`, `tests/unit/approve/**`, `tests/unit/check/test_authority*`.
- **KPIs, success:**
  - **`gov approve`** [DEC-724]:
    - It is run by the owner in a plain terminal. It shows the staged register entries (ids and titles), asks for a typed one-time code, and commits exactly those entries, with the files staged beside them, with `Role: owner`.
    - It refuses, with a named reason and nothing committed, when it is run with a Claude Code ancestor process, with a launched session's identity (`GOV_ROLE` or `GOV_TICKET` set), or without an interactive terminal. This is the freeze lift's test (DEC-409).
    - It refuses when nothing is staged, or when a staged entry is not an owner entry.
  - A register entry reads as the owner's only when the commit that sets it ACCEPTED carries `Role: owner` and was made by `gov approve`, or by the owner's own commit before W2-12, or (DEC-861, DEC-862 (b)) by the orchestrator's decision-record commit with `Decided-by: owner` once it is in the owner's pushed ref (or, once the owner chooses signatures, has a valid owner signature). Otherwise core-authority names it "transcribed" [AR-7, F-M6, W2-M258, W2-M108].
  - **DEC-891 (owner, 2026-10-21):** an `accepted_history` entry for a commit that changes code, tests or the kernel is in the same owner-only class as the ratchet entries and the escalation lifts, until this ticket moves that class to the owner's push in git; an entry for a commit that changes only records or ticket files is recorded by the orchestrator from the owner's decision.
  - A decision set ACTIVE without an owner approval fact turns core-authority red [W2-H049, W2-M227, W2-M257].
  - "The decision checker could not run" is a finding, never green [W2-H037, W2-H048].
  - Body edits that keep an approved decision ACTIVE are flagged [W2-L010]. An author date earlier than the committer date by more than a day is flagged [W2-M107].
  - **The owner's push as the acceptance in git (DEC-862 (b), owner, 2026-10-20):** the close counts a ratchet entry (`accepted_reds`, `load_sensitive`) or an escalation lift from a commit carrying `Task: decision-record` and `Decided-by: owner` only once that commit is an ancestor of the owner's pushed `origin/w2/integrate`; before the push it counts nothing, and says so by name. Paths gain `src/gov/close/ratchet.py` and `src/gov/close/state.py` (the owner-entry reading only), `tests/unit/close/test_ratchet*` and `tests/unit/close/test_owner_entry*`.
  - A register entry recorded by the orchestrator under DEC-861 reads as the owner's once its commit is in the pushed ref, and as "recorded, not yet pushed" before [DEC-861, DEC-862].
- **KPIs, failure:**
  - A `Decided-by` trailer alone, on a commit not in the owner's pushed ref, never counts as the owner's (DEC-862 (c): never, it fails open).
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
  - **Batched, ranked, stacked retrieval (DEC-860):** a question whose evidence exceeds one batch is answered in batches, ranked and stacked within the agent's budget, never by one giant query or context. The measure is the share of questions whose stacked context holds all their needed evidence, in order of relevance, across batches, against the owner's target of 99 %.
  - **Both figures in every report (DEC-833):** hit@5 against CAP-10's floor of 85, and the complete-stacked-evidence share against 99 %.
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
- **DEC-761 (owner, 2026-10-17; P-W2-21 (a)), one more round after the failed last review, tests first:** `gov release --lock-from` refuses once the lock records a release, and when the source holds no release record; a lock whose release block was deleted fails; a version tag from a source with no records is refused; `gov release` refuses unless the role is orchestrator (or the owner in a plain terminal), so engineers and auditors never cut or rewrite a release; W1-39's no-files case and W1-32's command list are revised as recorded rewrites with their reasons. Then one review of that change only.
- **DEC-767 (delegated) and DEC-772 (owner, 2026-10-18), W2-16's next round:** the case defect P-R3-2 corrected in one line as a recorded rewrite; **`gov release` is owner-only, from a plain terminal** (refused with a Claude Code ancestor, with `GOV_ROLE` or `GOV_TICKET` set, or without a terminal; a typed one-time code), replacing DEC-761's orchestrator line. The round does only this, tests first, with one review of that change; the allowed paths do not change. The guard's refusal of a `NAME=value` or `env` prefix is W2-42's (W2-H060).
- **DEC-771 (owner, 2026-10-18):** never-recorded sources (P-R3-1, with P-R3-4 and P-R3-5) are W2-17's and W2-18's, not W2-16's; R3-F3 is a residual of W2-16's close.

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
- **DEC-771 (owner, 2026-10-18):** an update from or to a source that has never recorded a release is handled here, tests first, with W2-16's P-R3-4 (the migration document copied again) and P-R3-5 (a shallow source refused).

#### W2-18 Pinned install: a product repository runs a fixed release, never the development copy (STANDARD, engineer)
- **Allowed paths:** `src/gov/install/**` (new), `src/gov/doctor/install*`, `template/governance/kernel/hooks/**` (the import fallback only), `tests/unit/install/**`.
- **KPIs, success:**
  - `gov install <version>` installs the CLI and kernel of a hash-verified release into a per-repository tool environment pinned to the release's wheel hash, never an editable install [CAP-43].
  - `gov doctor` in a product repository fails when its `gov` is an editable install, resolves to another repository's `src/`, or differs from `framework.lock` [CAP-43, W2-H021].
  - The guard and kernel hooks a session runs are the pinned release's code, not the session tree's [W2-M123].
  - The kernel hooks import the pinned `gov`, never a product's own package named `gov`. With no `gov` installed, they say so clearly instead of blocking every call [W2-H032, W2-M279, W2-L172, W2-L230, W2-L173, W2-L174].
  - Two repositories on the machine can run two different releases side by side [CAP-43].
- **KPIs, failure:** a product session that imports this repository's `src/gov` is refused by doctor and reported.
- **DEC-771 (owner, 2026-10-18):** `gov install` refuses to pin a product repository to a lock that shows `release: null`, and a source that has never recorded a release is handled here, tests first.

#### W2-19 Language-agnostic test commands (FULL, engineer)
- **Needs first:** a Rust toolchain for the fixture (an install package under DEC-083, queued Q-6); Node 22 is present.
- **Allowed paths:** `src/gov/close/**` (except W2-66's and W2-68's new modules; W2-48's `cache*` was withdrawn, DEC-880), `src/gov/config/**`, `template/governance/kernel/schemas/path-map.schema.json` (the test-command keys), `tests/unit/close/**`, `fixtures/lang/**` (new: a small Rust and a small TypeScript project).
- **KPIs, success:**
  - A project declares its test commands (for example `cargo test`, `npm test` or `vitest run`, `pytest`), each with its own parallel option, its own result reader, and the input globs W2-66's selection keys on (W2-48's cache was withdrawn, DEC-880). `gov close` and the regression run the declared commands [AR-10, W2-H042, W2-L119].
  - A Rust fixture and a TypeScript fixture each close a ticket with their own command [AR-10].
  - A run that collects or passes nothing counts as unmeasured or failed, never passed [W2-H026, W2-M162].
  - Tests run in a clean checkout of the commit, so ignored and compiled files neither dirty the tree nor reach the run [W2-M253, W2-M159, W2-M160].
  - **The ratchet's field rule, tested (lens H finding 19; DEC-890):** one acceptance case per list (`accepted_reds`, `load_sensitive`): an entry that names no fix is refused by the ratchet's check, naming the entry.
- **KPIs, failure:** an undeclared language in a project with no test command is a named refusal, not a silent pytest run.
- **On EXAMIN's path (DEC-736):** `gov close` runs its regression only over `tests/`, and EXAMIN's suites are elsewhere, so W2-27 needs the declared test commands. It also builds the ratchet baseline of known reds (estimate 300).
- **The ratchet's shrink rule for `load_sensitive` (DEC-762):** the ratchet core W2-53 built reads each `load_sensitive` entry's `fixed_by` (a ticket or a Wave 3 row) and refuses an entry without one; the close of the ticket an entry names refuses while that entry is still listed.

#### W2-20 Machine-wide resource gate (STANDARD, engineer)
- **The values (DEC-742):** at least 4 GiB available, 1-minute load below `nproc`, heavy sessions counting double, at most 8 Gov OS sessions on the machine; taken as configuration, in one place.
- **Allowed paths:** `src/gov/resources/**` (new), `src/gov/launch/gate*`, `tests/unit/resources/**`.
- **KPIs, success:**
  - `gov resources` reads free memory, load, and every live Gov OS session on the machine from a machine-wide registry under `~/.gov-os/machine/`, whichever repository started it.
  - The gate opens or shuts with a named reason.
  - A stale entry (dead PID) is cleared [W2-M244, W2-M188, W2-M262].
  - **The disk (owner, DEC-898 item 1):** the gate shuts below a floor of free space and of free inodes on the shared disk (100 GiB and 10,000,000 by default, in the configuration). `gov launch` refuses a start while it is shut, naming the reading. `gov close` calls the same reading before a close; that call is W2-07's or W2-66's, whose paths hold the close.
- **KPIs, failure:** a session in another repository counts against the gate; a start while the gate is shut is refused with the reading; a launch with the disk below either floor; a gate that reads space but not inodes.

#### W2-21 Stable launch: `gov launch lead`, the ticket-lead role, launch records (FULL, engineer, with a product-spec worker for the role file)
- **DEC-779 (owner, 2026-10-18), priority raised:** W2-21 takes the next free slot after W2-50 closes, ahead of any Track C ticket, so that the leads are sandboxed as early as possible. It leaves the held W2-20's `src/gov/launch/gate*` alone until W2-20 merges. Until W2-21 lands, a guard text-parsing hole that only unsandboxed sessions can reach, or that needs a precondition no session can create through the guard, is a row for every guard ticket.
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
- **DEC-769 (owner, 2026-10-18), leads sandboxed:** first a feasibility test of one to two hours (can a sandboxed lead start a sandboxed worker on this machine?), its result recorded; then leads run in the operating-system sandbox, their worktree writable and `tests/acceptance/**`, every other worktree and every other ticket's folder read-only; the independent test designer writes only `tests/acceptance/<its WBS id>/`. The orchestrator's session stays unsandboxed. DEC-770: once this closes, a guard text-reading hole only an unsandboxed session can reach becomes a row.

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

#### W2-48 Test-result cache at close and in the leads' runs, glued to pytest-testmon, subprocesses seen, a nightly full run (FULL, engineer; DEC-726, DEC-843, DEC-852)
- **WITHDRAWN (owner, 2026-10-21, DEC-880 item 2, P-W2-48-8 (d)).** The cache is not merged; the ticket ends by that decision, not by a clean `gov close`. The lesson, as measured: per-test tracking made almost every test "always run" here, mostly through folder listings (7,076 tests) and reads of undeclared files (3,750), with dot-files (125) and only about 500 child processes the cache could not follow (lens H, finding 12; DEC-889) (run 2: 11.5 % of tests reused, a close 79 min against 81). Branch `w2/W2-48` is kept as the record; its research record is `docs/research/W2-48-cache-choice.md`. Its purpose, a shorter close, passes to **W2-66** (path-scoped regression); DEC-852 item 3's nightly full run stays as W2-66's backstop. The text below is the history of the withdrawn ticket.
- **Priority (DEC-869, owner, 2026-10-20; replacing DEC-823 item 4's place):** it takes the very next free slot after W2-53's close, ahead of every other keystone-2 ticket, the held closes' resumes included: until it lands, every close costs over an hour. Its three conditions stay (DEC-852).
- **Restated by the owner, 2026-10-19 (DEC-843, DEC-852):** the key KPI as behaviour; glued to pytest-testmon and coverage; three conditions added (subprocesses, the leads' runs, a nightly full run). The ticket file `DAEO-xxgp` carries the same lines.
- **Allowed paths:** `src/gov/testcache/**` (new), `src/gov/close/cache*` (the call from close only), `src/gov/close/command.py` (the `--no-cache` option and the call into the cache only; DEC-875), `.coveragerc` (new: subprocess coverage only), `tests/unit/testcache/**`, `docs/research/W2-48-cache-choice.md`.
- **KPIs, success:**
  - **Reuse by behaviour (DEC-843).** Each planted change in an input class re-runs every test that depends on it: an imported module, a fixture or `conftest.py`, a configuration file, a data file the test reads, the interpreter or the dependency lock, the test command and its options. A change outside every input reuses.
  - A reused test is **reused, not skipped.** It is labelled "reused" in the close record (and in a lead's run record), with the run it came from [W2-H044, W2-M153].
  - **Subprocesses (DEC-852 item 1).** The code a test runs in a separate process (`python3 -m gov …`) is seen by the cache, through subprocess coverage configured and tested; otherwise any test that starts a process is always re-run. A test whose code changed never gets a reused result, proven by a test with a change reached only through a subprocess.
  - A test whose inputs cannot all be seen (a dynamic import, a read outside the declared inputs, a network or clock dependency it declares) is never reused: it runs.
  - A failed or errored result is never reused.
  - **Where entries come from.** `gov close` writes the shared entries, in the main tree, from a clean tree at a recorded commit. An entry from a dirty tree is ignored.
  - **The leads' runs (DEC-852 item 2).** A lead's suite runs in its worktree use the same cache with the same rules (exact inputs, failures never reused, `--no-cache` available): they reuse the close's entries, and any entry a lead's run keeps stays in that worktree and is never read by a close.
  - `gov close --no-cache` runs everything. W2-24 and W2-46 run the full, uncached regression (testmon's noselect) and say so in their records.
  - **The nightly full run (DEC-852 item 3).** One command runs the full uncached regression on `w2/integrate`'s head and writes a record naming every test that fails there but whose latest result through the cache was a pass or a reuse. (The orchestrator runs it every night in a quiet window from W2-48's merge; such a test is a P1 package about the cache.)
  - For a declared non-pytest command (W2-19), reuse happens only on its declared input globs; without them, everything runs.
  - **The glue (DEC-843).** pytest-testmon and coverage, one DEC-083 install package (Q-13) raised when the ticket starts; `--testmon-env` set to a hash of the declared data globs and the test command. `docs/research/W2-48-cache-choice.md` records the planted change set's results and the time saved on this repository's suite.
- **KPIs, failure:** each planted change in an input class makes every dependent test run, a change reached only through a subprocess included; a change outside every input reuses. A cache that cannot be read means everything runs, never "passed". A failed result is never reused, in a close or in a lead's run.

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
  - by DEC-778: `src/gov/guard/protected.py` (the option reader for `mv` and `cp -l`), `tests/unit/guard/test_protected*`;
  - `docs/changes/W2-50-CIT-P.md`, `docs/changes/W2-50-CIT-E.md`.
- **DEC-774 (owner, 2026-10-18; P-W2-29 (a)):** run 6's review found D: `cp -b`/`--backup`, `install`, `mv` and `cp --remove-destination` onto a link replace the link, while the guard judged its target. A lead can reach it (no sandbox), so one more short round, tests first: the guard refuses as doubt a replacing write onto a link; the change record gains a section correcting §10; one review of that change; the paths do not change.
- **DEC-778 (owner, 2026-10-18; P-I):** folded into run 7, which had not reached its review: `src/gov/guard/protected.py` uses the option reader W2-50 built for `cp` and `install` for `mv` and `cp -l` too, so the guard reads every copy-like command one way, for writes and for reads. The paths gain `src/gov/guard/protected.py` and `tests/unit/guard/test_protected*`; tests first; the round's one review covers it.
- **DEC-779 (owner, 2026-10-18): run 7 is W2-50's last.** After its review W2-50 closes; any further guard text-parsing finding is a list row unless a launched, sandboxed worker can reach it.
- **DEC-785 (owner, 2026-10-18):** run 7's review failed; its findings are rows W2-H062 (high), W2-M368 and W2-M369, and its probe record is committed as it is (judgement: fail). Whether the probe gate then lets W2-50 close goes to the owner before its close.
- **DEC-790 (owner, 2026-10-18; P-W2-35 (a)):** the resume's fresh probe judges under DEC-779 and DEC-785: a finding already accepted as a row does not fail it. Its passing record makes run 7's failed record an earlier round (W2-M209), so the probe gate passes.
- **DEC-801 (owner, 2026-10-19):** the resume's probe also judges against ADR-0001's threat model; W2-H062, W2-M368 and W2-M369 are Wave 3 rows.
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
- **Widened by the owner, 2026-10-19 (DEC-853, P-W2-49 (a)): the secrets scan at today's sizes, in this ticket's resume** (`src/gov/secrets/__init__.py`, the scan only; its tests):
  - the `secrets-indexing` scan finishes on stores of today's size (`store.db` about 250 MB, `code.db` about 210 MB): the time limit grows with the content's size, or a large store is scanned in bounded chunks each within the limit, and the pool is bounded so that large files are not starved;
  - a store whose hash has not changed since its last clean scan is not re-scanned: the clean result is reused, keyed on the store's hash; a changed store is always scanned in full; **a finding is never reused**;
  - failure: every file is still scanned with every rule set; a scan that cannot finish still fails closed; a store changed by one byte is scanned again in full.

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
- **DEC-786 (owner, 2026-10-18): starts now, stacked on the held W2-49.** It merges every change to W2-49's branch and re-verifies before its own merge, and merges only after W2-49 has closed.
- **Allowed paths:** `src/gov/adopt/lite_gates.py` (new), `src/gov/adopt/stages.py` (the A7 and A10 entries only), `template/governance/kernel/skills/adopt/**` (the A7 and A10 steps only), `tests/unit/adopt/test_lite_gates*`. The engineer writes the skill's steps too (DEC-738 item 1).
- **DEC-800 (owner, 2026-10-19; P-W2-39 (a)):** the paths gain `src/gov/adopt/command.py` (the `STAGES` entries `"A7"` and `"A10"` and the docstring's stage list beside them, only) and `.rulesync/skills/adopt/SKILL.md` and `template/.rulesync/skills/adopt/SKILL.md` (byte copies of the template's adopt skill). `stages.py`'s import line used only by the A7 and A10 routing counts as one of its A7 and A10 entries.
- **DEC-810 (delegated, 2026-10-19):** so does the two-line A7/A10 branch in `stages.py`'s `run()`.
- **DEC-814 (owner, 2026-10-19; P-W2-43 (b)):** the paths gain `.claude/skills/adopt/SKILL.md` (rulesync's output only), regenerated in the resume before its fresh probe.
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

#### W2-54 The context packet's dropped list in a stable order; the context check's declared time limit; the audit-report type (FULL, engineer; DEC-768)
- **Why:** W2-53's close refused on context-reproducibility (DEC-768). Run alone, the check takes 122 seconds against the 60 seconds a check without a declared limit gets, and fails on 15 tickets: two computations of a ticket's context give its `dropped` list in two orders, so two hashes. It refused on core-schema too: the W1-43 audit report states no `type` (P-W2-28).
- **Starts** right after the owner's commit of DEC-768, alone; W2-53 is closed again after it.
- **DEC-773 (owner, 2026-10-18; P-W2-30 (a)):** the first round showed that the two computations hold different items, not only two orders: the embedder returns a slightly different vector for a text after a different text. One more round, tests first, one review: the paths gain `src/gov/retrieval/semantic.py` and `tests/unit/retrieval/**`; query vectors are stored, keyed by model, model revision and exact text, so the same text always gets the same query vector; whether an embedder setting (thread count, seed) also removes the variation is measured first and recorded, and the stored vectors are used regardless. W2-15a's baseline is taken with this behaviour.
- **DEC-798 (owner, 2026-10-19; P-W2-40 (b)):** run 3b found the shared GPU Ollama's vector depends on the prompt computed before it. One more round: a CPU-only embedder that `gov` starts on its own port answers query embeddings only, and the shared GPU runner keeps building the index (no request to it names `num_gpu: 0`); the cache key names the device; the paths gain `src/gov/retrieval/ollama.py` (the CPU-only embedder only); DEC-261 is amended. W1-21's hit@5 is re-measured before the merge, and a figure below its pass line of 80 is a red for this ticket, not a rewrite.
- **DEC-782, DEC-784 (owner, 2026-10-18; P-W2-32 (a), P-W2-34 (a)):** one more round, tests first, one review. A read command may write the query-vector cache, and only that file, under the limits of the KPIs below (DEC-379 amended for it). The W1-19 and W1-21 cases that depended on the old, varying vectors are rewritten with a `Rewrite-Reason:` and their figures before and after; no pass line is lowered. W1-46's fixture removes every CLAUDE* variable before it launches a session, in this round's test-design batch.
- **DEC-811 (delegated, 2026-10-19):** the paths gain `tests/unit/semantic/test_semantic.py` (the stub's fixture only); the query embedder's interface is `GOV_QUERY_OLLAMA_HOST`, default `127.0.0.1:11435`.
- **Allowed paths:** `src/gov/context/**`, `template/governance/kernel/checks/context-reproducibility.yaml` (the `timeout-seconds` line only), `src/gov/check/schema.py` (the `audit-report` type only), `template/governance/kernel/schemas/audit-report.schema.json` (new), `tests/unit/context/**`, `tests/unit/check/test_schema_audit_report*` (new), `docs/changes/W2-54-CIT-E.md`; and, by DEC-773, `src/gov/retrieval/semantic.py` (the query vector) and `tests/unit/retrieval/**`. The two kernel files are approved by DEC-768 (CAP-33).
- **KPIs, success:**
  - Two computations of any ticket's context in one store give one hash: the `dropped` list is sorted stably with a full tie-break, whatever order retrieval returns tied items in [DEC-768].
  - The same text always gets the same query vector, whatever was embedded before it: query vectors are stored, keyed by model, model revision and exact text [DEC-773].
  - The query-vector cache is the one file a read command writes: a derived file under `.gov-runtime/`, keyed by model, model revision and a hash of the exact text, written atomically and safely by several sessions at once, bounded in size, and rebuildable from nothing [DEC-782].
  - Where the cache cannot be written (a sandboxed worker, whose `.gov-runtime` is read-only), the same text still gets the same vector; a test shows it inside a launched, sandboxed worker [DEC-782].
  - On the shared GPU Ollama, the same text read many times, after different texts and by two sessions at once, gets one vector: query embeddings come from the CPU-only embedder on its own port, the shared runner is never moved to the CPU, and the cache key names the device [DEC-798].
  - W1-21's hit@5 on the real models, with CPU query vectors against the GPU-built index, is at or above its pass line of 80; the figure is recorded in the change record [DEC-798]. (Kept with its reason, DEC-866: DEC-833 item 1 has W2-32's test designer raise W1-21's and W2-54's line to 85; until then 80 stands.)
  - W1-46's live cases launch their sessions with no CLAUDE* variable in the environment [DEC-784].
  - The context-reproducibility check declares a time limit that fits its measured run on this repository; the measurement (the run's seconds, the tickets measured, the machine's load) is recorded in the change record [DEC-768].
  - `gov check` gives context-reproducibility green on `w2/integrate` [DEC-768].
  - **The `audit-report` type exactly as W2-02 defines it on `w2/W2-02` (`2a35fd7b`)** [DEC-768 item 1]: its schema file byte for byte as W2-02's; in `src/gov/check/schema.py`, W2-02's lines for that type (its `SCHEMA_MAP` entry, the type among the standalone types, the audit-report folder `docs/audit` and its reading of a record there that states no `type` as an audit report), nothing of W2-02's other types; so W2-02's later merge adds nothing new for this type. Core-schema is green on `w2/integrate`, with the W1-43 audit report's body untouched.
  - **DEC-874 (delegated, 2026-10-20):** "nothing of W2-02's other types" is about W2-54's own change, not the tree: its four cases (three acceptance, one unit) assert that W2-54's own commits bring in no schema file or type of W2-02's beyond `audit-report`, which holds before and after W2-02's merge. Corrected in W2-54's resume (run 5), each with `Rewrite-Reason: DEC-874`.
- **KPIs, failure:**
  - A context whose items or hash differ between two computations still fails the check, naming the ticket.
  - A check that runs past its declared limit still fails; no hard-block check is weakened [DEC-768 item 4].
  - A record outside `docs/audit/` that states no `type` still fails core-schema; an audit report that lacks `milestone`, `commit` or `pack_sha256` fails it, naming the field.

#### W2-24 Track A gate run (FULL, orchestrator)
- **DEC-813 (owner, 2026-10-19):** does not start before W2-57 (W1-46 robust under load) has closed.
- **Allowed paths:** `docs/plan/wave-2/track-a-gate/**` (evidence); fixture clones under `~/gov-os-runs/W2-24/`.
- **KPIs:**
  - **The quality-control check of 2026-10-18 is repeated, sections (a) to (f), with evidence (counts, paths, commits)** [DEC-794]. Sections (a) (workers sandboxed through `gov launch`) and (d) (`gov retrieve` correct and deterministic on this repository) gate W2-27.
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
- **DEC-794 (owner, 2026-10-18):** W2-27 does not start unless W2-24's repeat of the quality-control check gives sections (a) and (d) green: workers sandboxed through `gov launch`, and `gov retrieve` returning correct, deterministic results on this repository.
- **DEC-799 (owner, 2026-10-19):** and W2-56 has closed.
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
- **DEC-833 item 1 and DEC-866 (the sweep of 2026-10-20):** its independent test designer raises every pass line of 80 to CAP-10's 85, with `Rewrite-Reason: DEC-833`: W1-19's `HIT_AT_5_PASS_LINE` (`tests/acceptance/W1-19/w1_19_support.py:92`) and its test, W1-21's (`w1_21_support.py:100` and its dev-tier and family-check cases), W2-54's change-record case (`test_w2_54_cpu_embedder.py:413, 434`); and the engineer the retrieval check's own baseline (`src/gov/retrieval/retrieve_baseline.yaml:4`, `retrieve_check.py:41`). Until then the 80 lines stand, with this reason.
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
- **DEC-812 (delegated, 2026-10-19):** the paths gain `src/gov/check/commands.py` (the line recording `impact` only) and, for its test designer, W1-07's command lists and W1-32's command-set assertion (`impact` only). The resume after W2-03 closes fixes the second review's A and B (no third round now, DEC-802) with C, E and F4 riding along; its fresh probe reviews them.
- **DEC-816 (owner, 2026-10-19; P-W2-44 (a); CAP-33):** the paths gain the impact-assessment section of `template/governance/kernel/skills/change/SKILL.md` and of its copies `template/.rulesync/skills/change/SKILL.md`, `.rulesync/skills/change/SKILL.md` and `.claude/skills/change/SKILL.md` (rulesync's output), routing the question to `gov impact`, in the resume.
- **DEC-815 (owner, 2026-10-19; P-W2-45 (a)):** the depths of R0/R1, R2 and R3 are 1, 3 and 8 hops; `depth_source` names DEC-815 (`readings.py`), set in the resume.
- **KPIs:**
  - A decision change raises a CIT-P that lists the affected specifications, decisions, tickets, tests and code from both graphs, with a radius [CAP-33.b, W2-M285].
  - After apply or archive, the CIT-E record matches the proposal or lists the differences [W2-L319].
  - "What's the impact of X?" in plain language runs `gov impact` [CAP-33.g, DEC-167].
  - It also takes the S0b2 glue G-16 (id mapping) and G-24 (deletable-class join).
- **DEC-859 (owner, 2026-10-20; standing), in the resume:** the paths gain `src/gov/codeintel/**` (the accepted plan's widening, §4.4).
  - Agents' questions use the code-graph tool's own traversal (`trace_path`, `search_graph`, `query_graph`), with small, targeted answers; the wrapper never loads the whole graph to answer a question; the tool's error is passed through.
  - Whole-graph jobs (a full impact map, an audit of every dependency) read the graph in pages, never one query over the tool's row cap.
  - On large repositories, a job may be split by module or folder, and its parts queried in parallel.
  - **KPIs:** no query ever exceeds the cap, tested on this repository (28,923 nodes and 117,939 edges on 2026-10-19, after DEC-856) and on a large synthetic repository well over the cap; the callers of `rrf` and `indexable` are answered on this repository.
  - The lead commits these lines to the ticket file first, in its worktree.

#### W2-38 Profile from impact; impact-selected tests at close (FULL, engineer)
- **Wave 3 (DEC-841), except its lite form:** path-scoped regression at close comes back into Wave 2 as **W2-66** (owner, 2026-10-21, DEC-880 item 2). The profile from impact and `gov impact`'s selection stay here, for Wave 3; W2-48's cache, which the KPI below builds on, is withdrawn.
- **Allowed paths:** `src/gov/impact/profile*`, `src/gov/close/select*`, `tests/unit/impact/**`, `tests/unit/close/test_select*`.
- **KPIs:**
  - An R0 change runs only the LITE checks, and an R3 change raises the FULL gate and readiness rows, with the profile computed by `gov impact` [CAP-53.b].
  - A close runs the tests `gov impact` names, on top of W2-66's path-scoped selection (W2-48's cache was withdrawn, DEC-880). The full suite runs at milestones and in CI [W2-H043, W2-M240, W2-M241, W2-M163].
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
  - **A leading `NAME=value` assignment or an `env` prefix in front of any `gov` command is refused, with a reason** (`GOV_ROLE=orchestrator gov release`, `env -u GOV_ROLE gov release`) [W2-H060, DEC-772].

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
  - **`openspec-validate` measures something or says it does not apply:** real openspec content that it validates, or an owner decision that declares it not applicable here, stated by the check; never silently yellow [W2-H061, DEC-781].
  - A hard-block key is covered only by a check of hard-block tier [W2-M211, W2-M259].
  - The time limit is stated and tested [W2-M151].

#### W2-55 Decisions tagged by domain, status and scope (STANDARD, engineer; DEC-791)
- **Why:** the register is about 244,000 tokens (783 entries). Superseded and amended entries are not marked as such, and nothing says which decisions are kernel-wide; agents see all of it (the quality-control check, 2026-10-18).
- **Starts** after W2-03 closes (it owns `src/gov/decisions/**` and `src/gov/records/**`). It shares `src/gov/context/**` with W2-04 and `src/gov/retrieve/**` with W2-13: it runs after them, or stacked under DEC-786.
- **Allowed paths:** `src/gov/decisions/**`, `src/gov/context/**` (the decisions filter only), `src/gov/retrieve/**` (the decisions filter only), `template/governance/kernel/schemas/decision*`, `tests/unit/decisions/**`, `docs/research/W2-55-backfill.md` (the proposed backfill).
- **KPIs, success:**
  - Every register entry has a domain from the closed list (guard, close, retrieval, context, adopt, launch, checks, plan, roles, records, release), a status that names what superseded or amended it, and a scope (this repository, or kernel-wide) [DEC-791 (i)].
  - `gov context` and `gov retrieve` leave out superseded and done entries, and say how many they left out [DEC-791 (i)].
  - The backfill is a proposal: every entry's proposed tags with the reason for each, and a sample drawn for the owner's review; nothing is applied before the owner accepts it [DEC-791 (i)].
- **DEC-866 (owner, 2026-10-20; standing): supersession propagates.** A check fails when anything (a test, code, a skill, a brief, a ticket's KPI, the prompt, the path map) still enforces a superseded or changed decision without a recorded reason: each superseded entry's status line names the entry that replaced it, and every place that cites or enforces the old one is either updated to the new decision or listed with its reason in the register. The sweep of 2026-10-20 (`governance/project/orchestration/packages/SWEEP-2026-10-20.md`) is its first fixture: W1-49's two window cases and W2-59's three earlier cases are what it must find.
- **KPIs, failure:** an entry with no domain, status or scope fails the decisions validator, naming it; a superseded entry that still reaches an agent's context fails a test; a test or check that enforces a superseded decision with no recorded reason fails the new check, naming both decisions and the place.

#### W2-56 `gov launch` usable for every worker (FULL, engineer; DEC-799)
- **Why:** the `gov launch` trial (DEC-789): the sandbox refuses writes outside the worktree and lets git commit, but a worker cannot run a suite that builds the code graph, because `/tmp/gov-cbm-<uid>` is read-only inside the sandbox (`DAEMON_BASE`, `src/gov/codeintel/__init__.py:35`). A worker's script can write anywhere in its worktree, the launcher's `.gov-runtime/` deny rules are patterns that the Linux sandbox skips, and placeholder files (`.bashrc`, `.gitconfig`, `.mcp.json` and others) appear in a worktree while a sandboxed worker runs.
- **Starts** with high priority: the first free slot after W2-50 and W2-05 close (both change files it needs), ahead of Track C. It shares `src/gov/launch/launcher.py` with W2-21: W2-56 runs first, and W2-21 after it or stacked on it (DEC-786). **Closes** before W2-27 starts (DEC-799).
- **Allowed paths:** `src/gov/codeintel/__init__.py` (the daemon's folder only), `src/gov/launch/**` (the sandbox settings the launcher writes), `tests/unit/launch/**`, `tests/unit/codeintel/**` (the daemon's folder only), `docs/changes/W2-56-CIT-E.md`. A file outside them that the placeholder KPI needs is a package.
- **KPIs, success:**
  - Inside a launched, sandboxed worker, a suite that builds the code graph runs: the code graph's folder is under the session's own temporary folder, and outside a sandbox it stays where it is [DEC-799].
  - The sandbox's write list is the ticket's allowed paths plus git's folders: a worker's script writing a file outside them, `.gov-runtime/` outside the session's scratch included, is refused by the operating system [DEC-799, DEC-789].
  - No placeholder file that the sandbox makes can reach a commit [DEC-799].
- **KPIs, failure:** a write outside the list from a script still fails; `/tmp/gov-cbm-<uid>` is never on the write list (DEC-799 item 2); a launch whose sandbox cannot be built still refuses to start.

#### W2-57 Load out of the close: the rulesync probe, the serial-only list, and a route out for every list entry (FULL, independent-test-designer then engineer; DEC-813, DEC-823, DEC-883 item 5, DEC-889 item 5, DEC-892 item 2; lens I's P-IS-6)
- **Why:**
  - The serial phase takes about 31 minutes of every close, and most refused closes since 2026-10-20 came from listed cases or load-caused reds.
  - The rulesync probe's 10-second limit turns load into reds, greens and a silent skip of up to 181 W1-38 cases. That is a live fail-open (I4 F2).
  - **This card replaces DEC-813's KPI.** That KPI had W1-46's live cases pass under the close's parallel load; DEC-889 item 5 moves live and real-model tests to the nightly instead (I2 F14).
- Ticket `DAEO-cy5o`. **Starts** in a free slot after the review point, the probe first (DEC-892 item 2). It **closes** before W2-24 starts (DEC-813).
- **Allowed paths (widened, I2 F12):**
  - `src/gov/adapters/portability.py` and `src/gov/doctor/command.py` (the probes only);
  - `src/gov/close/serial.py` (new: the serial phase and its reasons);
  - `tests/acceptance/serial-only.txt`;
  - W1-30's r11 and r13 files;
  - `tests/acceptance/W1-38/**`, `W1-07/**`, `W1-46/**`, `W1-50/**`, `W1-02/**`;
  - W1-33's `w1_33_support.py`;
  - `tests/acceptance/W2-57/**`;
  - `tests/unit/close/test_serial*`, `tests/unit/adapters/test_portability*`;
  - `docs/changes/W2-57-CIT-E.md`.
- **KPIs, success:**
  - **The probe's four effects (P-I4-5 (a)):**
    - a limit a loaded machine meets;
    - W1-38's fixture fails, never skips, on a timeout;
    - the 9 cases a timeout satisfies assert the reason;
    - W1-33's research case fails the same way;
    - 0 rulesync skips or timeouts in three closes' worth of parallel runs.
  - **The doctor probes:** limits a loaded machine meets, with failure text kept (W1-07 `[doctor]`).
  - **The serial-only list reworked as P-IS-6's table:**
    - every kept entry names its reason;
    - W1-16's 94 non-daemon cases, W1-09's two races and W1-50's read-merge case run in parallel;
    - the live and real-model files move to the nightly;
    - latency cases stay alone.
  - **Revisions:** W1-30's r11 test reads the reworked list. Also W1-30's r13 limit, W1-50's `CLAUDE*` removal (DEC-784), a p95 case for a designer's read, and W2-M332's timing without the memory sampler.
  - **The close's resource gate** covers W1-02's 5-second bound and the guard's 20-second deadline. The network check probes through the session's route.
  - **Then the orchestrator commits the removal** of every entry this ticket makes unnecessary (DEC-861).
  - **Already removed** by the owner's commit (DEC-899 item 3): W1-02's and W1-05's p95 entries. Their cases stay alone in the serial phase, and W2-M332 keeps its date before W2-24.
- **KPIs, failure:**
  - a timeout that skips or passes a case;
  - a serial entry without a reason;
  - a live file left in the close;
  - a case weakened, skipped or serialised by marker alone;
  - a list entry added.
- **Until it lands:** the close queue checks that each close's skip count equals the expected 31 (the orchestrator's interim guard).

#### W2-58 Policy 2 in the guard and the launcher: reads open, four refusals (STANDARD, engineer; DEC-820, DEC-821; keystone 3)
- **Why:** the owner's Policy 2 (DEC-820) opens reads to everything but four things, and needs two refusals the guard does not make yet: the counterpart's work on the same ticket (c), and the hidden half of an evaluation set (d). The listing refusals of DEC-508 go. The change is approved by the owner in DEC-821 (CAP-33).
- **Starts straight after W2-50 merges, ahead of every other start (DEC-857, owner, 2026-10-19):** the read refusals block the orchestrator's own work. Before the workers keystone 4 starts.
- **Widened (DEC-857 item 3):** the two files the guard protects by constant (`src/gov/guard/heldout.py:19-21`: the held-out list file and the settings file) are what today's refusals turn on; the KPIs below name both: the held-out list file's names readable and the held-out material's contents refused; the settings file's reads under Policy 2; searches from the repository root or `governance/project/` no longer refused for the files' sake. It shares `src/gov/guard/**` and `src/gov/launch/**` with W2-56 and W2-21: it runs before them, or stacked under DEC-786, as the plan orders.
- **Allowed paths (narrowed at its start, DEC-864: the read rules live in three files, and W2-05's unmerged branch changes `containment.py`):** `src/gov/guard/protected.py`, `src/gov/guard/heldout.py`, `src/gov/guard/decide.py` (the read rules only), `src/gov/guard/reads.py` (new, if needed), `src/gov/launch/**` (the sandbox's read denials only), `governance/project/path-map.yaml` (an `evaluation_sets` block only, reviewed by the orchestrator, DEC-861), `template/governance/kernel/schemas/path-map.schema.json` (the same block), `tests/unit/guard/**`, `tests/unit/launch/**`, `docs/changes/W2-58-CIT-E.md`.
- **KPIs, success:**
  - A session of role `engineer` on ticket T is refused reads of `tests/acceptance/<T's W2 id>/**` by the guard, on every tool read and the read side of every Bash route an honest agent takes (no OS-level Read rule for it, DEC-873), and can still run those tests with pytest and see their names, results and failure messages [DEC-820 (c)].
  - **DEC-873 (owner, 2026-10-20, P-W2-58-1 (a)):** the launcher adds no OS-level Read deny rule for (c) or (d), because running a test means reading it; the held-out material's Read rules (b) stay in the sandbox; a launch under a malformed `evaluation_sets` block is refused. A program run deliberately to evade the guard is Wave 3 row W2-L374.
  - A session of role `independent-test-designer` on T is refused reads of the files T's branch changes against its base, other than its own tests, and reads the base's version of existing code [DEC-820 (c), DEC-826 Q2].
  - An evaluation set declared in the path map with a visible and a hidden part: a session measured by it is refused reads of the hidden part, and the measurement script scores it without showing the answers [DEC-820 (d)].
  - The listing and search refusals over `governance/` and `.claude/` (DEC-508) are gone; the held-out material's file names are readable and its contents refused; secrets stay refused [DEC-820 (a), (b)].
  - Reviewers and auditors read everything, tests and code alike [DEC-820].
  - **DEC-880 (owner, 2026-10-21, P-W2-58-4 (a)): one narrow extra round, an exception to DEC-413.** A path with a leading `~` is judged as its expanded form in every path the guard judges (Read, Grep, Glob, Edit, Write and Bash), one test per tool; an engineer's `python3 -B -m pytest` and `coverage run -m pytest` of its own tests are allowed; full verification; a third review limited to the change; then the merge, ahead of everything (DEC-857). `decide.py`'s paths widen to the `~` expansion of every judged path.
- **KPIs, failure:** each of (a) to (d) still refuses, by every read route an honest agent takes in ordinary work (DEC-801); no write rule widens; a guard error still fails closed.

#### W2-59 The pinned judge: the declared checks and the hook lines run from the pin; the packaging gaps (STANDARD, engineer; CIT-P; DEC-822, DEC-835, DEC-854; keystone 1)
- **Why:** the bootstrap pin's dry run and its `gov check` of 2026-10-19: `src/gov/check/runner.py`'s `_run_command` runs each declared check as `python3 -m gov.check.*` with the working tree's `src` first on `PYTHONPATH`, and the hook lines do the same, so a ticket that edits the checks changes the checks that judge it (ordinary work: yes; fails open). The pin's `secrets-indexing` ran from `/home/usain/Dynamic-Agentic-Engineering-OS/src/gov/…`.
- **Starts** now (DEC-854), beside W2-05, whose unmerged branch changes `_run_command`'s environment (`env = git_env(root)`) and the git calls in `runner.py` and `retrieve_check.py`: the engineer keeps its edit of those lines small and composable; W2-05's resume takes the conflict.
- **Allowed paths:** `src/gov/check/runner.py`, `src/gov/retrieval/canary.py`, `src/gov/retrieval/retrieve_check.py`, `src/gov/cli/main.py` (the version only), `pyproject.toml` (package data only), `.rulesync/hooks.jsonc` (the hook command lines' interpreter only; owner-approved, DEC-822 step 2; the generated settings file is regenerated by the owner), `tests/unit/check/**`, `tests/unit/cli/**`, `tests/unit/retrieval/**` (the canary and baseline cases only), `docs/changes/W2-59-CIT-P.md`.
- **KPIs, success:**
  - The runner runs every declared check with the pinned interpreter and package; only the code under test comes from the tree (DEC-822 item 3).
  - The hook command lines call the pin's environment (DEC-822 step 2), after the independent test designer has checked W1-38's hook-source tests against the change.
  - Every module that finds the repository from its own install path finds it from the project root instead (today `src/gov/retrieval/canary.py:10` and `src/gov/retrieval/retrieve_check.py:16`), proven from an installed wheel (DEC-835).
  - `retrieve_baseline.yaml` is shipped as package data, proven from an installed wheel (DEC-835).
  - `gov --version` names the version and the commit.
- **KPIs, failure:** a check edited in the tree does not change the verdict of the pinned judge; a wheel without the data file fails the build or its test; a module that still reads the repository from its install path fails a test.
- **After it merges,** the owner re-pins at its merge commit, which must also hold W2-50's secrets fix (DEC-853 item 4).
- **Held unmerged (DEC-884, owner, 2026-10-21):** it merges together with W2-65 just before the one combined re-pin, after W2-66 is merged and trialled; first it merges `w2/integrate` back, with trailers, and is re-verified. Merged earlier, it would make the hooks call today's pin, which predates W2-58, and bring the old read refusals back; an earlier merge needs a package to the owner first. The owner re-pins once, at the combined merge commit (W2-58, W2-59, W2-65, W2-66).

#### W2-61 The standing 20-question measure, split under Policy 2 (d) (STANDARD; the questions by an independent auditor session, the script by an engineer; DEC-828, DEC-833, DEC-860; keystone 4)
- **Why:** the accepted plan's §4.4, order 6 (DEC-828 item 4): lens B's 20 questions become the standing measure at each release and on EXAMIN's copy. Ticket file at its start (DEC-825 item 7).
- **KPIs, success:**
  - Lens B's 20 questions and their gold answers (`docs/assessment/2026-10/B-memory-retrieval.md` §2) are the visible development half.
  - A hidden measurement half of 20 more questions is written by a session independent of the retrieval tickets, stored where W2-58's `evaluation_sets` block refuses it to the measured roles (DEC-820 (d)).
  - A measurement script reports the governing source in the first five and in the bundle, and repeatability on an unchanged index and after a rebuild; it prints scores, never the hidden answers.
  - **Both figures (DEC-833):** hit@5 against CAP-10's floor of 85, and the share of questions whose stacked context holds all their needed evidence, across batches, against the owner's target of 99 %.
  - **Stacked, never giant (DEC-860):** each question is answered by retrieval in batches, ranked and stacked within the budget, never one giant query or context; the script measures the stacked answer.
  - The same split for EXAMIN's set (DEC-828 item 3), written before W2-27; EXP-003's gold answers (W2-15a, W2-15b) split the same way.
- **KPIs, failure:** a measured role cannot read the hidden half by any route an honest agent takes; the script never prints a hidden answer; a figure is never reported without the other.

#### W2-64 W2-02's widening: the record validator through check-jsonschema; `docs/imported/` out of the schema check (STANDARD, engineer; DEC-831, DEC-844, DEC-872; keystone 4, order 1)
- **Why:** the accepted plan widened W2-02 (§5 and §4.4 order 1; lens G R2 (a), F2: the 169-line subset validator passes what the schemas refuse, which fails open). DEC-872 moved the widening out of W2-02's resume, so that W2-02's close-record type reaches every close sooner. Ticket file at its start.
- **Starts** after W2-02 merges (it holds the same paths: `template/governance/kernel/schemas/**`, `src/gov/check/schema.py`, `tests/unit/check/test_schema*`).
- **KPIs, success:**
  - `core-schema` validates every record against its schema through check-jsonschema (pinned in the tool registry), not a subset; lens G's planted ticket (a field the schema refuses that the subset passed) is refused [lens G R2 (a), F2].
  - `docs/imported/` is left out of the schema check, as history (DEC-844), and the check says so by name.
  - Every record on `w2/integrate` today, the close records of `docs/close/` included, still validates.
- **KPIs, failure:** a record that its schema refuses fails `core-schema`, naming the record and the rule; check-jsonschema missing or failing to run is RED, never green.

#### W2-65 The guard's hook lines refuse a call when the guard program cannot run (LITE, engineer; DEC-880 item 3; keystone 1)
- **Why:** P-W2-59-8 (W2-59's second review, R2-D1): Claude Code blocks a PreToolUse call only on exit 2 or a deny decision, and the hook lines pass their program's exit code on, so a guard program that cannot run (a half-finished edit) exits 1 and the call goes through. Ordinary work, fails open; it predates W2-59. Ticket `DAEO-e82f`.
- **Starts (DEC-884):** built stacked on `w2/W2-59` (both change `.rulesync/hooks.jsonc`; DEC-786), in a slot W2-66 does not need; it merges together with W2-59 just before the one combined re-pin, and the owner's settings regeneration follows the re-pin.
- **Allowed paths:** `.rulesync/hooks.jsonc` and `template/.rulesync/hooks.jsonc` (the preToolUse and containment lines' exit mapping only), `tests/unit/hooks/**`.
- **KPIs, success:** the preToolUse and containment lines end with exit 2 whenever their program ends with anything but 0 or 2, naming the program; 0, 2 and a deny decision pass through; the template's hook source does the same; one acceptance case per line.
  - **P-H-7 rides along (DEC-889 item 8):** the SubagentStop hook gives its block reason as Claude Code reads it (on standard error, or as `{"decision": "block", "reason": …}`), so a helper whose final message lacks the twelve fields learns what is missing; one acceptance case.
- Its paths gain `template/governance/kernel/hooks/subagentstop.py` (P-H-7, DEC-889).
- **KPIs, failure:** a program that exits 1 or cannot start lets the call through; a line that turns exit 0 into a refusal.

#### W2-66 Path-scoped regression at close: selection and evidence, the lite W2-38 (FULL, engineer; DEC-880 item 2, DEC-889, DEC-890, DEC-892, DEC-896; keystone 2)
- **Why:** W2-48's cache saved 3 %, because per-test tracking made almost every test "always run" here. The measured causes were folder listings (7,076 tests), undeclared reads (3,750), dot-files (125) and only about 500 child processes (DEC-880, DEC-889 item 11 d). So a close runs what the change can affect, and the full regression and the nightly run are the backstop. Batching, reuse and fingerprints are W2-68's (DEC-890). Ticket `DAEO-c1uz`; it takes in W2-H044 and W2-M153.
- **Place:** the first slot (the review point passed, DEC-899). Both it and W2-07 ride the first re-pin.
  - **The merge order (DEC-899 item 2):** built in parallel with W2-07; **W2-07 merges first.** Then W2-66 merges `w2/integrate` back, re-verifies and gets a fresh FULL probe on the merged head before the re-pin.
- **Allowed paths:**
  - new: `src/gov/close/select.py`, `src/gov/close/nightly.py`, `src/gov/close/evidence.py`;
  - `src/gov/close/command.py`: the calls, `--full` and the record's lines only;
  - **the test map:** `governance/project/test-map.yaml`, its schema `template/governance/kernel/schemas/test-map.schema.json`, and the template's copy (DEC-896 item 2: the path map is named by no ticket);
  - `tests/unit/close/test_select*`, `test_nightly*`, `test_evidence*`;
  - W1-30's regression files (one named revision);
  - `docs/research/W2-66-scoped-close.md`.
- **KPIs, success:**
  - **Selection:** a close runs the ticket's own suite, `tests/unit`, and the suites of every ticket whose `allowed_paths` overlap the change since the last fully green commit. It follows test-side imports, selects in the full run's form, and the record names each suite and why.
  - **The shared core runs everything (P-IS-1 (a)):**
    - `src/gov/close`, `guard`, `check`, `records`;
    - the retrieval core's eight modules;
    - both hook copies;
    - the path map and the test map;
    - DEC-892 c's three widest modules;
    - `src/gov/cli/main.py` and `src/gov/errors.py`, until measured.
    An unplaced file or a missing map also runs everything.
  - **The couplings that imports cannot see** are declared in the test map (text reads, the rerank worker's process, the hook copies, fixture inputs, declared checks). W1-07's three contract files run on every close.
  - **The serial-only tests** are scoped by the same selection.
  - **The record-reading set runs on every head (P-IS-2 (a)):** every test that reads a declared record-only path is in it, from a first list in the test map. The record-only paths are exactly DEC-891's list. It reads the pre-close gate's own `gov check` result.
  - **The evidence block:** scope, base commit, head, tree, what ran, what was left out and why, every skip and the skip count, failure text kept, and the JUnit XML (schema line in W2-64).
  - **The rest:**
    - `gov close --full`, which W2-24 and W2-46 use;
    - per-test limits (pytest-timeout, signal method, above the slowest test);
    - the distribution mode as a setting, with worksteal off until the nested reruns are gone (P-IS-3);
    - the nightly command (failures re-run alone, `git bisect run`, a scoped miss as a P1 with the map corrected, the weekly coverage map);
    - the time measured and the 15-minute target's scope stated;
    - the lead's verification unchanged.
  - **The test designer revises** W1-30's `test_regression_includes_other_acceptance_folders` (a valid case this ticket turns red).
- **KPIs, failure:**
  - less than the full regression for the shared core, an unplaced file or a missing map;
  - a scoped record that says full;
  - an unreported skip, left-out suite or failure;
  - a record-reading test outside the set;
  - a record-only list that hides code;
  - a hung test holding the close;
  - worksteal before the nested reruns are gone.
- **Ladder:** its FULL review; a fixture trial (a shared-core change runs everything; a one-module change runs its suites; a record-only commit runs the set); then the first re-pin (DEC-896).

#### W2-69 The secrets check reads what the stores hold: no chance red from where a scan begins (FULL, engineer; DEC-897; keystone 2)
- **Why:**
  - The secrets-indexing check, a hard-block check, feeds a store's content to `gitleaks stdin` as one input.
  - A read of gitleaks that begins inside a word makes a rule's leading word boundary match there, so a fragment of a longer identifier is taken for a token. Where the reads begin moves with every rebuild, so any rebuild can turn `gov check` and a close RED by chance.
  - W2-62's queue of 2026-10-22 stopped this way (P-W2-62-G1: a `gov-token-lower` hit, 62 bytes inside an 84-character identifier, in no tracked file).
  - Ticket `DAEO-rmbe`; it takes in W2-M404.
- **The design question (owner, DEC-897 item 1):** should the check scan the indexed text (the rows, as text) instead of the raw database bytes? That option comes with:
  - each store compacted (`VACUUM`) after each rebuild, so no deleted text survives in free pages;
  - a boundary-aware raw scan kept only as a backstop.
  The tests decide; the answer and its evidence go in `docs/research/W2-69-secrets-scan.md` before the code. Row W2-M395 (W2-45) is settled by the choice or left to W2-45 with a reason.
- **Place:**
  - Rides in the first re-pin (W2-58, W2-59, W2-65, W2-66, W2-07; DEC-896).
  - Starts in a free slot after W2-50's run 9 returns (W2-50 shares `src/gov/secrets/__init__.py`).
  - Until it is pinned, DEC-897 (b) allows one proven re-run of a close's queue per close.
- **Allowed paths:**
  - `src/gov/secrets/**`;
  - `src/gov/rebuild/command.py`: the compaction step after each store's build only;
  - `tests/unit/secrets/**`, `tests/unit/rebuild/test_compaction*`;
  - `docs/research/W2-69-secrets-scan.md`.
- **KPIs, success:**
  - A real token is found at every offset and in every form the stores hold it (a stored value, a row read as text, UTF-16 text, across every read or split boundary), at a word boundary as the rule defines it.
  - An embedded fragment of a longer identifier is not flagged, at every offset relative to any read edge, for every rule with a leading word boundary.
  - Deleted text does not survive a rebuild: neither in the rows nor in free pages.
  - The design question is answered with evidence.
  - Every file under `.gov-runtime/` scanned today is still scanned, with every rule set. A scan that cannot finish fails closed. DEC-853's clean-result reuse stays, and a finding is never reused.
- **KPIs, failure:**
  - a real token missed at any offset or in any form;
  - a word-internal fragment flagged at a read edge;
  - deleted text left in free pages after a rebuild;
  - a file the check scanned before no longer scanned;
  - an unfinished scan passing as clean.

#### W2-70 Retire the two nested reruns: W1-05's switch-over case and W1-47's builder rerun (LITE, independent-test-designer; DEC-899, P-IS-3 (a))
- **Why:** W1-05's switch-over case re-runs three suites the same close has already run (14.6 minutes of every close). W1-47's builder case re-runs `tests/unit/guard`. Both block worksteal (I1 F-5, DEC-892 a). Ticket `DAEO-uzme`.
- **Starts now; merges early; closes** once W2-07's test-revision class is pinned (DEC-896 item 3), as W2-63 does. The 15 unit nested runs are bounded in W2-67.
- **Allowed paths:** `tests/acceptance/W1-05/**`, `tests/acceptance/W1-47/**`, `tests/acceptance/serial-only.txt`, W1-30's r11 file.
- **KPIs, success:**
  - both cases retired in one commit with a `Retire-Reason:` naming DEC-899;
  - the switch-over line out of `serial-only.txt`, and W1-30's r11 test updated;
  - the suites they re-ran still run as themselves.
- **KPIs, failure:**
  - a covered suite that no longer runs;
  - any other test changed.

#### W2-68 Batched closes, reuse on the same code, and two fingerprints (FULL, engineer; DEC-883, DEC-889 item 2, DEC-890; keystone 2)
- **Why:** the queue of 2026-10-21 ran six closes on the same code, about 85 minutes each (DEC-883). Queued closes on one head share one regression. A close on code that already passed reuses that run. A store built on the same code fingerprint is fresh.
- **Starts** when W2-66 has merged and passed its ladder (DEC-890). The second re-pin follows it (DEC-889 item 15).
- **Entry criterion:** the record-reading set is settled and in W2-66's test map (P-IS-2). Without it, reuse would let a close pass on a red head (I2 F6, I3 F5).
- **Allowed paths:**
  - new: `src/gov/close/batch.py`, `src/gov/close/fingerprint.py`;
  - `src/gov/close/command.py`: the calls and the record's lines only;
  - `src/gov/close/repo.py`: the store-freshness check only;
  - `src/gov/store/**`: the fingerprints a rebuild records and the incremental record load only;
  - `tests/unit/close/test_batch*`, `test_fingerprint*`, `tests/unit/store/test_fingerprint*`;
  - `docs/research/W2-68-batched-close.md`.
  It reads the test map's record-only list; it does not write it.
- **KPIs, success:**
  - **A batch (DEC-883 item 1):**
    - queued closes on one integrated head share one rebuild, one `gov check` and one full regression on that head;
    - then each ticket's own checks run, one after another: its acceptance suite, the record-reading set, its trailers, paths, probe record and checkpoint;
    - no code merges while a batch runs;
    - each close record cites the batch's run (fingerprint, commit, JUnit XML) and its scope.
  - **A red batch (DEC-883 item 2, DEC-889 item 2 b):**
    - failing tests re-run alone first; a red that passes alone is a flaky candidate, not bisected;
    - a red that fails alone is attributed by `git bisect` over the batch's merges, or by the failing tests' own ticket, with the evidence;
    - nothing closes on a red run; the causing ticket is repaired and the batch re-runs; an unrelated ticket waits for a green run;
    - an outside cause is fixed by the orchestrator and recorded.
  - **Same code (DEC-883 item 3, DEC-889 item 2):**
    - a close whose code fingerprint (record-only paths left out) equals the last fully passing run's reuses it, and runs its own checks and the record-reading set;
    - a failing run is never reused;
    - the reused evidence states the reused run's skip count, so a silent skip is not inherited unseen (I4 F2).
  - **Two fingerprints (DEC-889 item 2, item 4):**
    - the code fingerprint governs the code index;
    - changed record files refresh their lexical and semantic chunks incrementally;
    - a lexical index whose record files differ is never fresh.
  - **The path map counts as code for the fingerprint:** it is in the shared core (DEC-880), so a change to it runs fresh. The synthesis asks this question; the recommendation is to keep DEC-880's answer.
  - **Re-read against two fingerprints:** W1-30's `test_a_store_rebuilt_without_embeddings_is_stale_one_commit_later` (I2 §2.6), by its test designer with a `Rewrite-Reason:`.
  - **Its trial (DEC-884 item 4),** on a fixture or dev-tier programme, measured:
    - the time per batch;
    - reuse correct;
    - a planted code change forcing a fresh run;
    - a planted record-only commit running the set and nothing else;
    - a red batch attributed, with nothing closing on it.
- **KPIs, failure:**
  - a close that cites a red run or another fingerprint's run;
  - a reused run on different code;
  - a store accepted on another code fingerprint;
  - a lexical index fresh with changed records;
  - a code merge during a batch;
  - a red that passes alone being bisected;
  - reused evidence that hides a skip.
- About 300 lines (DEC-890).

#### W2-67 Test hygiene: per-test copies, nested runs, temp folders, and the weak tests' revisions (FULL, independent-test-designer for the acceptance revisions, engineer for the builder tests; DEC-889 item 7, P-H-5, DEC-892 item 1, DEC-898; lens I's P-IS-3 and P-IS-7)
- **Why:** lens H and lens I found these.
  - **Per-test copies race git's garbage collection.** A copied tree past about 6,700 loose objects races git's background gc. It errored W1-25's and W1-07's cases in refused closes (I3 F9, I4 F5).
  - **Nested runs fail under load and block worksteal** (I1 F-5, I2 F5).
  - **pytest's temp folders are not cleaned:** `/tmp/pytest-of-usain` holds 61 run folders since 2026-10-20. One auditor's per-run base folders filled the disk's inodes on 2026-10-22 (DEC-898).
  - **About 277 weak or outdated functions** cannot fail for the fault they claim to catch, or encode an old rule (I-SYNTHESIS §5.2).
- **Place:**
  - Starts after W2-66 merges (DEC-889 item 7).
  - Its acceptance-test revisions can close only once W2-07's test-revision class lands, so it is planned to close after W2-07 (DEC-892 item 1, P-IS-7).
  - Once DEC-769 item 3 is built, its designer writes only the folders this card names (P-IS-11).
  - The two acceptance reruns are not here: P-IS-3 (a) retires them now, in a small ticket of their own (W2-70 in the bundle's index).
- **Allowed paths:**
  - for the engineer: the fixtures and helpers that make whole-tree copies (`tests/acceptance/W1-07/w1_07_support.py`, `tests/acceptance/W1-25/**`, the W1-27 old-path case's fixture);
  - `tests/unit/close/**` (the 15 nested-run functions only; it runs after W2-07, which holds that folder);
  - `tests/unit/guard/**` (the fixed `/tmp` folder only);
  - the root `tests/conftest.py` (the temp-folder rule only).
  - For the test designer, each with a `Rewrite-Reason:` and no expectation lowered:
    - `tests/acceptance/W1-26/**`, `W1-27/**`, `W1-30/**`, `W2-02/**`, `W2-50/**` (the large-store and hang cases only);
    - the folders of I3's T-A3 rows (I3 §4.5), each named in the ticket file when it is written.
- **KPIs, success:**
  - **Copies (I3 F9, I4 §2.1):** every per-test copy either commits with `gc.auto=0` or copies the working files without `.git`. W1-27's old-path case gets a project of its own instead of a whole-tree copy. A planted 7,000-object tree runs every copying case green in parallel.
  - **Nested runs (I2 F5):** the 15 unit close functions that start a nested pytest get a bound a loaded machine meets (one worker, or a measured limit). After them, worksteal is re-measured in the nightly in file order (DEC-892 a, P-IS-3).
  - **Long cases (I1 F-11):** W2-50's large-store and hang cases run against a declared short limit. The guard unit test's fixed `/tmp` folder becomes `tmp_path`.
  - **Temp folders (DEC-898):** the suites keep pytest's own retention of three base folders, and nothing passes a per-run `--basetemp`. A full run leaves at most three base folders behind.
  - **The weak tests (P-IS-7 (a)):** each revised case is first shown red against a planted fault, then green on the head. The order is the code a planned ticket will change first:
    - `gov doctor`'s 40 W1-27 cases, before W2-22, W2-18 or W2-09 changes doctor;
    - W1-26's 45 planted-defect cases, their fixture shown green before any defect;
    - W1-30's 13 first-round cases;
    - W2-02's unmeasured case;
    - T-A3's 42 rows.
    Revisions of files that an open ticket already holds ride in that ticket instead (P-IS-7 (a)): W2-11 the skills' 41, W2-34 W1-09's and W1-14's, W2-65 the unit hooks, W2-44 containment's PF-7 case, W2-04 W1-24's.
  - **Slimming, optional:** W1-02's 121 spelling functions merged; 27 renames ("as a read", "four worker roles"); the two dead modules and the stale help line (`src/gov/cli/commands/status.py`, `check.py`) go to W2-22.
- **KPIs, failure:**
  - a revised case that cannot fail for its fault;
  - an expectation lowered;
  - a copy that still races gc;
  - a nested run left unbounded;
  - a per-run base folder;
  - a test changed in a folder this card does not name.
- About 600 to 900 lines of test code (I2's estimate for its share), and about 150 to 200 functions, most one fixture line and one assertion each.

#### W2-62 Resume in full: the session-start hook delivers the whole RESUME HERE block and names the prompt in force (STANDARD, engineer; CIT-P; DEC-837; keystone 3)
- **Why:** the owner's item 1f (DEC-837): the resume must come back whole after every compaction. Split out of W2-10 so that it lands first; it takes W2-10's rows W2-M372 and W2-M373. Ticket file `DAEO-juee`.
- **Starts** at once: no dependency, and no ticket in flight shares its paths.
- **Allowed paths:** `template/governance/kernel/hooks/sessionstart.py`, `template/governance/kernel/skills/checkpoint/**` (the resume rule only), `tests/unit/hooks/**`, `docs/changes/W2-62-CIT-P.md`.
- **KPIs, success:**
  - The whole RESUME HERE section reaches the resumed session, however long: never a cut of its first 9,000 characters, and no "[truncated]" line in its place [W2-M372, DEC-837 item 1].
  - **Research first,** recorded in the CIT-P: whether Claude Code 2.1.292 caps or moves a SessionStart hook's `additionalContext` above a size, measured in a headless session. If it does, the hook delivers the section by a route that arrives whole, and a live resumed session shows the whole section read.
  - The overall cap never cuts the RESUME HERE section or the instruction to read it; the optional parts are the ones trimmed.
  - The hook names the prompt of the wave in progress, read from the project's configuration, not a constant; with no such setting it names none rather than a wrong one [W2-M373].
  - The checkpoint skill states the resume rule: the full session state, repository knowledge from retrieval and the context packets, a checkpoint at every handover [DEC-837 items 2 and 3].
- **KPIs, failure:** a section of 50,000 characters arrives with no character lost; a checkpoint without the section still says so; unreadable input still exits 0; a role other than orchestrator gets no RESUME HERE injection.
- **Once it lands,** DEC-792's 8,000-character limit is lifted.

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
- W2-48 takes the close queue off the critical path from layer 3 on (DEC-726). **Changed by DEC-880:** W2-48 is withdrawn; W2-66's path-scoped regression does this.
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
- **Closes.** Before W2-48, every close runs the full regression (≈ 1 hour) after a full rebuild (≈ 4 min), one at a time. That costs ≈ 7 hours over layers 1 and 2. From layer 3 on, a close runs only the tests whose inputs changed, plus the uncached runs at W2-24 and W2-46. **Changed by DEC-880:** from W2-66's merge a close runs the path-scoped regression (its own suite, the unit tests, the suites of overlapping tickets; the full suite for the shared core); before it, the full regression.
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
7. **The Contract's Wave 2 items after the re-baseline (DEC-841: eight, CAP-17.b, CAP-45.a, CAP-10.b, CAP-19.a, CAP-19.c, CAP-33.b, CAP-33.g and CAP-61.f; the other nine moved to Wave 3 through W2-49's CIT-P), and Contract v4.2's lite items** (CAP-44.h with A7 and A10, CAP-43.b), are each delivered by a closed ticket and cited by an acceptance test. The plan validator checks this both ways.
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
- **Every report starts with a countdown:** the steps left to the end of Wave 2, with a time estimate for each. Its first line is one progress line (DEC-878): tickets closed / merged, not closed / built and held / in flight / not started, out of the total; keystones done / in progress / ahead, out of nine.

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
