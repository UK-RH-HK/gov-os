#!/bin/bash
# AR-0018: reviewer B (AR-0016) held-out probes, unmodified scratch copies, against a scratch export of b9bed32 (pack = 4106885).
S=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0018
R=$S/export; L=$S/legacy; O=$S/runs/B; W=$S/work/B; LOG=$O/log.tsv; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache REVIEW_REPO=$R"
run() { id=$1; out=$2; shift 2; start=$(date +%s); ( cd $S/bprobes && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
mkdir -p $W/a01 $W/a02 $W/a03 $W/a04 $W/a10
run A01 $O/RV6-B-A01-first-contact-selectors.json $E SCRATCH=$W/a01 GOV=$L/gov-4.1.5 python3 -B RV6-B-A01-first-contact-selectors.py
run A03 $O/RV6-B-A03-generated-statement-rendering.json $E SCRATCH=$W/a03 python3 -B RV6-B-A03-generated-statement-rendering.py
run A04 $O/RV6-B-A04-readmission-rollback.json $E SCRATCH=$W/a04 GOV=$L/gov-4.1.5 python3 -B RV6-B-A04-readmission-rollback.py
run A10 $O/RV6-B-A10-surface-classes.json $E SCRATCH=$W/a10 python3 -B RV6-B-A10-surface-classes.py
run A11 $O/RV6-B-A11-machine-classes-r6.json $E python3 -B RV6-B-A11-machine-classes-r6.py
run A02 $O/RV6-B-A02-environment-manifest-author.json $E SCRATCH=$W/a02 A02_ACCOUNT_HOME=/home/usain python3 -B RV6-B-A02-environment-manifest-author.py
run A12 $O/RV6-B-A12-key-subsets-below-threshold.json $E python3 -B RV6-B-A12-key-subsets-below-threshold.py
echo DONE >> $LOG
