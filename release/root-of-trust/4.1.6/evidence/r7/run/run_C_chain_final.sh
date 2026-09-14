#!/bin/bash
# AR-0019: reviewer C (AR-0017) probes, unmodified scratch copies (attribution: review r6 C; run shape after AR-0018 rerun_C.sh).
S=<scratch>; C=$S/cf; O=<scratch>/final/C; LOG=$O/log.tsv; mkdir -p $O; : > $LOG
EXPORT=${1:-$S/base-export}
E="env -i PATH=/usr/bin:/bin HOME=$C/home LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$C/kcache AR17_SCRATCH=$C AR17_WT=$EXPORT"
run() { id=$1; out=$2; shift 2; start=$(date +%s); ( cd $S/cprobes && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
run register6 $O/register6.stdout env -i PATH=/usr/bin:/bin HOME=$C/home LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$C/kcache AR17_SCRATCH=$C AR17_WT=<worktree> python3 -B register6.py $O/registers6.json
run build6 $O/build6.json $E python3 -B build6.py $C/trees2
run gitops6 $O/gitops6.json $E python3 -B gitops6.py $C/trees2/trees.json $O/gitops
run struct6 $O/struct6.json $E python3 -B struct6.py
run attrprec6 $O/attrprec6.json $E python3 -B attrprec6.py
run admtx6 $O/admtx6.json $E python3 -B admtx6.py
run crashmig6 $O/crashmig6.json $E python3 -B crashmig6.py
run matrix6 $O/matrix6.stdout $E python3 -B matrix6.py $C/trees2/trees.json $O/registers6.json $O/gitops/gitops6-trees.json $O/matrix --workers 16
echo DONE >> $LOG
