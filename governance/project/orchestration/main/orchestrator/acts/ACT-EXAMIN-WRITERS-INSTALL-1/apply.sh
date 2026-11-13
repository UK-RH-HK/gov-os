#!/bin/bash
# ACT-EXAMIN-WRITERS-INSTALL-1's apply.sh: check | apply | verify | undo [<sets root>]. Class (O), rows `walled-sessions` of
# governance/project/operator/class-rules.yaml (governance/project/indep-briefs/** and gov-os-eval/**): the owner's
# operator runs it BY HAND, from the repository's top folder (its cwd); the operator agent never takes it.
# Under DEC-1143 (1) (the two briefs' bytes, approved) and DEC-1130 (3) (the walled writer route).
#
# What it changes, and nothing else:
#   1. two files, byte for byte the approved briefs (frozen in after/repo/, listed in list.txt):
#        governance/project/indep-briefs/examin-sets/EXAMIN-writer.md          d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f
#        governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md  57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c
#   2. two lines appended at the end of the walls' approved list <sets root>/indep-walls/APPROVED (lines.txt, byte for byte),
#      in the form the launch script's parse_approved reads (indep_launch.py: `<sha256>\s+brief\s+<kind>\s+<path>`) and
#      the list's existing brief lines use: `<sha256>  brief writer <repository path>`.
#
# The sets root: the argument if given, else the path map's `sets_root_hidden.root` (governance/project/path-map.yaml,
# "~/gov-os-eval", so $HOME/gov-os-eval), expanded with $HOME. Neither: refused. It never guesses, and it never creates
# the list: a missing list (or indep-walls folder) is refused.
#
# States (decided from the two files, the list's lines and the launch script's own parser; nothing else is read):
#   before   both files absent; neither line in the list, and no other non-comment line naming either hash or either path
#   applied  both files present and byte-exact; each line in the list exactly once, and no other line naming either
#   other    anything else (one file only, a changed byte, a line twice or in another spelling, the list missing, a link,
#            the list not ending in a newline, the parser not loadable): refused, nothing touched
#   check   read-only: "state before|applied (...)" exit 0; "state other: <why>" on stderr, exit 3
#   apply   only from before: the list (old bytes + the two lines, checked with the launch script's parser) written beside
#           the old as a mktemp file and renamed over it (mode kept, 0400 stays 0400); the two files written; then
#           re-checked to "state applied". A failure part way removes what it wrote (the old list is never edited in place)
#   verify  exit 0 only in the state applied; exit 3 otherwise
#   undo    only from applied: the two files removed and exactly the two lines removed (every other line byte-identical;
#           right after an apply the list is byte for byte as before it); then re-checked to "state before"
# Exit codes: 0 done; 2 usage; 3 state refused; 4 the bundle does not hash as listed; 5 a write failed (what this run
# wrote was removed again); 9 not run from a repository's top folder, or no sets root.
#
# The operator's steps (main tree, about one minute; this script does not commit):
#   cd /home/usain/Dynamic-Agentic-Engineering-OS
#   A=.gov-runtime/scratch/orchestrator/acts/ACT-EXAMIN-WRITERS-INSTALL-1
#   bash $A/apply.sh check     # expect "state before ..."
#   bash $A/apply.sh apply     # expect "state applied ..."
#   bash $A/apply.sh verify    # exit 0
#   git add governance/project/indep-briefs/examin-sets/ && git commit -m "ACT-EXAMIN-WRITERS-INSTALL-1: the two walled writer briefs as the owner approved them (DEC-1143 (1)), and their lines in the walls' approved list" --trailer "Task: DAEO-sdxk" --trailer "Implements: DEC-1143, DEC-1130" --trailer "Role: owner" -- governance/project/indep-briefs/examin-sets/
# Undo: bash $A/apply.sh undo (then commit the two removals with the same trailers, if the commit above was made).
set -u
umask 022
B="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
step="${1:-}"
case "$step" in check|apply|undo|verify) ;; *) echo "usage: apply.sh check|apply|verify|undo [<sets root>]" >&2; exit 2 ;; esac
[ $# -le 2 ] || { echo "usage: apply.sh check|apply|verify|undo [<sets root>]" >&2; exit 2; }

# -- the frozen constants (DEC-1143 (1)); list.txt and lines.txt must agree with them --------------------------------
P1=governance/project/indep-briefs/examin-sets/EXAMIN-writer.md
H1=d37834e08c86e24c0fdb1884c4f11164d734af4dcb4b3a5536bd20e3efc0085f
P2=governance/project/indep-briefs/examin-sets/PROVING-GROUND-writer.md
H2=57820503b56948bf9e6ebe41abb2182c9a81db234e685218f21f71c69076549c
LINES_SHA=9b2aa04ce704bb89a023e8ef9d707b9d1db5978a3d5610d221fb807087317df5
L1="$H1  brief writer $P1"
L2="$H2  brief writer $P2"
LAUNCHER=governance/project/orchestration/tools/indep_launch.py
PATH_MAP=governance/project/path-map.yaml

h() { if [ -f "$1" ] && [ ! -L "$1" ]; then sha256sum "$1" | cut -c1-64; else echo null; fi; }

# -- the bundle hashes as listed -------------------------------------------------------------------------------------
want_list="repo|$P1|null|$H1
repo|$P2|null|$H2
sets_root|indep-walls/APPROVED|live (unread; neither line present)|live + the two lines of lines.txt appended at the end"
[ "$(cat "$B/list.txt" 2>/dev/null)" = "$want_list" ] || { echo "the bundle's list.txt is not as frozen" >&2; exit 4; }
[ "$(h "$B/lines.txt")" = "$LINES_SHA" ] || { echo "the bundle's lines.txt does not hash as frozen" >&2; exit 4; }
[ "$(printf '%s\n%s\n' "$L1" "$L2" | sha256sum | cut -c1-64)" = "$LINES_SHA" ] || { echo "lines.txt is not the two lines" >&2; exit 4; }
[ "$(h "$B/after/repo/$P1")" = "$H1" ] || { echo "the frozen copy does not hash as listed: after/repo/$P1" >&2; exit 4; }
[ "$(h "$B/after/repo/$P2")" = "$H2" ] || { echo "the frozen copy does not hash as listed: after/repo/$P2" >&2; exit 4; }

# -- the repository (cwd) and the sets root --------------------------------------------------------------------------
R="$PWD"
top="$(git -C "$R" rev-parse --show-toplevel 2>/dev/null)" || top=""
{ [ -n "$top" ] && [ "$(realpath "$top")" = "$(realpath "$R")" ] && [ -f "$R/$PATH_MAP" ] && [ -f "$R/$LAUNCHER" ]; } \
  || { echo "refused: run from the repository's top folder (no $PATH_MAP or $LAUNCHER here)" >&2; exit 9; }
if [ $# -eq 2 ]; then
  given="$2"; from="the argument"
else
  given="$(python3 -I -c 'import sys, yaml
d = yaml.safe_load(open(sys.argv[1], encoding="utf-8"))
r = d.get("sets_root_hidden", {}).get("root") if isinstance(d, dict) and isinstance(d.get("sets_root_hidden"), dict) else None
sys.exit(1) if not isinstance(r, str) or not r.strip() else print(r)' "$R/$PATH_MAP")" \
    || { echo "refused: no sets root (no argument, and the path map names no sets_root_hidden.root)" >&2; exit 9; }
  from="the path map's sets_root_hidden.root ($given)"
fi
case "$given" in "~") given="$HOME" ;; "~/"*) given="$HOME/${given#\~/}" ;; esac
case "/$given/" in */indep-walls/*) echo "refused: the sets root is named, never a folder under it" >&2; exit 9 ;; esac
case "$given" in /*) ;; *) echo "refused: the sets root must be an absolute path: $given" >&2; exit 9 ;; esac
SR="$given"
WALLS="$SR/indep-walls"
LIST="$WALLS/APPROVED"

PY='import sys, os, importlib.util
mode, launcher, lst = sys.argv[1], sys.argv[2], sys.argv[3]
l1, l2 = sys.argv[4].encode(), sys.argv[5].encode()
spec = importlib.util.spec_from_file_location("indep_launch_for_act", launcher)
il = importlib.util.module_from_spec(spec)
spec.loader.exec_module(il)
def facts(data):
    lines = data.split(b"\n")
    tail = lines.pop() if lines else b""
    out = {"ends_nl": (data == b"" or data.endswith(b"\n")), "nlines": len(lines)}
    _t, briefs = il.parse_approved(data)
    for i, l in ((1, l1), (2, l2)):
        h, _b, _k, p = l.decode().split(None, 3)
        out[f"exact{i}"] = sum(1 for x in lines if x == l) + (1 if tail == l else 0)
        out[f"related{i}"] = sum(1 for x in lines + ([tail] if tail else [])
                                 if not x.lstrip().startswith(b"#") and (h.encode() in x or p.encode() in x))
        out[f"parser{i}"] = sum(1 for (bh, bk, bp) in briefs if bh == h and bk == "writer" and il.norm_repo_path(bp) == p)
    return out
data = open(lst, "rb").read()
f = facts(data)
if mode == "facts":
    print(" ".join(f"{k}={int(v)}" for k, v in f.items()))
    sys.exit(0)
tmp = sys.argv[6]
if mode == "append":
    if not (f["ends_nl"] and f["exact1"] == f["exact2"] == f["related1"] == f["related2"] == f["parser1"] == f["parser2"] == 0):
        sys.exit("the list is not in the state before")
    new = data + l1 + b"\n" + l2 + b"\n"
    g = facts(new)
    if not (g["exact1"] == g["exact2"] == g["related1"] == g["related2"] == g["parser1"] == g["parser2"] == 1
            and new[:len(data)] == data and g["nlines"] == f["nlines"] + 2):
        sys.exit("the new list does not read as the old plus the two lines")
elif mode == "remove":
    if not (f["ends_nl"] and f["exact1"] == f["exact2"] == f["related1"] == f["related2"] == f["parser1"] == f["parser2"] == 1):
        sys.exit("the list is not in the state applied")
    kept = [x for x in data.split(b"\n")[:-1] if x not in (l1, l2)]
    new = b"".join(x + b"\n" for x in kept)
    g = facts(new)
    if not (g["exact1"] == g["exact2"] == g["related1"] == g["related2"] == g["parser1"] == g["parser2"] == 0
            and g["nlines"] == f["nlines"] - 2 and len(new) == len(data) - len(l1) - len(l2) - 2):
        sys.exit("the new list does not read as the old less exactly the two lines")
else:
    sys.exit("mode")
with open(tmp, "wb") as fh:
    fh.write(new)
    fh.flush()
    os.fsync(fh.fileno())
'

# -- the state -------------------------------------------------------------------------------------------------------
why=""
file_state() { # file_state <path> <sha>: absent | exact | other
  local f="$R/$1"
  if [ ! -e "$f" ] && [ ! -L "$f" ]; then echo absent
  elif [ -f "$f" ] && [ ! -L "$f" ] && [ "$(h "$f")" = "$2" ]; then echo exact
  else echo other; fi
}
decide() {
  st=other; why=""; F=""
  f1="$(file_state "$P1" "$H1")"; f2="$(file_state "$P2" "$H2")"
  if [ ! -d "$SR" ]; then why="the sets root $SR is not a folder ($from)"; return; fi
  if [ -L "$WALLS" ] || [ ! -d "$WALLS" ]; then why="$WALLS is not a folder (a list is never created)"; return; fi
  if [ -L "$LIST" ]; then why="the list $LIST is a link"; return; fi
  if [ ! -e "$LIST" ]; then why="the list $LIST does not exist (a new list is never created)"; return; fi
  if [ ! -f "$LIST" ] || [ ! -r "$LIST" ]; then why="the list $LIST is not a readable file"; return; fi
  F="$(python3 -I -c "$PY" facts "$R/$LAUNCHER" "$LIST" "$L1" "$L2" 2>/dev/null)" \
    || { why="the launch script's parser ($LAUNCHER) cannot read the list"; return; }
  local ends_nl exact1 exact2 related1 related2 parser1 parser2 nlines
  eval "$F"
  [ "$ends_nl" = 1 ] || { why="the list does not end in a newline"; return; }
  if [ "$f1 $f2" = "absent absent" ] && [ "$exact1$exact2$related1$related2$parser1$parser2" = 000000 ]; then st=before
  elif [ "$f1 $f2" = "exact exact" ] && [ "$exact1$exact2$related1$related2$parser1$parser2" = 111111 ]; then st=applied
  else why="files: EXAMIN-writer.md $f1, PROVING-GROUND-writer.md $f2; list: EXAMIN line $exact1 exact/$related1 naming it/$parser1 parsed, PROVING-GROUND line $exact2/$related2/$parser2"; fi
}
summary() { echo "list sha256 $(h "$LIST" | cut -c1-12), $(echo "$F" | sed -n 's/.*nlines=\([0-9]*\).*/\1/p') lines; sets root from $from"; }

put_file() { # put_file <rel>: the frozen copy written through a mktemp file beside it, then renamed (0644)
  local f="$R/$1" tmp
  mkdir -p "$(dirname "$f")" || return 1
  tmp="$(mktemp "$f.act-tmp.XXXXXX")" || return 1
  if cat "$B/after/repo/$1" > "$tmp" && chmod 644 "$tmp" && mv -f "$tmp" "$f"; then return 0; fi
  rm -f "$tmp"; return 1
}
new_list() { # new_list append|remove: the new list as a mktemp file beside the old (mode kept); prints its name
  local mode tmp
  mode="$(stat -c %a "$LIST")" || return 1
  tmp="$(mktemp "$WALLS/.APPROVED.act-ewi.XXXXXX")" || return 1
  if python3 -I -c "$PY" "$1" "$R/$LAUNCHER" "$LIST" "$L1" "$L2" "$tmp" && chmod "$mode" "$tmp"; then echo "$tmp"; return 0; fi
  rm -f "$tmp"; return 1
}

decide
case "$step" in
  check)
    [ "$st" = other ] && { echo "state other: $why" >&2; exit 3; }
    echo "state $st ($(summary))"; exit 0 ;;
  verify)
    [ "$st" = applied ] || { echo "not applied: ${why:-state $st}" >&2; exit 3; }
    echo "state applied ($(summary))"; exit 0 ;;
  apply)
    [ "$st" = other ] && { echo "refused: state other: $why; nothing touched" >&2; exit 3; }
    [ "$st" = applied ] && { echo "refused: already applied ($(summary)); nothing touched" >&2; exit 3; }
    made_dir=0; [ -d "$R/$(dirname "$P1")" ] || made_dir=1
    tmp="$(new_list append)" || { echo "failed: the new list could not be built beside the old; nothing touched" >&2; exit 5; }
    wrote=""
    undo_partial() { for p in $wrote; do rm -f "$R/$p"; done; rm -f "$tmp"
      [ "$made_dir" = 1 ] && rmdir "$R/$(dirname "$P1")" 2>/dev/null; }
    for p in "$P1" "$P2"; do
      put_file "$p" || { echo "failed: $p could not be written; what this run wrote is removed" >&2; undo_partial; exit 5; }
      wrote="$wrote $p"
    done
    mv -f "$tmp" "$LIST" || { echo "failed: the list could not be renamed into place; the files are removed" >&2; undo_partial; exit 5; }
    decide
    [ "$st" = applied ] || { echo "failed: after the apply the state is not applied: ${why:-state $st}" >&2; exit 5; }
    echo "state applied ($(summary))"; exit 0 ;;
  undo)
    [ "$st" = other ] && { echo "refused: state other: $why; nothing touched" >&2; exit 3; }
    [ "$st" = before ] && { echo "refused: nothing to undo, state before ($(summary)); nothing touched" >&2; exit 3; }
    tmp="$(new_list remove)" || { echo "failed: the new list could not be built beside the old; nothing touched" >&2; exit 5; }
    removed=""
    restore_partial() { for p in $removed; do put_file "$p"; done; rm -f "$tmp"; }
    for p in "$P1" "$P2"; do
      rm -f "$R/$p" || { echo "failed: $p could not be removed; restored" >&2; restore_partial; exit 5; }
      removed="$removed $p"
    done
    mv -f "$tmp" "$LIST" || { echo "failed: the list could not be renamed into place; the files are restored" >&2; restore_partial; exit 5; }
    rmdir "$R/$(dirname "$P1")" 2>/dev/null
    decide
    [ "$st" = before ] || { echo "failed: after the undo the state is not before: ${why:-state $st}" >&2; exit 5; }
    echo "state before ($(summary))"; exit 0 ;;
esac
