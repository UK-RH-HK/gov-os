# Shared probe environment for P2-AR-0013 (alpha-r). Source this from every probe.
# Isolation: every probe runs with HOME / XDG_* pointed at a fresh scratch directory, so the Signed Release Root
# protected machine state (default $XDG_STATE_HOME/governance-os/machine) and the embedded-kernel cache are private
# to the probe and the operator's real machine state is never read or written.
set -u
EVROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$(cd "$EVROOT/../../../../.." && pwd)"
GOV="${GOV:-$REPO/target/release/gov}"
PROBE_TMP="${PROBE_TMP:-${TMPDIR:-/tmp}}"
new_sandbox() {   # new_sandbox <name> -> exports SB, HOME, XDG_*; unsets every GOV_* variable
  SB="$(mktemp -d "$PROBE_TMP/alpha-r-$1-XXXXXX")"
  export HOME="$SB/home" XDG_STATE_HOME="$SB/home/.local/state" XDG_CACHE_HOME="$SB/home/.cache" XDG_CONFIG_HOME="$SB/home/.config"
  mkdir -p "$HOME" "$XDG_STATE_HOME" "$XDG_CACHE_HOME"
  for v in $(env | sed -n 's/^\(GOV_[A-Z_]*\)=.*/\1/p'); do unset "$v"; done
  export GIT_AUTHOR_NAME=probe GIT_AUTHOR_EMAIL=probe@example.invalid GIT_COMMITTER_NAME=probe GIT_COMMITTER_EMAIL=probe@example.invalid
  export GIT_CONFIG_GLOBAL=/dev/null
}
# run a gov command with --json and print "$ gov <args>" then the JSON envelope; never aborts the probe
g() { echo "\$ gov $*"; "$GOV" --json "$@" 2>&1; echo "[exit=$?]"; }
# same, but only print selected jq-like fields via python (arg1 = python expression over `r` = parsed envelope)
gq() { local expr="$1"; shift; echo "\$ gov $*   | $expr"; "$GOV" --json "$@" >"$SB/.last.json" 2>"$SB/.last.err"; local rc=$?; python3 - "$SB/.last.json" "$expr" <<'PY'
import json,sys
try:
    r=json.load(open(sys.argv[1]))
except Exception as e:
    print("<<non-JSON output>>", open(sys.argv[1]).read()[:2000]); sys.exit(0)
try:
    v=eval(sys.argv[2],{"r":r,"json":json})
    print(json.dumps(v,indent=1,ensure_ascii=False) if not isinstance(v,str) else v)
except Exception as e:
    print("<<expr error>>",repr(e)); print(json.dumps(r,indent=1)[:3000])
PY
echo "[exit=$rc]"; }
hdr() { echo; echo "=================== $* ==================="; }
