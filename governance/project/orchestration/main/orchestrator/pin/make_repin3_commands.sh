#!/usr/bin/env bash
# Writes REPIN-COMMANDS-<C>.sh for window 1 (DEC-1037 (1)) from REPIN-COMMANDS.template.sh: the dry run builds the
# wheel of <commit> twice (repin3_dry.sh), the sha256 both builds agree on, the commit's full id and time are filled in.
#     bash make_repin3_commands.sh <commit>
set -euo pipefail
O=$(cd "$(dirname "$0")" && pwd)
R=/home/usain/Dynamic-Agentic-Engineering-OS
FULL=$(git -C "$R" rev-parse "$1^{commit}")
C=${FULL:0:8}
EPOCH=$(git -C "$R" log -1 --format=%ct "$FULL")
D=$HOME/.cache/gov-os-repin3-dry/$C
out=$(bash "$O/repin3_dry.sh" "$FULL" "$R" "$D")
echo "$out"
grep -q '^the two builds agree$' <<<"$out" || { echo "the two builds differ: no command file written"; exit 3; }
SHA=$(sed -n 's/^sha256 build 1 //p' <<<"$out")
sed -e "s/@C@/$C/g" -e "s/@FULL@/$FULL/g" -e "s/@EPOCH@/$EPOCH/g" -e "s/@SHA@/$SHA/g" "$O/REPIN-COMMANDS.template.sh" \
  > "$O/REPIN-COMMANDS-$C.sh"
! grep -n '@[A-Z]*@' "$O/REPIN-COMMANDS-$C.sh" || { echo "a placeholder left"; exit 4; }
bash -n "$O/REPIN-COMMANDS-$C.sh"
echo "written: $O/REPIN-COMMANDS-$C.sh (commit $FULL, epoch $EPOCH, sha256 $SHA); dry install: $D/venv"
