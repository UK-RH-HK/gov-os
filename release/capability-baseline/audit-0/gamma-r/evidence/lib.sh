#!/usr/bin/env bash
# P2-AR-0010 (gamma re-audit) probe library. Sourced by every probe script in this directory.
#
# Environment (override to re-run elsewhere):
#   WT       the audited worktree (candidate cap2-candidate-0 + orchestration commit); default: derived from this file
#   GOV      the gov binary under test; default: $WT/target/release/gov (built with `cargo build --release` in $WT)
#   PROBES   scratch parent for disposable projects; default: $TMPDIR/gamma-r-probes
#
# Every disposable project gets its own simulated machine (XDG_STATE_HOME under the project dir), exactly as the
# builder certification harness does (tests/certification/common.rs::Gov::run), so SRR protected state never leaks
# between probes or into the operator's own machine state. GOV_CANONICAL_ROOT is deliberately NOT set: `gov init`
# installs from the kernel payload embedded in the binary (kernel::resolve_kernel_source precedence).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WT="${WT:-$(cd "$HERE/../../../../.." && pwd)}"
GOV="${GOV:-$WT/target/release/gov}"
PROBES="${PROBES:-${TMPDIR:-/tmp}/gamma-r-probes}"
mkdir -p "$PROBES"
export PATH="$HOME/.cargo/bin:$PATH"   # native toolchain visible to ecosystem detection (D022)

# g <root> <role> <session> <args...>  — run gov with the JSON envelope; prints the envelope; returns gov's exit code
g() {
  local root="$1" role="$2" sess="$3"; shift 3
  env -u GOV_ROLE -u GOV_SESSION -u GOV_CANONICAL_ROOT XDG_STATE_HOME="$root/.probe-machine" \
    "$GOV" --json --root "$root" --role "$role" --session "$sess" "$@"
}
# gq: like g but prints only a compact summary line: exit code, ok, error code/message (first 300 chars)
gq() {
  local out rc
  out="$(g "$@" 2>&1)"; rc=$?
  python3 - "$rc" "$out" <<'PY'
import json, sys
rc, out = sys.argv[1], sys.argv[2]
try:
    e = json.loads(out)
    if e.get("ok"):
        print(f"exit={rc} ok=true")
    else:
        err = e.get("error") or {}
        print(f"exit={rc} ok=false code={err.get('code')} msg={str(err.get('message'))[:300]}")
except Exception:
    print(f"exit={rc} non-json: {out[:300]}")
PY
  return $rc
}
# jget <json-text> <python-expr over e>  — evaluate an expression over the parsed envelope
jget() {
  python3 -c 'import json,sys; e=json.loads(sys.argv[1]); print(eval(sys.argv[2]))' "$1" "$2"
}

# mkproj <name> [fixture]  — fresh disposable project: copy fixture, git init+commit, `gov init` as orchestrator.
# Prints the root path. The init envelope is kept at <root>/.probe-init.json.
mkproj() {
  local name="$1" fx="${2:-greenfield}"
  local root="$PROBES/$name"
  rm -rf "$root"; mkdir -p "$root"
  cp -r "$WT/fixtures/$fx/project/." "$root/"
  ( cd "$root" && git init -q && git config user.email probe@example.invalid && git config user.name probe \
      && git add -A && git commit -q -m "probe fixture baseline" )
  g "$root" orchestrator S-init init --name "$name" --alias "a-$name" > "$root/.probe-init.json" 2>&1
  local rc=$?
  ( cd "$root" && printf '.probe-machine/\n.probe-*\n' >> .git/info/exclude && git add -A && git commit -q -m "gov init" )
  if [ $rc -ne 0 ]; then echo "MKPROJ_INIT_FAILED rc=$rc $(head -c 600 "$root/.probe-init.json")" >&2; fi
  echo "$root"
}

# readiness_json <missing-csv> <na-csv>  — a readiness map over the kernel's 26 dimensions (framework/taxonomy)
readiness_json() {
  python3 - "$WT/framework/taxonomy/READINESS_DIMENSIONS.yaml" "${1:-}" "${2:-}" <<'PY'
import sys, json, re
dims = re.findall(r'\{id: ([a-z_]+),', open(sys.argv[1]).read())
missing = [x for x in sys.argv[2].split(',') if x]
na = [x for x in sys.argv[3].split(',') if x]
out = {}
for d in dims:
    if d in missing: out[d] = "MISSING"
    elif d in na: out[d] = {"status": "N/A_WITH_REASON", "reason": "probe: not applicable to this synthetic feature"}
    else: out[d] = "PRESENT"
print(json.dumps(out))
PY
}

# write_feature <root> <id> <readiness-json> [extra-json]
write_feature() {
  python3 - "$1" "$2" "$3" "${4:-{\}}" <<'PY'
import sys, json, os
root, fid, rd, extra = sys.argv[1], sys.argv[2], json.loads(sys.argv[3]), json.loads(sys.argv[4])
rec = {"id": fid, "type": "feature", "title": f"probe feature {fid}", "status": "ACTIVE", "capability_category": "backend",
       "readiness": rd}
rec.update(extra)
os.makedirs(os.path.join(root, "spec/features"), exist_ok=True)
import subprocess
# YAML is a superset of JSON: write JSON text into the .yaml file (the product loads it through serde_yaml)
open(os.path.join(root, "spec/features", fid + ".yaml"), "w").write(json.dumps(rec, indent=1) + "\n")
PY
}

# report_file <root> <name> <work> <files-csv> <tests-status>  — a worker return / close report on disk
report_file() {
  python3 - "$@" <<'PY'
import sys, json, os
root, name, work, files, ts = sys.argv[1:6]
d = os.path.join(root, ".governance-runtime", "reports"); os.makedirs(d, exist_ok=True)
f = os.path.join(d, name + ".json")
json.dump({"work_completed": work, "files_changed": [x for x in files.split(',') if x],
           "tests": {"status": ts, "reason": "probe"}, "outcome": "success", "evidence": []}, open(f, "w"))
print(f)
PY
}

hdr() { printf '\n==== %s ====\n' "$*"; }
cmd() { printf '$ %s\n' "$*"; }
