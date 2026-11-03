#!/usr/bin/env bash
# The emergency re-pin's dry run (DEC-1037 (1), window 1): build the wheel of commit $1 (in repository $2, default the
# main tree) twice from clean exports, print both sha256 and whether they agree, and install it into a scratch venv
# ($3) for the checks before the switch. Installs nothing under ~/.local; touches neither the pin nor ~/.local/bin.
#     bash repin3_dry.sh <commit> [<repo>] [<scratch dir>]
set -euo pipefail
C=$1
R=${2:-/home/usain/Dynamic-Agentic-Engineering-OS}
S=${3:-/tmp/claude-1000/-home-usain-Dynamic-Agentic-Engineering-OS/07f25884-3736-441a-8f80-ff5cef3fd2e0/scratchpad/repin3}
FULL=$(git -C "$R" rev-parse "$C^{commit}")
EPOCH=$(git -C "$R" log -1 --format=%ct "$FULL")
echo "commit $FULL epoch $EPOCH"
mkdir -p "$S"
for n in 1 2; do
  rm -rf "$S/src-$n" "$S/wheel-$n"
  mkdir -p "$S/src-$n" "$S/wheel-$n"
  git -C "$R" archive "$FULL" | tar -x -C "$S/src-$n"
  SOURCE_DATE_EPOCH="$EPOCH" python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$S/wheel-$n" "$S/src-$n" > /dev/null
done
a=$(sha256sum "$S"/wheel-1/*.whl | cut -d' ' -f1); b=$(sha256sum "$S"/wheel-2/*.whl | cut -d' ' -f1)
echo "sha256 build 1 $a"; echo "sha256 build 2 $b"
[ "$a" = "$b" ] && echo "the two builds agree" || { echo "THE TWO BUILDS DIFFER"; exit 3; }
rm -rf "$S/venv"
python3 -m venv --system-site-packages "$S/venv"
"$S/venv/bin/python" -m pip install -q --no-deps --no-index "$S"/wheel-1/*.whl
echo "installed in $S/venv: $("$S/venv/bin/python" -E -c 'import gov; print(gov.__file__)')"
