#!/usr/bin/env bash
# Re-pin window 3's checks before the switch (DEC-1068 (e); repin3_checks.sh, window 2's, with the store named and the
# store's own checks added), all through the new pin's own environment by its path; nothing switched, no gov link
# touched.
#     bash repin5_checks.sh <new pin dir> <scratch dir> <store tree> <the commit's full id>
# <store tree>: the integration store refreshed at the commit (the link ~/gov-os-worktrees/W2-00-store in the ACT).
# Prints one line per check and a last line ALL CHECKS PASS, or "CHECK FAILED: <which>" and exits 1 at the first
# failure (then: do not switch; the old pin stays).
# The search uses the real HOME: the user's one shared reranker (~/.cache/gov-os/rerank.sock) and the machine-wide
# vector cache are HOME's. The hooks run with a scratch HOME whose .local/bin/gov is the new pin (as window 2).
set -uo pipefail
N=${1:?the new pin directory}
S=${2:?the scratch directory}
STORE=${3:?the store tree}
FULL=${4:?the commit}
R=/home/usain/Dynamic-Agentic-Engineering-OS
T=$R/.gov-runtime/scratch/orchestrator/tools
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

# 2. no CPU-only gate; the padded reranker bound is the pin's (DEC-1067 (f), the CTO's bound of 2026-11-04)
n=$(grep -c -E 'NOT_ON_CPU|_on_cpu' "$SITE/retrieval/semantic.py"); [ "$n" = 0 ] || fail "semantic.py still has the CPU-only gate ($n lines)"
ok "semantic.py has no NOT_ON_CPU or _on_cpu"
"$N/bin/python" -E -c 'import gov.retrieval.rerank as r, sys; sys.exit(0 if (r.MAX_REQUEST_TEXTS, r.MAX_REQUEST_CHARS) == (16, 24000) and hasattr(r, "requests") else 1)' \
  || fail "the pin's rerank.py lacks the padded bound (16 texts, 24,000 characters)"
ok "rerank.py: at most 16 texts and 24,000 padded characters a request"

# 3. the dependencies
"$N/bin/python" -E -c 'import yaml, sqlite_vec, pytest, xdist, pytest_timeout' 2>/dev/null || fail "the dependencies do not import"
ok "yaml, sqlite_vec, pytest, xdist, pytest_timeout import"

# 4. the store: at the commit, its vectors made with headers, and a search on it with both facets and the shared reranker
head=$(git -C "$STORE" rev-parse HEAD) || fail "the store tree $STORE"
[ "$head" = "$FULL" ] || fail "the store is at $head, not $FULL"
st=$(python3 - "$STORE/.gov-runtime/store.db" <<'EOF'
import sqlite3, sys
c = sqlite3.connect(f"file:{sys.argv[1]}?mode=ro", uri=True)
h = c.execute("SELECT value FROM semantic_pin WHERE key = 'embed_headers'").fetchone()
n = c.execute("SELECT count(*) FROM semantic_vector").fetchone()[0]
print(h[0] if h else "absent", n)
EOF
) || fail "the store's semantic tables cannot be read"
[ "${st%% *}" = true ] || fail "the store's vectors are not made with headers (embed_headers: ${st%% *})"
ok "the store $(basename "$(readlink -f "$STORE")") at ${FULL:0:12}: embed_headers true, ${st##* } vectors"
t0=$(date +%s.%N)
(cd "$STORE" && "$N/bin/gov" retrieve "what decides a close" --json > "$S/retrieve.json" 2> "$S/retrieve.err") \
  || fail "gov retrieve exit $? ($(tail -c 200 "$S/retrieve.err"))"
t=$(echo "$(date +%s.%N) - $t0" | bc)
why=$(python3 - "$S/retrieve.json" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
f = r["facets"]
bad = [k for k in ("lexical", "semantic") if not f.get(k, {}).get("available")]
by = (r.get("rerank") or {}).get("by")
if bad:
    print(f"unavailable: {bad} {f}")
elif by != "service":
    print(f"rerank.by is {by!r}, not the shared service: {r.get('rerank')}")
EOF
) || fail "gov retrieve: its answer cannot be read"
[ -z "$why" ] || fail "gov retrieve: $why"
ok "gov retrieve on the store: lexical and semantic available, rerank.by service, ${t} s"

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
  event="{\"session_id\":\"repin5-check\",\"hook_event_name\":\"$ev\",\"cwd\":\"$CL\",\"source\":\"resume\",\"trigger\":\"manual\",\"stop_hook_active\":false,\"transcript_path\":\"$S/none.jsonl\"}"
  printf '%s' "$event" | (cd "$CL" && env HOME="$FH" PATH=/usr/bin:/bin CLAUDE_PROJECT_DIR="$CL" GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk bash -c "$line") \
    > "$S/hook-$ev.out" 2> "$S/hook-$ev.err"
  code=$?
  [ $code = 0 ] || fail "the $ev hook exit $code ($(tail -c 200 "$S/hook-$ev.err"))"
done
[ "$(readlink -f "$FH/.local/bin/gov")" = "$(readlink -f "$N/bin/gov")" ] || fail "the scratch HOME's gov is not the pin"
ok "SessionStart, PreCompact and Stop hooks exit 0 under the new pin"

# 7. the guard, against the new pin's interpreter: the planted cases (guard4_check.py), the live hook's suites as
#    ACT-G14b checked them (ACT-GUARD-FIX-4's, G-14's and tests/unit/hooks/test_live_hook.py, D-4's cut of them), and
#    ACT-GUARD-FIX-3's suite compared with the old pin's: since ACT-GUARD-FIX-4 (3bc25241, after window 2) the live
#    hook lets the unresolvable targets through by design (its LET_THROUGH), so FIX-3's suite fails those cases under
#    either pin; the check is that the new pin fails exactly the old pin's.
export GOV_PIN_PY=$N/bin/python
OLD_PY=${REPIN_OLD_PY:-$HOME/.local/share/gov-os/pin-9894b0cf/bin/python}
HOOK=$R/.claude/hooks/pretooluse.py
PT="python3 -m pytest -q -n 6 -o tmp_path_retention_policy=failed -p no:cacheprovider"
python3 "$T/guard4_check.py" > "$S/guard4.txt" 2>&1; tail -1 "$S/guard4.txt" | grep -qx PASS || fail "guard4_check.py ($(grep FAIL "$S/guard4.txt" | head -3))"
ok "guard4_check.py: PASS ($(grep -c '^ok ' "$S/guard4.txt") cases)"
suite() {  # $1 label, $2 output name, then the environment and the test path
  local label=$1 out=$S/$2; shift 2
  (cd "$R" && env "$@" > "$out" 2>&1) || true
  tail -1 "$out" | grep -q ' passed' && ! tail -1 "$out" | grep -q -E 'failed|error' || fail "$label ($(tail -1 "$out"))"
  ok "$label: $(tail -1 "$out" | sed 's/ in [0-9.]*s.*//')"
}
suite "test_guard_fix_4.py" fix4.txt GUARD_FIX4_HOOK="$HOOK" bash "$T/heavy_slot.sh" $PT \
  .gov-runtime/scratch/orchestrator/drafts/act-guard-fix-4/test_guard_fix_4.py
suite "test_g14.py" g14.txt G14_HOOK="$HOOK" bash "$T/heavy_slot.sh" $PT .gov-runtime/scratch/orchestrator/drafts/g14/test_g14.py
suite "tests/unit/hooks/test_live_hook.py" live.txt GOV_LIVE_HOOK_PY="$N/bin/python" bash "$T/heavy_slot.sh" $PT \
  tests/unit/hooks/test_live_hook.py
for who in new old; do
  py=$N/bin/python; [ $who = old ] && py=$OLD_PY
  (cd "$T" && GOV_PIN_PY=$py GUARD_FIX3_HOOK=$HOOK bash "$T/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -rf \
     test_guard_fix_3.py > "$S/fix3-$who.txt" 2>&1) || true
  grep '^FAILED' "$S/fix3-$who.txt" | sed 's/ - .*//' | sort > "$S/fix3-$who.failed"
done
cmp -s "$S/fix3-new.failed" "$S/fix3-old.failed" && grep -q ' passed' <(tail -1 "$S/fix3-new.txt") \
  || fail "test_guard_fix_3.py: the new pin's failures differ from the old pin's ($(tail -1 "$S/fix3-new.txt") / $(tail -1 "$S/fix3-old.txt"))"
ok "test_guard_fix_3.py: $(tail -1 "$S/fix3-new.txt" | sed 's/ in [0-9.]*s.*//'), the same $(wc -l < "$S/fix3-new.failed") cases as pin-9894b0cf (ACT-GUARD-FIX-4's LET_THROUGH)"
timing=$(python3 "$T/hook_timing.py")
python3 - "$timing" <<'EOF' || fail "hook_timing.py: $timing"
import re, sys
s = sys.argv[1]
times = [float(x) for x in re.findall(r"[0-9.]+", s.split("seconds", 1)[1])]
sys.exit(0 if s.startswith("exit 0") and sorted(times)[len(times) // 2] < 2.0 else 1)
EOF
ok "hook_timing.py: $timing"
echo "ALL CHECKS PASS ($N)"
