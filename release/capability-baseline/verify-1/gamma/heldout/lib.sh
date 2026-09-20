# Shared helpers for the gamma iteration-1 held-out probes.
# Every probe runs against a disposable project on an ISOLATED simulated machine
# (XDG_STATE_HOME per project), so no probe touches the real machine's governance state.
set -u
: "${GAMMA_WT:?set GAMMA_WT to the verification worktree}"
GOV="$GAMMA_WT/target/release/gov"
LAB="${GAMMA_LAB:-/tmp/gamma-lab}"
SIGNER="$GAMMA_WT/release/capability-baseline/verify-1/gamma/heldout/ownersign.py"
mkdir -p "$LAB/projects" "$LAB/machines" "$LAB/admin"
[ -f "$LAB/admin/root-1.json" ] || python3 "$SIGNER" root "$LAB/admin/root-1.json"

_pass=0; _fail=0
ok()   { _pass=$((_pass+1)); echo "PASS  $1"; }
bad()  { _fail=$((_fail+1)); echo "FAIL  $1"; }
check(){ if [ "$1" = "$2" ]; then ok "$3 (got $1)"; else bad "$3 (expected '$2', got '$1')"; fi; }
summary(){ echo "---- $(basename "$0"): $_pass passed, $_fail failed"; [ "$_fail" -eq 0 ]; }

# newproj <name> [--provision]  -> prints the project root; sets PROJ and XDG_STATE_HOME.
# --provision makes it one of the owner's machines: a throw-away Signed Release Root is provisioned and
# the installed kernel is re-verified against a signed release of exactly the payload framework.lock pins,
# which is what makes the authenticated human channel available (P2-ADJ-0001 / OD-P2-02 "provision, then work").
newproj() {
  local name="$1"; shift || true
  PROJ="$LAB/projects/$name"
  export XDG_STATE_HOME="$LAB/machines/$name"
  # a previous run's project/machine is moved aside, never reused (rm is not used anywhere in this suite)
  if [ -e "$PROJ" ]; then mkdir -p "$LAB/superseded"; mv "$PROJ" "$LAB/superseded/$name-$(date +%s)-$RANDOM"; fi
  if [ -e "$XDG_STATE_HOME" ]; then mkdir -p "$LAB/superseded"; mv "$XDG_STATE_HOME" "$LAB/superseded/m-$name-$(date +%s)-$RANDOM"; fi
  mkdir -p "$PROJ" "$XDG_STATE_HOME"
  export GOV_SESSION="main-$name"   # one stable session per probe unless a probe overrides it
  ( cd "$PROJ" && git init -q . && git config user.email g@x && git config user.name gamma \
    && echo "# $name" > README.md && git add -A && git commit -qm init ) >/dev/null 2>&1
  ( cd "$PROJ" && "$GOV" --role orchestrator init ) >/dev/null 2>&1
  if [ "${1:-}" = "--provision" ]; then
    ( cd "$PROJ" && "$GOV" --role orchestrator trust provision --anchor "$LAB/admin/root-1.json" ) >/dev/null 2>&1
    python3 "$(dirname "${BASH_SOURCE[0]}")/publish_release.py" "$PROJ/governance/kernel" "$LAB/rel-$name" 1 >/dev/null
    ( cd "$PROJ" && "$GOV" --role orchestrator kernel reinstall --source "$LAB/rel-$name/kernel" ) >/dev/null 2>&1
  fi
  echo "$PROJ"
}

# g <role> <args...>  -> run gov in $PROJ with --json, print the envelope
g() { local role="$1"; shift; ( cd "$PROJ" && "$GOV" --role "$role" --json "$@" 2>&1 ); }
gp() { local role="$1"; shift; ( cd "$PROJ" && "$GOV" --role "$role" "$@" 2>&1 ); }

# jq-less field read: jget '<json file or ->' '<python expr over d>'
jget() { python3 -c "
import sys,json
d=json.load(sys.stdin)
r=d.get('result',d)
try:
    print(eval(sys.argv[1]))
except Exception as e:
    print('ERR:'+type(e).__name__)
" "$1"; }

# answer_gate <role> <gate> <option>: render the package, have the 'owner' sign it, relay it.
answer_gate() {
  local role="$1" gate="$2" option="$3"
  local pres inst sha nonce f
  pres=$(g "$role" gate present "$gate")
  inst=$(printf '%s' "$pres" | jget "r['gate']['gate_instance']")
  sha=$(printf '%s' "$pres" | jget "r['gate']['package_sha256']")
  nonce="n-$gate-$option-$RANDOM$RANDOM"
  f="$LAB/admin/ans-$gate-$option-$nonce.json"
  python3 "$SIGNER" answer "$f" "$gate" "$inst" "$sha" "$option" "$nonce"
  g "$role" decide "$gate" --option "$option" --answer-file "$f"
}

# security_review <tool_id> <version> -> prints the governed security-review report id (RPT-nnnn).
# A `security`-class task closed by an independent role (security-engineer) in its own session.
security_review() {
  local tid="$1" ver="$2" out task rpt hash
  out=$(GOV_SESSION=sec-$tid g security-engineer task create --class security \
        --objective "Independent security review of $tid $ver")
  task=$(printf '%s' "$out" | jget "r['id']")
  GOV_SESSION=sec-$tid g security-engineer task status "$task" READY >/dev/null
  GOV_SESSION=sec-$tid g security-engineer task claim "$task" >/dev/null
  g memory-engineer rebuild-memory --incremental >/dev/null
  hash=$(GOV_SESSION=sec-$tid g security-engineer context compile "$task" | jget "r['packet_hash']")
  python3 - "$hash" "$tid" "$ver" "$LAB/review-$tid.json" <<'PY'
import json,sys
h,tid,ver,out=sys.argv[1:5]
json.dump({"work_completed":"independent review of %s %s"%(tid,ver),"files_changed":[],
  "evidence":["licence, maintenance, supply chain and permission review"],
  "tests":{"status":"not_applicable_with_reason","reason":"a static security review runs no product test"},
  "discoveries":[],"lessons":[],"unresolved":[],"next_action":"install",
  "context_packet_hash":h,"inputs_consumed":[],"outputs_produced":[],"requirements_implemented":[],
  "scenarios_implemented":[],"features_implemented":[],"decisions_applied":[],"constraints_applied":[],
  "acceptance_evidence":[],"deviations":[],
  "security_review":{"tool_id":tid,"version":ver,"verdict":"passed","scope":"licence, maintenance, supply chain, permissions"}},
  open(out,"w"),indent=1)
PY
  rpt=$(GOV_SESSION=sec-$tid g security-engineer task close "$task" --report "$LAB/review-$tid.json" | jget "r['report']")
  echo "$rpt"
}

# descriptor <file> <python-dict-patch-json>: write a tool descriptor from the non-elevated baseline plus a patch.
descriptor() {
  python3 - "$1" "$2" "$3" <<'PY'
import json,sys,yaml
out, rpt, patch = sys.argv[1], sys.argv[2], json.loads(sys.argv[3])
d={"tool_id":"TL-JQ","name":"jq","type":"CLI","version_pin":"1.7.1","license":"MIT","reversible":True,
   "cost_usd":0,"required_permission_classes":["READ_REPO"],"capabilities":["json-query"],
   "install_command":["echo","install"],"uninstall_command":["echo","uninstall"],
   "health_check":{"kind":"command","command":["echo","ok"]},"security_review_record":rpt}
d.update(patch)
yaml.safe_dump(d, open(out,"w"))
PY
}
