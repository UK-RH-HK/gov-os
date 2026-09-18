# P2-AR-0010 — iteration-0 capability baseline re-audit, family `gamma`

| Field | Value |
|---|---|
| Run | P2-AR-0010, fresh independent Governance Capability Baseline Auditor (re-audit under P2-HO-0009) |
| Agent model | `claude-opus-5[1m]` (Opus 5, 1M context) |
| Scope | Contract v3 Gates E (E1–E4), F (F1–F5), G (G1–G2), H (H1–H4), I (I1–I4) — P2-HO-0003 |
| Candidate | `cap2-candidate-0` = `57177a37ea296ece16b185874831462b6a76db18` |
| Audited worktree HEAD | `7eddf9103311a8e2ad144bcf61788f16b460782c` (candidate + one orchestration-only commit carrying P2-HO-0009) |
| `product_code_digest` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` (verified at HEAD, at the candidate and at `srr1-r1-accepted` `c7d3fef`) |
| Binary under test | `target/release/gov` built in the worktree, sha256 `3271ce0e4e095561911e0d03d8641aa92fbeda39ef3c8a2ecb2a9f21cacbe81d` |
| Verdict | `FAMILY_AUDIT_COMPLETE` |

## 1. Result in one paragraph

Of 19 capabilities, 4 are `PRESENT_AND_SUBSTANTIAL` (G2, H1, H2, I1) and 15 are `PARTIAL`; none is `ABSENT`, `UNCLEAR` or
`N/A_WITH_REASON`. 167 checklist items were evaluated individually (165 checkbox lines + the two normative qualifiers at
lines 385 and 515): 115 present and substantial, 42 partial, 10 absent. 36 findings were recorded (11 HIGH, 21 MEDIUM,
4 LOW); **19 are blocking** because the PARTIAL capability they sit in could undermine advanced qualification (AC-3) or
because F4 is not fully incorporated (AC-4). Two require an owner decision (A0-E1-04, A0-F4-03). **AC-4 (F4): not met** —
the Phase-1 R1 acceptance is still valid for this candidate, but four above-floor plugin-trust defects remain.

## 2. Pinned-input verification (all verified; no STOP)

| Input | Expected | Observed |
|---|---|---|
| `product_identity.py HEAD` | `bd4d65d9…0547` | `bd4d65d9d5ffd6aedbd9435e2091a664dfc3e62f80614a76197cfaf87efd0547` |
| Tag `cap2-candidate-0` | candidate commit | resolves to `57177a3…`; same digest |
| `srr1-r1-accepted` | same product digest | `c7d3fef…`, digest `bd4d65d9…0547` |
| Contract v3 owner source | `4c2df291…5ed3` | `4c2df29115c8d5389034b2e2d817772add80d61678807c23e0d520c937cb5ed3`; canonical import byte-identical |
| Frozen gate contract | `ORCHESTRATOR_STATE.yaml frozen_gate_contract.sha256` | `d2f33e89d5459dd809e17271e46854cc886ed958ca63f89765e16d6a26a9f25e` (matches, revision 1) |
| Frozen R0–R3 boundary | `70977d11…99c1` | `70977d11b778c4a8391a65cb3e0f53103bcc1e565de595c1e83150797f1699c1` |
| `gov contract verify` | CONTRACT_SOURCE_BOUND | ok (evidence/DV-derived-views.out) |

## 3. Method

* Read, in order: P2-HO-0009, P2-HO-0000, P2-HO-0003, the frozen gate contract, AGENT_RUNS/README; Contract v3 in full;
  framework Parts VI–XI (§§23–44) and the sections they cite (§2, §11.1, §47–48, §59–61, §63, §67); D-0003, D-0004,
  D-0005, D-0007, API-0001, API-0002; ARCH-0003 §§7–9; docs/ARCHITECTURE.md §4.8; the Phase-1 R1 reports and held-out
  suites for F4. I did **not** read `audit-0/gamma/`, any `P2-AR-0003.*` file, any other family's evidence, transcripts,
  task-output stores or auto-memory.
* Read the implementation for every capability (authority, orchestration/*, skills, tools, capabilities/*, srr/plugins,
  records, status, context, routing, cit, verification, init, adopt) and built every probe from it.
* **Every bullet was exercised** against disposable projects (`gov init` from the embedded kernel into fixture copies,
  each with its own simulated machine via `XDG_STATE_HOME`, exactly as the builder harness does). Probe sources and their
  captured outputs are in `evidence/`; `capability-audit.yaml` cites the exact lines of the output that demonstrate each
  bullet. `evidence/lib.sh` documents the environment; each `evidence/<name>.sh` regenerates `evidence/<name>.out`
  (`PROBES=<scratch> bash <name>.sh > <name>.out`, run from the evidence directory).
* A file-snapshot helper (`evidence/treesnap.py`) proves whether a command mutated the repository (E1 census, F5).
* Builder regression (O3 — regression evidence only): `cargo test --lib` 42/42, `cargo test --test certification` 79/79
  (`evidence/REGRESSION-builder-suites.out`).
* AC-4: the Phase-1 R1 iteration-4 held-out suite was re-run **unedited** against this candidate
  (`evidence/F4-AC4-r1-heldout-rerun.sh/.out`): 31/31 pass.

## 4. Per-capability summary

| Cap | Title | Status | Items | P&S | PARTIAL | ABSENT | Qualification impact | Findings |
|---|---|---|---|---|---|---|---|---|
| E1 | Authority levels | PARTIAL | 4 | 1 | 3 | 0 | COULD_UNDERMINE | A0-E1-01, -02, -03, -04, -05 |
| E2 | Representative roles | PARTIAL | 7 | 6 | 0 | 1 | CANNOT_UNDERMINE | A0-E2-01 |
| E3 | Typed A2A handoffs | PARTIAL | 8 | 7 | 1 | 0 | CANNOT_UNDERMINE | A0-E3-01 |
| E4 | Concurrency/task claims | PARTIAL | 5 | 2 | 3 | 0 | COULD_UNDERMINE | A0-E4-01, -02, -03, -04 |
| F1 | Skill lifecycle | PARTIAL | 4 | 1 | 3 | 0 | CANNOT_UNDERMINE | A0-F1-01, -02, -03 |
| F2 | Tool Capability Registry | PARTIAL | 8 | 4 | 4 | 0 | CANNOT_UNDERMINE | A0-F2-01, -02 |
| F3 | Missing-tool acquisition | PARTIAL | 9 | 4 | 5 | 0 | COULD_UNDERMINE | A0-F3-01, -02, A0-F4-05 |
| F4 | Plugin trust boundary [PVH] | PARTIAL | 6 | 0 | 6 | 0 | COULD_UNDERMINE | A0-F4-01..05, A0-F2-02 |
| F5 | MCP/A2A/tool separation | PARTIAL | 4 | 3 | 1 | 0 | CANNOT_UNDERMINE | A0-F5-01 |
| G1 | Natural-language intent | PARTIAL | 3 | 0 | 3 | 0 | COULD_UNDERMINE | A0-G1-01, -02, A0-I2-02 |
| G2 | Small explicit human control set | **PRESENT_AND_SUBSTANTIAL** | 5 | 5 | 0 | 0 | — | — |
| H1 | SPEC lineage | **PRESENT_AND_SUBSTANTIAL** | 17 | 17 | 0 | 0 | — | — |
| H2 | 26-dimension readiness contract | **PRESENT_AND_SUBSTANTIAL** | 32 | 32 | 0 | 0 | — | — |
| H3 | Readiness generates work | PARTIAL | 5 | 3 | 2 | 0 | COULD_UNDERMINE | A0-E4-02, A0-H3-01, A0-E1-05 |
| H4 | Scenarios drive data/tests | PARTIAL | 3 | 0 | 3 | 0 | COULD_UNDERMINE | A0-H4-01, -02, -03 |
| I1 | Unified task DAG | **PRESENT_AND_SUBSTANTIAL** | 22 | 22 | 0 | 0 | — | — |
| I2 | Task contract | PARTIAL | 9 | 4 | 5 | 0 | COULD_UNDERMINE | A0-I2-01, -02, -03, A0-E1-02 |
| I3 | Dynamic generation | PARTIAL | 11 | 1 | 1 | 9 | COULD_UNDERMINE | A0-I3-01 |
| I4 | Parallel execution | PARTIAL | 5 | 3 | 2 | 0 | CANNOT_UNDERMINE | A0-I4-01, A0-E4-04 |

Criterion used for PARTIAL impact (stated once in `capability-audit.yaml`): COULD_UNDERMINE when the gap lies on a path the
Contract v3 advanced-qualification challenges (or the AC-5/AC-8 observation) exercise, so qualification would be
predictably failed or its measurements made unreliable; otherwise CANNOT_UNDERMINE with the argument stated per capability.

## 5. The most important findings (blocking)

1. **A0-E1-01 (HIGH)** — `gov init` and every `gov adopt`/`migrate` stage ignore `--role`: authority is checked against
   `GOV_ROLE` or the default `orchestrator`. An L0 role reinstalls the kernel and runs a full brownfield migration; the
   same calls with `GOV_ROLE` are refused. The builder tests pass `--role` to adopt and never see it.
2. **A0-E1-02 (HIGH)** — An L1 worker writes ANSWERED gate records and `human_approved` decision records under
   `spec/decisions/`; task close exempts those OS-managed prefixes; the forged answer unblocks a gated task and makes
   `cit approve --method human` succeed and `cit execute` commit. Suite and doctor are silent. (Also AC-16 L3↔E1.)
3. **A0-E4-01 (HIGH)** — Claims are check-then-insert: three simultaneous sessions were all granted the same claim in
   15/15 trials.
4. **A0-E4-02 (HIGH)** — `task claim` checks only the stored status; READY is caller-settable. A dependency-blocked task was
   claimed and closed DONE before its dependency; a readiness-blocked implementation task was claimed.
5. **A0-F4-01 (HIGH)** — Any presented, answered-A gate (here "May we rename the docs folder?") authorises registration
   and execution of an elevated network plugin; plugin registration has no equivalent of CIT's `GATE_MISMATCH`.
6. **A0-F4-02 (HIGH)** — The plugin registry is a plain file under the exempt `governance/generated/` prefix; a worker's
   forged entry made an unapproved network plugin run, undetected by D028/`plugin_governance`, and without staling the
   green governance record.
7. **A0-F3-01 (HIGH)** — An install gate answered A can never lead to installation (a new gate is raised every time).
8. **A0-G1-02 (HIGH)** and **A0-I2-02 (HIGH)** — Consequential spec changes made inside ordinary tasks close with no
   impact simulation or gate, and any path once touched by any committed CIT is permanently in scope for every later task.
9. **A0-I3-01 (HIGH)** — Only readiness gaps generate tasks; failed tests, audit/security findings, discoveries,
   decisions, lessons, capability gaps, retrieval failures and performance regressions generate none.
10. MEDIUM, blocking: A0-E1-03 (replan/heldout-starter unauthorised), A0-E1-05 (tester independence self-attested; task
    role not enforced), A0-E4-03 (no worktree identity, no mutation-overlap constraint), A0-F4-03 (self-declared elevation;
    owner decision), A0-F4-05 (security review satisfied by any record), A0-H4-01/02/03 (data/test-data chain,
    data-author independence, provenance), A0-I2-01 (blocks/required_data/required_tools/production merge unenforced).

Non-blocking findings (justified PARTIALs, CANNOT_UNDERMINE, or owner decisions): A0-E1-04 (caller-declared role; owner
decision), A0-E1-06 (derived views headings-only), A0-E2-01, A0-E3-01, A0-E4-04, A0-F1-01/02/03, A0-F2-01/02, A0-F3-02,
A0-F4-04, A0-F5-01, A0-G1-01, A0-H3-01, A0-I2-03, A0-I4-01. Full statements, normative sources, reproductions and repair
directions are in `findings.yaml`.

## 6. AC-4 determination for F4 (POST_VERIFICATION_HARDENING)

**Determination: AC-4 is NOT met for F4.** The R1 acceptance F4 rests on is still valid for this candidate (identical
`product_code_digest`; R1-4 held-out `hv_a`/`hv_b`/`hv_c`/`hv_d` 10+7+6+8 = 31/31 pass unedited here; builder
certification 79/79 including the plugin tests), but F4 is not fully incorporated: A0-F4-01, A0-F4-02, A0-F4-03 and
A0-F4-05 are blocking defects in the above-floor plugin trust boundary that the R1 scope (release root of trust, §6
below-floor effects, SRR-R0-L6 acquisition classes) did not examine.

| F4 bullet | Phase-1 R1 evidence it maps to | Confirmed on this candidate | Remaining gap |
|---|---|---|---|
| 426 Descriptor cannot authorise itself | R1 item 9 (descriptor `provenance` stripped; AR31-N2: descriptor cannot decide whether §6 is asked — `hv_d::d4`); SRR-R0-L6; builder `repair3::plugin_descriptors_can_never_authorise_themselves` | claims ignored/refused, L2 floor from kernel, D028 reports claims (F4-plugins.out:3-12); `hv_d::d4` ok (F4-AC4 rerun :42) | self-declared elevation (A0-F4-03); descriptor chooses its gate (A0-F4-01); registry view (A0-F2-02) |
| 427 Registration/provenance in trusted OS state | R1 item 9; SRR-R0-L6 "kernel-owned registration"; SRR-R0-L3 (repository gate records are requests only for trust changes) | registration by `gov plugins register` only, provenance rewritten (F4:17-24) | registry forgeable and exempt at close, not detected, not invalidating (A0-F4-02) |
| 428 Descriptor/implementation bytes hash-bound | R1 item 11 (original controls valid; `repair2::plugins_are_governed_capabilities_not_arbitrary_commands`) | registry binds descriptor + implementation sha256 (F4:28-39) | unregistered plugins only machine-local TOFU; interpreter-only unpinned (A0-F4-04) |
| 429 Drift/tampering fails closed | R1 item 11 | PIN/REGISTRY_MISMATCH on tamper (F4:31-42) | TOFU reset accepts tampered bytes (A0-F4-04) |
| 430 Elevated permissions reference authoritative gate/decision | R1 item 9 (§6 bullet 5 asked unconditionally below floor, `hv_d::d4`); SRR-R0-L6 delegated targets (`SRR_PLUGIN_NOT_DELEGATED`, F4:25-26) | gate raised, answered-A required, revocation withdraws (F4:49-59) | gate not bound to the plugin (A0-F4-01); undeclared elevation needs no gate (A0-F4-03) |
| 431 Security review cannot be self-attested | D-0007 consequence 4 (pre-R1 trust audit); R1 item 11 | plugin descriptors cannot carry the claim; tool claim without record fails (F4:11-12, 88-92) | any existing record satisfies it (A0-F4-05) |

## 7. Family-specific duties

* **H2 — 26 dimensions and statuses (silent N/A invalid).** Each of the 26 dimensions is its own item
  (H2H3-readiness.out:4-29), each of the five statuses is its own item (:33-37), and the silent-N/A clause is evaluated
  separately (:38-39, 44, 47-48). All 32 hold.
* **I1 — 22 task classes.** Each class created, validated, tiered and scheduled in one DAG (I1I2-tasks.out:4-25); all hold.
* **I3 — 11 generation sources.** Each source triggered through the product and the task delta counted
  (I3-generation.out:4-45): readiness gaps generate; CIT effects only flag retest; nine sources generate nothing.
* **G1 — deterministic intent.** Framework §33 requires NL intent to be "translated into deterministic operations"; the
  kernel COMMAND_CONTRACT defines T0 substring patterns and states "Provider adapters may add an LLM intent parser in
  front", so an LLM is neither required nor forbidden. `gov intent` is byte-deterministic but covers control phrases only,
  inverts negations, is not wired into adapters and invokes nothing; consequential changes invoke CIT-P/gates only when
  routed through `cit propose` (A0-G1-01, A0-G1-02).
* **AC-16 L3 ↔ E1 (E1 side).** Exercised (E1-authority.out:199-215): through the CLI, presentation needs L1, answering
  needs presentation and L3 relay, agent resolution needs L3 within `agent_resolvable_when`, revocation needs L4 and
  withdraws the derived decision. It fails outside the CLI (A0-E1-02) and at the identity boundary (A0-E1-04).

## 8. Freshness and health-scheduler tiers

* Evidence is `FRESH_FOR_CANDIDATE` for every capability (produced on this exact build).
* Invalidation demonstrated (FRESH-invalidation.out): after a green governance record, changing TOOL_PERMISSIONS (:7-10),
  adding a project skill (:12-15) or a decision (:17-20) makes a governance-touching close fail `GOVERNANCE_SUITE_STALE`;
  editing kernel ROLES/AUTHORITY_POLICY/READINESS_DIMENSIONS/COMMAND_CONTRACT/TOOL_POLICY fails every mutation
  `KERNEL_TAMPERED` (:33-39). Not invalidating: plugin-registry edits (:22-25 — part of A0-F4-02); feature/task records are
  evaluated live, so there is no cached green to stale (:27-31).
* There is no explicit G0–G6 scheduler in the product. The observing tiers for gamma are embedded checks: G0 (authority +
  guard_write in each command), G1 (incremental rebuild, CIT propagation), G2 (task close), G3 (handoff/checkpoint), G4
  (CIT-E), G5 (the 20-family suite and doctor); G6 does not exist (Phase 4). Per-capability detail and whether each tier
  actually runs are in `capability-audit.yaml`.

## 9. Derived views

For all 19 gamma capabilities the compiled form, evidence map and generated view carry faithful ids, titles, requirement
classes and source lines, but the compiled form carries no checklist bullets and none of the Contract v3 lines 53–73
fields, and the evidence map lists zero automated checks (`NOT_YET_MAPPED`, the carried Phase-1 residual AR27-N7)
(DV-derived-views.out; A0-E1-06, non-blocking at family level; AC-10/AC-13 weighing is the synthesis auditor's).

## 10. What I could not establish, limits, observations

* **Concurrency beyond claims** (e.g. concurrent CIT execution, concurrent handoff returns) was not stress-tested; only
  claims were raced.
* **Stale-claim invalidation (E4) and I3 freshness** were not demonstrated by input change (`not_attempted`).
* **Skill validation scenarios** cannot be executed without agents; I established only that no harness exists.
* **The identity boundary (A0-E1-04)** is documented by the product; I did not attempt to design around it.
* Observations (not findings in my scope): a refused `init` leaves `governance/kernel`, `generated` and `project` behind
  (E1-authority.out:72-76); an L0 auditor cannot run `gov continue` while a gate is pending (:185-186); upstream submit's
  human approval is a CLI string (F1-skills.out:86-89; families Q4/L3); `--role` given to the `tools install` subcommand
  replaces the acting role (same caller-declared boundary as A0-E1-04); the no-baseline porcelain truncation also affects
  `gov recover`'s dirty-governance classification (A0-I2-03).

## 11. Files

`capability-audit.yaml` (19 capabilities, per-bullet records), `findings.yaml` (36 findings), `evidence/` (17 probe
scripts + outputs, `lib.sh`, `treesnap.py`, `DV-derived-views.py`, builder regression, R1 held-out rerun).
