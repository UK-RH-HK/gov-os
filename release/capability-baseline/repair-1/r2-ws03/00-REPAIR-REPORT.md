# WS-3 (+ docs) repair report: repair iteration 1, round 2 (P2-AR-0024)

| | |
|---|---|
| Run | P2-AR-0024, role `capability-repair`, model Claude Opus 5 (1M context), `claude-opus-5[1m]` |
| Handoffs | P2-HO-0022 (WS-3 round 2), P2-HO-0020 (round-2 common), P2-HO-0010 (common protocol) |
| Branch / base | `phase2/repair-1-r2-ws03` from `843d79c33e8a8db8b223611abc23d317edbc82a1` (integrated round-1 tree, `product_code_digest b1ab1c8c…fbb1`) |
| Work commits | `7dcf2e0` (product, tests, docs; `product_code_digest e84b9a91e9654e3e292eeed8d19476ef62891f603a9f7d7afbe914fbe3dbd504`), then the commit that adds this report, `claims.yaml` and `evidence/` (no product file) |
| Items | P2-ADJ-0001; O-1 (BC-P2-45 compatibility regression); O-4; BC-P2-08 remaining call-site/guard work; IP-WS02-08, IP-WS02-09, IP-WS02-11; ws04 IP-6; ws06 IP-6; ws08 IP-3; ws09-11 IP-3; docs (ws03 IP-11, ws05 IP-8) |
| Claims | `REPAIRED_CLAIMED`: P2-ADJ-0001, O-1, O-4, BC-P2-08 remainder, IP-WS02-08 (for the operations that start/hand off/complete work; see §3.1), IP-WS02-09, ws06 IP-6, ws08 IP-3, ws09-11 IP-3, docs. `PARTIAL`: ws04 IP-6 (CLI side; WS-5 accepts the handle). `NOT_REPAIRED` (not in WS-3 files): IP-WS02-11 (optional) |

**Status of these claims.** They are the builder's; the evidence is regression evidence (Contract v3 O3). Nothing here says an
item is accepted, verified or closed.

---

## 0. Evidence index and regression (all at `7dcf2e0`)

| What | Where | Result |
|---|---|---|
| `cargo test --lib` | `evidence/regression/REGRESSION-lib.out` | **149 passed, 0 failed** (146 at base + 3 new unit tests) |
| `cargo test --test certification` (includes `section6::*`, `srr::*`, `ws03::*`, `ws08::*`) | `evidence/regression/REGRESSION-certification.out` | **103 passed, 0 failed** (100 at base + 3 new `ws03` tests) |
| rustfmt on every changed Rust file, build warnings, diffstat | `evidence/regression/RUSTFMT-WARNINGS-DIFFSTAT.out` | 0 hunks in each file; 0 warnings; 18 files |
| R1 held-out suites, all four rounds, **unedited**, private scratch path, this worktree | `evidence/r1-heldout/r1-heldout-final-7dcf2e0.out`, runner `run-r1-heldout.P2-AR-0024.sh` | AR-0027 26/3, AR-0029 26/2 (+ `ho_f` does not compile), AR-0031 27/7, AR-0033 30/1 — each the recorded baseline, same tests (§6) |
| Round-2 builder probes (O1, ADJ, G0, CS lines) | `evidence/R2-WS03-probes.py`; `probes/R2-WS03-probes.final.out`; negative control `probes/R2-WS03-probes.base-843d79c.out` | final **24/24 PASS**; base 5/24 (19 FAIL: every repaired line) |
| Integration O-1 script, unedited | `probes/O1-integration-script.unedited.{base-843d79c,final}.out` | base: 7 descriptive keys refused, D027 CRITICAL, update rolled back; final: none refused, D027 ok (its human-answer step now stops at P2-ADJ-0001, §1) |
| Round-1 WS-3 named checks | unedited `probes/ws03-named-checks.unedited.final.out`; derived copy `ws03_named_checks.r2-derived.py` → `probes/ws03-named-checks.r2-derived.final.out` | unedited: 15 PASS, 1 intended FAIL (O-4), then stops at standalone-anchor provisioning (P2-ADJ-0001); derived: **39/39 PASS** |
| Round-1 WS-3 derived O5-G0 guard matrix, unedited | `probes/O5-G0-guard-matrix.derived-r1.final.out` | under FREEZE_WRITES and PAUSE only `rebuild-memory`, `memory rebuild`, `pause`, `freeze-writes` mutate |
| Audit-of-record probes, unedited | `probes/audit-shim/beta-r.D6-rebuild-guarantee.out`, `probes/audit-integrated/epsilon-r.O5-G0-focus.out` (runner `probes/run-audit-probe.P2-AR-0024.sh`) | D6 runs to completion (integrated round 1 stopped at the refused rebuild); O5-G0-focus every command FROZEN |
| Test material | `evidence/hc_root.py` (throw-away root), `evidence/r2_machine.py` (probe machine) | published seeds only |

---

## 1. O-1 — projects on a shipped older kernel keep their descriptive overlay (BC-P2-45 compatibility)

**Requirement.** Contract v3 S5 (preserve the project overlay; compatibility/migration) and A1 (a weakening is refused, a
description is not). Round-1 integration observation O-1: on the shipped 4.1.4/4.1.5 kernels the descriptive keys
`PROJECT_POLICY.project.{name,alias,created,onboarding_mode}` and `MODEL_ROUTING_OVERRIDES.{schema_version,providers,
preferences.*}` were refused "deny by default", D027 went CRITICAL, and an update to shipped 4.1.5 was rolled back.

**Cause.** `policy_precedence::load` used the installed kernel's `POLICY_PRECEDENCE.yaml`. The shipped kernels carry rules
for `policy_overrides` targets only; they predate the per-key evaluation of the overlay documents, so every overlay key
fell to their `default_mode: immutable`.

**Change** (`runtime/src/policy_precedence.rs`, `runtime/src/policy.rs`).
- `policy_precedence::Governing` holds every rule set that governs a repository: the installed, verified kernel's rules
  (or the embedded fallback when it has none) and the constitutional floor compiled into the binary (`embedded()`),
  the latter only when it differs.
- `Governing::evaluate` evaluates a key against every set that **declares** its policy or overlay label (has at least
  one rule for it) and accepts it only when **every** declaring set accepts it. A set that declares no rule at all for a
  label predates that label's evaluation and does not govern it. When no set declares a label, the installed set's
  default (deny) applies. A refusal by the binary's floor names that rule set.
- `PolicySet::load` uses it for `policy_overrides`, `PROJECT_EXCEPTIONS` and both overlay documents;
  `gov policy overrides` / context packet layer 3 show `precedence.governing_sets`.

**No floor is re-opened.** The change can only refuse more than before for a label the installed kernel declares (both
sets must accept), and for a label it does not declare the binary's current floor applies in full — the same one a
current-kernel project gets. On the shipped 4.1.4 kernel, readiness weakening, the catch-all `immutable`
(`governance.*`), the tier floor, the authority floor and the binary's new failure-memory floor are all still refused
(O1.c). A newer kernel that relaxed a rule the binary still enforces would be refused (fail closed).

**Product check and tier.** Policy load, i.e. every command (G0), doctor D027 (CRITICAL, a hard-block since §3.1), suite
family `policy_precedence`.

**Probes (before = 843d79c, after = 7dcf2e0).**

| Line | Before | After |
|---|---|---|
| integration `old_kernel_overlay_precedence.py` (unedited): refused keys on shipped 4.1.4 | 7 descriptive keys | none |
| same: doctor | UNHEALTHY, D027 CRITICAL | DEGRADED, D027 ok |
| same: update 4.1.4 → shipped 4.1.5 | `VERIFICATION_FAILED … D027 — update rolled back` | not reached as the script intends: its answer provisions a standalone anchor, refused since P2-ADJ-0001, so `update --apply --approve` returns without applying (INV-008). The provisioned reproduction is O1.d |
| R2 O1.a descriptive keys on signed shipped 4.1.4 (provisioned machine) | FAIL | PASS |
| R2 O1.b D027 on 4.1.4 | FAIL | PASS |
| R2 O1.c every weakening still refused (exact set) | FAIL | PASS |
| R2 O1.d update 4.1.4 → shipped 4.1.5 through the owner-signed gate applied | FAIL | PASS |
| R2 O1.e D027 clean after the update; two governing sets | FAIL | PASS |

**Tests.** Unit `a_rule_set_silent_on_a_label_does_not_govern_it_and_the_stricter_set_wins`; certification
`ws03::a_project_on_a_shipped_older_kernel_keeps_descriptive_overlay_keys_and_every_floor` (provisioned, signed test
releases of the shipped kernels; floors refused; update applied; D027 clean).

---

## 2. P2-ADJ-0001 — the standalone human-gate anchor is off by default

**Requirement.** P2-ADJ-0001 (orchestrator adjudication from OWNER-DECISION-P2-0002 and ARCH-0003 §2-§3): default
`false`; on an unprovisioned machine a human answer is refused typed and observable with remediation *provision*;
regression test.

**Change.**
- `framework/policies/HUMAN_GATE_POLICY.yaml`: `human_channel.standalone_anchor_when_unprovisioned: false`, with the reason.
- `gates::standalone_anchor_allowed`: code default `false`, so a kernel that predates the key (shipped 4.1.4/4.1.5) never
  enables it by silence.
- `human_channel::anchor`: with no release root and the switch off → `HUMAN_CHANNEL_UNAVAILABLE`, `details.cause:
  UNPROVISIONED`, `remediation` (provision a root whose `human-gate` role delegates the owner's key(s); dev/test machines
  provision a throw-away root), `provision_command`, `standalone_anchor_present` (a file placed in machine state is not
  honoured), `policy`. Every other unavailability now also carries a `cause` (`ROOT_DELEGATES_NO_HUMAN_GATE`,
  `NO_ANCHOR`, `MACHINE_STATE_UNRESOLVED`).
- `human_channel::provision_standalone(file, project_root, standalone_allowed)`: refused
  `HUMAN_CHANNEL_STANDALONE_DISABLED` (after the §6 `guard_effect`, before anything is read or written) while the switch
  is off.
- `human_channel::standalone_allowed_by_embedded_kernel`: `gov trust human-channel` outside a project reports the
  binary's kernel value (the CLI used `true` there before).
- Precedence: the existing strengthen-only rule (strict `false`) now also refuses `true` where the kernel declares no
  value; unit test.
- `ENFORCEMENT_MAP`: `human_channel.*` also names `human_channel::provision_standalone`.

**Observable.** `gov trust human-channel` (`available: false`, `standalone_anchor_permitted_by_policy: false`,
`unavailable_reason` with the remediation); `gov decide` exit 1 with the typed error; the O5-G0 matrix row `decide`
shows `HUMAN_CHANNEL_UNAVAILABLE` on the unprovisioned matrix machine.

**Probes.** R2 ADJ.a–ADJ.h: base 1/8 (ADJ.h held already), final 8/8 — kernel value false; status unavailable with the
remediation; owner-signed answer refused `UNPROVISIONED`; standalone provisioning refused and nothing written; a planted
anchor file not honoured; a project override to `true` refused and the effective value stays false; after provisioning a
root that delegates `human-gate` (and re-verifying the kernel) the same owner's answer is honoured and re-verifies; a root
without `human-gate` gives no channel.

**Tests.** `ws03::the_standalone_human_gate_anchor_is_off_and_an_unprovisioned_machine_refuses_human_answers`; the
channel test `ws03::human_answers_come_only_from_the_owner_signed_channel` now asserts `UNPROVISIONED`,
`HUMAN_CHANNEL_STANDALONE_DISABLED`, `SRR_ANCHOR_FROM_REPOSITORY_REFUSED` and `SRR_ALREADY_PROVISIONED` (an agent's own
root) instead of the standalone-anchor refusals; unit `the_embedded_kernel_keeps_the_standalone_anchor_off`.

**Consequence for the certification harness (tests changed, §5).** With the switch off, no human answer exists on an
unprovisioned machine, so every test that answers a gate needs a provisioned root that delegates `human-gate`.
`ws03::human_channel(g)` uses an available channel as it is (e.g. a harness root delegating to `ws03::owner()`);
otherwise it provisions the throw-away root `ws03::throwaway_root` (srr_material Publisher keys + the test owner's
`human-gate` key) and re-verifies the kernel installed while unprovisioned against a signed release of the pinned payload
(`ws03::reanchor_installed_kernel`). The three tests that update an unprovisioned installation with an unsigned source
and then roll back (`update::…`, `repair::update_approval_requires_presented_answered_gate`,
`repair2::genuine_412_consumer_updates_through_413_to_414_and_rolls_back_with_ledger`) now provision first, install and
update signed releases, and roll back below floor with the owner's break-glass authorisation — the flow
OWNER-DECISION-P2-0002 makes the only one. Every asserted property is kept.

---

## 3. BC-P2-08 remaining call-site/guard work and the routed integration points

### 3.1 IP-WS02-08 — the G0 hard-block site (`control::guard_write`)

`guard_write` now ends with `guard_health(p, operation)`, which calls `scheduler::guard(p, op, &[])` for the labels in
`control::GOVERNED_WORK_OPS`: `task create`, `task claim` (also reached by `continue --claim`), `task close` (also
`--force`), `cit propose`, `handoff create` — the operations BC-P2-06's acceptance names ("a hard-block state refuses task
create/claim/close/CIT propose") plus the handoff. A block whose inputs changed is re-evaluated first, so a repaired
condition never keeps refusing work.

**Deviation from the recipe, and why.** The IP's recipe maps every `catalogue::ops` operation. Wired that way, the
certification suite showed three ways a hard-block refused its own remedy:
- `brownfield_adoption_end_to_end`: D014/`schema_invariants` (duplicate id, supersession conflict; HIGH_RELY) refused
  `cit execute` of the governance-change CIT that repairs exactly that;
- `update::…` / `repair::update_approval…`: D006/D007 on an installed older release (HIGH_RELY) refused `update --apply`,
  the remedy;
- `srr::an_allow_listed_operation_cannot_create_a_human_gate_below_floor`: `update --apply` is an OWNER-DECISION-0006 §5
  restoration route; a health block masked the §6 refusal the test (and R1) asserts, and must not refuse a §5 route.

So the generic site guards the operations that start, hand off or complete work, and the operations that **apply** a
sanctioned change which may itself be the remedy (`cit approve|execute`, `update --apply|--rollback`, `adopt migrate`,
`release build`) stay with their hosts, which have the targets in hand (WS-4 IP-WS02-05, WS-8 IP-WS02-12/13, WS-9
IP-WS02-18). Those hosts meet the same three cases (§7, IP-R2-2). Unit test
`governed_work_labels_are_classified_writes_and_remedies_are_never_governed_work`.

**Evidence.** R2 G0.a (task create / claim / cit propose / handoff create refused `HEALTH_HARD_BLOCK` naming D027; base:
all allowed), G0.b (gate create, policy overrides, health status, checkpoint still run), G0.c (repair releases the block
without a manual re-run). Certification: `ws03::project_overlays_may_raise_floors_but_never_lower_them` and
`repair2::project_policy_cannot_weaken_constitutional_floors` now assert the refusal after the CRITICAL D027 finding
(their context-packet assertions run before the doctor run).

### 3.2 IP-WS02-09 — authority and FREEZE_WRITES class of evidence-writing commands (decision)

Decided as the integration registered them: `audit`, `verify governance`, `verify product`, `health run`, `health product`,
`health close-check` are **Write / `record_audit`** (L0: independent auditors record evidence); `health skills --record`
is Write / `record_skill_binding` (L3, declared). Under FREEZE_WRITES and PAUSE they are refused: each writes a governed
EVIDENCE record, and the controls exist so that no governed record changes. Diagnosis stays available through the
non-persisting forms (`audit --no-persist`, `health run --no-persist`, Read). Evidence: R2 G0.e (both controls),
certification G0 test rows `verify product`, `health run`, and a `health run --no-persist --tier G1` that writes nothing.

### 3.3 O-4 — `rebuild-memory` on the recovery allow-lists (decision)

**Decision: yes, on both FROZEN and PAUSED allow-lists (`rebuild-memory`, `memory rebuild`).** Reason (framework §19/§74;
Contract v3 B3 "indexes are derived; deleting derived state cannot delete project truth", D6 "all derived memory/index
state can be deleted and rebuilt", A5): the rebuild writes only the derived index (`.governance-runtime/state.db`) and its
generated manifests, deterministically from Git and the authoritative records (`MEMORY_POLICY.rebuild.must_reproduce_
manifest_hash`), so it cannot change project truth; inspection under the control (`status`, `memory query`, the context
packet) depends on it, and refusing it forced a `resume` — lifting the freeze for every agent — to repair derived state.
Any governed record it would write (tool-failure memory) still passes `guard_write` and is reported `not_recorded`.
Authority is unchanged (`rebuild_memory`, L0). `adapters generate` and `tools registry` were not moved: `governance/
generated/` also holds non-derived state (the plugin registry, A0-D6-02), and they were not adjudicated.

**Evidence.** R2 G0.d (both controls: runs, no authoritative/governed/evidence file changes; base: FROZEN/PAUSED); derived
named checks `O5-G0.*.rebuild-derived-only`; O5 matrix; beta-r `D6-rebuild-guarantee` unedited now runs to completion
(`D6-b1` PASS; its remaining FAILs `D6-b2-A-registry` and `D6-b2-B` are A0-D6-02/-01, not WS-3 classes).

### 3.4 WS-9/11 IP-3 — adoption stages record the declared actor

`adopt map` / `adopt plan` call `a3_map_by` / `a4_plan_by` with `Actor::declared(session, role)` when the invocation
declared a session (`--session` or `GOV_SESSION`) and the installed acting role; with no declared session the stage keeps
its documented fallback (the A0 planner session, recorded as such). Every other stage opens its projects with the
process-wide declared role (round 1). Evidence: R2 CS.a (producer session/role/`session_source: declared` in the catalogue
and the plan; base: `adoption-baseline planner session (A0)`, role null); certification
`ws03::round_two_call_sites_use_the_declared_role_and_typed_refusals`.

### 3.5 BC-P2-08 — one role per invocation at `tools install`

`tools install` evaluates its auto-install conditions (install authority, no privilege escalation) for the acting role,
not for a `--role` value handed to the runtime separately; `declared_role` treats that flag like the adopt stage flags.
With clap a `--role` after the subcommand is the same global flag, so the invocation has exactly one role (certification:
`tools install --role backend-engineer` is refused `AUTHORITY_DENIED` as `backend-engineer`).

### 3.6 WS-8 IP-3 — the pin refusal precedes break-glass (`kernel reinstall`)

The CLI binds `AdmissionRequest::with_pinned_payload(pin)` where the pin is unambiguous: framework.lock agrees with this
machine's protected record of what it committed into the project, or no record exists. **Deviation:** the recipe pinned
`framework.lock` unconditionally; that masked WS-8's own `KERNEL_PIN_REWRITTEN` diagnosis (a lock rewritten together
with the kernel pins a payload the machine never committed; `ws08::a_consistent_post_install_rewrite…` failed with
`KERNEL_MISMATCH`), and pinning the protected record instead would refuse the documented remedy after another machine's
update is pulled. When the two disagree, `kernel::install_kernel`'s precise check decides before anything moves, as
before. Evidence: R2 CS.d — a break-glass reinstall of an older signed release is refused `KERNEL_MISMATCH` with no
`DEGRADED` marking and the owner's token not consumed (base: KERNEL_MISMATCH too, but the machine is marked — the [K6a]
residual); `ws08::*` 7/7.

### 3.7 WS-4 IP-6 — `gov continue` and an unavailable derived index (`PARTIAL`)

The CLI arm opens the index with `context::open_index` and hands an `IndexHandle` (`Open` / `Unavailable(e)`) to
`continue_with_index`. `status::continue_work` (WS-5) still takes `&RuntimeDb`, so until it accepts the handle an
unavailable index is refused typed (`INDEX_UNAVAILABLE`, cause, remediation `gov rebuild-memory` — available under the
controls since O-4) instead of failing inside the command. Integration: once `continue_work` takes
`db: impl Into<context::IndexHandle<'a>>`, the body of `continue_with_index` becomes the single call
`gov_runtime::status::continue_work(p, index, claim)`. Evidence: R2 CS.c; certification round-two test.

### 3.8 WS-6 IP-6 — failure-memory policy keys and CLI

`MEMORY_POLICY.failure_memory: {retrieval_miss: {enabled: true, min_evidence_coverage: 0.5}, tool_failures: true}` declared
(the values WS-6's code already defaulted to); `ENFORCEMENT_MAP` entries (`retrieval::retrieve`,
`failures::record_tool_failure`); `POLICY_PRECEDENCE`: `enabled`/`tool_failures` strengthen-only, `min_evidence_coverage`
a floor, the rest immutable (the policy-enforcement coverage family stays green). CLI: `gov memory miss --query Q
[--expected id]… [--detail t]` records an agent-reported retrieval miss through `failures::record` (authority class
`record_failure_memory`, L1, declared in `AUTHORITY_POLICY`; a refused write is `FAILURE_NOT_RECORDED`, never success),
`gov memory failures` lists open failures; both classified in G0 (`memory miss` Write, `memory failures` Read). Evidence:
R2 CS.b; O1.c (the binary's failure-memory floor holds on an older kernel).

### 3.9 IP-WS02-11 (optional) — not done

Lifting `currency::GOVERNANCE_AFFECTING_TASK_CLASSES` into `TEST_POLICY` needs `framework/policies/TEST_POLICY.yaml` and
`runtime/src/verification/currency.rs`, both WS-2's files this round. The purpose (configurability) does not bind a class;
recorded for WS-2.

---

## 4. Docs (ws03 IP-11, ws05 IP-8)

`docs/ARCHITECTURE.md`: §4.3 (derived rebuild under the controls; failure memory), §4.5 (overlay documents, governing rule
sets), §4.6 rewritten (acting role, authority causes, G0, allow-lists, evidence commands, hard-blocks), §4.8 rewritten
(package, HC-1 human channel, P2-ADJ-0001, T2, agent resolution and human-only triggers, blocking and CIT approval, trust
boundary per OWNER-DECISION-P2-0001), §4.9 new (health scheduler, context delivery, artefact identity, qualification
oracle), §6.1 rewritten (claims: `TASK_CLAIMED`, `CLAIM_WORKTREE_MISMATCH`, `BUDGET_EXCEEDED`, `CLAIM_SCOPE_CONFLICT`,
`CLAIMS_BUSY`, `ROLE_NOT_DESIGNATED`, `UNKNOWN_ROLE`, `CLAIM_REQUIRED`, the claim-window CIT rule,
`PRODUCTION_MERGE_NOT_ALLOWED`). `docs/COMMANDS.md` rewritten: role and G0 semantics, the human-channel and trust commands,
context/artefact/health/oracle/memory-miss surfaces, and the refusal codes by area. `docs/generated/**` untouched.

---

## 5. Tests added or changed, and why

| File | Change | Reason |
|---|---|---|
| `ws03.rs` | helpers `human_channel` (root-based), `throwaway_root`, `reanchor_installed_kernel`, `provision`, `signed_release`, `break_glass_for`, `scratch_dir` | P2-ADJ-0001: the channel is a provisioned root's `human-gate` delegation |
| `ws03.rs` | new: ADJ test, O-1 test, round-two call-site test | §1, §2, §3 |
| `ws03.rs` `human_answers_come_only_from_the_owner_signed_channel` | standalone-anchor refusals replaced by `UNPROVISIONED` / `STANDALONE_DISABLED` / root refusals; the rest unchanged | P2-ADJ-0001 |
| `ws03.rs` `g0_freeze_and_pause…` | `rebuild-memory`/`memory rebuild` moved from the refused list to the recovery checks (derived-only); `verify product`, `health run` added to the refused list; a non-persisting health run asserted to write nothing | O-4, IP-WS02-09 |
| `ws03.rs` `project_overlays_may_raise_floors…`, `repair2.rs` `project_policy_cannot_weaken_constitutional_floors` | context-packet assertions moved before the doctor run; then assert the D027 hard-block refuses new work (ws03 also asserts the release after the repair) | IP-WS02-08 (intended); no assertion removed |
| `update.rs`, `repair.rs` `update_approval…`, `repair2.rs` chain | provision first; signed releases for init/update; below-floor rollback with break-glass; in `repair2` the lock identity assertions state the provisioned basis (`release:` label; manifest.json commit still never identity) | P2-ADJ-0001 + OWNER-DECISION-P2-0002 |
| `greenfield.rs` | `crate::ws03::human_channel(&g)` right after `init` (provision, then work) | P2-ADJ-0001; mid-task re-anchoring would rewrite `KERNEL_MANIFEST.json` inside the claim window |

No test was deleted and no assertion was weakened; every property the changed tests asserted is still asserted.

---

## 6. R1 preservation (AC-14)

Files on the R1 list touched: `cli/src/main.rs` (the `kernel reinstall` ingress call site, §3.6), `runtime/src/orchestration/
control.rs::guard_write` (a check added after the §6 guards), `runtime/src/human_channel.rs::provision_standalone` (a trust-
policy-mutation sink: a refusal added after `guard_effect`). No file under `runtime/src/srr/**`, `kernel*.rs`, `lock.rs`,
`init.rs`, `update.rs`, `release.rs`, `recovery.rs`, `records.rs`, `tools.rs` or `capabilities/**` changed.

All four prior R1 held-out suites were run unedited (byte-identity `cmp` lines in the output) through a private scratch path
whose `srr1-r1-verify*` symlinks point at this worktree (printed in the output):

| Suite | Baseline | This tree (`7dcf2e0`) |
|---|---|---|
| AR-0027 | 26 / 3 (`b1`, `b2`, `d3`) | 26 / 3, same tests |
| AR-0029 | 26 / 2 (`b3`, `b6`); `ho_f` does not compile | 26 / 2, same tests; `ho_f` does not compile |
| AR-0031 | 27 / 7 (`a1`, `a5`, `a8`, `b6`, `c2`, `c3`, `d2`) | 27 / 7, same tests |
| AR-0033 | 31 / 0 (30 / 1 on any larger tree) | 30 / 1: `hv_a::a1` only (its 84-file / 740-function pin) |

AR-0033 `hv_a::a1` census, labelled copy with only the two size assertions printed
(`r1-heldout/hv_a_derivation.a1-unpinned.P2-AR-0024.rs.txt`; the `diff` in the output shows exactly those two lines):
**105 files / 1472 functions** (round-1 integration: 105 / 1457), **0 violations in every §6 activity** (human_gate_create
43/38/1, human_gate_approve 1/1, release_certification 1/1, trust_policy_mutation 8/1, privileged_plugin_acquisition 10/2,
floor_lower_or_reset 3/1, present_below_floor_release_as_current 1/1). AR-0033's own `derive.py` (ROOT line only) agrees,
0 violations. `tests/certification/section6.rs` green.

---

## 7. Integration points for round 3

| IP | Owner / file | What | Why |
|---|---|---|---|
| IP-R2-1 | WS-5 `status::continue_work`; CLI `continue_with_index` | `continue_work(p, db: impl Into<context::IndexHandle<'a>>, claim)`; then the CLI body becomes `gov_runtime::status::continue_work(p, index, claim)` | completes ws04 IP-6 (W10 corrupted index) |
| IP-R2-2 | WS-2 catalogue block rules × host sites (WS-4 IP-WS02-05, WS-8 IP-WS02-12/13, WS-9 IP-WS02-18) | A host guard must not refuse its own remedy: D014/`schema_invariants` vs the repairing `cit execute` (brownfield); D006/D007 of an older installed release vs `update --apply`; OWNER-DECISION-0006 §5 `update --apply`/`--rollback` below floor. Scope the rules or exempt the remedy at the host | observed in this tree when those operations were guarded at the generic site (§3.1) |
| IP-R2-3 | WS-8 `srr::AdmissionRequest` | accept the set {framework.lock pin, protected-record pin} so the pin refusal precedes break-glass also when the two disagree | §3.6 residual |
| IP-R2-4 | WS-8 harness (`tests/certification/common.rs`) | the harness root delegates `human-gate` to `crate::ws03::owner()`; `ws03::human_channel` then uses it as is. `update.rs`, `repair.rs`, `repair2.rs`, `greenfield.rs` were provisioned here too: keep either version at integration (same properties) | P2-ADJ-0001 × OWNER-DECISION-P2-0002 |
| IP-R2-5 | docs owner, round 3 | document WS-8's round-2 admission (bootstrap mode, refused external ingress on unprovisioned machines) in ARCHITECTURE §4.4a/§7 and COMMANDS | lands in parallel with this round |
| IP-R2-6 | WS-2 (optional) | IP-WS02-11 (`TEST_POLICY.governance_affecting_task_classes`) | §3.9 |
| CLI | integration | WS-7/WS-9/WS-10 round-2 subcommands must be classified in `g0_label` / `COMMAND_GUARDS` (reviewed at integration, not now) | handoff |

## 8. What this run did not do

- No agent L0–L4 credentials (OWNER-DECISION-P2-0001).
- No edit outside the owned files and the listed test updates: no `srr/**`, `status.rs`, `tasks.rs`, `cit/**`, `update.rs`,
  `init.rs`, `adopt.rs`, `scheduler/**`, `verification/**`, `doctor.rs`, `upstream.rs`; nothing under `release/verification/`,
  `release/root-of-trust/`, `release/releases/`, `release/orchestration/phase-1/`, `release/capability-baseline/audit-0/`
  or another workstream's `repair-1/` directory; the Contract v3 source is byte-identical (`4c2df291…5ed3`).
- Audit-of-record probes, the integration's O-1 script and the round-1 named checks were run unedited; the derived copies
  (`ws03_named_checks.r2-derived.py`, the two runners) are separate, labelled files listing their changes.

## 9. Owner-decision questions

None. P2-ADJ-0001 is applied as adjudicated (a one-key reversal remains possible: kernel `true`, which POLICY_PRECEDENCE
lets no project do). Consequence stated for the owner's information: with the anchor off and OWNER-DECISION-P2-0002, an
unprovisioned machine cannot approve any human-gated operation (framework update, destructive migration, tool install,
privilege elevation, …); that is the adjudicated posture.

## 10. Process disclosures

- Model Claude Opus 5 (1M context), `claude-opus-5[1m]`. No sub-agents; the product owner was not contacted; no session or
  agent transcripts, task-output stores or user auto-memory were read. One long command (build + lib + certification) was
  moved to the background by the tool; its results were read only from the files it redirected to in my scratch
  directory, and the final regression was re-run in the foreground into `evidence/regression/`.
- Two shell commands containing `rm` (scratch cleanup; a stray `__pycache__` in the evidence directory, which is
  git-ignored) were denied by the permission system and not retried; fresh directories were used instead.
- A probe defect was found and fixed before any result was taken: the first `governed_hash` pruned directories inside a
  pre-sorted walk (so `.governance-runtime` was hashed) and the first `reanchor` copied the canonical `framework/`
  (not a self-contained kernel source). The recorded outputs are from the corrected probes.
