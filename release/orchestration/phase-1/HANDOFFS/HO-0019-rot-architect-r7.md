# HO-0019 — Handoff to the RoT-1 revision-7 architect (concrete certified profile)

| Field | Value |
|---|---|
| Handoff | HO-0019 |
| From | Phase 1 orchestrator (routing only; not an evidence source) |
| To | fresh Root-of-Trust architect, run `AR-0019` (role `rot-architect`) |
| Completed stages | revision 6 (`4106885dadebac55596067a2586cf4d3097fc025`); panel B (`512808695e8f3eb11187a8c70dc07e6783ad8395`) and C (`02bb90550342e8bb6d42ba636430ae3394d3a0f7`); synthesis `ROOT_OF_TRUST_ARCHITECTURE_REJECTED` (`ab6b1f8fab5f9f54261a01e5a0df431a13e9ddcd`) |
| Owner input | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md`, **binding** design requirements (verbatim text governs; `.yaml` is a derived index) |
| Integration branch | `release/4.1.6-rc1` |
| Your base | the commit that adds this file |
| Your branch / worktree | `phase1/rot1-r7-architect` at `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/wt/arch-r7` |

Reconstruct your task from this file and the repository. Read the review files and the owner requirements themselves: this
handoff routes you to them and does not replace them. You did not author revision 6, any review, or the owner requirements.

## 1. Authoritative inputs

| Input | Location | Identity |
|---|---|---|
| Revision 6 (the design you concretise) | `release/root-of-trust/4.1.6/` (00–34, `decision-register/`, `constitutional-surface/`, `schemas/`, `examples/`, `evidence/`), `spec/decisions/D-0008.yaml`, `spec/architecture/ARCH-0002.yaml` | `4106885dadebac55596067a2586cf4d3097fc025` |
| Review of revision 6 (**read in full**) | `release/root-of-trust/4.1.6-review-r6/`: `00-REVIEW-REPORT.md`, `10-BLOCKING-FINDINGS.md`, `11-CORRECTION-DELTA.md` or `11-IMPLEMENTATION-CONDITIONS.md`, `D-synthesis/`, `B-trust-security/`, `C-compat-transaction/` | synthesis `ab6b1f8fab5f9f54261a01e5a0df431a13e9ddcd`; B `512808695e8f3eb11187a8c70dc07e6783ad8395`; C `02bb90550342e8bb6d42ba636430ae3394d3a0f7` |
| **Owner design requirements (binding)** | `release/orchestration/phase-1/GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` and `.yaml` | at base |
| Owner requirements from the start of Phase 1 (binding) | `release/orchestration/phase-1/HANDOFFS/HO-0001-rot-architect-r3.md` §3–§4 | at base |
| Earlier reviews and escalation background | `release/root-of-trust/4.1.6-review*/`, `release/root-of-trust/4.1.6-alternatives-r5/` | Git history |
| Implementation the design governs | `runtime/`, `cli/`, `framework/`, `migrations/`, `capabilities/`, `release/releases/4.1.2`–`4.1.5` | unchanged since `da9c851` |

## 2. What revision 7 is

Revision 7 is a **concretisation**, not another option tree. The owner has selected the parameters. Your job is one
concrete certified production profile that closes every revision-6 finding as a class, with the owner's selections
applied exactly.

1. **The profile.** Build the single certified production profile:
   - D-0008 Option C / RoT-1, with OP-1…OP-16 exactly as selected;
   - the first-contact composer and signer requirement: root threshold 2-of-3 after independent reproduction and
     verification of the admitter, never the trust-state publisher;
   - the environment-manifest authority requirement: deterministic generation, authoritative only with agreeing
     reproducer evidence plus registration 2-of-3 over that exact identity;
   - the initial certified scope and its exclusions.
2. **Remove the option tree from the certified profile.**
   - Unused alternatives may stay documented as history, clearly marked as not production modes.
   - They must not remain as active modes, verifier-accepted schema values, compiled paths, Trust Policy fields that
     select them, or calculator branches presented as production choices.
   - Keep excluded paths out of the certified executable surface where practical, and make the certified verifier
     refuse them mechanically.
3. **Consequences for the concrete profile only.**
   - Recompute every consequence statement, minimal attack set and residual for the selected profile.
   - State the unavoidable core honestly, including OP-7 (a): a machine that never received newer metadata cannot know it.
4. **Every revision-6 finding, as a class**, inside the concrete profile. This covers the synthesis consolidated
   findings, all panel findings the synthesis confirmed, and every carried item.
   - A finding that concerned only an excluded option is recorded as *removed by exclusion*, with the enforcing
     mechanism named and tested.
5. **Owner parameters are not reopened.**
   - If a selected parameter is infeasible or contradicts a security invariant, do not silently change or weaken it.
   - State the conflict precisely in the pack as a genuine owner trade-off, with options and consequences, and complete
     the rest of the revision.
   - Another possible implementation is not a reason to reopen a parameter.
6. **Certified targets.**
   - Define a narrow initial certified target set of reproducible, static or self-contained targets.
   - Define the per-target certification criteria that OP-10 (b) and OP-16 (b) require, including provenance-based
     supplier and toolchain independence.
   - A target that does not meet them is labelled not certified; there is no fallback.
7. **Keep what the reviews confirmed sound**, and legacy containment: the R2-H4 property must stay at 0 violations.
8. **D-0008 package.**
   - Represent OP-1…OP-16, the first-contact composer and signer, the environment-manifest authority, the certified
     profile and its exclusions explicitly as owner design requirements, each citing OWNER-DESIGN-REQUIREMENTS-0001.
   - **Keep** `status: PROVISIONAL`, `proposal_state: PROPOSED`, `human_approved: false` and `in_effect: false`.
   - Set no chosen option or approval field.
   - Do not modify D-0007, which stays ACTIVE.

## 2b. Revision-6 synthesis routing mapped to the owner requirements (read `11-CORRECTION-DELTA.md` itself)

| Blocking class | Findings | Kind (per synthesis) | How the owner requirements apply (binding) |
|---|---|---|---|
| BC6-1 first-contact authority | RV6-H1 | engineering correction plus owner trade-off F1-a…F1-c | See note 1. |
| BC6-2 first-contact currency | RV6-H2 | engineering correction plus owner trade-off C-a…C-c | See note 2. |
| BC6-3 environment manifest | RV6-H3 | engineering correction | "Build-environment manifest author/signer": no single authoritative author; deterministic generation from measured inputs; authoritative only with agreeing independent reproducer evidence **and** registration 2-of-3 over that exact identity; independence by provenance, never by label. Combined with OP-16 (b), OP-10 (b) and OP-9 (b)+(d). |
| BC6-4 register and derived statements | RV6-M2, RV6-M1 | engineering correction | Register completeness over every input value, generated statements, and tests whose inputs are independent of the register, all for the **concrete profile only**. |

**Note 1 — BC6-1, first-contact authority.**
- **Owner requirements that apply:** "First-contact composer/signer", together with OP-13 (b) and OP-12 (a). The root
  2-of-3 approves the canonical first-contact trust base and admitter identity, after independent reproduction and
  verification. The ordinary trust-state publisher never composes first-contact material. OP-13 (c), platform package
  roots, and script or helper admission are excluded.
- **Apply the stricter reading.** No value that selects lineage, state or evaluator at first contact is composed or
  selected solely by the trust-state publisher, by an unadmitted binary, or by a package submitter.
- **If the state portion cannot be established first-hand** within the owner's selections, state the exact residual in
  the pack as an owner trade-off, using the synthesis F1 options as its consequences. Do not decide it.

**Note 2 — BC6-2, first-contact currency.**
- **Owner requirements that apply:**
  - OP-7 (a): production installation, update and rollback, including first admission as a production installation,
    need a fresh anchor no older than 24 h; CI admission or image anchors last at most 7 days; workstation anchors at
    most 90 days.
  - OP-13 (b) keeps a separately controlled offline media channel, so "state always read online" is not the owner's
    selection.
  - OP-14 (b): re-admission preserves and enforces the stored high-water, and never lowers revocations, root versions,
    trust-state sequence, minimum eligible release or security floors.
- **Apply** a per-path maximum age with these limits, and never state below held anchors, revocations or high-water.
- **Any residual** within the windows must be stated exactly. A genuinely new trade-off goes into the pack as an owner
  trade-off; it is not decided.

**Also binding from the review of revision 6:**
- the §6 carried items (RV6-M3…M6, RV6-L1…L12 and earlier carried items), each closed or carried with a named test in
  the concrete profile;
- the §7 re-review entry criteria;
- §3.1 and §3.4 of HO-0001 are SATISFIED: do not regress them, and keep the R2-H4 property at 0 violations;
- adjudication precedence: the synthesis governs where the panels disagree (for example, B's OP-11 claim was refuted,
  and B-M1 was re-rated LOW).

## 3. Deliverables

1. **Revision 7 of the pack**, amending `release/root-of-trust/4.1.6/` in place (Git keeps revision 6 at
   `4106885dadebac55596067a2586cf4d3097fc025`).
   - Include a profile document naming every selected parameter, every exclusion, and where each is enforced.
   - Update `21` to state the owner selections, and the historical alternatives as non-production.
   - Update `22` as a response matrix over every review-r6 finding and carried item: change, file, evidence. No
     "resolved" may rest on untested evidence.
   - Update the decision register and calculator to the concrete profile.
2. **D-0008 and ARCH-0002** as PROPOSED revision 7, with the D-0008 and ARCH-0002 rows of `docs/DECISIONS.md` updated.
3. **Evidence** under `release/root-of-trust/4.1.6/evidence/`:
   - every re-review entry criterion of the review of revision 6;
   - every blocking probe of reviews r5 and r6, re-run against the concrete profile;
   - a profile-conformance check showing that each excluded mode is refused or absent in the certified verifier and
     admitter model;
   - the legacy-containment matrix property still at 0 violations.
4. **Commits.**
   - Work product: `RoT-1 revision 7 root-of-trust architecture for 4.1.6 (concrete certified profile per owner design requirements; architecture only; D-0008 PROPOSED, not approved)`.
   - Then your typed report, `release/orchestration/phase-1/AGENT_RUNS/AR-0019.report.yaml` (schema in
     `AGENT_RUNS/README.md`), in a second commit.

## 4. Constraints

- **Architecture only.** Do not modify `runtime/`, `cli/`, `framework/`, `migrations/`, `tests/`, `fixtures/`,
  `capabilities/`, `Cargo.*`, `release/releases/**`, `release/verification/**`, `release/root-of-trust/4.1.6-review*/**`,
  `release/root-of-trust/4.1.6-alternatives-r5/**`, `release/orchestration/**` (except your report) or D-0001…D-0007.
- **Allowed writes:**
  - `release/root-of-trust/4.1.6/**`;
  - `spec/decisions/D-0008.yaml`;
  - `spec/architecture/ARCH-0002.yaml`;
  - the D-0008 and ARCH-0002 rows of `docs/DECISIONS.md`;
  - your report.
- **Probe hygiene.**
  - Probes run only in scratch (`/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0019/`).
  - Never mutate the canonical checkout or any other worktree.
  - Strip `GOV_*` from child environments and point `GOV_KERNEL_CACHE` into scratch.
  - Move `__pycache__` and other artefacts out of the worktree before committing.
  - Helper sessions, if any, work only in your scratch root under your specification and are disclosed.
- **Independence.** Under `release/orchestration/`, read only this handoff, `HO-0001`, `AGENT_RUNS/README.md` and
  `GATES/OWNER-DESIGN-REQUIREMENTS-0001.md` and `.yaml`. Do not inspect other branches or worktrees.
- **No transcripts.** Never read, list or search session or agent transcripts or task-output files: anything under
  `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/*/tasks/` or `~/.claude/projects/`. They hold other roles'
  work.
- **Keep your turn active** until every deliverable is committed. Wait for your own background probes yourself.
- **No forced deletes.** Avoid `rm -rf` and `rm -f`.
- **Legacy binaries**, for read-only use: `/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin/gov-4.1.{2,3,4,5}`.
- **Toolchain:** `~/.cargo/bin/cargo`, Python 3 with PyYAML.
- **No approval claims.** Never describe D-0008 or ARCH-0002 as active, approved, ratified or accepted.

## 5. Forbidden assumptions

- That the owner's selections are approval of D-0008. They are binding design inputs; ratification comes later.
- That documenting an excluded mode as "not selected" removes it. It must be absent or refused in the certified profile.
- That an option combination left reachable is harmless because no one is expected to choose it.
- That a stateless machine can know unseen metadata; or, conversely, that attacker-selected stale state may become current.
- That a repository-delivered record, or a file the governed account can write, can authorise a trust decision.
- That a label (distribution name, mirror, filename) establishes independence of a supplier or toolchain.
- That earlier probe results transfer unchanged to revision 7. Re-run them.

## 6. Next roles

Fresh reviewers B (trust and security) and C (compatibility and transactions) attack the concrete revision-7
configuration, including its real combinations and its exclusions. A fresh synthesis reviewer then issues the verdict.
Only after `ROOT_OF_TRUST_ARCHITECTURE_ACCEPTED` is the final D-0008 package presented to the owner for ratification.
