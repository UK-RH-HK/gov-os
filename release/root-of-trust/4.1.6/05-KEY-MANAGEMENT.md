# Output 5 — Key-purpose and key-management model

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 makes these changes:
> - adds the **`freshness-witness`** purpose, which shares a key with no other purpose (KS-11; `24` §3.3; CD3-2 (3));
> - **verification attestation v2** and **build attestation v2** name the verified `source` (CD3-3; `25` §5.1);
> - **the minimum distinct keys are re-derived** from the corrected rules: a lift needs an attestation naming the negative
>   (CR-01); an accepted malicious binary needs route S or route B (CD3-3 (3));
> - **blast radius restated** (CD3-2 (5), CR-07/RV3-L2);
> - custodial rules 3, 6 and 7 check the attested source before signing;
> - playbooks revoke and never un-reference artefacts (CR-04);
> - rotation re-signs retained statements (RV3-L8);
> - SV-11 refuses statements issued in the future (CR-06).
>
> CD3-0 retains the compiled whitelist and KS-1…KS-10.

## 1. Purposes

A **purpose** is the authority a key exercises when it signs. Every statement type maps to exactly one purpose, fixed in
the binary. Root metadata grants purposes to keys under compiled constraints (§3).

| Purpose | Signs | May assert | May never assert | Default keys / threshold (`21`) | Impact if this key alone is stolen (revision 4) |
|---|---|---|---|---|---|
| `root` | `trust-root.v2` | key set, grants, thresholds, key revocation | anything about releases or state | 3 keys, threshold 2 | none below threshold |
| `trust-policy` | `trust-policy.v2` | Constitutional Surface (`23`: exact precedence registration, presence, Overlay Surface, owner-domain slots), eligibility including historical releases and (OP-2) production sources, install authority, gating, bootstrap (OP-6, OP-7 parameters, clock reset), lowering history, unrevocation, chain reset | authenticity, certification | root keys at root threshold (KS-2) | as root |
| `trust-state` | `trust-state.v2` | the published set of separately signed statements at a sequence, including artefact statements | any fact not itself separately signed; currency (a TSS is never a witness) | 1, threshold 1 | **Anchored machine:** a statement that does not descend from the anchor is never effective (`BELOW_ANCHOR`, or `REGRESSION` when the anchored statement is held). A descendant that drops a held revocation is non-admissible (freeze). A descendant presented to a machine that never held a later revocation admits no more than withholding already admits (RS-1 core). **Stateless machine:** a freeze under OP-7 (a)–(c); under (d), a descendant of the compiled T0 (equals the (d) residual; never C3). **Never:** lift a negative, create certification, witness currency, or accept a binary alone (`17` §15). |
| `release-final` | `release-final.v2` | authenticity of final release content, including its `release.source`, which must equal its candidate's (V8) | binaries, binary source, certification, verification, eligibility, trust state, surface registration | 1 active + 1 standby, threshold 1 (OP-2 may choose 2) | Authentic finals can be forged. None becomes a policy root unless all of these hold: its whole surface is registered in a root-signed TPS (E7); its POLICY_PRECEDENCE equals the registration; it passes a local trust gate at ingress. Within that registration it sets the kernel value of the **52 `project_tunable` and 32 `release_bound` leaves**; the project layer can already set the tunables, and keys read by security decision points are not tunable (`23` §5.2, CR-07). **It cannot choose a binary's source** (V8 source equality, `25` A4b). |
| `release-candidate` | `release-candidate.v2`, `artifact-candidate.v2` | candidate content and its `release.source`; candidate binaries for evaluation | final stage, production binaries, certification | 1, threshold 1 (OP-4) | Candidates only; their references constrain only their own ingress (`17` S7). With `release-final` and `verification-attestation`, route S (§3). |
| **`release-artifact`** | `artifact-final.v2` | production binary digests, each bound to its Trust Base Manifest digest (`25` §3–§4) | release authenticity, source legitimacy, certification, trust state, reproduction | **≥ 2 keys, threshold 2** (compiled minimum; OP-2 may add a root co-signature) | nothing (threshold) |
| `build-attestation` | **`build-attestation.v2`** | an independent reproduction of a binary and its TBM from a `source {release_commit, source_tree_digest, build_inputs_digest}` | authenticity; that the source was verified | 1, threshold 1 (OP-2 may choose 2 rebuilders) | nothing alone (a binary also needs `release-artifact` ×2, a trust-state reference and an attested source) |
| `verification-attestation` | **`verification-attestation.v2`** | the verifier's verdict for one candidate digest, **the `source` it reproduced**, and optionally the negative statement a new ACCEPTED verdict lifts (`lifts_negative_statement_digest`) | certification, authenticity | 1, threshold 1 (OP-2 may choose 2) | A verdict alone certifies nothing and accepts no binary. Together with `release-candidate`, `release-final` and pipeline input, it gives route S (§3); under OP-2 (S1), not even that. |
| `certification-status` | `certification-status.v2` | CERTIFIED / REJECTED / WITHDRAWN for a final (optionally naming artefact statements) | authenticity; CERTIFIED without an ACCEPTED attestation | 1 + standby, threshold 1 | Negatives take effect (denial of service). CERTIFIED stays unreferenced: invisible, and it cannot lift a negative (`17` MS-2). |
| `revocation` | `revocation.v2` | refusal of named digests | new trust; unrevocation | 1, threshold 1 | denial of service only |
| `retrieval-profile` | `retrieval-profile.v1` | provenance and integrity of a reference retrieval profile | authorisation; release authenticity | 1, threshold 1 | profile integrity only |
| **`freshness-witness`** (OP-7 (c) only) | `freshness-witness.v1` | that `(sequence, digest)` of an existing TSS was the latest as of `issued_at` | any state; any other fact | owner choice; **C3 and binary acceptance need ≥ 2 distinct keys (compiled)**; threshold 1 admits C1–C2 only | One key at threshold 2: nothing. Keys at the C3 threshold: stale selection of genuine existing TSSs on witness-reliant machines until rotation (`24` §3.3, RS-5). Never state creation. |

The **test** lineage is a trust profile, not a purpose. It exists only in the separate test-profile binary (§10).

## 2. Compiled statement-type table (T0)

| payloadType (`application/vnd.agentic-engineering-os.` …) | `_type` (`https://agentic-engineering-os/statement/` …) | Purpose | Accepted from |
|---|---|---|---|
| `trust-root.v2+json` | `trust-root/v2` | `root` | compiled; bundle, PTR, VTS, refresh (chain-verified) |
| `trust-policy.v2+json` | `trust-policy/v2` | `trust-policy` | any source |
| `trust-state.v2+json` | `trust-state/v2` | `trust-state` | any source |
| `release-final.v2+json` | `release/v3`, `stage = final` | `release-final` | any source |
| `release-candidate.v2+json` | `release/v3`, `stage = candidate` | `release-candidate` | any source |
| `artifact-final.v2+json` | `artifact/v3`, `stage = final` | `release-artifact` | any source |
| `artifact-candidate.v2+json` | `artifact/v3`, `stage = candidate` | `release-candidate` | any source (evaluation only) |
| **`build-attestation.v2+json`** | `build-attestation/v2` | `build-attestation` | any source |
| **`verification-attestation.v2+json`** | `verification-attestation/v2` | `verification-attestation` | any source |
| `certification-status.v2+json` | `certification/v3` | `certification-status` | any source |
| `revocation.v2+json` | `revocation/v2` | `revocation` | any source |
| `retrieval-profile.v1+json` | `retrieval-profile/v1` | `retrieval-profile` | any source |
| **`freshness-witness.v1+json`** | `freshness-witness/v1` | `freshness-witness` | any source |

**Withdrawn:**
- `historical-identity.v1+json`;
- the revision-3 drafts `build-attestation.v1+json` and `verification-attestation.v1+json`, which carry no `source`.

None of these was ever issued. No revision-4 binary accepts them.

## 3. Grants and separation (compiled)

Root metadata lists, per purpose, `key_ids`, `threshold` and optionally `require_algorithms`
(`schemas/trust-root.schema.json`, `x-schema-version` 3.0.0).
- A key listed under several purposes is a grant.
- The binary checks every root version.
- A violation invalidates that version (`PURPOSE_SEPARATION_VIOLATION`).

**Compiled whitelist** (unchanged, CD3-0). A key may hold two or more purposes only if **every pair** of its purposes is
listed. Every unlisted pair is forbidden.

| Permitted pair | Why permitted | Owner choice |
|---|---|---|
| `root` + `trust-policy` | floors are constitutional (KS-2 requires it) | mandatory |
| `release-final` + `release-candidate` | OP-4 "no separate candidate key"; stage separation, E2 and V8 still hold | OP-4 |
| `revocation` + `certification-status` | both only add negative facts or unreferenced positives | OP-2 |
| `revocation` + `trust-state` | revocation adds negatives; trust-state references them | OP-2 |
| `retrieval-profile` + `release-final` | profile integrity only | OP-2 |

**Named constraints** (consequences of the whitelist, stated for tests and error details):

| ID | Constraint | Reason |
|---|---|---|
| KS-1 | `root` keys may additionally hold only `trust-policy` | root keys stay offline |
| KS-2 | `trust-policy` key ids ⊆ `root` key ids; `trust-policy.threshold ≥ root.threshold` | floors and surface are constitutional |
| KS-3 | `release-final` ∩ `certification-status` = ∅ | authenticity is not certification |
| KS-4 | `release-final` ∩ `verification-attestation` = ∅ | signer is not verifier |
| KS-5 | `certification-status` ∩ `verification-attestation` = ∅ | certifier is not verifier |
| KS-6 | `release-candidate` ∩ (`certification-status` ∪ `verification-attestation`) = ∅ | same |
| KS-7 | every threshold between 1 and the key count; no revoked key granted; no public key under two ids | well-formedness |
| KS-8 | `trust-state` ∩ (`certification-status` ∪ `verification-attestation`) = ∅ | a visible CERTIFIED, and any lift, needs three distinct keys |
| KS-9 | `release-artifact` keys hold no other purpose; `threshold ≥ 2` | binaries carry root-threshold authority (`25`) |
| KS-10 | `build-attestation` ∩ (`release-final` ∪ `release-candidate` ∪ `release-artifact`) = ∅ | the reproducer is not the signer |
| **KS-11** | **`freshness-witness` keys hold no other purpose; the C3 use requires ≥ 2 distinct valid witness keys** | currency must not come from a key that can also choose state (RV3-H2 (3)) |

**Minimum distinct keys, by consequence** (revision 4, re-derived; evidence named):

| Consequence | Distinct keys | Evidence |
|---|---|---|
| visible CERTIFIED | 3 (verification-attestation, certification-status, trust-state) | `P4r4` K1, K3 |
| lift of WITHDRAWN/REJECTED | **3, with an attestation issued for the lift that names the negative** (revision 3 claimed 3, but the pre-withdrawal attestation made it 2, RV3-M1) | `P4r4` RV3-B-A05 |
| **accepted malicious production binary, route S** (malicious source through the verification record) | **3** (verification-attestation, release-candidate, release-final; KS-4 and KS-6 force distinctness) **plus control of the build input**; **2** under OP-4 "no"; root threshold under OP-2 (S1); +1 under OP-2 (S2) or (S3) | `VA4` |
| **accepted malicious production binary, route B** (malicious bytes claimed as a build of genuine attested source) | **4 keys over 3 purposes** (release-artifact ×2, build-attestation, trust-state) | `VA4` |
| route I (insider commit accepted by an honest verifier) | none (process bound, TB-4) | `25` §7 |
| currency for C3 on a witness-reliant machine (OP-7 (c)) | 2 witness keys (compiled minimum) | `P4r4` RV3-B-A06 |
| new floor, surface registration, precedence registration, lowering, production source (S1), clock reset | root threshold | `19` §10.6 |

No single key of any purpose can mint an accepted production binary, lift a negative, witness C3 currency or register
constitutional content. Key separation is not people separation. The constraints stop one stolen key, and in the cases
above one custodian's set of keys, from spanning the stated authorities.

## 4. Signature verification rules (every statement, every source)

| ID | Rule | Failure code |
|---|---|---|
| SV-1 | Strict envelope; no duplicate members; strict padded base64; payload ≤ 4 MiB; ≥ 1 signature | `STATEMENT_MALFORMED` |
| SV-2 | payloadType in the compiled table (§2); withdrawn types refused | `STATEMENT_TYPE_UNKNOWN` |
| SV-3 | Payload bytes equal their GOV-JCS-1 re-serialisation | `STATEMENT_MALFORMED` |
| SV-4 | Effective root chain built (`17` S2); key ids recomputed; duplicate public keys refused; whitelist and KS-1…KS-11 hold | `TRUST_ROOT_INVALID` / `PURPOSE_SEPARATION_VIOLATION` |
| SV-5 | Purpose = compiled mapping of the payloadType | — |
| SV-6 | Each signature: key in the effective root, granted the purpose, not revoked; algorithm from the key record; strict Ed25519 over PAE | `SIGNER_UNKNOWN` / `PURPOSE_NOT_GRANTED` / `SIGNER_REVOKED` / `SIGNATURE_INVALID` |
| SV-7 | Distinct valid keys ≥ threshold (compiled minimum 2 for `release-artifact`; 2 for the C3 use of `freshness-witness`); `require_algorithms` satisfied | `THRESHOLD_NOT_MET` |
| SV-8 | Payload validates against the compiled schema | `STATEMENT_MALFORMED` |
| SV-9 | `_type`, `signing.purpose` and `stage` consistent with the payloadType | `STATEMENT_TYPE_MISMATCH` |
| SV-10 | `trust_profile` = binary profile; `trust_root_id` = binary lineage | `TRUST_PROFILE_MISMATCH` / `STATEMENT_LINEAGE_MISMATCH` |
| **SV-11** | `issued_at` ≤ local clock + compiled skew (300 s). Otherwise the statement is refused at ingest and never recorded (CR-06). | `STATEMENT_ISSUED_IN_FUTURE` |

## 5. Authority questions answered

| Authority | Held by | Can another purpose exercise it? |
|---|---|---|
| Final release authenticity | `release-final` | `release-candidate` only under OP-4 "no" |
| **Source of a production binary** | an ACCEPTED `verification-attestation` referenced by the effective TSS, equal across candidate, final, build attestation and TBM (`25` A4b); under OP-2 (S1) also `trust-policy` | no; `release-final` never chooses it |
| Production binary acceptance | `release-artifact` (≥ 2) + `build-attestation` + attested source + `trust-state` reference + currency proof (`25` §5) | no |
| Verification result | `verification-attestation` | no |
| Certification state | `certification-status`; a visible CERTIFIED also needs an attestation and a trust-state reference | no |
| Revocation | release level `revocation`; key level `root`; unrevocation `trust-policy` | revocation cannot unrevoke |
| Historical-release set; constitutional surface; precedence; floors | `trust-policy` | no |
| **Currency on a machine** | nobody signs it for a stateful machine: it is proven locally (`24` §4.4). Under OP-7 (c), `freshness-witness` at threshold. | never `trust-state` |
| Current install eligibility | nobody signs it; it is computed (`19` §6) | — |

## 6. Representation

- Key id: `ed25519:` + 64 lowercase hex of SHA-256(raw public key), recomputed on every use.
- Trust-root id: `sha256:` of the canonical v1 root payload.
- Canonical repository layout (public data only):
  - `trust/production/root/<version>.dsse.json`;
  - `policy/<policy_version>.dsse.json`;
  - `state/<sequence>.dsse.json`;
  - `statements/<digest>.dsse.json` (certification, attestation, revocation, build attestation, witness);
  - `artifacts/<release_id>/artifact-final.dsse.json`;
  - `fingerprints.txt` (root and state fingerprints; a convenience copy, not a channel).
- Test lineage: `tests/fixtures/trust/`.

## 7. Ceremony and signing rules

1. **No private keys outside custody.** Never in any repository or its history, bundles, CI logs, CI secrets,
   `.governance-runtime/`, or build machines.
2. **Sign what you reproduced** (`release-final`, `release-candidate`).
   - The signer rebuilds the unsigned payload from `git archive` of `release.source.release_commit`, byte for byte, with
     deterministic inputs.
   - The signer checks `source_tree_digest` and `build_inputs_digest`.
   - A final's signer additionally checks that `release.source` equals the promoted candidate's (V8).
3. **Attest what you verified, including its source** (`verification-attestation`).
   - The independent verifier reproduces the candidate payload from `release.source` with the named build inputs.
   - It attests `source` only when the reproduction is identical.
   - An attestation that lifts a negative names that negative's statement digest (CR-01).
4. **Certify only what was attested** (`certification-status`).
5. **Register before you release** (`trust-policy`). `gov trust draft-policy` lists every surface classification,
   precedence registration, Overlay Surface and bootstrap change, and every computed reduction (`23` §6.2). The root
   ceremony signs only after reviewing it. Under OP-2 (S1) it also registers the production source.
6. **Reproduce before you accept a binary, and only from attested source** (`build-attestation`, `release-artifact`).
   - The rebuilder runs `gov trust verify-artifact --stage rebuilder`: the candidate's ACCEPTED attestation names the
     source, and the final's source equals it. It then rebuilds from that source and attests only when the binary digest
     and TBM digest are identical.
   - The two `release-artifact` custodians run `--stage custodian`: A1–A4b hold, the build attestation names the
     attested source, and the TBM `binary.source` equals it. Only then do they sign.
   - Under OP-2 (iii), the root co-signers run the same stage and compare the source with the owner's verification
     record.
7. **Publish admissible state that references only attested sources** (`trust-state`).
   - `gov trust publish --stage publisher` refuses a TSS that is not admissible, or whose `prior_states[]` is incomplete.
   - It refuses one that references an artefact statement whose binary fails A4a/A4b.
   - It refuses one that drops any lower `artifacts[]` reference (use revocation instead; §9).
   - The state fingerprint is published in the independent channels (`24` §3.1).
8. **Producer hygiene.** `gov release build` refuses private key material, fills `release.source`, and runs the surface
   checker (`23` §6).
9. **Ceremony record.** Public keys, grants, thresholds, lineage id, custodians, date; never secrets.
10. **Witness custody (OP-7 (c) only).**
    - The witness service is scheduled, holds only `freshness-witness` keys (KS-11), and signs a witness only for the TSS
      the owner published most recently.
    - `expires_at − issued_at ≤ bootstrap.witness_max_validity_hours`.

## 8. Rotation, revocation, re-attestation and re-signing

- **Purpose rotation:** root N+1, signed by the thresholds of N and N+1.
- **Key revocation:** root N+1 removes the key and lists it in `revoked_keys`.
- **Re-signing (RV3-L8).** Before publishing a root N+1 that removes a key of any purpose, the owner re-signs, with the
  successor key, every retained honest statement signed by the removed key. That covers:
  - the trust-state history, including every TSS an anchor can name;
  - finals and candidates, attestations, certifications, build attestations, artefact statements and witnesses.

  The re-signed statements ship in the same bundle or refresh as N+1. Payload digests do not depend on signatures, so
  anchors, references and the TBM stay satisfied. Evidence: `P4r4` `RV3-D-A16_rotation_resigns_retained_statements`.
- **Durability:** a verifier is protected once it holds root N+1. Anchored machines receive it through refresh or a
  bundle. An anchor naming a TSS that references N+1 makes an unrotated machine `BELOW_ANCHOR` or `INCOMPLETE`
  (`17` §9).

## 9. Compromise and loss playbooks (revision 4)

Every row that publishes root N+1 includes re-signing per §8.

| Event | Actions | Durable once the verifier holds |
|---|---|---|
| `release-final` key stolen | Root N+1 removes the key. Revoke known forged digests. A TPS raises `min_release_sequence`. Re-sign genuine finals. Publish TSS and state fingerprint. | root N+1 or the TPS |
| `release-candidate` key stolen | Root removes the key; revoke forged candidates. | root N+1 |
| `verification-attestation` key stolen | Root removes the key. Revoke attestations not issued by the verifier. Revoke binaries accepted through them (route S). Review dependent certifications. Consider OP-2 (S1) or (S2). | root N+1 and the revocations |
| One `release-artifact` key stolen | Root N+1 replaces it; nothing to revoke (threshold). | root N+1 |
| **`release-artifact` ×2 (+ `build-attestation` + `trust-state`) stolen (CR-04)** | Root N+1 removes the keys. **Revoke** the forged artefact digests. The next TSS **keeps every `artifacts[]` reference** and adds the revocations. Advise re-verification of installed binaries. **A TSS never drops artefact references** (dropping them is non-admissible, `17` S4 (d)). Evidence: `P4r4` `RV3-B-A09_playbook_revokes_never_unreferences`. | root N+1 plus the TSS with the revocations |
| `build-attestation` key stolen | Root removes the key; review attestations it signed. | root N+1 |
| `certification-status` key stolen | Root removes the key; revoke forged certification statements. Nothing becomes visible or lifted without the other two purposes and a lift attestation. | root N+1 |
| `revocation` key stolen | Root removes the key; a TPS `unrevokes` forged revocations. | the TPS |
| `trust-state` key stolen | Root removes the key and re-signs the retained history (§8). If histories forked, a TPS `state_chain_reset`. Anchored machines never make non-descendants effective (`24` §3.4). | root N+1 / the TPS |
| **`freshness-witness` keys stolen (OP-7 (c))** | Root N+1 removes the keys. A TPS `bootstrap.clock_reset` if forged witnesses raised clock high-water marks. Advise re-anchoring of witness-reliant runners. | root N+1 and the TPS |
| `retrieval-profile` key stolen | Root removes the key. | root N+1 |
| One root key stolen or lost | The remaining custodians sign N+1. | immediately |
| Root threshold stolen or lost | New lineage; re-bootstrap (`06`). | reconfirmation |

## 10. Test, development and production separation

1. **Separate binary.** The test lineage covers all twelve purposes and compiles only into `gov-test-profile`, a separate
   crate with a `compile_error!` guard in `gov`. The TBM records `trust_profile`, and the release pipeline and
   `verify-artifact` require `production`.
2. **Production refuses test material** in every statement, root, lock and trust record.
3. **Development builds.** A development binary has TBM `binary.build: development`. `verify-artifact` never accepts it,
   and its embedded kernel is `DEVELOPMENT_UNSIGNED` unless the compiled statement verifies.

## 11. Algorithms

Ed25519 (RFC 8032, strict) and SHA-256 only. `require_algorithms` allows a transition requiring one signature per
algorithm. `source_tree_digest` is SHA-256 over `git archive`, so source binding does not rest on SHA-1 commit ids.
