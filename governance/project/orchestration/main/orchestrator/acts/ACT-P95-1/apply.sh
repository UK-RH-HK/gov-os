#!/bin/bash
# ACT-P95-1's apply.sh: check | apply | undo | verify, for one file: the machine gate's configuration
# ~/.gov-os/machine/gate.json (class (b), control: governance/project/operator/class-rules.yaml row machine-gate).
# The one change, frozen in the after copy: working_size_bytes 2191601664 (DEC-947 item 2, 2026-10-29) -> 805306368
# (0.75 GiB per live session, the owner's DEC-1149 (1), from the CTO's lead-memory ledger), its date and source; every
# other byte, the floor (3 GiB), the OOM trip (2 GiB) and both peak figures included, is unchanged.
# The state is decided by the file's sha256 alone (list.txt: root|path|before|after):
#   check   read-only: exit 0 "state before" | "state applied"; exit 3 "state other: ..." (changed, missing, a link)
#   apply   from the before only: the frozen after copy is written to a temp file beside it (mode kept) and moved into
#           place whole; from the after: left as it is (exit 0); anything else refused, nothing touched (exit 3)
#   undo    from the after only: the frozen before copy put back the same way; from the before: left as it is
#   verify  exit 0 only in the applied state, and the file's working_size_bytes reads 805306368
# Each frozen copy is hashed against list.txt before use (exit 4). HOME may be overridden (rehearsal only).
set -u
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|undo|verify" >&2; exit 2 ;; esac
IFS='|' read -r root rel before after < <(grep -v '^#' "$B/list.txt" | head -1)
[ "$root" = home ] || { echo "list.txt: root must be home" >&2; exit 2; }
F="$HOME/$rel"
h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }
[ "$(h "$B/before/home/$rel")" = "$before" ] || { echo "the frozen before copy does not hash as listed" >&2; exit 4; }
[ "$(h "$B/after/home/$rel")" = "$after" ] || { echo "the frozen after copy does not hash as listed" >&2; exit 4; }
put() { local src="$1" mode tmp; mode="$(stat -c %a "$F")" || return 1; tmp="$(mktemp "$F.act-XXXXXX")" || return 1
  if cat "$src" > "$tmp" && chmod "$mode" "$tmp" && mv -f "$tmp" "$F"; then return 0; fi; rm -f "$tmp"; return 1; }
cur="$(h "$F")"
state=other; [ "$cur" = "$before" ] && state=before; [ "$cur" = "$after" ] && state=applied
case "$step" in
  check) [ "$state" = other ] && { echo "state other: $F hashes $cur"; exit 3; }; echo "state $state"; exit 0 ;;
  apply) case "$state" in applied) echo "already applied"; exit 0;; before) put "$B/after/home/$rel" || exit 5
           [ "$(h "$F")" = "$after" ] || { echo "apply: the file does not hash as the after copy" >&2; exit 5; }; echo "applied"; exit 0;;
         *) echo "refused: state other: $F hashes $cur" >&2; exit 3;; esac ;;
  undo) case "$state" in before) echo "already before"; exit 0;; applied) put "$B/before/home/$rel" || exit 5
          [ "$(h "$F")" = "$before" ] || { echo "undo: the file does not hash as the before copy" >&2; exit 5; }; echo "undone"; exit 0;;
        *) echo "refused: state other: $F hashes $cur" >&2; exit 3;; esac ;;
  verify) [ "$state" = applied ] || { echo "not applied: $F"; exit 3; }
          python3 -I -c 'import json,sys; v=json.load(open(sys.argv[1]))["working_size_bytes"]["value"]; sys.exit(0 if v==805306368 else 1)' "$F" \
            || { echo "verify: working_size_bytes is not 805306368" >&2; exit 3; }
          echo "verified: working_size_bytes 805306368"; exit 0 ;;
esac
