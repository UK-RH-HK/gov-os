#!/usr/bin/env bash
# Not-lowered check (no tree copy): per revised test file, def test_ / parametrize / skip / xfail counts at
# the starting head 73c18fea1e1f, at w2/integrate, and at HEAD; then collect-only of the files at HEAD.
set -u
T=/home/usain/gov-os-worktrees/W2-90b
OUT=$T/.gov-runtime/scratch/land/notlowered
mkdir -p $OUT
git -C $T diff --name-only 8723754f3fec 73c18fea1e1f -- tests/acceptance | grep '/test_.*\.py$' > $OUT/files.txt
printf '%-70s %s\n' file "start(test/param/skip/xfail) integrate(...) head(...)"
for f in $(cat $OUT/files.txt); do
  row="$f"
  for rev in 73c18fea1e1f w2/integrate HEAD; do
    body=$(git -C $T show $rev:$f 2>/dev/null)
    a=$(grep -c '^ *def test_' <<< "$body"); b=$(grep -c 'pytest.mark.parametrize' <<< "$body")
    c=$(grep -c 'pytest.skip\|mark.skip' <<< "$body"); d=$(grep -c 'xfail' <<< "$body")
    row="$row $a/$b/$c/$d"
  done
  echo "$row"
done
env HOME=$T/.gov-runtime/scratch/empty-home PYTHONUSERBASE=/home/usain/.local PYTHONPATH=$T/src TMPDIR=/tmp/gov-os-lead-W2-90b \
  python3 -m pytest $(sed "s#^#$T/#" $OUT/files.txt) --collect-only -q -p no:cacheprovider > $OUT/after.txt 2>&1
echo "collect exit $?: $(tail -1 $OUT/after.txt)"
