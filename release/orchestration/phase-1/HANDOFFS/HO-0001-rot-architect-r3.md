# HO-0001 — Handoff to the RoT-1 revision-3 architect

| Field | Value |
|---|---|
| Handoff | HO-0001 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh Root-of-Trust architect, run `AR-0001` |
| Completed stage | Independent review of RoT-1 revision 2: `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (`e5a6b8a`) |
| Integration branch | `release/4.1.6-rc1` |
| Your base | the commit that adds this file (`git log -1` in your worktree) |
| Your branch / worktree | `phase1/rot1-r3-architect` at `<orchestrator scratch>/wt/arch-r3` |

Reconstruct your task from this file and the repository. Read the review files themselves: this handoff routes you to
them and does not replace them.

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Rejected release baseline 4.1.5 | `release/4.1.5-rc1`, tag `v4.1.5-rc1` | `da9c8518d3fddba6f37bafb4d046ca313335ec1f` |
| 4.1.5 re-verification (rejected, V-H3) | `release/verification/4.1.5/` | `c8a138f` |
| RoT-1 revision 1 | `release/root-of-trust/4.1.6/` at that commit | `676dfcedec84a2436c1f4e46d5dcd137f7eb655e` |
| Review of revision 1 | `release/root-of-trust/4.1.6-review/` | `1c6027c18822543d6927d9906b9efa4f7a54ed4e` |
| RoT-1 revision 2 (the design you amend) | `release/root-of-trust/4.1.6/` (00–22, `schemas/`, `examples/`, `evidence/`) | `d37b05cc83741821aad023e5845ecfeb1a396f4c` |
| Review of revision 2 (**read in full**) | `release/root-of-trust/4.1.6-review-r2/`: `00` report, `01`–`07` falsification, `08` held-out RV2-A01…A36, `09` residuals, `10` findings, `11` correction delta, `evidence/` P1–P4 | `e5a6b8aa39d2a36311489418506d911df2587722`; reviewed digests in `evidence/REVIEWED-CONTENT-DIGESTS.txt` |
| Decisions | `spec/decisions/D-0007.yaml` (ACTIVE, trust classes); `spec/decisions/D-0008.yaml` and `spec/architecture/ARCH-0002.yaml` (PROPOSED revision 2, file status PROVISIONAL); `docs/DECISIONS.md` | as at base |
| Implementation the design governs | `runtime/`, `cli/`, `framework/` (kernel), `migrations/`, `capabilities/`, released payloads `release/releases/4.1.2`–`4.1.5` | as at base |
| Governing protocols | repository-root `*.md` protocols | as at base |

## 2. Unresolved findings you must close as classes

| Severity | IDs | Full statements |
|---|---|---|
| HIGH | R2-H1 constitutional floor coverage; R2-H2 stateless-verifier currency; R2-H3 TCB/binary authenticated by threshold-1 `release-final`; R2-H4 pre-RoT binaries damage RoT-1 projects | `10-BLOCKING-FINDINGS.md` |
| MEDIUM | R2-M1 … R2-M10 | `10-BLOCKING-FINDINGS.md` |
| LOW | R2-L1 … R2-L3 | `10-BLOCKING-FINDINGS.md` |

`11-CORRECTION-DELTA.md` (CD2-0…CD2-14) is the prior reviewer's proposed direction. It is **not** the acceptance
criterion. The next reviewers will attack each class with new held-out attacks, not tick CD items. Where you choose a
different mechanism, show that it closes the class and say so in the response matrix.

The same class has rejected 4.1.3, 4.1.4, 4.1.5, revision 1 and revision 2: **a lower-trust input yielding a current,
higher-trust fact**. Treat every new mechanism as a candidate instance of that class and attack it yourself before
handing it on.

## 3. Owner requirements for revision 3 (Phase 1 protocol §6, binding)

### 3.1 Constitutional-floor closure (R2-H1)

Do not maintain an ad-hoc list of selected keys. Design a mechanism in which every security- or authority-critical
constitutional field is classified by machine-readable floor semantics. Require:
- a complete constitutional key inventory;
- default-deny handling of unknown new constitutional keys;
- an explicit floor mode for each mutable constitutional field;
- a coverage check that fails the release if a constitutional field has no trust-floor semantics;
- schema evolution that cannot silently introduce an unfloored constitutional setting.

Test at least:
- the role→authority map;
- sensitivity and indexing exclusions;
- irreversible Human Gate authority;
- the plugin and tool permission floor;
- outbound and export controls;
- project override controls;
- install and update authority;
- exception authority;
- a future unknown constitutional field.

### 3.2 New-machine trust bootstrap (R2-H2)

Explicitly solve each of:
- first install on a machine;
- a clean CI runner;
- a machine restored from backup;
- a machine with an old trust epoch;
- a machine with no trust epoch;
- two machines at different epochs;
- an offline machine returning after a long absence.

Distinguish safety from freshness. An attacker controlling transport or the repository must not be able to select an
old signed trust state and thereby create a current trusted fact. Do not pretend a machine can know about metadata it has
never received. Instead define exactly:
- what it may safely do without freshness proof;
- what becomes gated or read-only;
- what requires an online or freshness witness, if one is adopted;
- what monotonic state is persisted locally;
- how OP-7 affects all of the above.

Also cover signed-state replay, and gate records supplied from repository state. The reviewer proposed OP-7. **Do not
decide OP-7, or any OP, for the owner.** Present options with consequences. A proposed default may be stated, labelled
as a proposal.

### 3.3 Binary and root authenticity (R2-H3)

The binary contains trust authority, so its authentication must match. A single lower-threshold release key must not be
able to mint a malicious binary with arbitrary compiled roots or floors. Evaluate:
- a threshold root signature;
- a separate binary or root-bundle attestation;
- certification binding;
- reproducible-build or build-provenance evidence;
- a compiled trust-state digest;
- a binary trust-policy digest;
- multi-signature requirements.

Protect:
- the binary;
- its compiled trust roots;
- compiled minimum floors;
- compiled trust-policy identity;
- the compiled historical-release set;
- compiled trust-state and bootstrap rules.

Ordinary project installs need not understand build infrastructure internals, but the trust chain must be non-circular.

### 3.4 Legacy-binary damage containment (R2-H4)

Make new-format projects mechanically hostile to destructive pre-RoT commands where possible. Evaluate the review's
successful path-occupation defence (P3 layout V3). Protect:
- kernel paths;
- legacy lock paths;
- trust paths;
- rollback paths;
- reinstall paths;
- init-force paths;
- migration paths.

The defence must not depend on old binaries voluntarily understanding RoT-1. Backward safety must be solved as a class:
a pre-RoT binary must not be able to silently mutate the new kernel or trust state into a state it then treats as valid.

## 4. Forward-compatibility constraint (from later Phase 1 stages)

The 4.1.6 candidate will also add:
- an owner-supplied Capability Acceptance Contract: a hash-bound normative Markdown source plus a compiled executable
  YAML, schema and evidence map;
- Gate W artifact-flow and consumption-integrity policy: task input manifests, consumption receipts, lineage;
- a G0–G6 governance health scheduler.

Do not design these. The constitutional-surface classification and default-deny rule must be able to classify such new
constitutional files and keys without another architecture revision.

## 5. Deliverables

1. **Revision 3 of the pack**, amending `release/root-of-trust/4.1.6/` in place (Git keeps revision 2 at `d37b05c`).
   - Update every affected file, at least 01, 02, 03, 05, 06, 07, 08, 09, 11, 12, 13, 14, 16, 17, 18, 19, 20 and 21.
     In 21, add OP-7 and restate OP-2, OP-3 and OP-4 as review r2 §8 requires.
   - Update 22 as a response matrix over R2-H1…R2-L3 and every §3 requirement: change, file, evidence. No "resolved" may
     rest on untested evidence.
   - Add new files and schemas as needed.
2. **A machine-readable constitutional surface inventory** classifying every constitutional leaf of the current kernel
   (`framework/`), with a coverage checker that:
   - exits non-zero when any leaf lacks floor semantics;
   - demonstrates that an injected unknown constitutional key fails.
3. **D-0008 and ARCH-0002 as PROPOSED revision 3.**
   - Keep file status `PROVISIONAL`, and keep the title's "PROPOSED … not active, not approved" wording.
   - Update the `docs/DECISIONS.md` rows for these two only.
   - Include the rule changes the class closures require. The review's (6), (7), (9), (12), (18) and new (19)/(20) are
     the minimum.
4. **Architect evidence** under `release/root-of-trust/4.1.6/evidence/`, meeting the review r2 §11 re-review entry
   criteria:
   - **P1** re-derived against revision-3 floor and registration semantics. Every harm scenario (authority, secrets, R5
     gate) must flip, together with the §3.1 test list.
   - **P3** full pre-RoT command-register matrix for the real 4.1.2, 4.1.3, 4.1.4 and 4.1.5 binaries on the revision-3
     layout, run with a legacy update snapshot and a project restricted-classification present.
     - Property: no byte under `governance/`, `spec/` or any other protected path changes, shown by before/after tree
       digests.
     - Derive each binary's command register from its own CLI (`--help` recursion), not from a hand list.
   - **P4** reference model re-run against the revision-3 trust-state rules. Each B1–B6 must be flipped or removed by a
     design change. Add scenarios for the §3.2 machine list.
   - You may copy reviewer probe scripts into your evidence directory as starting points, with attribution. Never edit
     `release/root-of-trust/4.1.6-review*/`.
5. **Commits on your branch.**
   - Work product: `RoT-1 revision 3 root-of-trust architecture for 4.1.6 (architecture only; D-0008 PROPOSED, not approved)`.
   - Then your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0001.report.yaml` (schema in
     `AGENT_RUNS/README.md`), in a second commit.

## 6. Constraints

- **Architecture only.** Do not modify `runtime/`, `cli/`, `framework/`, `migrations/`, `tests/`, `fixtures/`,
  `capabilities/`, `Cargo.*`, `release/releases/**`, `release/verification/**`, `release/root-of-trust/4.1.6-review*/**`
  or D-0001…D-0007.
- **Allowed writes:**
  - `release/root-of-trust/4.1.6/**`;
  - `spec/decisions/D-0008.yaml`;
  - `spec/architecture/ARCH-0002.yaml`;
  - the D-0008 and ARCH-0002 rows of `docs/DECISIONS.md`;
  - your `AGENT_RUNS/AR-0001.report.yaml`.
- **Probe hygiene.**
  - Probes run only in scratch directories.
  - Never mutate the canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS` or any other worktree.
  - Strip `GOV_*` variables from child environments and point `GOV_KERNEL_CACHE` into scratch.
- **Do not claim acceptance.** D-0008 and ARCH-0002 must not be described as active, approved or accepted.
- **Stay in your branch.** Do not inspect other branches or worktrees; use only history reachable from your branch.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`. Move files aside or use fresh scratch directories.
- **Legacy binaries**, for read-only use: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}`.
  - 4.1.3 and 4.1.4 are being built by the orchestrator. If absent, build them yourself in your own scratch worktree
    from `26ab5b6` (`v4.1.3-rc1`) and `47d8394` (`v4.1.4-rc1`).
- **Toolchain:** `~/.cargo/bin/cargo` 1.98.1, Python 3.12 with PyYAML.

## 7. Forbidden assumptions

- That applying the CD2 text is sufficient, or that closing the demonstrated examples closes the class.
- That a stateless machine can know unseen metadata; or, conversely, that attacker-selected stale signed state may become
  a current fact.
- That a repository-delivered record can authorise a trust decision.
- That a pre-RoT binary reads any RoT-1 file before it acts.
- That any threshold-1 key's authenticity implies binary or TCB authenticity.
- That the prior reviewer's probe results transfer unchanged to revision 3. Re-run them.
- That this handoff summarises the review adequately. Read the review files.

## 8. Next roles

Three fresh reviewers will receive your committed revision and the review r2 evidence, but not your reasoning:
- **B**, trust and security;
- **C**, compatibility and transactions, running in parallel with B;
- an **architecture synthesis** reviewer, which will author further held-out attacks and issue the verdict.
