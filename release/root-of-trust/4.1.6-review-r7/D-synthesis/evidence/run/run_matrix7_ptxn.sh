#!/bin/bash
# AR-0022: P-TXN positions of reviewer C's matrix7 re-run with the txn7 output's scratch placeholder <ar21> resolved to the scratch root
# (txn7 scrubs paths in its JSON; the first full run read the scrubbed paths and recorded HARNESS_ERROR for every P-TXN row).
S=<scratch>; C7=$S/c7; O=$S/out/C; LOG=$O/matrix7-ptxn-log.tsv; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache AR21_SCRATCH=$C7 AR21_WT=<worktree> AR21_EXPORT=$S/export"
start=$(date +%s); ( cd $S/probes/C && $E python3 -B matrix7.py $C7/t7/trees.raw.json $O/registers7.json - $O/txn7/txn7.unscrubbed.json $O/matrix7-ptxn --workers 16 --only P-TXN > $O/matrix7-ptxn.stdout 2> $O/matrix7-ptxn.stderr ); rc=$?; end=$(date +%s)
printf "matrix7-P-TXN\t%s\t%s\n" "$rc" "$((end-start))" >> $LOG; echo DONE >> $LOG
