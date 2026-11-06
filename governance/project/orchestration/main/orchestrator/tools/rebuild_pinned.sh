#!/usr/bin/env bash
# DEC-1087 (2), (3): the integration store's rebuild with the PINNED gov (~/.local/bin/gov), not the tree's own code,
# so the store always matches the code that agents search it with. Used as seed_store.py's SEED_REBUILD_CMD by
# refresh_integration_store.sh (the daily backstop and by-hand runs) until W2-116's product refresh is live:
#   rebuild_pinned.sh <tree> [gov rebuild arguments, e.g. --seed <base>]
# After the rebuild, one search with the pinned gov must find its facets available, or it exits 75 and the refresh
# keeps the link where it was. Prints the rebuild's JSON envelope (seed_store.py reads it).
set -u
TREE=$1; shift
HERE=$(cd "$(dirname "$0")" && pwd)
GOV=${GOV_PINNED:-$HOME/.local/bin/gov}
cd "$TREE" || exit 2
bash "$HERE/heavy_slot.sh" "$GOV" rebuild --json "$@"; rc=$?
[ "$rc" = 0 ] || exit "$rc"
out=$("$GOV" retrieve "decision register status" --json 2>/dev/null)
if printf '%s' "$out" | python3 -c 'import json,sys; f=(json.load(sys.stdin).get("result") or {}).get("facets") or {}; sys.exit(0 if f and all(v.get("available") for v in f.values()) else 1)'; then
  exit 0
fi
echo "rebuild_pinned: the pinned gov finds the rebuilt store's facets unavailable in $TREE: not switched" >&2
exit 75
