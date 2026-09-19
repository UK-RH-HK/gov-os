#!/usr/bin/env bash
# P2-AR-0042 (BC-P2-02) — last-run evidence of the tier owners for the suite-to-contract matrix: the G5 full suite and
# `gov doctor` (the doctor checks run at G1 and G5), run by the product on a disposable bootstrap-installed project on
# a private unprovisioned machine. The matrix reads these outputs as supplied run evidence; it runs nothing itself.
# Usage: tier-runs.sh <gov> <scratch> <out-dir>
set -u
GOV="$1"; SCR="$2"; OUT="$3"
[ -e "$SCR" ] && mv "$SCR" "$SCR.old-$$"
mkdir -p "$SCR/proj/src" "$SCR/home" "$OUT"
export HOME="$SCR/home" XDG_STATE_HOME="$SCR/state" XDG_CACHE_HOME="$SCR/cache" GIT_CONFIG_GLOBAL=/dev/null \
  GIT_AUTHOR_NAME=p GIT_AUTHOR_EMAIL=p@example.invalid GIT_COMMITTER_NAME=p GIT_COMMITTER_EMAIL=p@example.invalid
unset GOV_CANONICAL_ROOT GOV_SESSION GOV_ROLE
cd "$SCR/proj"
printf '# tier-run probe\n' > README.md
printf 'pub fn total(a: i64, b: i64) -> i64 { a + b }\n' > src/lib.rs
git init -q && git add -A && git commit -qm baseline
g() { "$GOV" --json --root . --session S-tier --role orchestrator "$@"; }
g init --name tier --alias tier > "$OUT/init.json"
git add -A && git commit -qm installed
g rebuild-memory > "$OUT/rebuild-memory.json"
g health run --tier G5 --no-cache --no-persist > "$OUT/health-run-G5.json"
g doctor > "$OUT/doctor.json"
echo "# gov $GOV sha256 $(sha256sum "$GOV" | cut -c1-64); $(date -u +%FT%TZ)" > "$OUT/tier-runs.provenance.txt"
python3 - "$OUT" <<'PY'
import json, sys
out = sys.argv[1]
for f in ["health-run-G5.json", "doctor.json"]:
    d = json.load(open(f"{out}/{f}"))
    r = d.get("result") or (d.get("error") or {}).get("details") or {}
    fam = r.get("families") or {}
    chk = r.get("checks") or []
    print(f, "ok=", d.get("ok"), "verdict=", r.get("verdict"), "tier=", r.get("tier"),
          "families=", len(fam), "not_ok=", [k for k, v in fam.items() if not v.get("ok")],
          "doctor=", len(chk), "doctor_not_ok=", [c["id"] for c in chk if not c.get("ok")])
PY
