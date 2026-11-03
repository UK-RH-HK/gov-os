#!/usr/bin/env bash
# The emergency re-pin's checks before the switch (DEC-1037 (1); P1-REPIN-EMERGENCY section 4 (a), step 4), all
# through the new pin's own environment by its path; nothing switched, ~/.local/bin untouched.
#     bash repin3_checks.sh <new pin dir, e.g. ~/.local/share/gov-os/pin-<H>> [<scratch dir>]
# Prints one line per check and a last line ALL CHECKS PASS, or "CHECK FAILED: <which>" and exits 1 at the first
# failure (then: do not switch; the old pin stays).
set -uo pipefail
N=${1:?the new pin directory}
S=${2:-$(mktemp -d)}
R=/home/usain/Dynamic-Agentic-Engineering-OS
T=$R/.gov-runtime/scratch/orchestrator/tools
STORE=$HOME/gov-os-worktrees/W2-00-store
mkdir -p "$S"
fail() { echo "CHECK FAILED: $1"; exit 1; }
ok() { echo "ok   $1"; }
SITE=$("$N/bin/python" -E -c 'import gov, os; print(os.path.dirname(gov.__file__))') || fail "the pin's gov does not import"
case "$SITE" in "$N"/*) ok "gov imports from the pin ($SITE)";; *) fail "gov imports from $SITE, not the pin";; esac

# 1. the commands
help=$("$N/bin/gov" --help 2>&1) || fail "gov --help"
for c in accept release retrieve context launch checkpoint; do grep -qw "$c" <<<"$help" || fail "gov --help lacks $c"; done
ok "gov --help lists accept, release, retrieve, context, launch, checkpoint"
"$N/bin/gov" accept --help >/dev/null 2>&1 || fail "gov accept --help"
"$N/bin/gov" launch --help >/dev/null 2>&1 || fail "gov launch --help"
ok "gov accept --help and gov launch --help"

# 2. fix (b) in the pin: no CPU-only gate
n=$(grep -c -E 'NOT_ON_CPU|_on_cpu' "$SITE/retrieval/semantic.py"); [ "$n" = 0 ] || fail "semantic.py still has the CPU-only gate ($n lines)"
ok "semantic.py has no NOT_ON_CPU or _on_cpu"

# 3. the dependencies
"$N/bin/python" -E -c 'import yaml, sqlite_vec, pytest, xdist, pytest_timeout' 2>/dev/null || fail "the dependencies do not import"
ok "yaml, sqlite_vec, pytest, xdist, pytest_timeout import"

# 4. a search: both facets available (no reranker wait: the slot rule is not what is checked here)
t0=$(date +%s.%N)
(cd "$STORE" && GOV_RERANK_GPU_WAIT_S=0 "$N/bin/gov" retrieve "what decides a close" --json > "$S/retrieve.json" 2> "$S/retrieve.err") \
  || fail "gov retrieve exit $? ($(tail -c 200 "$S/retrieve.err"))"
t=$(echo "$(date +%s.%N) - $t0" | bc)
python3 - "$S/retrieve.json" <<'EOF' || fail "gov retrieve: a facet unavailable"
import json, sys
f = json.load(open(sys.argv[1]))["result"]["facets"]
bad = [k for k in ("lexical", "semantic") if not f.get(k, {}).get("available")]
sys.exit(f"unavailable: {bad} {f}" if bad else 0)
EOF
ok "gov retrieve: lexical and semantic available, ${t} s"

# 5. context
(cd "$R" && "$N/bin/gov" context DAEO-sdxk --json > "$S/context.json" 2> "$S/context.err") || fail "gov context DAEO-sdxk --json ($(tail -c 200 "$S/context.err"))"
(cd "$R" && "$N/bin/gov" context --in-force > "$S/inforce.txt" 2> "$S/inforce.err") || fail "gov context --in-force ($(tail -c 200 "$S/inforce.err"))"
ok "gov context DAEO-sdxk --json and --in-force"

# 6. the hooks, each by its exact line in .claude/settings.json, with a HOME whose ~/.local/bin/gov is the new pin, in a
#    scratch clone of the main tree (a Stop hook may write a checkpoint)
FH=$S/home; mkdir -p "$FH/.local/bin"; ln -sfn "$N/bin/gov" "$FH/.local/bin/gov"
CL=$S/clone
[ -d "$CL/.git" ] || git clone -q --shared "$R" "$CL" || fail "the scratch clone"
for ev in SessionStart PreCompact Stop; do
  line=$(python3 -c "import json,sys; print(json.load(open('$R/.claude/settings.json'))['hooks'][sys.argv[1]][0]['hooks'][0]['command'])" "$ev")
  event="{\"session_id\":\"repin3-check\",\"hook_event_name\":\"$ev\",\"cwd\":\"$CL\",\"source\":\"resume\",\"trigger\":\"manual\",\"stop_hook_active\":false,\"transcript_path\":\"$S/none.jsonl\"}"
  printf '%s' "$event" | (cd "$CL" && env HOME="$FH" PATH=/usr/bin:/bin CLAUDE_PROJECT_DIR="$CL" GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk bash -c "$line") \
    > "$S/hook-$ev.out" 2> "$S/hook-$ev.err"
  code=$?
  [ $code = 0 ] || fail "the $ev hook exit $code ($(tail -c 200 "$S/hook-$ev.err"))"
done
[ "$(readlink -f "$FH/.local/bin/gov")" = "$(readlink -f "$N/bin/gov")" ] || fail "the scratch HOME's gov is not the pin"
ok "SessionStart, PreCompact and Stop hooks exit 0 under the new pin"

# 7. the guard: the 54 planted cases, ACT-GUARD-FIX-3's suite, and the hook's time, against the new pin's interpreter
export GOV_PIN_PY=$N/bin/python
python3 "$T/guard4_check.py" > "$S/guard4.txt" 2>&1; tail -1 "$S/guard4.txt" | grep -qx PASS || fail "guard4_check.py ($(grep FAIL "$S/guard4.txt" | head -3))"
ok "guard4_check.py: PASS"
(cd "$T" && GUARD_FIX3_HOOK=$R/.claude/hooks/pretooluse.py bash "$T/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider test_guard_fix_3.py > "$S/fix3.txt" 2>&1) \
  || fail "test_guard_fix_3.py ($(tail -1 "$S/fix3.txt"))"
ok "test_guard_fix_3.py: $(tail -1 "$S/fix3.txt")"
timing=$(python3 "$T/hook_timing.py")
python3 - "$timing" <<'EOF' || fail "hook_timing.py: $timing"
import re, sys
s = sys.argv[1]
times = [float(x) for x in re.findall(r"[0-9.]+", s.split("seconds", 1)[1])]
sys.exit(0 if s.startswith("exit 0") and sorted(times)[len(times) // 2] < 2.0 else 1)
EOF
ok "hook_timing.py: $timing"
echo "ALL CHECKS PASS ($N)"
