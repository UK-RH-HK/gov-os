#!/bin/bash
# E0 (AR-0009, specialist A) — baseline re-execution, against the unchanged revision-4 pack, of:
#   (1) the architect's instruments behind the mechanisms this proposal RETAINS (CSI selftest/check, P4r4, VA4, P1r4);
#   (2) the review-r4 blocking probes (reviewer B model, AF1-AF3, surface part P, first-binary part B; synthesis D-A02);
#   (3) the review-r3 blocking probes still relevant to retained mechanisms (B's copies: RV3-B-A01, D lattice, D removal).
# Purpose: establish that each attack exists at base (so a later "refused" is attributable to the proposal) and that the
# retained closures still reproduce. Adapted from review-r4 D `probes/repro_ab.sh` (AR-0008) with attribution; every
# probe script is run unmodified from its committed location. Scratch only; env -i; no GOV_* except the scratch cache.
set -u
S=${AR9_SCRATCH:?set AR9_SCRATCH to a scratch directory}
W=${AR9_WORKTREE:?set AR9_WORKTREE to the worktree}
LEG=${AR9_LEGACY_BIN:?set AR9_LEGACY_BIN to the legacy binary directory}
R=$S/repro; O=$R/out
mkdir -p $O $R/home $R/surf $R/conf $R/p1r4 $R/r3 $R/da02
E="env -i PATH=/usr/bin:/bin HOME=$R/home XDG_CONFIG_HOME=$R/home/.config XDG_DATA_HOME=$R/home/.local/share XDG_STATE_HOME=$R/home/.local/state XDG_CACHE_HOME=$R/home/.cache PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=$R/kcache REVIEW_REPO=$W"
P=$W/release/root-of-trust/4.1.6
B=$W/release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence
D=$W/release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence
log(){ echo "$(date -u +%FT%TZ) $*" >> $O/LOG.txt; }
: > $O/LOG.txt
cd $R
for b in 4.1.2 4.1.3 4.1.4 4.1.5; do log "sha256 gov-$b $(sha256sum $LEG/gov-$b | cut -d' ' -f1)"; done
log "worktree HEAD $(git -C $W rev-parse HEAD)"
log "pack diff vs bca05a7: $(git -C $W diff --stat bca05a7 HEAD -- release/root-of-trust/4.1.6 spec/decisions/D-0008.yaml spec/architecture/ARCH-0002.yaml | wc -l) lines"
log "implementation diff vs da9c851: $(git -C $W diff --stat da9c851 HEAD -- runtime cli framework migrations capabilities Cargo.toml Cargo.lock release/releases | wc -l) lines"
# (1) architect instruments (retained mechanisms)
$E python3 -B $P/constitutional-surface/csi_check.py selftest --scratch $R/csi > $O/arch-selftest.json 2>$O/arch-selftest.err; log "csi selftest exit $?"
INV=$P/constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml
for k in framework release/releases/4.1.5/kernel; do
  $E python3 -B $P/constitutional-surface/csi_check.py check $W/$k > $O/arch-check-$(echo $k|tr / _).json 2>&1; log "csi check $k exit $?"
done
$E python3 -B $P/evidence/P4r4-trust-state-model.py > $O/P4r4.json 2>$O/P4r4.err; cmp -s $O/P4r4.json $P/evidence/P4r4-trust-state-model.json; log "P4r4 cmp $?"
$E python3 -B $P/evidence/VA4-verify-artifact-source-scenarios.py > $O/VA4.json 2>$O/VA4.err; cmp -s $O/VA4.json $P/evidence/VA4-verify-artifact-source-scenarios.json; log "VA4 cmp $?"
$E GOV_REVIEW_SCRATCH=$R/p1r4 GOV=$LEG/gov-4.1.5 python3 -B $P/evidence/P1r4-project-strength-and-absence.py > $O/P1r4.json 2>$O/P1r4.err; cmp -s $O/P1r4.json $P/evidence/P1r4-project-strength-and-absence.json; log "P1r4 cmp $?"
# (2) review r4 blocking probes
$E python3 -B $B/RV4-B-M-reference-model.py > $O/B-model.json 2>$O/B-model.err; cmp -s $O/B-model.json $B/RV4-B-M-reference-model.json; log "B model cmp $?"
$E python3 -B $B/RV4-B-arch-functions.py > $O/B-archfn.json 2>$O/B-archfn.err; cmp -s $O/B-archfn.json $B/RV4-B-arch-functions.json; log "B archfn cmp $?"
$E GOV_REVIEW_SCRATCH=$R/surf GOV=$LEG/gov-4.1.5 python3 -B $B/RV4-B-surface-probes.py > $O/B-surface.json 2>$O/B-surface.err; cmp -s $O/B-surface.json $B/RV4-B-surface-probes.json; log "B surface cmp $?"
$E GOV_REVIEW_SCRATCH=$R/conf GOV=$LEG/gov-4.1.5 python3 -B $B/RV4-B-confinement-and-first-binary.py > $O/B-conf.json 2>$O/B-conf.err; cmp -s $O/B-conf.json $B/RV4-B-confinement-and-first-binary.json; log "B conf cmp $?"
$E python3 -B $D/probes/RV4-D-A02-pinned-retention-breadth.py $W $R/da02 > $O/D-A02.json 2>$O/D-A02.err; cmp -s $O/D-A02.json $D/outputs/RV4-D-A02.json; log "D-A02 cmp $?"
# (3) review r3 blocking probes on retained mechanisms (B's unmodified copies)
for p in RV3-B-A01-precedence-immutable RV3-D-precedence-lattice; do
  $E GOV_REVIEW_SCRATCH=$R/r3 GOV=$LEG/gov-4.1.5 python3 -B $B/r3-probe-copies/$p.py > $O/r3-$p.json 2>$O/r3-$p.err; log "r3 $p exit $?"
done
$E python3 -B $B/r3-probe-copies/RV3-D-surface-forward-compat-and-removal.py $R/r3/fc > $O/r3-RV3-D-surface-forward-compat-and-removal.json 2>$O/r3-removal.err; log "r3 removal exit $?"
# normalised comparison for outputs that embed scratch paths
python3 -B - "$O" "$B/r3-rerun" <<'PY' >> $O/LOG.txt
import json, re, sys, os
o, ref = sys.argv[1], sys.argv[2]
norm = lambda t: re.sub(r'(<scratch>|<scratchpad-path>|/tmp/[^"\s]*)', '<p>', t)
for name in ("RV3-B-A01-precedence-immutable", "RV3-D-precedence-lattice", "RV3-D-surface-forward-compat-and-removal"):
    a = norm(open(os.path.join(o, f"r3-{name}.json")).read())
    b = norm(open(os.path.join(ref, f"{name}.json")).read())
    print(f"normalised-compare r3 {name} vs review-r4 B r3-rerun: {'identical' if a == b else 'DIFFERENT'}")
PY
log DONE
