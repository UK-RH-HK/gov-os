# Owner decisions required — iteration 0 (P2-AR-0007)

Two genuine owner decisions remain: **OD-P2-01** (agent-role identity binding) and **OD-P2-02** (scope of the
unprovisioned-machine posture). Neither changes the iteration-0 verdict, and neither blocks the determined repair
requirements. Every other item the families flagged is already determined by accepted sources. Those items are ordinary
repair requirements (`repair-delta.md`), not owner decisions.

Test applied: an item is an owner decision only if the accepted sources, read in the frozen contract's precedence order
(§1: governing documents > Contract v3 > hash-bound views > active owner decisions/directives and accepted architecture >
frozen lifecycle contracts > candidate evidence > operator UI), do not determine what must become true. A capability the
contract requires but the product lacks is not an owner decision. Nor is the choice among designs that all meet a
determined requirement, unless the choice itself trades security, availability, cost or usability in a way the sources
leave open, needs owner-controlled material, or changes a boundary the owner set.

## A. Adjudication of the flagged items

| # | Flag (raised by) | Sources I read | Determined? | Result |
|---|---|---|---|---|
| 1a | Human-approval / human-presence channel (delta-r A0-L3-01, A0-L3-05; gamma-r A0-E1-04 human part) | Contract v3 L3:675-679, E1:363-366; framework §23, §50-§54 (§52 "A Human Decision Gate that exists only in a file is not considered presented"); D-0007 rule 2 ("'human_approved' … are facts of T1/T2 only; a T4/T5/T6 field carrying such a name is a request, recorded and ignored"; T5 = `--role`, `--by`), consequence 5; ARCH-0003 §8 ("Interactive trust changes use local administrator/Human Gate authority. Repository gate records remain requests … Environment variables, repository files and caller/model/plugin claims cannot manufacture trust or approval"); OWNER-DIRECTIVE-0004 ("Repository files, environment variables, caller fields, plugins and models cannot manufacture trust or Human Gate approval"); OWNER-DECISION-0006 req. 2 and its R1 implementation (`runtime/src/srr/breakglass.rs`, `srr/state.rs`: an owner-signed token verified against a `recovery` role delegated by the administrator-provisioned root, dropped into a machine-protected inbox); ARCH-0003 §7.1 ("The mechanism of the break-glass authority … is an R1 matter and is deliberately not fixed here"); ARCH-0001; docs/ARCHITECTURE.md §4.8 | **Yes** | Repair requirement **BC-P2-10**. Contract v3 (row 2) states the property with no deployment qualifier. OWNER-DIRECTIVE-0004 and ARCH-0003 §8 (row 4, owner-set) restate it for Human Gate approval, and D-0007 rule 2 already classes `--role`/`--by` as requests. The class of acceptable authority is already defined: an owner-controlled local or out-of-band mechanism that repository content, environment, caller fields, plugins or model output cannot manufacture (OWNER-DECISION-0006 req. 2), anchored in the administrator-provisioned boundary (ARCH-0003 §5, §8). The owner has already shown, for break-glass, that the mechanism inside that class is an implementation matter (ARCH-0003 §7.1). The product's own boundary text ("Deployments that need authenticated human answers must bind `gov decide` … adapter responsibility", ARCHITECTURE §4.8) is product documentation (row 6) and cannot relax row-2/row-4 sources. |
| 1b | Default acting role when none is declared (surfaced by delta-r A0-L3-01 "CLI defaults"; synthesis S0-E1-01) | framework §23 ("No spawned worker behaves as an orchestrator unless explicitly assigned that role"); Contract v3:364 | **Yes** | Repair requirement **BC-P2-08**. |
| 1c | Whether the OS itself must authenticate which **agent** holds an L0–L4 role (gamma-r A0-E1-04 agent part) | Contract v3 E1:364-366 (does not say how role assignment is established); framework §23 (requires explicit assignment, silent on who enforces it); D-0007 rule 2 (lists 'authority' among T1/T2 facts) versus D-0007 consequence 5 ("The acting role remains caller-declared (T5) and is a documented adapter boundary … the OS enforces what a role may do, not who holds the session"); OWNER-DIRECTIVE-0004 (keeps D-0007's "trust-direction, precedence, Human Gate, plugin, exception, integrity and typed-refusal rules" normative, silent on consequence 5); ARCH-0003 §1 (the support envelope trusts the local OS/administrator, silent on agent processes) | **No** | **OD-P2-01** below. |
| 2 | Plugin self-declaration (gamma-r A0-F4-03) | Contract v3 F4:426 ("Descriptor cannot authorise itself"), :430; ARCH-0003 §9 ("Descriptors cannot self-authorise", owner-adopted); D-0005 consequence 3 ("hand-declared descriptors keep working for roles at/above L2"; approved by the orchestrator "within delegated authority; product owner may supersede"); API-0001 governance clause; R1 AR31-N2 disposition ("deciding whether to ask is a form of authorising") | **Yes** | Repair requirement **BC-P2-39**. Contract v3 (row 2) and ARCH-0003 §9 (owner-adopted) fix the requirement. D-0005 is subordinate, and there is no conflict to resolve: at least one conforming design (enforce declared permissions at run time) leaves D-0005's allowance intact, and another (registration plus a specific gate for every executable that can exceed the non-elevated floor) narrows an agent-approved decision to conform with a higher source. Choosing between them is an implementation choice. A design that would add a new external dependency class (for example an OS sandbox) would need owner adoption before it is chosen. The requirement would not. |
| 3 | A2 post-install integrity anchor (alpha-r A0-A2-01) | Contract v3 A2:146 ("Installed-kernel verification detects post-install tampering"); D-0007 T1 definition and rule 1 ("when T1 cannot be authenticated, the embedded baseline is substituted explicitly and mutating operations fail closed"); OWNER-DIRECTIVE-0004 ("D-0007's manifest and framework.lock remain post-install integrity and release-pin records; they are not the first-install authenticity root"; D-0007 not amended without a transition record); ARCH-0003 §2 ("Evidence may connect domains by digest"), §3 step 9, §7 ("the authenticity of an installed local recovery path derives from this machine's own protected record of the release identity it previously verified and installed, never from the manifest, the lock, the repository or mutually consistent files"), §8 ("Ephemeral runners verify their pinned release … before privileged lifecycle work"), §11; frozen gate contract §7 (the D-0007 transition record is outside Phase 2) | **Yes** (except the unprovisioned sub-case) | Repair requirement **BC-P2-35**. Contract v3 requires detection. D-0007's manifest/lock stay integrity records, but nothing makes them the only ones, and rule 1 already provides for T1 that "cannot be authenticated". Comparing the installed payload with the machine's protected installed record strengthens detection without changing D-0007's text, and ARCH-0003 §7/§8 already use that record and require pinned-release verification on additional machines. On an unprovisioned machine there is no authenticated record to compare with, so that sub-case follows OD-P2-02. |
| 4 | Unprovisioned-machine posture (alpha-r A0-A2-02) | Contract v3 A2:143 ("authenticity is established before any privileged kernel material is staged or installed"), :147, :150 ("Bootstrap/dev/test trust modes cannot masquerade as certified production"), S5:938; OWNER-DIRECTIVE-0004 target chain ("trusted platform/admin bootstrap -> embedded or pre-installed offline root public keys -> …") and "cannot manufacture trust"; ARCH-0003 §3 steps 1-2, §5 (bootstrap authenticity from the platform/admin installation boundary), §8; OWNER-DECISION-0005 §1 ("an architecture role must not select this security-versus-availability posture on the owner's behalf") and §3 (offline first install out of scope); OWNER-DECISION-0007 §1 (machine-state path derivation kept); R1 report `release/verification/4.1.6-r1/00-VERIFICATION-REPORT.md` residual 1 ("Unprovisioned posture — ACCEPTED as an IMPLEMENTATION-CHOICE", on floor-evasion and honesty grounds) | **Partly** | Determined, and blocking now: an unauthenticated installation must never be presented as current, verified or certified, and must be visible to doctor and audit (**BC-P2-36**; A2:150; OWNER-DIRECTIVE-0004). Not determined: whether a machine without a trust anchor may still admit privileged kernel material, and on what terms. A2:143 read literally forbids it. A2:150 contemplates bootstrap/dev/test trust modes. The R1 verifier accepted the posture as an implementation choice. The owner's own precedent (OWNER-DECISION-0005 §1) reserves this class of security-versus-availability posture to the owner. See **OD-P2-02**. |
| 5 | Any further `owner_decision_required: true` in alpha-r | alpha-r `findings.yaml` (only A0-A2-01 and A0-A2-02 carry `true`) | — | Covered by rows 3 and 4. |

## B. Decisions required

### OD-P2-01 — Agent-role identity binding (L0–L4)

- **Question (minimum decision).** For the private/local profile through Phase-4 qualification, may the acting
  *agent* role (L0–L4) continue to be declared by the invoking harness or adapter, as D-0007 consequence 5 and
  docs/ARCHITECTURE.md §4.8 state? Or must the Governance OS itself bind each agent session to the role it was assigned,
  so that a process assigned a lower role cannot act as a higher one by declaring it?
- **Not part of this decision** (already determined and required): human approval and presentation come only from
  the authenticated human channel (BC-P2-10); no invocation without an explicit role gets privileged authority, and
  the declared role is applied on every path (BC-P2-08); T2 facts arise only from OS operations (BC-P2-09).
- **Options.**
  - **A. Keep the adapter boundary for agent roles.** The determined requirements above still apply. Record the residual
    risk: a compromised or misbehaving agent can claim a higher agent role. Revisit at R2/R3.
  - **B. OS-issued role credentials.** The OS issues a role-scoped credential at dispatch (claim/handoff) and verifies it
    on every privileged path. This only helps if agents cannot read each other's credentials, which requires per-agent
    process or account isolation that the private/local profile does not assume. That means infrastructure cost and more
    operator friction.
  - **C. Bind L3+ only.** L3 (change controller) and L4 (orchestrator) authority requires an owner- or
    administrator-issued credential; L0–L2 stay declared. Middle cost; protects the roles that approve and execute
    change.
- **Consequences.** A keeps the iteration-1 scope as stated in `repair-delta.md`. B or C adds an owner-added requirement,
  logged as a new class, not a convergence failure. It extends BC-P2-34 (independence) and E1:365, and needs isolation
  mechanics before Phase 4. Under A, Phase-4 qualification treats agents as honest about their assigned role. Any
  adversarial-agent fault class would then measure a known, accepted gap.
- **Recommendation: A.** The highest-trust fact, human approval, is closed by BC-P2-10 whichever option is chosen. B and C
  only give real protection with agent isolation, which ARCH-0003's support envelope does not assume. D-0007's documented
  boundary stays coherent once defaults and T2 forgery are closed. Reconsider at R3, or if Phase-4 fault classes model
  hostile agents.

### OD-P2-02 — Scope of the unprovisioned-machine posture

- **Question (minimum decision).** On a machine with no administrator-provisioned trust anchor (the product's default
  state), may privileged kernel material still be installed? If so, from which sources (the verifier binary's own
  embedded payload; external source directories via `init --source`, `update`, `adopt`, `kernel reinstall`), and under
  what marking? And must Phase-4 qualification run on provisioned machines?
- **Not part of this decision** (already determined and required): no unauthenticated installation is presented as
  current, verified or certified, and doctor/audit disclose it (BC-P2-36). A provisioned machine refuses unsigned,
  tampered and below-floor material at every ingress; this already holds and was re-verified (AC16-X3 X3b; alpha-r A2-02).
- **Options.**
  - **A. Refuse external-source ingress until provisioned.** Read A2:143 literally. Dev/test machines provision a
    throw-away root, as the certification harness and every audit here already do. The embedded payload may install
    only as an explicitly marked bootstrap mode tied to the binary's own identity. Most secure. It changes the
    documented first-run path (provision first) and needs harness and docs updates.
  - **B. Keep admission as a marked non-production mode.** Read A2:150 as the licence. External sources still install
    with authenticity UNKNOWN, visibly marked, never presented as current, excluded from qualification and release
    evidence. Keeps availability. It leaves an unauthenticated install path whose safety rests on the marking being
    honoured by every consumer.
  - **C. Ship or pre-install production root public keys.** OWNER-DIRECTIVE-0004 allows "embedded … root public keys", so
    the default machine is provisioned. Needs owner-controlled production key material and custody (an R2 matter) before
    Phase 4.
- **Consequences.** The choice sets the admission requirement of BC-P2-36. It also settles the unprovisioned sub-case
  of BC-P2-35: under A there is no unprovisioned install to verify; under B the marked mode must also mark
  post-install integrity as unanchored; under C the question disappears. It fixes what Phase-4 qualification must run on.
- **Recommendation: A**, with a documented dev/test path that provisions a throw-away root, and a rule that Phase-4
  qualification and all release-relevant evidence run on provisioned machines. This satisfies A2:143 as written, uses the
  bootstrap chain the owner already chose, and needs no production key material before R2.

## C. Items considered and not raised

- Gate V's "NEW TESTING REFINEMENT" label is not one of the three requirement classes listed at Contract v3:60. This is
  not an owner decision: the compiled form must carry the source label verbatim (BC-P2-01) rather than choose a mapping.
- AC-3 criterion. The families applied two readings of "cannot undermine the qualification scenario". The synthesis
  applies one uniform reading, derived from the item's purpose (`00-SYNTHESIS-REPORT.md` §3). This is an adjudication
  of accepted text, not a new requirement. The owner may override it like any §9 interpretation.
