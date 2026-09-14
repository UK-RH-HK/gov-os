#!/bin/bash
S=<scratch>; P=<scratch>/export/release/root-of-trust/4.1.6; LOG=$S/out/D/bg-log.tsv; : > $LOG
E="env -i PATH=/usr/bin:/bin HOME=$S/home TMPDIR=$S/tmp PYTHONDONTWRITEBYTECODE=1 GOV_KERNEL_CACHE=$S/kcache PACK=$P RUSTC=<home>/.cargo/bin/rustc RUSTUP_HOME=<home>/.rustup CARGO_HOME=<home>/.cargo"
cd $S/probes/D
s=$(date +%s); $E A02_SCRATCH=$S/work/D/a02 python3 -B RV7-D-A02-cross-axis-reproduction.py > $S/out/D/RV7-D-A02.json 2> $S/out/D/RV7-D-A02.stderr; printf "A02\t%s\t%s\n" $? $(($(date +%s)-s)) >> $LOG
s=$(date +%s); $E python3 -B RV7-D-A06-vector-mutation-sensitivity.py $S/export $S/work/D/a06 > $S/out/D/RV7-D-A06.json 2> $S/out/D/RV7-D-A06.stderr; printf "A06\t%s\t%s\n" $? $(($(date +%s)-s)) >> $LOG
echo DONE >> $LOG
