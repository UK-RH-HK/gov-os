# Output 28 — Why the classes survived five revisions, and what revisions 5 and 6 change in kind

> **RoT-1 revision 6 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Updated in revision 6 (AR-0015). §1–§6 are revision 5's analysis (AR-0011), kept as the review trail; its hand-written
> minimal sets in §6 are restated in words, because revision 6 permits sets only as calculator output (`29` §5.5). §7–§10 are
> new: the root cause of review r5's classes, what revision 6 changes in kind, what remains a lower-trust input, and the attacks
> this architect ran against revision 6 before hand-off.

## 1. The recurring class

Every rejection since 4.1.3 is one class: **a lower-trust input yielding a current, higher-trust fact.** Review r4 found it
three more times, each a narrowed remainder of a revision-2 class:

| Class | Lower-trust input (review r4 §9) | Higher-trust fact obtained | Parent |
|---|---|---|---|
| BC4-1 | one threshold-1 attestation key plus release-pipeline input | an accepted production binary | R2-H3 / BC-3 |
| BC4-2 | a transport- or source-host-selected revoked, remediated or self-reporting binary | the first trusted binary on a machine | R2-H2 / BC-2 ∩ R2-H3 / BC-3 |
| BC4-3 | a threshold-1 final choosing among registered non-orderable digests | the effective constitutional content of the newest release | R2-H1 / BC-1 |
| BC4-4 | — (statements derived from BC4-1…3) | owner-option and blast-radius consequences | BC-4 |

Review r5 found it again (§7).

## 2. Why each correction left a remainder (revisions 1–4)

| Revision | What it added | What a lower-trust party still selected |
|---|---|---|
| 1 | authenticated statements; release floors for selected keys | which authentic statements were seen; which keys counted; the binary (one `release-final`) |
| 2 | floors for 145 keys; monotonic state; `release-artifact` ≥ 2 | every unregistered leaf; a stateless machine's state; the commit every artefact signer checked |
| 3 | whole-payload classification; anchors; attested-source custodial stages | kernel precedence inside a join; the sequence number satisfying an anchor; the commit named by `release-final` |
| 4 | registration-only precedence; inclusion anchors and currency proofs; source from an ACCEPTED attestation | **which registered digest** (BC4-3); **which binary is first** and who evaluates it (BC4-2); **who establishes the build and source facts** (BC4-1) |
| 5 | rule FD-1; registration; reproduction quorum; `gov-admit`; release-scoped registration | **which lineage, quorum and evaluator at first contact** (BC5-1); **which build environment** (BC5-2); **which constitutional content the registration signs** (BC5-3); **the statements derived from an incomplete register** (BC5-4) |

## 3. Root cause accepted in revision 5

Both specialists reached the same cause from different lenses (`4.1.6-alternatives-r5/SYNTHESIS.md` §1). No rule classified,
per trust decision, which inputs may **select** the effective fact and at what authority and currency, and no mechanism
computed the resulting minimum. Rule FD-1 (`29`) is that rule; the decision register, the Fact Threshold Check and the
derivation calculator are the mechanisms.

## 4. What revision 5 changed in kind

| Class | Revision-4 selector below authority | Revision-5 selector | Evidence |
|---|---|---|---|
| BC4-1 | `build-attestation` key + pipeline; one `verification-attestation` key; the release process | release registration (root threshold or quorum ≥ 2); ≥ 2 first-person reproductions confirmed first-hand; withdrawn pass-through purposes | CS5; P4r5; DA03r5 |
| BC4-2 | tooling A2–A6; candidate-printed values; self-verification; ceremonies on the unaccepted binary | typed fingerprint; `gov-admit` over measured bytes; GB rules; ceremonies after admission | FA5; P4r5 |
| BC4-3 | threshold-1 `release-final` choosing among permitted digests | the registration of exactly that release | REG5; selftest 71/71 |
| BC4-4 | hand-derived tables | calculator output; OP-1…OP-15 | CS5 |

## 5. What remained a lower-trust input in revision 5

Revision 5's table (fingerprint typed from the channels, pins, clock, verification processes, reproducer environments,
upstream toolchain, repository-delivered state, overlay, subdirectory legacy writes) is superseded by §9. Two of its rows were
wrong: "a human typing a fingerprint" was bounded only if that fingerprint selected state alone (RV5-H1), and "reproducer
environments" were bounded only if each reproducer's environment was independently established (RV5-H2).

## 6. Attacks the architect ran against revision 5 before hand-off (history)

| ID | Attack | Result on revision 5 | Evidence |
|---|---|---|---|
| A-R5-01 | One reproducer key plus pipeline plus trust-state key | refused | P4r5 VA5-B-prime, VA5-B-prime2; CS5 INV-ONE |
| A-R5-02 | Reproductions carried to the publisher through the pipeline (R-REP-3 removed) | accepted with pipeline input and two reproducer keys: R-REP-3 load-bearing | CS5 control |
| A-R5-03 | Inputs fetched from a CI-named mirror (R-REP-2 removed) | accepted with the mirror alone: R-REP-2 load-bearing | CS5 control |
| A-R5-04 | Custodians under OP-9 (d) name the digest handed to them | lowers the minimum to pipeline input and two reproducer processes; hence R-REG-3 (f) | CS5 control |
| A-R5-05 | CR4-B-07 option 2 | trust-state key + reproducer keys + transport accept on pinned machines | CS5 control; P4r5 |
| A-R5-06 | Open or unioned registration ranges | gap, inflated and stale-policy releases eligible | REG5 |
| A-R5-07 | Release-global presence with a newer member registered | legitimate older release refused | selftest S69 |
| A-R5-08 | Reproduction quorum counted per statement | honest binaries unusable | P4r5 |
| A-R5-09 | Measured bytes replaced before installation | installing by path installs the swapped bytes | FA5 INS1 |
| A-R5-10 | Genuine but revoked binary started directly | `BINARY_NOT_ADMITTED`; `BINARY_REVOKED_SELF` | FA5 DA04, CI1 |
| A-R5-11 | Stale or disagreeing channel at first admission | `CHANNEL_DISAGREEMENT` under OP-13 (b) — **but review r5 showed an attacker lineage's fingerprint on the channel(s) was never tried (RV5-H1)** | FA5 CH1 |
| A-R5-12 | Stateful machine, clock set back | fails closed | P4r5 CLOCK; DA03r5 |
| A-R5-13 | Legacy `init` from positions inside `governance/` | `PARTIAL` or reported | ST5 |

**What revision 5's own attacks missed.** Every attack above substituted an input the architect had already modelled. None
substituted a selector the register did not list (the lineage, the quorum, the evaluator, the environment, the content
derivation). The omission was structural: the calculator's strategies came from the register, and the register was partial.

## 7. Root cause of review r5's classes (accepted in revision 6)

| Class | Mistaken equivalence | Lower-trust input | Higher-trust fact obtained |
|---|---|---|---|
| BC5-1 | *the typed fingerprint is a good selector of state, therefore of everything it commits to* | one channel page (rank 2), no key | the root of trust, the evaluator and the first TCB |
| BC5-2 | *every input named by digest ⇒ every input legitimately selected* | an image record with no assigned authority | the bytes of every production binary |
| BC5-3 | *the registration authority signed the unit map ⇒ the registration authority established it* | pipeline plus threshold-1 candidate and final keys | the effective constitutional content |
| BC5-4 | *a partial register plus a calculator over it ⇒ derived statements* | the architect's choice of which decisions to list | the owner's view of every consequence |

**The common cause.** FD-1 was stated as a rule but applied only to the decisions revision 5 changed. The register was not a
complete, checked artefact, so the calculator's strategies and the tests could not see the selectors it omitted.

Revision 6 makes completeness mechanical:
- the register is a data file, and every rule id of the rule tables must belong to a decision;
- every selector names a calculator strategy or a stated bound;
- every restrictor names a scenario that fails without it;
- every consequence statement is a generated block (`29` §5.5).

## 8. What revision 6 changes in kind

| Class | Revision-5 selector below authority | Revision-6 selector | Retained | Evidence |
|---|---|---|---|---|
| BC5-1 | one channel page: lineage (bundle order in the executor), channel quorum (from the selected Trust Policy), evaluator (one-channel digest) | a **first-contact code** agreed across the OP-13 sources binds a manifest that is the only selector of lineage, state and admitter list; compiled quorum; evaluator binding; the remainder stated as the **first-contact root** with computed minima equal to executed results; the root's composition is owner option OP-13 (T1-a…T1-d) | `gov-admit`, measured bytes, GB rules, ceremony order | FA6 S2, S3, S7; CS6 FC-ROOT |
| BC5-2 | the image record (no producer, no authority) | environments registered with upstream-pinned components and a first-hand environment reproduction quorum; reproducers re-assemble; OP-16 residual (E-a…E-c) | reproduction quorum; inputs by digest; OP-10 | ENV6 (real Rust toolchain); CS6 G_ENV |
| BC5-3 | CI-derived unit map; attestations reused by source; E7 without restrictors | custodians derive content first-hand; attestations bound to the registered candidate and kernel; E7 with AP-5's restrictors; reductions at the verifier; changes listed per project | release-scoped registration; append-only | CON6 (real 4.1.5); P4r6 G; CSI S71–S77 |
| BC5-4 | hand-written statements over a partial register | complete register (35 decisions); calculator over every selector strategy and eleven victim classes; generated statements; register and statement checks | FD-1, FD-2, FD-3 | CS6; `register_check.py`; `statements_check.py`; DA07r6 |

## 9. What remains a lower-trust input in revision 6, and why it is bounded

| Input | Decision it enters | Bound | Where |
|---|---|---|---|
| The first-contact sources of the OP-13 answer | first admission | the first-contact root, computed and executed equal; owner option OP-13 | `32` §6 |
| An operator typing one source's value for every required source | first admission | inside the root (`op1src`); TA-5′ | `32` §10 |
| Upstream environment and toolchain suppliers | bytes | OP-16, OP-10; TA-12′, TA-12 | `33`, `30` |
| Verification processes | source and content | OP-8; TB-4, TB-4′ | `30`, `34` |
| Reproducer and environment-reproducer processes at the quorum | bytes and environments | OP-9; TB-S1 | `30`, `33` |
| The local clock | pin validity; C3 window; OP-7 (b)/(c) | TA-7; high-water; future statements disable clock proofs; RS-2, RS-2b | `24` |
| The repository writer's choice among eligible registered releases (OP-11 (a)) | use on machines without a record | DR-25 shortfall; RR-2 | `29`, `20` |
| Repository-delivered state at or below a valid anchor | C1–C2 | RS-1 core | `24` |
| Project overlay; subdirectory legacy writes | configuration; working tree | LR-4, strength vector; `18` §9.1 | `26` |

## 10. Attacks the architect ran against revision 6 before hand-off

| ID | Attack (candidate instance of the class) | Result on revision 6 | Evidence |
|---|---|---|---|
| A-R6-01 | Channel quorum read from the state the typed value selects (FC-4 removed) | a one-page attacker lineage is admitted under OP-13 (b): FC-4 is load-bearing | FA6 S7 `quorum_from_selected_state` |
| A-R6-02 | Lineage from bundle order (FC-6 removed) | the genuine code with an attacker root served first fails the genuine admission; with FC-6 it is accepted | FA6 S7 `lineage_from_bundle_order`; ORD rows |
| A-R6-03 | Evaluator binding removed (FC-8) | a genuine but unlisted or revoked admitter admits; defence in depth, since a substituted evaluator is stopped only by FC-1…FC-3 | FA6 S7; S2 evaluator rows |
| A-R6-04 | OP-13 (c) "either suffices" with the signing path compromised alone | admitted: exactly the stated root set of the path alone | FA6 S2 `c_either_*`; CS6 FC-ROOT |
| A-R6-05 | Pipeline-supplied environment digest with no environment reproductions (revision-5 shape) | `ENVIRONMENT_NOT_REPRODUCED`; the injected binary is never registered | ENV6 E1 |
| A-R6-06 | Both supplier classes compromised under OP-16 (b) | accepted: the stated residual (b) | ENV6 E6; CS6 OP-16-ENV |
| A-R6-07 | Ceremony handed records for another candidate while the content equals the fetched source | the first oracle had no row; the DA03r6 mutant of that rule went undetected; scenarios added; now refused and detected | P4r6 `R6-CER-records_for_another_candidate`; DA03r6 `R6-ceremony-first-hand-records` |
| A-R6-08 | Concurrent `gov-admit` runs on a first-admission machine | without a lock a store already holding a record was moved aside in 15 of 20 trials; R-ADM-13 added; with the lock, none | ADM6 A11 |
| A-R6-09 | `.git/info/attributes` `* text` with CRLF conversion | converts kernel bytes despite the member (highest attribute precedence); stated as a fail-closed condition with doctor naming the source | ATTR6 O1–O4 |
| A-R6-10 | KS-14 at the two executors | root v1 with threshold 1: `ROOT_CHAIN_INVALID` in `gov-admit` (no lineage); a later version: `ROOT_VERSION_INVALID`; AP-2 states both | FA6 S5; P4r6 `R6-KS14_root_threshold_1` |
| A-R6-11 | Environment invariant counted first-contact root sets as pipeline selection | false invariant failures on FA configurations; the invariant is scoped to non-root sets, which the first-contact root invariant covers | CS6 INV-ENV-PIPELINE, INV-FC |
| A-R6-12 | A tool health command changed in a new registration | not listed until `TOOLS_REGISTRY` and `MCP_REGISTRY` joined the security-classified names; now exit 8 | CSI S76; CON6 B-A09 |
| A-R6-13 | A newline-bearing path merging two tree entries (RV5-B-A05) | `SOURCE_PATH_REFUSED`; the encoding alone distinguishes the trees | SRC6 T1 |
| A-R6-14 | "User-writable installation is C0–C2" | false under OP-7 (a), (b) and (c) without witnesses; restated to the computed classes | UW6 |
| A-R6-15 | A mutant of the E7 candidate check that crashed the oracle (hiding sensitivity) | replaced by a non-crashing substitution (final stands in for the candidate): detected | DA03r6 `R6-E7-candidate-held` |
