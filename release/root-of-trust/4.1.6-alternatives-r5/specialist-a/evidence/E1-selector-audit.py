#!/usr/bin/env python3
"""E1 (AR-0009, specialist A) — selector audit: does one invariant predict every blocking finding of four reviews?

DESIGN-ENCODED evidence. The rows below are this specialist's encoding of decisions stated in the RoT-1 revisions
(676dfce, d37b05c, ca77a43, bca05a7) and of the findings the four independent reviews made about them (1c6027c, e5a6b8a,
79a09a1, 97a5545), with file references. The computation is trivial; the evidence value is the classification and whether
it is complete (every HIGH is flagged) and specific (no mechanism a review confirmed sound is flagged). No files, no
subprocesses. Output: JSON on stdout.

Invariant SEL-1 (00-ROOT-CAUSE.md §5). For every trust decision, each input is one of:
  selector   — its value determines WHICH of several authentic candidates (binary, source, inputs, state, content, anchor,
               installation state) becomes the effective fact;
  restrictor — it can only refuse, or strengthen through a monotone join;
  carrier    — it transports bytes whose identity a selector has already fixed.
SEL-1 holds for a decision iff every selector's authority >= the authority the decision confers AND every selector's
currency >= the currency the decision confers. A violation that the design states as an unavoidable or owner-selected
residual with an exact bound is "labelled"; any other violation is "unlabelled".

Authority ranks: 5 root threshold; 4 multi-party quorum of distinct custody (>= 2) or local machine authority (a human
typing from an independent channel, a protected operator pin, a local confirmation); 2 one key of one purpose;
1 repository writer / project (T4) / governed account; 0 transport, unauthenticated input, or the artefact under judgement.
Currency ranks: 3 established now (typed in the gate); 2 within a stated window (P1 pin, P3 witnesses); 1 as of a past
anchor or compiled state; 0 none.
"""
import json, sys

sys.dont_write_bytecode = True

# (id, revision, decision, conferred (authority, currency), selectors [(name, authority, currency)], label, finding, source refs)
ROWS = [
    # ------------------------------------------------------------------ revision 1 (676dfce), review 1c6027c
    ("r1-01", "r1", "policy root at use: which authentic kernel governs", (5, 1), [("installed authentic kernel delivered by Git/restore, no currency floor", 1, 0)], None, "RV-H1", "review 10 RV-H1"),
    ("r1-02", "r1", "lifecycle view that relaxes a gate (CERTIFIED, absence of REJECTED/revocation)", (4, 2), [("subset of statements the presenter chose", 0, 0)], None, "RV-H2", "review 10 RV-H2"),
    ("r1-03", "r1", "bytes enforced in a unit of work", (5, 1), [("installed directory re-read after verification (same-user writable)", 1, 0)], None, "RV-H3", "review 10 RV-H3"),
    ("r1-04", "r1", "legacy kernel authenticity", (5, 1), [("certification-role key", 2, 1)], None, "RV-H4", "review 10 RV-H4"),
    ("r1-05", "r1", "authenticity of a release statement", (2, 0), [("release key under the compiled root", 2, 1)], None, "sound", "review 00 §3 area 1, 4"),
    ("r1-06", "r1", "embedded baseline (no cache)", (5, 1), [("bytes compiled into the binary", 5, 1)], None, "sound", "review 00 §3 area 7"),
    # ------------------------------------------------------------------ revision 2 (d37b05c), review e5a6b8a
    ("r2-01", "r2", "floor values of 145 registered keys", (5, 1), [("join of registered floor and kernel value (restrictor)", 5, 1)], None, "sound", "review r2 00 §3"),
    ("r2-02", "r2", "unfloored constitutional leaves (role map, secret patterns, gate resolution)", (5, 1), [("threshold-1 release-final kernel", 2, 1)], None, "R2-H1", "r2 10 R2-H1"),
    ("r2-03", "r2", "effective trust state on a stateless verifier", (5, 2), [("repository-selected genuine statements", 1, 0)], None, "R2-H2", "r2 10 R2-H2"),
    ("r2-04", "r2", "production binary acceptance (TCB)", (5, 2), [("threshold-1 release-final artefact statement", 2, 1)], None, "R2-H3", "r2 10 R2-H3"),
    ("r2-05", "r2", "installed kernel/overlay state treated as valid after a pre-RoT remedy", (5, 1), [("legacy binary rewrite of kernel, lock and overlay", 1, 0)], None, "R2-H4", "r2 10 R2-H4"),
    ("r2-06", "r2", "authorisation of a trust transition (gate answer)", (4, 3), [("repository gate record", 1, 0)], None, "R2-M1", "r2 10 R2-M1"),
    ("r2-07", "r2", "lifting WITHDRAWN/REJECTED", (4, 1), [("certification key alone", 2, 1)], None, "R2-M3", "r2 10 R2-M3"),
    ("r2-08", "r2", "sticky revocations (negative set)", (2, 1), [("union of verified negatives (restrictor)", 2, 1)], None, "sound", "r2 00 §3"),
    # ------------------------------------------------------------------ revision 3 (ca77a43), review 79a09a1
    ("r3-01", "r3", "project-layer precedence rule", (5, 1), [("kernel POLICY_PRECEDENCE through an unsound join", 2, 1)], None, "RV3-H1", "r3 10 RV3-H1"),
    ("r3-02", "r3", "which Trust State satisfies an anchor", (4, 1), [("supplier-chosen sequence number (+ one trust-state key)", 2, 0)], None, "RV3-H2", "r3 10 RV3-H2 (1)"),
    ("r3-03", "r3", "currency for C3 and binary acceptance on a pinned machine", (4, 2), [("pin with no validity", 4, 1)], None, "RV3-H2", "r3 10 RV3-H2 (2)"),
    ("r3-04", "r3", "witnessed currency (OP-7 c)", (4, 2), [("one threshold-1 trust-state key", 2, 2)], None, "RV3-H2", "r3 10 RV3-H2 (3)"),
    ("r3-05", "r3", "source of the production binary", (5, 1), [("commit named by threshold-1 release-final", 2, 1)], None, "RV3-H3", "r3 10 RV3-H3"),
    ("r3-06", "r3", "anchor and decision pins honoured", (4, 1), [("files the governed account (and gov-run commands) can write", 1, 1)], None, "RV3-M2", "r3 10 RV3-M2"),
    ("r3-07", "r3", "clock high-water", (4, 2), [("issued_at of any verified statement", 2, 0)], None, "RV3-M3", "r3 10 RV3-M3"),
    ("r3-08", "r3", "default deny for added constitutional content", (5, 1), [("root-signed inventory (restrictor)", 5, 1)], None, "sound", "r3 00 §1"),
    ("r3-09", "r3", "trust decisions from repository records", (4, 3), [("local confirmation", 4, 3)], None, "sound", "r3 00 §1"),
    # ------------------------------------------------------------------ revision 4 (bca05a7), review 97a5545
    ("r4-01", "r4", "faithful build of the attested source (bytes of the TCB)", (4, 1), [("one build-attestation key + pipeline-handed bytes", 2, 1)], None, "RV4-H1", "r4 10 RV4-H1 (1)"),
    ("r4-02", "r4", "legitimate source of the TCB (proposal S1; architecture minimum S0)", (5, 1), [("one verification-attestation key (S0 minimum)", 2, 1)], None, "RV4-H1", "r4 10 RV4-H1 (2)"),
    ("r4-03", "r4", "build inputs (toolchain, lockfiles) of the TCB", (5, 1), [("build_inputs_digest named by the release pipeline / candidate, not evaluated by the verifier", 1, 1)], None, "NEW (E2)", "r4 07 §3 release.source; 05 §7 rules 2, 3, 6"),
    ("r4-04", "r4", "first binary on a machine", (4, 2), [("transport-served genuine statements, no state (path b)", 0, 0), ("values printed by the candidate (path c)", 0, 0), ("the candidate itself (Phase 4)", 0, 0)], None, "RV4-H2", "r4 10 RV4-H2"),
    ("r4-05", "r4", "TA-5 confirmations on a first-install machine", (4, 3), [("display and input handling of the unaccepted binary", 0, 3)], None, "RV4-H2", "r4 10 RV4-H2 (3), D-A04"),
    ("r4-06", "r4", "effective non-orderable constitutional content of a release", (5, 1), [("threshold-1 release-final choosing among a registered digest list", 2, 1)], None, "RV4-H3", "r4 10 RV4-H3"),
    ("r4-07", "r4", "which TSS a witness names (OP-7 c)", (4, 2), [("Git host / repository the witness service polls", 1, 2)], None, "RV4-M3", "r4 10 RV4-M3"),
    ("r4-08", "r4", "migration content applied on a machine without a record", (5, 1), [("release-final-signed migration on a whitelisted target", 2, 1)], None, "RV4-M5", "r4 10 RV4-M5"),
    ("r4-09", "r4", "members of a hash-bound owner contract set", (4, 1), [("independent per-path decision pins", 4, 0)], None, "RV4-L10", "r4 10 RV4-L10"),
    ("r4-10", "r4", "code the account later runs unconfined (PATH, hooks)", (4, 1), [("files planted by a gov-run repository command", 1, 1)], None, "RV4-M2", "r4 10 RV4-M2"),
    ("r4-11", "r4", "installation state COMPLETE", (5, 1), [("presence of named entries; foreign entries not examined", 0, 1)], None, "RV4-M1", "r4 10 RV4-M1"),
    ("r4-12", "r4", "clock for pin validity and the C3 window under OP-7 (a)", (4, 2), [("local clock with no high-water", 1, 2)], "RS-2 (TA-7) must be restated", "RV4-M4", "r4 10 RV4-M4"),
    ("r4-13", "r4", "anchor satisfaction", (4, 1), [("inclusion of an anchored (sequence, digest) from a pin or human", 4, 1)], None, "sound", "r4 00 §1 BC-2"),
    ("r4-14", "r4", "C3 currency", (4, 2), [("P1 recent anchoring event / P2 typed fingerprint / P3 >= 2 witnesses", 4, 2)], None, "sound", "r4 00 §1 BC-2"),
    ("r4-15", "r4", "project-layer precedence", (5, 1), [("root-signed registration", 5, 1)], None, "sound", "r4 00 §1 BC-1"),
    ("r4-16", "r4", "binary source vs release-final", (5, 1), [("V8 source equality (restrictor on release-final)", 5, 1)], None, "sound (as stated)", "r4 00 §1 BC-3"),
    ("r4-17", "r4", "project overlay configuration", (1, 0), [("repository writer (T4)", 1, 0)], None, "sound (LR-4)", "r4 05-RESIDUALS LR-4"),
    ("r4-18", "r4", "project_tunable kernel values", (1, 0), [("release-final (the project can override)", 2, 1)], None, "sound (RV4-B-A10)", "r4 B 02 A10"),
    ("r4-19", "r4", "C1-C2 on a machine anchored before a revocation", (5, 1), [("anchor prefix + supplier-chosen descendant", 4, 1), ("supplier-chosen descendant", 1, 1)], "RS-1 core (unavoidable, bounded)", "residual", "r4 24 §10 RS-1"),
    ("r4-20", "r4", "C1-C2 on an unanchored machine under OP-7 (d)", (5, 1), [("repository/transport-selected genuine state >= compiled TSS", 1, 1)], "OP-7 (d) owner-selected residual", "residual", "r4 24 §9"),
    # ------------------------------------------------------------------ this proposal (SAM)
    ("sam-01", "SAM", "faithful build of the registered source and inputs", (4, 1), [("reproducer quorum >= 2 of first-person reproductions, inputs fetched by digest", 4, 1)], None, "-", "01 §2.3"),
    ("sam-02", "SAM", "legitimate source AND build inputs of the TCB", (4, 1), [("release registration authority (root threshold Q1, or delegated quorum >= 2 Q2)", 4, 1)], None, "-", "01 §2.2; 03 OC-1"),
    ("sam-03", "SAM", "first binary on a machine", (4, 3), [("state fingerprint typed from the independent channel (commits to lineage, root, policy, state)", 4, 3)], None, "-", "01 §3.2"),
    ("sam-04", "SAM", "binary N+1 accepted by binary N", (4, 2), [("anchor inclusion + currency proof P1/P2/P3", 4, 2)], None, "-", "01 §3.4"),
    ("sam-05", "SAM", "TA-5 confirmations", (4, 3), [("accepted binary, after acceptance", 5, 3)], None, "-", "01 §3.5"),
    ("sam-06", "SAM", "effective non-orderable constitutional content of a release", (4, 1), [("registration function at the release's exact sequence", 4, 1)], None, "-", "01 §4"),
    ("sam-07", "SAM", "floor values", (5, 1), [("join (restrictor)", 5, 1)], None, "-", "01 §4.4 (retained)"),
    ("sam-08", "SAM", "migration content", (4, 1), [("registered unit of the release", 4, 1)], None, "-", "01 §4.3"),
    ("sam-09", "SAM", "owner contract set", (4, 1), [("local confirmation of the binding group digest", 4, 1)], None, "-", "01 §4.3"),
    ("sam-10", "SAM", "which TSS a witness names (if OP-7 c)", (4, 2), [("owner ceremony or independent channel (CR4-B-02)", 4, 2)], None, "-", "01 §6 carried"),
    ("sam-11", "SAM", "installation state COMPLETE", (5, 1), [("closed entry set recorded by the install transaction (RV4-M1 a)", 5, 1)], None, "-", "01 §6 carried"),
    ("sam-12", "SAM", "bytes that run are the bytes accepted", (4, 1), [("install location owned by another uid (OC-4 option i)", 4, 1)], "OC-4 option (ii) accepts A3 replacement (RS-3 class)", "-", "01 §3.3; 03 OC-4"),
    ("sam-13", "SAM", "C1-C2 on a machine anchored before a revocation", (5, 1), [("anchor prefix + supplier-chosen descendant", 4, 1), ("supplier-chosen descendant", 1, 1)], "RS-1 core (retained)", "residual", "01 §5"),
    ("sam-14", "SAM", "C1-C2 on an unanchored machine under OP-7 (d)", (5, 1), [("repository/transport-selected genuine state", 1, 1)], "OP-7 (d) owner-selected residual (retained)", "residual", "03 OC-7"),
    ("sam-15", "SAM", "channel currency of the typed fingerprint", (4, 3), [("what the operator reads on the channel now", 4, 3)], "RS-B1: a stale channel page (TA-5)", "residual", "02 N-FB1"),
    ("sam-16", "SAM", "legitimacy of an upstream toolchain release", (4, 1), [("upstream toolchain publisher", 2, 1)], "TA-12 common-mode toolchain (OC-3)", "residual", "02 E2 toolchain_upstream"),
    ("sam-17", "SAM", "clock for pin validity and P1 window", (4, 2), [("local clock", 1, 2)], "RS-2 restated (TA-7), CR4-B-03", "residual", "01 §5"),
    ("sam-18", "SAM", "project overlay configuration", (1, 0), [("repository writer (T4)", 1, 0)], None, "-", "retained LR-4"),
]


def audit(row):
    _, rev, decision, (ca, cc), selectors, label, finding, ref = row
    low = [s for s in selectors if s[1] < ca or s[2] < cc]
    return {"id": row[0], "revision": rev, "decision": decision, "conferred": {"authority": ca, "currency": cc},
            "selectors_below_conferred": [s[0] for s in low], "violation": bool(low), "label": label, "review_status": finding, "ref": ref}


def main():
    res = [audit(r) for r in ROWS]
    by_rev = {}
    for r in res:
        by_rev.setdefault(r["revision"], []).append(r)
    summary = {}
    for rev, rows in by_rev.items():
        highs = [r for r in rows if "-H" in r["review_status"]]
        mediums_lows = [r for r in rows if "-M" in r["review_status"] or "-L" in r["review_status"]]
        sound = [r for r in rows if r["review_status"].startswith("sound")]
        summary[rev] = {
            "rows": len(rows),
            "HIGH_findings_encoded": sorted({r["review_status"] for r in highs}),
            "HIGH_rows_flagged": sum(1 for r in highs if r["violation"]), "HIGH_rows": len(highs),
            "MEDIUM_LOW_rows_flagged": sum(1 for r in mediums_lows if r["violation"]), "MEDIUM_LOW_rows": len(mediums_lows),
            "sound_mechanisms_flagged (false positives)": [r["id"] for r in sound if r["violation"]], "sound_mechanisms": len(sound),
            "unlabelled_violations": [r["id"] for r in rows if r["violation"] and not r["label"]],
            "labelled_residual_violations": [r["id"] for r in rows if r["violation"] and r["label"]],
            "new_rows_flagged": [r["id"] for r in rows if r["review_status"].startswith("NEW") and r["violation"]],
        }
    print(json.dumps({"audit": "E1 selector audit (AR-0009), design-encoded", "rows": res, "summary": summary}, indent=1))


if __name__ == "__main__":
    main()
