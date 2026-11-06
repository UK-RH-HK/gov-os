#!/usr/bin/env bash
# rebuild_pinned.sh with stand-ins for gov and the heavy slot: the arguments reach `gov rebuild --json`, a failed
# rebuild's code is passed on, and a search whose facets are unavailable gives 75 (the link not switched).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
mkdir -p "$T/tools" "$T/tree"
cp "$HERE/rebuild_pinned.sh" "$T/tools/"
printf '#!/usr/bin/env bash\nexec "$@"\n' > "$T/tools/heavy_slot.sh"
fail=0
check() { if [ "$2" = "$3" ]; then echo "ok   $1"; else echo "FAIL $1: got $2, want $3"; fail=1; fi; }
mkgov() {  # $1 rebuild rc, $2 facet availability (true|false)
  cat > "$T/gov" <<EOF
#!/usr/bin/env bash
if [ "\$1" = rebuild ]; then echo "\$*" > "$T/args"; echo '{"ok": true}'; exit $1; fi
echo '{"ok": true, "result": {"facets": {"lexical": {"available": $2}, "semantic": {"available": $2}}}}'
EOF
  chmod +x "$T/gov"
}
mkgov 0 true
GOV_PINNED="$T/gov" bash "$T/tools/rebuild_pinned.sh" "$T/tree" --seed /base >/dev/null 2>&1; rc=$?
check "1 rebuilt and searchable: exit 0" "$rc" 0
check "1b the arguments reach gov rebuild --json" "$(cat "$T/args")" "rebuild --json --seed /base"
mkgov 3 true
GOV_PINNED="$T/gov" bash "$T/tools/rebuild_pinned.sh" "$T/tree" >/dev/null 2>&1; rc=$?
check "2 a failed rebuild's code passed on" "$rc" 3
mkgov 0 false
GOV_PINNED="$T/gov" bash "$T/tools/rebuild_pinned.sh" "$T/tree" >/dev/null 2>&1; rc=$?
check "3 facets unavailable after the rebuild: 75, not switched" "$rc" 75
exit $fail
