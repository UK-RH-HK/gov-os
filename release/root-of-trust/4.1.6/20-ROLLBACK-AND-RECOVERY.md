# Output 20 — Rollback and recovery model

> **RoT-1 revision 3 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> Revision 3 makes these changes:
> - union trust records (R2-M9);
> - a locally registered transaction area outside Git (R2-M9);
> - `overlay.prev` restores behind the computed-weakening trust gate (R2-M9);
> - trust gates bound locally (R2-M1, `27`);
> - freshness requirements on every restoring path (R2-H2, `24`);
> - legacy residue quarantined and occupied (R2-H4, `26`);
> - RR-2 restated.

## 1. Every restoring path

| ID | Path | Revision 3 treatment |
|---|---|---|
| RB-1 | Automatic transaction rollback | Exchange back `trust.prev` (kernel, release statement, lock). `state/` and `root/` are the union (`18` §5.2). Then normal use-time evaluation; may be `INELIGIBLE` and fail closed. |
| RB-2 | `gov update --rollback` | restore pipeline (§2) + downgrade policy (§4) |
| RB-3 | `gov kernel reinstall [--source]` | the statement digest must equal the installed one; re-attestation allowed; never a downgrade. Restores PPS and occupation entries. |
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
   ─► trust state KNOWN and freshness ANCHORED/WITNESSED (24 §4.3: C3)
   ─► downgrade policy (§4) with its local trust-gate confirmation (27)
   ─► authority floor for rollback_apply (19 §8)
   ─► install transaction (18 §5) with union trust record
   ─► post-commit snapshot equality + eligibility (VU-6) ─► project-strength vector re-recorded
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
| Same statement digest | reinstall; no gate; authority `install_kernel` |
| Same payload digest, different envelope | re-attestation; no gate |
| Higher `release.sequence` | an update (`framework_update` trust gate under OP-3 mode A) |
| Lower sequence, eligible | **downgrade**: the `downgrade` trust gate bound to both statement digests, confirmed locally (`27`), with the effective-policy comparison shown; authority `rollback_apply` from the floor |
| Lower sequence, below `min_release_sequence` | refused `RELEASE_INELIGIBLE(below_min_release_sequence)`; no override |
| Revoked with `refuse_install` | refused `RELEASE_INELIGIBLE(revoked)`; no override |
| Historical identity | refused `RELEASE_INELIGIBLE(historical)`; no override |
| Candidate in a production project | refused `RELEASE_INELIGIBLE(candidate)` |
| Surface not registered in the effective TPS | refused `RELEASE_INELIGIBLE(surface_*)` |
| Trust state not `KNOWN`, or freshness not `ANCHORED`/`WITNESSED` | refused with the `24` §4.3 code until metadata is supplied or the machine is anchored |

After a downgrade, the effective policy is the older kernel's registered content joined with the effective TPS
(`19` §5). The ledger records both CIs, the local confirmation digest, the TPS version, the anchor epoch and the
comparison. The ledger is evidence, never the rule.

## 5. Install-journal recovery (`gov recover`)

A journal is honoured only when the VTS per-project record lists its TX as open for this `project_trust_id` and path, and
the journal is untracked (`18` §5.1). Otherwise it is `FOREIGN_TRANSACTION_ARTEFACT`: reported and ignored.

| Journal phase (honoured) | Action |
|---|---|
| `prepared`, `staged`, `verified-staged` | move `trust-tx/<TX>` to `trust-tx/abandoned/`; deregister |
| `swapped`, `migrated` | Evaluate the exchange-back target (`trust.prev`) through the restore pipeline (§2). The downgrade policy applies relative to both the lock-recorded identity and the VTS per-project record. If eligible: exchange back with union `state/` and `root/`. **The `overlay.prev` restore runs the computed-weakening check of `19` §9 against the current overlay. A non-empty list needs the `weakening` trust gate.** Otherwise leave `PARTIAL` and report. |
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
   - `gov kernel reinstall --source <S>`: S authenticates to the lock-recorded identity. Occupation entries are recreated.
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
| RR-2 | On a machine without a per-project record, an A2-delivered older eligible release is accepted as installed content. | Its content must be registered in the machine's effective TPS (E7), with floors joined. Governed use follows freshness: under OP-7 (a)–(c) an unanchored machine performs no governed mutation, and an anchored machine judges the release at its anchor epoch (revocations and minimum sequence known there). Under OP-7 (d) unanchored use is bounded only by the compiled TPS and is labelled `FRESHNESS_UNPROVEN`. |
| RR-3 | A3 deletes the per-project record or the VTS. | As RR-2 on that machine; `UNANCHORED` (RS-3). |
