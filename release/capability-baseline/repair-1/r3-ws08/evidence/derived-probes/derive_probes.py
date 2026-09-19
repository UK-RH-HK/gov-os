#!/usr/bin/env python3
"""P2-AR-0039 (WS-8, round 3) — labelled DERIVED copies of audit-of-record probes whose premise the 4.1.6 version
decision changes. NOT the audit of record; the originals under release/capability-baseline/audit-0/ are never edited.

Why: the audit-of-record probes were written when HEAD was 4.1.5. Several build "the current release" from a
`git archive HEAD` canonical copy and ask `gov release build --version 4.1.5`. The working tree is now 4.1.6 (the
recorded next version; release/releases/4.1.5 is immutable and its payload differs), so those builds stop at
VERSION_MISMATCH before any root-of-trust line runs. The derived copies restore the probes' own premise — the
payload of HEAD labelled 4.1.5 — by passing `version="4.1.5"` to exactly those canonical copies (the probe library's
own re-versioning parameter), and change nothing else except where the probe library is imported from (so the copy
can run from this evidence directory against any tree) and, in A2-04 [L3], the one unprovisioned install whose premise
was "a HEAD copy is the embedded payload" (see the comment there). Each substitution is listed below and printed with
its diff. The provisioned derivation of S5-update (IP-R2-WS08-13) is a separate, hand-written file beside this one.

Usage: derive_probes.py <out-dir>   (writes <probe>.derived.P2-AR-0039.py and prints the diffs)
"""
import difflib
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
WT = os.path.abspath(os.path.join(HERE, *[".."] * 6))
AR = os.path.join(WT, "release/capability-baseline/audit-0/alpha-r/evidence")
SY = os.path.join(WT, "release/capability-baseline/audit-0/synthesis/evidence")

LIB_ALPHA = ('sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))',
             'sys.path.insert(0, os.environ["ALPHA_R_LIB"])  # P2-AR-0039 derived copy: the tree-under-test\'s probe library')
LIB_SYNTH = ('sys.path.insert(0, os.path.join(HERE, "..", "..", "alpha-r", "evidence", "lib"))',
             'sys.path.insert(0, os.environ["ALPHA_R_LIB"])  # P2-AR-0039 derived copy: the tree-under-test\'s probe library')

# (probe file, [(old, new), ...]) — every substitution is an exact, single-occurrence string replacement
DERIVATIONS = [
    (os.path.join(AR, "A2-01-unprovisioned-posture.py"), [
        LIB_ALPHA,
        ('canon = canonical_copy(sb.path("canon"))', 'canon = canonical_copy(sb.path("canon"), version="4.1.5")'),
        ('canon2 = canonical_copy(sb.path("canon2"), mutate=', 'canon2 = canonical_copy(sb.path("canon2"), version="4.1.5", mutate='),
    ]),
    (os.path.join(AR, "A2-03-post-install-tamper.py"), [
        LIB_ALPHA,
        ('canon = canonical_copy(sb.path("canon"))', 'canon = canonical_copy(sb.path("canon"), version="4.1.5")'),
    ]),
    (os.path.join(AR, "A2-04-lock-identity-and-masquerade.py"), [
        LIB_ALPHA,
        ('canonical_copy(sb.path("any-canon"))', 'canonical_copy(sb.path("any-canon"), version="4.1.5")'),
        # [L3] the unprovisioned row: the original installs "a copy of HEAD", which on the audited tree was byte-identical
        # to the binary's embedded payload and so (since OWNER-DECISION-P2-0002) the one kernel an unprovisioned machine
        # admits, as a marked bootstrap. With HEAD relabelled 4.1.5 it no longer is; the derived row installs the
        # embedded payload itself (no --source), which is what the row measured.
        ('o3 = sb2.gov("init", "--source", os.path.join(sb.path("r15-canon"), "framework"), "--name", "p3", "--alias", "p3a", "--skip-index", cwd=p3, quiet=True)',
         'o3 = sb2.gov("init", "--name", "p3", "--alias", "p3a", "--skip-index", cwd=p3, quiet=True)'),
    ]),
    (os.path.join(AR, "A2-05-rotation-revocation-recovery.py"), [
        LIB_ALPHA,
        ('canon = canonical_copy(sb.path("canon"))', 'canon = canonical_copy(sb.path("canon"), version="4.1.5")'),
    ]),
    (os.path.join(AR, "S5-update.py"), [
        LIB_ALPHA,
        ('cc = canonical_copy(sbp.path("cc"))', 'cc = canonical_copy(sbp.path("cc"), version="4.1.5")'),
    ]),
    (os.path.join(SY, "AC16-X3-ingress-root-of-trust-chain.py"), [
        LIB_SYNTH,
        ('canon = canonical_copy(sb.path("canon"))', 'canon = canonical_copy(sb.path("canon"), version="4.1.5")'),
        ('canon2 = canonical_copy(sbp.path("canon"))', 'canon2 = canonical_copy(sbp.path("canon"), version="4.1.5")'),
    ]),
]


def main(out):
    os.makedirs(out, exist_ok=True)
    for src, subs in DERIVATIONS:
        text = open(src).read()
        new = text
        for old, rep in subs:
            n = new.count(old)
            if n != 1:
                raise SystemExit(f"{os.path.basename(src)}: expected exactly one occurrence of {old!r}, found {n}")
            new = new.replace(old, rep)
        name = os.path.basename(src)[:-3] + ".derived.P2-AR-0039.py"
        header = (f"# DERIVED COPY (P2-AR-0039, WS-8 round 3) of {os.path.relpath(src, WT)} — NOT the audit of record.\n"
                  f"# Changes: the probe library is imported from $ALPHA_R_LIB (the tree under test); canonical copies that\n"
                  f"# feed a `release build --version 4.1.5` keep the probe's premise (HEAD's payload labelled 4.1.5) via\n"
                  f"# canonical_copy(..., version=\"4.1.5\"). Every change is listed in derive_probes.py and its printed diff.\n")
        open(os.path.join(out, name), "w").write(header + new)
        print(f"==== {name}  (source sha256 of the original printed by the runner)")
        sys.stdout.writelines(difflib.unified_diff(text.splitlines(True), new.splitlines(True),
                                                   fromfile=os.path.relpath(src, WT), tofile=name, n=0))


if __name__ == "__main__":
    main(sys.argv[1])
