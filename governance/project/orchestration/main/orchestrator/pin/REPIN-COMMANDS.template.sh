#!/usr/bin/env bash
# The emergency re-pin, window 1 (DEC-1037 (1); P1-REPIN-EMERGENCY (a)): the owner's act, by the owner's operator.
# Run in a PLAIN TERMINAL (not inside a Claude session: it reinstalls gov, DEC-928 item 3):
#     bash REPIN-COMMANDS-@C@.sh 2>&1 | tee ~/repin-@C@.log
# It stops at the first failure. Before the switch (parts A-C) a failure changes nothing that sessions use (the new
# pin sits beside the old one). After the switch (part D), a failed check switches straight back to the old pin by
# itself and prints ROLLED BACK: then tell the CTO. Then ACT-QUERY-GPU-2 (its own file), in the same window.
set -euo pipefail
R=/home/usain/Dynamic-Agentic-Engineering-OS
P="$HOME/.local/share/gov-os"
C=@C@                  # the owner's head for window 1 (16:5x: from a7182f6c, which carries fix (b); W2-122/123 in window 2)
FULL=@FULL@
EPOCH=@EPOCH@          # the commit's time: the wheel is reproducible
SHA=@SHA@              # the CTO's dry run: two builds from clean exports, the same bytes
OLD=5c401220
N="$P/pin-$C"
W="$P/wheels/$C/gov-0.1.0-py3-none-any.whl"
O="$R/.gov-runtime/scratch/orchestrator/pin"
stop() { echo; echo "STOP: $1"; echo "Nothing was switched: ~/.local/bin/gov is still pin-$OLD. Tell the CTO."; exit 1; }

echo "== 0. preconditions"
[ "$(readlink -f "$HOME/.local/bin/gov")" = "$(readlink -f "$P/pin-$OLD/bin/gov")" ] || stop "~/.local/bin/gov is not pin-$OLD"
[ ! -e "$N" ] || stop "$N already exists"
[ "$(git -C "$R" rev-parse "$C^{commit}")" = "$FULL" ] || stop "commit $C is not $FULL"
[ -f "$R/.gov-runtime/scratch/orchestrator/log/act-in-progress.txt" ] || stop "the CTO's hold (log/act-in-progress.txt) is not written"
echo ok

echo "== A. the wheel of $C (built from a clean export, checked against the dry run) and its own environment"
rm -rf "/tmp/gov-pin-src-$C" && mkdir "/tmp/gov-pin-src-$C"
git -C "$R" archive "$FULL" | tar -x -C "/tmp/gov-pin-src-$C"
mkdir -p "$P/wheels/$C"
SOURCE_DATE_EPOCH=$EPOCH python3 -m pip wheel -q --no-deps --no-build-isolation --no-index -w "$P/wheels/$C" "/tmp/gov-pin-src-$C"
echo "$SHA  $W" | sha256sum -c - || stop "the wheel's sha256 is not the dry run's"
python3 -m venv --system-site-packages "$N"
"$N/bin/python" -m pip install -q --no-deps --no-index "$W"
head -1 "$N/bin/gov"

echo "== B. every check before the switch, through $N by its path (the guard's included)"
bash "$O/repin3_checks.sh" "$N" "/tmp/repin-$C-checks" | tee "/tmp/repin-$C-checks.txt"
tail -1 "/tmp/repin-$C-checks.txt" | grep -q '^ALL CHECKS PASS' || stop "a check before the switch failed (above)"

echo "== C. the quiet point"
TB="$R/.gov-runtime/scratch/orchestrator/tools/tree_busy.sh"  # never pgrep -f: it matches its own command line
for job in close_build.py nightly.sh "merge_queue.py run"; do
  if bash "$TB" --cmd "$job" >/dev/null; then stop "a close, the nightly or a landing is running ($job)"; fi
done
echo "processes of the old pin now (expected: none, or sub-second hooks; they finish on the old code, which stays):"
bash "$TB" --cmd "$P/pin-$OLD" || true

echo "== D. the switch (an atomic rename: no moment without a gov)"
rollback() {
  ln -s "$P/pin-$OLD/bin/gov" "$HOME/.local/bin/gov.new" && mv -Tf "$HOME/.local/bin/gov.new" "$HOME/.local/bin/gov"; hash -r
  echo; echo "ROLLED BACK: $1"; echo "~/.local/bin/gov -> $(readlink -f "$HOME/.local/bin/gov"). Tell the CTO."; exit 1
}
ln -s "$N/bin/gov" "$HOME/.local/bin/gov.new" && mv -Tf "$HOME/.local/bin/gov.new" "$HOME/.local/bin/gov"; hash -r
[ "$(readlink -f "$HOME/.local/bin/gov")" = "$(readlink -f "$N/bin/gov")" ] || rollback "the link does not name pin-$C"
echo "~/.local/bin/gov -> $(readlink -f "$HOME/.local/bin/gov")"
smoke=$(bash "$O/smoke_repin2.sh" 2>&1); echo "$smoke"
grep -q '^1 Read README.md: exit 0' <<<"$smoke" && ! grep -q '^1 .*deny' <<<"$smoke" || rollback "the guard refused a plain Read"
grep -q '^2 Write tests/acceptance: exit 0; "permissionDecision": *"deny"' <<<"$smoke" \
  || grep -q '^2 Write tests/acceptance: exit 2' <<<"$smoke" || rollback "the guard did not refuse an acceptance-test write"
grep -q '^3 no judge reachable: exit 2' <<<"$smoke" || rollback "the guard did not refuse with no judge"
(cd "$HOME/gov-os-worktrees/W2-00-store" && GOV_RERANK_GPU_WAIT_S=0 gov retrieve "what decides a close" --json > "/tmp/repin-$C-search.json") \
  || rollback "a search through the new pin failed"
python3 -c "import json,sys; f=json.load(open(sys.argv[1]))['result']['facets']; sys.exit(0 if all(f[k]['available'] for k in ('lexical','semantic')) else 1)" \
  "/tmp/repin-$C-search.json" || rollback "a search through the new pin lost a facet"
echo "a search through ~/.local/bin/gov: both facets available"

echo "== E. the registry entry (refuses unless A and D hold), committed as the owner's"
python3 "$O/repin3_registry.py" "$C" "$SHA" "$EPOCH"
git -C "$R" commit -m "DEC-1037: the emergency re-pin, gov from the wheel of $C (window 1: fix (b) of DEC-1033)" \
  --trailer "Task: decision-record" --trailer "Implements: DEC-1037" --trailer "Role: owner" -- governance/project/tool-registry.yaml
echo; echo "RE-PIN DONE: pin-$C is live; pin-$OLD kept for the rollback. Next: ACT-QUERY-GPU-2 (same window)."

# ---- Rollback by hand (one step; if ACT-QUERY-GPU-2 has run, undo it FIRST: the old pin refuses GPU vectors) -------
#   ln -s ~/.local/share/gov-os/pin-5c401220/bin/gov ~/.local/bin/gov.new && mv -Tf ~/.local/bin/gov.new ~/.local/bin/gov; hash -r
#   then revert the registry commit.
