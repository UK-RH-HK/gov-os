#!/bin/bash
# AR-0019 final evidence run for RoT-1 revision 7: every instrument from a copy of the work-product tree (scratch only).
S=<scratch>
WT=<worktree>
F=$S/final; X=$F/export; P=$X/release/root-of-trust/4.1.6; R7=$P/evidence/r7; L=$S/legacy; O=$F/out; W=$F/work; LOG=$F/log.tsv
mkdir -p $X $O $W $S/home $S/tmp $S/kcache; : > $LOG
tar -C $WT --exclude=.git -cf - . | tar -C $X -xf -
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
run() { id=$1; out=$2; cwd=$3; shift 3; start=$(date +%s); ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG; }
for d in fa7a fa7b cur7 adm7 env7 prof7 da09 csi da03r6 fa6 fa5a con6 src6 adm6 uw6 attr6 env6 da03r5 fa5r5 reg5 p1r4 B/a01 B/a02 B/a03 B/a04 B/a10 D r5/a01 r5/a05 r5/a08 r5/a09 r5/da01 r5/da03 r5/da04 r5/da05; do mkdir -p $W/$d; done
# ---------------------------------------------------------------- revision-7 instruments (outputs written into the export so dependants read them)
run CS7 $R7/CS7-derivation-calculator.json $R7 $E CS7_RESULTS_GZ=$R7/CS7-results.json.gz python3 -B CS7-derivation-calculator.py
run FA7-run1 $R7/FA7-first-contact-authority.json $R7 $E FA7_SCRATCH=$W/fa7a python3 -B FA7-first-contact-authority.py
run FA7-run2 $O/FA7-first-contact-authority.run2.json $R7 $E FA7_SCRATCH=$W/fa7b python3 -B FA7-first-contact-authority.py
run CUR7 $R7/CUR7-first-contact-currency.json $R7 $E CUR7_SCRATCH=$W/cur7 python3 -B CUR7-first-contact-currency.py
run ADM7 $R7/ADM7-admission-stores.json $R7 $E ADM7_SCRATCH=$W/adm7 python3 -B ADM7-admission-stores.py
run ENV7 $R7/ENV7-environment-authority.json $R7 $E SCRATCH=$W/env7 ENV7_ACCOUNT_HOME=<home> python3 -B ENV7-environment-authority.py
run BA11r7 $R7/BA11r7-machine-classes.json $R7 $E python3 -B BA11r7-machine-classes.py
run BA12r7 $R7/BA12r7-key-subsets-below-threshold.json $R7 $E python3 -B BA12r7-key-subsets-below-threshold.py
run PPR7 $R7/PPR7-project-records.json $R7 $E python3 -B PPR7-project-records.py
run DA05r7 $R7/DA05r7-combinations-under-CP1.json $R7 $E python3 -B DA05r7-combinations-under-CP1.py
run DA06r7 $R7/DA06r7-rendering-and-classifier-vocabulary.json $R7 $E python3 -B DA06r7-rendering-and-classifier-vocabulary.py
run crashmig7 $R7/LAY7/crashmig7.json $R7/LAY7 $E AR17_SCRATCH=$S/c AR17_WT=$X AR17_PROBES=$S/cprobes python3 -B crashmig7.py
run STATEMENTS-CHECK $R7/STATEMENTS-CHECK.json $P $E python3 -B decision-register/statements_check.py
run PROF7 $R7/PROF7-profile-conformance.json $R7 $E PROF7_SCRATCH=$W/prof7 python3 -B PROF7-profile-conformance.py
run REGISTER-CHECK $R7/REGISTER-CHECK.json $P $E python3 -B decision-register/register_check.py
run DA09r7 $R7/DA09r7-schema-fields-versus-register.json $R7 $E DA09_SCRATCH=$W/da09 python3 -B DA09r7-schema-fields-versus-register.py
mkdir -p $O/examples; cp -a $P/examples/rev7/. $O/examples/
run EXAMPLES-rev7 $O/examples-rev7.stdout $O/examples $E python3 -B make_rev7.py
# ---------------------------------------------------------------- retained revision-6 and revision-5 instruments (unchanged files)
mkdir -p $O/retained
run CSI-selftest $O/retained/CSI6-selftest.json $P $E python3 -B constitutional-surface/csi_check.py selftest --scratch $W/csi
run CSI-framework $O/retained/CSI6-CSI-check-framework.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/framework
run CSI-4.1.5 $O/retained/CSI6-CSI-check-release-4.1.5.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/release/releases/4.1.5/kernel
for v in 4.1.2 4.1.3 4.1.4; do run CSI-$v $O/retained/CSI6-CSI-check-legacy-$v.json $P $E python3 -B constitutional-surface/csi_check.py check --json $X/release/releases/$v/kernel; done
run P4r6 $O/retained/P4r6-conformance-oracle.json $P/evidence/r6 $E python3 -B P4r6-conformance-oracle.py
run CS6 $O/retained/CS6-derivation-calculator.json $P/evidence/r6 $E CS6_RESULTS_GZ=$O/retained/CS6-results.json.gz python3 -B CS6-derivation-calculator.py
run DA03r6 $O/retained/DA03r6-oracle-regression-sensitivity.json $P/evidence/r6 $E python3 -B DA03r6-oracle-regression-sensitivity.py $X $W/da03r6
run FA6 $O/retained/FA6-first-admission.json $P/evidence/r6 $E FA6_SCRATCH=$W/fa6 FA5_SCRATCH=$W/fa5a GOV=$L/gov-4.1.5 P4R6_JSON=$O/retained/P4r6-conformance-oracle.json python3 -B FA6-first-admission.py
run CON6 $O/retained/CON6-first-hand-constitutional-content.json $P/evidence/r6 $E REVIEW_REPO=$X GOV=$L/gov-4.1.5 SCRATCH=$W/con6 P4R6_JSON=$O/retained/P4r6-conformance-oracle.json python3 -B CON6-first-hand-constitutional-content.py
run SRC6 $O/retained/SRC6-source-identity-v2.json $P/evidence/r6 $E SCRATCH=$W/src6 python3 -B SRC6-source-identity-v2.py
run ADM6 $O/retained/ADM6-admission-transactions.json $P/evidence/r6 $E SCRATCH=$W/adm6 python3 -B ADM6-admission-transactions.py
run UW6 $O/retained/UW6-user-writable-install.json $P/evidence/r6 $E SCRATCH=$W/uw6 python3 -B UW6-user-writable-install.py
run ATTR6 $O/retained/ATTR6-gitattributes-condition.json $P/evidence/r6 $E SCRATCH=$W/attr6 python3 -B ATTR6-gitattributes-condition.py
run ENV6 $O/retained/ENV6-build-environment.json $P/evidence/r6 $E ENV6_SCRATCH=$W/env6 ENV6_ACCOUNT_HOME=<home> python3 -B ENV6-build-environment.py
run DA07r6 $O/retained/DA07r6-plan-regression-detection.json $P/evidence/r6 $E REVIEW_REPO=$X python3 -B DA07r6-plan-regression-detection.py
run P4r5 $O/retained/P4r5-conformance-oracle.json $P/evidence/r5 $E python3 -B P4r5-conformance-oracle.py
run DA03r5 $O/retained/DA03r5-oracle-regression-sensitivity.json $P/evidence/r5 $E python3 -B DA03r5-oracle-regression-sensitivity.py $X $W/da03r5
run FA5 $O/retained/FA5-first-admission.stdout.json $P/evidence/r5 $E FA5_SCRATCH=$W/fa5r5 python3 -B FA5-first-admission.py
run REG5 $O/retained/REG5-release-scoped-registration.json $P/evidence/r5 $E REVIEW_REPO=$X GOV=$L/gov-4.1.5 GOV_REVIEW_SCRATCH=$W/reg5 python3 -B REG5-release-scoped-registration.py
run P1r4 $O/retained/P1r4-project-strength-and-absence.json $P/evidence $E REVIEW_REPO=$X GOV_REVIEW_SCRATCH=$W/p1r4 GOV=$L/gov-4.1.5 python3 -B P1r4-project-strength-and-absence.py
run CS5 $O/retained/CS5-tcb-capability-sets.json $P/evidence/r5 $E python3 -B CS5-tcb-capability-sets.py
# ---------------------------------------------------------------- review r6 panel B and synthesis D probes, unmodified copies, against the export
RB=$X/release/root-of-trust/4.1.6-review-r6/B-trust-security/evidence/probes; RD=$X/release/root-of-trust/4.1.6-review-r6/D-synthesis/evidence/probes
mkdir -p $F/probes/B $F/probes/D $F/probes/r5B $F/probes/r5D $O/r6-probes $O/r5-probes
cp $RB/*.py $F/probes/B/; cp $RD/*.py $F/probes/D/
cp $X/release/root-of-trust/4.1.6-review-r5/B-trust-security/evidence/probes/*.py $F/probes/r5B/; cp $X/release/root-of-trust/4.1.6-review-r5/D-synthesis/evidence/probes/*.py $F/probes/r5D/
EP="$E REVIEW_REPO=$X"
run RV6-B-A01 $O/r6-probes/RV6-B-A01.json $F/probes/B $EP SCRATCH=$W/B/a01 GOV=$L/gov-4.1.5 python3 -B RV6-B-A01-first-contact-selectors.py
run RV6-B-A02 $O/r6-probes/RV6-B-A02.json $F/probes/B $EP SCRATCH=$W/B/a02 A02_ACCOUNT_HOME=<home> python3 -B RV6-B-A02-environment-manifest-author.py
run RV6-B-A03 $O/r6-probes/RV6-B-A03.json $F/probes/B $EP SCRATCH=$W/B/a03 python3 -B RV6-B-A03-generated-statement-rendering.py
run RV6-B-A04 $O/r6-probes/RV6-B-A04.json $F/probes/B $EP SCRATCH=$W/B/a04 GOV=$L/gov-4.1.5 python3 -B RV6-B-A04-readmission-rollback.py
run RV6-B-A10 $O/r6-probes/RV6-B-A10.json $F/probes/B $EP SCRATCH=$W/B/a10 python3 -B RV6-B-A10-surface-classes.py
run RV6-B-A11 $O/r6-probes/RV6-B-A11.json $F/probes/B $EP python3 -B RV6-B-A11-machine-classes-r6.py
run RV6-B-A12 $O/r6-probes/RV6-B-A12.json $F/probes/B $EP python3 -B RV6-B-A12-key-subsets-below-threshold.py
for n in A01-first-contact-designation A02-readmission-ignores-held-state A03-forward-compat-new-kernel-files A04-plan-regression-detection-r6-defects A05-owner-option-combinations A06-rendering-and-classifier-vocabulary A07-planted-admission-record A08-stale-first-contact-value-media-and-ci A09-schema-fields-versus-register A10-init-on-absent-after-crash; do
  id=${n%%-*}; mkdir -p $W/D/$id; run RV6-D-$id $O/r6-probes/RV6-D-$id.json $F/probes/D $EP SCRATCH=$W/D/$id GOV=$L/gov-4.1.5 AR17_SCRATCH=$S/c AR17_WT=$X python3 -B RV6-D-$n.py
done
run RV5-B-A01 $O/r5-probes/RV5-B-A01.json $F/probes/r5B $EP SCRATCH=$W/r5/a01 python3 -B RV5-B-A01-first-admission-channel.py
run RV5-B-A04 $O/r5-probes/RV5-B-A04.json $F/probes/r5B $EP python3 -B RV5-B-A04-calculator-extensions.py
run RV5-B-A05 $O/r5-probes/RV5-B-A05.json $F/probes/r5B $EP SCRATCH=$W/r5/a05 python3 -B RV5-B-A05-source-identity.py
run RV5-B-A08 $O/r5-probes/RV5-B-A08.json $F/probes/r5B env -i PATH=/usr/bin:/bin HOME=<home> TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 SCRATCH=$W/r5/a08 python3 -B RV5-B-A08-build-image-selects-bytes.py
run RV5-B-A09 $O/r5-probes/RV5-B-A09.json $F/probes/r5B $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/a09 python3 -B RV5-B-A09-floor-class-kernels.py
run RV5-B-A12 $O/r5-probes/RV5-B-A12.json $F/probes/r5B $EP python3 -B RV5-B-A12-machine-classes.py
run RV5-D-A01 $O/r5-probes/RV5-D-A01.json $F/probes/r5D $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/da01 python3 -B RV5-D-A01-registered-content-not-first-hand.py
run RV5-D-A03 $O/r5-probes/RV5-D-A03.json $F/probes/r5D $EP SCRATCH=$W/r5/da03 python3 -B RV5-D-A03-user-writable-install-anchoring.py
run RV5-D-A04 $O/r5-probes/RV5-D-A04.json $F/probes/r5D $EP GOV=$L/gov-4.1.5 SCRATCH=$W/r5/da04 python3 -B RV5-D-A04-conformance-vector-gaps.py
run RV5-D-A05 $O/r5-probes/RV5-D-A05.json $F/probes/r5D $EP SCRATCH=$W/r5/da05 python3 -B RV5-D-A05-forward-compat-new-constitutional-file.py
run RV5-D-A07 $O/r5-probes/RV5-D-A07.json $F/probes/r5D $EP python3 -B RV5-D-A07-plan-regression-detection.py
# ---------------------------------------------------------------- DA04r7 (needs the D-A03 re-run, the checks and DA09r7)
mkdir -p $R7/r6-probes; cp $O/r6-probes/RV6-D-A03.json $R7/r6-probes/RV6-D-A03.json
run DA04r7 $R7/DA04r7-plan-regression-detection.json $R7 $E python3 -B DA04r7-plan-regression-detection.py
# ---------------------------------------------------------------- reviewer C chain against the export (legacy containment)
mkdir -p $F/C
sed -e "s#O=\$S/runs/C#O=$F/C#" $S/run_C_chain.sh > $F/run_C_chain_final.sh
bash $F/run_C_chain_final.sh $X
cp $F/C/log.tsv $O/C-log.tsv 2>/dev/null
echo DONE >> $LOG
