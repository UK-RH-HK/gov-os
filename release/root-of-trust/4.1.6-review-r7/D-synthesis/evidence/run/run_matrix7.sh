#!/bin/bash
S=<scratch>; C7=$S/c7; O=$S/out/C; LOG=$O/matrix7-log.tsv; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache AR21_SCRATCH=$C7 AR21_WT=<worktree> AR21_EXPORT=$S/export"
start=$(date +%s); ( cd $S/probes/C && $E python3 -B matrix7.py $C7/t7/trees.raw.json $O/registers7.json $O/gitops7/gitops7-trees.json $O/txn7/txn7.json $O/matrix7 --workers 16 > $O/matrix7.stdout 2> $O/matrix7.stderr ); rc=$?; end=$(date +%s)
printf "matrix7\t%s\t%s\n" "$rc" "$((end-start))" >> $LOG; echo DONE >> $LOG
