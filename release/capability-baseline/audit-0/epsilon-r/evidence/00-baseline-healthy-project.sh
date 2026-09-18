#!/usr/bin/env bash
# 00 — Establish the baseline: a `gov init` greenfield project and its doctor / audit verdicts.
# Every later health probe starts from this state and mutates exactly one thing.
source "$(dirname "$0")/lib.sh"
say "binary identity"; "$GOV" --version; sha256sum "$GOV" | cut -c1-64
say "gov init (greenfield fixture copy)"
R=$(mkproj base0)
python3 - "$R.init.json" <<'EOF'
import json,sys
d=json.load(open(sys.argv[1])); r=d.get("result") or {}
print("init ok:", d.get("ok"), "| version:", r.get("version"), "| conformance verdict:", (r.get("conformance") or {}).get("verdict"))
print("init result keys:", sorted(r.keys()))
EOF
say "gov doctor"; doctor_summary "$R"
say "gov audit --no-persist"; audit_summary "$R"
say "gov audit (persisted) to create a green record"; AUDIT_PERSIST=1 audit_summary "$R"
say "gov doctor after green audit record"; doctor_summary "$R"
say "records created by audit"; ls "$R/spec/reports" 2>/dev/null | head; find "$R/spec" -name 'AUD-*' | head
