# HO-0020 — Handoff to independent reviewer B (trust and security), RoT-1 revision 7

| Field | Value |
|---|---|
| Handoff | HO-0020 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh independent trust and security reviewer, run `AR-0020` (role `rot-reviewer-trust-security`) |
| Completed stage | RoT-1 revision 7 authored by architect run `AR-0019` |
| Architecture under review | `release/root-of-trust/4.1.6/`, `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml`, `docs/DECISIONS.md` at commit **`d07d200ac08a52c45071d33074e20cc62fbcc26e`** |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r7-review-b` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/review-r7-b` |
| Your output directory | `release/root-of-trust/4.1.6-review-r7/B-trust-security/` |

You work in parallel with reviewer C (compatibility and transactions). You must not see C's work, and C must not see
yours. A separate synthesis reviewer will consume both reports and issue the architecture verdict. **You do not issue
`ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` or `…_REJECTED`.**

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 7 (under review) | as above | `d07d200ac08a52c45071d33074e20cc62fbcc26e` |
| Revision 6 (rejected) | same paths | `4106885dadebac55596067a2586cf4d3097fc025` (`git diff 4106885dadebac55596067a2586cf4d3097fc025 d07d200ac08a52c45071d33074e20cc62fbcc26e -- release/root-of-trust/4.1.6 spec docs/DECISIONS.md`) |
| Consolidated review of revision 6 (synthesis adjudication governs over its panel) | `release/root-of-trust/4.1.6-review-r6/` (all files and evidence) | `ab6b1f8fab5f9f54261a01e5a0df431a13e9ddcd` |
| Earlier reviews | `release/root-of-trust/4.1.6-review*/` | in history |
| Decisions | `spec/decisions/D-0007.yaml` (ACTIVE); D-0008 and ARCH-0002 (PROPOSED) | at `d07d200ac08a52c45071d33074e20cc62fbcc26e` |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `release/releases/4.1.2`–`4.1.5` | at `d07d200ac08a52c45071d33074e20cc62fbcc26e` (unchanged since 4.1.5 `da9c851`) |
| Real legacy binaries | `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}` | sha256 in `release/orchestration/phase-1/ORCHESTRATOR_STATE.yaml` `infrastructure` |

The architect's response matrix (`22`) and the pack's own evidence are **claims** to be tested. They are not findings.
Re-derive or re-execute anything you rely on.

## 2. Attack surface (Phase 1 protocol §5 B)

Attack at least:
- root trust;
- constitutional floors;
- key hierarchy;
- signature purpose;
- binary authenticity;
- replay and freshness;
- first-machine bootstrap;
- revocation;
- downgrade;
- offline operation;
- trust-state monotonicity.

The owner's binding requirements that revision 7 must satisfy are in `HO-0001` §3 (constitutional-floor closure,
new-machine bootstrap, binary and root authenticity) and §4 (forward compatibility). Judge each as a **class**: an
instance fix that leaves the class open is not a closure.

The recurring rejection class is: **a lower-trust input yielding a current, higher-trust fact** (D-0007).

## 2b. Owner design requirements and the concrete certified profile

- **The profile under review.** Revision 7 implements one concrete certified production profile per the product
  owner's binding design requirements in `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`. The
  verbatim text governs; the `.yaml` beside it is a derived index. These are design inputs, not approval of D-0008.
- **Attack the configuration as specified**, including its real combinations and its exclusions. An excluded mode that
  remains reachable, accepted by a schema or verifier, or selectable by a Trust Policy is a finding. The excluded modes
  are:
  - a witness service;
  - helper-machine or script admission;
  - OP-13 (c) "either suffices";
  - a platform package-signing root;
  - mode B;
  - clock or grace-period trust;
  - unanchored governed mutation.
- **Check conformance.** Any place where the architecture deviates from, weakens, or silently reinterprets an owner
  selection is a finding.
- **Do not reopen owner parameters** merely because another design is possible. If an attack shows a selected parameter
  is insufficient, or contradicts a security invariant, report the precise consequence. Then classify whether closing it
  needs an engineering correction or a genuinely new owner trade-off.
- **Check D-0008's state.** D-0008 must remain `status: PROVISIONAL`, `proposal_state: PROPOSED`,
  `human_approved: false` and `in_effect: false`, and D-0007 must remain ACTIVE. Any other state is a finding.

## 3. Required work

1. **Prior findings.** Determine the status of blocking classes BC6-1, BC6-2, BC6-3 and BC6-4 as classes; RV6-H1, RV6-H2, RV6-H3; RV6-M1, RV6-M2 and the trust parts of RV6-M6; RV6-L1…L5 and RV6-L12; RV6-I1, RV6-I2; conformance of the concrete profile CP-1 with OWNER-DESIGN-REQUIREMENTS-0001; and the architect-surfaced owner-parameter conflicts OT-1 (offline media versus the 24-hour freshness bound) and OT-2 (OP-10 (b) not evidenced for the current compiler):
   `CLOSED`, `NARROWED` or `OPEN`, each with evidence.
2. **Re-execute prior probes.** Run the prior review's decisive probes (review r6 `B-trust-security` RV6-B-A01…A16, the `D-synthesis` RV6-D probes within trust/security scope, and the architect's FA7, CS7, CUR7, ADM7, ENV7, DA04r7, DA05r7, DA06r7, DA09r7, BA11r7, BA12r7, PROF7, `register_check` and `statements_check` evidence as claims) against revision 7
   as written. You may copy scripts into your evidence directory and adapt them, with attribution. Never edit any
   `release/root-of-trust/4.1.6-review*/` directory. Independently check the architect's re-run claims.
3. **Constitutional surface.**
   - Run the architect's coverage checker yourself.
   - Construct kernels that change only leaves the architect classified as non-security or content-registered, and show
     whether any of them yields weaker authority, secret handling, gate, plugin or tool, export, override, install or
     exception policy.
   - Inject an unknown constitutional key and a new constitutional file.
4. **Freshness bootstrap.** Model every machine class of `HO-0001` §3.2 under a repository and transport adversary, and
   under each OP-7 option. Report what each class can be made to accept as current.
5. **Binary and TCB.** Try to authenticate a malicious binary, or an older binary, with each key or key subset below the
   declared thresholds, including OP-4 variants. Check that the chain is non-circular.
6. **Author new held-out attacks** `RV7-B-A01…` that are not in the pack's acceptance plan. Execute or compute each
   one where feasible.
7. **Residuals.** Judge every residual the architect declares against explicit acceptance criteria. Documentation alone
   is not a bound.

## 4. Severity and blocking

| Severity | Meaning |
|---|---|
| CRITICAL / HIGH | **Blocking.** A lower-trust input can yield a current higher-trust fact, security control loss, or TCB compromise below the declared threshold. |
| MEDIUM | **Blocking** only when it cannot be carried as a bound, testable implementation requirement without an architecture change. Otherwise list it as a carried requirement with a precise acceptance test. |
| LOW | not blocking |

## 5. Deliverables (in your output directory only)

- `00-REPORT.md`: scope, method, prior-finding status table, summary, verdict `BLOCKING_FINDINGS_PRESENT` or `NO_BLOCKING_FINDINGS`.
- `01-FINDINGS.md`: each finding with statement, evidence class (executed, computed, code, design), failure scenario, severity and the correction direction (architectural only).
- `02-HELDOUT-ATTACKS.md`: your RV7-B register (attack, adversary, expected secure outcome, revision as written, finding).
- `03-RESIDUALS.md`
- `04-CARRIED-REQUIREMENTS.md`: non-blocking items that the implementation and verifier must test.
- `evidence/`: scripts, outputs, `REVIEWED-CONTENT-DIGESTS.txt` (sha256 of every reviewed file at `d07d200ac08a52c45071d33074e20cc62fbcc26e`), README.

Then write `release/orchestration/phase-1/AGENT_RUNS/AR-0020.report.yaml` (schema:
`AGENT_RUNS/README.md`).

## 6. Constraints

- **Independence.**
  - You did not author any RoT-1 revision or prior review.
  - Do not read reviewer C's output, other branches or other worktrees (`git branch -a`, `git log --all`, other scratch
    directories).
  - Under `release/orchestration/`, read only this handoff, `HO-0001`, `AGENT_RUNS/README.md` and `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` (with its `.yaml` index).
- **Writes.** Only your output directory and your report file. Never modify product source, the pack, D-0008,
  ARCH-0002, prior reviews, verification evidence or released payloads.
- **Probes.** Scratch only; never the canonical checkout `/home/usain/Dynamic-Agentic-Engineering-OS`. Strip `GOV_*`
  from child environments and point `GOV_KERNEL_CACHE` into scratch. Scratch root:
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0020/`.
- **No transcripts.** Never read, list or search session or agent transcripts or task-output files: anything under `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/*/tasks/` or `~/.claude/projects/`. They hold other roles' work.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Commits.** Commit the output directory first:
  `Independent trust/security review (B) of RoT-1 revision 7 (d07d200): <verdict>`. Then commit your
  report separately. End each message with `Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>`.
  Leave the worktree clean.

## 7. Forbidden assumptions

- That the architect's evidence or response matrix is correct.
- That the CD2 correction delta defines acceptance.
- That reviewer C covers anything you skip.
- That a stateless machine can know unseen metadata, or that attacker-selected stale signed state may become current.
- That a repository-delivered record can authorise a trust decision.
