#!/bin/bash
# AR-0012 re-execution of the architect's revision-5 instruments and review-r4 probes, from a scratch export of cdb4e14.
S=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0012
R=$S/repo
P=$R/release/root-of-trust/4.1.6
L=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin
O=$S/runs
LOG=$O/log.tsv
: > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=$S/kcache"
run() { # id outfile cwd cmd...
  id=$1; out=$2; cwd=$3; shift 3
  start=$(date +%s)
  ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?
  end=$(date +%s)
  printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG
}
mkdir -p $S/csi $S/p1r4 $S/reg5 $S/da03r5 $S/r3 $S/r4b $S/r4d
run CSI-selftest $O/CSI5-selftest.json $P $E python3 -B constitutional-surface/csi_check.py selftest --scratch $S/csi
run CSI-framework $O/CSI5-CSI-check-framework.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/framework
run CSI-4.1.5 $O/CSI5-CSI-check-release-4.1.5.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/release/releases/4.1.5/kernel
for v in 4.1.2 4.1.3 4.1.4; do run CSI-$v $O/CSI5-CSI-check-legacy-$v.json $P $E python3 -B constitutional-surface/csi_check.py check --json $R/release/releases/$v/kernel; done
run P1r4 $O/P1r4-project-strength-and-absence.json $P/evidence $E REVIEW_REPO=$R GOV_REVIEW_SCRATCH=$S/p1r4 GOV=$L/gov-4.1.5 python3 -B P1r4-project-strength-and-absence.py
run P4r5 $O/P4r5-conformance-oracle.json $P/evidence/r5 $E python3 -B P4r5-conformance-oracle.py
run DA03r5 $O/DA03r5-oracle-regression-sensitivity.json $P/evidence/r5 $E python3 -B DA03r5-oracle-regression-sensitivity.py $R $S/da03r5
run FA5-run1 $O/FA5-first-admission.run1.json $P/evidence/r5 $E FA5_SCRATCH=$S/fa5 python3 -B FA5-first-admission.py
run FA5-run2 $O/FA5-first-admission.run2.json $P/evidence/r5 $E FA5_SCRATCH=$S/fa5 python3 -B FA5-first-admission.py
run REG5 $O/REG5-release-scoped-registration.json $P/evidence/r5 $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/reg5 python3 -B REG5-release-scoped-registration.py
cp $P/evidence/r5/SRC5-source-identity.json $O/SRC5-committed.json
run SRC5 $O/SRC5-stdout.json $P/evidence/r5 $E GIT_CONFIG_NOSYSTEM=1 SRC5_SCRATCH=$S/src5 python3 -B SRC5-source-identity.py
# review r4 B probes, unmodified, against the revision-5 pack
B=$R/release/root-of-trust/4.1.6-review-r4/B-trust-security/evidence
run RV4-B-M $O/RV4-B-M-reference-model.json $B $E python3 -B RV4-B-M-reference-model.py
run RV4-B-AF $O/RV4-B-arch-functions.json $B $E REVIEW_REPO=$R python3 -B RV4-B-arch-functions.py
run RV4-B-surface $O/RV4-B-surface-probes.json $B $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/r4b python3 -B RV4-B-surface-probes.py
run RV4-B-conf $O/RV4-B-confinement-and-first-binary.json $B $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/r4b python3 -B RV4-B-confinement-and-first-binary.py
for p in RV3-B-A01-precedence-immutable RV3-B-A03-A14-A16-probes RV3-B-CSI-injections RV3-D-precedence-lattice RV3-D-surface-forward-compat-and-removal r2rerun-P2-gate-record-forgery; do
  run r3copy-$p $O/r3copy-$p.json $B/r3-probe-copies $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/r3 python3 -B $p.py
done
D=$R/release/root-of-trust/4.1.6-review-r4/D-synthesis/evidence/probes
for p in RV4-D-A02-pinned-retention-breadth RV4-D-A03-oracle-regression-sensitivity RV4-D-A03b-distinguishing-scenarios; do
  run $p $O/$p.json $D $E REVIEW_REPO=$R GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$S/r4d python3 -B $p.py
done
run CS5 $O/CS5-tcb-capability-sets.json $P/evidence/r5 $E python3 -B CS5-tcb-capability-sets.py
echo DONE >> $LOG
