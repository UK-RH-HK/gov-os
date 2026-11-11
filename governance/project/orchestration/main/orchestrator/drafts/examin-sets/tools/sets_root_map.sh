#!/bin/bash
# ACT-EXAMIN-SETS-1, the owner's step 2: the same two evaluation_sets entries in the SETS ROOT's own path map (the file
# gov.retrieval.measure reads: <sets root>/governance/project/path-map.yaml). The file lies under the sets root, which
# is the owner's by hand (class-rules row walled-sessions: class O), as ACT-MSET-3 section 10 did for memory-verdict-2.
# Nothing here opens any other file under the sets root.
#
#   bash sets_root_map.sh check  [map]    read-only: "state before|applied" (exit 0), "state other: ..." (exit 3)
#   bash sets_root_map.sh apply  [map]    from the state before only: a copy is kept beside the map as
#                                         <map>.pre-ACT-EXAMIN-SETS-1, the two entries are inserted at the end of the
#                                         evaluation_sets block (tools/insert_entries.py, beside this script), the result is
#                                         parsed (old entries unchanged, exactly two new), and its sha256 is written to
#                                         <map>.ACT-EXAMIN-SETS-1.sha256
#   bash sets_root_map.sh undo   [map]    the kept copy put back, only while the map still hashes as written by apply
# map defaults to $HOME/gov-os-eval/governance/project/path-map.yaml. Needs python3 with PyYAML (the pinned interpreter
# has it; set PY to use another).
set -u
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${PY:-python3}"
step="${1:-}"
map="${2:-$HOME/gov-os-eval/governance/project/path-map.yaml}"
case "$step" in check|apply|undo) ;; *) echo "usage: sets_root_map.sh check|apply|undo [map]" >&2; exit 2 ;; esac
[ -f "$map" ] && [ ! -L "$map" ] || { echo "refused: $map is not a regular file" >&2; exit 3; }
keep="$map.pre-ACT-EXAMIN-SETS-1"
rec="$map.ACT-EXAMIN-SETS-1.sha256"
sum() { sha256sum "$1" | cut -c1-64; }
case "$step" in
  check)
    "$PY" -I "$HERE/insert_entries.py" --check "$map"; exit $? ;;
  apply)
    "$PY" -I "$HERE/insert_entries.py" --check "$map" > /dev/null || { echo "refused: the map is not in a state this step can change" >&2; exit 3; }
    if "$PY" -I "$HERE/insert_entries.py" --check "$map" | grep -q "state applied"; then echo "state applied; nothing to do"; exit 0; fi
    [ ! -e "$keep" ] || { echo "refused: $keep exists already" >&2; exit 3; }
    cp -p "$map" "$keep" || exit 5
    if ! "$PY" -I "$HERE/insert_entries.py" "$map"; then rm -f "$keep"; exit 3; fi
    sum "$map" > "$rec"
    echo "applied; the old map is kept as $keep"
    exit 0 ;;
  undo)
    [ -f "$keep" ] && [ -f "$rec" ] || { echo "nothing to undo: no kept copy or no record" >&2; exit 3; }
    [ "$(sum "$map")" = "$(cat "$rec")" ] || { echo "refused: the map changed after this step; a later change is not overwritten" >&2; exit 3; }
    cp -p "$keep" "$map.act-tmp" && mv -f "$map.act-tmp" "$map" || { rm -f "$map.act-tmp"; exit 5; }
    rm -f "$keep" "$rec"
    echo "undone: the map is as before"
    exit 0 ;;
esac
