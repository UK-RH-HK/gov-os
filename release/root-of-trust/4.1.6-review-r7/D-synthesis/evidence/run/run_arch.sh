#!/bin/bash
# AR-0022 reproduction of the architect's revision-7 instruments (adapted from evidence/r7/run/run_r7_evidence.sh; scratch only).
S=<scratch>
X=$S/export; P=$X/release/root-of-trust/4.1.6; R7=$P/evidence/r7; O=$S/out/arch; W=$S/work/arch; LOG=$O/log.tsv
mkdir -p $O $W; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
run() { id=$1; out=$2; cwd=$3; shift 3; start=$(date +%s); ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG; }
for d in fa7a fa7b cur7 adm7 env7 prof7 da09 csi; do mkdir -p $W/$d; done
run CS7 $O/CS7-derivation-calculator.json $R7 $E CS7_RESULTS_GZ=$O/CS7-results.json.gz python3 -B CS7-derivation-calculator.py
run FA7-run1 $O/FA7-first-contact-authority.json $R7 $E FA7_SCRATCH=$W/fa7a python3 -B FA7-first-contact-authority.py
run FA7-run2 $O/FA7-first-contact-authority.run2.json $R7 $E FA7_SCRATCH=$W/fa7b python3 -B FA7-first-contact-authority.py
run CUR7 $O/CUR7-first-contact-currency.json $R7 $E CUR7_SCRATCH=$W/cur7 python3 -B CUR7-first-contact-currency.py
run ADM7 $O/ADM7-admission-stores.json $R7 $E ADM7_SCRATCH=$W/adm7 python3 -B ADM7-admission-stores.py
run BA11r7 $O/BA11r7-machine-classes.json $R7 $E python3 -B BA11r7-machine-classes.py
run BA12r7 $O/BA12r7-key-subsets-below-threshold.json $R7 $E python3 -B BA12r7-key-subsets-below-threshold.py
run PPR7 $O/PPR7-project-records.json $R7 $E python3 -B PPR7-project-records.py
run DA05r7 $O/DA05r7-combinations-under-CP1.json $R7 $E python3 -B DA05r7-combinations-under-CP1.py
run DA06r7 $O/DA06r7-rendering-and-classifier-vocabulary.json $R7 $E python3 -B DA06r7-rendering-and-classifier-vocabulary.py
run STATEMENTS-CHECK $O/STATEMENTS-CHECK.json $P $E python3 -B decision-register/statements_check.py
run PROF7 $O/PROF7-profile-conformance.json $R7 $E PROF7_SCRATCH=$W/prof7 python3 -B PROF7-profile-conformance.py
run REGISTER-CHECK $O/REGISTER-CHECK.json $P $E python3 -B decision-register/register_check.py
run DA09r7 $O/DA09r7-schema-fields-versus-register.json $R7 $E DA09_SCRATCH=$W/da09 python3 -B DA09r7-schema-fields-versus-register.py
run DA04r7 $O/DA04r7-plan-regression-detection.json $R7 $E python3 -B DA04r7-plan-regression-detection.py
run CSI-selftest $O/CSI-selftest.json $P $E python3 -B constitutional-surface/csi_check.py selftest --scratch $W/csi
run CSI-framework $O/CSI-check-framework.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/framework
run CSI-4.1.5 $O/CSI-check-release-4.1.5.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/release/releases/4.1.5/kernel
for v in 4.1.2 4.1.3 4.1.4; do run CSI-$v $O/CSI-check-legacy-$v.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/release/releases/$v/kernel; done
run ENV7 $O/ENV7-environment-authority.json $R7 $E SCRATCH=$W/env7 ENV7_ACCOUNT_HOME=<home> python3 -B ENV7-environment-authority.py
echo DONE >> $LOG
