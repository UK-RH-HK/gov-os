#!/bin/bash
# AR-0019: re-run of the steps invalidated in the final run (crashmig7 scratch collision -> empty JSON -> register_check crash),
# with the two instrument fixes copied from the work-product tree, and the examples generator run in place.
S=<scratch>
WT=<worktree>
F=$S/final; X=$F/export; P=$X/release/root-of-trust/4.1.6; R7=$P/evidence/r7; O=$F/out; W=$F/work; LOG=$F/log-rerun.tsv
: > $LOG; mkdir -p $W/da09b
for f in evidence/r7/LAY7/crashmig7.py evidence/r7/DA09r7-schema-fields-versus-register.py; do cp $WT/release/root-of-trust/4.1.6/$f $P/$f; done
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp XDG_CONFIG_HOME=$S/home/.config XDG_CACHE_HOME=$S/home/.cache XDG_STATE_HOME=$S/home/.state XDG_DATA_HOME=$S/home/.data PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache"
run() { id=$1; out=$2; cwd=$3; shift 3; start=$(date +%s); ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" "$out" >> $LOG; }
run crashmig7 $R7/LAY7/crashmig7.json $R7/LAY7 $E AR17_SCRATCH=$S/c AR17_WT=$X AR17_PROBES=$S/cprobes python3 -B crashmig7.py
run STATEMENTS-CHECK $R7/STATEMENTS-CHECK.json $P $E python3 -B decision-register/statements_check.py
run PROF7 $R7/PROF7-profile-conformance.json $R7 $E PROF7_SCRATCH=$W/prof7b python3 -B PROF7-profile-conformance.py
run REGISTER-CHECK $R7/REGISTER-CHECK.json $P $E python3 -B decision-register/register_check.py
run DA09r7 $R7/DA09r7-schema-fields-versus-register.json $R7 $E DA09_SCRATCH=$W/da09b python3 -B DA09r7-schema-fields-versus-register.py
run EXAMPLES-rev7 $O/examples-rev7.stdout $P/examples/rev7 $E python3 -B make_rev7.py
echo DONE >> $LOG
