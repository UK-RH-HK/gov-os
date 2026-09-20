#!/usr/bin/env bash
# P2-AR-0045 — the G6 entry point (`gov health qualify`): a qualification run is recorded only against a
# conforming, separate, bound hidden oracle, and a FORMAT_SAMPLE never counts as qualification.
# Usage: 07-g6-entry-point.sh <workspace-with-an-initialised-project>   (run from the repository root)
set -u
WT="$PWD"
GOV="$WT/target/release/gov"
S="$WT/release/capability-baseline/verify-1/oracle-format/samples"
FMT="$WT/release/capability-baseline/verify-1/oracle-format/evidence/_fmt.py"
W="$1"; P="$W/proj"
mkdir -p "$W/custody" "$W/pubsuite"
cp "$S/valid/oracle.json" "$W/custody/oracle.json"
cp "$S/valid/score-report.json" "$W/custody/report.json"

show() { python3 "$WT/release/capability-baseline/verify-1/oracle-format/evidence/_g6fmt.py"; }

q() { printf '%-50s ' "$1"; shift; (cd "$P" && "$GOV" --json --role orchestrator health qualify "$@" 2>&1) | show; }

echo "--- machine trust posture ---"
(cd "$P" && "$GOV" --json trust status 2>&1) | python3 -c 'import json,sys; d=json.load(sys.stdin); r=d.get("result") or {}; print("posture:", r.get("posture"), "| anchor:", r.get("trust_anchor_sha256"))' 2>/dev/null || echo "(trust status unavailable)"
echo

q "G0 conforming FORMAT_SAMPLE, bound report" --kind synthetic-repository --oracle "$W/custody/oracle.json" --report "$W/custody/report.json" --public-suite "$W/pubsuite"
q "G1 non-conforming oracle (missing V1.6)" --oracle "$S/invalid/v1-06-missing-expected-severity.json" --report "$W/custody/report.json"
q "G2 report unbound (wrong oracle digest)" --oracle "$W/custody/oracle.json" --report "$S/invalid/bind-03-unbound-wrong-oracle-digest.json"
q "G3 an injected fault left unscored" --oracle "$W/custody/oracle.json" --report "$S/invalid/bind-01-unscored-injected-fault.json"
q "G4 score report supplied as the oracle" --oracle "$W/custody/report.json" --report "$W/custody/report.json"
q "G5 unknown run kind" --kind made-up --oracle "$W/custody/oracle.json" --report "$W/custody/report.json"

# G6 — the oracle stored INSIDE the governed repository (the project root is always a forbidden location)
mkdir -p "$P/oracle-store"; cp "$W/custody/oracle.json" "$P/oracle-store/oracle.json"
q "G6 oracle stored inside the governed repo" --oracle "$P/oracle-store/oracle.json" --report "$W/custody/report.json"
mv "$P/oracle-store" "$W/moved-aside-oracle-store"

# G7 — only the oracle id leaked into the governed repository
echo "expected answers: P2AR0045-SAMPLE-ORACLE-A" > "$P/LEAK.md"
q "G7 oracle id leaked into the governed repo" --oracle "$W/custody/oracle.json" --report "$W/custody/report.json"
mv "$P/LEAK.md" "$W/moved-aside-LEAK.md"

# G8 — a real QUALIFICATION-purpose pair on this (unprovisioned) machine
python3 - "$W/custody/oracle.json" "$W/custody/qualification-oracle.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d["purpose"] = "QUALIFICATION"
json.dump(d, open(sys.argv[2], "w"), indent=1)
PY
DIG=$("$GOV" --json oracle validate "$W/custody/qualification-oracle.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["canonical_sha256"])')
python3 - "$W/custody/report.json" "$W/custody/qualification-report.json" "$DIG" <<'PY'
import json, sys
d = json.load(open(sys.argv[1])); d["purpose"] = "QUALIFICATION"; d["binding"]["oracle_sha256"] = sys.argv[3]
json.dump(d, open(sys.argv[2], "w"), indent=1)
PY
q "G8 purpose=QUALIFICATION, unprovisioned machine" --oracle "$W/custody/qualification-oracle.json" --report "$W/custody/qualification-report.json"

echo
echo "--- what the recorded G6 health result carries (leakage check) ---"
ORACLE_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["oracle_id"])' "$W/custody/oracle.json")
ORACLE_DIG=$("$GOV" --json oracle validate "$W/custody/oracle.json" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["canonical_sha256"])')
TRUTH=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["fault_manifest"]["faults"][0]["hidden_authoritative_truth"]["statement"])' "$W/custody/oracle.json")
for needle in "$ORACLE_ID" "$ORACLE_DIG" "SMP-F-001" "$TRUTH"; do
  n=$(grep -rlF "$needle" "$P" 2>/dev/null | grep -v "^$P/oracle-store" | wc -l)
  printf '  %-70s occurrences in the governed repository: %s\n' "${needle:0:66}" "$n"
done
echo
echo "--- the qualification block of the last recorded G6 result ---"
(cd "$P" && "$GOV" --json health history --tier G6 2>/dev/null) | python3 -c '
import json,sys
d=json.load(sys.stdin)
r=d.get("result")
print(json.dumps(r, indent=1)[:2000])
' 2>/dev/null || echo "(history unavailable; see the RECORDED lines above)"
