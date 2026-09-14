# Output 20 — Rollback and recovery model

> **RoT-1 revision 4 — PROPOSED, pending fresh independent reviews; not approved, not implemented.**
> Revision 4 keeps revision 3's restoring paths (CD3-0). It makes four changes:
> - reinstall and every PPS remedy take the identity to restore from the VTS per-project record (CR-09, RV3-L4);
> - restoring paths that are C3 need anchors satisfied by inclusion and a currency proof (`24`);
> - `overlay.prev` restores and remedies evaluate the recorded strength vector over the post-transaction effective policy;
> - RR-2 is restated.

## 1. Every restoring path

| ID | Path | Revision 3 treatment |
|---|---|---|
| RB-1 | Automatic transaction rollback | Exchange back `trust.prev` (kernel, release statement, lock). `state/` and `root/` are the union (`18` §5.2). Then normal use-time evaluation; may be `INELIGIBLE` and fail closed. |
| RB-2 | `gov update --rollback` | restore pipeline (§2) + downgrade policy (§4) |
| RB-3 | `gov kernel reinstall [--source]` | The statement digest must equal the installed identity **recorded in the VTS per-project record**; the lock is a hint (CR-09). Re-attestation allowed; never a downgrade. Restores PPS and occupation entries; never clears `PROJECT_STRENGTH_WEAKENED`. |
| RB-4 | `gov recover` for an install journal | §5 |
| RB-5 | `gov adopt rollback --batch 0` / recover | `install_tx::uninstall` (§6) |
| RB-6 | `gov adopt rollback --batch N` (N ≥ 1) / recover | project files only, from `.governance-runtime/adoption/batch-N/`; GovernedFs refuses PPS targets |
| RB-7 | `gov cit rollback` / recover | GovernedFs refuses PPS targets; CIT planning refuses them (§7) |
| RB-8 | Snapshot restore (`.governance-runtime/snapshots/<CI>/`) | untrusted source (T4), §3 |
| RB-9 | Cache restore | none exists |
| RB-10 | Git checkout, revert or merge changing protected paths | evaluated, not restored (§9) |
| RB-11 | Partial deletion of protected paths or occupation entries | `PARTIAL` (`18` §9), §8 |
| RB-12 | "Rollback" of trust metadata | impossible: every transaction writes the union; knowledge and anchors are monotonic (`17` S11, `24` §8) |
| RB-13 | Legacy residue: `.governance-runtime/update/*`, legacy `.governance-runtime/migration/*` | quarantined by the first RoT-1 transaction on the machine; never a RoT-1 restore source; `.governance-runtime/migration` is occupied (`26` §3.1) |

## 2. Common restore pipeline

```text
target (snapshot | bundle | release directory | trust-tx/<TX>/trust.prev)
   ─► authenticate (04 V0–V11) ─► E7 surface and eligibility under the CURRENT effective policy (19 §6)
   ─► trust state KNOWN, anchors satisfied by inclusion, freshness ANCHORED/WITNESSED and a currency proof (24 §4.3–§4.4: C3)
   ─► downgrade policy (§4) with its local trust-gate confirmation (27)
   ─► authority floor for rollback_apply (19 §8)
   ─► install transaction (18 §5) with union trust record
   ─► post-commit snapshot equality + eligibility (VU-6) ─► recorded strength vector over the post-transaction effective policy (19 §9) ─► re-recorded
```

No restoring path writes a byte into the Protected Path Set outside this pipeline.

## 3. Snapshots

- **Where and what.** Update transactions create `.governance-runtime/snapshots/<CI>/`, which is untracked. A snapshot
  holds:
  - the previous statement envelope and the previous trust statements;
  - content objects by digest;
  - the previous overlay and views;
  - the trust state and anchor epoch known when it was taken.
- **Authority.** A snapshot carries no authority. Restore reads it like a bundle and evaluates eligibility under the
  **current** effective policy and freshness.
- **Failure codes.** A tampered snapshot gives `SNAPSHOT_UNAUTHENTICATED`. An authentic but ineligible one gives
  `SNAPSHOT_INELIGIBLE(reason)`.
- **Legacy snapshots.** 4.1.x snapshots (`.governance-runtime/update/<v>/`) are quarantined, and historical identities are
  refused as restore targets (`13` §6).

## 4. Downgrade policy

Relative to the installed eligible release:

| Target | Rule |
|---|---|
| Same statement digest as the VTS per-project record | reinstall; no gate; authority `install_kernel` |
| Lock identity differs from the VTS per-project record | the record wins; the lock identity is a target judged by this table (RV3-B-A15: an older lock identity is a downgrade) |
| Same payload digest, different envelope | re-attestation; no gate |
| Higher `release.sequence` | an update (`framework_update` trust gate under OP-3 mode A) |
| Lower sequence, eligible | **downgrade**: the `downgrade` trust gate bound to both statement digests, confirmed locally (`27`), with the effective-policy comparison shown; authority `rollback_apply` from the floor |
| Lower sequence, below `min_release_sequence` | refused `RELEASE_INELIGIBLE(below_min_release_sequence)`; no override |
| Revoked with `refuse_install` | refused `RELEASE_INELIGIBLE(revoked)`; no override |
| Historical identity | refused `RELEASE_INELIGIBLE(historical)`; no override |
| Candidate in a production project | refused `RELEASE_INELIGIBLE(candidate)` |
| Surface not registered in the effective TPS | refused `RELEASE_INELIGIBLE(surface_*)` |
| Trust state not `KNOWN`, anchors not satisfied, freshness not `ANCHORED`/`WITNESSED`, or no currency proof | refused with the `24` §4.3 code until metadata is supplied, the machine is anchored or a currency proof is given |

After a downgrade, the effective policy is the older kernel's registered content joined with the effective TPS
(`19` §5). The ledger records both CIs, the local confirmation digest, the TPS version, the anchor epoch and the
comparison. The ledger is evidence, never the rule.

## 5. Install-journal recovery (`gov recover`)

A journal is honoured only when the VTS per-project record lists its TX as open for this `project_trust_id` and path, and
the journal is untracked (`18` §5.1). Otherwise it is `FOREIGN_TRANSACTION_ARTEFACT`: reported and ignored.

| Journal phase (honoured) | Action |
|---|---|
| `prepared`, `staged`, `verified-staged` | move `trust-tx/<TX>` to `trust-tx/abandoned/`; deregister |
| `swapped`, `migrated` | Evaluate the exchange-back target (`trust.prev`) through the restore pipeline (§2). The downgrade policy applies relative to the VTS per-project record; the lock is a hint. If eligible: exchange back with union `state/` and `root/`. **The `overlay.prev` restore runs the computed-weakening check of `19` §9 against the current overlay. A non-empty list needs the `weakening` trust gate.** Otherwise leave `PARTIAL` and report. |
| `committed` (lock written) | Evaluate the installed state; if verified and eligible, finish; otherwise evaluate `trust.prev` as above. |
| `verified` | clean up |

A forged journal or `.prev` planted by A3 is honoured only if A3 also forged the VTS registry entry (same-user boundary,
RS-3). Even then it is judged as a downgrade (refused or trust-gated), and a weakened `overlay.prev` meets the weakening
gate (review RV2-A25). A journal committed by A2 is foreign on every clone.

## 6. Adoption batch 0 and its rollback

- Batch 0 is an install transaction (operation `adopt_install`). On a brownfield repository it also performs the layout
  creation of `26` §2.
- RoT-1 adoption evidence lives at `spec/audits/ADOPTION/`, and RoT-1 adoption batch snapshots at
  `.governance-runtime/adoption/batch-N/`. The legacy names are occupied.
- Rolling back batch 0 is `install_tx::uninstall`. Under the exclusive lock it moves `governance/trust` and the
  occupation entries into `trust-tx/<TX>/removed/`, commits through the journal, and leaves the result `ABSENT`.
- Adoption snapshots never contain PPS paths. The planner classifies `governance/trust/**`, occupation entries and
  `.governance-runtime/trust-tx/**` as `GOVERNANCE_CURRENT`. The executor refuses PPS targets through GovernedFs.

## 7. CIT operations

- Planning refuses a manifest whose `write_file`, `move_file` (source or destination), `delete_file` or record operation
  resolves into the PPS, including occupation entries (`CIT_PROTECTED_PATH`).
- Execution and CIT snapshot restore go through GovernedFs.

## 8. Partial-install recovery (fail closed)

1. The policy root is EmbeddedSnapshot ⊔ floor.
2. Mutations are refused (`INSTALL_STATE_PARTIAL`), and doctor D033 reports CRITICAL with the observed components,
   including `occupation`.
3. Remedies (authority from the floor; freshness per `24` §4.3):
   - `gov kernel reinstall --source <S>`: S authenticates to the identity in the VTS per-project record or, on a machine with no record, to the lock-recorded identity if that is eligible (RR-2). Occupation entries are recreated. A same-digest reinstall needs no freshness, so an unanchored `PARTIAL` install stays repairable (C-2, RV3-C-A08).
   - `gov update --apply --source <eligible release>`;
   - `gov recover`;
   - `gov init --force`, treated as reinstall or update.
4. Each remedy is an install transaction. It restores PPS and occupation entries, never project strength: the strength
   check (`26` §6) remains until its trust gate.

## 9. Git-delivered changes and use-time downgrade detection

- Git can deliver any combination of files. That is evaluated, not restored: authenticity, integrity, E7, eligibility,
  floors, trust state and freshness.
- The VTS per-project record holds, per `(repository path, project_trust_id)`, the highest installed eligible sequence
  and CI, the anchor epoch at install, and the project-strength vector.
- A verified, eligible installed release whose sequence is **lower** than that record → `INELIGIBLE`
  (`downgrade_without_transaction`). Remedy: an authorised rollback (trust gate) or an update.
- A changed `project_trust_id` at a known path → `KERNEL_INELIGIBLE(project_trust_id_changed)`.
- A machine without a record (fresh clone) cannot detect a downgrade. §10 RR-2 bounds it.

## 10. Residuals (restated)

| ID | Residual | Bound |
|---|---|---|
| RR-1 | Automatic rollback may leave an ineligible installation when the failed update's bundle raised the policy. | Fails closed; remedy: complete an update to an eligible release. |
| RR-2 | On a machine without a per-project record, an A2-delivered older eligible release is accepted as installed content, and `kernel reinstall` uses the lock identity. | Its content must be registered in the machine's effective TPS (E7), with registered precedence and floors joined. Governed use follows anchors and currency. Under OP-7 (a)–(c) an unanchored machine performs no governed mutation. An anchored machine judges the release in its anchored chain, and statements outside the chain are never effective. C3 needs a currency proof. Under OP-7 (d), unanchored use is bounded by the compiled TSS, labelled `FRESHNESS_UNPROVEN`, and never C3. |
| RR-3 | A3 deletes the per-project record or the VTS. | As RR-2 on that machine; `UNANCHORED` (RS-3). |
