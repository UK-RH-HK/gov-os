#!/bin/bash
# AR-0022 re-run of reviewer C's (AR-0021) revision-7 legacy-containment chain, unmodified probe copies, scratch only.
S=<scratch>; C7=<scratch>/c7; X=<scratch>/export; O=$S/out/C; LOG=$O/chain-log.tsv; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache AR21_SCRATCH=$C7 AR21_WT=<worktree> AR21_EXPORT=$X"
run() { id=$1; out=$2; shift 2; start=$(date +%s); ( cd $S/probes/C && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
run register7 $O/register7.stdout $E python3 -B register7.py $O/registers7.json
run build7 $O/build7.json $E python3 -B build7.py $C7/t7
run struct7 $O/struct7.json $E python3 -B struct7.py $C7/t7/trees.raw.json
run gitops7 $O/gitops7.json $E python3 -B gitops7.py $C7/t7/trees.raw.json $O/gitops7
run txn7 $O/txn7.stdout $E python3 -B txn7.py $C7/t7/trees.raw.json $O/txn7
echo CHAIN-PREP-DONE >> $LOG
