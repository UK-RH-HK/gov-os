# Output 20 — Rollback and recovery model

> **RoT-1 revision 2 — PROPOSED, pending a fresh independent review; not approved, not implemented.**
> New in revision 2. Addresses RV-H1 on restoring paths (CD-1), RV-M1 for adoption rollback, CIT and snapshot/cache
> restore (CD-5), and RV-M2 (CD-6).

## 1. Every restoring path

| ID | Path | Trigger | Revision 2 treatment |
|---|---|---|---|
| RB-1 | Automatic transaction rollback | failure after `swapped` in any install transaction | Exchange back to `.tx/<TX>/kernel.prev` and `trust.prev`, then normal use-time evaluation (`18` §6). The result may be `INELIGIBLE` if the previous identity is no longer eligible (e.g. the failed update's bundle raised the policy) — fail closed with a remedy. |
| RB-2 | `gov update --rollback` | operator | restore pipeline (§2) + downgrade policy (§4) |
| RB-3 | `gov kernel reinstall [--source]` | operator | restore pipeline; the target statement digest must equal the installed `release.dsse.json` digest; re-attestation (same payload digest, new envelope) allowed; never a downgrade |
| RB-4 | `gov recover` for an install journal | incomplete journal | §5 |
| RB-5 | `gov adopt rollback --batch 0`, or `gov recover` for an interrupted batch 0 | operator / interruption | §6: `install_tx::uninstall`; never a file restore |
| RB-6 | `gov adopt rollback --batch N` (N ≥ 1), or `gov recover` for batch N | operator / interruption | restores project files only; GovernedFs refuses any PPS target in the snapshot |
| RB-7 | `gov cit rollback`, or `gov recover` for an interrupted CIT | operator / interruption | GovernedFs refuses PPS targets; CIT planning already refuses them (§7) |
| RB-8 | Snapshot restore (any snapshot under `.governance-runtime/`) | only via RB-2 or RB-4 | snapshot is an untrusted source (T4), §3 |
| RB-9 | Cache restore | — | does not exist: no cache on any trust path (`18` §7) |
| RB-10 | Git checkout, revert or merge that changes protected paths (no `gov`) | repository | not a restore; evaluated at the next process like any state (`19`); downgrade detection §9 |
| RB-11 | Partial deletion of protected paths | accident or attacker | installation state `PARTIAL` (`18` §9) → §8 |
| RB-12 | “Rollback” of trust metadata | any | not possible through any restore. Accepted metadata is monotonic (`17` §11) and never removed by RB-1…RB-8. |

## 2. Common restore pipeline

```text
target (snapshot | bundle | release directory | .tx/<TX>/*.prev)
   ─► authenticate: secure reader, VerifiedBlobs, 04 V0–V11
   ─► eligibility under the CURRENT effective policy: 19 §6 (E1 historical never, E3 minimum sequence, E4 revoked, …)
   ─► downgrade policy (§4)
   ─► authority floor for rollback_apply (19 §8)
   ─► install transaction (18 §5)
   ─► post-commit snapshot equality + eligibility (18 VU-6)
```

No restoring path writes a byte into the Protected Path Set outside this pipeline.

## 3. Snapshots

- Update transactions create snapshots under `.governance-runtime/snapshots/<CI>/`. A snapshot contains:
  - the previous statement envelope bytes and previous trust-record statements;
  - content objects named by digest (`objects/<sha256>`);
  - the previous overlay and generated views (project state, not protected);
  - the trust-state sequence known when the snapshot was taken.
- **A snapshot carries no authority.** Restore reads it through the secure reader exactly like a bundle. Objects are
  digested against the snapshot's statement, the statement is verified under T0, and eligibility is evaluated under the
  **current** effective policy, never the policy at snapshot time.
- Tampered snapshot → `SNAPSHOT_UNAUTHENTICATED`. Authentic but ineligible → `SNAPSHOT_INELIGIBLE` (with the nested
  eligibility reason).

## 4. Downgrade policy

Relative to the installed eligible release:

| Target | Rule |
|---|---|
| Same statement digest | reinstall; no gate; authority `install_kernel` |
| Same payload digest, different envelope | re-attestation; no gate |
| Higher `release.sequence` | an update (`09` update rules) |
| Lower sequence, eligible | **downgrade**: Human Decision Gate bound to both statement digests, with the effective-floor comparison shown; authority `rollback_apply` from the floor |
| Lower sequence, below `eligibility.min_release_sequence` | refused `RELEASE_INELIGIBLE` (`below_min_release_sequence`); no gate can override |
| Revoked with `refuse_install` | refused `RELEASE_INELIGIBLE` (`revoked`); no override |
| Historical (legacy 4.1.2–4.1.5) identity | refused `RELEASE_INELIGIBLE` (`historical`); no override in production |
| Candidate, in a production project | refused `RELEASE_INELIGIBLE` (`candidate`) |
| Trust state `STALE` | refused `TRUST_STATE_STALE` until the missing metadata is supplied |

After a downgrade, floors are the effective floor (`19` §5). The older kernel contributes content but never weaker
constitutional values. The ledger entry records both CIs, the gate, the effective policy version and the floor
comparison. The ledger is evidence, never the rule.

## 5. Install-journal recovery (`gov recover`)

The journal and `.tx/<TX>/` directories are T4 (A3-writable). Recovery uses them only as hints about which candidate
states to evaluate:

| Journal phase | Action |
|---|---|
| none, unreadable, or not matching the `18` §5.1 layout | report `PARTIAL` or `IN_TRANSACTION`; offer remedies (§8) |
| `prepared`, `staged`, `verified-staged` | delete `.tx/<TX>` (no installed state was changed) |
| `swapped`, `migrated` | Evaluate the state that exchanging back would produce (`kernel.prev`, `trust.prev`) through the restore pipeline. The downgrade policy is applied relative to both the lock-recorded identity and the VTS per-project record (§9). If it authenticates, is eligible and matches the lock identity: exchange back and restore the overlay from `overlay.prev/`. Otherwise: leave the installation `PARTIAL` (fail closed) and report. |
| `committed` | Evaluate the installed state (`18` §6). If verified and eligible: mark `verified` and clean up. Otherwise evaluate `.prev` as above. |
| `verified` | clean up |

A forged journal that plants an older genuine release as `.prev` is therefore judged as a downgrade: refused if
ineligible, gated if eligible and lower. The lock identity check remains as an extra condition. This closes the
independent review's RV-A15 in both variants (A3 alone; A2 with A3).

## 6. Adoption batch 0 and its rollback

- Batch 0 is an install transaction with operation `adopt_install`.
- Rolling back batch 0 is `install_tx::uninstall`. Under the exclusive lock it moves `governance/kernel`,
  `governance/trust` and `governance/framework.lock` into `.tx/<TX>/removed/`, commits through the journal, then deletes
  them. The result is `ABSENT`, plus project files restored by the other batches' rollbacks through GovernedFs.
- Adoption snapshots never contain PPS paths. The planner already classifies `governance/kernel/**` and
  `governance/framework.lock` as `GOVERNANCE_CURRENT` (`runtime/src/migrations/classify.rs:154-158`). Revision 2 adds
  `governance/trust/**` and `governance/.tx/**`. The executor refuses PPS targets through GovernedFs as a second line.
- Batch rollback never restores protected paths from `.governance-runtime/migration/batch-0/` (the 4.1.5 behaviour at
  `runtime/src/migrations/executor.rs:304-350` is replaced).

## 7. CIT operations

- Planning (`cit propose`, `simulate`) refuses a manifest whose `write_file`, `move_file` (source or destination),
  `delete_file` or record operation resolves into the PPS → `CIT_PROTECTED_PATH`.
- Execution and CIT snapshot restore go through GovernedFs (second line).
- This replaces the single `glob_match("governance/kernel/**")` check on `write_file` (`runtime/src/cit/mod.rs:704`),
  which left `move_file`, `delete_file`, `framework.lock` and `governance/trust/` unguarded.

## 8. Partial-install recovery (fail closed)

When `18` §9 yields `PARTIAL`:

1. The policy root is the EmbeddedSnapshot joined with the effective floor. The on-disk kernel directory is never read
   for policy.
2. Mutations are refused (`INSTALL_STATE_PARTIAL`); read-only diagnostics are allowed.
3. Doctor D033 reports CRITICAL with the observed component set.
4. Remedies (authority from the floor, `19` §8):
   - `gov kernel reinstall --source <S>`: S must authenticate to the identity recorded in the lock when a lock exists,
     otherwise to any eligible release;
   - `gov update --apply --source <eligible release>`;
   - `gov recover`;
   - `gov init --force`, treated as reinstall or update.
5. Each remedy is an install transaction, with eligibility, downgrade policy and gates applied.

## 9. Git-delivered changes and use-time downgrade detection

- Git can deliver any combination of protected files. That is **evaluated, not restored**: authenticity, integrity,
  eligibility and floors as in `19`.
- The VTS keeps a per-project record keyed by (canonical repository path, `project_trust_id` from the lock). It holds the
  highest installed eligible `release.sequence` and CI seen on this machine, either by an install transaction or by a
  verified snapshot.
- A verified, eligible installed release whose sequence is **lower** than that record → `INELIGIBLE`
  (`downgrade_without_transaction`). Remedy: an authorised rollback (gate) or an update.
- A changed `project_trust_id` at a known path → `KERNEL_INELIGIBLE` (`project_trust_id_changed`), treated the same way.
- Without a VTS record (fresh machine) this downgrade cannot be detected, but the floor still holds (`19` §10). That is
  residual RR-2.

## 10. Residuals

| ID | Residual | Bound |
|---|---|---|
| RR-1 | Automatic rollback may leave an ineligible installation when the failed update's bundle raised the policy. | Fails closed; the remedy is completing an update to an eligible release. |
| RR-2 | On a machine without a VTS record, an A2-delivered older **eligible** release is accepted as installed content. | Floors and install authority are unaffected; the content is at or above `min_release_sequence`. |
| RR-3 | A3 can delete the VTS per-project record. | Same as RR-2, on that machine. |
