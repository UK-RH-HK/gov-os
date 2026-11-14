#!/usr/bin/env bash
# The CTO's hand-over step at "released" (P-RELEASE-1 §4 step 8): fills the operator's script from the tag and the
# release record, so no value is copied by hand (RL-1). Reads, writes only <out>; changes nothing in the repository.
#     bash fill_release.sh <C, the commit named at "release ready" (12+ hex digits)> [<repo, default the main tree>] [<out>]
# <out> defaults to REPIN-COMMANDS-REL-0.1.0.sh beside this file. It refuses (exit 1, no file written) unless: the
# bundle's files pass `sha256sum -c BUNDLE.sha256` (checked first, before anything is read); v0.1.0
# is an annotated tag on a one-parent commit whose parent is <C>; between <C> and the tag only the record's two files
# changed; manifest.sha256 holds; the manifest names version 0.1.0, commit <C> in full, cli_version 0.1.0 and the wheel
# gov-0.1.0-py3-none-any.whl with a 64-digit sha256. It prints the four values and the filled script's sha256.
set -euo pipefail
B=$(cd "$(dirname "$0")" && pwd)
# First: the bundle's files are the reviewed ones (review F6). Any edit since the review stops the fill here.
(cd "$B" && sha256sum -c --strict --quiet BUNDLE.sha256) || { echo "REFUSED, nothing written: the bundle's files differ from BUNDLE.sha256 (the reviewed list)" >&2; exit 1; }
C_IN=${1:?the commit named at release ready}
REPO=${2:-/home/usain/Dynamic-Agentic-Engineering-OS}
OUT=${3:-$B/REPIN-COMMANDS-REL-0.1.0.sh}
VERSION=0.1.0; TAG=v0.1.0; REL=docs/releases/$VERSION
die() { echo "REFUSED, nothing written: $1" >&2; exit 1; }
FULL=$(git -C "$REPO" rev-parse --verify --quiet "$C_IN^{commit}") || die "$C_IN is not a commit in $REPO"
[ "$(git -C "$REPO" cat-file -t "refs/tags/$TAG" 2>/dev/null)" = tag ] || die "$TAG is not an annotated tag in $REPO"
TAGC=$(git -C "$REPO" rev-parse "$TAG^{commit}")
[ "$(git -C "$REPO" rev-list --parents -n 1 "$TAGC" | wc -w)" = 2 ] || die "$TAG's commit has not exactly one parent"
[ "$(git -C "$REPO" rev-parse "$TAGC^")" = "$FULL" ] || die "$TAG is on ${TAGC:0:12}, whose parent is not $C_IN (the tag goes on the record commit)"
changed=$(git -C "$REPO" diff --name-only "$FULL" "$TAGC" | sort | tr '\n' ' ')
[ "$changed" = "$REL/manifest.json $REL/manifest.sha256 " ] || die "between $C_IN and $TAG more than the record changed: $changed"
W=$(mktemp -d); trap 'rm -rf "$W"' EXIT
git -C "$REPO" show "$TAGC:$REL/manifest.json" > "$W/manifest.json"
git -C "$REPO" show "$TAGC:$REL/manifest.sha256" > "$W/manifest.sha256"
(cd "$W" && sha256sum -c --strict --quiet manifest.sha256) || die "manifest.json does not match manifest.sha256 at $TAG"
RECORD=$(sha256sum < "$W/manifest.json" | cut -d' ' -f1)
SHA=$(python3 - "$W/manifest.json" "$VERSION" "$FULL" <<'EOF'
import json, re, sys
m = json.load(open(sys.argv[1])); w = m.get("wheel") or {}
ok = (m.get("version") == sys.argv[2] and m.get("commit") == sys.argv[3] and m.get("cli_version") == "0.1.0"
      and w.get("name") == "gov-0.1.0-py3-none-any.whl" and re.fullmatch(r"[0-9a-f]{64}", str(w.get("sha256"))))
print(w["sha256"] if ok else "")
EOF
)
[ -n "$SHA" ] || die "the manifest does not name version $VERSION, commit $FULL, cli_version 0.1.0 and the wheel gov-0.1.0-py3-none-any.whl with its sha256"
C=${FULL:0:12}
EPOCH=$(git -C "$REPO" show -s --format=%ct "$FULL")
sed -e "s/__C__/$C/" -e "s/__EPOCH__/$EPOCH/" -e "s/__SHA__/$SHA/" -e "s/__RECORD__/$RECORD/" "$B/REPIN-COMMANDS-REL.template.sh" > "$OUT.tmp"
! grep -q '__[A-Z]*__' "$OUT.tmp" || { rm -f "$OUT.tmp"; die "a slot is left in the filled script"; }
mv "$OUT.tmp" "$OUT"
# The hash list the operator's line checks first (sha256sum -c): the filled script and every file it runs, 18 in all:
# the filled script, its checks and registry edit, the smoke test, the CTO's 9 tools, and the 5 files part B also runs
# (ACT-GUARD-FIX-4's and G-14's suites, the heavy slots' sizes, the staged W2-141 pair; the CTO's decision on review F3).
R=/home/usain/Dynamic-Agentic-Engineering-OS
O=$R/.gov-runtime/scratch/orchestrator
HASHES=$(dirname "$OUT")/REPIN-REL-$VERSION.sha256
( cd / && sha256sum "$OUT" "$B/rel_checks.sh" "$B/rel_registry.py" "$O/pin/smoke_repin5.sh" \
    "$O/tools/guard4_check.py" "$O/tools/hook_timing.py" "$O/tools/heavy_slot.sh" "$O/tools/refresh_integration_store.sh" \
    "$O/tools/seed_store.py" "$O/tools/rebuild_slot.sh" "$O/tools/test_guard_fix_3.py" "$O/tools/tree_busy.sh" "$O/tools/proc.sh" \
    "$O/drafts/act-guard-fix-4/test_guard_fix_4.py" "$O/drafts/g14/test_g14.py" "$O/tools/heavy_slots.conf" \
    "$R/docs/changes/W2-141-hook/pretooluse.py" "$R/docs/changes/W2-141-hook/role_reads.py" ) > "$HASHES.tmp" \
  || { rm -f "$OUT" "$HASHES.tmp"; die "a file the script runs cannot be read (above)"; }
mv "$HASHES.tmp" "$HASHES"
echo "C=$C (tag $TAG on ${TAGC:0:12})"
echo "EPOCH=$EPOCH"
echo "SHA=$SHA (the record's wheel sha256)"
echo "RECORD=$RECORD (manifest.json's sha256)"
echo "filled: $OUT sha256 $(sha256sum < "$OUT" | cut -d' ' -f1)"
echo "hash list: $HASHES ($(wc -l < "$HASHES") files) sha256 $(sha256sum < "$HASHES" | cut -d' ' -f1)"
