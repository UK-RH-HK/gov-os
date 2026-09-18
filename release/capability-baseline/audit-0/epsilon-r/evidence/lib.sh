#!/usr/bin/env bash
# P2-AR-0008 (epsilon re-audit) probe library. Independent evidence; NOT a product test.
#
# Re-run any probe from the worktree root:
#   bash release/capability-baseline/audit-0/epsilon-r/evidence/<probe>.sh > release/.../evidence/<probe>.out 2>&1
#
# Environment:
#   WT       worktree root (default: derived from this file's location)
#   SCRATCH  disposable work area (default: a fresh mktemp -d); every project is created under it
#   GOV      the product binary (default: $WT/target/release/gov, built with `cargo build --release`)
set -u
EVD="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="${WT:-$(cd "$EVD/../../../../.." && pwd)}"
GOV="${GOV:-$WT/target/release/gov}"
SCRATCH="${SCRATCH:-$(mktemp -d)}"
mkdir -p "$SCRATCH"
export GOV_CANONICAL_ROOT="$WT"
# the greenfield fixture is a Cargo project; with cargo on PATH doctor D022 (native toolchain) passes
export PATH="$HOME/.cargo/bin:$PATH"
unset GOV_SESSION GOV_ROLE GOV_MACHINE_STATE_DIR

say() { printf '\n=== %s\n' "$*"; }
note() { printf '# %s\n' "$*"; }

# g <root> <args...> : run gov with --json against a project root, per-project simulated machine state
g() {
  local root="$1"; shift
  XDG_STATE_HOME="$root.machine" "$GOV" --json --root "$root" --session "${SESS:-S-probe}" --role "${ROLE:-orchestrator}" "$@"
}
# gq <root> <jq-ish python expr> <args...> : run gov and print a python-selected projection of the envelope
gp() {
  local root="$1"; local expr="$2"; shift 2
  local out rc
  out="$(g "$root" "$@" 2>/dev/null)"; rc=$?
  printf 'exit=%s ' "$rc"
  printf '%s' "$out" | python3 -c "
import json,sys
raw=sys.stdin.read()
try:
    d=json.loads(raw)
except Exception as e:
    print('NON-JSON:', raw[:400]); sys.exit(0)
ok=d.get('ok'); r=d.get('result'); e=d.get('error') or {}
det=e.get('details') if isinstance(e,dict) else None
x=$expr
print(json.dumps(x, sort_keys=True) if not isinstance(x,str) else x)
"
}

git_base() { # <dir> : git init + baseline commit
  ( cd "$1" && git init -q && git config user.email probe@example.invalid && git config user.name probe \
    && git add -A && git commit -qm "probe baseline" )
}
git_commit() { ( cd "$1" && git add -A && git commit -qm "${2:-probe change}" ) >/dev/null 2>&1; }

# mkproj <name> [fixture] : copy fixture (default greenfield), git baseline, gov init; echoes the root path
mkproj() {
  local name="$1" fx="${2:-greenfield}" root="$SCRATCH/$1"
  rm -rf "$root" "$root.machine"
  cp -r "$WT/fixtures/$fx/project" "$root"
  git_base "$root" >/dev/null 2>&1
  g "$root" init --name "$name" --alias "fx-$name" >"$root.init.json" 2>&1
  git_commit "$root" "gov init"
  echo "$root"
}

# clone <src-root> <new-name> : byte copy of a project (incl. derived runtime and its simulated machine state)
clone() {
  local src="$1" dst="$SCRATCH/$2"
  rm -rf "$dst" "$dst.machine"
  cp -a "$src" "$dst"; [ -d "$src.machine" ] && cp -a "$src.machine" "$dst.machine"
  echo "$dst"
}
# base_project : one shared HEALTHY baseline per SCRATCH (created once)
base_project() {
  if [ ! -f "$SCRATCH/.base_ok" ]; then mkproj base >/dev/null; touch "$SCRATCH/.base_ok"; fi
  echo "$SCRATCH/base"
}
# yw <root> <rel> <python-dict-literal> : write a YAML record
yw() {
  python3 - "$1/$2" "$3" <<'EOF'
import sys, os, yaml, ast
p=sys.argv[1]; os.makedirs(os.path.dirname(p), exist_ok=True)
yaml.safe_dump(ast.literal_eval(sys.argv[2]), open(p,"w"), sort_keys=False)
EOF
}
# ye <root> <rel> <python statements operating on dict d> : edit a YAML file in place
ye() {
  python3 - "$1/$2" "$3" <<'EOF'
import sys, yaml
p=sys.argv[1]; d=yaml.safe_load(open(p))
exec(sys.argv[2])
yaml.safe_dump(d, open(p,"w"), sort_keys=False)
EOF
}
# readiness_full : python literal for a feature readiness map with every dimension PRESENT
readiness_full() {
  python3 -c "
import yaml; d=yaml.safe_load(open('$WT/framework/taxonomy/READINESS_DIMENSIONS.yaml'))
print({x['id']:'PRESENT' for x in d['dimensions']})"
}

# new_task <root> <class> <allowed-csv> [extra gov task create args...] : prints the created task id
new_task() {
  local root="$1" cls="$2" allowed="$3"; shift 3
  g "$root" task create --class "$cls" --objective "probe $cls task" --allowed "$allowed" --status READY "$@" 2>/dev/null \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print((d.get('result') or {}).get('id') or 'ERR:'+json.dumps(d.get('error'))[:300])"
}
# report_json <file> <tests-status> <files-csv> [extra python dict items] : write a task-close report
report_json() {
  python3 - "$1" "$2" "$3" "${4:-}" <<'EOF'
import json,sys,ast
f,ts,files,extra=sys.argv[1:5]
d={"work_completed":"probe work","tests":{"status":ts},"files_changed":[x for x in files.split(",") if x],"evidence":[]}
if extra: d.update(ast.literal_eval("{"+extra+"}"))
json.dump(d,open(f,"w"))
EOF
}

# doctor verdict + failed checks
doctor_summary() { gp "$1" "{'ok':ok,'verdict':(r or det or {}).get('verdict'),'failed':[ (c['id'],c['severity'],c['message'][:140]) for c in (r or det or {}).get('checks',[]) if not c.get('ok')]}" doctor; }
# audit verdict + findings (no persist unless AUDIT_PERSIST=1)
audit_summary() {
  local extra=(--no-persist); [ "${AUDIT_PERSIST:-0}" = 1 ] && extra=()
  gp "$1" "{'ok':ok,'verdict':(r or det or {}).get('verdict'),'findings':[ (f['family'],f['severity'],f['message'][:150]) for f in (r or det or {}).get('findings',[])]}" audit "${extra[@]}" "${@:2}"
}
