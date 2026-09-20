#!/usr/bin/env bash
# P2-AR-0045 — physical separation attacks on Contract v3:1062 ("The permanent public qualification suite
# and fresh verifier hidden oracle must remain separate").
#
# Builds a disposable tree per attack: a stand-in public qualification suite, a stand-in qualification
# repository and a verifier-custody directory. Run from the repository root with one argument, a writable
# workspace. `rm` is denied in this environment, so each attack gets its own sub-workspace.
set -u
GOV="$PWD/target/release/gov"
SAMPLE="$PWD/release/capability-baseline/verify-1/oracle-format/samples/valid/oracle.json"
FMT="$PWD/release/capability-baseline/verify-1/oracle-format/evidence/_fmt.py"
W="$1"
echo "workspace: $W"

fresh() {
  D="$W/$1"; mkdir -p "$D/pubsuite/tests" "$D/repo/src" "$D/custody"
  echo "public qualification suite test 1" > "$D/pubsuite/tests/t1.md"
  echo "fn main() {}" > "$D/repo/src/main.rs"
  echo "# sample qualification repository" > "$D/repo/README.md"
  cp "$SAMPLE" "$D/custody/oracle.json"
}

run() { # <label> <oracle> <pubsuite> <repo>
  printf '%-54s ' "$1"
  "$GOV" --json oracle validate "$2" --public-suite "$3" --repository "$4" 2>&1 | python3 "$FMT"
}

fresh a0
run "A0 clean (oracle in verifier custody)" "$W/a0/custody/oracle.json" "$W/a0/pubsuite" "$W/a0/repo"

fresh a1; cp "$SAMPLE" "$W/a1/pubsuite/oracle.json"
run "A1 oracle stored inside the public suite" "$W/a1/pubsuite/oracle.json" "$W/a1/pubsuite" "$W/a1/repo"

fresh a2; mkdir -p "$W/a2/repo/.oracle"; cp "$SAMPLE" "$W/a2/repo/.oracle/oracle.json"
run "A2 oracle stored inside the qualification repo" "$W/a2/repo/.oracle/oracle.json" "$W/a2/pubsuite" "$W/a2/repo"

fresh a3; cp "$SAMPLE" "$W/a3/pubsuite/tests/fixture-oracle.json"
run "A3 copy of the oracle inside the public suite" "$W/a3/custody/oracle.json" "$W/a3/pubsuite" "$W/a3/repo"

fresh a4; echo "see P2AR0045-SAMPLE-ORACLE-A for the expected answers" > "$W/a4/repo/NOTES.md"
run "A4 oracle id leaked into the qualification repo" "$W/a4/custody/oracle.json" "$W/a4/pubsuite" "$W/a4/repo"

fresh a5
DIG=$("$GOV" --json oracle validate "$SAMPLE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["result"]["canonical_sha256"])')
echo "expected-oracle: $DIG" > "$W/a5/pubsuite/tests/pin.txt"
run "A5 oracle digest leaked into the public suite" "$W/a5/custody/oracle.json" "$W/a5/pubsuite" "$W/a5/repo"

fresh a6
python3 - "$SAMPLE" "$W/a6/repo/src/notes.rs" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
t = d["fault_manifest"]["faults"][0]["hidden_authoritative_truth"]["statement"]
open(sys.argv[2], "w").write("// %s\n" % t)
PY
run "A6 hidden truth leaked verbatim into the repo" "$W/a6/custody/oracle.json" "$W/a6/pubsuite" "$W/a6/repo"

# A7: the same V1 fault-manifest content re-expressed as a GOVERNED RECORD (type: fault-manifest, no
# `format:` key) and left inside the public suite. `qualification_oracle::is_hidden_oracle_material`
# calls this hidden-oracle material; the question is whether the separation scan finds it.
fresh a7
python3 - "$SAMPLE" "$W/a7/pubsuite/tests/fm.yaml" <<'PY'
import json, sys, yaml
d = json.load(open(sys.argv[1]))
rec = {"type": "fault-manifest", "id": "LEAKED-FM-1",
       "faults": d["fault_manifest"]["faults"]}
open(sys.argv[2], "w").write(yaml.safe_dump(rec, sort_keys=False))
PY
run "A7 V1 manifest as 'type: fault-manifest' in suite" "$W/a7/custody/oracle.json" "$W/a7/pubsuite" "$W/a7/repo"

# A8: the same, but with the hidden truths removed (a pure structural leak of the fault ids/classes)
fresh a8
python3 - "$SAMPLE" "$W/a8/repo/fm.yaml" <<'PY'
import json, sys, yaml
d = json.load(open(sys.argv[1]))
faults = []
for f in d["fault_manifest"]["faults"]:
    g = {k: v for k, v in f.items() if k != "hidden_authoritative_truth"}
    faults.append(g)
open(sys.argv[2], "w").write(yaml.safe_dump({"type": "hidden-memory-oracle", "id": "LEAKED-MO-1", "faults": faults}, sort_keys=False))
PY
run "A8 'type: hidden-memory-oracle' record in the repo" "$W/a8/custody/oracle.json" "$W/a8/pubsuite" "$W/a8/repo"

echo "workspace kept at: $W"

# ---- appended: isolate the two leak-scan blind spots -------------------------------------------
# A9: the hidden truth verbatim but REFLOWED across two lines (what any YAML/Markdown writer does)
fresh a9
python3 - "$SAMPLE" "$W/a9/repo/README.md" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
t = d["fault_manifest"]["faults"][0]["hidden_authoritative_truth"]["statement"]
half = t.rfind(" ", 0, 60)
open(sys.argv[2], "w").write("notes:\n  %s\n  %s\n" % (t[:half], t[half + 1:]))
PY
run "A9 hidden truth reflowed over two lines" "$W/a9/custody/oracle.json" "$W/a9/pubsuite" "$W/a9/repo"

# A10: the oracle document copied into the suite as YAML rather than JSON
fresh a10
python3 - "$SAMPLE" "$W/a10/pubsuite/tests/oracle.yaml" <<'PY'
import json, sys, yaml
open(sys.argv[2], "w").write(yaml.safe_dump(json.load(open(sys.argv[1])), sort_keys=False))
PY
run "A10 oracle copied into the suite as YAML" "$W/a10/custody/oracle.json" "$W/a10/pubsuite" "$W/a10/repo"

# A11: only the fault ids and classes leaked, as plain text
fresh a11
echo "fixtures cover SMP-F-001 and SMP-F-002 (SAMPLE_STALE_MANDATORY_INPUT)" > "$W/a11/pubsuite/tests/plan.md"
run "A11 fault ids/classes leaked as plain text" "$W/a11/custody/oracle.json" "$W/a11/pubsuite" "$W/a11/repo"
