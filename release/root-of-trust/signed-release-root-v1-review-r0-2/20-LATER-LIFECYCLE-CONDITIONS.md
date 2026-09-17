# 20 — Later-lifecycle conditions (AR-0025)

None of the items in this file blocks `GATE-R0-ARCH-ACCEPT`. Each states its normative
source, provenance class, lifecycle, whether it falsifies an existing claim or merely
proposes stronger assurance, and its consequence, per the frozen boundary's finding-intake
contract.

## Register

| id | lifecycle | class | severity | falsifies a claim? | owner action |
|---|---|---|---|---|---|
| `SRR2-R1-C1` | R1 | `NEW_OWNER_DECISION_REQUIRED` | MEDIUM | no — internal ambiguity | **yes** |
| `SRR2-R1-C2` | R1 | `NECESSARY_DERIVED` | MEDIUM | no — proposes precision | no |
| `SRR2-R1-C3` | R1 | `NECESSARY_DERIVED` | LOW | no | no |
| `SRR-R0-L8` | INFO | `IMPLEMENTATION_CHOICE` | INFO | no | no |

Carried forward unchanged from AR-0023 at their original lifecycles: `SRR-R0-L1` (R1),
`SRR-R0-L2` (R1), `SRR-R0-L3` (R1), `SRR-R0-L4` (R1), `SRR-R0-L5` (R1), `SRR-R0-L9` (R2).
`SRR-R0-L6` is owner-deferred to R1 and `SRR-R0-L7` is owner-closed, both by
`OWNER-DECISION-0005`; neither is reopened here.

---

## `SRR2-R1-C1` — R1 — `NEW_OWNER_DECISION_REQUIRED` — Break-glass exit clears the marking on one of the two floors

**1. Exact normative source.** `01-FROZEN-…-BOUNDARY.md` §R0 item 8 ("signed rollback floors
and protected local high-water"); `OWNER-DECISION-0006` requirements 4, 6 and 7;
`00-ARCHITECTURE.md:96` (floor defined over two floors) against `:108` ("While below floor
the machine is marked") and `:112` (exit clears the marking at the minimum secure release);
`ARCH-0003.yaml:113-115` against `:145-146` and `:154-155`.

**2. Provenance class.** `NEW_OWNER_DECISION_REQUIRED`. The architecture transcribes
`OWNER-DECISION-0006` requirement 7 faithfully; the ambiguity originates in the interaction
between that requirement's single-floor exit and the architecture's necessary two-floor
admission rule. Resolving it cleanly is an owner scoping choice, not a reviewer's.

**3. Baseline and approval status.** Original-baseline: no. Current-owner-approved: the exit
condition is owner-approved as written; the interaction with the high-water is unaddressed
by any owner record.

**4. Lifecycle / gate.** **R1.** Not R0: the compliant reading is already present in the
architecture, so no architecture change is required to meet an R0 guarantee. R1 is where the
marking lifetime becomes a testable state-machine property.

**5. Explicit claim falsified, or stronger assurance?** **Neither a falsification nor a
hardening proposal — an internal ambiguity.** The R0 guarantee at `00-ARCHITECTURE.md:32`
governs which ingress may place the machine below a floor, and it holds: the ingress is
authorised, durably recorded and marked at the time it occurs. What is underspecified is
the *lifetime* of the marking afterwards. The document uses "floor" in two senses — the
two-part admission floor and the single-part exit floor.

**6. Bounded counterexample.** Machine `M`: protected high-water `v6`, signed minimum secure
release `v4`. After a fault its only complete local state is `v5` — authentic, previously
verified by `M`, at or above `v4`, below the high-water. Installing `v5` is a below-floor
ingress requiring break-glass. On completion `v5 ≥ v4` satisfies the exit condition, the
marking is cleared, and `M` resumes privileged governance work while still below its
protected high-water — the state `:108` says should remain marked. Entirely inside the
declared envelope; no hostile administrator, OS or network attacker.

**7. Consequence.** *Security:* nil without break-glass authority, which is owner-controlled
and non-manufacturable (`evidence/PROBES.md` NA-2); no unauthorised party reaches the state.
*Availability:* the strict reading (hold the marking until both floors are met) slightly
prolongs degraded mode; the lax reading restores service sooner. *Usability:* an operator
cannot currently predict which behaviour to expect — the same class of ambiguity AR-0023
identified, at much lower severity. *Cost:* one clause.

**8. Owner decision needed.** **Yes, bounded.** Does exit from `DEGRADED — RECOVERY ONLY`
require a release at or above (a) the signed minimum secure release only, as requirement 7
states today, or (b) **both** that floor and the protected local high-water? This review does
not choose, does not author the clause, and does not treat either answer as a condition of
R0 acceptance. Recorded here for the orchestrator to route; the product owner was not
contacted.

**9. Recommended R1 default pending that answer.** The stricter reading, which is already
supported by `00-ARCHITECTURE.md:96` and `:108` and fails safe.

---

## `SRR2-R1-C2` — R1 — Offline authenticity record binds "release identity"; digest granularity is unstated

**1. Exact normative source.** `01-FROZEN-…-BOUNDARY.md` §R0 items 11 and 14; Contract v3 §A2
("A source directory cannot regenerate its own trusted identity"; "Trusted release identity
is recorded, not invented, by `framework.lock`"; "Integrity and authenticity are treated as
separate properties"); `00-ARCHITECTURE.md:98`; `ARCH-0003.yaml:124-129` read against §4
(`:83-85`), which distinguishes "release version" from "exact kernel/CLI/payload digests".

**2. Provenance class.** `NECESSARY_DERIVED`.

**3. Baseline and approval status.** Original-baseline: yes (Contract v3 A2).
Current-owner-approved: yes (frozen boundary items 11 and 14).

**4. Lifecycle / gate.** **R1.** The R0 question — is the offline authenticity basis
circular? — is answered, and the answer is no (`evidence/PROBES.md` NA-8). Authenticity flows
metadata → verification → protected machine state → later offline recovery, never from the
artifact being validated. What remains is the record's granularity, which is a mechanism.
R1 already carries the matching test: "candidate/source files cannot create their own trusted
identity" and "verified bytes are staged, installed and used without substitution".

**5. Explicit claim falsified, or stronger assurance?** **Proposes precision; falsifies
nothing.** "Release identity" is not defined narrowly enough in the architecture to *exclude*
digests, and the transaction invariant already requires the committed representation to be
verified and journalled (`ARCH-0003.yaml:105-107`; `00-ARCHITECTURE.md:120-127`), so the safe
reading is available without an architecture change.

**6. Bounded counterexample, applicable only under the narrow reading.** If the protected
record held a version string alone, a local tree rewritten coherently across payload,
`KERNEL_MANIFEST.json` and `framework.lock`, bearing the same version, would satisfy both the
D-0007 intactness chain and the identity match, and would be admitted by the offline recovery
path as "previously authenticated by this machine" — the "mutually consistent files" case that
`00-ARCHITECTURE.md:98` exists to exclude. This requires write access to the installed tree,
which is partly outside the declared envelope but is precisely what D-0007 exists to detect.

**7. Consequence.** *Security:* under the narrow reading, the offline recovery path's
authenticity claim would rest on a label rather than on bytes. *Availability/usability:* none.
*Cost:* one clause.

**8. Owner decision needed.** No.

**9. Recommended R1 design obligation.** The protected record binds what the machine actually
verified — the payload/kernel digests, or the `kernel_manifest_hash` — and not the release
version alone.

---

## `SRR2-R1-C3` — R1 — LOW — High-water durability across uninstall is less explicit than the break-glass case

**1. Exact normative source.** `01-FROZEN-…-BOUNDARY.md` §R0 item 8; `00-ARCHITECTURE.md:96`,
`:141`, `:152`, `:154`.

**2. Provenance class.** `NECESSARY_DERIVED`.

**3. Baseline and approval status.** Original-baseline: partly. Current-owner-approved: yes,
via item 8.

**4. Lifecycle / gate.** **R1**, which already tests "metadata/release high-water is durable
and monotonic".

**5. Explicit claim falsified, or stronger assurance?** **Neither.** The safe reading is
stated — floors are "a property of the machine, not of one operation", protected state
"prevents forgetting" a received revocation/minimum, and protected machine policy is
provisioned outside the project repository. No claim is falsified.

**6. Observation.** The floor rule is scoped over the six *ingresses*; `uninstall` is not an
ingress, and only the break-glass section explicitly forbids resetting the floor. A future
implementation that cleared protected machine state on uninstall would leave a subsequent
`init` with no floor, without any break-glass authority being involved.

**7. Consequence.** *Security:* a floor bypass if implemented wrongly; none on the stated
reading. *Availability/usability/cost:* negligible.

**8. Owner decision needed.** No.

**9. Recommended R1 design obligation.** State and test that the protected high-water and the
signed minimum secure release survive uninstall and project removal, as the break-glass
section already states for its own mode.

---

## `SRR-R0-L8` — INFO — R0 traceability table maps 11 of the 14 frozen R0 items

Carried forward from AR-0023 at **unchanged INFO severity**. `00-ARCHITECTURE.md`
§"R0 traceability" still has eleven rows against fourteen frozen R0 items. Items 13
(preservation of the original mission and Contract v3 capabilities) and 14 (D-0007 active;
non-circular first-install authenticity supplied outside its manifest/lock) remain covered in
body text — `00-ARCHITECTURE.md` §"Preservation of Governance OS", the bootstrap
trust-domain row, `ARCH-0003.yaml` §9 and §11, and `03-TRANSITION-MAP.md` — but absent from
the table.

AR-0024 disclosed that it did not fix this and re-pointed only two existing rows whose target
sections moved. That disclosure is **accurate**: the row count is unchanged at eleven, and both
re-points resolve to sections that exist verbatim and contain the cited material
(`evidence/PROBES.md` NA-16). Cosmetic; completing the table would make the R0 self-check
mechanical for future reviewers.

---

## Stronger-assurance proposals — recorded as NOT requirements and NOT conditions

Listed only so that no future reader mistakes them for obligations created by this review.
None is required at R0, R1, R2 or R3 by any current owner record, and none is a condition of
this verdict:

- A clock-independent freshness mechanism (trusted time, attested time, monotonic time,
  signed-time floor, roughtime). `OWNER-DECISION-0006` expressly directs that `SRR-R0-M1`
  "must not be broadened into another trust-state protocol", and `00-ARCHITECTURE.md:53`
  correctly declares that no such mechanism is assumed, required or provided. Not proposed.
- A second-operator or dual-control requirement on break-glass entry.
- Cryptographic binding of the break-glass entry record to the machine's protected state.

Each would require explicit owner adoption under the frozen boundary's change-control rule.
This review recommends none of them and asserts none as a gap.
