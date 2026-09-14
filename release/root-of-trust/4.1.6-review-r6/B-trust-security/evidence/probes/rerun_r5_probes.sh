#!/bin/bash
# AR-0016: review r5 decisive probes (reviewer B RV5-B-A01/A04/A05/A08/A09/A12; synthesis D RV5-D-A01/A03/A04/A05/A07), run
# UNMODIFIED from scratch copies against a scratch export of 4106885 (revision 6). Each probe loads its instruments by path from
# REVIEW_REPO; where an instrument it names is a retained revision-5 file, the run reproduces the revision-5 behaviour of that
# file, which this review records as such.
S=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/ar-0016
R=$S/export
L=/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/fc4fea1b-ad8d-4050-bd73-d14eea9b9c18/scratchpad/legacy-bin
O=$S/runs-r5probes
LOG=$O/log.tsv
: > $LOG
B=$S/r5copies/B; D=$S/r5copies/D
mkdir -p $B $D
cp $S/pristine/release/root-of-trust/4.1.6-review-r5/B-trust-security/evidence/probes/*.py $B/
cp $S/pristine/release/root-of-trust/4.1.6-review-r5/D-synthesis/evidence/probes/*.py $D/
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 GIT_CONFIG_NOSYSTEM=1 GOV_KERNEL_CACHE=$S/kcache REVIEW_REPO=$R"
run() { id=$1; out=$2; cwd=$3; shift 3; start=$(date +%s); ( cd "$cwd" && "$@" > "$out" 2> "$out.stderr" ); rc=$?; end=$(date +%s); printf "%s\t%s\t%s\t%s\n" "$id" "$rc" "$((end-start))" "$(sha256sum "$out" | cut -c1-64)" >> $LOG; }
mkdir -p $S/r5p/a01 $S/r5p/a05 $S/r5p/a08 $S/r5p/a09 $S/r5p/da01 $S/r5p/da03 $S/r5p/da04 $S/r5p/da05
run RV5-B-A01 $O/RV5-B-A01.json $B $E SCRATCH=$S/r5p/a01 python3 -B RV5-B-A01-first-admission-channel.py
run RV5-B-A04 $O/RV5-B-A04.json $B $E python3 -B RV5-B-A04-calculator-extensions.py
run RV5-B-A05 $O/RV5-B-A05.json $B $E SCRATCH=$S/r5p/a05 python3 -B RV5-B-A05-source-identity.py
run RV5-B-A08 $O/RV5-B-A08.json $B env -i PATH=/usr/bin:/bin HOME=/home/usain TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 SCRATCH=$S/r5p/a08 python3 -B RV5-B-A08-build-image-selects-bytes.py
run RV5-B-A09 $O/RV5-B-A09.json $B $E GOV=$L/gov-4.1.5 SCRATCH=$S/r5p/a09 python3 -B RV5-B-A09-floor-class-kernels.py
run RV5-B-A12 $O/RV5-B-A12.json $B $E python3 -B RV5-B-A12-machine-classes.py
run RV5-D-A01 $O/RV5-D-A01.json $D $E GOV=$L/gov-4.1.5 SCRATCH=$S/r5p/da01 python3 -B RV5-D-A01-registered-content-not-first-hand.py
run RV5-D-A03 $O/RV5-D-A03.json $D $E SCRATCH=$S/r5p/da03 python3 -B RV5-D-A03-user-writable-install-anchoring.py
run RV5-D-A04 $O/RV5-D-A04.json $D $E GOV=$L/gov-4.1.5 SCRATCH=$S/r5p/da04 python3 -B RV5-D-A04-conformance-vector-gaps.py
run RV5-D-A05 $O/RV5-D-A05.json $D $E SCRATCH=$S/r5p/da05 python3 -B RV5-D-A05-forward-compat-new-constitutional-file.py
run RV5-D-A07 $O/RV5-D-A07.json $D $E python3 -B RV5-D-A07-plan-regression-detection.py
echo DONE >> $LOG
