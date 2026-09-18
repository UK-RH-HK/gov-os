# OWNER-DECISION-P2-0002 — Machines with no trust anchor (OD-P2-02): Option A, refuse until provisioned

| Field | Value |
|---|---|
| Record | OWNER-DECISION-P2-0002 |
| Date | 2026-09-19 |
| Gate | HG-P2-0001 (`HG-P2-0001-OWNER-DECISIONS.md`), question OD-P2-02 |
| Channel | answered by the product owner in the active chat (AskUserQuestion), after presentation of the full gate package |
| Classification | binding owner security-versus-availability posture decision (the class reserved to the owner by OWNER-DECISION-0005 §1) |
| Raised by | fresh independent synthesis P2-AR-0007, `owner-decisions-required.md` row 4 / OD-P2-02 |

## Decision

**Option A — refuse external-source ingress until the machine is provisioned.** Contract v3 A2 bullet 1 (*"Release/source
authenticity is established before any privileged kernel material is staged or installed"*) is applied as written.

## Requirements this adds (owner-added normative, lifecycle P2)

1. On a machine with no administrator-provisioned trust anchor, privileged kernel material from an **external source**
   (`init --source`, `update`, `adopt`, `kernel reinstall`, and any other ingress that stages or installs kernel material
   not embedded in the running verifier binary) is **refused**, typed and observable, with remediation pointing to
   provisioning.
2. The verifier binary's **own embedded payload** may be installed on an unprovisioned machine only as an explicitly
   marked **bootstrap mode** tied to the binary's own identity; that installation is never presented as current, verified
   or certified (BC-P2-36 presentation part, already determined), and doctor/audit disclose it.
3. **Dev/test machines provision a throw-away root**, as the certification harness and every Phase-2 audit already do. The
   harness, fixtures and documentation are updated so the documented first-run path is "provision, then install".
4. **Phase-4 qualification and all release-relevant evidence run on provisioned machines.**
5. Provisioned-machine behaviour (refusing unsigned, tampered and below-floor material at every ingress) is unchanged and
   must be preserved (R1 / AC-14).

## Effect

BC-P2-36's admission part is now **determined** by this record and joins the repair plan (round 2, WS-8), together with
the unprovisioned sub-case of BC-P2-35 (under Option A there is no unprovisioned external-source install to verify). This
is an owner-added requirement: per the repair delta §0.4 it opens an owner-added scope item, not a convergence failure.
No production key material is required before R2. D-0007 is unchanged.
