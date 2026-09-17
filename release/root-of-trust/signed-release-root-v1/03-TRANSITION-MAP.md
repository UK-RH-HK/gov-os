# Transition map — 4.1.5 and D-0007 to Signed Release Root

## State sequence

```text
4.1.5 implementation + D-0007 ACTIVE
        |
        | V-H3: source/release authenticity is not established at ingress
        v
D-0009 owner direction + ARCH-0003 R0 candidate
        |
        | fresh independent R0 architecture review only
        v
ROT_ARCHITECTURE_ACCEPTED_R0
        |
        | later separately authorised implementation
        v
R1 exact candidate + fresh independent verification
        |
        v
ROT_PHASE1_CANDIDATE_ACCEPTED_R1
        |
        +--> R2 standard release certification
        |
        `--> optional R3 high-assurance platform qualification
```

## What remains active now

- ARCH-0001 remains the active Governance OS implementation architecture.
- D-0007 remains ACTIVE in full.
- The 4.1.5 runtime/kernel/CLI implementation remains unchanged.
- Existing policy precedence, Human Gates, plugin governance, governed exceptions, installed-kernel integrity, mutation controls, memory safeguards, migration safety and evidence remain in force.
- D-0009 is the active owner direction for the new release-authentication architecture.
- ARCH-0003 is a provisional R0 review candidate, not an implemented/active runtime architecture.

## What R0 may change conceptually

Only the architecture for authenticating release sources and safely admitting their bytes:

- trust begins outside the candidate/project repository;
- signed standard metadata authorises releases;
- all lifecycle ingress shares one verifier;
- verified bytes flow through atomic staging/install;
- signed versions and protected local high-water prevent rollback;
- freshness and offline status are explicit.

R0 does not modify source code or the existing product architecture.

## D-0007 transition rule

D-0007's manifest and `framework.lock` continue to pin and verify an installed kernel. They do not authenticate a first install or update source. After R0, an R1 implementation may add the external authenticated-release input in front of the existing installed-integrity boundary.

D-0007 cannot be superseded or amended merely because R0 is accepted. A later explicit transition record must identify which wording, if any, changes after the R1 implementation is independently accepted. All unaffected D-0007 rules survive.

## CP-1 disposition

- D-0008 and ARCH-0002 stay non-active and unchanged.
- RoT-1 revisions 1–7 and reviews remain immutable evidence.
- Valid attacks and mechanisms—ingress coverage, bootstrap impossibility, TOCTOU, verified-byte install, rollback/revocation, recovery and build/toolchain research—remain inputs to R0/R1/R3 where their lifecycle matches.
- Custom Trust State, C0–C3 calculus, bespoke admitter, selector register, registration/reproducer protocol and CP-1 certification coupling are not carried into the standard Phase-1 architecture.
- No Revision 8 is created.

## Next deterministic action

`FRESH_R0_ARCHITECTURE_REVIEW_OF_ARCH_0003_AT_COMMITTED_REBASE_CANDIDATE`

The reviewer evaluates D-0009, ARCH-0003 and this directory against the frozen acceptance boundary. The reviewer does not implement, activate ARCH-0003, amend D-0007, mutate D-0008/ARCH-0002, or revive the CP-1 repair loop.
