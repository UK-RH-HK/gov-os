#!/usr/bin/env bash
# Re-pin window 5's checks before the switch (DEC-1125 (3) (i), the lift; repin6_checks.sh, window 4's, with section 3c
# for the builds since pin-bcea09060ebc), all through the new pin's own environment by its path; nothing switched, no
# gov link touched.
#     bash repin7_checks.sh <new pin dir> <scratch dir> <store tree> <the commit the store is at, full id>
# <store tree>: the integration store refreshed at that commit (the link ~/gov-os-worktrees/W2-00-store in the ACT).
# Prints one line per check and a last line ALL CHECKS PASS, or "CHECK FAILED: <which>" and exits 1 at the first
# failure (then: do not switch; the old pin stays).
# Named reds that are NOT gates (DEC-1125 (1), DEC-1123 (3)): the warm real-model query latency (W1-19, W2-13; this
# script measures no p95: it times one search and one hook only); the trailers family (a warning until W2-115; no
# trailers check runs here). Four cases of g14 are expected red BY NAME while W2-141's hook is live (row 88): see 7.
# The search uses the real HOME: the user's one shared reranker (~/.cache/gov-os/rerank.sock) and the machine-wide
# vector cache are HOME's. The hooks run with a scratch HOME whose .local/bin/gov is the new pin (as window 2).
set -uo pipefail
N=${1:?the new pin directory}
S=${2:?the scratch directory}
STORE=${3:?the store tree}
FULL=${4:?the commit the store is at}
R=/home/usain/Dynamic-Agentic-Engineering-OS
T=$R/.gov-runtime/scratch/orchestrator/tools
STAGED=${REPIN_STAGED_HOOK:-$R/docs/changes/W2-141-hook}
mkdir -p "$S"
fail() { echo "CHECK FAILED: $1"; exit 1; }
ok() { echo "ok   $1"; }
SITE=$("$N/bin/python" -E -c 'import gov, os; print(os.path.dirname(gov.__file__))') || fail "the pin's gov does not import"
case "$SITE" in "$N"/*) ok "gov imports from the pin ($SITE)";; *) fail "gov imports from $SITE, not the pin";; esac
PY=("$N/bin/python" -E -c)

# 1. the commands
help=$("$N/bin/gov" --help 2>&1) || fail "gov --help"
for c in accept release retrieve context launch checkpoint brief links plan resources; do grep -qw "$c" <<<"$help" || fail "gov --help lacks $c"; done
ok "gov --help lists accept, release, retrieve, context, launch, checkpoint, brief, links, plan, resources"
"$N/bin/gov" accept --help >/dev/null 2>&1 || fail "gov accept --help"
"$N/bin/gov" launch --help 2>&1 | grep -q -- '--gate-override' || fail "gov launch --help names no --gate-override (W2-20)"
ok "gov accept --help and gov launch --help (with --gate-override)"

# 2. no CPU-only gate; the padded reranker bound is the pin's, and no private reranker (W2-137: 64 texts, W2-145)
n=$(grep -c -E 'NOT_ON_CPU|_on_cpu' "$SITE/retrieval/semantic.py"); [ "$n" = 0 ] || fail "semantic.py still has the CPU-only gate ($n lines)"
ok "semantic.py has no NOT_ON_CPU or _on_cpu"
"${PY[@]}" 'import gov.retrieval.rerank as r, sys; sys.exit(0 if (r.MAX_REQUEST_TEXTS, r.MAX_REQUEST_CHARS) == (64, 24000) and hasattr(r, "requests") else 1)' \
  || fail "the pin's rerank.py lacks the bound of window 5 (64 texts, 24,000 padded characters)"
ok "rerank.py: at most 64 texts (W2-137) and 24,000 padded characters a request"

# 3. the dependencies
"${PY[@]}" 'import yaml, sqlite_vec, pytest, xdist, pytest_timeout' 2>/dev/null || fail "the dependencies do not import"
ok "yaml, sqlite_vec, pytest, xdist, pytest_timeout import"

# 3b. window 4's builds stay in the pin (DEC-1087)
grep -q 'empty_cache' "$SITE/retrieval/rerank_service.py" || fail "rerank_service.py does not release its GPU memory after a request (W2-112)"
"$N/bin/gov" links --help >/dev/null 2>&1 || fail "gov links --help (W2-129)"
"$N/bin/gov" rebuild --help 2>&1 | grep -q -- '--integration' || fail "gov rebuild offers no --integration (W2-116)"
grep -q 'GOV_STORE' "$SITE/launch/launcher.py" || fail "the launcher sets no GOV_STORE (W2-116 S3)"
"${PY[@]}" 'import gov.retrieval.retrieve as r, sys; sys.exit(0 if getattr(r, "ITEM_CHARS", None) == 4000 and callable(getattr(r, "capped", None)) else 1)' || fail "retrieve.py has no line cap (W2-135)"
grep -q 'evaluation_families' "$SITE/retrieval/measure.py" || fail "measure.py has no source families (W2-61h S7)"
ok "window 4's builds: W2-112's release, gov links, gov rebuild --integration, the launcher's GOV_STORE, the line cap, the measure's families"
"${PY[@]}" 'import gov.retrieval.pool' 2>/dev/null || fail "gov.retrieval.pool does not import (W2-32 S11)"
d=$(mktemp -d "$S/pool.XXXX"); mkdir -p "$d/governance/project"
printf 'pool:\n  meaning_uncut: true\n  route_depth: 60\n  rerank_depth: 40\n  per_file_first10: 2\n  drop_nested: true\n' > "$d/governance/project/retrieval.yaml"
"${PY[@]}" 'import sys; from pathlib import Path; from gov.retrieval import pool; pool.settings(Path(sys.argv[1]))' "$d" 2>/dev/null \
  || fail "the new pin does not accept the five pool settings (W2-32 S11)"
"${PY[@]}" 'import sys; from pathlib import Path; from gov.retrieval import pool; pool.settings(Path(sys.argv[1]))' "$R" 2> "$S/pool-real.err" \
  || fail "the new pin does not accept the main tree's own retrieval.yaml ($(tail -c 200 "$S/pool-real.err"))"
ok "W2-32 S11: the pool module; the new pin accepts the five pool settings, and the main tree's own retrieval.yaml (the pool is on since window 4)"

# 3c. window 5's builds are in the pin (DEC-1087, DEC-1125 (3): what changed since pin-bcea09060ebc)
"${PY[@]}" 'import gov.retrieval.rerank as r, sys; sys.exit(0 if not hasattr(r, "_started") and getattr(r, "RECALL_S", None) == 10.0 else 1)' \
  || fail "rerank.py still starts a private reranker, or lacks the failed-ask memory (W2-145)"
"${PY[@]}" 'import gov.retrieval.rerank_service as s, sys; sys.exit(0 if callable(getattr(s, "take_free_slots", None)) and s.MAX_TEXTS >= 64 else 1)' \
  || fail "rerank_service.py does not hold the free reranker slots, or its request bound is under 64 (W2-145, W2-137)"
ok "W2-137, W2-145: the service's bound, no private reranker beside it, the service holds the free slots"
grep -q 'BEGIN W2-141 BLOCK' "$SITE/guard/reads.py" || fail "gov.guard.reads has no W2-141 block (the engineer's wide search)"
"${PY[@]}" 'import gov.util.role_paths, gov.util.parts, gov.util.gitrun, gov.util.register, gov.util.patterns, gov.util.tickets, gov.util.runs_root' 2>/dev/null \
  || fail "a gov.util module of W2-150 does not import"
"${PY[@]}" 'import gov.guard.reads, gov.guard.heldout, gov.guard.decide, gov.guard.protected, gov.guard.role_paths, gov.guard.runs, gov.decisions.register, gov.close.fingerprint, gov.close.select' 2>/dev/null \
  || fail "a module the old names re-import from does not import (W2-150)"
ok "W2-141: the guard's search rule in gov.guard.reads; W2-150: the gov.util modules, and the old names still import"
for m in sandbox gate environ plan_check launcher; do "${PY[@]}" "import gov.launch.$m" 2>/dev/null || fail "gov.launch.$m does not import (W2-56, W2-20, W2-136)"; done
grep -q -- '--append-system-prompt-file' "$SITE/launch/launcher.py" || fail "the launcher passes no role template (W2-153)"
"${PY[@]}" 'import gov.adapters.portability as p, sys; sys.exit(0 if callable(getattr(p, "compose", None)) else 1)' || fail "portability.compose is missing (W2-153)"
ok "W2-56, W2-20, W2-136, W2-153: the launcher's sandbox, gate, environment and plan check import; the role template flag; portability.compose"
grep -q 'GOV_TESTS_OPTIN' "$SITE/accept/runner.py" || fail "gov accept does not run the opt-in suites its map needs (W2-96)"
ok "W2-96: gov accept's opt-in suites"
"$N/bin/gov" brief --help 2>&1 | grep -q -- '--run' || fail "gov brief offers no --run (W2-152)"
"$N/bin/gov" resources --help 2>&1 | grep -q -- '--slot' || fail "gov resources offers no --slot (W2-20)"
ok "W2-152: gov brief --run; W2-20: gov resources --slot"
# The gate reads this machine's gate.json, from a scratch HOME (nothing written beside the real one). A fault in the
# file shuts the gate by name; a gate shut by load is the machine's state and no fault of the pin.
GH=$S/gate-home; mkdir -p "$GH/.gov-os/machine"
[ -f "$HOME/.gov-os/machine/gate.json" ] || fail "this machine has no ~/.gov-os/machine/gate.json (W2-20: gov launch would refuse every start)"
cp "$HOME/.gov-os/machine/gate.json" "$GH/.gov-os/machine/gate.json"
CL=$S/clone
[ -d "$CL/.git" ] || git clone -q --shared "$R" "$CL" || fail "the scratch clone"
(cd "$CL" && env HOME="$GH" "$N/bin/gov" resources --json > "$S/resources.json" 2> "$S/resources.err") || fail "gov resources --json ($(tail -c 200 "$S/resources.err"))"
gate=$(python3 - "$S/resources.json" <<'EOF'
import json, sys
d = json.load(open(sys.argv[1]))
g = d["result"]["gate"]
bad = [r for r in g["reasons"] if any(w in str(r).lower() for w in ("gate.json", "fault", "malformed", "missing", "not json"))]
print(("FAULT " + str(bad)) if bad or not d["ok"] else ("open" if g["open"] else "shut by load: " + "; ".join(map(str, g["reasons"]))[:160]))
EOF
) || fail "gov resources --json: its answer cannot be read"
case "$gate" in FAULT*) fail "the new pin reads this machine's gate.json as a fault: $gate";; esac
ok "W2-20: gov resources reads this machine's gate.json, no fault (the gate is $gate)"
(cd "$CL" && env HOME="$GH" "$N/bin/gov" launch engineer NO-SUCH-TICKET --json > "$S/launch.json" 2> "$S/launch.err"); code=$?
python3 - "$S/launch.json" "$code" <<'EOF' || fail "gov launch NO-SUCH-TICKET: $(head -c 300 "$S/launch.json")"
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if sys.argv[2] != "0" and d.get("ok") is False and d["error"]["code"] == "LAUNCH_REFUSED" and "NO-SUCH-TICKET" in d["error"]["message"] else 1)
EOF
ok "W2-56: gov launch refuses an unknown ticket by name (LAUNCH_REFUSED), starting nothing"
(cd "$CL" && "$N/bin/gov" plan --json > "$S/plan.json" 2> "$S/plan.err"); python3 - "$S/plan.json" <<'EOF' || fail "gov plan --json ($(head -c 300 "$S/plan.err"))"
import json, sys
d = json.load(open(sys.argv[1]))
sys.exit(0 if d.get("ok") is True and d["result"]["counts"]["tickets"] > 0 else 1)
EOF
ok "W2-136: gov plan --json answers (read-only)"
# gov links is a notice: it exits 1 when it finds something new (W2-129), so the check is its answer's "ok", not its exit.
(cd "$CL" && "$N/bin/gov" links --since HEAD~1 --json > "$S/links.json" 2> "$S/links.err"); true
python3 - "$S/links.json" <<'EOF' || fail "gov links --since HEAD~1: its answer is not ok ($(head -c 300 "$S/links.err"))"
import json, sys
sys.exit(0 if json.load(open(sys.argv[1])).get("ok") is True else 1)
EOF
ok "W2-129, W2-55, W2-92: gov links --since HEAD~1 answers"

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
why=$(python3 - "$S/retrieve.json" "$FULL" "$(readlink -f "$STORE")" <<'EOF'
import json, sys
r = json.load(open(sys.argv[1]))["result"]
f = r["facets"]
bad = [k for k in ("lexical", "semantic") if not f.get(k, {}).get("available")]
by = (r.get("rerank") or {}).get("by")
st = r.get("store") or {}
if bad:
    print(f"unavailable: {bad} {f}")
elif by != "service":
    print(f"rerank.by is {by!r}, not the shared service: {r.get('rerank')}")
elif st.get("commit") != sys.argv[2] or st.get("root") != sys.argv[3]:
    print(f"the result names the store {st}, not {sys.argv[2][:12]} in {sys.argv[3]} (W2-138)")
EOF
) || fail "gov retrieve: its answer cannot be read"
[ -z "$why" ] || fail "gov retrieve: $why"
ok "gov retrieve on the store: lexical and semantic available, rerank.by service, the result names the store's commit and folder (W2-138), ${t} s (not a latency gate: DEC-1125 (1))"

# 5. context
# Since the tickets grew, gov context's default 6,000-token ceiling answers CONTEXT_OVER_CEILING for DAEO-sdxk under any
# pin (a documented answer, DEC-1027: the lead trims or names a package). So: the packet builds with a wide budget, and
# the default call gives the old pin's answer.
OLD_PY=${REPIN_OLD_PY:-$HOME/.local/share/gov-os/pin-bcea09060ebc/bin/python}
(cd "$R" && "$N/bin/gov" context DAEO-sdxk --budget 100000 --json > "$S/context.json" 2> "$S/context.err") || fail "gov context DAEO-sdxk --budget 100000 --json ($(tail -c 200 "$S/context.err"))"
python3 - "$S/context.json" <<'EOF' || fail "gov context DAEO-sdxk --budget 100000: not ok"
import json, sys
sys.exit(0 if json.load(open(sys.argv[1])).get("ok") is True else 1)
EOF
code_of() { (cd "$R" && "$1" context DAEO-sdxk --json 2> /dev/null | python3 -c 'import json,sys; d=json.load(sys.stdin); print("ok" if d.get("ok") else d["error"]["code"])'); }
cn=$(code_of "$N/bin/gov"); co=$(code_of "${OLD_PY%/python}/gov")
[ "$cn" = "$co" ] || fail "gov context DAEO-sdxk --json: the new pin answers $cn, the old pin $co"
(cd "$R" && "$N/bin/gov" context --in-force > "$S/inforce.txt" 2> "$S/inforce.err") || fail "gov context --in-force ($(tail -c 200 "$S/inforce.err"))"
ok "gov context DAEO-sdxk builds with a wide budget; at the default ceiling it answers $cn, as the old pin does; --in-force"

# 6. the hooks, each by its exact line in .claude/settings.json, with a HOME whose ~/.local/bin/gov is the new pin, in a
#    scratch clone of the main tree (a Stop hook may write a checkpoint)
FH=$S/home; mkdir -p "$FH/.local/bin"; ln -sfn "$N/bin/gov" "$FH/.local/bin/gov"
for ev in SessionStart PreCompact Stop; do
  line=$(python3 -c "import json,sys; print(json.load(open('$R/.claude/settings.json'))['hooks'][sys.argv[1]][0]['hooks'][0]['command'])" "$ev")
  event="{\"session_id\":\"repin7-check\",\"hook_event_name\":\"$ev\",\"cwd\":\"$CL\",\"source\":\"resume\",\"trigger\":\"manual\",\"stop_hook_active\":false,\"transcript_path\":\"$S/none.jsonl\"}"
  printf '%s' "$event" | (cd "$CL" && env HOME="$FH" PATH=/usr/bin:/bin CLAUDE_PROJECT_DIR="$CL" GOV_ROLE=orchestrator GOV_TICKET=DAEO-sdxk bash -c "$line") \
    > "$S/hook-$ev.out" 2> "$S/hook-$ev.err"
  code=$?
  [ $code = 0 ] || fail "the $ev hook exit $code ($(tail -c 200 "$S/hook-$ev.err"))"
done
[ "$(readlink -f "$FH/.local/bin/gov")" = "$(readlink -f "$N/bin/gov")" ] || fail "the scratch HOME's gov is not the pin"
ok "SessionStart, PreCompact and Stop hooks exit 0 under the new pin"

# 6b. every gov name the live guard hook imports (and the staged W2-141 pair's) is in the new pin: a missing one would
#     refuse every tool call of every session
imports() {  # the hook files' own import statements of gov, run by the new pin's interpreter
  python3 - "$@" <<'EOF'
import ast, sys
lines = []
for path in sys.argv[1:]:
    for node in ast.walk(ast.parse(open(path, encoding="utf-8").read())):
        if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "gov" and not node.level:
            lines.append(f"from {node.module} import " + ", ".join(a.name for a in node.names))
        elif isinstance(node, ast.Import):
            lines += [f"import {a.name}" for a in node.names if a.name.split(".")[0] == "gov"]
print("\n".join(sorted(set(lines))))
EOF
}
imports "$R"/.claude/hooks/*.py > "$S/hook-imports.py" || fail "the live hooks' imports cannot be read"
[ -s "$S/hook-imports.py" ] || fail "no gov import found in the live hooks (the check is blind)"
"${PY[@]}" "$(cat "$S/hook-imports.py")" 2> "$S/hook-imports.err" || fail "a gov name the live hooks import is not in the new pin ($(tail -c 300 "$S/hook-imports.err"))"
ok "the live hooks' $(wc -l < "$S/hook-imports.py") gov imports resolve in the new pin"
if [ -f "$STAGED/pretooluse.py" ]; then
  imports "$STAGED"/*.py > "$S/staged-imports.py" || fail "the staged hooks' imports cannot be read"
  "${PY[@]}" "$(cat "$S/staged-imports.py")" 2> "$S/staged-imports.err" || fail "a gov name the staged W2-141 hooks import is not in the new pin ($(tail -c 300 "$S/staged-imports.err"))"
  ok "the staged W2-141 pair's $(wc -l < "$S/staged-imports.py") gov imports resolve in the new pin"
fi

# 7. the guard, against the new pin's interpreter: the planted cases (guard4_check.py), the live hook's suites as
#    ACT-G14b checked them (ACT-GUARD-FIX-4's, G-14's and tests/unit/hooks/test_live_hook.py, D-4's cut of them), the
#    W2-141 unit cases, and ACT-GUARD-FIX-3's suite compared with the old pin's (since ACT-GUARD-FIX-4 the live hook lets
#    the unresolvable targets through by design, so FIX-3's suite fails those cases under either pin).
export GOV_PIN_PY=$N/bin/python
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
suite "tests/unit/hooks/test_live_hook.py and tests/unit/guard/test_w2_141_search.py" live.txt GOV_LIVE_HOOK_PY="$N/bin/python" bash "$T/heavy_slot.sh" $PT \
  tests/unit/hooks/test_live_hook.py tests/unit/guard/test_w2_141_search.py
# G-14's suite (DECIDED-NOT-DONE row 88). Four engineer near-miss cases ("a search of the whole acceptance folder (from
# above)", "Glob lists names", "Grep from above", "grep -r from above") encode the rule W2-141 changes: with W2-141's
# hook live they must fail, these four by name and no other; with the old hook none may fail. The staged pair is
# checked the same way, so the result does not depend on which ACT (this one or the hook's) runs first.
G14_RED=$(printf '%s\n' 'test_near_misses_pass[Glob lists names0]' 'test_near_misses_pass[Grep from above0]' \
  'test_near_misses_pass[a search of the whole acceptance folder (from above)]' 'test_near_misses_pass[grep -r from above]' | sort)
g14() {  # $1 label, $2 hook, $3 the red cases expected ("" for none)
  local out=$S/g14-$1.txt
  (cd "$R" && env G14_HOOK="$2" bash "$T/heavy_slot.sh" $PT -rf .gov-runtime/scratch/orchestrator/drafts/g14/test_g14.py > "$out" 2>&1) || true
  grep '^FAILED' "$out" | sed -E 's/^FAILED .*test_g14\.py:://; s/\] - .*$/]/' | sort > "$out.failed"
  grep -q ' passed' <(tail -1 "$out") || fail "test_g14.py ($1): $(tail -1 "$out")"
  if [ "$3" = none ]; then
    [ ! -s "$out.failed" ] || fail "test_g14.py ($1): cases failed that must pass: $(tr '\n' ';' < "$out.failed")"
  else
    [ "$(cat "$out.failed")" = "$G14_RED" ] || fail "test_g14.py ($1): the failures are not the four expected by name: $(tr '\n' ';' < "$out.failed")"
  fi
  ok "test_g14.py ($1): $(tail -1 "$out" | sed 's/ in [0-9.]*s.*//')$([ "$3" = none ] || echo ', the four W2-141 near-miss cases red by name')"
}
if grep -q 'BEGIN W2-141 BLOCK' "$R/.claude/hooks/role_reads.py"; then g14 "the live hook, W2-141's" "$HOOK" red; else g14 "the live hook, before W2-141's" "$HOOK" none; fi
if [ -f "$STAGED/pretooluse.py" ] && [ -f "$STAGED/role_reads.py" ]; then
  SH=$S/staged-hook; rm -rf "$SH"; mkdir -p "$SH"
  cp "$STAGED/pretooluse.py" "$STAGED/role_reads.py" "$R/.claude/hooks/bash_writes.py" "$SH/"
  g14 "the staged W2-141 pair" "$SH/pretooluse.py" red
fi
for who in new old; do
  py=$N/bin/python; [ $who = old ] && py=$OLD_PY
  (cd "$T" && GOV_PIN_PY=$py GUARD_FIX3_HOOK=$HOOK bash "$T/heavy_slot.sh" python3 -m pytest -q -p no:cacheprovider -rf \
     test_guard_fix_3.py > "$S/fix3-$who.txt" 2>&1) || true
  grep '^FAILED' "$S/fix3-$who.txt" | sed 's/ - .*//' | sort > "$S/fix3-$who.failed"
done
cmp -s "$S/fix3-new.failed" "$S/fix3-old.failed" && grep -q ' passed' <(tail -1 "$S/fix3-new.txt") \
  || fail "test_guard_fix_3.py: the new pin's failures differ from the old pin's ($(tail -1 "$S/fix3-new.txt") / $(tail -1 "$S/fix3-old.txt"))"
ok "test_guard_fix_3.py: $(tail -1 "$S/fix3-new.txt" | sed 's/ in [0-9.]*s.*//'), the same $(wc -l < "$S/fix3-new.failed") cases as the old pin (ACT-GUARD-FIX-4's LET_THROUGH)"
timing=$(python3 "$T/hook_timing.py")
python3 - "$timing" <<'EOF' || fail "hook_timing.py: $timing"
import re, sys
s = sys.argv[1]
times = [float(x) for x in re.findall(r"[0-9.]+", s.split("seconds", 1)[1])]
sys.exit(0 if s.startswith("exit 0") and sorted(times)[len(times) // 2] < 2.0 else 1)
EOF
ok "hook_timing.py: $timing"
echo "ALL CHECKS PASS ($N)"
