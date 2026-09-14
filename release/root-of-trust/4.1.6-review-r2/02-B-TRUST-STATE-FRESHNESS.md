# B — Trust-state freshness

## 1. Confirmed sound

| Property | Mechanism | Holds against |
|---|---|---|
| Omitted or replayed certification never skips a gate (mode A) | certification informational; absence never positive (`17` MS-1, MS-3) | A1, A5, A12 (source, transport, withholder) |
| Revocations accumulate across all sources; only a root-signed TPS unrevokes | `17` S5, §8 | everyone, **once the revocation is in the verifier's knowledge** |
| Truncating revocations or attestations from a later TSS is detected | `17` S4 (a), (e) | trust-state key thief, publisher error |
| The trust-store location cannot be redirected by environment | account-database resolution (`17` §4) | A4 |
| Mode A uses no clock; no decision uses the network | `17` §13, `09` R-NET-3 | A13, A5 |

## 2. Attacks

| # | Attack | What the verifier holds | Revision 2 result | Holds? | Evidence | Finding |
|---|---|---|---|---|---|---|
| B-1 | Omitted WITHDRAWN | bundle lacks the WITHDRAWN statement | NOT_CERTIFIED or CERTIFIED_AS_OF; gate required; `refuse_known_withdrawn` only if known | against A1: yes. Against A2/A3: the gate is a writable record | D, E P2 | R2-M1 |
| B-2 | Omitted REJECTED | same | same | same | D, E P2 | R2-M1 |
| B-3 | Omitted revocation | VTS knows it → refused. Fresh verifier, PTR stripped → release eligible; **no gate at use** for Git-delivered installs; ingress gate forgeable | only with retained state | E P4-B5, E P2 | R2-H2 |
| B-4 | Stale but correctly signed state | S7 signed references reveal staleness only while a statement carrying the higher reference is present; A1/A2 choose which statements are present | as B-3 | D, E P4-B5 | R2-H2 |
| B-5 | Forked chain: two TSS with the same sequence | both admissible; "the highest admissible" is ambiguous; no equivocation event; `S4 (f)` is checked only when the predecessor is present | **fails** | E P4-B3 | R2-M4 |
| B-6 | Truncated state (entries dropped from a higher TSS) | S4 → REGRESSION on verifiers holding the lower TSS | detected. Side effect: governed mutations refused until an admissible TSS arrives | D | (R2-M2 impact) |
| B-7 | Trust-state rollback (only older TSS files shipped) | highest admissible known | with retained state: yes. Fresh: attacker chooses | D | R2-H2 |
| B-8 | Root-rotation replay (key K removed in root N+1) | `TRUST_ROOT_STALE` if a statement references N+1; otherwise RS-1 | with retained state or a surviving reference: yes. Fresh, reference stripped: K's statements verify and its releases are eligible | D | R2-H2 |
| B-9 | Offline machine returning after a long absence | its VTS retains everything it ever verified; new PTR and bundles are accepted monotonically | **yes**, as long as the VTS survived. A new CI runner or wiped VTS falls into B-3 | D | — / R2-H2 |
| B-10 | Two machines with different last-seen states | each evaluates its own K; the PTR is extended only inside transactions; lock hints can raise HINT_MISMATCH | logically consistent, divergence acceptable. The HINT_MISMATCH gate is forgeable (M1) | D | R2-M1 |
| B-11 | **Purpose leakage into required minimums**: a release-candidate statement (lowest-custody key) carries `trust_state_sequence = 2^53−1` | `RM_state` = 2^53−1 → `STALE` on every verifier that ever sees it (and S10 copies it into the VTS). Revoking that statement does not remove it from S7. **No override** at ingress (`17` §7), so security updates cannot be installed until a root rotation removes the key. | **fails** the `05` §1 blast-radius claim ("candidates only") | E P4-B1 | R2-M2 |
| B-12 | Trust-state key thief publishes TSS n with `root_version: 999` | every later honest TSS fails S4 (c) → `TRUST_STATE_REGRESSION` → **governed mutations refused at use** on every verifier that saw n | **fails** the `05` §1 claim ("withholding only") | E P4-B4 | R2-M2 |
| B-13 | Certification key alone publishes CERTIFIED seq 3 after WITHDRAWN seq 2 (no attestation, no TSS reference) | S5 keeps only the highest sequence → the release leaves the negative set → `refuse_known_withdrawn` no longer applies | **fails** MS-2 and the "three signatures" claim for lifting a negative | E P4-B2 | R2-M3 |

## 3. Is the freshness design implementable without making network availability or the local clock the root of correctness?

**For a verifier with retained monotonic state: yes.**
- The root of freshness is the compiled T0 joined with everything the Verifier Trust Store has verified.
- Mode A never consults the clock, and no decision consults the network.
- The design does not accidentally turn either into a root.

**For a verifier without retained state** (new machine, ephemeral CI runner, deleted VTS), the design has no root for
currency beyond the build date of the binary:
- The effective state is whichever subset of genuine statements the repository writer leaves in `governance/trust/` and
  the installed release.
- Signed references (S7) help only while the referencing statement survives, and A2 decides that.
- Every compromise-recovery lever travels through the same channel: `min_binary_version`, `min_release_sequence`
  raises, revocations and root rotations (`05` §9, `19` §10).
- The verdict surface still shows `CURRENT_KNOWN(n)` and `verified: true`. Doctor stays silent because the OP-5 age is
  measured from the VTS's own last acceptance, and a fresh VTS has just accepted.

P4-B5 computes the consequence for an older binary on a fresh clone after A2 swaps in an older authentic release and
removes the trust record:
- effective TPS 1 instead of 3;
- floor 4 instead of 5;
- `min_binary_version` 4.1.6 instead of 4.1.8;
- an older release that was revoked under TSS 9 becomes the eligible policy root;
- no gate is involved.

Three honest designs exist, and they are owner-selectable (correction CD2-2):
- (a) require retained or pinned state from outside the repository before governed mutations;
- (b) expiring trust state for mutating use by stateless verifiers, with an explicit clock assumption;
- (c) accept the limit, show `FRESHNESS_UNPROVEN`, and scope G11 and rules (6), (7) and (18).

Revision 2 takes none of them and states bounds that do not hold (R2-H2).

## 4. Reference model

`evidence/P4-trust-state-model.py` encodes `17` S2–S9 and §6, `19` §5–§6 and §10 step 6 as written, with signatures
assumed valid. All six scenarios contradict a claim of the pack (`evidence/P4-trust-state-model.json`, every `agrees:
false`). The model is small enough for the architect to check each rule against the text.
