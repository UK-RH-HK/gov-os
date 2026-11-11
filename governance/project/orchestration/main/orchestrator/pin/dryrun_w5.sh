#!/usr/bin/env bash
# Re-pin window 5's dry run (DEC-1125 (3), the lift): gov's wheel built twice from clean exports of one commit, with
# SOURCE_DATE_EPOCH the commit's time; prints the commit, the epoch and the two sha256 (they must be equal).
#     bash dryrun_w5.sh <commit12> <scratch dir>
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
C=$1; X=$2
FULL=$(git -C "$R" rev-parse --verify "$C^{commit}")
EPOCH=$(git -C "$R" log -1 --format=%ct "$FULL")
mkdir -p "$X"
for n in 1 2; do
  rm -rf "$X/src-$n" "$X/wheel-$n"; mkdir -p "$X/src-$n" "$X/wheel-$n"
  git -C "$R" archive "$FULL" | tar -x -C "$X/src-$n"
  SOURCE_DATE_EPOCH=$EPOCH python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$X/wheel-$n" "$X/src-$n" > /dev/null
done
a=$(sha256sum "$X/wheel-1/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1)
b=$(sha256sum "$X/wheel-2/gov-0.1.0-py3-none-any.whl" | cut -d' ' -f1)
echo "commit ${FULL:0:12} epoch $EPOCH"
echo "build 1 $a"
echo "build 2 $b"
[ "$a" = "$b" ] && echo "SAME" || { echo "DIFFER"; exit 1; }
