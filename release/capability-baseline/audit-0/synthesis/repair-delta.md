# Repair delta — iteration 0 → iteration 1 (P2-AR-0007)

Candidate rejected: `cap2-candidate-0` (`57177a37…`, `product_code_digest bd4d65d9…0547`). This file states **what must
become true** for each blocker class in `blocker-classes.yaml`, the normative source that requires it, the evidence a
later independent verifier will demand, the dependencies between classes, and a partition into repair workstreams. It
states requirements, not designs. Where several conforming designs exist, the choice is the repair role's, graded by the
next independent verifier; two genuinely open choices are routed to the owner (`owner-decisions-required.md`,
OD-P2-01, OD-P2-02) and are marked where they touch a class.

## 0. Rules that apply to every class

1. **New candidate → R1 preservation (AC-14).** Any product-code change produces a new candidate whose
   `product_code_digest` differs from `srr1-r1-accepted`. Before or within its Phase-2 verification a fresh independent
   verifier must re-run every prior R1 held-out suite (`release/verification/4.1.6-r1*/evidence/heldout-tests/`) unedited
   and re-establish the twelve frozen R1 items for every changed area. WS-8 (root of trust) changes `srr/**` directly.
2. **Evidence standard for acceptance.** For every class the verifier will demand: (a) the named attack or scenario run
   against `target/release/gov` on disposable projects and observed to fail closed or behave as required; (b) the same
   attack as a negative control that still succeeds on `cap2-candidate-0` (so the probe is shown to discriminate);
   (c) an evidence owner in the product suite that runs the check (AC-10: the class's check must appear in
   `tests/governance/capability-evidence-map.yaml` and actually run at its G-tier); (d) invalidation shown: changing the
   relevant input makes prior green evidence stale (AC-10). Builder tests are regression evidence only (O3).
3. **Probes to reuse.** Each class lists the audit-of-record probes whose FAIL lines must turn PASS. They are runnable
   unchanged against a new candidate (`evidence/RERUN-family-probes.sh`, `evidence/AC16-*.py`, `evidence/LEAD-*.py`).
   A repair that makes a probe pass by special-casing the probe's fixture is not a repair.
4. **Convergence.** Frozen contract §8: a later finding in the same class (same capability and mechanism, including an
   incomplete fix) is RESIDUAL; anything else, including a regression in a capability that held, is MATERIALLY_NEW.
   Requirements added by an owner decision (OD-P2-01/02) open owner-added classes, not convergence failures.

## 1. Requirements per blocker class

Notation: **Req** = requirement and source; **Accept** = evidence the verifier will demand; **Dep** = classes that must
land first or together; **WS** = workstream (§3).

### Contract binding and evidence mapping

**BC-P2-01 Compiled contract views lose owner-source semantics; verification is self-referential** (AC-13)
- Req: The compiled form, the generated view and the evidence map carry, for every capability section of the owner
  source **including Gate U**, every checklist item (the 713 checkbox bullets plus the two normative qualifiers at
  lines 385 and 515), the W10 hard-invariant text, each gate's advanced-qualification challenge, the per-capability fields
  of Contract v3:53-73, and the requirement-class **label exactly as the source states it** (O5 "NEW EXECUTION REFINEMENT",
  Gate V "NEW TESTING REFINEMENT" — the source's three-value list at line 60 does not contain the latter; carry it
  verbatim rather than mapping it). `gov contract verify` fails on any semantic difference between the owner source and
  any derived view, including the evidence map and the generated view (Contract v3:37-49; AC-13).
- Accept: `evidence/AC01-09-13-14-universe-identity-binding.py` reports 101/101 capabilities in all three views, 344/344
  substantive bullets carried, labels equal; mutation controls: deleting one bullet, one capability (U), or changing one
  label in any derived view each make `gov contract verify` fail with a typed error; the compiled-form schema admits
  every owner-source id.
- Dep: none. WS-1.

**BC-P2-02 Evidence map declares no evidence owner** (AC-10)
- Req: Every one of the 101 capabilities names at least one evidence owner that actually runs (G0…G6 tier check,
  independent held-out suite, Human Decision Gate evidence, or release/clean-clone evidence), with the Contract v3:53-73
  evidence-class and check-id fields populated (Contract v3:75-93; AC-10).
- Accept: `evidence/suite-to-contract` style matrix regenerated from the product's own map shows no capability with zero
  owners; for a sample of owners per gate, the verifier runs the owner and observes it exercise the capability.
- Dep: BC-P2-06/07 (tier owners must exist) and every class whose check becomes an owner. WS-1 (closes last).

### Evidence currency, scheduler and health

**BC-P2-03 Green-evidence currency key and enforcement** (AC-10, AC-3, AC-5)
- Req: Green governance evidence is keyed by every Contract v3:97-109 input class relevant to it — including
  authoritative spec beyond decisions (requirements, architecture, interfaces, tasks), relevant source files, the index
  manifest, tool/plugin registries, research/experiment/checkpoint/handoff records, adoption evidence, machine trust
  state and the runtime implementation identity — and a change to any of them makes it stale before work relies on it;
  every governance-affecting task (by class and by the governed records it touches) is refused close on stale evidence
  (Contract v3:95-111, :788-789).
- Accept: the invalidation matrices of alpha-r `FRESH-invalidation`, beta-r `FRESH-evidence-invalidation`, delta-r
  `FRESH-invalidation`, epsilon-r `O4-suite-currency §A-§E`, zeta-r `FR-freshness-invalidation` all PASS for every input
  class; a modified `gov` binary changes the evidence key; AC16-X1 `X1-O4-green-stale-after-direct-spec-change` PASS.
- Dep: none (BC-P2-06's cache keys reuse the same key). WS-2.

**BC-P2-06 Health scheduler mechanics** (AC-5)
- Req: A G0-G6 scheduler selects checks from the dependency relation between changed inputs and checks, runs
  independent checks concurrently when safe, isolates checks that mutate state, caches results under the relevant
  content/policy/framework hashes, declares hard-block vs warning per check and refuses the operations a hard-block
  governs, and records each health result with tier, checks, inputs, runtime identity, repository state, actor and time;
  a trivial mutation does not re-run the whole suite serially (Contract v3:791-808; AC-5).
- Accept: epsilon-r `O5-scheduler-requirements` S1-S9 PASS (impacted selection from a one-line change; >1 thread/process
  for independent checks; live `state.db` untouched by a deep check; second identical run served from cache; a
  hard-block state refuses task create/claim/close/CIT propose); health results persisted with provenance.
- Dep: BC-P2-03. WS-2.

**BC-P2-07 Tier duties at trigger events, including Gate-W duties** (AC-5, AC-8, AC-16)
- Req: Each tier runs at its trigger events and performs its duties: G1 on every material mutation however made
  (changed paths, schema, secrets, index and dependency/lineage invalidation); G2 at task close (mutation scope, readiness,
  tests from recorded evidence, references, memory freshness, input consumption and traceability); G3 at
  checkpoint/handoff (claims, pending gates, decisions, checkpoint and mandatory-input continuity); G4 after
  CIT-E/migration/memory/architecture changes (wider staleness/impact propagation); G5 full suite at adopt, update,
  release and full audit; G6 exists and observes synthetic-repository, chaos, soak and hidden-test qualification runs
  (Contract v3:793-799, :1186-1192).
- Accept: epsilon-r `O5-tiers-G1-G6`, `O5-G5-update` and zeta-r `W12-scheduler-integration` FAIL lines turn PASS;
  AC16-X1 `X1-W12-G4-wider-check-recorded` PASS; a G6 entry point accepts a qualification run and records its health.
- Dep: BC-P2-06; host hooks in WS-4 (CIT, checkpoint, handoff), WS-5 (task close), WS-8 (update/release), WS-9 (adopt).
  WS-2 owns the tier contract; each host WS owns its call site.

**BC-P2-43 Product-test results governed** (AC-3)
- Req: Per-family product-test results are recorded as governed, freshness-bound evidence; a failing family changes the
  health state and blocks close of the work it covers; test outcome at close is verified from recorded evidence, not
  self-attested; a failed suite is not reported as a successful command (Contract v3:751-761, :980, :1004).
- Accept: epsilon-r `O1-product-families §F-§H` and `U-slos-and-healthy SLO-2` PASS.
- Dep: BC-P2-06. WS-2.

**BC-P2-44 Health SLO thresholds and the HEALTHY conjunction** (AC-3, AC-16)
- Req: Every Gate U SLO is computed, carries a declared threshold and changes the health state when crossed, and is
  observed by the scheduler; one repository verdict is HEALTHY only when all thirteen Contract v3:995-1008 conditions hold,
  including no unresolved critical audit finding and explicit readiness per active feature (Contract v3:976-1008).
- Accept: epsilon-r `U-slos-and-healthy` SLO-1…15 and H1…H13 PASS; AC16-X1 `X1-UxO5-health-reflects-invalid-completed-work`
  PASS.
- Dep: BC-P2-03, -06, -16, -22, -23, -43. WS-2.

**BC-P2-42 Skill regression executed** (AC-3)
- Req: The skill-regression family executes each skill's validation scenarios (or equivalent executable checks) and fails
  when an expectation is not met; a skill version identifies its content, for project and kernel skills (Contract
  v3:399-402, :774).
- Accept: epsilon-r `O2-governance-families §11/§11b` and gamma-r `F1-skills F1.b3` PASS: a skill whose method was
  changed without a version change, or whose scenario is false, is reported.
- Dep: none. WS-2.

**BC-P2-24 Governed work generated from events** (AC-3, AC-5)
- Req: Each Contract v3:572-583 source (failed tests, audit findings, research discoveries, human decisions, CIT
  effects, lessons, missing tools/skills, retrieval failures, security findings, performance regressions) and each health
  failure generates governed, linked work in the same DAG when it occurs (Contract v3:571-583; AC-5
  "remediation/task generation").
- Accept: gamma-r `I3-generation` counts ≥1 linked task per source; epsilon-r `O5-scheduler-requirements S8` PASS.
- Dep: BC-P2-04, -06/07, -22, -32, -43. WS-5 (engine), event producers in WS-2/WS-4/WS-6.

### Authority, identity and Human Decision Gates

**BC-P2-08 Acting-role resolution and G0 guard coverage** (AC-3, AC-5)
- Req: Every command evaluates authority against the role the caller declared by whichever documented means,
  consistently (init and every adopt/migrate stage included, first install batch included); an invocation that
  declares no role receives no privileged authority (framework §23 "No spawned worker behaves as an orchestrator unless
  explicitly assigned"); every command that writes authoritative or governed test state has a declared authority class;
  no command changes governed state while FREEZE_WRITES/PAUSE forbids it except an explicit, listed recovery allow-list
  (Contract v3:364, :173-174, :793; framework §23, §74).
- Accept: gamma-r `E1-authority E1.b2` census and `E1.b3` PASS; alpha-r `S3-S4-role-flag-authority` PASS; epsilon-r
  `O5-G0-guard-matrix` shows zero mutations under FREEZE_WRITES/PAUSE outside the allow-list and L0 `init --force`
  refused; AC16-X2 `X2-E1-init-honours-declared-role` and `X2-E1-undeclared-role-is-not-orchestrator` PASS.
- Dep: none. WS-3 (with call sites in `init.rs`/`adopt.rs` owned by WS-8/WS-9). OD-P2-01 does **not** block this class.

**BC-P2-09 OS-written (T2) records bound to OS operations** (AC-3, AC-4, AC-16)
- Req: A T2 fact (gate presentation/answer, decision, CIT state, plugin registration) is honoured only when it provably
  results from the corresponding OS operation; a lower-trust write to OS-written state is observed and refused at task
  close rather than exempted; the governance suite and doctor report T2 records that no OS operation produced, and such a
  change invalidates prior green evidence (Contract v3:365, :427, :675; D-0007 T2 and rule 2; ARCH-0003 §8).
- Accept: gamma-r `E1-authority E1.b3.d`, delta-r `L3-gate-presentation-attacks` b1.6/b5.8-b5.10, gamma-r `F4-plugins
  F4.b2.x` and `FRESH-invalidation FRESH.4` PASS; AC16-X2 `X2-E1xG2-*`, `X2-L3xE1-*`, `X2-L3xK2-*`, `X2-L3xU-*` PASS.
- Dep: none; it provides the binding primitive BC-P2-10/-11/-12 and WS-7's registry repair use. WS-3 (+ close-side in
  WS-5, registry in WS-7).

**BC-P2-10 Human approval and presentation from an authenticated human channel** (AC-3, AC-16)
- Req: A human answer to a Human Decision Gate, any record asserting human approval (CIT approval, retrieval-profile
  selection, upstream export approval), and the evidence that a gate reached the active human interface derive from a
  channel the acting agent cannot operate through CLI arguments, environment, role claims, defaults, repository files,
  plugins or model output. The accepted sources fix the property and the authority class (owner-controlled local or
  out-of-band authority anchored in the administrator-provisioned boundary, as OWNER-DECISION-0006 requirement 2 and the
  break-glass implementation already do); the concrete mechanism is the repair role's choice, graded by the verifier
  (Contract v3:676, :679, :851; D-0007 rule 2; ARCH-0003 §8; OWNER-DIRECTIVE-0004).
- Accept: delta-r `L3-gate-presentation-attacks` b2.x, b5.1-b5.3, b5.11 and `L3-supplement L3s.2` PASS; epsilon-r
  `Q-learning-upstream Q1.6-8` PASS; AC16-X2 `X2-L3-fabrication-default|role-human|env-GOV_ROLE` PASS; plus a
  verifier-authored attack in which an agent process running with the operator's OS privileges tries every local means
  to produce a human answer.
- Dep: BC-P2-09. WS-3 (export use in WS-11). Not blocked by OD-P2-01.

**BC-P2-11 Gate approval bound to its subject and content** (AC-3, AC-4)
- Req: An approval binds the exact transaction content, simulated impact and CIT it answered, and any later change makes
  it stale at approve and at execute; an elevated plugin registration is authorised only by a presented, answered-A gate
  raised for that plugin identity/version and permission set (Contract v3:430, :678).
- Accept: delta-r `L3-gate-presentation-attacks` b4.s2, b4.s3, b4.o2 and gamma-r `F4-plugins F4.b5.x` PASS.
- Dep: BC-P2-09. WS-4 (CIT side), WS-7 (plugin side).

**BC-P2-12 Task-blocking gate semantics** (AC-3)
- Req: Work blocked by a Human Decision Gate becomes runnable only on an answer that authorises it, returns to blocked
  when that authorisation is revoked or withdrawn, cannot be completed while the gate is unanswered, and a reference to a
  missing gate blocks (Contract v3:678; framework §53).
- Accept: delta-r `L3-gate-presentation-attacks` b4.t2-t5 and `L3-supplement L3s.1` PASS.
- Dep: BC-P2-09/10. WS-3 (answer side), WS-5 (DAG side).

**BC-P2-49 Human Decision Gate package enforced** (AC-3)
- Req: A gate is not presented without substantive content for every package field and at least one option; the answer
  is one of the offered options; every gate states the exact permitted next actions for that gate (Contract v3:662-672).
- Accept: delta-r `L2-decision-package` FAIL lines PASS.
- Dep: none. WS-3.

**BC-P2-18 Contradiction detection and resolution** (AC-3)
- Req: Contradictory authoritative inputs that deterministic precedence cannot resolve are detected and routed to agent
  resolution within policy or to a Human Decision Gate instead of being delivered together as authority; agent
  resolution requires assessed impact, reversibility and confidence that do not rest solely on the resolving agent's own
  declaration; a task whose mandatory inputs conflict does not become READY until resolved (Contract v3:657-660, :1103;
  framework §50).
- Accept: delta-r `L1-contradiction-resolution` L1.b1.6, L1.b2.neg.* and zeta-r `W03 W3-r3-*` PASS.
- Dep: BC-P2-17. WS-3 (resolution rules), WS-4 (detection in context/readiness).

**BC-P2-45 Project overlays bound by policy precedence** (AC-3)
- Req: Every project-level policy input — MODEL_ROUTING_OVERRIDES, readiness switches, any overlay key — is subject to
  POLICY_PRECEDENCE: kernel floors (tier, reasoning minimum, readiness gating, authority, sensitivity) may be raised,
  never lowered, and a refused weakening is reported (Contract v3:134-138, :693-699, :522; D-0007 rule 3).
- Accept: delta-r `M1-M3-routing` M1.floor.1, M2.b1.4, M3.b1.floor and gamma-r `H2H3-readiness H3.b5` PASS.
- Dep: none. WS-3 (with the readiness read site in `dag.rs`, WS-5).

### Change control, propagation and Gate W

**BC-P2-13 Material changes cannot escape change control** (AC-3)
- Req: Whether a proposed or performed change is material for each of the eight Contract v3:640-647 classes is
  determined from what it changes (records, paths, contracts), not only from a proposer label, and material changes
  cannot complete outside CIT-P/CIT-E (including edits made inside ordinary tasks) (Contract v3:446, :638-647;
  framework §47-48).
- Accept: delta-r `K3-auto-impact-simulation` K3.b*.mislabel and K3.outside.* PASS; gamma-r `G1G2-command-surface G1.b3`
  PASS.
- Dep: BC-P2-09 (close exemption), BC-P2-14. WS-4 (CIT-P), WS-5 (close-side detection).

**BC-P2-14 Task-contract fields and path scope enforced** (AC-3)
- Req: `blocks` orders work; required data and tools gate readiness; production merge is refused where not permitted
  (experiments); a mutation outside a task's allowed paths is accepted only when a CIT governing that specific change
  covers it (Contract v3:563-569, :614).
- Accept: gamma-r `I1I2-tasks` I2 sections and I2.b8.x PASS; delta-r `J1-J2 J2.merge.*` PASS.
- Dep: none. WS-5.

**BC-P2-04 Upstream change invalidates completed work, evidence and packets** (AC-8, AC-3, AC-16)
- Req: When an authoritative upstream artefact changes — through CIT-E or directly — dependent task evidence (open and
  COMPLETED), implementation/test/release evidence and compiled context packets become stale as the impact analysis
  dictates, revalidation/rework work is generated, close cannot clear staleness without retest evidence, and an index
  rebuild never substitutes for dependency staleness (Contract v3:632, :1129-1136, :788-789).
- Accept: zeta-r `W06-staleness-propagation` FAIL lines, delta-r `K2-cit-e` K2.b4.4-6/K2.w6.*, epsilon-r `O4 §F` and
  AC16-X1 `X1-K2xW6-*`, `X1-G1xW6-*` PASS.
- Dep: BC-P2-21 (edges), BC-P2-19 (packet identity), BC-P2-24 (rework generation). WS-4.

**BC-P2-05 Checkpoint and handoff continuity** (AC-3, AC-8, AC-16)
- Req: Every mandatory trigger produces a checkpoint without relying on the agent (product operations for decisions,
  transitions, significant mutations; generated provider hooks or an equivalent product-observed boundary for
  model/provider switch, session close and known compaction); checkpoints record mandatory-input ids/versions (or a state
  reference current at checkpoint time) and become stale when the material state they captured changes; handoff and
  session close are blocked or explicitly degraded when checkpoint or required-input freshness violates a stated policy;
  the watchdog observes execution boundaries itself (Contract v3:729-742, :1155-1160).
- Accept: delta-r `N1-N2-checkpoints` N2.*, `N3-N4-W9-watchdog-handoff` N3.*, zeta-r `W09-*` and AC16-X1
  `X1-NxW9-*` PASS.
- Dep: BC-P2-17, BC-P2-19. WS-4.

**BC-P2-17 Mandatory task-input manifest semantics** (AC-8, AC-3)
- Req: A task's manifest declares, per dependency, id, required/optional, required authority/lifecycle state,
  version/hash constraint where applicable and reason, plus separately declared supplementary context; readiness and
  delivery enforce them; a superseded/historical input never silently satisfies a current requirement; authority class
  survives into the packet; output contracts declare what downstream stages may consume (Contract v3:1084-1104).
- Accept: zeta-r `W02-typed-contracts` W2-b2/b3/b6/b7 and `W03-task-input-manifest` W3-m2..m5, W3-r2 PASS.
- Dep: BC-P2-21. WS-4 (with task schema fields in WS-5).

**BC-P2-19 Context-packet delivery, provenance and outage** (AC-8, AC-3)
- Req: Every declarable mandatory input type (requirements, decisions, scenarios, interfaces at task and feature level,
  architecture, datasets, experiments, research, test designs) is delivered deterministically with its normative content,
  exact id and version/content hash; the packet hash changes whenever supplied content changes and is traceable to input
  versions and repository state; a missing required input causes refusal or an explicit blocked state; a retrieval or
  index failure degrades only the supplementary block, explicitly marked (Contract v3:1106-1112, :1164-1171).
- Accept: zeta-r `W04-context-delivery`, `W04b-input-class-delivery`, `W10-hard-invariant-attacks` a4-* PASS.
- Dep: BC-P2-17. WS-4.

**BC-P2-20 Consumption receipt and implementation traceability** (AC-8, AC-3)
- Req: The worker's structured return is the consumption receipt (one contract, or a lossless validated mapping):
  consumed input ids/versions, implemented requirements/scenarios, applied decisions/constraints, acceptance evidence
  against the declared tests, deviations/unknowns — validated against the manifest; close refuses missing mandatory
  traceability and reports untraceable implementation; code/test/output evidence is linked back to the authoritative
  inputs, followable both ways through code, tests, evidence and release (Contract v3:1115-1126, :1147-1152).
- Accept: zeta-r `W05-consumption-receipt`, `W08-lineage` PASS; AC16-X2 `X2-N4xW5-worker-return-usable-at-close` PASS.
- Dep: BC-P2-17, BC-P2-21. WS-4 (contract/lineage), WS-5 (close-side validation).

**BC-P2-21 Artefact identity and relation-edge semantics** (AC-8, AC-3)
- Req: Every W1-named output type — including migration plans, adoption catalogue entries and audit findings — carries
  a stable id, type, version/hash, producer and supersession lineage that survive re-generation and re-runs; records
  outside their canonical location are reported; every relation field yields an edge whose direction matches its meaning
  and every declared upstream-input field (including required_data) yields an edge impact traversal follows
  (Contract v3:1069-1080, :1090, :1133).
- Accept: zeta-r `W01-*`, `W01b-*`, `W02 W2-b8-*`, `W04b W4b-impact-reaches-declaring-task:*` PASS; `LEAD-X5`
  `X5-W1-*` and `X5-T3-*` PASS.
- Dep: none. WS-4 (records/edges), WS-9 (adoption catalogue/plan identity).

**BC-P2-22 Orphan / unexplained output detection** (AC-8, AC-3)
- Req: Each W7 orphan class is detected by name and turned into governed investigation/remediation work
  (Contract v3:1139-1144).
- Accept: zeta-r `W07-orphan-detection` PASS.
- Dep: BC-P2-20, -21, -24. WS-2 (G5 lineage/orphan family) with graph queries from WS-4.

**BC-P2-23 Artifact-flow quantitative health** (AC-2)
- Req: The nine W11 metrics are tracked and reported for the governed repository (Contract v3:1173-1183).
- Accept: zeta-r `W11-quantitative-health` m1..m9 PASS with values that move when the corresponding fault is injected.
- Dep: BC-P2-04, -17, -19, -20, -22. WS-2.

### Task DAG and claims

**BC-P2-15 Claim atomicity and scope** (AC-3)
- Req: A claim is granted to exactly one session under concurrent attempts; the unit of isolation (session/worktree) is
  recorded; parallel claims are refused or serialised when mutation scopes overlap (Contract v3:388-392).
- Accept: gamma-r `E4-claims` E4.b2.race (0 double grants in ≥15 trials) and E4.b5 overlap PASS.
- Dep: none. WS-5.

**BC-P2-16 Runnable / claimable / READY state derived from the DAG** (AC-3, AC-8)
- Req: A task is claimable, stored READY or offered as runnable only when the DAG allows it — dependencies, readiness
  policy, TEST_POLICY, gates, mandatory inputs present, and not in a blocked status (Contract v3:392, :522, :587, :1101).
- Accept: gamma-r `E4-claims E4.b5`, `H2H3-readiness H3.b5`, zeta-r `W03 W3-r1-*` and AC16-X2 `X2-I4-*` PASS.
- Dep: BC-P2-12, -17, -45. WS-5.

### Knowledge fabric and retrieval

**BC-P2-25 Index content coverage and chunk granularity** (AC-3, AC-7)
- Req: All governed record content (list-valued and nested fields included, worker returns included) and every
  non-empty line of indexed code are held by at least one chunk with section-level provenance; code is chunked down to
  function/method units and symbol lookups return the unit's own slice (Contract v3:234-249, :274, :323-327).
- Accept: beta-r `C3-semantic-memory`, `C4-lexical-memory`, `C7-episodic-memory`, `D3-hierarchical-retrieval` PASS.
- Dep: none. WS-6.

**BC-P2-26 Retrieval ordering, routing, de-duplication** (AC-3)
- Req: Authority and namespace filters apply before candidate truncation and before any plugin receives candidate text;
  filename-shaped queries reach a route that resolves file names; dependency/impact questions (including code entities)
  deliver graph answers; content-level duplicates are suppressed across artefacts (Contract v3:241, :246, :291, :316-321).
- Accept: beta-r `C3 C3-b7`, `D2-retrieval-router`, `C9-context-packet` PASS.
- Dep: none. WS-6.

**BC-P2-27 Code-structural extraction** (AC-3)
- Req: Route registrations, database models and inheritance/implementation relations are represented for the languages
  in scope; extraction is AST/LSP/SCIP-equivalent (no symbols from comments/strings); test→code relationships exist for
  standard layouts (Contract v3:251-259).
- Accept: beta-r `C5-code-structural-memory` PASS.
- Dep: none. WS-6.

**BC-P2-28 Graph integrity detection** (AC-3)
- Req: Integrity checks raise orphan relationships, relationships to superseded/retired/historical targets, and
  reversed or ill-typed relationships per relation type (Contract v3:231).
- Accept: beta-r `C2-relationship-graph` PASS.
- Dep: BC-P2-21. WS-6.

**BC-P2-29 Incremental index invalidation** (AC-3, AC-16)
- Req: Incremental indexing invalidates derived facts in other artefacts that depend on a changed artefact
  (incremental equals full); a path-map or classification change re-derives every affected artefact before freshness
  reports fresh; CIT-E refreshes and verifies under the post-mutation policy and path map and rolls back when the result
  is incompatible (Contract v3:308-313, :634-636, :888).
- Accept: beta-r `D1-incremental-freshness` and `X-K2-D1-W6-interactions` PASS.
- Dep: none. WS-6 (CIT-E call site in WS-4).

**BC-P2-30 Retrieval-profile component identity and change governance** (AC-7, AC-3)
- Req: The embedding model artefact and inference runtime are separately identified and content-bound in the index
  manifest; pins bind the implementation/model revision actually executed and fail closed on mismatch; changing a profile
  requires benchmark evidence for the chosen candidate, a recorded held-out regression after re-indexing, and the
  change-control gate for its radius; ungoverned pin edits are detected (Contract v3:329-349; frozen contract §9.1).
- Accept: beta-r `D4-component-separation`, `D5-model-selection` PASS; a re-pin does not withhold deterministic inputs
  (zeta-r `W10 W10-a4-embedder-repinned-before-reindex` PASS).
- Dep: BC-P2-13, -19, -29. WS-6.

**BC-P2-31 Non-rebuildable authoritative state stored and classified as authoritative** (AC-3)
- Req: Claims, emergency-control state and OS plugin registration survive deletion of every path the product
  classifies derived or generated, and the product's repository contract and documentation classify their storage
  truthfully (Contract v3:188, :202, :352; D-0007 T2).
- Accept: beta-r `D6-rebuild-guarantee` (A)/(B) PASS; AC16-X2 `X2-B1B3-*` PASS.
- Dep: coordinate the registry location with BC-P2-09 (WS-7). WS-6.

**BC-P2-32 Durable failure memory** (AC-3)
- Req: Retrieval misses and tool failures produce durable, structured, kind-distinguishable records that survive memory
  rebuilds and link to the follow-up (framework §11.8, §18; Contract v3:276-283).
- Accept: beta-r `C8-failure-memory` PASS.
- Dep: none. WS-6.

### Root of trust and lifecycle ingress (AC-4)

**BC-P2-35 Post-install integrity detects consistent rewrites** (AC-4, AC-3, AC-16)
- Req: Installed-kernel verification detects a mutually consistent payload/KERNEL_MANIFEST.json/framework.lock rewrite
  wherever the machine holds a protected record of what it verified and installed, and treats the installed kernel as
  unauthenticated T1 (D-0007 rule 1: embedded baseline substituted, mutations fail closed) until it matches; a machine
  that holds no protected record for the project verifies the installed kernel against the pinned authenticated release
  before privileged work (Contract v3:146; D-0007 rule 1; ARCH-0003 §7, §8; OWNER-DIRECTIVE-0004). This strengthens
  detection and requires no change to D-0007's text; if a repair believes it must amend D-0007, stop — that is the
  owner's open transition record (frozen contract §7).
- Accept: alpha-r `A2-03-post-install-tamper [T2]` and AC16-X3 `X3c-A2:146-*`, `X3d-A2xE1xL3-*` PASS; control: the
  authentic install still verifies; the unprovisioned case follows OD-P2-02.
- Dep: none. WS-8.

**BC-P2-36 No unauthenticated installation presented as current or verified** (AC-4, AC-3, AC-16)
- Req (determined now): An installation whose authenticity is not established is never presented as current, verified
  or certified by any surface (CLI envelope, `gov status`, init/update results), is reported by doctor and audit, and
  cannot yield a HEALTHY verdict without disclosing it (Contract v3:150; OWNER-DIRECTIVE-0004 "cannot manufacture trust").
- Req (after OD-P2-02): the admission scope of the unprovisioned posture as the owner decides.
- Accept: alpha-r `A2-01-unprovisioned-posture [U2]-[U4]` presentation lines and AC16-X3 `X3a-A2:150xU-no-masquerade`
  PASS; per OD-P2-02, `X3a-S3xA2-unprovisioned-refuses-unauthenticated` PASS or the marked mode demonstrated.
- Dep: OD-P2-02 (second requirement only). WS-8 (+ doctor check in WS-2).

**BC-P2-37 No trust decision from unauthenticated release fields** (AC-4, AC-3)
- Req: No gate-relaxing or trust-relaxing decision rests on a certification claim the trust root has not authenticated;
  an unauthenticated certification is treated as uncertified everywhere; minting a certification claim is an
  authority-gated act; every identity field framework.lock records comes from what verification established (or is
  marked unverified), records its authenticity basis, and does not vary with machine paths (Contract v3:149-150, :161,
  :937, :950; D-0007 rule 2).
- Accept: alpha-r `A2-04-lock-identity-and-masquerade` [L1]-[L4], `S6-cross-machine [X3]`,
  `00-regression-variant-xdg-cache` PASS.
- Dep: none. WS-8.

**BC-P2-38 Provisioned-machine rollback and failure atomicity** (AC-3)
- Req: On a provisioned machine the rollback ingress can restore a release this machine previously verified, subject to
  the owner's floor/break-glass rule; a refused privileged lifecycle command leaves the installation as it found it
  (Contract v3:944, :151; OWNER-DIRECTIVE-0004; ARCH-0003 §6-§7; OWNER-DECISION-0006/0007).
- Accept: alpha-r `A2-05 [K6a]/[K6b]`, `A2-08-reinstall-version-change [V1]-[V3]` PASS without weakening any floor.
- Dep: none. WS-8.

### Plugins and tools (AC-4)

**BC-P2-39 Plugin elevation not decided by self-declaration** (AC-4)
- Req: Whether a plugin's execution needs an elevated-permission gate does not depend on the descriptor's own
  declarations: either declared permissions are enforced at run time, or every executable plugin that can exceed the
  non-elevated floor requires registration and a specific gate. D-0005's allowance for hand-declared descriptors remains
  satisfiable for effects that are enforced or non-elevated (Contract v3:426, :430; ARCH-0003 §9). Not an owner
  decision; a design that would add a new external dependency class needs owner adoption before it is chosen.
- Accept: gamma-r `F4-plugins F4.b1` UNDER-declaration PASS (no undeclared effect without a gate).
- Dep: none. WS-7.

**BC-P2-40 Plugin implementation bytes bound** (AC-4, AC-3)
- Req: Every executable plugin's implementation and descriptor bytes — module-form and interpreter-only commands included —
  are bound in tracked, OS-written registration state; any change fails closed at execution and is reported by health
  checks; a reset of machine-local state or a fresh clone cannot re-baseline tampered bytes (Contract v3:428-429).
- Accept: `LEAD-X4-registered-module-plugin-unpinned` PASS; gamma-r `F4-plugins F4.b3/b4` PASS.
- Dep: BC-P2-09 (registry binding). WS-7.

**BC-P2-41 Tool acquisition gates bound to the installation** (AC-4, AC-3)
- Req: Security-review evidence is a governed security review of that tool identity/version; when approval is required,
  a presented, answered-A gate raised for that exact installation lets the governed install proceed and a decline ends it
  (Contract v3:416-423, :431; D-0007 consequence 4).
- Accept: gamma-r `F2F3-tools` F3 (a)/(b) and `F4-plugins F4.b6` PASS.
- Dep: BC-P2-11. WS-7.

### Adoption, legacy and independence

**BC-P2-34 Independence established from recorded authorship** (AC-3)
- Req: Test, review and verification independence is established from recorded authorship (role and session of the
  author versus the implementer/executor/builder), bound to the evidence; a task's designated role binds who may claim
  and close it; each independent adoption stage (A5, A7, A10, A11) is performed by a kernel role designated for it;
  execution and every independent verdict are bound to the exact artefacts approved (changing plan/map/tests after
  approval invalidates the approval or is refused); A10's held-out tests come from the independent verifier; builder
  tests are classified regression evidence; verifier held-out sets are protected from overwrite by other roles
  (Contract v3:366, :521, :526, :783-785, :928-934, :957-972; adoption protocol §3, §11, §15).
- Accept: alpha-r `S4-T2-B2-negative [N1][N2][N7]`, `T1-roles [T1c]`, epsilon-r `O3-independent-authorship`, gamma-r
  `E1-authority E1.b4.b`, `H4-scenarios-data-tests H4.b2` PASS.
- Dep: BC-P2-08. Its reach beyond caller-declared agent identity depends on OD-P2-01. WS-9 (adoption), WS-5 (task roles),
  WS-2 (held-out protection in governance tests), WS-10 (data authorship).

**BC-P2-33 Legacy identification, extraction and retirement** (AC-3)
- Req: Legacy extraction covers decisions, lessons, skills, evidence, research and other unique durable knowledge (or
  surfaces everything not extracted for review) before a store is retired; retirement is preceded by a dependency proof
  over code, configuration and docs and is refused or gated while active references exist; migration never rewrites
  active references into archived legacy material; the plan and the independently scaffolded tests agree on every
  artefact's disposition, secret-bearing legacy stores included; classification never treats the Governance OS's own
  installed or generated state as legacy (Contract v3:872-885, :191, :928-929).
- Accept: beta-r `R1-R2-legacy-and-chat-retirement` PASS; alpha-r `S4-adopt-end-to-end` with `RAW_SQL_STORE=1` completes
  A0-A11; `LEAD-X5 X5-S4xB2-*` PASS.
- Dep: none. WS-9.

**BC-P2-52 Path map represents citations** (AC-3)
- Req: Document citations/links appear in the path map alongside imports and consumers (Contract v3:194).
- Accept: alpha-r `S4-T2-B2-negative [N5]` shows the README→spec link in both entries' references.
- Dep: none. WS-9.

### Records, research and experiments

**BC-P2-46 Scenario → data → test-data lineage and provenance** (AC-3)
- Req: The FEATURE → SCENARIOS → DATA → TEST DATA → SUCCESS/FAILURE → INDEPENDENT TESTS chain is machine-traceable through
  the product's own fields with missing links detected; test data used by acceptance/independent tests carries recorded
  provenance and its absence is detected (Contract v3:524-527; framework §39).
- Accept: gamma-r `H4-scenarios-data-tests` H4.b1, H4.b3 PASS.
- Dep: BC-P2-21 (relation fields). WS-10.

**BC-P2-47 Research output completeness** (AC-3)
- Req: A research record is not treated as governed evidence (EVIDENCE class, retrievable as current, citable by a
  decision) unless it records question/reason, method, sources/data, measurements, uncertainty, conclusion and
  confidence; incomplete ones are refused or held reference-only and reported; the output records the decisions/tasks it
  influenced (Contract v3:596-605; framework §45).
- Accept: delta-r `J1-J2-research-experiments` J1.* PASS.
- Dep: none. WS-10.

**BC-P2-48 Experiment lifecycle** (AC-2)
- Req: Experiments are governed through a lifecycle recording hypothesis/question, method/data, reproducibility, results,
  interpretation and decision influence; experimental output cannot enter the production tree without a governed
  promotion (Contract v3:607-614).
- Accept: delta-r `J1-J2-research-experiments` J2.* PASS; the Gate J challenge "irreproducible experiment" is detectable.
- Dep: BC-P2-14 (merge enforcement). WS-10.

### Learning and export

**BC-P2-50 Export gate fails closed on content** (AC-3)
- Req: The upstream export gate fails closed on raw project content and index data whatever their names or synthetic
  declaration (Contract v3:861-866; release protocol §17; framework §75G).
- Accept: epsilon-r `Q-learning-upstream Q4.5` PASS.
- Dep: none. WS-11.

### Qualification oracle

**BC-P2-51 Qualification Oracle format** (AC-2, AC-6, AC-10)
- Req: A machine-checkable Qualification Oracle format covering every V1-V4 element exists, is kept separate from the
  public qualification suite, and is accepted by a fresh independent reviewer against V1-V4 before any hidden fault is
  generated (Contract v3:1012-1062, :1206; frozen contract AC-6, §9.2). No hidden fault is generated in Phase 2.
- Accept: the format validates a well-formed sample and rejects samples missing each V1-V4 field; a fresh
  `oracle-format-reviewer` issues `QUALIFICATION_ORACLE_FORMAT_ACCEPTED`; `GATE-P2-ORACLE-FORMAT` satisfied.
- Dep: none on product code. WS-12.

## 2. Dependency order (class level)

```text
Wave 1 (parallel):  BC-01  BC-08  BC-09  BC-45  BC-49  BC-21  BC-15  BC-14  BC-25 BC-26 BC-27 BC-29 BC-32
                    BC-35  BC-37  BC-38  BC-39  BC-42  BC-43  BC-47  BC-50  BC-51  BC-52  BC-33  BC-36(presentation)
Wave 2:             BC-10 <- 09          BC-11 <- 09          BC-12 <- 09,10      BC-17 <- 21      BC-28 <- 21
                    BC-40 <- 09          BC-41 <- 11          BC-46 <- 21         BC-48 <- 14      BC-34 <- 08 (+OD-P2-01)
                    BC-31 (registry location with 09)          BC-13 <- 09,14      BC-06 <- 03 ... BC-03 first in WS-2
Wave 3:             BC-19 <- 17          BC-18 <- 17          BC-16 <- 12,17,45   BC-20 <- 17,21
Wave 4:             BC-04 <- 19,21       BC-05 <- 17,19       BC-30 <- 13,19,29   BC-07 <- 06 + host hooks
Wave 5:             BC-22 <- 20,21       BC-24 <- 04,06/07,22,32,43               BC-23 <- 04,17,19,20,22
                    BC-44 <- 03,06,16,22,23,43
Last:               BC-02 (every capability's owner must exist and run)          BC-36(admission) after OD-P2-02
Then:               AC-14 R1-preservation verification of the new candidate; AC-6 fresh oracle-format review;
                    iteration-1 independent capability verification.
```

## 3. Workstream partition (single file owner per path)

Each workstream owns the files listed; another workstream that needs a change in an owned file supplies it as an
integration point to the owner (named below). Shared hot spots are listed in §3.1.

| WS | Scope | Owned files (non-overlapping) | Classes |
|---|---|---|---|
| WS-1 | Contract binding and evidence map | `runtime/src/contracts.rs`; `framework/contracts/**`; `framework/schemas/governance-capability-acceptance.schema.json`; `tests/governance/capability-evidence-map.yaml`; `docs/generated/**` | BC-01, BC-02 |
| WS-2 | Health scheduler, currency, health verdict, governance families | `runtime/src/verification/**`; `runtime/src/doctor.rs`; `runtime/src/observability.rs`; `runtime/src/skills.rs`; new scheduler module; `framework/policies/TEST_POLICY.yaml`; `framework/schemas/audit.schema.json` | BC-03, BC-06, BC-07 (engine + tier contract), BC-22, BC-23, BC-42, BC-43, BC-44 |
| WS-3 | Identity, authority, Human Decision Gates, policy precedence | `runtime/src/authority.rs`; `runtime/src/project.rs`; `runtime/src/orchestration/control.rs`; `runtime/src/orchestration/gates.rs`; `runtime/src/policy.rs`; `runtime/src/policy_precedence.rs`; `runtime/src/policy_coverage.rs`; `runtime/src/routing.rs`; `cli/src/main.rs`; `framework/policies/{AUTHORITY_POLICY,HUMAN_GATE_POLICY,POLICY_PRECEDENCE,MODEL_ROUTING_POLICY,ENFORCEMENT_MAP}.yaml`; `framework/schemas/{human-gate,decision,model-routing-overrides,roles}.schema.json`; `framework/roles/**`; `framework/overlay-templates/MODEL_ROUTING_OVERRIDES.yaml` | BC-08, BC-09 (gate/decision/CIT binding + primitive), BC-10, BC-12 (answer side), BC-18 (resolution rules), BC-45, BC-49 |
| WS-4 | Change control, propagation, Gate-W delivery, continuity | `runtime/src/cit/**`; `runtime/src/graph/**`; `runtime/src/context/**`; `runtime/src/checkpoints.rs`; `runtime/src/orchestration/handoffs.rs`; `runtime/src/records.rs` (relation fields/edges region); `framework/policies/{CHANGE_POLICY,CHECKPOINT_POLICY,CONTEXT_POLICY}.yaml`; `framework/schemas/{cit,checkpoint,context-packet,handoff,record,requirement,feature,interface}.schema.json` | BC-04, BC-05, BC-11 (CIT side), BC-13 (CIT-P side), BC-17, BC-19, BC-20 (contract + lineage), BC-21 (records) |
| WS-5 | Task lifecycle, DAG, claims, readiness, work generation | `runtime/src/orchestration/{tasks,dag,readiness,claims,intents}.rs`; `runtime/src/memory/claims.rs`; `runtime/src/status.rs`; `framework/schemas/{task,report,worker-return,test-obligation}.schema.json`; `framework/taxonomy/**` | BC-14, BC-15, BC-16, BC-24; host side of BC-07 (G2), BC-09 (close exemption), BC-12 (DAG), BC-13 (in-task detection), BC-20 (close validation), BC-34 (task roles) |
| WS-6 | Knowledge fabric and retrieval | `runtime/src/memory/**` except `claims.rs`; `runtime/src/retrieval/**`; `runtime/src/code_intelligence/**`; `runtime/src/paths.rs`; `runtime/src/security/**`; `runtime/src/records.rs` (record-text/chunk region); `framework/policies/{MEMORY_POLICY,SECURITY_POLICY,ARCHIVE_POLICY}.yaml`; `framework/overlay-templates/{REPOSITORY_CONTRACT,DATA_SENSITIVITY}.yaml`; `framework/schemas/{index-manifest,memory-manifest,repository-contract,data-sensitivity,heldout-tests}.schema.json`; `capabilities/python/govos_capabilities/code_intel_*` | BC-25, BC-26, BC-27, BC-28, BC-29, BC-30, BC-31, BC-32 |
| WS-7 | Plugin and tool trust | `runtime/src/capabilities/**`; `runtime/src/srr/plugins.rs`; `runtime/src/tools.rs`; `framework/policies/TOOL_POLICY.yaml`; `framework/schemas/{plugin-descriptor,plugin-registry,tool,tool-registry,tool-permissions,mcp-registry}.schema.json`; `capabilities/**` except code_intel | BC-39, BC-40, BC-41, BC-11 (plugin side), BC-09 (registry side) |
| WS-8 | Root of trust and lifecycle ingress | `runtime/src/kernel_trust.rs`; `runtime/src/kernel.rs`; `runtime/src/lock.rs`; `runtime/src/srr/**` except `plugins.rs`; `runtime/src/init.rs`; `runtime/src/update.rs`; `runtime/src/release.rs`; `runtime/src/recovery.rs`; `framework/schemas/{framework-lock,kernel-manifest,release-manifest}.schema.json` | BC-35, BC-36, BC-37, BC-38; host side of BC-07 (G5 update/release) and BC-08 (init call site) |
| WS-9 | Adoption, migration, legacy | `runtime/src/adopt.rs`; `runtime/src/migrations/**`; `framework/schemas/{migration,migration-catalogue-entry,adoption-baseline}.schema.json`; `migrations/**` | BC-33, BC-34 (adoption), BC-52, BC-21 (catalogue/plan identity); host side of BC-07 (G5 adopt) and BC-08 (adopt call sites) |
| WS-10 | Research, experiment and test-data records | new research/experiment lifecycle module; `framework/schemas/{research,experiment,scenario}.schema.json` | BC-46, BC-47, BC-48 |
| WS-11 | Learning and export | `runtime/src/upstream.rs`; `runtime/src/lessons.rs`; `framework/policies/LEARNING_POLICY.yaml`; `framework/schemas/{upstream-packet,lesson,framework-change-proposal}.schema.json` | BC-50; export-approval use of BC-10 |
| WS-12 | Qualification Oracle format | a new, separate oracle-format definition and validator (not part of the public qualification suite) | BC-51 (+ AC-6 fresh review) |

### 3.1 Shared hot spots and integration rule

- `cli/src/main.rs` (WS-3): all CLI surface changes (new subcommands for WS-2 scheduler, WS-10 lifecycles, role plumbing)
  go through WS-3 or are merged sequentially after WS-3's role-resolution change.
- `runtime/src/orchestration/tasks.rs` (WS-5): receives four integration points — the G2 tier call (WS-2), removal of
  the OS-managed exemption in favour of the T2 binding primitive (WS-3), receipt validation (WS-4) and in-task
  material-change detection (WS-4). WS-5 applies them in that order.
- `runtime/src/records.rs`: two disjoint regions — relation fields/edges (WS-4) and record text/chunk builder (WS-6).
- `runtime/src/doctor.rs` (WS-2): the posture/authenticity check (WS-8) and the plugin checks (WS-7) are added by WS-2
  against APIs the owners expose.
- `runtime/src/init.rs` / `runtime/src/adopt.rs`: role plumbing for BC-08 is written by their owners (WS-8, WS-9) against
  WS-3's resolution API.

## 4. What iteration 1 must present

A new candidate tag and `product_code_digest`; the AC-14 R1-preservation verdict for it; the AC-6 oracle-format verdict;
per class, the builder's claim with the probes named above re-run (builder evidence is regression only); and the owner's
answers to OD-P2-01 and OD-P2-02 (or an explicit deferral, in which case BC-P2-36's admission requirement and any
agent-identity extension of BC-P2-34 stay open without blocking the determined parts).
