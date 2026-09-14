#!/bin/bash
# AR-0019: final re-run of the unmodified review r6 (B, D) and review r5 decisive probes against the export (latest pack text).
S=<scratch>
F=$S/final; X=$F/export; L=$S/legacy; O=$F/out; W=$F/work/probes-final; LOG=$F/log-probes-final.tsv
mkdir -p $W $O/r6-probes-final $O/r5-probes-final; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
EP="$E REVIEW_REPO=$X"
run() { id=$1; out=$2; cwd=$3; shift 3; start=$(date +%s); ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG; }
for d in B/a01 B/a02 B/a03 B/a04 B/a10 r5/a01 r5/a05 r5/a08 r5/a09 r5/da01 r5/da03 r5/da04 r5/da05; do mkdir -p $W/$d; done
R6=$O/r6-probes-final; R5=$O/r5-probes-final
run RV6-B-A01 $R6/RV6-B-A01.json $F/probes/B $EP SCRATCH=$W/B/a01 GOV=$L/gov-4.1.5 python3 -B RV6-B-A01-first-contact-selectors.py
run RV6-B-A02 $R6/RV6-B-A02.json $F/probes/B $EP SCRATCH=$W/B/a02 A02_ACCOUNT_HOME=<home> python3 -B RV6-B-A02-environment-manifest-author.py
run RV6-B-A03 $R6/RV6-B-A03.json $F/probes/B $EP SCRATCH=$W/B/a03 python3 -B RV6-B-A03-generated-statement-rendering.py
run RV6-B-A04 $R6/RV6-B-A04.json $F/probes/B $EP SCRATCH=$W/B/a04 GOV=$L/gov-4.1.5 python3 -B RV6-B-A04-readmission-rollback.py
run RV6-B-A10 $R6/RV6-B-A10.json $F/probes/B $EP SCRATCH=$W/B/a10 python3 -B RV6-B-A10-surface-classes.py
run RV6-B-A11 $R6/RV6-B-A11.json $F/probes/B $EP python3 -B RV6-B-A11-machine-classes-r6.py
run RV6-B-A12 $R6/RV6-B-A12.json $F/probes/B $EP python3 -B RV6-B-A12-key-subsets-below-threshold.py
for n in A01-first-contact-designation A02-readmission-ignores-held-state A03-forward-compat-new-kernel-files A04-plan-regression-detection-r6-defects A05-owner-option-combinations A06-rendering-and-classifier-vocabulary A07-planted-admission-record A08-stale-first-contact-value-media-and-ci A09-schema-fields-versus-register A10-init-on-absent-after-crash; do
  id=${n%%-*}; mkdir -p $W/D/$id; run RV6-D-$id $R6/RV6-D-$id.json $F/probes/D $EP SCRATCH=$W/D/$id GOV=$L/gov-4.1.5 AR17_SCRATCH=$S/c AR17_WT=$X python3 -B RV6-D-$n.py
done
run RV5-B-A01 $R5/RV5-B-A01.json $F/probes/r5B $EP SCRATCH=$W/r5/a01 python3 -B RV5-B-A01-first-admission-channel.py
run RV5-B-A04 $R5/RV5-B-A04.json $F/probes/r5B $EP python3 -B RV5-B-A04-calculator-extensions.py
run RV5-B-A05 $R5/RV5-B-A05.json $F/probes/r5B $EP SCRATCH=$W/r5/a05 python3 -B RV5-B-A05-source-identity.py
run RV5-B-A08 $R5/RV5-B-A08.json $F/probes/r5B env -i PATH=/usr/bin:/bin HOME=<home> TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 SCRATCH=$W/r5/a08 python3 -B RV5-B-A08-build-image-selects-bytes.py
run RV5-B-A09 $R5/RV5-B-A09.json $F/probes/r5B $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/a09 python3 -B RV5-B-A09-floor-class-kernels.py
run RV5-B-A12 $R5/RV5-B-A12.json $F/probes/r5B $EP python3 -B RV5-B-A12-machine-classes.py
run RV5-D-A01 $R5/RV5-D-A01.json $F/probes/r5D $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/da01 python3 -B RV5-D-A01-registered-content-not-first-hand.py
run RV5-D-A03 $R5/RV5-D-A03.json $F/probes/r5D $EP SCRATCH=$W/r5/da03 python3 -B RV5-D-A03-user-writable-install-anchoring.py
run RV5-D-A04 $R5/RV5-D-A04.json $F/probes/r5D $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/da04 python3 -B RV5-D-A04-conformance-vector-gaps.py
run RV5-D-A05 $R5/RV5-D-A05.json $F/probes/r5D $EP SCRATCH=$W/r5/da05 python3 -B RV5-D-A05-forward-compat-new-constitutional-file.py
run RV5-D-A07 $R5/RV5-D-A07.json $F/probes/r5D $EP python3 -B RV5-D-A07-plan-regression-detection.py
echo DONE >> $LOG
