#!/bin/bash
# AR-0008 reproduction of architect instruments and reviewer B probes. Scratch only; env -i; no GOV_* except scratch cache.
S=${AR8_SCRATCH:?set AR8_SCRATCH to a scratch directory}
W=${AR8_WORKTREE:?set AR8_WORKTREE to the worktree}
LEG=${AR8_LEGACY_BIN:?set AR8_LEGACY_BIN}
R=$S/repro; O=$R/out
E="env -i PATH=/usr/bin:/bin HOME=$R/home XDG_CONFIG_HOME=$R/home/.config XDG_DATA_HOME=$R/home/.local/share XDG_STATE_HOME=$R/home/.local/state XDG_CACHE_HOME=$R/home/.cache PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=$R/kcache REVIEW_REPO=$W"
P=$W/release/root-of-trust/4.1.6
B=$W/release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence
log(){ echo "$(date -u +%FT%TZ) $*" >> $O/LOG.txt; }
cd $R
# architect
$E python3 -B $P/constitutional-surface/csi_check.py selftest --scratch $R/csi > $O/arch-selftest.json 2>$O/arch-selftest.err; log "selftest exit $?"
INV=$P/constitutional-surface/CONSTITUTIONAL_SURFACE_INVENTORY.yaml
for k in framework release/releases/4.1.5/kernel release/releases/4.1.2/kernel release/releases/4.1.3/kernel release/releases/4.1.4/kernel; do
  $E python3 -B $P/constitutional-surface/csi_check.py check $W/$k > $O/arch-check-$(echo $k|tr / _).json 2>&1; log "check $k exit $?"
done
$E python3 -B $P/evidence/P4r4-trust-state-model.py > $O/P4r4.json 2>$O/P4r4.err; cmp $O/P4r4.json $P/evidence/P4r4-trust-state-model.json; log "P4r4 cmp $?"
$E python3 -B $P/evidence/VA4-verify-artifact-source-scenarios.py > $O/VA4.json 2>$O/VA4.err; cmp $O/VA4.json $P/evidence/VA4-verify-artifact-source-scenarios.json; log "VA4 cmp $?"
$E GOV_REVIEW_SCRATCH=$R/p1r4 GOV=$LEG/gov-4.1.5 python3 -B $P/evidence/P1r4-project-strength-and-absence.py > $O/P1r4.json 2>$O/P1r4.err; cmp $O/P1r4.json $P/evidence/P1r4-project-strength-and-absence.json; log "P1r4 cmp $?"
# B
$E python3 -B $B/RV4-B-M-reference-model.py > $O/B-model.json 2>$O/B-model.err; cmp $O/B-model.json $B/RV4-B-M-reference-model.json; log "B model cmp $?"
$E python3 -B $B/RV4-B-arch-functions.py > $O/B-archfn.json 2>$O/B-archfn.err; cmp $O/B-archfn.json $B/RV4-B-arch-functions.json; log "B archfn cmp $?"
$E GOV_REVIEW_SCRATCH=$R/surf GOV=$LEG/gov-4.1.5 python3 -B $B/RV4-B-surface-probes.py > $O/B-surface.json 2>$O/B-surface.err; cmp $O/B-surface.json $B/RV4-B-surface-probes.json; log "B surface cmp $?"
$E GOV_REVIEW_SCRATCH=$R/conf GOV=$LEG/gov-4.1.5 python3 -B $B/RV4-B-confinement-and-first-binary.py > $O/B-conf.json 2>$O/B-conf.err; cmp $O/B-conf.json $B/RV4-B-confinement-and-first-binary.json; log "B conf cmp $?"
log DONE
