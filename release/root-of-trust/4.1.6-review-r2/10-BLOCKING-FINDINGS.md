# Blocking findings (ranked)

| Severity | Count | IDs |
|---|---|---|
| CRITICAL | 0 | — |
| HIGH | 4 | R2-H1, R2-H2, R2-H3, R2-H4 |
| MEDIUM | 10 | R2-M1 … R2-M10 |
| LOW | 3 | R2-L1 … R2-L3 |

**Evidence classes:**
- **E** — executed or computed in `evidence/`.
- **C** — code reading of the 4.1.5 runtime, unchanged since `da9c851`. It shows how kernel content and records are
  consumed today, and revision 2 does not change the consumers named.
- **D** — design reading of the pack.

**No CRITICAL finding.** The anchor is non-circular:
- compiled root chain;
- purpose-bound DSSE statements over the full file map;
- single authentication boundary;
- lock as record.

Byte binding inside `gov` is proven by design (`03` §1). RV-H3 and RV-H4 are closed.

**Four HIGH findings block acceptance.** Each is the same class that rejected 4.1.3–4.1.5 and revision 1: a lower-trust
input producing a current, higher-trust fact.

---

## R2-H1 — HIGH — The non-downgradable floor covers 145 keys; the rest of the constitution still comes from whichever authentic eligible kernel is installed

**Statement.**
- `19` §4 registers floors for part of AUTHORITY_POLICY, SECURITY_POLICY, HUMAN_GATE_POLICY, TOOL_POLICY and
  POLICY_PRECEDENCE, plus invariant ids. Of 125 leaves in the files the pack itself calls constitutional floors (`01`
  AS-1), 64 are unfloored.
- The unfloored leaves include:
  - the role → authority-level map (`roles/ROLES.yaml`);
  - secret path and content patterns;
  - `agent_resolvable_when`;
  - `permission_classes` and `auto_install_conditions`;
  - state classes;
  - precedence `layers` and per-rule `exception_relaxable`;
  - invariant statements.
- Beyond AS-1, no floor or content registration covers `CHANGE_POLICY` gating, `MEMORY_POLICY` namespaces, schemas
  (AS-2), agent-facing content (AS-4) or the tool registry (AS-5).
- E7 and the producer check only registered floor keys. The only other barrier is `min_release_sequence`, whose raise is
  a manual owner action not tied to content change.
- Rollback, recovery and Git delivery therefore *can* restore weaker constitutional policy, contradicting:
  - G11;
  - D-0008 rule (6);
  - `19` §1: "They cannot restore weaker floors";
  - `19` §10.

**Evidence.**
- **E** `evidence/P1` part 1: the coverage table, derived exactly as `examples/make_example.py` derives TPS v1.
- **E** P1 part 2: all 145 floors hold on a kernel that raises `backend-engineer` to L4, disables secret patterns and
  widens `agent_resolvable_when`.
- **E** P1 part 3, 4.1.5 binary, both kernels `verified: true`:

  | Test | Genuine kernel | Unfloored-only kernel |
  |---|---|---|
  | L1 `resume` (floor L4 unchanged) | `AUTHORITY_DENIED` | succeeds |
  | AWS credential file after `rebuild-memory` | excluded | indexed and retrievable |
  | L3 agent answers an R5 irreversible gate | denied | succeeds |

- **C** `authority.rs:25-35` (actor level from ROLES), `security/secrets.rs:51-79`, `gates.rs:226-240`,
  `update.rs:109-176` (agent answers accepted), `policy.rs:192-255` with `policy_precedence.rs:160-192` (exceptions
  relax keys marked relaxable).

**Failure scenarios.**
1. **Future loosening.** 4.1.8 tightens `migration-executor` from L3 to L2 after an incident. A2 commits the eligible
   4.1.7 set. Fresh clones use it without any gate. On machines with a VTS record, E10 refuses until a "downgrade gate",
   which A2 also commits (R2-M1). The authority floor holds, but the role that should no longer reach it does.
2. **Stolen `release-final` key (threshold 1) plus A2.** The thief signs a final with sequence above every minimum.
   Floors hold, and ROLES maps every role to L5. A2 commits the installed set. Every clone uses it as policy root with
   `verified: true`, and no gate exists at use. The install-authority floor (RV-M3) is bypassed through actor levels.

**Why HIGH.** It is RV-H1 reduced in scope but not closed. An authentic (plus sequence-eligible) release still confers
weaker authority, secret handling and gate policy, with persistent harm and a clean verdict.

**Correction:** CD2-1. **Acceptance:** RV2-A01…A08.

---

## R2-H2 — HIGH — For a verifier without retained state, currency is chosen by the repository writer and bounded only by the binary's build date; the stated bounds do not hold

**Statement.**
- Knowledge K on a new machine, ephemeral CI runner or wiped VTS is T0 plus whatever genuine statements remain in the
  repository.
- A2 removes the Project Trust Record, and swaps the installed release for an older authentic one or one signed by a
  later-removed key.
- The verifier then uses:
  - the compiled TPS (`min_release_sequence`, floors, `min_binary_version`);
  - the compiled TSS (revocations);
  - the compiled root.
- Git-delivered installations are evaluated at use with **no gate** (`19` §6 E9 applies at ingress only). Ingress gates
  are repository records (R2-M1).
- The verdict reads `CURRENT_KNOWN(n)` and `verified: true`. OP-5 age is measured from the fresh VTS, so nothing warns.
- The architecture presents this residual as bounded:
  - RS-1: "cannot produce a relaxation (mode A)";
  - RR-2: "Floors and install authority are unaffected";
  - `19` §10: "at least as strong as the newest registered ones";
  - `22` §8.

  In reality the only bound is the compiled T0 of whatever binary runs. Its age is unbounded, and the lever to retire it
  (`min_binary_version`) travels through the stripped channel.
- The compromise playbooks (`05` §9: remove key, revoke, raise `min_release_sequence`) never reach these verifiers
  except through a new binary.

**Evidence.**
- **E** `evidence/P4-B5`:
  - honest project: TPS 3, floor 5, `min_binary_version` 4.1.8, older release ineligible;
  - after the A2 swap, on a verifier with a TPS v1 binary: TPS 1, floor 4, `min_binary_version` 4.1.6, the revoked older
    release eligible, `CURRENT_KNOWN(1)`, no gate at use.
- **E** `evidence/P2`: A2 edits `spec/decisions/HDG-0001.yaml` to an answered, presented state. The victim's
  `update --apply --approve` installs 4.1.5 (control: `applied: false`).
- **D** `17` §7, §15, `19` §6, `20` §9–§10, `03` §3, `15` rule (18).

**Failure scenario.**
1. A security-relevant kernel defect in 4.1.7 leads to TPS v3: `min_release_sequence` above 4.1.7, a raised floor,
   `min_binary_version` 4.1.8, and a revocation of 4.1.7.
2. A malicious collaborator or agent with commit rights reinstates the 4.1.7 set and removes `governance/trust/state/`.
3. Every CI job whose pinned `gov` predates TPS v3 runs governance checks and agent mutations against 4.1.7 as a
   verified, current policy root, until someone upgrades the binary.

**Why HIGH.** It reopens RV-H2 scenario 3 (revocation stripping by A2) for the verifier class most likely to enforce
governance automatically. The architecture claims it as resolved with a bounded residual, which is false.

**Correction:** CD2-2 (with CD2-5). **Acceptance:** RV2-A09…A12.

---

## R2-H3 — HIGH — The trusted computing base is authenticated by a single threshold-1 `release-final` signature with no attestation, certification, gate or T0 binding

**Statement.**
- `artifact-final` statements belong to the `release-final` purpose (`05` §2, default threshold 1).
- Subsequent binaries are accepted by `gov trust verify-artifact` on that statement alone (`06` §2 steps 5a, 6;
  R-BOOT-4).
- The artifact schema carries no compiled-T0 identity: root, TPS or TSS version or digest, historical registry digest,
  embedded release digest. The "root chain ≥ VTS high-water" rule of `06` §2 step 6 therefore cannot be enforced.
- No certification or attestation can bind a binary: certification carries only `release_statement_digest`.
- `05` §1 and `21` OP-2 describe `release-final` theft as bounded by floors, gates and certification. A forged binary
  bypasses all of them.
- Under OP-4 "no", the everyday candidate key gains the same power.

**Evidence.** **D** `05` §1–§2, `06` §2, `07` §4, `schemas/artifact-statement.schema.json`, `09` R-BOOT-4, `01` TH-22,
RK-11.

**Failure scenario.** A7 steals the `release-final` token and A5 controls the release host. A malicious `gov` compiled
with an attacker-chosen TPS, no revocations and permissive enforcement is published with a genuine-key artifact
statement. Operators verify it with the documented command and install it. Every project those operators touch is
governed by attacker code reporting `verified: true`.

**Why HIGH.** It is a purpose-separation failure at the top of the chain. The key with the lowest threshold and the
highest use carries TCB authority, and the pack's blast-radius statement is materially wrong.

**Correction:** CD2-3. **Acceptance:** RV2-A27…A29.

---

## R2-H4 — HIGH — The trust-format boundary does not bound pre-RoT binaries: routine exempt remedies rewrite a RoT-1 project, delete project-owned strengthening that no RoT-1 remedy restores, and report the result verified

**Statement.**
- The boundary (`13` §3) relies on sentinels read *after* old binaries act.
- On a RoT-1 project, three commands succeed: 4.1.5 `update --rollback`, 4.1.5 `init --force` and 4.1.2
  `update --rollback`. Each overwrites the kernel, the lock and `governance/project/` from a legacy snapshot or
  templates. The old binary then reports `verified: true` (4.1.5) or `kernel verify` ok (4.1.2) and serves restricted
  material.
- 4.1.5 `kernel reinstall` and 4.1.2 `init --force` write before failing. 4.1.2 runs governed mutations.
- The overlay is not protected, signed or recorded. RoT-1 remedies write only Protected Paths, so the deleted
  classification is neither restored nor reported.
- LC-1 ("availability impact only") and LC-2 ("RoT-1 cannot change their behaviour through data") are false.
- A layout that occupies the legacy kernel and lock paths with inert non-directory and non-file entries (V3) makes every
  tested command of both binaries refuse before any write.

**Evidence.**
- **E** `evidence/P3` matrix: 48 runs across layouts V0, V1 and V3 with the real 4.1.5 and 4.1.2 binaries.
- **E** `evidence/P3b` attribution control.
- **C** `kernel_trust.rs:31-43` (exempt remedies), `update.rs:348-420`, `init.rs:43-82, 217-240`, `kernel.rs:215-217`.

**Failure scenario.**
1. During migration a teammate still on 4.1.5 hits a problem and runs the documented `gov update --rollback`.
2. Their tool reports success and `verified: true`.
3. The team's restricted classifications added since the 4.1.4→4.1.5 update are gone.
4. Colleagues on 4.1.6 see `KERNEL_TAMPERED`, run the documented `gov kernel reinstall`, return to green, and index the
   now-unclassified material.

**Why HIGH.** Silent, persistent loss of a security control across the boundary that rule (12) exists to protect. No
attacker is needed, and a feasible design removes it.

**Correction:** CD2-4. **Acceptance:** RV2-A31…A36.

---

## MEDIUM

| ID | Finding | Evidence | Correction | Acceptance |
|---|---|---|---|---|
| **R2-M1** | **Gate, decision and exception records are A2/A3-writable data, yet they authorise production installs, downgrades (E9, `20` §4–§5), computed weakenings (`19` §9), HINT_MISMATCH (`17` §7), floor-lowering acceptance (`19` §10.6) and exceptions.** This contradicts rule (18) and `03` §3, which claims authorisation "against A1/A3/A5". A3 or a plugin can write the record, or run `gov decide` with a caller-declared role. `is_answered_yes` ignores `by_kind`. | E P2; E P1c; C `gates.rs:212-318`, `records.rs:53`, `capabilities/host.rs:175-190` | CD2-5 | RV2-A13, A14, A03, A04 |
| **R2-M2** | **Trust-state minimums are asserted by non-trust-state purposes and by unresolvable references.** S7 takes unbounded `trust_references` and `issued_under` values from release, candidate and certification statements. Revoking the statement does not clear it. STALE has no override at ingress, so security updates are blocked until root rotation. A trust-state key can make every honest successor a REGRESSION, refusing governed mutations at use. This contradicts the `05` §1 blast radius. | E P4-B1, P4-B4 | CD2-6 | RV2-A15, A16 |
| **R2-M3** | **The certification key alone lifts sticky WITHDRAWN/REJECTED** via a higher, unreferenced, unattested sequence (S5). Contradicts MS-2 and `17` §3. | E P4-B2 | CD2-7 | RV2-A17 |
| **R2-M4** | **Trust-state equivocation is undefined.** Same-sequence forks are both admissible, "highest admissible" is ambiguous, and the hash chain is checked only when the predecessor is present. | E P4-B3 | CD2-8 | RV2-A18, A19 |
| **R2-M5** | **Floor lowering is gated on the arriving TPS's declared `lowers[]`,** so a lowering across a skipped version is silent. `rule_mode_at_least` has no order over non-comparable modes. | E P4-B6; D `19` §4, §10 | CD2-9 | RV2-A20 |
| **R2-M6** | **Separation constraints are incomplete.** KS-1…KS-7 never separate `trust-state` from `certification-status` or `verification-attestation`, and the permitted-sharing list is not a compiled whitelist. The OP-2 matrix allows one token to hold certification, revocation and trust-state. | D `05` §3, `21` OP-2 | CD2-10 | RV2-A30 |
| **R2-M7** | **Long-lived processes keep one snapshot for their lifetime** (`18` §6 step 8). Units of work never compare the snapshot CI with the installed identity or re-evaluate negative facts, so updates, TPS raises and `refuse_operation` revocations do not apply. VR-1 has no "next process". The planned MCP server is registered (`cli/src/main.rs:234, 890`). | D; C | CD2-11 | RV2-A21 |
| **R2-M8** | **Agent-facing kernel content (AS-4) is consumed from disk outside verify-and-use.** Adapters point agents at `governance/kernel/`. VU-8 binds a CI stamp in a manifest that A2 can rewrite along with the adapter body. | C `framework/adapters/generic/template.md:4`, `adapters.rs` | CD2-12 | RV2-A22 |
| **R2-M9** | **Trust-record and recovery-state semantics are inconsistent.** Exchanging `governance/trust` drops PTR statements, contradicting R-RB-5 and RB-12 on other clones. `governance/.tx/` sits inside Git-tracked `governance/` with no exclusion, so a committed journal makes every clone `IN_TRANSACTION`. `overlay.prev` is restored without the computed-weakening check. | D `18` §4–§5, `20` §1, §5, `08` §2 | CD2-13 | RV2-A24…A26 |
| **R2-M10** | **The acceptance plan would not detect R2-H1…H4 or R2-M1…M9.** Documented-residual variants have no pass criterion. RT-50 and RT-72 expectations are the architect's own evidence. [FS] evidence comes from builder instrumentation. | D `12`; `07` | CD2-14 | all RV2-A* |

## LOW

| ID | Finding | Correction |
|---|---|---|
| **R2-L1** | The verdict label `CURRENT_KNOWN(n)` and the OP-5 age warning (measured from the VTS's own last acceptance) present unproven freshness as current on fresh verifiers. | CD2-2 |
| **R2-L2** | Staged and installed files with `st_nlink > 1` are accepted; a hard-link write after read-back is caught only after the exchange (VU-6). | CD2-11 |
| **R2-L3** | Evidence and record hygiene. `evidence/F1` writes `trust/FORMAT` as `rot-1\n` rather than the `08` §2 JSON, omits lock `kernel.*`, and ran one destructive command. `22` marks RV-M4 resolved on that basis. | CD2-4, CD2-14 |
