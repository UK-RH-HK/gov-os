#!/bin/bash
# AR-0019: two full passes of every revision-7 instrument after the executor determinism fix; pass a writes the export evidence
# (hash seed unset = random), pass b writes $F/det/b (PYTHONHASHSEED=12345); byte comparison per output. Optional args: instrument ids.
S=<scratch>
WT=<worktree>
F=$S/final; X=$F/export; P=$X/release/root-of-trust/4.1.6; R7=$P/evidence/r7; B=$F/det/b; N=$(date +%s); W=$F/det/work-$N; LOG=$F/det/log-$N.tsv
mkdir -p $B/LAY7 $W; : > $LOG
# sync the work-product pack (instruments, text, register, schemas) into the export, keeping the export's outputs
for d in decision-register schemas profile examples; do tar -C $WT/release/root-of-trust/4.1.6 -cf - $d | tar -C $P -xf -; done
cp $WT/release/root-of-trust/4.1.6/*.md $P/; for f in $WT/release/root-of-trust/4.1.6/evidence/r7/*.py $WT/release/root-of-trust/4.1.6/evidence/r7/LAY7/*.py; do cp $f ${f/$WT/$X}; done
BASEENV="PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
run() { pass=$1; id=$2; out=$3; cwd=$4; shift 4; mkdir -p $W/$pass-$id; start=$(date +%s)
  if [ $pass = a ]; then seed=""; else seed="PYTHONHASHSEED=12345"; fi
  ( cd "$cwd" && env -i $BASEENV $seed SCR_ID=$W/$pass-$id "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s)
  printf "%s\t%s\t%s\t%s\t%s\t%s\n" "$pass" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG; }
want() { [ $# -eq 0 ] && return 0; return 1; }
IDS="$*"; sel() { [ -z "$IDS" ] || [[ " $IDS " == *" $1 "* ]]; }
for pass in a b; do
  if [ $pass = a ]; then D=$R7; else D=$B; fi
  sel CS7 && run $pass CS7 $D/CS7-derivation-calculator.json $R7 env CS7_RESULTS_GZ=$D/CS7-results.json.gz python3 -B CS7-derivation-calculator.py
  sel FA7 && run $pass FA7 $D/FA7-first-contact-authority.json $R7 env FA7_SCRATCH=$W/$pass-FA7 python3 -B FA7-first-contact-authority.py
  sel CUR7 && run $pass CUR7 $D/CUR7-first-contact-currency.json $R7 env CUR7_SCRATCH=$W/$pass-CUR7 python3 -B CUR7-first-contact-currency.py
  sel ADM7 && run $pass ADM7 $D/ADM7-admission-stores.json $R7 env ADM7_SCRATCH=$W/$pass-ADM7 python3 -B ADM7-admission-stores.py
  sel ENV7 && run $pass ENV7 $D/ENV7-environment-authority.json $R7 env SCRATCH=$W/$pass-ENV7 ENV7_ACCOUNT_HOME=<home> python3 -B ENV7-environment-authority.py
  sel BA11r7 && run $pass BA11r7 $D/BA11r7-machine-classes.json $R7 python3 -B BA11r7-machine-classes.py
  sel BA12r7 && run $pass BA12r7 $D/BA12r7-key-subsets-below-threshold.json $R7 python3 -B BA12r7-key-subsets-below-threshold.py
  sel PPR7 && run $pass PPR7 $D/PPR7-project-records.json $R7 python3 -B PPR7-project-records.py
  sel DA05r7 && run $pass DA05r7 $D/DA05r7-combinations-under-CP1.json $R7 python3 -B DA05r7-combinations-under-CP1.py
  sel DA06r7 && run $pass DA06r7 $D/DA06r7-rendering-and-classifier-vocabulary.json $R7 python3 -B DA06r7-rendering-and-classifier-vocabulary.py
  sel crashmig7 && run $pass crashmig7 $D/LAY7/crashmig7.json $R7/LAY7 env AR17_SCRATCH=$S/c AR17_WT=$X AR17_PROBES=$S/cprobes python3 -B crashmig7.py
  sel STATEMENTS-CHECK && run $pass STATEMENTS-CHECK $D/STATEMENTS-CHECK.json $P python3 -B decision-register/statements_check.py
  sel PROF7 && run $pass PROF7 $D/PROF7-profile-conformance.json $R7 env PROF7_SCRATCH=$W/$pass-PROF7 python3 -B PROF7-profile-conformance.py
  sel REGISTER-CHECK && run $pass REGISTER-CHECK $D/REGISTER-CHECK.json $P python3 -B decision-register/register_check.py
  sel DA09r7 && run $pass DA09r7 $D/DA09r7-schema-fields-versus-register.json $R7 env DA09_SCRATCH=$W/$pass-DA09r7 python3 -B DA09r7-schema-fields-versus-register.py
  sel DA04r7 && run $pass DA04r7 $D/DA04r7-plan-regression-detection.json $R7 python3 -B DA04r7-plan-regression-detection.py
  sel EXAMPLES && { mkdir -p $D/ex; run $pass EXAMPLES $D/ex/examples.stdout $P/examples/rev7 python3 -B make_rev7.py; cp $P/examples/rev7/validation.json $D/ex/validation.json; }
done
echo DONE >> $LOG
