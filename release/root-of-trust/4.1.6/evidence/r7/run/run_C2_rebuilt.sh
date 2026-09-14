#!/bin/bash
# AR-0019: reviewer C's gitops6 and matrix6 (unmodified) on trees rebuilt by build6 from the final export.
E="env -i PATH=/usr/bin:/bin HOME=<scratch>/cf/home LANG=C.UTF-8 PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=<scratch>/cf/kcache AR17_SCRATCH=<scratch>/cf AR17_WT=<export>"
LOG=<scratch>/final/C2/log.tsv; : > $LOG
run() { id=$1; out=$2; shift 2; start=$(date +%s); ( cd <scratch>/cprobes && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
run gitops6 <scratch>/final/C2/gitops6.stdout $E python3 -B gitops6.py <scratch>/cf/trees2-rebuild/trees.json <scratch>/final/C2/gitops
run matrix6 <scratch>/final/C2/matrix6.stdout $E python3 -B matrix6.py <scratch>/cf/trees2-rebuild/trees.json <scratch>/final/C/registers6.json <scratch>/final/C2/gitops/gitops6-trees.json <scratch>/final/C2/matrix --workers 16
echo DONE >> $LOG
