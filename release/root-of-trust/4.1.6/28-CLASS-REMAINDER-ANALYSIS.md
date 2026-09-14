# Output 28 — Why the classes survived four revisions, and what revision 5 changes in kind

> **RoT-1 revision 5 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Updated in revision 5 (HO-0011). Revision 4's analysis (§2 of the revision-4 text at `bca05a7`) is kept in substance in
> §2 below; §3–§6 are new. The two root-cause specialist proposals and the synthesis of them are in
> `4.1.6-alternatives-r5/`; this file states the accepted root cause per class, the mechanism change, and the attacks the
> architect ran against revision 5 before hand-off.

## 1. The recurring class

Every rejection since 4.1.3 is one class: **a lower-trust input yielding a current, higher-trust fact.** Review r4 found it
three more times, each a narrowed remainder of a revision-2 class:

| Class | Lower-trust input (review r4 §9) | Higher-trust fact obtained | Parent |
|---|---|---|---|
| BC4-1 | one threshold-1 attestation key plus release-pipeline input | an accepted production binary | R2-H3 / BC-3 |
| BC4-2 | a transport- or source-host-selected revoked, remediated or self-reporting binary | the first trusted binary on a machine | R2-H2 / BC-2 ∩ R2-H3 / BC-3 |
| BC4-3 | a threshold-1 final choosing among registered non-orderable digests | the effective constitutional content of the newest release | R2-H1 / BC-1 |
| BC4-4 | — (statements derived from BC4-1…3) | owner-option and blast-radius consequences | BC-4 |

## 2. Why each correction left a remainder (revisions 1–4)

| Revision | What it added | What a lower-trust party still selected |
|---|---|---|
| 1 | authenticated statements; release floors for selected keys | which authentic statements were seen; which keys counted; the binary (one `release-final`) |
| 2 | floors for 145 keys; monotonic state; `release-artifact` ≥ 2 | every unregistered leaf; a stateless machine's state; the commit every artefact signer checked |
| 3 | whole-payload classification; anchors; attested-source custodial stages | kernel precedence inside a join; the sequence number satisfying an anchor; the commit named by `release-final` |
| 4 | registration-only precedence; inclusion anchors and currency proofs; source from an ACCEPTED attestation | **which registered digest** (BC4-3); **which binary is first** and who evaluates it (BC4-2); **who establishes the build and source facts** (BC4-1) |

Revision 4 diagnosed the pattern correctly for each instance ("each revision added conditions downstream of a choice that a
lower-trust party still made") but did not turn it into a rule or a computation. It therefore re-created the pattern one
input away in three places.

## 3. Root cause accepted in revision 5

Both specialists reached the same cause from different lenses (`4.1.6-alternatives-r5/SYNTHESIS.md` §1):
- **Specialist A (verifier's minimal inputs):** every revision checked that a lower-trust value was a **member of an
  authorised set**; the lower-trust party still chose **which member** became effective. A join neutralises that choice for
  orderable values only.
- **Specialist B (release and custody supply chain):** trust strength was attached to **artefacts**, not derived for
  **facts**; pass-through signatures, selections among authorised alternatives and evaluators inside the evaluated object
  added strength they did not have.

**Accepted cause:** no rule classified, per trust decision, which inputs may **select** the effective fact and at what
authority and currency, and no mechanism computed the resulting minimum. Rule FD-1 (`29`) is that rule; the decision
register, the Fact Threshold Check and the derivation calculator are the mechanisms.

## 4. What revision 5 changes in kind

| Class | Revision-4 selector below authority | Revision-5 selector (removal, not a condition) | Retained from revision 4 | Evidence |
|---|---|---|---|---|
| BC4-1 | `build-attestation` key + pipeline for bytes; one `verification-attestation` key for source; the release process for build inputs; custodians passing through | release **registration** at root threshold or a root-granted quorum ≥ 2 selects source, input manifest, content and final (`30` §5); **≥ 2 first-person reproductions** confirmed first-hand select bytes (`30` §7); `release-artifact` and `build-attestation` withdrawn; verification and final become restrictors | compiled roots; purpose-bound DSSE; TBM resolution; accepted-TBM high-water; V8 (as producer restrictor); trust-state publication rules | CS5 (408 configurations; 0 invariant failures); P4r5 VA5 rows; DA03r5 |
| BC4-2 | tooling A2–A6; values printed by the candidate; Phase 4 self-verification; ceremonies on the unaccepted binary | a **fingerprint typed now** selects state; **`gov-admit`** (registered, reproduced, digest compared) or an admitted `gov` evaluates admission-predicate/1 over **measured bytes**, installed from the buffer; **GB rules** make a genuine binary refuse above C0 without an admission record; ceremonies only after admission (`31`) | inclusion anchors; pin validity and integrity; currency proofs; witness purpose; no `current` label | FA5 (45 scenarios, 17 vectors; revision-4 paths (b), (c) as controls); P4r5 |
| BC4-3 | threshold-1 `release-final` choosing among permitted digests | the **registration of exactly that release** fixes every non-join unit and the kernel tree; append-only; reversion, removal and narrowing are computed reductions (`23` §12) | default deny; exact precedence registration; required presence (now release-scoped for non-join units); YAML profile; directed join; Overlay Surface; strength over effective policy | REG5 (executed on real 4.1.5); selftest 71/71 |
| BC4-4 | hand-derived consequence tables | the calculator's output; options reconciled into OP-1…OP-15 with no proposals (`21`) | OP-1, OP-3, OP-5, OP-7 subjects | CS5; `21` §0 |

## 5. What remains a lower-trust input in revision 5, and why it is bounded

| Input | Decision it enters | Bound | Where |
|---|---|---|---|
| A human typing a fingerprint from the channels | first admission; anchors; in-gate currency | TA-5; OP-13; `issued_at` and age shown (RS-B1) | `31`, `24` |
| Operator-provisioned pins and admission records | anchors on CI; C3 on pinned machines | TA-9; integrity predicate; validity; a pin proves currency only for the TSS it names | `24` §3.2, §4.4; `31` R-ADM-7 |
| Local clock | pin validity; C3 window; OP-7 (b)/(c) | TA-7; stateful high-water from every ingested non-future statement; RS-2 restated for stateless runners | `24` §8, §10 |
| Verification processes | registration ceremony | OP-8; TB-4, TB-4′ | `30` §6 |
| Reproducer environments | bytes | OP-9 quorum; TA-10′; TB-S1 | `30` §7 |
| Upstream toolchain release | bytes of every honest reproducer | OP-10; TA-12 | `30` §12 |
| Repository-delivered state at or below a valid anchor | C1–C2 on machines anchored before a revocation | RS-1 core | `24` §10 |
| Project overlay | project configuration | LR-4; strength vector; CR4-B-04 | `26` §6, `19` §9 |
| Legacy binaries operated in subdirectories | writes under the project | `18` §9.1 makes the result `PARTIAL` or reported; LR-2 | `26` §3 |

## 6. Attacks the architect ran against revision 5 before hand-off

| ID | Attack (candidate instance of the class) | Result on revision 5 | Evidence |
|---|---|---|---|
| A-R5-01 | Revision-4 route B′ with honest downstream parties: one reproducer key plus pipeline plus trust-state key | refused: quorum not met; with two keys and honest reproductions visible, `REPRODUCTION_CONFLICT` | P4r5 VA5-B-prime, VA5-B-prime2; CS5 INV-ONE |
| A-R5-02 | Reproductions carried to the publisher through the pipeline (R-REP-3 removed) | accepted with {pipeline, 2 reproducer keys}: R-REP-3 is load-bearing and is architecture minimum | CS5 control |
| A-R5-03 | Inputs fetched from a CI-named mirror (R-REP-2 removed) | accepted with {mirror}: R-REP-2 is load-bearing | CS5 control |
| A-R5-04 | D-A07 re-expressed: custodians under OP-9 (d) name the digest handed to them | lowers the minimum to {pipeline, 2 reproducer processes}; hence R-REG-3 (f) requires their own reproduction | CS5 control |
| A-R5-05 | CR4-B-07 option 2 (a P1 proof on the anchored TSS covers a later descendant) | trust-state key + reproducer keys + transport accept on pinned machines; option 1 removes the trust-state key as a C3 selector there | CS5 control `P1_relaxed_control`; P4r5 `AP-R5_p1_proof_does_not_cover_later_descendant` |
| A-R5-06 | Open or unioned registration ranges (specialist B E2-open) | gap, inflated and stale-policy releases eligible; exact per-release lookup refuses all three | REG5 `ranges_excluded`; specialist A E4 |
| A-R5-07 | Release-global presence with a newer member registered | legitimate older release refused (`required_missing`); release-scoped presence accepts it | selftest S69; REG5 legitimate rows (a first REG5 run without scoping exited 2, which led to the rule) |
| A-R5-08 | Reproduction quorum counted as a per-statement threshold | every one-signature reproduction refused at ingest (honest binaries unusable); SV-7 excepts `reproducer` | P4r5 (a first oracle run under that reading failed its honest controls) |
| A-R5-09 | Measured bytes replaced before installation | installing by re-reading the path installs the swapped bytes; installing from the buffer does not | FA5 INS1 |
| A-R5-10 | Genuine but revoked binary started directly, without admission | `BINARY_NOT_ADMITTED`; with its revocation held, `BINARY_REVOKED_SELF` | FA5 DA04, CI1 |
| A-R5-11 | Stale or disagreeing channel at first admission | one stale channel under OP-13 (b): `CHANNEL_DISAGREEMENT`; under (a): the stated residual RS-B1 | FA5 CH1 |
| A-R5-12 | Stateful machine, clock set back below ingested statements | fails closed; the witness-only high-water rule accepts (mutant detected) | P4r5 CLOCK; DA03r5 |
| A-R5-13 | Legacy `init` from `governance/`, `governance/trust/kernel/`, `governance/framework.lock/` (positions reviewer C did not run) | every write under `governance/` other than overlay leaves `PARTIAL`; discovery refuses inside the PPS | ST5 matrix and D-A01 re-run |
