#!/bin/bash
# AR-0022 re-run of reviewer B's probes (unmodified copies) against the d07d200 export.
S=<scratch>
X=$S/export; P=$X/release/root-of-trust/4.1.6; BP=$S/probes/B; O=$S/out/B; W=$S/work/B; LOG=$O/log.tsv
mkdir -p $BP $O $W/a01 $W/a01m $W/a02 $W/a04 $W/a09; : > $LOG
cp $X/release/root-of-trust/4.1.6-review-r7/B-trust-security/evidence/probes/*.py $BP/
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache PACK=$P"
run() { id=$1; out=$2; shift 2; start=$(date +%s); ( cd $BP && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
run RV7-B-A01 $O/RV7-B-A01.json $E A01_SCRATCH=$W/a01 python3 -B RV7-B-A01-revocation-omission.py
run RV7-B-A01m $O/RV7-B-A01m.json $E A01M_SCRATCH=$W/a01m python3 -B RV7-B-A01m-executor-mutant.py
run RV7-B-A02 $O/RV7-B-A02.json $E A02_SCRATCH=$W/a02 python3 -B RV7-B-A02-c3-currency-stale-state.py
run RV7-B-CS7 $O/RV7-B-CS7.json $E python3 -B RV7-B-CS7-extensions.py
run RV7-B-A04-A05 $O/RV7-B-A04-A05.json $E A04_SCRATCH=$W/a04 SCRATCH=$W/a04 python3 -B RV7-B-A04-A05-provenance-labels-and-schema-shapes.py
run RV7-B-A09 $O/RV7-B-A09.json $E A09_SCRATCH=$W/a09 SCRATCH=$W/a09 python3 -B RV7-B-A09-exclusion-schema-sweep.py
echo DONE >> $LOG
