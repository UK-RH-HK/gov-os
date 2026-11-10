#!/usr/bin/env bash
# D-10's full run on the whole machine (owner, 2026-11-10 after DEC-1122): nightly.sh in day mode on a fresh clone of
# w2/integrate's head, with the heavy-slot CPU limits lifted for this run only (NIGHTLY_HEAVY points at no gate, so
# `-n auto` takes PYTEST_XDIST_AUTO_NUM_WORKERS), the parallel workers sized to memory and cores, then the `lifted`
# suite once, report-only (D4-LIST §2). A vmstat sampler records swap activity every 30 s. Writes only under
# log/d10/<run>/. No commits on w2/integrate while it runs.
#   d10_run.sh <run name, e.g. run1> <workers>        (LIFTED_ONLY=1: the lifted step alone, no nightly)
# Fix 2026-11-10 19:2x (session 8ddb8b14): run 1's lifted step ran nothing (exit 5): the guard list's `rep:` lines were
# passed to pytest as a path. Now the prefix is stripped and d10_lifted_only.py keeps only the lifted cases (~8,604).
set -u
RUN=${1:?run name}; W=${2:?workers}
ROOT=/home/usain/Dynamic-Agentic-Engineering-OS
ORCH=$ROOT/.gov-runtime/scratch/orchestrator
D=$ORCH/log/d10/$RUN
mkdir -p "$D"
# Setup fix after run 1 (group A): a short TMPDIR below /tmp, so the socket helpers find a folder (they refuse /tmp itself).
export TMPDIR=${D10_TMPDIR:-/tmp/gov-d10}; mkdir -p "$TMPDIR"
echo "$$" > "$D/pid"
head=$(git -C "$ROOT" rev-parse HEAD)
{ echo "run: $RUN"; echo "tmpdir: $TMPDIR"; grep -E "^Sig(Ign|Blk)" /proc/$$/status | tr "\n" " "; echo; echo "head: ${head:0:12}"; echo "workers: $W (nproc $(nproc))"; date -u "+start: %F %T UTC"; } > "$D/summary.txt"
free -m > "$D/free-before.txt"
( vmstat -t 30 > "$D/vmstat.log" 2>&1 ) & VM=$!
t0=$(date +%s)
if [ "${LIFTED_ONLY:-0}" = 1 ]; then echo "nightly: skipped (LIFTED_ONLY=1)" >> "$D/summary.txt"; n_exit=skipped; else
env NIGHTLY_HEAVY=/nonexistent/no-heavy-gate PYTEST_XDIST_AUTO_NUM_WORKERS="$W" \
  bash "$ROOT/governance/project/orchestration/nightly/nightly.sh" day > "$D/nightly.out" 2>&1
n_exit=$?
fi
t1=$(date +%s)
{ echo "nightly exit: $n_exit"; echo "nightly wall_s: $((t1 - t0))"; } >> "$D/summary.txt"
# The lifted suite once, report-only, on the same head, from the nightly's clone if it was kept, else the main tree's
# committed state is not used: a fresh clone.
LC=$D/lifted-clone
git clone -q --no-hardlinks --single-branch -b w2/integrate "file://$ROOT" "$LC" && git -C "$LC" checkout -q "$head"
t2=$(date +%s)
# Only the paths the lifted lists name (folders, files or cases; there is no lifted-only switch), so the default cases
# are not run a second time except those sharing a file with a lifted entry.
mapfile -t LIFTED < <(cat "$LC"/tests/optin-lifted.txt "$LC"/tests/optin-lifted-guard.txt | grep -v '^#' | grep -v '^[[:space:]]*$' \
  | sed -E 's/^[a-z-]+:[[:space:]]+//; s/[[:space:]].*//; s/::.*//' | sort -u)
echo "lifted paths: ${#LIFTED[@]}" >> "$D/summary.txt"
( cd "$LC" && env -u PYTEST_ADDOPTS -u PYTEST_PLUGINS PYTHONPATH="$LC/src:$ORCH/tools" PYTEST_XDIST_AUTO_NUM_WORKERS="$W" \
  python3 -m pytest "${LIFTED[@]}" -n auto -q -p no:cacheprovider -p d10_lifted_only --no-header --optin=lifted -o tmp_path_retention_policy=failed \
  --junitxml="$D/lifted.xml" ) > "$D/lifted.out" 2>&1
l_exit=$?
t3=$(date +%s)
kill "$VM" 2>/dev/null
free -m > "$D/free-after.txt"
{ echo "lifted exit: $l_exit (report-only)"; echo "lifted wall_s: $((t3 - t2))"; date -u "+end: %F %T UTC";
  echo "swap in/out (vmstat si+so, KB/s, max of 30 s samples): $(awk 'NR>2 && $7~/^[0-9]+$/ {s=$7+$8; if (s>m) m=s} END {print m+0}' "$D/vmstat.log")";
  echo "min free memory MB (vmstat free+cache): $(awk 'NR>2 && $4~/^[0-9]+$/ {f=($4+$6)/1024; if (m==""||f<m) m=f} END {printf "%d", m}' "$D/vmstat.log")"; } >> "$D/summary.txt"
rm -rf "$LC"
echo done > "$D/exit"
