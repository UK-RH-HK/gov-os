#!/usr/bin/env bash
# P2-AR-0047 held-out probe library (family beta: C1-C10, D1-D6, R1-R3).
#
# Independent evidence for verification iteration 1. Written from Contract v3's checklist text and the product's
# observable behaviour; it copies no builder test and no builder probe. It never enters the product tree.
#
# Conventions:
#   * every check prints exactly one `PASS <id> — <what was shown>` or `FAIL <id> — <what was shown>` line;
#   * `<id>` is <CAP>-<n> (the capability and the bullet group it evidences);
#   * a probe that cannot establish its precondition prints `FAIL <id> — PRECONDITION ...` and never a vacuous PASS.
set -uo pipefail

: "${BETA_WT:?BETA_WT (the verifier worktree) must be set}"
GOV="$BETA_WT/target/release/gov"
: "${BETA_SCRATCH:=${TMPDIR:-/tmp}/p2ar0047-heldout}"
mkdir -p "$BETA_SCRATCH"

PASSN=0; FAILN=0
pass() { PASSN=$((PASSN+1)); echo "PASS $1 — $2"; }
fail() { FAILN=$((FAILN+1)); echo "FAIL $1 — $2"; }
# check <id> <condition-exit-code> <message-on-pass> <message-on-fail>
chk() { if [ "$2" -eq 0 ]; then pass "$1" "$3"; else fail "$1" "$4"; fi; }
summary() { echo "---- $(basename "$0"): $PASSN passed, $FAILN failed"; [ "$FAILN" -eq 0 ]; }

# `rm` is denied to this verifier, so nothing is ever deleted: a stale path is MOVED ASIDE to <path>.aside-<n>.
# Where a probe must "delete" state (D6), it moves it aside — the process under test sees the same absence.
# The destination is a graveyard OUTSIDE every project, so a moved-aside store never becomes a file the product
# under test can see (an in-tree `.aside` copy would itself change what the indexer walks).
aside() {
  local p="$1"
  [ -e "$p" ] || return 0
  local grave="$BETA_SCRATCH/aside"
  mkdir -p "$grave"
  local n=0 base
  base=$(basename "$p")
  while [ -e "$grave/$base.$n" ]; do n=$((n+1)); done
  mv "$p" "$grave/$base.$n"
}

# A disposable project on its own simulated machine. $1 = short name, $2 = fixture (greenfield|brownfield|empty)
new_project() {
  local name="$1" fixture="${2:-greenfield}"
  local root="$BETA_SCRATCH/$name.$$.$RANDOM"
  aside "$root"
  mkdir -p "$root"
  if [ "$fixture" != "empty" ]; then cp -r "$BETA_WT/fixtures/$fixture/project/." "$root/"; fi
  ( cd "$root" && git init -q && git config user.email v@example.invalid && git config user.name v \
      && git add -A && git commit -q -m baseline ) >/dev/null 2>&1
  echo "$root"
}

# gov <root> <args...> : JSON envelope on stdout, per-root simulated machine state.
gov() {
  local root="$1"; shift
  XDG_STATE_HOME="$BETA_SCRATCH/machine/$(echo "$root" | md5sum | cut -c1-16)" \
  GOV_CANONICAL_ROOT="$BETA_WT" \
  PATH="$HOME/.cargo/bin:$PATH" \
  "$GOV" --json --root "$root" --role "${GOV_AS_ROLE:-orchestrator}" --session "${GOV_SESSION_ID:-hs1}" "$@" 2>&1
}

# jq-free JSON field read: jget <json> <python-expression over `d`>
jget() { python3 -c '
import sys, json
raw = sys.stdin.read()
try:
    d = json.loads(raw)
except Exception:
    print("<<UNPARSEABLE>>"); sys.exit(0)
try:
    v = eval(sys.argv[1], {"d": d, "json": json})
except Exception as e:
    print("<<ERR:%s>>" % e); sys.exit(0)
print(json.dumps(v) if not isinstance(v, str) else v)
' "$1"; }

commit_all() { ( cd "$1" && git add -A && git commit -q -m "${2:-step}" ) >/dev/null 2>&1; }

# Re-establish a CURRENT green governance record. The suite's own run mutates input classes of its own currency key
# (index_manifest, spec_tasks, and the memory-quality records a held-out miss writes), so one run is not enough: this
# runs `gov audit` until two consecutive runs agree on the input snapshot. See finding V1-BETA-04.
# establish_green <root> -> prints the green audit id, or GREEN_NOT_ESTABLISHED
establish_green() {
  local root="$1" prev="" cur="" id="" green="" i=0
  while [ $i -lt 6 ]; do
    local out; out=$(GOV_AS_ROLE=orchestrator GOV_SESSION_ID="S-green-$i" gov "$root" audit)
    cur=$(echo "$out" | jget 'json.dumps((d.get("result") or d.get("error",{}).get("details",{})).get("inputs_hash"))')
    id=$(echo "$out" | jget 'json.dumps((d.get("result") or d.get("error",{}).get("details",{})).get("audit"))')
    green=$(echo "$out" | jget 'json.dumps((d.get("result") or d.get("error",{}).get("details",{})).get("green"))')
    if [ "$cur" = "$prev" ] && [ "$green" = "true" ]; then echo "$id"; return 0; fi
    prev="$cur"; i=$((i+1))
  done
  echo "GREEN_NOT_ESTABLISHED(green=$green)"; return 1
}
