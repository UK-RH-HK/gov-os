#!/bin/bash
# AR-0016 re-execution of the architect's revision-6 instruments (and the retained revision-5 instruments) from a scratch
# export of 4106885. Adapted from review r5 B rerun_arch.sh (AR-0012), with attribution.
S=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0016
R=$S/export
P=$R/release/root-of-trust/4.1.6
L=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin
O=$S/runs
LOG=$O/log.tsv
: > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
run() { # id outfile cwd cmd...
  id=$1; out=$2; cwd=$3; shift 3
  start=$(date +%s)
  ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?
  end=$(date +%s)
  printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG
}
mkdir -p $S/csi $S/da03r6 $S/fa6a $S/fa6b $S/fa5a $S/fa5b $S/con6 $S/src6a $S/src6b $S/adm6 $S/uw6 $S/attr6 $S/env6a $S/env6b $S/p1r4 $S/reg5 $S/da03r5 $S/fa5r5
run CSI6-selftest $O/CSI6-selftest.json $P $E python3 -B constitutional-surface/csi_check.py selftest --scratch $S/csi
run CSI6-framework $O/CSI6-CSI-check-framework.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/framework
run CSI6-4.1.5 $O/CSI6-CSI-check-release-4.1.5.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/release/releases/4.1.5/kernel
for v in 4.1.2 4.1.3 4.1.4; do run CSI6-$v $O/CSI6-CSI-check-legacy-$v.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/release/releases/$v/kernel; done
run P4r6 $O/P4r6-conformance-oracle.json $P/evidence/r6 $E python3 -B P4r6-conformance-oracle.py
run DA03r6 $O/DA03r6-oracle-regression-sensitivity.json $P/evidence/r6 $E python3 -B DA03r6-oracle-regression-sensitivity.py $R $S/da03r6
run FA6-run1 $O/FA6-first-admission.json $P/evidence/r6 $E FA6_SCRATCH=$S/fa6a FA5_SCRATCH=$S/fa5a GOV=$L/gov-4.1.5 P4R6_JSON=$O/P4r6-conformance-oracle.json python3 -B FA6-first-admission.py
run FA6-run2 $O/FA6-first-admission.run2.json $P/evidence/r6 $E FA6_SCRATCH=$S/fa6b FA5_SCRATCH=$S/fa5b GOV=$L/gov-4.1.5 P4R6_JSON=$O/P4r6-conformance-oracle.json python3 -B FA6-first-admission.py
run CON6 $O/CON6-first-hand-constitutional-content.json $P/evidence/r6 $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 SCRATCH=$S/con6 P4R6_JSON=$O/P4r6-conformance-oracle.json python3 -B CON6-first-hand-constitutional-content.py
run SRC6-run1 $O/SRC6-source-identity-v2.json $P/evidence/r6 $E SCRATCH=$S/src6a python3 -B SRC6-source-identity-v2.py
run SRC6-run2 $O/SRC6-source-identity-v2.run2.json $P/evidence/r6 $E SCRATCH=$S/src6b python3 -B SRC6-source-identity-v2.py
run ADM6 $O/ADM6-admission-transactions.json $P/evidence/r6 $E SCRATCH=$S/adm6 python3 -B ADM6-admission-transactions.py
run UW6 $O/UW6-user-writable-install.json $P/evidence/r6 $E SCRATCH=$S/uw6 python3 -B UW6-user-writable-install.py
run ATTR6 $O/ATTR6-gitattributes-condition.json $P/evidence/r6 $E SCRATCH=$S/attr6 python3 -B ATTR6-gitattributes-condition.py
run ENV6-run1 $O/ENV6-build-environment.json $P/evidence/r6 $E ENV6_SCRATCH=$S/env6a ENV6_ACCOUNT_HOME=/home/usain python3 -B ENV6-build-environment.py
run ENV6-run2 $O/ENV6-build-environment.run2.json $P/evidence/r6 $E ENV6_SCRATCH=$S/env6b ENV6_ACCOUNT_HOME=/home/usain python3 -B ENV6-build-environment.py
run DA07r6 $O/DA07r6-plan-regression-detection.json $P/evidence/r6 $E REVIEW_REPO=$R python3 -B DA07r6-plan-regression-detection.py
run CS6 $O/CS6-derivation-calculator.json $P/evidence/r6 $E CS6_RESULTS_GZ=$O/CS6-results.json.gz python3 -B CS6-derivation-calculator.py
run REGISTER-CHECK $O/REGISTER-CHECK.json $P $E python3 -B decision-register/register_check.py
run STATEMENTS-CHECK $O/STATEMENTS-CHECK.json $P $E python3 -B decision-register/statements_check.py
run STATEMENTS-CHECK-rerunCS6 $O/STATEMENTS-CHECK.rerun-cs6.json $P $E python3 -B decision-register/statements_check.py --cs6 $O/CS6-derivation-calculator.json
# retained revision-5 instruments (entry criterion 2 (e))
run P4r5 $O/P4r5-conformance-oracle.json $P/evidence/r5 $E python3 -B P4r5-conformance-oracle.py
run DA03r5 $O/DA03r5-oracle-regression-sensitivity.json $P/evidence/r5 $E python3 -B DA03r5-oracle-regression-sensitivity.py $R $S/da03r5
run FA5 $O/FA5-first-admission.stdout.json $P/evidence/r5 $E FA5_SCRATCH=$S/fa5r5 python3 -B FA5-first-admission.py
run REG5 $O/REG5-release-scoped-registration.json $P/evidence/r5 $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/reg5 python3 -B REG5-release-scoped-registration.py
run P1r4 $O/P1r4-project-strength-and-absence.json $P/evidence $E REVIEW_REPO=$R GOV_REVIEW_SCRATCH=$S/p1r4 GOV=$L/gov-4.1.5 python3 -B P1r4-project-strength-and-absence.py
run CS5 $O/CS5-tcb-capability-sets.json $P/evidence/r5 $E python3 -B CS5-tcb-capability-sets.py
echo DONE >> $LOG
