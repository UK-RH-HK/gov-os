#!/bin/bash
S=${AR8_SCRATCH:?set AR8_SCRATCH to a scratch directory}
W=${AR8_WORKTREE:?set AR8_WORKTREE to the worktree}
C=$W/release/root-of-trust/4.1.6-review-r4/C-compat-transaction/evidence
R=$S/reproC; O=$R/out; mkdir -p $O $R/home
E="env -i PATH=/usr/bin:/bin HOME=$R/home PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 AR7_WT=$W AR7_LEGACY_BIN=${AR8_LEGACY_BIN:?}"
log(){ echo "$(date -u +%FT%TZ) $*" >> $O/LOG.txt; }
cd $R
$E python3 -B $C/build_trees.py $R/t > $O/build.stdout 2>$O/build.err; log "build exit $?"
$E python3 -B $C/subdir_escape.py $R/t/trees.json $R/subesc > $O/subdir_escape.stdout 2>$O/subdir_escape.err; log "subdir exit $?"
$E python3 -B $C/durability.py $R/t/trees.json $R/dur > $O/durability.stdout 2>$O/durability.err; log "durability exit $?"
$E python3 -B $C/legacy_regain.py $R/t/trees.json $R/regain > $O/legacy_regain.stdout 2>$O/legacy_regain.err; log "regain exit $?"
log DONE-SMALL
$E AR7_DISCARD_RUNS=1 python3 -B $C/matrix.py $R/t/trees.json $C/registers.json $R/matrix --workers 16 > $O/matrix.stdout 2>$O/matrix.err; log "matrix exit $?"
log DONE
