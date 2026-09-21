# P2-AR-0052 — repair delta for `cap2-candidate-1`

Requirements, not designs. For each blocker class: what must become **true**, the normative source that says so,
the acceptance evidence a later verifier will demand, dependencies, and a suggested partition with non-overlapping
file scopes.

Seven classes carry the eight blocking findings. Three of them — BC-P2-53, BC-P2-41 and BC-P2-45 — are the same
tool-installation trust surface that OWNER-DECISION-P2-0003 created, and they compound: the OS's own derivation can
be evaded, the independent review meant to carry what the OS cannot observe is about a different artefact, and the
authorised side of the comparison is an unprotected repository file. They should be repaired together.

---

## BC-P2-53 — tool-installation authority derivation is defeated by interpreter wrapping *(new; HIGH; AC-4, AC-3)*

**Findings:** `V1-F4-01`. **Capabilities:** F4, F3.

**What must become true.**

1. An installation whose command cannot be *evaluated* by the OS must be recorded `undetermined` and must gate. The
   present code records `undetermined` only when the descriptor carries no command at all
   (`runtime/src/tools.rs:969-972`), while its own documentation states the opposite rule.
   *Source:* OWNER-DECISION-P2-0003 requirement 3 — *"If the envelope cannot be determined, a condition cannot be
   evaluated … the Human Gate is required and the installation does not proceed"*; and
   `Governance_OS_Capability_Acceptance_Contract_v3.md:429` — *"Drift/tampering fails closed."*
2. An installation that would perform an authority-expanding effect must gate however that effect is expressed. The
   six triggers OD-P2-03 names are properties of what the installation *does*, not of how its argv happens to be
   tokenised; today `["sh","-c","sudo apt-get install -y x"]` is recorded `expands_authority: false,
   triggers_fired: []`.
   *Source:* Contract v3:430 — *"Elevated permissions reference authoritative gate/decision"*; OD-P2-03's six
   authority-expansion triggers.
3. `health_check.command` must be inside the same boundary as `install_command`: it runs on every installation, with
   or without `--execute`, so it is an installation effect.

**Acceptance evidence a later verifier will demand.** For each of at least these shapes — `sh -c`, `bash -lc`,
`python3 -c`, an opaque build target such as `make install`, and the same four in `health_check.command` — a
Human Decision Gate is raised, OR the installation is recorded `undetermined` and refused; and for each, nothing
outside the project root is written, shown by running the installation and inspecting the filesystem, not by
reading the branch field. Plus the negative control that must still hold: a non-elevated, reviewed, pinned,
reversible installation inside the envelope completes with **no** gate (OD-P2-03 requirement 6), and ordinary
allowlisted network use alone does not gate.

**Dependencies.** None inbound. BC-P2-41 and BC-P2-45 compound with it; all three must close before AC-4 can hold.

**File scope.** `runtime/src/tools.rs` (the derivation), `framework/policies/TOOL_POLICY.yaml` (the envelope
vocabulary), `framework/policies/CHANGE_POLICY.yaml` (the trigger declarations).

---

## BC-P2-41 — the governed security review is not bound to the installation it authorises *(HIGH; AC-4, AC-3)*

**Findings:** `V1-F3-01` (residual; iteration-0 `A0-F4-05`). **Capabilities:** F3, F4.

**What must become true.** The review that permits a non-gated installation must be bound to **that installation** —
the exact descriptor content the transaction will write, i.e. the same installation subject digest the product
already computes — not to a tool id and version string. A descriptor whose command, permissions, pin or health
check changed after the review must not satisfy `licence_and_security_satisfied`.

*Source:* OD-P2-03 requirement 3, which names the property in the class's own words — *"the review is missing,
self-attested or **not bound to this exact installation (BC-P2-41)**"* → gate; Contract v3:431 — *"Security review
cannot be self-attested"*; Contract v3:415–417 (F3 review, approval when required).

**Acceptance evidence.** One governed review of tool T at version V, then six descriptors for T at V differing in
install command, permissions, pin and health check: exactly the reviewed one proceeds non-gated; the other five are
refused or gated, each naming the difference. Today one review satisfied all six.

**Dependencies.** Compounds with BC-P2-53: while the derivation is evadable, this review is the only backstop, so
closing one without the other leaves the surface open.

**File scope.** `runtime/src/tools.rs` (`review_verdict` and the installation subject), and the F3/F4 governance
fixtures.

---

## BC-P2-45 — project overlay files bypass POLICY_PRECEDENCE *(HIGH; AC-4, AC-3)*

**Findings:** `V1-F4-02`, `S1-A1-01` (mine). **Capabilities:** A1, F4, F3, E1 (and the inventoried M1, M2, M3, H3).

**What must become true.** Every project overlay document whose content can change an authority, permission,
filesystem-scope or sensitivity decision must pass through `policy_precedence::evaluate_overlay` **before** the
decision that reads it, with a rule of its own in `POLICY_PRECEDENCE.yaml`, so that a weakening is refused, left
without effect and reported. Today the evaluator is reached for `PROJECT_POLICY.yaml` and
`MODEL_ROUTING_OVERRIDES.yaml` only (`runtime/src/policy.rs:295, :340`), under a comment claiming it covers every
overlay input (`:285`); `TOOL_PERMISSIONS.yaml`, `REPOSITORY_CONTRACT.yaml` and `DATA_SENSITIVITY.yaml` are read
directly and have no rule, so POLICY_PRECEDENCE's own deny-by-default never reaches them. Which documents these are
is *determined by the accepted sources*, not a choice: OD-P2-03 requirement 2 names `TOOL_PERMISSIONS`,
`AUTHORITY_POLICY`, `DATA_SENSITIVITY`, the path map and the tool policy's allowlists as the envelope sources.

*Source:* Contract v3:134 — *"Security and authority floors cannot be weakened by lower-precedence policy"*; :137 —
*"Invalid weakening attempts fail closed and are observable"*; OD-P2-03 requirement 2 — the envelope is *"computed
from trusted OS state"*.

**Acceptance evidence.** For each of the three documents: a hand edit that widens authority, filesystem scope or
sensitivity appears in `gov policy overrides`'s `refused` list with its policy, key, value, kernel value and reason;
the effective decision is unchanged; and a governance-suite surface reports it. Specifically, the edit that today
turns `expands_authority: true, triggers_fired: [privilege_escalation]` into `false` must stop doing so.

**Dependencies.** None inbound. Closing it is what makes BC-P2-53's "trusted OS state" side actually trusted.

**File scope.** `runtime/src/policy.rs`, `runtime/src/policy_precedence.rs`,
`framework/policies/POLICY_PRECEDENCE.yaml`. (Note the overlap with BC-P2-53's `runtime/src/tools.rs` at the read
site `role_permissions`; one workstream should own both or the read site should move behind the evaluator.)

---

## BC-P2-33 — adoption stalls at A6 on a brownfield tree the OS itself classified *(HIGH; AC-3)*

**Findings:** `V1-S4-01` (residual; iteration-0 `A0-S4-02`). **Capabilities:** S4 (R1, R2 in the class).

**What must become true.** The documented A0–A11 sequence must be completable on a brownfield tree carrying
secret-bearing files, without an out-of-band hand edit. Either A2's own SECRET classification reaches the project's
sensitivity overlay as part of adoption, or the `D011` and `path_map_compliance` blocks that stand in A6's way must
list an adoption stage among their remedies, so that the block does not refuse its own remedy.

*Source:* Contract v3:929 — S4's bullet *"A6 controlled migration"*, under the section heading *"Stages are
executable/evidenced"*; Contract v3 L4 and O5:807, the availability rule — a block's listed remedy stays available
and no block refuses its own remedy.

**Acceptance evidence.** `gov adopt` driven A0 → A11 on the product's own brownfield fixture, unmodified, with no
hand edit of `governance/project/DATA_SENSITIVITY.yaml` between stages, ending `ADOPTED_HEALTHY`; and the secret
files still classified secret at the end, not declassified to get past the block.

**Dependencies.** None. Independent of the tool-installation cluster.

**File scope.** `runtime/src/adopt.rs`, the adoption stage definitions, and the `D011` / `path_map_compliance`
remedy declarations in `runtime/src/scheduler/catalogue.rs`.

---

## BC-P2-37 — a trust report taken from an unauthenticated release field *(MEDIUM; AC-3)*

**Findings:** `V1-S5-01` (residual). **Capabilities:** S5, A2.

**What must become true.** `gov update` must not return an affirmative result about a source whose authenticity it
has not established. The version comparison that produces `{"applied": false, "reason": "already up to date",
ok: true}` is taken from the source's own `KERNEL.yaml`/`KERNEL_MANIFEST.json` before the single verification policy
runs (`runtime/src/update.rs:238-240`, `:55-63`). Either the source is authenticated before any conclusion is drawn
from its declared identity, or the result states plainly that the source was not authenticated and no currency claim
is made about it.

*Source:* Contract v3:937 — S5's bullet *"authenticated source"*; :143 — *"Release/source authenticity is
established before any privileged kernel material is staged or installed"*; :148 — *"Source-release authentication
detects pre-install tampering"*.

**Acceptance evidence.** Three sources at the installed version string — payload-tampered, foreign-signed, and
correctly signed but below the machine's floor — each produce a typed, non-affirmative result from
`gov update --apply` and `--check`, and the correctly signed at-version source still reports "up to date" as it
should. The A2 challenge text (Contract v3:154) is the fault list a later verifier will draw from.

**Dependencies.** None.

**File scope.** `runtime/src/update.rs`.

---

## BC-P2-32 — failure memory has four classes with no writer *(MEDIUM; AC-3)*

**Findings:** `V1-BETA-01` (residual; iteration-0 `A0-C8-01`). **Capabilities:** C8.

**What must become true.** Each of the seven failure classes Contract v3:276–283 lists — bugs, failed approaches,
wrong assumptions, retrieval misses, regressions, migration failures, tool failures — must have a governed way to
come into existence and a durable, structured, rebuild-surviving record when it does. Three have writers today
(`record_tool_failure`, `retrieval_miss_event`, the regression recorders); `bug`, `failed-approach`,
`incorrect-assumption` and `migration-failure` exist only in the `KINDS` constant and the schema. Where the OS
observes the failure it should record it itself (a failing product-test family is a regression; a refused or
rolled-back migration is a migration failure); where an agent observes it, a governed command must record it the way
`gov memory miss` already records a retrieval miss.

*Source:* Contract v3:276–283, and :93 — *"A capability may not be reported `PRESENT_AND_SUBSTANTIAL` solely because
a file/schema/policy exists."*

**Acceptance evidence.** For each of the four classes: a governed path that creates the record, the record read back
after `gov rebuild-memory`, and follow-up work generated from it. The evidence map's owner for checklist items C8.1,
C8.2, C8.3 and C8.6 must then be a check that exercises the behaviour, not the unit test over the `KINDS` constant.

**Dependencies.** None.

**File scope.** `runtime/src/memory/failures.rs`, the commands that would write each class, and
`tests/governance/capability-evidence-map.yaml`'s C8 rows.

---

## BC-P2-07 — a tier run leaves a third of its declared membership unevaluated and reports it complete *(MEDIUM; AC-5)*

**Findings:** `E-O5-01` (residual; iteration-0 `A0-O5-09`). **Capabilities:** O5, U.

**What must become true.** A tier run must evaluate every check its own catalogue declares at that tier, or record
precisely which members it did not evaluate and why. `gov health checks` declares 74 checks, all 74 at G5 and 49 at
G1; `gov health run --tier G5` evaluates 39 and writes `complete: true, executed: 39, not_evaluated: 0`, and
`--tier G1` evaluates 18 of 49 with the same claim. `run_suite` iterates the governance-suite families only;
`doctor::run` is reached from the G0 guard's block re-evaluation and the `gov doctor` CLI. Either the tier run
executes the doctor half, or the catalogue stops declaring those 35 at G1/G5 and the record's completeness claim is
made true as stated.

*Source:* frozen gate contract AC-5 (health-result provenance; G0–G6 tiers perform their duties); Contract v3 O5,
and :979–993 for Gate U, whose governance-suite-freshness SLO crosses without reaching the RED/YELLOW/GREEN state
because its owning check D021 no tier run executes.

**Acceptance evidence.** `gov health run --tier G1` and `--tier G5` each evaluate their declared membership, or name
every unevaluated member in `not_evaluated_checks` with a reason; and `gov health status` does not read GREEN while
the same output reads `repository.verdict: DEGRADED` with 18 stale checks.

**Dependencies.** None.

**File scope.** `runtime/src/scheduler/` (`run_suite`, the tier membership and the health-result summary),
`runtime/src/doctor.rs`.

---

## Non-blocking requirements worth carrying into the same rounds

These leave no acceptance criterion unmet, so they do not gate; each is cheap beside the class it sits in.

| Id | Requirement | Source | Scope |
|---|---|---|---|
| `V1-R1P-01` | `paths::relocate_legacy` must not delete a legacy copy of a non-rebuildable OS store whose bytes it could not read: `read(&f).ok() == read(&t).ok()` makes two unreadable files compare equal, contradicting the function's own stated contract (`STATE_LOCATION_CONFLICT`, nothing overwritten). | the function's documented contract; Contract v3 B3 :202 | `runtime/src/paths.rs:262-280` |
| `V1-BETA-08` | A generated graph held-out query must expect what the graph route returns (the dependants of the seed), or be generated pending, so that no project carries a permanently failing regression baseline. | Contract v3:345–346 | `runtime/src/memory/heldout.rs:43` |
| `A1-W12-01` | `gov health close-check` must agree with `gov task close` on the same receipt: the preview must not report admissible what the gate refuses. | Contract v3 W12, W5 | `runtime/src/scheduler/`, `runtime/src/task.rs` |
| `S1-AC13-01` | Every capability must carry the Contract v3:53–73 fields with a value (`severity if violated` is null for all 101), and every checklist item must name its automated check or record why none exists (126 of 713 do not). | Contract v3:53–73, :61, :64 | `tests/governance/capability-evidence-map.yaml` |
| `V1-BETA-03` | The generated held-out set must be able to discriminate the component a governed profile change selects; its semantic queries are left pending, so every embedder candidate measures identically. | Contract v3:345–346; frozen §9.1 | `runtime/src/memory/heldout.rs` — **Phase-3 relevant, see later-lifecycle-notes.md** |
| `V1-A5-01` | `gov rebuild-memory` and `gov memory rebuild` should not change tracked generated manifests while FREEZE_WRITES or PAUSE is in force. | Contract v3:173–174 | `runtime/src/control.rs`, the rebuild entry points |
| `V1-G1-01` | Deterministic intent routing must not invert negation (`do not approve this change` routes to APPROVE). | Contract v3:444 | `runtime/src/intent.rs` |
| `V1-E3-01`, `V1-F5-02` | A handoff return must be bound to the role the handoff names and must not silently overwrite an earlier return; a handoff's authority envelope must not exceed its task's allowed paths. | Contract v3:377–386 | `runtime/src/handoff.rs` |

---

## Suggested work partition (non-overlapping file scopes where possible)

| WS | Classes | Files |
|---|---|---|
| **WS-A — tool-installation trust surface** | BC-P2-53, BC-P2-41, **and** BC-P2-45's read site | `runtime/src/tools.rs`, `framework/policies/TOOL_POLICY.yaml`, `framework/policies/CHANGE_POLICY.yaml` |
| **WS-B — overlay precedence coverage** | BC-P2-45 | `runtime/src/policy.rs`, `runtime/src/policy_precedence.rs`, `framework/policies/POLICY_PRECEDENCE.yaml` |
| **WS-C — adoption on a secret-bearing tree** | BC-P2-33 | `runtime/src/adopt.rs`, `runtime/src/scheduler/catalogue.rs` (the two remedy lists only) |
| **WS-D — update ingress** | BC-P2-37 | `runtime/src/update.rs` |
| **WS-E — failure memory** | BC-P2-32 | `runtime/src/memory/failures.rs`, its writers, the C8 evidence-map rows |
| **WS-F — health tier coverage** | BC-P2-07 | `runtime/src/scheduler/`, `runtime/src/doctor.rs` |

**The one unavoidable overlap** is `runtime/src/scheduler/catalogue.rs` between WS-C (two remedy lists) and WS-F
(tier membership and the run summary), and `runtime/src/tools.rs` between WS-A and WS-B (`role_permissions` is the
read site of the overlay WS-B must put behind the evaluator). WS-A and WS-B should sequence — WS-B first, so that
WS-A's "trusted OS state" is trustworthy when its derivation is repaired — or be one workstream.

WS-C, WS-D, WS-E and WS-F are independent of each other and of WS-A/WS-B and may run in parallel.

**Convergence caution for the next iteration.** BC-P2-53 was introduced by the repair that built the OD-P2-03
surface. Three of the seven blocking classes now live on that one surface. A repair round that adds further new
mechanism there should expect the next verifier to look hardest at exactly that, and frozen §8's three-consecutive
rule is at one of three.
