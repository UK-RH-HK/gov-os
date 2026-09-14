#!/bin/bash
# AR-0013 reproduction of prior decisive probes (review r4 C, r4 D-A01, architect ST5 and P3r3) against revision 5.
# Scratch only; env -i; GOV_* absent except GOV_KERNEL_CACHE set by each library into scratch; no forced deletes.
set -u
S=${AR13_SCRATCH:?}; W=${AR13_WT:?}; L=${AR13_LEGACY_BIN:?}
R=$S/repro; O=$R/out; mkdir -p $O $R/home
C=$W/release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence
D=$W/release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence/probes
A=$W/release/root-of-trust/4.1.6/evidence
E="env -i PATH=/usr/bin:/bin HOME=$R/home PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 AR7_WT=$W AR7_LEGACY_BIN=$L"
log(){ echo "$(date -u +%FT%TZ) $*" >> $O/LOG.txt; }
cd $R
log START
$E python3 -B $C/build_trees.py $R/t > $O/C-build.stdout 2>$O/C-build.err; log "C build_trees exit $?"
$E python3 -B $C/subdir_escape.py $R/t/trees.json $R/subesc > $O/C-subdir_escape.stdout 2>$O/C-subdir_escape.err; log "C subdir_escape exit $?"
$E python3 -B $C/durability.py $R/t/trees.json $R/dur > $O/C-durability.stdout 2>$O/C-durability.err; log "C durability exit $?"
$E python3 -B $C/legacy_regain.py $R/t/trees.json $R/regain > $O/C-legacy_regain.stdout 2>$O/C-legacy_regain.err; log "C legacy_regain exit $?"
$E python3 -B $D/RV4-D-A01-nested-root-escalation.py $R/t/trees.json $R/da01 $W > $O/D-A01.stdout 2>$O/D-A01.err; log "D-A01 exit $?"
mkdir -p $R/st5
$E python3 -B $A/r5/ST5-installation-state-r5.py $R/t/trees.json > $R/st5/ST5-installation-state.stdout 2>$O/ST5-state.err; log "ST5 state exit $?"
$E python3 -B $A/r5/ST5-subdir-escape.py $R/t/trees.json $R/st5 > $O/ST5-subdir-escape.stdout 2>$O/ST5-subdir-escape.err; log "ST5 subdir-escape exit $?"
$E python3 -B $A/r5/ST5-D-A01-rerun.py $R/t/trees.json $R/st5-da01 $W > $O/ST5-D-A01.stdout 2>$O/ST5-D-A01.err; log "ST5 D-A01 exit $?"
$E python3 -B $A/r5/ST5-gitignore-surgery.py $R/t/trees.json $R/st5 > $O/ST5-gitignore.stdout 2>$O/ST5-gitignore.err; log "ST5 gitignore exit $?"
$E python3 -B $A/r5/ST5-subdir-matrix.py $R/t/trees.json $C/registers.json $R/st5 --workers 16 > $O/ST5-matrix.stdout 2>$O/ST5-matrix.err; log "ST5 matrix exit $?"
log DONE-ST5
( cd $A && env -i PATH=/usr/bin:/bin HOME=$R/home PYTHONDONTWRITEBYTECODE=1 P3_REPO=$W P3_LEGACY_BIN=$L python3 -B P3r3-pre-rot-register-matrix.py $R/p3 --workers 12 > $R/P3r3-full.json 2>$O/P3r3.err ); log "P3r3 exit $?"
log DONE-P3
$E AR7_DISCARD_RUNS=1 python3 -B $C/matrix.py $R/t/trees.json $C/registers.json $R/matrix --workers 16 > $O/C-matrix.stdout 2>$O/C-matrix.err; log "C matrix exit $?"
log DONE
